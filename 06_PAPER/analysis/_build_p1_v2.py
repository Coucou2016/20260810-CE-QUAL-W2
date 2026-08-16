# One-shot builder: P1_GMD_draft_v1.md -> P1_GMD_draft_v2.md
from pathlib import Path

src = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\drafts\P1_GMD_draft_v1.md")
dst = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\drafts\P1_GMD_draft_v2.md")
text = src.read_text(encoding="utf-8")


def between(start, end=None, *, drop_start=True):
    """Return text from start to end. If drop_start, omit the start marker itself."""
    i = text.find(start)
    if i < 0:
        raise SystemExit(f"missing {start!r}")
    body_i = i + len(start) if drop_start else i
    if end is None:
        return text[body_i:]
    j = text.find(end, i + len(start))
    if j < 0:
        raise SystemExit(f"missing end {end!r}")
    return text[body_i:j]


unresolved = between(
    "## Unresolved discrepancies", "## Abstract", drop_start=False
)
arch = between(
    "### 2.1 CE-QUAL-W2 output architecture\n\n", "### 2.2 Layer add/subtract"
)
rollback = between(
    "### 2.2 Layer add/subtract and H1 < 0 rollback\n\n", "### 2.3 Cases"
)
cases = between("### 2.3 Cases\n\n", "## 3 Protocol")
protocol = between(
    "## 3 Protocol: VPR, conditional evaluation, NHR, and w2eval\n\n", "## 4 Results"
)
bonn = between(
    "#### 4.1.1 Bonneville TDG versus CCIW (skill)\n\n", "#### 4.1.2 DeGray"
)
degray = between(
    "#### 4.1.2 DeGray temperature (internal consistency)\n\n",
    "#### 4.1.3 Columbia",
)
columbia = between(
    "#### 4.1.3 Columbia DO (internal consistency)\n\n",
    "#### 4.1.4 Literature",
)
lit = between(
    "#### 4.1.4 Literature audit (motivation, not a W2 run)\n\n",
    "### 4.2 Control-rule",
)
control = between("### 4.2 Control-rule confounding\n\n", "### 4.3 Numerical health")
nhr = between("### 4.3 Numerical health\n\n", "### 4.4 Official example")
repro = between(
    "### 4.4 Official example reproducibility and SOD magnitude\n\n",
    "## 5 Discussion",
)
disc = between("## 5 Discussion\n\n", "## 6 Conclusions")
conc = between("## 6 Conclusions\n\n", "## 7 Code and data availability")
code = between("## 7 Code and data availability\n\n", "## Appendix A")
app = between("## Appendix A: Figure file map\n\n", "## Author contributions")
auth = between(
    "## Author contributions (stub — CRediT-style)\n\n", "## Competing interests"
)
comp = between("## Competing interests (stub)\n\n", "## Acknowledgements")
ack = between("## Acknowledgements (stub)\n\n", "## References")
refs = between("## References\n\n")

prot = protocol
for a, b in [
    ("### 3.1 Variable Provenance Record (VPR)", "### 3.3 Variable Provenance Record (VPR)"),
    ("### 3.2 Controller-conditional evaluation", "### 3.4 Controller-conditional evaluation"),
    ("### 3.3 Numerical Health Record (NHR)", "### 3.5 Numerical Health Record (NHR)"),
    ("### 3.4 Metrics", "### 3.6 Metrics"),
    ("### 3.5 w2eval", "### 3.7 w2eval"),
    ("### 3.6 Literature audit methods (W5)", "### 3.8 Literature audit methods (W5)"),
    ("### 3.7 DART comparison methods (W4)", "### 3.9 DART comparison methods (W4)"),
]:
    prot = prot.replace(a, b)

control2 = control.replace("#### 4.2.", "#### 5.2.")
bonn2 = bonn.replace(
    "Figure 1 overlays the ON/OFF series on CCIW and the controller target band. Figure 2 shows 1:1 scatter. Figure 3 decomposes KGE into *r*, α, and β: the plot in which Claim 1 is visible at a glance.",
    "Figure 3 decomposes KGE into *r*, α, and β and is the glance test for Contribution 1. Figure 1 overlays the ON/OFF series on CCIW and the controller target band. Figure 2 shows 1:1 scatter.",
)

disc2 = disc
for a, b in [
    ("### 5.1 ", "### 6.1 "),
    ("### 5.2 ", "### 6.2 "),
    ("### 5.3 ", "### 6.3 "),
    ("### 5.4 ", "### 6.4 "),
]:
    disc2 = disc2.replace(a, b)
disc2 = disc2.replace("listed in Sect. 4.4", "listed in Sect. 5.5")
disc2 = disc2.replace(
    "### 6.1 Why *R*² alone cannot establish provenance equivalence\n\n",
    "### 6.1 Why *R*² alone cannot establish provenance equivalence\n\n"
    "Bennett et al. (2013) summarize evaluation practice as requiring transparency about what was compared and how. "
    "Gupta et al. (2009) show why correlation-based scores can remain high while variability and bias fail. "
    "The Bonneville and internal-consistency demonstrations instantiate both points for CE-QUAL-W2 output architecture.\n\n",
)
disc2 = disc2.replace(
    "### 6.4 Relation to Almeida and Coelho (2025)\n\n"
    "Almeida and Coelho (2025) is both a journal precedent (GMD accepts W2 evaluation papers with open archives) and an independent SOD magnitude anchor.",
    "### 6.4 Relation to Almeida and Coelho (2025)\n\n"
    "Almeida and Coelho (2025) is both a journal precedent (GMD accepts open, reproducible W2 evaluation) and an independent SOD magnitude anchor. "
    "Their article type evaluates sediment-diagenesis **process options**; ours is complementary: an auditable assessment layer **under** such performance statistics "
    "(Methods for assessment of models).",
)
disc2 = disc2.replace(
    "What remains, and what we think is publishable as a GMD model-evaluation paper, is a **reporting recommendation**",
    "What remains, and what we think is publishable as a GMD **methods-for-assessment** paper, is a **reporting recommendation**",
)

header = """<!--
P1 working draft for Geoscientific Model Development (Methods for assessment of models).
Not a final submission. Numbers follow analysis JSON / run-cards; notes are narrative only.
Do not treat DeGray temperature or Columbia DO metrics as skill versus observations.
Blueprint: P1_MERGED_BLUEPRINT.md. Prior structural draft: P1_GMD_draft_v1.md (retained).
-->

# Variable provenance, control-state outputs, and numerical health: a methods framework for assessing reported goodness-of-fit in CE-QUAL-W2 applications

**Working Chinese title:** 变量溯源、控制状态输出与数值健康：面向 CE-QUAL-W2 拟合优度报告的方法学评估框架

**Target journal:** *Geoscientific Model Development* (**Methods for assessment of models**)

**Draft status:** v2 merged manuscript (2026-08-16). Restructured from v1 per `P1_MERGED_BLUEPRINT.md` (GMD Methods spine + nature-skills discipline; figure inventory unchanged). Not a camera-ready submission. Zenodo archive not yet minted. Out-of-sample NSE was **not** computed.

"""

abstract = """## Abstract

Published CE-QUAL-W2 goodness-of-fit numbers are not generally portable skill scores across applications. Without reconstructable provenance, cross-site comparison of those numbers is not generally warranted. A structured audit of the 38 eutrophication applications assembled by Benicio et al. (2024) shows that a Variable Provenance Record (output file, column, segment, layer, units, derivation chain, time support, pairing tolerance) can be reconstructed from the paper alone in only 2 of 38 studies (5.3%); that a W2 output file or column name was confirmed in 0 of 38 (partial constituent wording is common; unknowns stay unknown); and that only 1 of 12 *R*² values in the review’s summary table can be confirmed as W2-versus-observation skill. <!-- w5_lit_audit_summary.json --> Full text of methods-plus-calibration results was obtainable for 9 of 38 papers (23.7%); the rest were coded from abstracts and the review tables, with unknowns left as unknowns rather than coded as confirmed absence.

We reproduce official example applications and show three independent reasons why a published skill number is not a portable quantity. First, the same run emits several numerical series that a practitioner might call “TDG”, “temperature”, or “dissolved oxygen”. At Bonneville Dam, pairing the same Cascade Island (CCIW) observations (*n* = 1614; JDAY 40613.583–40681.542) to three output channels yields *R*² in a narrow band 0.508–0.551 while Nash–Sutcliffe efficiency (NSE) is −2.804, +0.500, and −2.752. <!-- w3_tdgta_off_metrics.json --> The highest *R*² is among the worst NSE values. The same *R*²-blind, α/β-visible pattern appears as **internal consistency** (not skill versus observations) for DeGray surface temperature versus volume-average temperature (*R*² = 0.9027, NSE = −0.5855, *n* = 2943) and for Columbia Slough dissolved oxygen at three TSR segments (highest-*R*² pair *R*² = 0.6505, NSE = −1.4821, *n* = 116). <!-- w1_provenance_metrics.json --> Pearson *R*² is invariant to affine rescaling of the simulated series and therefore cannot detect the variance-ratio (α) and bias-ratio (β) errors that variable misidentification produces.

Second, the skill-best Bonneville series (NSE = +0.500, β = 0.9986, paired maximum 120.09%) exists only in the controller-gated file `TDGTarget_output.csv`. Turning `TDGTA` off removes that file; it does **not** delete the physical TDG variable. SYSTDG still writes `TDG_TDG` to `TDG_output.csv`, a pre-control snapshot that is bit-identical on and off (MAE = 0) and cannot substitute for the gated series (daily MAE = 1.7073 versus the gated file; raw maxima 131.7% versus 120.1%). <!-- w3_tdgta_off_metrics.json --> Independent DART hours confirm that the example observations were not rewritten (hourly *n* = 17805, MAE = 0.026537%). Out-of-sample NSE for 2016–2025 was **not** computed: the reproduced model ends near 2011 (TMEND = 40909). Those later years are used only for exceedance frequency (21.2% of valid hours >120%) and for the 2011 spill comparison.

Third, a run can return exit code 0 and “Normal termination” while `w2.wrn` records negative surface-layer thickness (H1 < 0) rollbacks to DLTMIN. That geometry failure is visible only at Long Lake among completed runs. Under official `DLTINTER=ON`, negative-thickness counts at the day-30 DLTMAX knot 20/50/100/200 s are 5/4/1/5; under `DLTINTER=OFF` they are 0/0/0/0. <!-- nhr_dlt_scan.json --> The main claim is that a Numerical Health Record (NHR) should accompany skill reporting, not that smaller time steps are less stable.

We propose a reporting protocol packaged as an evaluation record—VPR, control-state provenance, NHR, and run-cards—implemented in a minimal evaluator (`w2eval`) that writes cards from existing analysis files without rerunning the model. Without those reporting elements, the direct comparability of goodness-of-fit values across CE-QUAL-W2 applications cannot generally be established from the reported metric alone.

"""

intro = """## 1 Introduction

CE-QUAL-W2 (hereafter W2) is a two-dimensional, laterally averaged hydrodynamic and water-quality model used for reservoirs, rivers, and estuaries (Cole and Wells, 2003; Wells, 2002). Applications routinely publish a single goodness-of-fit number, most often the coefficient of determination *R*², and reviews then array those numbers as if they ranked calibration quality. Benicio et al. (2024) screened the eutrophication literature and tabulated *R*² from 0.32 to 0.977 for 12 of 38 selected studies, attributing the spread in their §3.2 (“Calibration Variability”) to data quality, methodological maturity, and site complexity. That explanation may be part of the story. It cannot be tested, however, unless each *R*² is attached to a reconstructable evaluation object: which output file and column, which segment and layer, whether an internal control rule was binding, and whether the time integration was numerically healthy.

Those three attachments are almost never present. We coded all 38 selected rows of Benicio et al. (2024) Table 1 (their references [12]–[14], [18], [21]–[54]; Table 1 has 38 rows and matches the stated “38 selected”). <!-- w5_lit_audit_summary.json --> A Variable Provenance Record as defined in Sect. 3.3 is reconstructable from the paper alone in 2 of 38 studies (5.3%). A W2 output file or column name was confirmed in 0 of 38 (`vpr_variable=yes`); many rows have only partial constituent wording. Eleven of 38 report *R*² for any model they used; nine of those eleven (81.8%) do not report NSE; none report the Kling–Gupta efficiency (KGE; Gupta et al., 2009). Of the 12 *R*² entries in the review’s Table 2, only one—Lima Neto (2023), *R*² = 0.32—can be confirmed as W2 output versus field observations of the stated constituents. The remaining Table 2 entries mix pan-evaporation correlations, inflow concentration regressions, load-reduction response curves, watershed-model (SWAT) skill mislabelled as W2 skill, and values that the review text itself describes as *R* rather than *R*². Full text covering methods and calibration results was legally obtainable for 9 of 38 papers (23.7%). Nineteen papers are `unknown` on VPR reconstructability because full text was unavailable and the abstract was silent. We do not upgrade those unknowns to “no”.

Assessment guidance in environmental modelling has long stressed that reported skill is conditional on the evaluation protocol (Bennett et al., 2013). Decomposition of error into correlation, variability, and bias components (Gupta et al., 2009) further shows why a single scalar cannot stand in for an incompletely specified evaluation object. This paper is a **methods paper for assessment of models** in the GMD sense: the object of inference is the evaluation workflow, not a new process algorithm. Almeida and Coelho (2025) remain the closest CE-QUAL-W2 + GMD precedent for open, reproducible evaluation of process options; we complement that layer by making the provenance, control state, and numerical health behind goodness-of-fit statistics auditable.

The argument is organized around four contributions, stated as falsifiable claims.

**Contribution 1 (variable provenance).** We show that goodness-of-fit statistics can depend materially on the provenance of the evaluated output variable, and introduce a **variable provenance record (VPR)** that makes the model quantity, extraction route, processing state, and evaluation target explicit. On a single Bonneville run with the total-dissolved-gas target controller on (`TDGTA=ON`), three defensible choices of “the TDG series” produce *R*² values that would all be written as moderate agreement (~0.5) while NSE ranges from worse than the observational mean (NSE = −2.804 and −2.752) to NSE = +0.500. <!-- w3_tdgta_off_metrics.json --> *R*² and NSE describe different properties; neither resolves ambiguity in *which* model quantity entered the metric. DeGray temperature and Columbia dissolved-oxygen **output channels disagree with one another** on the same run; those NSE/KGE values are internal consistency, not skill versus observations. Official example folders for DeGray and Columbia contain no independent temperature or DO observations.

**Contribution 2 (control-state confounding).** We identify **control-state dependence** as an evaluation confounder when diagnostic or controller-specific outputs are conditionally available, and incorporate control-state provenance into the evaluation record. The series with NSE = +0.500, β ≈ 1, and a 120.09% cap exists only in `TDGTarget_output.csv`. Switching `TDGTA` to OFF removes that file together with `TDGTarget_warning.opt`. SYSTDG continues to write `TDG_TDG` to `TDG_output.csv`. That file is a pre-control snapshot: ON and OFF copies are identical (MAE = 0) and must not be used as a stand-in for B. <!-- w3_tdgta_off_metrics.json --> We do **not** claim that the physical variable was deleted. DART hourly data show that 21.2% of valid hours in 2016–2025 still exceed 120%; that statistic supports a reachable-range argument. It is not an out-of-sample NSE.

**Contribution 3 (numerical health).** We propose that statistical performance be accompanied by a **numerical health record (NHR)** documenting execution diagnostics relevant to interpretation of reported skill. When surface-layer thickness `H1(KT,I)` is negative and the time step exceeds `DLTMIN`, W2 writes a warning, forces `CURMAX = DLTMIN`, and recomputes the step (`w2_4_win.f90`). The run still ends with exit 0 and “Normal termination” if no fatal `w2.err` is opened. Negative-thickness rollbacks appear only at Long Lake among completed Bonneville, Columbia, DeGray, and Long Lake runs. Counts 5/4/1/5 versus DLTMAX 20/50/100/200 s hold **only** for official `DLTINTER=ON` knot interpolation; `DLTINTER=OFF` yields 0/0/0/0. <!-- nhr_dlt_scan.json --> The NHR is a **reporting recommendation**, not a universal timestep-stability criterion. We do **not** claim a general law that reducing the time step makes the geometry less stable.

**Contribution 4 (protocol and demonstration corpus).** We implement these reporting elements in reproducible **run-cards** and use official CE-QUAL-W2 examples as a heterogeneous **demonstration corpus** for auditing evaluation provenance and numerical-health information. Of 17 official examples (eight in v4.5.5, nine in v5.0 beta), only Bonneville ships field observations. Long Lake requires a `HabitatFiles/` directory that the distribution does not include. Columbia sets `SED_DIAG=ON` without shipping `W2_diagenesis.npt`; the diagenesis parameters used here were transplanted from DeGray and are **not** a Columbia field calibration. We provide `w2eval`, a provenance-aware run-card writer. We do **not** claim a first reproducible validation of CE-QUAL-W2.

The rest of the paper defines an evidence taxonomy (Sect. 2), states the assessment methods (Sect. 3), describes the demonstration corpus (Sect. 4), reports finding-led results (Sect. 5), discusses conditional comparability and likely objections (Sect. 6), and concludes (Sect. 7).

"""

taxonomy = """## 2 Evidence taxonomy

We distinguish four kinds of claim that a CE-QUAL-W2 evaluation record may support. Mixing them in a single skill table is a category error.

1. **Observational skill.** Paired model output versus independent field observations under a stated VPR and run configuration. In this paper, only Bonneville TDG versus CCIW occupies this class.
2. **Internal consistency.** Agreement among model output channels on the same run when no independent observations exist. DeGray temperature and Columbia DO metrics are labelled `internal_consistency` in every table, run-card, and caption. They diagnose provenance ambiguity; they do not rank calibration quality.
3. **Numerical health.** Execution diagnostics (especially H1 < 0 → DLTMIN rollback, layer add/subtract counts, exit status versus warning files) that condition whether two skill numbers are like-for-like. Exit code 0 is not a health certificate.
4. **Reproducibility / magnitude plausibility.** Whether an official deck can be executed as distributed, and whether transplanted parameters produce order-of-magnitude-plausible fluxes (Columbia SOD versus the Almeida and Coelho (2025) scan band). Plausibility is not site calibration.

A goodness-of-fit value is not only a property of a model and observations; it is a property of a specified model quantity, observation pairing, processing pathway, run configuration, and metric. This does **not** make cross-study comparison intrinsically invalid; it makes interpretation **conditional** on sufficient alignment of those evaluation conditions.

"""

demo = (
    "## 4 Demonstration corpus\n\n"
    "Official CE-QUAL-W2 example decks are used here as a heterogeneous **demonstration corpus** "
    "for auditing evaluation provenance and numerical health. They are not a multi-site validation "
    "campaign and are not presented as “calibration sites.”\n\n"
    + cases
    + "\nCase-to-question map used in Sect. 5: Bonneville TDG → observational VPR sensitivity; "
    "TDGTA ON/OFF → gated-output semantics; DeGray T and Columbia DO → internal-consistency negative controls; "
    "Long Lake → NHR under exit 0; Columbia SOD → transplanted-parameter magnitude check; "
    "W5 audit → literature gap (not a W2 run). Suite inventory appears with Results in Table 3 (Sect. 5.5).\n\n"
)

results = f"""## 5 Results

Results are organized by methodological finding. Reservoir names identify the demonstration, not the claim type.

### 5.1 Variable provenance (observational skill and literature gap)

#### 5.1.1 Bonneville TDG versus CCIW (skill)

{bonn2}#### 5.1.2 Literature audit (motivation, not a W2 run)

{lit}### 5.2 Control-state confounding and gated outputs

{control2}### 5.3 Internal consistency (negative controls)

#### 5.3.1 DeGray temperature (internal consistency)

{degray}#### 5.3.2 Columbia DO (internal consistency)

{columbia}### 5.4 Numerical health

{nhr}### 5.5 Reproducibility, SOD magnitude, and run-cards

{repro}"""

out = (
    header
    + unresolved
    + abstract
    + intro
    + taxonomy
    + "## 3 Assessment methods\n\n### 3.1 CE-QUAL-W2 output architecture\n\n"
    + arch
    + "### 3.2 Layer add/subtract and H1 < 0 rollback\n\n"
    + rollback
    + prot
    + demo
    + results
    + "## 6 Discussion\n\n"
    + disc2
    + "## 7 Conclusions\n\n"
    + conc
    + "## 8 Code and data availability\n\n"
    + code
    + "## Appendix A: Figure file map\n\n"
    + app
    + "## Author contributions (stub — CRediT-style)\n\n"
    + auth
    + "## Competing interests (stub)\n\n"
    + comp
    + "## Acknowledgements (stub)\n\n"
    + ack
    + "## References\n\n"
    + refs
)

out = out.replace(
    "Sect. 4 supplies the empirical instances",
    "Sect. 5 supplies the empirical instances",
)
out = out.replace(
    "Full inventory: `P1_figure_inventory.md`.",
    "Full inventory: `P1_figure_inventory.md`. SciencePlots redraw 2026-08-16; filenames unchanged.",
)

# Move Table 4 into §5.3
table4_marker = "**Table 4.** Primary internal-consistency pairs."
t4_i = out.find(table4_marker)
if t4_i < 0:
    raise SystemExit("Table 4 missing")
t4_end = out.find("\n## 6 Discussion", t4_i)
table4_block = out[t4_i:t4_end].rstrip() + "\n\n"
out = out[:t4_i] + out[t4_end:]
ins = out.find("### 5.4 Numerical health")
if ins < 0:
    raise SystemExit("5.4 missing")
out = out[:ins] + table4_block + out[ins:]

if "Bennett" not in out.split("## References")[1]:
    bennett = (
        "Bennett, N. D., Croke, B. F. W., Guariso, G., Guillaume, J. H. A., Hamilton, S. H., "
        "Jakeman, A. J., Marsili-Libelli, S., Newham, L. T. H., Norton, J. P., Perrin, C., "
        "Pierce, S. A., Robson, B., Seppelt, R., Voinov, A. A., Fath, B. D., and Andreassian, V.: "
        "Characterising performance of environmental models, Environ. Model. Softw., 40, 1–20, "
        "https://doi.org/10.1016/j.envsoft.2012.09.011, 2013.\n\n"
    )
    out = out.replace("## References\n\nAlmeida", "## References\n\n" + bennett + "Almeida")

import re

leftovers = re.findall(r"^#{2,4} 4\..*$", out, flags=re.M)
if leftovers:
    print("WARN leftovers:", leftovers[:20])

dst.write_text(out, encoding="utf-8")
print("Wrote", dst)
print("chars", len(out))
for line in out.splitlines():
    if line.startswith("## ") or (
        line.startswith("### ") and len(line) > 4 and line[4].isdigit()
    ):
        print(line)
