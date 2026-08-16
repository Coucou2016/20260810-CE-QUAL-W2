# Dual-agent literature-architecture report — 2026-08-16

Cursor = sole executor + independent DOI verifier.  
ChatGPT = external literature/architecture advisor (**web search required**).  
Advisor conclusions not trusted without verification.

---

## 1. Collaboration

| Item | Value |
|---|---|
| **New conversation URL** | https://chatgpt.com/c/6a812957-b108-83ea-b941-617f36744d76 |
| Title | CE-QUAL-W2 评估架构 |
| Isolation | Separate from critical-review chat `https://chatgpt.com/c/6a809d8e-db58-83ea-b9e7-073f76a8e52c` |
| Link log | `notes/chatgpt_briefs/conversation_links.md` (appended) |
| Raw extract | `notes/chatgpt_briefs/_chatgpt_lit_extract.txt` |
| Summarized raw + verification | `notes/chatgpt_briefs/literature_architecture_raw.md` |
| Communication | cursor-ide-browser; **text paste only**; **no attachments**; CONTEXT 1 → CONTEXT 2/END |
| Auth | Logged in (Pro); **网页搜索 ON**; response showed “已搜索 N 个网站”; no CAPTCHA block |
| Local fallback | Parallel WebSearch/WebFetch used for DOI verification regardless |

---

## 2. Baseline

| Item | Value |
|---|---|
| Root | `I:\Projects\20260810-CE-QUAL-W2` |
| Git | **No `.git`** (`fatal: not a git repository`) |
| Branch / HEAD | N/A |
| Progress note | `notes/PROGRESS_20260816.md` |
| Prior dual-agent | `notes/DUAL_AGENT_REPORT_20260816.md` (review rounds) |
| Commit / push | **Forbidden** this task; also impossible without git |

---

## 3. Advisor recommendations (accepted after check)

1. Primary venue/type: **GMD — Methods for assessment of models** (EMS Research Article alternate).  
2. Blend GMD assessment spine with EMS compact protocol packaging.  
3. Contribution templates for VPR / gating / NHR / run-cards with hard-constraint wording.  
4. Organize Results by **methodological finding**, not by reservoir.  
5. Novelty = auditable layer complementary to Almeida; gap informed by Benicio/W5 — not replacement for calibration papers.  
6. Conditional comparability language (not absolute incomparability).

---

## 4. Vetoes / corrections (Cursor)

| Advisor item | Decision | Reason |
|---|---|---|
| Renumber figures to advisor Fig. 3/4 scheme | **Veto** | Keep existing Fig. 1–8 / Tables 1–5 inventory |
| Treat Seuru 2026 ODE as core structural model | **Soft veto** | DOI PASS but ML-focused; format analogy only |
| Treat Lindenschmidt Sci. Data as architecture template | **Soft veto** | DOI PASS but data descriptor, not GMD methods spine |
| Absolute “incomparable” framing | **Already vetoed historically**; advisor now aligns | Keep conditional wording |
| Claim universal NHR timestep law / OOS NSE / physical deletion | **Veto if appeared** | Advisor complied; frameworks restate bans |
| Any DOI failure | **None** | 12/12 resolve |

**GMD type nuance (Cursor add):** “Model evaluation papers” formally expect a prior model-description paper; prefer **Methods for assessment** so we do not fake a new process-module evaluation. Fallback evaluation type must cite Cole & Wells / official docs.

---

## 5. Landed files

| Path | Role |
|---|---|
| `notes/PROGRESS_20260816.md` | Phase-0 progress inventory |
| `drafts/P1_WRITING_FRAMEWORK.md` | English writing framework |
| `drafts/P1_WRITING_FRAMEWORK_zh.md` | Chinese counterpart |
| `notes/chatgpt_briefs/literature_architecture_raw.md` | Advisor digest + verified lit table |
| `notes/chatgpt_briefs/conversation_links.md` | Appended new URL |
| `notes/chatgpt_briefs/_chatgpt_lit_extract.txt` | Full advisor paste |
| `notes/DUAL_AGENT_LITFRAME_20260816.md` | This report |

Not modified: analysis JSON; W2 runs; draft prose numbers (surgical rewrite deferred).

---

## 6. Tests

| Test | Result |
|---|---|
| Conventional unit tests | **N/A** (repo has none for this task) |
| Literature DOI verification (12 advisor items) | **PASS 12/12** |
| Web search used by ChatGPT | **PASS** (UI chip + “已搜索 … 网站”) |
| Attachments uploaded | **PASS** (none) |
| Commit / push | **PASS** (none; no git) |
| Hard-constraint language in frameworks | **PASS** (written explicitly) |

### DOI checklist

| # | Paper | DOI | Result |
|---:|---|---|---|
| 1 | Almeida & Coelho 2025 GMD | 10.5194/gmd-18-6135-2025 | PASS |
| 2 | Jakeman et al. 2006 EMS | 10.1016/j.envsoft.2006.01.004 | PASS |
| 3 | Bennett et al. 2013 EMS | 10.1016/j.envsoft.2012.09.011 | PASS |
| 4 | Planque et al. 2022 Ecol. Model. | 10.1016/j.ecolmodel.2022.110059 | PASS |
| 5 | Seuru et al. 2026 EMS | 10.1016/j.envsoft.2026.106912 | PASS |
| 6 | Legates & McCabe 1999 WRR | 10.1029/1998WR900018 | PASS |
| 7 | Gupta et al. 2009 JoH | 10.1016/j.jhydrol.2009.08.003 | PASS |
| 8 | Knoben et al. 2019 HESS | 10.5194/hess-23-4323-2019 | PASS |
| 9 | Clark et al. 2021 WRR | 10.1029/2020WR029001 | PASS |
| 10 | Benicio et al. 2024 Water | 10.3390/w16243556 | PASS |
| 11 | Stagge et al. 2019 Sci. Data | 10.1038/sdata.2019.30 | PASS |
| 12 | Lindenschmidt et al. 2019 Sci. Data | 10.1038/s41597-019-0316-y | PASS |

---

## 7. Git status

**Local files only; not committed.** Repository root has no `.git`, so no staged/untracked semantics. User must decide whether to initialize VCS separately.
