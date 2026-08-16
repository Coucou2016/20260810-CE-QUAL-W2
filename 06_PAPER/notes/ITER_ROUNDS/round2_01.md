# ITER ROUND 2-01 — Paper de-processization

**Date:** 2026-08-17  
**ChatGPT:** https://chatgpt.com/c/6a81f023-6e24-83ea-b398-fcfacbff3192  
**Brief:** `06_PAPER/notes/chatgpt_briefs/round2_01_brief.md`  
**Raw:** `06_PAPER/notes/chatgpt_briefs/round2_01_raw.md`

## Adopt

- Delete Working Chinese title, Cursor×ChatGPT draft-status banner, Unresolved-discrepancies QC list from submission-facing draft.
- Strip Methods script-path narration (`parse_nhr.py`, `w2eval.py` path stacks); keep scientific semantics.
- Rewrite Sect. 4 run-directory narrative as configuration/state language.
- Remove figure caption `File: … (exists)` inventory tails; delete Appendix A figure-file map; rename pairing appendix → Appendix A.
- Convert Sect. 6.2/6.3 rebuttal/process voice → Scope and interpretation limits; drop plan T3/T4/T6 IDs.
- Rewrite Code availability (GitHub + Zenodo **待补充**; no “user steps” tutorial).
- Report note: process stays in `report.md`; paper stripped.

## Veto

- Inventing Zenodo DOI / changing locked numbers / reopening Fig. 4–6 science.
- Absolute `I:\` paths were already absent from the draft (advisor negative finding confirmed).

## Landed

- `06_PAPER/drafts/P1_GMD_draft_v2.md` de-processized.
- `06_PAPER/report/report.md` one-line paper≠report note.
- Number audit: **PASS=40 FAIL=0**.

## HEAD after this round

`913986f`
