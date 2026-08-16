# Local pre-submission checklist — 2026-08-16

**Source:** advisor ≤7 items in `chatgpt_briefs/gmd_blueprint_confirm_raw.md` + judgment `GMD_BLUEPRINT_CONFIRM_20260816.md`.  
**Scope:** items completable locally. **No Zenodo mint. No OOS long run. No git commit.**

---

## Checklist

| # | Advisor item | Local status | Notes |
|---|---|---|---|
| 1 | Title / GMD Methods + version scope | **DONE (local)** | EN/ZH titles on `P1_GMD_draft_v2.md` now carry **v4.5.5 primary + v5.0 beta inventory**. Cover-letter manuscript-type sentence: **queued stub below** (full cover letter not drafted). |
| 2 | Claim–evidence matrix freeze | **DONE** | `drafts/P1_claim_evidence_matrix.md` — claims ↔ class ↔ tables/figs ↔ JSON; hard exclusions listed. |
| 3 | W5 coding transparency (full text 9/38; present/absent/unknown) | **DONE** | §3.8 strengthened: full text **9/38**; three-way coding; `unknown` never → confirmed absence. |
| 4 | Reproducibility package file list | **DONE (prep only)** | `zenodo/FILE_MANIFEST.md` + `README_ARCHIVE.md` updated for v2 / matrix / audit notes; core paths verified present; `checksums.sha256` regenerated. **Deposit/DOI not minted.** |
| 5 | Headline numbers vs JSON | **DONE** | `_audit_p1_numbers_20260816.py` retargeted to **v2**; **PASS 40/40** → `notes/P1_number_audit_20260816.md`. No W2 rerun. |
| 6 | Figure caption evidence boundaries | **DONE** | Figs 1–4, 6–7, D1–D3, C1–C2 captions mark skill vs internal consistency vs NHR vs evaluation-record / downstream metrics. |
| 7 | Claim-language audit | **DONE** | `confounder`/`confounding`/`not comparable`/`incomparable` = 0. Remaining `mandatory` / `deleted` / `first reproducible validation` only in **negation / refusal** contexts. Abstract “must be interpreted” → **should**. §5.2 / Conclusions headings de-“confounding”. |

---

## Score

- **Completed locally: 7 / 7 checklist rows** (item 1 cover letter = stub only; title/version done).
- **Still blocked on user account / action:**
  1. **Mint Zenodo DOI** and paste into §8 Data availability (do not invent).
  2. Optional polish: full **cover letter** with “Methods for assessment of models” rationale + Cole & Wells / Almeida precedent citation.
  3. Explicitly deferred: **OOS NSE** (`P2_oos_roadmap.md`); Discussion “Scope and limitations” heading rename (soft-adopt).

---

## Cover-letter stub (item 1 remainder)

> We submit this manuscript as a GMD **Methods for assessment of models** paper. The object of inference is an evaluation workflow (variable provenance, control-state documentation, numerical-health context, and run-cards), demonstrated on official CE-QUAL-W2 **v4.5.5** examples with a **v5.0 beta** example inventory, not a new process algorithm or a multi-site calibration campaign. Closest named-model GMD precedent for open CE-QUAL-W2 evaluation remains Almeida and Coelho (2025); we complement that process-option evaluation layer with an auditable assessment record under reported goodness-of-fit statistics.

---

## Files touched this pass

| File | Change |
|---|---|
| `drafts/P1_GMD_draft_v2.md` | Title/version; W5 §3.8; captions; language softens |
| `drafts/P1_claim_evidence_matrix.md` | **New** claim–evidence freeze |
| `notes/_audit_p1_numbers_20260816.py` | Audit target → v2 |
| `notes/P1_number_audit_20260816.md` | Regenerated PASS 40/40 |
| `zenodo/FILE_MANIFEST.md` | v2 / matrix / pre-sub notes |
| `zenodo/README_ARCHIVE.md` | Point to v2; metadata title |
| `zenodo/checksums.sha256` | Regenerated include hashes |
| `notes/PRESUBMISSION_LOCAL_20260816.md` | This checklist |

**No commit. No Zenodo upload.**
