# ChatGPT raw review (2026-08-16)\n\nSource: https://chatgpt.com/c/6a809d8e-db58-83ea-b9e7-073f76a8e52c\n\n1) Understanding of the paper problem

The manuscript is not primarily arguing that CE-QUAL-W2 itself produces unreliable simulations; it argues that a reported goodness-of-fit value can become scientifically ambiguous when the evaluated variable/output pathway, controller state, and numerical health of the run are not documented together. The paper therefore proposes a W2-specific reporting discipline centered on VPR, controller-conditional evaluation, and a numerical-health record (NHR), and uses selected CE-QUAL-W2 applications to show why conventional GOF values—especially R² considered alone—can conceal materially different evaluation conditions. The defensible claim is about the conditions required to interpret and compare reported GOF, not that existing W2 studies are invalid.

2) Weakest points in the argument, ranked
1. The categorical “not comparable” claim is stronger than the evidence supports

This is the largest remaining vulnerability.

The present Abstract says:

“Until those three items are public, goodness-of-fit numbers from different CE-QUAL-W2 applications are not comparable.”

The Conclusions similarly say:

“Goodness-of-fit numbers reported for CE-QUAL-W2 applications are not comparable unless three attachments travel with them.”

Your evidence demonstrates something slightly narrower and more defensible: without those reporting elements, direct comparability cannot be established reliably, or should not be presumed.

There is an important epistemic distinction:

“not comparable” = the quantities cannot legitimately be compared;

“comparability cannot be established from the published information” = available metadata are insufficient to know whether the comparison is like-for-like.

The paper supports the second much more strongly than the first.

This is a surgical wording problem, not a study-design problem.

Recommended core formulation:

“GOF values from different CE-QUAL-W2 applications should not be assumed to be directly comparable unless the evaluated variable and provenance, controller state, and numerical health are reported sufficiently to establish like-for-like evaluation.”

That still carries the paper.

2. The empirical base is heterogeneous, so the paper must separate demonstration from validation

The 17-example suite sounds broad, but the evidentiary roles are not equivalent.

Bonneville is the strongest observational example. By contrast:

DeGray temperature is an internal-consistency comparison.

Columbia DO is an internal-consistency comparison.

The SOD exercise is based on parameters transplanted from DeGray.

Long Lake primarily informs the NHR argument.

Parts of the literature audit remain unresolved because full text was available for only 9/38 items.

A referee can therefore attack any sentence implying that the entire three-part framework has been “validated across 17 applications.”

That is not what the evidence shows.

The stronger structure is:

the examples exercise different failure modes or reporting ambiguities;

not:

the examples independently validate the full framework.

This distinction should be explicit in the Abstract, Results synthesis, Discussion, and Conclusions.

3. The NHR result is useful, but mechanistically thin and case-specific

The corrected treatment is now substantially safer, but this remains a likely referee target.

The Long Lake matrix is:

DLTINTER ON:

DLTMAX 20 s → 5 negative-thickness events

50 s → 4

100 s → 1

200 s → 5

DLTINTER OFF:

0/0/0/0

This is plainly non-monotonic. Moreover, with DLTINTER ON, nominal DLTMAX=20 s does not mean the integration window remains at 20 s; the window reaches approximately 231 s, with the day-40 knot at 1800 s.

Therefore the experiment does not identify a “smaller Δt causes instability” relationship.

Columbia further limits generalization: 120/360/720 produced 0/0/0.

The result still matters because it establishes the narrower point:

a normal process exit can coexist with internal H1<0 → DLTMIN rollback behavior that would be invisible if numerical health were reduced to exit status.

That is sufficient justification for NHR.

Do not try to make it into a general numerical-stability result.

4. The literature-review denominator is potentially vulnerable

The W5 evidence must be handled very carefully.

You have:

VPR: 2/38;

file-level criterion: 0/38;

full text actually inspected: 9/38;

unresolved cases retained as unknown.

A referee will object immediately if 2/38 or 0/38 is written as though absence were established in all 38 publications.

The safe distinction is between:

“confirmed present,”

and

“confirmed absent.”

For the cases where full text was unavailable, “not observed from the material accessible to us” is not equivalent to “absent.”

This is probably the single easiest place for a skeptical referee to allege denominator inflation.

Keep the unknown category visible.

5. Some diagnostic demonstrations risk being mistaken for physical or predictive validation

Three cases are especially sensitive.

First, a gated file is not equivalent to deletion of the underlying modeled quantity. TDG_output.csv remains, and the ON/OFF comparison gives MAE = 0. The paper therefore cannot say that the physical TDG variable or process was “removed.”

Second, the SOD result is not a calibration. The parameters were transplanted from DeGray 31→50. For the wet cells, 968/1081 = 0.8955 lie within the cited 0.5–3.0 band, with none exceeding 3.0. That is a plausibility/internal-consistency screen only.

Third, neither DeGray nor Columbia supports predictive-skill claims. Their R²/NSE values are internal-consistency diagnostics, and no out-of-sample NSE should appear.

These limitations do not weaken the manuscript if stated explicitly. They become weaknesses only if the prose overstates what those exercises establish.

3) Must-downgrade / rewrite sentence list
A. Abstract closing sentence

Current:

“Until those three items are public, goodness-of-fit numbers from different CE-QUAL-W2 applications are not comparable.”

Why it is too strong:

It transforms an evidentiary limitation into an absolute mathematical statement. Two independently published NSE values could in fact be comparable; the problem is that without adequate provenance and run-state information, the reader may be unable to establish that comparability.

Use:

“Without these reporting elements, goodness-of-fit values from different CE-QUAL-W2 applications should not be assumed to represent directly comparable evaluation conditions.”

Or slightly stronger:

“Without these reporting elements, the direct comparability of goodness-of-fit values across CE-QUAL-W2 applications cannot generally be established from the reported metric alone.”

I prefer the second.

B. Conclusions opening sentence

Current:

“Goodness-of-fit numbers reported for CE-QUAL-W2 applications are not comparable unless three attachments travel with them.”

Problems:

“Not comparable” is categorical, and “attachments travel with them” is rhetorically memorable but slightly informal for the principal scientific conclusion.

Use:

“Goodness-of-fit values reported for different CE-QUAL-W2 applications should be interpreted as conditionally comparable: like-for-like comparison requires sufficient information on variable provenance, controller state, and numerical health.”

C. Any sentence implying that R² establishes or disproves provenance

Current argument, paraphrased:

R² cannot police provenance.

The mathematical point is correct, but “police provenance” is rhetorically stronger than necessary.

Because R² is invariant to a positive affine transformation s
′
=as+b, it cannot by itself diagnose offset or scale mismatch.

Use:

“R² alone cannot establish that two evaluated series have equivalent provenance, scale, or mean behavior. Metrics sensitive to bias and scaling, including the corresponding α/β terms and NSE, provide complementary information.”

Important nuance: α/β/NSE also do not prove provenance. They merely expose mismatches that R² can conceal.

D. Any wording such as “the TDG variable was removed/deleted when the output was gated”

Must be removed.

Why:

The file-level gate is not evidence that the modeled physical variable disappeared. TDG_output.csv remains, and ON/OFF MAE = 0.

Use:

“The tested gate changed the reporting/output pathway rather than demonstrating removal of the underlying TDG state or process; TDG_output.csv remained available and the tested ON/OFF outputs had MAE = 0.”

If filename-level detail is too implementation-specific for the Discussion:

“The tested output gate should therefore be interpreted as a reporting-pathway condition, not as deletion of the underlying physical variable.”

E. Any wording such as “smaller time steps destabilized Long Lake”

Must be removed.

Why:

The counts are 5/4/1/5, not monotonic. Nominal DLTMAX is also not identical to the time step actually encountered under DLTINTER.

Use:

“For Long Lake, negative-thickness rollback events occurred under DLTINTER=ON for each tested nominal DLTMAX setting, whereas none occurred with DLTINTER=OFF. Because event counts were non-monotonic and the active controller allowed time steps to depart from the nominal DLTMAX settings, these tests do not establish a general dependence of instability on smaller Δt.”

Then:

“Their role here is to demonstrate why an NHR should accompany conventional run-success indicators.”

F. Any wording such as “the Long Lake instability was reproduced across CE-QUAL-W2 cases”

Must be removed.

Columbia 120/360/720 gave 0/0/0.

Use:

“The negative-thickness rollback signature was observed in the completed Long Lake tests but was not reproduced in the tested Columbia configurations.”

G. Any statement interpreting SNP NV as the same numerical pathology

Must be separated.

You have OFF/20 s NV = 7.75% with zero negative-thickness events.

Use:

“SNP NV and the negative-thickness rollback diagnostic are distinct numerical-health indicators; the former occurred in a configuration with zero negative-thickness events.”

H. “DeGray/Columbia validate model skill”

Must be downgraded.

Use:

“The DeGray and Columbia comparisons are used as internal-consistency diagnostics rather than independent observational validation.”

If reporting the values:

“For DeGray, T2 versus Tvolavg gave R² = 0.9027 and NSE = −0.5855; for the Columbia 49-versus-33 comparison, R² = 0.6505 and NSE = −1.4821. These values characterize agreement between internal representations and are not measures of external predictive skill.”

I. Any “out-of-sample NSE” wording

Remove the OOS qualifier entirely.

The manuscript should state explicitly, where ambiguity is possible:

“No out-of-sample NSE is claimed in this analysis.”

Likewise, the 21.2% quantity must not be relabeled as out-of-sample performance.

J. Any wording such as “the transferred SOD parameters were calibrated/validated”

Must be replaced.

Use:

“The SOD parameters were transplanted from the DeGray configuration rather than calibrated for this application. The resulting spatial values were used only for a plausibility/internal-consistency check against the cited range and do not support calibration or scenario-response claims.”

You can then report the actual result:

“Among 1081 wet cells, 968 (0.8955) fell within the cited 0.5–3.0 range and none exceeded 3.0.”

Do not turn this into validation.

K. Any literature-review statement equivalent to “only 2 of 38 papers reported VPR” without missing-data qualification

Use:

“VPR information could be confirmed for 2 of the 38 records examined. Full text was available for 9/38 records; cases that could not be resolved from the accessible material were retained as unknown rather than coded as absent.”

For the file criterion, use the same logic.

4) Rewritten Abstract + rewritten Conclusions
Rewritten Abstract

Goodness-of-fit metrics are widely used to summarize CE-QUAL-W2 applications, but the same numerical metric can refer to different modeled variables, output pathways, controller states, and numerical conditions. This creates a reproducibility problem when results from different applications are compared without sufficient information to establish that the evaluations are like-for-like. We examine this problem using CE-QUAL-W2 application cases and organize the required reporting information into three elements: VPR, controller-conditional evaluation, and a numerical-health record (NHR). The Bonneville analysis illustrates the sensitivity of interpretation to the evaluation pathway: for n=1614, the A/B/C comparisons produced NSE values of −2.8044, +0.5000, and −2.7516 while R² remained within 0.508–0.551. This contrast demonstrates why R² alone cannot establish equivalent bias, scale, or provenance. DeGray temperature and Columbia dissolved-oxygen comparisons are used only as internal-consistency diagnostics rather than as independent validation of predictive skill. Numerical-health tests further show that a successful process exit does not necessarily establish a numerically uneventful simulation. In the completed Long Lake tests, DLTINTER=ON produced 5, 4, 1, and 5 negative-thickness rollback events for nominal DLTMAX settings of 20, 50, 100, and 200 s, respectively, whereas DLTINTER=OFF produced none. This pattern is reported as an NHR result and does not establish a general smaller-Δt instability law. The broader example suite and literature audit also expose limitations in observational coverage and reporting completeness; where full text could not be resolved, records are retained as unknown rather than treated as negative evidence. We therefore argue that cross-application CE-QUAL-W2 goodness-of-fit values should be treated as conditionally interpretable: their direct comparability cannot generally be established from the metric alone without adequate provenance, controller-state, and numerical-health information.

Rewritten Conclusions

This study examined a reproducibility problem in the interpretation of goodness-of-fit values reported for CE-QUAL-W2 applications. A numerical GOF value is not self-defining: its meaning depends on the modeled quantity being evaluated, the pathway by which that quantity was extracted or constructed, the controller and output conditions under which the simulation was run, and the numerical health of the run. We therefore recommend that cross-application GOF values be treated as conditionally comparable rather than assumed to be like-for-like from the metric value alone. In the terminology used here, VPR, controller-conditional evaluation, and an NHR provide the minimum reporting structure needed to make that assessment more transparent.

The Bonneville tests provide the clearest quantitative example of the metric problem. For n=1614, the A/B/C evaluations gave NSE values of −2.8044, +0.5000, and −2.7516 while R² varied only from 0.508 to 0.551. The result does not imply that R² is an invalid statistic. It shows that R² alone is insufficient to establish equivalent mean, scale, or provenance because correlation-type measures can remain similar under transformations that substantially alter other components of agreement. Bias- and scale-sensitive quantities and NSE therefore provide complementary information. The DeGray temperature comparison (R² = 0.9027, NSE = −0.5855) and the Columbia 49-versus-33 dissolved-oxygen comparison (R² = 0.6505, NSE = −1.4821) are interpreted only as internal-consistency diagnostics. They are not independent observational validations, and no out-of-sample NSE is claimed.

The NHR analysis addresses a different failure mode. A CE-QUAL-W2 run can return process exit status 0 while internal numerical-control events still occur. In the completed Long Lake tests, DLTINTER=ON produced 5, 4, 1, and 5 negative-thickness rollback events at nominal DLTMAX settings of 20, 50, 100, and 200 s, whereas DLTINTER=OFF produced 0, 0, 0, and 0. The counts are non-monotonic, and under DLTINTER=ON the realized time-step behavior is not represented by the nominal DLTMAX label alone. The tested Columbia settings of 120, 360, and 720 s produced no corresponding events. These experiments therefore do not support a general law linking smaller Δt to instability. Their contribution is narrower: they demonstrate why process completion alone is an incomplete numerical-health criterion and why controller state and rollback diagnostics should be reported. SNP NV is treated separately because it can occur without negative-thickness events.

The remaining examples likewise require explicit limits on interpretation. A gated output file should not be interpreted as deletion of the underlying modeled physical variable: in the TDG test, TDG_output.csv remained and the tested ON/OFF comparison gave MAE = 0. The SOD exercise is also not a calibration. Its parameters were transplanted from the DeGray configuration; among 1081 wet cells, 968 (0.8955) lay within the cited 0.5–3.0 range and none exceeded 3.0. This is used only as a plausibility/internal-consistency check and does not support scenario-response inference. More generally, observational support is uneven across the 17-example suite, with Bonneville providing the principal field-observation case among the completed examples considered here.

The literature assessment should be interpreted with the same restraint. Full text was available for 9 of 38 records, and unresolved cases are retained as unknown rather than treated as evidence of absence. The audit therefore identifies reporting gaps that could be confirmed from the accessible material; it does not establish that every inaccessible study omitted the relevant information.

The main conclusion is consequently procedural rather than model-specific. A published CE-QUAL-W2 GOF value should not be treated as directly comparable with another application solely because the same statistic is reported. Comparability becomes assessable when the evaluated variable and its provenance, the relevant controller and output conditions, and the numerical-health information required to interpret the run are reported together. The proposed reporting structure is intended to make those conditions explicit, not to invalidate previous CE-QUAL-W2 applications or to substitute internal-consistency diagnostics for observational validation.

5) Likely referee attacks + suggested author replies
Referee attack 1: “The main conclusion is obvious or tautological—metrics are always conditional on what was evaluated.”

Suggested reply:

We agree that the general principle that a metric depends on its evaluation protocol is not new. We have revised the manuscript to avoid presenting that principle itself as the novelty. The contribution is the operationalization of this problem for CE-QUAL-W2 through three concrete reporting elements—VPR, controller-conditional evaluation, and NHR—and through W2-specific examples showing how output provenance, controller behavior, and internal numerical events can alter the interpretation of otherwise conventional GOF reporting. We have also softened the claim from “GOF values are not comparable” to “direct comparability should not be assumed or cannot be established from the metric alone.”

This is probably the most important pre-emptive reply.

Referee attack 2: “Your evidence does not validate the framework across 17 independent applications.”

Suggested reply:

We agree and have revised the text accordingly. The 17 examples do not serve as 17 independent validation cases of the entire framework. They exercise different components of the reporting problem. Bonneville provides the main observation-based quantitative example, whereas DeGray and Columbia are explicitly treated as internal-consistency tests, Long Lake is used for the NHR analysis, and the SOD case is a parameter-plausibility check. We now distinguish these evidentiary roles throughout the manuscript.

Do not defend the broader interpretation. Concede and narrow.

Referee attack 3: “DeGray and Columbia are not model validation because you compare internal model quantities.”

Suggested reply:

Correct. These comparisons are not presented as independent validation and do not support claims of predictive skill. Their purpose is to demonstrate internal consistency and the behavior of different agreement statistics under defined model-output comparisons. We have revised the corresponding Results, Discussion, Abstract, and Conclusions to label them explicitly as internal-consistency diagnostics.

Referee attack 4: “A high R² with poor NSE is elementary and does not demonstrate provenance failure.”

Suggested reply:

We agree that disagreement between correlation and NSE is not itself novel. Our point is narrower. Because R² is invariant to affine changes in the evaluated series, R² alone cannot establish equivalence of mean, scale, or extraction provenance. We therefore do not claim that α, β, or NSE prove provenance; rather, they provide complementary diagnostics that can expose discrepancies hidden by R². The manuscript has been revised to state this limited interpretation.

This distinction is technically important.

Referee attack 5: “Your Long Lake result does not establish a time-step instability mechanism.”

Suggested reply:

We agree and do not make that claim. In Long Lake, the negative-thickness counts under DLTINTER=ON were 5, 4, 1, and 5 across nominal DLTMAX settings of 20, 50, 100, and 200 s, respectively, so there is no monotonic smaller-Δt relationship. In addition, the active controller allows realized time steps to differ from the nominal DLTMAX setting. DLTINTER=OFF produced zero events in the tested matrix, and the tested Columbia cases also produced zero corresponding events. We therefore report this only as a numerical-health observation demonstrating that exit status 0 can coexist with internal rollback events.

That reply is strong because it concedes exactly what the data cannot show.

Referee attack 6: “Why call the Long Lake behavior important if it appears in only one completed example?”

Suggested reply:

The purpose of the NHR example is not to estimate the prevalence of this behavior across CE-QUAL-W2 applications. Its role is to demonstrate existence: a completed run with process exit status 0 can still contain internal numerical-control events relevant to interpretation. A single documented case is sufficient for that limited methodological point. We now avoid language implying that the behavior is universal or frequent.

Referee attack 7: “You conflate disabling an output with removing the physical process.”

Suggested reply:

We agree that these are distinct operations. The manuscript has been corrected to describe the tested condition as a reporting/output gate rather than deletion of the physical variable. TDG_output.csv remained available, and the tested ON/OFF comparison had MAE = 0. We therefore make no claim that the underlying TDG state or physics was removed.

Referee attack 8: “The SOD analysis is not a validation because the parameters were imported from another model.”

Suggested reply:

Correct. The SOD parameters were transplanted from the DeGray configuration and were not calibrated for this case. We use the resulting field only as a plausibility/internal-consistency check against the cited range. The manuscript now states explicitly that this exercise is neither a calibration nor evidence for scenario-response accuracy.

Referee attack 9: “Your literature review overstates absence because you had full text for only 9/38 studies.”

Suggested reply:

We agree that inaccessible records cannot be coded as confirmed absence. Full text was available for 9/38 records, and unresolved cases are retained as unknown. We have revised the wording so that the reported counts distinguish information that could be positively confirmed from information that could not be resolved. The literature audit is therefore evidence of incomplete confirmability from the accessible record, not proof that all unresolved publications omitted the reporting item.

I would make this logic visible in the table itself, not just the Discussion.

Referee attack 10: “Where is the out-of-sample validation?”

Suggested reply:

Out-of-sample predictive validation is not a claim of this study and is not required for the methodological question addressed here. The manuscript evaluates provenance, controller-conditioned interpretation, numerical health, and reproducibility of reported GOF. We have removed any wording that could imply out-of-sample NSE and explicitly state that no OOS NSE is claimed.

Do not promise a new OOS experiment in this revision.

Referee attack 11: “Your successful-run criterion is arbitrary if exit 0 is insufficient.”

Suggested reply:

That is precisely the motivation for the NHR component. Process exit status remains useful as a software-level completion indicator, but it is not treated as a sufficient numerical-health criterion. The NHR supplements rather than replaces exit status by recording controller events and other numerical diagnostics relevant to interpretation.

Referee attack 12: “You are proposing a mandatory reporting standard from a small case set.”

Suggested reply:

We have revised the language from a universal standard-setting claim to a reporting recommendation. The three elements are proposed as a minimal reproducibility structure motivated by the demonstrated failure modes. The manuscript does not claim that the present case set establishes regulatory or community-wide sufficiency of these fields for every CE-QUAL-W2 application.

That is the right GMD posture: operational recommendation, not decree.

6) Uncertainties / what I cannot judge without the full 6700-word PDF

There are several issues I would not sign off on from the supplied context alone.

First, I cannot determine whether VPR is defined precisely enough for another group to apply it without author interpretation. The manuscript needs an operational definition—what fields are mandatory, what constitutes provenance resolution, and what is coded unknown. I can judge the argument for provenance reporting, but not the exact adequacy of the VPR specification without seeing the Methods and tables.

Second, I cannot assess whether the A/B/C Bonneville pathways are described clearly enough for a reader to reproduce exactly why NSE changes from −2.8044 to +0.5000 to −2.7516 while R² remains in the 0.508–0.551 range. This example is carrying a substantial portion of the paper's argument, so its procedural explanation must be unusually clear.

Third, I cannot verify the literature-audit search strategy, inclusion/exclusion criteria, duplicate handling, date cutoff, or coding rules. Given the 9/38 full-text limitation, these methodological details matter considerably.

Fourth, I cannot judge whether every figure and table caption preserves the same epistemic distinctions as the main text. Captions are a common place for overclaims such as “validation,” “instability,” or “parameter agreement” to survive after the body text has been corrected.

Fifth, I cannot determine whether the manuscript consistently distinguishes DLTMAX, realized DLT, DLTINTER behavior, H1<0 events, rollback to DLTMIN, negative-thickness counts, and SNP NV. Those terms should not collapse into a generic “instability” category.

Sixth, I cannot judge whether the NHR event-counting implementation is specified sufficiently to reproduce Table 5: exactly what constitutes one event, whether repeated rollback messages at the same model time are deduplicated, and how the counting window is defined. That is a reproducibility issue, not a request for a new experiment.

Seventh, I cannot verify whether the cited Almeida SOD range of 0.5–3.0 is contextually comparable in units, definition, and environmental interpretation to the transplanted SOD field. Even if it is, the present wording should remain “plausibility check,” not calibration.

Eighth, I cannot determine whether the 17-example suite is described in a way that makes the uneven evidence base obvious to the reader. If Table 1 or the Methods visually presents all 17 as equivalent validation cases, the prose corrections alone will not be enough.

Ninth, I cannot inspect whether any residual v1 wording still states or implies physical deletion of TDG, a general Δt-instability law, OOS NSE, or calibrated SOD. Those four phrases deserve a literal manuscript-wide search before submission.

Tenth, I cannot evaluate the GMD reproducibility statement in full. Because the working directory has no .git, the manuscript should not claim a branch, HEAD, or commit identifier that cannot be verified from the workspace. Run cards, configurations, CE-QUAL-W2 version/source information, and JSON-derived result provenance can still support reproducibility, but the exact adequacy of the archival package requires inspection of the paper and supplementary material.

Overall, I would not redesign P1. The main required revision is claim calibration. The underlying paper is more defensible when framed as demonstrating why CE-QUAL-W2 GOF requires explicit provenance, controller context, and numerical-health metadata for cross-study interpretation, rather than claiming that all published GOF values are intrinsically incomparable.

---

## Round-2 follow-up ranking (same URL; text-only; 2026-08-16)

Advisor ranked remaining candidates:

**P1**
1. Soften residual absolute phrasing (“They do not,” “must be reported,” “incomparable on skill,” “police provenance”); keep recommendation not mandatory standard.
2. Lengthen Methods limits: NHR event = one wrn negative-thickness line, no same-JDAY dedup; W5 confirmed-present vs confirmed-absent / unknown.

**P2**
4. Caption hygiene (Fig. S1 plausibility-not-calibration; Fig. 5 annual not forecast skill; keep Fig. 6 non-universal CFL).
- Add short Discussion pre-answers (novelty≠tautology; 17 examples≠full-framework validation; protocol=recommendation).

**P3**
5. Align Chinese outline Conclusions + w2eval README.

Executor already applied R1–R6 locally in matching priority; no redesign / no OOS / no Zenodo upload.