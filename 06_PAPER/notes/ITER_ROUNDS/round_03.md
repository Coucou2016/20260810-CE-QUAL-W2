# Round 03/5 — Figure maturity (Theme B)

**Date:** 2026-08-16  
**ChatGPT:** https://chatgpt.com/c/6a819d49-3cd8-83ea-b3c8-289ba7dcf436 (ROUND 3/5 in Theme B chat)  
**Repo base:** `c036526`

## Advisor (verified)

- Prefer **2+1 strip** Fig.4: (a) skill, (b) internal, (c) literature R² strip without NSE.
- Caption: panels (a)/(b) different evaluation objects; (c) NSE not inferred.
- Fig.6: xlabel “DLTMAX schedule knot”; caption binds knot ≠ realized Δt (window max 231.096 s at 20 s knot).
- Fig.4 Bonneville points from `w3` JSON not cards.
- Fig.5 keep; SciencePlots already OK.

## Landed

- `plot_p1_missing_figures.py`: 2+1 Fig.4 from W3 JSON; regenerated PNG
- `plot_nhr_scan.py`: schedule-knot labels + window-max annotations; regenerated NHR PNGs
- Draft Fig.4 / Fig.6 captions updated

## Audit

PASS 40/40 (after regen)

## Git

(filled after push)
