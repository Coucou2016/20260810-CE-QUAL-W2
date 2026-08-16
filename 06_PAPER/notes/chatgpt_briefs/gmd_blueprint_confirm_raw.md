# GMD blueprint confirmation — ChatGPT advisor raw

**Date:** 2026-08-16  
**Conversation (reused):** https://chatgpt.com/c/6a812957-b108-83ea-b941-617f36744d76  
**Title (browser):** CE-QUAL-W2 评估架构  
**Mode:** text paste only; **网页搜索 ON** (response showed site-search chips / GMD guidance citations); **no attachments**  
**Thinking time (UI):** 思考了 57s  
**Source extract:** CDP `innerText` of last assistant message (citation badges cleaned lightly below)

---

## Prompt sent (follow-up summary)

FOLLOW-UP requesting confirmation of locked drafting contract: GMD Methods for assessment; structure Evidence taxonomy → Assessment methods → Demonstration corpus → Findings 5.1–5.5; contributions VPR / control-rule gated output / NHR (+ run-cards as implementation); hard constraints (conditional comparability; internal≠skill; no deleted state variable; NHR≠timestep law; no OOS NSE). Four numbered advisor questions on venue fit, structure, claim strength, and ≤7 pre-submission checklist items.

---

## Advisor reply (verbatim extract)

Article type: KEEP — GMD “Methods for assessment of models.”

This is still the best primary fit. Current GMD guidance explicitly defines this category to include “new metrics for assessing model performance,” “novel ways of comparing model results with observational data,” relevant data-analysis/visualisation methods, and fully fledged assessment software tools. By contrast, GMD “Model evaluation papers” are framed primarily as substantial stand-alone evaluations of the performance of an already described model, often comparing configurations or parameterisations. Your assessment object is explicitly the evaluation workflow and evidentiary interpretation, with CE-QUAL-W2 cases serving as demonstrations; that distinction is decisive.

Soft fallback: GMD “Model evaluation paper” only if the manuscript drifts during drafting so that most of the scientific content becomes “how CE-QUAL-W2 performs in these examples” rather than “how model evaluations should document provenance/control/numerical health.” Almeida & Coelho (2025) is a useful contrast: their GMD paper is explicitly a model-evaluation study of CE-QUAL-W2 v4.5 sediment diagenesis performance, which is not your intended contribution.

I would not switch to EMS now. EMS remains a plausible second-journal destination because its scope explicitly accepts Research Articles on advances in environmental modelling and software, but GMD gives your precise methodological contribution a named manuscript category.

One important current-GMD compliance issue: because the manuscript deals with one named model, GMD's review criteria say the model name and version number should be included in the title. Your working title has CE-QUAL-W2 but no version. Before submission, replace this with the exact audited version/release identifier(s); if multiple releases are involved, state that scope accurately rather than inventing one version.

Structure: fundamentally keep it; I recommend only three surgical changes.

KEEP Section 2, Evidence taxonomy. This is not redundant. In this particular paper it performs an essential logical function: it prevents observational skill, internal consistency, numerical-health evidence, and reproducibility evidence from being silently collapsed into one category. I would rename it slightly to “Evidence taxonomy and interpretation rules” and begin it with one short subsection defining the assessment object and the permitted claims for each evidence class.

KEEP Sections 3 and 4 separate. Section 3 should define the assessment method independently of individual reservoirs/examples; Section 4 should then specify the demonstration corpus and case→question mapping. This separation is very compatible with the GMD Methods logic: method first, example implementation second. GMD explicitly allows theoretical assessment methods provided an example implementation is supplied.

I would reorder Section 3 internally to make the hierarchy unmistakable:

3.1 output/evaluation architecture → 3.2 VPR → 3.3 control-state provenance → 3.4 NHR → 3.5 downstream GoF metrics → 3.6 W4/W5 literature-audit coding → 3.7 w2eval run-card implementation.

That ordering visibly makes R²/NSE/KGE downstream, not a fourth pillar.

MERGE/RENAME Results 5.5. “Reproducibility, SOD magnitude, run-cards” currently combines three different logical objects. I suggest:

5.5 Reproducibility audit and run-card implementation

with Columbia SOD as a bounded sub-subsection/case result:

5.5.x Transplanted-parameter SOD magnitude check

This prevents reviewers from reading SOD as another calibration/validation contribution.

No new top-level section is needed. Put a clearly labelled “Scope and limitations” subsection inside Discussion. That is where the six hard boundaries should be consolidated.

A recent 2026 GMD precedent is also directionally supportive: the Rapid Evaluation Framework for the CMIP7 Assessment Fast Track is classified under “Methods for assessment of models” and explicitly emphasizes consistency, transparency and provenance metadata around evaluation packages.

Contribution strength: C1 and C4 are good; C2 and C3 merit minor softening. The main overclaim is actually in the one-sentence argument.

C1 VPR — KEEP as written. “Can depend materially” is appropriately existential rather than universal. The Bonneville result provides the concrete demonstration. Just ensure the numerical sentence always remains explicitly case-specific.

C2 — soften “confounder.” “Confounder” can invite a stricter causal/statistical interpretation than your gated-file evidence requires.

Recommended rewrite:

We identify control-state dependence as a source of evaluation ambiguity when diagnostic or controller-specific outputs are conditionally available, and incorporate control-state provenance into the evaluation record.

This fully preserves the contribution without implying that controller state causally explains every GoF difference.

C3 — minor terminology correction. Because NHR accompanies internal-consistency analyses as well as genuine observational skill, replace “reported skill” with “reported evaluation statistics”:

We propose that statistical performance be accompanied by a numerical health record (NHR) documenting execution diagnostics relevant to interpretation of reported evaluation statistics.

Then retain the explicit bound: reporting recommendation, not universal timestep law; H1<0 evidence principally Long Lake.

C4 — KEEP. Correctly positioned as implementation rather than a fourth scientific pillar.

The one sentence I would definitely change is:

“published goodness-of-fit is not a portable skill quantity unless…”

That is too binary for your locked conditional comparability position, and “skill” also becomes problematic for internal-consistency cases.

Use instead:

In CE-QUAL-W2 evaluation practice, the interpretation and cross-study portability of reported goodness-of-fit are conditional on adequate documentation and alignment of variable provenance, controller state, and numerical-health context; we demonstrate these dependencies using official-example reproductions and a 38-paper audit, while distinguishing internal consistency from observational skill and making no claim of out-of-sample NSE performance.

That is materially safer.

Pre-submission minimum revision checklist, in priority order

1. Resolve GMD manuscript-type/title compliance. State explicitly in the cover letter why this is “Methods for assessment of models,” cite the prior CE-QUAL-W2 description, and insert the exact CE-QUAL-W2 version/release scope into the title where applicable. GMD explicitly checks model name/version and manuscript-type fit.

2. Freeze a claim–evidence matrix before prose polishing. Every headline result should be tagged observational skill / internal consistency / NHR / reproducibility. Hard-code the exclusions: no OOS NSE; 2016–2025 exceedance descriptive only; Columbia SOD magnitude check only; no “deleted physical quantity.”

3. Make the 38-paper audit method referee-proof. State search/inclusion rules, W4/W5 coding rules and denominators explicitly. For W5, preserve full text assessed = 9/38, and distinguish confirmed present, confirmed absent, and unknown/not verifiable; never convert unknown into absence.

4. Freeze the reproducibility package before submission. GMD currently requires exact versions of relevant code/data and preprocessing, run-control and post-processing scripts; for Methods papers, the coded assessment product must be available, and access must exist already at preprint submission. Use a compliant persistent archive when ready, but do not cite a repository DOI until one actually exists.

5. Regenerate every headline number from run-cards in one reproducible pass. Especially Bonneville n=1614, the R²/NSE channel comparison, TDG ON/OFF semantics, Long Lake NHR counts, and the literature-audit summary. This directly addresses GMD's explicit “traceability of results” review criterion.

6. Make the figures encode evidence boundaries. Fig. 1 should distinguish evaluation record from downstream metrics; the gated-output figure must distinguish file availability from physical-state existence; internal-consistency figures should say “internal consistency” directly in captions; the NHR figure should explicitly disavow a universal timestep criterion.

7. Run a final claim-language audit on Abstract, Introduction last paragraph, Discussion and Conclusions. Search specifically for: validation, skill, comparable/incomparable, delete/deleted, calibration, forecast/out-of-sample, must/mandatory, and first. Each occurrence should survive only if its evidence class supports it.

With those changes, I would keep the blueprint essentially intact. The principal remaining submission risk is not the section architecture; it is whether the manuscript demonstrates that VPR + control-state provenance + NHR constitute a sufficiently general assessment method rather than a taxonomy retrospectively fitted to several CE-QUAL-W2 peculiarities. The Evidence-taxonomy section, 38-paper audit, and executable run-card specification are therefore central to the GMD case, not ancillary material.
