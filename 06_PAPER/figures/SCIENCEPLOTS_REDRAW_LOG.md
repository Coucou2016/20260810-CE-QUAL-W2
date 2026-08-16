# SciencePlots redraw log

Generated: 2026-08-16T13:59:26

Style: `science` + `no-latex` (SciencePlots); font Times New Roman (CJK fallback YaHei/SimHei); save dpi ≥ 300.

Policy: overwrite same filenames under `06_PAPER/figures/` (draft inventory paths unchanged).
W2 model not re-run.

| Figure file | Data source | Status | Detail |
|---|---|---|---|
| `W3_tdgta_on_off_timeseries.png` | eval_w3_tdgta_off (ON/OFF runs + CCIW CSV) | ok |  |
| `W3_tdgta_on_off_scatter.png` | eval_w3_tdgta_off (ON/OFF runs + CCIW CSV) | ok |  |
| `W3_tdgta_kge_decomposition.png` | eval_w3_tdgta_off (ON/OFF runs + CCIW CSV) | ok |  |
| `w1_degray_T_timeseries.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `w1_degray_T_scatter.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `w1_degray_T_kge_bars.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `w1_degray_T_r2_vs_nse.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `w1_columbia_DO_timeseries.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `w1_columbia_DO_scatter.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `w1_columbia_DO_kge_bars.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `w1_columbia_DO_r2_vs_nse.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `w7_columbia_sod_timeseries.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `w7_columbia_sod_histogram.png` | w1_w7_provenance (repro CSVs + JSON metrics) | ok |  |
| `nhr_dltmax_neg_thickness.png` | nhr_dlt_scan.json → plot_scan | ok |  |
| `nhr_dltmax_layers_dltmin.png` | nhr_dlt_scan.json → plot_scan | ok |  |
| `nhr_dltmax_heatmap.png` | nhr_dlt_scan.json → plot_scan | ok |  |
| `fig04_r2_vs_nse_literature.png` | plot_p1_missing_figures (JSON + CCIW + card) | ok |  |
| `fig05_tdg_reachable_range.png` | plot_p1_missing_figures (JSON + CCIW + card) | ok |  |
| `fig07_w2eval_runcard.png` | plot_p1_missing_figures (JSON + CCIW + card) | ok |  |
| `w4_tdg_gt120_annual.png` | w4_cciw_vs_dart.json exceedance_all_downloaded | ok |  |
| `w4_tdg_annual_max.png` | w4_cciw_vs_dart.json exceedance_all_downloaded | ok |  |
| `w4_cciw_vs_dart_scatter.png` | download_dart_cciw analyze (--skip-download) | ok |  |
| `w4_cciw_vs_dart_timeseries.png` | download_dart_cciw analyze (--skip-download) | ok |  |
| `w4_spill_scatter.png` | download_dart_cciw analyze (--skip-download) | ok |  |
| `w4_spill_tdgta_vs_dart.png` | download_dart_cciw analyze (--skip-download) | ok |  |
| `w4_tdg_gt120_annual.png` | w4_cciw_vs_dart.json exceedance_all_downloaded | ok |  |
| `w4_tdg_annual_max.png` | w4_cciw_vs_dart.json exceedance_all_downloaded | ok |  |

## Inventory mapping (draft Fig. → file)

| Fig. | File |
|---|---|
| 1 | `W3_tdgta_on_off_timeseries.png` |
| 2 | `W3_tdgta_on_off_scatter.png` |
| 3 | `W3_tdgta_kge_decomposition.png` |
| 3b/3c | `w1_degray_T_kge_bars.png`, `w1_columbia_DO_kge_bars.png` |
| 4 | `fig04_r2_vs_nse_literature.png` |
| 5 | `fig05_tdg_reachable_range.png` |
| 5 companion | `w4_tdg_gt120_annual.png` |
| 6 | `nhr_dltmax_neg_thickness.png` (+ companions) |
| 7 | `fig07_w2eval_runcard.png` |
| 8 | `w4_spill_tdgta_vs_dart.png` |
| D*/C* | `w1_degray_T_*`, `w1_columbia_DO_*` |
| S1 | `w7_columbia_sod_*` |

## Report note

`00_INDEX/build_repro_report.py` embeds case-local `05_REPRO_RUNS/**/analysis/*.png` (Bonneville TSR/tailwater/SYSTDG, Columbia diagenesis), not the P1 `06_PAPER/figures/` set. Paper/draft figures above were refreshed; full HTML/PDF report regeneration is optional and not required for this redraw.
