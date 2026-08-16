#!/usr/bin/env python3
"""Assemble nhr_dlt_scan.json and figures from Long Lake DLTMAX scan dirs."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
SCAN_ROOT = ROOT / "05_REPRO_RUNS" / "run_20260815_ll_dlt_scan"
OUT_JSON = ROOT / "06_PAPER" / "analysis" / "nhr_dlt_scan.json"
FIG_DIR = ROOT / "06_PAPER" / "figures"

sys.path.insert(0, str(ROOT / "00_INDEX"))
from parse_nhr import parse_nhr  # noqa: E402


def collect() -> dict:
    jobs = []
    for d in sorted(SCAN_ROOT.iterdir()):
        if not d.is_dir() or not (d / "w2_con.csv").exists():
            continue
        meta = {}
        mp = d / "scan_meta.json"
        if mp.exists():
            meta = json.loads(mp.read_text(encoding="utf-8"))
        rec = parse_nhr(d, window=(30.0, 40.0))
        nhr = rec["nhr"]
        jobs.append(
            {
                "name": d.name,
                "dir": str(d),
                "dltmax_window_30_40": meta.get("dltmax_window_30_40"),
                "dltf_window_30_40": meta.get("dltf_window_30_40"),
                "dltinter": meta.get("dltinter"),
                "completed": rec["completed"],
                "last_jday": rec["last_jday"],
                "neg_surface_thickness_count": nhr["neg_surface_thickness_count"],
                "add_layer_count": nhr["add_layer_count"],
                "subtract_layer_count": nhr["subtract_layer_count"],
                "low_water_count": nhr["low_water_count"],
                "dltmin_reduced_count": nhr["dltmin_reduced_count"],
                "dltmin_set_count": nhr["dltmin_set_count"],
                "dltmin_hint_count": nhr["dltmin_hint_count"],
                "exit_zero_masks_rollback": nhr.get("exit_zero_masks_rollback"),
                "snp_runtime": nhr.get("snp_runtime"),
                "dlt_trajectory": nhr.get("dlt_trajectory"),
                "neg_events": nhr.get("neg_surface_thickness_events"),
                "add_layer_jdays": nhr.get("add_layer_jdays"),
                "subtract_layer_jdays": nhr.get("subtract_layer_jdays"),
                "full_nhr": rec,
            }
        )
    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "scan": "Long Lake DLTMAX at DLTD=30 (JDAY 30-40 window); official knot=100 s",
        "source_dir": str(SCAN_ROOT),
        "n_jobs": len(jobs),
        "jobs": jobs,
    }


def _series(jobs: list[dict], inter: str) -> list[dict]:
    rows = [j for j in jobs if j.get("dltinter") == inter and j.get("dltmax_window_30_40") is not None]
    rows.sort(key=lambda j: float(j["dltmax_window_30_40"]))
    return rows


def _monotonic_report(xs: list[float], ys: list[int]) -> dict:
    """Is y monotone decreasing in x (the 'smaller DLTMAX is safer' intuition)?"""
    if len(ys) < 2:
        return {"n": len(ys), "monotone_decreasing": None, "nonmonotonic": None}
    dec = all(ys[i] >= ys[i + 1] for i in range(len(ys) - 1))
    inc = all(ys[i] <= ys[i + 1] for i in range(len(ys) - 1))
    report = {
        "dltmax": xs,
        "neg_counts": ys,
        "monotone_decreasing": dec,
        "monotone_increasing": inc,
        "nonmonotonic": (not dec) and (not inc),
        "min_count": min(ys),
        "max_count": max(ys),
        "count_at_official_100": next((y for x, y in zip(xs, ys) if abs(x - 100) < 1e-9), None),
        "tighter_than_official_worse": None,
        "opposes_tighter_is_safer": False,
    }
    if 20.0 in xs and 100.0 in xs:
        y20 = ys[xs.index(20.0)]
        y100 = ys[xs.index(100.0)]
        report["tighter_than_official_worse"] = y20 > y100
        report["opposes_tighter_is_safer"] = y20 > y100
    return report


def plot_scan(payload: dict) -> list[str]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    jobs = payload["jobs"]
    written = []

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
    for ax, inter, title in zip(
        axes,
        ("ON", "OFF"),
        (
            "DLTINTER=ON: interpolated schedule (toward JDAY-40 1800 s)",
            "DLTINTER=OFF: stepwise window cap",
        ),
    ):
        rows = _series(jobs, inter)
        if not rows:
            ax.set_title(title + "\n(no completed points)")
            continue
        xs = [float(r["dltmax_window_30_40"]) for r in rows]
        ys = [int(r["neg_surface_thickness_count"]) for r in rows]
        colors = ["#c0392b" if abs(x - 100) < 1e-9 else "#2471a3" for x in xs]
        ax.plot(xs, ys, "-o", color="#1f4e79", lw=1.6, ms=7, zorder=2)
        ax.scatter(xs, ys, c=colors, s=55, zorder=3, edgecolors="k", linewidths=0.4)
        for r, x, y in zip(rows, xs, ys):
            win = (r.get("dlt_trajectory") or {}).get("window") or {}
            wmax = win.get("dlt_max_s")
            label = str(y)
            if wmax is not None:
                label = f"{y}\n(win max {wmax:.0f}s)"
            ax.annotate(
                label,
                (x, y),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=7,
            )
        ax.axvline(100, color="#888", ls="--", lw=0.8, label="official DLTMAX knot=100 s")
        ax.set_xlabel("DLTMAX schedule knot at JDAY 30 (s)\n≠ realized window Δt when DLTINTER=ON")
        ax.set_title(title, fontsize=10)
        ax.set_xticks(xs)
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("Negative surface layer thickness events")
    fig.suptitle(
        "Long Lake: negative-thickness warnings vs JDAY-30 DLTMAX schedule knot\n"
        "(point labels: TSR-sampled window max DLT; knot ≠ hard window cap under DLTINTER=ON)",
        fontsize=11,
    )
    fig.tight_layout()
    p1 = FIG_DIR / "nhr_dltmax_neg_thickness.png"
    fig.savefig(p1, dpi=160)
    plt.close(fig)
    written.append(str(p1))

    # Companion: add/sub + dltmin hints
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=False)
    for ax, inter, title in zip(axes, ("ON", "OFF"), ("DLTINTER=ON", "DLTINTER=OFF")):
        rows = _series(jobs, inter)
        if not rows:
            continue
        xs = np.array([float(r["dltmax_window_30_40"]) for r in rows])
        ax.plot(xs, [r["add_layer_count"] for r in rows], "-s", label="Add layer", color="#1e8449")
        ax.plot(xs, [r["subtract_layer_count"] for r in rows], "-^", label="Subtract layer", color="#b9770e")
        ax.plot(xs, [r["dltmin_reduced_count"] for r in rows], "-o", label="Rollback to DLTMIN", color="#c0392b")
        ax.axvline(100, color="#888", ls="--", lw=0.8)
        ax.set_xlabel("DLTMAX knot at JDAY 30 (s)")
        ax.set_title(title)
        ax.set_xticks(list(xs))
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Event count")
    fig.suptitle("Long Lake NHR: layer add/sub and DLTMIN rollbacks vs DLTMAX", fontsize=12)
    fig.tight_layout()
    p2 = FIG_DIR / "nhr_dltmax_layers_dltmin.png"
    fig.savefig(p2, dpi=160)
    plt.close(fig)
    written.append(str(p2))

    # Heatmap: DLTINTER x DLTMAX of neg counts
    inters = ["ON", "OFF"]
    dltmaxs = sorted(
        {
            float(j["dltmax_window_30_40"])
            for j in jobs
            if j.get("dltmax_window_30_40") is not None
        }
    )
    mat = np.full((len(inters), len(dltmaxs)), np.nan)
    for i, inter in enumerate(inters):
        for k, dm in enumerate(dltmaxs):
            hits = [
                j
                for j in jobs
                if j.get("dltinter") == inter and j.get("dltmax_window_30_40") is not None and abs(float(j["dltmax_window_30_40"]) - dm) < 1e-9
            ]
            if hits:
                mat[i, k] = hits[0]["neg_surface_thickness_count"]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    masked = np.ma.masked_invalid(mat)
    im = ax.imshow(masked, cmap="YlOrRd", aspect="auto", origin="upper")
    ax.set_xticks(range(len(dltmaxs)))
    ax.set_xticklabels([str(int(x)) for x in dltmaxs])
    ax.set_yticks(range(len(inters)))
    ax.set_yticklabels([f"DLTINTER={s}" for s in inters])
    ax.set_xlabel("DLTMAX knot at JDAY 30 (s)")
    ax.set_title("NHR heatmap: negative surface-layer thickness counts")
    for i in range(mat.shape[0]):
        for k in range(mat.shape[1]):
            v = mat[i, k]
            if np.isfinite(v):
                ax.text(k, i, str(int(v)), ha="center", va="center", color="black", fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="count")
    fig.tight_layout()
    p3 = FIG_DIR / "nhr_dltmax_heatmap.png"
    fig.savefig(p3, dpi=160)
    plt.close(fig)
    written.append(str(p3))
    return written


def analyze(payload: dict) -> dict:
    out = {}
    for inter in ("ON", "OFF"):
        rows = [r for r in _series(payload["jobs"], inter) if r.get("completed")]
        xs = [float(r["dltmax_window_30_40"]) for r in rows]
        ys = [int(r["neg_surface_thickness_count"]) for r in rows]
        out[f"DLTINTER_{inter}"] = _monotonic_report(xs, ys)
    return out


def main() -> None:
    payload = collect()
    payload["monotonicity"] = analyze(payload)
    payload["verdict"] = {
        "exit0_masks_rollback": any(j.get("exit_zero_masks_rollback") for j in payload["jobs"]),
        "nonmonotonic_under_official_dltinter_on": bool(
            (payload["monotonicity"].get("DLTINTER_ON") or {}).get("nonmonotonic")
        ),
        "nonmonotonic_when_dltmax_is_true_cap": bool(
            (payload["monotonicity"].get("DLTINTER_OFF") or {}).get("nonmonotonic")
        ),
        "interoff_eliminates_neg_thickness": all(
            int(j["neg_surface_thickness_count"]) == 0
            for j in payload["jobs"]
            if j.get("dltinter") == "OFF" and j.get("completed")
        ),
        "recommendation": (
            "Keep NHR as a required report item. Treat non-monotonic vs DLTMAX as "
            "conditional on DLTINTER=ON knot interpolation, not as a general CFL result."
        ),
    }
    payload["figures"] = plot_scan(payload)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    # slim copy without full nested nhr duplication in the written file? keep it — paper wants the record
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("wrote", OUT_JSON)
    print("figures:")
    for f in payload["figures"]:
        print(" ", f)
    print(json.dumps(payload["monotonicity"], indent=2))


if __name__ == "__main__":
    main()
