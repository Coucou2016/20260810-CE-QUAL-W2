from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
SRC_BASE = ROOT / "02_LIBRARY" / "06_examples" / "v4.5.5"
RUN_BASE = ROOT / "05_REPRO_RUNS" / "run_20260811_seq"
OUT_DIR = RUN_BASE / "analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class CaseConfig:
    name: str
    rel_file: str
    parser: str  # "opt" or "csv"
    x_index: int
    y_index: int
    ref_mode: str  # "source" or "run_ref"
    note: str


CASES = [
    CaseConfig(
        name="Long Lake",
        rel_file="tsr_8_seg36.csv",
        parser="csv",
        x_index=0,
        y_index=3,
        ref_mode="run_ref",
        note="Model output timeseries reproducibility between two independent runs (tsr_8_seg36.csv).",
    ),
    CaseConfig(
        name="DeGray Reservoir with sediment diagenesis and vertical algae migration",
        rel_file="tsr_1_seg31.csv",
        parser="csv",
        x_index=0,
        y_index=3,
        ref_mode="run_ref",
        note="Model output timeseries reproducibility between two independent runs (tsr_1_seg31.csv).",
    ),
    CaseConfig(
        name="Columbia Slough Estuary",
        rel_file="tdh_br1.csv",
        parser="csv",
        x_index=0,
        y_index=1,
        ref_mode="source",
        note="No clear runtime timeseries output configured; use boundary/reference curve reproducibility proxy.",
    ),
]


def load_opt_numeric(path: Path) -> np.ndarray:
    rows = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = raw.strip()
        if not s:
            continue
        u = s.upper()
        if u.startswith("TITLE") or u.startswith("VARIABLES") or u.startswith("ZONE"):
            continue
        parts = s.replace(",", " ").split()
        vals = []
        ok = True
        for p in parts:
            try:
                vals.append(float(p))
            except ValueError:
                ok = False
                break
        if ok and vals:
            rows.append(vals)
    if not rows:
        raise RuntimeError(f"No numeric rows parsed from {path}")
    # ensure rectangular
    width = min(len(r) for r in rows)
    arr = np.array([r[:width] for r in rows], dtype=float)
    return arr


def load_csv_numeric(path: Path) -> np.ndarray:
    # Skip comment lines starting with '$'
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.lstrip().startswith("$"):
            continue
        if raw.strip():
            lines.append(raw)
    if not lines:
        raise RuntimeError(f"No non-comment lines in {path}")
    # pandas robust parsing
    from io import StringIO

    df = pd.read_csv(StringIO("\n".join(lines)))
    # keep numeric-only columns
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if df.empty:
        raise RuntimeError(f"No numeric data after parse: {path}")
    return df.to_numpy(dtype=float)


def metrics(obs: np.ndarray, sim: np.ndarray) -> Tuple[float, float, float]:
    diff = sim - obs
    mae = float(np.mean(np.abs(diff)))
    rmse = float(np.sqrt(np.mean(diff**2)))
    span = float(np.max(obs) - np.min(obs))
    nrmse = float(rmse / span) if span > 0 else 0.0
    return mae, rmse, nrmse


def main() -> None:
    ref_run_base = ROOT / "05_REPRO_RUNS" / "run_20260811"
    rows = []
    for cfg in CASES:
        src_file = (
            (SRC_BASE / cfg.name / cfg.rel_file)
            if cfg.ref_mode == "source"
            else (ref_run_base / cfg.name / cfg.rel_file)
        )
        run_file = RUN_BASE / cfg.name / cfg.rel_file
        if not src_file.exists() or not run_file.exists():
            rows.append(
                {
                    "case": cfg.name,
                    "status": "missing_file",
                    "source_file": str(src_file),
                    "run_file": str(run_file),
                    "mae": None,
                    "rmse": None,
                    "nrmse": None,
                    "points": 0,
                    "note": cfg.note,
                }
            )
            continue

        if cfg.parser == "opt":
            src = load_opt_numeric(src_file)
            run = load_opt_numeric(run_file)
        else:
            src = load_csv_numeric(src_file)
            run = load_csv_numeric(run_file)

        n = min(len(src), len(run))
        src = src[:n]
        run = run[:n]

        x_src = src[:, cfg.x_index]
        y_src = src[:, cfg.y_index]
        x_run = run[:, cfg.x_index]
        y_run = run[:, cfg.y_index]

        # filter fill/missing flags
        mask = np.isfinite(y_src) & np.isfinite(y_run) & (y_src > -98.0) & (y_run > -98.0)
        x_src = x_src[mask]
        y_src = y_src[mask]
        x_run = x_run[mask]
        y_run = y_run[mask]

        if len(y_src) == 0:
            rows.append(
                {
                    "case": cfg.name,
                    "status": "no_valid_points",
                    "source_file": str(src_file),
                    "run_file": str(run_file),
                    "mae": None,
                    "rmse": None,
                    "nrmse": None,
                    "points": 0,
                    "note": cfg.note,
                }
            )
            continue

        mae, rmse, nrmse = metrics(y_src, y_run)

        # plot
        plt.figure(figsize=(10, 4))
        plt.plot(x_src, y_src, label="Reference", linewidth=1.8)
        plt.plot(x_run, y_run, "--", label="Reproduced", linewidth=1.4)
        plt.title(cfg.name)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.tight_layout()
        plot_name = cfg.name.replace(" ", "_").replace("/", "_") + ".png"
        plot_path = OUT_DIR / plot_name
        plt.savefig(plot_path, dpi=150)
        plt.close()

        rows.append(
            {
                "case": cfg.name,
                "status": "ok",
                "source_file": str(src_file),
                "run_file": str(run_file),
                "mae": mae,
                "rmse": rmse,
                "nrmse": nrmse,
                "points": int(len(y_src)),
                "plot": str(plot_path),
                "note": cfg.note,
            }
        )

    df = pd.DataFrame(rows)
    out_csv = OUT_DIR / "metrics_summary.csv"
    out_json = OUT_DIR / "metrics_summary.json"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"WROTE {out_csv}")
    print(f"WROTE {out_json}")


if __name__ == "__main__":
    main()
