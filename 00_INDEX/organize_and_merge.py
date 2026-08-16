# -*- coding: utf-8 -*-
"""Organize CE-QUAL-W2 downloads and merge PDFs by category under W2LIB alias scheme."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
RAW = ROOT / "01_RAW_DOWNLOADS"
EXTRACT = RAW / "_extract"
LIB = ROOT / "02_LIBRARY"
MERGED = ROOT / "03_MERGED_PDF"
INDEX = ROOT / "00_INDEX"

# Corpus alias / 假名体系：后续 PDF→Markdown 统一用同一 ID
#   W2LIB-{CAT}-{NNN}-{slug}.pdf   原始归档名
#   W2MD-{CAT}-{NNN}-{slug}.md     未来 Markdown 目标名
CORPUS_ALIAS = "W2LIB"
MD_ALIAS = "W2MD"

CAT_DIRS = {
    "MAN": LIB / "01_manuals",
    "DOC": LIB / "02_tech_docs",
    "LIT": LIB / "03_literature",
    "FAC": LIB / "04_factsheets",
    "EXA": LIB / "10_misc_pdf",  # example-only PDFs live with misc classified PDF
    "REL": LIB / "09_release_notes",
}

MERGE_ORDER = ["MAN", "DOC", "LIT", "FAC", "EXA", "REL"]
MERGE_TITLES = {
    "MAN": "User Manuals",
    "DOC": "Technical Documents",
    "LIT": "Literature and Reports",
    "FAC": "Fact Sheets and Summaries",
    "EXA": "Example Notes",
    "REL": "Release Notes",
}


@dataclass
class Item:
    alias: str
    md_target: str
    cat: str
    seq: int
    slug: str
    title: str
    source_path: str
    library_path: str
    sha256: str
    bytes: int
    pages: int | None
    notes: str = ""


def slugify(name: str, maxlen: int = 70) -> str:
    # Avoid Path().stem — names like V4.5.5 are truncated to V4.5
    s = name[:-4] if name.lower().endswith(".pdf") else name
    s = re.sub(r"[^\w\-]+", "_", s, flags=re.UNICODE)
    s = re.sub(r"_+", "_", s).strip("_")
    return (s[:maxlen] or "doc").lower()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path: Path) -> int | None:
    try:
        return len(PdfReader(str(path)).pages)
    except Exception:
        return None


def copy_named(src: Path, cat: str, seq: int, title: str, notes: str = "") -> Item:
    slug = slugify(title or src.name)
    alias = f"{CORPUS_ALIAS}-{cat}-{seq:03d}-{slug}"
    md_target = f"{MD_ALIAS}-{cat}-{seq:03d}-{slug}.md"
    dest_dir = CAT_DIRS[cat]
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{alias}{src.suffix.lower()}"
    shutil.copy2(src, dest)
    digest = sha256_file(dest)
    return Item(
        alias=alias,
        md_target=md_target,
        cat=cat,
        seq=seq,
        slug=slug,
        title=title,
        source_path=str(src),
        library_path=str(dest),
        sha256=digest,
        bytes=dest.stat().st_size,
        pages=pdf_pages(dest) if dest.suffix.lower() == ".pdf" else None,
        notes=notes,
    )


def robocopy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def merge_pdfs(paths: list[Path], out: Path, bookmark_titles: list[str]) -> dict:
    writer = PdfWriter()
    used = 0
    skipped: list[str] = []
    for path, title in zip(paths, bookmark_titles):
        try:
            reader = PdfReader(str(path))
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    skipped.append(str(path))
                    continue
            start = len(writer.pages)
            for page in reader.pages:
                writer.add_page(page)
            writer.add_outline_item(title, start)
            used += 1
        except (PdfReadError, Exception) as exc:
            skipped.append(f"{path} ({exc})")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as f:
        writer.write(f)
    return {"files_merged": used, "pages": len(writer.pages), "skipped": skipped, "out": str(out)}


def main() -> None:
    items: list[Item] = []
    counters = {k: 1 for k in CAT_DIRS}

    v455 = EXTRACT / "v455"
    v5 = EXTRACT / "v5"
    gh = EXTRACT / "github-v45" / "CE-QUAL-W2-4.5"

    # --- Manuals (prefer V4.5.5 package; also keep V5 beta + public Part1 rev9) ---
    man_specs = [
        (v455 / "User Manual" / "W2manual455_Part1_Intro_rev0.pdf", "V4.5.5 User Manual Part1 Intro"),
        (v455 / "User Manual" / "W2manual455_Part2_Theory_rev0.pdf", "V4.5.5 User Manual Part2 Theory"),
        (v455 / "User Manual" / "W2manual455_Part3_InputOutputFiles_rev1.pdf", "V4.5.5 User Manual Part3 InputOutput"),
        (v455 / "User Manual" / "W2manual455_Part4_ModelExamples_rev0.pdf", "V4.5.5 User Manual Part4 Examples"),
        (v455 / "User Manual" / "W2manual455_Part5_ModelUtilities_rev1.pdf", "V4.5.5 User Manual Part5 Utilities"),
        (RAW / "W2manual45_Part1_Intro_rev9.pdf", "Public Part1 Intro rev9 (PSU web)"),
        (v5 / "Documentation" / "W2manual5Beta_Part1_Intro_rev6.pdf", "V5.0 Beta Manual Part1 Intro"),
        (v5 / "Documentation" / "W2manual5Beta_Part2_Theory_rev6.pdf", "V5.0 Beta Manual Part2 Theory"),
        (v5 / "Documentation" / "W2manual5Beta_Part3_InputOutputFiles_rev6.pdf", "V5.0 Beta Manual Part3 InputOutput"),
        (v5 / "Documentation" / "W2manual5Beta_Part4_ModelExamples_rev3.pdf", "V5.0 Beta Manual Part4 Examples"),
        (v5 / "Documentation" / "W2manual5Beta_Part5_ModelUtilities_rev6.pdf", "V5.0 Beta Manual Part5 Utilities"),
    ]
    for src, title in man_specs:
        if src.exists():
            items.append(copy_named(src, "MAN", counters["MAN"], title, "manual"))
            counters["MAN"] += 1

    # --- Tech docs ---
    doc_specs = [
        (v455 / "USGS documentation for using USGS Auto Port Selection Algorithm" / "USGS Report on Improved Algorithms_ofr2015-1027.pdf",
         "USGS OFR 2015-1027 Auto Port Selection"),
        (v455 / "Control File Converter" / "ControlFIleConverter4.5.pdf", "Control File Converter 4.5 Guide"),
        (v455 / "W2tools post-processor" / "W2_Post_Quick_Guide (Rev03).pdf", "W2Tools Post-Processor Quick Guide"),
        (v5 / "Documentation" / "Mercury_Theory_Model_Dec2023_PSU.pdf", "V5 Mercury Theory Model Dec2023"),
        (v5 / "Documentation" / "W2 TN Selective Withdrawl_Jan2024.pdf", "V5 TN Selective Withdrawal Jan2024"),
    ]
    for src, title in doc_specs:
        if src.exists():
            items.append(copy_named(src, "DOC", counters["DOC"], title, "tech_doc"))
            counters["DOC"] += 1

    # --- Literature / research reports bundled with model ---
    lit_specs = [
        (v455 / "Sediment diagenesis documentation" / "CEMA Oil Sands Pit Lake Model May 2011.pdf",
         "CEMA Oil Sands Pit Lake Model May 2011"),
        (v455 / "Sediment diagenesis documentation" / "Prakash Vandenberg Buchak 2014 Sediment Diagenesis Part 2.pdf",
         "Prakash et al. 2014 Sediment Diagenesis Part2"),
        (v455 / "Sediment diagenesis documentation" / "Updating the CEMA OSPLM Report Aug2014.pdf",
         "Updating CEMA OSPLM Report Aug2014"),
    ]
    for src, title in lit_specs:
        if src.exists():
            items.append(copy_named(src, "LIT", counters["LIT"], title, "bundled_report"))
            counters["LIT"] += 1

    # Literature wishlist (blocked remote downloads) as markdown note only
    wishlist = INDEX / "literature_wishlist.md"
    wishlist.write_text(
        """# Literature wishlist (download blocked or paywalled)

以下文献本次未能自动下载（HTTP 403/404），请手动放入 `02_LIBRARY/03_literature/` 后按 `W2LIB-LIT-xxx-slug.pdf` 命名，并更新 `manifest.csv`。

| 建议假名 | 文献 | URL |
|---|---|---|
| W2LIB-LIT-010-mdpi_water_2024_eutrophication_review | Global Applications of CE-QUAL-W2 in Reservoir Eutrophication (MDPI Water 2024) | https://www.mdpi.com/2073-4441/16/24/3556/pdf |
| W2LIB-LIT-011-wells_cole_basis_v3 | Basis of CE-QUAL-W2 Version 3 (PDXScholar) | https://pdxscholar.library.pdx.edu/cgi/viewcontent.cgi?article=1112&context=cengin_fac |
| W2LIB-LIT-012-cole_wells_usermanual_classic | Cole & Wells official manuals (historical) | https://cee.pdx.edu/w2/ |

转换 Markdown 时：目标文件名 = 将 `W2LIB` 替换为 `W2MD`，扩展名改为 `.md`。
""",
        encoding="utf-8",
    )

    # --- Fact sheets / summaries ---
    fac_specs = [
        (gh / "CE-QUAL-W2_Version_4.5_Summary.pdf", "CE-QUAL-W2 Version 4.5 Summary"),
        (gh / "fact-sheets" / "images" / "Graphical-Abstract.pdf", "Graphical Abstract"),
    ]
    for src, title in fac_specs:
        if src.exists():
            items.append(copy_named(src, "FAC", counters["FAC"], title, "factsheet"))
            counters["FAC"] += 1

    # --- Example PDFs ---
    exa = v455 / "Examples" / "BonnevilleDam with TDG computed using SYSTDG" / "BonnevilleDamSYSTDG.pdf"
    if exa.exists():
        items.append(copy_named(exa, "EXA", counters["EXA"], "Bonneville Dam SYSTDG Example Note", "example_pdf"))
        counters["EXA"] += 1

    # --- Release notes ---
    rel_specs = [
        (RAW / "bug_fixes_updates.pdf", "Bug Fixes and Updates (legacy index)"),
        (RAW / "W2_Version_3.6_Release_Notes.pdf", "Version 3.6 Release Notes"),
    ]
    for src, title in rel_specs:
        if src.exists():
            items.append(copy_named(src, "REL", counters["REL"], title, "release_note"))
            counters["REL"] += 1

    # --- Non-PDF bulk assets ---
    robocopy_tree(v455 / "Source codes", LIB / "05_source" / "v4.5.5")
    if (v5 / "Source code").exists():
        robocopy_tree(v5 / "Source code", LIB / "05_source" / "v5.0_beta")
    if (gh / "src").exists():
        robocopy_tree(gh / "src", LIB / "05_source" / "github_v4.5")

    robocopy_tree(v455 / "Examples", LIB / "06_examples" / "v4.5.5")
    if (v5 / "Examples").exists():
        robocopy_tree(v5 / "Examples", LIB / "06_examples" / "v5.0_beta")

    robocopy_tree(v455 / "Executables", LIB / "07_executables" / "v4.5.5")
    if (v5 / "Executable").exists():
        robocopy_tree(v5 / "Executable", LIB / "07_executables" / "v5.0_beta")

    for name in [
        "Control File Converter",
        "Excel macro utility for writing files in W2 format from Excel",
        "Waterbalance",
        "W2tools post-processor",
        "Sediment diagenesis documentation",
        "USGS documentation for using USGS Auto Port Selection Algorithm",
    ]:
        src = v455 / name
        if src.exists():
            robocopy_tree(src, LIB / "08_utilities" / slugify(name, 80))

    # Copy useful markdown/text from github into factsheets/docs area
    for md_name in [
        "README.md",
        "FAQ.md",
        "CE-QUAL-W2_Version_4.5_Summary.md",
        "CE-QUAL-W2_Model_Application_History.md",
        "LICENSE.md",
    ]:
        src = gh / md_name
        if src.exists():
            dest = LIB / "04_factsheets" / f"W2LIB-FAC-MD-{slugify(md_name)}.md"
            shutil.copy2(src, dest)

    # --- Merge PDFs by category ---
    merge_report = []
    by_cat: dict[str, list[Item]] = {k: [] for k in MERGE_ORDER}
    for it in items:
        if it.cat in by_cat:
            by_cat[it.cat].append(it)

    for cat in MERGE_ORDER:
        group = sorted(by_cat[cat], key=lambda x: x.seq)
        if not group:
            continue
        paths = [Path(x.library_path) for x in group]
        titles = [f"{x.alias} | {x.title}" for x in group]
        out = MERGED / f"{CORPUS_ALIAS}-MERGED-{cat}-{MERGE_TITLES[cat].replace(' ', '_')}.pdf"
        info = merge_pdfs(paths, out, titles)
        info["cat"] = cat
        info["aliases"] = [x.alias for x in group]
        merge_report.append(info)

    # Super-merge of all classified PDFs (optional archive)
    all_items = sorted(items, key=lambda x: (MERGE_ORDER.index(x.cat) if x.cat in MERGE_ORDER else 99, x.seq))
    if all_items:
        info = merge_pdfs(
            [Path(x.library_path) for x in all_items],
            MERGED / f"{CORPUS_ALIAS}-MERGED-ALL-Corpus.pdf",
            [f"{x.alias} | {x.title}" for x in all_items],
        )
        info["cat"] = "ALL"
        info["aliases"] = [x.alias for x in all_items]
        merge_report.append(info)

    # --- Manifest / naming schema ---
    manifest_rows = [asdict(x) for x in items]
    with (INDEX / "manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
        if manifest_rows:
            w = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
            w.writeheader()
            w.writerows(manifest_rows)

    schema = {
        "corpus_alias": CORPUS_ALIAS,
        "markdown_alias": MD_ALIAS,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "naming_rule": {
            "pdf_archive": "W2LIB-{CAT}-{NNN}-{slug}.pdf",
            "markdown_target": "W2MD-{CAT}-{NNN}-{slug}.md",
            "merged_by_category": "W2LIB-MERGED-{CAT}-{Title}.pdf",
            "categories": {
                "MAN": "User manuals",
                "DOC": "Technical documents / tool guides",
                "LIT": "Literature and research reports",
                "FAC": "Fact sheets / summaries",
                "EXA": "Example notes (PDF)",
                "REL": "Release notes / bugfix logs",
            },
            "conversion_hint": "Replace prefix W2LIB→W2MD and extension .pdf→.md; keep CAT-NNN-slug unchanged.",
        },
        "source_packages": {
            "v455.zip": "PSU CE-QUAL-W2 Version 4.5.5 official package",
            "v5.zip": "PSU CE-QUAL-W2 Version 5.0 Beta package",
            "CE-QUAL-W2-v4.5-github.zip": "GitHub CE-QUAL-W2-ERDC/CE-QUAL-W2 branch v4.5",
        },
        "items": manifest_rows,
        "merge_report": merge_report,
    }
    (INDEX / "naming_schema.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")

    readme = INDEX / "README_NAMING.md"
    readme.write_text(
        f"""# W2LIB 假名体系（Corpus Alias）

统一代号：**`{CORPUS_ALIAS}`**  
未来 Markdown 代号：**`{MD_ALIAS}`**

## 命名规则

| 用途 | 模式 | 示例 |
|---|---|---|
| 单份 PDF 归档 | `W2LIB-{{CAT}}-{{NNN}}-{{slug}}.pdf` | `W2LIB-MAN-001-w2manual455_part1_intro_rev0.pdf` |
| 转 Markdown 目标 | `W2MD-{{CAT}}-{{NNN}}-{{slug}}.md` | `W2MD-MAN-001-w2manual455_part1_intro_rev0.md` |
| 分类合并 PDF | `W2LIB-MERGED-{{CAT}}-{{Title}}.pdf` | `W2LIB-MERGED-MAN-User_Manuals.pdf` |
| 全库合并 | `W2LIB-MERGED-ALL-Corpus.pdf` | 见 `03_MERGED_PDF/` |

## 分类代码 CAT

- **MAN** 用户手册
- **DOC** 技术文档 / 工具说明
- **LIT** 文献与研究报告
- **FAC** 简介 / Fact sheet / Summary
- **EXA** 算例说明 PDF
- **REL** 版本说明 / Bugfix

## 目录结构

```
00_INDEX/           假名规则、manifest、本说明
01_RAW_DOWNLOADS/   原始 zip 与零散下载
02_LIBRARY/         分类后的资料（含源码/算例/可执行文件）
03_MERGED_PDF/      按分类合并后的 PDF（便于备份）
```

## PDF → Markdown 建议流程

1. 读取 `manifest.csv`（每行一个 `alias` / `md_target` / `library_path`）
2. 对 `library_path` 做 OCR/文本抽取
3. 输出到例如 `04_MARKDOWN/{{md_target}}`
4. 保持 `CAT-NNN-slug` 不变，仅前缀 `W2LIB`→`W2MD`

生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}
""",
        encoding="utf-8",
    )

    print(f"PDF items archived: {len(items)}")
    for it in items:
        print(f"  {it.alias}  pages={it.pages}  {it.title}")
    print("Merges:")
    for m in merge_report:
        print(f"  {m['cat']}: files={m['files_merged']} pages={m['pages']} -> {m['out']}")
        if m["skipped"]:
            print(f"    skipped: {m['skipped']}")


if __name__ == "__main__":
    main()
