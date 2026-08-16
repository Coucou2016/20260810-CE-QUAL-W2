# 复现运行目录说明

**权威结果（请以此为准）：** `run_20260811_fixed`

该目录含 Long Lake、DeGray、Columbia Slough 的完整输出，以及 `analysis\` 下时序 / 俯视 / 剖面 / 流域底图 / 侧向误差图。

**Bonneville 模型–观测对照：** `run_20260814_bonneville`（2011 年 SYSTDG，对照 CCIW）。**正确对照变量**是 `TDGTarget_output.csv` 的 TDG 列（模块 `TDG_TDG`），NSE=0.50；库内 TSR / c_wdo 的 N2+DO 换算不是 SYSTDG 输出。`run_20260814_bonneville_notarget` 为关 TDGTA 的对照重跑。

**Columbia 底泥成岩（SED_DIAG ON）：** `run_20260814_columbia_diag`。输入由 DeGray 的 `W2_diagenesis.npt` 改编（速率区结束河段 31→50），**不是** Columbia 率定参数。权威三案例目录仍保持 `run_20260811_fixed`（该处 Columbia 为 SED_DIAG OFF）。

## 其他子目录（归档，勿当作最新结论）

| 目录 | 性质 |
|---|---|
| `run_20260811` | 早期试跑（输出不完整） |
| `run_20260811_seq` | 顺序试跑；部分案例几乎空输出 |
| `run_20260811_repeat` | 重复运行尝试，曾超时中止 |
| `diag_longlake` / `diag_columbia` / `diag_columbia2` | 排错副本（habitat 缺文件等） |

复现报告请看项目根目录 `report.html`，不要用 `04_MARKDOWN\W2MD-REPRO-THREE_CASES-20260811.md`（该文件已过时，仅作历史记录）。
