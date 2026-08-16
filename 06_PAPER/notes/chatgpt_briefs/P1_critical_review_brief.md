# P1 critical review brief（本地；不上传文件）

**Date:** 2026-08-16  
**Role for ChatGPT:** 外部 GMD 审稿级顾问（只审论证；不得编造数字）  
**Role for Cursor:** 读 JSON/源码、改文件、验收；ChatGPT 结论不得直接采信  

---

## 1. 项目背景

CE-QUAL-W2（W2）二维水温水质模型复现工作区。主稿 P1 目标期刊 *Geoscientific Model Development*（model evaluation paper），论证：跨研究比较拟合优度在方法上不成立，除非公开 **VPR**（变量溯源）、**控制器条件化评估 + 可达范围**、**NHR**（数值健康记录）。实证来自官方案例复现（Bonneville / DeGray / Columbia / Long Lake）+ 38 篇文献审计（Benicio et al. 2024）+ DART 小时核对；**不重跑**完整积分写稿。

权威数字：`06_PAPER/analysis/*.json` 与 `06_PAPER/w2eval/cards/`。草稿：`06_PAPER/drafts/P1_GMD_draft_v1.md`。

---

## 2. 源码 / 工作区基线

| 项 | 值 |
|---|---|
| 路径 | `I:\Projects\20260810-CE-QUAL-W2` |
| Git | **无 `.git` 仓库**（`git status` fatal）。无 branch/commit。working tree = 普通目录。 |
| AGENTS.md / CLAUDE.md | 不存在 |
| 用户未提交修改 | 无 git 可追踪；本轮只新增/改 `06_PAPER/notes/` 与必要时草稿最小编辑 |

---

## 3. 硬约束（顾问不得违反；执行者据此否决建议）

1. **不编造数字。** 一切 NSE/R²/计数以 JSON 为准。  
2. **DeGray 水温、Columbia DO = internal consistency**，不是对观测 skill。  
3. **门控文件 ≠ 物理量删除。** `TDGTA=OFF` 删 `TDGTarget_output.csv`；SYSTDG 仍写 `TDG_output.csv`（控制前快照，ON/OFF MAE=0），不能顶替 B。  
4. **NHR 必报 ≠「减小时间步更不稳」定律。** 5/4/1/5 仅 Long Lake + `DLTINTER=ON`；OFF 全 0。  
5. **无样本外 NSE。** `computed_nse=false`；2016–2025 只做超标频率。  
6. **Columbia SOD = DeGray 模板移植（31→50）**，量级检查非现场率定，禁止情景推断。  
7. **W5：** 全文 9/38；unknown 保留；不要写「38 篇都只报 R²」。  
8. 禁止建议：上传附件、编造观测、把内部一致性改写成 calibration skill、开 OOS 长跑作为本轮必做。

---

## 4. 五个主张摘要 + 关键数字（摘自 JSON）

### Claim 1 — 变量溯源

- Bonneville ON vs CCIW，*n*=1614，窗 40613.583–40681.542：  
  A NSE=−2.8044 / B=+0.5000 / C=−2.752；*R*² 0.5082–0.5512。  
- DeGray T2 vs Tvolavg：*R*²=0.9027，NSE=−0.5855（内部一致性）。  
- Columbia I=49 vs I=33：*R*²=0.6505，NSE=−1.4821（内部一致性）。  
- W5：VPR reconstructable 2/38（5.3%）；文件/列名 0/38；表 2 确认 W2↔obs skill 1/12（Lima Neto 0.32）；only_r2_not_nse 9/11（81.8%）；KGE=0。

### Claim 2 — 控制律混淆

- 技能最好序列只在 `TDGTarget_output.csv`（ON B：NSE=0.5，β=0.9986，sim_max=120.09%）。OFF → 文件 absent。  
- S=`TDG_output.csv` 控制前快照；ON/OFF MAE=0；不能顶替 B。  
- 配对观测 251/1614（15.55%）>120%。  
- DART：小时 *n*=17805，MAE=0.026537%，match_rate_|Δ|≤0.051=0.994945。  
- 2016–2025：21.2% 有效小时 >120%；**非 NSE**。  
- 泄流：QGT vs DART *r*=0.868638；再分配日 *n*=116，均值 173.8573→39.2308 kcfs，*r*=−0.596447。

### Claim 3 — 数值健康

- Long Lake DLTINTER ON，DLTMAX 20/50/100/200：负厚度 **5/4/1/5**；OFF：**0/0/0/0**。  
- H1<0 仅 Long Lake（已完成案例中）。主张 = 报告 NHR，非时间步定律。

### Claim 4 — 示例可复现性 + SOD

- 17 示例几乎仅 Bonneville 有实测；Long Lake 缺 HabitatFiles；Columbia 缺成岩文件。  
- SOD 湿段 *n*=1081，mean=0.8762；968/1081（0.8955）在 Almeida 0.5–3.0；无点 >3.0。

### Claim 5（协议）

- `w2eval` 五张 run-card；不跑模型。Zenodo DOI **未铸**。

---

## 5. 分条消息计划（粘贴文本，不上传）

| 消息 | 内容 |
|---|---|
| CONTEXT 1 | 本 brief §1–4（背景、基线、硬约束、五主张+数字）+「未完勿下最终结论」 |
| CONTEXT 2 | 草稿 Results §4.1–4.2 关键段（Bonneville 三口径、DeGray/Columbia、控制律三句、DART/泄流） |
| CONTEXT 3 | Results §4.3–4.4 + Discussion §5.1–5.3 关键段 |
| END OF CONTEXT | 正式任务 + 六项交付物 |

---

## 6. 需要 ChatGPT 做的事

GMD 审稿级 **critical review**（英文交付即可）：

1. 对论文问题理解（一段）  
2. 论证中最弱的 3–5 点  
3. 必须降级/改写的句子清单（引用或 paraphrased 原文）  
4. Abstract + Conclusions 改写建议（可整段替换）  
5. 审稿人可能攻击点 + 预答  
6. 不确定事项  

**不要**重算数字、不要建议编造观测、不要要求本轮做 OOS。
