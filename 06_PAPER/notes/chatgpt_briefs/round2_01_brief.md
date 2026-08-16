# ROUND 2-01 brief — Paper de-processization (paper ≠ research report)

**Date:** 2026-08-17  
**Repo:** https://github.com/Coucou2016/20260810-CE-QUAL-W2  
**Role:** GMD Methods manuscript advisor (English academic style). Read GitHub; do **not** ask for uploaded attachments.  
**Web search:** ON (GMD Methods for assessment; Almeida & Coelho 2025; Bennett et al. 2013; Gupta KGE phrasing).

## Background

Prior Cursor×ChatGPT rounds matured numbers, figures, and claim boundaries in `06_PAPER/drafts/P1_GMD_draft_v2.md`. This **second series (ROUND 2)** targets **publication-facing prose hygiene**: the manuscript must read as a GMD Methods paper, not as an internal research report or dual-agent lab notebook.

## This round’s question

Scan the manuscript for **process / tooling / collaboration / local-path residue** and propose **sentence-level rewrites** that a GMD referee would accept.

Specifically identify and rewrite (or flag for deletion) any of:

1. Absolute Windows paths, `I:\`, drive letters, or “local project root” language in the **paper body**.
2. Mentions of Cursor, ChatGPT, dual-agent, advisor rounds, blueprints, iteration logs.
3. Working Chinese title / draft-status banners / unresolved-discrepancy checklists that belong in notes, not in a submitted Methods article.
4. Internal script stacks as scientific narrative (`00_INDEX/parse_nhr.py`, `pairing_tolerance_scan.py`, HTML build scripts, SciencePlots redraw logs) — keep scientific meaning; move path inventories to Code availability with **repository-relative** paths only.
5. HTML HTML-comment JSON tags are OK as author notes if stripped at build; flag if they leak into readable prose.
6. Appendix A “figure file map” if it reads as an internal inventory rather than SI-ready captions.

**Allowed academic substitutes:** “archived with the manuscript / in the accompanying GitHub repository / in the analysis JSON deposited with the code”; name scientific objects (VPR, NHR, run-card), not CI tools.

## Files to read on GitHub (in order)

1. `06_PAPER/notes/chatgpt_briefs/round2_01_brief.md` (this file)
2. `06_PAPER/drafts/P1_GMD_draft_v2.md` — **primary** (full manuscript)
3. `06_PAPER/report/report.md` — contrast: report may keep process detail; paper must not
4. `06_PAPER/drafts/P1_claim_evidence_matrix.md` — claim boundaries only
5. `06_PAPER/notes/ITER_5ROUNDS_FINAL_20260816.md` — prior maturity context (do not paste process into paper)

Optional style anchors (web):

- https://gmd.copernicus.org/methods_for_assessment_of_models.html
- https://doi.org/10.5194/gmd-18-6135-2025 (Almeida & Coelho 2025)
- https://www.geoscientific-model-development.net/submission.html (abstract rules)

## Hard constraints (do not violate)

- **internal ≠ skill:** DeGray T and Columbia DO are internal consistency, never observational skill.
- **Gate ≠ delete physics:** TDGTA OFF removes `TDGTarget_output.csv`, not the physical TDG variable; SYSTDG snapshot remains.
- **NHR ≠ timestep law:** do not claim smaller Δt is less stable; Long Lake 5/4/1/5 is `DLTINTER=ON` knot result only.
- **No OOS NSE:** 2016–2025 used for exceedance/spill context only.
- **SOD transplant:** Columbia diagenesis from DeGray template; not field calibration.
- **W5 unknown:** unknowns stay unknown; never invent absence.
- **No invented provenance / DOI / Zenodo DOI.**
- Do not invent numbers; cite JSON if proposing numeric edits (none expected this round).

## Known JSON number summary (do not change this round)

| Claim | Anchor | Source |
|---|---|---|
| VPR-core yes | 2/38 (5.3%) | `w5_lit_audit_summary.json` |
| Table-2 R² objects | **1 / 7 / 4** | same |
| Full text | 9/38 (23.7%) | same |
| Bonneville A/B/C NSE | −2.804 / +0.500 / −2.752; R² ~0.508–0.551; n=1614 | `w3_tdgta_off_metrics.json` |
| Obs >120% | 15.55% (251/1614) | same |
| DART MAE | 0.026537%; match 0.994945; n=17805 | `w4_cciw_vs_dart.json` |
| Long Lake NHR | ON 5/4/1/5; OFF 0/0/0/0 | `nhr_dlt_scan.json` |
| DeGray internal | R²=0.9027, NSE=−0.5855 | `w1_provenance_metrics.json` |
| Columbia DO internal | R²=0.6505, NSE=−1.4821 | same |
| Columbia SOD mean | 0.8762 g O₂ m⁻² d⁻¹; in-band 0.8955 | `w7_columbia_sod_vs_almeida.json` |

## Deliverables requested from advisor

1. **Hit list** of process/tooling/local-path/collaboration residues in `P1_GMD_draft_v2.md` (quote short excerpts + line-theme).
2. **Rewrite table:** for each hit, proposed replacement sentence(s) suitable for GMD Methods (English).
3. **Front-matter recommendation:** what to delete vs move to `report.md` / notes (Working Chinese title; Draft status; Unresolved discrepancies; HTML HTML comments).
4. **Code availability rewrite sketch** (≤15 lines): GitHub URL + Zenodo **待补充** placeholder + repository-relative paths only; no “user steps” tutorial voice if avoidable—use “Authors will mint…” / “A persistent archive is pending.”
5. **Do-not-touch list:** numbers, hard-constraint claims, figure science.
6. Confirm: paper vs report separation is clear after proposed edits.

## Out of scope this round

Full Abstract/Intro stylistic polish (ROUND 2-02); number re-audit (ROUND 2-03); caption SciencePlots (ROUND 2-04); HTML regen / Zenodo checklist (ROUND 2-05).
