# HTML 硬性合规核验 — 2026-08-16

对 `06_PAPER/drafts/P1_paper.html` 与 `06_PAPER/report/report.html` 逐条核验用户硬要求。修补后已重新生成报告三件套。

**核验脚本：** `notes/_html_compliance_scan_20260816.py`、`notes/_html_structure_probe_20260816.py`  
**修补入口：** `analysis/build_research_report.py` + `analysis/report_fig_narratives.py`

---

## 总表

| # | 要求 | P1_paper.html | report.html | 曾不达标？ | 处置 |
|---|---|---|---|---|---|
| 1 | DOCTYPE/html/head/style/body；CSS 全内联 | PASS | PASS | 否 | — |
| 2 | 图全部 `data:...;base64`；无 `src="../"` / `./` / `http` | PASS（25/25） | PASS（25/25） | 否 | — |
| 3 | 原生 `<table>`；无外部数据依赖 | PASS（7 表） | PASS（8 表） | 否 | — |
| 4 | 无 ECharts/Plotly/D3/MathJax/Google Fonts/`https://` 资源 | PASS（无外链） | PASS（无外链；公式改为纯文本） | 报告曾用 `\(…\)` LaTeX 占位（无 CDN，但无渲染） | 已改为 Unicode/纯文本公式 |
| 5 | charset utf-8；中文字体栈 | PASS（Times + SimSun） | PASS（含微软雅黑等） | 否 | — |
| 6 | 图 `max-width:100%` | PASS | PASS | 否 | — |
| 7 | 报告十段结构（封面…展望） | N/A（英文学术稿） | PASS（目录含「封面」） | 封面仅有 `section.cover`、目录缺「封面」字样 | 目录已加「封面」锚点 |
| 8 | 每图五段解释（背景/怎么读/曲线/结论/通俗） | N/A（论文用 caption；非中文报告体） | PASS（25×5；标题对齐用户措辞） | 标题旧称「产生背景…/通俗解读」；多图过短 | 新建深度文案模块并重生 |
| 9 | 术语首次全称+深度解释（含 KTMAX、forrtl 等） | 英文稿内已有主要术语 | PASS（表 G 扩写；含 KTMAX、forrtl） | 报告缺 KTMAX、forrtl；解释偏短 | 已扩写术语表 |
| 10 | 「待补充」仅真实缺失 | PASS（作者/单位/Zenodo） | PASS（OOS NSE、独立观测、W5 全文、Zenodo 等） | 否 | 未编造 |

---

## 第 8 / 9 条细节（报告）

**修补前：** h4 为「产生背景与在全篇中的作用 / 如何阅读 / 曲线·分量 / 可得出的结论 / 通俗解读」；若干图总解释 <200 汉字；术语表无 KTMAX、forrtl。

**修补后：**
- 统一为：背景与作用 → 怎么读（坐标轴/曲线/散点/直方图/热图）→ 每条曲线（或分量）含义 → 能得出什么结论 → 通俗版结论
- 25 图深度文案来自 `report_fig_narratives.py`（数字锚定 JSON，不编造）
- 术语表含 NSE/KGE/α/β/PBIAS/R²/TDG/SOD/DLT*/H1/ZMIN/KT/KTMAX/TDGTA/SYSTDG/VPR/NHR/segment/layer/JDAY/forrtl

**论文 HTML：** 保持 GMD 英文学位稿结构（figcaption），不强制中文五段；合规项 1–6、10 PASS。

---

## 重生后体积（本轮）

| 文件 | 约大小 |
|---|---|
| `06_PAPER/report/report.html` | 8.32 MB（25 base64） |
| `06_PAPER/report/report.md` | 0.05 MB |
| `06_PAPER/report/report.pdf` | 8.27 MB（Chrome headless） |
| `06_PAPER/drafts/P1_paper.html` | 8.34 MB（本轮未改结构重生） |

---

## 结论

硬性结构与自包含性：**通过**。第 8、9 条曾不达标，已就地修补并重生报告 HTML/MD/PDF。论文 HTML 作为英文稿不套用中文报告五段模板（记为适用范围说明，非失败）。
