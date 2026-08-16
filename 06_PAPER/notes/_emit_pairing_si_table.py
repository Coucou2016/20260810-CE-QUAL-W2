"""Emit Appendix B markdown table from pairing_tolerance_scan.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "analysis" / "pairing_tolerance_scan.json"
d = json.loads(src.read_text(encoding="utf-8"))
lines = [
    "| Caliber | Tolerance (d) | *n* | *R*² | NSE | Baseline | Status |",
    "|---|---:|---:|---:|---:|:---:|---|",
]
for cal in ("A", "C", "B", "S"):
    for r in d["calibers"][cal]["rows"]:
        bl = "yes" if r.get("is_baseline") else ""
        lines.append(
            f"| {cal} | {r['tol_d']:.2f} | {r['n']} | {r['r2']:.4f} | "
            f"{r['nse']:+.4f} | {bl} | {r['status']} |"
        )
print("\n".join(lines))
