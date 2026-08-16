# -*- coding: utf-8 -*-
"""ROUND 2-04 caption academicization + light Conclusions polish."""
from pathlib import Path
import re

p = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\drafts\P1_GMD_draft_v2.md")
t = p.read_text(encoding="utf-8")

caps = {
    "**Table 1.** Bonneville TDG calibers versus CCIW. Kind = skill versus observations. B is absent when TDGTA=OFF. S is the SYSTDG pre-control snapshot, not a substitute for B. Baseline pairing tolerances: A/C = 0.05 d; B/S = 0.6 d (pairing-tolerance sensitivity in Appendix A). <!-- w3_tdgta_off_metrics.json -->":
    "**Table 1.** Bonneville TDG calibers versus CCIW observations (*n* = 1614; observational skill). B is the controller-specific series and is absent when `TDGTA=OFF`; S is the SYSTDG pre-control snapshot and is not a substitute for B. Baseline pairing tolerances are 0.05 d for A/C and 0.6 d for B/S (pairing-tolerance sensitivity in Appendix A). <!-- w3_tdgta_off_metrics.json -->",

    "**Figure 1.** Bonneville TDG time series for calibers A, B, C, and S with `TDGTA` ON and OFF, CCIW observations, and the 120% target cap (**observational skill** versus CCIW; not an internal-consistency panel). Paired evaluation occupies JDAY 40613.583–40681.542 (*n* = 1614), not the full model year.":
    "**Figure 1.** Bonneville TDG time series for calibers A, B, C, and S with `TDGTA` ON and OFF, CCIW observations, and the 120% controller target. Observational comparison with CCIW over JDAY 40613.583–40681.542 (*n* = 1614); not an internal-consistency panel.",

    "**Figure 2.** One-to-one scatter of the same calibers against CCIW (**observational skill**). OLS slopes 1.079 / 0.664 / 1.154 for ON A/B/C.":
    "**Figure 2.** One-to-one comparison of Bonneville TDG calibers A, B, and C against CCIW over the paired evaluation window (*n* = 1614; observational skill). Ordinary-least-squares slopes for the `TDGTA=ON` A/B/C series are 1.079, 0.664, and 1.154, respectively.",

    "**Figure 3.** KGE decomposition (*r*, α, β) for Bonneville ON/OFF calibers (**observational skill versus CCIW**). Companion **internal-consistency** decompositions (not field skill) for DeGray temperature and Columbia DO are provided with the Supporting Information.":
    "**Figure 3.** KGE components (*r*, α, β) for Bonneville ON/OFF TDG calibers versus CCIW (*n* = 1614; observational skill). DeGray temperature and Columbia DO companion panels (Supporting Information) are internal-consistency diagnostics only; primary aligned sample sizes are *n* = 2943 (DeGray) and *n* = 116 (Columbia TSR station pairs).",

    "**Table 2.** Structured audit of Benicio et al. (2024) Table 1 (*n* = 38). Review Table 2 *R*² object coding: **1** confirmed W2↔observation skill / **7** confirmed other objects / **4** unresolved. <!-- w5_lit_audit_summary.json -->":
    "**Table 2.** Structured literature-gap audit of the 38 studies selected by Benicio et al. (2024). Among the 12 *R*² entries in the review summary table, **1** is confirmed W2↔observation skill, **7** represent other evaluation objects, and **4** remain unresolved. This table audits reporting provenance and is not a pooled ranking of CE-QUAL-W2 skill. <!-- w5_lit_audit_summary.json -->",

    "**Figure 5.** Paired-window CCIW TDG histogram (JDAY 40613.583–40681.542, *n* = 1614) with 120% controller-cap line; 251/1614 = 15.55% of hours exceed 120% and are unreachable on gated B. Companion annual exceedance 2011–2025 is shown in the Supporting Information (**exceedance frequency only—not forecast skill**; model NSE ends near 2011).":
    "**Figure 5.** Distribution of paired CCIW TDG observations over JDAY 40613.583–40681.542 (*n* = 1614) relative to the 120% controller cap. Of the paired observations, **15.55% (251/1614)** exceed 120% and therefore lie outside the reachable range of gated B. Annual 2011–2025 exceedance frequencies (Supporting Information) are descriptive observation statistics only; no NSE is computed for 2016–2025.",

    "**Figure 8.** 2011 spill: QGT, TDGTA, and DART, including reallocation days 173.86 → 39.23 kcfs.":
    "**Figure 8.** Comparison of 2011 Bonneville spill from QGT, the TDGTA-controlled series, and DART over 365 paired days. On controller-reallocation days, mean DART and TDGTA spill are 173.86 and 39.23 kcfs, respectively. Descriptive controller/spill context; not out-of-sample TDG skill.",

    "**Figure 4.** *R*² versus NSE with evidence classes separated: **(a)** Bonneville ON A/B/C versus CCIW (**observational skill**); **(b)** DeGray temperature and Columbia DO primary pairs (**internal consistency only**—no independent observations); **(c)** Benicio et al. Table 2 *R*² as an audit strip (confirmed W2↔obs / other object / unresolved; **NSE was not available in the literature audit and is not inferred**). Panels (a) and (b) have different evaluation objects and must not be interpreted as a pooled skill comparison.":
    "**Figure 4.** *R*² versus NSE with evidence classes kept separate: **(a)** Bonneville `TDGTA=ON` A/B/C versus CCIW (*n* = 1614; observational skill); **(b)** DeGray temperature (*n* = 2943 for primary pairs) and Columbia DO (*n* = 116 for TSR station pairs), both internal consistency only; **(c)** the 12 *R*² entries from the 38-study literature audit, coded **1 / 7 / 4** (confirmed W2↔obs / other objects / unresolved). NSE was not available for the literature-audit entries and is not inferred. Panels (a) and (b) must not be pooled as a single skill comparison.",

    "**Table 5.** Negative-thickness counts for the Long Lake DLTMAX × DLTINTER scan (day-30 knot; DLTF held at 0.9). All eight jobs complete at JDAY 239.943 with exit 0. Add/sub = 3/3 at every point. Columbia DLTMAX 120/360/720 s (`DLTINTER=OFF`): 0/0/0. <!-- nhr_dlt_scan.json -->":
    "**Table 5.** Numerical-health diagnostic for eight Long Lake DLTMAX × `DLTINTER` configurations (day-30 schedule knots; DLTF = 0.9). All jobs complete at JDAY 239.943 with exit 0 and add/sub = 3/3. Negative-thickness warning counts are 5/4/1/5 for `DLTINTER=ON` at 20/50/100/200 s and 0/0/0/0 for `DLTINTER=OFF`. Columbia DLTMAX 120/360/720 s (`DLTINTER=OFF`): 0/0/0. NHR diagnostic only—not observational skill and not a universal timestep–stability law. <!-- nhr_dlt_scan.json -->",

    "**Figure 6.** Long Lake numerical-health scan. Negative surface-layer-thickness warning counts versus the **DLTMAX schedule knot at JDAY 30**. With `DLTINTER=ON`, this knot is the starting value for interpolation toward the JDAY-40 knot and is **not** the realized timestep or a hard DLTMAX over JDAY 30–40 (e.g. the 20 s knot has TSR-sampled window maximum DLT = 231.096 s). With `DLTINTER=OFF`, the specified values act as stepwise window caps. Counts are warning-line events, not unique model days. Reporting recommendation only—**not** a universal timestep-stability criterion.":
    "**Figure 6.** Long Lake numerical-health scan: negative surface-layer-thickness warning counts versus the DLTMAX schedule knot at JDAY 30. Counts are **5/4/1/5** under `DLTINTER=ON` and **0/0/0/0** under `DLTINTER=OFF`. Under interpolation the horizontal axis is a schedule knot, not the realized timestep (e.g. the nominal 20 s knot reaches TSR-sampled window maximum DLT = 231.096 s). Counts are warning-line events, not unique model days. Motivates NHR reporting; does not establish a universal timestep–stability relationship.",

    "**Figure 7.** Example three-block **evaluation record** (VPR, metrics panel, NHR) typeset from `w2eval`; *R*²/NSE/KGE remain **downstream** statistics on the card, not a fourth scientific pillar.":
    "**Figure 7.** Schematic three-block evaluation record (VPR, performance statistics, and NHR) from the run-card implementation. *R*², NSE, and KGE are downstream statistics on a defined evaluation object, not an additional scientific pillar.",

    "**Figure S1.** Columbia wet-cell SOD time series with 0.5–3.0 band and Almeida reference means (**transplanted-parameter plausibility check, not a Columbia calibration**).":
    "**Figure S1.** Columbia wet-cell sediment oxygen demand for JDAY ≥ 33 (*n* = 1081) relative to the 0.5–3.0 g O₂ m⁻² d⁻¹ comparison band. Parameters were transplanted from the DeGray template; magnitude-plausibility check only—not Columbia field calibration.",
}

missing = []
for a, b in caps.items():
    if a not in t:
        missing.append(a[:70])
    else:
        t = t.replace(a, b, 1)

# Conclusions: ensure 15.55% (251/1614) wording if not already
# DeGray/Columbia figure captions if still short
for old, new in [
    ("**Figure D1.** DeGray surface T2, Tvolavg, WDO, STR, and GATE time series (**internal consistency only**—no field observations).",
     "**Figure D1.** DeGray surface T2, volume-average temperature, WDO, structure, and gate temperatures on the same run (**internal consistency only**—no field observations; primary aligned *n* = 2943)."),
    ("**Figure D2.** DeGray 1:1 channel scatter (**internal consistency**; not observational skill).",
     "**Figure D2.** One-to-one comparisons among DeGray temperature output channels (**internal consistency**; not observational skill; primary *n* = 2943)."),
    ("**Figure D3.** DeGray *R*² versus NSE for channel pairs (**internal consistency**).",
     "**Figure D3.** *R*² versus NSE for DeGray temperature channel pairs (**internal consistency**; primary *n* = 2943)."),
    ("**Figure C1.** Columbia TSR DO at I=45/49/33 (**internal consistency only**—no field observations).",
     "**Figure C1.** Columbia TSR dissolved oxygen at segments I=45/49/33 over the aligned period (*n* = 116; **internal consistency only**—no field observations)."),
    ("**Figure C2.** Columbia DO scatter and *R*²–NSE (**internal consistency**; not observational skill).",
     "**Figure C2.** Columbia DO channel comparisons as scatter and *R*²–NSE diagnostics (TSR pairs *n* = 116; **internal consistency**; not observational skill)."),
]:
    if old in t:
        t = t.replace(old, new, 1)

# Strip any leftover Files:,
t = re.sub(r"\s*Files:,\.?", "", t)

p.write_text(t, encoding="utf-8")
print("caption updates done; missing", len(missing))
for m in missing:
    print("MISS", m)
