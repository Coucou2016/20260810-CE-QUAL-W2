# Dual-agent GitHub review — 20260816

> **Deduped:** Primary public-release dual-agent log is `DUAL_AGENT_GITHUB_20260816.md`. This file keeps only the *second* ChatGPT GitHub-review pass (checklist + DOI verify). Do not duplicate push/repo baseline labor from the primary note.


**ChatGPT (advisor):** https://chatgpt.com/c/6a8188fb-f1f0-83ea-b44b-cd639d077748  
**Title:** GMD框架复核与创新 / GitHub仓库评审  
**Mode:** new chat; web search ON; **no attachments**; text asked ChatGPT to read public repo  
**GitHub read?** **Yes** — ChatGPT stated「仓库已能直接读取」and cited draft/JSON/notes paths; also「已搜索 7 个网站」(+ follow-on GitHub/web searches)  
**Cursor (executor):** independent verify + minimal local edits + push  

Raw advisor extract: `chatgpt_briefs/github_repo_review_raw_20260816.md`

---

## 1) Problem understanding (shared)

Reported CE-QUAL-W2 goodness-of-fit (especially *R*²) is not a portable ranking of “calibration quality” unless the **evaluation object** is reconstructable: output file/column, segment/layer, derivation, time support/pairing, **control-state / gated outputs**, and **numerical-health** context. The public repo demonstrates this with official v4.5.5 examples + a 38-paper audit (Benicio et al. 2024), while locking hard boundaries (no invented Zenodo DOI; no OOS NSE; DeGray/Columbia = within-run diagnostics).

## 2) GMD Methods framework — still appropriate?

| Source | Verdict |
|---|---|
| Advisor | **KEEP** Methods for assessment of models (better than Model evaluation) |
| Cursor | **Agree** — inference object is the evaluation workflow/record, not process-option skill ranking (contrast Almeida & Coelho 2025, Model evaluation) |
| Primary URL | https://www.geoscientific-model-development.net/about/manuscript_types.html |

## 3) Innovation strength — overclaim / underclaim

| Claim class | Advisor | Cursor |
|---|---|---|
| Multi-metric / *R*² limits | Background (Bennett 2013; Gupta 2009), not novelty | **Agree** |
| Provenance / run-record as first invention | **Too strong** — ESMValTool provenance (Schlund 2023); REF (Hoffman 2026) | **Agree — veto “first”** |
| CE-QUAL-W2-specific evaluation-object + control-state + NHR | **Defendable novelty** | **Agree — keep as core** |
| W5 “almost never present” | Soften (2/38 confirmed; 19 unknown) | **Adopted** |
| “Same physical quantity” | Soften → constituent/family + operators | **Adopted** |

**Stable one-line contribution (Cursor):** Metrics must bind to a reconstructable CE-QUAL-W2 evaluation object plus control-state and numerical-health context before cross-study comparison.

## 4) ≤10 minimal modification checklist

| # | Item | Status this pass |
|---|---|---|
| 1 | Soften W5 “almost never present” → confirmed 2/38; unknown ≠ absence | **Done** (`P1_GMD_draft_v2.md`) |
| 2 | Disambiguate *R*² as squared Pearson correlation | **Done** |
| 3 | Explicit prior-art: Schlund 2023 + Hoffman 2026 + Almeida 2025 Model-evaluation contrast | **Done** (Intro) |
| 4 | Soften “same physical quantity” | **Done** (§3.1) |
| 5 | Clarify internal consistency = within-run cross-output diagnostic | **Done** (§2) |
| 6 | Remove hardcoded `I:\Projects\...` in `w2eval.py` | **Done** |
| 7 | Bonneville B/S pairing sensitivity (hourly obs ↔ daily model) | **Queued** (would touch metrics JSON; not this push) |
| 8 | Split observational vs within-run panels on R²–NSE figures | **Queued** (figure regen) |
| 9 | NHR axis = DLTMAX knot + realized `window_dlt` | **Queued** |
| 10 | Frozen archive / Zenodo mint when ready; no placeholder DOI | **Queued** (user-gated) |

Advisor P0 order was 7→3→6; Cursor applied the text/portability items immediately and deferred JSON/figure regenerations.

## 5) Primary literature DOIs (Cursor WebSearch verified)

| Citation | DOI / URL | Verified |
|---|---|---|
| GMD manuscript types | https://www.geoscientific-model-development.net/about/manuscript_types.html | Yes |
| GMD code & data policy | https://www.geoscientific-model-development.net/policies/code_and_data_policy.html | Yes (policy page) |
| Hoffman et al. 2026 REF | https://doi.org/10.5194/gmd-19-7415-2026 | Yes |
| Schlund et al. 2023 ESMValTool | https://doi.org/10.5194/gmd-16-315-2023 | Yes |
| Almeida & Coelho 2025 | https://doi.org/10.5194/gmd-18-6135-2025 | Yes |
| Benicio et al. 2024 | https://doi.org/10.3390/w16243556 | Yes |
| Bennett et al. 2013 | https://doi.org/10.1016/j.envsoft.2012.09.011 | Cited; not re-fetched this pass |
| Gupta et al. 2009 | https://doi.org/10.1016/j.jhydrol.2009.08.003 | Cited; not re-fetched this pass |

## 6) Adopt / veto summary

- **Adopt:** KEEP GMD Methods; narrow novelty to W2 evaluation-object contract; softens above; portable `w2eval` root.
- **Veto / do not:** invent Zenodo DOI; claim OOS NSE; claim TDG “physically deleted”; claim universal timestep-stability law; claim “first CE-QUAL-W2 reproducible framework.”
- **Defer:** pairing sensitivity + figure panel splits (need controlled JSON/figure regen, not big raw data).

## 7) Push

Public repo: https://github.com/Coucou2016/20260810-CE-QUAL-W2  
This review’s commit is recorded in git history after `d8ef2d1` (initial public push) / subsequent status notes.
