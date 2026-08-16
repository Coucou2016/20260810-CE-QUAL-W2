# ITER2 — Five ChatGPT rounds final (2026-08-17)

Cursor × ChatGPT second maturation series for `P1_GMD_draft_v2.md` (≥5 advisor rounds).  
Public repo: https://github.com/Coucou2016/20260810-CE-QUAL-W2

## Collaboration links

| Round | Theme | ChatGPT URL | Brief | After-round HEAD |
|---|---|---|---|---|
| 2-01 | Paper de-processization | https://chatgpt.com/c/6a81f023-6e24-83ea-b398-fcfacbff3192 | `06_PAPER/notes/chatgpt_briefs/round2_01_brief.md` | `913986f` |
| 2-02 | GMD Methods voice | same | `round2_02_brief.md` | `55b0637` |
| 2-03 | Evidence authenticity | same (combined) | `round2_03_brief.md` | 1105455 |
| 2-04 | Captions academicization | same (combined) | `round2_04_brief.md` | 1105455 |
| 2-05 | Submission completeness | same (combined) | `round2_05_brief.md` | 1105455 |

Raw replies: `round2_01_raw.md`, `round2_02_raw.md`, `round2_03_04_05_raw.md`.  
Per-round notes: `06_PAPER/notes/ITER_ROUNDS/round2_0{1..5}.md`.

## Veto log (material)

- Inventing Zenodo DOI / `10.5281/zenodo.XXXXXX` placeholders as if real.
- Changing locked Results numbers or Fig. 4/6 science.
- Treating DeGray/Columbia as observational skill.
- Claiming TDGTA OFF deletes physical TDG.
- Generalizing Long Lake 5/4/1/5 as a timestep-stability law.
- Computing or implying OOS NSE for 2016–2025.
- Upgrading W5 `unknown` to confirmed absence.
- Using Almeida Zenodo DOI as this manuscript’s archive DOI.

## Landed summary

1. **De-processized** submission draft: removed Cursor/ChatGPT banners, Working Chinese title, unresolved-discrepancy QC list, rebuttal-letter Discussion, figure-file Appendix, tutorial Code-availability voice; repository-relative paths only in Code availability.
2. **GMD Methods voice:** Abstract + Contributions + Methods §3.1–3.2 cadence aligned with assessment-protocol tone (Almeida/GMD).
3. **Evidence:** full claim–number checklist PASS; audit script **PASS=40 FAIL=0**.
4. **Captions:** self-contained with *n* and evidence class; no `File:`/`(exists)` science narration.
5. **Submission:** Conclusions anchors retained; Code availability = GitHub + Zenodo **待补充**; `P1_paper.html` regenerated; `report.md` keeps process / paper stripped.

## Number audit

- Script: `06_PAPER/notes/_audit_p1_numbers_20260816.py`
- Final gate this series: **PASS=40 FAIL=0**
- JSON authority unchanged: `w3`, `w1`, `w4`, `w5`, `nhr_dlt_scan`, `w7`, `pairing_tolerance_scan`

## Still for the user (not inventable)

1. **Mint Zenodo** and replace **待补充** with the real DOI.
2. **Author / CRediT / affiliations / funding / corresponding author.**
3. **Redistribution / reviewer access** for CE-QUAL-W2 executable, full example trees, and any non-public large runs.
4. Optional: extend TMEND + meteorology for a future OOS NSE paper (explicitly out of scope here).

## Primary deliverable

Matured manuscript: `06_PAPER/drafts/P1_GMD_draft_v2.md` (single mainline; no v3 split).  
Local HTML: `06_PAPER/drafts/P1_paper.html` (rebuild via `06_PAPER/analysis/build_paper_html.py`).

## Final HEAD SHA

1105455
