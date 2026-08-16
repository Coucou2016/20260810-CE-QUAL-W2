# ITER 5 ROUNDS FINAL ? 20260816

Cursor x ChatGPT maturation of `P1_GMD_draft_v2.md` (>=5 independent advisor rounds).  
Public repo: https://github.com/Coucou2016/20260810-CE-QUAL-W2

## Collaboration links

| Round | Theme | ChatGPT URL | Git SHA after round |
|---|---|---|---|
| 0 baseline | ? | ? | start `8bc423b` (see `ITER_ROUNDS/round_00.md`) |
| 1 | A contribution / prior-art | https://chatgpt.com/c/6a819bd6-4aac-83ea-9af9-572d08d5495f | `8a01424` |
| 2 | B number consistency | https://chatgpt.com/c/6a819d49-3cd8-83ea-b3c8-289ba7dcf436 | `c036526` |
| 3 | B figures / NHR | same Theme B chat | `e5cab85` |
| 4 | B pairing Methods/SI | same Theme B chat | `6821379` |
| 5 | A submission readiness | Theme A chat (ROUND 5/5) | `b847302` (content); tip after notes `058a541+` |

## Per-round adopt / veto / land

### Round 1 ? contribution boundary
- **Adopt:** soften invent/propose to operationalize W2-specific VPR/NHR/evaluation-object contract; matrix C1d = VPR-core; KEEP GMD Methods.
- **Veto:** advisor "main vs master drift" (only `main`); fake provenance invention.
- **Land:** wording in Abstract/Intro/Contributions.

### Round 2 ? numbers
- **Adopt:** Table 2 VPR-core + self-contained **1/7/4**; Conclusions exact A/B/C + `15.55% (251/1614)`.
- **Veto:** none material (advisor overall PASS).
- **Audit:** PASS 40/40.

### Round 3 ? figures
- **Adopt:** Fig.4 **2+1** panels (skill / internal / literature R2 strip); Fig.6 schedule-knot axis + caption; Fig.4 from W3 JSON.
- **Veto:** fabricating NSE for literature rug.
- **Land:** plot scripts + PNG regen + captions.
- **Audit:** PASS 40/40.

### Round 4 ? pairing tolerance
- **Adopt:** Sect. 3.3 scan paragraph; bounded sign-stability sentence; Appendix B table; Table 1 footnote; no Table 1 number change.
- **Veto:** "robust/invariant to pairing," "correct tolerance."
- **Land:** `pairing_tolerance_scan.py/.json`; Methods + Appendix B.
- **Audit:** PASS 40/40.

### Round 5 ? submission readiness
- **Adopt:** keep Abstract anchors (VPR-core + 1/7/4); KEEP Methods article type; DOI list PASS; Zenodo stays ??? with user steps.
- **Veto:** Abstract shortening that drops VPR-core or 1/7/4; inventing Zenodo DOI.
- **Land:** Conclusions 1/7/4 + pairing pointer; Code and data mint steps; matrix C1e + Fig.4 panel map; local `P1_paper.html` regen.
- **Audit:** PASS 40/40.

## Number-audit authority

Script: `06_PAPER/notes/_audit_p1_numbers_20260816.py`  
Final gate this pass: **PASS=40 FAIL=0**.  
JSON truth: `w3_tdgta_off_metrics.json`, `w4_cciw_vs_dart.json`, `w5_lit_audit_summary.json` (1/7/4), `nhr_dlt_scan.json` (ON 5/4/1/5), `w1_provenance_metrics.json`, `w7_columbia_sod_vs_almeida.json`, `pairing_tolerance_scan.json`.

## Still blocked (human / policy ? not inventable)

1. **Zenodo DOI ???** ? mint release archive; replace placeholder; GitHub alone is not a GMD persistent archive.
2. **Redistribution / reviewer access** for CE-QUAL-W2 executable / full example / large run trees not in public snapshot.
3. **Author stubs** ? CRediT, affiliations, funding, corresponding author.
4. No OOS NSE (by design); no multi-hour Bonneville OOS rerun required for this maturity pass.

## Deliverables

- Matured draft: `06_PAPER/drafts/P1_GMD_draft_v2.md` (kept as v2; no v3 split needed)
- Figures updated in Rounds 3-4 (Fig.4 split; Fig.6 NHR labels)
- Claim matrix: `06_PAPER/drafts/P1_claim_evidence_matrix.md`
- Local HTML: `06_PAPER/drafts/P1_paper.html` (gitignored; rebuild via `06_PAPER/analysis/build_paper_html.py`)
- Round notes: `06_PAPER/notes/ITER_ROUNDS/round_0{0..5}.md`
