#!/usr/bin/env python3
"""Compare Bonneville TSR output with CCIW tailwater TDG/temperature observations."""
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
MISSING = -900.0


def metrics(obs: np.ndarray, sim: np.ndarray) -> dict:
    d = sim - obs
    mae = float(np.mean(np.abs(d)))
    rmse = float(np.sqrt(np.mean(d**2)))
    span = float(np.max(obs) - np.min(obs))
    nrmse = float(rmse / span) if span > 0 else float("nan")
    # Nash-Sutcliffe
    den = float(np.sum((obs - np.mean(obs)) ** 2))
    nse = float(1.0 - np.sum(d**2) / den) if den > 0 else float("nan")
    return {
        "n": int(len(obs)),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "nrmse": None if np.isnan(nrmse) else round(nrmse, 4),
        "nse": None if np.isnan(nse) else round(nse, 4),
        "obs_min": round(float(np.min(obs)), 4),
        "obs_max": round(float(np.max(obs)), 4),
        "sim_min": round(float(np.min(sim)), 4),
        "sim_max": round(float(np.max(sim)), 4),
    }


def load_obs(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=2)
    df["JDAY"] = pd.to_numeric(df["JDAY"], errors="coerce")
    df["TDG"] = pd.to_numeric(df["Total dissolved gas"], errors="coerce")
    df["TEMP"] = pd.to_numeric(df["Temperature"], errors="coerce")
    df = df.dropna(subset=["JDAY"])
    return df[(df["JDAY"] >= 40544) & (df["JDAY"] <= 40910)].copy()


def load_tsr(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    if "JDAY" not in df.columns:
        raise RuntimeError(f"No JDAY in {path}")
    df["JDAY"] = pd.to_numeric(df["JDAY"], errors="coerce")
    return df


def pick_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in cols:
            return cols[name.lower()]
        for k, orig in cols.items():
            if name.lower() in k:
                return orig
    return None


def align(obs_s: pd.Series, sim_s: pd.Series, obs_j: np.ndarray, sim_j: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # nearest-neighbor in time within 1 hour
    out_o, out_s = [], []
    sim_j = np.asarray(sim_j, dtype=float)
    sim_v = np.asarray(sim_s, dtype=float)
    for j, v in zip(obs_j, obs_s):
        if not np.isfinite(v) or v <= MISSING:
            continue
        k = int(np.argmin(np.abs(sim_j - j)))
        if abs(sim_j[k] - j) <= 0.05 and np.isfinite(sim_v[k]) and sim_v[k] > MISSING:
            out_o.append(float(v))
            out_s.append(float(sim_v[k]))
    return np.array(out_o), np.array(out_s)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    obs_path = RUN / "CCIW_TDG_Temp_2011-2015.csv"
    if not obs_path.exists():
        raise SystemExit(f"Missing obs: {obs_path}")
    obs = load_obs(obs_path)

    tsr_files = sorted(RUN.glob("tsr_*.csv")) + sorted(RUN.glob("BON_tsr*.csv"))
    if not tsr_files:
        raise SystemExit(f"No TSR files in {RUN}")

    rows = []
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    for fp in tsr_files:
        sim = load_tsr(fp)
        tdg_col = pick_col(sim, ["TDG", "N2SAT", "TDG(%)", "TDG %"])
        t2_col = pick_col(sim, ["T2(C)", "T2", "TEMP"])
        for var, ocol, scol in [
            ("TDG_pct", "TDG", tdg_col),
            ("Temperature_C", "TEMP", t2_col),
        ]:
            if scol is None:
                rows.append({"file": fp.name, "variable": var, "status": "missing_sim_column"})
                continue
            o, s = align(obs[ocol], sim[scol], obs["JDAY"].to_numpy(), sim["JDAY"].to_numpy())
            if len(o) < 10:
                rows.append({"file": fp.name, "variable": var, "status": "too_few_pairs", "n": int(len(o))})
                continue
            m = metrics(o, s)
            m.update({"file": fp.name, "variable": var, "status": "ok", "sim_column": scol})
            rows.append(m)

            fig, ax = plt.subplots(figsize=(11, 4.2))
            ax.plot(obs["JDAY"], obs[ocol].where(obs[ocol] > MISSING), ".", ms=2, alpha=0.5, label="CCIW 观测")
            ax.plot(sim["JDAY"], sim[scol], "-", lw=1.0, label=f"模型 {fp.name}")
            ax.set_xlabel("JDAY（Excel 序列日，2011 年 ≈ 40544–40909）")
            ax.set_ylabel(var)
            ax.set_title(f"Bonneville 尾水 {var}：模型 vs CCIW")
            ax.legend()
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            fig.savefig(OUT / f"Bonneville_{fp.stem}_{var}_timeseries.png", dpi=140)
            plt.close(fig)

            fig, ax = plt.subplots(figsize=(5.2, 5.2))
            lim = [min(o.min(), s.min()), max(o.max(), s.max())]
            ax.plot(lim, lim, "k--", lw=1, label="1:1")
            ax.scatter(o, s, s=8, alpha=0.35)
            ax.set_xlabel("观测")
            ax.set_ylabel("模拟")
            ax.set_title(f"{var}  1:1  MAE={m['mae']}  RMSE={m['rmse']}  NSE={m['nse']}")
            ax.set_aspect("equal", adjustable="box")
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            fig.savefig(OUT / f"Bonneville_{fp.stem}_{var}_scatter.png", dpi=140)
            plt.close(fig)

    (OUT / "obs_metrics.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(OUT / "obs_metrics.csv", index=False, encoding="utf-8-sig")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
