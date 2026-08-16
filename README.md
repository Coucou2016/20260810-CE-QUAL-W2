# CE-QUAL-W2 assessment paper (public code + drafts)

**Public repository:** https://github.com/Coucou2016/20260810-CE-QUAL-W2

Working materials for a **Geoscientific Model Development** *Methods for assessment of models* manuscript on CE-QUAL-W2 evaluation practice: **variable provenance (VPR)**, **control-state outputs**, **numerical health (NHR)**, and **run-cards** (`w2eval`).

This public repository contains **structured scripts, Markdown drafts, analysis JSON, figures, and notes**. It does **not** ship multi-GB model runs, the CE-QUAL-W2 executable, or hourly observation caches. See [`06_PAPER/GITHUB_CONTENTS.md`](06_PAPER/GITHUB_CONTENTS.md).

## Start here

| What | Path |
|---|---|
| English GMD draft (current) | [`06_PAPER/drafts/P1_GMD_draft_v2.md`](06_PAPER/drafts/P1_GMD_draft_v2.md) |
| Claim–evidence matrix | [`06_PAPER/drafts/P1_claim_evidence_matrix.md`](06_PAPER/drafts/P1_claim_evidence_matrix.md) |
| Research report (Markdown) | [`06_PAPER/report/report.md`](06_PAPER/report/report.md) |
| Status / dual-agent notes | [`06_PAPER/notes/`](06_PAPER/notes/) |
| Metrics JSON + plot/build scripts | [`06_PAPER/analysis/`](06_PAPER/analysis/) |
| Figures (PNG) | [`06_PAPER/figures/`](06_PAPER/figures/) |
| Run-card MVP | [`06_PAPER/w2eval/`](06_PAPER/w2eval/) |
| Zenodo prep (DOI not minted) | [`06_PAPER/zenodo/`](06_PAPER/zenodo/) |
| Index / repro helper scripts | [`00_INDEX/`](00_INDEX/) |
| Local run-directory map (no outputs here) | [`05_REPRO_RUNS/README.md`](05_REPRO_RUNS/README.md) |

## Regenerate HTML (optional)

Large self-contained HTML/PDF are **gitignored**. From a full local workspace (with figures present):

```bash
python 06_PAPER/analysis/build_research_report.py
python 06_PAPER/analysis/build_paper_html.py
```

## Scope reminders (do not overclaim)

- DeGray temperature and Columbia DO comparisons in the draft are **internal consistency**, not skill versus field observations.
- Out-of-sample NSE for 2016–2025 was **not** computed (model ends near 2011).
- Zenodo DOI is **not** minted in this repo; see `06_PAPER/zenodo/`.

## License / citation

Working drafts — not a camera-ready submission. Cite analysis JSON paths when quoting headline numbers. Official CE-QUAL-W2 binaries and examples remain under their upstream licenses (not redistributed here).
