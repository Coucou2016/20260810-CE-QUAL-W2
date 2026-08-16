# P1 中文对应大纲（审阅用）

对应英文稿：`P1_GMD_draft_v1.md`  
工作题名：变量溯源、控制律混淆与数值健康度——论 CE-QUAL-W2 拟合优度跨研究比较的条件性及其评估协议  
目标期刊：GMD（model evaluation paper）  
规则：数字以 JSON 为准；DeGray / Columbia ≠ 对观测技能；不要写物理量被删；NHR 必报而非时间步定律；无样本外 NSE。  
措辞（2026-08-16）：跨研究 GOF 主张用「条件可比 / 不能仅凭指标断定可直接比较」，避免绝对「不可比」。

---

## 文首：未决差异（英文稿已按 JSON 改）

主张：笔记/方案若与 JSON 四舍五入或 v1 口径名冲突，**以 JSON 为准**。  
要点：B 口径是 `TDGTarget_output.csv` 不是 SYSTDG 文件名；SOD 带内 0.8955（968/1081）不是口算 89.6%；配对窗 40613.583–40681.542；泄流用 173.8573→39.2308 kcfs。

---

## Abstract（摘要）

**主张一句话：** 跨研究比较 W2 拟合优度时，不应仅凭同一统计量就假定评估对象同类；须同时公开变量溯源（VPR）、控制律状态与可达范围、以及数值健康记录（NHR），否则直接可比性一般无法从指标本身建立。  
关键数字：38 篇仅 2 篇可重建 VPR、0 篇写出文件/列名、表 2 仅 1 条确认为 W2↔观测技能；Bonneville *n*=1614，*R*² 0.508–0.551，NSE −2.804 / +0.500 / −2.752；DeGray/Columbia 为内部一致性；门控文件消失≠物理量删除；5/4/1/5 仅 DLTINTER=ON；2016–2025 无 NSE。

---

## 1 Introduction（引言）

**主张一句话：** Benicio 等（2024）用一张 *R*² 表概括 38 篇率定质量，但审计表明缺 VPR、缺控制律声明、缺数值健康，表 2 还在比较不同数学对象。  
要点：不要写「38 篇都只报 *R*²」；不要把 0.32 与 0.977 写成同一口径技能差距；全文 9/38，unknown 必须保留；Almeida & Coelho 2025 是文体先例而非本文 SOD 率定。

---

## 2 Model and cases（模型与案例）

**主张一句话：** 同一物理量从 TSR / WDO / PRF / SNP / 结构闸门 / SYSTDG / TDGTA 多通道写出，评估对象必须按文件与派生链区分。  
要点：TDGTA 是优化控制器；`TDG_output.csv` 在再分配前写入；H1<0 回退仍 exit 0；DLTINTER=ON 时 day-30 结点是插值起点不是窗内硬顶；三个案例角色不同——Bonneville 对观测、DeGray/Columbia 内部一致性、Long Lake 数值健康；Columbia SOD 参数来自 DeGray 移植。

---

## 3 Protocol（协议：VPR / 条件化评估 / NHR / w2eval）

**主张一句话：** 任何 W2 评估应公开 VPR 八元组、按控制器是否 binding 分层并声明可达范围、以及从 wrn/err/SNP 解析的 NHR；`w2eval` 只读 JSON 写 run-card，不跑模型。  
要点：A/C 配对容差 0.05 d，B/S 为 0.6 d；KGE 用 Gupta 2009；*R*²=*r*² 对仿射变换不变；W5 全文局限写进方法；W4 明确 `computed_nse=false`。

---

## 4.1 Results — 变量溯源

**主张一句话：** 只换「把哪条输出叫做 TDG/T/DO」，*R*² 可以几乎不动而 NSE/KGE 因 α、β 崩溃；该模式在 Bonneville 是对观测技能，在 DeGray/Columbia 只是通道内部一致性。  
Bonneville：同一 CCIW，窗 JDAY 40613.583–40681.542，*n*=1614；*R*² 最高的 C 口径正是 NSE 最差之一；A 口径是源码自带亨利公式，不是稻草人。  
DeGray：T2 vs Tvolavg *R*²=0.9027 而 NSE=−0.5855（α=0.35，β=0.61）；STR vs GATE *R*²=0.534 而 NSE=−6.58；GATE≈T2 只是该高程，不能推广。  
Columbia：三站 NSE 全 < −1.48；*R*² 最高一对（0.6505）NSE 仍为负；浅汊表/底 NSE=0.91，错站比错层危险。  
文献：可重建 VPR 2/38；表 2 确认技能 1/12；KGE=0。

---

## 4.2 Results — 控制律混淆

**主张一句话：** 技能最好、β≈1、封顶 120.1% 的序列只存在于控制器门控文件；关掉 TDGTA 文件消失，物理量仍由 SYSTDG 写到控制前快照，ON/OFF mae=0，不能顶替 B。  
要点：OFF A NSE=−2.337 仍远差于均值预报；OFF S 能过 120% 但配对到不了观测 129.1%；库内 CCIW vs DART *n*=17805，MAE=0.026537%，示例观测未被改写；2016–2025 有效小时 21.2%>120% **不是**预报 NSE；再分配日 116 天把泄流从 173.86 kcfs 压到 39.23 kcfs（*r*=−0.60）。

---

## 4.3 Results — 数值健康

**主张一句话：** NHR 必须报告（负厚度次数、exit 0 是否掩盖、DLTINTER 状态）；5/4/1/5 仅官方 INTER ON 结点扫描，INTER OFF 全 0，H1<0 只在 Long Lake 出现，不能写成「减小时间步更不稳」定律。  
要点：INTER ON 时 DLTMAX=20 窗内实际 DLT 仍达 231 s；INTER OFF 20 s 的 NV=7.75% 但负厚度=0；Columbia 120/360/720 为 0/0/0；层增减本身不是错误。

---

## 4.4 Results — 官方示例可复现性

**主张一句话：** 17 个官方案例里只有 Bonneville 附带实测；Long Lake 缺 HabitatFiles；Columbia 成岩文件缺失，本项目 SOD 是 DeGray 模板移植的量级检查，不是现场率定。  
要点：湿段 SOD 均值 0.8762 gO₂ m⁻² d⁻¹；968/1081 落在 Almeida 0.5–3.0；无点 >3.0；不能做水质情景推断。`w2eval` 五张卡已落盘。

---

## 5 Discussion（讨论）

**主张一句话：** 仅报 *R*² 不能建立溯源等价；α/β/NSE 也只是互补诊断、不能「证明」溯源。审稿预答已扩：非套话式创新、17 例是失败模式演示而非全框架验证、三件套是报告建议而非强制标准；v1 过时表述已降级。  
预答：A 口径非稻草人；DeGray/Columbia 不得写成 skill；样本外 NSE 未做；全文率 9/38 限制 unknown 精度但不推翻表 2 口径混杂；confirmed-absent ≠ unknown。

---

## 6 Conclusions（结论）

**主张一句话：** 跨应用 GOF 应视为条件可比；在缺少足够的 VPR、控制律条件化声明和 NHR 时，不应仅凭同一统计量假定评估对象同类。三件套是报告建议，不是强制社区标准。

---

## 7 Code and data availability

**主张一句话：** 权威数字在 `06_PAPER/analysis/*.json` 与 run-card；尚未 Zenodo。  
列出运行目录、脚本、DART 原始小时、v4.5 源码与 `w2_v455_ifx.exe`。

---

## 8 References（最低集合）

- Benicio et al., 2024, Water 16:3556  
- Almeida & Coelho, 2025, GMD 18:6135  
- Wells, 2002（LIT-011 实际题名）；Cole & Wells, 2003（Instruction Report EL-03-1）  
- Gupta et al., 2009（KGE）；Nash & Sutcliffe, 1970  
- Chang et al., 2015（Water 7:1687–1711）；Lima Neto, 2023（RBRH 28:e8）—英文稿 References 已补全（2026-08-15）

---

## 用户审稿时请先核对的 5 个主张（应对英文稿）

1. DeGray 水温、Columbia DO = **内部一致性**，不是对观测技能。  
2. 创新点 2：最优序列只在 `TDGTarget_output.csv`；`TDG_output.csv` 是控制前快照，ON/OFF mae=0，**不能**写成物理量被删，也**不能**顶替 B。  
3. 创新点 3：主主张是 **NHR 必报**；5/4/1/5 仅 DLTINTER=ON；INTER OFF 全 0；H1<0 只在 Long Lake。  
4. 样本外 NSE **未做**；DART 2016–2025 只用于超标频率与 CCIW 核对。  
5. Columbia SOD 是 DeGray 模板移植；W5 全文 9/38 与 unknown 已写入方法局限；Bonneville 配对窗以 JSON 为准（40613.583–40681.542，*n*=1614）。
