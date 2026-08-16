# -*- coding: utf-8 -*-
"""Organize Mathpix Markdown zip exports into W2MD library structure."""
from __future__ import annotations

import csv
import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
DL = Path(r"C:\Users\Administrator\Downloads")
MD = ROOT / "04_MARKDOWN"
RAW = MD / "_mathpix_raw"
BY_ALIAS = MD / "by_alias"
BY_CAT = MD / "by_category"
INDEX = ROOT / "00_INDEX"

# Map downloaded zip name patterns -> (alias_stem without W2MD prefix details, category, preferred W2MD filename)
EXPORT_MAP = [
    (
        r"water-16-03556\.md\.zip$",
        "W2MD-LIT-010-mdpi_water_2024_global_applications_ce_qual_w2_eutrophication_review",
        "LIT",
    ),
    (
        r"Basis of the CE-QUAL-W2.*\.md\.zip$",
        "W2MD-LIT-011-wells_cole_basis_of_ce_qual_w2_version_3_river_basin_model",
        "LIT",
    ),
    (
        r"W2LIB-MERGED-REL-Release_Notes\.md\.zip$",
        "W2MD-MERGED-REL-Release_Notes",
        "REL",
    ),
    (
        r"W2LIB-MERGED-EXA-Example_Notes\.md\.zip$",
        "W2MD-MERGED-EXA-Example_Notes",
        "EXA",
    ),
    (
        r"W2LIB-MERGED-FAC-Fact_Sheets_and_Summaries\.md\.zip$",
        "W2MD-MERGED-FAC-Fact_Sheets_and_Summaries",
        "FAC",
    ),
    (
        r"W2LIB-MERGED-DOC-Technical_Documents\.md\.zip$",
        "W2MD-MERGED-DOC-Technical_Documents",
        "DOC",
    ),
    (
        r"W2LIB-MERGED-LIT-Literature_and_Reports\.md\.zip$",
        "W2MD-MERGED-LIT-Literature_and_Reports",
        "LIT",
    ),
    (
        r"W2LIB-MERGED-MAN-User_Manuals\.md\.zip$",
        "W2MD-MERGED-MAN-User_Manuals",
        "MAN",
    ),
    (
        r"W2LIB-MERGED-ALL-Corpus\.md\.zip$",
        "W2MD-MERGED-ALL-Corpus",
        "ALL",
    ),
]


def match_export(name: str):
    for pat, alias, cat in EXPORT_MAP:
        if re.search(pat, name, flags=re.I):
            return alias, cat
    return None


def unpack_and_place(zip_path: Path, alias: str, cat: str) -> dict:
    dest_raw = RAW / alias
    if dest_raw.exists():
        shutil.rmtree(dest_raw)
    dest_raw.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_raw)

    md_files = list(dest_raw.rglob("*.md")) + list(dest_raw.rglob("*.mmd"))
    if not md_files:
        raise RuntimeError(f"No markdown in {zip_path}")
    # Prefer largest md as main body
    main = max(md_files, key=lambda p: p.stat().st_size)

    alias_dir = BY_ALIAS / alias
    if alias_dir.exists():
        shutil.rmtree(alias_dir)
    alias_dir.mkdir(parents=True, exist_ok=True)

    # Copy images next to markdown if present
    images_src = None
    for cand in dest_raw.rglob("images"):
        if cand.is_dir():
            images_src = cand
            break
    out_md = alias_dir / f"{alias}.md"
    text = main.read_text(encoding="utf-8", errors="replace")
    if images_src:
        images_dst = alias_dir / "images"
        shutil.copytree(images_src, images_dst)
        # normalize image paths to ./images/
        text = re.sub(r"\]\((?:\./)?images/", "](./images/", text)
        text = re.sub(r"\]\([^)]+/images/", "](./images/", text)

    header = (
        f"---\n"
        f"alias: {alias}\n"
        f"category: {cat}\n"
        f"source_zip: {zip_path.name}\n"
        f"converted_via: Mathpix Snip\n"
        f"generated_at_utc: {datetime.now(timezone.utc).isoformat()}\n"
        f"---\n\n"
    )
    out_md.write_text(header + text, encoding="utf-8")

    cat_dir = BY_CAT / cat
    cat_dir.mkdir(parents=True, exist_ok=True)
    # also place a copy (or junction-like duplicate file) in category folder
    shutil.copy2(out_md, cat_dir / f"{alias}.md")
    if (alias_dir / "images").exists():
        cat_img = cat_dir / f"{alias}_images"
        if cat_img.exists():
            shutil.rmtree(cat_img)
        shutil.copytree(alias_dir / "images", cat_img)

    return {
        "alias": alias,
        "category": cat,
        "zip": str(zip_path),
        "markdown": str(out_md),
        "bytes": out_md.stat().st_size,
        "images": bool((alias_dir / "images").exists()),
    }


def main():
    BY_ALIAS.mkdir(parents=True, exist_ok=True)
    BY_CAT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)

    # Prefer zips dropped directly into 04_MARKDOWN, then fall back to Downloads.
    zip_sources = [MD, DL]
    zips: list[Path] = []
    for src in zip_sources:
        zips.extend(sorted(src.glob("*.md.zip"), key=lambda p: p.stat().st_mtime, reverse=True))
        # also include oddly named
        zips.extend([p for p in src.glob("*.zip") if "md.zip" in p.name.lower()])

    # Deduplicate while preserving order.
    unique_zips: list[Path] = []
    seen_paths = set()
    for zp in zips:
        key = str(zp.resolve())
        if key in seen_paths:
            continue
        seen_paths.add(key)
        unique_zips.append(zp)
    zips = unique_zips

    results = []
    seen_alias = set()
    for zp in zips:
        m = match_export(zp.name)
        if not m:
            continue
        alias, cat = m
        if alias in seen_alias:
            continue
        seen_alias.add(alias)
        info = unpack_and_place(zp, alias, cat)
        results.append(info)
        print("organized", alias, "->", info["markdown"])

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "items": results,
        "naming": {
            "pdf": "W2LIB-...",
            "markdown": "W2MD-...",
            "rule": "Replace W2LIB prefix with W2MD for converted docs; merged packs use W2MD-MERGED-{CAT}-...",
        },
    }
    (MD / "markdown_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (MD / "markdown_manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
        if results:
            w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            w.writeheader()
            w.writerows(results)

    (MD / "README.md").write_text(
        f"""# CE-QUAL-W2 Markdown 库（Mathpix 导出）

- `by_alias/`：按 **W2MD** 假名归档的 Markdown（含 images）
- `by_category/`：按分类副本（LIT/DOC/FAC/EXA/REL/MAN/ALL）
- `_mathpix_raw/`：Mathpix 原始解压内容
- `markdown_manifest.csv`：清单

已整理：{len(results)} 份  
生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}
""",
        encoding="utf-8",
    )
    print("TOTAL", len(results))


if __name__ == "__main__":
    main()
