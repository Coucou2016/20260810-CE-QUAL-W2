# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")


def strip_data(c: str) -> str:
    return re.sub(r'src="data:[^"]+"', 'src="DATA"', c)


def analyze(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    c = strip_data(raw)
    print("====", path.name, "chars", len(c))
    print("封面 literal", "封面" in c)
    for pat in ["研究报告", "题名页", "封面页", "cover", "作者", "生成时间"]:
        print(" ", pat, c.count(pat) if not pat.isascii() else c.lower().count(pat.lower()))

    h4 = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<h4[^>]*>(.*?)</h4>", c, re.S)]
    print("h4 Counter", Counter(h4))

    # per figure after stripping data
    parts = re.split(r'<div class="fig-title">', c)[1:]
    print("fig parts", len(parts))
    required = {
        "背景与作用": ["背景与作用"],
        "如何阅读": ["如何阅读", "怎么读"],
        "曲线/分量": ["曲线 / 分量含义", "曲线/分量含义", "分量含义"],
        "结论": ["可得出的结论", "结论与理由"],
        "通俗": ["通俗版结论", "通俗结论"],
    }
    short = []
    missing_any = []
    for p in parts:
        title = re.sub(r"<[^>]+>", "", p.split("</div>", 1)[0]).strip()
        # take until next major heading-ish: next fig already split
        chunk = p
        miss = [k for k, names in required.items() if not any(n in chunk for n in names)]
        texts = re.findall(r"<p>(.*?)</p>", chunk, re.S)
        plain = " ".join(re.sub(r"<[^>]+>", "", t) for t in texts)
        if miss:
            missing_any.append((title, miss, len(plain)))
        if len(plain) < 350:
            short.append((title, len(plain), miss))
    print("missing_any", len(missing_any))
    for t, m, n in missing_any[:5]:
        print(" ", t, m, "chars", n)
    print("short<350", len(short))
    for t, n, m in short[:8]:
        print(" ", n, t, m)

    print("pending contexts:")
    for m in re.finditer("待补充", c):
        print(" ", c[max(0, m.start() - 50) : m.start() + 60].replace("\n", " "))

    terms = [
        "NSE",
        "KGE",
        "PBIAS",
        "R²",
        "TDG",
        "SOD",
        "DLTMAX",
        "DLTINTER",
        "DLTMIN",
        "H1(KT",
        "ZMIN",
        "KTMAX",
        "TDGTA",
        "SYSTDG",
        "VPR",
        "NHR",
        "segment",
        "layer",
        "JDAY",
        "forrtl",
        "α",
        "β",
    ]
    for t in terms:
        print(f" term {t}: {t in c}")

    # sample fig1 explanation
    if parts:
        print("--- FIG1 EXPLAIN ---")
        # remove img tag
        body = re.sub(r"<img[^>]*>", "", parts[0])
        # print fig-blocks
        blocks = re.findall(r'<div class="fig-block"><h4>(.*?)</h4><p>(.*?)</p></div>', body, re.S)
        for lab, txt in blocks:
            plain = re.sub(r"<[^>]+>", "", txt)
            print(f"[{lab}] ({len(plain)} chars) {plain[:220]}...")


analyze(ROOT / "06_PAPER" / "report" / "report.html")
print()
analyze(ROOT / "06_PAPER" / "drafts" / "P1_paper.html")
