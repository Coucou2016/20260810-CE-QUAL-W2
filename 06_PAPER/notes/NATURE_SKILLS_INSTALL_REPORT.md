# Nature-skills install & apply report (P1)

**Date:** 2026-08-16  
**Project:** `I:\Projects\20260810-CE-QUAL-W2`  
**Git:** no commit/push performed (per request)

---

## 1. Discovery

| Location | Result |
|---|---|
| `C:\Users\Administrator\.codex\skills\` | **Already present:** full `nature-*` set + `nature-shared` |
| `C:\Users\Administrator\.cursor\skills-cursor\` | No nature packs |
| `C:\Users\Administrator\.cursor\skills\` | **Was missing** → installed this session |
| `C:\Users\Administrator\.agents\skills\` | Path does not exist |
| Web | Official/common pack: [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) |

---

## 2. Install actions

1. Copied all `nature-*` directories from `~\.codex\skills\` → `~\.cursor\skills\` (whole folders, not `SKILL.md` alone).  
2. Cloned upstream for provenance:  
   `git clone --depth 1 https://github.com/Yuan1z0825/nature-skills.git`  
   → `C:\Users\Administrator\.cursor\skills\_nature-skills-src`  
3. **Upstream pin:** commit `7316aff80302f105c5703cf8d7dfd0f608a9b411` (2026-08-16, `chore: update star history`).  
4. Verified `nature-writing\SKILL.md` and `nature-shared` present under Cursor path.

### Installed skill versions (manifest)

| Skill | Version |
|---|---|
| nature-writing | 1.2.1 |
| nature-polishing | 6.3.1 |
| nature-figure | 2.4.1 |
| nature-shared | 1.3.1 |
| nature-reviewer | 1.4.0 |
| nature-response | 1.6.0 |
| nature-statistics | 1.3.0 |
| nature-data | 2.2.0 |
| nature-citation | 2.1.0 |
| nature-academic-search | 2.0.0 |
| nature-reader | 2.1.0 |
| nature-paper-card | 1.2.0 |
| nature-paper2ppt | 2.0.0 |
| nature-proposal-writer | 1.1.1 |
| nature-literature-pipeline | 1.0.1 |
| nature-ref-verifier | 1.0.1 |
| nature-downloader | 2.1.0 |
| nature-experiment-log | 1.0.2 |
| nature-paper-to-patent | 1.0.0 |

**Cursor install root:** `C:\Users\Administrator\.cursor\skills\`  
**Codex mirror (pre-existing):** `C:\Users\Administrator\.codex\skills\`

---

## 3. Skill原文要点 (read & used)

From `nature-writing` / `nature-polishing` / `nature-figure` / `nature-shared`:

- Router loads `manifest.yaml` + `always_load` fragments; do not draft from memory.  
- Axes: paper_type (methods for P1), journal (generic while venue = GMD), section, language.  
- Stance: no invented evidence; argument before sentences; bounded claims; verb calibration.  
- Workflow: one-sentence argument → terminology ledger → one job per paragraph → confirmation gate → evidence-outward draft.  
- Methods papers: Methods/Results first; fair baselines; reproducibility; failure modes.  
- Abstracts: mini-paper; Nat. Commun. ≤150 words, finding-led; GMD keeps length but same logic.  
- Figures: conclusion → evidence chain → archetype → export contract; data-integrity gate.  
- Reader path: Relevance → Novelty → Trust → Reuse → Meaning/boundaries.  
- Sentence rule: ~10–30 words; one proposition; Nature reference style only if venue is Nature-family.

---

## 4. Applicability to P1

| Question | Answer |
|---|---|
| Applicable? | **Yes**, as writing discipline |
| Convert to Nature Letter? | **No** — would destroy Methods depth |
| Best skill paper_type | **methods** (evaluation protocol) |
| Best venue for this draft | **GMD** (Almeida & Coelho precedent) |
| Optional future venue | Nat. Commun. Article only with conscious word/display budget + SI Methods |
| Hard project constraints | Compatible: skills forbid invention; P1 already encodes conditionality, NHR, no OOS NSE, JSON authority |

---

## 5. Artifacts written / edited

| Path | Role |
|---|---|
| `06_PAPER/drafts/NATURE_SKILLS_GUIDE.md` | Constraint digest |
| `06_PAPER/drafts/P1_NATURE_ALIGNED_OUTLINE.md` | GMD vs Nature table + outline (`P1_WRITING_FRAMEWORK.md` absent) |
| `06_PAPER/notes/NATURE_SKILLS_APPLY_PLAN.md` | Diff intent; Round-2 deferred |
| `06_PAPER/notes/NATURE_SKILLS_INSTALL_REPORT.md` | This report |
| `06_PAPER/drafts/P1_GMD_draft_v1.md` | Round-1 minimal edits (Abstract lead, contribution bullets, CRediT stub) |

---

## 6. Acceptance checklist

- [x] Skills landed under Cursor skills path  
- [x] Source URL + commit/version recorded  
- [x] Guide + outline + apply plan + install report  
- [x] P1 applicability concluded without forcing Nature Letter  
- [x] No git commit / push  
