<!--
Manuscript for Geoscientific Model Development (Methods for assessment of models).
Numbers follow archived analysis records. DeGray temperature and Columbia DO metrics are internal consistency, not skill versus observations.
Authoring notes and JSON reconciliation live outside this submission-facing draft.
-->

# Variable provenance, control-state outputs, and numerical health: a methods framework for assessing reported goodness-of-fit in CE-QUAL-W2 v4.5.5 applications (with v5.0 beta example inventory)

All hydrodynamic integrations analysed here used CE-QUAL-W2 v4.5.5 (`w2_v455_ifx.exe`). Official v5.0 beta example folders are included only in the example inventory (Table 3); no cross-release skill comparison is made. Out-of-sample NSE was not computed.

---

## Abstract

Reported goodness-of-fit values are comparable across model applications only when the evaluated quantity and the conditions under which it was produced are sufficiently reconstructable. We develop a CE-QUAL-W2-specific assessment protocol that links each reported performance statistic to a variable provenance record (VPR), controller-state provenance, a numerical health record (NHR), and a reproducible run-card. A structured audit of 38 eutrophication applications shows that the paper-level VPR-core criterion—station or segment, layer or depth, constituent, and comparison period—is reconstructable in only 2 of 38 studies (5.3%). <!-- w5_lit_audit_summary.json --> Among the 12 *R*² values reported in the review summary table, **1** is confirmed as CE-QUAL-W2 output versus observations, **7** correspond to other evaluation objects, and **4** remain unresolved. Full methods-plus-calibration text was available for 9 of 38 studies (23.7%); inaccessible or silent cases were retained as unknown rather than treated as confirmed absence.

We then apply the protocol to official CE-QUAL-W2 examples. At Bonneville Dam, the same Cascade Island observations (*n* = 1614) paired with three defensible TDG output channels give a narrow *R*² range of 0.508–0.551 but NSE values of −2.804, +0.500, and −2.752, showing that correlation alone neither identifies the evaluated model quantity nor reveals associated bias and variability differences. <!-- w3_tdgta_off_metrics.json --> The best-performing Bonneville series is controller-specific: disabling `TDGTA` removes that output file but does not remove the physical TDG state, which remains available through the pre-control SYSTDG pathway. Out-of-sample NSE for 2016–2025 was not computed because the reproduced simulation ends near 2011; the later observations are used only for contextual exceedance analysis. <!-- w4_cciw_vs_dart.json -->

Numerical diagnostics provide a third conditioning factor. At Long Lake, runs can terminate normally while recording negative surface-layer-thickness rollbacks. With the official `DLTINTER=ON` interpolation, warning counts for day-30 DLTMAX knots of 20/50/100/200 s are 5/4/1/5, whereas `DLTINTER=OFF` gives 0/0/0/0. <!-- nhr_dlt_scan.json --> This result motivates NHR reporting but does not imply a general timestep–stability law. Together, the examples show that goodness-of-fit values should be treated as conditionally comparable when variable identity, controller state, or numerical health differs or is insufficiently documented.

We therefore operationalize the evaluation-object contract in a minimal evaluator (`w2eval`) that writes VPR, metrics, and NHR run-cards from archived analysis records without rerunning the model. Without those reporting elements, the direct comparability of goodness-of-fit values across CE-QUAL-W2 applications cannot generally be established from the reported metric alone.

## 1 Introduction

CE-QUAL-W2 (hereafter W2) is a two-dimensional, laterally averaged hydrodynamic and water-quality model used for reservoirs, rivers, and estuaries (Cole and Wells, 2003; Wells, 2002). Applications routinely publish a single goodness-of-fit number, most often the squared Pearson correlation *R*² (≡ *r*<sub>P</sub>²; not always identical to a regression coefficient of determination), and reviews then array those numbers as if they ranked calibration quality. Benicio et al. (2024) screened the eutrophication literature and tabulated *R*² from 0.32 to 0.977 for 12 of 38 selected studies, attributing the spread in their §3.2 (“Calibration Variability”) to data quality, methodological maturity, and site complexity. That explanation may be part of the story. It cannot be tested, however, unless each *R*² is attached to a reconstructable evaluation object: which output file and column, which segment and layer, whether an internal control rule was binding, and whether the time integration was numerically healthy.

Under our coding rules those attachments are rarely confirmed from the paper alone. We coded all 38 selected rows of Benicio et al. (2024) Table 1 (their references [12]–[14], [18], [21]–[54]; Table 1 has 38 rows and matches the stated “38 selected”). <!-- w5_lit_audit_summary.json --> A **VPR-core** reconstructability criterion (Sect. 3.8; weaker than the full VPR tuple in Sect. 3.3, and never requiring an output filename in this corpus) is met in 2 of 38 studies (5.3%; 19/38 remain `unknown` and are **not** coded as absence). A W2 output file or column name was confirmed in 0 of 38 (`vpr_variable=yes`); many rows have only partial constituent wording. Eleven of 38 report *R*² for any model they used; nine of those eleven (81.8%) do not report NSE; none report the Kling–Gupta efficiency (KGE; Gupta et al., 2009). Of the 12 *R*² entries in the review’s Table 2, **1** (Lima Neto, 2023, *R*² = 0.32) is confirmed W2 output versus field observations of the stated constituents; **7** are confirmed to represent other mathematical objects (pan-evaporation / inflow regressions, load-reduction curves, elevation skill mislabelled as water-quality skill, etc.); and **4** remain unresolved. <!-- w5_lit_audit_summary.json --> Full text covering methods and calibration results was legally obtainable for 9 of 38 papers (23.7%). Nineteen papers are `unknown` on VPR-core reconstructability because full text was unavailable and the abstract was silent. We do not upgrade those unknowns to “no”.

Assessment guidance in environmental modelling has long stressed that reported skill is conditional on the evaluation protocol (Bennett et al., 2013). Decomposition of error into correlation, variability, and bias components (Gupta et al., 2009) further shows why a single scalar cannot stand in for an incompletely specified evaluation object. This paper is a **methods paper for assessment of models** in the GMD sense: the object of inference is the evaluation workflow, not a new process algorithm. General provenance-aware and reproducible evaluation practice is already mature in the Earth-system modelling community: ESMValTool attaches provenance records to diagnostics (Schlund et al., 2023), and the CMIP Rapid Evaluation Framework standardises community benchmarking workflows (Hoffman et al., 2026); see also PCMDI Metrics Package and FAIR research-model guidance in References. Almeida and Coelho (2025) remain the closest CE-QUAL-W2 + GMD precedent (*Model evaluation* of sediment-diagenesis options). The contribution here is the CE-QUAL-W2-specific operationalization of evaluation-object principles that jointly bind variable provenance, controller-conditional outputs, and numerical-health context to reported goodness-of-fit statistics.

The argument is organized around four contributions, stated as falsifiable claims.

**Contribution 1 (variable provenance).** We define and operationalize an eight-field **variable provenance record (VPR)** that specifies the model quantity, extraction route, spatial support, processing state, time support, and observation-pairing rule associated with an evaluation statistic. The Bonneville example demonstrates that alternative defensible output channels paired with the same observations can produce similar *R*² values but substantially different NSE values (*R*² ≈ 0.508–0.551; NSE = −2.804, +0.500, and −2.752); <!-- w3_tdgta_off_metrics.json --> DeGray temperature and Columbia dissolved-oxygen comparisons are used only as within-run internal-consistency diagnostics, not as observational skill.

**Contribution 2 (control-state and gated outputs).** We incorporate controller state into the evaluation record when the availability or interpretation of an output channel depends on an internal control rule. In the Bonneville example, the series with NSE = +0.500 is available only when `TDGTA=ON`; disabling the controller removes the controller-specific output but does not delete the underlying physical TDG state, because SYSTDG continues to write the pre-control TDG series. <!-- w3_tdgta_off_metrics.json --> Controller state is therefore treated as part of the evaluation-object definition rather than as evidence that the physical variable itself is absent. DART hourly data show that 21.2% of valid hours in 2016–2025 still exceed 120%; that statistic supports a reachable-range argument and is not an out-of-sample NSE. <!-- w4_cciw_vs_dart.json -->

**Contribution 3 (numerical health).** We define a **numerical health record (NHR)** as an execution-diagnostic component accompanying statistical model assessment. The Long Lake example demonstrates that successful termination can coexist with negative surface-layer-thickness rollbacks to `DLTMIN`; the observed 5/4/1/5 counts under the tested `DLTINTER=ON` schedule knots, compared with 0/0/0/0 under `DLTINTER=OFF`, are used to demonstrate the information added by the NHR rather than to infer a general relationship between timestep size and numerical stability. <!-- nhr_dlt_scan.json -->

**Contribution 4 (assessment protocol and demonstration corpus).** We combine VPR, controller-state provenance, and NHR information in reproducible **run-cards** and apply the protocol to heterogeneous official CE-QUAL-W2 examples as a **demonstration corpus**. The corpus exercises distinct assessment conditions rather than serving as a multi-site validation campaign: Bonneville provides the observation-based skill case; DeGray and Columbia provide internal-consistency diagnostics; Long Lake provides the numerical-health case; and the Columbia SOD calculation is only a magnitude-plausibility check based on parameters transplanted from DeGray, not a Columbia field calibration. We provide `w2eval`, a provenance-aware run-card writer. We do **not** claim a first reproducible validation of CE-QUAL-W2.

The rest of the paper defines an evidence taxonomy and interpretation rules (Sect. 2), states the assessment methods (Sect. 3), describes the demonstration corpus (Sect. 4), reports finding-led results (Sect. 5), discusses conditional comparability and scope limitations (Sect. 6), and concludes (Sect. 7).

## 2 Evidence taxonomy and interpretation rules

We distinguish four kinds of claim that a CE-QUAL-W2 evaluation record may support. Mixing them in a single skill table is a category error.

1. **Observational skill.** Paired model output versus independent field observations under a stated VPR and run configuration. In this paper, only Bonneville TDG versus CCIW occupies this class.
2. **Internal consistency / within-run cross-output diagnostic.** Disagreement (or apparent agreement) among model output channels on the same run when no independent observations exist—not a claim that those channels “should” match. DeGray temperature and Columbia DO metrics are labelled `internal_consistency` in every table, run-card, and caption. They diagnose provenance ambiguity; they do not rank calibration quality.
3. **Numerical health.** Execution diagnostics (especially H1 < 0 → DLTMIN rollback, layer add/subtract counts, exit status versus warning files) that condition whether two skill numbers are like-for-like. Exit code 0 is not a health certificate.
4. **Reproducibility / magnitude plausibility.** Whether an official deck can be executed as distributed, and whether transplanted parameters produce order-of-magnitude-plausible fluxes (Columbia SOD versus the Almeida and Coelho (2025) scan band). Plausibility is not site calibration.

A goodness-of-fit value is not only a property of a model and observations; it is a property of a specified model quantity, observation pairing, processing pathway, run configuration, and metric. This does **not** make cross-study comparison intrinsically invalid; it makes interpretation **conditional** on sufficient alignment of those evaluation conditions.

## 3 Assessment methods

### 3.1 CE-QUAL-W2 output architecture

CE-QUAL-W2 can represent a constituent or state-variable family in several output channels that differ in spatial support, aggregation, derivation, or control state (Cole and Wells, 2003; Wells, 2002). Time-series output (TSR) samples nominated segments, typically at the current surface layer when `ETSR = 0`. Withdrawal output (WDO) writes flow-weighted structure and gate temperatures and constituents. Profile (PRF) and snapshot (SNP) files dump the two-dimensional field. Structure (`two_str*.csv`) and gate (`two_gate*.csv`) files report centerline elevations. Volume-averaged temperature `Tvolavg` shares a TSR file with surface `T2` but is a different spatial operator.

For the Bonneville total-dissolved-gas example, additional TDG representations arise from the withdrawal, SYSTDG, and TDG-target pathways. In `withdrawal.f90`, dissolved N2 and DO are converted to TDG percentage using the model’s Henry-law formulation. Module `systdg.f90` writes native `TDG_TDG` to unit 88888 (`TDG_output.csv`) when SYSTDG is on, independently of the TDG target switch. Module `TDGtarget.f90` is an optimization controller: it reads `w2_TDGtarget.csv` (spill priority `SPPRIOR`, minimum split fraction `SPMINFRAC`, powerhouse maximum `PHMAXFLOW`, iteration count `tsiteration`) and dynamic 115%/120% targets (`TDGdyntarget.csv`), then reallocates flow between spillways and the powerhouse. Its post-control series is written only to `TDGTarget_output.csv`, and only when `TDGTA=ON`.

Accordingly, four distinct TDG evaluation objects can be constructed from a single Bonneville run: Henry-converted WDO at segment 76 (caliber A), the controller file (B), the in-reservoir TSR TDG column at segment 40 (C), and the SYSTDG daily file (S). A, B, C, and S therefore correspond to distinct VPRs and should not be treated as interchangeable observational-skill objects.

### 3.2 Layer add/subtract and H1 < 0 rollback

Layer addition and subtraction are treated here as geometry-management events rather than as truncation-error diagnostics. `layeraddsub.F90` adds a layer when `ZMIN < −0.85 H(KT−1)` (loop recheck −0.80 *H*) and subtracts a layer when `ZMIN > 0.60 H(KT)` and `KT < KTMAX`, with a one-layer special case and a “Low water” warning if `ZMIN > 0.99 H(KT)`. The 0.85/0.80 pair is a hysteresis band. Because these threshold crossings can arise from changes in simulated stage, add/subtract counts are recorded in the NHR as geometry events rather than classified as failures by themselves.

Negative surface-layer thickness is evaluated separately because it activates the model’s timestep-rollback pathway. In `w2_4_win.f90` (autostepping, approximately lines 1415–1424 of the v4.5 source tree used here), if `H1(KT,I) < 0` and `DLT > DLTMIN`, the model writes `w2.wrn` (“Negative surface layer thickness” / “time step reduced to DLTMIN”), sets `CURMAX = DLTMIN`, and `GO TO 220` to recompute the step. Only failure already at `DLTMIN` becomes a fatal `w2.err` (“Unstable water surface elevation”). `endsimulation.F90` prints “Normal termination” when `ERROR_OPEN` is false, and **deletes** `w2.wrn` when `WARNING_OPEN` is false. Consequently, a completed run can return exit code 0 and “Normal termination” while retaining rollback warnings that are not represented by the statistical performance metrics. Snapshot-file “violations” (`NV`) increment on any time-step rollback, including CFL and viscosity limits, and must not be used as a proxy for H1 < 0 counts.

When `DLTINTER=ON`, `update.F90` linearly interpolates `DLTMAX` between schedule knots. Long Lake’s official `w2_con.csv` has six knots; days 30–40 interpolate from the day-30 `DLTMAX` (officially 100 s) to 1800 s at day 40. Consequently, the day-30 DLTMAX value is an interpolation knot rather than a hard timestep cap over days 30–40.

### 3.3 Variable Provenance Record (VPR)

A VPR is the tuple that makes an evaluation object reconstructable by a second analyst:

{output file, column name, segment *I* or mapped station, layer *K* or withdrawal elevation, units, derivation chain, time support (instantaneous / daily mean / snapshot / event log), pairing tolerance}.

Derivation chain distinguishes native TSR, Henry conversion from N2+DO, pre-control SYSTDG writes, and post-control controller writes. Time support and pairing tolerance are part of the object: Bonneville A/C use nearest-neighbour pairing with tolerance 0.05 d; B/S use 0.6 d to match the daily SYSTDG file against hourly CCIW. Changing the tolerance is a different evaluation. To assess sensitivity to the pairing rule, we recomputed metrics from the archived CCIW observations and TDGTA=ON outputs without rerunning W2 (`pairing_tolerance_scan.json`). We scanned nearest-neighbour tolerances of 0.01, 0.02, 0.05, 0.10, and 0.25 d for A/C and 0.25, 0.50, 0.60, 0.75, 1.00, and 1.50 d for B/S. Each tolerance defines a distinct VPR evaluation object; the Table 1 baseline remains A/C = 0.05 d and B/S = 0.6 d. Within this archived-output sensitivity scan, A and C retained negative NSE at every successful tested tolerance, whereas B retained positive NSE; this supports the sign-level qualitative contrast over the tested pairing rules, not robustness to pairing choices in general. C *R*² ranges 0.4502–0.5512 across the A/C grid (more sensitive at tight tolerances) while A is flat at 0.5082; B *R*² ranges 0.5332–0.5417. Paired counts and metrics are listed in Appendix A. The Bonneville multi-channel comparison is therefore an **evaluation-object sensitivity** demonstration (channel identity plus time-support/pairing choices), not a claim that only the output-file label changed while every other pairing choice was held fixed. DeGray and Columbia VPRs are labelled `internal_consistency`; their “reference” series is another model channel, not a field observation.

### 3.4 Controller-conditional evaluation

When an internal control rule can bind, skill is reported **conditional on controller state**, with an explicit reachable range. For Bonneville that means: (i) `TDGTA` ON or OFF; (ii) whether the evaluated file is `TDGTarget_output.csv` (post-control), `TDG_output.csv` (pre-control snapshot), Henry WDO, or TSR; (iii) the fraction of observations that lie outside the controller cap. Same-named column `TDG_TDG` in two files is not the same VPR. A classical “freeze the metric, toggle the process” experiment is impossible on path B, because the metric’s file disappears when the controller is off.

### 3.5 Numerical Health Record (NHR)

An NHR is an **execution-diagnostic record**, not a convergence test or a numerical-stability certificate. It was derived programmatically from `w2.wrn`, `w2.err`, SNP runtime footers, and, where available, TSR timestep records. Recommended fields for this paper:

- negative surface-thickness count and event list (segment, JDAY, DLT at warning, H1, Z);
- add-layer and subtract-layer counts (geometry thresholds; not failures by themselves);
- whether exit 0 / Normal termination masked a DLTMIN rollback;
- `DLTINTER` and the DLTMAX schedule;
- SNP `NV` **separately** from H1 < 0;
- TSR-sampled DLT min/max in a nominated window (a lower bound on DLTMIN occupancy; exact time-at-DLTMIN needs source instrumentation, not done here).

Counting rule used here: each matching `w2.wrn` negative-thickness line is one event (`neg_surface_thickness_count = len(events)`). Same-JDAY repeats are **not** deduplicated; the Table 5 integers are therefore warning-line counts over the completed Long Lake jobs, not unique model days. SNP `NV` remains a separate series and is never folded into that count.

We treat two runs as not like-for-like on skill if one has frequent H1 < 0 rollbacks and the other does not, even if both returned exit 0.

### 3.6 Metrics

For paired series *s* (simulation or alternate channel) and *o* (observation or reference channel), we report Pearson *r* and *R*² = *r*², NSE (Nash and Sutcliffe, 1970), percent bias, MAE, and KGE (Gupta et al., 2009)

\[
\mathrm{KGE}=1-\sqrt{(r-1)^2+(\alpha-1)^2+(\beta-1)^2},\quad
\alpha=\sigma_s/\sigma_o,\quad \beta=\mu_s/\mu_o.
\]

Pearson *r* is invariant under affine maps *s*′ = *a s* + *b* with *a* ≠ 0. Consequently *R*² cannot see α or β. NSE and KGE can. Variable misidentification that stretches or shifts a series while preserving rank correlation is invisible to *R*² by construction. Thus *R*² alone cannot diagnose the variance and bias differences represented by α and β. `w2eval` copies these scores from the archived analysis records and does not reimplement the formulae.

### 3.7 w2eval

`w2eval` is a minimal run-card generator that consumes the archived analysis records and writes the VPR, metrics, and NHR components. Five cards are provided for the Bonneville TDGTA ON/OFF cases, Long Lake DLT/NHR, Columbia DO internal consistency plus SOD magnitude, and DeGray temperature internal consistency. The tool neither launches CE-QUAL-W2 nor recomputes the performance metrics.

### 3.8 Literature-audit methods

Coding followed the archived literature-audit record. The audit population was fixed to the 38 studies selected by Benicio et al. (2024) (Table 1 refs [12]–[14], [18], [21]–[54]). **Full text** covering methods-plus-calibration results was legally obtainable for **9 of 38** papers (23.7%); the remaining 29 were coded from abstracts and the review tables only.

`vpr_reconstruct = yes` is the literature-audit **VPR-core** criterion: from the paper alone (not supplement), a locatable segment or mapped station, a layer or sampling depth, the constituent identity, and the comparison period. It is **weaker** than the full eight-field VPR in Sect. 3.3. An output filename is never required for `yes` in this corpus because none of the 38 provide one. Every coded field uses a three-way transparency rule: **confirmed present**, **confirmed absent** (positively established from accessible material), and **unknown / not verifiable**. Paywalled or abstract-only rows without a usable statement were coded `unknown` and are **never** converted to confirmed absence (`no`). Secondary citations of MAE/RMSE were flagged and not treated as verified primary text. Control-rule coding is `described` / `not_mentioned` / `NA`; none of the 38 is a TDG/SYSTDG paper, because the review query is eutrophication. Claim 2 is therefore **not** extrapolated from those 38 studies; they support only the weaker statement that run state is rarely declared as an evaluation condition. For the review’s Table 2 (*n* = 12), coding follows `table2_r2_is_w2_obs_sim_skill`: **1** confirmed skill, **7** confirmed other objects, **4** unresolved.

### 3.9 DART comparison methods

Hourly Cascade Island records were downloaded from Columbia River DART (Columbia Basin Research, University of Washington; source USACE NWD) for 2011–2025 using the public CSV endpoint with station code `sc=1`. Library `Datetime` hour *h* on date *D* maps to DART `Hour = (h+1)×100` (hour-ending Pacific timestamp minus 1 h), verified on 2011-04-01. Exceedance percentages use hours with non-missing dissolved-gas percent as the denominator; CCIW winters are often missing. Out-of-sample NSE was not computed. <!-- w4_cciw_vs_dart.json -->

---

## 4 Demonstration corpus

Official CE-QUAL-W2 example decks are used here as a heterogeneous **demonstration corpus** for auditing evaluation provenance and numerical health. They are not a multi-site validation campaign and are not presented as “calibration sites.”

All hydrodynamic integrations used the distributed `w2_v455_ifx.exe`. Metrics reported here were recomputed from archived model outputs; no new hydrodynamic integrations were performed for the present analysis.

**Bonneville Dam (skill versus observations).** Official SYSTDG example evaluated under documented `TDGTA=ON` and `TDGTA=OFF` configurations. Control file `TMSTRT = 40544`, `TMEND = 40909` (Excel serial; JDAY 40544 = 2011-01-01, origin 1899-12-30). <!-- w4_cciw_vs_dart.json --> Both integrations reach the prescribed simulation endpoint without a fatal `w2.err`. Observations are the example file `CCIW_TDG_Temp_2011-2015.csv` (Cascade Island tailwater). Valid CCIW TDG does not cover the calendar year: all 1614 paired hours fall in JDAY 40613.583–40681.542 (about 11 March–18 May 2011). <!-- w3_tdgta_off_metrics.json --> The full model period therefore differs from the observation-paired evaluation period reported below.

**DeGray Reservoir (internal consistency, no observations).** Official DeGray sediment-diagenesis example; evaluation window JDAY 64.5–358.7. Searches of v4.5.5 and v5.0 beta example folders found no independent temperature or DO observations. Metrics compare output channels on the same run.

**Columbia Slough Estuary (internal consistency, no observations).** Hydrodynamics and DO under `SED_DIAG=ON`. Official `w2_con.csv` requests sediment diagenesis but the example does not ship `W2_diagenesis.npt`. Parameters were copied from DeGray, with region-2 end segment 31 → 50. That transplant is **not** a Columbia calibration. The series is short: TSR pairing *n* = 116 over JDAY 32–55 (~23 days). A `SED_DIAG=OFF` companion integration was also archived; ON versus OFF DO is a process-switch comparison, not a provenance comparison, and is not used as Contribution 1 evidence.

**Long Lake (numerical health, no observations).** Official DLT schedule (`NDLT = 6`, `DLTMIN = 0.1` s, `DLTINTER=ON`), with a DLTMAX schedule-knot scan at day 30 (20/50/100/200 s × `DLTINTER` ON/OFF). The distribution omits `HabitatFiles/`; without that directory the habitat output path in `w2_habitat.npt` raises Intel Fortran severe (29). Completed scan jobs all reach JDAY 239.943 with exit 0.

---


The cases address complementary assessment questions: Bonneville TDG for observational VPR sensitivity; TDGTA ON/OFF for gated-output semantics; DeGray T and Columbia DO for internal-consistency diagnostics; Long Lake for NHR under exit 0; Columbia SOD for transplanted-parameter magnitude check; and the literature audit for reporting gaps (not a W2 run). Suite inventory appears with Results in Table 3 (Sect. 5.5).

## 5 Results

Results are organized by methodological finding. Reservoir names identify the demonstration, not the claim type.

### 5.1 Variable provenance (observational skill and literature gap)

#### 5.1.1 Bonneville TDG versus CCIW (skill)

Table 1 reports four calibers on the TDGTA=ON run and the same four with TDGTA=OFF, all paired to the same CCIW series (*n* = 1614; JDAY 40613.583–40681.542). <!-- w3_tdgta_off_metrics.json --> Observed TDG ranges from 107.7% to 129.1%; 251 of 1614 paired hours (15.55%) exceed 120%.

**Table 1.** Bonneville TDG calibers versus CCIW observations (*n* = 1614; observational skill). B is the controller-specific series and is absent when `TDGTA=OFF`; S is the SYSTDG pre-control snapshot and is not a substitute for B. Baseline pairing tolerances are 0.05 d for A/C and 0.6 d for B/S (pairing-tolerance sensitivity in Appendix A). <!-- w3_tdgta_off_metrics.json -->

| Run | Caliber | File | *R*² | NSE | KGE | *r* | α | β | PBIAS | MAE | Paired sim max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ON | A | N2+DO Henry, seg. 76 | 0.5082 | −2.8044 | 0.4089 | 0.7129 | 1.5133 | 0.9411 | −5.89% | 6.878 | 121.29% |
| ON | B | `TDGTarget_output.csv` | 0.5332 | +0.5000 | 0.7152 | 0.7302 | 0.9087 | 0.9986 | −0.14% | 2.196 | 120.09% |
| ON | C | TSR seg. 40 TDG | 0.5512 | −2.7516 | 0.3854 | 0.7424 | 1.5549 | 0.9414 | −5.86% | 6.840 | 123.40% |
| ON | S | `TDG_output.csv` | 0.5614 | +0.3573 | 0.7057 | 0.7492 | 1.1539 | 1.0072 | +0.72% | 2.746 | 127.49% |
| OFF | A | N2+DO Henry, seg. 76 | 0.5212 | −2.3371 | 0.1603 | 0.7219 | 1.7909 | 0.9528 | −4.72% | 5.671 | 123.99% |
| OFF | B | `TDGTarget_output.csv` | — | file absent | — | — | — | — | — | — | — |
| OFF | C | TSR seg. 40 TDG | 0.5511 | −2.7522 | 0.3855 | 0.7424 | 1.5548 | 0.9414 | −5.86% | 6.841 | 123.42% |
| OFF | S | `TDG_output.csv` | 0.5614 | +0.3573 | 0.7057 | 0.7492 | 1.1539 | 1.0072 | +0.72% | 2.746 | 127.49% |

Three facts follow from the ON block alone.

1. Correlation barely moves (*r* = 0.713 / 0.730 / 0.742 for A/B/C), so *R*² occupies 0.508–0.551. Under the review-table convention all three would be “moderate agreement ≈ 0.5”. NSE is −2.804, +0.500, and −2.752: A and C are worse than forecasting the observed mean. The largest *R*² (C, 0.5512) is among the worst NSE values.

2. The damage is in KGE’s α and β, not in *r*. A and C inflate variance (α = 1.513 and 1.555) and sit ~6% low (β = 0.941). B has α = 0.909 and β = 0.999. Ordinary least-squares slopes of sim on obs are 1.0788, 0.6636, and 1.1544 for A, B, and C. <!-- w3_tdgta_off_metrics.json -->

3. Caliber A follows the Henry-law conversion implemented in `withdrawal.f90` and therefore represents a technically plausible output-selection pathway in the absence of an explicit VPR. The model itself emits at least three TDG number streams.

Figure 3 decomposes KGE into *r*, α, and β and is the glance test for Contribution 1. Figure 1 overlays the ON/OFF series on CCIW and the controller target band. Figure 2 shows 1:1 scatter.

**Figure 1.** Bonneville TDG time series for calibers A, B, C, and S with `TDGTA` ON and OFF, CCIW observations, and the 120% controller target. Observational comparison with CCIW over JDAY 40613.583–40681.542 (*n* = 1614); not an internal-consistency panel.

**Figure 2.** One-to-one comparison of Bonneville TDG calibers A, B, and C against CCIW over the paired evaluation window (*n* = 1614; observational skill). Ordinary-least-squares slopes for the `TDGTA=ON` A/B/C series are 1.079, 0.664, and 1.154, respectively.

**Figure 3.** KGE components (*r*, α, β) for Bonneville ON/OFF TDG calibers versus CCIW (*n* = 1614; observational skill). DeGray temperature and Columbia DO companion panels (Supporting Information) are internal-consistency diagnostics only; primary aligned sample sizes are *n* = 2943 (DeGray) and *n* = 116 (Columbia TSR station pairs).

#### 5.1.2 Literature audit (motivation, not a W2 run)

**Table 2.** Structured literature-gap audit of the 38 studies selected by Benicio et al. (2024). Among the 12 *R*² entries in the review summary table, **1** is confirmed W2↔observation skill, **7** represent other evaluation objects, and **4** remain unresolved. This table audits reporting provenance and is not a pooled ranking of CE-QUAL-W2 skill. <!-- w5_lit_audit_summary.json -->

| Item | Count | Share |
|---|---:|---:|
| Full text (methods + calibration results) | 9 | 23.7% |
| VPR-core reconstructable from the paper (`yes`) | 2 | 5.3% |
| VPR `partial` / `no` / `unknown` | 6 / 11 / 19 | 15.8% / 28.9% / 50.0% |
| W2 output file or column named | 0 | 0% |
| Location to segment *I* or mapped station | 3 | 7.9% |
| Reports *R*² (any model) | 11 | 28.9% |
| Reports NSE / KGE / PBIAS | 2 / 0 / 1 | 5.3% / 0% / 2.6% |
| *R*² without NSE | 9 of 11 | 81.8% of *R*² papers |
| Open W2 inputs or code | 1 | 2.6% |
| Table 2 *R*² object coding (W2↔obs skill / other / unresolved) | 1 / 7 / 4 of 12 | Lima Neto 0.32 is the confirmed skill cell |

The two reconstructable papers are Lima Neto (2023) (outlet = segment 31, second cell; inlet = segment 2, second cell; still no output filename) and Chang et al. (2015) (Station 1 → segment 3 surface; not in the review’s Table 2). We do **not** claim that all 38 papers report only *R*²: 11 report *R*², and many others report AME/RMSE or nothing that we could verify. We do **not** treat Table 2’s 0.32 and 0.977 as a skill gap: 0.977 is a load-reduction response curve.

Limitation, to be read with the counts: 19/38 VPR codes are `unknown` because full text was not obtained. Paywalled papers might document provenance more carefully. Open-access Table 2 entries already suffice to show that the summary table mixes mathematical objects. Unknowns stay unknown.

### 5.2 Control-state dependence and gated outputs

#### 5.2.1 Gated file versus pre-control snapshot

On TDGTA=ON, caliber B is the only series with NSE = +0.500, β = 0.9986, PBIAS = −0.14%, and paired maximum 120.09%. Raw B maximum is 120.1%. <!-- w3_tdgta_off_metrics.json --> That file is not written when `TDGTA=OFF`; `TDGTarget_warning.opt` disappears with it. Standard WDO, TSR, and `TDG_output.csv` remain.

`TDG_output.csv` is produced by SYSTDG (`INPUT_SYSTDG` opens unit 88888) regardless of TDGTA. Source order in `TDGtarget.f90` / `hydroinout.F90` / `systdg.f90` is: the controller calls `SYSTDG_TDG` **before** reallocating; that first call of the day writes unit 88888 and advances `NXTSPLIT3`; later calls the same day do not rewrite the daily row. Consequently ON and OFF `TDG_output.csv` are identical (365 days, MAE = 0, max |Δ| = 0, raw max 131.7% both). The same file versus `TDGTarget_output.csv` has MAE = 1.7073, max |Δ| = 11.743, raw maxima 131.7% versus 120.1%. Column name `TDG_TDG` is shared; the evaluation object is not.

These results establish three distinctions. The skill-best, β ≈ 1, 120.1%-capped series exists only in the controller-gated file `TDGTarget_output.csv`; when `TDGTA` is off that file is absent, so a freeze-the-metric / toggle-the-controller experiment cannot be performed on path B. Disabling the controller does not remove the physical TDG state, because SYSTDG continues to write the pre-control snapshot to `TDG_output.csv`, which cannot replace B. The 120% bound is a property of the controller pathway rather than a ceiling of the SYSTDG TDG formulation (model hard cap 145%); the observed paired maximum is 129.1%, and 15.55% of paired hours exceed 120% and are structurally unreachable on B.

Turning the controller off does **not** make A a usable forecast: OFF A NSE = −2.3371 (still far below a mean forecast), KGE falls from 0.4089 to 0.1603 because α inflates from 1.513 to 1.791. OFF S NSE = +0.3573, paired max 127.49%, raw max 131.7%: it can exceed 120% but the paired series does not reach observed 129.1%. In-reservoir TSR (C) is almost unaffected (ON versus OFF MAE = 0.0075 on 6211 in-file points). Henry WDO (A) does move (MAE = 0.6951, OFF raw max 129.04%).

#### 5.2.2 DART check, exceedance, and 2011 spill (not out-of-sample NSE)

Library CCIW versus DART hourly TDG, 2011–2015, both valid: *n* = 17805, MAE = 0.026537%, RMSE = 0.04124%, |Δ| ≤ 0.051 match rate = 0.994945. <!-- w4_cciw_vs_dart.json --> Five hours differ by more than 1% (max |Δ| = 1.9), almost all in 2011–2012; 2013–2015 match at 1.0 within 0.05. The library series is consistent with rounded DART values. We find no evidence that the example observations were materially rewritten.

Among DART hours with non-missing TDG, 14.6842% exceed 120% in 2011–2015 (valid hours *n* = 17924) and 21.2% exceed 120% in 2016–2025 (*n* = 40434). Annual fractions are not a stationary 15%: 2015 has 0% of valid hours >120% (annual max 118.97%); 2017 has 46.9214% (annual max 131.38%). The cap problem does not age out of the record. **These percentages are not forecast skill.** The reproduced model’s `TMEND = 40909` covers about 2011 only; out-of-sample NSE was not computed.

2011 daily spill (365 paired days). Input `QGT` versus DART spill: *r* = 0.868638. Controller (`TDGTarget_output`) versus DART spill: *r* = 0.237349. Controller flag `C = R` on 116 days (U = 0, blank = 249). On reallocation days, mean DART spill is 173.8573 kcfs and mean controller spill is 39.2308 kcfs (*r* = −0.596447). <!-- w4_cciw_vs_dart.json --> The ON run’s low bias and 120% cap are partly the result of operating a different spill programme than 2011 reality, not merely of a better physical TDG closure.

**Figure 5.** Distribution of paired CCIW TDG observations over JDAY 40613.583–40681.542 (*n* = 1614) relative to the 120% controller cap. Of the paired observations, **15.55% (251/1614)** exceed 120% and therefore lie outside the reachable range of gated B. Annual 2011–2025 exceedance frequencies (Supporting Information) are descriptive observation statistics only; no NSE is computed for 2016–2025.

**Figure 8.** Comparison of 2011 Bonneville spill from QGT, the TDGTA-controlled series, and DART over 365 paired days. On controller-reallocation days, mean DART and TDGTA spill are 173.86 and 39.23 kcfs, respectively. Descriptive controller/spill context; not out-of-sample TDG skill.

Library versus DART identity plots:, (exist).

### 5.3 Internal consistency (negative controls)

#### 5.3.1 DeGray temperature (internal consistency)

No independent observations. Table 4 (upper block) compares channels on one run (*n* = 2943 unless noted; JDAY 64.5–358.7). <!-- w1_provenance_metrics.json -->

Same TSR file, surface `T2(C)` versus volume-average `Tvolavg(C)`: *R*² = 0.9027, NSE = −0.5855, KGE = 0.2354, *r* = 0.9501, α = 0.3456, β = 0.6077. A review table would call *R*² = 0.90 excellent. NSE says the volume-average is worse than using the surface-series mean as a predictor. Volume averaging compresses variance by about 65% (α = 0.35) and lowers the mean by 39% (β = 0.61). *R*² cannot see that affine-scale error.

Surface T2 versus WDO mixed withdrawal temperature: *R*² = 0.5293, NSE = −0.3653. Structure centerline 115 m versus gate centerline 120 m: *R*² = 0.5336, NSE = −6.5825, α = 2.3772, β = 1.4882. The two *R*² values differ by 0.004 and sit inside the Bonneville TDG *R*² band; NSE differs by six units. Reporting only *R*² would describe two “outflow temperatures” as equally moderate.

Gate 120 m versus surface T2 is *not* a counterexample to write as “gates equal the surface.” NSE = 0.9993 because this gate centerline (120 m) is near the water surface (ELWS ≈ 123.8 m on this deck). WDO is essentially the structure temperature (WDO versus STR: *R*² = 1.0000). A VPR that omits elevation has already changed the predictand. Deep-layer mistakes *do* collapse *R*²: PRF segment 26 bottom versus TSR surface T2 has *R*² = 0.0572, NSE = −2.9461 (*n* = 296). The *R*² blind spot is for correlated-but-wrong-scale channels (volume average, the other outlet, another segment), not for every wrong layer.

Parser self-checks: SNP surface versus TSR T2, NSE = 1.0000 at 47 snapshots; PRF segment 26 surface versus TSR segment 31 surface, NSE = 0.9987. Cross-file surface channels agree; the disagreements are layer, outlet, and averaging operator.

**Figure D1.** DeGray surface T2, volume-average temperature, WDO, structure, and gate temperatures on the same run (**internal consistency only**—no field observations; primary aligned *n* = 2943).

**Figure D2.** One-to-one comparisons among DeGray temperature output channels (**internal consistency**; not observational skill; primary *n* = 2943).

**Figure D3.** *R*² versus NSE for DeGray temperature channel pairs (**internal consistency**; primary *n* = 2943).

#### 5.3.2 Columbia DO (internal consistency)

No independent observations. TSR segments 45, 49, and 33, `SED_DIAG=ON`, *n* = 116, JDAY 32–55. <!-- w1_provenance_metrics.json -->

| Pair | *R*² | NSE | KGE | *r* | α | β |
|---|---:|---:|---:|---:|---:|---:|
| I=45 vs I=49 | 0.2071 | −4.4940 | 0.1665 | 0.4551 | 0.6816 | 1.5444 |
| I=45 vs I=33 | 0.3275 | −2.2675 | 0.3794 | 0.5723 | 1.2585 | 1.3679 |
| I=49 vs I=33 | 0.6505 | −1.4821 | 0.1243 | 0.8065 | 1.8464 | 0.8858 |
| SNP I=45 surface vs bottom (*n* = 24) | 0.9321 | 0.9072 | 0.9362 | 0.9655 | 0.9713 | 0.9547 |

All three station pairs have NSE < −1.48. Ranking by *R*² would select I=49 versus I=33 as best; that pair still has negative NSE and α = 1.85. On the shallow tidal slough, SNP surface versus bottom NSE = 0.91: **wrong station is more dangerous than wrong layer**. The Columbia *R*² band (0.21–0.65) is wider than Bonneville’s 0.04, as expected for 23 tidal days. Generalization of Contribution 1 rests primarily on DeGray (*n* = 2943) plus Bonneville skill, with Columbia as a station-ambiguity illustration.

**Figure C1.** Columbia TSR dissolved oxygen at segments I=45/49/33 over the aligned period (*n* = 116; **internal consistency only**—no field observations).

**Figure C2.** Columbia DO channel comparisons as scatter and *R*²–NSE diagnostics (TSR pairs *n* = 116; **internal consistency**; not observational skill). 

**Figure 4.** *R*² versus NSE with evidence classes kept separate: **(a)** Bonneville `TDGTA=ON` A/B/C versus CCIW (*n* = 1614; observational skill); **(b)** DeGray temperature (*n* = 2943 for primary pairs) and Columbia DO (*n* = 116 for TSR station pairs), both internal consistency only; **(c)** the 12 *R*² entries from the 38-study literature audit, coded **1 / 7 / 4** (confirmed W2↔obs / other objects / unresolved). NSE was not available for the literature-audit entries and is not inferred. Panels (a) and (b) must not be pooled as a single skill comparison.

**Table 4.** Primary internal-consistency pairs. Kind = `internal_consistency`. Do not quote these NSE/KGE values as calibration skill. <!-- w1_provenance_metrics.json -->

| Case | Pair | *n* | *R*² | NSE | KGE | *r* | α | β |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| DeGray T | T2 vs Tvolavg | 2943 | 0.9027 | −0.5855 | 0.2354 | 0.9501 | 0.3456 | 0.6077 |
| DeGray T | T2 vs WDO mix | 2943 | 0.5293 | −0.3653 | 0.2790 | 0.7275 | 0.4204 | 0.6688 |
| DeGray T | STR 115 m vs GATE 120 m | 2943 | 0.5336 | −6.5825 | −0.4858 | 0.7305 | 2.3772 | 1.4882 |
| DeGray T | T2 vs GATE 120 m | 2943 | 0.9995 | 0.9993 | 0.9943 | 0.9998 | 0.9982 | 0.9945 |
| DeGray T | T2 vs PRF I=26 bottom | 296 | 0.0572 | −2.9461 | −0.3717 | 0.2392 | 0.0566 | 0.3575 |
| Columbia DO | TSR I=45 vs I=49 | 116 | 0.2071 | −4.4940 | 0.1665 | 0.4551 | 0.6816 | 1.5444 |
| Columbia DO | TSR I=45 vs I=33 | 116 | 0.3275 | −2.2675 | 0.3794 | 0.5723 | 1.2585 | 1.3679 |
| Columbia DO | TSR I=49 vs I=33 | 116 | 0.6505 | −1.4821 | 0.1243 | 0.8065 | 1.8464 | 0.8858 |
| Columbia DO | SNP I=45 sfc vs bot | 24 | 0.9321 | 0.9072 | 0.9362 | 0.9655 | 0.9713 | 0.9547 |

---

### 5.4 Numerical health

Completed runs outside Long Lake have **zero** H1 < 0 events: DeGray (no `w2.wrn`), Columbia diagnostic (add = 7, sub = 8), Bonneville ON (add = 42, sub = 43, NV = 7495 / NIT = 438555 = 1.71%), Bonneville OFF (add = 48, sub = 49). <!-- nhr_existing_runs.json --> Layer add/subtract at Bonneville and Columbia is seasonal or tidal stage crossing `layeraddsub` thresholds, not a failure.

Long Lake is the exception. Official `DLTINTER=ON`, day-30 knot 100 s: one negative-thickness event (segment 3, JDAY 31.936, H1 = −27.144 m, DLT = 74.022 s → DLTMIN 0.1 s), add = 3, sub = 3, SNP NV = 2395 (1.06% of NIT = 226804), Normal termination, exit 0, `exit_zero_masks_rollback = true`. <!-- nhr_dlt_scan.json -->

**Table 5.** Numerical-health diagnostic for eight Long Lake DLTMAX × `DLTINTER` configurations (day-30 schedule knots; DLTF = 0.9). All jobs complete at JDAY 239.943 with exit 0 and add/sub = 3/3. Negative-thickness warning counts are 5/4/1/5 for `DLTINTER=ON` at 20/50/100/200 s and 0/0/0/0 for `DLTINTER=OFF`. Columbia DLTMAX 120/360/720 s (`DLTINTER=OFF`): 0/0/0. NHR diagnostic only—not observational skill and not a universal timestep–stability law. <!-- nhr_dlt_scan.json -->

| DLTMAX at JDAY 30 | DLTINTER=ON (official interpolation toward 1800 s) | DLTINTER=OFF (true window cap) |
|---:|---:|---:|
| 20 s | 5 | 0 |
| 50 s | 4 | 0 |
| 100 s (official) | 1 | 0 |
| 200 s | 5 | 0 |

Under `DLTINTER=ON`, window (JDAY 30–40) TSR-sampled DLT at the “20 s” knot still reaches 231.096 s because the day-40 knot remains 1800 s. Negative-thickness events at that knot occur at DLT 240, 89, 214, 188, and 233 s—not at 20 s. The deepest recorded H1 in the scan is −113.522 m (ON, 50 s knot, JDAY 32.225). Counts 5/4/1/5 are non-monotonic; the official 100 s knot is the valley. That statement is about **interpolation knots**, not about a hard DLTMAX inside the window.

Under `DLTINTER=OFF`, window DLT equals the cap at 20/50/100 s (200 s window 109.497–200 s) and negative-thickness counts are 0/0/0/0. The same geometry thresholds, with a true time-step cap, eliminate H1 < 0. Therefore “reducing the time step makes the run less stable” is **not** a general conclusion.

SNP `NV` is a different series. INTER OFF / 20 s: NV = 16803 (7.75% of NIT = 216840) and **zero** negative-thickness events. Switching interpolation off increases CFL-type violations while removing geometric H1 < 0. An NHR that folded NV and H1 < 0 into one “unhealthiness” score would get the diagnosis backwards.

Columbia’s smaller scan (official already `NDLT=1`, `DLTINTER=OFF`, DLTMAX 360 s) at 120/360/720 s: negative thickness 0/0/0, add/sub 7/8 at all three. Layer-event counts are insensitive to DLTMAX on this deck. H1 < 0 non-monotonicity is not a cross-case law. Sample size for negative thickness is **one waterbody** (Long Lake).

**Figure 6.** Long Lake numerical-health scan: negative surface-layer-thickness warning counts versus the DLTMAX schedule knot at JDAY 30. Counts are **5/4/1/5** under `DLTINTER=ON` and **0/0/0/0** under `DLTINTER=OFF`. Under interpolation the horizontal axis is a schedule knot, not the realized timestep (e.g. the nominal 20 s knot reaches TSR-sampled window maximum DLT = 231.096 s). Counts are warning-line events, not unique model days. Motivates NHR reporting; does not establish a universal timestep–stability relationship.

### 5.5 Reproducibility audit and run-card implementation

**Table 3.** Official example suites included in the audit (v4.5.5 eight folders + v5.0 beta nine folders = 17). Execution outcomes are reported only for Bonneville, Columbia, DeGray, and Long Lake; the remaining entries document example availability and were not treated as independent run audits.

| Suite | Example folder | Field observations in the distributed deck | Execution status in the present audit |
|---|---|---|---|
| v4.5.5 | BonnevilleDam with TDG computed using SYSTDG | CCIW TDG/temperature (shared with v5 Bonneville_TDG) | None required to start; TDGTA default ON |
| v4.5.5 | Columbia Slough Estuary | None found | `SED_DIAG=ON` without `W2_diagenesis.npt` |
| v4.5.5 | DeGray Reservoir with sediment diagenesis and vertical algae migration | None found | Completed after using the shipped diagenesis file |
| v4.5.5 | Long Lake | None found | Missing `HabitatFiles/` → forrtl 29 |
| v4.5.5 | Detroit Reservoir; MultipleWaterBodyCascade; Particle Tracking in Reservoir; Spokane River | Not the Bonneville CCIW file; not used as skill cases here | Not independently completed for this paper |
| v5.0 beta | Bonneville_TDG | `CCIW_TDG_Temp_2011-2015.csv` | Only example with field observations among the 17 |
| v5.0 beta | Columbia Slough Estuary; DeGray; Long Lake | None found in those folders | Same HabitatFiles / diagenesis issues as v4.5.5 counterparts |
| v5.0 beta | DetroitReservoir; LMNR_ORGC; MultipleWaterBodyCascade; Particle Tracking in Reservoir; Spokane River | Not used as skill cases here | Not independently completed for this paper |

The integrations analysed here used the distributed CE-QUAL-W2 v4.5.5 Windows executable `w2_v455_ifx.exe`. The executable itself is not redistributed with the manuscript repository; model source and executable availability follow the upstream CE-QUAL-W2 distribution.

#### 5.5.1 Transplanted-parameter SOD magnitude check

Columbia SOD, after the DeGray-template transplant, is an order-of-magnitude check against the 0.5–3.0 g O₂ m⁻² d⁻¹ range examined by Almeida and Coelho (2025); that published Portuguese-reservoir experiment is used as a magnitude reference and not as a global ecological range or a Columbia calibration. Wet cells (SOD > 0), instantaneous, JDAY ≥ 33 (spin-up row at JDAY 32 dropped): *n* = 1081, mean = 0.8762, median = 0.8082, min = 0.1349, max = 1.6761; 968/1081 (0.8955) lie in 0.5–3.0; 0.1045 lie below 0.5; **no point exceeds 3.0**. <!-- w7_columbia_sod_vs_almeida.json --> Last-day wet mean 0.7752 g O₂ m⁻² d⁻¹. CSOD mean 0.8034, NSOD mean 0.0727. This is **not** a Columbia calibration and supports **no** water-quality scenario inference. The comparison is limited to a magnitude-plausibility check and provides no evidence of Columbia-specific calibration.

**Figure 7.** Schematic three-block evaluation record (VPR, performance statistics, and NHR) from the run-card implementation. *R*², NSE, and KGE are downstream statistics on a defined evaluation object, not an additional scientific pillar.

**Figure S1.** Columbia wet-cell sediment oxygen demand for JDAY ≥ 33 (*n* = 1081) relative to the 0.5–3.0 g O₂ m⁻² d⁻¹ comparison band. Parameters were transplanted from the DeGray template; magnitude-plausibility check only—not Columbia field calibration.


## 6 Discussion

### 6.1 Why *R*² alone cannot establish provenance equivalence

Bennett et al. (2013) summarize evaluation practice as requiring transparency about what was compared and how. Gupta et al. (2009) show why correlation-based scores can remain high while variability and bias fail. The Bonneville and internal-consistency demonstrations instantiate both points for CE-QUAL-W2 output architecture.

Let *s* be a simulated (or alternate-channel) series and *s*′ = *a s* + *b* with *a* ≠ 0. Pearson *r*(*s*′, *o*) = sign(*a*) *r*(*s*, *o*), so *R*² = *r*² is unchanged. The KGE components α′ = |*a*| σ_s / σ_o and β′ = (*a* μ_s + *b*) / μ_o generally change, as does NSE. Volume averaging (DeGray Tvolavg), a 120% controller cap (Bonneville B), and a different tidal segment (Columbia I=49 versus I=33) are all approximately affine or variance-scaling operations relative to a reference channel. A literature table that records only *R*² is structurally unable to detect them. That is why 9 of 11 papers in the 38-study corpus that report *R*² omit NSE, and why KGE is entirely absent: the prevalent reporting pattern therefore provides limited information on variance and bias errors.

We are not arguing that *R*² is useless. We are arguing that it is not a sufficient statistic for “how well W2 was calibrated”, and that it is the wrong axis for a cross-application ranking. α/β/NSE likewise do not **prove** provenance; they only expose bias and scale mismatches that *R*² can conceal.

### 6.2 Scope and interpretation limits

The general principle that metrics depend on the evaluation protocol is not new (Bennett et al., 2013). The contribution here is operational for CE-QUAL-W2: three concrete reporting elements (VPR, controller-conditional evaluation, NHR) plus W2-specific examples showing how output provenance, controller gating, and internal numerical events change the interpretation of otherwise conventional goodness-of-fit numbers.

The demonstration corpus exercises distinct failure modes rather than validating a single three-part framework across all 17 official examples. Bonneville supplies the principal observation-based skill contrast; DeGray and Columbia provide within-run internal-consistency diagnostics because their official decks do not include the independent observations required for observational-skill evaluation; Long Lake informs NHR existence under exit 0; SOD is a transplanted-parameter plausibility check; Table 3 cells outside those decks are inventory facts, not independent validation runs.

Caliber A follows the Henry conversion in `withdrawal.f90`; caliber C is a TSR column named TDG; caliber B exists only with the controller on. Among 38 eutrophication papers, a W2 output file or column name was confirmed in 0/38, and a paper-level **VPR-core** criterion is met in 2/38; unresolved rows remain `unknown`. Undetectability of output-channel identity in the published literature is itself a finding.

The Long Lake scan demonstrates that exit status alone can omit relevant numerical-health information. The observed 5/4/1/5 pattern is specific to the tested `DLTINTER=ON` schedule knots and does not establish a general timestep–stability law; `DLTINTER=OFF` yields 0/0/0/0, and Columbia’s smaller DLTMAX scan remains 0/0/0. Disabling `TDGTA` removes the controller-specific output file, not the underlying physical TDG variable; SYSTDG still writes `TDG_output.csv`, and ON ≡ OFF on that file (MAE = 0).

The study does not estimate out-of-sample NSE for 2016–2025 because the reproduced simulation terminates near 2011; the later observations are used solely to characterize TDG exceedance frequency. Cross-version skill differences between v4.5.5 and v5.0 beta are outside the scope of this study. The fraction of simulated time spent at `DLTMIN` is not quantified because this would require additional source-level instrumentation. Columbia SOD parameters were transplanted from DeGray: 89.55% of wet cells fall in the Almeida and Coelho (2025) 0.5–3.0 g O₂ m⁻² d⁻¹ scan; none exceed 3.0. That is a sanity check on a missing example file, not a site calibration. Full-text availability for 9/38 papers limits precision on `unknown` rows but does not reverse the Table 2 object-mixing result among coded entries. VPR / controller-conditional evaluation / NHR are a **reporting recommendation** motivated by the demonstrated failure modes, not a decree of regulatory sufficiency for every W2 application.

### 6.3 Relation to Almeida and Coelho (2025)

Almeida and Coelho (2025) is both a journal precedent (GMD accepts open, reproducible W2 evaluation) and an independent SOD magnitude anchor. Their article type evaluates sediment-diagenesis **process options**; ours is complementary: an auditable assessment layer **under** such performance statistics (Methods for assessment of models). Our Columbia mean 0.8762 g O₂ m⁻² d⁻¹ lies below their sediment-diagenesis best mean (1.07) and inside their 0.5–3.0 scan. We use that fact only as listed in Sect. 5.5. A formal sensitivity analysis of the transplanted diagenesis parameters would constitute a separate investigation and is not inferred from the present magnitude check; 0.876 is not Columbia’s true SOD.

---

## 7 Conclusions

Goodness-of-fit values reported for different CE-QUAL-W2 applications should be treated as conditionally comparable: like-for-like comparison requires sufficient information on variable provenance, controller state, and numerical health.

1. **Variable provenance.** Same Bonneville run, same CCIW, *n* = 1614: *R*² stays in 0.5082–0.5512 while NSE is −2.8044, +0.5000, and −2.7516. <!-- w3_tdgta_off_metrics.json --> DeGray and Columbia reproduce the *R*²-blind / αβ-visible pattern as internal consistency, not as field skill. In the 38-paper eutrophication corpus, **VPR-core** is reconstructable in 2/38 studies and a W2 output file or column is named in 0/38; Table-2 object coding of the review’s twelve *R*² entries is **1 confirmed skill / 7 confirmed other objects / 4 unresolved**. <!-- w5_lit_audit_summary.json --> Pairing-tolerance scans of archived ON outputs (Appendix A) keep A/C NSE negative and B NSE positive across the tested grids without changing Table 1 baselines. <!-- pairing_tolerance_scan.json -->

2. **Control-state / gated outputs.** The skill-best Bonneville series lives in `TDGTarget_output.csv` and vanishes when `TDGTA=OFF`. `TDG_output.csv` is a pre-control snapshot (ON/OFF MAE = 0) and is not B. **15.55% (251/1614)** of paired observations exceed the controller cap. <!-- w3_tdgta_off_metrics.json --> DART shows the example observations are intact and that >120% hours remain common in 2016–2025; those years have no model NSE in this study. <!-- w4_cciw_vs_dart.json -->

3. **Numerical health.** Exit 0 can mask H1 < 0 → DLTMIN rollback. Counts 5/4/1/5 are a Long Lake, `DLTINTER=ON` knot result; `DLTINTER=OFF` is all zeros; H1 < 0 was not observed at completed Bonneville, Columbia, or DeGray runs. Report NHR. The Long Lake result should not be generalized into a monotonic timestep–stability relationship.

4. **Protocol.** Evaluate W2 with a VPR, a controller-conditional statement including reachable range, and an NHR. `w2eval` writes those three blocks from archived analysis records. These are recommended reporting elements, not a claim that the present cases prove regulatory sufficiency for every application. Official examples, as distributed, cannot support a calibration claim except at Bonneville: only that deck includes observations, Long Lake is missing `HabitatFiles/`, and Columbia diagenesis parameters used here are a DeGray transplant.

Until those practices are standard, a table of *R*² values across CE-QUAL-W2 studies should not be assumed to rank like-for-like evaluation objects.

---

## 8 Code and data availability

The public development repository for this study is https://github.com/Coucou2016/20260810-CE-QUAL-W2. Paper-facing analysis records are under `06_PAPER/analysis/`, and the run-card implementation and example cards are under `06_PAPER/w2eval/`. Reproducibility utilities used for the reported analyses are provided under `00_INDEX/`. Archived model outputs used to recompute metrics are retained under `05_REPRO_RUNS/` where redistribution is permitted. Observation extracts used here include the official Bonneville CCIW example series and DART hourly Cascade Island downloads under `06_PAPER/data/dart_cciw/`.

A frozen persistent archive of the paper-relevant code and data is pending. Zenodo DOI: **待补充**. GitHub alone is not a substitute for a persistent archive under the GMD code and data policy (https://www.geoscientific-model-development.net/policies/code_and_data_policy.html).

The CE-QUAL-W2 executable is not redistributed in this repository and should be obtained from the upstream CE-QUAL-W2 distribution. Any artefacts that cannot be redistributed will be identified with their access source and restriction in the archived release. Line citations to model source (`w2_4_win.f90`, `layeraddsub.F90`, `update.F90`, `TDGtarget.f90`, `systdg.f90`, `withdrawal.f90`, `endsimulation.F90`) refer to the v4.5 source tree used for this study.

DART data citation: Columbia River DART, Columbia Basin Research, University of Washington, Hourly Water Quality Measurements, https://cbr.washington.edu/dart/query/wqm_hourly (downloaded 2026-08-15). Almeida and Coelho (2025) reproduction package: https://doi.org/10.5281/zenodo.15775127.

---

## Appendix A: Pairing-tolerance scan (no W2 rerun)

Nearest-neighbour pairing of archived CCIW observations to TDGTA=ON Bonneville outputs. Each row is a distinct VPR evaluation object. Baseline rows match Table 1. Source analysis record: `pairing_tolerance_scan.json` in the accompanying repository.

| Caliber | Tolerance (d) | *n* | *R*² | NSE | Baseline | Status |
|---|---:|---:|---:|---:|:---:|---|
| A | 0.01 | 1614 | 0.5082 | −2.8044 |  | ok |
| A | 0.02 | 1614 | 0.5082 | −2.8044 |  | ok |
| A | 0.05 | 1614 | 0.5082 | −2.8044 | yes | ok |
| A | 0.10 | 1614 | 0.5082 | −2.8044 |  | ok |
| A | 0.25 | 1614 | 0.5082 | −2.8044 |  | ok |
| C | 0.01 | 1157 | 0.4502 | −3.8076 |  | ok |
| C | 0.02 | 1614 | 0.5512 | −2.7516 |  | ok |
| C | 0.05 | 1614 | 0.5512 | −2.7516 | yes | ok |
| C | 0.10 | 1614 | 0.5512 | −2.7516 |  | ok |
| C | 0.25 | 1614 | 0.5512 | −2.7516 |  | ok |
| B | 0.25 | 875 | 0.5417 | +0.5211 |  | ok |
| B | 0.50 | 1614 | 0.5332 | +0.5000 |  | ok |
| B | 0.60 | 1614 | 0.5332 | +0.5000 | yes | ok |
| B | 0.75 | 1614 | 0.5332 | +0.5000 |  | ok |
| B | 1.00 | 1614 | 0.5332 | +0.5000 |  | ok |
| B | 1.50 | 1614 | 0.5332 | +0.5000 |  | ok |
| S | 0.25 | 875 | 0.5689 | +0.3924 |  | ok |
| S | 0.50 | 1614 | 0.5614 | +0.3573 |  | ok |
| S | 0.60 | 1614 | 0.5614 | +0.3573 | yes | ok |
| S | 0.75 | 1614 | 0.5614 | +0.3573 |  | ok |
| S | 1.00 | 1614 | 0.5614 | +0.3573 |  | ok |
| S | 1.50 | 1614 | 0.5614 | +0.3573 |  | ok |

---

## Author contributions (CRediT-style; names 待补充)

- Conceptualization; Methodology; Software; Formal analysis; Investigation; Data curation; Writing — original draft; Writing — review & editing: project authors (to be named).
- Resources (model code and example decks): Cole, Wells, and the CE-QUAL-W2 community.
- Resources (observations): USACE NWD via DART and the official Bonneville example.

## Competing interests

The authors declare that they have no conflict of interest.

## Acknowledgements

CE-QUAL-W2 example decks and source are distributed by ERDC / Portland State University. DART is operated by Columbia Basin Research, University of Washington.

---

## References

Bennett, N. D., Croke, B. F. W., Guariso, G., Guillaume, J. H. A., Hamilton, S. H., Jakeman, A. J., Marsili-Libelli, S., Newham, L. T. H., Norton, J. P., Perrin, C., Pierce, S. A., Robson, B., Seppelt, R., Voinov, A. A., Fath, B. D., and Andreassian, V.: Characterising performance of environmental models, Environ. Model. Softw., 40, 1–20, https://doi.org/10.1016/j.envsoft.2012.09.011, 2013.

Almeida, M. and Coelho, P.: Evaluating the performance of CE-QUAL-W2 version 4.5 sediment diagenesis model, Geosci. Model Dev., 18, 6135–6165, https://doi.org/10.5194/gmd-18-6135-2025, 2025.

Benicio, S. H. M., Basso, R. E., and Formiga, K. T. M.: Global applications of the CE-QUAL-W2 model in reservoir eutrophication: a systematic review and perspectives for Brazil, Water, 16, 3556, https://doi.org/10.3390/w16243556, 2024.

Chang, C.-H., Cai, L.-Y., Lin, T.-F., Chung, C.-L., van der Linden, L., and Burch, M.: Assessment of the impacts of climate change on the water quality of a small deep reservoir in a humid-subtropical climatic region, Water, 7, 1687–1711, https://doi.org/10.3390/w7041687, 2015.

Cole, T. M. and Wells, S. A.: CE-QUAL-W2: a two-dimensional, laterally averaged, hydrodynamic and water quality model, version 3.1, Instruction Report EL-03-1, U.S. Army Engineer Research and Development Center, Vicksburg, Mississippi, 2003.

Columbia River DART, Columbia Basin Research, University of Washington: Hourly water quality measurements, https://cbr.washington.edu/dart/query/wqm_hourly, last access: 15 August 2026.

Gupta, H. V., Kling, H., Yilmaz, K. K., and Martinez, G. F.: Decomposition of the mean squared error and NSE performance criteria: implications for improving hydrological modelling, J. Hydrol., 377, 80–91, https://doi.org/10.1016/j.jhydrol.2009.08.003, 2009.

Hoffman, F. M., et al.: Rapid Evaluation Framework for the CMIP7 Assessment Fast Track, Geosci. Model Dev., 19, 7415–7455, https://doi.org/10.5194/gmd-19-7415-2026, 2026.

Kettner, A. J., Hsu, L., and Serna, B. S.: The path to FAIR research models: lessons learned, Geosci. Model Dev., 19, 5381–5399, https://doi.org/10.5194/gmd-19-5381-2026, 2026.

Lee, J., Gleckler, P. J., Ahn, M.-S., Ordonez, A., Ullrich, P. A., Sperber, K. R., Taylor, K. E., Planton, Y. Y., Guilyardi, E., Durack, P., Bonfils, C., Zelinka, M. D., Chao, L.-W., Dong, B., Doutriaux, C., Zhang, C., Vo, T., Boutte, J., Wehner, M. F., Pendergrass, A. G., Kim, D., Xue, Z., Wittenberg, A. T., and Krasting, J.: Systematic and objective evaluation of Earth system models: PCMDI Metrics Package (PMP) version 3, Geosci. Model Dev., 17, 3919–3948, https://doi.org/10.5194/gmd-17-3919-2024, 2024.

Lima Neto, I. E.: Modeling water quality in a tropical reservoir using CE-QUAL-W2: handling data scarcity, urban pollution and hydroclimatic seasonality, RBRH, 28, e8, https://doi.org/10.1590/2318-0331.282320230003, 2023.

Nash, J. E. and Sutcliffe, J. V.: River flow forecasting through conceptual models part I — a discussion of principles, J. Hydrol., 10, 282–290, https://doi.org/10.1016/0022-1694(70)90255-6, 1970.

Schlund, M., Hassler, B., Lauer, A., Andela, B., Jöckel, P., Kazeroni, R., Loosveldt Tomas, S., Medeiros, B., Predoi, V., Sénési, S., Servonnat, J., Stacke, T., Vegas-Regidor, J., Zimmermann, K., and Eyring, V.: Evaluation of native Earth system model output with ESMValTool v2.6.0, Geosci. Model Dev., 16, 315–333, https://doi.org/10.5194/gmd-16-315-2023, 2023.

Wells, S. A.: Basis of the CE-QUAL-W2 version 3 river basin hydrodynamic and water quality model, in: Proceedings of the 2nd Federal Interagency Hydrologic Modeling Conference, Las Vegas, Nevada, 28 July–1 August 2002, available at: https://pdxscholar.library.pdx.edu/cengin_fac/113/ (last access: 15 August 2026), 2002.
