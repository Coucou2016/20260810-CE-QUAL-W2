# P1 用户审阅清单（中文）

对应：`P1_GMD_draft_v2.md`（英文合并稿；v1 保留）、`P1_outline_zh_v2.md`、`P1_MERGED_BLUEPRINT.md`。  
性质：可投稿**结构**稿，不是最终投稿。未 git commit，未重跑 W2。

**相对 v1：** 文体锁定 GMD Methods for assessment；新增证据分类；结果按发现分节（§5.1–5.5）；图号不变。

---

## 1. 先核对五个主张（建议按这个顺序读）

| # | 主张 | 英文稿位置 (v2) | 应看到的写法 | 不应看到的写法 |
|---|---|---|---|---|
| 1 | DeGray T、Columbia DO 是内部一致性 | §2、§4、§5.3、Table 4 | *internal consistency*；无独立观测 | “率定技能”“calibration skill” |
| 2 | 门控文件，不是物理量被删 | §5.2.1；Table 1 的 B/S | B=`TDGTarget_output.csv`；S 控制前快照 ON/OFF MAE=0 | “关掉控制器 TDG 变量消失/被删” |
| 3 | NHR 应报，不是时间步定律 | §5.4、Table 5、§6.2 | 5/4/1/5 仅 INTER ON；OFF 全 0；H1<0 仅 Long Lake | “减小时间步更不稳”作为普遍结论 |
| 4 | 无样本外 NSE | Abstract、§3.9、§5.2.2 | 2016–2025 只做超标频率；`computed_nse=false` | 把 21.2%>120% 写成预报检验 |
| 5 | SOD 移植 + W5 全文局限 + 配对窗 JSON | §4、§3.8、§5.1、§5.5 | DeGray 模板 31→50；全文 9/38、unknown 19；窗 40613.583–40681.542，*n*=1614 | 假装 Columbia 现场率定；假装 38 篇都读了全文 |

Bonneville 对观测技能（A/B/C vs CCIW）**可以**写 skill；不要把这种写法套到 DeGray/Columbia。

---

## 2. 关键表（数字应对 JSON，不应对笔记圆整）

| 表 | 内容 | 权威文件 |
|---|---|---|
| Table 1 | Bonneville ON/OFF × A/B/C/S | `analysis/w3_tdgta_off_metrics.json` |
| Table 2 | 38 篇 VPR/指标审计 | `analysis/w5_lit_audit_summary.json` |
| Table 3 | 17 示例可复现性 | 方案已核实事实；未跑的案例不要补造 pass/fail |
| Table 4 | DeGray / Columbia 内部一致性 | `analysis/w1_provenance_metrics.json` |
| Table 5 | NHR：负厚度 × DLTINTER × DLTMAX | `analysis/nhr_dlt_scan.json` |

抽查：ON B NSE=+0.500、配对 max=120.09%；OFF B = file_absent；T2–Tvolavg *R*²=0.9027、NSE=−0.5855；INTER ON 负厚度 5/4/1/5；SOD 968/1081 在 0.5–3.0。

Run-card 交叉：`w2eval/cards/bonneville_tdgta_{on,off}.md`、`degray_t_internal.md`、`columbia_do_internal.md`、`longlake_dlt_nhr.md`。

---

## 3. 关键图（已有；SciencePlots 已重绘）

完整表见 `P1_figure_inventory.md`；路径相对 `drafts/` → `../figures/`。Fig. 4/5/7 缺口已关。投稿前可微调排版，不再缺 caption-only 主图。

建议阅读：§5.1 先 Fig.3，再 Table 1。

---

## 4. 审稿人可能打的点（英文 Discussion §6.2 已预答）

1. 「谁会选错输出？」——A 是 `withdrawal.f90` 自带公式；W5：文件/列名 confirmed 0/38。  
2. 「DeGray/Columbia 的 NSE 也是技能」——无独立观测；必须保持 internal consistency。  
3. 「5/4/1/5 证明减小时间步更不稳」——仅 Long Lake + INTER ON；OFF 全 0。  
4. 「关 TDGTA 等于删掉 TDG」——S 文件仍在且 mae=0。  
5. 「21.2% 超标=样本外验证」——模型未跑 2016+。  
6. 「SOD 在 Almeida 带内=已率定」——移植参数，禁止情景推断。  
7. 「全文只有 9/38」——unknown 已声明；表 2 口径混杂不依赖那 19 篇 unknown。  
8. 「这不是物理创新」——本文定位 GMD **Methods for assessment**；物理样本外是 P2。  
9. 「结论是套话 / 17 例验证了全框架 / 强制标准」——§6.2：报告建议；失败模式演示。

---

## 5. 投稿前还缺什么

| 项 | 状态 | 是否阻塞 GMD 投稿 |
|---|---|---|
| Zenodo 代码/数据 DOI | **未铸**；清单在 `06_PAPER/zenodo/` | **是** |
| 样本外 NSE（2016–2025） | 未做；`notes/P2_oos_roadmap.md` | 否（方法论稿可明写未做） |
| 图编号统一 + 缺图 | **已关闭**；SciencePlots 已重绘 | 否 |
| Chang/Neto 完整参考文献 | **已补全**；v2 另增 Bennett 2013 | 否 |
| 跨版本 v4.5.5 vs v5.0 指标漂移（T3） | 未做 | 否 |
| NHR 插桩写 DLTMIN 时长（T4） | 未做 | 否 |
| Columbia/DeGray 独立实测 | 没有 | 有则能把内部一致性做成 skill |
| `w2eval` 归档 | 五张卡已有；随 Zenodo | 建议 |
| 向官方仓库开 issue | 未做 | 加分项 |

---

## 6. 建议阅读顺序（约 40 分钟）

1. Abstract + Unresolved discrepancies（5 min）  
2. §2 taxonomy + Contribution 子弹（5 min）  
3. Table 1、Table 4、Table 5（10 min）  
4. §5.2.1 三句 + §5.4 降级段（10 min）  
5. Discussion §6.2 + Appendix 图清单（10 min）
