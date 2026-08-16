# P1 claim–evidence matrix (pre-submission freeze)

**Date:** 2026-08-16  
**Draft:** `P1_GMD_draft_v2.md`  
**Authority:** `06_PAPER/analysis/*.json` + `w2eval/cards/*.json`  
**Evidence classes:** observational skill | internal consistency | NHR | reproducibility / magnitude | literature gap  

Hard exclusions (never claim): **no OOS NSE**; **2016–2025 exceedance = descriptive only**; **Columbia SOD = transplanted magnitude check only**; **no “deleted physical quantity”**; **NHR ≠ universal timestep law**; **unknown ≠ confirmed absent**.

---

## Headline claims

| ID | Claim (falsifiable) | Evidence class | Primary tables / figures | JSON / card | Bound / exclusion |
|---|---|---|---|---|---|
| C1 | Same Bonneville run + same CCIW (*n*=1614): *R*² stays ~0.508–0.551 while NSE spans −2.804 / +0.500 / −2.752 across calibers A/B/C | Observational skill | Table 1; Figs 1–3; Fig. 4 panel (a) | `w3_tdgta_off_metrics.json`; `cards/bonneville_tdgta_on.*` | Case-specific; *R*² and NSE describe different properties; does not alone prove provenance |
| C1b | DeGray T2 vs Tvolavg: *R*²=0.9027, NSE=−0.5855 (*n*=2943); STR vs GATE: *R*²≈0.53, NSE=−6.58 | Internal consistency | Table 4; Figs D1–D3; Fig. 3b; Fig. 4 panel (b) | `w1_provenance_metrics.json`; `cards/degray_t_internal.*` | **Not** field skill; no T obs in deck |
| C1c | Columbia DO station pairs: highest-*R*² pair *R*²=0.6505, NSE=−1.4821 (*n*=116); wrong station > wrong layer (SNP sfc/bot NSE=0.91) | Internal consistency | Table 4; Figs C1–C2; Fig. 3c; Fig. 4 panel (b) | `w1_provenance_metrics.json`; `cards/columbia_do_internal.*` | **Not** field skill; no DO obs in deck |
| C1d | Literature: **VPR-core** yes 2/38 (5.3%); `vpr_variable=yes` 0/38 (file/column); Table 2 W2↔obs skill **1/7/4** (skill_true / skill_false / skill_unknown); *R*² without NSE 9/11 | Literature gap | Table 2; Fig. 4 panel (c) rug | `w5_lit_audit_summary.json`; `w5_lit_audit.csv` | Full text **9/38**; `unknown` not upgraded to absence; VPR-core ≠ full eight-field VPR |
| C1e | Pairing-tolerance scan (archived CCIW + ON; no W2): A/C NSE sign stays − and B stays + across scanned grids; Table 1 baselines unchanged (A/C 0.05 d; B/S 0.6 d); C *R*² 0.4502–0.5512 | Observational skill (sensitivity of evaluation object) | §3.3; Appendix B | `pairing_tolerance_scan.json` | Changing tol = different VPR object; **not** “robust to pairing”; not a uniquely correct tolerance |
| C2 | Skill-best series (NSE=+0.500, β≈1, paired max 120.09%) exists only in gated `TDGTarget_output.csv`; OFF → file absent; SYSTDG `TDG_output.csv` ON≡OFF (MAE=0) | Control-state / evaluation ambiguity (gates observational skill interpretation) | Table 1 B/S rows; Fig. 1; Fig. 5 | `w3_tdgta_off_metrics.json`; ON/OFF cards | **Not** “physical TDG deleted”; gated file ≠ physical state |
| C2b | Library CCIW ≈ DART (*n*=17805, MAE=0.026537, match 0.994945); 2016–2025 >120% = 21.2% (descriptive); 2011 spill realloc 173.8573→39.2308 kcfs | Observational identity + descriptive exceedance / spill context | Fig. 5 companion; Fig. 8 | `w4_cciw_vs_dart.json` | **`out_of_sample.computed_nse = false`**; exceedance ≠ forecast skill |
| C3 | Exit 0 can mask H1<0→DLTMIN rollback; Long Lake DLTINTER=ON counts 5/4/1/5 vs OFF 0/0/0/0 at day-30 knots 20/50/100/200 s | NHR | Table 5; Fig. 6 | `nhr_dlt_scan.json`; `nhr_existing_runs.json`; `cards/longlake_dlt_nhr.*` | Reporting recommendation; **not** universal Δ*t* law; H1<0 principally Long Lake |
| C4 | Evaluation record = VPR + control-state + NHR + run-card; `w2eval` writes cards from cached JSON | Reproducibility / protocol implementation | Fig. 7; Table 3 | `w2eval/`; five cards | Implementation, not a fourth scientific pillar; not “first validation of W2” |
| C4b | Columbia wet-cell SOD: *n*=1081, mean=0.8762, frac in 0.5–3.0 = 0.8955 (DeGray-template transplant) | Reproducibility / magnitude plausibility | Fig. S1; §5.5.1 | `w7_columbia_sod_vs_almeida.json`; Columbia card | **Not** Columbia calibration / scenario inference |

---

## Permitted vs refused language (quick map)

| May write | Must not write |
|---|---|
| Conditional comparability / interpretation | Absolute “never comparable” / “incomparable” as a blanket law |
| Internal consistency | DeGray/Columbia as observational skill or calibration rank |
| Gated file removed / absent | Physical TDG (or any state variable) deleted |
| NHR accompanies reported evaluation statistics | Mandatory community standard; smaller Δ*t* always less stable |
| Exceedance frequency 2016–2025 | Out-of-sample NSE / forecast skill for those years |
| Transplanted SOD magnitude check | Columbia diagenesis field calibration |
| Confirmed present / confirmed absent / unknown | Treat `unknown` as confirmed absence |

---

## Section ↔ matrix crosswalk

| Draft section | Matrix IDs |
|---|---|
| Abstract / §1 C1–C4 | C1–C4 + C1d/C1e bounds |
| §2 Evidence taxonomy | class definitions for all rows |
| §3.3 VPR / pairing | C1e |
| §3.8 W5 methods | C1d coding rules |
| §5.1 | C1, C1d |
| §5.2 | C2, C2b |
| §5.3 | C1b, C1c |
| §5.4 | C3 |
| §5.5 (+5.5.1 SOD) | C4, C4b |
| Appendix B | C1e |
| §6–§7 | bounds / refusals |

Freeze status: **local pre-sub 2026-08-16 (post 5-round Cursor×ChatGPT iteration)**. Update only if JSON regenerates change a headline number.
