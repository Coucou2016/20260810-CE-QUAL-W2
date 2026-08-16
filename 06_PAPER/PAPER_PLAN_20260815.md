# CE-QUAL-W2 论文方案（v2，2026-08-15）

本方案基于本项目已完成的复现与诊断实证（W1–W5、W7 已落盘），不含推测性结论。
所有关键数字均可由 `00_INDEX/` 与 `06_PAPER/analysis/` 下脚本在 `05_REPRO_RUNS/`
的既有运行目录上重算；**以 JSON 为准**，不以本文件旧稿为准。标注 `【待补】` 的是
尚未验证、必须先做实验才能写入论文的部分。

**本版相对 v1 的主张修订：** 创新点 1 已从 Bonneville TDG 推广到 DeGray 水温与
Columbia DO，并用 38 篇文献审计量化动机；创新点 2 改为「控制器门控评估文件」，
**不再写「物理量被删掉」**；创新点 3 主交付改为 NHR 必报，跨案例「减小时间步更不稳」
降级。DeGray / Columbia 的 NSE/KGE **是输出通道内部一致性，不是对观测的技能**。

---

## 0. 文献定位（我们站在谁的肩膀上）

**锚点 A — 综述缺口（本文的问题来源）**
Benicio, S.H.M.; Basso, R.E.; Formiga, K.T.M. *Global Applications of the CE-QUAL-W2
Model in Reservoir Eutrophication: A Systematic Review and Perspectives for Brazil.*
Water 2024, 16, 3556. doi:10.3390/w16243556（库内 `LIT-010`）

该综述筛选 38 篇 CE-QUAL-W2 富营养化研究，其**表 2 用单一 R² 汇总各研究的率定质量**
（0.32 至 0.977），并在 §3.2「Calibration Variability」中把 R² 的离散归因于
「数据质量、方法成熟度、场地复杂度」。综述**没有**记录：
1. 每篇研究拿模型的**哪一个输出变量/哪个断面/哪一层**去对观测；
2. 该次运行是否启用了**内部控制律**（TDG 目标、选择性取水、动态调度）；
3. 该次运行的**数值健康状况**。

W5 把上述缺口从定性变成计数（编码表 `06_PAPER/analysis/w5_lit_audit.csv`；
计数 `w5_lit_audit_summary.json`）。对象是综述表 1 的 **38** 篇（与正文「38 selected」
一致）。全文获取 **9/38**（23.7%）；其余用摘要 + 综述表，不确定标 `unknown`。

| 项目 | 计数 | 比例 |
|---|---:|---:|
| 仅凭论文可重建 VPR | **2/38** | **5.3%** |
| 写出 W2 输出文件/列名 | **0/38** | 0% |
| 报 R²（任一模型） | 11/38 | 28.9% |
| 报 R² 且不报 NSE | **9/11** | **81.8%** |
| 报告 KGE | **0** | 0% |
| 表 2 的 12 个 R² 中，能确认是 W2 对观测技能 | **1**（Neto 0.32） | 1/12 |

因此：缺少这三项，表 2 那样的跨研究 R² 比较在方法上不成立。这不是对综述的否定，
而是补上它自己指出的「变异性」的真正来源。**不能声称「38 篇都只报 R²」**——11 篇
报了 R²，其余多数连 R² 也未在可核段落出现。也不能把表 2 的 0.32 与 0.977 写成
同一口径的技能差距：0.977 不是拟合优度。

**锚点 B — 模型机理基准**
Wells & Cole, *Basis of CE-QUAL-W2 Version 3 River Basin Model*（库内 `LIT-011`）——
提供层增减、水面偏移 Z、时间步控制的原始表述，用于源码级论证的引用基础。

**锚点 C — 同类论文的期刊先例（证明该文体可发表）**
Almeida, M.; Coelho, P. *Evaluating the performance of CE-QUAL-W2 version 4.5
sediment diagenesis model.* Geosci. Model Dev. 2025, 18, 6135–6161.
doi:10.5194/gmd-18-6135-2025；复现包 Zenodo doi:10.5281/zenodo.15775127

该文是 GMD 的「model evaluation paper」：用 NSE±SD 报告、做 0 阶/1 阶/混合/成岩四种
SOD 方案的横向 benchmark、公开全部输入与 exe。它同时是**引文锚点**（给出 SOD
0.5–3.0 gO₂/m²/d 的独立参考区间，可用来检验我们 Columbia 成岩量级是否合理）和
**投稿先例**（GMD 接受这一文体）。

W7：Columbia 湿段 SOD 均值 **0.876 gO₂/m²/d**（瞬时，JDAY≥33，n=1081）；
**89.6%** 落在 Almeida 0.5–3.0；**无点 >3.0**；约 **10.5% <0.5**。参数由 DeGray
`W2_diagenesis.npt` 移植（区域 2 末断面 31→50），**不是现场率定**。量级「看起来合理」
只说明移植没有跑出荒谬 SOD，不能支持水质情景推断。

---

## 1. 能取得什么样的创新点

推荐主论文（P1）一篇，四个创新点由强到弱排列。前两点已有硬证据且已加强；
第三点机理已定位，主张改为 NHR 必报（非单调性仅有条件成立）；第四点是交付物。

### 建议题名（P1）

> **Variable provenance, control-rule confounding, and numerical health:
> why reported goodness-of-fit is not comparable across CE-QUAL-W2 applications**

中文工作题名：《变量溯源、控制律混淆与数值健康度——论 CE-QUAL-W2 拟合优度的
跨研究不可比性及其评估协议》

### 创新点 1（加强并已推广）：变量溯源歧义可以把同一次运行的 NSE 从 −2.80 翻到 +0.50；该模式不依赖 TDG

#### 1a. Bonneville TDG 三口径（对观测技能，仍成立）

同一次 Bonneville 运行（TDGTA=ON）、同一份 CCIW 观测。模型窗是 JDAY 40544–40910；
**配对评估实际是 n=1614、JDAY 40613.58–40681.54**（约 2011-03-11 至 2011-05-18），
不是全年。仅改变「把哪个输出叫做 TDG」：

| 口径 | R² | NSE | KGE | r | α=σs/σo | β=μs/μo | PBIAS | MAE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A 由 seg76 的 N2+DO 按模型自带亨利公式换算 | 0.508 | **−2.804** | 0.409 | 0.713 | **1.513** | 0.941 | −5.89% | 6.88 |
| B 控制器门控文件 `TDGTarget_output.csv` | 0.533 | **+0.500** | 0.715 | 0.730 | **0.909** | 0.999 | −0.14% | 2.20 |
| C 库内 TSR seg40 的 TDG 通道 | **0.551** | −2.752 | 0.385 | 0.742 | **1.555** | 0.941 | −5.86% | 6.84 |

（数字：`w3_tdgta_off_metrics.json`。B 在方案 v1 曾写作「SYSTDG 模块自身输出 `TDG_TDG`」；
W3 核实后 B 是控制器写出的后控制序列，见创新点 2。）

三个论点：

1. **相关系数几乎不变**（r = 0.713 / 0.730 / 0.742），所以 R²=r² 三者落在
   **0.508–0.551** 的窄带内，按综述表 2 的口径三者都会被写成「moderate agreement ≈0.5」。
   而 NSE 分别是 **−2.80、+0.50、−2.75**：其中两个比直接用观测均值预报还差。
   **R² 最高的那一个（C, 0.551）恰恰是 NSE 最差的之一。**
2. **可给出小段理论**：R² 对模拟序列的仿射变换 s′ = a·s + b 不变，因此它在结构上
   看不见 KGE 分解中的方差比 α 和均值比 β。而错误的变量选择正是通过 α（1.51/1.56
   对 0.91，方差虚增约 50–70%）和 β（0.941，均值低 6%）表现出来的。**只报 R² 的
   评估在数学上不可能检出变量误指认。**
3. A 口径并非稻草人：它用的是模型源码 `withdrawal.f90` 自带的 N2/DO→TDG 公式，
   是一个专业读者会做的合理选择；且 W2 对同一物理量至少发出三套数值。

#### 1b. DeGray 水温（内部一致性，无独立观测）

官方示例无独立水温观测。下列指标是**同一运行、不同输出通道**的分歧，
**不是对观测的技能**。运行：`run_20260811_fixed/DeGray Reservoir…`；n=2943。

| 对照 | R² | NSE | KGE | r | α | β | 含义 |
|---|---:|---:|---:|---:|---:|---:|---|
| 同一 TSR 表层 T2 vs 库容均温 Tvolavg | **0.903** | **−0.59** | 0.235 | 0.950 | **0.35** | **0.61** | R² 会被写成 excellent |
| 表层 T2 vs WDO 取水混合 | 0.529 | −0.37 | 0.279 | 0.728 | 0.420 | 0.669 | 与 Bonneville R² 带重合 |
| 两取水口 STR 115 m vs GATE 120 m | **0.534** | **−6.58** | −0.486 | 0.731 | **2.38** | **1.49** | 只报 R² 会写成同等 moderate |

机制与 Bonneville 相同：T2 vs Tvolavg 的 α=0.35（方差被库容平均压掉约 65%）、
β=0.61（均值低 39%）。R² 看不见这件事。GATE 中心线 120 m 接近水面，T2 vs GATE120
的 NSE=0.999，不能推广成「闸门输出总等于表层」——VPR 必须写高程。
深孔/底层那种错法 R² 也会垮（PRF 底层 vs TSR 表层 R²=0.057）。

#### 1c. Columbia DO（内部一致性，无独立观测）

`run_20260814_columbia_diag`，n=116（约 23 天）。**不是对观测的技能。**

| 对照 | R² | NSE | KGE | r | α | β |
|---|---:|---:|---:|---:|---:|---:|
| TSR I=45 vs I=49 | 0.207 | **−4.49** | 0.167 | 0.455 | 0.682 | 1.544 |
| TSR I=45 vs I=33 | 0.328 | −2.27 | 0.379 | 0.572 | 1.259 | 1.368 |
| TSR I=49 vs I=33（R² 最高的一对） | **0.65** | **−1.48** | 0.124 | 0.807 | **1.85** | 0.886 |
| 浅汊 SNP 表/底（I=45） | 0.93 | **0.91** | 0.936 | 0.966 | 0.971 | 0.955 |

三站 NSE 全部 < −1.48。若只按 R² 排序，会把 I=49 vs I=33 当成最好，而它的 NSE 仍为负、
α=1.85。浅潮汐汊道上 SNP 表层 vs 底层 NSE=0.91，**层误指认几乎检不出**；
**错站比错层危险**。Columbia 序列短、潮汐变幅大，R² 带宽宽于 Bonneville；推广力度
主要靠 DeGray（n=2943）。

#### 1d. 文献层（W5）把动机定量化

综述表 1 的 38 篇：可重建 VPR 仅 **2/38（5.3%）**；**0** 篇写出输出文件/列名；
报 R² 的 11 篇里 **9 篇（81.8%）不报 NSE**；**KGE=0**。表 2 的 12 个 R² 里能确认是
W2 对观测技能的只有 **1 个（Neto 0.32）**。其余是蒸发皿相关、入库浓度回归、情景响应
曲线、或把 SWAT/R 误标成 W2 R²。

**交付概念：变量溯源记录（Variable Provenance Record, VPR）** ——
{输出文件, 列名, 断面 I, 层 K, 单位, 派生链, 时间支撑（瞬时/日均）, 配对容差}。
论文主张任何 W2 评估必须公开 VPR。DeGray/Columbia 必须在正文用
*provenance disagreement* / *internal consistency*，避免写成 *skill*。

### 创新点 2（加强，必须改表述）：被控输出不能作为预测能力的证据——最优序列只存在于控制器门控文件

Bonneville 官方示例默认 `TDGTA=ON`。源码 `TDGtarget.f90` 显示这是一个**优化控制器**
（读 `w2_TDGtarget.csv`；含泄流优先序 `SPPRIOR`、最小分流比 `SPMINFRAC`、
厂房最大流量 `PHMAXFLOW`、迭代次数 `tsiteration`），按 115%/120% 动态目标
（`TDGdyntarget.csv`）在泄洪道与厂房之间重分配流量。

**v1 的错误表述：「关掉控制器，最优变量本身就消失了 / 物理量被删掉」。不要再用。**

W3 核实后的正确三句：

1. **技能最好、β≈1、封顶 120.1% 的序列只存在于控制器门控文件 `TDGTarget_output.csv`。**
   ON B：NSE=+0.500，β=0.999，PBIAS=−0.14%，配对 sim max=**120.09%**。
   **TDGTA=OFF 时该文件与 `TDGTarget_warning.opt` 一起消失。** 标准对照「固定指标、
   只切换控制」在这条路径上做不到。
2. **不要写成「物理量被模型删掉」。** SYSTDG 仍把 `TDG_TDG` 写到 `TDG_output.csv`
   （`INPUT_SYSTDG` 打开 unit 88888，与 TDGTA 无关）。那是**控制前快照**：
   `TDGtarget.f90` 再分配之前就 `CALL SYSTDG_TDG` 并推进 `NXTSPLIT3`，同日后续调用
   不再写该文件。因此 ON/OFF 的 `TDG_output.csv` **逐日相同（mae=0）**，raw max 都是
   **131.7%**。它**不能顶替 B 口径**（与 `TDGTarget_output.csv` 日值 MAE=1.71，
   峰值 131.7 vs 120.1）。同名 `TDG_TDG` 在两个文件里不是同一个评估对象。
3. **120% 封顶是控制器造的，不是 SYSTDG 公式的天花板。** 观测 max=129.1%；
   **15.6%**（251/1614）点 >120%，在 B 口径结构上不可复现。

OFF 对 CCIW（n=1614，窗 **40613–40681**）：

| 口径 | 文件 | NSE | 配对 max | 备注 |
|---|---|---:|---:|---|
| A | N2+DO 亨利 seg76 | **−2.337** | **124.0%** | NSE 仍远差于均值预报；KGE 从 0.41 掉到 0.16（α 胀到 1.79） |
| B | `TDGTarget_output.csv` | — | — | **文件不存在** |
| S | `TDG_output.csv` | **+0.357** | **127.49%** | raw max **131.7%**（能过 120%；配对序列到不了观测 129.1%） |
| C | TSR seg40 | −2.752 | 123.42% | 库内通道几乎不受控制器影响（ON vs OFF MAE=0.0075） |

关控制器**没有**把 A 口径变成可用预报。

#### W4 DART 独立证据（加强创新点 2，不是样本外技能）

- 库内 CCIW vs DART 小时 **n=17805**，MAE=**0.027%**，|Δ|≤0.051 匹配率 **99.5%**。
  示例观测**未被实质性改过**。JDAY **40544 = 2011-01-01**（Excel 序列，原点 1899-12-30）。
- **2016–2025** 有效小时 **21.2% >120%**（2011–2015 为 **14.7%**）；封顶问题没有随时间消失。
- **未做样本外 NSE**：模型只跑到约 2011（TMEND=40909）。DART 十年已落盘，NSE 必须先扩时段。
- 2011 泄流：输入 **QGT vs DART r=0.87**；TDGTA 对 DART 泄流 r=0.24。
  再分配日（C=R，**116** 天）把实测约 **174 kcfs** 压到约 **39 kcfs**（**r=−0.60**）。
  ON 的低偏差/封顶，部分来自「把泄流调成与 2011 年实际运行不同的方案」。

**交付概念：条件化评估（conditional evaluation）** —— 按控制器是否 binding 分层
报告指标，并显式声明**可达范围**（reachable range）以及用的是
`TDGTarget_output.csv`（后控制）还是 `TDG_output.csv`（控制前）还是 N2+DO/TSR。

### 创新点 3（部分加强、部分降级）：NHR 必报；不要写成跨案例非单调定律

源码级机理（`w2_4_win.f90` L1415–1424）：当表层厚度 `H1(KT,I) < 0` 时，若
`DLT > DLTMIN`，模型写警告、把 `CURMAX` 强制设为 `DLTMIN`、`GO TO 220` **重算该时间步**；
只有已经在 DLTMIN 上还失败才转为 `w2.err` 致命错误。**因此运行照常以 exit 0 结束，
而 N 次回退事件只留在 `w2.wrn` 里。** `endsimulation.F90`：无 `ERROR_OPEN` 则
Normal termination；无 `WARNING_OPEN` 则删除 `w2.wrn`。

失效的几何来源（`layeraddsub.F90`）：层增减由硬阈值控制——
加层 `ZMIN < −0.85·H(KT−1)`（L241）、减层 `ZMIN > 0.60·H(KT) .AND. KT < KTMAX`（L242），
循环内复检阈值不同（加层 −0.80·H，L767；减层 0.60·H，L1277），构成滞回带。
**这是几何/阈值失效，不是截断误差。**

**扫描前未写入方案、但决定实验含义：** `DLTINTER=ON` 时 DLTMAX 在结点之间线性插值
（`update.F90` L152–163）。Long Lake 官方第 30–40 天并不是 DLTMAX=100 的平台，
而是从 100 s **插值到 1800 s**。只改 day-30 结点改变的是插值**起点**，不是窗内硬顶。

W2 扫描后的诚实分级：

| 主张 | 扫描后 | 写法 |
|---|---|---|
| exit 0 掩盖 H1<0→DLTMIN 回退 | **加强**。Long Lake DLTINTER=ON 四点均为 Normal termination，wrn 仍有 **1–5** 次负厚度；H1 可到 −113 m。 | 硬结果；NHR 必报。 |
| 警告数对 DLTMAX 非单调 | **有条件**：官方 INTER ON 下 DLTMAX 20/50/100/200 的负厚度为 **5/4/1/5**，非单调，官方 **100 s 是谷底**。 | 可写，必须写清是**插值结点**不是窗内硬顶。 |
| 「减小时间步更不稳」为普遍结论 | **降级，不能当普遍结论。** INTER ON 时 DLTMAX=20 窗内实际 DLT 仍达 **~230 s**（day-40 结点仍 1800 s）。INTER OFF 后 20–200 s 负厚度全是 **0**。Columbia 120/360/720 s 负厚度 **0/0/0**。**H1<0 只在 Long Lake 出现。** | 改为：H1<0 对 DLT 历史/插值路径敏感。 |

INTER OFF、20 s：SNP 的 NV 约 8%，负厚度却是 0。NHR 必须把 **H1<0 回退** 与
**一般时间步 violation（NV）** 分开报。层增减（Columbia 15 次、Bonneville 80+ 次）
是水位波动触发阈值，本身不是错误。

**主张改为：NHR 必报**（负厚度回退次数、是否被 exit 0 盖住、DLTINTER 状态），
**不是跨案例非单调定律。**

**交付概念：数值健康记录（Numerical Health Record, NHR）** —— 从 `w2.wrn`/`w2.err`/
`*_snp.opt` 解析：加层/减层事件数、负厚度回退次数、低水位警告、DLT 轨迹、
处于 DLTMIN 的模拟时长占比（后者目前只能用 wrn 事件作下限；精确占比需插桩 T4）。
主张：回退频发的运行，其技能指标与干净运行不可比。

### 创新点 4（交付物）：官方示例套件可复现性审计 + 开源评估协议与工具

已核实的具体缺陷（17 个案例：v4.5.5 八个 + v5.0 beta 九个）：

- **Long Lake** 运行需要 `HabitatFiles/` 目录，而发行包未附带 → `forrtl` 29 崩溃；
- **Columbia Slough Estuary** 的 `w2_con.csv` 设 `SED_DIAG=ON`，但**缺 `W2_diagenesis.npt`**
  → 运行失败；本项目改用 DeGray 模板（区域 2 末断面 31→50）才跑通，故其成岩参数
  **是移植的、非现场率定**，这一限制必须在论文中明写；W7 已给出量级对照（见 §0）。
- **17 个案例中只有 1 个（Bonneville）附带任何实测数据**（CCIW 2011–2015），
  即官方示例套件在结构上无法用于验证率定主张；
- 可执行文件以 Git-LFS 指针形式分发，直接 clone 得不到能运行的 exe。

**交付物**：`w2eval` —— 溯源感知的评估器 + run-card 生成器 + 报告清单（checklist），
连同全部输入/输出归档到 Zenodo，对标 Almeida & Coelho 2025 的复现包规格。
W6 进行中：最小可用版读取既有 JSON 写出 VPR / 指标面板 / NHR 三段式 run-card，
**暂不自动跑模型**。

---

## 2. 在本路径的库与代码中能否实现（可行性映射）

| 创新点 | 依赖资产 | 路径 | 状态 |
|---|---|---|---|
| 1 变量溯源（Bonneville） | 运行 + CCIW + 三套输出 | `05_REPRO_RUNS/run_20260814_bonneville/` | ✅ 已算出全表 |
| 1 推广（DeGray T / Columbia DO） | 无观测；内部一致性 | `w1_provenance_metrics.json` | ✅ W1 完成 |
| 1 理论部分 | 亨利换算公式原文 | `02_LIBRARY/05_source/.../withdrawal.f90` | ✅ 已定位 |
| 1 文献动机 | 38 篇审计 | `w5_lit_audit_summary.json` | ✅ W5 完成 |
| 2 控制律 ON/OFF | 控制器源码、两次运行 | `…_notarget/`、`w3_tdgta_off_metrics.json` | ✅ W3 完成（未重跑；既有 OFF 已到 TMEND） |
| 2 DART 核对 / 泄流 | CCIW vs DART、QGT vs 控制器 | `w4_cciw_vs_dart.json` | ✅ W4 完成；样本外 NSE `【待补】` |
| 3 数值健康 | 层增减与回退源码、LL 扫描 | `nhr_dlt_scan.json`、`parse_nhr.py` | ✅ W2 完成；主张已降级 |
| 4 审计与工具 | 17 案例、既有运行、脚本 | `w2eval/` | 🔄 W6 进行中（MVP） |
| 4 SOD 量级 | Columbia 成岩 + Almeida 带 | `w7_columbia_sod_vs_almeida.json` | ✅ W7 完成 |

**关键可行性结论：**

- **全套 v4.5 Fortran 源码在库**（53 个文件，`02_LIBRARY/05_source/github_v4.5/model/w2_model_source/`），
  含 `systdg.f90`、`TDGtarget.f90`、`tdg.f90`、`layeraddsub.F90`、`w2_4_win.f90`、
  `withdrawal.f90`、六个 `Diagenesis *.f90`。→ 创新点 1–3 都能做到**源码级归因**而非黑箱推测。
- **两套编译器可用**：`ifort`（D:\programs\inteloneAPI\...\intel64\ifort.exe）与
  `gfortran`（D:\msys64\mingw64\bin\）。→ 可插桩重编译（见拓展 T2），并可做
  跨编译器复现性检验。
- **两个版本的 exe 与示例**（v4.5.5 `w2_v455_ifx.exe` 与 v5.0 beta）→ 可做跨版本指标漂移。
- **已有脚本**（`00_INDEX/`）：`eval_bonneville_tailwater.py`、`eval_systdg_tdg.py`、
  `diagnose_tdg_target.py`、`run_bonneville_notarget.py`、`rerun_columbia_diagenesis.py`、
  `rerun_longlake_dlt.py`、`plot_columbia_diagenesis.py`、`build_repro_report.py`、
  `parse_nhr.py`、`eval_w3_tdgta_off.py`、`download_dart_cciw.py`。
  → `w2eval` 是对这些脚本的收敛重构，不是从零开始。
- **Python 栈就绪**（numpy/pandas/matplotlib 已验证可用）。

**尚缺、投稿前仍须补的：**

1. 样本外 NSE：把 Bonneville 模型时段扩到 2016+（W4 数据已就绪，模型未跑）；
2. `w2eval` 从 MVP 收敛到可归档协议（W6，进行中）；
3. 跨版本指标漂移（T3）仍可选；
4. DeGray/Columbia 若要写成与 Bonneville 同构的「对观测 NSE」，需要独立实测
   （目前没有，不得假装有技能）。

---

## 3. 能找到的公开资料与验证路径

### 3.1 Columbia River DART（核心外部验证源，已下载）

`https://cbr.washington.edu/dart/query/wqm_hourly`（Columbia Basin Research,
University of Washington；数据源为 USACE NWD）

站点 **CCIW = Cascade Island (Bonneville Tailwater)，2004 年至今**，小时级。
脚本化查询必须带 **`sc=1`**，否则 302 到 Drupal HTML。数据在
`06_PAPER/data/dart_cciw/cciw_hourly_YYYY.csv`（2011–2025，15 年成功）。

三层验证的现状：

1. **溯源验证（已完成）：** 库内 CCIW 与 2026 年 DART 原始小时高度一致
   （n=17805，MAE=0.027%，|Δ|≤0.051 匹配率 99.5%）。示例附带观测未经实质性改动。
2. **样本外检验（数据就绪，NSE 未做）：** 示例模型只到约 2011；DART 有到 2025 年。
   2016–2025 有效小时 21.2% >120%（示例期 14.7%）。**不能把超标统计写成预报技能。**
3. **直接检验创新点 2（已完成 2011 泄流对照）：** QGT 跟实测（r=0.87），控制器在
   116 个再分配日把泄流从约 174 kcfs 压到约 39 kcfs（r=−0.60）。

### 3.2 USACE Northwestern Division

`https://www.nwd.usace.army.mil/CRWM/Water-Control-Data/` —— dataquery 交互访问、
历史水质/工程绘图、Water Year Reports（PDF）。用于交叉核对 DART，并取得
TDG 管理标准（110%/115%/120% 豁免）的官方依据，支撑创新点 2 的政策背景叙述。

### 3.3 Almeida & Coelho 2025 复现包（成岩模块的独立基准）

Zenodo doi:10.5281/zenodo.15775127。W7 已把 Columbia 移植 SOD 与该文 0.5–3.0
扫描带对照（均值 0.876，89.6% 落在带内）。这是对创新点 4 中「移植参数」限制的
诚实量化，而不是回避。

### 3.4 LIT-010 的 38 篇原始文献（W5 已完成结构化审计）

对综述表 1 的 38 篇编码 VPR 可重建性、控制律、指标组合、输入公开。结论见 §0 / §1d。
引言可用表述见 `06_PAPER/notes/W5_findings.md` §7。创新点 2 的 TDGTA 不能从这 38 篇
直接外推（检索式是富营养化，0 篇声明 TDG/SYSTDG）；这 38 篇支撑的是
「运行状态很少被当成评估条件来声明」。

### 3.5 CE-QUAL-W2 官方仓库

`github.com/CE-QUAL-W2-ERDC/CE-QUAL-W2`（v4.5 分支含版本摘要）。
用于（a）核实本项目发现的示例缺陷是否为已知问题（issue 检索）；
（b）以 PR/issue 形式回报缺陷——这在 GMD/EMS 审稿中是很受欢迎的社区贡献证据。

---

## 4. 进一步的拓展

### 近期（并入 P1，投稿前完成）

- **T1 溯源歧义的多案例推广：✅ 已完成（W1）。** DeGray 水温与 Columbia DO 内部一致性
  已算出。限制：无独立观测，正文不得写成 skill。若要同构的「对观测 NSE 从负翻正」，
  需另找实测（Columbia 可考虑 ORDEQ/USGS；DeGray 需 1980 年剖面）。
- **T2 DLTMAX×DLTF 扫描：✅ 已完成（W2），结论已降级。** Long Lake INTER ON/OFF ×
  DLTMAX 20/50/100/200 + Columbia 120/360/720。非单调性不能写成普遍定律。
  DLTF 未做二维扫描；INTER OFF 已足够区分「真 DLTMAX」与「插值结点」。
- **T3 跨版本指标漂移：** 同一套输入分别用 v4.5.5 与 v5.0 beta 运行，比较技能指标。
  若同一案例跨版本 NSE 明显移动，则「文献报告的 NSE」还隐含第四个未披露维度——
  版本。这一点做成功会很有分量，且成本低（exe 与示例都在）。**仍待做。**

### 中期（P1 的加分项或 P2 的基础）

- **T4 插桩重编译**：利用已有的 ifort/gfortran，给源码加一个结构化诊断写出器
  （记录 `H1<0` 事件、DLT 轨迹、控制器 binding 状态到 CSV），把 NHR 从
  「解析日志文本」升级为「模型原生输出」。这是把方法论论文变成工具论文的关键一步。
- **T5 跨编译器复现性**：ifort 编译版 vs gfortran 编译版在同一输入下的指标差异。
- **T6 成岩参数的形式化敏感性分析**：针对 Columbia「DeGray 模板移植」这一已知弱点，
  做 Morris 筛选 + Sobol 指数。不要把 SOD=0.88 当成 Columbia 的真值。

### 长期（独立论文）

- **P2（应用+物理型论文）**：《Out-of-sample evaluation of the SYSTDG spillway TDG
  formulation at Bonneville, 2016–2025》。用 DART 公开数据覆盖示例未涉及的十年，
  在**关闭控制器**的条件下检验并重新拟合泄洪道 TDG 产生的回归式。
  **前置：扩展模型时段。** 这是有实质物理内容的论文。
  若用户更想要「物理创新」而非「方法论创新」，应以 P2 为主。
- **P3**：把协议推广到其他二维/三维水质模型（EFDC、Delft3D），做成跨模型的
  评估报告规范。
- **P4（面向国内期刊）**：把协议应用于一座国内水库案例，以中文发表；
  国内 W2 应用文献同样普遍只报 R²，本协议的适用性强。

---

## 5. 工作分解与时间线

| 编号 | 任务 | 支撑创新点 | 预估 | 状态 |
|---|---|---|---|---|
| W1 | DeGray 水温 + Columbia DO 多口径对照 | 1 | 3–4 d | ✅ 完成 |
| W2 | DLTMAX×DLTF 扫描 + NHR 解析器 | 3 | 5–7 d | ✅ 完成（主张已修订） |
| W3 | TDGTA=OFF 溯源一致对照 + 可达范围 | 2 | 2–3 d | ✅ 完成（未重跑） |
| W4 | DART 下载器 + CCIW 核对 + 超标/泄流 | 1,2 | 4–5 d | ✅ 完成；样本外 NSE 未做 |
| W5 | 38 篇溯源报告率结构化审计 | 动机 | 5–6 d | ✅ 完成 |
| W6 | `w2eval` 重构（VPR + 指标面板 + NHR + run-card） | 全部 | 6–8 d | 🔄 **进行中**（MVP） |
| W7 | Almeida & Coelho 基准对照（Columbia SOD 量级） | 4 | 2 d | ✅ 完成 |
| W8 | 图表定稿 + 正文撰写 | — | 10–12 d | ⬜ 待 W6 后再写正文 |
| W9 | Zenodo 归档 + 向官方仓库回报缺陷 | 4 | 2 d | ⬜ 待 W6 |

建议顺序：W1–W5、W7 已完成 → **先完成 W6 MVP** → 再 W8/W9。样本外 NSE 与 T3 可并行，
但不阻塞方法论正文的起草。

## 6. 图表清单（P1）

既有草图在 `06_PAPER/figures/` 与 `06_PAPER/analysis/`（W4 png）。定稿时再统一编号。

- **图 1** 三口径 TDG 时间序列叠加 + CCIW 观测 + TDGTA 目标带（一眼看出封顶）；
  加 OFF 对照见 `W3_tdgta_on_off_timeseries.png`
- **图 2** 三口径 1:1 散点 + 回归线（斜率 1.079 / 0.664 / 1.154）
- **图 3** KGE 分解条形图：r、α、β 三分量并列——**本文的核心图**，
  直观显示 r 不变而 α 剧变；DeGray T2–Tvolavg / STR–GATE 应并入或作附图
- **图 4** R² 对 NSE 的散点（含 38 篇文献值、Bonneville 三口径、DeGray 主对照）
- **图 5** 可达范围图：观测 TDG 直方图 + 控制器上限 120% 竖线（阴影 15.6%）；
  加 2011–2025 年超标比例（`w4_tdg_gt120_annual.png`）
- **图 6** Long Lake DLTMAX 扫描的 NHR（INTER ON 5/4/1/5 vs INTER OFF 全 0）；
  **不要画成跨案例非单调定律**
- **图 7** `w2eval` run-card 示例（VPR + 指标面板 + NHR 三段式）
- **图 8** 2011 泄流：QGT / TDGTA / DART（再分配日 174→39 kcfs）
- **表 1** Bonneville 三口径 + SYSTDG 控制前快照（S）+ OFF
- **表 2** 38 篇溯源报告率审计（W5）
- **表 3** 17 个官方示例的可复现性审计矩阵
- **表 4** DeGray / Columbia 内部一致性主对照（必须标注 `internal_consistency`）
- **表 5** NHR：负厚度 × DLTINTER × DLTMAX；Columbia 对照 0/0/0

## 7. 目标期刊（按推荐度）

1. **Geoscientific Model Development (GMD)** —— 最佳匹配。「model evaluation paper」
   文体，强制代码/数据公开（我们本来就要归档），且 Almeida & Coelho 2025 是
   直接先例。IF 约 4–5，社区声誉高。
2. **Environmental Modelling & Software** —— 若把 `w2eval` 工具做成主角，
   这里比 GMD 更合适。
3. **Water Research / Journal of Hydrology** —— 需要更强的物理/环境结论，
   更适合 P2 而非 P1。
4. **Water (MDPI)** —— 审稿快，且 LIT-010 就发在这里，对该主题接受度高；
   作为 fallback 或 P4 的去处。

## 8. 风险与诚实的自我评估

1. **「没人会犯这种变量错误」的质疑**（最可能的审稿意见）。
   应对：（a）A 口径用的是模型自带公式，是合理选择而非稻草人；
   （b）W5：**38 篇中仅 2 篇可据文重建 VPR，0 篇写出文件/列名**——错误无法被检出，
   正是问题本身；表 2 能确认的 W2↔观测技能只有 1 条；（c）W1 已在水温/DO 通道上
   再现「高 R²、负 NSE」，且必须写清那是内部一致性。
2. **创新点 3：非单调性不是普遍定律。** W2 已把「减小时间步更不稳」降级。
   主主张改为 NHR 必报（负厚度次数、exit 0 是否掩盖、DLTINTER 状态）。
   负厚度目前 **n=1 个水域（Long Lake）**；Columbia / DeGray / Bonneville 完成运行
   的 H1<0 计数均为 0。不能外推到「所有 W2 应用」。
3. **Columbia 成岩参数是移植的**，不能用于任何水质情景推断。
   W7：湿段均值 0.876 gO₂/m²/d，89.6% 在 Almeida 0.5–3.0，无点 >3.0，约 10.5% <0.5。
   这只是量级合理性，不是率定。
4. **本文不是物理机理创新**。若目标是「物理创新」，应改以 P2 为主论文，
   P1 降为其方法学附录或并行短文。P2 的前置是扩展模型时段。
5. **TDGTA=OFF 的对照：最优评估文件随控制器消失，物理量并未被删除。**
   这既是风险也是发现——写成「门控文件 + 控制前快照」，而不是「变量被删」。
6. **样本外技能尚未计算。** 2016–2025 超标 21.2% 只能支撑可达范围叙事，
   不能写成预报检验。审稿人若要求 validation，必须先扩 TMEND。
7. **全文获取 9/38。** W5 的 `unknown` 有 19 篇；付费墙论文的 VPR 可能更好，
   但表 2 里已核对的 OA 篇已足够证明口径混杂。不确定处保持 `unknown`，不编造。

---

## 附：本方案中所有数字的复算入口

- Bonneville 三口径 + SYSTDG S + TDGTA OFF：
  `06_PAPER/analysis/w3_tdgta_off_metrics.json`；
  脚本 `00_INDEX/eval_w3_tdgta_off.py`（复用 `eval_bonneville_tailwater.py` 的
  `load_csv_skip` / `tdg_from_n2_do` / `align`）。
  运行目录：`05_REPRO_RUNS/run_20260814_bonneville/Bonneville_SYSTDG/` 与
  `…/run_20260814_bonneville_notarget/Bonneville_SYSTDG/`。
- DeGray T / Columbia DO 内部一致性：`06_PAPER/analysis/w1_provenance_metrics.json`；
  脚本 `06_PAPER/analysis/w1_w7_provenance.py`。
- DART / 泄流：`06_PAPER/analysis/w4_cciw_vs_dart.json`；
  脚本 `00_INDEX/download_dart_cciw.py`。
- 38 篇审计：`w5_lit_audit_summary.json`、`w5_lit_audit.csv`。
- Columbia SOD：`w7_columbia_sod_vs_almeida.json`。
- NHR：`00_INDEX/parse_nhr.py`；`nhr_existing_runs.json`；`nhr_dlt_scan.json`。
- 负厚度机理：`02_LIBRARY/05_source/github_v4.5/model/w2_model_source/w2_4_win.f90` L1415–1424；
  `layeraddsub.F90` L241–242、L767、L1277；`update.F90` L152–163（DLTINTER）。
- 示例套件审计：`02_LIBRARY/06_examples/{v4.5.5,v5.0_beta}/`（8+9 个案例）。
- run-card：`06_PAPER/w2eval/`（W6）。
