# Round 01/5 — Contribution & prior-art boundary

**Date:** 2026-08-16  
**ChatGPT:** https://chatgpt.com/c/6a819bd6-4aac-83ea-9af9-572d08d5495f (title: GMD Methods Paper Review)  
**Mode:** NEW chat; web search ON; no attachments; GitHub URL given  
**Theme A:** contribution sentences & prior-art boundary

## Advisor summary (verified)

- KEEP GMD **Methods for assessment of models** (Cursor WebSearch confirmed manuscript-types page).
- Soften C1 “introduce VPR”, C2 “identify…”, C3/Abstract “propose…”, C4 framing → operationalize W2-specific evaluation-object contract.
- Matrix: “reconstructable VPR 2/38” → **VPR-core**; keep `vpr_variable=0/38` separate.
- Almeida = Model evaluation (process options) vs our Methods assessment layer.

## Cursor verify / veto

| Item | Verdict |
|---|---|
| Soften introduce/propose/identify | **Adopt** — phrases present in local draft |
| Matrix VPR-core wording | **Adopt** |
| KEEP Methods article type | **Adopt** (GMD page + Almeida contrast) |
| “main vs master drift” / Minimal edit 1 source quote of full-8-field in Abstract | **Veto** — only `main` exists; Abstract already used VPR-core; quoted full-8-field 2/38 sentence not in current Abstract |
| Invent Zenodo / OOS / deleted physics | Not suggested |

## Landed

- `P1_GMD_draft_v2.md`: Abstract + C1–C4 + Discussion 2/38 → VPR-core
- `P1_claim_evidence_matrix.md`: C1d VPR-core
- `P1_MERGED_BLUEPRINT.md`: C1–C4 mirror

## Audit

`_audit_p1_numbers_20260816.py` → **PASS 40/40**

## Git

- SHA: `8a0142410af58bb4cb4ea61daecab67c480578f9` (short `8a01424`)
- Push: yes → origin/main
