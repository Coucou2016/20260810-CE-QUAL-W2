# Zenodo archive preparation (not uploaded)

**Status:** packaging plan only. No deposit has been made. A real Zenodo DOI requires a user account and an explicit upload step outside this note.

**Purpose:** list what should enter a GMD-compatible reproducibility package for P1 (`P1_GMD_draft_v2.md`; v1 retained), what to omit because it is huge or redistributable elsewhere, and how to verify small files (`checksums.sha256`).

Paths below are relative to the project root `I:\Projects\20260810-CE-QUAL-W2` unless noted. The deposit tree should be a curated subset, not a dump of the whole disk.

---

## 1. Recommended include (core deposit)

| Role | What | Notes |
|---|---|---|
| Draft + review aids | `06_PAPER/drafts/*` | English draft, ZH outline, review checklist, figure inventory |
| Analysis JSON | `06_PAPER/analysis/*.json` | Metrics cited in tables; exclude `_w5_cache/` |
| Lit audit table | `06_PAPER/analysis/w5_lit_audit.csv` | Basis of Table 2 |
| Plot / emit scripts | `06_PAPER/analysis/*.py` (top level only) | `plot_p1_missing_figures.py`, `plot_nhr_scan.py`, `w1_w7_provenance.py`, etc. |
| Figures | `06_PAPER/figures/*.png` | All captioned figures (~2.7 MB total) |
| w2eval protocol | `06_PAPER/w2eval/` | `w2eval.py`, README, five run-cards (`.md` + `.json`) |
| Status / plan notes | `06_PAPER/notes/*.md`, `06_PAPER/PAPER_PLAN_20260815.md` | Provenance of claims; optional but useful |
| This package | `06_PAPER/zenodo/` | README, FILE_MANIFEST, checksums |
| DART CCIW (obs) | `06_PAPER/data/dart_cciw/*.csv` + `download_log.json` | ~11 MB; already downloaded; include files **or** script+checksums (see §3) |
| Input decks (small) | Official Bonneville / DeGray / Columbia / Long Lake **inputs** from `02_LIBRARY/06_examples/` (or a frozen copy under `05_REPRO_RUNS/*/…` without bulky SPR/SNP) | Needed to re-run; not full output trees |
| Runner stubs | Any `run_*.py` used for Bonneville ON/OFF if present under `05_REPRO_RUNS` | Document TDGTA ON/OFF and TMEND |

## 2. Model-output subset (not full repro trees)

Full `05_REPRO_RUNS` is **~2.6 GB**. A single Bonneville year is **~400 MB**, dominated by `BON_spr.csv` (~207 MB), `BON_snp.opt` (~67 MB), `Bonneville.w2l` (~42 MB), `BON_flx.opt` (~37 MB).

**Archive only these outputs per case (illustrative):**

- Bonneville ON/OFF: `TDGTarget_output.csv`, `TDG_output.csv`, `TDGTarget_warning.opt` (ON only), `BON_tsr_*_seg*.csv`, `t_wdo_76.csv` / `c_wdo_76.csv` / `q_wdo_76.csv` (or the WDO columns used for A), `flowbal.csv`, `w2.wrn`, `w2_con.csv`, `run_stdout.txt` / `run_stderr.txt`
- DeGray / Columbia internal pairs: TSR / WDO / gate files named in the VPR cards + `w2.wrn`
- Long Lake NHR scan: `w2.wrn` + `w2_con.csv` per DLTMAX point (not full SPR)

Omit from Zenodo: `*.spr`, dense SNP/FLX dumps, compiler intermediates, duplicate example trees already published by ERDC/PSU.

## 3. DART / large raw data policy

| Asset | Size (approx.) | Recommendation |
|---|---|---|
| `06_PAPER/data/dart_cciw/cciw_hourly_2011–2025.csv` | ~11 MB total | **Include** in deposit (fits Zenodo easily) |
| Full `01_RAW_DOWNLOADS` | ~656 MB | **Exclude**; cite upstream URLs |
| Full `02_LIBRARY` (manuals, source, all examples) | ~353 MB | **Exclude** bulk; ship only the few example decks used, or point to official CE-QUAL-W2 distribution |
| Full `05_REPRO_RUNS` | ~2.6 GB | **Exclude**; ship input + output **subset** (§2) |

If a future deposit omits the CCIW CSVs to save space: keep `download_log.json` (already has per-year `sha256`), document the DART URL pattern in W4 notes, and do **not** re-host USACE proprietary redistributions beyond fair academic use.

## 4. Explicitly out of scope for this prep step

- Minting a DOI / uploading via the Zenodo web UI or API  
- Packaging CE-QUAL-W2 **executables** (license / redistribution; cite ERDC/PSU and record the binary hash used in-house)  
- Re-running W2 or extending TMEND (see `06_PAPER/notes/P2_oos_roadmap.md`)

## 5. Suggested Zenodo metadata (draft)

- **Title:** Variable provenance, control-state outputs, and numerical health in CE-QUAL-W2 v4.5.5 evaluation (P1 reproduction package; v5.0 beta inventory)
- **License:** CC-BY-4.0 for text/figures/JSON; upstream model/data licenses unchanged
- **Related identifiers:** Almeida & Coelho (2025) Zenodo `10.5281/zenodo.15775127` (precedent, not this deposit)
- **Upload once:** after checklist items and OOS policy are decided; then paste DOI into § Data availability of the draft

## 6. Verification

After assembling the upload folder, regenerate or compare against:

```text
06_PAPER/zenodo/checksums.sha256
```

That file hashes **small** analysis/draft/figure/script/card assets only—not multi-hundred-MB SPR dumps.
