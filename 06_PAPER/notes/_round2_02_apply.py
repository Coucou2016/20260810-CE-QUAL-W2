# -*- coding: utf-8 -*-
"""Apply ROUND 2-02 ChatGPT-adopted rewrites."""
from pathlib import Path
import re

p = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\drafts\P1_GMD_draft_v2.md")
t = p.read_text(encoding="utf-8")

# Front matter: remove Intended article type; keep version scope; move Zenodo only in §8
t = t.replace(
    "**Intended article type:** *Geoscientific Model Development* — Methods for assessment of models.\n\n",
    "",
)
t = t.replace(
    " Out-of-sample NSE was not computed. A persistent Zenodo archive of the paper-relevant materials is pending (**待补充**).",
    " Out-of-sample NSE was not computed.",
)

# Abstract full replace between ## Abstract and ## 1 Introduction
a0 = t.find("## Abstract\n")
a1 = t.find("## 1 Introduction")
if a0 < 0 or a1 < 0:
    raise SystemExit("abstract markers missing")
new_abs = """## Abstract

Reported goodness-of-fit values are comparable across model applications only when the evaluated quantity and the conditions under which it was produced are sufficiently reconstructable. We develop a CE-QUAL-W2-specific assessment protocol that links each reported performance statistic to a variable provenance record (VPR), controller-state provenance, a numerical health record (NHR), and a reproducible run-card. A structured audit of 38 eutrophication applications shows that the paper-level VPR-core criterion—station or segment, layer or depth, constituent, and comparison period—is reconstructable in only 2 of 38 studies (5.3%). <!-- w5_lit_audit_summary.json --> Among the 12 *R*² values reported in the review summary table, **1** is confirmed as CE-QUAL-W2 output versus observations, **7** correspond to other evaluation objects, and **4** remain unresolved. Full methods-plus-calibration text was available for 9 of 38 studies (23.7%); inaccessible or silent cases were retained as unknown rather than treated as confirmed absence.

We then apply the protocol to official CE-QUAL-W2 examples. At Bonneville Dam, the same Cascade Island observations (*n* = 1614) paired with three defensible TDG output channels give a narrow *R*² range of 0.508–0.551 but NSE values of −2.804, +0.500, and −2.752, showing that correlation alone neither identifies the evaluated model quantity nor reveals associated bias and variability differences. <!-- w3_tdgta_off_metrics.json --> The best-performing Bonneville series is controller-specific: disabling `TDGTA` removes that output file but does not remove the physical TDG state, which remains available through the pre-control SYSTDG pathway. Out-of-sample NSE for 2016–2025 was not computed because the reproduced simulation ends near 2011; the later observations are used only for contextual exceedance analysis. <!-- w4_cciw_vs_dart.json -->

Numerical diagnostics provide a third conditioning factor. At Long Lake, runs can terminate normally while recording negative surface-layer-thickness rollbacks. With the official `DLTINTER=ON` interpolation, warning counts for day-30 DLTMAX knots of 20/50/100/200 s are 5/4/1/5, whereas `DLTINTER=OFF` gives 0/0/0/0. <!-- nhr_dlt_scan.json --> This result motivates NHR reporting but does not imply a general timestep–stability law. Together, the examples show that goodness-of-fit values should be treated as conditionally comparable when variable identity, controller state, or numerical health differs or is insufficiently documented.

We therefore operationalize the evaluation-object contract in a minimal evaluator (`w2eval`) that writes VPR, metrics, and NHR run-cards from archived analysis records without rerunning the model. Without those reporting elements, the direct comparability of goodness-of-fit values across CE-QUAL-W2 applications cannot generally be established from the reported metric alone.

"""
t = t[:a0] + new_abs + t[a1:]

# Contribution blocks
c1_old_start = "**Contribution 1 (variable provenance).**"
c4_end = "We do **not** claim a first reproducible validation of CE-QUAL-W2.\n\nThe rest of the paper"
i1 = t.find(c1_old_start)
i2 = t.find(c4_end)
if i1 < 0 or i2 < 0:
    raise SystemExit("contribution markers missing")
new_contrib = """**Contribution 1 (variable provenance).** We define and operationalize an eight-field **variable provenance record (VPR)** that specifies the model quantity, extraction route, spatial support, processing state, time support, and observation-pairing rule associated with an evaluation statistic. The Bonneville example demonstrates that alternative defensible output channels paired with the same observations can produce similar *R*² values but substantially different NSE values (*R*² ≈ 0.508–0.551; NSE = −2.804, +0.500, and −2.752); <!-- w3_tdgta_off_metrics.json --> DeGray temperature and Columbia dissolved-oxygen comparisons are used only as within-run internal-consistency diagnostics, not as observational skill.

**Contribution 2 (control-state and gated outputs).** We incorporate controller state into the evaluation record when the availability or interpretation of an output channel depends on an internal control rule. In the Bonneville example, the series with NSE = +0.500 is available only when `TDGTA=ON`; disabling the controller removes the controller-specific output but does not delete the underlying physical TDG state, because SYSTDG continues to write the pre-control TDG series. <!-- w3_tdgta_off_metrics.json --> Controller state is therefore treated as part of the evaluation-object definition rather than as evidence that the physical variable itself is absent. DART hourly data show that 21.2% of valid hours in 2016–2025 still exceed 120%; that statistic supports a reachable-range argument and is not an out-of-sample NSE. <!-- w4_cciw_vs_dart.json -->

**Contribution 3 (numerical health).** We define an **numerical health record (NHR)** as an execution-diagnostic component accompanying statistical model assessment. The Long Lake example demonstrates that successful termination can coexist with negative surface-layer-thickness rollbacks to `DLTMIN`; the observed 5/4/1/5 counts under the tested `DLTINTER=ON` schedule knots, compared with 0/0/0/0 under `DLTINTER=OFF`, are used to demonstrate the information added by the NHR rather than to infer a general relationship between timestep size and numerical stability. <!-- nhr_dlt_scan.json -->

**Contribution 4 (assessment protocol and demonstration corpus).** We combine VPR, controller-state provenance, and NHR information in reproducible **run-cards** and apply the protocol to heterogeneous official CE-QUAL-W2 examples as a **demonstration corpus**. The corpus exercises distinct assessment conditions rather than serving as a multi-site validation campaign: Bonneville provides the observation-based skill case; DeGray and Columbia provide internal-consistency diagnostics; Long Lake provides the numerical-health case; and the Columbia SOD calculation is only a magnitude-plausibility check based on parameters transplanted from DeGray, not a Columbia field calibration. We provide `w2eval`, a provenance-aware run-card writer. We do **not** claim a first reproducible validation of CE-QUAL-W2.

The rest of the paper"""
# Fix grammar: "an numerical" -> "a numerical"
new_contrib = new_contrib.replace("an **numerical health record", "a **numerical health record")
t = t[:i1] + new_contrib + t[i2 + len("We do **not** claim a first reproducible validation of CE-QUAL-W2.\n\nThe rest of the paper") :]

t = t.replace(
    "We do **not** claim to invent provenance or reproducible evaluation as concepts. Almeida and Coelho (2025) remain the closest CE-QUAL-W2 + GMD precedent (*Model evaluation* of sediment-diagenesis options); we complement that layer by **operationalizing** a CE-QUAL-W2-specific evaluation-object contract that jointly binds variable provenance, controller-conditional outputs, and numerical-health context to reported goodness-of-fit statistics.",
    "Almeida and Coelho (2025) remain the closest CE-QUAL-W2 + GMD precedent (*Model evaluation* of sediment-diagenesis options). The contribution here is the CE-QUAL-W2-specific operationalization of evaluation-object principles that jointly bind variable provenance, controller-conditional outputs, and numerical-health context to reported goodness-of-fit statistics.",
)
t = t.replace(
    "discusses conditional comparability and interpretation limits (Sect. 6), and concludes (Sect. 7).",
    "discusses conditional comparability and scope limitations (Sect. 6), and concludes (Sect. 7).",
)
t = t.replace(
    "discusses conditional comparability and likely objections (Sect. 6), and concludes (Sect. 7).",
    "discusses conditional comparability and scope limitations (Sect. 6), and concludes (Sect. 7).",
)

# Methods micro-edits
repls = [
    (
        "W2 may expose the same constituent or state-variable family through several output channels with different spatial support, aggregation, derivation, or control state (Cole and Wells, 2003; Wells, 2002).",
        "CE-QUAL-W2 can represent a constituent or state-variable family in several output channels that differ in spatial support, aggregation, derivation, or control state (Cole and Wells, 2003; Wells, 2002).",
    ),
    (
        "For total dissolved gas at Bonneville, three further channels exist.",
        "For the Bonneville total-dissolved-gas example, additional TDG representations arise from the withdrawal, SYSTDG, and TDG-target pathways.",
    ),
    (
        "Module `withdrawal.f90` converts dissolved N2 and DO to a TDG percentage using the model’s Henry-law formula.",
        "In `withdrawal.f90`, dissolved N2 and DO are converted to TDG percentage using the model’s Henry-law formulation.",
    ),
    (
        "A practitioner who asks “what is modelled TDG?” therefore has at least four answers on one Bonneville run: Henry-converted WDO at segment 76 (caliber A), the controller file (B), the in-reservoir TSR TDG column at segment 40 (C), and the SYSTDG daily file (S). A, B, C, and S are different Variable Provenance Records. Calling them all “TDG skill” is a category error.",
        "Accordingly, four distinct TDG evaluation objects can be constructed from a single Bonneville run: Henry-converted WDO at segment 76 (caliber A), the controller file (B), the in-reservoir TSR TDG column at segment 40 (C), and the SYSTDG daily file (S). A, B, C, and S therefore correspond to distinct VPRs and should not be treated as interchangeable observational-skill objects.",
    ),
    (
        "Layer counts are not a truncation-error diagnostic.",
        "Layer addition and subtraction are treated here as geometry-management events rather than as truncation-error diagnostics.",
    ),
    (
        "Seasonal stage at a dam or in a tidal slough will cross those thresholds; add/subtract counts belong in an NHR as geometry events, not as failures.",
        "Because these threshold crossings can arise from changes in simulated stage, add/subtract counts are recorded in the NHR as geometry events rather than classified as failures by themselves.",
    ),
    (
        "Negative surface thickness is a different event.",
        "Negative surface-layer thickness is evaluated separately because it activates the model’s timestep-rollback pathway.",
    ),
    (
        "A rollback-prone run can therefore finish with exit 0, a clean-looking terminal message, and a warning file that a skill table never reads.",
        "Consequently, a completed run can return exit code 0 and “Normal termination” while retaining rollback warnings that are not represented by the statistical performance metrics.",
    ),
    (
        "Editing the day-30 knot changes the interpolation **start**, not a hard cap inside the window.",
        "Consequently, the day-30 DLTMAX value is an interpolation knot rather than a hard timestep cap over days 30–40.",
    ),
    (
        "That is the theoretical content of Contribution 1; Sect. 5 supplies the empirical instances.",
        "Thus *R*² alone cannot diagnose the variance and bias differences represented by α and β.",
    ),
    (
        "The tool neither launches CE-QUAL-W2 nor recomputes the performance metrics; when archived records and a run directory diverge, the card follows the archived analysis.",
        "The tool neither launches CE-QUAL-W2 nor recomputes the performance metrics.",
    ),
    (
        "Coding definitions follow the archived literature-audit summary record (`w5_lit_audit_summary.json` in the accompanying repository). Inclusion is the review’s own 38-row Table 1 (refs [12]–[14], [18], [21]–[54]); we do not re-run a bibliographic search.",
        "Coding followed the archived literature-audit record. The audit population was fixed to the 38 studies selected by Benicio et al. (2024) (Table 1 refs [12]–[14], [18], [21]–[54]).",
    ),
    (
        "Case-to-question map used in Sect. 5: Bonneville TDG → observational VPR sensitivity; TDGTA ON/OFF → gated-output semantics; DeGray T and Columbia DO → internal-consistency negative controls; Long Lake → NHR under exit 0; Columbia SOD → transplanted-parameter magnitude check; W5 audit → literature gap (not a W2 run). Suite inventory appears with Results in Table 3 (Sect. 5.5).",
        "The cases address complementary assessment questions: Bonneville TDG for observational VPR sensitivity; TDGTA ON/OFF for gated-output semantics; DeGray T and Columbia DO for internal-consistency diagnostics; Long Lake for NHR under exit 0; Columbia SOD for transplanted-parameter magnitude check; and the literature audit for reporting gaps (not a W2 run). Suite inventory appears with Results in Table 3 (Sect. 5.5).",
    ),
    (
        "Caliber A is not a straw man. It uses the Henry conversion shipped in `withdrawal.f90`, a choice a competent reader would make in the absence of a VPR.",
        "Caliber A follows the Henry-law conversion implemented in `withdrawal.f90` and therefore represents a technically plausible output-selection pathway in the absence of an explicit VPR.",
    ),
    (
        "This is **not** a Columbia calibration and supports **no** water-quality scenario inference. It only shows that the transplanted file did not produce absurd SOD.",
        "This is **not** a Columbia calibration and supports **no** water-quality scenario inference. The comparison is limited to a magnitude-plausibility check and provides no evidence of Columbia-specific calibration.",
    ),
    (
        "the metric that is published is the metric that is blind.",
        "the prevalent reporting pattern therefore provides limited information on variance and bias errors.",
    ),
    (
        "Report NHR. Do not generalize “smaller Δ*t* is less stable”.",
        "Report NHR. The Long Lake result should not be generalized into a monotonic timestep–stability relationship.",
    ),
]
for a, b in repls:
    if a not in t:
        print("MISSING:", a[:60])
    else:
        t = t.replace(a, b, 1)

# Clean any leftover figure path crumbs
t = re.sub(r"\s*`\.\./w2eval/[^`]+`", "", t)
t = re.sub(r"\s*`\.\./figures/[^`]+`", "", t)

p.write_text(t, encoding="utf-8")
print("ROUND 2-02 landed")
