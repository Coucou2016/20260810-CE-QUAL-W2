"""Redraw all P1 paper figures with SciencePlots + Times New Roman.

Overwrites PNGs under ``06_PAPER/figures/`` (same filenames as inventory).
W4 copies also refresh ``06_PAPER/analysis/w4_*.png``.
Numbers come from existing analysis JSON + repro CSVs; W2 is not run.

Usage:
  python 06_PAPER/analysis/redraw_all_scienceplots.py
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "06_PAPER" / "analysis"
FIGURES = ROOT / "06_PAPER" / "figures"
sys.path.insert(0, str(ANALYSIS))
sys.path.insert(0, str(ROOT / "00_INDEX"))

from sp_plot_style import apply_style, patch_pyplot_hooks  # noqa: E402

LOG: list[dict] = []


def _note(name: str, source: str, status: str = "ok", detail: str = "") -> None:
    LOG.append(
        {
            "file": name,
            "source": source,
            "status": status,
            "detail": detail,
            "when": datetime.now().isoformat(timespec="seconds"),
        }
    )
    print(f"[{status}] {name}  ← {source}" + (f"  ({detail})" if detail else ""))


def redraw_w3() -> None:
    """Bonneville TDGTA ON/OFF timeseries, scatter, KGE from repro CSVs."""
    import eval_w3_tdgta_off as w3

    apply_style(force=True)
    w3.main()
    for name in (
        "W3_tdgta_on_off_timeseries.png",
        "W3_tdgta_on_off_scatter.png",
        "W3_tdgta_kge_decomposition.png",
    ):
        p = FIGURES / name
        _note(name, "eval_w3_tdgta_off (ON/OFF runs + CCIW CSV)", "ok" if p.exists() else "missing")


def redraw_w1_w7() -> None:
    """DeGray / Columbia internal-consistency + Columbia SOD panels."""
    import w1_w7_provenance as w1

    w1.setup_style = lambda: apply_style(force=True)  # type: ignore[assignment]
    apply_style(force=True)
    w1.main()
    names = [
        "w1_degray_T_timeseries.png",
        "w1_degray_T_scatter.png",
        "w1_degray_T_kge_bars.png",
        "w1_degray_T_r2_vs_nse.png",
        "w1_columbia_DO_timeseries.png",
        "w1_columbia_DO_scatter.png",
        "w1_columbia_DO_kge_bars.png",
        "w1_columbia_DO_r2_vs_nse.png",
        "w7_columbia_sod_timeseries.png",
        "w7_columbia_sod_histogram.png",
    ]
    for name in names:
        p = FIGURES / name
        _note(name, "w1_w7_provenance (repro CSVs + JSON metrics)", "ok" if p.exists() else "missing")


def redraw_nhr_from_json() -> None:
    """NHR DLTMAX scan panels from nhr_dlt_scan.json (no W2 / no re-collect)."""
    from plot_nhr_scan import plot_scan

    apply_style(force=True)
    payload = json.loads((ANALYSIS / "nhr_dlt_scan.json").read_text(encoding="utf-8"))
    written = plot_scan(payload)
    for path in written:
        name = Path(path).name
        _note(name, "nhr_dlt_scan.json → plot_scan", "ok")


def redraw_fig0457() -> None:
    """Fig. 4 / 5 / 7 from analysis JSON + CCIW + w2eval card."""
    import plot_p1_missing_figures as p1

    apply_style(force=True)
    p1.FIGURES = FIGURES
    p1.fig04_r2_vs_nse()
    p1.fig05_reachable_range()
    p1.fig07_runcard()
    for name in (
        "fig04_r2_vs_nse_literature.png",
        "fig05_tdg_reachable_range.png",
        "fig07_w2eval_runcard.png",
    ):
        _note(name, "plot_p1_missing_figures (JSON + CCIW + card)", "ok" if (FIGURES / name).exists() else "missing")


def redraw_w4_annual_from_json() -> None:
    """Annual exceedance / max from w4_cciw_vs_dart.json (no re-download)."""
    apply_style(force=True)
    w4 = json.loads((ANALYSIS / "w4_cciw_vs_dart.json").read_text(encoding="utf-8"))
    by_year = w4["exceedance_all_downloaded"]["by_year"]
    years = [r["year"] for r in by_year]
    gt120 = [r["pct_hours_gt_120"] for r in by_year]
    gt115 = [r["pct_hours_gt_115"] for r in by_year]
    ymax = [r["annual_max_tdg"] for r in by_year]

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    x = np.arange(len(years))
    ax.bar(x - 0.18, gt115, 0.36, label=">115% of valid hours")
    ax.bar(x + 0.18, gt120, 0.36, label=">120% of valid hours")
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha="right")
    ax.set_ylabel("% of valid hours")
    ax.set_xlabel("Year")
    ax.set_title("CCIW annual exceedance (DART hourly TDG %)")
    ax.legend(loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    for dest in (ANALYSIS / "w4_tdg_gt120_annual.png", FIGURES / "w4_tdg_gt120_annual.png"):
        fig.savefig(dest, dpi=300, bbox_inches="tight")
    plt.close(fig)
    _note("w4_tdg_gt120_annual.png", "w4_cciw_vs_dart.json exceedance_all_downloaded")

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.plot(years, ymax, "o-", lw=1.4, ms=5)
    ax.axhline(120, color="#D55E00", ls="--", label="120%")
    ax.axhline(115, color="#E69F00", ls=":", label="115%")
    ax.set_ylabel("Annual max TDG (%)")
    ax.set_xlabel("Year")
    ax.set_title("CCIW annual maximum TDG (DART)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    for dest in (ANALYSIS / "w4_tdg_annual_max.png", FIGURES / "w4_tdg_annual_max.png"):
        fig.savefig(dest, dpi=300, bbox_inches="tight")
    plt.close(fig)
    _note("w4_tdg_annual_max.png", "w4_cciw_vs_dart.json exceedance_all_downloaded")

def redraw_w4_series() -> None:
    """CCIW–DART identity + 2011 spill panels via download_dart_cciw (--skip-download)."""
    import download_dart_cciw as w4

    apply_style(force=True)
    # Point plot outputs at analysis/; we copy to figures/ after.
    orig_make = w4.make_plots

    def make_plots_and_copy(cmp, dart, spill, exceed_all):
        written = orig_make(cmp, dart, spill, exceed_all)
        for name in (
            "w4_cciw_vs_dart_scatter.png",
            "w4_cciw_vs_dart_timeseries.png",
            "w4_spill_scatter.png",
            "w4_spill_tdgta_vs_dart.png",
            "w4_tdg_gt120_annual.png",
            "w4_tdg_annual_max.png",
        ):
            src = ANALYSIS / name
            if src.exists():
                shutil.copy2(src, FIGURES / name)
        return written

    w4.make_plots = make_plots_and_copy  # type: ignore[assignment]
    rc = w4.main(["--skip-download"])
    if rc != 0:
        _note("w4_* series", "download_dart_cciw --skip-download", "warn", f"exit={rc}")
    else:
        for name in (
            "w4_cciw_vs_dart_scatter.png",
            "w4_cciw_vs_dart_timeseries.png",
            "w4_spill_scatter.png",
            "w4_spill_tdgta_vs_dart.png",
        ):
            _note(name, "download_dart_cciw analyze (--skip-download)", "ok" if (FIGURES / name).exists() else "missing")


def write_log() -> Path:
    out = FIGURES / "SCIENCEPLOTS_REDRAW_LOG.md"
    lines = [
        "# SciencePlots redraw log",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Style: `science` + `no-latex` (SciencePlots); font Times New Roman "
        "(CJK fallback YaHei/SimHei); save dpi ≥ 300.",
        "",
        "Policy: overwrite same filenames under `06_PAPER/figures/` (draft inventory paths unchanged).",
        "W2 model not re-run.",
        "",
        "| Figure file | Data source | Status | Detail |",
        "|---|---|---|---|",
    ]
    for row in LOG:
        lines.append(
            f"| `{row['file']}` | {row['source']} | {row['status']} | {row.get('detail','')} |"
        )
    lines.extend(
        [
            "",
            "## Inventory mapping (draft Fig. → file)",
            "",
            "| Fig. | File |",
            "|---|---|",
            "| 1 | `W3_tdgta_on_off_timeseries.png` |",
            "| 2 | `W3_tdgta_on_off_scatter.png` |",
            "| 3 | `W3_tdgta_kge_decomposition.png` |",
            "| 3b/3c | `w1_degray_T_kge_bars.png`, `w1_columbia_DO_kge_bars.png` |",
            "| 4 | `fig04_r2_vs_nse_literature.png` |",
            "| 5 | `fig05_tdg_reachable_range.png` |",
            "| 5 companion | `w4_tdg_gt120_annual.png` |",
            "| 6 | `nhr_dltmax_neg_thickness.png` (+ companions) |",
            "| 7 | `fig07_w2eval_runcard.png` |",
            "| 8 | `w4_spill_tdgta_vs_dart.png` |",
            "| D*/C* | `w1_degray_T_*`, `w1_columbia_DO_*` |",
            "| S1 | `w7_columbia_sod_*` |",
            "",
            "## Report note",
            "",
            "`00_INDEX/build_repro_report.py` embeds case-local `05_REPRO_RUNS/**/analysis/*.png` "
            "(Bonneville TSR/tailwater/SYSTDG, Columbia diagenesis), not the P1 `06_PAPER/figures/` set. "
            "Paper/draft figures above were refreshed; full HTML/PDF report regeneration is optional and not required for this redraw.",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")
    return out


def main() -> int:
    FIGURES.mkdir(parents=True, exist_ok=True)
    patch_pyplot_hooks()
    apply_style(force=True)

    print("=== W3 Bonneville TDG ===")
    redraw_w3()

    print("=== W1 / W7 DeGray Columbia SOD ===")
    redraw_w1_w7()

    print("=== NHR DLT scan ===")
    redraw_nhr_from_json()

    print("=== Fig. 4 / 5 / 7 ===")
    redraw_fig0457()

    print("=== W4 annual (JSON) ===")
    redraw_w4_annual_from_json()

    print("=== W4 series (local DART CSVs, no download) ===")
    redraw_w4_series()

    # Re-apply annual after W4 series (make_plots also writes annual; keep SP style)
    redraw_w4_annual_from_json()

    write_log()
    ok = sum(1 for r in LOG if r["status"] == "ok")
    miss = [r["file"] for r in LOG if r["status"] != "ok"]
    print(f"done: {ok} ok, missing/warn={miss}")
    return 0 if not miss else 1


if __name__ == "__main__":
    raise SystemExit(main())
