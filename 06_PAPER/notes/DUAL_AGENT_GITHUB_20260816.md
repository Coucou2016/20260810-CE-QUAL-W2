# Dual-agent GitHub public release — 2026-08-16

Cursor = sole executor + independent verifier. ChatGPT = advisor with **web search ON**. Advisor output not trusted without verification.

---

## 1. Collaboration link

| Item | Value |
|---|---|
| ChatGPT conversation | https://chatgpt.com/c/6a81889c-05ec-83ea-8a40-bdad88d5ecda （标题「GitHub仓库评审」） |
| Mode | New chat; **网页搜索** chip ON; text brief + GitHub URL only; **no attachments** |
| Isolation | Explicitly instructed not to reuse prior review memory |
| Prior failed/partial advisor turns | R2 deliverables chat `6a815e07-…` (search-only); not used as source |

---

## 2. Baseline (Phase 0)

| Item | Value |
|---|---|
| Root | `I:\Projects\20260810-CE-QUAL-W2` |
| Start Git | No usable public remote at start of authorized push cycle; local `.git` initialized / reused |
| Key docs read | `STATUS_20260815.md`, `PRESUBMISSION_LOCAL_20260816.md`, `DUAL_AGENT_REPORT_20260816_R2.md`, `P1_GMD_draft_v2.md`, `06_PAPER/report/report.md`, `GITHUB_UPLOAD_PLAN.md` |
| Report paths | `06_PAPER/report/report.md` (source); large html/pdf gitignored |
| gh | `C:\Program Files\GitHub CLI\gh.exe` v2.97.0; logged in as **Coucou2016** |

---

## 3. GitHub public repo (Phase 1–2)

| Item | Value |
|---|---|
| URL | https://github.com/Coucou2016/20260810-CE-QUAL-W2 |
| Visibility | **PUBLIC** |
| Initial commit | `d8ef2d1a4b36536f4135278b24fcd3becf1b760d` |
| Tracked | ~146 files / ~7.8 MB (scripts, drafts md, analysis JSON, figures png, w2eval, notes, zenodo manifests) |
| Excluded | `01_RAW_DOWNLOADS`, `02_LIBRARY`, run outputs, dart_cciw cache, regenerable html/pdf (`P1_paper.html`, report.html/pdf), `_w5_cache`, secrets |
| Manifest | `06_PAPER/GITHUB_CONTENTS.md` + root `.gitignore` |

---

## 4. ChatGPT advice (Phase 3) — verified summary

### Adopted (reasonable)

1. Lock novelty to **CE-QUAL-W2-specific operationalization** of VPR + controller-conditional outputs + NHR; do **not** claim inventing provenance.
2. Distinguish **full VPR** vs literature-audit **VPR-core** (2/38 is core, not eight-field complete).
3. Table 2 classification **1 confirmed skill / 7 confirmed other / 4 unresolved**.
4. Bonneville = evaluation-object sensitivity (pairing 0.05 d vs 0.6 d), not a strict single-factor causal claim.
5. Define NHR as **execution-diagnostic record**, not convergence/stability certificate.
6. Align Code/Data availability with public GitHub subset + “Zenodo not minted”.
7. Fix Almeida pages to **6135–6165**.
8. Cite prior-art Methods papers (ESMValTool, PMP, CMIP7 REF, FAIR models) as boundary.

### Deferred (time / scope)

- Full Fig. 4 visual redesign (marker/facet); migrate all report figure narratives into paper captions.
- Global rename `caliber` → `evaluation channel` across scripts/cards.
- Zenodo mint / full config+run archive packaging.
- Regenerate large HTML/PDF this pass.

### Rejected

- Inventing Zenodo DOI or OOS NSE.
- Absolute “first provenance framework” novelty.
- Claiming DeGray/Columbia observational skill; TDG physics deleted; small-timestep instability law.
- Merging Table 2 unknowns into confirmed non-skill.

---

## 5. Local changes this pass (Phase 4)

| File | Change |
|---|---|
| `README.md` | Public-repo entry + paper/report pointers |
| `.gitignore` | Exclude large runs / caches / regenerable html/pdf |
| `06_PAPER/GITHUB_CONTENTS.md` | Include/exclude list |
| `06_PAPER/drafts/P1_GMD_draft_v2.md` | VPR-core; Table 2 1/7/4; NHR wording; pairing caveat; prior-art boundary; Almeida pages; §8 GitHub note; prior-art refs |
| `06_PAPER/report/report.md` | Table 2 1/7/4 wording |
| `06_PAPER/notes/DUAL_AGENT_GITHUB_20260816.md` | This report |
| `06_PAPER/notes/chatgpt_briefs/github_repo_review_20260816.md` | Brief pointer + conversation URL |

**HTML/PDF regeneration:** deferred (md sources updated; rebuild with `build_research_report.py` / `build_paper_html.py` when needed).

---

## 6. DOI / URL verification (local WebSearch)

| Citation | DOI / URL | Result |
|---|---|---|
| GMD manuscript types | https://www.geoscientific-model-development.net/about/manuscript_types.html | PASS (policy page) |
| GMD code/data policy | https://www.geoscientific-model-development.net/policies/code_and_data_policy.html | PASS |
| Hoffman et al. 2026 REF | https://doi.org/10.5194/gmd-19-7415-2026 | **PASS** (GMD 19, 7415–7455) |
| Schlund et al. 2023 ESMValTool | https://doi.org/10.5194/gmd-16-315-2023 | **PASS** |
| Lee et al. 2024 PMP v3 | https://doi.org/10.5194/gmd-17-3919-2024 | **PASS** (GMD 17, 3919–3948) |
| Kettner et al. 2026 FAIR | https://doi.org/10.5194/gmd-19-5381-2026 | **PASS** (GMD 19, 5381–5399; advisor had 5404 — corrected) |
| Almeida & Coelho 2025 | https://doi.org/10.5194/gmd-18-6135-2025 | **PASS**; pages **6135–6165** (was 6161 locally) |
| Benicio et al. 2024 | https://doi.org/10.3390/w16243556 | PASS (already in JSON) |

---

## 7. Git status at acceptance

| Item | Value |
|---|---|
| Remote | `origin` → https://github.com/Coucou2016/20260810-CE-QUAL-W2.git |
| Branch | `main` |
| Status goal | Follow-up commit pushed with Phase-4 text fixes (see `git log -1` after push) |
| Forbidden actions | No deploy, no production changes, no secrets, no ZIP to ChatGPT |

---

## 8. Bottom line

Public structured workspace is live. Advisor affirms **GMD Methods framing** and core empirical chain, with novelty and VPR/Table-2 wording tightened. Submission still blocked on **persistent Zenodo archive**, not on the scientific spine.
