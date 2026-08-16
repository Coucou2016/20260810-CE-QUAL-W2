# P1 Writing Framework (English)

**Status:** Executable architecture for drafting / revising `P1_GMD_draft_v1.md`.  
**Date:** 2026-08-16  
**Advisor chat (web search):** https://chatgpt.com/c/6a812957-b108-83ea-b941-617f36744d76  
**Numbers:** still bind to `06_PAPER/analysis/*.json` — this file is structure only.

---

## Hard constraints (must appear in Methods / Discussion / captions)

1. **Conditional comparability** of goodness-of-fit across studies — not absolute “never comparable.”
2. **Internal consistency ≠ observational skill** (DeGray T, Columbia DO: no independent observations).
3. **Do not write that a physical quantity was deleted.** TDGTA=OFF removes gated file `TDGTarget_output.csv`; SYSTDG `TDG_output.csv` remains as pre-control snapshot.
4. **NHR should be reported with skill**; it is **not** a universal timestep law. H1<0 evidence is principally Long Lake.
5. **No out-of-sample NSE** in P1. 2016–2025 exceedance frequencies are descriptive, not forecast skill.
6. Columbia **SOD = transplanted parameters** (magnitude check only), not field calibration.
7. W5: full text **9/38**; `unknown` ≠ confirmed absent.

---

## 1. Journal and article type

| Rank | Venue | Article type | When |
|---:|---|---|---|
| **1** | *Geoscientific Model Development* (GMD) | **Methods for assessment of models** | Primary: object of inference is the evaluation workflow (VPR + control-state provenance + NHR + run-cards) |
| 2 | *Environmental Modelling & Software* | Research Article | If `w2eval` is framed as the protocol/tool deliverable |
| 3 | GMD | Model evaluation paper | Fallback if editors require evaluation type; then cite official W2 description (Cole & Wells / release docs) and keep demos as assessment of *evaluation practice*, not process skill |
| — | Water / JoH / WR | Application / physical | **Not P1** — reserve for P2 (OOS / process) |

**Working title pattern (non-overclaiming):**  
*Provenance- and numerical-health-aware evaluation of CE-QUAL-W2 simulations: variable provenance records, control-state outputs, and run-cards*

Avoid in title: standard / universal / mandatory / validation standard.

**Precedent:** Almeida & Coelho (2025) is the closest *CE-QUAL-W2 + GMD* case template, but that paper’s type is **model evaluation** of diagenesis formulations. Ours is complementary: an auditable layer *under* such performance statistics.

---

## 2. Architecture choice (imitate 2–3 spines)

| Architecture | Narrative spine | Fit | Imitate | Danger |
|---|---|---|---|---|
| **A. Classic IMRaD application** | Site → setup → calibrate → results | Low–moderate | Case discipline only | Novelty looks like “audit of several reservoirs” |
| **B. GMD assessment / evaluation** | Assessment problem → evidence taxonomy → method → controlled demos → implications → code/data | **Primary** | Versioning, assessment object, full processing provenance | Over-specificity to W2 |
| **C. EMS protocol / tool** | Practice gap → requirements → named protocol → implementation → demos → limits | **Secondary (blend)** | Compact named elements + checklist | Claiming a general “standard” from one model family |

**Chosen blend:** GMD Methods spine + EMS compact protocol packaging  
`Evaluation record = VPR + control-state provenance + NHR + run-card`  
(R²/NSE/KGE remain **downstream statistics**, not a fourth pillar.)

---

## 3. Contribution sentence templates (use as-is or lightly adapt)

### C1 — Variable provenance (VPR)
> We show that goodness-of-fit statistics can depend materially on the provenance of the evaluated output variable, and introduce a **variable provenance record (VPR)** that makes the model quantity, extraction route, processing state, and evaluation target explicit.

Bonneville clause:  
> In the Bonneville TDG demonstration, alternative output channels retain similar correlation structure while yielding materially different NSE values, illustrating why variable provenance should be reported together with goodness-of-fit statistics.

**Do not write:** “R² is misleading and NSE reveals true skill.”  
**Write:** “R² and NSE describe different properties; neither resolves ambiguity in *which* model quantity entered the metric.”

### C2 — Control-rule confounding / gated outputs
> We identify **control-state dependence** as an evaluation confounder when diagnostic or controller-specific outputs are conditionally available, and incorporate control-state provenance into the evaluation record.

Operational clause:  
> When TDGTA is OFF, the controller-specific `TDGTarget_output.csv` is absent, whereas the SYSTDG `TDG_output.csv` remains available as a **pre-control snapshot**; the framework therefore treats output availability and meaning as functions of run configuration.

**Forbidden:** “physical quantity deleted / TDG removed.”

### C3 — Numerical health record (NHR)
> We propose that statistical performance be accompanied by a **numerical health record (NHR)** documenting execution diagnostics relevant to interpretation of reported skill.

Bound immediately:  
> The NHR is a **reporting recommendation**, not a universal timestep-stability criterion; in the present examples, the clearest H1<0 evidence is concentrated in the Long Lake case.

### C4 — Reproducibility / run-cards
> We implement these reporting elements in reproducible **run-cards** and use official CE-QUAL-W2 examples as a heterogeneous **demonstration corpus** for auditing evaluation provenance and numerical-health information.

**Forbidden:** “first reproducible validation of CE-QUAL-W2.”

### Core conceptual pair (Abstract / Discussion)
> A goodness-of-fit value is not only a property of a model and observations; it is a property of a specified model quantity, observation pairing, processing pathway, run configuration, and metric.  
> This does **not** make cross-study comparison intrinsically invalid; it makes interpretation **conditional** on sufficient alignment of those evaluation conditions.

---

## 4. Section blueprint (what to write + which Fig/Table)

Keep existing inventory numbering (`P1_figure_inventory.md`, Tables 1–5).

| Section | Write | Primary figures / tables |
|---|---|---|
| **Abstract** | Purpose = evaluation integrity; four deliverables; one Bonneville numeric hook; hard bounds (no OOS; internal ≠ skill) | — |
| **1 Intro** | Metrics are one layer; R²/NSE/KGE differ; metrics cannot encode provenance/control/NHR. Bridge via Benicio gap (W5 counts). Contributions C1–C4 | Fig. 4 (lit R² vs NSE rug) optional early |
| **2 Claim taxonomy** | Define *observational skill* vs *internal consistency* vs *numerical health* vs *reproducibility* | Table 4 caption language |
| **3 Methods / Framework** | VPR schema; control-state matrix; metrics + comparability envelope; NHR fields; w2eval run-card | Fig. 7 run-card; Table 2 (W5) |
| **4 Demo corpus** | Official examples as **demonstrations**, not “validation sites.” Map cases → questions | Table 3 |
| **5.1 VPR** | Bonneville A/B/C (+ S); lead with correlation vs NSE | Fig. 1–3; **Table 1** |
| **5.2 Gating** | ON/OFF availability semantics | Fig. 5; Table 1 B/S; Fig. 8 spill |
| **5.3 Internal** | DeGray / Columbia as negative controls on interpretation | Table 4; w1 figures |
| **5.4 NHR** | Long Lake INTER ON 5/4/1/5 vs OFF 0; Columbia 0/0/0 | Fig. 6; **Table 5** |
| **5.5 Repro / SOD** | Example audit; SOD magnitude only | Table 3; w7 figures |
| **6 Discussion** | Upstream provenance problem; conditional comparability; relationship to Almeida (complement) & Benicio (gap); limitations list | — |
| **7 Conclusions** | Three claims + run-card sentence; no “mandatory standard” | — |
| **Code/data** | Zenodo (when cast); scripts; cards | `zenodo/` |

### Case → question map
| Case | Role |
|---|---|
| Bonneville TDG | VPR + metric sensitivity (**skill** vs CCIW) |
| TDGTA ON/OFF | Gated-output semantics |
| DeGray T | Internal consistency only |
| Columbia DO | Internal consistency only |
| Columbia SOD | Transplanted-parameter magnitude check |
| Long Lake | Principal NHR / H1<0 demonstration |

---

## 5. Suggested figure order (existing assets)

1. Fig. 1 — TDG timeseries / ON–OFF  
2. Fig. 2 — 1:1 scatters  
3. Fig. 3 — KGE decomposition (r, α, β) — **core**  
4. Fig. 4 — Literature R² vs NSE context  
5. Fig. 5 — Reachable range / >120%  
6. Fig. 6 — NHR DLT scan (not a universal law)  
7. Fig. 7 — w2eval run-card  
8. Fig. 8 — Spill redistribution  

Captions must flag skill vs internal; non-forecast; non-calibrated SOD where relevant.

---

## 6. Essential reading for writers (verified; top 5 starred)

1. ★ Almeida & Coelho 2025 — https://doi.org/10.5194/gmd-18-6135-2025  
2. ★ Bennett et al. 2013 — https://doi.org/10.1016/j.envsoft.2012.09.011  
3. ★ Gupta et al. 2009 — https://doi.org/10.1016/j.jhydrol.2009.08.003  
4. ★ Knoben et al. 2019 — https://doi.org/10.5194/hess-23-4323-2019  
5. ★ Benicio et al. 2024 — https://doi.org/10.3390/w16243556  
6. Jakeman et al. 2006 — https://doi.org/10.1016/j.envsoft.2006.01.004  
7. Legates & McCabe 1999 — https://doi.org/10.1029/1998WR900018  
8. Clark et al. 2021 — https://doi.org/10.1029/2020WR029001  
9. Planque et al. 2022 — https://doi.org/10.1016/j.ecolmodel.2022.110059  
10. Stagge et al. 2019 — https://doi.org/10.1038/sdata.2019.30  

Full verified table: `../notes/chatgpt_briefs/literature_architecture_raw.md`.

---

## 7. Next drafting steps (no commit)

1. Align Abstract / §1.3 contribution bullets to templates above (surgical, keep JSON anchors).  
2. Ensure Discussion §5.x uses “conditional comparability” wording.  
3. Keep w2eval MVP as reference implementation, not the sole claim.  
4. Zenodo DOI remains user-side blocker for GMD submission.
