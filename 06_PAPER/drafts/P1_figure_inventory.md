# P1 figure inventory

Draft: `P1_GMD_draft_v2.md` (v1 retained). Paths relative to `06_PAPER/drafts/` unless noted as repo-absolute under `06_PAPER/`.  
Generated 2026-08-15 via `06_PAPER/analysis/plot_p1_missing_figures.py` (copies W4; draws Fig. 4/5/7 from analysis JSON + w2eval cards + CCIW CSV). W2 not re-run.

**SciencePlots redraw (2026-08-16):** all listed PNGs overwritten in place under `../figures/` via `06_PAPER/analysis/redraw_all_scienceplots.py` (`science` + `no-latex`, Times New Roman, dpi≥300). Log: `../figures/SCIENCEPLOTS_REDRAW_LOG.md`. Filenames unchanged.

| Fig. | File path | Status | Draft section (v2) |
|---|---|---|---|
| 1 | `../figures/W3_tdgta_on_off_timeseries.png` | exists | §5.1 |
| 2 | `../figures/W3_tdgta_on_off_scatter.png` | exists | §5.1 |
| 3 | `../figures/W3_tdgta_kge_decomposition.png` | exists | §5.1 |
| 3b | `../figures/w1_degray_T_kge_bars.png` | exists | §5.3 (companion) |
| 3c | `../figures/w1_columbia_DO_kge_bars.png` | exists | §5.3 (companion) |
| 4 | `../figures/fig04_r2_vs_nse_literature.png` | generated | §5.1 |
| 5 | `../figures/fig05_tdg_reachable_range.png` | generated | §5.2 |
| 5 companion | `../figures/w4_tdg_gt120_annual.png` | exists (copied from analysis) | §5.2 |
| 6 | `../figures/nhr_dltmax_neg_thickness.png` | exists | §5.4 |
| 6 companions | `../figures/nhr_dltmax_layers_dltmin.png`, `../figures/nhr_dltmax_heatmap.png` | exists | §5.4 |
| 7 | `../figures/fig07_w2eval_runcard.png` | generated | §5.5 |
| 8 | `../figures/w4_spill_tdgta_vs_dart.png` | exists (copied from analysis) | §5.2 |
| 8 companion | `../figures/w4_spill_scatter.png` | exists (copied from analysis) | §5.2 |
| D1 | `../figures/w1_degray_T_timeseries.png` | exists | §5.3 |
| D2 | `../figures/w1_degray_T_scatter.png` | exists | §5.3 |
| D3 | `../figures/w1_degray_T_r2_vs_nse.png` | exists | §5.3 |
| C1 | `../figures/w1_columbia_DO_timeseries.png` | exists | §5.3 |
| C2 | `../figures/w1_columbia_DO_scatter.png`, `../figures/w1_columbia_DO_r2_vs_nse.png` | exists | §5.3 |
| S1 | `../figures/w7_columbia_sod_timeseries.png`, `../figures/w7_columbia_sod_histogram.png` | exists | §5.5 |
| W4 extras | `../figures/w4_cciw_vs_dart_scatter.png`, `../figures/w4_cciw_vs_dart_timeseries.png`, `../figures/w4_tdg_annual_max.png` | exists (copied from analysis) | §5.2 (cited, not numbered) |

## Data sources for generated panels

| Fig. | Numbers from |
|---|---|
| 4 | `w2eval/cards/bonneville_tdgta_on.json` (A/B/C); `analysis/w1_provenance_metrics.json` (DeGray/Columbia primary); `analysis/w5_lit_audit_summary.json` Table 2 *R*² rug only |
| 5 | `analysis/w3_tdgta_off_metrics.json` → `reachable_range`; histogram bars from run CCIW CSV (`05_REPRO_RUNS/.../CCIW_TDG_Temp_2011-2015.csv`), same J0/J1/MISSING filter as W3 (*n*=1614, >120%=251) |
| 7 | `w2eval/cards/bonneville_tdgta_on.json` (VPR + metrics + NHR blocks) |

## Gap status

**Closed for draft purposes:** Fig. 4/5/7 PNGs exist under `06_PAPER/figures/`; all draft-cited W4 PNGs live in `figures/` with matching captions; Appendix A and this inventory agree.

**Not a figure gap:** Zenodo DOI, out-of-sample NSE, Chang/Neto reference fields — see `P1_review_checklist.md` §5.
