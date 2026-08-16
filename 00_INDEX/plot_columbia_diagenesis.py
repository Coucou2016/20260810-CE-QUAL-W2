#!/usr/bin/env python3
"""Plot Columbia SED_DIAG ON outputs vs the SED_DIAG OFF baseline."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
ON = ROOT / "05_REPRO_RUNS/run_20260814_columbia_diag/Columbia Slough Estuary"
OFF = ROOT / "05_REPRO_RUNS/run_20260811_fixed/Columbia Slough Estuary"
OUT = ROOT / "05_REPRO_RUNS/run_20260814_columbia_diag/analysis"
SEGS = [2, 13, 33, 45, 49]


def load_tsr(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df["JDAY"] = pd.to_numeric(df["JDAY"], errors="coerce")
    return df


def pick(df: pd.DataFrame, name: str) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    if name.lower() in cols:
        return cols[name.lower()]
    for k, orig in cols.items():
        if name.lower() in k.lower():
            return orig
    return None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    sod = pd.read_csv(ON / "SedimentDiagenesis" / "Diagenesis_SOD.csv")
    # col0=label, col1=JDAY, cols 2..52 = segs 1..51 instantaneous
    jday = pd.to_numeric(sod.iloc[:, 1], errors="coerce")
    fig, ax = plt.subplots(figsize=(11, 4.2))
    for s in SEGS:
        ax.plot(jday, pd.to_numeric(sod.iloc[:, 1 + s], errors="coerce"), lw=1.2, label=f"seg {s}")
    ax.set_xlabel("JDAY")
    ax.set_ylabel("SOD gO2 m$^{-2}$ d$^{-1}$")
    ax.set_title("Columbia Slough 底泥耗氧率 SOD（SED_DIAG ON）")
    ax.legend(ncol=5)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "Columbia_diagenesis_SOD_timeseries.png", dpi=140)
    plt.close()

    on = load_tsr(ON / "tsr_1_seg45.csv")
    off = load_tsr(OFF / "tsr_1_seg45.csv")
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.2), sharex=True)
    for ax, var in zip(axes, ["DO", "NH4"]):
        c_on, c_off = pick(on, var), pick(off, var)
        ax.plot(off["JDAY"], off[c_off], "--", lw=1.2, label=f"SED_DIAG OFF {var}")
        ax.plot(on["JDAY"], on[c_on], "-", lw=1.2, label=f"SED_DIAG ON {var}")
        ax.set_ylabel(var)
        ax.legend()
        ax.grid(True, alpha=0.3)
    axes[0].set_title("Columbia seg45：成岩开/关对照")
    axes[1].set_xlabel("JDAY")
    fig.tight_layout()
    fig.savefig(OUT / "Columbia_diagenesis_DO_NH4_vs_off.png", dpi=140)
    plt.close()

    # last-day SOD along segments (instantaneous block)
    last = sod.iloc[-1]
    inst = pd.to_numeric(last.iloc[2:53], errors="coerce").to_numpy()
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.plot(np.arange(1, 52), inst, "o-", ms=3)
    ax.set_xlabel("segment")
    ax.set_ylabel("SOD gO2 m$^{-2}$ d$^{-1}$")
    ax.set_title(f"Columbia 沿程 SOD（JDAY={float(last.iloc[1]):.1f}）")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "Columbia_diagenesis_SOD_plan.png", dpi=140)
    plt.close()

    do_on = pd.to_numeric(on[pick(on, "DO")], errors="coerce")
    do_off = pd.to_numeric(off[pick(off, "DO")], errors="coerce")
    n = min(len(do_on), len(do_off))
    d = (do_on.iloc[:n] - do_off.iloc[:n]).to_numpy()
    summary = {
        "sod_files": sorted(p.name for p in (ON / "SedimentDiagenesis").glob("Diagenesis_*.csv")),
        "n_sod_rows": int(len(sod)),
        "sod_last_jday": float(last.iloc[1]),
        "sod_last_mean_wet": float(np.nanmean(inst[inst > 0])) if np.any(inst > 0) else 0.0,
        "seg45_DO_mean_on": float(np.nanmean(do_on)),
        "seg45_DO_mean_off": float(np.nanmean(do_off)),
        "seg45_DO_mean_diff_on_minus_off": float(np.nanmean(d)),
        "note": "DeGray W2_diagenesis.npt adapted: region-2 end seg 31→50. Not Columbia-calibrated.",
    }
    (OUT / "columbia_diag_metrics.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
