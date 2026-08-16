# w2eval（最小可用版）

溯源感知的 CE-QUAL-W2 **run-card** 生成器。读取本项目已经算好的分析 JSON 与 NHR 记录，写出一份机器可读 JSON 和一份人类可读 Markdown。每张卡固定三段：**VPR**（变量溯源）、**指标面板**、**NHR**（数值健康）。

**本版不跑模型。** 不会调用 `w2_v455_ifx.exe`，也不会重算 Bonneville / Long Lake / Columbia 的完整积分。指标数字来自 `06_PAPER/analysis/*.json`；NHR 来自 `nhr_existing_runs.json` / `nhr_dlt_scan.json`（由 `00_INDEX/parse_nhr.py` 生成）。若缓存缺失，脚本会尝试 import `parse_nhr.parse_nhr` 解析既有运行目录，仍然不启动 exe。

## 如何运行

在仓库根目录：

```text
python 06_PAPER/w2eval/w2eval.py
python 06_PAPER/w2eval/w2eval.py --out 06_PAPER/w2eval/cards
```

依赖：标准库 + 已存在的分析 JSON。不需要 numpy/pandas（MVP 不重算 R²/NSE）。

输出目录默认 `06_PAPER/w2eval/cards/`：

| 文件 | 内容 |
|---|---|
| `index.json` | 卡清单 |
| `bonneville_tdgta_on.{json,md}` | Bonneville TDGTA ON：A/B/C 三口径 + SYSTDG 控制前快照 S |
| `bonneville_tdgta_off.{json,md}` | Bonneville TDGTA OFF：B 文件消失；S 不能顶替 B |
| `longlake_dlt_nhr.{json,md}` | Long Lake 官方 vs 扫描（DLTINTER ON/OFF） |
| `columbia_do_internal.{json,md}` | Columbia DO 内部一致性 + SOD 量级注释 |
| `degray_t_internal.{json,md}` | DeGray 水温内部一致性 |

图表不重新绘制；Markdown 只引用 `06_PAPER/figures/` 与 `06_PAPER/analysis/` 里已有 png。

## 卡的字段定义

顶层：

| 字段 | 含义 |
|---|---|
| `card_id` | 文件名主干 |
| `title` | 人类可读标题 |
| `mode` | `skill_vs_observations` / `internal_consistency` / `numerical_health` |
| `tdgta` | 若适用：`ON` / `OFF` |
| `case.run_dir` | 相对仓库根的运行目录 |
| `claim` | 该卡要支撑的一句主张 |
| `vpr` | 变量溯源记录列表 |
| `metrics_panel` | 指标面板 |
| `nhr` | 一条 NHR 对象，或 Long Lake 扫描的 NHR 列表 |
| `notes` / `figures` / `sources` | 注释、已有图、复算入口 |

### 1. VPR（Variable Provenance Record）

每条必须能回答「评估用的是哪一条序列」：

| 字段 | 含义 |
|---|---|
| `caliber` | 口径代号（A/B/C/S 或通道短名） |
| `file` | 输出文件名 |
| `column` | 列名 |
| `segment` | 断面 I 或站点 |
| `layer` | 层 K / 取水高程 / 表层 KT |
| `unit` | 单位 |
| `derived_from` | 派生链（原生 TSR、亨利换算、控制前快照、控制器门控文件…） |
| `time_support` | 瞬时 / 日均 / 快照 / 事件日志 |
| `pairing_tolerance` | 配对容差（天）；无配对则为 `n/a` |

**内部一致性卡**（DeGray、Columbia）的「ref」不是观测。正文与卡上都标 `internal_consistency`，不要写成 skill。

### 2. 指标面板

| 字段 | 含义 |
|---|---|
| `kind` | `skill_vs_observations` / `internal_consistency` / `no_observation_skill` |
| `observation` | 观测文件；无观测则为 `null` |
| `n` / `window` | 配对数与 JDAY 窗 |
| `calibers[]` | 多口径并排：`r2`, `nse`, `kge`, `r`, `alpha`, `beta`, `pbias`, `mae` |
| `status` | `ok` 或 `file_absent`（如 TDGTA OFF 的 B） |
| `scan_table` | 仅 Long Lake：DLTMAX × DLTINTER 负厚度计数 |

KGE 分解与既有脚本一致：  
\( \mathrm{KGE}=1-\sqrt{(r-1)^2+(\alpha-1)^2+(\beta-1)^2} \)，\(\alpha=\sigma_s/\sigma_o\)，\(\beta=\mu_s/\mu_o\)。  
MVP **不重新实现**这些公式，直接复制 JSON。

### 3. NHR（Numerical Health Record）

| 字段 | 含义 |
|---|---|
| `neg_surface_thickness_count` | `w2.wrn` 中负表面层厚度（H1<0 → DLTMIN 回退）次数 |
| `add_layer_count` / `subtract_layer_count` | 加层 / 减层次数（几何阈值，本身不是错误） |
| `exit_zero_masks_rollback` | 是否 exit 0 + Normal termination 但仍有负厚度回退 |
| `dltinter` | `w2_con.csv` 的 DLTINTER |
| `wrn_path` | `w2.wrn` 相对路径；干净运行可能无此文件 |
| `snp_n_violations` | SNP 的 NV；**不是** H1<0 次数（含 CFL/粘性限制） |
| `window_dlt` | TSR 抽样的窗内 DLT min/max（抓不到单步 DLTMIN 回退） |

解析器：`00_INDEX/parse_nhr.py`。

## 局限（请在论文里写明）

1. **暂不自动跑模型。** 换一套输入或改 `TDGTA` / `DLTMAX` 后，必须先用 `00_INDEX/` 下的运行脚本生成新目录，再重跑对应 `eval_*.py` / `parse_nhr.py`，最后再生成卡。
2. **不重算指标。** 若 JSON 与运行目录不一致，卡会跟着 JSON 错。权威数字以 analysis JSON 为准。
3. **DeGray / Columbia 无独立观测。** 卡上的 NSE 是通道间内部一致性。
4. **样本外 NSE 不在卡上。** W4 已下载 2016–2025 DART，但模型只到约 2011。
5. **NHR 的 DLTMIN 时长占比** 目前只能用 wrn 事件作下限；精确占比需要源码插桩（方案 T4）。
6. **图表只引用，不生成。**

## 与英文草稿的对齐（2026-08-16）

与 `drafts/P1_GMD_draft_v1.md` 一致的主张边界：

| 项 | 卡 / README 口径 |
|---|---|
| DeGray / Columbia | `mode` / `kind` = `internal_consistency`；不是对观测 skill |
| Bonneville A/B/C | `skill_vs_observations`；B = 门控文件，S = 控制前快照，不能顶替 B |
| NHR | 负厚度来自 `w2.wrn` 行计数；与 SNP `NV` 分开；不推广「减小 Δt 更不稳」 |
| 样本外 NSE | **不在卡上**；`computed_nse=false` |
| SOD | Columbia 卡仅量级注释；移植参数，非率定 |
| 跨研究可比 | 三件套是**报告建议**；直接可比性不能仅凭指标断定 |

正文措辞若再软化（条件可比 / recommendation），以草稿为准；本 README 不单独升格主张。

## 与方案的对应

见 `06_PAPER/PAPER_PLAN_20260815.md` 创新点 4 / W6。W1–W5、W7 已完成；本目录是 W6 的最小可用版。
