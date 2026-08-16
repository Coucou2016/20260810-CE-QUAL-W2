#!/usr/bin/env python3
"""Check whether Bonneville TDG follows the TDGTA 115/120% target more than CCIW."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eval_bonneville_tailwater import (
    MISSING,
    OUT,
    RUN,
    align,
    load_csv_skip,
    metrics,
    tdg_from_n2_do,
)

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")


def target_at(jday: np.ndarray) -> np.ndarray:
    dyn = pd.read_csv(RUN / "TDGdyntarget.csv", skiprows=2)
    dyn.columns = [c.strip() for c in dyn.columns]
    dyn["JDAY"] = pd.to_numeric(dyn["JDAY"], errors="coerce")
    tdg = pd.to_numeric(dyn["TDG (%)"], errors="coerce")
    jj = dyn["JDAY"].to_numpy()
    vv = tdg.to_numpy()
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

    met = pd.read_csv(RUN / "HOXO_DLS_BON_2011_2015_MET_withBP.csv", skiprows=2)
    met.columns = [c.strip() for c in met.columns]
    met["JDAY"] = pd.to_numeric(met["JDAY"], errors="coerce")
    met_m = met[["JDAY", "TDEW_C", "BP_mmHg"]].dropna(subset=["JDAY"]).sort_values("JDAY")

    cwo = load_csv_skip(RUN / "c_wdo_76.csv")
    two = load_csv_skip(RUN / "t_wdo_76.csv")
    tw = pd.merge(cwo[["JDAY", "N2", "DO"]], two[["JDAY", "T(C)"]], on="JDAY", how="inner")
    tw = pd.merge_asof(tw.sort_values("JDAY"), met_m, on="JDAY", direction="nearest", tolerance=0.05)
    tw = tw.dropna(subset=["N2", "DO", "T(C)", "TDEW_C", "BP_mmHg"])
    tw["TDG"] = tdg_from_n2_do(tw["N2"], tw["DO"], tw["T(C)"], tw["BP_mmHg"] / 760.0, tw["TDEW_C"])
    tw["TARGET"] = target_at(tw["JDAY"].to_numpy())

    tgt_out = pd.read_csv(RUN / "TDGTarget_output.csv", skipinitialspace=True)
    tgt_out.columns = [c.strip() for c in tgt_out.columns]

    o, s = align(obs["JDAY"], obs["TDG"], tw["JDAY"], tw["TDG"])
    rows = [{"pair": "c_wdo76_vs_CCIW", **metrics(o, s)}]
    t_on_obs = target_at(np.asarray(obs.loc[obs["TDG"] > 0, "JDAY"], float))
    o2 = obs.loc[obs["TDG"] > 0, "TDG"].to_numpy()
    # model vs its own TDG target
    rows.append({"pair": "c_wdo76_vs_TDGTA_target", **metrics(tw["TARGET"].to_numpy(), tw["TDG"].to_numpy())})
    rows.append({"pair": "CCIW_vs_TDGTA_target", **metrics(o2[o2 > MISSING], t_on_obs[o2 > MISSING])})

    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.plot(obs["JDAY"], obs["TDG"].where(obs["TDG"] > 0), ".", ms=2, alpha=0.35, label="CCIW 坝下观测")
    ax.plot(tw["JDAY"], tw["TDG"], "-", lw=1, label="seg76 下泄 TDG（TDGTA ON）")
    ax.plot(tw["JDAY"], tw["TARGET"], "--", lw=1.2, color="tab:red", label="TDGTA 目标 115/120%")
    ax.set_xlabel("JDAY")
    ax.set_ylabel("TDG %")
    ax.set_title("TDGTA 开：模型是否在追目标而非复现 CCIW")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "Bonneville_TDGTA_target_overlay.png", dpi=140)
    plt.close()

    (OUT / "tdg_target_diag.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
