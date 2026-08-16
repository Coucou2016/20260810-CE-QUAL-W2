#!/usr/bin/env python3
"""Rerun Long Lake with a tighter DLTMAX in the window that hit negative layer thickness."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
SRC = ROOT / "02_LIBRARY" / "06_examples" / "v4.5.5" / "Long Lake"
EXE = ROOT / "02_LIBRARY" / "07_executables" / "v4.5.5" / "w2_v455_ifx.exe"
DST = ROOT / "05_REPRO_RUNS" / "run_20260814_longlake_dlt" / "Long Lake"
TMEND = 240.0


def ensure_habitat(case_dir: Path) -> None:
    (case_dir / "HabitatFiles").mkdir(exist_ok=True)


def turn_scr_off(con: Path) -> None:
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.lstrip().startswith("SCR") and i + 1 < len(lines) and lines[i + 1].lstrip().upper().startswith("ON"):
            commas = lines[i + 1].count(",")
            nl = "\n" if lines[i + 1].endswith("\n") else ""
            lines[i + 1] = "OFF" + ("," * commas) + nl
            con.write_text("".join(lines), encoding="utf-8")
            return


def patch_dltmax(con: Path) -> str:
    """Official DLTMAX at DLTD=30 is 100 s; warning at JDAY 31.936 used ~74 s then blew up."""
    text = con.read_text(encoding="utf-8", errors="ignore")
    old = "5,800,100,1800,60,100"
    new = "5,800,20,1800,60,100"
    if old not in text:
        raise RuntimeError("DLTMAX line not found")
    con.write_text(text.replace(old, new, 1), encoding="utf-8")
    return f"{old} -> {new}"


def last_tsr_jday(case_dir: Path) -> float | None:
    files = list(case_dir.glob("tsr_*.csv"))
    if not files:
        return None
    last = None
    for raw in files[0].read_text(encoding="utf-8", errors="ignore").splitlines():
        s = raw.strip()
        if not s or s.upper().startswith("JDAY"):
            continue
        try:
            last = float(s.split(",")[0])
        except ValueError:
            continue
    return last


def count_neg_thickness(wrn: Path) -> int:
    if not wrn.exists():
        return 0
    t = wrn.read_text(encoding="utf-8", errors="ignore")
    return t.lower().count("negative surface layer thickness")


def main() -> None:
    if DST.exists():
        shutil.rmtree(DST)
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, DST)
    ensure_habitat(DST)
    turn_scr_off(DST / "w2_con.csv")
    patch = patch_dltmax(DST / "w2_con.csv")

    log_out, log_err = DST / "run_stdout.txt", DST / "run_stderr.txt"
    t0 = time.time()
    with log_out.open("w", encoding="utf-8", errors="replace") as fo, log_err.open(
        "w", encoding="utf-8", errors="replace"
    ) as fe:
        proc = subprocess.Popen([str(EXE)], cwd=str(DST), stdout=fo, stderr=fe)
        idle = 0
        last_j = None
        while proc.poll() is None:
            time.sleep(5)
            j = last_tsr_jday(DST)
            if j is not None and last_j is not None and abs(j - last_j) < 1e-4:
                idle += 5
            else:
                idle = 0
            last_j = j if j is not None else last_j
            if j is not None and j >= TMEND - 0.5 and idle >= 20:
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except Exception:
                    proc.kill()
                break
            if time.time() - t0 > 1800:
                proc.kill()
                break
    elapsed = time.time() - t0
    wrn = DST / "w2.wrn"
    summary = {
        "case": "Long Lake DLTMAX 100->20 (days 30-40)",
        "patch": patch,
        "exit_code": proc.returncode,
        "elapsed_sec": round(elapsed, 2),
        "last_tsr_jday": last_tsr_jday(DST),
        "neg_thickness_count": count_neg_thickness(wrn),
        "forrtl": "forrtl" in log_err.read_text(encoding="utf-8", errors="ignore").lower(),
        "w2_err": (DST / "w2.err").read_text(encoding="utf-8", errors="ignore") if (DST / "w2.err").exists() else "",
        "started": datetime.now().isoformat(timespec="seconds"),
    }
    (DST.parent / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
