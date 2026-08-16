# Nature-skills writing constraints (project digest)

**Source:** [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills)  
**Installed:** `C:\Users\Administrator\.cursor\skills\` (also mirrored from `C:\Users\Administrator\.codex\skills\`)  
**Upstream pin:** commit `7316aff80302f105c5703cf8d7dfd0f608a9b411` (2026-08-16)  
**Primary skills for P1:** `nature-writing` v1.2.1, `nature-polishing` v6.3.1, `nature-figure` v2.4.1, `nature-shared` v1.3.1  

This note is a **project-facing digest**, not a replacement for reading `SKILL.md` + routed `static/` fragments at draft time.

---

## 1. What nature-skills is

A folder-based agent skill pack. Each `nature-*` directory is one install unit centred on `SKILL.md`, with `manifest.yaml`, `static/`, `references/`, and shared support in `nature-shared/`. Agents must load fragments from disk (router protocol), not improvise from memory.

**Not** an npm/Python package. Install by copying whole skill folders.

---

## 2. Paper-type choice (do not force Nature Letter)

| Skill axis | Allowed | P1 recommendation |
|---|---|---|
| `paper_type` | research / **methods** / hypothesis / algorithmic / review | **methods** (evaluation protocol + fair comparisons) |
| `journal` | nature / nature-family / nat-comms / nat-mach-intell / **generic** | Keep **GMD** as venue; use **generic** Nature-leaning discipline, or treat **nat-comms** only as a style reference for length/display discipline |
| Article form | Flagship Letter/Article vs Communications Article vs domain journal | **Retain GMD model-evaluation paper.** Do **not** compress into a Nature Letter (would destroy Methods depth). Optional secondary path: Nat. Commun. Article (~5k words incl. Methods) only if a future rewrite consciously accepts that budget |

**Methods argument chain (skill):**  
`task/problem → limits of existing methods → proposed method → evaluation showing advantage → reproducibility → boundary`

**Drafting order (methods):** Methods → Results → Introduction (retrospective) → Conclusion → Discussion → Abstract (last).

---

## 3. Reader path (always)

Readers ask, in order: **Relevance → Novelty → Trust → Reuse → Meaning (boundaries)**.  
Every section should serve a one-sentence argument:

> In [system/problem], we show [advance] using [approach], supported by [evidence], with [boundary].

---

## 4. Structure and section jobs

- **One paragraph, one job** among: context, gap, approach, result, comparison, mechanism, implication, limitation.
- First sentence = topic/claim; later sentences need an explicit relation (cause, comparison, restriction, example).
- Claims stay next to supporting numbers/figures; do not stack claims then dump evidence later.
- **Confirmation gate:** if claim / evidence / boundary is ambiguous, echo argument + assumptions before rewriting a whole section.

---

## 5. Abstract length and pattern

| Target | Abstract rule (skill / journal facts) |
|---|---|
| Nature Communications Article | **≤150 words**, single unstructured paragraph, **no citations**, spell out abbreviations, **lead with finding**, quantitative results preferred |
| Flagship Nature | Stricter significance framing; separate summary-paragraph conventions in `references/nature-summary-paragraph.md` |
| GMD (this project) | No 150-word hard cap; still apply the pattern: `problem → gap → approach → key results → implication → boundary` |

**Diagnostics:** avoid opening with bare `Here, we…`; avoid ending on unbounded promises; keep at least one hard number or comparison.

---

## 6. Figure / display rules (`nature-figure`)

Before plotting or rearranging figures:

1. Write the **one-sentence conclusion** the figure defends.  
2. Map each panel to **one** claim question; merge redundant panels.  
3. Classify archetype; set export/journal contract (size, font ≥5 pt, editable text).  
4. **Data integrity:** do not drop points for aesthetics; exclusions need a stated rule.  
5. Chart serves scientific logic; aesthetics are secondary.

**Nat. Commun. display budget (if ever used):** ≤10 main display items (figures+tables); no Extended Data tier; extras → SI.  
**GMD:** keep enough panels to defend VPR / controller / NHR claims; prefer figure-first narration (Fig. 3 KGE decomposition is the Claim-1 glance test).

---

## 7. Contribution / authorship statements

- Prefer **3–5 falsifiable contribution bullets** (what is shown, under what conditions), not marketing novelty.  
- Submission packages expect **CRediT-style** author contributions when the journal asks.  
- Sweep unsupported novelty words: `first`, `unprecedented`, `comprehensive`, `always`, `never` — replace with bounded claims.

---

## 8. Sentence and claim discipline (`language/en`)

- Aim for **10–30 word** sentences; one proposition per sentence.  
- Prefer SVO; avoid stacked prepositions and em-dash clutter unless requested.  
- Calibrate verbs: `show`/`demonstrate` (strong evidence) vs `suggest`/`indicate` vs `may`/`could`.  
- No invented results, mechanisms, references, sample sizes, or statistics.

---

## 9. References style (when Nature-family)

Nature / Nat. Commun. style (skill facts): superscript numbered citations; author `Last, Initials`; journal ISO abbreviations; volume bold; year in parentheses; DOIs encouraged. Cap ~60 refs for Nat. Commun. Articles.

**This project’s P1 stays on GMD / Copernicus citation style** (author–year) unless the venue changes. Absorb Nature **discipline**, not the citation syntax.

---

## 10. Project hard constraints (override stylistic compression)

These remain non-negotiable even when applying nature-skills:

| Constraint | Rule |
|---|---|
| Conditional comparability | Skill is comparable only under stated VPR + controller state + NHR |
| Internal consistency | DeGray T / Columbia DO metrics are **not** skill vs observations |
| Gate files | Controller-gated series exist only when the controller is on |
| NHR | Exit 0 / “Normal termination” ≠ numerical health |
| No OOS NSE | Out-of-sample NSE was **not** computed; do not imply otherwise |
| Numbers | Analysis **JSON** is authoritative; notes/plan labels yield to JSON |

---

## 11. Skills to invoke for later work

| Task | Skill |
|---|---|
| Rebuild section argument / outline | `nature-writing` |
| Sentence-level English polish | `nature-polishing` |
| Figure QA / redraw | `nature-figure` |
| Stats wording audit | `nature-statistics` |
| Data/code availability text | `nature-data` |
| Pre-submission mock review | `nature-reviewer` |
| Revision letters (post-decision) | `nature-response` (not now) |
