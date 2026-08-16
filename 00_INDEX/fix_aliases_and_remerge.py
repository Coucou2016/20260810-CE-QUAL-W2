# -*- coding: utf-8 -*-
from pathlib import Path
import re, csv, json
from datetime import datetime, timezone
from pypdf import PdfReader, PdfWriter

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
LIB = ROOT / "02_LIBRARY"
MERGED = ROOT / "03_MERGED_PDF"
INDEX = ROOT / "00_INDEX"


def slugify(name: str, maxlen: int = 70) -> str:
    s = name
    if s.lower().endswith(".pdf"):
        s = s[:-4]
    s = re.sub(r"[^\w\-]+", "_", s, flags=re.UNICODE)
    s = re.sub(r"_+", "_", s).strip("_")
    return (s[:maxlen] or "doc").lower()


rows = list(csv.DictReader((INDEX / "manifest.csv").open(encoding="utf-8-sig")))

CAT_DIRS = {
    "MAN": LIB / "01_manuals",
    "DOC": LIB / "02_tech_docs",
    "LIT": LIB / "03_literature",
    "FAC": LIB / "04_factsheets",
    "EXA": LIB / "10_misc_pdf",
    "REL": LIB / "09_release_notes",
}

new_rows = []
for r in rows:
    cat = r["cat"]
    seq = int(r["seq"])
    title = r["title"]
    old = Path(r["library_path"])
    slug = slugify(title)
    alias = f"W2LIB-{cat}-{seq:03d}-{slug}"
    md_target = f"W2MD-{cat}-{seq:03d}-{slug}.md"
    dest = CAT_DIRS[cat] / f"{alias}.pdf"
    if old.exists() and old.resolve() != dest.resolve():
        if dest.exists():
            dest.unlink()
        old.rename(dest)
    elif not dest.exists():
        candidates = list(CAT_DIRS[cat].glob(f"W2LIB-{cat}-{seq:03d}-*.pdf"))
        if candidates:
            if dest.exists():
                dest.unlink()
            candidates[0].rename(dest)
    r["alias"] = alias
    r["md_target"] = md_target
    r["slug"] = slug
    r["library_path"] = str(dest)
    new_rows.append(r)
    print(alias)

with (INDEX / "manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(new_rows[0].keys()))
    w.writeheader()
    w.writerows(new_rows)

schema = json.loads((INDEX / "naming_schema.json").read_text(encoding="utf-8"))
schema["items"] = new_rows
schema["generated_at_utc"] = datetime.now(timezone.utc).isoformat()

MERGE_ORDER = ["MAN", "DOC", "LIT", "FAC", "EXA", "REL"]
MERGE_TITLES = {
    "MAN": "User_Manuals",
    "DOC": "Technical_Documents",
    "LIT": "Literature_and_Reports",
    "FAC": "Fact_Sheets_and_Summaries",
    "EXA": "Example_Notes",
    "REL": "Release_Notes",
}
by = {k: [] for k in MERGE_ORDER}
for r in new_rows:
    by[r["cat"]].append(r)


def merge(paths, titles, out):
    writer = PdfWriter()
    for path, title in zip(paths, titles):
        reader = PdfReader(str(path))
        start = len(writer.pages)
        for p in reader.pages:
            writer.add_page(p)
        writer.add_outline_item(title, start)
    with open(out, "wb") as f:
        writer.write(f)
    return len(writer.pages)


merge_report = []
for cat in MERGE_ORDER:
    group = sorted(by[cat], key=lambda x: int(x["seq"]))
    if not group:
        continue
    out = MERGED / f"W2LIB-MERGED-{cat}-{MERGE_TITLES[cat]}.pdf"
    pages = merge(
        [Path(x["library_path"]) for x in group],
        [f"{x['alias']} | {x['title']}" for x in group],
        out,
    )
    merge_report.append({"cat": cat, "files_merged": len(group), "pages": pages, "out": str(out)})
    print("merged", cat, pages)

all_items = sorted(new_rows, key=lambda x: (MERGE_ORDER.index(x["cat"]), int(x["seq"])))
out = MERGED / "W2LIB-MERGED-ALL-Corpus.pdf"
pages = merge(
    [Path(x["library_path"]) for x in all_items],
    [f"{x['alias']} | {x['title']}" for x in all_items],
    out,
)
merge_report.append({"cat": "ALL", "files_merged": len(all_items), "pages": pages, "out": str(out)})
schema["merge_report"] = merge_report
(INDEX / "naming_schema.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")

# also patch organize script slugify for future runs
org = INDEX / "organize_and_merge.py"
text = org.read_text(encoding="utf-8")
old = '''def slugify(name: str, maxlen: int = 60) -> str:
    s = Path(name).stem
    s = re.sub(r"[^\\w\\-]+", "_", s, flags=re.UNICODE)
    s = re.sub(r"_+", "_", s).strip("_")
    return (s[:maxlen] or "doc").lower()'''
new = '''def slugify(name: str, maxlen: int = 70) -> str:
    # Avoid Path().stem — names like V4.5.5 are truncated to V4.5
    s = name[:-4] if name.lower().endswith(".pdf") else name
    s = re.sub(r"[^\\w\\-]+", "_", s, flags=re.UNICODE)
    s = re.sub(r"_+", "_", s).strip("_")
    return (s[:maxlen] or "doc").lower()'''
if old in text:
    org.write_text(text.replace(old, new), encoding="utf-8")
    print("patched organize_and_merge.py")
else:
    print("organize script slugify not patched (pattern mismatch)")

print("ALL pages", pages)
print("done")
