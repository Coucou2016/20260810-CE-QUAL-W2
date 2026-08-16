# Round 02/5 — Table/result number consistency

**Date:** 2026-08-16  
**ChatGPT:** https://chatgpt.com/c/6a819d49-3cd8-83ea-b3c8-289ba7dcf436 (Theme B isolated NEW chat)  
**Mode:** web search ON; no attachments; GitHub + commit `8a01424`  
**Prior Theme A chat:** https://chatgpt.com/c/6a819bd6-4aac-83ea-9af9-572d08d5495f

## Advisor summary

- Overall **PASS** vs locked JSON; no 1/11, 8/12, fake OOS, fake Zenodo.
- Soft issues only: Table 2 / Conclusions “VPR” vs **VPR-core**; Table 2 not self-contained on 1/7/4; Abstract DART needs `w4` HTML comment; Conclusions spell-out 15.55%.

## Cursor verify

All five minimal fixes **adopted** after local grep + prior PASS audit. No veto of numerical claims.

## Landed

- Table 2 caption + row: VPR-core; 1/7/4 object coding
- Abstract: `<!-- w4_cciw_vs_dart.json -->` on DART sentence
- Conclusions: exact A/B/C decimals; VPR-core 2/38 + file/column 0/38; `15.55% (251/1614)`

## Audit

**PASS 40/40**

## Git

(filled after push)
