# ROUND 2-01 raw — ChatGPT advisor reply

**Conversation:** https://chatgpt.com/c/6a81f023-6e24-83ea-b398-fcfacbff3192  
**Mode:** web search ON; GitHub read (no attachments)  
**Date:** 2026-08-17

## Advisor reply (extracted)

Web search ran. I read the Round 2-01 brief, the current manuscript, report.md, the claim–evidence matrix, and the five-round maturity notes, and checked current GMD “Methods for assessment of models”, submission/code-data policy, Almeida & Coelho (2025), Bennett et al. (2013), and Gupta et al. (2009). The brief’s requested boundary is correct: this round should remove workflow scaffolding without reopening the frozen science.

### 1. Hit list — process/tooling/local-path/collaboration residues

| Hit | Current residue | Line-theme | Action |
|---|---|---|---|
| H1 | P1 working draft... Blueprint... | Hidden front-matter comment | MOVE to notes or retain only if stripped from rendered submission |
| H2 | Working Chinese title | Internal bilingual working title | DELETE from submitted manuscript |
| H3 | Target journal..., Version scope (title-locked) | Submission/workflow metadata | DELETE labels; retain scientific version-scope in Methods |
| H4 | Draft status: Cursor×ChatGPT advisor rounds... | Collaboration/iteration log | DELETE entirely from paper |
| H5 | Unresolved discrepancies (8 items) | Internal QC checklist | MOVE wholesale to notes |
| H6 | (W5)/(W4) in Methods headings | Internal work-package labels | Remove labels |
| H7 | parse_nhr.py / w2eval path stacks in Methods | Script-stack-as-science | Keep semantics; paths to Code availability |
| H8 | 05_REPRO_RUNS/... local run-directory names | Local workspace narrative | Replace with run states |
| H9 | File: ../figures/... (exists) in captions | Build/inventory residue | DELETE filenames/status from captions |
| H10 | We therefore write three sentences... | Frozen-writing instruction | DELETE instruction; keep propositions |
| H11 | inspected in this project / Verified run defect | Lab-notebook voice | Rewrite as audit scope |
| H12 | Project notes further record... LFS... | Strong local residue | DELETE; concise executable statement |
| H13 | user-specified Portuguese-reservoir experiment | Process residue | Cite Almeida published scan range |
| H14 | Likely referee objections / rebuttal voice | Rebuttal-letter voice | Convert to Scope and interpretation limits |
| H15 | Downgraded and refused claims / plan T3 T4 | Claim-negotiation log | Remove process; keep limitations |
| H16 | plan T6 | Internal task ID | Keep future-work; delete T6 |
| H17 | User steps to mint Zenodo / local project root | Author tutorial | Rewrite Code availability |
| H18 | Appendix A Figure file map / SciencePlots redraw | Internal inventory | DELETE from article |
| H19 | Author contributions (stub...) | Placeholders | Keep stub content; remove word "stub" if possible; names remain 待补充 |

Negative finding: no `I:/Projects/...` absolute Windows path in the manuscript (those remain in report.md).

### 2–6. Rewrite guidance

See conversation; Cursor adopts H2–H18 rewrites below in `P1_GMD_draft_v2.md`. Numbers untouched. Appendix B becomes Appendix A after removing figure file map.

### Cursor verification notes

- Confirmed no `I:\` in draft (grep).
- Number audit baseline before land: PASS=40 FAIL=0.
- Veto: none material; do not invent Zenodo DOI; do not change 1/7/4 or hard constraints.
