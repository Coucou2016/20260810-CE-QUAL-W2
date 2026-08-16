# GitHub public contents — what is included and excluded

**Repo purpose:** Structured code, paper drafts, notes, figures, and analysis JSON for the CE-QUAL-W2 assessment / GMD Methods manuscript. **Not** a full model-run archive.

**Local root:** `I:\Projects\20260810-CE-QUAL-W2`  
**Suggested remote name:** `CE-QUAL-W2-assessment-paper`  
**Date:** 2026-08-16

---

## Included (public)

| Path | Why |
|---|---|
| `README.md` | Paper / report / script entry points |
| `.gitignore` | Keeps large / secret / regenerable artifacts out |
| `00_INDEX/*.py`, `00_INDEX/README_NAMING.md`, `00_INDEX/manifest.csv`, `00_INDEX/naming_schema.json`, `00_INDEX/literature_wishlist.md` | Indexing & repro scripts (no model binaries) |
| `05_REPRO_RUNS/README.md` only | Points to local run directories; **no** `run_*` outputs |
| `06_PAPER/drafts/*.md` | GMD draft v1/v2, outlines, claim–evidence matrix, frameworks |
| `06_PAPER/notes/**` | STATUS, dual-agent, pre-sub, audits (markdown) |
| `06_PAPER/analysis/*.py`, `*.json`, `*.csv`, `*.md` | Metrics + build/plot scripts (**no** `_w5_cache/`, no `__pycache__`) |
| `06_PAPER/figures/*.png` | Paper/report figures (SciencePlots) |
| `06_PAPER/w2eval/**` | Minimal evaluator + run-cards |
| `06_PAPER/zenodo/**` | Manifest / checksums / archive README (DOI **not** minted) |
| `06_PAPER/report/report.md` | Research report source |
| `06_PAPER/GITHUB_CONTENTS.md` | This file |
| Root `report.md` | Thin pointer / legacy summary (optional; md only) |

---

## Excluded (local only)

| Path | Why |
|---|---|
| `01_RAW_DOWNLOADS/` | Large zips / original downloads |
| `02_LIBRARY/` | Manuals, executables, example I/O |
| `03_MERGED_PDF/`, `04_MARKDOWN/` | Bulk literature conversion |
| `05_REPRO_RUNS/run_*`, `diag_*` | Multi-GB model outputs / CSVs |
| `06_PAPER/data/dart_cciw/` | Hourly observation cache (~11 MB+); fetch via `00_INDEX/download_dart_cciw.py` |
| `06_PAPER/analysis/_w5_cache/` | Literature PDF / API cache |
| Root `report.html`, `report.pdf` | >10 MB self-contained builds |
| `06_PAPER/report/report.html`, `report.pdf` | Regenerable; prefer md + scripts |
| `06_PAPER/drafts/P1_paper.html` | ~8 MB base64 figures; regenerate with `06_PAPER/analysis/build_paper_html.py` |
| `.env`, secrets, `agent-transcripts/`, `.cursor/` | Secrets / local IDE chatter |

---

## How to regenerate large HTML/PDF locally

```text
# Research report (writes 06_PAPER/report/report.html; PDF if tooling present)
python 06_PAPER/analysis/build_research_report.py

# Paper HTML from draft + figures
python 06_PAPER/analysis/build_paper_html.py
```

Root `report.html` / `report.pdf` may still be produced by older `00_INDEX/build_repro_report.py` workflows when full `05_REPRO_RUNS` exist locally.

---

## Hard non-goals for this public repo

- No deployment / production changes  
- No secrets / tokens  
- No ZIP upload to ChatGPT web UI  
- No claim that Zenodo DOI is minted until user deposits
