# P1 number audit 20260816

Authority: `06_PAPER/analysis/*.json`. Draft: `drafts/P1_GMD_draft_v2.md`.

Checks: 40; **PASS=40**; **FAIL=0**.

| Check | OK | Expected | Note |
|---|---|---|---|
| ON A NSE | PASS | -2.8044 | json=-2.8044 |
| ON A R2 | PASS | 0.5082 | json=0.5082 |
| draft mentions ON A NSE token | PASS | -2.8044 |  |
| ON B NSE | PASS | 0.5 | json=0.5 |
| ON B R2 | PASS | 0.5332 | json=0.5332 |
| draft mentions ON B NSE token | PASS | +0.5000 |  |
| ON C NSE | PASS | -2.7516 | json=-2.7516 |
| ON C R2 | PASS | 0.5512 | json=0.5512 |
| draft mentions ON C NSE token | PASS | -2.7516 |  |
| ON B sim_max | PASS | 120.09 | json=120.09 |
| OFF B absent | PASS | file_absent | file_absent |
| W5 VPR yes | PASS | 2 |  |
| W5 VPR pct | PASS | 5.3 |  |
| W5 only_r2 pct of r2 | PASS | 81.8 |  |
| draft has 2/38 or 2 of 38 | PASS | True |  |
| NHR ON 20 | PASS | 5 |  |
| NHR ON 50 | PASS | 4 |  |
| NHR ON 100 | PASS | 1 |  |
| NHR ON 200 | PASS | 5 |  |
| draft 5/4/1/5 | PASS | True |  |
| NHR OFF all zero | PASS | 0/0/0/0 |  |
| DART n=17805 | PASS | 17805 |  |
| DART mae | PASS | 0.026537 |  |
| DART match_rate | PASS | 0.994945 |  |
| draft DART mae 0.026537 | PASS | True |  |
| draft match 0.994945 | PASS | True |  |
| OOS computed_nse false | PASS | False |  |
| QGT vs DART r | PASS | 0.868638 |  |
| realloc mean dart | PASS | 173.8573 |  |
| realloc mean tdgta | PASS | 39.2308 |  |
| realloc r | PASS | -0.596447 |  |
| draft spill means | PASS | True |  |
| SOD n | PASS | 1081 | 1081 |
| SOD mean | PASS | 0.8762 |  |
| SOD frac | PASS | 0.8955 |  |
| draft SOD 0.8955 | PASS | True |  |
| no affirmative 'physical variable deleted' | PASS | absent |  |
| forbidden absent: 减小时间步更不稳 | PASS | absent |  |
| draft DeGray 0.9027/-0.5855 | PASS | True |  |
| draft Columbia 0.6505/-1.4821 | PASS | True |  |

Script: `06_PAPER/notes/_audit_p1_numbers_20260816.py`. No W2 rerun. No unit tests in repo.