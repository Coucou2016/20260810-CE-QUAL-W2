# Run-card: Long Lake official vs DLTMAX scan (DLTINTER ON/OFF)

- **card_id:** `longlake_dlt_nhr`
- **generated:** 2026-08-15T01:27:26
- **mode:** `numerical_health`
- **run:** `05_REPRO_RUNS/run_20260815_ll_dlt_scan/`

All INTER ON scan points Normal-terminate with exit 0 while wrn still records 1–5 negative-thickness rollbacks. INTER ON counts 5/4/1/5 are non-monotonic (official 100 s is the valley) but INTER OFF is 0/0/0/0. Do not generalize 'smaller timestep is less stable'. Report NHR: neg-thickness count, whether exit 0 hid it, and DLTINTER state.

---

## 1. VPR — variable provenance

| caliber | file | column | I | layer | unit | derived from | time support | pairing |
|---|---|---|---|---|---|---|---|---|
| NHR.wrn | `w2.wrn` | Negative surface layer thickness / Add layer / Subtract layer | event segment (typically 3 at Long Lake) | KT surface layer H1 | m (H1, Z); s (DLT) | w2_4_win.f90 L1415–1424 rollback to DLTMIN; layeraddsub.F90 thresholds | event log (not a water-quality series) | n/a |
| NHR.snp | `snp1.opt` | Total iterations, # of violations (NV), Normal termination | n/a | n/a | count; seconds | endsimulation.F90; NV includes CFL/viscosity, not just H1<0 | end-of-run summary | n/a |
| NHR.tsr_dlt | `tsr_1_seg2.csv` | DLT | 2 | n/a | s | TSR output-step sample of DLT; misses single-step DLTMIN rollbacks | TSR dump interval; window JDAY 30–40 | n/a |
| NHR.con | `w2_con.csv` | NDLT, DLTMIN, DLTINTER, DLTD, DLTMAX, DLTF | n/a | n/a | s | official schedule; scan edits only DLTMAX at DLTD=30 | DLTINTER=ON interpolates between knots (update.F90 L152–163) | n/a |

- **NHR.tsr_dlt:** INTER ON + DLTMAX=20 still has window DLT max ~230 s because day-40 knot is 1800 s.

## 2. Metrics panel

- **kind:** `no_observation_skill`
- **note:** Long Lake official example has no independent T/DO/TDG observations. R²/NSE/KGE/PBIAS/MAE vs field data are not applicable. The evaluation object is NHR. Columbia DLTMAX 120/360/720 (INTER OFF) neg-thickness = [0, 0, 0] — H1<0 is not a cross-case law.

_No skill metrics (see kind/note)._

### DLTMAX × DLTINTER negative-thickness counts

| DLTMAX @ JDAY 30 | DLTINTER=ON | DLTINTER=OFF |
|---:|---:|---:|
| 20 s | 5 | 0 |
| 50 s | 4 | 0 |
| 100 s | 1 | 0 |
| 200 s | 5 | 0 |

## 3. NHR — numerical health

| run | neg thickness | Add | Sub | exit 0 masks rollback | DLTINTER | Normal term | wrn |
|---|---:|---:|---:|---|---|---|---|
| official baseline (INTER ON, knot 100 s) | 1 | 3 | 3 | yes | ON | yes | `05_REPRO_RUNS/run_20260811_fixed/Long Lake/w2.wrn` |
| prior DLTMAX=20 INTER ON (run_20260814_longlake_dlt) | 5 | 3 | 3 | yes | ON | yes | `05_REPRO_RUNS/run_20260814_longlake_dlt/Long Lake/w2.wrn` |
| scan INTER ON 20 s | 5 | 3 | 3 | yes | ON | yes | `05_REPRO_RUNS/run_20260815_ll_dlt_scan/dltmax_20/w2.wrn` |
| scan INTER ON 50 s | 4 | 3 | 3 | yes | ON | yes | `05_REPRO_RUNS/run_20260815_ll_dlt_scan/dltmax_50/w2.wrn` |
| scan INTER ON 100 s (official knot) | 1 | 3 | 3 | yes | ON | yes | `05_REPRO_RUNS/run_20260815_ll_dlt_scan/dltmax_100/w2.wrn` |
| scan INTER ON 200 s | 5 | 3 | 3 | yes | ON | yes | `05_REPRO_RUNS/run_20260815_ll_dlt_scan/dltmax_200/w2.wrn` |
| scan INTER OFF 20 s | 0 | 3 | 3 | no | OFF | yes | `05_REPRO_RUNS/run_20260815_ll_dlt_scan/dltmax_20_interoff/w2.wrn` |
| scan INTER OFF 50 s | 0 | 3 | 3 | no | OFF | yes | `05_REPRO_RUNS/run_20260815_ll_dlt_scan/dltmax_50_interoff/w2.wrn` |
| scan INTER OFF 100 s | 0 | 3 | 3 | no | OFF | yes | `05_REPRO_RUNS/run_20260815_ll_dlt_scan/dltmax_100_interoff/w2.wrn` |
| scan INTER OFF 200 s | 0 | 3 | 3 | no | OFF | yes | `05_REPRO_RUNS/run_20260815_ll_dlt_scan/dltmax_200_interoff/w2.wrn` |

- **official baseline (INTER ON, knot 100 s) window DLT:** min=53.941 s, max=227.041 s (jday[30.0,40.0))
- **official baseline (INTER ON, knot 100 s) NV:** 2395 (1.06% of NIT=226804); NV is not H1<0 count.
- **prior DLTMAX=20 INTER ON (run_20260814_longlake_dlt) window DLT:** min=27.39 s, max=231.096 s (jday[30.0,40.0))
- **prior DLTMAX=20 INTER ON (run_20260814_longlake_dlt) NV:** 2494 (1.08% of NIT=230624); NV is not H1<0 count.
- **scan INTER ON 20 s window DLT:** min=27.39 s, max=231.096 s (jday[30.0,40.0))
- **scan INTER ON 20 s NV:** 2494 (1.08% of NIT=230624); NV is not H1<0 count.
- **scan INTER ON 50 s window DLT:** min=57.288 s, max=254.189 s (jday[30.0,40.0))
- **scan INTER ON 50 s NV:** 2586 (1.14% of NIT=227773); NV is not H1<0 count.
- **scan INTER ON 100 s (official knot) window DLT:** min=53.941 s, max=227.041 s (jday[30.0,40.0))
- **scan INTER ON 100 s (official knot) NV:** 2395 (1.06% of NIT=226804); NV is not H1<0 count.
- **scan INTER ON 200 s window DLT:** min=53.011 s, max=229.709 s (jday[30.0,40.0))
- **scan INTER ON 200 s NV:** 2837 (1.26% of NIT=225647); NV is not H1<0 count.
- **scan INTER OFF 20 s window DLT:** min=20.0 s, max=20.0 s (jday[30.0,40.0))
- **scan INTER OFF 20 s NV:** 16803 (7.75% of NIT=216840); NV is not H1<0 count.
- **scan INTER OFF 50 s window DLT:** min=50.0 s, max=50.0 s (jday[30.0,40.0))
- **scan INTER OFF 50 s NV:** 16878 (8.84% of NIT=191035); NV is not H1<0 count.
- **scan INTER OFF 100 s window DLT:** min=100.0 s, max=100.0 s (jday[30.0,40.0))
- **scan INTER OFF 100 s NV:** 16915 (9.28% of NIT=182227); NV is not H1<0 count.
- **scan INTER OFF 200 s window DLT:** min=109.497 s, max=200.0 s (jday[30.0,40.0))
- **scan INTER OFF 200 s NV:** 17018 (9.48% of NIT=179497); NV is not H1<0 count.

NHR fields: negative surface-layer thickness count; Add/Sub layer; whether exit 0 + Normal termination hid DLTMIN rollback; DLTINTER; source `w2.wrn` path. Layer add/sub is a geometric threshold event, not by itself a failure.

## Notes

- Official DLTINTER=ON: day-30 knot is interpolated toward 1800 s at day 40; tightening DLTMAX to 20 s does not cap window DLT at 20 s.
- INTER OFF makes window DLT equal the set cap; all four points have 0 negative-thickness events.
- NV (timestep violations) is not the H1<0 count: INTER OFF 20 s has high NV and 0 neg-thickness.
- H1<0 observed only at Long Lake among completed Bonneville/Columbia/DeGray runs.
- Keep NHR as a required report item. Treat non-monotonic vs DLTMAX as conditional on DLTINTER=ON knot interpolation, not as a general CFL result.

## Figures (existing, not regenerated)

- `06_PAPER/figures/nhr_dltmax_neg_thickness.png`
- `06_PAPER/figures/nhr_dltmax_layers_dltmin.png`
- `06_PAPER/figures/nhr_dltmax_heatmap.png`

## Sources

- `06_PAPER/analysis/nhr_dlt_scan.json`
- `06_PAPER/analysis/nhr_existing_runs.json`
- `00_INDEX/parse_nhr.py`
- `00_INDEX/run_ll_dlt_scan.py`

_Generated by `06_PAPER/w2eval/w2eval.py` from cached analysis JSON. Does not run the W2 executable._
