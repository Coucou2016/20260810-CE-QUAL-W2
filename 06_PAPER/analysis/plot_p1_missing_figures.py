"""Generate missing P1 figures (Fig. 4/5/7) and copy W4 PNGs into figures/.

Numbers come only from analysis/*.json, w2eval cards, and the CCIW CSV
already used by W3 (same reachable_range window). Does not run W2.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "06_PAPER" / "analysis"
FIGURES = ROOT / "06_PAPER" / "figures"
CARDS = ROOT / "06_PAPER" / "w2eval" / "cards"
CCIW = (
    ROOT
    / "05_REPRO_RUNS"
    / "run_20260814_bonneville"
    / "Bonneville_SYSTDG"
    / "CCIW_TDG_Temp_2011-2015.csv"
)

W4_COPY = [
    "w4_cciw_vs_dart_scatter.png",
    "w4_cciw_vs_dart_timeseries.png",
    "w4_spill_scatter.png",
    "w4_spill_tdgta_vs_dart.png",
    "w4_tdg_annual_max.png",
    "w4_tdg_gt120_annual.png",
]


def load_json(name: str) -> dict:
    with (ANALYSIS / name).open(encoding="utf-8") as f:
        return json.load(f)


def copy_w4() -> list[str]:
    FIGURES.mkdir(parents=True, exist_ok=True)
    done = []
    for name in W4_COPY:
        src = ANALYSIS / name
        dst = FIGURES / name
        if not src.exists():
            print(f"SKIP missing source: {src}")
            continue
        shutil.copy2(src, dst)
        done.append(name)
        print(f"copied {name}")
    return done


def parse_table2_r2(raw: str) -> list[float]:
    """Extract numeric R² values from Table 2 cell text; skip ranges/inequalities."""
    if not raw or not str(raw).strip():
        return []
    s = str(raw).strip()
    if "-" in s and re.search(r"\d\s*-\s*\d", s):
        return []  # ranges like 0.62-0.95
    if s.startswith(">"):
        return []
    vals = []
    for m in re.findall(r"\d+\.\d+", s):
        v = float(m)
        if 0.0 <= v <= 1.0:
            vals.append(v)
    return vals


def fig04_r2_vs_nse() -> Path:
    w1 = load_json("w1_provenance_metrics.json")
    w5 = load_json("w5_lit_audit_summary.json")

    # Prefer analysis JSON (authoritative); cards are downstream.
    w3 = load_json("w3_tdgta_off_metrics.json")
    bon_pts = []
    for m in w3["metrics"]:
        if m.get("run") == "ON" and m.get("caliber") in ("A", "B", "C"):
            bon_pts.append(
                {
                    "label": f"BON {m['caliber']}",
                    "r2": m["r2"],
                    "nse": m["nse"],
                    "kind": "skill",
                }
            )

    dg_pts = []
    for p in w1["degray"]["pairs"]:
        if p.get("primary"):
            short = p["id"].replace("DG_", "")
            dg_pts.append(
                {"label": short, "r2": p["r2"], "nse": p["nse"], "kind": "internal_degray"}
            )

    col_pts = []
    for p in w1["columbia"]["pairs"]:
        if p.get("primary"):
            short = p["id"].replace("COL_DO_", "")
            col_pts.append(
                {"label": short, "r2": p["r2"], "nse": p["nse"], "kind": "internal_columbia"}
            )

    # Literature Table 2 R² (no NSE in audit — rug on R² axis only)
    lit_skill = []
    lit_not = []
    lit_unk = []
    for item in w5["table2"]["skill_true"]:
        for v in parse_table2_r2(item["r2"]):
            lit_skill.append((v, f"n{item['n']}"))
    for item in w5["table2"]["skill_false"]:
        for v in parse_table2_r2(item["r2"]):
            lit_not.append((v, f"n{item['n']}"))
    for item in w5["table2"]["skill_unknown"]:
        for v in parse_table2_r2(item["r2"]):
            lit_unk.append((v, f"n{item['n']}"))

    # 2 + 1 strip: (a) skill, (b) internal, (c) literature R² rug (no NSE).
    try:
        from sp_plot_style import apply_style, save_fig

        apply_style()
    except Exception:
        save_fig = None

    fig = plt.figure(figsize=(10.8, 6.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[3.2, 1.0], hspace=0.35, wspace=0.28)
    ax_sk = fig.add_subplot(gs[0, 0])
    ax_in = fig.add_subplot(gs[0, 1])
    ax_rug = fig.add_subplot(gs[1, :])

    def scatter(ax, pts, color, marker, label, z=4):
        if not pts:
            return
        ax.scatter(
            [p["r2"] for p in pts],
            [p["nse"] for p in pts],
            c=color,
            marker=marker,
            s=70,
            label=label,
            zorder=z,
            edgecolors="k",
            linewidths=0.4,
        )
        for p in pts:
            ax.annotate(
                p["label"],
                (p["r2"], p["nse"]),
                fontsize=7,
                xytext=(4, 4),
                textcoords="offset points",
            )

    scatter(ax_sk, bon_pts, "#D55E00", "o", "Bonneville ON A/B/C vs CCIW")
    scatter(ax_in, dg_pts, "#0072B2", "s", "DeGray T (primary)")
    scatter(ax_in, col_pts, "#009E73", "^", "Columbia DO (primary)")

    def finish_axis(ax, pts, title):
        all_nse = [p["nse"] for p in pts]
        y_lo = min(all_nse) - 0.4
        y_hi = max(1.05, max(all_nse) + 0.4)
        ax.set_ylim(y_lo, y_hi)
        ax.axhline(0.0, color="k", lw=0.8, ls="--")
        ax.set_xlabel(r"$R^2$")
        ax.set_ylabel("NSE")
        ax.set_title(title, fontsize=9.5)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-0.02, 1.05)
        ax.legend(loc="lower left", fontsize=7, framealpha=0.92)

    finish_axis(ax_sk, bon_pts, "(a) Observational skill — Bonneville TDG vs CCIW")
    finish_axis(
        ax_in,
        dg_pts + col_pts,
        "(b) Internal consistency — DeGray T / Columbia DO\n(no independent observations; not field skill)",
    )

    y_map = {"skill": 2, "other": 1, "unk": 0}
    for items, ykey, color, lab in (
        (lit_skill, "skill", "darkorange", "confirmed W2↔obs skill (1)"),
        (lit_not, "other", "0.45", "confirmed other object (7)"),
        (lit_unk, "unk", "0.7", "unresolved (4)"),
    ):
        if not items:
            continue
        xs = [v for v, _ in items]
        ax_rug.scatter(xs, [y_map[ykey]] * len(xs), c=color, marker="|", s=140, label=lab, zorder=3)
    ax_rug.set_yticks([0, 1, 2])
    ax_rug.set_yticklabels(["unresolved", "other object", "W2↔obs skill"], fontsize=8)
    ax_rug.set_xlim(-0.02, 1.05)
    ax_rug.set_xlabel(r"Benicio et al. Table 2 $R^2$ (NSE unavailable in audit; not inferred)")
    ax_rug.set_title(
        "(c) Literature $R^2$ audit strip — not a pooled skill ranking with panels (a)/(b)",
        fontsize=9.5,
    )
    ax_rug.grid(True, axis="x", alpha=0.3)
    ax_rug.legend(loc="upper right", fontsize=7, ncol=3, framealpha=0.92)

    fig.suptitle(
        "Fig. 4  $R^2$–NSE evidence taxonomy: observational skill | internal consistency | literature $R^2$\n"
        "Panels (a) and (b) have different evaluation objects and must not be pooled as skill",
        fontsize=10.5,
    )
    out = FIGURES / "fig04_r2_vs_nse_literature.png"
    if save_fig is not None:
        save_fig(fig, out)
    else:
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close()
    print(f"wrote {out}")
    return out


def fig05_reachable_range() -> Path:
    w3 = load_json("w3_tdgta_off_metrics.json")
    rr = w3["reachable_range"]
    obs_n = rr["obs_n"]
    obs_n_gt = rr["obs_n_gt_120"]
    frac = rr["obs_frac_gt_120"]
    obs_max = rr["obs_max"]
    jmin, jmax = rr["obs_jday_min"], rr["obs_jday_max"]
    cap = rr["controller_cap_pct"]

    obs = pd.read_csv(CCIW, skiprows=2)
    obs["JDAY"] = pd.to_numeric(obs["JDAY"], errors="coerce")
    obs["TDG"] = pd.to_numeric(obs["Total dissolved gas"], errors="coerce")
    # Match eval_w3_tdgta_off.py reachable_range: model window + MISSING=-90
    J0, J1, MISSING = 40544.0, 40910.0, -90.0
    mask = (
        obs["JDAY"].between(J0, J1)
        & obs["TDG"].notna()
        & (obs["TDG"] > MISSING)
    )
    tdg = obs.loc[mask, "TDG"].to_numpy(float)
    if len(tdg) != obs_n:
        print(f"WARN: CCIW filtered n={len(tdg)} vs JSON obs_n={obs_n}")
    gt = int((tdg > cap).sum())
    if gt != obs_n_gt or abs(float(np.mean(tdg > cap)) - frac) > 1e-3:
        print(f"WARN: gt120 hist={gt}/{len(tdg)} vs JSON {obs_n_gt}/{obs_n} frac={frac}")

    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    bins = np.arange(95, 132, 1.0)
    n_lo = tdg[tdg <= cap]
    n_hi = tdg[tdg > cap]
    ax.hist(n_lo, bins=bins, color="tab:blue", alpha=0.75, edgecolor="white", linewidth=0.4, label=f"≤{cap:g}%")
    ax.hist(n_hi, bins=bins, color="tab:red", alpha=0.75, edgecolor="white", linewidth=0.4, label=f">{cap:g}%")
    ax.axvline(cap, color="k", ls="--", lw=1.4, label=f"controller cap {cap:g}%")
    ax.axvline(obs_max, color="tab:purple", ls=":", lw=1.2, label=f"obs max {obs_max}%")

    # Shade unreachable band for B (above cap)
    ymax = ax.get_ylim()[1]
    ax.axvspan(cap, max(bins), color="tab:red", alpha=0.12, zorder=0)

    ax.set_xlabel("CCIW TDG (% saturation)")
    ax.set_ylabel("Hours")
    ax.set_title(
        f"Fig. 5  Paired-window CCIW TDG (JDAY {jmin}–{jmax}, n={obs_n})\n"
        f"{obs_n_gt}/{obs_n} = {100*frac:.2f}% of hours >{cap:g}% (unreachable on gated B)"
    )
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = FIGURES / "fig05_tdg_reachable_range.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"wrote {out} (hist n={len(tdg)}, gt120={int((tdg > cap).sum())})")
    return out


def fig07_runcard() -> Path:
    card = json.loads((CARDS / "bonneville_tdgta_on.json").read_text(encoding="utf-8"))
    fig = plt.figure(figsize=(11.0, 8.2))
    fig.suptitle(
        f"Fig. 7  w2eval run-card: {card['card_id']}\n{card['title']}",
        fontsize=12,
        fontweight="bold",
        y=0.98,
    )

    # Block 1: VPR
    ax1 = fig.add_axes([0.06, 0.58, 0.88, 0.32])
    ax1.axis("off")
    ax1.set_title("1. VPR — variable provenance", loc="left", fontsize=10, pad=8)
    vpr_rows = [["cal", "file", "column", "I / layer", "unit"]]
    for v in card["vpr"]:
        vpr_rows.append(
            [
                str(v["caliber"]),
                str(v["file"])[:42],
                str(v["column"])[:28],
                f"{v.get('segment')}/{str(v.get('layer'))[:22]}",
                str(v.get("unit", ""))[:12],
            ]
        )
    table1 = ax1.table(
        cellText=vpr_rows,
        loc="center",
        cellLoc="left",
        colWidths=[0.06, 0.32, 0.22, 0.28, 0.12],
    )
    table1.auto_set_font_size(False)
    table1.set_fontsize(7)
    table1.scale(1, 1.35)
    for (r, _c), cell in table1.get_celld().items():
        if r == 0:
            cell.set_facecolor("#d9e8f5")
            cell.set_text_props(fontweight="bold")
        cell.set_edgecolor("#888")

    # Block 2: metrics
    ax2 = fig.add_axes([0.06, 0.28, 0.88, 0.26])
    ax2.axis("off")
    mp = card["metrics_panel"]
    ax2.set_title(
        f"2. Metrics — {mp['kind']}  |  n={mp['n']}  |  {mp['window']}",
        loc="left",
        fontsize=10,
        pad=8,
    )
    m_rows = [["cal", "R²", "NSE", "KGE", "r", "α", "β", "PBIAS", "MAE", "sim_max"]]
    for c in mp["calibers"]:
        m_rows.append(
            [
                c["caliber"],
                f"{c['r2']:.3f}",
                f"{c['nse']:.3f}",
                f"{c['kge']:.3f}",
                f"{c['r']:.3f}",
                f"{c['alpha']:.3f}",
                f"{c['beta']:.3f}",
                f"{c['pbias']:.2f}%",
                f"{c['mae']:.2f}",
                f"{c['sim_max']}",
            ]
        )
    table2 = ax2.table(cellText=m_rows, loc="center", cellLoc="center")
    table2.auto_set_font_size(False)
    table2.set_fontsize(7.5)
    table2.scale(1, 1.4)
    for (r, _c), cell in table2.get_celld().items():
        if r == 0:
            cell.set_facecolor("#d9e8f5")
            cell.set_text_props(fontweight="bold")
        if r > 0 and m_rows[r][0] == "B":
            cell.set_facecolor("#fff3cd")
        cell.set_edgecolor("#888")

    # Block 3: NHR from card JSON fields
    ax3 = fig.add_axes([0.06, 0.06, 0.88, 0.18])
    ax3.axis("off")
    ax3.set_title("3. NHR — numerical health", loc="left", fontsize=10, pad=8)
    nh = card["nhr"]
    nv = nh.get("snp_n_violations")
    nv_pct = nh.get("snp_pct_violations")
    nit = nh.get("snp_total_iterations")
    nv_txt = f"{nv} ({nv_pct}% of NIT={nit})" if nv is not None else ""
    nhr_rows = [
        ["run", "neg thickness", "Add", "Sub", "exit0 masks", "DLTINTER", "Normal", "NV"],
        [
            "TDGTA ON",
            str(nh.get("neg_surface_thickness_count")),
            str(nh.get("add_layer_count")),
            str(nh.get("subtract_layer_count")),
            "no" if nh.get("exit_zero_masks_rollback") is False else str(nh.get("exit_zero_masks_rollback")),
            str(nh.get("dltinter")),
            "yes" if nh.get("normal_termination") else str(nh.get("normal_termination")),
            nv_txt,
        ],
    ]
    table3 = ax3.table(cellText=nhr_rows, loc="center", cellLoc="center")
    table3.auto_set_font_size(False)
    table3.set_fontsize(8)
    table3.scale(1, 1.45)
    for (r, _c), cell in table3.get_celld().items():
        if r == 0:
            cell.set_facecolor("#d9e8f5")
            cell.set_text_props(fontweight="bold")
        cell.set_edgecolor("#888")

    fig.text(
        0.06,
        0.01,
        mp.get("note", "")
        + "  |  Source: w2eval/cards/bonneville_tdgta_on.json (cached analysis; W2 not re-run).",
        fontsize=7,
        va="bottom",
    )

    out = FIGURES / "fig07_w2eval_runcard.png"
    fig.savefig(out, dpi=150)
    plt.close()
    print(f"wrote {out}")
    return out


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    copy_w4()
    fig04_r2_vs_nse()
    fig05_reachable_range()
    fig07_runcard()


if __name__ == "__main__":
    main()
