"""Redraw report-embedded PNGs under 05_REPRO_RUNS/**/analysis with SciencePlots.

Reuses ``sp_plot_style`` (same hooks as ``redraw_all_scienceplots.py``).
Re-runs existing plotters on local CSV/JSON only — no W2 model runs.

Usage:
  python 06_PAPER/analysis/redraw_report_scienceplots.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "06_PAPER" / "analysis"
FIGURES = ROOT / "06_PAPER" / "figures"
INDEX = ROOT / "00_INDEX"
sys.path.insert(0, str(ANALYSIS))
sys.path.insert(0, str(INDEX))

from sp_plot_style import apply_style, patch_pyplot_hooks  # noqa: E402

LOG: list[dict] = []

BON_AN = ROOT / "05_REPRO_RUNS" / "run_20260814_bonneville" / "analysis"
COL_AN = ROOT / "05_REPRO_RUNS" / "run_20260814_columbia_diag" / "analysis"
FIXED_AN = ROOT / "05_REPRO_RUNS" / "run_20260811_fixed" / "analysis"

# Paths hard-coded in build_repro_report.py (plus sibling Bonneville TSR plots).
REPORT_FIGS: list[tuple[str, Path]] = [
    # Three-case viz
    ("Long_Lake_timeseries.png", FIXED_AN),
    ("Long_Lake_planview.png", FIXED_AN),
    ("Long_Lake_profile.png", FIXED_AN),
    ("Long_Lake_watershed_basemap.png", FIXED_AN),
    ("Long_Lake_alignment_error.png", FIXED_AN),
    ("DeGray_timeseries.png", FIXED_AN),
    ("DeGray_planview.png", FIXED_AN),
    ("DeGray_profile.png", FIXED_AN),
    ("DeGray_watershed_basemap.png", FIXED_AN),
    ("DeGray_alignment_error.png", FIXED_AN),
    ("Columbia_Slough_timeseries.png", FIXED_AN),
    ("Columbia_Slough_planview.png", FIXED_AN),
    ("Columbia_Slough_profile.png", FIXED_AN),
    ("Columbia_Slough_watershed_basemap.png", FIXED_AN),
    ("Columbia_Slough_alignment_error.png", FIXED_AN),
    # Bonneville
    ("Bonneville_BON_tsr_1_seg40_TDG_pct_timeseries.png", BON_AN),
    ("Bonneville_BON_tsr_1_seg40_TDG_pct_scatter.png", BON_AN),
    ("Bonneville_BON_tsr_1_seg40_Temperature_C_timeseries.png", BON_AN),
    ("Bonneville_BON_tsr_1_seg40_Temperature_C_scatter.png", BON_AN),
    ("Bonneville_tailwater_TDG_timeseries.png", BON_AN),
    ("Bonneville_tailwater_TDG_scatter.png", BON_AN),
    ("Bonneville_tailwater_Temp_timeseries.png", BON_AN),
    ("Bonneville_tailwater_Temp_scatter.png", BON_AN),
    ("Bonneville_SYSTDG_TDG_vs_CCIW_timeseries.png", BON_AN),
    ("Bonneville_SYSTDG_TDG_vs_CCIW_scatter.png", BON_AN),
    ("Bonneville_TDGTA_target_overlay.png", BON_AN),
    # Columbia diagenesis
    ("Columbia_diagenesis_SOD_timeseries.png", COL_AN),
    ("Columbia_diagenesis_SOD_plan.png", COL_AN),
    ("Columbia_diagenesis_DO_NH4_vs_off.png", COL_AN),
]


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


def _check_batch(names: list[str], folder: Path, source: str) -> None:
    for name in names:
        p = folder / name
        _note(name, source, "ok" if p.exists() else "missing", str(folder.relative_to(ROOT)))


def run_module_main(mod_name: str) -> None:
    apply_style(force=True)
    mod = __import__(mod_name)
    mod.main()


def redraw_bonneville() -> None:
    print("=== Bonneville TSR vs CCIW ===")
    run_module_main("eval_bonneville_obs")
    _check_batch(
        [
            "Bonneville_BON_tsr_1_seg40_TDG_pct_timeseries.png",
            "Bonneville_BON_tsr_1_seg40_TDG_pct_scatter.png",
            "Bonneville_BON_tsr_1_seg40_Temperature_C_timeseries.png",
            "Bonneville_BON_tsr_1_seg40_Temperature_C_scatter.png",
        ],
        BON_AN,
        "eval_bonneville_obs (TSR CSV + CCIW)",
    )

    print("=== Bonneville tailwater ===")
    run_module_main("eval_bonneville_tailwater")
    _check_batch(
        [
            "Bonneville_tailwater_TDG_timeseries.png",
            "Bonneville_tailwater_TDG_scatter.png",
            "Bonneville_tailwater_Temp_timeseries.png",
            "Bonneville_tailwater_Temp_scatter.png",
        ],
        BON_AN,
        "eval_bonneville_tailwater (c_wdo/t_wdo + CCIW)",
    )

    print("=== Bonneville SYSTDG TDG ===")
    run_module_main("eval_systdg_tdg")
    _check_batch(
        [
            "Bonneville_SYSTDG_TDG_vs_CCIW_timeseries.png",
            "Bonneville_SYSTDG_TDG_vs_CCIW_scatter.png",
        ],
        BON_AN,
        "eval_systdg_tdg (TDGTarget_output + CCIW)",
    )

    print("=== Bonneville TDGTA overlay ===")
    run_module_main("diagnose_tdg_target")
    _check_batch(
        ["Bonneville_TDGTA_target_overlay.png"],
        BON_AN,
        "diagnose_tdg_target (N2+DO + TDGTA target)",
    )


def redraw_columbia_diag() -> None:
    print("=== Columbia diagenesis ===")
    run_module_main("plot_columbia_diagenesis")
    _check_batch(
        [
            "Columbia_diagenesis_SOD_timeseries.png",
            "Columbia_diagenesis_SOD_plan.png",
            "Columbia_diagenesis_DO_NH4_vs_off.png",
        ],
        COL_AN,
        "plot_columbia_diagenesis (Diagenesis_SOD + TSR ON/OFF)",
    )


def redraw_three_case_viz() -> None:
    print("=== Three-case timeseries / planview / profile ===")
    run_module_main("make_visualizations")
    names = []
    for short in ("Long_Lake", "DeGray", "Columbia_Slough"):
        names.extend(
            [
                f"{short}_timeseries.png",
                f"{short}_planview.png",
                f"{short}_profile.png",
            ]
        )
    _check_batch(names, FIXED_AN, "make_visualizations (repro TSR/CPL/PRF CSV)")


def redraw_basemaps() -> None:
    print("=== Watershed basemaps + alignment ===")
    run_module_main("make_watershed_basemaps")
    names = []
    for short in ("Long_Lake", "DeGray", "Columbia_Slough"):
        names.extend(
            [
                f"{short}_watershed_basemap.png",
                f"{short}_alignment_error.png",
            ]
        )
    _check_batch(names, FIXED_AN, "make_watershed_basemaps (local tile cache + bathy)")


def append_log() -> Path:
    out = FIGURES / "SCIENCEPLOTS_REDRAW_LOG.md"
    existing = out.read_text(encoding="utf-8") if out.exists() else ""
    # Drop previous 「报告图」 section if re-running.
    marker = "## 报告图"
    if marker in existing:
        existing = existing.split(marker)[0].rstrip() + "\n\n"

    lines = [
        existing.rstrip(),
        "",
        "## 报告图",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Style: same as paper figures (`science` + `no-latex`, Times New Roman, dpi≥300).",
        "Driver: `06_PAPER/analysis/redraw_report_scienceplots.py`.",
        "Policy: overwrite same filenames under `05_REPRO_RUNS/**/analysis/` "
        "(paths in `build_repro_report.py` unchanged).",
        "W2 model not re-run.",
        "",
        "| Figure file | Location | Data source | Status | Detail |",
        "|---|---|---|---|---|",
    ]
    for row in LOG:
        loc = row.get("detail", "")
        lines.append(
            f"| `{row['file']}` | `{loc}` | {row['source']} | {row['status']} | |"
        )
    lines.append("")
    out.write_text("\n".join(lines).lstrip() + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return out


def main() -> int:
    patch_pyplot_hooks()
    apply_style(force=True)

    redraw_bonneville()
    redraw_columbia_diag()
    redraw_three_case_viz()
    redraw_basemaps()

    # Final existence sweep for every report-referenced fig.
    print("=== Final sweep ===")
    for name, folder in REPORT_FIGS:
        p = folder / name
        if not any(r["file"] == name for r in LOG):
            _note(name, "report inventory", "ok" if p.exists() else "missing", str(folder.relative_to(ROOT)))
        elif not p.exists():
            for r in LOG:
                if r["file"] == name:
                    r["status"] = "missing"

    append_log()
    ok = sum(1 for r in LOG if r["status"] == "ok")
    miss = [r["file"] for r in LOG if r["status"] != "ok"]
    print(f"done: {ok} ok, missing/warn={miss}")
    return 0 if not miss else 1


if __name__ == "__main__":
    raise SystemExit(main())
