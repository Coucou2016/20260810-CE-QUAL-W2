# GitHub upload plan (NOT executed) — 2026-08-16

**Status:** 本轮**不创建、不推送**任何 GitHub 仓库。可见性由用户决定。  
**Git:** 仓库根 `I:\Projects\20260810-CE-QUAL-W2` **无 `.git`**。  
**gh:** `gh` 命令在本机 PATH 中**不可用**（`CommandNotFoundException`）；未认证状态无法查询。

---

## Include (structured code + docs)

| Path | Approx. | Notes |
|---|---|---|
| `README.md` | small | Root conventions |
| `00_INDEX/*.py` (+ naming README) | ~0.4 MB | Repro / index scripts |
| `06_PAPER/analysis/` | ~6.1 MB | JSON + build/plot scripts（含报告/论文 HTML 生成器） |
| `06_PAPER/w2eval/` | ~0.1 MB | run-card MVP |
| `06_PAPER/drafts/` | ~9 MB | 含 `P1_paper.html` base64（可改只交 md + figures） |
| `06_PAPER/notes/` | ~0.2 MB | 双代理/审计笔记 |
| `06_PAPER/zenodo/` | ~0.02 MB | Manifest / checksums（DOI 未铸） |
| `06_PAPER/figures/` | ~6.5 MB | SciencePlots png dpi≥300 |
| `06_PAPER/report/report.md` | ~0.05 MB | 建议交 md；巨型 html/pdf 可选 |

**Include subtotal (as measured):** ~22 MB（若排除 `P1_paper.html` / `report.html` / `report.pdf` 的 base64，可降至约 **7–8 MB** 代码+图+笔记）。

---

## Exclude

| Path | Approx. | Reason |
|---|---|---|
| `06_PAPER/data/dart_cciw/` | ~11 MB | 大数据；改在 Zenodo/README 指向获取方式 |
| `05_REPRO_RUNS/` | ~2.7 GB | 模型输出与分析大文件 |
| `01_RAW_DOWNLOADS/`, `02_LIBRARY/`, `03_MERGED_PDF/`, `04_MARKDOWN/` | large | 资料库原件，非投稿代码包 |
| `report.html` / `report.pdf` at repo root (if duplicated) | large | 可选；权威在 `06_PAPER/report/` |

---

## Suggested `.gitignore` draft

```gitignore
# large local runs / data
05_REPRO_RUNS/
01_RAW_DOWNLOADS/
02_LIBRARY/
03_MERGED_PDF/
04_MARKDOWN/
06_PAPER/data/dart_cciw/

# optional regenerated megabyte HTML/PDF (keep md + figures)
06_PAPER/report/report.html
06_PAPER/report/report.pdf
06_PAPER/drafts/P1_paper.html

# python
__pycache__/
*.pyc
.ipynb_checkpoints/

# OS / editor
Thumbs.db
Desktop.ini
.DS_Store
```

---

## Recommended first public layout options

1. **Code+docs repo (public or private):** `00_INDEX` + `06_PAPER/{analysis,w2eval,drafts/*.md,notes,zenodo,figures}` ≈ 7–8 MB.  
2. **Zenodo archive:** full reproducibility bundle + DOI for GMD §8（用户上传）。  
3. **Do not** push until visibility (public/private) is chosen by the user.
