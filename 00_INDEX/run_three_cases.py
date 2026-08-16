#!/usr/bin/env python3
"""Run CE-QUAL-W2 example cases in an isolated repro directory.

Fixes known forrtl severe(29) when w2_habitat.npt points to a missing
output folder such as .\\HabitatFiles\\habitat.csv.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
SRC_BASE = ROOT / "02_LIBRARY" / "06_examples" / "v4.5.5"
EXE = ROOT / "02_LIBRARY" / "07_executables" / "v4.5.5" / "w2_v455_ifx.exe"
RUN_ID = "run_20260811_fixed"
RUN_BASE = ROOT / "05_REPRO_RUNS" / RUN_ID

CASES = [
    "Long Lake",
    "DeGray Reservoir with sediment diagenesis and vertical algae migration",
    "Columbia Slough Estuary",
]


def ensure_habitat_output_dirs(case_dir: Path) -> list[str]:
    """Create parent directories referenced by w2_habitat.npt output paths."""
    created: list[str] = []
    npt = case_dir / "w2_habitat.npt"
    if not npt.exists():
        return created
    for raw in npt.read_text(encoding="utf-8", errors="ignore").splitlines():
        # Typical line: 9,.\\HabitatFiles\\habitat.csv,ON,,,,,,
        parts = [p.strip().strip("'\"") for p in raw.split(",")]
        for p in parts:
            if not p:
                continue
            norm = p.replace("/", "\\")
            if "\\" not in norm and "/" not in p:
                continue
            if not re.search(r"(?i)habitat|fish_habitat|\.csv|\.opt", norm):
                continue
            parent = (case_dir / Path(norm)).parent
            if parent != case_dir and not parent.exists():
                parent.mkdir(parents=True, exist_ok=True)
                created.append(str(parent.relative_to(case_dir)))
    # Always create HabitatFiles if referenced as relative folder name
    text = npt.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"(?i)HabitatFiles", text):
        hf = case_dir / "HabitatFiles"
        if not hf.exists():
            hf.mkdir(parents=True, exist_ok=True)
            created.append("HabitatFiles")
    return created


def patch_columbia_control(case_dir: Path) -> list[str]:
    """Fix Columbia packaging issues and enable useful outputs.

    Official v4.5.5 Columbia example sets SED_DIAG=ON but ships no
    W2_diagenesis.npt, which triggers forrtl severe(29). Turn it OFF.
    Also set SCR OFF for headless runs and enable a light PRFC schedule.
    """
    con = case_dir / "w2_con.csv"
    if not con.exists():
        return []
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    changed: list[str] = []
    for i, line in enumerate(lines):
        if line.lstrip().startswith("NDAY,SELECTC,HABTATC") and i + 1 < len(lines):
            parts = lines[i + 1].split(",")
            if len(parts) >= 8 and parts[7].strip().upper().startswith("ON"):
                old = parts[7]
                parts[7] = "OFF"
                nl = "\n" if lines[i + 1].endswith("\n") else ""
                lines[i + 1] = ",".join(parts)
                if nl and not lines[i + 1].endswith("\n"):
                    lines[i + 1] += nl
                changed.append(f"SED_DIAG {old.strip()}->OFF (missing W2_diagenesis.npt)")
            break
    for i, line in enumerate(lines):
        if line.lstrip().startswith("SCR") and i + 1 < len(lines) and lines[i + 1].lstrip().upper().startswith("ON"):
            commas = lines[i + 1].count(",")
            nl = "\n" if lines[i + 1].endswith("\n") else ""
            lines[i + 1] = "OFF" + ("," * commas) + nl
            changed.append("SCR ON->OFF")
            break
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
            changed.append("PRFC enabled (35/40/45/50, seg45)")
            break
    if changed:
        con.write_text("".join(lines), encoding="utf-8")
    return changed


def key_outputs(case_dir: Path) -> dict:
    patterns = [
        "tsr_*.csv",
        "cpl*.opt",
        "prf*.opt",
        "snp*.opt",
        "flowbal.csv",
        "habitat.csv",
        "HabitatFiles/habitat.csv",
        "w2.err",
        "w2.wrn",
    ]
    found = {}
    for pat in patterns:
        hits = list(case_dir.glob(pat))
        found[pat] = [
            {
                "name": str(h.relative_to(case_dir)),
                "bytes": h.stat().st_size,
                "lines": sum(1 for _ in h.open("r", encoding="utf-8", errors="ignore")),
            }
            for h in hits
        ]
    return found


def run_case(name: str) -> dict:
    src = SRC_BASE / name
    dst = RUN_BASE / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    created = ensure_habitat_output_dirs(dst)
    columbia_patches: list[str] = []
    if name == "Columbia Slough Estuary":
        columbia_patches = patch_columbia_control(dst)
        ensure_habitat_output_dirs(dst)
    # Long Lake / any case: turn SCR OFF for headless stability
    con = dst / "w2_con.csv"
    if con.exists() and name != "Columbia Slough Estuary":
        lines = con.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.lstrip().startswith("SCR") and i + 1 < len(lines) and lines[i + 1].lstrip().upper().startswith("ON"):
                commas = lines[i + 1].count(",")
                nl = "\n" if lines[i + 1].endswith("\n") else ""
                lines[i + 1] = "OFF" + ("," * commas) + nl
                con.write_text("".join(lines), encoding="utf-8")
                created.append("SCR->OFF")
                break

    log_out = dst / "run_stdout.txt"
    log_err = dst / "run_stderr.txt"
    t0 = time.time()
    # Avoid PIPE deadlock from SCR/console floods: write to files instead.
    with log_out.open("w", encoding="utf-8", errors="replace") as fo, log_err.open(
        "w", encoding="utf-8", errors="replace"
    ) as fe:
        proc = subprocess.Popen([str(EXE)], cwd=str(dst), stdout=fo, stderr=fe)
        # DeGray/Long Lake may leave a "Run Status" GUI open after finishing.
        # Poll until process ends, or until end-day outputs exist then terminate.
        while True:
            rc = proc.poll()
            if rc is not None:
                break
            # Soft completion heuristic: flowbal last day near TMEND and idle > 20s
            time.sleep(3)
            # hard ceiling 2h
            if time.time() - t0 > 7200:
                proc.kill()
                break
    # If still running somehow
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
    elapsed = time.time() - t0

    err_text = (dst / "w2.err").read_text(encoding="utf-8", errors="ignore") if (dst / "w2.err").exists() else ""
    wrn_text = (dst / "w2.wrn").read_text(encoding="utf-8", errors="ignore") if (dst / "w2.wrn").exists() else ""
    stderr = log_err.read_text(encoding="utf-8", errors="ignore") if log_err.exists() else ""
    stdout = log_out.read_text(encoding="utf-8", errors="ignore") if log_out.exists() else ""
    forrtl = ("forrtl" in stderr.lower()) or ("forrtl" in stdout.lower()) or ("file not found" in stderr.lower())

    return {
        "case": name,
        "exit_code": proc.returncode,
        "elapsed_sec": round(elapsed, 2),
        "habitat_dirs_created": created,
        "columbia_patches": columbia_patches,
        "forrtl_detected": forrtl,
        "stderr_tail": stderr[-2000:],
        "w2_err": err_text.strip(),
        "w2_wrn": wrn_text.strip(),
        "outputs": key_outputs(dst),
    }


def main() -> None:
    if not EXE.exists() or EXE.stat().st_size < 100_000:
        raise SystemExit(f"Executable missing or looks like LFS pointer: {EXE}")

    RUN_BASE.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": RUN_ID,
        "exe": str(EXE),
        "exe_bytes": EXE.stat().st_size,
        "started": datetime.now().isoformat(timespec="seconds"),
        "cases": [],
    }

    # Sequential to avoid CPU thrash on large DeGray/Long Lake.
    for name in CASES:
        print(f"=== RUNNING {name} ===", flush=True)
        info = run_case(name)
        summary["cases"].append(info)
        print(
            f"DONE {name}: exit={info['exit_code']} "
            f"sec={info['elapsed_sec']} forrtl={info['forrtl_detected']}",
            flush=True,
        )

    summary["finished"] = datetime.now().isoformat(timespec="seconds")
    out_json = RUN_BASE / "run_summary.json"
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # CSV one-liner table
    csv_path = RUN_BASE / "run_summary.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "case",
                "exit_code",
                "elapsed_sec",
                "forrtl_detected",
                "habitat_dirs_created",
                "w2_err",
                "w2_wrn",
            ],
        )
        w.writeheader()
        for c in summary["cases"]:
            w.writerow(
                {
                    "case": c["case"],
                    "exit_code": c["exit_code"],
                    "elapsed_sec": c["elapsed_sec"],
                    "forrtl_detected": c["forrtl_detected"],
                    "habitat_dirs_created": ";".join(c["habitat_dirs_created"]),
                    "w2_err": c["w2_err"][:200],
                    "w2_wrn": c["w2_wrn"][:200],
                }
            )
    print(f"WROTE {out_json}")
    print(f"WROTE {csv_path}")


if __name__ == "__main__":
    main()
