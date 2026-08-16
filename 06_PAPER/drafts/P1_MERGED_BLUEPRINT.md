# P1 Merged Blueprint (v2 drafting contract)

**Date:** 2026-08-16  
**Inputs:** `P1_WRITING_FRAMEWORK.md`, `P1_NATURE_ALIGNED_OUTLINE.md`, `NATURE_SKILLS_GUIDE.md`, `P1_GMD_draft_v1.md`, `P1_figure_inventory.md`  
**Outputs:** `P1_GMD_draft_v2.md`, `P1_outline_zh_v2.md`  
**Advisor chat:** https://chatgpt.com/c/6a812957-b108-83ea-b941-617f36744d76  
**Numbers:** bind only to `06_PAPER/analysis/*.json` and `w2eval/cards/*.json`. Do not invent values.

---

## 0. Venue and form (locked)

| Decision | Value |
|---|---|
| Primary venue | *Geoscientific Model Development* |
| Article type | **Methods for assessment of models** |
| Not | Nature Letter / Nat. Commun. condensation |
| Style absorb | nature-skills discipline (short falsifiable contribution sentences; figure-first Results; explicit boundaries) |
| Citation style | Copernicus author–year (not Nature numbered) |
| Title pattern | Provenance- and numerical-health-aware evaluation; avoid standard / universal / mandatory |

**Working English title (v2):**  
Variable provenance, control-state outputs, and numerical health: a methods framework for assessing reported goodness-of-fit in CE-QUAL-W2 v4.5.5 applications (with v5.0 beta example inventory)

**Working Chinese title:**  
变量溯源、控制状态输出与数值健康：面向 CE-QUAL-W2 v4.5.5（兼 v5.0 beta 算例清单）拟合优度报告的方法学评估框架

**One-sentence argument:**  
In CE-QUAL-W2 evaluation practice, the interpretation and cross-study portability of reported goodness-of-fit are conditional on adequate documentation and alignment of variable provenance, controller state, and numerical-health context; we demonstrate these dependencies with official-example reproductions and a 38-paper audit, while distinguishing internal consistency from observational skill and making no claim of out-of-sample NSE performance.

**Evaluation record (named protocol):**  
`Evaluation record = VPR + control-state provenance + NHR + run-card`  
(*R*² / NSE / KGE remain downstream statistics, not a fourth pillar.)

---

## 1. Hard constraints (must survive v2)

1. **Conditional comparability** — not absolute “never comparable.”
2. **Internal consistency ≠ observational skill** (DeGray T, Columbia DO).
3. **No “physical quantity deleted”** — OFF removes gated `TDGTarget_output.csv`; SYSTDG `TDG_output.csv` remains pre-control snapshot.
4. **NHR accompanies reported evaluation statistics**; not a universal timestep law; H1<0 evidence principally Long Lake.
5. **No OOS NSE** in P1; 2016–2025 exceedance is descriptive only.
6. Columbia **SOD = transplanted parameters** (magnitude check only).
7. W5: full text **9/38**; `unknown` ≠ confirmed absent.
8. All headline numbers match analysis JSON (see v1 Unresolved discrepancies list — retain in v2).

---

## 2. Final section order

| # | Section | Contribution / job | Primary Figs / Tables |
|---|---|---|---|
| — | Abstract | Problem → gap → approach → quantified hooks → protocol → boundary | — |
| 1 | Introduction | Relevance → Benicio gap (W5) → C1–C4 bullets → roadmap | Fig. 4 optional early mention |
| 2 | Evidence taxonomy and interpretation rules | Define four claim kinds (skill / internal / NHR / reproducibility) + permitted claims | Table 4 language seed |
| 3 | Assessment methods | Internal order: 3.1 architecture → 3.2 VPR → 3.3 control-state → 3.4 NHR → 3.5 GoF metrics → 3.6 W4/W5 coding → 3.7 w2eval | Fig. 7 (preview); Table 2 methods note |
| 4 | Demonstration corpus | Official examples as **demos**, not validation sites; case→question map | Table 3 |
| 5 | Results | Finding-led, not reservoir-led | see §3 below |
| 5.1 | Variable provenance (observational) | Bonneville A/B/C/S vs CCIW; *R*² band vs NSE span | Figs 1–3; **Table 1**; Fig. 4 |
| 5.2 | Control-state / gated outputs | ON/OFF availability semantics; DART/spill/reachability | Fig. 5; Fig. 8; Table 1 B/S |
| 5.3 | Internal consistency (negative controls) | DeGray T; Columbia DO | Figs D*/C*/3b/3c; **Table 4** |
| 5.4 | Numerical health | Long Lake INTER ON 5/4/1/5 vs OFF 0; Columbia 0/0/0 | Fig. 6; **Table 5** |
| 5.5 | Reproducibility audit and run-card implementation | w2eval + example audit; nest SOD as transplanted-parameter magnitude check only | Fig. 7; Fig. S1; Table 3 |
| 6 | Discussion | Conditional comparability; Bennett/Gupta/Almeida/Benicio; referee pre-answers; labelled Scope and limitations | — |
| 7 | Conclusions | Three claims + run-card sentence; no mandatory standard | — |
| 8 | Code and data availability | JSON authority; cards; scripts; Zenodo stub | `zenodo/` |
| A | Appendix figure map | Paths under `../figures/` | Inventory |

**vs v1 structure change (summary):**  
v1 used classic Model→Protocol→Results(by claim mixed with sites).  
v2 inserts **§2 Evidence taxonomy**, merges model architecture into **§3 Assessment methods**, renames cases to **§4 Demonstration corpus**, and splits Results into **§5.1–5.5 finding blocks** (VPR skill / gating / internal / NHR / repro). Article type label changes from “model evaluation paper” to **Methods for assessment of models**. Figure/table numbers **unchanged**.

---

## 3. Contribution sentences (use in Intro; falsifiable)

### C1 — Variable provenance (VPR)
> We show that goodness-of-fit statistics can depend materially on the provenance of the evaluated output variable, and introduce a **variable provenance record (VPR)** that makes the model quantity, extraction route, processing state, and evaluation target explicit.

Bonneville lock: same CCIW pairs (*n* = 1614), *R*² ≈ 0.51–0.55 while NSE spans −2.80 to +0.50 (`w3_tdgta_off_metrics.json`).

**Do not write:** “*R*² is misleading and NSE reveals true skill.”  
**Write:** “*R*² and NSE describe different properties; neither resolves ambiguity in *which* model quantity entered the metric.”

### C2 — Control-state / gated outputs
> We identify **control-state dependence** as a source of **evaluation ambiguity** when diagnostic or controller-specific outputs are conditionally available, and incorporate control-state provenance into the evaluation record.

Operational lock: OFF removes `TDGTarget_output.csv`; SYSTDG `TDG_output.csv` remains pre-control snapshot (ON/OFF MAE = 0). Avoid “confounder” if it invites causal over-reading.

### C3 — Numerical health record (NHR)
> We propose that statistical performance be accompanied by a **numerical health record (NHR)** documenting execution diagnostics relevant to interpretation of **reported evaluation statistics**.

Bound: reporting recommendation, not universal timestep law; clearest H1<0 evidence at Long Lake (ON 5/4/1/5; OFF 0/0/0/0).

### C4 — Run-cards / demo corpus
> We implement these reporting elements in reproducible **run-cards** and use official CE-QUAL-W2 examples as a heterogeneous **demonstration corpus** for auditing evaluation provenance and numerical-health information.

**Forbidden:** “first reproducible validation of CE-QUAL-W2.”

### Core conceptual pair (Abstract / Discussion)
> A goodness-of-fit value is not only a property of a model and observations; it is a property of a specified model quantity, observation pairing, processing pathway, run configuration, and metric.  
> This does **not** make cross-study comparison intrinsically invalid; it makes interpretation **conditional** on sufficient alignment of those evaluation conditions.

---

## 4. Case → question map

| Case | Role in v2 | Claim kind |
|---|---|---|
| Bonneville TDG | VPR + metric sensitivity vs CCIW | Observational skill |
| TDGTA ON/OFF | Gated-output semantics | Control-state evaluation ambiguity |
| DeGray T | Channel disagreement on one run | Internal consistency |
| Columbia DO | Station ambiguity on one run | Internal consistency |
| Columbia SOD | Transplanted-parameter magnitude | Reproducibility / plausibility |
| Long Lake | H1<0 under exit 0 | Numerical health |
| W5 38-paper audit | Literature motivation for VPR gap | Gap evidence (not a W2 run) |

---

## 5. Figure → SciencePlots file map (paths relative to `drafts/`)

Filenames unchanged after 2026-08-16 SciencePlots redraw; cite `../figures/`.

| Fig. | File | Defends (one sentence) | Draft home (v2) |
|---|---|---|---|
| 1 | `../figures/W3_tdgta_on_off_timeseries.png` | Multiple TDG channels and ON/OFF diverge visually against CCIW in the paired window. | §5.1 |
| 2 | `../figures/W3_tdgta_on_off_scatter.png` | 1:1 slopes differ across calibers despite similar correlation. | §5.1 |
| 3 | `../figures/W3_tdgta_kge_decomposition.png` | Claim-1 glance: α/β, not *r*, separate A/C from B. | §5.1 (lead) |
| 3b | `../figures/w1_degray_T_kge_bars.png` | Internal-consistency α/β failure for DeGray T. | §5.3 |
| 3c | `../figures/w1_columbia_DO_kge_bars.png` | Internal-consistency α/β failure for Columbia DO. | §5.3 |
| 4 | `../figures/fig04_r2_vs_nse_literature.png` | Same *R*² band can hide NSE collapse; literature rug is *R*²-only. | §5.1 end |
| 5 | `../figures/fig05_tdg_reachable_range.png` | 15.55% of paired obs >120% unreachable on gated B. | §5.2 |
| 5c | `../figures/w4_tdg_gt120_annual.png` | Exceedance frequency 2011–2025 (not forecast skill). | §5.2 |
| 6 | `../figures/nhr_dltmax_neg_thickness.png` | Long Lake ON vs OFF negative-thickness counts. | §5.4 |
| 6c | `../figures/nhr_dltmax_layers_dltmin.png`, `nhr_dltmax_heatmap.png` | Companions for DLT/layer context. | §5.4 |
| 7 | `../figures/fig07_w2eval_runcard.png` | Three-block evaluation record as run-card. | §5.5 |
| 8 | `../figures/w4_spill_tdgta_vs_dart.png` | Reallocation changes spill programme vs 2011 DART. | §5.2 |
| 8c | `../figures/w4_spill_scatter.png` | Spill companion scatter. | §5.2 |
| D1–D3 | `../figures/w1_degray_T_*.png` | DeGray internal panels. | §5.3 |
| C1–C2 | `../figures/w1_columbia_DO_*.png` | Columbia internal panels. | §5.3 |
| S1 | `../figures/w7_columbia_sod_*.png` | SOD magnitude band check (not calibration). | §5.5 |
| W4 extras | `w4_cciw_vs_dart_*.png`, `w4_tdg_annual_max.png` | Library identity / annual max (cited, not renumbered). | §5.2 |

**Narration rule:** open §5.1 with Fig. 3 (glance test), then Table 1, then Figs 1–2.

---

## 6. Writing cues vs Bennett / Gupta / Almeida / Benicio

| Anchor | How to write in v2 | Where |
|---|---|---|
| **Bennett et al. 2013** (EMS evaluation guidelines) | Frame P1 as making *evaluation conditions* explicit for W2; do not claim a new universal EMS standard. Cite as practice context for assessment transparency. | Intro bridge; Discussion §6.1 |
| **Gupta et al. 2009** (KGE decomposition) | Own the theoretical spine: *R*² cannot see α/β; KGE/NSE can. Keep formula in Methods; Fig. 3 is the empirical glance. | §3 Metrics; §5.1; Discussion |
| **Almeida & Coelho 2025** (GMD W2 evaluation) | **Complement, not compete:** they evaluate diagenesis *process options* with open archives; we evaluate the *assessment layer* under GOF statistics. SOD band = magnitude sanity only. | Intro; §5.5; Discussion §6.x |
| **Benicio et al. 2024** | Gap engine via W5 counts; do not treat Table 2 0.32–0.977 as like-for-like skill span. | Intro; §5.1 literature block |
| **Knoben / Legates / Clark / Planque / Stagge** | Optional support citations if space; do not expand into a review. | Discussion light touch |

**Tone:** GMD Methods — assessment object = evaluation workflow; demos illustrate failure modes; protocol = reporting recommendation.

---

## 7. Nature-skills discipline checklist (apply without Letter compression)

- [ ] One paragraph, one job (context / gap / approach / result / comparison / implication / limitation).
- [ ] Contribution bullets: show/demonstrate verbs; bounded conditions; JSON-adjacent numbers.
- [ ] Claims stay next to figures/tables (no claim stack then evidence dump).
- [ ] Ban unsupported first / comprehensive / always / never / mandatory standard.
- [ ] Abstract pattern: problem → gap → approach → results → implication → boundary (GMD length OK).
- [ ] Preserve in-line Methods depth (source paths, pairing rules, counting rules).

---

## 8. Drafting rules for `P1_GMD_draft_v2.md`

1. **Do not destroy v1** — new file only.
2. Preserve Unresolved discrepancies block and all JSON-locked tables.
3. Retarget header to Methods for assessment; update roadmap sentences to new § numbers.
4. Move DeGray/Columbia narrative from under “Variable provenance” into **§5.3**; keep Bonneville + literature audit in **§5.1**.
5. Keep Discussion referee pre-answers; strengthen Bennett/Gupta/Almeida sentences.
6. Figure paths remain `../figures/...` (SciencePlots redraw filenames unchanged).
7. No Zenodo DOI invention; no OOS NSE; no commit.

---

## 9. Deliverables this merge

| File | Action |
|---|---|
| `drafts/P1_MERGED_BLUEPRINT.md` | This contract |
| `drafts/P1_GMD_draft_v2.md` | Restructured English draft |
| `drafts/P1_outline_zh_v2.md` | Chinese outline aligned to v2 |
| `drafts/P1_review_checklist.md` | Point to v2 + blueprint |
| `notes/STATUS_20260815.md` | Append merge status |
| `notes/MERGE_BLUEPRINT_V2_20260816.md` | Short acceptance |

**User-side blockers (unchanged):** Zenodo upload/DOI; optional OOS (P2 roadmap only).
