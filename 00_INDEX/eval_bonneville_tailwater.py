#!/usr/bin/env python3
"""Compare dam-outflow (seg 76) TDG/T with CCIW using W2's TDG formula."""
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
    }


def load_csv_skip(path: Path, usecols: list[int] | None = None) -> pd.DataFrame:
    names = None
    skip = 0
    for i, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        s = raw.strip()
        if not s or s.startswith("$"):
            continue
        if s.upper().startswith("JDAY"):
            names = [c.strip() for c in s.split(",") if c.strip()]
            skip = i + 1
            break
    if not names:
        raise RuntimeError(f"No JDAY header in {path}")
    n = len(usecols) if usecols is not None else len(names)
    df = pd.read_csv(
        path,
        skiprows=skip,
        header=None,
        usecols=list(range(n)),
        names=names[:n],
        engine="python",
    )
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["JDAY"])


def tdg_from_n2_do(n2, do, t_c, palt_atm, tdew_c):
    """W2 withdrawal.f90: TDG% = 100*(0.79*N2/n2sat + 0.21*DO/dosat)."""
    dosat = np.exp(7.7117 - 1.31403 * np.log(t_c + 45.93)) * palt_atm
    ea = np.exp(2.3026 * (7.5 * tdew_c / (tdew_c + 237.3) + 0.6609)) * 0.001316
    n2sat = 1.5568e6 * 0.79 * (palt_atm - ea) * (1.8816e-5 - 4.116e-7 * t_c + 4.6e-9 * t_c**2)
    return 100.0 * (0.79 * (n2 / n2sat) + 0.21 * (do / dosat))


def align(oj, ov, sj, sv):
    out_o, out_s = [], []
    sj = np.asarray(sj, float)
    sv = np.asarray(sv, float)
    for j, v in zip(oj, ov):
        if not np.isfinite(v) or v <= MISSING:
            continue
        k = int(np.argmin(np.abs(sj - j)))
        if abs(sj[k] - j) <= 0.05 and np.isfinite(sv[k]) and sv[k] > MISSING:
            out_o.append(float(v))
            out_s.append(float(sv[k]))
    return np.array(out_o), np.array(out_s)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    obs = pd.read_csv(RUN / "CCIW_TDG_Temp_2011-2015.csv", skiprows=2)
    obs["JDAY"] = pd.to_numeric(obs["JDAY"], errors="coerce")
    obs["TDG"] = pd.to_numeric(obs["Total dissolved gas"], errors="coerce")
    obs["TEMP"] = pd.to_numeric(obs["Temperature"], errors="coerce")
    obs = obs[(obs["JDAY"] >= 40544) & (obs["JDAY"] <= 40910)]

    met = pd.read_csv(RUN / "HOXO_DLS_BON_2011_2015_MET_withBP.csv", skiprows=2)
    met.columns = [c.strip() for c in met.columns]
    met["JDAY"] = pd.to_numeric(met["JDAY"], errors="coerce")
    met["TDEW_C"] = pd.to_numeric(met["TDEW_C"], errors="coerce")
    met["BP_mmHg"] = pd.to_numeric(met["BP_mmHg"], errors="coerce")

    cwo = load_csv_skip(RUN / "c_wdo_76.csv")
    two = load_csv_skip(RUN / "t_wdo_76.csv")
    tsr = pd.read_csv(RUN / "BON_tsr_1_seg40.csv", skipinitialspace=True)
    tsr.columns = [c.strip() for c in tsr.columns]

    tw = pd.merge(cwo[["JDAY", "N2", "DO"]], two[["JDAY", "T(C)"]], on="JDAY", how="inner")
    met_m = met[["JDAY", "TDEW_C", "BP_mmHg"]].dropna(subset=["JDAY"]).sort_values("JDAY")
    tw = pd.merge_asof(
        tw.sort_values("JDAY"),
        met_m,
        on="JDAY",
        direction="nearest",
        tolerance=0.05,
    )
    tw = tw.dropna(subset=["N2", "DO", "T(C)", "TDEW_C", "BP_mmHg"])
    tw["PALT"] = tw["BP_mmHg"] / 760.0
    tw["TDG"] = tdg_from_n2_do(tw["N2"], tw["DO"], tw["T(C)"], tw["PALT"], tw["TDEW_C"])

    # validate formula on in-reservoir TSR
    tsr_m = pd.merge_asof(
        tsr[["JDAY", "N2", "DO", "T2(C)", "TDG"]].sort_values("JDAY"),
        met_m,
        on="JDAY",
        direction="nearest",
        tolerance=0.05,
    )
    tsr_m["PALT"] = tsr_m["BP_mmHg"] / 760.0
    tsr_m["TDG_rec"] = tdg_from_n2_do(
        tsr_m["N2"], tsr_m["DO"], tsr_m["T2(C)"], tsr_m["PALT"], tsr_m["TDEW_C"]
    )
    ok = (
        np.isfinite(tsr_m["TDG"])
        & np.isfinite(tsr_m["TDG_rec"])
        & (tsr_m["TDG"] > 1.0)
        & (tsr_m["TDG_rec"] > 1.0)
    )
    recon = metrics(tsr_m.loc[ok, "TDG"].to_numpy(), tsr_m.loc[ok, "TDG_rec"].to_numpy())

    rows = [{"source": "TSR_seg40_formula_vs_W2_TDG", **recon}]
    plots = []

    o, s = align(obs["JDAY"], obs["TDG"], tw["JDAY"], tw["TDG"])
    if len(o) < 10:
        raise SystemExit(f"too few TDG pairs: {len(o)}")
    m = metrics(o, s)
    m.update({"source": "c_wdo_76_TDG_vs_CCIW", "status": "ok"})
    rows.append(m)
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(obs["JDAY"], obs["TDG"].where(obs["TDG"] > 0), ".", ms=2, alpha=0.45, label="CCIW 坝下观测 TDG")
    ax.plot(tw["JDAY"], tw["TDG"], "-", lw=1, label="坝段 76 下泄 TDG（由 N2+DO 按 W2 公式）")
    ax.set_xlabel("JDAY")
    ax.set_ylabel("TDG %")
    ax.set_title(f"尾水 TDG 对照  MAE={m['mae']} RMSE={m['rmse']} NSE={m['nse']}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p = OUT / "Bonneville_tailwater_TDG_timeseries.png"
    fig.savefig(p, dpi=140)
    plt.close()
    plots.append(str(p))

    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    lim = [min(o.min(), s.min()), max(o.max(), s.max())]
    ax.plot(lim, lim, "k--", lw=1)
    ax.scatter(o, s, s=8, alpha=0.35)
    ax.set_xlabel("CCIW 观测 TDG %")
    ax.set_ylabel("seg76 下泄 TDG %")
    ax.set_title(f"尾水 TDG 1:1  NSE={m['nse']}")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p = OUT / "Bonneville_tailwater_TDG_scatter.png"
    fig.savefig(p, dpi=140)
    plt.close()
    plots.append(str(p))

    o, s = align(obs["JDAY"], obs["TEMP"], tw["JDAY"], tw["T(C)"])
    m = metrics(o, s)
    m.update({"source": "t_wdo_76_T_vs_CCIW", "status": "ok"})
    rows.append(m)
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(obs["JDAY"], obs["TEMP"].where(obs["TEMP"] > -90), ".", ms=2, alpha=0.45, label="CCIW 水温")
    ax.plot(tw["JDAY"], tw["T(C)"], "-", lw=1, label="坝段 76 下泄水温")
    ax.set_xlabel("JDAY")
    ax.set_ylabel("T ℃")
    ax.set_title(f"尾水水温对照  MAE={m['mae']} RMSE={m['rmse']} NSE={m['nse']}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p = OUT / "Bonneville_tailwater_Temp_timeseries.png"
    fig.savefig(p, dpi=140)
    plt.close()
    plots.append(str(p))

    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    lim = [min(o.min(), s.min()), max(o.max(), s.max())]
    ax.plot(lim, lim, "k--", lw=1)
    ax.scatter(o, s, s=8, alpha=0.35)
    ax.set_xlabel("CCIW 观测 ℃")
    ax.set_ylabel("seg76 下泄 ℃")
    ax.set_title(f"尾水水温 1:1  NSE={m['nse']}")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p = OUT / "Bonneville_tailwater_Temp_scatter.png"
    fig.savefig(p, dpi=140)
    plt.close()
    plots.append(str(p))

    (OUT / "tailwater_metrics.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(OUT / "tailwater_metrics.csv", index=False, encoding="utf-8-sig")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
