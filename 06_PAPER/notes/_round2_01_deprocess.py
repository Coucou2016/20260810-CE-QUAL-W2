# -*- coding: utf-8 -*-
"""ROUND 2-01 de-processization edits for P1_GMD_draft_v2.md"""
from pathlib import Path
import re

p = Path(__file__).resolve().parents[1] / "drafts" / "P1_GMD_draft_v2.md"
text = p.read_text(encoding="utf-8")

old_fm = """<!--
P1 working draft for Geoscientific Model Development (Methods for assessment of models).
Not a final submission. Numbers follow analysis JSON / run-cards; notes are narrative only.
Do not treat DeGray temperature or Columbia DO metrics as skill versus observations.
Blueprint: P1_MERGED_BLUEPRINT.md. Prior structural draft: P1_GMD_draft_v1.md (retained).
-->

# Variable provenance, control-state outputs, and numerical health: a methods framework for assessing reported goodness-of-fit in CE-QUAL-W2 v4.5.5 applications (with v5.0 beta example inventory)

**Working Chinese title:** 变量溯源、控制状态输出与数值健康：面向 CE-QUAL-W2 v4.5.5（兼 v5.0 beta 算例清单）拟合优度报告的方法学评估框架

**Target journal:** *Geoscientific Model Development* (**Methods for assessment of models**)

**Version scope (title-locked):** Primary executable and hydrodynamic integrations use distributed **`w2_v455_ifx.exe` (v4.5.5)**. The demonstration corpus also **inventories** official example folders from **v5.0 beta** (Table 3); we do **not** claim a single-version paper or a cross-release skill comparison.

**Draft status:** v2 matured through ≥5 Cursor×ChatGPT advisor rounds (2026-08-16). Blueprint + claim–evidence matrix aligned; pairing-tolerance Appendix B added. Not a camera-ready submission. Zenodo archive **待补充** (not minted). Out-of-sample NSE was **not** computed.

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
"""

new_fm = """<!--
Manuscript for Geoscientific Model Development (Methods for assessment of models).
Numbers follow archived analysis records. DeGray temperature and Columbia DO metrics are internal consistency, not skill versus observations.
Authoring notes and JSON reconciliation live outside this submission-facing draft.
-->

# Variable provenance, control-state outputs, and numerical health: a methods framework for assessing reported goodness-of-fit in CE-QUAL-W2 v4.5.5 applications (with v5.0 beta example inventory)

**Intended article type:** *Geoscientific Model Development* — Methods for assessment of models.

All hydrodynamic integrations analysed here used CE-QUAL-W2 v4.5.5 (`w2_v455_ifx.exe`). Official v5.0 beta example folders are included only in the example inventory (Table 3); no cross-release skill comparison is made. Out-of-sample NSE was not computed. A persistent Zenodo archive of the paper-relevant materials is pending (**待补充**).

---

## Abstract
"""
if old_fm not in text:
    raise SystemExit("front matter block not found")
text = text.replace(old_fm, new_fm, 1)

text = text.replace(
    "An NHR is an **execution-diagnostic record**, not a convergence test or a numerical-stability certificate. It is parsed from `w2.wrn`, `w2.err`, SNP runtime footers, and (when present) TSR DLT samples (`00_INDEX/parse_nhr.py`). Recommended fields for this paper:",
    "An NHR is an **execution-diagnostic record**, not a convergence test or a numerical-stability certificate. It was derived programmatically from `w2.wrn`, `w2.err`, SNP runtime footers, and, where available, TSR timestep records. Recommended fields for this paper:",
)
text = text.replace(
    "`w2eval` is a minimum viable run-card generator (`06_PAPER/w2eval/w2eval.py`). It reads cached JSON, not the executable. Each card has three sections: VPR, metrics panel, NHR. Five cards exist: Bonneville TDGTA ON, Bonneville TDGTA OFF, Long Lake DLT/NHR, Columbia DO internal consistency plus SOD magnitude, and DeGray temperature internal consistency (`06_PAPER/w2eval/cards/`). The tool does not launch `w2_v455_ifx.exe`, does not recompute NSE, and does not draw figures. If the JSON and the run directory diverge, the card follows the JSON.",
    "`w2eval` is a minimal run-card generator that consumes the archived analysis records and writes the VPR, metrics, and NHR components. Five cards are provided for the Bonneville TDGTA ON/OFF cases, Long Lake DLT/NHR, Columbia DO internal consistency plus SOD magnitude, and DeGray temperature internal consistency. The tool neither launches CE-QUAL-W2 nor recomputes the performance metrics; when archived records and a run directory diverge, the card follows the archived analysis.",
)
text = text.replace("### 3.8 Literature audit methods (W5)", "### 3.8 Literature-audit methods")
text = text.replace("### 3.9 DART comparison methods (W4)", "### 3.9 DART comparison methods")
text = text.replace(
    "Hourly Cascade Island records were downloaded from Columbia River DART (Columbia Basin Research, University of Washington; source USACE NWD) for 2011–2025 using `sc=1` on the CSV endpoint. Library `Datetime` hour *h* on date *D* maps to DART `Hour = (h+1)×100` (hour-ending Pacific timestamp minus 1 h), verified on 2011-04-01. Exceedance percentages use hours with non-missing dissolved-gas percent as the denominator; CCIW winters are often missing. Out-of-sample NSE is explicitly not computed (`out_of_sample.computed_nse = false`). <!-- w4_cciw_vs_dart.json -->",
    "Hourly Cascade Island records were downloaded from Columbia River DART (Columbia Basin Research, University of Washington; source USACE NWD) for 2011–2025 using the public CSV endpoint with station code `sc=1`. Library `Datetime` hour *h* on date *D* maps to DART `Hour = (h+1)×100` (hour-ending Pacific timestamp minus 1 h), verified on 2011-04-01. Exceedance percentages use hours with non-missing dissolved-gas percent as the denominator; CCIW winters are often missing. Out-of-sample NSE was not computed. <!-- w4_cciw_vs_dart.json -->",
)

text = text.replace(
    "All hydrodynamic integrations used the distributed `w2_v455_ifx.exe`. We did not rerun the model for this manuscript; metrics are recomputed from archived output in `05_REPRO_RUNS/`.",
    "All hydrodynamic integrations used the distributed `w2_v455_ifx.exe`. Metrics reported here were recomputed from archived model outputs; no new hydrodynamic integrations were performed for the present analysis.",
)
text = text.replace(
    "**Bonneville Dam (skill versus observations).** Official SYSTDG example; `TDGTA=ON` in `05_REPRO_RUNS/run_20260814_bonneville/Bonneville_SYSTDG` and `TDGTA=OFF` in `…/run_20260814_bonneville_notarget/…`. Control file `TMSTRT = 40544`, `TMEND = 40909` (Excel serial; JDAY 40544 = 2011-01-01, origin 1899-12-30). <!-- w4_cciw_vs_dart.json --> Both runs reach the end-of-period criterion used by the project runner (`flowbal` last JDAY 40908; OFF `c_wdo` last JDAY 40909) without `w2.err`. Observations are the example file `CCIW_TDG_Temp_2011-2015.csv` (Cascade Island tailwater). Valid CCIW TDG does not cover the calendar year: all 1614 paired hours fall in JDAY 40613.583–40681.542 (about 11 March–18 May 2011). <!-- w3_tdgta_off_metrics.json --> The plan window 40544–40910 is the model window, not the paired evaluation window.",
    "**Bonneville Dam (skill versus observations).** Official SYSTDG example evaluated under documented `TDGTA=ON` and `TDGTA=OFF` configurations. Control file `TMSTRT = 40544`, `TMEND = 40909` (Excel serial; JDAY 40544 = 2011-01-01, origin 1899-12-30). <!-- w4_cciw_vs_dart.json --> Both integrations reach the prescribed simulation endpoint without a fatal `w2.err`. Observations are the example file `CCIW_TDG_Temp_2011-2015.csv` (Cascade Island tailwater). Valid CCIW TDG does not cover the calendar year: all 1614 paired hours fall in JDAY 40613.583–40681.542 (about 11 March–18 May 2011). <!-- w3_tdgta_off_metrics.json --> The full model period therefore differs from the observation-paired evaluation period reported below.",
)
text = text.replace(
    "**DeGray Reservoir (internal consistency, no observations).** `05_REPRO_RUNS/run_20260811_fixed/DeGray Reservoir with sediment diagenesis and vertical algae migration`. JDAY 64.5–358.7. Searches of v4.5.5 and v5.0 beta example folders found no independent temperature or DO observations. Metrics compare output channels on the same run.",
    "**DeGray Reservoir (internal consistency, no observations).** Official DeGray sediment-diagenesis example; evaluation window JDAY 64.5–358.7. Searches of v4.5.5 and v5.0 beta example folders found no independent temperature or DO observations. Metrics compare output channels on the same run.",
)
text = text.replace(
    "**Columbia Slough Estuary (internal consistency, no observations).** Hydrodynamics and DO from `05_REPRO_RUNS/run_20260814_columbia_diag/` with `SED_DIAG=ON`. Official `w2_con.csv` requests sediment diagenesis but the example does not ship `W2_diagenesis.npt`. Parameters were copied from DeGray, with region-2 end segment 31 → 50. That transplant is **not** a Columbia calibration. The series is short: TSR pairing *n* = 116 over JDAY 32–55 (~23 days). A `SED_DIAG=OFF` companion run exists at `run_20260811_fixed`; ON versus OFF DO is a process-switch comparison, not a provenance comparison, and is not used as Contribution 1 evidence.",
    "**Columbia Slough Estuary (internal consistency, no observations).** Hydrodynamics and DO under `SED_DIAG=ON`. Official `w2_con.csv` requests sediment diagenesis but the example does not ship `W2_diagenesis.npt`. Parameters were copied from DeGray, with region-2 end segment 31 → 50. That transplant is **not** a Columbia calibration. The series is short: TSR pairing *n* = 116 over JDAY 32–55 (~23 days). A `SED_DIAG=OFF` companion integration was also archived; ON versus OFF DO is a process-switch comparison, not a provenance comparison, and is not used as Contribution 1 evidence.",
)
text = text.replace(
    "**Long Lake (numerical health, no observations).** Official DLT schedule (`NDLT = 6`, `DLTMIN = 0.1` s, `DLTINTER=ON`). Baseline `run_20260811_fixed/Long Lake` and the DLTMAX scan `run_20260815_ll_dlt_scan/` (day-30 knot 20/50/100/200 s × `DLTINTER` ON/OFF). The distribution omits `HabitatFiles/`; without that directory the habitat output path in `w2_habitat.npt` raises Intel Fortran severe (29). Completed scan jobs all reach JDAY 239.943 with exit 0.",
    "**Long Lake (numerical health, no observations).** Official DLT schedule (`NDLT = 6`, `DLTMIN = 0.1` s, `DLTINTER=ON`), with a DLTMAX schedule-knot scan at day 30 (20/50/100/200 s × `DLTINTER` ON/OFF). The distribution omits `HabitatFiles/`; without that directory the habitat output path in `w2_habitat.npt` raises Intel Fortran severe (29). Completed scan jobs all reach JDAY 239.943 with exit 0.",
)

# Caption cleanup
out_lines = []
for line in text.splitlines():
    if line.startswith("**Figure ") or line.startswith("**Figure S"):
        line = re.sub(r"\s*File: `[^`]+` \(exists\)\.?", "", line)
        line = re.sub(r"\s*Companions?:[^.]*\(exist[s]?[^)]*\)\.?", "", line)
        line = re.sub(r"\s*Sources?:[^.]*\.", "", line)
        line = re.sub(
            r"\s*Companion annual exceedance 2011–2025: `[^`]+` \(exists; ([^)]+)\)\.?",
            r" Companion annual exceedance 2011–2025 is shown in the Supporting Information (\1).",
            line,
        )
        line = re.sub(r"\s*Companion scatter: `[^`]+` \(exists\)\.?", "", line)
        line = re.sub(r"\s*Histogram: `[^`]+` \(exists\)\.?", "", line)
        line = re.sub(
            r"\s*Library versus DART identity plots: `[^`]+`, `[^`]+` \(exist\)\.?",
            "",
            line,
        )
        line = re.sub(
            r"Companion \*\*internal-consistency\*\* decompositions \(not field skill\): DeGray temperature `[^`]+`; Columbia DO `[^`]+` \(both exist\)\. Core panel: `[^`]+` \(exists\)\.",
            "Companion **internal-consistency** decompositions (not field skill) for DeGray temperature and Columbia DO are provided with the Supporting Information.",
            line,
        )
        line = re.sub(r"\s*`\.\./figures/[^`]+`", "", line)
        line = re.sub(r"\s*`\.\./w2eval/[^`]+`", "", line)
        line = re.sub(r"\s*\(exists\)\.?", "", line)
        line = re.sub(r"\s*\(exist\)\.?", "", line)
        line = re.sub(r"  +", " ", line).rstrip()
        if line and not line.endswith("."):
            line = line.rstrip(".") + "."
    out_lines.append(line)
text = "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")

text = text.replace(
    "We therefore write three sentences and only these three:\n\n1. The skill-best, β ≈ 1, 120.1%-capped series exists only in the controller-gated file `TDGTarget_output.csv`. OFF, that file is gone, so a freeze-the-metric / toggle-the-controller experiment cannot be done on path B.\n2. The physical TDG variable is not deleted. SYSTDG still writes a pre-control snapshot to `TDG_output.csv`. That snapshot cannot replace B.\n3. The 120% cap is a controller artefact, not a SYSTDG formula ceiling (hard cap in the metrics JSON: 145%). Observed paired maximum is 129.1%; 15.55% of paired hours exceed 120% and are structurally unreachable on B.",
    "These results establish three distinctions. The skill-best, β ≈ 1, 120.1%-capped series exists only in the controller-gated file `TDGTarget_output.csv`; when `TDGTA` is off that file is absent, so a freeze-the-metric / toggle-the-controller experiment cannot be performed on path B. Disabling the controller does not remove the physical TDG state, because SYSTDG continues to write the pre-control snapshot to `TDG_output.csv`, which cannot replace B. The 120% bound is a property of the controller pathway rather than a ceiling of the SYSTDG TDG formulation (model hard cap 145%); the observed paired maximum is 129.1%, and 15.55% of paired hours exceed 120% and are structurally unreachable on B.",
)
text = text.replace(
    "Library CCIW versus DART hourly TDG, 2011–2015, both valid: *n* = 17805, MAE = 0.026537%, RMSE = 0.04124%, |Δ| ≤ 0.051 match rate = 0.994945. <!-- w4_cciw_vs_dart.json --> Five hours differ by more than 1% (max |Δ| = 1.9), almost all in 2011–2012; 2013–2015 match at 1.0 within 0.05. Verdict recorded in JSON: `library_is_dart_rounded`. We find no evidence that the example observations were materially rewritten.",
    "Library CCIW versus DART hourly TDG, 2011–2015, both valid: *n* = 17805, MAE = 0.026537%, RMSE = 0.04124%, |Δ| ≤ 0.051 match rate = 0.994945. <!-- w4_cciw_vs_dart.json --> Five hours differ by more than 1% (max |Δ| = 1.9), almost all in 2011–2012; 2013–2015 match at 1.0 within 0.05. The library series is consistent with rounded DART values. We find no evidence that the example observations were materially rewritten.",
)
text = text.replace(
    "Among DART hours with non-missing TDG, 14.6842% exceed 120% in 2011–2015 (valid hours *n* = 17924) and 21.2% exceed 120% in 2016–2025 (*n* = 40434). Annual fractions are not a stationary 15%: 2015 has 0% of valid hours >120% (annual max 118.97%); 2017 has 46.9214% (annual max 131.38%). The cap problem does not age out of the record. **These percentages are not forecast skill.** The reproduced model’s `TMEND = 40909` covers about 2011 only. JSON flag: `out_of_sample.computed_nse = false`.",
    "Among DART hours with non-missing TDG, 14.6842% exceed 120% in 2011–2015 (valid hours *n* = 17924) and 21.2% exceed 120% in 2016–2025 (*n* = 40434). Annual fractions are not a stationary 15%: 2015 has 0% of valid hours >120% (annual max 118.97%); 2017 has 46.9214% (annual max 131.38%). The cap problem does not age out of the record. **These percentages are not forecast skill.** The reproduced model’s `TMEND = 40909` covers about 2011 only; out-of-sample NSE was not computed.",
)

text = text.replace(
    "**Table 3.** Official example suites inspected in this project (v4.5.5 eight folders + v5.0 beta nine folders = 17). Cells other than Bonneville, Columbia, DeGray, and Long Lake are inventory facts (folder exists), not independent run audits. We do not invent pass/fail for Detroit, Spokane, particle tracking, or cascade cases.\n\n| Suite | Example folder | Field observations in the distributed deck | Verified run defect (this project) |",
    "**Table 3.** Official example suites included in the audit (v4.5.5 eight folders + v5.0 beta nine folders = 17). Execution outcomes are reported only for Bonneville, Columbia, DeGray, and Long Lake; the remaining entries document example availability and were not treated as independent run audits.\n\n| Suite | Example folder | Field observations in the distributed deck | Execution status in the present audit |",
)
text = text.replace(
    "Project notes further record that upstream Git distribution of Windows executables as Git LFS pointers means a naive clone does not yield a runnable `exe`. We did not re-hash LFS pointers for this draft; the working executable used throughout is the local `02_LIBRARY/07_executables/v4.5.5/w2_v455_ifx.exe`.",
    "The integrations analysed here used the distributed CE-QUAL-W2 v4.5.5 Windows executable `w2_v455_ifx.exe`. The executable itself is not redistributed with the manuscript repository; model source and executable availability follow the upstream CE-QUAL-W2 distribution.",
)
text = text.replace(
    "Columbia SOD, after the DeGray-template transplant, is an order-of-magnitude check against the Almeida and Coelho (2025) zero-order/hybrid scan band 0.5–3.0 g O₂ m⁻² d⁻¹ (a user-specified Portuguese-reservoir experiment, not a global ecological range).",
    "Columbia SOD, after the DeGray-template transplant, is an order-of-magnitude check against the 0.5–3.0 g O₂ m⁻² d⁻¹ range examined by Almeida and Coelho (2025); that published Portuguese-reservoir experiment is used as a magnitude reference and not as a global ecological range or a Columbia calibration.",
)

# Discussion rewrite via markers
start = text.find("### 6.2 Likely referee objections")
end = text.find("## 7 Conclusions")
if start < 0 or end < 0:
    raise SystemExit("discussion markers not found")
new_disc = """### 6.2 Scope and interpretation limits

The general principle that metrics depend on the evaluation protocol is not new (Bennett et al., 2013). The contribution here is operational for CE-QUAL-W2: three concrete reporting elements (VPR, controller-conditional evaluation, NHR) plus W2-specific examples showing how output provenance, controller gating, and internal numerical events change the interpretation of otherwise conventional goodness-of-fit numbers.

The demonstration corpus exercises distinct failure modes rather than validating a single three-part framework across all 17 official examples. Bonneville supplies the principal observation-based skill contrast; DeGray and Columbia provide within-run internal-consistency diagnostics because their official decks do not include the independent observations required for observational-skill evaluation; Long Lake informs NHR existence under exit 0; SOD is a transplanted-parameter plausibility check; Table 3 cells outside those decks are inventory facts, not independent validation runs.

Caliber A follows the Henry conversion in `withdrawal.f90`; caliber C is a TSR column named TDG; caliber B exists only with the controller on. Among 38 eutrophication papers, a W2 output file or column name was confirmed in 0/38, and a paper-level **VPR-core** criterion is met in 2/38; unresolved rows remain `unknown`. Undetectability of output-channel identity in the published literature is itself a finding.

The Long Lake scan demonstrates that exit status alone can omit relevant numerical-health information. The observed 5/4/1/5 pattern is specific to the tested `DLTINTER=ON` schedule knots and does not establish a general timestep–stability law; `DLTINTER=OFF` yields 0/0/0/0, and Columbia’s smaller DLTMAX scan remains 0/0/0. Disabling `TDGTA` removes the controller-specific output file, not the underlying physical TDG variable; SYSTDG still writes `TDG_output.csv`, and ON ≡ OFF on that file (MAE = 0).

The study does not estimate out-of-sample NSE for 2016–2025 because the reproduced simulation terminates near 2011; the later observations are used solely to characterize TDG exceedance frequency. Cross-version skill differences between v4.5.5 and v5.0 beta are outside the scope of this study. The fraction of simulated time spent at `DLTMIN` is not quantified because this would require additional source-level instrumentation. Columbia SOD parameters were transplanted from DeGray: 89.55% of wet cells fall in the Almeida and Coelho (2025) 0.5–3.0 g O₂ m⁻² d⁻¹ scan; none exceed 3.0. That is a sanity check on a missing example file, not a site calibration. Full-text availability for 9/38 papers limits precision on `unknown` rows but does not reverse the Table 2 object-mixing result among coded entries. VPR / controller-conditional evaluation / NHR are a **reporting recommendation** motivated by the demonstrated failure modes, not a decree of regulatory sufficiency for every W2 application.

### 6.3 Relation to Almeida and Coelho (2025)

Almeida and Coelho (2025) is both a journal precedent (GMD accepts open, reproducible W2 evaluation) and an independent SOD magnitude anchor. Their article type evaluates sediment-diagenesis **process options**; ours is complementary: an auditable assessment layer **under** such performance statistics (Methods for assessment of models). Our Columbia mean 0.8762 g O₂ m⁻² d⁻¹ lies below their sediment-diagenesis best mean (1.07) and inside their 0.5–3.0 scan. We use that fact only as listed in Sect. 5.5. A formal sensitivity analysis of the transplanted diagenesis parameters would constitute a separate investigation and is not inferred from the present magnitude check; 0.876 is not Columbia’s true SOD.

---

"""
text = text[:start] + new_disc + text[end:]

text = text.replace(
    "pairing-tolerance scans of archived ON outputs (Appendix B)",
    "pairing-tolerance scans of archived ON outputs (Appendix A)",
)
text = text.replace(
    "(pairing-tolerance sensitivity in Appendix B)",
    "(pairing-tolerance sensitivity in Appendix A)",
)
text = text.replace(
    "`w2eval` writes those three blocks from cached JSON.",
    "`w2eval` writes those three blocks from archived analysis records.",
)
text = text.replace(
    "`w2eval` copies these scores from analysis JSON and does not reimplement the formulae.",
    "`w2eval` copies these scores from the archived analysis records and does not reimplement the formulae.",
)
text = text.replace(
    "Coding definitions follow `w5_lit_audit_summary.json`.",
    "Coding definitions follow the archived literature-audit summary record (`w5_lit_audit_summary.json` in the accompanying repository).",
)

# Code availability
c0 = text.find("## 8 Code and data availability")
c1 = text.find("## Appendix A: Figure file map")
if c0 < 0 or c1 < 0:
    raise SystemExit("code/appendix markers not found")
new_code = """## 8 Code and data availability

The public development repository for this study is https://github.com/Coucou2016/20260810-CE-QUAL-W2. Paper-facing analysis records are under `06_PAPER/analysis/`, and the run-card implementation and example cards are under `06_PAPER/w2eval/`. Reproducibility utilities used for the reported analyses are provided under `00_INDEX/`. Archived model outputs used to recompute metrics are retained under `05_REPRO_RUNS/` where redistribution is permitted. Observation extracts used here include the official Bonneville CCIW example series and DART hourly Cascade Island downloads under `06_PAPER/data/dart_cciw/`.

A frozen persistent archive of the paper-relevant code and data is pending. Zenodo DOI: **待补充**. GitHub alone is not a substitute for a persistent archive under the GMD code and data policy (https://www.geoscientific-model-development.net/policies/code_and_data_policy.html).

The CE-QUAL-W2 executable is not redistributed in this repository and should be obtained from the upstream CE-QUAL-W2 distribution. Any artefacts that cannot be redistributed will be identified with their access source and restriction in the archived release. Line citations to model source (`w2_4_win.f90`, `layeraddsub.F90`, `update.F90`, `TDGtarget.f90`, `systdg.f90`, `withdrawal.f90`, `endsimulation.F90`) refer to the v4.5 source tree used for this study.

DART data citation: Columbia River DART, Columbia Basin Research, University of Washington, Hourly Water Quality Measurements, https://cbr.washington.edu/dart/query/wqm_hourly (downloaded 2026-08-15). Almeida and Coelho (2025) reproduction package: https://doi.org/10.5281/zenodo.15775127.

---

"""
# drop old Appendix A figure map; keep Appendix B content as Appendix A
b0 = text.find("## Appendix B: Pairing-tolerance scan")
if b0 < 0:
    raise SystemExit("appendix B not found")
rest = text[b0:]
rest = rest.replace(
    "## Appendix B: Pairing-tolerance scan (no W2 rerun)\n\nNearest-neighbour pairing of archived CCIW observations to TDGTA=ON Bonneville outputs. Each row is a distinct VPR evaluation object. Baseline rows match Table 1. Source: `06_PAPER/analysis/pairing_tolerance_scan.json`.",
    "## Appendix A: Pairing-tolerance scan (no W2 rerun)\n\nNearest-neighbour pairing of archived CCIW observations to TDGTA=ON Bonneville outputs. Each row is a distinct VPR evaluation object. Baseline rows match Table 1. Source analysis record: `pairing_tolerance_scan.json` in the accompanying repository.",
    1,
)
text = text[:c0] + new_code + rest

text = text.replace(
    "## Author contributions (stub — CRediT-style)",
    "## Author contributions (CRediT-style; names 待补充)",
)
text = text.replace("## Competing interests (stub)", "## Competing interests")
text = text.replace("## Acknowledgements (stub)", "## Acknowledgements")

p.write_text(text, encoding="utf-8")
print("wrote", p)
for pat in [
    "Cursor×ChatGPT",
    "Working Chinese",
    "Unresolved discrepancies",
    "User steps to mint",
    "Appendix B",
    "plan T6",
    "Likely referee",
    "File: `../figures",
    "Verified run defect (this project)",
    "I:\\",
]:
    print(repr(pat), text.count(pat))
