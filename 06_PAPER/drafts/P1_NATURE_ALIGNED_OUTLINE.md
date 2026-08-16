# P1 nature-aligned outline (GMD venue + nature-skills discipline)

`P1_WRITING_FRAMEWORK.md` was **not** present in the tree at apply time; this file is the independent alignment outline.

**Detected axes (nature-writing):** `task=manuscript`, `paper_type=methods`, `journal=generic` (venue remains GMD), `language=en`.

**One-sentence argument:**  
In CE-QUAL-W2 evaluation practice, we show that published goodness-of-fit is not a portable skill quantity unless variable provenance, controller state, and numerical health are reported, using official example reproductions and a 38-paper audit, with the boundary that DeGray/Columbia channel comparisons are internal consistency and that out-of-sample NSE was not computed.

---

## Venue decision

| Option | Fit | Decision |
|---|---|---|
| Nature Letter | Too short; Methods depth destroyed | **Reject** |
| Nat. Commun. Article (~5k incl. Methods) | Possible future condensation | Hold; would require SI for source-level Methods |
| **GMD model evaluation** | Matches Almeida & Coelho precedent; keeps protocol depth | **Keep as primary** |

Absorb nature-skills: short sentences, falsifiable claims, figure-first Results, explicit boundaries — **without** Nature Letter compression.

---

## GMD vs Nature-family (working contrast)

| Dimension | Current GMD draft | Nature / Nat. Commun. style | P1 action |
|---|---|---|---|
| Opening | Problem → audit → three reasons | Finding-led abstract (≤150 w for Nat. Commun.) | Keep GMD length; tighten lead sentence |
| Methods depth | In-line source paths, pairing rules, counting rules | Flagship: Methods often after refs; Nat. Commun.: Methods in word budget | **Preserve** in-line Methods for GMD |
| Claims | Four numbered claims in Intro | 3–5 contribution bullets, bounded verbs | Keep four claims; rephrase as contribution bullets |
| Figures | Many companions allowed | Strict display caps (6 / 10) | Keep inventory; narrate Fig. 3 first for Claim 1 |
| Citations | Copernicus author–year | Numbered Nature style | Stay Copernicus |
| Availability | Path list + future Zenodo | Mandatory Data/Code Availability + DOIs | Keep stub; mint DOI before submission |
| Novelty tone | Already cautious | Ban unsupported “first/comprehensive” | Maintain; audit wording |

---

## Recommended section map (reader questions)

| Section | Reader Q | Paragraph jobs (nature-skills) |
|---|---|---|
| Abstract | Relevance + Novelty | problem → gap → approach → quantified results → protocol implication → boundary (no OOS NSE; internal consistency labeled) |
| §1 Intro | Relevance → Novelty | context W2 skill tables → gap (VPR/controller/NHR absent) → contribution bullets → roadmap |
| §2 Model & cases | Trust | output architecture → H1 rollback → cases with observation vs internal-consistency labels |
| §3 Protocol | Reuse | VPR → controller-conditional → NHR → metrics (*R*² invariance) → w2eval → W5/W4 methods |
| §4 Results | Trust | Claim1 (Bonneville + DeGray/Columbia) → Claim2 → Claim3 → Claim4; each block ends at a figure/table |
| §5 Discussion | Meaning | *R*² theory → referee objections → what reviews can/cannot claim |
| §6 Conclusions | Meaning + boundary | protocol triad; hard negatives (no OOS NSE; no “controller deletes physics”) |
| Availability | Reuse | JSON authority; run-cards; scripts; example paths |

---

## Contribution bullets (Nature-leaning wording; evidence-locked)

1. **Show** that three defensible Bonneville TDG calibers share *R*² ≈ 0.51–0.55 while NSE spans −2.80 to +0.50 on the same CCIW pairs (*n* = 1614; JSON `w3_tdgta_off_metrics.json`).  
2. **Show** that the skill-best gated series lives only in `TDGTarget_output.csv` under `TDGTA=ON`; OFF removes the file, not the physical TDG variable (SYSTDG snapshot bit-identical ON/OFF).  
3. **Demonstrate** *R*²-blind α/β failure for DeGray temperature and Columbia DO as **internal consistency**, not field skill.  
4. **Show** Long Lake H1 < 0 rollback counts under official `DLTINTER=ON` vs zero under `OFF` at the day-30 DLTMAX knots (`nhr_dlt_scan.json`), motivating NHR alongside exit status.  
5. **Propose** VPR + controller-conditional evaluation + NHR, implemented as `w2eval` run-cards from cached JSON (no model rerun).

---

## Hard-constraint checklist (must survive any polish)

- [ ] Conditional comparability stated wherever skill is compared  
- [ ] Internal-consistency labels on DeGray / Columbia  
- [ ] Gate-file existence tied to controller ON  
- [ ] NHR ≠ exit 0  
- [ ] Explicit “OOS NSE not computed”  
- [ ] All headline numbers match analysis JSON  

---

## Next drafting passes (not done here)

1. Abstract: finding-led first sentence (done in v1 minimal edit if applied).  
2. Intro: replace claim block with contribution bullets (minimal edit).  
3. Results: ensure each claim opens with the glance figure before table prose.  
4. Full `nature-polishing` pass only after numbers freeze and Zenodo plan exists.
