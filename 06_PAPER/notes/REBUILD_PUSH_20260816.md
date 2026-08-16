# Rebuild + push — 2026-08-16

## Why
Public repo already had ChatGPT-落地 draft softens (~`efd1737` / `7d9811b`). Deep report triad risked lagging those fixes (esp. Table 2 **1/7/4**, **VPR-core**, hard boundaries).

## Actions
1. Re-ran `06_PAPER/analysis/build_paper_html.py` → `06_PAPER/drafts/P1_paper.html` (local; gitignored).
2. Aligned `build_research_report.py` + `report_fig_narratives_{extra,autodepth}.py` with draft Table 2 **1/7/4** and **VPR-core** wording; re-ran `build_research_report.py`.
3. Outputs: `06_PAPER/report/report.{html,md,pdf}`; self-check Base64×25, no CDN/http/rel/`file:` images; PDF via Chrome OK.
4. Per `.gitignore`, **html/pdf not pushed**; tracked: `report.md`, build/narrative scripts, STATUS + this note.
5. Dual-agent GitHub notes: see merge note in `DUAL_AGENT_GITHUB_20260816.md` §8 / `DUAL_AGENT_GITHUB_REVIEW_20260816.md` header — no duplicate checklist labor.

## Build summary (local)
- Paper HTML: success (~8.75 MB, 25 images)
- Report: HTML 8,786,851 B; MD 117,367 B; PDF 9,917,580 B; `pdf_ok=True`
- Includes html in git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>"? **No** (ignored by design)
