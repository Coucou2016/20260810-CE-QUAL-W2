#!/usr/bin/env python3
"""W1 variable-provenance metrics (DeGray T, Columbia DO) and W7 Columbia SOD vs Almeida.

Internal consistency only: DeGray and Columbia official examples have no field
observations. Metrics compare two model output channels of the same named
physical quantity. This is provenance ambiguity, not skill vs observations.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
DEGRAY = (
    ROOT
    / "05_REPRO_RUNS"
    / "run_20260811_fixed"
    / "DeGray Reservoir with sediment diagenesis and vertical algae migration"
)
COL_ON = ROOT / "05_REPRO_RUNS" / "run_20260814_columbia_diag" / "Columbia Slough Estuary"
COL_OFF = ROOT / "05_REPRO_RUNS" / "run_20260811_fixed" / "Columbia Slough Estuary"
OUT_A = ROOT / "06_PAPER" / "analysis"
OUT_F = ROOT / "06_PAPER" / "figures"
MISSING = -90.0

# Almeida & Coelho 2025 GMD 18:6135–6161. Zero-order / Hybrid SOD scan.
ALMEIDA_SOD_SCAN = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
ALMEIDA_BAND = (0.5, 3.0)
ALMEIDA_SD_BEST_MEAN = 1.07
ALMEIDA_HYBRID_MEAN = 1.49
ALMEIDA_ZERO_MEAN = 1.43

# Previously verified Bonneville vs CCIW (PAPER_PLAN_20260815). Not recomputed.
BONNEVILLE_REF = [
    {
        "id": "BON_A_c_wdo76_N2DO_henry",
        "r2": 0.508,
        "nse": -2.804,
        "kge": 0.409,
        "r": 0.713,
        "alpha": 1.513,
        "beta": 0.941,
        "pbias": -5.89,
        "mae": 6.88,
        "n": 1614,
        "note": "reused from PAPER_PLAN; not recomputed in W1",
    },
    {
        "id": "BON_B_SYSTDG_TDG_TDG",
        "r2": 0.533,
        "nse": 0.500,
        "kge": 0.715,
        "r": 0.730,
        "alpha": 0.909,
        "beta": 0.999,
        "pbias": -0.14,
        "mae": 2.20,
        "n": 1614,
        "note": "reused from PAPER_PLAN; not recomputed in W1",
    },
    {
        "id": "BON_C_TSR_seg40_TDG",
        "r2": 0.551,
        "nse": -2.752,
        "kge": 0.385,
        "r": 0.742,
        "alpha": 1.555,
        "beta": 0.941,
        "pbias": -5.86,
        "mae": 6.84,
        "n": 1614,
        "note": "reused from PAPER_PLAN; not recomputed in W1",
    },
]


def _r4(x):
    if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))):
        return None
    return round(float(x), 4)


def metrics(obs, sim) -> dict:
    obs = np.asarray(obs, float)
    sim = np.asarray(sim, float)
    m = np.isfinite(obs) & np.isfinite(sim)
    obs, sim = obs[m], sim[m]
    n = int(len(obs))
    if n < 3:
        return {"n": n}
    d = sim - obs
    mae = float(np.mean(np.abs(d)))
    rmse = float(np.sqrt(np.mean(d**2)))
    span = float(np.max(obs) - np.min(obs))
    nrmse = float(rmse / span) if span > 0 else float("nan")
    den = float(np.sum((obs - np.mean(obs)) ** 2))
    nse = float(1.0 - np.sum(d**2) / den) if den > 0 else float("nan")
    mu_o = float(np.mean(obs))
    mu_s = float(np.mean(sim))
    sd_o = float(np.std(obs, ddof=0))
    sd_s = float(np.std(sim, ddof=0))
    if sd_o > 0 and sd_s > 0:
        r = float(np.corrcoef(obs, sim)[0, 1])
    else:
        r = float("nan")
    r2 = float(r * r) if np.isfinite(r) else float("nan")
    alpha = float(sd_s / sd_o) if sd_o > 0 else float("nan")
    beta = float(mu_s / mu_o) if mu_o != 0 else float("nan")
    if np.isfinite(r) and np.isfinite(alpha) and np.isfinite(beta):
        kge = float(1.0 - np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2))
    else:
        kge = float("nan")
    pbias = float(100.0 * np.sum(d) / np.sum(obs)) if np.sum(obs) != 0 else float("nan")
    if sd_o > 0:
        slope, intercept = np.polyfit(obs, sim, 1)
    else:
        slope, intercept = float("nan"), float("nan")
    return {
        "n": n,
        "r2": _r4(r2),
        "nse": _r4(nse),
        "kge": _r4(kge),
        "r": _r4(r),
        "alpha": _r4(alpha),
        "beta": _r4(beta),
        "pbias": _r4(pbias),
        "mae": _r4(mae),
        "rmse": _r4(rmse),
        "nrmse": _r4(nrmse),
        "slope": _r4(float(slope)),
        "intercept": _r4(float(intercept)),
        "mu_ref": _r4(mu_o),
        "mu_alt": _r4(mu_s),
        "sigma_ref": _r4(sd_o),
        "sigma_alt": _r4(sd_s),
    }


def align(oj, ov, sj, sv, tol=0.05):
    """Nearest-neighbor pairing driven by the shorter series so sparse dumps are not reused."""
    oj = np.asarray(oj, float)
    ov = np.asarray(ov, float)
    sj = np.asarray(sj, float)
    sv = np.asarray(sv, float)
    mo = np.isfinite(oj) & np.isfinite(ov) & (ov > MISSING)
    ms = np.isfinite(sj) & np.isfinite(sv) & (sv > MISSING)
    oj, ov, sj, sv = oj[mo], ov[mo], sj[ms], sv[ms]
    if len(oj) == 0 or len(sj) == 0:
        return np.array([]), np.array([]), np.array([])
    if len(oj) <= len(sj):
        clock_j, clock_o, other_j, other_v = oj, ov, sj, sv
        clock_is_obs = True
    else:
        clock_j, clock_o, other_j, other_v = sj, sv, oj, ov
        clock_is_obs = False
    order = np.argsort(clock_j)
    used = np.zeros(len(other_j), dtype=bool)
    jj, oo, ss = [], [], []
    for i in order:
        j, v = clock_j[i], clock_o[i]
        d = np.abs(other_j - j)
        d[used] = np.inf
        k = int(np.argmin(d))
        if d[k] <= tol:
            used[k] = True
            if clock_is_obs:
                jj.append(float(j))
                oo.append(float(v))
                ss.append(float(other_v[k]))
            else:
                jj.append(float(other_j[k]))
                oo.append(float(other_v[k]))
                ss.append(float(v))
    return np.array(jj), np.array(oo), np.array(ss)


def load_csv_skip(path: Path, usecols: list[int] | None = None) -> pd.DataFrame:
    names = None
    skip = 0
    for i, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        s = raw.strip()
        if not s or s.startswith("$"):
            continue
        if s.upper().startswith("JDAY"):
            names = [c.strip() for c in s.split(",") if c.strip()]
            skip = i + 1
            break
    if not names:
        raise RuntimeError(f"No JDAY header in {path}")
    n = len(usecols) if usecols is not None else len(names)
    df = pd.read_csv(
        path,
        skiprows=skip,
        header=None,
        usecols=list(range(n)),
        names=names[:n],
        engine="python",
    )
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["JDAY"])


def load_tsr(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df["JDAY"] = pd.to_numeric(df["JDAY"], errors="coerce")
    return df.dropna(subset=["JDAY"])


def pick(df: pd.DataFrame, name: str) -> str:
    cols = {c.lower(): c for c in df.columns}
    if name.lower() in cols:
        return cols[name.lower()]
    for k, orig in cols.items():
        if name.lower() == k.lower() or name.lower() in k.lower():
            return orig
    raise KeyError(f"{name} not in {list(df.columns)[:12]}")


def daily_mean(jday, val) -> tuple[np.ndarray, np.ndarray]:
    df = pd.DataFrame({"j": np.asarray(jday, float), "v": np.asarray(val, float)}).dropna()
    df["day"] = np.floor(df["j"]) + 0.5
    g = df.groupby("day", as_index=False)["v"].mean()
    return g["day"].to_numpy(), g["v"].to_numpy()


def parse_prf_temperature(path: Path) -> dict[int, pd.DataFrame]:
    """PRF vertical TEMP at IPR segments 10, 18, 26. Surface = layer 0, bottom = last."""
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    segs = [10, 18, 26]
    nlay_to_seg = {8: 10, 13: 18, 23: 26}
    dumps: dict[int, list[tuple[float, np.ndarray]]] = {s: [] for s in segs}
    current_jday = 64.5
    i = 0
    date_re = re.compile(r"^\s*(\d+\.\d+)\s+[A-Z][a-z]{2}\s")
    while i < len(lines):
        m = date_re.match(lines[i])
        if m:
            current_jday = float(m.group(1))
        parts = lines[i].split()
        if parts and parts[0].upper() == "TEMP" and len(parts) >= 2:
            try:
                nlay = int(float(parts[1]))
            except ValueError:
                i += 1
                continue
            vals: list[float] = []
            j = i + 1
            while j < len(lines) and len(vals) < nlay:
                for p in lines[j].split():
                    try:
                        vals.append(float(p))
                    except ValueError:
                        continue
                    if len(vals) >= nlay:
                        break
                j += 1
            seg = nlay_to_seg.get(nlay)
            if seg is not None and len(vals) >= nlay:
                dumps[seg].append((current_jday, np.array(vals[:nlay], float)))
            i = j
            continue
        i += 1
    out = {}
    for seg, rows in dumps.items():
        if not rows:
            continue
        jdays = np.array([r[0] for r in rows], float)
        sfc = np.array([r[1][0] for r in rows], float)
        bot = np.array([r[1][-1] for r in rows], float)
        out[seg] = pd.DataFrame({"JDAY": jdays, "T_sfc": sfc, "T_bot": bot, "nlay": [len(r[1]) for r in rows]})
    return out


def _header_fields(header: str) -> list[tuple[int, int, int]]:
    idx = header.upper().find("DEPTH")
    rest = idx + 5 if idx >= 0 else 0
    ends = []
    for m in re.finditer(r"\d+", header[rest:]):
        ends.append((int(m.group()), rest + m.end()))
    if len(ends) < 2:
        return []
    width = ends[1][1] - ends[0][1]
    if width < 6 or width > 16:
        width = 10
    return [(seg, end - width, end) for seg, end in ends]


def _jday_from_title(line: str) -> float | None:
    m = re.search(r"Julian\s+(?:Date|day\s*=)\s*(\d+)\s+days\s+([\d.]+)\s+hours", line, re.I)
    if not m:
        return None
    days = float(m.group(1))
    hours = float(m.group(2))
    return days + hours / 24.0


def parse_snp_series(path: Path, title_key: str, segment: int) -> pd.DataFrame:
    """Extract surface and bottom values at one segment from W2 snp.opt grids."""
    rows = []
    with path.open(encoding="utf-8", errors="ignore") as f:
        pending_title = None
        pending_jday = None
        fields = None
        collecting = False
        col = None
        sfc = None
        bot = None
        k_sfc = None
        k_bot = None
        for raw in f:
            line = raw.rstrip("\n")
            if title_key.lower() in line.lower() and "Julian" in line:
                pending_jday = _jday_from_title(line)
                pending_title = line
                collecting = False
                fields = None
                continue
            if pending_jday is not None and (not collecting) and "Layer" in line and "Depth" in line:
                fields = _header_fields(line)
                col = None
                for seg, a, b in fields:
                    if seg == segment:
                        col = (a, b)
                        break
                collecting = col is not None
                sfc = bot = k_sfc = k_bot = None
                if not collecting:
                    pending_jday = None
                continue
            if collecting:
                s = line.strip()
                if not s:
                    if sfc is not None and pending_jday is not None:
                        rows.append((pending_jday, sfc, bot, k_sfc, k_bot))
                    collecting = False
                    pending_jday = None
                    continue
                if s.lower().startswith("layer") or "Julian" in line or line.startswith(" ***"):
                    if sfc is not None and pending_jday is not None:
                        rows.append((pending_jday, sfc, bot, k_sfc, k_bot))
                    collecting = False
                    pending_jday = None
                    continue
                parts = s.split()
                if not parts:
                    continue
                try:
                    k = int(float(parts[0]))
                except ValueError:
                    if sfc is not None and pending_jday is not None:
                        rows.append((pending_jday, sfc, bot, k_sfc, k_bot))
                    collecting = False
                    pending_jday = None
                    continue
                a, b = col
                if len(line) >= b:
                    chunk = line[a:b].strip()
                    if chunk:
                        try:
                            val = float(chunk)
                        except ValueError:
                            val = float("nan")
                        if np.isfinite(val) and val > MISSING:
                            if sfc is None:
                                sfc = val
                                k_sfc = k
                            bot = val
                            k_bot = k
        if collecting and sfc is not None and pending_jday is not None:
            rows.append((pending_jday, sfc, bot, k_sfc, k_bot))
    if not rows:
        return pd.DataFrame(columns=["JDAY", "sfc", "bot", "k_sfc", "k_bot"])
    return pd.DataFrame(rows, columns=["JDAY", "sfc", "bot", "k_sfc", "k_bot"])


def series_dict(jday, val, **meta) -> dict:
    jday = np.asarray(jday, float)
    val = np.asarray(val, float)
    m = np.isfinite(jday) & np.isfinite(val) & (val > MISSING)
    return {"jday": jday[m], "val": val[m], **meta}


def compare(ref: dict, alt: dict, pair_id: str, tol: float, primary: bool) -> dict:
    jj, o, s = align(ref["jday"], ref["val"], alt["jday"], alt["val"], tol=tol)
    row = {
        "id": pair_id,
        "primary": primary,
        "kind": "internal_consistency",
        "ref": {k: v for k, v in ref.items() if k not in ("jday", "val")},
        "alt": {k: v for k, v in alt.items() if k not in ("jday", "val")},
        "align_tol_day": tol,
        "jday_paired": jj.tolist() if len(jj) <= 8 else [float(jj.min()), float(jj.max())],
        **metrics(o, s),
    }
    row["_arrays"] = (jj, o, s)
    return row


def sod_stats(vals: np.ndarray) -> dict:
    v = np.asarray(vals, float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return {"n": 0}
    lo, hi = ALMEIDA_BAND
    return {
        "n": int(len(v)),
        "mean": _r4(float(np.mean(v))),
        "median": _r4(float(np.median(v))),
        "std": _r4(float(np.std(v))),
        "min": _r4(float(np.min(v))),
        "max": _r4(float(np.max(v))),
        "p10": _r4(float(np.percentile(v, 10))),
        "p90": _r4(float(np.percentile(v, 90))),
        "frac_in_0.5_3.0": _r4(float(np.mean((v >= lo) & (v <= hi)))),
        "frac_below_0.5": _r4(float(np.mean(v < lo))),
        "frac_above_3.0": _r4(float(np.mean(v > hi))),
        "n_in_band": int(np.sum((v >= lo) & (v <= hi))),
    }


def load_diag_block(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return jday, inst (n_t, 51), daily (n_t, 51)."""
    df = pd.read_csv(path)
    jday = pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy()
    inst = df.iloc[:, 2:53].apply(pd.to_numeric, errors="coerce").to_numpy()
    daily = df.iloc[:, 53:104].apply(pd.to_numeric, errors="coerce").to_numpy()
    return jday, inst, daily


def setup_style():
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 120


def plot_timeseries(pairs_for_legend, path, ylabel, title):
    fig, ax = plt.subplots(figsize=(11.2, 4.4))
    styles = [
        ("-", 1.6, 0.95),
        ("--", 1.3, 0.9),
        ("-.", 1.3, 0.9),
        (":", 1.5, 0.85),
        ("-", 1.0, 0.7),
    ]
    for i, ser in enumerate(pairs_for_legend):
        ls, lw, al = styles[i % len(styles)]
        ax.plot(ser["jday"], ser["val"], ls, lw=lw, alpha=al, label=ser["label"])
    ax.set_xlabel("JDAY")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="best", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()


def plot_scatter_grid(rows, path, xlabel_prefix, title):
    use = [r for r in rows if r.get("n", 0) >= 10]
    n = len(use)
    if n == 0:
        return
    cols = min(3, n)
    rws = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rws, cols, figsize=(4.2 * cols, 4.1 * rws), squeeze=False)
    for i, row in enumerate(use):
        ax = axes[i // cols][i % cols]
        _, o, s = row["_arrays"]
        lim = [min(o.min(), s.min()), max(o.max(), s.max())]
        pad = 0.04 * (lim[1] - lim[0] + 1e-6)
        lim = [lim[0] - pad, lim[1] + pad]
        ax.plot(lim, lim, "k--", lw=1)
        ax.scatter(o, s, s=8, alpha=0.35, c="tab:blue", edgecolors="none")
        if row.get("slope") is not None:
            xx = np.linspace(lim[0], lim[1], 50)
            ax.plot(xx, row["slope"] * xx + row["intercept"], color="tab:red", lw=1.1)
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("ref: " + row["ref"]["short"])
        ax.set_ylabel("alt: " + row["alt"]["short"])
        ax.set_title(
            f"{row['id']}\nR²={row.get('r2')}  NSE={row.get('nse')}  KGE={row.get('kge')}",
            fontsize=9,
        )
        ax.grid(True, alpha=0.3)
    for j in range(n, rws * cols):
        axes[j // cols][j % cols].axis("off")
    fig.suptitle(title, y=1.01)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_kge_bars(rows, path, title):
    use = [r for r in rows if r.get("n", 0) >= 10 and r.get("kge") is not None]
    if not use:
        return
    labels = [r["id"] for r in use]
    x = np.arange(len(use))
    w = 0.25
    fig, ax = plt.subplots(figsize=(max(8.5, 1.35 * len(use)), 4.6))
    ax.bar(x - w, [r["r"] for r in use], w, label="r", color="#4C78A8")
    ax.bar(x, [r["alpha"] for r in use], w, label="α = σs/σo", color="#F58518")
    ax.bar(x + w, [r["beta"] for r in use], w, label="β = μs/μo", color="#54A24B")
    ax.axhline(1.0, color="k", lw=0.8, ls="--")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=28, ha="right", fontsize=8)
    ax.set_ylabel("KGE 分量")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()


def plot_r2_nse(rows, path, title):
    use = [r for r in rows if r.get("n", 0) >= 10 and r.get("r2") is not None]
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    ax.scatter([r["r2"] for r in use], [r["nse"] for r in use], s=55, c="tab:blue", zorder=3)
    for r in use:
        ax.annotate(r["id"], (r["r2"], r["nse"]), fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.axhline(0.0, color="k", lw=0.7, ls="--")
    ax.set_xlabel("R²")
    ax.set_ylabel("NSE")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close()


def main() -> None:
    OUT_A.mkdir(parents=True, exist_ok=True)
    OUT_F.mkdir(parents=True, exist_ok=True)
    setup_style()

    # ----- DeGray temperature series -----
    tsr = load_tsr(DEGRAY / "tsr_1_seg31.csv")
    two = load_csv_skip(DEGRAY / "t_wdo_31.csv")
    str_t = load_csv_skip(DEGRAY / "two_str1_seg31.csv")
    gate_t = load_csv_skip(DEGRAY / "two_gate1_seg31.csv")
    prf = parse_prf_temperature(DEGRAY / "prf.opt")
    snp31 = parse_snp_series(DEGRAY / "snp.opt", "Temperature [T1]", 31)

    dg = {
        "TSR_T2_sfc_I31": series_dict(
            tsr["JDAY"],
            tsr[pick(tsr, "T2(C)")],
            short="TSR T2 I=31",
            file="tsr_1_seg31.csv",
            column="T2(C)",
            segment=31,
            layer="ETSR=0 surface (KT)",
            unit="degC",
            derived_from="native TSR surface temperature",
            time_support="instantaneous ~0.1 d",
        ),
        "TSR_Tvolavg": series_dict(
            tsr["JDAY"],
            tsr[pick(tsr, "Tvolavg(C)")],
            short="TSR Tvolavg",
            file="tsr_1_seg31.csv",
            column="Tvolavg(C)",
            segment=31,
            layer="waterbody volume average",
            unit="degC",
            derived_from="native TSR volume-averaged temperature",
            time_support="instantaneous ~0.1 d",
        ),
        "WDO_T_composite_I31": series_dict(
            two["JDAY"],
            two["T(C)"],
            short="WDO composite T",
            file="t_wdo_31.csv",
            column="T(C)",
            segment=31,
            layer="flow-weighted withdrawal mix",
            unit="degC",
            derived_from="WDO summed withdrawal temperature (STR+GATE)",
            time_support="instantaneous ~0.1 d",
        ),
        "STR_T_elev115_I31": series_dict(
            str_t["JDAY"],
            str_t["T(C)"],
            short="STR T elev 115 m",
            file="two_str1_seg31.csv",
            column="T(C)",
            segment=31,
            layer="structure centerline elev 115 m",
            unit="degC",
            derived_from="structure withdrawal temperature",
            time_support="instantaneous ~0.1 d",
        ),
        "GATE_T_elev120_I31": series_dict(
            gate_t["JDAY"],
            gate_t["T(C)"],
            short="GATE T elev 120 m",
            file="two_gate1_seg31.csv",
            column="T(C)",
            segment=31,
            layer="gate centerline elev 120 m",
            unit="degC",
            derived_from="gate withdrawal temperature",
            time_support="instantaneous ~0.1 d",
        ),
    }
    if 26 in prf:
        dg["PRF_T_sfc_I26"] = series_dict(
            prf[26]["JDAY"],
            prf[26]["T_sfc"],
            short="PRF T sfc I=26",
            file="prf.opt",
            column="TEMP first layer",
            segment=26,
            layer="K surface (first TEMP value)",
            unit="degC",
            derived_from="PRF vertical profile TEMP at IPR=26",
            time_support="profile dumps ~1 d",
        )
        dg["PRF_T_bot_I26"] = series_dict(
            prf[26]["JDAY"],
            prf[26]["T_bot"],
            short="PRF T bot I=26",
            file="prf.opt",
            column="TEMP last layer",
            segment=26,
            layer="K bottom (last TEMP value, 23 layers)",
            unit="degC",
            derived_from="PRF vertical profile TEMP at IPR=26",
            time_support="profile dumps ~1 d",
        )
    if len(snp31):
        dg["SNP_T_sfc_I31"] = series_dict(
            snp31["JDAY"],
            snp31["sfc"],
            short="SNP T sfc I=31",
            file="snp.opt",
            column="Temperature [T1] surface",
            segment=31,
            layer="first wet layer at I=31",
            unit="degC",
            derived_from="SNP 2-D temperature grid",
            time_support="snapshot (irregular, ~hours to ~14 d)",
        )
        dg["SNP_T_bot_I31"] = series_dict(
            snp31["JDAY"],
            snp31["bot"],
            short="SNP T bot I=31",
            file="snp.opt",
            column="Temperature [T1] bottom",
            segment=31,
            layer="last wet layer at I=31",
            unit="degC",
            derived_from="SNP 2-D temperature grid",
            time_support="snapshot (irregular, ~hours to ~14 d)",
        )

    ref_t = dg["TSR_T2_sfc_I31"]
    degray_pairs = [
        compare(ref_t, dg["TSR_Tvolavg"], "DG_T2_vs_Tvolavg", 0.05, True),
        compare(ref_t, dg["WDO_T_composite_I31"], "DG_T2_vs_WDO", 0.05, True),
        compare(ref_t, dg["STR_T_elev115_I31"], "DG_T2_vs_STR115", 0.05, False),
        compare(ref_t, dg["GATE_T_elev120_I31"], "DG_T2_vs_GATE120", 0.05, False),
        compare(dg["STR_T_elev115_I31"], dg["GATE_T_elev120_I31"], "DG_STR115_vs_GATE120", 0.05, True),
        compare(dg["WDO_T_composite_I31"], dg["STR_T_elev115_I31"], "DG_WDO_vs_STR115", 0.05, False),
    ]
    if "PRF_T_sfc_I26" in dg:
        degray_pairs.append(compare(ref_t, dg["PRF_T_sfc_I26"], "DG_T2_vs_PRF26sfc", 0.15, False))
        degray_pairs.append(compare(ref_t, dg["PRF_T_bot_I26"], "DG_T2_vs_PRF26bot", 0.15, False))
        degray_pairs.append(compare(dg["PRF_T_sfc_I26"], dg["PRF_T_bot_I26"], "DG_PRF26_sfc_vs_bot", 0.05, False))
    if "SNP_T_sfc_I31" in dg:
        degray_pairs.append(compare(ref_t, dg["SNP_T_sfc_I31"], "DG_T2_vs_SNP31sfc", 0.6, False))
        degray_pairs.append(compare(ref_t, dg["SNP_T_bot_I31"], "DG_T2_vs_SNP31bot", 0.6, False))
        degray_pairs.append(compare(dg["SNP_T_sfc_I31"], dg["SNP_T_bot_I31"], "DG_SNP31_sfc_vs_bot", 0.05, False))

    # daily-mean T2 vs instantaneous T2 (time-support provenance)
    dj, dv = daily_mean(ref_t["jday"], ref_t["val"])
    dg["TSR_T2_daily"] = series_dict(
        dj,
        dv,
        short="TSR T2 daily mean",
        file="tsr_1_seg31.csv",
        column="T2(C) grouped by floor(JDAY)+0.5",
        segment=31,
        layer="ETSR=0 surface, daily mean of instantaneous",
        unit="degC",
        derived_from="post-hoc daily mean of TSR T2",
        time_support="daily mean",
    )
    degray_pairs.append(compare(dg["TSR_T2_daily"], ref_t, "DG_T2daily_vs_T2inst", 0.55, False))

    # ----- Columbia DO series -----
    t45 = load_tsr(COL_ON / "tsr_1_seg45.csv")
    t49 = load_tsr(COL_ON / "tsr_2_seg49.csv")
    t33 = load_tsr(COL_ON / "tsr_3_seg33.csv")
    t45_off = load_tsr(COL_OFF / "tsr_1_seg45.csv")
    snp45 = parse_snp_series(COL_ON / "snp.opt", "Dissolved oxygen, g/m", 45)
    snp33 = parse_snp_series(COL_ON / "snp.opt", "Dissolved oxygen, g/m", 33)
    snp49 = parse_snp_series(COL_ON / "snp.opt", "Dissolved oxygen, g/m", 49)

    co = {
        "TSR_DO_I45": series_dict(
            t45["JDAY"],
            t45[pick(t45, "DO")],
            short="TSR DO I=45",
            file="tsr_1_seg45.csv",
            column="DO",
            segment=45,
            layer="ETSR=0 surface (KT)",
            unit="g/m3",
            derived_from="native TSR DO, SED_DIAG ON",
            time_support="instantaneous ~0.2 d",
            run="columbia_diag SED_DIAG=ON",
        ),
        "TSR_DO_I49": series_dict(
            t49["JDAY"],
            t49[pick(t49, "DO")],
            short="TSR DO I=49",
            file="tsr_2_seg49.csv",
            column="DO",
            segment=49,
            layer="ETSR=0 surface (KT)",
            unit="g/m3",
            derived_from="native TSR DO, SED_DIAG ON",
            time_support="instantaneous ~0.2 d",
            run="columbia_diag SED_DIAG=ON",
        ),
        "TSR_DO_I33": series_dict(
            t33["JDAY"],
            t33[pick(t33, "DO")],
            short="TSR DO I=33",
            file="tsr_3_seg33.csv",
            column="DO",
            segment=33,
            layer="ETSR=0 surface (KT)",
            unit="g/m3",
            derived_from="native TSR DO, SED_DIAG ON",
            time_support="instantaneous ~0.2 d",
            run="columbia_diag SED_DIAG=ON",
        ),
        "TSR_DO_I45_OFF": series_dict(
            t45_off["JDAY"],
            t45_off[pick(t45_off, "DO")],
            short="TSR DO I=45 OFF",
            file="tsr_1_seg45.csv",
            column="DO",
            segment=45,
            layer="ETSR=0 surface (KT)",
            unit="g/m3",
            derived_from="native TSR DO, SED_DIAG OFF baseline",
            time_support="instantaneous ~0.2 d",
            run="run_20260811_fixed SED_DIAG=OFF",
        ),
    }
    if len(snp45):
        co["SNP_DO_sfc_I45"] = series_dict(
            snp45["JDAY"],
            snp45["sfc"],
            short="SNP DO sfc I=45",
            file="snp.opt",
            column="Dissolved oxygen surface",
            segment=45,
            layer="first wet layer",
            unit="g/m3",
            derived_from="SNP 2-D DO grid, SED_DIAG ON",
            time_support="snapshot ~1 d",
            run="columbia_diag SED_DIAG=ON",
        )
        co["SNP_DO_bot_I45"] = series_dict(
            snp45["JDAY"],
            snp45["bot"],
            short="SNP DO bot I=45",
            file="snp.opt",
            column="Dissolved oxygen bottom",
            segment=45,
            layer="last wet layer",
            unit="g/m3",
            derived_from="SNP 2-D DO grid, SED_DIAG ON",
            time_support="snapshot ~1 d",
            run="columbia_diag SED_DIAG=ON",
        )
    if len(snp33):
        co["SNP_DO_sfc_I33"] = series_dict(
            snp33["JDAY"],
            snp33["sfc"],
            short="SNP DO sfc I=33",
            file="snp.opt",
            column="Dissolved oxygen surface",
            segment=33,
            layer="first wet layer",
            unit="g/m3",
            derived_from="SNP 2-D DO grid",
            time_support="snapshot ~1 d",
            run="columbia_diag SED_DIAG=ON",
        )
    if len(snp49):
        co["SNP_DO_sfc_I49"] = series_dict(
            snp49["JDAY"],
            snp49["sfc"],
            short="SNP DO sfc I=49",
            file="snp.opt",
            column="Dissolved oxygen surface",
            segment=49,
            layer="first wet layer",
            unit="g/m3",
            derived_from="SNP 2-D DO grid",
            time_support="snapshot ~1 d",
            run="columbia_diag SED_DIAG=ON",
        )

    ref_do = co["TSR_DO_I45"]
    columbia_pairs = [
        compare(ref_do, co["TSR_DO_I49"], "COL_DO_I45_vs_I49", 0.05, True),
        compare(ref_do, co["TSR_DO_I33"], "COL_DO_I45_vs_I33", 0.05, True),
        compare(co["TSR_DO_I49"], co["TSR_DO_I33"], "COL_DO_I49_vs_I33", 0.05, True),
        compare(ref_do, co["TSR_DO_I45_OFF"], "COL_DO_I45_ON_vs_OFF", 0.05, False),
    ]
    if "SNP_DO_sfc_I45" in co:
        columbia_pairs.append(compare(ref_do, co["SNP_DO_sfc_I45"], "COL_DO_TSR45_vs_SNPsfc", 0.15, False))
        columbia_pairs.append(compare(ref_do, co["SNP_DO_bot_I45"], "COL_DO_TSR45_vs_SNPbot", 0.15, False))
        columbia_pairs.append(compare(co["SNP_DO_sfc_I45"], co["SNP_DO_bot_I45"], "COL_DO_SNP45_sfc_vs_bot", 0.05, False))
    dj, dv = daily_mean(ref_do["jday"], ref_do["val"])
    co["TSR_DO_I45_daily"] = series_dict(
        dj,
        dv,
        short="TSR DO I=45 daily",
        file="tsr_1_seg45.csv",
        column="DO grouped by floor(JDAY)+0.5",
        segment=45,
        layer="ETSR=0, daily mean",
        unit="g/m3",
        derived_from="post-hoc daily mean of TSR DO",
        time_support="daily mean",
        run="columbia_diag SED_DIAG=ON",
    )
    columbia_pairs.append(compare(co["TSR_DO_I45_daily"], ref_do, "COL_DO_daily_vs_inst", 0.55, False))

    # ----- plots -----
    plot_timeseries(
        [
            {**ref_t, "label": "TSR T2 表层 I=31"},
            {**dg["TSR_Tvolavg"], "label": "TSR Tvolavg 库容均温"},
            {**dg["WDO_T_composite_I31"], "label": "WDO 取水混合 T"},
            {**dg["STR_T_elev115_I31"], "label": "STR 取水口 115 m"},
            {**dg.get("PRF_T_bot_I26", dg["GATE_T_elev120_I31"]), "label": "PRF I=26 底层" if "PRF_T_bot_I26" in dg else "GATE 120 m"},
        ],
        OUT_F / "w1_degray_T_timeseries.png",
        "T (°C)",
        "DeGray 水温：同一运行、不同输出通道（内部一致性，无观测）",
    )
    primary_dg = [p for p in degray_pairs if p["primary"]]
    plot_scatter_grid(
        primary_dg,
        OUT_F / "w1_degray_T_scatter.png",
        "ref T",
        "DeGray T 1:1（主口径；ref 不是观测）",
    )
    plot_kge_bars(
        primary_dg + [p for p in degray_pairs if p["id"] in ("DG_STR115_vs_GATE120", "DG_PRF26_sfc_vs_bot")],
        OUT_F / "w1_degray_T_kge_bars.png",
        "DeGray 水温 KGE 分解（r / α / β）",
    )
    plot_r2_nse(degray_pairs, OUT_F / "w1_degray_T_r2_vs_nse.png", "DeGray T：R² vs NSE（内部对照）")

    plot_timeseries(
        [
            {**co["TSR_DO_I45"], "label": "TSR DO I=45 ON"},
            {**co["TSR_DO_I49"], "label": "TSR DO I=49 ON"},
            {**co["TSR_DO_I33"], "label": "TSR DO I=33 ON"},
            {**co["TSR_DO_I45_OFF"], "label": "TSR DO I=45 OFF"},
        ],
        OUT_F / "w1_columbia_DO_timeseries.png",
        "DO (g m$^{-3}$)",
        "Columbia DO：同一物理量、不同断面 / ON vs OFF（内部一致性，无观测）",
    )
    primary_co = [p for p in columbia_pairs if p["primary"]]
    plot_scatter_grid(
        primary_co,
        OUT_F / "w1_columbia_DO_scatter.png",
        "ref DO",
        "Columbia DO 1:1（主口径；ref 不是观测）",
    )
    plot_kge_bars(
        primary_co + [p for p in columbia_pairs if p["id"] in ("COL_DO_I45_ON_vs_OFF", "COL_DO_SNP45_sfc_vs_bot")],
        OUT_F / "w1_columbia_DO_kge_bars.png",
        "Columbia DO KGE 分解（r / α / β）",
    )
    plot_r2_nse(columbia_pairs, OUT_F / "w1_columbia_DO_r2_vs_nse.png", "Columbia DO：R² vs NSE（内部对照）")

    # ----- W7 SOD -----
    sod_j, sod_i, sod_d = load_diag_block(COL_ON / "SedimentDiagenesis" / "Diagenesis_SOD.csv")
    csod_j, csod_i, csod_d = load_diag_block(COL_ON / "SedimentDiagenesis" / "Diagenesis_CSOD.csv")
    nsod_j, nsod_i, nsod_d = load_diag_block(COL_ON / "SedimentDiagenesis" / "Diagenesis_NSOD.csv")
    segs = np.arange(1, 52)
    spin = sod_j >= 33.0
    wet_i = sod_i > 0
    wet_d = sod_d > 0
    last = int(np.where(np.isfinite(sod_j))[0][-1])
    last_inst = sod_i[last]
    last_wet = last_inst[last_inst > 0]
    mean_wet_t = np.array([np.nanmean(sod_i[t, wet_i[t]]) if np.any(wet_i[t]) else np.nan for t in range(len(sod_j))])
    pooled_inst = sod_i[spin][wet_i[spin]]
    pooled_daily = sod_d[spin][wet_d[spin]]
    pooled_csod = csod_i[spin][wet_i[spin]]
    pooled_nsod = nsod_i[spin][wet_i[spin]]

    fig, ax = plt.subplots(figsize=(11.2, 4.3))
    ax.axhspan(ALMEIDA_BAND[0], ALMEIDA_BAND[1], color="tab:green", alpha=0.12, label="Almeida 扫描 0.5–3.0")
    ax.axhline(ALMEIDA_SD_BEST_MEAN, color="tab:green", ls="--", lw=1.1, label=f"Almeida SD 最优均值 {ALMEIDA_SD_BEST_MEAN}")
    ax.axhline(ALMEIDA_HYBRID_MEAN, color="tab:olive", ls=":", lw=1.1, label=f"Almeida Hybrid 均值 {ALMEIDA_HYBRID_MEAN}")
    ax.plot(sod_j[spin], mean_wet_t[spin], "-", lw=1.6, color="tab:blue", label="Columbia 湿段瞬时 SOD 均值")
    ax.set_xlabel("JDAY")
    ax.set_ylabel("SOD (g O$_2$ m$^{-2}$ d$^{-1}$)")
    ax.set_title("Columbia 移植成岩 SOD vs Almeida & Coelho 2025 区间（非率定）")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_F / "w7_columbia_sod_timeseries.png", dpi=150)
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
    axes[0].hist(pooled_inst, bins=30, color="tab:blue", alpha=0.85)
    axes[0].axvspan(*ALMEIDA_BAND, color="tab:green", alpha=0.15)
    axes[0].axvline(ALMEIDA_BAND[0], color="tab:green", ls="--")
    axes[0].axvline(ALMEIDA_BAND[1], color="tab:green", ls="--")
    axes[0].set_xlabel("湿段瞬时 SOD")
    axes[0].set_ylabel("计数（时间×断面）")
    axes[0].set_title("SOD 分布（JDAY≥33, SOD>0）")
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(segs, last_inst, "o-", ms=3, color="tab:blue")
    axes[1].axhspan(*ALMEIDA_BAND, color="tab:green", alpha=0.12)
    axes[1].set_xlabel("segment")
    axes[1].set_ylabel("SOD")
    axes[1].set_title(f"沿程瞬时 SOD  JDAY={sod_j[last]:.1f}")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_F / "w7_columbia_sod_histogram.png", dpi=150)
    plt.close()

    sod_json = {
        "source": {
            "run": str(COL_ON),
            "sod_file": "SedimentDiagenesis/Diagenesis_SOD.csv",
            "csod_file": "SedimentDiagenesis/Diagenesis_CSOD.csv",
            "nsod_file": "SedimentDiagenesis/Diagenesis_NSOD.csv",
            "layout": "col0=label, col1=JDAY, cols2-52=segs1-51 instantaneous, cols53-103=segs1-51 daily average",
            "wet_definition": "SOD > 0 (dry/boundary segments are 0)",
            "spinup_excluded": "JDAY < 33 (initial all-zero row at 32)",
            "parameter_origin": "W2_diagenesis.npt transplanted from DeGray; region-2 end segment 31→50. NOT Columbia-calibrated.",
        },
        "almeida_coelho_2025": {
            "citation": "Almeida, M.; Coelho, P. Geosci. Model Dev. 18, 6135–6161, 2025. doi:10.5194/gmd-18-6135-2025",
            "zenodo": "10.5281/zenodo.15775127",
            "zero_order_hybrid_sod_scan_gO2_m2_d": ALMEIDA_SOD_SCAN,
            "band": {"lo": ALMEIDA_BAND[0], "hi": ALMEIDA_BAND[1], "unit": "gO2 m-2 d-1"},
            "reported_best_mean_sod": {
                "sediment_diagenesis_run4": ALMEIDA_SD_BEST_MEAN,
                "hybrid": ALMEIDA_HYBRID_MEAN,
                "zero_order": ALMEIDA_ZERO_MEAN,
            },
            "note": "Scan is a user-specified zero-order/hybrid SOD experiment on a Portuguese reservoir, not a universal ecological range. Used here only as an independent order-of-magnitude benchmark.",
        },
        "columbia_instantaneous_wet_jday_ge_33": sod_stats(pooled_inst),
        "columbia_dailyavg_wet_jday_ge_33": sod_stats(pooled_daily),
        "columbia_last_jday_instantaneous_wet": {
            "jday": _r4(float(sod_j[last])),
            **sod_stats(last_wet),
            "matches_existing_diag_mean": _r4(float(np.mean(last_wet))),
        },
        "columbia_csod_wet_jday_ge_33": sod_stats(pooled_csod),
        "columbia_nsod_wet_jday_ge_33": sod_stats(pooled_nsod),
        "time_series_wet_mean_instantaneous": {
            "jday": [float(x) for x in sod_j[spin]],
            "mean_wet": [_r4(float(x)) for x in mean_wet_t[spin]],
        },
        "verdict": None,
    }
    inst_mean = sod_json["columbia_instantaneous_wet_jday_ge_33"].get("mean")
    last_mean = sod_json["columbia_last_jday_instantaneous_wet"].get("mean")
    frac = sod_json["columbia_instantaneous_wet_jday_ge_33"].get("frac_in_0.5_3.0")
    sod_json["verdict"] = {
        "mean_in_almeida_scan_band": bool(inst_mean is not None and ALMEIDA_BAND[0] <= inst_mean <= ALMEIDA_BAND[1]),
        "last_day_mean_in_band": bool(last_mean is not None and ALMEIDA_BAND[0] <= last_mean <= ALMEIDA_BAND[1]),
        "compared_to_almeida_sd_best_1.07": "Columbia wet-mean is lower than Almeida SD-model best mean (1.07) but still inside the 0.5–3.0 scan band used for zero-order/hybrid experiments."
        if inst_mean is not None
        else None,
        "cannot_treat_as_calibration": True,
        "frac_of_wet_cells_in_band": frac,
    }

    def strip_arrays(rows):
        out = []
        for r in rows:
            d = {k: v for k, v in r.items() if k != "_arrays"}
            out.append(d)
        return out

    def r2_nse_pattern(rows, primary_only=True):
        use = [r for r in rows if r.get("n", 0) >= 10 and r.get("r2") is not None]
        if primary_only:
            use = [r for r in use if r.get("primary")]
        if len(use) < 2:
            return {"n_pairs": len(use), "reproduced": False}
        r2s = [r["r2"] for r in use]
        nses = [r["nse"] for r in use]
        kges = [r["kge"] for r in use]
        return {
            "n_pairs": len(use),
            "r2_min": min(r2s),
            "r2_max": max(r2s),
            "r2_span": _r4(max(r2s) - min(r2s)),
            "nse_min": min(nses),
            "nse_max": max(nses),
            "nse_span": _r4(max(nses) - min(nses)),
            "kge_min": min(kges),
            "kge_max": max(kges),
            "kge_span": _r4(max(kges) - min(kges)),
            "r2_span_narrow_nse_span_wide": bool((max(r2s) - min(r2s)) < 0.15 and (max(nses) - min(nses)) > 0.4),
        }

    w1 = {
        "mode": "internal_consistency_provenance_ambiguity",
        "not_skill_vs_observations": True,
        "observation_search": {
            "degray_official_example": "no independent T/DO observations in v4.5.5 or v5.0_beta example folders",
            "columbia_official_example": "no independent DO observations; only forcing/boundary files",
            "only_example_with_obs": "Bonneville CCIW_TDG_Temp_2011-2015.csv",
        },
        "bonneville_reference_not_recomputed": BONNEVILLE_REF,
        "degray": {
            "run": str(DEGRAY),
            "variable": "temperature_C",
            "n_prf_seg26": int(len(prf[26])) if 26 in prf else 0,
            "n_snp_seg31": int(len(snp31)),
            "series_vpr": {k: {kk: vv for kk, vv in v.items() if kk not in ("jday", "val")} for k, v in dg.items()},
            "pairs": strip_arrays(degray_pairs),
            "pattern_primary": r2_nse_pattern(degray_pairs, True),
            "pattern_all": r2_nse_pattern(degray_pairs, False),
        },
        "columbia": {
            "run_on": str(COL_ON),
            "run_off": str(COL_OFF),
            "variable": "DO_g_m3",
            "wdo_enabled": False,
            "n_snp_do_seg45": int(len(snp45)),
            "series_vpr": {k: {kk: vv for kk, vv in v.items() if kk not in ("jday", "val")} for k, v in co.items()},
            "pairs": strip_arrays(columbia_pairs),
            "pattern_primary": r2_nse_pattern(columbia_pairs, True),
            "pattern_all": r2_nse_pattern(columbia_pairs, False),
        },
        "figures": [
            str(OUT_F / "w1_degray_T_timeseries.png"),
            str(OUT_F / "w1_degray_T_scatter.png"),
            str(OUT_F / "w1_degray_T_kge_bars.png"),
            str(OUT_F / "w1_degray_T_r2_vs_nse.png"),
            str(OUT_F / "w1_columbia_DO_timeseries.png"),
            str(OUT_F / "w1_columbia_DO_scatter.png"),
            str(OUT_F / "w1_columbia_DO_kge_bars.png"),
            str(OUT_F / "w1_columbia_DO_r2_vs_nse.png"),
            str(OUT_F / "w7_columbia_sod_timeseries.png"),
            str(OUT_F / "w7_columbia_sod_histogram.png"),
        ],
    }
    (OUT_A / "w1_provenance_metrics.json").write_text(json.dumps(w1, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_A / "w7_columbia_sod_vs_almeida.json").write_text(json.dumps(sod_json, ensure_ascii=False, indent=2), encoding="utf-8")

    print("DeGray primary:")
    for r in primary_dg:
        print(r["id"], {k: r.get(k) for k in ("n", "r2", "nse", "kge", "r", "alpha", "beta", "pbias", "mae", "slope")})
    print("Columbia primary:")
    for r in primary_co:
        print(r["id"], {k: r.get(k) for k in ("n", "r2", "nse", "kge", "r", "alpha", "beta", "pbias", "mae", "slope")})
    print("pattern DG", w1["degray"]["pattern_primary"])
    print("pattern COL", w1["columbia"]["pattern_primary"])
    print("SOD inst wet", sod_json["columbia_instantaneous_wet_jday_ge_33"])
    print("SOD last", sod_json["columbia_last_jday_instantaneous_wet"])
    print("wrote", OUT_A / "w1_provenance_metrics.json")


if __name__ == "__main__":
    main()
