#!/usr/bin/env python3
"""Re-run Columbia Slough with SED_DIAG OFF (missing W2_diagenesis.npt)."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
EXE = ROOT / "02_LIBRARY/07_executables/v4.5.5/w2_v455_ifx.exe"
SRC = ROOT / "02_LIBRARY/06_examples/v4.5.5/Columbia Slough Estuary"
DST = ROOT / "05_REPRO_RUNS/run_20260811_fixed/Columbia Slough Estuary"


def patch_columbia(con: Path) -> list[str]:
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    changed: list[str] = []
    for i, line in enumerate(lines):
        if line.lstrip().startswith("NDAY,SELECTC,HABTATC") and i + 1 < len(lines):
            parts = lines[i + 1].split(",")
            if len(parts) >= 8:
                old = parts[7]
                parts[7] = "OFF"
                nl = "\n" if lines[i + 1].endswith("\n") else ""
                lines[i + 1] = ",".join(parts)
                if nl and not lines[i + 1].endswith("\n"):
                    lines[i + 1] += nl
                changed.append(f"SED_DIAG {old.strip()} -> OFF")
            break
    for i, line in enumerate(lines):
        if line.lstrip().startswith("SCR") and i + 1 < len(lines) and lines[i + 1].lstrip().upper().startswith("ON"):
            commas = lines[i + 1].count(",")
            nl = "\n" if lines[i + 1].endswith("\n") else ""
            lines[i + 1] = "OFF" + ("," * commas) + nl
            changed.append("SCR ON -> OFF")
            break
    # Enable PRFC lightly for profiles
    for i, line in enumerate(lines):
        if line.lstrip().startswith("PRFC") and i + 1 < len(lines) and lines[i + 1].lstrip().upper().startswith("OFF"):
            commas = lines[i + 1].count(",")
            nl = "\n" if lines[i + 1].endswith("\n") else ""
            lines[i + 1] = "ON" + ("," * max(commas, 1)) + nl
            pad = "," * 80 + "\n"
            if i + 2 < len(lines):
                lines[i + 2] = "4" + pad
            if i + 3 < len(lines):
                lines[i + 3] = "1" + pad
            if i + 4 < len(lines):
                lines[i + 4] = "35,40,45,50" + pad
            if i + 5 < len(lines):
                lines[i + 5] = "500,500,500,500" + pad
            if i + 6 < len(lines):
                lines[i + 6] = "45" + pad
            changed.append("PRFC OFF -> ON (days 35/40/45/50, seg 45)")
            break
    con.write_text("".join(lines), encoding="utf-8")
    return changed


def main() -> None:
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    changed = patch_columbia(DST / "w2_con.csv")
    print("patches:", changed)

    log_out = DST / "run_stdout.txt"
    log_err = DST / "run_stderr.txt"
    t0 = time.time()
    with log_out.open("w", encoding="utf-8") as fo, log_err.open("w", encoding="utf-8") as fe:
        proc = subprocess.Popen([str(EXE)], cwd=str(DST), stdout=fo, stderr=fe)
        timed_out = False
        while True:
            rc = proc.poll()
            if rc is not None:
                break
            if time.time() - t0 > 600:
                timed_out = True
                proc.kill()
                break
            time.sleep(2)
    elapsed = time.time() - t0
    rc = proc.returncode if proc.returncode is not None else -9
    stderr = log_err.read_text(encoding="utf-8", errors="ignore")
    stdout = log_out.read_text(encoding="utf-8", errors="ignore")
    forrtl = ("forrtl" in stderr.lower()) or ("forrtl" in stdout.lower())
    tsr = list(DST.glob("tsr_*.csv"))
    cpl = list(DST.glob("cpl*.opt"))
    prf = list(DST.glob("prf*.opt"))
    info = {
        "exit": rc,
        "elapsed": round(elapsed, 2),
        "forrtl": forrtl,
        "timed_out": timed_out,
        "patches": changed,
        "tsr": [
            {
                "name": p.name,
                "bytes": p.stat().st_size,
                "lines": sum(1 for _ in p.open("r", encoding="utf-8", errors="ignore")),
            }
            for p in tsr
        ],
        "cpl": [(p.name, p.stat().st_size) for p in cpl],
        "prf": [(p.name, p.stat().st_size) for p in prf],
        "w2_err": (DST / "w2.err").read_text(encoding="utf-8", errors="ignore") if (DST / "w2.err").exists() else "",
        "w2_wrn": ((DST / "w2.wrn").read_text(encoding="utf-8", errors="ignore")[:800] if (DST / "w2.wrn").exists() else ""),
        "stderr_tail": stderr[-1500:],
    }
    out = DST / "columbia_rerun.json"
    out.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
