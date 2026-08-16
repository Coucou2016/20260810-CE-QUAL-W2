#!/usr/bin/env python3
"""Numerical Health Record (NHR) parser for CE-QUAL-W2 runs.

Reads w2.wrn / w2.err / *_snp*.opt / tsr_*.csv (and w2_con.csv for DLTMIN /
DLTMAX schedule) and emits a structured JSON record.

Primary signals (source-backed):
  - Negative surface layer thickness + DLT rollback to DLTMIN
    (w2_4_win.f90 ~L1415-1424, L1483-1488)
  - Add / Subtract layer events (layeraddsub.F90 L261-265, L773-775)
  - Low-water guard (layeraddsub.F90 L245-246)
  - SNP runtime: NIT, NV (timestep violations), average DLT
"""
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
REPRO = ROOT / "05_REPRO_RUNS"

RE_NEG = re.compile(r"Negative surface layer thickness in segment\s+(\d+)", re.I)
RE_REDUCED = re.compile(
    r"time step reduced to\s+([0-9]*\.?[0-9]+)\s+s on day\s+([0-9]*\.?[0-9]+)\s+at iteration\s+(\d+)",
    re.I,
)
RE_COMP_SEG = re.compile(
    r"Computational warning at Julian day\s*=\s*([0-9]*\.?[0-9]+)\s+at segment\s+(\d+)",
    re.I,
)
RE_Z_H1 = re.compile(
    r"timestep\s*=\s*([0-9eE.+-]+)\s+water surface deviation\s*\[Z\]\s*=\s*([0-9eE.+-]+)\s*m"
    r"\s+layer thickness\s*=\s*([0-9eE.+-]+)\s*m",
    re.I,
)
RE_DLTMIN_SET = re.compile(
    r"timestep\s*=\s*([0-9eE.+-]+)\s+sec:\s*DLT\s*<\s*DLTMIN set DLT=DLTMIN",
    re.I,
)
RE_COMP_DAY = re.compile(r"Computational warning at Julian day\s*=\s*([0-9]*\.?[0-9]+)", re.I)
RE_ADD = re.compile(
    r"Add layer\s+(\d+)\s+at Julian day\s*=\s*([0-9]*\.?[0-9]+)\s+NIT\s*=\s*(\d+)\s+"
    r"IZMIN\s*=\s*(\d+)\s+Waterbody\s*=\s*(\d+)",
    re.I,
)
RE_SUB = re.compile(
    r"Subtract layer\s+(\d+)\s+at Julian day\s*=\s*([0-9]*\.?[0-9]+)\s+NIT\s*=\s*(\d+)\s+"
    r"IZMIN\s*=\s*(\d+)\s+WaterBody\s*=\s*(\d+)",
    re.I,
)
RE_LOW = re.compile(
    r"Low water in segment\s+(\d+)\s+water surface deviation\s*=\s*([0-9eE.+-]+)\s+at day\s+([0-9]*\.?[0-9]+)",
    re.I,
)
RE_WS_ABOVE = re.compile(
    r"Water surface is above the top of layer 2 in segment\s+(\d+)\s+at day\s+([0-9]*\.?[0-9]+)",
    re.I,
)
RE_H1H2 = re.compile(
    r"\|h1-h2\|/h2>0\.35 on Julian day\s*=\s*([0-9]*\.?[0-9]+)\s+at segment\s+(\d+).*?timestep DLT=\s*([0-9eE.+-]+)",
    re.I | re.S,
)
RE_UNSTABLE = re.compile(r"Unstable water surface elevation on day\s+([0-9]*\.?[0-9]+)", re.I)
RE_SNP_NIT = re.compile(r"Total iterations\s*=\s*(\d+)", re.I)
RE_SNP_NV = re.compile(r"# of violations\s*=\s*(\d+)", re.I)
RE_SNP_PCT = re.compile(r"% violations\s*=\s*([0-9]*\.?[0-9]+)", re.I)
RE_SNP_AVG = re.compile(r"Average timestep\s*=\s*(\d+)\s*sec", re.I)
RE_SNP_SIM = re.compile(r"Simulation time\s*=\s*(\d+)\s*days\s+([0-9]*\.?[0-9]+)\s*hours", re.I)
RE_SNP_TERM = re.compile(r"Normal termination", re.I)
RE_SNP_ERR = re.compile(r"Runtime error", re.I)


def _f(x: str) -> float:
    return float(x)


def _i(x: str) -> int:
    return int(x)


def _nonempty_csv_fields(line: str) -> list[str]:
    return [p.strip() for p in line.split(",") if p.strip() != ""]


def parse_dlt_schedule(con: Path) -> dict[str, Any]:
    """Parse NDLT / DLTMIN / DLTD / DLTMAX / DLTF / TMEND from w2_con.csv."""
    out: dict[str, Any] = {
        "tmstrt": None,
        "tmend": None,
        "ndlt": None,
        "dltmin": None,
        "dltinter": None,
        "dltd": [],
        "dltmax": [],
        "dltf": [],
    }
    if not con.exists():
        return out
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines()
    for i, line in enumerate(lines):
        key = line.lstrip().split(",")[0].strip().upper()
        if key == "TMSTRT" and i + 1 < len(lines):
            vals = _nonempty_csv_fields(lines[i + 1])
            if len(vals) >= 2:
                try:
                    out["tmstrt"] = float(vals[0])
                    out["tmend"] = float(vals[1])
                except ValueError:
                    pass
        elif key == "NDLT" and i + 1 < len(lines):
            vals = _nonempty_csv_fields(lines[i + 1])
            if len(vals) >= 2:
                try:
                    out["ndlt"] = int(float(vals[0]))
                    out["dltmin"] = float(vals[1])
                except ValueError:
                    pass
                if len(vals) >= 3:
                    out["dltinter"] = vals[2]
        elif key == "DLTD" and i + 1 < len(lines) and not out["dltd"]:
            vals = _nonempty_csv_fields(lines[i + 1])
            try:
                out["dltd"] = [float(v) for v in vals]
            except ValueError:
                pass
        elif key == "DLTMAX" and i + 1 < len(lines) and not out["dltmax"]:
            vals = _nonempty_csv_fields(lines[i + 1])
            try:
                out["dltmax"] = [float(v) for v in vals]
            except ValueError:
                pass
        elif key == "DLTF" and i + 1 < len(lines) and not out["dltf"]:
            vals = _nonempty_csv_fields(lines[i + 1])
            try:
                out["dltf"] = [float(v) for v in vals]
            except ValueError:
                pass
    ndlt = out["ndlt"]
    if isinstance(ndlt, int) and ndlt > 0:
        for k in ("dltd", "dltmax", "dltf"):
            seq = out[k]
            if isinstance(seq, list) and len(seq) > ndlt:
                out[k] = seq[:ndlt]
    windows = []
    dltd = out["dltd"] or []
    dltmax = out["dltmax"] or []
    dltf = out["dltf"] or []
    n = min(len(dltd), len(dltmax), len(dltf)) if dltd else 0
    for j in range(n):
        end = dltd[j + 1] if j + 1 < n else out["tmend"]
        windows.append(
            {
                "index": j,
                "jday_start": dltd[j],
                "jday_end": end,
                "dltmax": dltmax[j],
                "dltf": dltf[j],
            }
        )
    out["windows"] = windows
    return out


def parse_wrn(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    neg_events: list[dict[str, Any]] = []
    reduced_events: list[dict[str, Any]] = []
    dltmin_set_events: list[dict[str, Any]] = []
    pending_comp: dict[str, Any] | None = None

    for i, line in enumerate(lines):
        m_comp = RE_COMP_SEG.search(line)
        if m_comp:
            pending_comp = {"jday": _f(m_comp.group(1)), "segment": _i(m_comp.group(2))}
            if i + 1 < len(lines):
                mz = RE_Z_H1.search(lines[i + 1])
                if mz:
                    pending_comp["dlt_at_warning"] = _f(mz.group(1))
                    pending_comp["z_m"] = _f(mz.group(2))
                    pending_comp["h1_m"] = _f(mz.group(3))
            continue
        m_neg = RE_NEG.search(line)
        if m_neg:
            ev = {"segment": _i(m_neg.group(1))}
            if pending_comp:
                ev.update(pending_comp)
            if i + 1 < len(lines):
                mr = RE_REDUCED.search(lines[i + 1])
                if mr:
                    ev["reduced_to_s"] = _f(mr.group(1))
                    ev["jday"] = _f(mr.group(2))
                    ev["nit"] = _i(mr.group(3))
            neg_events.append(ev)
            pending_comp = None
            continue
        m_red = RE_REDUCED.search(line)
        if m_red:
            reduced_events.append(
                {
                    "reduced_to_s": _f(m_red.group(1)),
                    "jday": _f(m_red.group(2)),
                    "nit": _i(m_red.group(3)),
                }
            )
            continue
        m_set = RE_DLTMIN_SET.search(line)
        if m_set:
            jday = None
            if i > 0:
                md = RE_COMP_DAY.search(lines[i - 1])
                if md:
                    jday = _f(md.group(1))
            dltmin_set_events.append({"dlt_before_s": _f(m_set.group(1)), "jday": jday})

    add_events = [
        {
            "layer": _i(m.group(1)),
            "jday": _f(m.group(2)),
            "nit": _i(m.group(3)),
            "izmin": _i(m.group(4)),
            "waterbody": _i(m.group(5)),
        }
        for m in RE_ADD.finditer(text)
    ]
    sub_events = [
        {
            "layer": _i(m.group(1)),
            "jday": _f(m.group(2)),
            "nit": _i(m.group(3)),
            "izmin": _i(m.group(4)),
            "waterbody": _i(m.group(5)),
        }
        for m in RE_SUB.finditer(text)
    ]
    low_events = [
        {"segment": _i(m.group(1)), "z_m": _f(m.group(2)), "jday": _f(m.group(3))}
        for m in RE_LOW.finditer(text)
    ]
    ws_events = [
        {"segment": _i(m.group(1)), "jday": _f(m.group(2))} for m in RE_WS_ABOVE.finditer(text)
    ]
    h1h2 = [
        {"jday": _f(m.group(1)), "segment": _i(m.group(2)), "dlt_s": _f(m.group(3))}
        for m in RE_H1H2.finditer(text)
    ]

    return {
        "neg_surface_thickness_count": len(neg_events),
        "neg_surface_thickness_events": neg_events,
        "add_layer_count": len(add_events),
        "add_layer_jdays": [e["jday"] for e in add_events],
        "add_layer_events": add_events,
        "subtract_layer_count": len(sub_events),
        "subtract_layer_jdays": [e["jday"] for e in sub_events],
        "subtract_layer_events": sub_events,
        "low_water_count": len(low_events),
        "low_water_events": low_events,
        "ws_above_layer2_count": len(ws_events),
        "ws_above_layer2_events": ws_events,
        "h1h2_gt_035_count": len(h1h2),
        "h1h2_gt_035_events": h1h2,
        "dltmin_reduced_count": len(reduced_events) if reduced_events else len(neg_events),
        "dltmin_reduced_events": reduced_events or [
            {k: e[k] for k in ("jday", "nit", "reduced_to_s") if k in e} for e in neg_events
        ],
        "dltmin_set_count": len(dltmin_set_events),
        "dltmin_set_events": dltmin_set_events,
        "dltmin_hint_count": len(neg_events) + len(dltmin_set_events),
    }


def parse_err(text: str) -> dict[str, Any]:
    if not text.strip():
        return {"present": False, "unstable_ws_count": 0, "text_head": ""}
    days = [_f(m.group(1)) for m in RE_UNSTABLE.finditer(text)]
    return {
        "present": True,
        "unstable_ws_count": len(days),
        "unstable_ws_jdays": days,
        "text_head": text[:2000],
    }


def _tail_text(path: Path, max_bytes: int = 80_000) -> str:
    size = path.stat().st_size
    with path.open("rb") as f:
        if size > max_bytes:
            f.seek(-max_bytes, 2)
        raw = f.read()
    return raw.decode("utf-8", errors="ignore")


def parse_snp_runtime(case_dir: Path) -> dict[str, Any]:
    snps = sorted(case_dir.glob("*snp*.opt")) + sorted(case_dir.glob("snp*.opt"))
    # de-dup
    seen: set[Path] = set()
    files: list[Path] = []
    for p in snps:
        if p not in seen:
            seen.add(p)
            files.append(p)
    if not files:
        return {"present": False}
    # Prefer the largest (main waterbody)
    path = max(files, key=lambda p: p.stat().st_size)
    tail = _tail_text(path)
    out: dict[str, Any] = {
        "present": True,
        "file": path.name,
        "bytes": path.stat().st_size,
        "normal_termination": bool(RE_SNP_TERM.search(tail)),
        "runtime_error": bool(RE_SNP_ERR.search(tail)),
    }
    m = RE_SNP_NIT.search(tail)
    if m:
        out["total_iterations"] = int(m.group(1))
    m = RE_SNP_NV.search(tail)
    if m:
        out["n_violations"] = int(m.group(1))
    m = RE_SNP_PCT.search(tail)
    if m:
        out["pct_violations"] = float(m.group(1))
    m = RE_SNP_AVG.search(tail)
    if m:
        out["avg_timestep_s"] = int(m.group(1))
    m = RE_SNP_SIM.search(tail)
    if m:
        out["sim_days"] = int(m.group(1)) + float(m.group(2)) / 24.0
    # Layer events also echo into SNP when SNAPSHOT is on
    add_n = len(list(RE_ADD.finditer(tail)))
    sub_n = len(list(RE_SUB.finditer(tail)))
    # Tail-only is incomplete for layer counts; note that
    out["tail_add_layer_count"] = add_n
    out["tail_subtract_layer_count"] = sub_n
    return out


def parse_tsr_dlt(case_dir: Path, dltmin: float | None, window: tuple[float, float] | None = None) -> dict[str, Any]:
    files = sorted(case_dir.glob("tsr_*.csv"))
    if not files:
        return {"present": False, "last_jday": None}
    path = files[0]
    jdays: list[float] = []
    dlts: list[float] = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        header = None
        dlt_col = 1
        jday_col = 0
        for raw in f:
            s = raw.strip()
            if not s:
                continue
            parts = [p.strip() for p in s.split(",")]
            if header is None:
                header = [p.upper() for p in parts]
                for k, name in enumerate(header):
                    if name.startswith("JDAY"):
                        jday_col = k
                    if name.startswith("DLT"):
                        dlt_col = k
                if header[0].startswith("JDAY"):
                    continue
            try:
                j = float(parts[jday_col])
                d = float(parts[dlt_col])
            except (ValueError, IndexError):
                continue
            jdays.append(j)
            dlts.append(d)
    if not jdays:
        return {"present": True, "file": path.name, "n_samples": 0, "last_jday": None}

    def _stats(js: list[float], ds: list[float], label: str) -> dict[str, Any]:
        if not ds:
            return {"label": label, "n_samples": 0}
        n_near = 0
        if dltmin is not None and dltmin > 0:
            thresh = max(dltmin * 1.5, dltmin + 1e-6)
            n_near = sum(1 for d in ds if d <= thresh)
        return {
            "label": label,
            "n_samples": len(ds),
            "jday_first": js[0],
            "jday_last": js[-1],
            "dlt_min_s": min(ds),
            "dlt_max_s": max(ds),
            "dlt_mean_s": sum(ds) / len(ds),
            "n_samples_near_dltmin": n_near,
            "frac_samples_near_dltmin": n_near / len(ds),
        }

    out: dict[str, Any] = {
        "present": True,
        "file": path.name,
        "last_jday": jdays[-1],
        "full": _stats(jdays, dlts, "full"),
    }
    if window is not None:
        lo, hi = window
        js_w = []
        ds_w = []
        for j, d in zip(jdays, dlts):
            if lo <= j < hi:
                js_w.append(j)
                ds_w.append(d)
        out["window"] = _stats(js_w, ds_w, f"jday[{lo},{hi})")
    return out


def last_progress_jday(case_dir: Path) -> float | None:
    tsr = parse_tsr_dlt(case_dir, None)
    if tsr.get("last_jday") is not None:
        return tsr["last_jday"]
    flow = case_dir / "flowbal.csv"
    if flow.exists():
        last = None
        for raw in flow.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = raw.strip()
            if not s or s.upper().startswith("JDAY"):
                continue
            try:
                last = float(s.split(",")[0])
            except ValueError:
                continue
        return last
    return None


def parse_nhr(case_dir: Path | str, window: tuple[float, float] | None = None) -> dict[str, Any]:
    case_dir = Path(case_dir)
    wrn_path = case_dir / "w2.wrn"
    err_path = case_dir / "w2.err"
    con_path = case_dir / "w2_con.csv"
    sched = parse_dlt_schedule(con_path) if con_path.exists() else {}
    dltmin = sched.get("dltmin") if isinstance(sched, dict) else None

    wrn_text = wrn_path.read_text(encoding="utf-8", errors="ignore") if wrn_path.exists() else ""
    err_text = err_path.read_text(encoding="utf-8", errors="ignore") if err_path.exists() else ""
    wrn = parse_wrn(wrn_text) if wrn_text else {
        "neg_surface_thickness_count": 0,
        "neg_surface_thickness_events": [],
        "add_layer_count": 0,
        "add_layer_jdays": [],
        "add_layer_events": [],
        "subtract_layer_count": 0,
        "subtract_layer_jdays": [],
        "subtract_layer_events": [],
        "low_water_count": 0,
        "low_water_events": [],
        "ws_above_layer2_count": 0,
        "ws_above_layer2_events": [],
        "h1h2_gt_035_count": 0,
        "h1h2_gt_035_events": [],
        "dltmin_reduced_count": 0,
        "dltmin_reduced_events": [],
        "dltmin_set_count": 0,
        "dltmin_set_events": [],
        "dltmin_hint_count": 0,
        "wrn_missing": True,
    }
    wrn["wrn_exists"] = wrn_path.exists()
    wrn["wrn_bytes"] = wrn_path.stat().st_size if wrn_path.exists() else 0

    snp = parse_snp_runtime(case_dir)
    tsr = parse_tsr_dlt(case_dir, dltmin if isinstance(dltmin, float) else None, window)
    last_j = tsr.get("last_jday")
    tmend = sched.get("tmend") if isinstance(sched, dict) else None
    reached = False
    if last_j is not None and tmend is not None:
        reached = last_j >= float(tmend) - 1.0
    elif snp.get("normal_termination"):
        reached = True

    rec: dict[str, Any] = {
        "case_dir": str(case_dir),
        "case_name": case_dir.name,
        "parsed_at": datetime.now().isoformat(timespec="seconds"),
        "completed": bool(reached),
        "last_jday": last_j,
        "dlt_schedule": sched,
        "nhr": {
            **wrn,
            "w2_err": parse_err(err_text),
            "snp_runtime": snp,
            "dlt_trajectory": tsr,
            "exit_zero_masks_rollback": wrn.get("neg_surface_thickness_count", 0) > 0
            and not parse_err(err_text).get("present")
            and bool(snp.get("normal_termination") or reached),
        },
    }
    return rec


def discover_case_dirs(root: Path = REPRO) -> list[Path]:
    dirs: list[Path] = []
    if not root.exists():
        return dirs
    for con in root.rglob("w2_con.csv"):
        dirs.append(con.parent)
    dirs.sort(key=lambda p: str(p).lower())
    return dirs


def parse_existing_runs(root: Path = REPRO) -> dict[str, Any]:
    cases = []
    for d in discover_case_dirs(root):
        rel = str(d.relative_to(root)) if d.is_relative_to(root) else str(d)
        # Long Lake unstable window is the paper's focus
        win = (30.0, 40.0) if "long lake" in d.name.lower() else None
        rec = parse_nhr(d, window=win)
        rec["run_relative"] = rel.replace("\\", "/")
        rec["run_id"] = rel.split("/")[0].split("\\")[0]
        cases.append(rec)
    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "parser": "00_INDEX/parse_nhr.py",
        "n_cases": len(cases),
        "cases": cases,
    }


def _json_default(o: Any) -> Any:
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    raise TypeError(type(o))


def dump_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Parse CE-QUAL-W2 Numerical Health Record")
    ap.add_argument("dirs", nargs="*", type=Path, help="case directories (containing w2_con.csv)")
    ap.add_argument("--existing", action="store_true", help="scan all 05_REPRO_RUNS cases")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--window", type=float, nargs=2, metavar=("LO", "HI"), default=None)
    args = ap.parse_args()
    win = tuple(args.window) if args.window else None
    if args.existing:
        payload = parse_existing_runs()
        out = args.out or (ROOT / "06_PAPER" / "analysis" / "nhr_existing_runs.json")
        dump_json(payload, out)
        print(f"wrote {out}  n={payload['n_cases']}")
        return
    if not args.dirs:
        ap.error("provide dirs or --existing")
    recs = [parse_nhr(d, window=win) for d in args.dirs]
    payload = recs[0] if len(recs) == 1 else {"cases": recs}
    if args.out:
        dump_json(payload, args.out)
        print(f"wrote {args.out}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default))


if __name__ == "__main__":
    main()
