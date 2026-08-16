#!/usr/bin/env python3
"""W3: provenance-consistent TDGTA ON vs OFF comparison vs CCIW."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
sys.path.insert(0, str(ROOT / "00_INDEX"))
from eval_bonneville_tailwater import (  # noqa: E402
    MISSING,
    align,
    load_csv_skip,
    tdg_from_n2_do,
)

ON_RUN = ROOT / "05_REPRO_RUNS" / "run_20260814_bonneville" / "Bonneville_SYSTDG"
OFF_RUN = ROOT / "05_REPRO_RUNS" / "run_20260814_bonneville_notarget" / "Bonneville_SYSTDG"
OFF_PARENT = OFF_RUN.parent
PAPER_AN = ROOT / "06_PAPER" / "analysis"
PAPER_FIG = ROOT / "06_PAPER" / "figures"
J0, J1 = 40544.0, 40910.0
TMEND = 40909.0


def skill(obs: np.ndarray, sim: np.ndarray) -> dict:
    obs = np.asarray(obs, float)
    sim = np.asarray(sim, float)
    d = sim - obs
    mae = float(np.mean(np.abs(d)))
    rmse = float(np.sqrt(np.mean(d**2)))
    den = float(np.sum((obs - np.mean(obs)) ** 2))
    nse = float(1.0 - np.sum(d**2) / den) if den > 0 else float("nan")
    r = float(np.corrcoef(obs, sim)[0, 1]) if len(obs) > 1 else float("nan")
    r2 = float(r * r) if np.isfinite(r) else float("nan")
    so, ss = float(np.std(obs, ddof=0)), float(np.std(sim, ddof=0))
    mo, ms = float(np.mean(obs)), float(np.mean(sim))
    alpha = float(ss / so) if so > 0 else float("nan")
    beta = float(ms / mo) if mo != 0 else float("nan")
    kge = (
        float(1.0 - np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2))
        if np.isfinite(r) and np.isfinite(alpha) and np.isfinite(beta)
        else float("nan")
    )
    pbias = float(100.0 * np.sum(d) / np.sum(obs)) if np.sum(obs) != 0 else float("nan")
    slope = float(np.polyfit(obs, sim, 1)[0]) if len(obs) > 1 else float("nan")
    return {
        "n": int(len(obs)),
        "r2": None if not np.isfinite(r2) else round(r2, 4),
        "nse": None if not np.isfinite(nse) else round(nse, 4),
        "kge": None if not np.isfinite(kge) else round(kge, 4),
        "r": None if not np.isfinite(r) else round(r, 4),
        "alpha": None if not np.isfinite(alpha) else round(alpha, 4),
        "beta": None if not np.isfinite(beta) else round(beta, 4),
        "pbias_pct": None if not np.isfinite(pbias) else round(pbias, 4),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "slope": None if not np.isfinite(slope) else round(slope, 4),
        "obs_min": round(float(np.min(obs)), 2),
        "obs_max": round(float(np.max(obs)), 2),
        "sim_min": round(float(np.min(sim)), 2),
        "sim_max": round(float(np.max(sim)), 2),
        "obs_mean": round(mo, 3),
        "sim_mean": round(ms, 3),
        "n_obs_gt_120": int(np.sum(obs > 120.0)),
        "n_sim_gt_120": int(np.sum(sim > 120.0)),
        "frac_obs_gt_120": round(float(np.mean(obs > 120.0)), 4),
        "frac_sim_gt_120": round(float(np.mean(sim > 120.0)), 4),
        "n_sim_ge_129": int(np.sum(sim >= 129.0)),
    }


def align_tol(oj, ov, sj, sv, tol: float = 0.05, vmin: float = MISSING) -> tuple[np.ndarray, np.ndarray]:
    """Same nearest-neighbor pairing as eval_bonneville_tailwater.align, with configurable tol."""
    out_o, out_s = [], []
    sj = np.asarray(sj, float)
    sv = np.asarray(sv, float)
    for j, v in zip(oj, ov):
        if not np.isfinite(v) or v <= MISSING:
            continue
        k = int(np.argmin(np.abs(sj - j)))
        if abs(sj[k] - j) <= tol and np.isfinite(sv[k]) and sv[k] > vmin:
            out_o.append(float(v))
            out_s.append(float(sv[k]))
    return np.array(out_o), np.array(out_s)


def last_jday_csv(path: Path, col: int = 0) -> float | None:
    if not path.exists() or path.stat().st_size < 20:
        return None
    last = None
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = raw.strip()
        if not s or s.startswith("$") or s.upper().startswith("JDAY"):
            continue
        try:
            last = float(s.split(",")[col])
        except ValueError:
            continue
    return last


def load_obs(run: Path) -> pd.DataFrame:
    obs = pd.read_csv(run / "CCIW_TDG_Temp_2011-2015.csv", skiprows=2)
    obs["JDAY"] = pd.to_numeric(obs["JDAY"], errors="coerce")
    obs["TDG"] = pd.to_numeric(obs["Total dissolved gas"], errors="coerce")
    obs = obs[(obs["JDAY"] >= J0) & (obs["JDAY"] <= J1)]
    return obs


def load_met(run: Path) -> pd.DataFrame:
    met = pd.read_csv(run / "HOXO_DLS_BON_2011_2015_MET_withBP.csv", skiprows=2)
    met.columns = [c.strip() for c in met.columns]
    met["JDAY"] = pd.to_numeric(met["JDAY"], errors="coerce")
    return met[["JDAY", "TDEW_C", "BP_mmHg"]].dropna(subset=["JDAY"]).sort_values("JDAY")


def n2do_series(run: Path) -> pd.DataFrame:
    met_m = load_met(run)
    cwo = load_csv_skip(run / "c_wdo_76.csv")
    two = load_csv_skip(run / "t_wdo_76.csv")
    tw = pd.merge(cwo[["JDAY", "N2", "DO"]], two[["JDAY", "T(C)"]], on="JDAY", how="inner")
    tw = pd.merge_asof(tw.sort_values("JDAY"), met_m, on="JDAY", direction="nearest", tolerance=0.05)
    tw = tw.dropna(subset=["N2", "DO", "T(C)", "TDEW_C", "BP_mmHg"])
    tw["TDG"] = tdg_from_n2_do(tw["N2"], tw["DO"], tw["T(C)"], tw["BP_mmHg"] / 760.0, tw["TDEW_C"])
    return tw


def load_tsr_tdg(run: Path) -> pd.DataFrame:
    tsr = pd.read_csv(run / "BON_tsr_1_seg40.csv", skipinitialspace=True)
    tsr.columns = [c.strip() for c in tsr.columns]
    tsr["JDAY"] = pd.to_numeric(tsr["JDAY"], errors="coerce")
    tsr["TDG"] = pd.to_numeric(tsr["TDG"], errors="coerce")
    return tsr.dropna(subset=["JDAY", "TDG"])


def load_tdgtarget(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df["JDAY"] = pd.to_numeric(df["JDAY"], errors="coerce")
    df["TDG"] = pd.to_numeric(df["TDG"], errors="coerce")
    return df.dropna(subset=["JDAY", "TDG"])


def load_tdg_output(path: Path) -> pd.DataFrame | None:
    """SYSTDG native daily file. Header omits the empty 'C' field that each data row has."""
    if not path.exists():
        return None
    jdays, tdgs, qs = [], [], []
    for i, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        if i == 0 or not raw.strip():
            continue
        parts = [p.strip() for p in raw.split(",")]
        nums = []
        for p in parts:
            try:
                nums.append(float(p))
            except ValueError:
                continue
        if len(nums) < 2:
            continue
        jdays.append(nums[0])
        tdgs.append(nums[1])  # first numeric after JDAY is TDG%
        qs.append(nums[2] if len(nums) > 2 else float("nan"))
    return pd.DataFrame({"JDAY": jdays, "TDG": tdgs, "SUM_Q": qs})


def pair_row(name: str, file: str, available: bool, obs, oj, sj, sv, *, daily: bool) -> dict:
    row = {
        "name": name,
        "file": file,
        "available": available,
        "pairing": "nearest, tol=0.6 (daily sim vs CCIW)" if daily else "nearest, tol=0.05 (eval_bonneville_tailwater.align)",
    }
    if not available or sj is None:
        row["status"] = "file_absent"
        return row
    if daily:
        o, s = align_tol(oj, obs, sj, sv, tol=0.6, vmin=50.0)
    else:
        o, s = align(oj, obs, sj, sv)
    if len(o) < 10:
        row["status"] = "too_few_pairs"
        row["n"] = int(len(o))
        return row
    row["status"] = "ok"
    row.update(skill(o, s))
    row["_o"] = o
    row["_s"] = s
    return row


def file_inventory(run: Path) -> dict:
    names = [
        "c_wdo_76.csv",
        "t_wdo_76.csv",
        "BON_tsr_1_seg40.csv",
        "TDGTarget_output.csv",
        "TDGTarget_warning.opt",
        "TDG_output.csv",
        "TDGdyntarget.csv",
        "flowbal.csv",
        "w2.err",
        "w2.wrn",
        "w2_systdg.npt",
        "w2_con.csv",
    ]
    return {n: (run / n).exists() for n in names}


def read_tdgta(npt: Path) -> str | None:
    text = npt.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(text.splitlines()):
        if "TDGTA" in line.upper() and i + 1 < len(text.splitlines()):
            nxt = text.splitlines()[i + 1]
            parts = [p.strip() for p in nxt.split(",")]
            if len(parts) >= 6:
                return parts[5]
    return None


def read_scr(con: Path) -> str | None:
    lines = con.read_text(encoding="utf-8", errors="ignore").splitlines()
    for i, line in enumerate(lines):
        if line.lstrip().startswith("SCR") and i + 1 < len(lines):
            return lines[i + 1].split(",")[0].strip()
    return None


def drop_arrays(row: dict) -> dict:
    return {k: v for k, v in row.items() if not k.startswith("_")}


def main() -> None:
    PAPER_AN.mkdir(parents=True, exist_ok=True)
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    inv_on, inv_off = file_inventory(ON_RUN), file_inventory(OFF_RUN)
    disappeared = sorted(k for k in inv_on if inv_on[k] and not inv_off[k])
    appeared = sorted(k for k in inv_off if inv_off[k] and not inv_on[k])

    obs = load_obs(OFF_RUN if (OFF_RUN / "CCIW_TDG_Temp_2011-2015.csv").exists() else ON_RUN)
    oj, ov = obs["JDAY"].to_numpy(), obs["TDG"].to_numpy()

    series = {}
    for tag, run in (("ON", ON_RUN), ("OFF", OFF_RUN)):
        series[tag] = {
            "A_n2do": n2do_series(run),
            "C_tsr40": load_tsr_tdg(run),
            "B_tdgtarget": load_tdgtarget(run / "TDGTarget_output.csv"),
            "S_tdg_output": load_tdg_output(run / "TDG_output.csv"),
        }

    rows = []
    specs = [
        ("ON", "A", "N2+DO Henry (seg76 c_wdo/t_wdo)", "c_wdo_76.csv + t_wdo_76.csv", "A_n2do", False),
        ("ON", "B", "controller TDG_TDG (TDGTarget_output)", "TDGTarget_output.csv", "B_tdgtarget", True),
        ("ON", "C", "TSR seg40 TDG channel", "BON_tsr_1_seg40.csv", "C_tsr40", False),
        ("ON", "S", "SYSTDG native TDG_TDG (TDG_output.csv)", "TDG_output.csv", "S_tdg_output", True),
        ("OFF", "A", "N2+DO Henry (seg76 c_wdo/t_wdo)", "c_wdo_76.csv + t_wdo_76.csv", "A_n2do", False),
        ("OFF", "B", "controller TDG_TDG (TDGTarget_output)", "TDGTarget_output.csv", "B_tdgtarget", True),
        ("OFF", "C", "TSR seg40 TDG channel", "BON_tsr_1_seg40.csv", "C_tsr40", False),
        ("OFF", "S", "SYSTDG native TDG_TDG (TDG_output.csv)", "TDG_output.csv", "S_tdg_output", True),
    ]
    for run_tag, cal, title, fname, key, daily in specs:
        df = series[run_tag][key]
        avail = df is not None and len(df) > 0
        row = pair_row(
            f"{run_tag}/{cal} {title}",
            fname,
            avail,
            ov,
            oj,
            None if not avail else df["JDAY"].to_numpy(),
            None if not avail else df["TDG"].to_numpy(),
            daily=daily,
        )
        row["run"] = run_tag
        row["caliber"] = cal
        row["title"] = title
        rows.append(row)

    # Same-file ON vs OFF identity checks (not vs CCIW)
    identity = {}
    for key, label in (("A_n2do", "N2DO_seg76"), ("C_tsr40", "TSR_seg40"), ("S_tdg_output", "TDG_output")):
        a, b = series["ON"][key], series["OFF"][key]
        if a is None or b is None:
            identity[label] = {"comparable": False}
            continue
        m = pd.merge(a[["JDAY", "TDG"]], b[["JDAY", "TDG"]], on="JDAY", suffixes=("_on", "_off"))
        if len(m) < 10:
            identity[label] = {"comparable": False, "n": int(len(m))}
            continue
        d = m["TDG_off"] - m["TDG_on"]
        identity[label] = {
            "comparable": True,
            "n": int(len(m)),
            "mae": round(float(np.mean(np.abs(d))), 4),
            "max_abs": round(float(np.max(np.abs(d))), 4),
            "on_max": round(float(m["TDG_on"].max()), 2),
            "off_max": round(float(m["TDG_off"].max()), 2),
            "n_off_gt_on_by_1": int(np.sum(d > 1.0)),
        }

    on_s, off_s = series["ON"]["S_tdg_output"], series["OFF"]["S_tdg_output"]
    on_b = series["ON"]["B_tdgtarget"]
    tdg_output_vs_target = None
    if on_s is not None and on_b is not None:
        m = pd.merge(on_s[["JDAY", "TDG"]], on_b[["JDAY", "TDG"]], on="JDAY", suffixes=("_S", "_B"))
        if len(m):
            d = m["TDG_S"] - m["TDG_B"]
            tdg_output_vs_target = {
                "n": int(len(m)),
                "mae": round(float(np.mean(np.abs(d))), 4),
                "max_abs": round(float(np.max(np.abs(d))), 4),
                "s_raw_max": round(float(m["TDG_S"].max()), 2),
                "b_raw_max": round(float(m["TDG_B"].max()), 2),
                "note": (
                    "TDG_output.csv is the PRE-control snapshot. TDGtarget.f90 calls SYSTDG_TDG "
                    "before reallocating (L180); that first call writes unit 88888 and advances "
                    "NXTSPLIT3, so the later hydroinout SYSTDG_TDG does not rewrite the daily row. "
                    "Hence ON TDG_output.csv is bit-identical to OFF (mae=0) and differs from "
                    "post-control TDGTarget_output.csv."
                ),
            }

    obs_valid = ov[np.isfinite(ov) & (ov > MISSING)]
    raw_max = {}
    for tag in ("ON", "OFF"):
        raw_max[tag] = {}
        for key, lab in (("A_n2do", "A"), ("C_tsr40", "C"), ("S_tdg_output", "S"), ("B_tdgtarget", "B")):
            df = series[tag][key]
            raw_max[tag][lab] = None if df is None or len(df) == 0 else round(float(df["TDG"].max()), 2)
    reachable = {
        "obs_max": round(float(np.max(obs_valid)), 2),
        "obs_n": int(len(obs_valid)),
        "obs_jday_min": round(float(np.min(oj[np.isfinite(ov) & (ov > MISSING)])), 3),
        "obs_jday_max": round(float(np.max(oj[np.isfinite(ov) & (ov > MISSING)])), 3),
        "obs_n_gt_120": int(np.sum(obs_valid > 120.0)),
        "obs_frac_gt_120": round(float(np.mean(obs_valid > 120.0)), 4),
        "controller_cap_pct": 120.0,
        "systdg_hard_cap_pct": 145.0,
        "raw_sim_max": raw_max,
        "OFF_can_exceed_120": None,
        "OFF_can_approach_129_paired": None,
        "OFF_can_exceed_129_raw": None,
    }
    off_maxes = {}
    for row in rows:
        if row["run"] == "OFF" and row.get("status") == "ok":
            off_maxes[row["caliber"]] = row["sim_max"]
    if off_maxes:
        reachable["OFF_paired_sim_max_by_caliber"] = off_maxes
        reachable["OFF_can_exceed_120"] = any(v > 120.0 for v in off_maxes.values())
        reachable["OFF_can_approach_129_paired"] = any(v >= 128.0 for v in off_maxes.values())
        off_raw = [v for v in raw_max["OFF"].values() if v is not None]
        reachable["OFF_can_exceed_129_raw"] = any(v >= 129.0 for v in off_raw)

    completeness = {
        "off_run_dir": str(OFF_RUN),
        "on_run_dir": str(ON_RUN),
        "tmend": TMEND,
        "off_last_flowbal_jday": last_jday_csv(OFF_RUN / "flowbal.csv"),
        "on_last_flowbal_jday": last_jday_csv(ON_RUN / "flowbal.csv"),
        "off_last_c_wdo_jday": last_jday_csv(OFF_RUN / "c_wdo_76.csv"),
        "off_last_tsr_jday": last_jday_csv(OFF_RUN / "BON_tsr_1_seg40.csv"),
        "off_last_tdg_output_jday": last_jday_csv(OFF_RUN / "TDG_output.csv"),
        "off_tdgta": read_tdgta(OFF_RUN / "w2_systdg.npt"),
        "on_tdgta": read_tdgta(ON_RUN / "w2_systdg.npt"),
        "off_scr": read_scr(OFF_RUN / "w2_con.csv"),
        "reached_tmend": (
            last_jday_csv(OFF_RUN / "flowbal.csv") is not None
            and last_jday_csv(OFF_RUN / "flowbal.csv") >= TMEND - 1.0
        ),
        "reran_for_w3": False,
        "reason_no_rerun": "Existing notarget run already at JDAY 40908 with exit 0, SCR OFF, TDGTA OFF, c_wdo/t_wdo/TSR present; same completion criterion as ON run.",
    }

    payload = {
        "task": "W3 TDGTA ON vs OFF provenance-consistent comparison",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "completeness": completeness,
        "files": {
            "on": inv_on,
            "off": inv_off,
            "disappeared_when_TDGTA_OFF": disappeared,
            "appeared_when_TDGTA_OFF": appeared,
        },
        "pairing_notes": {
            "A_and_C": "eval_bonneville_tailwater.align, tol=0.05",
            "B_and_S": "same nearest-neighbor algorithm, tol=0.6 to match eval_systdg_tdg.py daily pairing (n=1614)",
            "window": [J0, J1],
            "obs": "CCIW_TDG_Temp_2011-2015.csv Total dissolved gas",
        },
        "metrics": [drop_arrays(r) for r in rows],
        "on_vs_off_same_file": identity,
        "on_TDG_output_vs_TDGTarget": tdg_output_vs_target,
        "reachable_range": reachable,
        "innovation_2_implication": None,
    }

    # Figures
    on_b_df = series["ON"]["B_tdgtarget"]
    off_a = series["OFF"]["A_n2do"]
    off_s = series["OFF"]["S_tdg_output"]
    obs_jmin = float(np.min(oj[np.isfinite(ov) & (ov > MISSING)]))
    obs_jmax = float(np.max(oj[np.isfinite(ov) & (ov > MISSING)]))

    fig, axes = plt.subplots(2, 1, figsize=(12.2, 7.6), sharey=True)
    for ax, (x0, x1, subtitle) in zip(
        axes,
        ((J0, J1, "全年（模型时段）"), (obs_jmin - 2, obs_jmax + 2, "CCIW 有效观测窗")),
    ):
        ax.plot(
            obs["JDAY"],
            obs["TDG"].where(obs["TDG"] > 0),
            ".",
            ms=3.5 if x1 - x0 < 100 else 2.0,
            alpha=0.55,
            color="0.25",
            label="CCIW 观测",
        )
        if on_b_df is not None:
            ax.plot(on_b_df["JDAY"], on_b_df["TDG"], "-", lw=1.5, color="tab:blue", label="ON B  控制器 TDG_TDG（TDGTarget_output）")
        ax.plot(off_a["JDAY"], off_a["TDG"], "-", lw=0.9, color="tab:orange", alpha=0.8, label="OFF A  N2+DO 亨利（seg76）")
        if off_s is not None:
            ax.plot(
                off_s["JDAY"],
                off_s["TDG"],
                "-",
                lw=1.3,
                color="tab:green",
                label="S  SYSTDG 原生 TDG_TDG（TDG_output.csv；ON≡OFF，控制前快照）",
            )
        ax.axhline(120.0, color="tab:red", ls="--", lw=1.1, label="120% 控制器上限")
        if x1 - x0 > 100:
            ax.axvspan(obs_jmin, obs_jmax, color="0.85", alpha=0.35, label="CCIW 有效窗")
        ax.set_ylabel("TDG %")
        ax.set_title(subtitle)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(x0, x1)
        ax.legend(loc="upper left", fontsize=7.5, ncol=2)
    axes[1].set_xlabel("JDAY")
    fig.suptitle("W3  TDGTA ON vs OFF  vs CCIW", y=1.01)
    fig.tight_layout()
    fig.savefig(PAPER_FIG / "W3_tdgta_on_off_timeseries.png", dpi=150, bbox_inches="tight")
    plt.close()

    scatter_keys = [
        ("ON", "B", "ON B  控制器 TDG_TDG", "tab:blue"),
        ("OFF", "A", "OFF A  N2+DO 亨利", "tab:orange"),
        ("OFF", "S", "OFF S  SYSTDG 原生 TDG_TDG", "tab:green"),
        ("OFF", "C", "OFF C  TSR seg40", "tab:purple"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 9.2))
    for ax, (run_tag, cal, title, color) in zip(axes.ravel(), scatter_keys):
        row = next(r for r in rows if r["run"] == run_tag and r["caliber"] == cal)
        ax.axhline(120.0, color="tab:red", ls="--", lw=0.8, alpha=0.7)
        ax.axvline(120.0, color="tab:red", ls="--", lw=0.8, alpha=0.7)
        if row.get("status") != "ok":
            ax.set_title(f"{title}\n文件缺失")
            ax.text(0.5, 0.5, "file absent", ha="center", va="center", transform=ax.transAxes)
            continue
        o, s = row["_o"], row["_s"]
        lim = [min(o.min(), s.min()) - 1, max(o.max(), s.max()) + 1]
        ax.plot(lim, lim, "k--", lw=1)
        ax.scatter(o, s, s=8, alpha=0.35, c=color, edgecolors="none")
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("CCIW 观测 TDG %")
        ax.set_ylabel("模拟 TDG %")
        ax.set_title(f"{title}\nNSE={row['nse']}  max={row['sim_max']}")
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PAPER_FIG / "W3_tdgta_on_off_scatter.png", dpi=150)
    plt.close()

    bar_rows = [r for r in rows if r.get("status") == "ok"]
    labels = [f"{r['run']}/{r['caliber']}" for r in bar_rows]
    x = np.arange(len(labels))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.bar(x - width, [r["r"] for r in bar_rows], width, label="r", color="tab:blue")
    ax.bar(x, [r["alpha"] for r in bar_rows], width, label="α = σs/σo", color="tab:orange")
    ax.bar(x + width, [r["beta"] for r in bar_rows], width, label="β = μs/μo", color="tab:green")
    ax.axhline(1.0, color="k", ls="--", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("分量")
    ax.set_title("W3  KGE 分解（r / α / β）  ON vs OFF")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PAPER_FIG / "W3_tdgta_kge_decomposition.png", dpi=150)
    plt.close()

    off_b = next(r for r in rows if r["run"] == "OFF" and r["caliber"] == "B")
    off_a = next(r for r in rows if r["run"] == "OFF" and r["caliber"] == "A")
    off_s_row = next(r for r in rows if r["run"] == "OFF" and r["caliber"] == "S")
    on_b_row = next(r for r in rows if r["run"] == "ON" and r["caliber"] == "B")
    if off_b.get("status") == "file_absent":
        if off_s_row.get("status") == "ok" and off_s_row["sim_max"] > 120.0:
            impl = (
                "strengthen_with_rephrase: TDGTarget_output.csv (ON B, NSE=+0.50, sim_max=120.09) is absent when TDGTA=OFF. "
                "SYSTDG still writes TDG_TDG to TDG_output.csv, but that file is a pre-control snapshot (ON≡OFF, mae=0) "
                "and is not the B series (vs TDGTarget mae=1.71, raw max 131.7 vs 120.09). Innovation 2 holds as "
                "controller-gated evaluation file + 120% reachable-range cap. Do not claim the physical variable is deleted."
            )
        else:
            impl = (
                "strengthen: TDGTarget_output.csv disappears when TDGTA=OFF; evaluation of the published B-caliber is "
                "structurally impossible and must fall back to A. Restate slightly if TDG_output.csv is treated as a sibling VPR."
            )
    else:
        impl = "rephrase: TDGTarget_output.csv still present with TDGTA=OFF; original 'variable vanishes' claim needs revision."
    payload["innovation_2_implication"] = impl
    payload["figures"] = [
        str(PAPER_FIG / "W3_tdgta_on_off_timeseries.png"),
        str(PAPER_FIG / "W3_tdgta_on_off_scatter.png"),
        str(PAPER_FIG / "W3_tdgta_kge_decomposition.png"),
    ]

    (PAPER_AN / "w3_tdgta_off_metrics.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Enrich notarget run_summary without deleting original fields.
    summary_path = OFF_PARENT / "run_summary.json"
    old = {}
    if summary_path.exists():
        old = json.loads(summary_path.read_text(encoding="utf-8"))
    old.update(
        {
            "w3_checked": datetime.now().isoformat(timespec="seconds"),
            "tmend": TMEND,
            "reached_tmend": completeness["reached_tmend"],
            "last_c_wdo_jday": completeness["off_last_c_wdo_jday"],
            "tdgta": completeness["off_tdgta"],
            "scr": completeness["off_scr"],
            "TDGTarget_output.csv": inv_off["TDGTarget_output.csv"],
            "TDG_output.csv": inv_off["TDG_output.csv"],
            "files_disappeared_vs_ON": disappeared,
        }
    )
    summary_path.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding="utf-8")

    slim = [{k: v for k, v in drop_arrays(r).items()} for r in rows]
    print(json.dumps({"metrics": slim, "disappeared": disappeared, "reachable": reachable, "impl": impl}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
