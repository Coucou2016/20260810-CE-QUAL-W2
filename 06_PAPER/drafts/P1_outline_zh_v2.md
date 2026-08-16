# P1 中文对应大纲 v2（审阅用）

对应英文稿：`P1_GMD_draft_v2.md`（v1 保留不改）  
蓝图：`P1_MERGED_BLUEPRINT.md`  
工作题名：变量溯源、控制状态输出与数值健康：面向 CE-QUAL-W2 拟合优度报告的方法学评估框架  
目标期刊：GMD（**Methods for assessment of models**）  
规则：数字以 JSON 为准；DeGray / Columbia ≠ 对观测技能；不要写物理量被删；NHR 应随技能报告而非时间步定律；无样本外 NSE；unknown ≠ confirmed absent。

相对 v1 结构：新增 §2 证据分类；原「模型与案例」拆入 §3 方法 + §4 演示语料；结果按发现重组为 §5.1–5.5；讨论/结论顺延为 §6–7；代码数据为 §8。图号 Fig.1–8 / Table 1–5 **不变**。

---

## 文首：未决差异（同 v1，仍按 JSON）

B 口径=`TDGTarget_output.csv`；SOD 带内 0.8955；配对窗 40613.583–40681.542；泄流 173.8573→39.2308 kcfs。

---

## Abstract

**主张：** 跨研究比较 W2 拟合优度时，不应仅凭同一统计量假定评估对象同类；须公开 VPR、控制状态溯源、NHR 与 run-card，否则直接可比性一般无法从指标本身建立。  
关键数字同 v1（38 篇审计；Bonneville *n*=1614；门控≠删物理量；5/4/1/5 仅 INTER ON；无 OOS NSE）。

---

## 1 Introduction

**主张：** Benicio 表缺 VPR/控制律/NHR；表 2 混杂数学对象。锚定 Bennett（评估条件透明）+ Gupta（KGE/αβ）+ Almeida（GMD 过程评估先例，本文为互补评估层）。  
贡献句 C1–C4 用框架 falsifiable 模板（show / identify / propose / implement）。

---

## 2 Evidence taxonomy（新增）

**主张：** 区分观测技能 / 内部一致性 / 数值健康 / 可复现性（量级合理性）；混进一张技能表是范畴错误。  
核心对：GOF 是「模型量×配对×处理×配置×指标」的属性；条件可比，非绝对不可比。

---

## 3 Assessment methods

**主张：** 评估对象可重建：输出架构 + VPR 八元组 + 控制状态条件化 + NHR + 指标（*R*² 仿射不变）+ w2eval + W5/W4 方法。  
§3.1–3.2：多通道写出；H1<0 回退仍 exit 0。  
§3.3–3.9：原协议全文，编号顺延。

---

## 4 Demonstration corpus

**主张：** 官方案例是**演示语料**，不是多站点率定验证。  
Bonneville=观测技能；DeGray/Columbia=内部一致性；Long Lake=NHR；SOD=移植量级；W5=文献缺口。

---

## 5.1 Results — 变量溯源（观测 + 文献）

**主张：** 只换输出通道，*R*² 可几乎不动而 NSE/KGE 因 α、β 崩溃（Bonneville 对 CCIW）。  
先 Fig.3 一眼检验，再 Table 1、Fig.1–2；文献审计 Table 2 / Fig.4。  
DeGray/Columbia **不在本节**（移至 §5.3）。

---

## 5.2 Results — 控制状态 / 门控输出

**主张：** 最优序列只在 `TDGTarget_output.csv`；OFF 文件消失；SYSTDG 快照 mae=0，不能顶替 B。  
Fig.5 / Fig.8；DART 超标频率≠预报 NSE。

---

## 5.3 Results — 内部一致性（负对照）

**主张：** DeGray / Columbia 通道互比是 provenance 诊断，不是技能。  
Table 4 放本节；Fig.3b/3c、D*/C*。

---

## 5.4 Results — 数值健康

**主张：** NHR 应随技能报告；5/4/1/5 仅 Long Lake + INTER ON；OFF 全 0；非时间步定律。  
Fig.6；Table 5。

---

## 5.5 Results — 可复现 / SOD / run-card

**主张：** 17 例仅 Bonneville 有实测；SOD 移植量级检查；`w2eval` 三块卡。  
Fig.7；Fig.S1；Table 3。

---

## 6 Discussion

**主张：** 条件可比；Bennett/Gupta 理论脊；Almeida=互补非竞争；审稿预答保留；三件套=报告建议≠强制标准。

---

## 7 Conclusions

**主张：** 三主张 + run-card；无强制社区标准；无 OOS NSE。

---

## 8 Code and data availability

权威数字在 `analysis/*.json`；尚未 Zenodo。

---

## 用户审稿时请先核对的 5 个主张

1. DeGray / Columbia = **内部一致性**（现 §5.3）。  
2. 门控文件消失 ≠ 物理量被删（§5.2）。  
3. NHR 应报；5/4/1/5 仅 INTER ON（§5.4）。  
4. 样本外 NSE **未做**。  
5. SOD 移植 + W5 9/38 + 配对窗 JSON。
