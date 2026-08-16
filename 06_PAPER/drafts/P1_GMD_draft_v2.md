<!--
P1 working draft for Geoscientific Model Development (Methods for assessment of models).
Not a final submission. Numbers follow analysis JSON / run-cards; notes are narrative only.
Do not treat DeGray temperature or Columbia DO metrics as skill versus observations.
Blueprint: P1_MERGED_BLUEPRINT.md. Prior structural draft: P1_GMD_draft_v1.md (retained).
-->

# Variable provenance, control-state outputs, and numerical health: a methods framework for assessing reported goodness-of-fit in CE-QUAL-W2 v4.5.5 applications (with v5.0 beta example inventory)

**Working Chinese title:** 变量溯源、控制状态输出与数值健康：面向 CE-QUAL-W2 v4.5.5（兼 v5.0 beta 算例清单）拟合优度报告的方法学评估框架

**Target journal:** *Geoscientific Model Development* (**Methods for assessment of models**)

**Version scope (title-locked):** Primary executable and hydrodynamic integrations use distributed **`w2_v455_ifx.exe` (v4.5.5)**. The demonstration corpus also **inventories** official example folders from **v5.0 beta** (Table 3); we do **not** claim a single-version paper or a cross-release skill comparison.

**Draft status:** v2 merged manuscript (2026-08-16; blueprint-confirm softens + local pre-sub checklist same day). Restructured from v1 per `P1_MERGED_BLUEPRINT.md` (GMD Methods spine + nature-skills discipline; figure inventory unchanged). Not a camera-ready submission. Zenodo archive not yet minted. Out-of-sample NSE was **not** computed.

## Unresolved discrepancies

Where notes or the paper plan round or reuse v1 labels, this draft follows the analysis JSON. Items below are the differences a reader will notice if they compare files:

1. `w1_provenance_metrics.json` still labels the Bonneville B series `BON_B_SYSTDG_TDG_TDG` (plan v1 name). `w3_tdgta_off_metrics.json` and the run-cards identify B as the controller file `TDGTarget_output.csv`. **This draft follows W3.**
2. Notes/plan round the Columbia wet-cell SOD in-band fraction to 89.6% and the below-band fraction to ~10.5%. JSON: `frac_in_0.5_3.0 = 0.8955` (968/1081) and `frac_below_0.5 = 0.1045`. **Draft uses JSON.**
3. Notes/plan round CCIW versus DART hourly MAE to 0.027% and the |Δ|≤0.051 match rate to 99.5%. JSON: `mae = 0.026537`, `match_rate_abs_le_0p051 = 0.994945`. **Draft uses JSON** (prose may round with a source tag).
4. Notes/plan write 2011 spill as QGT versus DART *r* = 0.87 and reallocation-day means ~174 → ~39 kcfs (*r* = −0.60). JSON: `r = 0.868638`; realloc means 173.8573 → 39.2308 kcfs; `r = −0.596447`. **Draft uses JSON.**
5. W3 notes write the pairing window as JDAY 40613–40681. JSON `reachable_range.obs_jday_min/max = 40613.583 / 40681.542`. **Draft uses JSON.**
6. The plan writes “Bonneville 80+” layer add/subtract events. JSON completed runs: TDGTA ON add = 42, sub = 43; OFF add = 48, sub = 49. **Draft uses JSON.**
7. W2 notes write SNP violations at DLTINTER OFF / 20 s as “about 8%”. JSON `pct_violations = 7.75`. **Draft uses 7.75%.**
8. The plan writes 15.6% of paired observations >120%. JSON `frac_obs_gt_120 = 0.1555` (251/1614). **Draft uses 15.55% (251/1614).**

---

## Abstract

In CE-QUAL-W2 evaluation practice, the interpretation and cross-study portability of reported goodness-of-fit are conditional on adequate documentation and alignment of variable provenance, controller state, and numerical-health context. Without reconstructable provenance, cross-site comparison of those numbers cannot generally be established from the reported metric alone. A structured audit of the 38 eutrophication applications assembled by Benicio et al. (2024) shows that a Variable Provenance Record (output file, column, segment, layer, units, derivation chain, time support, pairing tolerance) can be reconstructed from the paper alone in only 2 of 38 studies (5.3%); that a W2 output file or column name was confirmed in 0 of 38 (partial constituent wording is common; unknowns stay unknown); and that only 1 of 12 *R*² values in the review’s summary table can be confirmed as W2-versus-observation skill. <!-- w5_lit_audit_summary.json --> Full text of methods-plus-calibration results was obtainable for 9 of 38 papers (23.7%); the rest were coded from abstracts and the review tables, with unknowns left as unknowns rather than coded as confirmed absence.

We reproduce official example applications and show three independent reasons why reported goodness-of-fit should be interpreted conditionally. First, the same run emits several numerical series that a practitioner might call “TDG”, “temperature”, or “dissolved oxygen”. At Bonneville Dam, pairing the same Cascade Island (CCIW) observations (*n* = 1614; JDAY 40613.583–40681.542) to three output channels yields *R*² in a narrow band 0.508–0.551 while Nash–Sutcliffe efficiency (NSE) is −2.804, +0.500, and −2.752. <!-- w3_tdgta_off_metrics.json --> The highest *R*² is among the worst NSE values. The same *R*²-blind, α/β-visible pattern appears as **internal consistency** (not skill versus observations) for DeGray surface temperature versus volume-average temperature (*R*² = 0.9027, NSE = −0.5855, *n* = 2943) and for Columbia Slough dissolved oxygen at three TSR segments (highest-*R*² pair *R*² = 0.6505, NSE = −1.4821, *n* = 116). <!-- w1_provenance_metrics.json --> Pearson *R*² is invariant to affine rescaling of the simulated series and therefore cannot detect the variance-ratio (α) and bias-ratio (β) errors that variable misidentification produces.

Second, the skill-best Bonneville series (NSE = +0.500, β = 0.9986, paired maximum 120.09%) exists only in the controller-gated file `TDGTarget_output.csv`. Turning `TDGTA` off removes that file; it does **not** delete the physical TDG variable. SYSTDG still writes `TDG_TDG` to `TDG_output.csv`, a pre-control snapshot that is bit-identical on and off (MAE = 0) and cannot substitute for the gated series (daily MAE = 1.7073 versus the gated file; raw maxima 131.7% versus 120.1%). <!-- w3_tdgta_off_metrics.json --> Independent DART hours confirm that the example observations were not rewritten (hourly *n* = 17805, MAE = 0.026537%). Out-of-sample NSE for 2016–2025 was **not** computed: the reproduced model ends near 2011 (TMEND = 40909). Those later years are used only for exceedance frequency (21.2% of valid hours >120%) and for the 2011 spill comparison.

Third, a run can return exit code 0 and “Normal termination” while `w2.wrn` records negative surface-layer thickness (H1 < 0) rollbacks to DLTMIN. That geometry failure is visible only at Long Lake among completed runs. Under official `DLTINTER=ON`, negative-thickness counts at the day-30 DLTMAX knot 20/50/100/200 s are 5/4/1/5; under `DLTINTER=OFF` they are 0/0/0/0. <!-- nhr_dlt_scan.json --> The main claim is that a Numerical Health Record (NHR) should accompany reported evaluation statistics, not that smaller time steps are less stable.

We propose a reporting protocol packaged as an evaluation record—VPR, control-state provenance, NHR, and run-cards—implemented in a minimal evaluator (`w2eval`) that writes cards from existing analysis files without rerunning the model. Without those reporting elements, the direct comparability of goodness-of-fit values across CE-QUAL-W2 applications cannot generally be established from the reported metric alone.

## 1 Introduction

CE-QUAL-W2 (hereafter W2) is a two-dimensional, laterally averaged hydrodynamic and water-quality model used for reservoirs, rivers, and estuaries (Cole and Wells, 2003; Wells, 2002). Applications routinely publish a single goodness-of-fit number, most often the coefficient of determination *R*², and reviews then array those numbers as if they ranked calibration quality. Benicio et al. (2024) screened the eutrophication literature and tabulated *R*² from 0.32 to 0.977 for 12 of 38 selected studies, attributing the spread in their §3.2 (“Calibration Variability”) to data quality, methodological maturity, and site complexity. That explanation may be part of the story. It cannot be tested, however, unless each *R*² is attached to a reconstructable evaluation object: which output file and column, which segment and layer, whether an internal control rule was binding, and whether the time integration was numerically healthy.

Those three attachments are almost never present. We coded all 38 selected rows of Benicio et al. (2024) Table 1 (their references [12]–[14], [18], [21]–[54]; Table 1 has 38 rows and matches the stated “38 selected”). <!-- w5_lit_audit_summary.json --> A Variable Provenance Record as defined in Sect. 3.3 is reconstructable from the paper alone in 2 of 38 studies (5.3%). A W2 output file or column name was confirmed in 0 of 38 (`vpr_variable=yes`); many rows have only partial constituent wording. Eleven of 38 report *R*² for any model they used; nine of those eleven (81.8%) do not report NSE; none report the Kling–Gupta efficiency (KGE; Gupta et al., 2009). Of the 12 *R*² entries in the review’s Table 2, only one—Lima Neto (2023), *R*² = 0.32—can be confirmed as W2 output versus field observations of the stated constituents. The remaining Table 2 entries mix pan-evaporation correlations, inflow concentration regressions, load-reduction response curves, watershed-model (SWAT) skill mislabelled as W2 skill, and values that the review text itself describes as *R* rather than *R*². Full text covering methods and calibration results was legally obtainable for 9 of 38 papers (23.7%). Nineteen papers are `unknown` on VPR reconstructability because full text was unavailable and the abstract was silent. We do not upgrade those unknowns to “no”.

Assessment guidance in environmental modelling has long stressed that reported skill is conditional on the evaluation protocol (Bennett et al., 2013). Decomposition of error into correlation, variability, and bias components (Gupta et al., 2009) further shows why a single scalar cannot stand in for an incompletely specified evaluation object. This paper is a **methods paper for assessment of models** in the GMD sense: the object of inference is the evaluation workflow, not a new process algorithm. Almeida and Coelho (2025) remain the closest CE-QUAL-W2 + GMD precedent for open, reproducible evaluation of process options; we complement that layer by making the provenance, control state, and numerical health behind goodness-of-fit statistics auditable.

The argument is organized around four contributions, stated as falsifiable claims.

**Contribution 1 (variable provenance).** We show that goodness-of-fit statistics can depend materially on the provenance of the evaluated output variable, and introduce a **variable provenance record (VPR)** that makes the model quantity, extraction route, processing state, and evaluation target explicit. On a single Bonneville run with the total-dissolved-gas target controller on (`TDGTA=ON`), three defensible choices of “the TDG series” produce *R*² values that would all be written as moderate agreement (~0.5) while NSE ranges from worse than the observational mean (NSE = −2.804 and −2.752) to NSE = +0.500. <!-- w3_tdgta_off_metrics.json --> *R*² and NSE describe different properties; neither resolves ambiguity in *which* model quantity entered the metric. DeGray temperature and Columbia dissolved-oxygen **output channels disagree with one another** on the same run; those NSE/KGE values are internal consistency, not skill versus observations. Official example folders for DeGray and Columbia contain no independent temperature or DO observations.

**Contribution 2 (control-state / gated outputs).** We identify **control-state dependence** as a source of **evaluation ambiguity** when diagnostic or controller-specific outputs are conditionally available, and incorporate control-state provenance into the evaluation record. The series with NSE = +0.500, β ≈ 1, and a 120.09% cap exists only in `TDGTarget_output.csv`. Switching `TDGTA` to OFF removes that file together with `TDGTarget_warning.opt`. SYSTDG continues to write `TDG_TDG` to `TDG_output.csv`. That file is a pre-control snapshot: ON and OFF copies are identical (MAE = 0) and must not be used as a stand-in for B. <!-- w3_tdgta_off_metrics.json --> We do **not** claim that the physical variable was deleted. DART hourly data show that 21.2% of valid hours in 2016–2025 still exceed 120%; that statistic supports a reachable-range argument. It is not an out-of-sample NSE.

**Contribution 3 (numerical health).** We propose that statistical performance be accompanied by a **numerical health record (NHR)** documenting execution diagnostics relevant to interpretation of reported evaluation statistics. When surface-layer thickness `H1(KT,I)` is negative and the time step exceeds `DLTMIN`, W2 writes a warning, forces `CURMAX = DLTMIN`, and recomputes the step (`w2_4_win.f90`). The run still ends with exit 0 and “Normal termination” if no fatal `w2.err` is opened. Negative-thickness rollbacks appear only at Long Lake among completed Bonneville, Columbia, DeGray, and Long Lake runs. Counts 5/4/1/5 versus DLTMAX 20/50/100/200 s hold **only** for official `DLTINTER=ON` knot interpolation; `DLTINTER=OFF` yields 0/0/0/0. <!-- nhr_dlt_scan.json --> The NHR is a **reporting recommendation**, not a universal timestep-stability criterion. We do **not** claim a general law that reducing the time step makes the geometry less stable.

**Contribution 4 (protocol and demonstration corpus).** We implement these reporting elements in reproducible **run-cards** and use official CE-QUAL-W2 examples as a heterogeneous **demonstration corpus** for auditing evaluation provenance and numerical-health information. Of 17 official examples (eight in v4.5.5, nine in v5.0 beta), only Bonneville ships field observations. Long Lake requires a `HabitatFiles/` directory that the distribution does not include. Columbia sets `SED_DIAG=ON` without shipping `W2_diagenesis.npt`; the diagenesis parameters used here were transplanted from DeGray and are **not** a Columbia field calibration. We provide `w2eval`, a provenance-aware run-card writer. We do **not** claim a first reproducible validation of CE-QUAL-W2.

The rest of the paper defines an evidence taxonomy and interpretation rules (Sect. 2), states the assessment methods (Sect. 3), describes the demonstration corpus (Sect. 4), reports finding-led results (Sect. 5), discusses conditional comparability and likely objections (Sect. 6), and concludes (Sect. 7).

## 2 Evidence taxonomy and interpretation rules

We distinguish four kinds of claim that a CE-QUAL-W2 evaluation record may support. Mixing them in a single skill table is a category error.

1. **Observational skill.** Paired model output versus independent field observations under a stated VPR and run configuration. In this paper, only Bonneville TDG versus CCIW occupies this class.
2. **Internal consistency.** Agreement among model output channels on the same run when no independent observations exist. DeGray temperature and Columbia DO metrics are labelled `internal_consistency` in every table, run-card, and caption. They diagnose provenance ambiguity; they do not rank calibration quality.
3. **Numerical health.** Execution diagnostics (especially H1 < 0 → DLTMIN rollback, layer add/subtract counts, exit status versus warning files) that condition whether two skill numbers are like-for-like. Exit code 0 is not a health certificate.
4. **Reproducibility / magnitude plausibility.** Whether an official deck can be executed as distributed, and whether transplanted parameters produce order-of-magnitude-plausible fluxes (Columbia SOD versus the Almeida and Coelho (2025) scan band). Plausibility is not site calibration.

A goodness-of-fit value is not only a property of a model and observations; it is a property of a specified model quantity, observation pairing, processing pathway, run configuration, and metric. This does **not** make cross-study comparison intrinsically invalid; it makes interpretation **conditional** on sufficient alignment of those evaluation conditions.

## 3 Assessment methods

### 3.1 CE-QUAL-W2 output architecture

W2 writes the same physical quantity through several files that do not share a column layout or a spatial support (Cole and Wells, 2003; Wells, 2002). Time-series output (TSR) samples nominated segments, typically at the current surface layer when `ETSR = 0`. Withdrawal output (WDO) writes flow-weighted structure and gate temperatures and constituents. Profile (PRF) and snapshot (SNP) files dump the two-dimensional field. Structure (`two_str*.csv`) and gate (`two_gate*.csv`) files report centerline elevations. Volume-averaged temperature `Tvolavg` shares a TSR file with surface `T2` but is a different spatial operator.

For total dissolved gas at Bonneville, three further channels exist. Module `withdrawal.f90` converts dissolved N2 and DO to a TDG percentage using the model’s Henry-law formula. Module `systdg.f90` writes native `TDG_TDG` to unit 88888 (`TDG_output.csv`) when SYSTDG is on, independently of the TDG target switch. Module `TDGtarget.f90` is an optimization controller: it reads `w2_TDGtarget.csv` (spill priority `SPPRIOR`, minimum split fraction `SPMINFRAC`, powerhouse maximum `PHMAXFLOW`, iteration count `tsiteration`) and dynamic 115%/120% targets (`TDGdyntarget.csv`), then reallocates flow between spillways and the powerhouse. Its post-control series is written only to `TDGTarget_output.csv`, and only when `TDGTA=ON`.

A practitioner who asks “what is modelled TDG?” therefore has at least four answers on one Bonneville run: Henry-converted WDO at segment 76 (caliber A), the controller file (B), the in-reservoir TSR TDG column at segment 40 (C), and the SYSTDG daily file (S). A, B, C, and S are different Variable Provenance Records. Calling them all “TDG skill” is a category error.

### 3.2 Layer add/subtract and H1 < 0 rollback

Layer counts are not a truncation-error diagnostic. `layeraddsub.F90` adds a layer when `ZMIN < −0.85 H(KT−1)` (loop recheck −0.80 *H*) and subtracts a layer when `ZMIN > 0.60 H(KT)` and `KT < KTMAX`, with a one-layer special case and a “Low water” warning if `ZMIN > 0.99 H(KT)`. The 0.85/0.80 pair is a hysteresis band. Seasonal stage at a dam or in a tidal slough will cross those thresholds; add/subtract counts belong in an NHR as geometry events, not as failures.

Negative surface thickness is a different event. In `w2_4_win.f90` (autostepping, approximately lines 1415–1424 of the v4.5 source tree used here), if `H1(KT,I) < 0` and `DLT > DLTMIN`, the model writes `w2.wrn` (“Negative surface layer thickness” / “time step reduced to DLTMIN”), sets `CURMAX = DLTMIN`, and `GO TO 220` to recompute the step. Only failure already at `DLTMIN` becomes a fatal `w2.err` (“Unstable water surface elevation”). `endsimulation.F90` prints “Normal termination” when `ERROR_OPEN` is false, and **deletes** `w2.wrn` when `WARNING_OPEN` is false. A rollback-prone run can therefore finish with exit 0, a clean-looking terminal message, and a warning file that a skill table never reads. Snapshot-file “violations” (`NV`) increment on any time-step rollback, including CFL and viscosity limits, and must not be used as a proxy for H1 < 0 counts.

When `DLTINTER=ON`, `update.F90` linearly interpolates `DLTMAX` between schedule knots. Long Lake’s official `w2_con.csv` has six knots; days 30–40 interpolate from the day-30 `DLTMAX` (officially 100 s) to 1800 s at day 40. Editing the day-30 knot changes the interpolation **start**, not a hard cap inside the window.

### 3.3 Variable Provenance Record (VPR)

A VPR is the tuple that makes an evaluation object reconstructable by a second analyst:

{output file, column name, segment *I* or mapped station, layer *K* or withdrawal elevation, units, derivation chain, time support (instantaneous / daily mean / snapshot / event log), pairing tolerance}.

Derivation chain distinguishes native TSR, Henry conversion from N2+DO, pre-control SYSTDG writes, and post-control controller writes. Time support and pairing tolerance are part of the object: Bonneville A/C use nearest-neighbour pairing with tolerance 0.05 d; B/S use 0.6 d to match the daily SYSTDG file against hourly CCIW. Changing the tolerance is a different evaluation. DeGray and Columbia VPRs are labelled `internal_consistency`; their “reference” series is another model channel, not a field observation.

### 3.4 Controller-conditional evaluation

When an internal control rule can bind, skill is reported **conditional on controller state**, with an explicit reachable range. For Bonneville that means: (i) `TDGTA` ON or OFF; (ii) whether the evaluated file is `TDGTarget_output.csv` (post-control), `TDG_output.csv` (pre-control snapshot), Henry WDO, or TSR; (iii) the fraction of observations that lie outside the controller cap. Same-named column `TDG_TDG` in two files is not the same VPR. A classical “freeze the metric, toggle the process” experiment is impossible on path B, because the metric’s file disappears when the controller is off.

### 3.5 Numerical Health Record (NHR)

An NHR is parsed from `w2.wrn`, `w2.err`, SNP runtime footers, and (when present) TSR DLT samples (`00_INDEX/parse_nhr.py`). Recommended fields for this paper:

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

Pearson *r* is invariant under affine maps *s*′ = *a s* + *b* with *a* ≠ 0. Consequently *R*² cannot see α or β. NSE and KGE can. Variable misidentification that stretches or shifts a series while preserving rank correlation is invisible to *R*² by construction. That is the theoretical content of Contribution 1; Sect. 5 supplies the empirical instances. `w2eval` copies these scores from analysis JSON and does not reimplement the formulae.

### 3.7 w2eval

`w2eval` is a minimum viable run-card generator (`06_PAPER/w2eval/w2eval.py`). It reads cached JSON, not the executable. Each card has three sections: VPR, metrics panel, NHR. Five cards exist: Bonneville TDGTA ON, Bonneville TDGTA OFF, Long Lake DLT/NHR, Columbia DO internal consistency plus SOD magnitude, and DeGray temperature internal consistency (`06_PAPER/w2eval/cards/`). The tool does not launch `w2_v455_ifx.exe`, does not recompute NSE, and does not draw figures. If the JSON and the run directory diverge, the card follows the JSON.

### 3.8 Literature audit methods (W5)

Coding definitions follow `w5_lit_audit_summary.json`. Inclusion is the review’s own 38-row Table 1 (refs [12]–[14], [18], [21]–[54]); we do not re-run a bibliographic search. **Full text** covering methods-plus-calibration results was legally obtainable for **9 of 38** papers (23.7%); the remaining 29 were coded from abstracts and the review tables only.

`vpr_reconstruct = yes` requires, from the paper alone (not supplement), a locatable segment or mapped station, a layer or sampling depth, the constituent identity, and the comparison period. An output filename is never required for `yes` in this corpus because none of the 38 provide one. Every coded field uses a three-way transparency rule: **confirmed present**, **confirmed absent** (positively established from accessible material), and **unknown / not verifiable**. Paywalled or abstract-only rows without a usable statement were coded `unknown` and are **never** converted to confirmed absence (`no`). Secondary citations of MAE/RMSE were flagged and not treated as verified primary text. Control-rule coding is `described` / `not_mentioned` / `NA`; none of the 38 is a TDG/SYSTDG paper, because the review query is eutrophication. Claim 2 is therefore **not** extrapolated from those 38 studies; they support only the weaker statement that run state is rarely declared as an evaluation condition.

### 3.9 DART comparison methods (W4)

Hourly Cascade Island records were downloaded from Columbia River DART (Columbia Basin Research, University of Washington; source USACE NWD) for 2011–2025 using `sc=1` on the CSV endpoint. Library `Datetime` hour *h* on date *D* maps to DART `Hour = (h+1)×100` (hour-ending Pacific timestamp minus 1 h), verified on 2011-04-01. Exceedance percentages use hours with non-missing dissolved-gas percent as the denominator; CCIW winters are often missing. Out-of-sample NSE is explicitly not computed (`out_of_sample.computed_nse = false`). <!-- w4_cciw_vs_dart.json -->

---

## 4 Demonstration corpus

Official CE-QUAL-W2 example decks are used here as a heterogeneous **demonstration corpus** for auditing evaluation provenance and numerical health. They are not a multi-site validation campaign and are not presented as “calibration sites.”

All hydrodynamic integrations used the distributed `w2_v455_ifx.exe`. We did not rerun the model for this manuscript; metrics are recomputed from archived output in `05_REPRO_RUNS/`.

**Bonneville Dam (skill versus observations).** Official SYSTDG example; `TDGTA=ON` in `05_REPRO_RUNS/run_20260814_bonneville/Bonneville_SYSTDG` and `TDGTA=OFF` in `…/run_20260814_bonneville_notarget/…`. Control file `TMSTRT = 40544`, `TMEND = 40909` (Excel serial; JDAY 40544 = 2011-01-01, origin 1899-12-30). <!-- w4_cciw_vs_dart.json --> Both runs reach the end-of-period criterion used by the project runner (`flowbal` last JDAY 40908; OFF `c_wdo` last JDAY 40909) without `w2.err`. Observations are the example file `CCIW_TDG_Temp_2011-2015.csv` (Cascade Island tailwater). Valid CCIW TDG does not cover the calendar year: all 1614 paired hours fall in JDAY 40613.583–40681.542 (about 11 March–18 May 2011). <!-- w3_tdgta_off_metrics.json --> The plan window 40544–40910 is the model window, not the paired evaluation window.

**DeGray Reservoir (internal consistency, no observations).** `05_REPRO_RUNS/run_20260811_fixed/DeGray Reservoir with sediment diagenesis and vertical algae migration`. JDAY 64.5–358.7. Searches of v4.5.5 and v5.0 beta example folders found no independent temperature or DO observations. Metrics compare output channels on the same run.

**Columbia Slough Estuary (internal consistency, no observations).** Hydrodynamics and DO from `05_REPRO_RUNS/run_20260814_columbia_diag/` with `SED_DIAG=ON`. Official `w2_con.csv` requests sediment diagenesis but the example does not ship `W2_diagenesis.npt`. Parameters were copied from DeGray, with region-2 end segment 31 → 50. That transplant is **not** a Columbia calibration. The series is short: TSR pairing *n* = 116 over JDAY 32–55 (~23 days). A `SED_DIAG=OFF` companion run exists at `run_20260811_fixed`; ON versus OFF DO is a process-switch comparison, not a provenance comparison, and is not used as Contribution 1 evidence.

**Long Lake (numerical health, no observations).** Official DLT schedule (`NDLT = 6`, `DLTMIN = 0.1` s, `DLTINTER=ON`). Baseline `run_20260811_fixed/Long Lake` and the DLTMAX scan `run_20260815_ll_dlt_scan/` (day-30 knot 20/50/100/200 s × `DLTINTER` ON/OFF). The distribution omits `HabitatFiles/`; without that directory the habitat output path in `w2_habitat.npt` raises Intel Fortran severe (29). Completed scan jobs all reach JDAY 239.943 with exit 0.

---


Case-to-question map used in Sect. 5: Bonneville TDG → observational VPR sensitivity; TDGTA ON/OFF → gated-output semantics; DeGray T and Columbia DO → internal-consistency negative controls; Long Lake → NHR under exit 0; Columbia SOD → transplanted-parameter magnitude check; W5 audit → literature gap (not a W2 run). Suite inventory appears with Results in Table 3 (Sect. 5.5).

## 5 Results

Results are organized by methodological finding. Reservoir names identify the demonstration, not the claim type.

### 5.1 Variable provenance (observational skill and literature gap)

#### 5.1.1 Bonneville TDG versus CCIW (skill)

Table 1 reports four calibers on the TDGTA=ON run and the same four with TDGTA=OFF, all paired to the same CCIW series (*n* = 1614; JDAY 40613.583–40681.542). <!-- w3_tdgta_off_metrics.json --> Observed TDG ranges from 107.7% to 129.1%; 251 of 1614 paired hours (15.55%) exceed 120%.

**Table 1.** Bonneville TDG calibers versus CCIW. Kind = skill versus observations. B is absent when TDGTA=OFF. S is the SYSTDG pre-control snapshot, not a substitute for B. <!-- w3_tdgta_off_metrics.json -->

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

3. Caliber A is not a straw man. It uses the Henry conversion shipped in `withdrawal.f90`, a choice a competent reader would make in the absence of a VPR. The model itself emits at least three TDG number streams.

Figure 3 decomposes KGE into *r*, α, and β and is the glance test for Contribution 1. Figure 1 overlays the ON/OFF series on CCIW and the controller target band. Figure 2 shows 1:1 scatter.

**Figure 1.** Bonneville TDG time series for calibers A, B, C, and S with `TDGTA` ON and OFF, CCIW observations, and the 120% target cap (**observational skill** versus CCIW; not an internal-consistency panel). Paired evaluation occupies JDAY 40613.583–40681.542 (*n* = 1614), not the full model year. File: `../figures/W3_tdgta_on_off_timeseries.png` (exists).

**Figure 2.** One-to-one scatter of the same calibers against CCIW (**observational skill**). OLS slopes 1.079 / 0.664 / 1.154 for ON A/B/C. File: `../figures/W3_tdgta_on_off_scatter.png` (exists).

**Figure 3.** KGE decomposition (*r*, α, β) for Bonneville ON/OFF calibers (**observational skill versus CCIW**). Companion **internal-consistency** decompositions (not field skill): DeGray temperature `../figures/w1_degray_T_kge_bars.png`; Columbia DO `../figures/w1_columbia_DO_kge_bars.png` (both exist). Core panel: `../figures/W3_tdgta_kge_decomposition.png` (exists).

#### 5.1.2 Literature audit (motivation, not a W2 run)

**Table 2.** Structured audit of Benicio et al. (2024) Table 1 (*n* = 38). <!-- w5_lit_audit_summary.json -->

| Item | Count | Share |
|---|---:|---:|
| Full text (methods + calibration results) | 9 | 23.7% |
| VPR reconstructable from the paper (`yes`) | 2 | 5.3% |
| VPR `partial` / `no` / `unknown` | 6 / 11 / 19 | 15.8% / 28.9% / 50.0% |
| W2 output file or column named | 0 | 0% |
| Location to segment *I* or mapped station | 3 | 7.9% |
| Reports *R*² (any model) | 11 | 28.9% |
| Reports NSE / KGE / PBIAS | 2 / 0 / 1 | 5.3% / 0% / 2.6% |
| *R*² without NSE | 9 of 11 | 81.8% of *R*² papers |
| Open W2 inputs or code | 1 | 2.6% |
| Table 2 *R*² confirmed as W2↔observation skill | 1 of 12 | Lima Neto 0.32 |

The two reconstructable papers are Lima Neto (2023) (outlet = segment 31, second cell; inlet = segment 2, second cell; still no output filename) and Chang et al. (2015) (Station 1 → segment 3 surface; not in the review’s Table 2). We do **not** claim that all 38 papers report only *R*²: 11 report *R*², and many others report AME/RMSE or nothing that we could verify. We do **not** treat Table 2’s 0.32 and 0.977 as a skill gap: 0.977 is a load-reduction response curve.

Limitation, to be read with the counts: 19/38 VPR codes are `unknown` because full text was not obtained. Paywalled papers might document provenance more carefully. Open-access Table 2 entries already suffice to show that the summary table mixes mathematical objects. Unknowns stay unknown.

### 5.2 Control-state dependence and gated outputs

#### 5.2.1 Gated file versus pre-control snapshot

On TDGTA=ON, caliber B is the only series with NSE = +0.500, β = 0.9986, PBIAS = −0.14%, and paired maximum 120.09%. Raw B maximum is 120.1%. <!-- w3_tdgta_off_metrics.json --> That file is not written when `TDGTA=OFF`; `TDGTarget_warning.opt` disappears with it. Standard WDO, TSR, and `TDG_output.csv` remain.

`TDG_output.csv` is produced by SYSTDG (`INPUT_SYSTDG` opens unit 88888) regardless of TDGTA. Source order in `TDGtarget.f90` / `hydroinout.F90` / `systdg.f90` is: the controller calls `SYSTDG_TDG` **before** reallocating; that first call of the day writes unit 88888 and advances `NXTSPLIT3`; later calls the same day do not rewrite the daily row. Consequently ON and OFF `TDG_output.csv` are identical (365 days, MAE = 0, max |Δ| = 0, raw max 131.7% both). The same file versus `TDGTarget_output.csv` has MAE = 1.7073, max |Δ| = 11.743, raw maxima 131.7% versus 120.1%. Column name `TDG_TDG` is shared; the evaluation object is not.

We therefore write three sentences and only these three:

1. The skill-best, β ≈ 1, 120.1%-capped series exists only in the controller-gated file `TDGTarget_output.csv`. OFF, that file is gone, so a freeze-the-metric / toggle-the-controller experiment cannot be done on path B.
2. The physical TDG variable is not deleted. SYSTDG still writes a pre-control snapshot to `TDG_output.csv`. That snapshot cannot replace B.
3. The 120% cap is a controller artefact, not a SYSTDG formula ceiling (hard cap in the metrics JSON: 145%). Observed paired maximum is 129.1%; 15.55% of paired hours exceed 120% and are structurally unreachable on B.

Turning the controller off does **not** make A a usable forecast: OFF A NSE = −2.3371 (still far below a mean forecast), KGE falls from 0.4089 to 0.1603 because α inflates from 1.513 to 1.791. OFF S NSE = +0.3573, paired max 127.49%, raw max 131.7%: it can exceed 120% but the paired series does not reach observed 129.1%. In-reservoir TSR (C) is almost unaffected (ON versus OFF MAE = 0.0075 on 6211 in-file points). Henry WDO (A) does move (MAE = 0.6951, OFF raw max 129.04%).

#### 5.2.2 DART check, exceedance, and 2011 spill (not out-of-sample NSE)

Library CCIW versus DART hourly TDG, 2011–2015, both valid: *n* = 17805, MAE = 0.026537%, RMSE = 0.04124%, |Δ| ≤ 0.051 match rate = 0.994945. <!-- w4_cciw_vs_dart.json --> Five hours differ by more than 1% (max |Δ| = 1.9), almost all in 2011–2012; 2013–2015 match at 1.0 within 0.05. Verdict recorded in JSON: `library_is_dart_rounded`. We find no evidence that the example observations were materially rewritten.

Among DART hours with non-missing TDG, 14.6842% exceed 120% in 2011–2015 (valid hours *n* = 17924) and 21.2% exceed 120% in 2016–2025 (*n* = 40434). Annual fractions are not a stationary 15%: 2015 has 0% of valid hours >120% (annual max 118.97%); 2017 has 46.9214% (annual max 131.38%). The cap problem does not age out of the record. **These percentages are not forecast skill.** The reproduced model’s `TMEND = 40909` covers about 2011 only. JSON flag: `out_of_sample.computed_nse = false`.

2011 daily spill (365 paired days). Input `QGT` versus DART spill: *r* = 0.868638. Controller (`TDGTarget_output`) versus DART spill: *r* = 0.237349. Controller flag `C = R` on 116 days (U = 0, blank = 249). On reallocation days, mean DART spill is 173.8573 kcfs and mean controller spill is 39.2308 kcfs (*r* = −0.596447). <!-- w4_cciw_vs_dart.json --> The ON run’s low bias and 120% cap are partly the result of operating a different spill programme than 2011 reality, not merely of a better physical TDG closure.

**Figure 5.** Paired-window CCIW TDG histogram (JDAY 40613.583–40681.542, *n* = 1614) with 120% controller-cap line; 251/1614 = 15.55% of hours exceed 120% and are unreachable on gated B. File: `../figures/fig05_tdg_reachable_range.png` (exists). Companion annual exceedance 2011–2025: `../figures/w4_tdg_gt120_annual.png` (exists; **exceedance frequency only—not forecast skill**; model NSE ends near 2011).

**Figure 8.** 2011 spill: QGT, TDGTA, and DART, including reallocation days 173.86 → 39.23 kcfs. File: `../figures/w4_spill_tdgta_vs_dart.png` (exists). Companion scatter: `../figures/w4_spill_scatter.png` (exists).

Library versus DART identity plots: `../figures/w4_cciw_vs_dart_scatter.png`, `../figures/w4_cciw_vs_dart_timeseries.png` (exist).

### 5.3 Internal consistency (negative controls)

#### 5.3.1 DeGray temperature (internal consistency)

No independent observations. Table 4 (upper block) compares channels on one run (*n* = 2943 unless noted; JDAY 64.5–358.7). <!-- w1_provenance_metrics.json -->

Same TSR file, surface `T2(C)` versus volume-average `Tvolavg(C)`: *R*² = 0.9027, NSE = −0.5855, KGE = 0.2354, *r* = 0.9501, α = 0.3456, β = 0.6077. A review table would call *R*² = 0.90 excellent. NSE says the volume-average is worse than using the surface-series mean as a predictor. Volume averaging compresses variance by about 65% (α = 0.35) and lowers the mean by 39% (β = 0.61). *R*² cannot see that affine-scale error.

Surface T2 versus WDO mixed withdrawal temperature: *R*² = 0.5293, NSE = −0.3653. Structure centerline 115 m versus gate centerline 120 m: *R*² = 0.5336, NSE = −6.5825, α = 2.3772, β = 1.4882. The two *R*² values differ by 0.004 and sit inside the Bonneville TDG *R*² band; NSE differs by six units. Reporting only *R*² would describe two “outflow temperatures” as equally moderate.

Gate 120 m versus surface T2 is *not* a counterexample to write as “gates equal the surface.” NSE = 0.9993 because this gate centerline (120 m) is near the water surface (ELWS ≈ 123.8 m on this deck). WDO is essentially the structure temperature (WDO versus STR: *R*² = 1.0000). A VPR that omits elevation has already changed the predictand. Deep-layer mistakes *do* collapse *R*²: PRF segment 26 bottom versus TSR surface T2 has *R*² = 0.0572, NSE = −2.9461 (*n* = 296). The *R*² blind spot is for correlated-but-wrong-scale channels (volume average, the other outlet, another segment), not for every wrong layer.

Parser self-checks: SNP surface versus TSR T2, NSE = 1.0000 at 47 snapshots; PRF segment 26 surface versus TSR segment 31 surface, NSE = 0.9987. Cross-file surface channels agree; the disagreements are layer, outlet, and averaging operator.

**Figure D1.** DeGray surface T2, Tvolavg, WDO, STR, and GATE time series (**internal consistency only**—no field observations). File: `../figures/w1_degray_T_timeseries.png` (exists).

**Figure D2.** DeGray 1:1 channel scatter (**internal consistency**; not observational skill). File: `../figures/w1_degray_T_scatter.png` (exists).

**Figure D3.** DeGray *R*² versus NSE for channel pairs (**internal consistency**). File: `../figures/w1_degray_T_r2_vs_nse.png` (exists).

#### 5.3.2 Columbia DO (internal consistency)

No independent observations. TSR segments 45, 49, and 33, `SED_DIAG=ON`, *n* = 116, JDAY 32–55. <!-- w1_provenance_metrics.json -->

| Pair | *R*² | NSE | KGE | *r* | α | β |
|---|---:|---:|---:|---:|---:|---:|
| I=45 vs I=49 | 0.2071 | −4.4940 | 0.1665 | 0.4551 | 0.6816 | 1.5444 |
| I=45 vs I=33 | 0.3275 | −2.2675 | 0.3794 | 0.5723 | 1.2585 | 1.3679 |
| I=49 vs I=33 | 0.6505 | −1.4821 | 0.1243 | 0.8065 | 1.8464 | 0.8858 |
| SNP I=45 surface vs bottom (*n* = 24) | 0.9321 | 0.9072 | 0.9362 | 0.9655 | 0.9713 | 0.9547 |

All three station pairs have NSE < −1.48. Ranking by *R*² would select I=49 versus I=33 as best; that pair still has negative NSE and α = 1.85. On the shallow tidal slough, SNP surface versus bottom NSE = 0.91: **wrong station is more dangerous than wrong layer**. The Columbia *R*² band (0.21–0.65) is wider than Bonneville’s 0.04, as expected for 23 tidal days. Generalization of Contribution 1 rests primarily on DeGray (*n* = 2943) plus Bonneville skill, with Columbia as a station-ambiguity illustration.

**Figure C1.** Columbia TSR DO at I=45/49/33 (**internal consistency only**—no field observations). File: `../figures/w1_columbia_DO_timeseries.png` (exists).

**Figure C2.** Columbia DO scatter and *R*²–NSE (**internal consistency**; not observational skill). Files: `../figures/w1_columbia_DO_scatter.png`, `../figures/w1_columbia_DO_r2_vs_nse.png` (exist).

**Figure 4.** *R*² versus NSE for Bonneville ON A/B/C (**observational skill** vs CCIW), DeGray primary **internal-consistency** pairs, and Columbia primary **internal-consistency** pairs. Benicio et al. Table 2 *R*² values appear as a top rug only (audit has no NSE numbers for those cells; confirmed W2↔obs skill is Lima Neto *R*² = 0.32). Separate DeGray and Columbia panels: Figures D3 and C2. File: `../figures/fig04_r2_vs_nse_literature.png` (exists).

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

**Table 5.** Negative-thickness counts for the Long Lake DLTMAX × DLTINTER scan (day-30 knot; DLTF held at 0.9). All eight jobs complete at JDAY 239.943 with exit 0. Add/sub = 3/3 at every point. Columbia DLTMAX 120/360/720 s (`DLTINTER=OFF`): 0/0/0. <!-- nhr_dlt_scan.json -->

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

**Figure 6.** Long Lake negative-thickness counts versus DLTMAX under DLTINTER ON and OFF (**numerical-health evidence**; reporting recommendation only—**not** a universal timestep-stability criterion). File: `../figures/nhr_dltmax_neg_thickness.png` (exists). Companions: `../figures/nhr_dltmax_layers_dltmin.png`, `../figures/nhr_dltmax_heatmap.png` (exist).

### 5.5 Reproducibility audit and run-card implementation

**Table 3.** Official example suites inspected in this project (v4.5.5 eight folders + v5.0 beta nine folders = 17). Cells other than Bonneville, Columbia, DeGray, and Long Lake are inventory facts (folder exists), not independent run audits. We do not invent pass/fail for Detroit, Spokane, particle tracking, or cascade cases.

| Suite | Example folder | Field observations in the distributed deck | Verified run defect (this project) |
|---|---|---|---|
| v4.5.5 | BonnevilleDam with TDG computed using SYSTDG | CCIW TDG/temperature (shared with v5 Bonneville_TDG) | None required to start; TDGTA default ON |
| v4.5.5 | Columbia Slough Estuary | None found | `SED_DIAG=ON` without `W2_diagenesis.npt` |
| v4.5.5 | DeGray Reservoir with sediment diagenesis and vertical algae migration | None found | Completed after using the shipped diagenesis file |
| v4.5.5 | Long Lake | None found | Missing `HabitatFiles/` → forrtl 29 |
| v4.5.5 | Detroit Reservoir; MultipleWaterBodyCascade; Particle Tracking in Reservoir; Spokane River | Not the Bonneville CCIW file; not used as skill cases here | Not independently completed for this paper |
| v5.0 beta | Bonneville_TDG | `CCIW_TDG_Temp_2011-2015.csv` | Only example with field observations among the 17 |
| v5.0 beta | Columbia Slough Estuary; DeGray; Long Lake | None found in those folders | Same HabitatFiles / diagenesis issues as v4.5.5 counterparts |
| v5.0 beta | DetroitReservoir; LMNR_ORGC; MultipleWaterBodyCascade; Particle Tracking in Reservoir; Spokane River | Not used as skill cases here | Not independently completed for this paper |

Project notes further record that upstream Git distribution of Windows executables as Git LFS pointers means a naive clone does not yield a runnable `exe`. We did not re-hash LFS pointers for this draft; the working executable used throughout is the local `02_LIBRARY/07_executables/v4.5.5/w2_v455_ifx.exe`.

#### 5.5.1 Transplanted-parameter SOD magnitude check

Columbia SOD, after the DeGray-template transplant, is an order-of-magnitude check against the Almeida and Coelho (2025) zero-order/hybrid scan band 0.5–3.0 g O₂ m⁻² d⁻¹ (a user-specified Portuguese-reservoir experiment, not a global ecological range). Wet cells (SOD > 0), instantaneous, JDAY ≥ 33 (spin-up row at JDAY 32 dropped): *n* = 1081, mean = 0.8762, median = 0.8082, min = 0.1349, max = 1.6761; 968/1081 (0.8955) lie in 0.5–3.0; 0.1045 lie below 0.5; **no point exceeds 3.0**. <!-- w7_columbia_sod_vs_almeida.json --> Last-day wet mean 0.7752 g O₂ m⁻² d⁻¹. CSOD mean 0.8034, NSOD mean 0.0727. This is **not** a Columbia calibration and supports **no** water-quality scenario inference. It only shows that the transplanted file did not produce absurd SOD.

**Figure 7.** Example three-block **evaluation record** (VPR, metrics panel, NHR) typeset from `w2eval`; *R*²/NSE/KGE remain **downstream** statistics on the card, not a fourth scientific pillar. File: `../figures/fig07_w2eval_runcard.png` (exists). Sources: `../w2eval/cards/bonneville_tdgta_on.md`, `../w2eval/cards/bonneville_tdgta_on.json`.

**Figure S1.** Columbia wet-cell SOD time series with 0.5–3.0 band and Almeida reference means (**transplanted-parameter plausibility check, not a Columbia calibration**). File: `../figures/w7_columbia_sod_timeseries.png` (exists). Histogram: `../figures/w7_columbia_sod_histogram.png` (exists).


## 6 Discussion

### 6.1 Why *R*² alone cannot establish provenance equivalence

Bennett et al. (2013) summarize evaluation practice as requiring transparency about what was compared and how. Gupta et al. (2009) show why correlation-based scores can remain high while variability and bias fail. The Bonneville and internal-consistency demonstrations instantiate both points for CE-QUAL-W2 output architecture.

Let *s* be a simulated (or alternate-channel) series and *s*′ = *a s* + *b* with *a* ≠ 0. Pearson *r*(*s*′, *o*) = sign(*a*) *r*(*s*, *o*), so *R*² = *r*² is unchanged. The KGE components α′ = |*a*| σ_s / σ_o and β′ = (*a* μ_s + *b*) / μ_o generally change, as does NSE. Volume averaging (DeGray Tvolavg), a 120% controller cap (Bonneville B), and a different tidal segment (Columbia I=49 versus I=33) are all approximately affine or variance-scaling operations relative to a reference channel. A literature table that records only *R*² is structurally unable to detect them. That is why 9 of 11 papers in the 38-study corpus that report *R*² omit NSE, and why KGE is entirely absent: the metric that is published is the metric that is blind.

We are not arguing that *R*² is useless. We are arguing that it is not a sufficient statistic for “how well W2 was calibrated”, and that it is the wrong axis for a cross-application ranking. α/β/NSE likewise do not **prove** provenance; they only expose bias and scale mismatches that *R*² can conceal.

### 6.2 Likely referee objections

**“The conclusion is tautological—metrics are always conditional on what was evaluated.”** The general principle is not new. The contribution here is operational for CE-QUAL-W2: three concrete reporting elements (VPR, controller-conditional evaluation, NHR) plus W2-specific examples showing how output provenance, controller gating, and internal numerical events change the interpretation of otherwise conventional GOF numbers. We do not claim novelty for the abstract idea that a metric depends on its evaluation protocol.

**“The 17 examples validate the whole three-part framework.”** They do not. The suite exercises different failure modes. Bonneville supplies the principal observation-based skill contrast; DeGray and Columbia are internal-consistency diagnostics only; Long Lake informs NHR existence under exit 0; SOD is a transplanted-parameter plausibility check; Table 3 cells outside those decks are inventory facts, not independent validation runs. Demonstration of reporting ambiguities is the claim; full-framework validation across 17 applications is not.

**“Nobody would pick the wrong output.”** Caliber A is the formula in `withdrawal.f90`. Caliber C is a TSR column named TDG. Caliber B is a file that exists only with the controller on. Among 38 eutrophication papers, a W2 output file or column name was confirmed in 0/38, and a reconstructable VPR in 2/38; unresolved rows remain `unknown`. The error is undetectable in the literature as published; undetectability is the finding.

**“DeGray and Columbia NSE values look like skill.”** They are labelled internal consistency in every table, run-card, and caption. Official decks contain no T or DO observations. If a referee wants isomorphic “NSE flips from negative to positive versus field data” at those sites, independent observations must be obtained first (Columbia: ORDEQ/USGS slough DO is a candidate; DeGray: 1980 profiles). Until then we will not write *skill*.

**“5/4/1/5 shows that smaller time steps are less stable.”** Only under official `DLTINTER=ON` knot interpolation at Long Lake. `DLTINTER=OFF` is 0/0/0/0. Columbia 120/360/720 s is 0/0/0. H1 < 0 has been seen at one waterbody. The claim we will defend is: report NHR (negative-thickness count, whether exit 0 hid it, `DLTINTER` state). The claim we will not defend is a cross-case CFL geometry law.

**“Turning TDGTA off deleted TDG.”** It deleted the gated evaluation file. SYSTDG still writes `TDG_output.csv`. ON ≡ OFF on that file (MAE = 0). Use of S as B is a VPR error.

**“21.2% exceedance in 2016–2025 validates the model.”** It does not. The model was not run after ~2011. The statistic supports reachable-range persistence only.

**“Columbia SOD in the Almeida band means diagenesis is calibrated.”** Parameters were transplanted from DeGray. 89.55% of wet cells fall in a Portuguese-reservoir scan grid; none exceed 3.0 g O₂ m⁻² d⁻¹. That is a sanity check on a missing example file, not a site calibration.

**“Full-text rate 9/38 undermines the audit.”** It limits precision on `unknown` rows. It does not reverse the Table 2 object-mixing result, which is concentrated in papers we did read or that the review text itself reinterprets. Confirmed-absent statements are reserved for codes that were positively established; unknowns stay unknown.

**“You are proposing a mandatory community standard from a small case set.”** No. VPR / controller-conditional evaluation / NHR are a **reporting recommendation** motivated by the demonstrated failure modes. We do not claim regulatory sufficiency or that the present cases prove these fields are complete for every W2 application.

### 6.3 Downgraded and refused claims

Relative to an earlier internal plan (v1) this manuscript **drops** two sentences: that the physical TDG variable is deleted when the controller is off, and that reducing DLTMAX generally increases geometric instability. Out-of-sample NSE is **refused** until `TMEND` is extended and 2016+ meteorology, boundaries, and outflows are prepared. Cross-version (v4.5.5 versus v5.0 beta) skill drift is not reported (optional task T3, not done). Exact fraction of simulated time spent at DLTMIN is not reported (needs instrumentation, T4).

What remains, and what we think is publishable as a GMD **methods-for-assessment** paper, is a **reporting recommendation**: publish VPR, publish controller state and reachable range, publish NHR. Without them, direct comparability of goodness-of-fit cannot generally be established from the metric alone. The present case set motivates those fields; it does not decree a mandatory community standard.

### 6.4 Relation to Almeida and Coelho (2025)

Almeida and Coelho (2025) is both a journal precedent (GMD accepts open, reproducible W2 evaluation) and an independent SOD magnitude anchor. Their article type evaluates sediment-diagenesis **process options**; ours is complementary: an auditable assessment layer **under** such performance statistics (Methods for assessment of models). Our Columbia mean 0.8762 g O₂ m⁻² d⁻¹ lies below their sediment-diagenesis best mean (1.07) and inside their 0.5–3.0 scan. We use that fact only as listed in Sect. 5.5. A future Morris/Sobol study of the transplanted `W2_diagenesis.npt` (plan T6) would be a different paper; 0.876 is not Columbia’s true SOD.

---

## 7 Conclusions

Goodness-of-fit values reported for different CE-QUAL-W2 applications should be treated as conditionally comparable: like-for-like comparison requires sufficient information on variable provenance, controller state, and numerical health.

1. **Variable provenance.** Same Bonneville run, same CCIW, *n* = 1614: *R*² stays in 0.508–0.551 while NSE is −2.804, +0.500, and −2.752. DeGray and Columbia reproduce the *R*²-blind / αβ-visible pattern as internal consistency, not as field skill. In the 38-paper eutrophication corpus, VPR is reconstructable 2/38 times and output files are named 0/38 times.

2. **Control-state / gated outputs.** The skill-best Bonneville series lives in `TDGTarget_output.csv` and vanishes when `TDGTA=OFF`. `TDG_output.csv` is a pre-control snapshot (ON/OFF MAE = 0) and is not B. Fifteen point five five percent of paired observations exceed the controller cap. DART shows the example observations are intact and that >120% hours remain common in 2016–2025; those years have no model NSE in this study.

3. **Numerical health.** Exit 0 can mask H1 < 0 → DLTMIN rollback. Counts 5/4/1/5 are a Long Lake, `DLTINTER=ON` knot result; `DLTINTER=OFF` is all zeros; H1 < 0 was not observed at completed Bonneville, Columbia, or DeGray runs. Report NHR. Do not generalize “smaller Δ*t* is less stable”.

4. **Protocol.** Evaluate W2 with a VPR, a controller-conditional statement including reachable range, and an NHR. `w2eval` writes those three blocks from cached JSON. These are recommended reporting elements, not a claim that the present cases prove regulatory sufficiency for every application. Official examples, as distributed, cannot support a calibration claim except at Bonneville: only that deck includes observations, Long Lake is missing `HabitatFiles/`, and Columbia diagenesis parameters used here are a DeGray transplant.

Until those practices are standard, a table of *R*² values across CE-QUAL-W2 studies should not be assumed to rank like-for-like evaluation objects.

---

## 8 Code and data availability

GMD requires a **Code and data availability** section before acknowledgements, with persistent public archives (e.g. Zenodo DOI) for the precise code/data versions used in a Methods for assessment paper ([GMD code and data policy](https://www.geoscientific-model-development.net/policies/code_and_data_policy.html); [manuscript types](https://www.geoscientific-model-development.net/about/manuscript_types.html)). **No Zenodo DOI has been minted for this draft.** Paths below are relative to the project root `I:\Projects\20260810-CE-QUAL-W2` (to be replaced by an archive tree at submission).

**Analysis JSON (authoritative numbers)**

- `06_PAPER/analysis/w3_tdgta_off_metrics.json` — Bonneville ON/OFF A/B/C/S
- `06_PAPER/analysis/w1_provenance_metrics.json` — DeGray T and Columbia DO internal consistency
- `06_PAPER/analysis/w4_cciw_vs_dart.json` — DART download, CCIW identity, exceedance, 2011 spill
- `06_PAPER/analysis/w5_lit_audit_summary.json` and `06_PAPER/analysis/w5_lit_audit.csv` — 38-paper audit
- `06_PAPER/analysis/w7_columbia_sod_vs_almeida.json` — SOD magnitude
- `06_PAPER/analysis/nhr_dlt_scan.json` — Long Lake × Columbia DLT scans
- `06_PAPER/analysis/nhr_existing_runs.json` — NHR for archived runs

**Run-cards**

- `06_PAPER/w2eval/w2eval.py`
- `06_PAPER/w2eval/cards/*.md` and `*.json`

**Scripts (recompute from existing output; do not require a new W2 integration)**

- `00_INDEX/eval_w3_tdgta_off.py`, `00_INDEX/eval_bonneville_tailwater.py`, `00_INDEX/eval_systdg_tdg.py`
- `00_INDEX/parse_nhr.py`, `00_INDEX/download_dart_cciw.py`
- `06_PAPER/analysis/w1_w7_provenance.py`

**Archived W2 output**

- `05_REPRO_RUNS/run_20260814_bonneville/` and `run_20260814_bonneville_notarget/`
- `05_REPRO_RUNS/run_20260811_fixed/` (DeGray, Long Lake, Columbia SED_DIAG OFF)
- `05_REPRO_RUNS/run_20260814_columbia_diag/`
- `05_REPRO_RUNS/run_20260815_ll_dlt_scan/` and `run_20260815_columbia_dlt_scan/`

**Observations**

- Example CCIW: `02_LIBRARY/06_examples/v5.0_beta/Bonneville_TDG/CCIW_TDG_Temp_2011-2015.csv`
- DART hours: `06_PAPER/data/dart_cciw/cciw_hourly_YYYY.csv` (2011–2025)

**Source (v4.5 tree used for line citations)**

- `02_LIBRARY/05_source/github_v4.5/model/w2_model_source/` (`w2_4_win.f90`, `layeraddsub.F90`, `update.F90`, `TDGtarget.f90`, `systdg.f90`, `withdrawal.f90`, `endsimulation.F90`)

**Executable used**

- `02_LIBRARY/07_executables/v4.5.5/w2_v455_ifx.exe`

DART data citation: Columbia River DART, Columbia Basin Research, University of Washington, Hourly Water Quality Measurements, https://cbr.washington.edu/dart/query/wqm_hourly (downloaded 2026-08-15). Almeida and Coelho (2025) reproduction package: https://doi.org/10.5281/zenodo.15775127.

---

## Appendix A: Figure file map

Paths relative to `06_PAPER/drafts/`. Full inventory: `P1_figure_inventory.md`. SciencePlots redraw 2026-08-16; filenames unchanged.

| Paper figure | Path | Status |
|---|---|---|
| Fig. 1 TDG time series | `../figures/W3_tdgta_on_off_timeseries.png` | exists |
| Fig. 2 TDG 1:1 | `../figures/W3_tdgta_on_off_scatter.png` | exists |
| Fig. 3 KGE bars (Bonneville) | `../figures/W3_tdgta_kge_decomposition.png` | exists |
| Fig. 3b DeGray KGE | `../figures/w1_degray_T_kge_bars.png` | exists |
| Fig. 3c Columbia KGE | `../figures/w1_columbia_DO_kge_bars.png` | exists |
| Fig. 4 combined *R*²–NSE + literature rug | `../figures/fig04_r2_vs_nse_literature.png` | exists |
| Fig. 5 reachable-range histogram | `../figures/fig05_tdg_reachable_range.png` | exists |
| Fig. 5 companion (annual >120%) | `../figures/w4_tdg_gt120_annual.png` | exists |
| Fig. 6 NHR scan | `../figures/nhr_dltmax_neg_thickness.png` | exists |
| Fig. 7 run-card graphic | `../figures/fig07_w2eval_runcard.png` | exists |
| Fig. 8 2011 spill | `../figures/w4_spill_tdgta_vs_dart.png` | exists |
| DeGray T panels | `../figures/w1_degray_T_*.png` | exist |
| Columbia DO panels | `../figures/w1_columbia_DO_*.png` | exist |
| Columbia SOD | `../figures/w7_columbia_sod_*.png` | exist |
| W4 library/DART companions | `../figures/w4_cciw_vs_dart_*.png`, `w4_spill_scatter.png`, `w4_tdg_annual_max.png` | exist |

---

## Author contributions (stub — CRediT-style)

- Conceptualization; Methodology; Software; Formal analysis; Investigation; Data curation; Writing — original draft; Writing — review & editing: project authors (to be named).
- Resources (model code and example decks): Cole, Wells, and the CE-QUAL-W2 community.
- Resources (observations): USACE NWD via DART and the official Bonneville example.

## Competing interests (stub)

The authors declare that they have no conflict of interest.

## Acknowledgements (stub)

CE-QUAL-W2 example decks and source are distributed by ERDC / Portland State University. DART is operated by Columbia Basin Research, University of Washington.

---

## References

Bennett, N. D., Croke, B. F. W., Guariso, G., Guillaume, J. H. A., Hamilton, S. H., Jakeman, A. J., Marsili-Libelli, S., Newham, L. T. H., Norton, J. P., Perrin, C., Pierce, S. A., Robson, B., Seppelt, R., Voinov, A. A., Fath, B. D., and Andreassian, V.: Characterising performance of environmental models, Environ. Model. Softw., 40, 1–20, https://doi.org/10.1016/j.envsoft.2012.09.011, 2013.

Almeida, M. and Coelho, P.: Evaluating the performance of CE-QUAL-W2 version 4.5 sediment diagenesis model, Geosci. Model Dev., 18, 6135–6161, https://doi.org/10.5194/gmd-18-6135-2025, 2025.

Benicio, S. H. M., Basso, R. E., and Formiga, K. T. M.: Global applications of the CE-QUAL-W2 model in reservoir eutrophication: a systematic review and perspectives for Brazil, Water, 16, 3556, https://doi.org/10.3390/w16243556, 2024.

Chang, C.-H., Cai, L.-Y., Lin, T.-F., Chung, C.-L., van der Linden, L., and Burch, M.: Assessment of the impacts of climate change on the water quality of a small deep reservoir in a humid-subtropical climatic region, Water, 7, 1687–1711, https://doi.org/10.3390/w7041687, 2015.

Cole, T. M. and Wells, S. A.: CE-QUAL-W2: a two-dimensional, laterally averaged, hydrodynamic and water quality model, version 3.1, Instruction Report EL-03-1, U.S. Army Engineer Research and Development Center, Vicksburg, Mississippi, 2003.

Columbia River DART, Columbia Basin Research, University of Washington: Hourly water quality measurements, https://cbr.washington.edu/dart/query/wqm_hourly, last access: 15 August 2026.

Gupta, H. V., Kling, H., Yilmaz, K. K., and Martinez, G. F.: Decomposition of the mean squared error and NSE performance criteria: implications for improving hydrological modelling, J. Hydrol., 377, 80–91, https://doi.org/10.1016/j.jhydrol.2009.08.003, 2009.

Lima Neto, I. E.: Modeling water quality in a tropical reservoir using CE-QUAL-W2: handling data scarcity, urban pollution and hydroclimatic seasonality, RBRH, 28, e8, https://doi.org/10.1590/2318-0331.282320230003, 2023.

Nash, J. E. and Sutcliffe, J. V.: River flow forecasting through conceptual models part I — a discussion of principles, J. Hydrol., 10, 282–290, https://doi.org/10.1016/0022-1694(70)90255-6, 1970.

Wells, S. A.: Basis of the CE-QUAL-W2 version 3 river basin hydrodynamic and water quality model, in: Proceedings of the 2nd Federal Interagency Hydrologic Modeling Conference, Las Vegas, Nevada, 28 July–1 August 2002, available at: https://pdxscholar.library.pdx.edu/cengin_fac/113/ (last access: 15 August 2026), 2002.
