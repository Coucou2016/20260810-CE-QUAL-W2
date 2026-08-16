#!/usr/bin/env python3
"""Compare SYSTDG's own TDG output (not N2/DO-derived c_wdo) with CCIW."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
RUN = ROOT / "05_REPRO_RUNS" / "run_20260814_bonneville" / "Bonneville_SYSTDG"
OUT = ROOT / "05_REPRO_RUNS" / "run_20260814_bonneville" / "analysis"
MISSING = -90.0


def metrics(obs, sim):
    d = sim - obs
    mae = float(np.mean(np.abs(d)))
    rmse = float(np.sqrt(np.mean(d**2)))
    span = float(np.max(obs) - np.min(obs))
    nrmse = float(rmse / span) if span > 0 else float("nan")
    den = float(np.sum((obs - np.mean(obs)) ** 2))
    nse = float(1.0 - np.sum(d**2) / den) if den > 0 else float("nan")
    return {
        "n": int(len(obs)),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "nrmse": None if np.isnan(nrmse) else round(nrmse, 4),
        "nse": None if np.isnan(nse) else round(nse, 4),
        "obs_min": round(float(np.min(obs)), 2),
        "obs_max": round(float(np.max(obs)), 2),
        "sim_min": round(float(np.min(sim)), 2),
        "sim_max": round(float(np.max(sim)), 2),
    }


def align(oj, ov, sj, sv, tol=0.6):
    sj = np.asarray(sj, float)
    sv = np.asarray(sv, float)
    oo, ss = [], []
    for j, v in zip(oj, ov):
        if not np.isfinite(v) or v <= MISSING:
            continue
        k = int(np.argmin(np.abs(sj - j)))
        if abs(sj[k] - j) <= tol and np.isfinite(sv[k]) and sv[k] > 50:
            oo.append(float(v))
            ss.append(float(sv[k]))
    return np.array(oo), np.array(ss)


def load_systdg_tdg() -> pd.DataFrame:
    df = pd.read_csv(RUN / "TDGTarget_output.csv", skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df["JDAY"] = pd.to_numeric(df["JDAY"], errors="coerce")
    df["TDG"] = pd.to_numeric(df["TDG"], errors="coerce")
    return df.dropna(subset=["JDAY", "TDG"])


def target_at(jday: np.ndarray) -> np.ndarray:
    dyn = pd.read_csv(RUN / "TDGdyntarget.csv", skiprows=2)
    dyn.columns = [c.strip() for c in dyn.columns]
    jj = pd.to_numeric(dyn["JDAY"], errors="coerce").to_numpy()
    vv = pd.to_numeric(dyn["TDG (%)"], errors="coerce").to_numpy()
    out = np.empty_like(jday, dtype=float)
    for i, j in enumerate(jday):
        k = int(np.searchsorted(jj, j, side="right") - 1)
        k = max(0, min(k, len(vv) - 1))
        out[i] = vv[k]
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    obs = pd.read_csv(RUN / "CCIW_TDG_Temp_2011-2015.csv", skiprows=2)
    obs["JDAY"] = pd.to_numeric(obs["JDAY"], errors="coerce")
    obs["TDG"] = pd.to_numeric(obs["Total dissolved gas"], errors="coerce")
    obs = obs[(obs["JDAY"] >= 40544) & (obs["JDAY"] <= 40910)]
    sim = load_systdg_tdg()
    o, s = align(obs["JDAY"], obs["TDG"], sim["JDAY"], sim["TDG"])
    rows = [{"pair": "SYSTDG_TDG_vs_CCIW", "status": "ok", **metrics(o, s)}]
    hi = o > 120
    if hi.sum() >= 10:
        rows.append({"pair": "SYSTDG_TDG_vs_CCIW_obsGT120", "status": "ok", **metrics(o[hi], s[hi])})
    lo = o <= 120
    rows.append({"pair": "SYSTDG_TDG_vs_CCIW_obsLE120", "status": "ok", **metrics(o[lo], s[lo])})

    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.plot(obs["JDAY"], obs["TDG"].where(obs["TDG"] > 0), ".", ms=2, alpha=0.4, label="CCIW 坝下观测")
    ax.plot(sim["JDAY"], sim["TDG"], "-", lw=1.2, label="SYSTDG TDG_TDG（日）")
    ax.plot(sim["JDAY"], target_at(sim["JDAY"].to_numpy()), "--", color="tab:red", lw=1.1, label="TDGTA 目标 115/120%")
    ax.set_xlabel("JDAY")
    ax.set_ylabel("TDG %")
    m0 = rows[0]
    ax.set_title(f"SYSTDG 自身 TDG vs CCIW  MAE={m0['mae']} NSE={m0['nse']}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "Bonneville_SYSTDG_TDG_vs_CCIW_timeseries.png", dpi=140)
    plt.close()

    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    lim = [min(o.min(), s.min()), max(o.max(), s.max())]
    ax.plot(lim, lim, "k--", lw=1)
    ax.scatter(o, s, s=10, alpha=0.4)
    ax.set_xlabel("CCIW 观测 TDG %")
    ax.set_ylabel("SYSTDG TDG %")
    ax.set_title(f"SYSTDG TDG 1:1  NSE={m0['nse']}")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "Bonneville_SYSTDG_TDG_vs_CCIW_scatter.png", dpi=140)
    plt.close()

    (OUT / "systdg_tdg_metrics.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
