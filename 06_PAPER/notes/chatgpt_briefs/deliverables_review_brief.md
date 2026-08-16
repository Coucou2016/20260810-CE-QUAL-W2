# Deliverables review brief for ChatGPT (text-only paste). Web search ON required.
# Do NOT upload attachments. Conversation: literature-framework or new deliverables-review.

## Hard constraints (must obey)
1. No inventing numbers; Bonneville A/B/C NSE = -2.804 / +0.500 / -2.752 (JSON); DeGray/Columbia = internal consistency only.
2. Do NOT claim physical TDG deleted; SYSTDG snapshot remains when TDGTA=OFF.
3. NHR 5/4/1/5 is NOT a universal timestep-stability law; OFF → 0/0/0/0.
4. No out-of-sample NSE (model ~2011); 21.2% exceedance is frequency only.
5. Primary venue: GMD Methods for assessment of models.
6. Conditional comparability language only (no absolute incomparability).
7. Cursor will independently verify any journal requirement / DOI you cite.

## Paper: Abstract (current v2, condensed)
In CE-QUAL-W2 evaluation practice, interpretation and cross-study portability of reported goodness-of-fit are conditional on variable provenance, controller state, and numerical-health context. Without reconstructable provenance, cross-site comparison cannot generally be established from the reported metric alone. VPR reconstructable in 2/38 Benicio studies; file/column confirmed 0/38; only 1/12 Table-2 R² confirmed as W2-vs-obs skill; full text 9/38.

Three independent reasons: (1) Same CCIW n=1614 → R² 0.508–0.551 but NSE −2.804 / +0.500 / −2.752 across three TDG channels; same R²-blind α/β-visible pattern as internal consistency at DeGray T and Columbia DO. (2) Skill-best series only in TDGTarget_output.csv; TDGTA=OFF removes file but not physical TDG (SYSTDG snapshot MAE=0 ON/OFF). (3) Exit 0 can coexist with H1<0→DLTMIN rollbacks; Long Lake DLTINTER ON 5/4/1/5 vs OFF 0/0/0/0. Protocol: VPR + control-state + NHR + run-cards (w2eval).

## Paper: chapter skeleton
1 Intro → 2 Evidence taxonomy → 3 Assessment methods → 4 Demonstration corpus → 5 Results (finding-led) → 6 Discussion → 7 Conclusions → Code/Data availability (Zenodo DOI pending) → Refs. Target: GMD Methods for assessment of models; v4.5.5 primary + v5.0 beta inventory.

## Three contribution sentences
C1: Goodness-of-fit can depend materially on output-variable provenance; VPR makes quantity/route/state/target explicit (Bonneville three-caliber R²-narrow / NSE-wide; DeGray/Columbia internal consistency).
C2: Control-state dependence: skill-best TDG exists only in gated file; OFF removes file ≠ deletes physical variable (SYSTDG snapshot persists).
C3: Statistical performance should be accompanied by NHR (H1<0 rollbacks under exit 0); reporting recommendation, not universal Δt law.

## Report: TOC structure
Cover → Abstract → Background & aims → Data & methods (incl. deep glossary) → Process → Results (25 figures each with: 背景与作用 / 怎么读 / 每条曲线含义 / 能得出什么结论 / 通俗版结论) → Discussion → Conclusions → Limitations → Appendix.

## Two example figure explanation paragraphs (representative)
Fig.1 TDGTA ON/OFF multi-caliber timeseries: explains gated file vs SYSTDG snapshot; CCIW window; A/B/C/S meanings; conclusion that best skill only in B; plain-language “dispatcher report card” analogy.
Fig. NHR neg-thickness vs DLTMAX: exit 0 vs warnings; ON 5/4/1/5 non-monotone; OFF all zero; not a universal smaller-Δt instability law.

## Advisor tasks (web search ON)
1. Verify against primary sources: GMD “Methods for assessment of models” submission requirements (sections, Code/Data availability, figure rules) vs our skeleton.
2. Are Abstract/contribution sentences still too strong?
3. Are report figure+glossary explanations readable for non-specialists? Name weakest 3 places.
4. Any missing near-2-year evaluation-protocol / reproducibility papers in hydro & water-quality modelling?
5. ≤7 minimal revision bullets.

Respond in structured Markdown. Cite DOIs/URLs for every journal requirement claim.
