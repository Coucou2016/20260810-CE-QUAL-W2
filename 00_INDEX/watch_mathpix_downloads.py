# -*- coding: utf-8 -*-
"""Watch Downloads for Mathpix zip temps and rename to expected names."""
from __future__ import annotations

import time
import zipfile
from pathlib import Path

DL = Path(r"C:\Users\Administrator\Downloads")

# expected unfinished names -> final names (also detect by zip content)
EXPECTED = [
    "W2LIB-MERGED-FAC-Fact_Sheets_and_Summaries.md.zip",
    "W2LIB-MERGED-DOC-Technical_Documents.md.zip",
    "W2LIB-MERGED-ALL-Corpus.md.zip",
]


def is_zip(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            zf.namelist()
        return True
    except Exception:
        return False


def guess_name(path: Path) -> str | None:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
    except Exception:
        return None
    joined = "\n".join(names).lower()
    # Heuristics from content
    if any("fact" in n.lower() or "summary" in n.lower() for n in names):
        # weak
        pass
    # Prefer matching md filename inside
    for n in names:
        if n.lower().endswith(".md"):
            stem = Path(n).stem.lower()
            if "fac" in stem or "fact" in stem:
                return "W2LIB-MERGED-FAC-Fact_Sheets_and_Summaries.md.zip"
            if "doc" in stem or "technical" in stem or "usgs" in stem:
                return "W2LIB-MERGED-DOC-Technical_Documents.md.zip"
            if "all" in stem or "corpus" in stem:
                return "W2LIB-MERGED-ALL-Corpus.md.zip"
            if "lit" in stem or "literature" in stem:
                return "W2LIB-MERGED-LIT-Literature_and_Reports.md.zip"
    # fallback by size bands if only one pending
    return None


def main(timeout_s: int = 180):
    t0 = time.time()
    seen = {}
    while time.time() - t0 < timeout_s:
        # already present?
        for name in EXPECTED:
            p = DL / name
            if p.exists() and p.stat().st_size > 1000:
                print("have", name, p.stat().st_size)
        tmps = list(DL.glob("*.tmp"))
        for tmp in tmps:
            size = tmp.stat().st_size
            prev = seen.get(tmp.name)
            if prev == size and size > 1000 and is_zip(tmp):
                name = guess_name(tmp)
                if not name:
                    # if only one expected missing, assign it
                    missing = [n for n in EXPECTED if not (DL / n).exists()]
                    if len(missing) == 1:
                        name = missing[0]
                if name:
                    dest = DL / name
                    if dest.exists():
                        dest.unlink()
                    tmp.rename(dest)
                    print("renamed", tmp.name, "->", name, dest.stat().st_size)
                else:
                    print("stable zip but unknown", tmp, size)
            else:
                seen[tmp.name] = size
                print("watching", tmp.name, size)
        if all((DL / n).exists() for n in EXPECTED):
            print("all expected present")
            return
        time.sleep(2)
    print("timeout")


if __name__ == "__main__":
    main()
