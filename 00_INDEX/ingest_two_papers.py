# -*- coding: utf-8 -*-
from pathlib import Path
import re, csv, json, shutil, hashlib
from datetime import datetime, timezone
from pypdf import PdfReader, PdfWriter

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
LIT = ROOT / "02_LIBRARY" / "03_literature"
MERGED = ROOT / "03_MERGED_PDF"
INDEX = ROOT / "00_INDEX"
LIT.mkdir(parents=True, exist_ok=True)


def slugify(name, maxlen=70):
    s = name[:-4] if name.lower().endswith(".pdf") else name
    s = re.sub(r"[^\w\-]+", "_", s, flags=re.UNICODE)
    s = re.sub(r"_+", "_", s).strip("_")
    return (s[:maxlen] or "doc").lower()


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


news = [
    (
        Path(r"c:\Users\Administrator\Downloads\water-16-03556.pdf"),
        "MDPI Water 2024 Global Applications CE-QUAL-W2 Eutrophication Review",
        10,
    ),
    (
        Path(
            r"c:\Users\Administrator\Downloads\Basis of the CE-QUAL-W2 Version 3 River Basin Hydrodynamic and Wa.pdf"
        ),
        "Wells Cole Basis of CE-QUAL-W2 Version 3 River Basin Model",
        11,
    ),
]

rows = list(csv.DictReader((INDEX / "manifest.csv").open(encoding="utf-8-sig")))

for src, title, seq in news:
    assert src.exists(), src
    slug = slugify(title)
    alias = f"W2LIB-LIT-{seq:03d}-{slug}"
    md_target = f"W2MD-LIT-{seq:03d}-{slug}.md"
    dest = LIT / f"{alias}.pdf"
    shutil.copy2(src, dest)
    pages = len(PdfReader(str(dest)).pages)
    rows = [r for r in rows if not (r["cat"] == "LIT" and int(r["seq"]) == seq)]
    row = {
        "alias": alias,
        "md_target": md_target,
        "cat": "LIT",
        "seq": str(seq),
        "slug": slug,
        "title": title,
        "source_path": str(src),
        "library_path": str(dest),
        "sha256": sha(dest),
        "bytes": str(dest.stat().st_size),
        "pages": str(pages),
        "notes": "user_provided_download",
    }
    rows.append(row)
    print("added", alias, "pages", pages)

order = {"MAN": 0, "DOC": 1, "LIT": 2, "FAC": 3, "EXA": 4, "REL": 5}
rows.sort(key=lambda r: (order.get(r["cat"], 9), int(r["seq"])))
with (INDEX / "manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)


def merge(group, out: Path):
    writer = PdfWriter()
    for r in group:
        reader = PdfReader(r["library_path"])
        start = len(writer.pages)
        for p in reader.pages:
            writer.add_page(p)
        title = r["alias"] + " | " + r["title"]
        writer.add_outline_item(title, start)
    with out.open("wb") as f:
        writer.write(f)
    print("merged", out.name, "pages", len(writer.pages), "files", len(group))


lit_rows = sorted([r for r in rows if r["cat"] == "LIT"], key=lambda r: int(r["seq"]))
merge(lit_rows, MERGED / "W2LIB-MERGED-LIT-Literature_and_Reports.pdf")
merge(rows, MERGED / "W2LIB-MERGED-ALL-Corpus.pdf")

schema = json.loads((INDEX / "naming_schema.json").read_text(encoding="utf-8"))
schema["items"] = rows
schema["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
(INDEX / "naming_schema.json").write_text(
    json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8"
)

(INDEX / "literature_wishlist.md").write_text(
    """# Literature wishlist status

已入库（用户提供）：
- W2LIB-LIT-010-mdpi_water_2024_global_applications_ce_qual_w2_eutrophication_review.pdf
- W2LIB-LIT-011-wells_cole_basis_of_ce_qual_w2_version_3_river_basin_model.pdf
""",
    encoding="utf-8",
)
print("done")
