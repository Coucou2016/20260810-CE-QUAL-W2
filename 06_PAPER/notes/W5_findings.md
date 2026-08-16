# W5 发现：38 篇 CE-QUAL-W2 富营养化研究的变量溯源报告率审计

日期：2026-08-15  
综述：Benicio, Basso & Formiga, *Water* 2024, 16:3556, doi:10.3390/w16243556（库内 LIT-010）  
编码表：`06_PAPER/analysis/w5_lit_audit.csv`  
计数：`06_PAPER/analysis/w5_lit_audit_summary.json`  
未 git commit，未跑模型。

---

## 1. 方法

编码对象是综述声明筛选出的 **38 篇**。清单取自综述表 1 全部行，对应参考文献 **[12]–[14]、[18]、[21]–[54]**。表 1 行数 = 38，与正文「38 selected」一致，**无篇数差异**。参考文献 [1]–[11]、[15]–[17]、[19]–[20]、[55]–[65] 不是纳入研究。

每篇一行，字段见 CSV 表头。关键定义（与 JSON `definitions` 一致）：

- **VPR（变量溯源记录）**：输出文件、列名、断面 I、层 K、单位、派生链、时间支撑、配对容差。
- **vpr_reconstruct（仅凭论文）**：`yes` = 同时给出可定位的断面（I 或已映射站点）、层/采样深度、对照变量、对照时段，第二名分析者能抽出同一条序列。**不要求**写出 TSR/PRF 文件名（本批 38 篇无人写出文件名）。`partial` / `no` / `unknown` 见 JSON。
- **control-rule**：`described` / `not_mentioned` / `NA`。TDG 目标在这 38 篇里全部为 N/A（综述检索式是富营养化/藻，不含 SYSTDG/TDG）。
- **不确定不编造**：付费墙且摘要不够 → `unknown`，并写原因。`fulltext=false` 表示只读了摘要 + 综述表 + 偶尔的二手引用。

全文来源（合法 OA，未破解 PDF）：SciELO、Water SA、MDPI HTML（经检索抓取）、Springer OA、Nature Scientific Data、UFC 机构库、IWA HTML。Crossref / OpenAlex 用于 DOI 与 OA 状态。MDPI 直接 PDF 与 IWA PDF 在本环境被拦；OpenAlex 标为 green OA 的 [14]、[46] 未给出可用 PDF。

---

## 2. 纳入清单（38）

| [n] | 年 | 第一作者 | 场地 | fulltext |
|---:|---:|---|---|---|
| 12 | 2022 | Mesquita | Santo Anastácio, BR | true |
| 13 | 2022 | Rocha | Santo Anastácio, BR | true |
| 14 | 2013 | Deus | Tucuruí, BR | false |
| 18 | 2023 | Hanjaniamin | Yamchi, IR | true |
| 21 | 2008 | Debele | Cedar Creek, US | false |
| 22 | 2023 | Masoumi | Karkheh, IR | false |
| 23 | 2023 | Neto | Santo Anastácio, BR | true |
| 24 | 2020 | Mesquita | Santo Anastácio, BR | true |
| 25 | 2022 | Ijaz | Xiangxi / TGR, CN | false |
| 26 | 2023 | Almeida | Furnas lagoon, PT | false |
| 27 | 2022 | Terry | Buffalo Pound, CA | true |
| 28 | 2022 | Nazari-Sharabian | Mahabad, IR | false |
| 29 | 2022 | Yosefipoor | Ilam, IR | false |
| 30 | 2022 | Kheirkhah | Behesht-Abad, IR | false |
| 31 | 2021 | Almeida | Montargil, PT | true |
| 32 | 2021 | Akomeah | Diefenbaker, CA | false |
| 33 | 2021 | Yahyaee | Seimare, IR | false |
| 34 | 2021 | Morales-Marín | Diefenbaker, CA | false |
| 35 | 2020 | Hasanzadeh | Behesht-Abad/Kaj, IR | false |
| 36 | 2019 | Lindenschmidt | Diefenbaker, CA | true |
| 37 | 2019 | Aghasian | Gotvand, IR | false |
| 38 | 2019 | Moridi | Dousti, IR/TM | false |
| 39 | 2019 | Ziaie | Zayandeh Roud, IR | false |
| 40 | 2019 | Kim | Uiam, KR | false |
| 41 | 2018 | Dehbalaei | Ilam, IR | false |
| 42 | 2017 | Yazdi | Seimare, IR | false |
| 43 | 2016 | Shourian | Ilam, IR | false |
| 44 | 2016 | Masoumi | Karkheh, IR | false |
| 45 | 2015 | Noori | Karkheh, IR | false |
| 46 | 2015 | Park | Yeongsan, KR | false |
| 47 | 2014 | Park | Yeongsan/Yeongam/Kumho, KR | false |
| 48 | 2015 | Chang | Hsin Shan, TW | true |
| 49 | 2012 | Afshar | Karkheh, IR（系统动力学+W2） | false |
| 50 | 2010 | Lee | Daecheong, KR | false |
| 51 | 2009 | Liu | Mingder, TW | false |
| 52 | 2009 | Afshar | Karkheh, IR | false |
| 53 | 2006 | Kuo | Te-Chi / Tseng-Wen, TW | false |
| 54 | 2003 | Kuo | Feitsui, TW | false |

表 1 年份笔误：[26] 表中写 2022，Crossref 为 2023。[30] 场地栏 OCR 成 “(Will)”，实为伊朗。

---

## 3. 主要比例（真实计数，不为叙事凑数）

分母均为 **38**，除非另行注明。

| 项目 | 计数 | 比例 |
|---|---:|---:|
| 全文可读（方法+率定结果） | 9 | **23.7%** |
| 仅凭论文可重建 VPR（`yes`） | 2 | **5.3%** |
| VPR `partial` | 6 | 15.8% |
| VPR `no` | 11 | 28.9% |
| VPR `unknown`（无全文且摘要不够） | 19 | 50.0% |
| 写出 W2 **输出文件/列名**（`vpr_variable=yes`） | **0** | 0% |
| 对照位置写到断面 I 或已映射站点（`vpr_location=yes`） | 3 | 7.9% |
| 报告 R²（任一模型） | 11 | 28.9% |
| 报告 NSE | 2 | 5.3% |
| 其中 NSE 明确用于 **W2** | 1（[31] 方法声明；W2 水温/DO 的 NSE 数值未在抓取 HTML 中列出） | 2.6% |
| 报告 KGE | **0** | 0% |
| 报告 PBIAS | 1 | 2.6% |
| 报告 RMSE | 7 | 18.4% |
| 报告 MAE/AME | 4 | 10.5% |
| 报了 R² 且不报 NSE | 9 | **23.7%**（占报 R² 者的 **81.8%**） |
| 公开 W2 输入/代码 | 1 | 2.6%（[36] FRDR） |
| 率定/验证时段分开（`yes`） | 16 | 42.1% |
| 继承前人率定 | 8 | 21.1% |
| 控制律 `described` | 11 | 28.9% |
| 控制律 `NA`（非调度/取水论文） | 24 | 63.2% |
| 控制律相关但未声明状态 | 3 | 7.9% |
| 声明 TDG 目标/SYSTDG | **0** | 0% |

可重建 VPR 的 2 篇：

1. **[23] Neto 2023**：出口 = 段 31 第二格，进口 = 段 2 第二格；T/DO/Chl-a/PO4；2013 率定 / 2019 验证。仍缺输出文件名与配对容差。
2. **[48] Chang 2015**：Station 1 → **段 3 表层**；采样 0.5–1 m；AME/RMSE/R²；2004–2008 / 2009–2012。仍缺文件名。该文**不在综述表 2**。

`partial` 的 6 篇（全文为主）：[18][24][27][31][36][53]。其中 [36] 若连 FRDR 输入包一起算，实际可重建，但协议是「仅凭论文」，故仍为 partial。

---

## 4. 综述表 2 的 R² vs 能否重建 VPR

表 2 只有 **12/38** 篇。把表中数字当成「W2 对观测的率定技能」时，**经全文或综述自己的正文核对，只有 1 条成立**。

| 表 2 R² | 参数（表 2 所写） | [n] | 表中数字是不是 W2↔观测技能？ | 仅凭论文重建 VPR |
|---:|---|---:|---|---|
| 0.32 | DO, Chl-a, PO4 | 23 | **是**（出口 DO/Chl-a/PO4 合成 R²） | **yes** |
| 0.6781 | DO | 18 | **否**。综述 §3.7：这是气温与入库水温相关 | partial |
| 0.92 | 水位、水温、DO | 26 | unknown（无全文；综述 §3.6 写 W2 水位/T/DO） | unknown |
| 0.70 | TP | 13 | **否**。入库 TP–流量幂律 | no |
| 0.76 | TP | 12 | **否**。完全混合 TP 与蒸发皿系数 K（旱季） | no |
| 0.92 | Flow, TN, TP | 31 | **否**。0.92 是 **W2 水位**；Flow/TN/TP 的 R² 来自 SWAT（0.71/0.59/0.14） | partial |
| 0.41 | TP（旱季） | 24 | **否**。K 与 TP 相关 | partial |
| >0.9 | 水位、水温、SS | 40 | unknown（无全文） | unknown |
| 0.62–0.95 | DO, T, TDS, TN, TP | 42 | unknown。综述 §3.6 写的是 **R 而非 R²** | no |
| 0.977 | TP | 51 | **否**。磷负荷削减与 TP 的情景响应曲线 | no |
| 0.906 | DO, T | 21 | unknown。综述 §3.6 写 **R=0.906**，表 2 写成 R² | no |
| 0.9605 / 0.9724 | TP, NH3, NO2/NO3, Chl-a, DO | 53 | **否**。1998/1999 年磷负荷削减相关（§3.7） | partial |

补充：综述 §3.2 用 [48] 的 DO R²=0.49、NH3 R²=0.51 讨论「Calibration Variability」，但这篇**没有进入表 2**；而表 2 最高的两个 R²（0.977、0.96）都不是拟合优度。

---

## 5. 对创新点 1 动机的支撑强度

P1 主张：跨研究比较 R² 在方法上不成立，因为缺少（i）输出变量/断面/层，（ii）控制律，（iii）数值健康。W5 把（i）（ii）从定性变成计数。

**支撑强的部分（有硬计数）：**

1. **38 篇中仅 2 篇（5.3%）可据文重建 VPR**；**0 篇**写出 W2 输出文件或列名。表 2 那条 0.32–0.977 的「率定质量」轴，在变量溯源上几乎是空的。
2. **表 2 的 12 个数里，能确认是 W2↔观测技能的只有 1 个（[23] 的 0.32）**。其余是蒸发皿相关、入库浓度回归、情景响应曲线、或把 SWAT/R 误标成 W2 R²。这比「没写断面」更重：表 2 在比较不同数学对象。
3. **报 R² 的 11 篇里 9 篇不报 NSE（81.8%）**；**KGE = 0**；PBIAS 仅 1 篇。这与创新点 1 的理论命题一致：只报 R² 看不见 α/β，也看不见变量误指认。
4. **公开输入的只有 1 篇（[36]）**。官方示例套件之外，文献层同样几乎不可复现。

**支撑中等、需在正文里写清边界的部分：**

- 控制律：11 篇描述了选择性取水/泄流层/渠道调度，但对象是富营养化调度，**不是 TDG 控制器**。创新点 2 的 TDGTA 案例不能从这 38 篇直接外推；这 38 篇能支撑的是「运行状态很少被当成评估条件来声明」。
- NSE 在 W2 上几乎不出现（明确声明者 1 篇），但 29 篇无全文，真实 NSE 使用率可能略高于 1/38。方向不会翻：OA 全文 9 篇里，W2 NSE 数值仍基本缺席。

**不能声称的：**

- 不能说「38 篇都只报 R²」——11 篇报了 R²，其余多数连 R² 也没在可核段落出现，或只报 AME/RMSE。
- 不能说表 2 的 0.32 与 0.977 是同一口径的技能差距——0.977 不是技能。

一句话给引言：综述用一张 R² 表概括 38 篇的率定质量；审计显示其中可确认的 W2 观测技能只有 1 条，可据文重建对照序列的只有 2 篇，无人给出输出文件名，无人报告 KGE。

---

## 6. 局限

1. **综述偏富营养化**，检索式含 reservoir + CE-QUAL-W2 + eutrophication/algae/phytoplankton/cyanobacteria。不含 SYSTDG、TDG、Bonneville 类工程案例。创新点 1 的 Bonneville 三口径证据是本项目实证，不是这 38 篇里的发现。
2. **全文获取率 23.7%（9/38）**。`unknown` 有 19 篇。付费墙论文的 VPR 可能比摘要更好，但表 2 里已核对的 OA 篇已经足够证明「表 2 口径混杂」。
3. **二手指标**：Ziaie [39]、Kuo [53] 的 MAE/RMSE 来自后来论文的引用，CSV 已标明 secondary，未当作已核原文。
4. **继承率定**：Santo Anastácio（[12][13]←[24]）、Diefenbaker（[32][34]←Sadeghian）、Yeongsan（[46]←[47]）把 VPR 推到另一篇；本审计按「本篇能否重建」编码为 inherited/no。
5. **[49] Afshar 2012** 更像系统动力学模型而非标准 W2 输出评估，仍保留在 38 篇内因为综述表 1 收录了它。
6. 未评估数值健康（NHR）；综述与原文几乎都不报告 `w2.wrn` / 负厚度 / DLT 回退。

---

## 7. 给 P1 引言可用的表述（不夸大）

> Benicio 等（2024）综述纳入 38 篇 CE-QUAL-W2 富营养化应用，并以表 2 的单一 R²（0.32–0.977）概括率定质量。对这 38 篇的结构化审计表明：仅 2 篇（5.3%）可据正文重建对照用的断面/层/变量；0 篇给出模型输出文件名；表 2 的 12 个 R² 中仅 1 个能确认为 W2 输出对观测的拟合优度，其余为相关分析、负荷情景曲线或把流域模型指标误标为水库模型技能。报告 R² 的 11 篇中 9 篇不报告 NSE；KGE 为 0。因此，跨研究比较这些 R² 在方法上缺乏共同的变量溯源。
