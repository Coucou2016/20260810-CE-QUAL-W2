#!/usr/bin/env python3
"""Run the v4.5.5 Bonneville SYSTDG example and copy CCIW observations."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
SRC = ROOT / "02_LIBRARY" / "06_examples" / "v4.5.5" / "BonnevilleDam with TDG computed using SYSTDG"
OBS = ROOT / "02_LIBRARY" / "06_examples" / "v5.0_beta" / "Bonneville_TDG" / "CCIW_TDG_Temp_2011-2015.csv"
EXE = ROOT / "02_LIBRARY" / "07_executables" / "v4.5.5" / "w2_v455_ifx.exe"
RUN = ROOT / "05_REPRO_RUNS" / "run_20260814_bonneville" / "Bonneville_SYSTDG"


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


def last_flowbal_jday(case_dir: Path) -> float | None:
    p = case_dir / "flowbal.csv"
    if not p.exists() or p.stat().st_size < 50:
        return None
    last = None
    for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = raw.strip()
        if not s or s.startswith("JDAY") or s.startswith("$"):
            continue
        try:
            last = float(s.split(",")[0])
        except ValueError:
            continue
    return last


def main() -> None:
    if not EXE.exists() or EXE.stat().st_size < 100_000:
        raise SystemExit(f"Bad exe: {EXE}")
    if RUN.exists():
        shutil.rmtree(RUN)
    RUN.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, RUN)
    shutil.copy2(OBS, RUN / "CCIW_TDG_Temp_2011-2015.csv")
    scr = turn_scr_off(RUN / "w2_con.csv")

    log_out = RUN / "run_stdout.txt"
    log_err = RUN / "run_stderr.txt"
    t0 = time.time()
    with log_out.open("w", encoding="utf-8", errors="replace") as fo, log_err.open(
        "w", encoding="utf-8", errors="replace"
    ) as fe:
        proc = subprocess.Popen([str(EXE)], cwd=str(RUN), stdout=fo, stderr=fe)
        idle = 0
        last_j = None
        while True:
            rc = proc.poll()
            if rc is not None:
                break
            time.sleep(10)
            j = last_flowbal_jday(RUN)
            if j is not None and last_j is not None and abs(j - last_j) < 1e-6:
                idle += 10
            else:
                idle = 0
            last_j = j if j is not None else last_j
            # Official TMEND=40909; if flowbal reached end and idle, close leftover GUI.
            if j is not None and j >= 40908.0 and idle >= 40:
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except Exception:
                    proc.kill()
                break
            if time.time() - t0 > 10800:
                proc.kill()
                break

    elapsed = time.time() - t0
    tsr = sorted(RUN.glob("tsr_*.csv")) + sorted(RUN.glob("BON_tsr*.csv"))
    summary = {
        "case": "Bonneville SYSTDG",
        "run_dir": str(RUN),
        "exe": str(EXE),
        "scr_off": scr,
        "exit_code": proc.returncode,
        "elapsed_sec": round(elapsed, 2),
        "last_flowbal_jday": last_flowbal_jday(RUN),
        "tsr_files": [p.name for p in tsr],
        "w2_err": (RUN / "w2.err").read_text(encoding="utf-8", errors="ignore")[:500]
        if (RUN / "w2.err").exists()
        else "",
        "started": datetime.now().isoformat(timespec="seconds"),
    }
    (RUN.parent / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
