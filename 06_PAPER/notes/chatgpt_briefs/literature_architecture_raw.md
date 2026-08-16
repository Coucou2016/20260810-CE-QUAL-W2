# Literature architecture — ChatGPT advisor raw + Cursor verification

**Date:** 2026-08-16  
**Conversation:** https://chatgpt.com/c/6a812957-b108-83ea-b941-617f36744d76  
**Isolation:** NEW chat (not the critical-review thread `6a809d8e-…`)  
**Mode:** text paste only; **网页搜索 ON**; no attachments  
**Full advisor extract:** `_chatgpt_lit_extract.txt` (33 342 chars)

---

## 1. Advisor summary (CURSOR paraphrase)

### Overall recommendation
- Prefer **GMD — Methods for assessment of models**, with EMS-style protocol logic (named compact protocol + checklist/run-card), rather than classic CE-QUAL-W2 application IMRaD.
- **Almeida & Coelho (2025)** = excellent *model evaluation application* template, but our center of gravity is the **evaluation methodology** (VPR / gated outputs / NHR / run-cards), with official examples as demonstrations.
- Fallback: GMD **Model evaluation paper** if the text stays too W2-specific to claim a transferable method.
- EMS: submit as **Research Article** (no separate formal “software paper” type).

### Three architectures
| Arch | Fit | Use |
|---|---|---|
| Classic IMRaD / application | Moderate–low | Case discipline only; avoid reservoir-by-reservoir novelty hierarchy |
| GMD assessment/evaluation | Very high | Assessment problem → evidence taxonomy → framework → demos → bounds → reproducibility |
| EMS protocol/tool | Very high if w2eval matures | Deficiency → requirements → named protocol → implementation → demos → limits |

### Contribution sentence style (advisor; accepted with hard constraints)
- VPR: GoF can depend on output provenance; report VPR with metrics.
- Gating: control-state dependence / conditional availability of diagnostic outputs — **not** “physical quantity deleted”.
- NHR: accompany skill with execution diagnostics — **reporting recommendation**, not timestep law; H1<0 mainly Long Lake.
- Run-cards: reference implementation + official-example audit — not “first reproducible validation of W2”.

### Novelty paragraph (advisor; adopted with “conditional comparability”)
Contemporary W2 studies do calibration/process evaluation; broader literature covers metrics/reproducibility. Remaining issue: performance hard to interpret when **variable provenance**, **control configuration of diagnostic outputs**, and **numerical health** are not co-recorded. Framework = VPR + control-state audit + NHR + run-cards — **complementary to** Almeida, **informed by gap in** Benicio-style practice, not a replacement for calibration papers.

---

## 2. Verified reading list (Cursor independent check)

| # | Citation (verified) | DOI / URL | Verdict | Imitation point (Cursor) |
|---:|---|---|---|---|
| 1 | Almeida, M.; Coelho, P. *Evaluating the performance of CE-QUAL-W2 version 4.5 sediment diagenesis model.* Geosci. Model Dev., **18**, 6135–6165, 2025. | https://doi.org/10.5194/gmd-18-6135-2025 | **PASS** | GMD model-evaluation spine; Zenodo package precedent |
| 2 | Jakeman, A.J.; Letcher, R.A.; Norton, J.P. *Ten iterative steps in development and evaluation of environmental models.* Environ. Model. Softw., **21**, 602–614, 2006. | https://doi.org/10.1016/j.envsoft.2006.01.004 | **PASS** | Protocol as iterative practice, not one case |
| 3 | Bennett, N.D. et al. *Characterising performance of environmental models.* Environ. Model. Softw., **40**, 1–20, 2013. | https://doi.org/10.1016/j.envsoft.2012.09.011 | **PASS** | Purpose-conditioned performance workflow |
| 4 | Planque, B. et al. *A standard protocol for describing the evaluation of ecological models.* Ecol. Model., **470**, 110059, 2022. | https://doi.org/10.1016/j.ecolmodel.2022.110059 | **PASS** | Named protocol + answerable fields (OPE) → run-card analogy |
| 5 | Seuru, S. et al. *The ODE (Overview, Data, and Execution) protocol…* Environ. Model. Softw., **198**, 106912, 2026. | https://doi.org/10.1016/j.envsoft.2026.106912 | **PASS** (DOI/year OK) | Checklist reporting; **soft relevance** (ML-focused — imitate format only) |
| 6 | Legates, D.R.; McCabe, G.J. *Evaluating the use of “goodness-of-fit” measures…* Water Resour. Res., **35**, 233–241, 1999. | https://doi.org/10.1029/1998WR900018 | **PASS** | R² alone insufficient for validation |
| 7 | Gupta, H.V.; Kling, H.; Yilmaz, K.K.; Martinez, G.F. *Decomposition of the mean squared error and NSE…* J. Hydrol., **377**, 80–91, 2009. | https://doi.org/10.1016/j.jhydrol.2009.08.003 | **PASS** | r / α / β decomposition → Fig. 3 logic |
| 8 | Knoben, W.J.M.; Freer, J.E.; Woods, R.A. *Inherent benchmark or not? Comparing NSE and KGE…* Hydrol. Earth Syst. Sci., **23**, 4323–4331, 2019. | https://doi.org/10.5194/hess-23-4323-2019 | **PASS** | Do not equate NSE/KGE benchmarks |
| 9 | Clark, M.P. et al. *The abuse of popular performance metrics in hydrologic modeling.* Water Resour. Res., **57**, e2020WR029001, 2021. | https://doi.org/10.1029/2020WR029001 | **PASS** | Sampling uncertainty; avoid metric overclaim |
| 10 | Benício, S.H.M.; Basso, R.E.; Formiga, K.T.M. *Global Applications of the CE-QUAL-W2 Model…* Water, **16**, 3556, 2024. | https://doi.org/10.3390/w16243556 | **PASS** | Application landscape / motivation for VPR gap (W5) |
| 11 | Stagge, J.H. et al. *Assessing data availability and research reproducibility in hydrology…* Sci. Data, **6**, 190030, 2019. | https://doi.org/10.1038/sdata.2019.30 | **PASS** | Reproducibility artefacts / run-card motivation |
| 12 | Lindenschmidt, K.-E. et al. *CE-QUAL-W2 model of dam outflow elevation impact…* Sci. Data, **6**, 312, 2019. | https://doi.org/10.1038/s41597-019-0316-y | **PASS** | Nature-portfolio data descriptor with W2 archive; **not** our architecture template |

**Rejected / corrected by Cursor**
- None of the 12 DOIs failed resolution.
- **Soft-reject as structural model:** Seuru (ML ODE) and Lindenschmidt (data descriptor) — keep as optional reading, not spine templates.
- **Page range note:** Almeida GMD HTML cites **6135–6165** (plan v2 had 6135–6161); use journal citation from GMD page.
- **GMD type nuance (Cursor):** “Model evaluation papers” require a prior model-description citation; our primary target **Methods for assessment of models** avoids forcing a fake “new model version evaluation” framing. If editors push evaluation type, cite Cole & Wells / official W2 docs as description anchors.

**Local supplements already in project (not from ChatGPT list but keep)**
- Nash & Sutcliffe 1970; Cole & Wells EL-03-1 (2003); Wells 2002; Chang 2015; Lima Neto 2023; Hipsey et al. EMS aquatic metrics 2020 (`10.1016/j.envsoft.2020.104697`) as optional Level 0–3 analogy.

---

## 3. Hard-constraint compliance check on advisor text

| Constraint | Advisor | Cursor |
|---|---|---|
| Conditional comparability (not absolute incomparable) | Explicit §6.2 | **Adopt** |
| Internal ≠ skill | Explicit | **Adopt** |
| No “physical quantity deleted” | Explicit | **Adopt** |
| NHR ≠ timestep law; Long Lake | Explicit | **Adopt** |
| No OOS NSE; 2016–2025 ≠ forecast | Explicit limitations | **Adopt** |
| SOD transplant only | Explicit | **Adopt** |

---

## 4. What Cursor will land in framework docs

- Journal: **GMD Methods for assessment of models** (primary); EMS Research Article (alt); GMD Model evaluation (fallback).
- Spine: GMD assessment + EMS protocol compactness.
- Existing Fig. 1–8 / Tables 1–5 retained (do not renumber to ChatGPT’s draft Fig. 3/4).
- Contribution templates in English + Chinese frameworks.
