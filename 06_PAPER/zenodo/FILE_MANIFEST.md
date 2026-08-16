# Zenodo file manifest (relative to project root)

Roles: **include** = recommended in deposit; **subset** = include only listed outputs, not whole tree; **cite-only** = do not upload bulk; **prep** = this packaging folder.

**No upload performed.** Paths are planning references.

---

## A. Paper package (`06_PAPER/`) — include

| Relative path | Role |
|---|---|
| `06_PAPER/drafts/P1_GMD_draft_v2.md` | Manuscript draft (current) |
| `06_PAPER/drafts/P1_GMD_draft_v1.md` | Prior structural draft (retained) |
| `06_PAPER/drafts/P1_MERGED_BLUEPRINT.md` | Drafting contract |
| `06_PAPER/drafts/P1_claim_evidence_matrix.md` | Claim ↔ evidence freeze |
| `06_PAPER/drafts/P1_outline_zh_v2.md` | ZH claim map (v2) |
| `06_PAPER/drafts/P1_outline_zh.md` | ZH claim map (v1 retained) |
| `06_PAPER/drafts/P1_review_checklist.md` | Author review checklist |
| `06_PAPER/drafts/P1_figure_inventory.md` | Figure path inventory |
| `06_PAPER/notes/PRESUBMISSION_LOCAL_20260816.md` | Local pre-sub checklist status |
| `06_PAPER/notes/P1_number_audit_20260816.md` | Headline number audit vs JSON |
| `06_PAPER/PAPER_PLAN_20260815.md` | Study plan |
| `06_PAPER/notes/STATUS_20260815.md` | Status snapshot |
| `06_PAPER/notes/W1_W7_findings.md` | Workstream notes |
| `06_PAPER/notes/W2_findings.md` | NHR notes |
| `06_PAPER/notes/W3_findings.md` | TDGTA notes |
| `06_PAPER/notes/W4_findings.md` | DART / spill notes |
| `06_PAPER/notes/W5_findings.md` | Literature audit notes |
| `06_PAPER/notes/P2_oos_roadmap.md` | Out-of-sample NSE roadmap (no run) |
| `06_PAPER/zenodo/README_ARCHIVE.md` | Archive policy |
| `06_PAPER/zenodo/FILE_MANIFEST.md` | This list |
| `06_PAPER/zenodo/checksums.sha256` | Hashes of small include set |

## B. Analysis products — include

| Relative path | Role |
|---|---|
| `06_PAPER/analysis/w1_provenance_metrics.json` | Table 4 / DeGray–Columbia |
| `06_PAPER/analysis/w3_tdgta_off_metrics.json` | Table 1 TDGTA ON/OFF |
| `06_PAPER/analysis/w4_cciw_vs_dart.json` | DART match + spill + exceedance |
| `06_PAPER/analysis/w5_lit_audit.csv` | 38-study coding |
| `06_PAPER/analysis/w5_lit_audit_summary.json` | Table 2 aggregates |
| `06_PAPER/analysis/w7_columbia_sod_vs_almeida.json` | SOD magnitude |
| `06_PAPER/analysis/nhr_dlt_scan.json` | Table 5 NHR |
| `06_PAPER/analysis/nhr_existing_runs.json` | Pre-scan inventory |
| `06_PAPER/analysis/plot_p1_missing_figures.py` | Fig. 4/5/7 generator |
| `06_PAPER/analysis/plot_nhr_scan.py` | NHR figures |
| `06_PAPER/analysis/w1_w7_provenance.py` | Provenance metrics emitter |

**Exclude:** `06_PAPER/analysis/_w5_cache/` (PDFs, API caches).

## C. Figures — include

| Relative path | Role |
|---|---|
| `06_PAPER/figures/fig04_r2_vs_nse_literature.png` | Fig. 4 |
| `06_PAPER/figures/fig05_tdg_reachable_range.png` | Fig. 5 |
| `06_PAPER/figures/fig07_w2eval_runcard.png` | Fig. 7 |
| `06_PAPER/figures/W3_tdgta_*.png` | Fig. 1–3 family |
| `06_PAPER/figures/w4_*.png` | Spill / CCIW–DART / gt120 |
| `06_PAPER/figures/nhr_dltmax_*.png` | Fig. 6 family |
| `06_PAPER/figures/w1_*.png` | DeGray / Columbia internal |
| `06_PAPER/figures/w7_*.png` | SOD panels |

(Full listing = all `06_PAPER/figures/*.png` present on disk at packaging time.)

## D. w2eval — include

| Relative path | Role |
|---|---|
| `06_PAPER/w2eval/w2eval.py` | Card builder |
| `06_PAPER/w2eval/README.md` | Protocol notes |
| `06_PAPER/w2eval/cards/index.json` | Card index |
| `06_PAPER/w2eval/cards/bonneville_tdgta_on.{md,json}` | Run-card ON |
| `06_PAPER/w2eval/cards/bonneville_tdgta_off.{md,json}` | Run-card OFF |
| `06_PAPER/w2eval/cards/degray_t_internal.{md,json}` | Internal T |
| `06_PAPER/w2eval/cards/columbia_do_internal.{md,json}` | Internal DO |
| `06_PAPER/w2eval/cards/longlake_dlt_nhr.{md,json}` | NHR card |

## E. Observations — include (small)

| Relative path | Role |
|---|---|
| `06_PAPER/data/dart_cciw/cciw_hourly_2011.csv` … `cciw_hourly_2025.csv` | DART CCIW hours |
| `06_PAPER/data/dart_cciw/download_log.json` | URLs + per-file sha256 |

## F. Model runs — subset only

| Relative path / pattern | Role |
|---|---|
| `05_REPRO_RUNS/run_20260814_bonneville/Bonneville_SYSTDG/w2_con.csv` | Control (TMEND, TDGTA) |
| `…/QGT_BON_2011_2015_daily_DSS-scaled.csv` | Gate outflow input |
| `…/HOXO_DLS_BON_2011_2015_MET_withBP.csv` | Meteorology |
| `…/THE_DALLES_OUTFLOW.csv` | Upstream boundary |
| `…/BonnevilleDam_DistributedTributaryInflow.npt` | Distributed inflow |
| `…/BON_NAVD88_BTH_2011.csv`, `BON_WSC.npt`, `BON_SHD_1.npt` | Bathymetry / wind / shade |
| `…/CCIW_TDG_Temp_2011-2015.csv` | Example obs file |
| `…/TDGTarget_output.csv`, `TDG_output.csv`, `BON_tsr_*`, `*_wdo_76.csv`, `flowbal.csv`, `w2.wrn` | **Evaluation outputs** |
| Same pattern under `run_20260814_bonneville_notarget/` | TDGTA OFF twin |
| Long Lake / Columbia / DeGray: `w2_con.csv` + VPR-named series + `w2.wrn` | NHR / internal consistency |

**Do not archive whole trees:** `BON_spr.csv`, `BON_snp.opt`, `BON_flx.opt`, `Bonneville.w2l`, gate-by-gate `*wo_gate*` dumps unless a VPR cites them.

## G. Cite-only (too large or redistributable upstream)

| Relative path | Role |
|---|---|
| `01_RAW_DOWNLOADS/` (~656 MB) | cite-only |
| `02_LIBRARY/` bulk manuals/source (~353 MB) | cite-only; ship used example decks only |
| `05_REPRO_RUNS/` full (~2.6 GB) | cite-only except §F subset |
| `03_MERGED_PDF/`, `04_MARKDOWN/` | optional / omit |
| CE-QUAL-W2 `.exe` / compiler builds | cite ERDC/PSU; record local hash in README if needed |

## H. Size snapshot (planning, 2026-08-15)

| Tree | Approx. size |
|---|---|
| `06_PAPER/figures` | 2.7 MB |
| `06_PAPER/analysis` (no `_w5_cache`) | <1 MB |
| `06_PAPER/data/dart_cciw` | 11 MB |
| `06_PAPER` drafts+cards+notes | <1 MB |
| Bonneville ON full run dir | ~408 MB |
| Core deposit if §A–E + §F subset | likely **tens of MB**, not GB |
