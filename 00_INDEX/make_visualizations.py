#!/usr/bin/env python3
"""Post-process CE-QUAL-W2 repro runs into meaningful figures.

Outputs under 05_REPRO_RUNS/<run_id>/analysis/:
  - multi-variable timeseries (ELWS/T2/DO/...)
  - bathymetry plan / planform-style width map
  - longitudinal / vertical profile contour when cpl/prf available
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
RUN_ID = "run_20260811_fixed"
RUN_BASE = ROOT / "05_REPRO_RUNS" / RUN_ID
OUT_DIR = RUN_BASE / "analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Prefer Chinese-capable fonts when available
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


@dataclass
class CaseSpec:
    name: str
    short: str
    tsr_glob: str
    preferred_vars: list[str]


CASES = [
    CaseSpec("Long Lake", "Long_Lake", "tsr_*.csv", ["ELWS(m)", "T2(C)", "DEPTH(m)", "DO", "Gen1"]),
    CaseSpec(
        "DeGray Reservoir with sediment diagenesis and vertical algae migration",
        "DeGray",
        "tsr_*.csv",
        ["ELWS(m)", "T2(C)", "DEPTH(m)", "DO", "ALG1"],
    ),
    CaseSpec("Columbia Slough Estuary", "Columbia_Slough", "tsr_*.csv", ["ELWS(m)", "T2(C)", "DEPTH(m)", "DO"]),
]


def load_tsr(path: Path) -> pd.DataFrame:
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.lstrip().startswith("$"):
            continue
        if raw.strip():
            lines.append(raw)
    if not lines:
        raise RuntimeError(f"empty TSR: {path}")
    df = pd.read_csv(StringIO("\n".join(lines))
                     )
    # normalize column names
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(axis=0, how="all")
    return df


def find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    cols = list(df.columns)
    lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand in cols:
            return cand
        if cand.lower() in lower:
            return lower[cand.lower()]
        # fuzzy contains
        for c in cols:
            if cand.lower().replace(" ", "") in c.lower().replace(" ", ""):
                return c
    return None


def parse_bathy(case_dir: Path) -> Optional[dict]:
    bths = sorted(case_dir.glob("bth*.csv"))
    if not bths:
        return None
    path = bths[0]
    rows = [r.strip() for r in path.read_text(encoding="utf-8", errors="ignore").splitlines() if r.strip() and not r.strip().startswith("$")]
    seg = dlx = elws = phi0 = None
    width_rows = []
    layer_h = []
    mode = None
    for r in rows:
        parts = [p.strip() for p in r.split(",")]
        key = parts[0].upper().replace("$", "")
        # Some examples use a leading blank key then segment numbers: ", 1, 2, 3, ..."
        if key.startswith("SEG") or (key == "" and len(parts) > 3 and all(re.fullmatch(r"-?\d+(\.\d+)?", p or "x") for p in parts[1:4])):
            vals = []
            for x in parts[1:]:
                if x in {"", "?", "K", "ELEV"}:
                    continue
                try:
                    vals.append(float(x))
                except ValueError:
                    break
            if len(vals) >= 3:
                seg = np.array(vals, dtype=float)
        elif key == "DLX":
            dlx = np.array([float(x) for x in parts[1:] if x not in {"", "K", "ELEV"}], dtype=float)
        elif key == "ELWS":
            elws = np.array([float(x) for x in parts[1:] if x not in {"", "K", "ELEV"}], dtype=float)
        elif key == "PHI0":
            phi0 = np.array([float(x) for x in parts[1:] if x not in {"", "K", "ELEV"}], dtype=float)
        elif key.startswith("LAYER"):
            mode = "widths"
            continue
        elif mode == "widths":
            vals = []
            ok = True
            for p in parts:
                if p in {"", "K", "ELEV"}:
                    continue
                try:
                    vals.append(float(p))
                except ValueError:
                    ok = False
                    break
            if ok and len(vals) >= 2:
                layer_h.append(vals[0])
                # drop trailing layer index if present (..., K)
                width_vals = vals[1:]
                if len(width_vals) > 1 and width_vals[-1] in {float(i) for i in range(0, 200)} and width_vals[-1] < 200:
                    # last column often layer index; keep widths only if length matches seg later
                    pass
                width_rows.append(width_vals)
    if seg is None or dlx is None or not width_rows:
        return None
    # normalize width matrix columns to seg/dlx length
    n = min(len(seg), len(dlx), min(len(r) for r in width_rows))
    # if trailing layer-index column exists, width_rows may be n or n+1
    widths = []
    for r in width_rows:
        if len(r) >= n + 1 and abs(r[-1] - (len(widths) + 1)) < 1e-6:
            widths.append(r[:n])
        else:
            widths.append(r[:n])
    W = np.array(widths, dtype=float)
    seg = seg[:n]
    dlx = dlx[:n]
    elws = elws[:n] if elws is not None else None
    phi0 = phi0[:n] if phi0 is not None else None
    with np.errstate(all="ignore"):
        surface_width = np.nanmax(np.where(W > 0, W, np.nan), axis=0)
    surface_width = np.nan_to_num(surface_width, nan=0.0)
    depth_proxy = np.sum(W > 0, axis=0).astype(float)
    if layer_h:
        lh = np.array(layer_h, dtype=float)
        depth_m = np.array([float(np.sum(lh[: int(k)])) if k > 0 else 0.0 for k in depth_proxy])
    else:
        depth_m = depth_proxy
    return {
        "path": str(path),
        "seg": seg,
        "dlx": dlx,
        "elws": elws,
        "phi0": phi0,
        "W": W,
        "surface_width": surface_width,
        "depth_m": depth_m,
        "layer_h": np.array(layer_h, dtype=float) if layer_h else None,
    }


def xy_from_phi(dlx: np.ndarray, phi0: Optional[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    x = np.zeros(len(dlx))
    y = np.zeros(len(dlx))
    if phi0 is None or len(phi0) != len(dlx):
        # fall back to cumulative distance on x
        x[0] = dlx[0] * 0.5
        for i in range(1, len(dlx)):
            x[i] = x[i - 1] + 0.5 * (dlx[i - 1] + dlx[i])
        return x, y
    # integrate segment centerline using orientation PHI0 (radians)
    x[0] = 0.0
    y[0] = 0.0
    for i in range(1, len(dlx)):
        ang = phi0[i - 1]
        x[i] = x[i - 1] + dlx[i - 1] * np.cos(ang)
        y[i] = y[i - 1] + dlx[i - 1] * np.sin(ang)
    return x, y


def plot_timeseries(case: CaseSpec, case_dir: Path, manifest: dict) -> None:
    files = sorted(case_dir.glob(case.tsr_glob))
    if not files:
        manifest["timeseries"] = {"status": "missing_tsr"}
        return
    # pick up to 4 segments including first/mid/last
    pick = []
    if len(files) == 1:
        pick = files
    else:
        idxs = sorted(set([0, len(files) // 3, 2 * len(files) // 3, len(files) - 1]))
        pick = [files[i] for i in idxs]

    frames = []
    for f in pick:
        df = load_tsr(f)
        jday = find_col(df, ["JDAY", "JDAY(day)", "JDAY "])
        if jday is None:
            continue
        seg = re.search(r"seg(\d+)", f.name, re.I)
        seg_lab = f"seg{seg.group(1)}" if seg else f.stem
        frames.append((seg_lab, df, jday))
    if not frames:
        manifest["timeseries"] = {"status": "parse_failed"}
        return

    # discover available vars
    sample = frames[0][1]
    var_map = {}
    for pref in case.preferred_vars:
        aliases = {
            "DO": ["DO", "DO(mg/l)", "Dissolved oxygen", "             DO"],
            "ALG1": ["ALG1", "Algae1", "           ALG1"],
            "Gen1": ["Gen1", "           Gen1"],
            "ELWS(m)": ["ELWS(m)", "ELWS"],
            "T2(C)": ["T2(C)", "T2"],
            "DEPTH(m)": ["DEPTH(m)", "DEPTH"],
        }.get(pref, [pref])
        col = find_col(sample, aliases)
        if col is not None:
            var_map[pref] = col

    if not var_map:
        # fallback: first few numeric columns after JDAY
        j0 = frames[0][2]
        nums = [c for c in sample.columns if c != j0 and sample[c].notna().sum() > 5]
        for c in nums[:3]:
            var_map[c] = c

    nvars = len(var_map)
    fig, axes = plt.subplots(nvars, 1, figsize=(11, 2.6 * nvars), sharex=True)
    if nvars == 1:
        axes = [axes]
    titles = {
        "ELWS(m)": "水位 ELWS（Elevation of Water Surface，水面高程，m）",
        "T2(C)": "水温 T2（Temperature，℃）",
        "DEPTH(m)": "水深 DEPTH（m）",
        "DO": "溶解氧 DO（Dissolved Oxygen，mg/L 或 g/m³）",
        "ALG1": "藻类 ALG1（Algae biomass）",
        "Gen1": "通用示踪/组分 Gen1",
    }
    for ax, (lab, col) in zip(axes, var_map.items()):
        for seg_lab, df, jday in frames:
            y = df[col].to_numpy()
            x = df[jday].to_numpy()
            m = np.isfinite(x) & np.isfinite(y) & (y > -98)
            if m.sum() == 0:
                continue
            ax.plot(x[m], y[m], lw=1.2, label=seg_lab)
        ax.set_ylabel(lab)
        ax.set_title(titles.get(lab, lab))
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=8, ncol=min(4, len(frames)))
    axes[-1].set_xlabel("儒略日 JDAY（Julian day）")
    fig.suptitle(f"{case.name} — 多断面时间序列", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    out = OUT_DIR / f"{case.short}_timeseries.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)

    # metrics: points and ranges
    info = {
        "status": "ok",
        "file": str(out),
        "segments_plotted": [s for s, _, _ in frames],
        "variables": list(var_map.keys()),
        "points_by_segment": {s: int(df.shape[0]) for s, df, _ in frames},
    }
    manifest["timeseries"] = info


def plot_planview(case: CaseSpec, case_dir: Path, manifest: dict) -> None:
    b = parse_bathy(case_dir)
    if b is None:
        manifest["planview"] = {"status": "missing_bathy"}
        return
    x, y = xy_from_phi(b["dlx"], b["phi0"])
    # left/right bank from surface width and orientation
    half = np.nan_to_num(b["surface_width"], nan=0.0) * 0.5
    if b["phi0"] is not None:
        nx = -np.sin(b["phi0"])
        ny = np.cos(b["phi0"])
    else:
        nx = np.zeros_like(x)
        ny = np.ones_like(x)
    xl, yl = x + half * nx, y + half * ny
    xr, yr = x - half * nx, y - half * ny

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    sc = ax.scatter(x, y, c=b["depth_m"], cmap="viridis", s=28)
    ax.plot(xl, yl, color="steelblue", lw=1.0, alpha=0.8, label="近似左岸")
    ax.plot(xr, yr, color="steelblue", lw=1.0, alpha=0.8, label="近似右岸")
    ax.plot(x, y, color="k", lw=0.6, alpha=0.5)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_title("河道/库区俯视（中心线+岸线示意）")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    cb = fig.colorbar(sc, ax=ax, fraction=0.046)
    cb.set_label("近似水深 (m)")
    ax.legend(fontsize=8)

    ax2 = axes[1]
    dist = np.concatenate([[0.0], np.cumsum(b["dlx"][:-1])])
    # longitudinal depth/width
    ax2.fill_between(dist, 0, b["depth_m"], color="#4C78A8", alpha=0.35, label="近似最大水深")
    ax2.plot(dist, b["depth_m"], color="#4C78A8", lw=1.5)
    ax2b = ax2.twinx()
    ax2b.plot(dist, b["surface_width"], color="#F58518", lw=1.4, label="表层宽度")
    ax2.set_xlabel("沿程距离 (m)")
    ax2.set_ylabel("水深 (m)", color="#4C78A8")
    ax2b.set_ylabel("宽度 (m)", color="#F58518")
    ax2.set_title("沿程水深 / 宽度剖面")
    ax2.grid(True, alpha=0.3)

    fig.suptitle(f"{case.name} — 地形俯视与沿程剖面（来自 {Path(b['path']).name}）", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = OUT_DIR / f"{case.short}_planview.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    manifest["planview"] = {
        "status": "ok",
        "file": str(out),
        "segments": int(len(b["seg"])),
        "bathy": Path(b["path"]).name,
    }


def parse_w2_prf_temperature(path: Path) -> Optional[tuple[np.ndarray, np.ndarray, np.ndarray, str]]:
    """Parse W2 native prf.opt vertical TEMP blocks (non-Tecplot).

    Returns layer bottom elevations (m), temperatures (C), metadata string.
    """
    if not path.exists() or path.stat().st_size < 100:
        return None
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    layer_h: list[float] = []
    for i, line in enumerate(lines):
        parts = line.split()
        if len(parts) == 1:
            try:
                n = int(float(parts[0]))
            except ValueError:
                continue
            if n < 4 or n > 80:
                continue
            vals: list[float] = []
            j = i + 1
            while j < len(lines) and len(vals) < n:
                for p in lines[j].split():
                    try:
                        vals.append(float(p))
                    except ValueError:
                        continue
                    if len(vals) >= n:
                        break
                j += 1
            if len(vals) >= n:
                layer_h = vals[:n]
                break

    if not layer_h:
        return None

    best_temps: list[float] = []
    best_meta = ""
    for i, line in enumerate(lines):
        parts = line.split()
        if not parts or parts[0].upper() != "TEMP":
            continue
        if len(parts) < 2:
            continue
        try:
            nlay = int(float(parts[1]))
        except ValueError:
            continue
        temps: list[float] = []
        j = i + 1
        while j < len(lines) and len(temps) < nlay:
            for p in lines[j].split():
                try:
                    temps.append(float(p))
                except ValueError:
                    continue
                if len(temps) >= nlay:
                    break
            j += 1
        if len(temps) >= max(4, nlay - 1):
            best_temps = temps[:nlay]
            meta = ""
            for k in range(i + 1, min(i + 8, len(lines))):
                if any(m in lines[k] for m in ("Feb", "Jan", "Mar", "199")):
                    meta = lines[k].strip()
                    break
            best_meta = meta or f"TEMP n={nlay}"

    if len(best_temps) < 4:
        return None

    n = min(len(best_temps), len(layer_h))
    h = np.array(layer_h[:n], dtype=float)
    temp = np.array(best_temps[:n], dtype=float)
    depth = np.cumsum(h) - h * 0.5  # layer-center depth below surface (m)
    m = np.isfinite(temp) & (temp > -50) & (temp < 50)
    if np.sum(m) < 4:
        return None
    return depth[m], temp[m], h[m], best_meta


def parse_cpl_temperature(path: Path) -> Optional[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Parse first ZONE of Tecplot-like cpl*.opt into distance, elevation, T."""
    if not path.exists() or path.stat().st_size < 50:
        return None
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    # find VARIABLES and first ZONE
    var_idx = None
    zone_idx = None
    for i, line in enumerate(text):
        u = line.strip().upper()
        if u.startswith("VARIABLES"):
            var_idx = i
        if u.startswith("ZONE") and zone_idx is None and var_idx is not None:
            zone_idx = i
            break
    if zone_idx is None:
        return None
    rows = []
    for line in text[zone_idx + 1 :]:
        s = line.strip()
        if not s:
            continue
        if s.upper().startswith("ZONE") or s.upper().startswith("TITLE") or s.upper().startswith("VARIABLES"):
            break
        parts = s.replace(",", " ").split()
        vals = []
        ok = True
        for p in parts:
            try:
                vals.append(float(p))
            except ValueError:
                ok = False
                break
        if ok and len(vals) >= 5:
            rows.append(vals[:5])  # Distance, Elevation, U, W, T
    if len(rows) < 8:
        return None
    arr = np.array(rows, dtype=float)
    dist, elev, temp = arr[:, 0], arr[:, 1], arr[:, 4]
    return dist, elev, temp


def plot_profile(case: CaseSpec, case_dir: Path, manifest: dict) -> None:
    cpls = sorted(case_dir.glob("cpl*.opt"))
    prfs = sorted(case_dir.glob("prf*.opt"))
    target = None
    kind = None
    for p in cpls + prfs:
        if p.stat().st_size > 200:
            target = p
            kind = "CPL" if "cpl" in p.name.lower() else "PRF"
            break
    if target is None:
        manifest["profile"] = {"status": "missing_cpl_prf"}
        return

    parsed = parse_cpl_temperature(target)
    prf_parsed = None
    if parsed is None:
        for p in prfs:
            if p.stat().st_size > 100:
                prf_parsed = parse_w2_prf_temperature(p)
                if prf_parsed is not None:
                    target = p
                    kind = "PRF"
                    break

    if parsed is None and prf_parsed is not None:
        elev, temp, _layer_h, meta = prf_parsed
        fig, ax = plt.subplots(figsize=(11, 4.8))
        ax.plot(temp, elev, "o-", color="#dc2626", lw=1.6, markersize=5)
        ax.set_xlabel("温度 T (℃)")
        ax.set_ylabel("深度（层中心，m）")
        ax.set_title(f"{case.name} — PRF 垂向温度剖面（{target.name}；{meta}）")
        ax.grid(True, alpha=0.35)
        fig.tight_layout()
        out = OUT_DIR / f"{case.short}_profile.png"
        fig.savefig(out, dpi=160)
        plt.close(fig)
        manifest["profile"] = {
            "status": "ok_prf_vertical",
            "file": str(out),
            "source": target.name,
            "kind": "PRF",
            "points": int(len(temp)),
            "t_min": float(np.nanmin(temp)),
            "t_max": float(np.nanmax(temp)),
            "note": "W2 native PRF vertical profile (non-Tecplot)",
        }
        return

    if parsed is None:
        # fallback: plot raw numeric heatmap from width matrix in bathy as "剖面示意"
        b = parse_bathy(case_dir)
        if b is None:
            manifest["profile"] = {"status": "unparsed", "file": target.name}
            return
        fig, ax = plt.subplots(figsize=(11, 4.8))
        im = ax.imshow(
            np.where(b["W"] > 0, b["W"], np.nan),
            aspect="auto",
            origin="upper",
            cmap="YlGnBu",
        )
        ax.set_xlabel("河段编号（列）")
        ax.set_ylabel("层号（行，上→下）")
        ax.set_title(f"{case.name} — 地形宽度场（替代剖面；{Path(b['path']).name}）")
        cb = fig.colorbar(im, ax=ax)
        cb.set_label("宽度 (m)")
        fig.tight_layout()
        out = OUT_DIR / f"{case.short}_profile.png"
        fig.savefig(out, dpi=160)
        plt.close(fig)
        manifest["profile"] = {"status": "bathy_fallback", "file": str(out), "source": Path(b["path"]).name}
        return

    dist, elev, temp = parsed
    # drop fill flags
    m = np.isfinite(temp) & (temp > -90) & np.isfinite(dist) & np.isfinite(elev)
    dist, elev, temp = dist[m], elev[m], temp[m]
    if len(temp) < 8:
        manifest["profile"] = {"status": "too_few_valid_points", "source": target.name}
        return

    fig, ax = plt.subplots(figsize=(11, 4.8))
    sc = ax.tricontourf(dist, elev, temp, levels=16, cmap="coolwarm")
    ax.scatter(dist, elev, c=temp, s=8, cmap="coolwarm", edgecolors="none")
    ax.set_xlabel("沿程距离 Distance (m)")
    ax.set_ylabel("高程 Elevation (m)")
    ax.set_title(f"{case.name} — {kind} 温度纵剖面/等值线（{target.name} 首个 ZONE）")
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("温度 T (℃)")
    fig.tight_layout()
    out = OUT_DIR / f"{case.short}_profile.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    manifest["profile"] = {
        "status": "ok",
        "file": str(out),
        "source": target.name,
        "kind": kind,
        "points": int(len(temp)),
        "t_min": float(np.nanmin(temp)),
        "t_max": float(np.nanmax(temp)),
    }


def main() -> None:
    summary_path = RUN_BASE / "run_summary.json"
    run_summary = {}
    if summary_path.exists():
        run_summary = json.loads(summary_path.read_text(encoding="utf-8"))

    manifest_path = OUT_DIR / "figure_manifest.json"
    if manifest_path.exists():
        all_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        all_manifest.setdefault("cases", {})
    else:
        all_manifest = {"run_id": RUN_ID, "cases": {}}

    for case in CASES:
        case_dir = RUN_BASE / case.name
        man = all_manifest.setdefault("cases", {}).setdefault(case.short, {"case": case.name})
        man["case"] = case.name
        man["exists"] = case_dir.exists()
        if not case_dir.exists():
            continue
        plot_timeseries(case, case_dir, man)
        plot_planview(case, case_dir, man)
        plot_profile(case, case_dir, man)
        # tsr point count quick stats
        tsr_files = sorted(case_dir.glob("tsr_*.csv"))
        man["tsr_files"] = len(tsr_files)
        if tsr_files:
            try:
                man["tsr_rows_example"] = int(load_tsr(tsr_files[0]).shape[0])
            except Exception as e:
                man["tsr_rows_example"] = f"error:{e}"
        all_manifest["cases"][case.short] = man
        print(f"figures: {case.short} -> {json.dumps({k: man[k] for k in man if k != 'watershed_basemap'}, ensure_ascii=False)}")

    all_manifest["run_summary"] = run_summary
    out = OUT_DIR / "figure_manifest.json"
    out.write_text(json.dumps(all_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"WROTE {out}")


if __name__ == "__main__":
    main()
