# P2 roadmap: out-of-sample NSE (Bonneville TMEND → 2016–2025)

**Scope of this note:** how to do it. **Do not start multi-year W2 runs from this document.**

P1 already states `out_of_sample.computed_nse = false`. DART CCIW hours for 2016–2025 exist under `06_PAPER/data/dart_cciw/` and are used only for exceedance frequency, not model skill.

---

## 1. Why P1 cannot report OOS NSE today

| Fact | Implication |
|---|---|
| Official / reproduced control: `TMSTRT=40544`, `TMEND=40909` | Calendar ~2011-01-01 → 2012-01-01 only |
| Deck title mentions “2011–2015” and MET/QGT filenames include `2011_2015` | Files may hold multi-year forcing, but **the run stops at TMEND≈2011** |
| P1 skill window | Paired CCIW hours in JDAY **40613.583–40681.542** (*n*=1614), not the full model year |
| 2016–2025 DART | Obs only; no matching W2 series |

---

## 2. Inputs that must change (minimum)

All paths relative to a Bonneville SYSTDG working copy (e.g. `05_REPRO_RUNS/run_20260814_bonneville/Bonneville_SYSTDG/`).

| Input | Current (P1) | Change for 2016–2025 coverage |
|---|---|---|
| `w2_con.csv` → `TMEND` (and `YEAR` / date conventions) | `40909` | Extend through end of 2025 (Excel serial consistent with JDAY 40544 = 2011-01-01, origin 1899-12-30). Decide whether one continuous run or year-chunks. |
| Meteorology | `HOXO_DLS_BON_2011_2015_MET_withBP.csv` | Build **2016–2025** (or full 2011–2025) MET in the same column layout / units / time step. Source: HOXO / Dalles-class station product used for the official deck—do not invent columns. |
| Gate / structure outflow | `QGT_BON_2011_2015_daily_DSS-scaled.csv` | Extend QGT (and any DSS scaling recipe) through 2025. Prefer observed or authorized operations series; document scaling. |
| Upstream / boundary inflow | `THE_DALLES_OUTFLOW.csv` | Extend The Dalles outflow (flow + temperature/constituents if present) to match TMEND. |
| Distributed tributary | `BonnevilleDam_DistributedTributaryInflow.npt` | Extend or justify holding constant; document choice. |
| Tailwater / pool elevation (if time-varying) | `BON_TW_Elev_2011_2015.csv` (and related elev files) | Extend if the control file reads them for the new window. |
| Wind shelter / shade / bathymetry | `BON_WSC.npt`, `BON_SHD_1.npt`, `BON_NAVD88_BTH_2011.csv` | Usually static; verify no year-specific edits. |
| Observations for skill | Example `CCIW_TDG_Temp_2011-2015.csv` | For OOS, pair against **DART** `cciw_hourly_YYYY.csv` (already downloaded) with the **same** pairing rules as P1. |
| TDG controller tables | `w2_TDGtarget.csv`, `TDGdyntarget.csv`, `w2_systdg.npt` | Keep P1 settings for a fair ON comparison; any target-schedule change is a different experiment. |

Optional but recommended: turn off or thin **SPR/SNP/FLX** output for multi-year runs (P1 Bonneville year ≈ 400 MB, mostly SPR) so storage stays manageable.

---

## 3. Expected compute / storage (order of magnitude)

| Item | Estimate |
|---|---|
| Wall time, 1 year Bonneville (P1 timestamps) | ~35–40 min (17:44→18:20 on the 2026-08-14 machine) |
| 2016–2025 continuous (~10 y), **one** TDGTA state | ~6–8 h wall if linear in years |
| ON + OFF twins | ~12–16 h wall |
| Storage if SPR left on | ~4 GB per decade-scale twin; **avoid** |
| Storage if eval subset only (TSR/WDO/TDG*/flowbal/wrn) | tens of MB per year |

Chunked yearly runs (reset IC from prior year or cold start each Jan 1) are acceptable if documented; do not mix chunk protocols when quoting a single NSE.

---

## 4. Evaluation protocol (must match P1 VPR)

OOS NSE is only meaningful if the evaluation object is identical to P1 except for the calendar window.

1. **VPR (copy from P1 run-cards)**  
   - **A:** withdrawal / N2+DO Henry path used in Table 1  
   - **B:** `TDGTarget_output.csv` (post-control)  
   - **C:** TSR segment 40 `TDG`  
   - **S:** `TDG_output.csv` pre-control snapshot — diagnostic only; not a substitute for B  

2. **Declare `TDGTA` state** on every reported number (`ON` / `OFF`). Never pool ON and OFF series.

3. **Pairing**  
   - A/C: nearest-neighbour tolerance **0.05 d** (P1)  
   - B/S vs daily SYSTDG: **0.6 d** if the daily/hourly mismatch remains (P1)  
   - Document any change; a different tolerance is a different evaluation  

4. **Metrics**  
   Same panel as P1: *r*, *R*², NSE, PBIAS, MAE, KGE (α, β, *r*).  
   Flag `computed_nse=true` only when model output exists for the paired hours.

5. **Windows**  
   - Report skill for a declared season (e.g. spring spill window analogous to 40613–40681) **and/or** all valid paired hours in 2016–2025.  
   - Do **not** treat annual % hours >120% as NSE.

6. **Spill confounding**  
   Repeat the 2011 QGT vs DART vs controller spill comparison for OOS years if QGT is extended—controller reallocation can still inflate B skill.

---

## 5. Suggested sequence (when someone is ready to run)

1. Freeze P1 cards and JSON hashes.  
2. Build MET + QGT + The Dalles (+ elev) through 2025; checksum inputs.  
3. Set TMEND; dry-run one month; confirm `flowbal` / no `w2.err`.  
4. Run TDGTA ON then OFF (or year chunks); keep eval subset.  
5. Pair to DART; write `analysis/wX_oos_nse.json` with VPR + TDGTA fields.  
6. Only then update the manuscript Data/Results language.

Until step 5 finishes, P1 wording stands: no out-of-sample NSE.
