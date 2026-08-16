# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\notes\STATUS_20260815.md")
text = p.read_text(encoding="utf-8", errors="replace")

idx = text.find("## 报告图 SciencePlots 重绘")
if idx < 0:
    raise SystemExit("report section missing")

needle = "未 git commit。未重跑 W2。\n"
good_end = text.find(needle, idx)
if good_end < 0:
    raise SystemExit("closing line missing")
good_end = good_end + len(needle)
base = text[:good_end]

append = """
---

## 三线合成 → 正文 v2（2026-08-16）

| 项 | 结果 |
|---|---|
| 输入 | nature-skills 纪律 + SciencePlots 图 + ChatGPT 文献框架（GMD Methods） |
| 蓝图 | `drafts/P1_MERGED_BLUEPRINT.md` |
| 英文稿 | `drafts/P1_GMD_draft_v2.md`（**v1 保留**） |
| 中文大纲 | `drafts/P1_outline_zh_v2.md` |
| 清单 | `drafts/P1_review_checklist.md` 已改指 v2 |
| 验收 | `notes/MERGE_BLUEPRINT_V2_20260816.md` |
| 结构变化 | 新增 §2 证据分类；§3 方法+§4 演示语料；结果 §5.1–5.5 按发现分节；文体 **Methods for assessment of models**；图号不变 |
| ChatGPT follow-up | 打开文献对话 URL 后输入框为 disabled/未载入会话正文 → **跳过**粘贴确认 |
| 禁止项 | 未 commit；未开 OOS；未编造数字 |

仍需用户：Zenodo 铸 DOI；可选自行在文献对话确认蓝图仍适合 GMD Methods。
"""

p.write_text(base + append, encoding="utf-8")
print("STATUS ok", len(base + append))
