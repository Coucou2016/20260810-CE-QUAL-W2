# Deliverables review judgment — 2026-08-16

Cursor = independent verifier. ChatGPT advisor chat `https://chatgpt.com/c/6a815e07-55b8-83ea-9f34-e1929be4f609` enabled web search but **did not deliver** the five-task structured review (see raw note). Judgment below is therefore **Cursor-primary**, with advisor acknowledgements logged only as process evidence.

---

## 1) GMD Methods for assessment — structure check (PASS with one submission blocker)

**Primary sources verified:**

| Claim | Source | Cursor verdict |
|---|---|---|
| Manuscript type covers metrics / novel comparison with observations / software tools for assessment | https://www.geoscientific-model-development.net/about/manuscript_types.html | **PASS** — our object is evaluation workflow (VPR/control/NHR/run-cards), not a new process module |
| Every paper needs **Code and data availability** before acknowledgements | https://www.geoscientific-model-development.net/policies/code_and_data_policy.html | **PASS structure / FAIL mint** — §8 exists in `P1_GMD_draft_v2.md` but Zenodo DOI still **待补充** |
| Methods-for-assessment / software tools: name+version in title; code for review | same manuscript-types + code policy pages | **PASS local** — title locks v4.5.5 (+ v5.0 beta inventory); `w2eval` is MVP cards writer |
| Figures: self-contained manuscript PDF at submission | GMD author/submission pages | **Local HTML is self-contained**; camera-ready PDF/Zenodo still user-gated |

**Skeleton alignment:** Intro → taxonomy → methods → corpus → finding-led results → discussion → conclusions → Code/Data availability → refs is compatible with GMD Methods spine. No forced rename of existing Fig.1–8 inventory.

---

## 2) Abstract / contributions — strength

**Cursor verdict:** Already appropriately conditional after prior rounds. Keep:

- “cannot generally be established from the reported metric alone”
- internal consistency labels for DeGray/Columbia
- gated file ≠ physical deletion
- NHR as **should / reporting recommendation**, not universal Δt law
- no OOS NSE

**Do not** accept whole-cloth Abstract rewrites that dilute JSON anchors (historical veto still stands).

---

## 3) Report figure + glossary readability — weakest 3 (Cursor)

After deepening narratives + glossary this round, residual weak spots:

1. **Columbia DO KGE / short-series figures** — even with five blocks, short n≈23 d and α/β jargon remain hard for non-specialists; keep “不是观测技能” callout adjacent.  
2. **NHR heatmaps / layer-add bars** — still denser than Bonneville story; rely on “急刹车记账” plain block.  
3. **W5 literature plane (fig04)** — evidence-type colors must be read before numbers; caption/body already warn, but non-specialists may still misread as skill ranking.

---

## 4) Near-2-year literature (Cursor WebSearch; optional cites)

Verified DOIs/URLs (complementary, not required core):

| Paper | DOI | Role |
|---|---|---|
| Building trust in large-scale water quality models: 13 alternative strategies beyond validation (2024) | https://doi.org/10.1007/s43832-024-00149-y | Trust beyond validation — soft optional cite |
| EnvSoft computational reproducibility of geo-simulation experiments (2025) | https://doi.org/10.1016/j.envsoft.2025.106323 | Reproducibility assessment framework — soft optional |
| Watershed sediment/nutrient performance criteria fine timescales (Water Research 2025) | https://doi.org/10.1016/j.watres.2025.123156 | Performance-criteria culture — soft optional |
| DL water-quality trustworthiness protocol (arXiv 2025) | https://doi.org/10.48550/arxiv.2503.09947 | Reproducibility dimension — **soft only** (ML-focused) |

**Veto as structural templates:** ML trust protocols or ODE/data-descriptor papers that would displace GMD Methods spine (consistent with prior lit-frame vetoes).

---

## 5) ≤7 minimal revisions (adopted / deferred)

| # | Item | Decision |
|---|---|---|
| 1 | Strengthen §8 wording with explicit GMD policy URLs; keep Zenodo as 待补充 | **DONE** (draft v2) |
| 2 | Report fig block titles + deep narratives + KTMAX/forrtl glossary | **DONE** (report rebuild) |
| 3 | Cover entry in report TOC | **DONE** |
| 4 | Mint Zenodo DOI | **DEFERRED** (user account) |
| 5 | Add optional 2024–25 trust/reproducibility cites | **SOFT** — not required this round |
| 6 | Whole Abstract rewrite | **VETO** |
| 7 | Open OOS / invent DeGray·Columbia obs | **VETO** |

---

## Advisor vetoes this round

| Item | Reason |
|---|---|
| Empty “web search enabled” replies as review deliverable | No five-task substance |
| Any CardioFAN / arterial PTT ranking appearing in wrong tab | Crosstalk; unrelated project |
| Claims that would require fabricated Zenodo DOI | Forbidden |
