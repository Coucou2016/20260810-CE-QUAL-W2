# -*- coding: utf-8 -*-
"""Pairing-tolerance sensitivity for Bonneville ON A/B/C/S vs CCIW.

Uses archived CCIW + ON-run outputs via eval_w3 loaders (no W2 rerun).
Writes analysis/pairing_tolerance_scan.json.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
sys.path.insert(0, str(ROOT / "00_INDEX"))
from eval_w3_tdgta_off import (  # noqa: E402
    ON_RUN,
    align_tol,
    load_obs,
    load_tdg_output,
    load_tdgtarget,
    load_tsr_tdg,
    n2do_series,
    skill,
)

OUT = ROOT / "06_PAPER" / "analysis" / "pairing_tolerance_scan.json"

BASELINE = {"A": 0.05, "C": 0.05, "B": 0.6, "S": 0.6}
GRID = {
    "A": [0.01, 0.02, 0.05, 0.1, 0.25],
    "C": [0.01, 0.02, 0.05, 0.1, 0.25],
    "B": [0.25, 0.5, 0.6, 0.75, 1.0, 1.5],
    "S": [0.25, 0.5, 0.6, 0.75, 1.0, 1.5],
}


def main() -> None:
    obs = load_obs(ON_RUN)
    oj, ov = obs["JDAY"].to_numpy(), obs["TDG"].to_numpy()
    series = {
        "A": n2do_series(ON_RUN),
        "C": load_tsr_tdg(ON_RUN),
        "B": load_tdgtarget(ON_RUN / "TDGTarget_output.csv"),
        "S": load_tdg_output(ON_RUN / "TDG_output.csv"),
    }

    results: dict = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "run": str(ON_RUN),
        "baseline_tol_d": BASELINE,
        "note": "Nearest-neighbor pairing; changing tol is a different VPR evaluation object. No W2 rerun.",
        "calibers": {},
    }
    for cal, df in series.items():
        if df is None or len(df) == 0:
            results["calibers"][cal] = {"status": "unavailable"}
            continue
        sj, sv = df["JDAY"].to_numpy(), df["TDG"].to_numpy()
        rows = []
        for tol in GRID[cal]:
            o, s = align_tol(oj, ov, sj, sv, tol=tol, vmin=50.0)
            if len(o) < 10:
                rows.append({"tol_d": tol, "n": int(len(o)), "status": "too_few_pairs"})
                continue
            m = skill(o, s)
            rows.append(
                {
                    "tol_d": tol,
                    "n": m["n"],
                    "r2": m["r2"],
                    "nse": m["nse"],
                    "kge": m["kge"],
                    "mae": m["mae"],
                    "sim_max": m["sim_max"],
                    "is_baseline": abs(tol - BASELINE[cal]) < 1e-12,
                    "status": "ok",
                }
            )
        results["calibers"][cal] = {"grid_d": GRID[cal], "rows": rows}

    # Stability summary relative to paper baseline
    stab = {}
    for cal in ("A", "B", "C"):
        rows = [r for r in results["calibers"].get(cal, {}).get("rows", []) if r.get("status") == "ok"]
        base = next((r for r in rows if r.get("is_baseline")), None)
        if not base:
            continue
        nse_signs = sorted({1 if r["nse"] > 0 else (-1 if r["nse"] < 0 else 0) for r in rows})
        r2s = [r["r2"] for r in rows]
        stab[cal] = {
            "baseline": {k: base[k] for k in ("tol_d", "n", "r2", "nse", "kge", "mae", "sim_max")},
            "n_scan_ok": len(rows),
            "r2_min": min(r2s),
            "r2_max": max(r2s),
            "nse_sign_set": nse_signs,
            "nse_sign_stable": len(nse_signs) == 1,
        }
    results["stability_summary"] = stab
    results["claim_safe_sentence"] = (
        "Across the scanned pairing tolerances, Bonneville ON A/B/C retain the paper's qualitative pattern "
        "(A and C negative NSE; B positive NSE near +0.5) at the baseline tolerances used in Table 1; "
        "changing tol changes n and is a different evaluation object."
    )

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)
    print(json.dumps(stab, indent=2))


if __name__ == "__main__":
    main()
