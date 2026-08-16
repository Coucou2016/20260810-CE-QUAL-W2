#!/usr/bin/env python3
"""Rerun Bonneville with SYSTDG ON but TDGTA OFF (no spill reallocation to a target)."""
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
RUN = ROOT / "05_REPRO_RUNS" / "run_20260814_bonneville_notarget" / "Bonneville_SYSTDG"
TMEND = 40909.0


def turn_scr_off(con: Path) -> None:
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.lstrip().startswith("SCR") and i + 1 < len(lines) and lines[i + 1].lstrip().upper().startswith("ON"):
            commas = lines[i + 1].count(",")
            nl = "\n" if lines[i + 1].endswith("\n") else ""
            lines[i + 1] = "OFF" + ("," * commas) + nl
            con.write_text("".join(lines), encoding="utf-8")
            return


def turn_tdgta_off(npt: Path) -> None:
    text = npt.read_text(encoding="utf-8")
    old = ",ON,OFF,OFF,OFF,ON,,,,,"
    new = ",ON,OFF,OFF,OFF,OFF,,,,,"
    if old not in text:
        raise RuntimeError("could not find SYSTDG/TDGTA switch line")
    npt.write_text(text.replace(old, new, 1), encoding="utf-8")


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
    if RUN.exists():
        shutil.rmtree(RUN)
    RUN.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, RUN)
    shutil.copy2(OBS, RUN / "CCIW_TDG_Temp_2011-2015.csv")
    turn_scr_off(RUN / "w2_con.csv")
    turn_tdgta_off(RUN / "w2_systdg.npt")

    log_out, log_err = RUN / "run_stdout.txt", RUN / "run_stderr.txt"
    t0 = time.time()
    with log_out.open("w", encoding="utf-8", errors="replace") as fo, log_err.open(
        "w", encoding="utf-8", errors="replace"
    ) as fe:
        proc = subprocess.Popen([str(EXE)], cwd=str(RUN), stdout=fo, stderr=fe)
        idle = 0
        last_j = None
        while proc.poll() is None:
            time.sleep(10)
            j = last_flowbal_jday(RUN)
            if j is not None and last_j is not None and abs(j - last_j) < 1e-6:
                idle += 10
            else:
                idle = 0
            last_j = j if j is not None else last_j
            if j is not None and j >= TMEND - 1.0 and idle >= 40:
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
    summary = {
        "case": "Bonneville SYSTDG TDGTA OFF",
        "exit_code": proc.returncode,
        "elapsed_sec": round(elapsed, 2),
        "last_flowbal_jday": last_flowbal_jday(RUN),
        "forrtl": "forrtl" in log_err.read_text(encoding="utf-8", errors="ignore").lower(),
        "w2_err": (RUN / "w2.err").read_text(encoding="utf-8", errors="ignore") if (RUN / "w2.err").exists() else "",
        "started": datetime.now().isoformat(timespec="seconds"),
    }
    (RUN.parent / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
