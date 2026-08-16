# Round 04/5 — Pairing-tolerance Methods/SI (Theme B)

**Date:** 2026-08-16  
**ChatGPT:** https://chatgpt.com/c/6a819d49-3cd8-83ea-b3c8-289ba7dcf436 (ROUND 4/5)  
**Repo base:** `e5cab85`

## Advisor (verified vs JSON)

- Place scan paragraph in §3.3 after “Changing the tolerance is a different evaluation.”
- Use bounded sign-stability sentence (not “robust/invariant”).
- Optional SI table with baseline marked; each row = distinct VPR object.
- Table 1 numbers unchanged; optional baseline-tol footnote.
- **VETO adopted:** no “robust to pairing tolerance” wording.

## Landed

- Regenerated `pairing_tolerance_scan.py` / `.json` from archived CCIW + ON (no W2).
- §3.3 Methods paragraph + Appendix B full scan table.
- Table 1 caption: baseline tolerances + Appendix B pointer.
- Code & data lists include pairing JSON/script.

## Audit

PASS 40/40 (`_audit_p1_numbers_20260816.py`)

## Git

- SHA: *(filled after push)*
