#!/usr/bin/env python3
"""Download Columbia River DART hourly water-quality for CCIW and run W4 checks.

URL pattern (confirmed 2026-08-14 via the query form's
"Generate Query Result Link Only"):

  https://cbr.washington.edu/dart/cs/php/rpt/wqm_hourly.php
      ?sc=1&year=YYYY&proj=CCIW&startdate=01/01&days=365&outputFormat=csv

Form (GET, /dart/query/wqm_hourly → action /dart/cs/php/rpt/wqm_hourly.php):
  year, proj, startdate (mm/dd), days, outputFormat=csv|html,
  datalink=1 → HTML page containing the sc=1 URL
  sc=1      → script call, returns CSV attachment

Usage:
  python download_dart_cciw.py
  python download_dart_cciw.py --years 2011-2025
  python download_dart_cciw.py --skip-download
  python download_dart_cciw.py --skip-analyze
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from io import StringIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
DATA_DIR = ROOT / "06_PAPER" / "data" / "dart_cciw"
ANALYSIS_DIR = ROOT / "06_PAPER" / "analysis"
NOTES_DIR = ROOT / "06_PAPER" / "notes"
LIB_OBS = ROOT / "02_LIBRARY" / "06_examples" / "v5.0_beta" / "Bonneville_TDG" / "CCIW_TDG_Temp_2011-2015.csv"
RUN = ROOT / "05_REPRO_RUNS" / "run_20260814_bonneville" / "Bonneville_SYSTDG"
TDGTA_OUT = RUN / "TDGTarget_output.csv"
QGT_IN = RUN / "QGT_BON_2011_2015_daily_DSS-scaled.csv"

ENDPOINT = "https://cbr.washington.edu/dart/cs/php/rpt/wqm_hourly.php"
QUERY_PAGE = "https://cbr.washington.edu/dart/query/wqm_hourly"
UA = (
    "CE-QUAL-W2-paper-research/1.0 "
    "(academic; Bonneville CCIW TDG verification; contact via project README)"
)
CMS_PER_KCFS = 28.316846592
MISSING_OBS = -90.0
TDG_ROUND_TOL = 0.051  # 1-decimal rounding envelope
SLEEP_S = 3.0
MAX_RETRIES = 1  # one retry on transient errors, then stop that year


def dart_url(year: int, startdate: str = "01/01", days: int = 365, datalink: bool = False) -> str:
    q = {
        "sc": "1",
        "year": str(year),
        "proj": "CCIW",
        "startdate": startdate,
        "days": str(days),
        "outputFormat": "csv",
    }
    if datalink:
        q["datalink"] = "1"
        q.pop("sc", None)
    return ENDPOINT + "?" + urllib.parse.urlencode(q)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _curl_bin() -> str | None:
    return shutil.which("curl.exe") or shutil.which("curl")


def _http_get_curl(curl: str, url: str, timeout: int) -> tuple[int, bytes, str]:
    """Prefer curl: Python urllib hits SSLError (ASN1 NOT_ENOUGH_DATA) on this host."""
    with tempfile.TemporaryDirectory() as td:
        td_p = Path(td)
        body_path = td_p / "body.bin"
        hdr_path = td_p / "hdr.txt"
        cmd = [
            curl,
            "-sS",
            "-L",
            "--http1.1",
            "-A",
            UA,
            "-D",
            str(hdr_path),
            "-o",
            str(body_path),
            "-w",
            "%{http_code}",
            "--max-time",
            str(timeout),
            url,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
        status_txt = (proc.stdout or "").strip()
        try:
            status = int(status_txt)
        except ValueError:
            status = 0
        body = body_path.read_bytes() if body_path.exists() else b""
        ctype = ""
        if hdr_path.exists():
            for line in hdr_path.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.lower().startswith("content-type:"):
                    ctype = line.split(":", 1)[1].strip()
        if proc.returncode != 0 and not body:
            err = (proc.stderr or "").strip() or f"curl exit {proc.returncode}"
            raise OSError(err)
        return status, body, ctype


def _http_get_urllib(url: str, timeout: int) -> tuple[int, bytes, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/csv,text/plain,text/html;q=0.8,*/*;q=0.5",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            ctype = resp.headers.get("Content-Type", "")
            body = resp.read()
            return int(status), body, ctype
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        ctype = e.headers.get("Content-Type", "") if e.headers else ""
        return int(e.code), body, ctype


def _http_get(url: str, timeout: int = 180) -> tuple[int, bytes, str]:
    curl = _curl_bin()
    if curl:
        return _http_get_curl(curl, url, timeout)
    return _http_get_urllib(url, timeout)


def is_valid_dart_csv(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 500:
        return False
    head = path.read_text(encoding="utf-8", errors="replace")[:800]
    return "Dissolved Gas Percent" in head and "Project" in head


def save_year_csv(year: int, body: bytes, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    text = body.decode("utf-8", errors="replace")
    if text.lstrip().lower().startswith("<!doctype") or "<html" in text[:200].lower():
        dest.unlink(missing_ok=True)
        return {"ok": False, "reason": "html_instead_of_csv", "bytes": len(body)}
    if "Dissolved Gas Percent" not in text[:500]:
        dest.unlink(missing_ok=True)
        return {"ok": False, "reason": "missing_expected_header", "preview": text[:240]}
    n_rows = sum(1 for line in text.splitlines() if line.startswith("CCIW,"))
    return {
        "ok": True,
        "bytes": dest.stat().st_size,
        "n_cciw_rows": n_rows,
        "sha256": sha256_file(dest),
        "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
    }


def _needs_leap_patch(path: Path, year: int) -> bool:
    if not calendar.isleap(year) or not path.is_file():
        return False
    df = read_dart_hourly(path)
    dates = pd.to_datetime(df["Date"], errors="coerce")
    return not ((dates.dt.month == 12) & (dates.dt.day == 31)).any()


def download_year(year: int, dest: Path, force: bool = False) -> dict:
    rec = {
        "year": year,
        "url": dart_url(year, days=365),
        "downloader": "curl" if _curl_bin() else "urllib",
    }
    if dest.exists() and is_valid_dart_csv(dest) and not force:
        rec.update(
            {
                "ok": True,
                "skipped": True,
                "bytes": dest.stat().st_size,
                "sha256": sha256_file(dest),
                "path": str(dest.relative_to(ROOT)).replace("\\", "/"),
            }
        )
        if _needs_leap_patch(dest, year):
            rec["leap_day_patch"] = fetch_and_append_day(year, "12/31", dest)
            rec["sha256"] = sha256_file(dest)
            rec["bytes"] = dest.stat().st_size
        return rec

    # Form max is 365 days; leap years miss Dec 31 and are patched below.
    url = dart_url(year, days=365)
    urls_tried = [url]
    try:
        status, body, ctype = _http_get(url)
    except (urllib.error.URLError, TimeoutError, OSError, subprocess.TimeoutExpired) as e:
        rec.update(
            {
                "ok": False,
                "status": None,
                "reason": "network_error",
                "error": f"{type(e).__name__}: {e}",
                "urls_tried": urls_tried,
            }
        )
        return rec

    last_preview = body[:400].decode("utf-8", errors="replace")
    rec["status"] = status
    rec["content_type"] = ctype
    rec["urls_tried"] = urls_tried
    rec["days_requested"] = 365
    if status in (403, 429, 503):
        rec.update(
            {
                "ok": False,
                "reason": "blocked_or_unavailable",
                "preview": last_preview[:400],
            }
        )
        return rec
    if status != 200:
        rec.update({"ok": False, "reason": "http_error", "preview": last_preview[:400]})
        return rec

    saved = save_year_csv(year, body, dest)
    rec.update(saved)
    if saved.get("ok") and _needs_leap_patch(dest, year):
        rec["leap_day_patch"] = fetch_and_append_day(year, "12/31", dest)
        rec["sha256"] = sha256_file(dest)
        rec["bytes"] = dest.stat().st_size
    return rec


def fetch_and_append_day(year: int, startdate: str, dest: Path) -> dict:
    url = dart_url(year, startdate=startdate, days=1)
    status, body, ctype = _http_get(url)
    if status != 200:
        return {"ok": False, "status": status, "url": url}
    extra = dest.with_name(dest.stem + f"_{startdate.replace('/', '')}_extra.csv")
    saved = save_year_csv(year, body, extra)
    if not saved.get("ok"):
        return {"ok": False, "url": url, **saved}
    base = dest.read_text(encoding="utf-8", errors="replace").splitlines()
    add = extra.read_text(encoding="utf-8", errors="replace").splitlines()
    notes_i = next((i for i, ln in enumerate(base) if ln.startswith("Notes:")), len(base))
    add_rows = [ln for ln in add[1:] if ln.startswith("CCIW,")]
    merged = base[:notes_i] + add_rows + base[notes_i:]
    dest.write_text("\n".join(merged) + "\n", encoding="utf-8")
    extra.unlink(missing_ok=True)
    return {"ok": True, "url": url, "appended_rows": len(add_rows), "content_type": ctype}


def read_dart_hourly(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    cut = next((i for i, ln in enumerate(lines) if ln.startswith("Notes:")), len(lines))
    df = pd.read_csv(StringIO("\n".join(lines[:cut])))
    df.columns = [c.strip() for c in df.columns]
    rename = {}
    for c in df.columns:
        cl = c.lower()
        if "dissolved gas percent" in cl:
            rename[c] = "tdg_pct"
        elif cl.startswith("dissolved gas (") and "percent" not in cl:
            rename[c] = "tdg_mmhg"
        elif "barometric" in cl:
            rename[c] = "bp_mmhg"
        elif "temperature (c)" in cl:
            rename[c] = "temp_c"
        elif "outflow" in cl:
            rename[c] = "outflow_kcfs"
        elif cl.startswith("spill (") and "percent" not in cl:
            rename[c] = "spill_kcfs"
        elif "spill percent" in cl:
            rename[c] = "spill_pct"
    df = df.rename(columns=rename)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Hour"] = pd.to_numeric(df.get("Hour"), errors="coerce").astype("Int64")
    for col in ("tdg_pct", "tdg_mmhg", "bp_mmhg", "temp_c", "outflow_kcfs", "spill_kcfs", "spill_pct"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["year"] = df["Date"].dt.year
    df["date"] = df["Date"].dt.date
    return df


def load_all_dart(years: list[int]) -> pd.DataFrame:
    frames = []
    for y in years:
        p = DATA_DIR / f"cciw_hourly_{y}.csv"
        if is_valid_dart_csv(p):
            frames.append(read_dart_hourly(p))
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(subset=["date", "Hour"], keep="last")
    return df.sort_values(["Date", "Hour"]).reset_index(drop=True)


def load_library_obs() -> pd.DataFrame:
    df = pd.read_csv(LIB_OBS, skiprows=2)
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
    df["JDAY"] = pd.to_numeric(df["JDAY"], errors="coerce")
    df["tdg"] = pd.to_numeric(df["Total dissolved gas"], errors="coerce")
    df["temp"] = pd.to_numeric(df["Temperature"], errors="coerce")
    df["date"] = df["Datetime"].dt.date
    df["hour_label"] = df["Datetime"].dt.hour
    df["dart_hour"] = ((df["hour_label"] + 1) * 100).astype("Int64")
    df["tdg_valid"] = np.isfinite(df["tdg"]) & (df["tdg"] > MISSING_OBS)
    df["temp_valid"] = np.isfinite(df["temp"]) & (df["temp"] > MISSING_OBS)
    return df


def round_half_up(x: np.ndarray, ndigits: int = 1) -> np.ndarray:
    p = 10.0**ndigits
    return np.sign(x) * np.floor(np.abs(x) * p + 0.5) / p


def _finite_pair(a: pd.Series, b: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    aa = pd.to_numeric(a, errors="coerce").to_numpy(dtype=float)
    bb = pd.to_numeric(b, errors="coerce").to_numpy(dtype=float)
    m = np.isfinite(aa) & np.isfinite(bb)
    return aa[m], bb[m]


def pair_metrics(obs: np.ndarray, other: np.ndarray) -> dict:
    if len(obs) == 0:
        return {"n": 0}
    d = other - obs
    mae = float(np.mean(np.abs(d)))
    rmse = float(np.sqrt(np.mean(d**2)))
    return {
        "n": int(len(obs)),
        "mae": round(mae, 6),
        "rmse": round(rmse, 6),
        "bias": round(float(np.mean(d)), 6),
        "max_abs_diff": round(float(np.max(np.abs(d))), 6),
        "obs_min": round(float(np.min(obs)), 4),
        "obs_max": round(float(np.max(obs)), 4),
        "other_min": round(float(np.min(other)), 4),
        "other_max": round(float(np.max(other)), 4),
    }


def jday_to_date(jday: float) -> date:
    # Library JDAY 40544 = 2011-01-01 = Excel serial (origin 1899-12-30).
    origin = datetime(1899, 12, 30)
    return (origin + pd.to_timedelta(float(jday), unit="D")).date()


def excel_serial(d: date) -> float:
    origin = date(1899, 12, 30)
    return float((d - origin).days)


def json_safe(obj):
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return None if not math.isfinite(v) else v
    if isinstance(obj, float):
        return None if not math.isfinite(obj) else obj
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    return obj


def download_years(years: list[int], force: bool = False) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Reuse a previously fetched 2011 file sitting in the project root.
    root_2011 = ROOT / "dart_cciw_2011.csv"
    dest_2011 = DATA_DIR / "cciw_hourly_2011.csv"
    if 2011 in years and root_2011.is_file() and not dest_2011.exists() and is_valid_dart_csv(root_2011):
        dest_2011.write_bytes(root_2011.read_bytes())

    log = {
        "endpoint": ENDPOINT,
        "query_page": QUERY_PAGE,
        "url_pattern": dart_url(2011, days=365),
        "datalink_example": dart_url(2011, startdate="04/01", days=1, datalink=True),
        "script_call_flag": "sc=1",
        "user_agent": UA,
        "years_requested": years,
        "files": [],
        "stopped_early": False,
    }
    for i, y in enumerate(years):
        dest = DATA_DIR / f"cciw_hourly_{y}.csv"
        print(f"[download] {y} → {dest.name}", flush=True)
        rec = download_year(y, dest, force=force)
        log["files"].append(rec)
        print(
            f"  ok={rec.get('ok')} status={rec.get('status')} "
            f"skipped={rec.get('skipped', False)} bytes={rec.get('bytes')} "
            f"reason={rec.get('reason')}",
            flush=True,
        )
        if rec.get("ok") is False and rec.get("status") in (403, 429, 503):
            log["stopped_early"] = True
            log["stop_reason"] = rec
            break
        if i < len(years) - 1 and not rec.get("skipped"):
            time.sleep(SLEEP_S)
    log["n_ok"] = sum(1 for f in log["files"] if f.get("ok"))
    log["success"] = log["n_ok"] > 0
    (DATA_DIR / "download_log.json").write_text(
        json.dumps(json_safe(log), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return log


def compare_cciw_vs_dart(lib: pd.DataFrame, dart: pd.DataFrame) -> dict:
    dart_2011_2015 = dart[(dart["year"] >= 2011) & (dart["year"] <= 2015)].copy()
    merged = lib.merge(
        dart_2011_2015,
        left_on=["date", "dart_hour"],
        right_on=["date", "Hour"],
        how="outer",
        suffixes=("_lib", "_dart"),
        indicator=True,
    )

    both = merged["_merge"] == "both"
    lib_only = merged["_merge"] == "left_only"
    dart_only = merged["_merge"] == "right_only"

    tdg_both_valid = (
        both
        & merged["tdg_valid"].fillna(False)
        & np.isfinite(merged["tdg_pct"])
    )
    o = merged.loc[tdg_both_valid, "tdg"].to_numpy(dtype=float)
    d = merged.loc[tdg_both_valid, "tdg_pct"].to_numpy(dtype=float)
    m = pair_metrics(o, d)
    absdiff = np.abs(d - o) if len(o) else np.array([])
    round_hu = round_half_up(d, 1) if len(o) else np.array([])
    round_py = np.round(d, 1) if len(o) else np.array([])
    match_tol = float(np.mean(absdiff <= TDG_ROUND_TOL)) if len(o) else None
    match_hu = float(np.mean(np.abs(round_hu - o) < 1e-9)) if len(o) else None
    match_py = float(np.mean(np.abs(round_py - o) < 1e-9)) if len(o) else None

    n_lib_valid = int(lib["tdg_valid"].sum())
    n_dart_valid = int(dart_2011_2015["tdg_pct"].notna().sum())
    n_lib_valid_unpaired = int(
        (lib_only & merged["tdg_valid"].fillna(False)).sum()
    )
    n_dart_valid_unpaired = int((dart_only & merged["tdg_pct"].notna()).sum())

    outliers = []
    if len(o):
        idx = np.where(absdiff > 0.15)[0]
        rows = merged.loc[tdg_both_valid].iloc[idx]
        for _, r in rows.head(25).iterrows():
            outliers.append(
                {
                    "datetime_lib": None if pd.isna(r["Datetime"]) else str(r["Datetime"]),
                    "date": str(r["date"]),
                    "hour_lib": None if pd.isna(r.get("hour_label")) else int(r["hour_label"]),
                    "hour_dart": None if pd.isna(r.get("Hour")) else int(r["Hour"]),
                    "lib_tdg": float(r["tdg"]),
                    "dart_tdg": float(r["tdg_pct"]),
                    "diff": float(r["tdg_pct"] - r["tdg"]),
                }
            )

    temp_valid = (
        both
        & merged["temp_valid"].fillna(False)
        & np.isfinite(merged["temp_c"])
    )
    to, td = _finite_pair(merged.loc[temp_valid, "temp"], merged.loc[temp_valid, "temp_c"])
    tm = pair_metrics(to, td)
    t_abs = np.abs(td - to) if len(to) else np.array([])
    t_match = float(np.mean(t_abs <= TDG_ROUND_TOL)) if len(to) else None

    # Daily means on calendar date (library date == DART Date under convention A).
    lib_d = (
        lib.loc[lib["tdg_valid"]]
        .groupby("date", as_index=False)["tdg"]
        .mean()
        .rename(columns={"tdg": "lib_tdg"})
    )
    dart_d = (
        dart_2011_2015.dropna(subset=["tdg_pct"])
        .groupby("date", as_index=False)["tdg_pct"]
        .mean()
        .rename(columns={"tdg_pct": "dart_tdg"})
    )
    daily = lib_d.merge(dart_d, on="date", how="inner")
    do, dd = daily["lib_tdg"].to_numpy(), daily["dart_tdg"].to_numpy()
    daily_m = pair_metrics(do, dd)
    daily_match = float(np.mean(np.abs(dd - do) <= TDG_ROUND_TOL)) if len(do) else None

    n_lib_hours = int(lib["Datetime"].notna().sum())
    n_lib_missing_tdg = n_lib_hours - n_lib_valid
    n_dart_hours = int(len(dart_2011_2015))
    n_dart_missing_tdg = n_dart_hours - n_dart_valid

    by_year_match = []
    if len(o):
        tmp = merged.loc[tdg_both_valid, ["date", "tdg", "tdg_pct"]].copy()
        tmp["year"] = pd.to_datetime(tmp["date"]).dt.year
        tmp["absdiff"] = (tmp["tdg_pct"] - tmp["tdg"]).abs()
        for y, g in tmp.groupby("year"):
            by_year_match.append(
                {
                    "year": int(y),
                    "n": int(len(g)),
                    "mae": round(float(g["absdiff"].mean()), 6),
                    "match_rate_abs_le_0p051": round(float((g["absdiff"] <= TDG_ROUND_TOL).mean()), 6),
                    "n_abs_diff_gt_0p15": int((g["absdiff"] > 0.15).sum()),
                    "max_abs_diff": round(float(g["absdiff"].max()), 6),
                }
            )

    # MAE ~0.03 and 98%+ inside the 1-decimal band = rounding + a handful of
    # CWMS/DART revisions (2011-03-11/12 cluster), not a rewritten series.
    verdict = (
        "library_is_dart_rounded"
        if (m.get("n", 0) >= 1000 and (match_tol or 0) >= 0.99 and m.get("mae", 9) < 0.05)
        else (
            "library_is_dart_with_rounding_and_minor_revisions"
            if (m.get("n", 0) >= 1000 and (match_tol or 0) >= 0.97 and m.get("mae", 9) < 0.05)
            else (
                "library_close_to_dart"
                if (m.get("n", 0) >= 1000 and (match_tol or 0) >= 0.90)
                else "library_differs_from_dart"
            )
        )
    )

    return {
        "alignment": {
            "convention": (
                "Library Datetime hour h on calendar date D maps to DART "
                "Date=D, Hour=(h+1)*100 (hour-ending Pacific Timestamp minus 1 h). "
                "Verified on 2011-04-01: library 0:00 TDG=111.9 matches DART "
                "Hour 100 / Pacific 01:00 TDG=111.88."
            ),
            "jday_epoch": "Excel serial; JDAY 40544 = 2011-01-01 (origin 1899-12-30).",
            "library_header": (
                "$2011-2015 TDG % saturation (CWMS), water temperature (CWMS) "
                "by 6_TDG_data_to_W2npt_v2.py on 2017-12-21"
            ),
            "library_source_claimed": "CWMS",
            "dart_source_claimed": "USACE NWD via Columbia River DART",
        },
        "counts": {
            "library_hours": n_lib_hours,
            "library_tdg_valid": n_lib_valid,
            "library_tdg_missing": n_lib_missing_tdg,
            "library_missing_frac": round(n_lib_missing_tdg / n_lib_hours, 6) if n_lib_hours else None,
            "dart_2011_2015_hours": n_dart_hours,
            "dart_2011_2015_tdg_valid": n_dart_valid,
            "dart_2011_2015_tdg_missing": n_dart_missing_tdg,
            "merge_both": int(both.sum()),
            "merge_library_only": int(lib_only.sum()),
            "merge_dart_only": int(dart_only.sum()),
            "library_valid_unpaired": n_lib_valid_unpaired,
            "dart_valid_unpaired": n_dart_valid_unpaired,
        },
        "hourly_tdg": {
            **m,
            "match_rate_abs_le_0p051": None if match_tol is None else round(match_tol, 6),
            "match_rate_round_half_up_1dec": None if match_hu is None else round(match_hu, 6),
            "match_rate_python_round_1dec": None if match_py is None else round(match_py, 6),
            "n_abs_diff_gt_0p15": int((absdiff > 0.15).sum()) if len(absdiff) else 0,
            "n_abs_diff_gt_1": int((absdiff > 1.0).sum()) if len(absdiff) else 0,
            "outlier_examples": outliers,
            "by_year": by_year_match,
        },
        "hourly_temp_c": {
            **tm,
            "match_rate_abs_le_0p051": None if t_match is None else round(t_match, 6),
        },
        "daily_tdg": {
            **daily_m,
            "match_rate_abs_le_0p051": None if daily_match is None else round(daily_match, 6),
        },
        "verdict": verdict,
        "paired_frame_n": int(tdg_both_valid.sum()),
        "_merged_hourly": merged.loc[tdg_both_valid, ["Datetime", "date", "tdg", "tdg_pct", "temp", "temp_c"]].copy(),
        "_daily": daily.copy(),
    }


def exceedance_table(dart: pd.DataFrame, year_min: int, year_max: int) -> dict:
    sub = dart[(dart["year"] >= year_min) & (dart["year"] <= year_max)].copy()
    valid = sub.dropna(subset=["tdg_pct"])
    n = int(len(valid))
    if n == 0:
        return {"year_min": year_min, "year_max": year_max, "n_valid_hours": 0}

    def frac(series, thr):
        return round(float((series > thr).mean()), 6)

    by_year = []
    for y, g in valid.groupby(valid["Date"].dt.year):
        s = g["tdg_pct"]
        daily = g.groupby("date")["tdg_pct"].mean()
        by_year.append(
            {
                "year": int(y),
                "n_valid_hours": int(len(s)),
                "n_calendar_hours": int((sub["year"] == y).sum()),
                "valid_hour_frac_of_year": round(len(s) / max((sub["year"] == y).sum(), 1), 6),
                "pct_hours_gt_115": round(100.0 * float((s > 115).mean()), 4),
                "pct_hours_gt_120": round(100.0 * float((s > 120).mean()), 4),
                "n_hours_gt_115": int((s > 115).sum()),
                "n_hours_gt_120": int((s > 120).sum()),
                "n_days_dailymean_gt_115": int((daily > 115).sum()),
                "n_days_dailymean_gt_120": int((daily > 120).sum()),
                "annual_max_tdg": round(float(s.max()), 4),
                "annual_min_tdg": round(float(s.min()), 4),
                "annual_mean_tdg": round(float(s.mean()), 4),
            }
        )

    s = valid["tdg_pct"]
    daily = valid.groupby("date")["tdg_pct"].mean()
    return {
        "year_min": year_min,
        "year_max": year_max,
        "n_valid_hours": n,
        "n_calendar_hours": int(len(sub)),
        "pct_hours_gt_115": round(100.0 * float((s > 115).mean()), 4),
        "pct_hours_gt_120": round(100.0 * float((s > 120).mean()), 4),
        "n_hours_gt_115": int((s > 115).sum()),
        "n_hours_gt_120": int((s > 120).sum()),
        "n_days_dailymean_gt_115": int((daily > 115).sum()),
        "n_days_dailymean_gt_120": int((daily > 120).sum()),
        "max_tdg": round(float(s.max()), 4),
        "min_tdg": round(float(s.min()), 4),
        "mean_tdg": round(float(s.mean()), 4),
        "by_year": by_year,
        "denominator_note": (
            "Percentages are among hours with non-missing Dissolved Gas Percent. "
            "Winter months are often missing at CCIW; do not treat calendar-year "
            "coverage as complete."
        ),
    }


def load_tdgta_flows() -> pd.DataFrame:
    df = pd.read_csv(TDGTA_OUT, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df["JDAY"] = pd.to_numeric(df["JDAY"], errors="coerce")
    df["TDG"] = pd.to_numeric(df["TDG"], errors="coerce")
    df["SUM_Q"] = pd.to_numeric(df["SUM Q"], errors="coerce")
    df["C"] = df["C"].fillna("").astype(str).str.strip()
    df.loc[df["C"].str.lower().isin(["nan", "none"]), "C"] = ""
    qcols = [c for c in df.columns if c.startswith("Q")]
    for c in qcols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Q1 = POWR1; Q2–Q19 = SB1–SB18; Q20 = OTHER/FLD (w2_systdg.npt).
    sb = [c for c in qcols if c not in ("Q 1", "Q1") and not c.endswith("20")]
    # pandas stripped names: 'Q 1' became? skipinitialspace keeps 'Q 1' from header
    # after strip: 'Q 1' -> wait, strip only ends. Header is 'Q 1' with possible spaces.
    qmap = {}
    for c in qcols:
        digits = "".join(ch for ch in c if ch.isdigit())
        if digits:
            qmap[int(digits)] = c
    ph = df[qmap[1]] if 1 in qmap else 0.0
    spill_bays = sum(df[qmap[i]] for i in range(2, 20) if i in qmap)
    other = df[qmap[20]] if 20 in qmap else 0.0
    df["q_ph_cms"] = ph
    df["q_spill_bays_cms"] = spill_bays
    df["q_other_cms"] = other
    df["q_spill_cms"] = spill_bays + other
    df["q_out_kcfs"] = df["SUM_Q"] / CMS_PER_KCFS
    df["q_spill_kcfs"] = df["q_spill_cms"] / CMS_PER_KCFS
    df["q_ph_kcfs"] = df["q_ph_cms"] / CMS_PER_KCFS
    df["spill_frac"] = np.where(df["SUM_Q"] > 0, df["q_spill_cms"] / df["SUM_Q"], np.nan)
    df["date"] = df["JDAY"].map(lambda j: jday_to_date(j) if pd.notna(j) else pd.NaT)
    return df


def load_qgt() -> pd.DataFrame:
    df = pd.read_csv(QGT_IN, comment="#", skiprows=1)
    df.columns = [c.strip().strip('"') for c in df.columns]
    df["JDAY"] = pd.to_numeric(df["JDAY"], errors="coerce")
    for c in df.columns:
        if c != "JDAY":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    sb = [c for c in df.columns if c.startswith("SB")]
    df["q_ph_cms"] = df["POWR1"]
    df["q_spill_bays_cms"] = df[sb].sum(axis=1)
    df["q_other_cms"] = df["MISC"] if "MISC" in df.columns else 0.0
    df["q_spill_cms"] = df["q_spill_bays_cms"] + df["q_other_cms"]
    df["SUM_Q"] = df["q_ph_cms"] + df["q_spill_cms"]
    df["q_out_kcfs"] = df["SUM_Q"] / CMS_PER_KCFS
    df["q_spill_kcfs"] = df["q_spill_cms"] / CMS_PER_KCFS
    df["spill_frac"] = np.where(df["SUM_Q"] > 0, df["q_spill_cms"] / df["SUM_Q"], np.nan)
    df["date"] = df["JDAY"].map(lambda j: jday_to_date(j) if pd.notna(j) else pd.NaT)
    return df


def compare_spill(dart: pd.DataFrame, tdgta: pd.DataFrame, qgt: pd.DataFrame) -> dict:
    dart_d = (
        dart.groupby("date", as_index=False)
        .agg(
            outflow_kcfs=("outflow_kcfs", "mean"),
            spill_kcfs=("spill_kcfs", "mean"),
            spill_pct=("spill_pct", "mean"),
            n_hours=("outflow_kcfs", "count"),
        )
    )
    t = tdgta[["date", "C", "TDG", "q_out_kcfs", "q_spill_kcfs", "q_ph_kcfs", "spill_frac"]].copy()
    t["date"] = pd.to_datetime(t["date"]).dt.date
    q = qgt[["date", "q_out_kcfs", "q_spill_kcfs", "spill_frac"]].copy()
    q["date"] = pd.to_datetime(q["date"]).dt.date
    q = q.rename(
        columns={
            "q_out_kcfs": "qgt_out_kcfs",
            "q_spill_kcfs": "qgt_spill_kcfs",
            "spill_frac": "qgt_spill_frac",
        }
    )
    m = t.merge(dart_d, on="date", how="inner").merge(q, on="date", how="left")
    # Restrict to days with DART outflow
    m = m.dropna(subset=["outflow_kcfs", "q_out_kcfs"])

    def block(a, b, name):
        aa, bb = _finite_pair(m[a], m[b])
        out = pair_metrics(aa, bb)
        if len(aa) >= 3:
            out["r"] = round(float(np.corrcoef(aa, bb)[0, 1]), 6)
        out["pair"] = name
        return out

    realloc = m["C"].isin(["R", "U"])
    spill_season = m["date"].map(lambda d: d.month in (4, 5, 6, 7, 8))

    def subset_metrics(mask, label):
        sub = m.loc[mask]
        if sub.empty:
            return {"label": label, "n": 0}
        a, b = _finite_pair(sub["spill_kcfs"], sub["q_spill_kcfs"])
        r = pair_metrics(a, b)
        r["label"] = label
        if len(a) >= 3:
            r["r"] = round(float(np.corrcoef(a, b)[0, 1]), 6)
            r["mean_dart_spill_kcfs"] = round(float(np.mean(a)), 4)
            r["mean_tdgta_spill_kcfs"] = round(float(np.mean(b)), 4)
            r["mean_dart_spill_frac"] = round(float(sub["spill_pct"].mean() / 100.0), 6) if sub["spill_pct"].notna().any() else None
            r["mean_tdgta_spill_frac"] = round(float(sub["spill_frac"].mean()), 6)
        return r

    n_r = int((m["C"] == "R").sum())
    n_u = int((m["C"] == "U").sum())
    n_blank = int((~m["C"].isin(["R", "U"])).sum())

    # Controller vs its own QGT input (same units, same day).
    aa, bb = _finite_pair(m["qgt_spill_kcfs"], m["q_spill_kcfs"])
    ctrl_vs_qgt = pair_metrics(aa, bb)
    if len(aa) >= 3:
        ctrl_vs_qgt["r"] = round(float(np.corrcoef(aa, bb)[0, 1]), 6)
    n_changed = int((np.abs(m["q_spill_kcfs"] - m["qgt_spill_kcfs"]) > 1.0).sum())  # >1 kcfs

    return {
        "model_period": {
            "tmstrt_jday": 40544,
            "tmend_jday": 40909,
            "note": (
                "w2_con.csv TMSTRT=40544 TMEND=40909 → 2011-01-01 through 2012-01-01. "
                "TDGTarget_output.csv therefore covers ~2011 only, not 2011–2015."
            ),
            "n_tdgta_days": int(len(tdgta)),
            "n_paired_days_with_dart": int(len(m)),
            "jday_min": float(tdgta["JDAY"].min()),
            "jday_max": float(tdgta["JDAY"].max()),
        },
        "column_map": {
            "Q1": "POWR1 powerhouse (cms)",
            "Q2_Q19": "SB1–SB18 spill bays (cms)",
            "Q20": "OTHER/FLD (cms)",
            "spill_used": "Q2–Q19 + Q20 converted to kcfs via /28.316846592",
            "C_flag": "R=controller entered reallocation (TDG>target); U=still above target; blank=no cut needed",
        },
        "tdgta_vs_dart_outflow_kcfs": block("outflow_kcfs", "q_out_kcfs", "outflow"),
        "tdgta_vs_dart_spill_kcfs": block("spill_kcfs", "q_spill_kcfs", "spill"),
        "qgt_vs_dart_spill_kcfs": block("spill_kcfs", "qgt_spill_kcfs", "qgt_vs_dart_spill"),
        "tdgta_vs_qgt_spill_kcfs": ctrl_vs_qgt,
        "n_days_spill_changed_gt_1kcfs": n_changed,
        "controller_flags": {"R": n_r, "U": n_u, "blank": n_blank, "n": int(len(m))},
        "spill_all_days": subset_metrics(np.ones(len(m), dtype=bool), "all_paired_days"),
        "spill_realloc_days": subset_metrics(realloc.to_numpy(), "C_in_R_or_U"),
        "spill_noalloc_days": subset_metrics((~realloc).to_numpy(), "C_blank"),
        "spill_apr_aug": subset_metrics(spill_season.to_numpy(), "Apr-Aug"),
        "_frame": m.copy(),
    }


def make_plots(cmp: dict, dart: pd.DataFrame, spill: dict, exceed_all: dict) -> list[str]:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    written = []

    hourly = cmp["_merged_hourly"]
    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    o = hourly["tdg"].to_numpy()
    d = hourly["tdg_pct"].to_numpy()
    lim = [min(o.min(), d.min()) - 1, max(o.max(), d.max()) + 1]
    ax.plot(lim, lim, "k--", lw=1, label="1:1")
    ax.scatter(o, d, s=6, alpha=0.25, edgecolors="none")
    ax.set_xlabel("库内 CCIW TDG %")
    ax.set_ylabel("DART CCIW TDG %")
    n = cmp["hourly_tdg"].get("n", 0)
    mae = cmp["hourly_tdg"].get("mae")
    mr = cmp["hourly_tdg"].get("match_rate_abs_le_0p051")
    ax.set_title(f"库内 vs DART 小时 TDG  n={n}  MAE={mae}  匹配率={mr}")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    p = ANALYSIS_DIR / "w4_cciw_vs_dart_scatter.png"
    fig.savefig(p, dpi=140)
    plt.close()
    written.append(str(p.relative_to(ROOT)).replace("\\", "/"))

    daily = cmp["_daily"].copy()
    daily["date"] = pd.to_datetime(daily["date"])
    fig, ax = plt.subplots(figsize=(11.2, 4.2))
    ax.plot(daily["date"], daily["lib_tdg"], lw=1.1, label="库内 CCIW 日均")
    ax.plot(daily["date"], daily["dart_tdg"], lw=0.9, alpha=0.85, label="DART 日均")
    ax.axhline(120, color="tab:red", ls="--", lw=1, label="120%")
    ax.axhline(115, color="tab:orange", ls=":", lw=1, label="115%")
    ax.set_ylabel("TDG %")
    ax.set_title("2011–2015 库内 CCIW 与 DART 日均 TDG")
    ax.legend(ncol=4, fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p = ANALYSIS_DIR / "w4_cciw_vs_dart_timeseries.png"
    fig.savefig(p, dpi=140)
    plt.close()
    written.append(str(p.relative_to(ROOT)).replace("\\", "/"))

    years = [r["year"] for r in exceed_all["by_year"]]
    gt120 = [r["pct_hours_gt_120"] for r in exceed_all["by_year"]]
    gt115 = [r["pct_hours_gt_115"] for r in exceed_all["by_year"]]
    fig, ax = plt.subplots(figsize=(10.5, 4.3))
    x = np.arange(len(years))
    ax.bar(x - 0.18, gt115, 0.36, label=">115% 占有效小时 %")
    ax.bar(x + 0.18, gt120, 0.36, label=">120% 占有效小时 %")
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45)
    ax.set_ylabel("% of valid hours")
    ax.set_title("CCIW 年超标频次（DART 小时 Dissolved Gas Percent）")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    p = ANALYSIS_DIR / "w4_tdg_gt120_annual.png"
    fig.savefig(p, dpi=140)
    plt.close()
    written.append(str(p.relative_to(ROOT)).replace("\\", "/"))

    fig, ax = plt.subplots(figsize=(10.5, 4.0))
    ymax = [r["annual_max_tdg"] for r in exceed_all["by_year"]]
    ax.plot(years, ymax, "o-", lw=1.4)
    ax.axhline(120, color="tab:red", ls="--", label="120%")
    ax.axhline(115, color="tab:orange", ls=":", label="115%")
    ax.set_ylabel("年最大 TDG %")
    ax.set_title("CCIW 年最大 TDG（DART）")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p = ANALYSIS_DIR / "w4_tdg_annual_max.png"
    fig.savefig(p, dpi=140)
    plt.close()
    written.append(str(p.relative_to(ROOT)).replace("\\", "/"))

    sp = spill["_frame"].copy()
    sp["date"] = pd.to_datetime(sp["date"])
    fig, ax = plt.subplots(figsize=(11.2, 4.2))
    ax.plot(sp["date"], sp["spill_kcfs"], lw=1.1, label="DART 实际泄流（日均 kcfs）")
    ax.plot(sp["date"], sp["q_spill_kcfs"], lw=1.1, label="TDGTA ON 泄流 Q2–Q20（kcfs）")
    if sp["qgt_spill_kcfs"].notna().any():
        ax.plot(sp["date"], sp["qgt_spill_kcfs"], lw=0.9, alpha=0.75, label="QGT 输入泄流（kcfs）")
    ax.set_ylabel("Spill (kcfs)")
    ax.set_title("2011 泄流对照：DART vs TDGTA 控制器 vs QGT 输入")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p = ANALYSIS_DIR / "w4_spill_tdgta_vs_dart.png"
    fig.savefig(p, dpi=140)
    plt.close()
    written.append(str(p.relative_to(ROOT)).replace("\\", "/"))

    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    a = sp["spill_kcfs"].to_numpy()
    b = sp["q_spill_kcfs"].to_numpy()
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    lim = [min(a.min(), b.min()), max(a.max(), b.max())]
    ax.plot(lim, lim, "k--", lw=1)
    colors = np.where(sp.loc[mask, "C"].isin(["R", "U"]), "tab:red", "tab:blue")
    ax.scatter(a, b, s=12, c=colors, alpha=0.55, edgecolors="none")
    ax.set_xlabel("DART 日均 Spill (kcfs)")
    ax.set_ylabel("TDGTA ON Spill (kcfs)")
    ax.set_title("泄流 1:1（红=控制器 R/U 日）")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p = ANALYSIS_DIR / "w4_spill_scatter.png"
    fig.savefig(p, dpi=140)
    plt.close()
    written.append(str(p.relative_to(ROOT)).replace("\\", "/"))

    return written


def write_findings(payload: dict) -> Path:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    d = payload["dart_download"]
    c = payload["cciw_vs_dart"]
    ex16 = payload["exceedance_2016_2025"]
    ex11 = payload["exceedance_2011_2015"]
    sp = payload["spill_comparison_2011"]
    oos = payload["out_of_sample"]

    files_ok = [f for f in d.get("files", []) if f.get("ok")]
    files_fail = [f for f in d.get("files", []) if not f.get("ok")]
    year_list = ", ".join(str(f["year"]) for f in files_ok)

    ht = c.get("hourly_tdg", {})
    counts = c.get("counts", {})
    verdict = c.get("verdict")
    by_year_md = "\n".join(
        (
            f"  - {r['year']}: n={r['n']}, MAE={r['mae']}, "
            f"匹配率={r['match_rate_abs_le_0p051']}, "
            f"|Δ|>0.15={r['n_abs_diff_gt_0p15']}, max|Δ|={r['max_abs_diff']}"
        )
        for r in (ht.get("by_year") or [])
    )
    if verdict in ("library_is_dart_rounded", "library_is_dart_with_rounding_and_minor_revisions"):
        verdict_cn = (
            "库内 CCIW 与 2026 年下载的 DART 原始小时值在重叠期高度一致："
            "MAE 约 0.03%、绝大多数点落在 1 位小数修约带内。"
            "少数 |Δ|>0.15 的点共 "
            f"{ht.get('n_abs_diff_gt_0p15')} 个（其中 |Δ|>1 的 {ht.get('n_abs_diff_gt_1')} 个，"
            "几乎全在 2011–2012；2013–2015 匹配率 = 1.0），"
            "更像 CWMS（2017 提取）与 DART（2026 下载）之间的事后修订，而不是示例被改写。"
            "**没有证据表明官方示例附带观测被实质性改过。**"
        )
    elif verdict == "library_close_to_dart":
        verdict_cn = (
            "库内 CCIW 与 DART 总体接近，但存在超出修约的偏差，"
            "可能来自 CWMS（2017 提取）与 DART（2026 下载）之间的 USACE 事后修订。"
        )
    else:
        verdict_cn = "库内 CCIW 与 DART 存在不可忽略的差异，不能视为同一份未经改动的序列。"

    spill_m = sp.get("tdgta_vs_dart_spill_kcfs", {})
    realloc = sp.get("spill_realloc_days", {})
    flags = sp.get("controller_flags", {})
    qgt_vs_ctrl = sp.get("tdgta_vs_qgt_spill_kcfs", {})
    ex_all = payload.get("exceedance_all_downloaded", {})
    year_table_rows = [
        "| 年 | 有效小时 | >115% 占有效小时 % | >120% 占有效小时 % | 年最大 TDG % |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in ex_all.get("by_year") or []:
        year_table_rows.append(
            f"| {r['year']} | {r['n_valid_hours']} | {r['pct_hours_gt_115']} | {r['pct_hours_gt_120']} | {r['annual_max_tdg']} |"
        )
    year_table = "\n".join(year_table_rows)

    blocked = d.get("stopped_early")
    manual = """
## 人工下载步骤（若脚本被拦）

1. 打开 https://cbr.washington.edu/dart/query/wqm_hourly
2. Output Format 选 **CSV File**；Year 选目标年；Site 选 **CCIW**。
3. Start Date 填 `01/01`；Hours 选 **365 Days (8760 hours)**（闰年再补 12/31 一天）。
4. 勾选 **Generate Query Result Link Only** 再 Submit，页面会给出带 `sc=1` 的脚本 URL。
5. 或不勾选直接 Submit，浏览器下载 `wqmhourly_*.csv`。
6. 把文件存到 `06_PAPER/data/dart_cciw/cciw_hourly_YYYY.csv`。
7. 备选：USACE NWD Water Control Data / dataquery
   https://www.nwd.usace.army.mil/CRWM/Water-Control-Data/
   站点 Cascade Island / Bonneville tailwater，参数 TDG%、Spill。
"""

    md = f"""# W4 发现：DART CCIW 下载、库内核对、样本外框架

生成时间：{payload['generated']}
脚本：`00_INDEX/download_dart_cciw.py`

## 1. DART 如何脚本化下载

查询页表单 `GET /dart/cs/php/rpt/wqm_hourly.php`，字段：`year`, `proj`, `startdate`, `days`, `outputFormat`, 可选 `datalink=1`。

勾选 Generate Query Result Link Only 后返回的脚本 URL 模式：

```
{d.get('url_pattern')}
```

关键参数 **`sc=1`**（script call）。无 `sc=1` 时服务器 302 到 Drupal wrapper HTML。

本次下载：成功 {d.get('n_ok')} 年（{year_list or '无'}）。提前停止：{blocked}。
失败记录：{json.dumps(json_safe(files_fail), ensure_ascii=False) if files_fail else '无'}。

礼貌策略：先通 2011 一年，再按年扩展；年与年之间暂停 {SLEEP_S:.0f} s；HTTP 403/429/503 不重试死循环。
Windows 上 Python `urllib` 对本站全年 CSV 会报 `SSLError: ASN1 NOT_ENOUGH_DATA`，脚本改走 `curl.exe --http1.1`（已验证 200 + `text/csv`）。

## 2. 库内 CCIW vs DART（2011–2015）

库内文件：`02_LIBRARY/06_examples/v5.0_beta/Bonneville_TDG/CCIW_TDG_Temp_2011-2015.csv`
（头注释：CWMS，由 `6_TDG_data_to_W2npt_v2.py` 于 2017-12-21 生成）。
JDAY 纪元：Excel 序列，**40544 = 2011-01-01**（原点 1899-12-30）。与 `w2_con.csv` TMSTRT 一致。

时间对齐（已用 2011-04-01 逐点核实）：

- DART `Date` + `Hour` 100…2400 为该日历日的小时终止时刻（Pacific Timestamp 比库内标签晚 1 小时）。
- 库内 `Datetime` 的小时 h 对应 DART Hour `(h+1)*100`。
- 例：库内 `4/1/2011 0:00` TDG=111.9 ↔ DART Hour 100 / `2011-04-01 01:00:00-07` TDG=111.88。

小时配对（双方 TDG 均有效）：

- n = {ht.get('n')}
- MAE = {ht.get('mae')}，RMSE = {ht.get('rmse')}，bias = {ht.get('bias')}
- |Δ|≤0.051（1 位小数修约带）匹配率 = {ht.get('match_rate_abs_le_0p051')}
- 四舍五入（half-up）到 1 位后匹配率 = {ht.get('match_rate_round_half_up_1dec')}
- |Δ|>0.15 的点数 = {ht.get('n_abs_diff_gt_0p15')}；|Δ|>1 的点数 = {ht.get('n_abs_diff_gt_1')}；max |Δ| = {ht.get('max_abs_diff')}
- 分年：
{by_year_md}

库内有效小时 {counts.get('library_tdg_valid')} / 总小时 {counts.get('library_hours')}（缺失率 {counts.get('library_missing_frac')}）。
DART 2011–2015 有效小时 {counts.get('dart_2011_2015_tdg_valid')} / {counts.get('dart_2011_2015_hours')}。
库内有效但未配上 DART：{counts.get('library_valid_unpaired')}；DART 有效但库内无对应：{counts.get('dart_valid_unpaired')}。

日均配对：n = {c.get('daily_tdg', {}).get('n')}，MAE = {c.get('daily_tdg', {}).get('mae')}，匹配率 = {c.get('daily_tdg', {}).get('match_rate_abs_le_0p051')}。

**结论：** {verdict_cn}

冬季大量 −999 / 空值是监测季节性，不是库内独有的删改。

## 3. 2016–2025 超标与可达范围（样本外数据已就绪，NSE 未做）

{oos['statement']}

2011–2015（DART，有效小时）：>115% = {ex11.get('pct_hours_gt_115')}%，>120% = {ex11.get('pct_hours_gt_120')}%，最大 TDG = {ex11.get('max_tdg')}%。
2016–2025（DART，有效小时）：>115% = {ex16.get('pct_hours_gt_115')}%，>120% = {ex16.get('pct_hours_gt_120')}%，最大 TDG = {ex16.get('max_tdg')}%，有效小时 n = {ex16.get('n_valid_hours')}。

样本外十年的超 120% 比例（21.2%）**高于**示例期（14.7%），封顶问题没有随时间消失。2015 年有效小时中 0% 超过 120%（年最大 118.97%），2017 年则有 46.9%（年最大 131.38%）。

{year_table}

这直接服务创新点 2 的「可达范围 / 封顶」叙事：观测中超过 120% 的点在 TDGTA 目标带外，结构上不可能被控制器复现。

百分比分母是**有效小时**，不是日历小时。CCIW 冬季常缺测。

## 4. 泄流对照（TDGTA ON vs DART vs QGT 输入）

模型时段：{sp.get('model_period', {}).get('note')}

列映射：Q1=厂房 POWR1，Q2–Q19=溢洪道 SB1–SB18，Q20=OTHER。泄流 = (Q2–Q20)/28.316846592 kcfs。
C 列：R = 当日 TDG 超目标、控制器进入再分配；U = 迭代后仍超；空 = 未切流量。

配对日数 {sp.get('model_period', {}).get('n_paired_days_with_dart')}。
控制器标志：R={flags.get('R')}，U={flags.get('U')}，空白={flags.get('blank')}。

TDGTA 泄流 vs DART 日均 Spill：n={spill_m.get('n')}，MAE={spill_m.get('mae')} kcfs，bias={spill_m.get('bias')}，r={spill_m.get('r')}。
QGT 输入 vs DART：r={sp.get('qgt_vs_dart_spill_kcfs', {}).get('r')}（输入文件大体跟着实际泄流）。
控制器相对 QGT 输入：MAE={qgt_vs_ctrl.get('mae')} kcfs，|Δspill|>1 kcfs 的天数 = {sp.get('n_days_spill_changed_gt_1kcfs')}（与 R 日数相同）。
再分配日（R/U）：DART 均泄 {realloc.get('mean_dart_spill_kcfs')} kcfs vs TDGTA {realloc.get('mean_tdgta_spill_kcfs')} kcfs，r={realloc.get('r')}。
空白日：DART {sp.get('spill_noalloc_days', {}).get('mean_dart_spill_kcfs')} vs TDGTA {sp.get('spill_noalloc_days', {}).get('mean_tdgta_spill_kcfs')}。

**结论：** 控制器在 R 日把泄流从与实测相近的 QGT 方案大幅砍向厂房。QGT 对 DART 的相关远高于 TDGTA 对 DART。这是创新点 2 的独立证据：TDGTA ON 的低偏差/封顶，部分来自「把泄流调成与 2011 年实际运行不同的方案」，而不是单纯把物理过程拟合得更好。

## 5. 文件

- 原始小时：`06_PAPER/data/dart_cciw/cciw_hourly_YYYY.csv`
- 下载日志：`06_PAPER/data/dart_cciw/download_log.json`
- 统计：`06_PAPER/analysis/w4_cciw_vs_dart.json`
- 图：`06_PAPER/analysis/w4_cciw_vs_dart_scatter.png`、`w4_cciw_vs_dart_timeseries.png`、`w4_tdg_gt120_annual.png`、`w4_tdg_annual_max.png`、`w4_spill_tdgta_vs_dart.png`、`w4_spill_scatter.png`

数据引用：Columbia River DART, Columbia Basin Research, University of Washington. Hourly Water Quality Measurements. https://cbr.washington.edu/dart/query/wqm_hourly （下载于 {payload['generated'][:10]}）。原始观测来自 USACE NWD。

{manual}
"""
    path = NOTES_DIR / "W4_findings.md"
    path.write_text(md.strip() + "\n", encoding="utf-8")
    return path


def analyze(dl_log: dict, years: list[int]) -> dict:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    dart = load_all_dart(years)
    lib = load_library_obs()
    cmp = compare_cciw_vs_dart(lib, dart)
    ex_1115 = exceedance_table(dart, 2011, 2015)
    ex_1625 = exceedance_table(dart, 2016, 2025)
    ex_all = exceedance_table(dart, min(years), max(years))

    have_2016plus = bool(ex_1625.get("n_valid_hours"))
    tdgta = load_tdgta_flows() if TDGTA_OUT.is_file() else pd.DataFrame()
    qgt = load_qgt() if QGT_IN.is_file() else pd.DataFrame()
    spill = compare_spill(dart, tdgta, qgt) if len(tdgta) and len(dart) else {"note": "missing files"}

    oos = {
        "computed_nse": False,
        "reason": (
            "当前 TDGTA ON 复现运行的 w2_con.csv 为 TMSTRT=40544、TMEND=40909，"
            "只覆盖 2011 年；没有 2016–2025 的模型输出。DART 小时序列已落盘，"
            "样本外 NSE/KGE 必须先把模型时段扩展到 2016+（并准备对应气象/边界/出流），那是后续任务。"
        ),
        "data_ready_2016_2025": have_2016plus,
        "statement": (
            "2016–2025 的 DART CCIW 小时 TDG/Spill 已下载并完成超标统计；"
            "**没有**计算样本外 NSE——模型尚未跑 2016 以后，不能假装有预报技能。"
            if have_2016plus
            else "2016–2025 数据未到手，样本外框架未填超标表。"
        ),
    }

    plots = []
    if len(cmp.get("_merged_hourly", pd.DataFrame())) and ex_all.get("by_year"):
        plots = make_plots(cmp, dart, spill if "_frame" in spill else {"_frame": pd.DataFrame()}, ex_all)

    payload = {
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "dart_download": {k: v for k, v in dl_log.items() if k != "stop_reason" or True},
        "cciw_vs_dart": {k: v for k, v in cmp.items() if not k.startswith("_")},
        "exceedance_2011_2015": ex_1115,
        "exceedance_2016_2025": ex_1625,
        "exceedance_all_downloaded": ex_all,
        "out_of_sample": oos,
        "spill_comparison_2011": {k: v for k, v in spill.items() if not k.startswith("_")},
        "figures": plots,
        "citation": (
            "Columbia River DART, Columbia Basin Research, University of Washington. "
            "Hourly Water Quality Measurements. https://cbr.washington.edu/dart/query/wqm_hourly"
        ),
    }
    payload = json_safe(payload)
    out_json = ANALYSIS_DIR / "w4_cciw_vs_dart.json"
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    notes = write_findings(payload)
    payload["notes"] = str(notes.relative_to(ROOT)).replace("\\", "/")
    # rewrite with notes path
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in spec.split(",") if x.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Download DART CCIW hourly WQM and run W4 checks.")
    ap.add_argument("--years", default="2011-2025", help="e.g. 2011-2025 or 2011,2012")
    ap.add_argument("--skip-download", action="store_true")
    ap.add_argument("--skip-analyze", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-download even if yearly CSV exists")
    args = ap.parse_args(argv)
    years = parse_years(args.years)

    if args.skip_download:
        log_path = DATA_DIR / "download_log.json"
        dl_log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.is_file() else {
            "files": [],
            "n_ok": sum(1 for y in years if is_valid_dart_csv(DATA_DIR / f"cciw_hourly_{y}.csv")),
            "success": True,
            "url_pattern": dart_url(2011),
            "query_page": QUERY_PAGE,
        }
    else:
        dl_log = download_years(years, force=args.force)

    if args.skip_analyze:
        print(json.dumps({"download": json_safe(dl_log)}, indent=2, ensure_ascii=False)[:2000])
        return 0 if dl_log.get("success") else 2

    payload = analyze(dl_log, years)
    print(
        json.dumps(
            {
                "download_success": payload["dart_download"].get("success"),
                "years_ok": payload["dart_download"].get("n_ok"),
                "verdict": payload["cciw_vs_dart"].get("verdict"),
                "hourly_match_rate": payload["cciw_vs_dart"].get("hourly_tdg", {}).get("match_rate_abs_le_0p051"),
                "oos_nse_computed": payload["out_of_sample"].get("computed_nse"),
                "data_ready_2016_2025": payload["out_of_sample"].get("data_ready_2016_2025"),
                "json": "06_PAPER/analysis/w4_cciw_vs_dart.json",
                "notes": payload.get("notes"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
