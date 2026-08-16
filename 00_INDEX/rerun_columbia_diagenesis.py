#!/usr/bin/env python3
"""Copy DeGray diagenesis file, clamp segments to Columbia IMX=51, rerun with SED_DIAG ON."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
EXE = ROOT / "02_LIBRARY/07_executables/v4.5.5/w2_v455_ifx.exe"
SRC = ROOT / "02_LIBRARY/06_examples/v4.5.5/Columbia Slough Estuary"
DIA_SRC = ROOT / "02_LIBRARY/06_examples/v4.5.5/DeGray Reservoir with sediment diagenesis and vertical algae migration/w2_diagenesis.npt"
DST = ROOT / "05_REPRO_RUNS/run_20260814_columbia_diag/Columbia Slough Estuary"
IMX = 51


def adapt_diagenesis(src: Path, dst: Path) -> None:
    """Copy DeGray template; extend rate/IC region 2 from seg 31 to IMX-1.

    Bed consolidation stays OFF so DeGray's segs 82–90 are skipped at parse time.
    Region loops index CEMAMFT_*_RegN(IMX); 50 is in range for Columbia IMX=51.
    """
    text = src.read_text(encoding="utf-8", errors="replace")
    old = '"Ending segment for regions",13,31,,,,,,'
    new = f'"Ending segment for regions",13,{IMX - 1},,,,,,,'
    n = text.count(old)
    if n != 2:
        raise RuntimeError(f"expected 2 IC/rate ending-segment lines, found {n}")
    dst.write_text(text.replace(old, new), encoding="utf-8")


def patch_con(con: Path) -> list[str]:
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    changed = []
    for i, line in enumerate(lines):
        if line.lstrip().startswith("NDAY,SELECTC,HABTATC") and i + 1 < len(lines):
            parts = lines[i + 1].split(",")
            if len(parts) >= 8:
                parts[7] = "ON"
                nl = "\n" if lines[i + 1].endswith("\n") else ""
                lines[i + 1] = ",".join(parts)
                if nl and not lines[i + 1].endswith("\n"):
                    lines[i + 1] += nl
                changed.append("SED_DIAG ON")
            break
    for i, line in enumerate(lines):
        if line.lstrip().startswith("SCR") and i + 1 < len(lines) and lines[i + 1].lstrip().upper().startswith("ON"):
            commas = lines[i + 1].count(",")
            nl = "\n" if lines[i + 1].endswith("\n") else ""
            lines[i + 1] = "OFF" + ("," * commas) + nl
            changed.append("SCR OFF")
            break
    con.write_text("".join(lines), encoding="utf-8")
    return changed


def main() -> None:
    if DST.exists():
        shutil.rmtree(DST)
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SRC, DST)
    adapt_diagenesis(DIA_SRC, DST / "W2_diagenesis.npt")
    (DST / "SedimentDiagenesis").mkdir(exist_ok=True)
    changed = patch_con(DST / "w2_con.csv")
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
            jmax = None
            tsr = list(DST.glob("tsr_*.csv"))
            if tsr:
                try:
                    lines = tsr[0].read_text(encoding="utf-8", errors="ignore").splitlines()
                    for line in reversed(lines):
                        p = line.strip().split(",")[0]
                        try:
                            jmax = float(p)
                            break
                        except ValueError:
                            continue
                except OSError:
                    jmax = None
            if jmax is not None and last_j is not None and abs(jmax - last_j) < 1e-6:
                idle += 5
            else:
                idle = 0
            last_j = jmax if jmax is not None else last_j
            if jmax is not None and jmax >= 54.9 and idle >= 30:
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
    err = (DST / "w2.err").read_text(encoding="utf-8", errors="ignore") if (DST / "w2.err").exists() else ""
    stderr = log_err.read_text(encoding="utf-8", errors="ignore")
    summary = {
        "case": "Columbia Slough SED_DIAG ON",
        "patches": changed,
        "exit_code": proc.returncode,
        "elapsed_sec": round(elapsed, 2),
        "forrtl": "forrtl" in stderr.lower() or "file not found" in stderr.lower(),
        "w2_err": err[:800],
        "stderr_tail": stderr[-1500:],
        "dia_outputs": [p.name for p in (DST / "SedimentDiagenesis").glob("*.csv")],
        "tsr": [p.name for p in DST.glob("tsr_*.csv")],
        "started": datetime.now().isoformat(timespec="seconds"),
    }
    (DST.parent / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
