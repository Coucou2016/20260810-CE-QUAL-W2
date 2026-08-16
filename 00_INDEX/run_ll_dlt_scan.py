#!/usr/bin/env python3
"""Long Lake DLTMAX (x optional DLTF) scan for paper innovation 3 / NHR.

Patches only the JDAY 30-40 window in w2_con.csv:
  DLTD    = 1, 1.2, 30, 40, 175, 193
  DLTMAX  = 5, 800, [THIS], 1800, 60, 100     # official THIS=100
  DLTF    = 0.9, 0.9, [THIS], 0.9, 0.2, 0.2  # official THIS=0.9

SCR OFF, HabitatFiles created, idle+TMEND terminate, wall-clock timeout.
At most MAX_PARALLEL exe processes.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
SRC = ROOT / "02_LIBRARY" / "06_examples" / "v4.5.5" / "Long Lake"
EXE = ROOT / "02_LIBRARY" / "07_executables" / "v4.5.5" / "w2_v455_ifx.exe"
SCAN_ROOT = ROOT / "05_REPRO_RUNS" / "run_20260815_ll_dlt_scan"
TMEND = 240.0
TIMEOUT_SEC = 40 * 60
MAX_PARALLEL = 3
IDLE_SEC_AT_END = 20
POLL_SEC = 5

# Official DLTMAX line (6 windows). Third value is JDAY 30-40.
OFFICIAL_DLTMAX = [5.0, 800.0, 100.0, 1800.0, 60.0, 100.0]
OFFICIAL_DLTF = [0.9, 0.9, 0.9, 0.9, 0.2, 0.2]
DLTMAX_GRID = [20, 50, 100, 200]
# 1-D first; extra DLTF points can be appended by CLI
DEFAULT_DLTF = 0.9

sys.path.insert(0, str(ROOT / "00_INDEX"))
from parse_nhr import last_progress_jday, parse_nhr  # noqa: E402


def ensure_habitat(case_dir: Path) -> None:
    (case_dir / "HabitatFiles").mkdir(exist_ok=True)


def turn_scr_off(con: Path) -> bool:
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.lstrip().startswith("SCR") and i + 1 < len(lines) and lines[i + 1].lstrip().upper().startswith("ON"):
            commas = lines[i + 1].count(",")
            nl = "\n" if lines[i + 1].endswith("\n") else ""
            lines[i + 1] = "OFF" + ("," * commas) + nl
            con.write_text("".join(lines), encoding="utf-8")
            return True
    return False


def _fmt_num(x: float) -> str:
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    s = f"{x:g}"
    return s


def _csv_row(values: list[float], n_commas: int) -> str:
    body = ",".join(_fmt_num(v) for v in values)
    extra = n_commas - (len(values) - 1)
    if extra < 0:
        extra = 0
    return body + ("," * extra)


def patch_dlt_window(con: Path, dltmax_w: float, dltf_w: float) -> dict:
    """Replace DLTMAX and DLTF rows by locating the header then the value line."""
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    found = {"dltmax": False, "dltf": False}
    new_dltmax = list(OFFICIAL_DLTMAX)
    new_dltf = list(OFFICIAL_DLTF)
    new_dltmax[2] = float(dltmax_w)
    new_dltf[2] = float(dltf_w)
    for i, line in enumerate(lines):
        key = line.lstrip().split(",")[0].strip().upper()
        if key == "DLTMAX" and i + 1 < len(lines) and not found["dltmax"]:
            old = lines[i + 1]
            commas = old.count(",")
            nl = "\n" if old.endswith("\n") else ""
            # Verify we are on the official 6-value row (or a previously patched one)
            fields = [p.strip() for p in old.split(",") if p.strip() != ""]
            if len(fields) < 6:
                raise RuntimeError(f"DLTMAX value row has {len(fields)} fields, expected 6: {old!r}")
            # First two and last three should stay official; only index 2 is the scan knob
            lines[i + 1] = _csv_row(new_dltmax, commas) + nl
            found["dltmax"] = True
        elif key == "DLTF" and i + 1 < len(lines) and not found["dltf"]:
            old = lines[i + 1]
            commas = old.count(",")
            nl = "\n" if old.endswith("\n") else ""
            fields = [p.strip() for p in old.split(",") if p.strip() != ""]
            if len(fields) < 6:
                raise RuntimeError(f"DLTF value row has {len(fields)} fields, expected 6: {old!r}")
            lines[i + 1] = _csv_row(new_dltf, commas) + nl
            found["dltf"] = True
    if not found["dltmax"] or not found["dltf"]:
        raise RuntimeError(f"failed to locate DLTMAX/DLTF rows: {found}")
    con.write_text("".join(lines), encoding="utf-8")
    return {"dltmax_row": new_dltmax, "dltf_row": new_dltf}


def set_dltinter(con: Path, on: bool) -> str:
    """DLTINTER=ON linearly interpolates DLTMAX between DLTD knots (update.F90 L157-159)."""
    target = "ON" if on else "OFF"
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    for i, line in enumerate(lines):
        key = line.lstrip().split(",")[0].strip().upper()
        if key == "NDLT" and i + 1 < len(lines):
            parts = lines[i + 1].split(",")
            if len(parts) >= 3:
                old = parts[2]
                # Fortran ADJUSTR's this to 8 chars; compare is DLTINTER == '      ON'
                parts[2] = f"{target:<8}"
                nl = "\n" if lines[i + 1].endswith("\n") else ""
                lines[i + 1] = ",".join(parts)
                if nl and not lines[i + 1].endswith("\n"):
                    lines[i + 1] += nl
                con.write_text("".join(lines), encoding="utf-8")
                return f"{old.strip()}->{target}"
    raise RuntimeError("NDLT/DLTINTER row not found")


def job_dir_name(dltmax: float, dltf: float, inter_on: bool) -> str:
    dm = _fmt_num(dltmax)
    parts = [f"dltmax_{dm}"]
    if abs(dltf - DEFAULT_DLTF) >= 1e-12:
        parts.append("dltf_" + str(dltf).replace(".", "p"))
    if not inter_on:
        parts.append("interoff")
    return "_".join(parts)


def prepare_job(dltmax: float, dltf: float, inter_on: bool = True) -> Path:
    name = job_dir_name(dltmax, dltf, inter_on)
    dst = SCAN_ROOT / name
    if dst.exists():
        shutil.rmtree(dst)
    SCAN_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, dst)
    ensure_habitat(dst)
    turn_scr_off(dst / "w2_con.csv")
    inter_patch = set_dltinter(dst / "w2_con.csv", inter_on)
    patch = patch_dlt_window(dst / "w2_con.csv", dltmax, dltf)
    (dst / "scan_meta.json").write_text(
        json.dumps(
            {
                "dltmax_window_30_40": dltmax,
                "dltf_window_30_40": dltf,
                "dltinter": "ON" if inter_on else "OFF",
                "dltinter_patch": inter_patch,
                "patch": patch,
                "src": str(SRC),
                "note": (
                    "With DLTINTER=ON, DLTMAX is interpolated from the day-30 knot "
                    "to the day-40 knot (official 1800 s). Patching only the day-30 "
                    "value changes the interpolation start, not a hard cap."
                ),
                "prepared": datetime.now().isoformat(timespec="seconds"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return dst


def watch_proc(proc: subprocess.Popen, case_dir: Path, t0: float) -> dict:
    idle = 0
    last_j = None
    reason = "exit"
    while proc.poll() is None:
        time.sleep(POLL_SEC)
        j = last_progress_jday(case_dir)
        if j is not None and last_j is not None and abs(j - last_j) < 1e-4:
            idle += POLL_SEC
        else:
            idle = 0
        last_j = j if j is not None else last_j
        if j is not None and j >= TMEND - 0.5 and idle >= IDLE_SEC_AT_END:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except Exception:
                proc.kill()
            reason = "idle_tmend"
            break
        if time.time() - t0 > TIMEOUT_SEC:
            proc.kill()
            reason = "timeout"
            break
    elapsed = time.time() - t0
    return {
        "exit_code": proc.returncode,
        "elapsed_sec": round(elapsed, 2),
        "stop_reason": reason,
        "last_tsr_jday": last_progress_jday(case_dir),
    }


def launch(case_dir: Path) -> tuple[subprocess.Popen, Path, Path, float]:
    log_out, log_err = case_dir / "run_stdout.txt", case_dir / "run_stderr.txt"
    fo = log_out.open("w", encoding="utf-8", errors="replace")
    fe = log_err.open("w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen([str(EXE)], cwd=str(case_dir), stdout=fo, stderr=fe)
    fo.close()
    fe.close()
    return proc, log_out, log_err, time.time()


def run_scan(grid: list[tuple[float, float, bool]]) -> dict:
    jobs = []
    for dltmax, dltf, inter_on in grid:
        dst = prepare_job(dltmax, dltf, inter_on)
        jobs.append(
            {
                "dltmax": dltmax,
                "dltf": dltf,
                "inter_on": inter_on,
                "dir": dst,
                "name": dst.name,
            }
        )

    pending = list(jobs)
    running: list[dict] = []
    finished: list[dict] = []

    def start_next() -> None:
        if not pending:
            return
        job = pending.pop(0)
        proc, log_out, log_err, t0 = launch(job["dir"])
        job["proc"] = proc
        job["t0"] = t0
        job["log_out"] = log_out
        job["log_err"] = log_err
        job["idle"] = 0
        job["last_j"] = None
        running.append(job)
        print(f"[start] {job['name']} pid={proc.pid}", flush=True)

    for _ in range(min(MAX_PARALLEL, len(pending))):
        start_next()

    while running or pending:
        time.sleep(POLL_SEC)
        still = []
        for job in running:
            proc: subprocess.Popen = job["proc"]
            t0 = job["t0"]
            case_dir: Path = job["dir"]
            j = last_progress_jday(case_dir)
            if j is not None and job["last_j"] is not None and abs(j - job["last_j"]) < 1e-4:
                job["idle"] += POLL_SEC
            else:
                job["idle"] = 0
            if j is not None:
                job["last_j"] = j
            stop = None
            if proc.poll() is not None:
                stop = "exit"
            elif j is not None and j >= TMEND - 0.5 and job["idle"] >= IDLE_SEC_AT_END:
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except Exception:
                    proc.kill()
                stop = "idle_tmend"
            elif time.time() - t0 > TIMEOUT_SEC:
                proc.kill()
                stop = "timeout"
            if stop is None:
                still.append(job)
                continue
            elapsed = time.time() - t0
            err_txt = ""
            if job["log_err"].exists():
                err_txt = job["log_err"].read_text(encoding="utf-8", errors="ignore")
            rec = {
                "name": job["name"],
                "dltmax_window_30_40": job["dltmax"],
                "dltf_window_30_40": job["dltf"],
                "dltinter": "ON" if job["inter_on"] else "OFF",
                "dir": str(job["dir"]),
                "exit_code": proc.returncode,
                "elapsed_sec": round(elapsed, 2),
                "stop_reason": stop,
                "last_tsr_jday": last_progress_jday(case_dir),
                "forrtl": "forrtl" in err_txt.lower(),
            }
            try:
                rec["nhr"] = parse_nhr(case_dir, window=(30.0, 40.0))
            except Exception as exc:
                rec["nhr_error"] = str(exc)
            finished.append(rec)
            print(
                f"[done] {job['name']} reason={stop} exit={proc.returncode} "
                f"t={elapsed:.0f}s jday={rec['last_tsr_jday']}",
                flush=True,
            )
            start_next()
        running = still

    summary = {
        "scan": "Long Lake DLTMAX window JDAY 30-40",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "exe": str(EXE),
        "timeout_sec": TIMEOUT_SEC,
        "jobs": finished,
    }
    (SCAN_ROOT / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    return summary


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--dltmax", type=float, nargs="*", default=DLTMAX_GRID)
    ap.add_argument("--dltf", type=float, nargs="*", default=[DEFAULT_DLTF])
    ap.add_argument(
        "--interoff",
        action="store_true",
        help="Also run DLTINTER=OFF (step DLTMAX, no interpolation to 1800 s)",
    )
    args = ap.parse_args()
    inter_flags = [True, False] if args.interoff else [True]
    grid = [(dm, df, inter) for inter in inter_flags for dm in args.dltmax for df in args.dltf]
    print(f"grid n={len(grid)} parallel<={MAX_PARALLEL}: {grid}", flush=True)
    summary = run_scan(grid)
    print(json.dumps({k: summary[k] for k in ("scan", "generated") if k in summary}, indent=2))
    print(f"n_jobs={len(summary['jobs'])}")


if __name__ == "__main__":
    main()
