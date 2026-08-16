#!/usr/bin/env python3
"""Minimal w2eval: assemble run-cards from existing analysis JSON + NHR records.

Does not run CE-QUAL-W2. Reads 06_PAPER/analysis/*.json and optionally
00_INDEX/parse_nhr.py if a case is missing from the cached NHR dump.

Usage:
    python 06_PAPER/w2eval/w2eval.py
    python 06_PAPER/w2eval/w2eval.py --out 06_PAPER/w2eval/cards
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
PAPER = ROOT / "06_PAPER"
ANALYSIS = PAPER / "analysis"
DEFAULT_OUT = PAPER / "w2eval" / "cards"

sys.path.insert(0, str(ROOT / "00_INDEX"))
try:
    from parse_nhr import parse_nhr  # noqa: E402
except Exception:  # pragma: no cover - parser still optional if JSON is complete
    parse_nhr = None  # type: ignore[assignment]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: str | Path | None) -> str | None:
    if path is None:
        return None
    p = Path(str(path))
    try:
        return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path).replace("\\", "/")


def wrn_path_for(case_dir: str | None) -> str | None:
    if not case_dir:
        return None
    p = Path(case_dir) / "w2.wrn"
    return rel(p)


def round_or_none(x: Any, nd: int) -> Any:
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return x
    if v != v:  # NaN
        return None
    return round(v, nd)


def metric_row(
    *,
    caliber: str,
    title: str,
    file: str | None = None,
    column: str | None = None,
    n: int | None = None,
    r2: Any = None,
    nse: Any = None,
    kge: Any = None,
    r: Any = None,
    alpha: Any = None,
    beta: Any = None,
    pbias: Any = None,
    mae: Any = None,
    extra: dict[str, Any] | None = None,
    available: bool = True,
    status: str = "ok",
    pairing: str | None = None,
) -> dict[str, Any]:
    row = {
        "caliber": caliber,
        "title": title,
        "available": available,
        "status": status,
        "file": file,
        "column": column,
        "n": n,
        "r2": round_or_none(r2, 4),
        "nse": round_or_none(nse, 4),
        "kge": round_or_none(kge, 4),
        "r": round_or_none(r, 4),
        "alpha": round_or_none(alpha, 4),
        "beta": round_or_none(beta, 4),
        "pbias": round_or_none(pbias, 4),
        "mae": round_or_none(mae, 4),
        "pairing": pairing,
    }
    if extra:
        row.update(extra)
    return row


def vpr_item(
    *,
    caliber: str,
    file: str,
    column: str,
    segment: Any,
    layer: str,
    unit: str,
    derived_from: str,
    time_support: str,
    pairing_tolerance: str | None,
    notes: str | None = None,
) -> dict[str, Any]:
    item = {
        "caliber": caliber,
        "file": file,
        "column": column,
        "segment": segment,
        "layer": layer,
        "unit": unit,
        "derived_from": derived_from,
        "time_support": time_support,
        "pairing_tolerance": pairing_tolerance,
    }
    if notes:
        item["notes"] = notes
    return item


def find_nhr_case(existing: dict[str, Any], *needles: str) -> dict[str, Any] | None:
    for case in existing.get("cases", []):
        blob = (case.get("run_relative") or "") + " | " + (case.get("case_dir") or "")
        blob = blob.replace("\\", "/")
        if all(n.replace("\\", "/") in blob for n in needles):
            return case
    # Cached dump missed this directory: parse wrn/snp in place (still no model run).
    if parse_nhr is not None and needles:
        guess = ROOT / "05_REPRO_RUNS" / Path(needles[0])
        if guess.exists() and (guess / "w2_con.csv").exists():
            rec = parse_nhr(guess)
            rec["run_relative"] = rel(guess)
            return rec
    return None


def slim_nhr(
    case: dict[str, Any] | None,
    *,
    fallback_dir: str | None = None,
    scan_job: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Numerical Health Record slice required on every run-card."""
    nhr_src: dict[str, Any] = {}
    sched: dict[str, Any] = {}
    case_dir = fallback_dir
    wrn_exists = None
    completed = None
    last_jday = None
    if case:
        nhr_src = case.get("nhr") or {}
        sched = case.get("dlt_schedule") or {}
        case_dir = case.get("case_dir") or fallback_dir
        completed = case.get("completed")
        last_jday = case.get("last_jday")
        wrn_exists = nhr_src.get("wrn_exists")
    if scan_job:
        nhr_src = {
            **nhr_src,
            "neg_surface_thickness_count": scan_job.get(
                "neg_surface_thickness_count", nhr_src.get("neg_surface_thickness_count")
            ),
            "add_layer_count": scan_job.get("add_layer_count", nhr_src.get("add_layer_count")),
            "subtract_layer_count": scan_job.get(
                "subtract_layer_count", nhr_src.get("subtract_layer_count")
            ),
            "low_water_count": scan_job.get("low_water_count", nhr_src.get("low_water_count")),
            "dltmin_hint_count": scan_job.get(
                "dltmin_hint_count", nhr_src.get("dltmin_hint_count")
            ),
            "exit_zero_masks_rollback": scan_job.get(
                "exit_zero_masks_rollback", nhr_src.get("exit_zero_masks_rollback")
            ),
            "snp_runtime": scan_job.get("snp_runtime") or nhr_src.get("snp_runtime") or {},
            "dlt_trajectory": scan_job.get("dlt_trajectory") or nhr_src.get("dlt_trajectory"),
        }
        case_dir = scan_job.get("dir") or case_dir
        completed = scan_job.get("completed", completed)
        last_jday = scan_job.get("last_jday", last_jday)
        if "dltinter" in scan_job:
            sched = {**sched, "dltinter": scan_job["dltinter"]}
        nested = scan_job.get("nhr") or {}
        if nested:
            wrn_exists = nested.get("wrn_exists", wrn_exists)
            nhr_src = {**nested, **{k: v for k, v in nhr_src.items() if v is not None}}

    snp = nhr_src.get("snp_runtime") or {}
    err = nhr_src.get("w2_err") or {}
    exit_zero = nhr_src.get("exit_zero_masks_rollback")
    if exit_zero is None:
        exit_zero = bool(
            (nhr_src.get("neg_surface_thickness_count") or 0) > 0
            and not err.get("present")
            and (snp.get("normal_termination") or completed)
        )
    dltinter = sched.get("dltinter")
    if isinstance(dltinter, str):
        dltinter = dltinter.strip() or None
    wrn = wrn_path_for(case_dir)
    if wrn_exists is None and wrn:
        wrn_exists = (ROOT / wrn).exists() if not Path(wrn).is_absolute() else Path(wrn).exists()

    window_dlt = None
    traj = nhr_src.get("dlt_trajectory") or {}
    if isinstance(traj, dict):
        window_dlt = traj.get("window") or traj.get("full")

    return {
        "case_dir": rel(case_dir) if case_dir else None,
        "wrn_path": wrn,
        "wrn_exists": bool(wrn_exists) if wrn_exists is not None else None,
        "neg_surface_thickness_count": int(nhr_src.get("neg_surface_thickness_count") or 0),
        "add_layer_count": int(nhr_src.get("add_layer_count") or 0),
        "subtract_layer_count": int(nhr_src.get("subtract_layer_count") or 0),
        "low_water_count": int(nhr_src.get("low_water_count") or 0),
        "dltmin_hint_count": int(nhr_src.get("dltmin_hint_count") or 0),
        "exit_code_zero": True if (snp.get("normal_termination") or completed) else None,
        "exit_zero_masks_rollback": bool(exit_zero),
        "dltinter": dltinter,
        "dltmin_s": sched.get("dltmin"),
        "dltmax": sched.get("dltmax"),
        "normal_termination": bool(snp.get("normal_termination")) if snp else None,
        "snp_file": snp.get("file"),
        "snp_n_violations": snp.get("n_violations"),
        "snp_pct_violations": snp.get("pct_violations"),
        "snp_total_iterations": snp.get("total_iterations"),
        "w2_err_present": bool(err.get("present")) if err else False,
        "completed": completed,
        "last_jday": last_jday,
        "window_dlt": window_dlt,
        "neg_events": nhr_src.get("neg_surface_thickness_events") or [],
        "source": "06_PAPER/analysis/nhr_existing_runs.json or nhr_dlt_scan.json (parse_nhr.py)",
    }


def existing_pngs(paths: list[str]) -> list[str]:
    out = []
    for p in paths:
        fp = ROOT / p if not Path(p).is_absolute() else Path(p)
        if fp.exists():
            out.append(rel(fp) or p)
        else:
            out.append(rel(fp) or p.replace("\\", "/"))
    return out


def md_escape(s: Any) -> str:
    return "" if s is None else str(s).replace("|", "\\|")


def fmt_num(x: Any, nd: int = 3) -> str:
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, int) and not isinstance(x, bool):
        return str(x)
    try:
        v = float(x)
    except (TypeError, ValueError):
        return md_escape(x)
    if abs(v) >= 100 or nd == 0:
        return f"{v:.{nd}f}" if nd else f"{v:.0f}"
    return f"{v:.{nd}f}"


def render_markdown(card: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Run-card: {card['title']}")
    lines.append("")
    lines.append(f"- **card_id:** `{card['card_id']}`")
    lines.append(f"- **generated:** {card['generated']}")
    lines.append(f"- **mode:** `{card['mode']}`")
    if card.get("tdgta") is not None:
        lines.append(f"- **TDGTA:** {card['tdgta']}")
    case = card.get("case") or {}
    if case.get("run_dir"):
        lines.append(f"- **run:** `{case['run_dir']}`")
    if card.get("claim"):
        lines.append("")
        lines.append(card["claim"])
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. VPR — variable provenance")
    lines.append("")
    vpr = card.get("vpr") or []
    if vpr:
        lines.append(
            "| caliber | file | column | I | layer | unit | derived from | time support | pairing |"
        )
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for v in vpr:
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_escape(v.get("caliber")),
                        f"`{v.get('file')}`" if v.get("file") else "—",
                        md_escape(v.get("column")),
                        md_escape(v.get("segment")),
                        md_escape(v.get("layer")),
                        md_escape(v.get("unit")),
                        md_escape(v.get("derived_from")),
                        md_escape(v.get("time_support")),
                        md_escape(v.get("pairing_tolerance")),
                    ]
                )
                + " |"
            )
        lines.append("")
        for v in vpr:
            if v.get("notes"):
                lines.append(f"- **{v.get('caliber')}:** {v['notes']}")
        lines.append("")
    else:
        lines.append("_No VPR rows._")
        lines.append("")

    lines.append("## 2. Metrics panel")
    lines.append("")
    panel = card.get("metrics_panel") or {}
    kind = panel.get("kind") or card.get("mode")
    lines.append(f"- **kind:** `{kind}`")
    if panel.get("observation"):
        lines.append(f"- **observation:** {panel['observation']}")
    if panel.get("n"):
        lines.append(f"- **n (paired):** {panel['n']}")
    if panel.get("window"):
        lines.append(f"- **window:** {panel['window']}")
    if panel.get("note"):
        lines.append(f"- **note:** {panel['note']}")
    lines.append("")
    rows = panel.get("calibers") or []
    if rows:
        lines.append("| caliber | n | R² | NSE | KGE | r | α | β | PBIAS | MAE | status |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
        for m in rows:
            pbias = m.get("pbias")
            pbias_s = "—" if pbias is None else f"{pbias:.2f}%"
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_escape(m.get("caliber")),
                        fmt_num(m.get("n"), 0) if m.get("n") is not None else "—",
                        fmt_num(m.get("r2"), 3),
                        fmt_num(m.get("nse"), 3),
                        fmt_num(m.get("kge"), 3),
                        fmt_num(m.get("r"), 3),
                        fmt_num(m.get("alpha"), 3),
                        fmt_num(m.get("beta"), 3),
                        pbias_s,
                        fmt_num(m.get("mae"), 2),
                        md_escape(m.get("status")),
                    ]
                )
                + " |"
            )
        lines.append("")
        extra_bits = []
        for m in rows:
            if m.get("sim_max") is not None:
                extra_bits.append(f"{m['caliber']} sim max={m['sim_max']}")
            if m.get("status") == "file_absent":
                extra_bits.append(f"{m['caliber']}: file absent (`{m.get('file')}`)")
        if extra_bits:
            lines.append("- " + "; ".join(extra_bits))
            lines.append("")
    else:
        lines.append("_No skill metrics (see kind/note)._")
        lines.append("")

    if panel.get("scan_table"):
        lines.append("### DLTMAX × DLTINTER negative-thickness counts")
        lines.append("")
        lines.append("| DLTMAX @ JDAY 30 | DLTINTER=ON | DLTINTER=OFF |")
        lines.append("|---:|---:|---:|")
        for row in panel["scan_table"]:
            lines.append(
                f"| {row['dltmax']} s | {row['inter_on']} | {row['inter_off']} |"
            )
        lines.append("")

    lines.append("## 3. NHR — numerical health")
    lines.append("")
    nhrs = card.get("nhr")
    nhr_list = nhrs if isinstance(nhrs, list) else [nhrs] if nhrs else []
    if nhr_list:
        lines.append(
            "| run | neg thickness | Add | Sub | exit 0 masks rollback | DLTINTER | Normal term | wrn |"
        )
        lines.append("|---|---:|---:|---:|---|---|---|---|")
        for item in nhr_list:
            label = item.get("label") or item.get("case_dir") or "run"
            wrn = item.get("wrn_path") or "—"
            exists = item.get("wrn_exists")
            wrn_s = f"`{wrn}`" if wrn != "—" else "—"
            if exists is False:
                wrn_s += " (missing)"
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_escape(label),
                        str(item.get("neg_surface_thickness_count", "—")),
                        str(item.get("add_layer_count", "—")),
                        str(item.get("subtract_layer_count", "—")),
                        "yes" if item.get("exit_zero_masks_rollback") else "no",
                        md_escape(item.get("dltinter") or "—"),
                        "yes" if item.get("normal_termination") else "no",
                        wrn_s,
                    ]
                )
                + " |"
            )
        lines.append("")
        for item in nhr_list:
            if item.get("window_dlt"):
                w = item["window_dlt"]
                lines.append(
                    f"- **{item.get('label', 'DLT')} window DLT:** "
                    f"min={w.get('dlt_min_s')} s, max={w.get('dlt_max_s')} s "
                    f"({w.get('label', '')})"
                )
            nv = item.get("snp_n_violations")
            if nv is not None:
                lines.append(
                    f"- **{item.get('label', 'SNP')} NV:** {nv} "
                    f"({item.get('snp_pct_violations')}% of NIT="
                    f"{item.get('snp_total_iterations')}); NV is not H1<0 count."
                )
        lines.append("")
        lines.append(
            "NHR fields: negative surface-layer thickness count; Add/Sub layer; "
            "whether exit 0 + Normal termination hid DLTMIN rollback; DLTINTER; "
            "source `w2.wrn` path. Layer add/sub is a geometric threshold event, "
            "not by itself a failure."
        )
        lines.append("")

    notes = card.get("notes") or []
    if notes:
        lines.append("## Notes")
        lines.append("")
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")

    figs = card.get("figures") or []
    if figs:
        lines.append("## Figures (existing, not regenerated)")
        lines.append("")
        for f in figs:
            lines.append(f"- `{f}`")
        lines.append("")

    srcs = card.get("sources") or []
    if srcs:
        lines.append("## Sources")
        lines.append("")
        for s in srcs:
            lines.append(f"- `{s}`")
        lines.append("")

    lines.append(
        "_Generated by `06_PAPER/w2eval/w2eval.py` from cached analysis JSON. "
        "Does not run the W2 executable._"
    )
    lines.append("")
    return "\n".join(lines)


def write_card(card: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    jpath = out_dir / f"{card['card_id']}.json"
    mpath = out_dir / f"{card['card_id']}.md"
    jpath.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    mpath.write_text(render_markdown(card), encoding="utf-8")
    return jpath, mpath


def w3_metric(w3: dict[str, Any], run: str, caliber: str) -> dict[str, Any] | None:
    for m in w3.get("metrics") or []:
        if m.get("run") == run and m.get("caliber") == caliber:
            return m
    return None


def pair_to_row(p: dict[str, Any], caliber: str) -> dict[str, Any]:
    return metric_row(
        caliber=caliber,
        title=p.get("id") or caliber,
        file=f"{(p.get('ref') or {}).get('file')} vs {(p.get('alt') or {}).get('file')}",
        column=f"{(p.get('ref') or {}).get('column')} vs {(p.get('alt') or {}).get('column')}",
        n=p.get("n"),
        r2=p.get("r2"),
        nse=p.get("nse"),
        kge=p.get("kge"),
        r=p.get("r"),
        alpha=p.get("alpha"),
        beta=p.get("beta"),
        pbias=p.get("pbias"),
        mae=p.get("mae"),
        pairing=f"nearest, tol={p.get('align_tol_day')} d",
        extra={"kind": p.get("kind"), "id": p.get("id")},
    )


def vpr_from_series(caliber: str, s: dict[str, Any], tol: str) -> dict[str, Any]:
    return vpr_item(
        caliber=caliber,
        file=s.get("file") or "",
        column=s.get("column") or "",
        segment=s.get("segment"),
        layer=s.get("layer") or "",
        unit=s.get("unit") or "",
        derived_from=s.get("derived_from") or "",
        time_support=s.get("time_support") or "",
        pairing_tolerance=tol,
    )


def build_bonneville_on(ctx: dict[str, Any]) -> dict[str, Any]:
    w3 = ctx["w3"]
    nhr = slim_nhr(find_nhr_case(ctx["nhr_existing"], "run_20260814_bonneville/Bonneville_SYSTDG"))
    nhr["label"] = "TDGTA ON"
    rr = w3.get("reachable_range") or {}
    rows = []
    vprs = [
        vpr_item(
            caliber="A",
            file="c_wdo_76.csv + t_wdo_76.csv",
            column="N2, DO → Henry TDG%",
            segment=76,
            layer="withdrawal mix (WDO)",
            unit="% saturation",
            derived_from="withdrawal.f90 N2+DO Henry conversion (not SYSTDG native TDG)",
            time_support="instantaneous WDO; paired to CCIW hours",
            pairing_tolerance="nearest, tol=0.05 d (eval_bonneville_tailwater.align)",
        ),
        vpr_item(
            caliber="B",
            file="TDGTarget_output.csv",
            column="TDG_TDG",
            segment="tailwater / controller",
            layer="post-control SYSTDG after TDGtarget reallocation",
            unit="% saturation",
            derived_from="TDGtarget.f90 gated file; written only if TDGTA=ON",
            time_support="daily controller output vs CCIW hours",
            pairing_tolerance="nearest, tol=0.6 d (eval_systdg_tdg.py daily pairing)",
            notes="Skill-best series (NSE=+0.50, β≈1, sim max 120.09%). File is controller-gated.",
        ),
        vpr_item(
            caliber="C",
            file="BON_tsr_1_seg40.csv",
            column="TDG",
            segment=40,
            layer="TSR in-reservoir channel",
            unit="% saturation",
            derived_from="native TSR TDG column",
            time_support="instantaneous TSR",
            pairing_tolerance="nearest, tol=0.05 d",
        ),
        vpr_item(
            caliber="S",
            file="TDG_output.csv",
            column="TDG_TDG",
            segment="SYSTDG unit 88888",
            layer="pre-control snapshot",
            unit="% saturation",
            derived_from="systdg.f90 write at first SYSTDG_TDG call of the day (before reallocation)",
            time_support="daily",
            pairing_tolerance="nearest, tol=0.6 d",
            notes="Same filename/column as B but not the same VPR. ON≡OFF (mae=0). Cannot substitute for B.",
        ),
        vpr_item(
            caliber="obs",
            file="CCIW_TDG_Temp_2011-2015.csv",
            column="Total dissolved gas",
            segment="CCIW Cascade Island tailwater",
            layer="n/a (station)",
            unit="% saturation",
            derived_from="example-bundled CWMS extract; W4 vs DART MAE=0.027%",
            time_support="hourly; valid CCIW does not cover the full year",
            pairing_tolerance="see A/C 0.05 d and B/S 0.6 d",
        ),
    ]
    for cal, title in [
        ("A", "N2+DO Henry (seg76)"),
        ("B", "controller TDG_TDG (TDGTarget_output)"),
        ("C", "TSR seg40 TDG"),
        ("S", "SYSTDG native TDG_TDG (TDG_output.csv, pre-control)"),
    ]:
        m = w3_metric(w3, "ON", cal)
        if not m:
            continue
        rows.append(
            metric_row(
                caliber=cal,
                title=title,
                file=m.get("file"),
                n=m.get("n"),
                r2=m.get("r2"),
                nse=m.get("nse"),
                kge=m.get("kge"),
                r=m.get("r"),
                alpha=m.get("alpha"),
                beta=m.get("beta"),
                pbias=m.get("pbias_pct"),
                mae=m.get("mae"),
                pairing=m.get("pairing"),
                extra={
                    "sim_max": m.get("sim_max"),
                    "obs_max": m.get("obs_max"),
                    "slope": m.get("slope"),
                },
            )
        )
    w4 = ctx["w4"]
    hourly = (w4.get("cciw_vs_dart") or {}).get("hourly_tdg") or {}
    spill = w4.get("spill_comparison_2011") or {}
    realloc = spill.get("spill_realloc_days") or {}
    return {
        "card_id": "bonneville_tdgta_on",
        "title": "Bonneville TDGTA ON — three calibers + SYSTDG pre-control snapshot",
        "generated": ctx["generated"],
        "mode": "skill_vs_observations",
        "tdgta": "ON",
        "case": {
            "run_dir": "05_REPRO_RUNS/run_20260814_bonneville/Bonneville_SYSTDG",
            "example": "Bonneville_SYSTDG (v5.0 beta)",
        },
        "claim": (
            "Same run, same CCIW, n=1614. R² stays in 0.508–0.551 while NSE flips "
            "from −2.80 / −2.75 (A, C) to +0.50 (B). B is the controller-gated file, "
            "not a substitute for S (`TDG_output.csv`)."
        ),
        "vpr": vprs,
        "metrics_panel": {
            "kind": "skill_vs_observations",
            "observation": "CCIW Total dissolved gas % (bundled example file)",
            "n": 1614,
            "window": "paired JDAY 40613.58–40681.54 (model window 40544–40910); JDAY 40544=2011-01-01",
            "note": (
                "Obs max 129.1%; 15.55% of paired obs >120%. B sim max 120.09% "
                "(structural cap). S is pre-control (raw max 131.7%) and is not B."
            ),
            "calibers": rows,
            "obs_frac_gt_120": rr.get("obs_frac_gt_120"),
            "controller_cap_pct": rr.get("controller_cap_pct"),
        },
        "nhr": nhr,
        "notes": [
            "Layer add/sub is frequent at Bonneville (seasonal stage) and is not a failure by itself; H1<0 count is 0.",
            f"W4 library CCIW vs DART hourly n={hourly.get('n')}, MAE={hourly.get('mae')}%, "
            f"|Δ|≤0.051 match rate={hourly.get('match_rate_abs_le_0p051')}. Example obs not materially rewritten.",
            f"2011 spill: QGT vs DART r={(spill.get('qgt_vs_dart_spill_kcfs') or {}).get('r')}; "
            f"realloc days C=R n={realloc.get('n')}, DART mean {realloc.get('mean_dart_spill_kcfs')} kcfs "
            f"vs TDGTA {realloc.get('mean_tdgta_spill_kcfs')} kcfs, r={realloc.get('r')}.",
            "Out-of-sample NSE not computed: model ends ~2011; 2016–2025 DART is on disk only.",
        ],
        "figures": existing_pngs(
            [
                "06_PAPER/figures/W3_tdgta_on_off_timeseries.png",
                "06_PAPER/figures/W3_tdgta_on_off_scatter.png",
                "06_PAPER/figures/W3_tdgta_kge_decomposition.png",
                "06_PAPER/analysis/w4_spill_tdgta_vs_dart.png",
            ]
        ),
        "sources": [
            "06_PAPER/analysis/w3_tdgta_off_metrics.json",
            "06_PAPER/analysis/w4_cciw_vs_dart.json",
            "06_PAPER/analysis/nhr_existing_runs.json",
            "00_INDEX/eval_w3_tdgta_off.py",
            "00_INDEX/parse_nhr.py",
        ],
    }


def build_bonneville_off(ctx: dict[str, Any]) -> dict[str, Any]:
    w3 = ctx["w3"]
    nhr = slim_nhr(
        find_nhr_case(ctx["nhr_existing"], "run_20260814_bonneville_notarget/Bonneville_SYSTDG")
    )
    nhr["label"] = "TDGTA OFF"
    rows = []
    for cal, title in [
        ("A", "N2+DO Henry (seg76)"),
        ("B", "controller TDG_TDG (TDGTarget_output) — ABSENT"),
        ("C", "TSR seg40 TDG"),
        ("S", "SYSTDG native TDG_TDG (TDG_output.csv, pre-control)"),
    ]:
        m = w3_metric(w3, "OFF", cal)
        if not m:
            continue
        if not m.get("available"):
            rows.append(
                metric_row(
                    caliber=cal,
                    title=title,
                    file=m.get("file"),
                    available=False,
                    status="file_absent",
                    pairing=m.get("pairing"),
                )
            )
            continue
        rows.append(
            metric_row(
                caliber=cal,
                title=title,
                file=m.get("file"),
                n=m.get("n"),
                r2=m.get("r2"),
                nse=m.get("nse"),
                kge=m.get("kge"),
                r=m.get("r"),
                alpha=m.get("alpha"),
                beta=m.get("beta"),
                pbias=m.get("pbias_pct"),
                mae=m.get("mae"),
                pairing=m.get("pairing"),
                extra={"sim_max": m.get("sim_max"), "obs_max": m.get("obs_max")},
            )
        )
    same = w3.get("on_vs_off_same_file") or {}
    rr = w3.get("reachable_range") or {}
    return {
        "card_id": "bonneville_tdgta_off",
        "title": "Bonneville TDGTA OFF — B file gone; S is pre-control snapshot",
        "generated": ctx["generated"],
        "mode": "skill_vs_observations",
        "tdgta": "OFF",
        "case": {
            "run_dir": "05_REPRO_RUNS/run_20260814_bonneville_notarget/Bonneville_SYSTDG",
            "example": "Bonneville_SYSTDG (TDGTA=OFF, not re-run for W3; already at TMEND)",
        },
        "claim": (
            "Do not write that the physical TDG variable was deleted. SYSTDG still writes "
            "TDG_TDG to TDG_output.csv (ON≡OFF, mae=0). The skill-best / β≈1 / 120.1% series "
            "exists only in TDGTarget_output.csv, which disappears when TDGTA=OFF."
        ),
        "vpr": [
            vpr_item(
                caliber="A",
                file="c_wdo_76.csv + t_wdo_76.csv",
                column="N2, DO → Henry TDG%",
                segment=76,
                layer="withdrawal mix (WDO)",
                unit="% saturation",
                derived_from="same Henry conversion as ON A",
                time_support="instantaneous WDO vs CCIW",
                pairing_tolerance="nearest, tol=0.05 d",
            ),
            vpr_item(
                caliber="B",
                file="TDGTarget_output.csv",
                column="TDG_TDG",
                segment="tailwater / controller",
                layer="post-control (file not written)",
                unit="% saturation",
                derived_from="TDGtarget.f90 InitTDGtarget — not called when TDGTA=OFF",
                time_support="n/a",
                pairing_tolerance="n/a",
                notes="File absent together with TDGTarget_warning.opt.",
            ),
            vpr_item(
                caliber="C",
                file="BON_tsr_1_seg40.csv",
                column="TDG",
                segment=40,
                layer="TSR in-reservoir",
                unit="% saturation",
                derived_from="native TSR; nearly identical to ON C",
                time_support="instantaneous TSR",
                pairing_tolerance="nearest, tol=0.05 d",
            ),
            vpr_item(
                caliber="S",
                file="TDG_output.csv",
                column="TDG_TDG",
                segment="SYSTDG unit 88888",
                layer="pre-control snapshot",
                unit="% saturation",
                derived_from="same write timing as ON S; cannot stand in for B",
                time_support="daily",
                pairing_tolerance="nearest, tol=0.6 d",
            ),
            vpr_item(
                caliber="obs",
                file="CCIW_TDG_Temp_2011-2015.csv",
                column="Total dissolved gas",
                segment="CCIW",
                layer="n/a",
                unit="% saturation",
                derived_from="same observation series as ON card",
                time_support="hourly valid in JDAY 40613–40681",
                pairing_tolerance="see A/C and B/S",
            ),
        ],
        "metrics_panel": {
            "kind": "skill_vs_observations",
            "observation": "CCIW Total dissolved gas %",
            "n": 1614,
            "window": "JDAY 40613–40681 (paired); n=1614",
            "note": (
                f"OFF A NSE=−2.337, paired max {rr.get('OFF_paired_sim_max_by_caliber', {}).get('A')}%. "
                f"OFF S NSE=+0.357, paired max {rr.get('OFF_paired_sim_max_by_caliber', {}).get('S')}%, "
                f"raw max {(rr.get('raw_sim_max') or {}).get('OFF', {}).get('S')}%. "
                "Paired S does not reach obs 129.1%. Turning the controller off does not make A a usable forecast."
            ),
            "calibers": rows,
            "on_vs_off_same_file": {
                "A_mae": (same.get("N2DO_seg76") or {}).get("mae"),
                "C_mae": (same.get("TSR_seg40") or {}).get("mae"),
                "S_mae": (same.get("TDG_output") or {}).get("mae"),
                "S_raw_max": (same.get("TDG_output") or {}).get("off_max"),
            },
        },
        "nhr": nhr,
        "notes": [
            "Disappeared when TDGTA=OFF: TDGTarget_output.csv, TDGTarget_warning.opt only.",
            "ON vs OFF TDG_output.csv mae=0 is a write-timing result, not 'controller has no effect'.",
            f"ON TDG_output vs TDGTarget: MAE={(w3.get('on_TDG_output_vs_TDGTarget') or {}).get('mae')}, "
            f"raw max {(w3.get('on_TDG_output_vs_TDGTarget') or {}).get('s_raw_max')} vs "
            f"{(w3.get('on_TDG_output_vs_TDGTarget') or {}).get('b_raw_max')}.",
        ],
        "figures": existing_pngs(
            [
                "06_PAPER/figures/W3_tdgta_on_off_timeseries.png",
                "06_PAPER/figures/W3_tdgta_on_off_scatter.png",
                "06_PAPER/figures/W3_tdgta_kge_decomposition.png",
            ]
        ),
        "sources": [
            "06_PAPER/analysis/w3_tdgta_off_metrics.json",
            "06_PAPER/analysis/nhr_existing_runs.json",
            "00_INDEX/eval_w3_tdgta_off.py",
            "00_INDEX/parse_nhr.py",
        ],
    }


def build_longlake(ctx: dict[str, Any]) -> dict[str, Any]:
    scan = ctx["nhr_scan"]
    official = find_nhr_case(ctx["nhr_existing"], "run_20260811_fixed/Long Lake")
    dlt20 = find_nhr_case(ctx["nhr_existing"], "run_20260814_longlake_dlt/Long Lake")
    jobs = {j["name"]: j for j in (scan.get("jobs") or []) if "dltmax_" in j.get("name", "")}
    nhr_rows = []
    if official:
        rec = slim_nhr(official)
        rec["label"] = "official baseline (INTER ON, knot 100 s)"
        nhr_rows.append(rec)
    if dlt20:
        rec = slim_nhr(dlt20)
        rec["label"] = "prior DLTMAX=20 INTER ON (run_20260814_longlake_dlt)"
        nhr_rows.append(rec)
    for name, label in [
        ("dltmax_20", "scan INTER ON 20 s"),
        ("dltmax_50", "scan INTER ON 50 s"),
        ("dltmax_100", "scan INTER ON 100 s (official knot)"),
        ("dltmax_200", "scan INTER ON 200 s"),
        ("dltmax_20_interoff", "scan INTER OFF 20 s"),
        ("dltmax_50_interoff", "scan INTER OFF 50 s"),
        ("dltmax_100_interoff", "scan INTER OFF 100 s"),
        ("dltmax_200_interoff", "scan INTER OFF 200 s"),
    ]:
        job = jobs.get(name)
        if not job:
            continue
        rec = slim_nhr(None, scan_job=job)
        rec["label"] = label
        nhr_rows.append(rec)

    scan_table = []
    for dlt in (20, 50, 100, 200):
        onj = jobs.get(f"dltmax_{dlt}") or {}
        offj = jobs.get(f"dltmax_{dlt}_interoff") or {}
        scan_table.append(
            {
                "dltmax": dlt,
                "inter_on": onj.get("neg_surface_thickness_count"),
                "inter_off": offj.get("neg_surface_thickness_count"),
            }
        )
    col_jobs = (scan.get("columbia_scan") or {}).get("jobs") or []
    col_neg = [j.get("neg_surface_thickness_count") for j in col_jobs]

    j20 = jobs.get("dltmax_20") or {}
    win20 = ((j20.get("dlt_trajectory") or {}).get("window") or {})
    return {
        "card_id": "longlake_dlt_nhr",
        "title": "Long Lake official vs DLTMAX scan (DLTINTER ON/OFF)",
        "generated": ctx["generated"],
        "mode": "numerical_health",
        "case": {
            "run_dir": "05_REPRO_RUNS/run_20260815_ll_dlt_scan/",
            "official": "05_REPRO_RUNS/run_20260811_fixed/Long Lake",
            "example": "Long Lake (v4.5.5); HabitatFiles required",
        },
        "claim": (
            "All INTER ON scan points Normal-terminate with exit 0 while wrn still records "
            "1–5 negative-thickness rollbacks. INTER ON counts 5/4/1/5 are non-monotonic "
            "(official 100 s is the valley) but INTER OFF is 0/0/0/0. Do not generalize "
            "'smaller timestep is less stable'. Report NHR: neg-thickness count, whether "
            "exit 0 hid it, and DLTINTER state."
        ),
        "vpr": [
            vpr_item(
                caliber="NHR.wrn",
                file="w2.wrn",
                column="Negative surface layer thickness / Add layer / Subtract layer",
                segment="event segment (typically 3 at Long Lake)",
                layer="KT surface layer H1",
                unit="m (H1, Z); s (DLT)",
                derived_from="w2_4_win.f90 L1415–1424 rollback to DLTMIN; layeraddsub.F90 thresholds",
                time_support="event log (not a water-quality series)",
                pairing_tolerance="n/a",
            ),
            vpr_item(
                caliber="NHR.snp",
                file="snp1.opt",
                column="Total iterations, # of violations (NV), Normal termination",
                segment="n/a",
                layer="n/a",
                unit="count; seconds",
                derived_from="endsimulation.F90; NV includes CFL/viscosity, not just H1<0",
                time_support="end-of-run summary",
                pairing_tolerance="n/a",
            ),
            vpr_item(
                caliber="NHR.tsr_dlt",
                file="tsr_1_seg2.csv",
                column="DLT",
                segment=2,
                layer="n/a",
                unit="s",
                derived_from="TSR output-step sample of DLT; misses single-step DLTMIN rollbacks",
                time_support="TSR dump interval; window JDAY 30–40",
                pairing_tolerance="n/a",
                notes="INTER ON + DLTMAX=20 still has window DLT max ~230 s because day-40 knot is 1800 s.",
            ),
            vpr_item(
                caliber="NHR.con",
                file="w2_con.csv",
                column="NDLT, DLTMIN, DLTINTER, DLTD, DLTMAX, DLTF",
                segment="n/a",
                layer="n/a",
                unit="s",
                derived_from="official schedule; scan edits only DLTMAX at DLTD=30",
                time_support="DLTINTER=ON interpolates between knots (update.F90 L152–163)",
                pairing_tolerance="n/a",
            ),
        ],
        "metrics_panel": {
            "kind": "no_observation_skill",
            "observation": None,
            "note": (
                "Long Lake official example has no independent T/DO/TDG observations. "
                "R²/NSE/KGE/PBIAS/MAE vs field data are not applicable. The evaluation "
                "object is NHR. Columbia DLTMAX 120/360/720 (INTER OFF) neg-thickness "
                f"= {col_neg} — H1<0 is not a cross-case law."
            ),
            "calibers": [],
            "scan_table": scan_table,
            "window_dlt_inter_on_20": {
                "dlt_min_s": win20.get("dlt_min_s"),
                "dlt_max_s": win20.get("dlt_max_s"),
                "label": win20.get("label"),
            },
        },
        "nhr": nhr_rows,
        "notes": [
            "Official DLTINTER=ON: day-30 knot is interpolated toward 1800 s at day 40; tightening DLTMAX to 20 s does not cap window DLT at 20 s.",
            "INTER OFF makes window DLT equal the set cap; all four points have 0 negative-thickness events.",
            "NV (timestep violations) is not the H1<0 count: INTER OFF 20 s has high NV and 0 neg-thickness.",
            "H1<0 observed only at Long Lake among completed Bonneville/Columbia/DeGray runs.",
            (scan.get("verdict") or {}).get("recommendation")
            or "Keep NHR as a required report item.",
        ],
        "figures": existing_pngs(
            [
                "06_PAPER/figures/nhr_dltmax_neg_thickness.png",
                "06_PAPER/figures/nhr_dltmax_layers_dltmin.png",
                "06_PAPER/figures/nhr_dltmax_heatmap.png",
            ]
        ),
        "sources": [
            "06_PAPER/analysis/nhr_dlt_scan.json",
            "06_PAPER/analysis/nhr_existing_runs.json",
            "00_INDEX/parse_nhr.py",
            "00_INDEX/run_ll_dlt_scan.py",
        ],
    }


def build_columbia(ctx: dict[str, Any]) -> dict[str, Any]:
    w1 = ctx["w1"]
    col = w1.get("columbia") or {}
    sod = ctx["w7"]
    series = col.get("series_vpr") or {}
    pairs = {p["id"]: p for p in col.get("pairs") or []}
    wanted = [
        "COL_DO_I45_vs_I49",
        "COL_DO_I45_vs_I33",
        "COL_DO_I49_vs_I33",
        "COL_DO_SNP45_sfc_vs_bot",
    ]
    rows = [pair_to_row(pairs[i], i) for i in wanted if i in pairs]
    nhr = slim_nhr(
        find_nhr_case(ctx["nhr_existing"], "run_20260814_columbia_diag/Columbia Slough Estuary")
    )
    nhr["label"] = "Columbia diag SED_DIAG=ON"
    inst = sod.get("columbia_instantaneous_wet_jday_ge_33") or {}
    vprs = []
    for key, cal in [
        ("TSR_DO_I45", "TSR45"),
        ("TSR_DO_I49", "TSR49"),
        ("TSR_DO_I33", "TSR33"),
        ("SNP_DO_sfc_I45", "SNPsfc"),
        ("SNP_DO_bot_I45", "SNPbot"),
    ]:
        if key in series:
            vprs.append(vpr_from_series(cal, series[key], "0.05 d TSR; 0.15 d SNP"))
    vprs.append(
        vpr_item(
            caliber="SOD",
            file="SedimentDiagenesis/Diagenesis_SOD.csv",
            column="segs 1–51 instantaneous (cols 2–52)",
            segment="wet segments SOD>0",
            layer="sediment–water interface",
            unit="gO2 m-2 d-1",
            derived_from="diagenesis module; W2_diagenesis.npt transplanted from DeGray (31→50)",
            time_support="instantaneous; spin-up JDAY<33 dropped",
            pairing_tolerance="n/a (magnitude check vs Almeida 0.5–3.0 band)",
            notes="NOT Columbia-calibrated. Order-of-magnitude only.",
        )
    )
    return {
        "card_id": "columbia_do_internal",
        "title": "Columbia DO internal consistency + SOD magnitude note",
        "generated": ctx["generated"],
        "mode": "internal_consistency",
        "case": {
            "run_dir": "05_REPRO_RUNS/run_20260814_columbia_diag/Columbia Slough Estuary",
            "run_off": "05_REPRO_RUNS/run_20260811_fixed/Columbia Slough Estuary",
            "example": "Columbia Slough Estuary",
        },
        "claim": (
            "No independent DO observations. Metrics are output-channel disagreement. "
            "I=45 vs 49 NSE=−4.49; the highest-R² pair (49 vs 33, R²=0.65) still has "
            "NSE=−1.48 (α=1.85). Shallow-slough SNP surface vs bottom NSE=0.91 — "
            "wrong station is more dangerous than wrong layer."
        ),
        "vpr": vprs,
        "metrics_panel": {
            "kind": "internal_consistency",
            "observation": None,
            "n": 116,
            "window": "JDAY 32–55 (~0.2 d TSR); SNP snapshots ~1 d (n=24 for SNP pair)",
            "note": (
                "Do not report these NSE/KGE values as calibration skill. "
                "WDO=OFF (no c_wdo). PRF OFF."
            ),
            "calibers": rows,
        },
        "nhr": nhr,
        "notes": [
            (
                f"SOD wet instantaneous JDAY≥33: n={inst.get('n')}, "
                f"mean={inst.get('mean')} gO2/m2/d; "
                f"{inst.get('n_in_band')}/{inst.get('n')} (89.6%) in Almeida 0.5–3.0; "
                f"no point >3.0; ~10.5% <0.5 "
                f"(JSON frac_in_band={inst.get('frac_in_0.5_3.0')}, "
                f"frac_below_0.5={inst.get('frac_below_0.5')})."
            ),
            (sod.get("source") or {}).get("parameter_origin")
            or "Diagenesis parameters transplanted from DeGray.",
            "Almeida & Coelho 2025 scan is a user-specified Portuguese-reservoir experiment, not a global ecological range.",
            "Columbia DLTMAX 120/360/720 s: negative thickness 0/0/0 (see Long Lake card).",
        ],
        "figures": existing_pngs(
            [
                "06_PAPER/figures/w1_columbia_DO_timeseries.png",
                "06_PAPER/figures/w1_columbia_DO_scatter.png",
                "06_PAPER/figures/w1_columbia_DO_kge_bars.png",
                "06_PAPER/figures/w1_columbia_DO_r2_vs_nse.png",
                "06_PAPER/figures/w7_columbia_sod_timeseries.png",
                "06_PAPER/figures/w7_columbia_sod_histogram.png",
            ]
        ),
        "sources": [
            "06_PAPER/analysis/w1_provenance_metrics.json",
            "06_PAPER/analysis/w7_columbia_sod_vs_almeida.json",
            "06_PAPER/analysis/nhr_existing_runs.json",
            "06_PAPER/analysis/w1_w7_provenance.py",
        ],
    }


def build_degray(ctx: dict[str, Any]) -> dict[str, Any]:
    w1 = ctx["w1"]
    dg = w1.get("degray") or {}
    series = dg.get("series_vpr") or {}
    pairs = {p["id"]: p for p in dg.get("pairs") or []}
    wanted = [
        "DG_T2_vs_Tvolavg",
        "DG_T2_vs_WDO",
        "DG_STR115_vs_GATE120",
        "DG_T2_vs_GATE120",
        "DG_T2_vs_PRF26bot",
    ]
    rows = [pair_to_row(pairs[i], i) for i in wanted if i in pairs]
    nhr = slim_nhr(
        find_nhr_case(
            ctx["nhr_existing"],
            "run_20260811_fixed/DeGray Reservoir with sediment diagenesis and vertical algae migration",
        )
    )
    nhr["label"] = "DeGray (no wrn file)"
    vprs = []
    mapping = [
        ("TSR_T2_sfc_I31", "A T2", "0.05 d"),
        ("TSR_Tvolavg", "B Tvolavg", "0.05 d"),
        ("WDO_T_composite_I31", "C WDO", "0.05 d"),
        ("STR_T_elev115_I31", "D STR115", "0.05 d"),
        ("GATE_T_elev120_I31", "E GATE120", "0.05 d"),
        ("PRF_T_sfc_I26", "F PRF sfc", "0.15 d"),
        ("PRF_T_bot_I26", "G PRF bot", "0.15 d"),
    ]
    for key, cal, tol in mapping:
        if key in series:
            vprs.append(vpr_from_series(cal, series[key], tol))
    return {
        "card_id": "degray_t_internal",
        "title": "DeGray temperature internal consistency (no independent observations)",
        "generated": ctx["generated"],
        "mode": "internal_consistency",
        "case": {
            "run_dir": "05_REPRO_RUNS/run_20260811_fixed/DeGray Reservoir with sediment diagenesis and vertical algae migration",
            "example": "DeGray Reservoir with sediment diagenesis and vertical algae migration",
        },
        "claim": (
            "Same TSR file: surface T2 vs volume-average Tvolavg has R²=0.903 and NSE=−0.59 "
            "(α=0.35, β=0.61). STR 115 m vs GATE 120 m: R²=0.534 and NSE=−6.58. "
            "These are provenance disagreements, not skill vs observations."
        ),
        "vpr": vprs,
        "metrics_panel": {
            "kind": "internal_consistency",
            "observation": None,
            "n": 2943,
            "window": "JDAY 64.5–358.7 (1980-03-04 start)",
            "note": (
                "Official example folders contain no independent T/DO observations. "
                "GATE≈T2 is this geometry (gate centerline 120 m near ELWS≈123.8 m); "
                "do not generalize. Parser self-check: SNP surface vs TSR T2 NSE=1.000 at 47 snapshots."
            ),
            "calibers": rows,
        },
        "nhr": nhr,
        "notes": [
            "No w2.wrn (clean run). H1<0 count 0; add/sub layer 0.",
            "R² blind spot appears for correlated-but-wrong-scale channels (volume average, other outlet), not for every wrong layer.",
        ],
        "figures": existing_pngs(
            [
                "06_PAPER/figures/w1_degray_T_timeseries.png",
                "06_PAPER/figures/w1_degray_T_scatter.png",
                "06_PAPER/figures/w1_degray_T_kge_bars.png",
                "06_PAPER/figures/w1_degray_T_r2_vs_nse.png",
            ]
        ),
        "sources": [
            "06_PAPER/analysis/w1_provenance_metrics.json",
            "06_PAPER/analysis/nhr_existing_runs.json",
            "06_PAPER/analysis/w1_w7_provenance.py",
            "00_INDEX/parse_nhr.py",
        ],
    }


def load_context() -> dict[str, Any]:
    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "w1": load_json(ANALYSIS / "w1_provenance_metrics.json"),
        "w3": load_json(ANALYSIS / "w3_tdgta_off_metrics.json"),
        "w4": load_json(ANALYSIS / "w4_cciw_vs_dart.json"),
        "w7": load_json(ANALYSIS / "w7_columbia_sod_vs_almeida.json"),
        "nhr_existing": load_json(ANALYSIS / "nhr_existing_runs.json"),
        "nhr_scan": load_json(ANALYSIS / "nhr_dlt_scan.json"),
    }


def build_all(ctx: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    ctx = ctx or load_context()
    return [
        build_bonneville_on(ctx),
        build_bonneville_off(ctx),
        build_longlake(ctx),
        build_columbia(ctx),
        build_degray(ctx),
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description="Build w2eval run-cards from cached analysis JSON")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory for cards")
    args = ap.parse_args()
    ctx = load_context()
    cards = build_all(ctx)
    written = []
    for card in cards:
        j, m = write_card(card, args.out)
        written.append((j, m))
        print(f"wrote {rel(j)}  {rel(m)}")
    index = {
        "generated": ctx["generated"],
        "n_cards": len(cards),
        "cards": [
            {
                "card_id": c["card_id"],
                "title": c["title"],
                "mode": c["mode"],
                "json": f"{c['card_id']}.json",
                "markdown": f"{c['card_id']}.md",
            }
            for c in cards
        ],
        "note": "MVP reads existing analysis JSON; does not execute w2_v455_ifx.exe.",
    }
    ipath = args.out / "index.json"
    ipath.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {rel(ipath)}  n={len(cards)}")


if __name__ == "__main__":
    main()
