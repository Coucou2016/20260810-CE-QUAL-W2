# W3 发现：TDGTA=OFF 溯源一致对照

生成时间：2026-08-15
脚本：`00_INDEX/eval_w3_tdgta_off.py`  
指标 JSON：`06_PAPER/analysis/w3_tdgta_off_metrics.json`  
图：`06_PAPER/figures/W3_tdgta_on_off_timeseries.png`、`W3_tdgta_on_off_scatter.png`、`W3_tdgta_kge_decomposition.png`

未重跑。`05_REPRO_RUNS/run_20260814_bonneville_notarget/` 已完整，与 ON 运行同一结束判据。

---

## 1. 运行是否完整

| 项 | ON `run_20260814_bonneville` | OFF `run_20260814_bonneville_notarget` |
|---|---|---|
| `w2_systdg.npt` TDGTA | ON | **OFF**（`,ON,OFF,OFF,OFF,OFF,,,,,`） |
| `w2_con.csv` SCR | OFF | OFF |
| exit | 0 | 0 |
| 耗时 | 2163 s | 2292 s |
| `flowbal` 末 JDAY | 40908 | 40908 |
| `c_wdo_76.csv` 末 JDAY | — | 40909 |
| `w2.err` / forrtl | 无 | 无 |
| 当时 `w2_v455_ifx.exe` | — | 检查时无进程 |

官方 `TMEND=40909`。两次运行都在 `flowbal` 到 40908 且空闲后 terminate，与 `run_bonneville.py` / `run_bonneville_notarget.py` 的 idle+TMEND 逻辑一致。`c_wdo` 已写到 40909。**判定：已到 TMEND，不重跑。**

CCIW 有效 TDG 并不覆盖全年：n=1614 全部落在 **JDAY 40613.58–40681.54**（约 2011-03-11 至 2011-05-18）。论文方案写的 40544–40910 是模型窗；配对评估实际是这 68 天。

---

## 2. OFF 时哪些输出消失

相对 ON 目录，OFF **只少两个文件**（均为控制器模块写出）：

- `TDGTarget_output.csv` — `TDGtarget.f90` `InitTDGtarget` 打开；`w2_4_win.f90` 仅 `IF (TDGTA) CALL InitTDGtarget`
- `TDGTarget_warning.opt`

**仍然存在：** `c_wdo_76.csv`、`t_wdo_76.csv`、`BON_tsr_1_seg40.csv`、`TDG_output.csv`（SYSTDG 在 `INPUT_SYSTDG` 打开 unit 88888，与 TDGTA 无关）。

因此方案里「关掉 TDGTA 后评估被迫退回 A 口径」对 **B 口径所用文件** 成立；不能写成「模型不再计算 TDG_TDG」。SYSTDG 仍把同名量写到 `TDG_output.csv`。

---

## 3. 对照表（同一套 CCIW，n=1614）

KGE = \(1-\sqrt{(r-1)^2+(\alpha-1)^2+(\beta-1)^2}\)，\(\alpha=\sigma_s/\sigma_o\)，\(\beta=\mu_s/\mu_o\)。A/C 用 `eval_bonneville_tailwater.align`（tol=0.05）；B/S 用同一算法、tol=0.6（与 `eval_systdg_tdg.py` 日尺度配对一致）。ON 的 A/B/C 与论文方案表完全重合。

| 口径 | 文件 | R² | NSE | KGE | r | α | β | PBIAS | MAE | sim max |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ON A | N2+DO 亨利 seg76 | 0.508 | **−2.804** | 0.409 | 0.713 | 1.513 | 0.941 | −5.89% | 6.88 | 121.29 |
| ON B | `TDGTarget_output.csv` | 0.533 | **+0.500** | 0.715 | 0.730 | 0.909 | 0.999 | −0.14% | 2.20 | **120.09** |
| ON C | TSR seg40 TDG | 0.551 | −2.752 | 0.385 | 0.742 | 1.555 | 0.941 | −5.86% | 6.84 | 123.40 |
| ON S | `TDG_output.csv` | 0.561 | +0.357 | 0.706 | 0.749 | 1.154 | 1.007 | +0.72% | 2.75 | 127.49 |
| OFF A | N2+DO 亨利 seg76 | 0.521 | **−2.337** | 0.160 | 0.722 | **1.791** | 0.953 | −4.72% | 5.67 | 123.99 |
| OFF B | `TDGTarget_output.csv` | — | **文件不存在** | — | — | — | — | — | — | — |
| OFF C | TSR seg40 TDG | 0.551 | −2.752 | 0.386 | 0.742 | 1.555 | 0.941 | −5.86% | 6.84 | 123.42 |
| OFF S | `TDG_output.csv` | 0.561 | +0.357 | 0.706 | 0.749 | 1.154 | 1.007 | +0.72% | 2.75 | 127.49 |

观测：max=129.1%；**15.55%**（251/1614）点 >120%。

同文件 ON vs OFF（未对 CCIW，按 JDAY 内连接）：

| 序列 | n | MAE(OFF−ON) | max \|Δ\| | ON raw max | OFF raw max |
|---|---:|---:|---:|---:|---:|
| A N2+DO | 5599 | 0.70 | 9.22 | 127.37 | **129.04** |
| C TSR40 | 6211 | 0.0075 | 0.70 | 128.37 | 128.38 |
| S `TDG_output.csv` | 365 | **0** | **0** | 131.7 | 131.7 |

库内 TSR 几乎不受控制器影响（泄流再分配不改库内通道）。A 口径会变：关控制器后下泄 N2+DO 换算的峰值抬高、方差更大。

---

## 4. `TDG_output.csv` 不是 B 口径的替身

ON 的 `TDG_output.csv` 与 `TDGTarget_output.csv` 日值 MAE=1.71，最大差 11.74；raw max **131.7 vs 120.1**。

源码顺序：

1. `hydroinout.F90`：先 `IF(TDGTA) CALL TDGtarget`，再 `IF (SYSTDG) CALL SYSTDG_TDG`
2. `TDGtarget.f90` L180：再分配**之前**就 `CALL SYSTDG_TDG`
3. `systdg.f90`：该次调用若 `JDAY>=NXTSPLIT3` 就写 unit 88888 并把 `NXTSPLIT3 += 1`
4. 同日后续的 SYSTDG_TDG（含控制器收敛后）**不再写** `TDG_output.csv`

所以 `TDG_output.csv` 是 **控制前快照**。TDGTA ON/OFF 两个文件逐日相同（mae=0）是源码写出时机的结果，不是「关控制器没有效果」。后控制序列只存在于 `TDGTarget_output.csv`。

不能用 `TDG_output.csv` 顶替已消失的 B 口径。S 的 NSE=+0.357、α=1.15、sim max=127.49，与 B 的 +0.50 / 0.91 / 120.09 不是同一评估对象。

---

## 5. 峰值有没有回来？可达范围

**能超过 120%：能。** OFF A 配对 max=124.0%（76 个点 >120%）；OFF S 配对 max=127.49%。ON B 配对 max=120.09%，钉在目标上限。

**能否接近观测 129.1%：**

- 配对时刻：OFF S 到 127.49%，接近但未到 129.1%；OFF A 只有 123.99%。
- 原始序列（不对齐 CCIW）：OFF A raw max=**129.04%**，OFF S raw max=**131.7%**（SYSTDG 硬上限 145%）。公式本身写得出 ≥129% 的数；这些峰值不落在 CCIW 有效小时上。

关控制器 **没有** 把 A 口径变成可用预报：NSE 从 −2.80 升到 −2.34，仍远差于均值预报；KGE 反而从 0.41 掉到 0.16，因为 α 从 1.51 胀到 1.79。控制器压缩的是 B 文件的方差，不是 A 口径的物理偏差。

---

## 6. 对创新点 2 的含义：**加强，但必须改表述**

方案原文：「关掉控制器，最优变量本身就消失了」。W3 核实后应改成下面三句，证据更硬，不是更弱。

1. **评估所用的最优文件是控制器门控的。** NSE=+0.50、β=0.999、PBIAS=−0.14%、sim max=120.1% 的序列只存在于 `TDGTarget_output.csv`。TDGTA=OFF 时该文件与 `TDGTarget_warning.opt` 一起消失。标准对照「固定指标、只切换控制」在这条路径上做不到。
2. **不要写成「物理量被模型删掉」。** SYSTDG=ON 时 `TDG_TDG` 仍写入 `TDG_output.csv`。该文件是控制前快照（ON≡OFF），与控制器输出不是同一 VPR（MAE 1.71，峰值 131.7 vs 120.1）。
3. **120% 封顶是控制器造的，不是 SYSTDG 公式的天花板。** 无控制的 SYSTDG 日值可到 131.7%；关控制器后 A 口径 raw 也可到 129%。ON B 的 α<1 与水平截断，是把输出钉在目标带上的特征。观测 15.6% 点 >120%，在 B 口径结构上不可复现。

条件化评估（conditional evaluation）仍然成立，且更精确：必须声明 TDGTA 状态，并写明用的是 `TDGTarget_output.csv`（后控制）还是 `TDG_output.csv`（控制前）还是 N2+DO/TSR。同名 `TDG_TDG` 在两个文件里不是同一个评估对象。

---

## 7. 交付文件

- 运行目录：`05_REPRO_RUNS/run_20260814_bonneville_notarget/`（`run_summary.json` 已补 W3 核查字段）
- `06_PAPER/analysis/w3_tdgta_off_metrics.json`
- `06_PAPER/figures/W3_tdgta_on_off_timeseries.png`（全年 + CCIW 窗）
- `06_PAPER/figures/W3_tdgta_on_off_scatter.png`
- `06_PAPER/figures/W3_tdgta_kge_decomposition.png`
- 复算脚本：`00_INDEX/eval_w3_tdgta_off.py`
