# 本轮可落地问题清单（2026-08-16）

执行者自拟；不上传。数字权威：`06_PAPER/analysis/*.json`。  
仓库根无 `.git`（见双代理报告）。未开 OOS 长跑。

## A. 本轮本地可改（不依赖 ChatGPT）

| ID | 问题 | 证据 | 动作 |
|---|---|---|---|
| L1 | `P1_outline_zh.md` References 仍写 Cole & Wells **2001**；英文稿已是 **2003**（EL-03-1） | outline §8 vs draft References | 改大纲为 2003 |
| L2 | 大纲写 Chang/Neto「占位」；英文稿 References 已补全 | outline §8 vs checklist §5 / draft | 删占位句，标已补全 |
| L3 | 笔记/STATUS 仍口算 89.6%、99.5%、~174→~39；英文稿已按 JSON | STATUS 五线结论；discrepancies 1–8 | **不改正文数字**；审计时以 JSON 为准；STATUS 本轮可轻标「口算 vs JSON」避免再混 |
| L4 | 关键数字抽查（Bonneville 三口径、W5、NHR 5/4/1/5、DART、泄流） | draft Tables vs JSON | 写 `P1_number_audit_20260816.md` |
| L5 | Abstract / Conclusions「not comparable」是否过强 | draft §Abstract, §6 | 等 ChatGPT Review 后由执行者独立裁定是否降级措辞 |

## B. 交给 ChatGPT 的审阅焦点（论证，非数字）

| ID | 焦点 | 为何本轮 |
|---|---|---|
| C1 | Abstract + Conclusions 是否过度宣称「跨研究不可比」 | GMD 审稿常打这里 |
| C2 | DeGray/Columbia 内部一致性是否被读者误读为 skill | 清单主张 1；预答已有，问是否够硬 |
| C3 | 用 Bonneville 控制器门控推广到「评估协议」是否外推过远 | Claim 2 仅一例控制器 |
| C4 | NHR 样本=1 水体液（Long Lake）时主张强度 | Claim 3 已降级，问 Abstract 是否仍过响 |
| C5 | W5 全文 9/38 + unknown 19 是否支撑「文献几乎不可重建 VPR」 | 方法局限是否够 |
| C6 | 图表是否支撑结论（Fig.4 rug 无 NSE；Fig.6 非普遍 CFL） | 对齐 inventory |
| C7 | References 缺口（GMD 惯例：数据/软件 DOI、更多 W2 评估先例） | Zenodo 未铸已自知 |

## C. 明确不做（本轮）

- Bonneville / 任意案例 OOS 扩时段重跑  
- Zenodo 上传 / DOI  
- git commit / push / PR  
- 向 ChatGPT 上传附件或整篇 6700 词一次粘贴  

## D. 优先级

1. 写 brief + 分条 CONTEXT → ChatGPT Review  
2. L1–L4 本地硬伤与数字审计  
3. 核验 ChatGPT 建议 → 仅采纳经 JSON/硬约束核验者 → 最小改 `P1_GMD_draft_v1.md`（及必要时 outline/checklist/STATUS）  
4. `DUAL_AGENT_REPORT_20260816.md`

## E. 第二轮剩余项（2026-08-16 续；已本地落地）

| ID | 项 | 状态 |
|---|---|---|
| R1 | 残余绝对措辞软化 | 已改草稿 |
| R2 | Discussion 防御段加长 | 已改 §5.2 |
| R3 | NHR 计数 + W5 present/absent 方法句 | 已改 §3.3/§3.6 |
| R4 | Fig.3/5/S1 caption | 已改 |
| R5 | 中英 + w2eval README | 已改 |
| R6 | STATUS 口算标注 | 已改 |
| — | 整段换 Abstract；OOS；Zenodo；改 JSON | **否决** |
