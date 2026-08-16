#!/usr/bin/env python3
"""Small Columbia Slough DLTMAX scan (NDLT=1, DLTINTER already OFF)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
SRC = ROOT / "02_LIBRARY" / "06_examples" / "v4.5.5" / "Columbia Slough Estuary"
EXE = ROOT / "02_LIBRARY" / "07_executables" / "v4.5.5" / "w2_v455_ifx.exe"
SCAN_ROOT = ROOT / "05_REPRO_RUNS" / "run_20260815_columbia_dlt_scan"
TMEND = 55.0
TIMEOUT_SEC = 20 * 60
MAX_PARALLEL = 3
GRID = [120, 360, 720]

sys.path.insert(0, str(ROOT / "00_INDEX"))
from parse_nhr import last_progress_jday, parse_nhr  # noqa: E402
from run_ll_dlt_scan import turn_scr_off  # noqa: E402


def patch_sed_diag_off(con: Path) -> None:
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.lstrip().startswith("NDAY,SELECTC,HABTATC") and i + 1 < len(lines):
            parts = lines[i + 1].split(",")
            if len(parts) >= 8 and parts[7].strip().upper().startswith("ON"):
                parts[7] = "OFF"
                nl = "\n" if lines[i + 1].endswith("\n") else ""
                lines[i + 1] = ",".join(parts)
                if nl and not lines[i + 1].endswith("\n"):
                    lines[i + 1] += nl
                con.write_text("".join(lines), encoding="utf-8")
            return


def patch_dltmax(con: Path, dltmax: float) -> None:
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    for i, line in enumerate(lines):
        key = line.lstrip().split(",")[0].strip().upper()
        if key == "DLTMAX" and i + 1 < len(lines):
            old = lines[i + 1]
            commas = old.count(",")
            nl = "\n" if old.endswith("\n") else ""
            fields = [p.strip() for p in old.split(",") if p.strip() != ""]
            if not fields:
                raise RuntimeError("empty DLTMAX row")
            fields[0] = str(int(dltmax) if abs(dltmax - round(dltmax)) < 1e-9 else dltmax)
            extra = commas - (len(fields) - 1)
            lines[i + 1] = ",".join(fields) + ("," * max(extra, 0)) + nl
            con.write_text("".join(lines), encoding="utf-8")
            return
    raise RuntimeError("DLTMAX not found")


def prepare(dltmax: int) -> Path:
    dst = SCAN_ROOT / f"dltmax_{dltmax}"
    if dst.exists():
        shutil.rmtree(dst)
    SCAN_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, dst)
    (dst / "HabitatFiles").mkdir(exist_ok=True)
    turn_scr_off(dst / "w2_con.csv")
    patch_sed_diag_off(dst / "w2_con.csv")
    patch_dltmax(dst / "w2_con.csv", dltmax)
    (dst / "scan_meta.json").write_text(
        json.dumps({"case": "Columbia Slough Estuary", "dltmax": dltmax, "dltinter": "OFF"}, indent=2),
        encoding="utf-8",
    )
    return dst


def main() -> None:
    jobs = []
    for dm in GRID:
        dst = prepare(dm)
        jobs.append({"dltmax": dm, "dir": dst, "name": dst.name})
    pending = list(jobs)
    running = []
    finished = []

    def launch(job):
        fo = (job["dir"] / "run_stdout.txt").open("w", encoding="utf-8", errors="replace")
        fe = (job["dir"] / "run_stderr.txt").open("w", encoding="utf-8", errors="replace")
        proc = subprocess.Popen([str(EXE)], cwd=str(job["dir"]), stdout=fo, stderr=fe)
        fo.close()
        fe.close()
        job["proc"] = proc
        job["t0"] = time.time()
        job["idle"] = 0
        job["last_j"] = None
        running.append(job)
        print(f"[start] {job['name']} pid={proc.pid}", flush=True)

    for _ in range(min(MAX_PARALLEL, len(pending))):
        launch(pending.pop(0))
    while running or pending:
        time.sleep(5)
        still = []
        for job in running:
            proc = job["proc"]
            j = last_progress_jday(job["dir"])
            if j is not None and job["last_j"] is not None and abs(j - job["last_j"]) < 1e-4:
                job["idle"] += 5
            else:
                job["idle"] = 0
            if j is not None:
                job["last_j"] = j
            stop = None
            if proc.poll() is not None:
                stop = "exit"
            elif j is not None and j >= TMEND - 0.5 and job["idle"] >= 20:
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except Exception:
                    proc.kill()
                stop = "idle_tmend"
            elif time.time() - job["t0"] > TIMEOUT_SEC:
                proc.kill()
                stop = "timeout"
            if stop is None:
                still.append(job)
                continue
            rec = {
                "name": job["name"],
                "dltmax": job["dltmax"],
                "exit_code": proc.returncode,
                "elapsed_sec": round(time.time() - job["t0"], 2),
                "stop_reason": stop,
                "last_jday": last_progress_jday(job["dir"]),
                "nhr": parse_nhr(job["dir"]),
            }
            finished.append(rec)
            print(f"[done] {job['name']} {stop} t={rec['elapsed_sec']}s j={rec['last_jday']}", flush=True)
            if pending:
                launch(pending.pop(0))
        running = still
    summary = {"scan": "Columbia DLTMAX", "generated": datetime.now().isoformat(timespec="seconds"), "jobs": finished}
    (SCAN_ROOT / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("n_jobs=", len(finished))


if __name__ == "__main__":
    main()
