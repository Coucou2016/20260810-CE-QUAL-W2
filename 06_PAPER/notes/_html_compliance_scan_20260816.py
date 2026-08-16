# -*- coding: utf-8 -*-
"""Hard compliance scan for P1_paper.html and report.html."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "06_PAPER" / "drafts" / "P1_paper.html",
    ROOT / "06_PAPER" / "report" / "report.html",
]
CDN_PATTERNS = [
    r"echarts",
    r"plotly",
    r"\bd3\.",
    r"mathjax",
    r"fonts\.googleapis",
    r"cdn\.jsdelivr",
    r"unpkg\.com",
    r"cdnjs",
]
SECTION_KEYS = [
    "封面",
    "目录",
    "摘要",
    "研究背景",
    "数据与方法",
    "研究过程",
    "结果",
    "分析与讨论",
    "主要结论",
    "不足与展望",
]
TERM_KEYS = [
    "NSE",
    "KGE",
    "PBIAS",
    "R²",
    "TDG",
    "SOD",
    "DLTMAX",
    "DLTINTER",
    "DLTMIN",
    "H1",
    "ZMIN",
    "KT",
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
FIG_HEADINGS = [
    "背景与作用",
    "如何阅读",
    "怎么读",
    "曲线",
    "分量含义",
    "可得出的结论",
    "通俗",
]


def scan(path: Path) -> dict:
    c = path.read_text(encoding="utf-8", errors="replace")
    imgs = re.findall(r"<img\b[^>]*>", c, flags=re.I)
    srcs = []
    for tag in imgs:
        m = re.search(r'src=["\']([^"\']+)["\']', tag, flags=re.I)
        srcs.append(m.group(1) if m else "")
    https_all = re.findall(r"https://[^\s\"'<>]+", c)
    # exclude data URLs that embed matplotlib attribution with https inside base64? count literal https:// outside base64 is hard;
    # report raw count and sample non-base64 contexts
    https_outside_img = []
    for m in re.finditer(r"https://[^\s\"'<>]+", c):
        start = max(0, m.start() - 40)
        ctx = c[start : m.start()]
        if "base64," in ctx[-40:]:
            continue
        # skip if inside a long data URI
        prev = c[max(0, m.start() - 200) : m.start()]
        if "data:image" in prev and "base64" in prev:
            continue
        https_outside_img.append(m.group(0)[:80])

    fig_blocks = len(re.findall(r'class="fig(?:-block|-title|)"', c))
    fig_titles = re.findall(r'class="fig-title"[^>]*>(.*?)</div>', c, flags=re.S)
    h4s = re.findall(r"<h4[^>]*>(.*?)</h4>", c, flags=re.S)
    h4_text = [re.sub(r"<[^>]+>", "", h).strip() for h in h4s]

    out = {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "size_mb": round(path.stat().st_size / 1e6, 3),
        "DOCTYPE": bool(re.search(r"<!DOCTYPE\s+html", c, re.I)),
        "html": bool(re.search(r"<html\b", c, re.I)),
        "head": bool(re.search(r"<head\b", c, re.I)),
        "style": bool(re.search(r"<style\b", c, re.I)),
        "body": bool(re.search(r"<body\b", c, re.I)),
        "charset_utf8": bool(re.search(r'charset\s*=\s*["\']?utf-8', c, re.I)),
        "img_count": len(imgs),
        "src_data": sum(1 for s in srcs if s.startswith("data:")),
        "src_dotdot": sum(1 for s in srcs if s.startswith("../")),
        "src_dot": sum(1 for s in srcs if s.startswith("./")),
        "src_http": sum(1 for s in srcs if s.startswith("http")),
        "src_other": [s[:60] for s in srcs if not s.startswith("data:")],
        "table_count": len(re.findall(r"<table\b", c, re.I)),
        "max_width_100": len(re.findall(r"max-width\s*:\s*100%", c)),
        "chinese_font": bool(
            re.search(
                r"微软雅黑|宋体|Noto Sans SC|SimSun|Microsoft YaHei|PingFang|Source Han|SimHei|楷体",
                c,
            )
        ),
        "pending_bu": len(re.findall("待补充", c)),
        "https_literal_count": len(https_all),
        "https_outside_datauri_samples": https_outside_img[:20],
        "cdn_hits": {
            p: len(re.findall(p, c, re.I))
            for p in CDN_PATTERNS
            if re.search(p, c, re.I)
        },
        "fig_title_count": len(fig_titles),
        "h4_counts": {k: sum(1 for t in h4_text if k in t) for k in FIG_HEADINGS},
        "h4_unique": sorted(set(h4_text))[:40],
        "term_present": {t: (t in c) for t in TERM_KEYS},
    }
    if "report" in path.name:
        out["sections"] = {s: (s in c) for s in SECTION_KEYS}
        # per-figure explanation completeness: count fig-title then following required h4
        # heuristic: each figure has blocks after img
        required = ["背景与作用", "如何阅读", "曲线 / 分量含义", "可得出的结论与理由", "通俗版结论"]
        # also accept alternate names
        alts = {
            "背景与作用": ["背景与作用"],
            "如何阅读": ["如何阅读", "怎么读"],
            "曲线 / 分量含义": ["曲线 / 分量含义", "曲线/分量含义", "分量含义"],
            "可得出的结论与理由": ["可得出的结论", "结论与理由"],
            "通俗版结论": ["通俗版结论", "通俗结论"],
        }
        # Split by fig-title
        parts = re.split(r'<div class="fig-title">', c)[1:]
        per = []
        for p in parts:
            title = re.split(r"</div>", p, maxsplit=1)[0]
            title = re.sub(r"<[^>]+>", "", title).strip()
            chunk = p[:8000]  # local neighborhood
            miss = []
            for req, names in alts.items():
                if not any(n in chunk for n in names):
                    miss.append(req)
            # length of explanation text
            texts = re.findall(r"<p>(.*?)</p>", chunk, flags=re.S)
            plain = " ".join(re.sub(r"<[^>]+>", "", t) for t in texts)
            per.append(
                {
                    "title": title[:80],
                    "missing": miss,
                    "explain_chars": len(plain),
                }
            )
        out["per_fig"] = per
        out["figs_missing_any"] = sum(1 for x in per if x["missing"])
        out["figs_short"] = [
            x["title"] for x in per if x["explain_chars"] < 400
        ]
    return out


def main() -> None:
    import json

    results = [scan(p) for p in FILES if p.exists()]
    out = ROOT / "06_PAPER" / "notes" / "_html_compliance_scan_result.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out)
    for r in results:
        print("---", r["path"], "size_mb", r["size_mb"])
        for k in [
            "DOCTYPE",
            "html",
            "head",
            "style",
            "body",
            "charset_utf8",
            "img_count",
            "src_data",
            "src_dotdot",
            "src_dot",
            "src_http",
            "table_count",
            "max_width_100",
            "chinese_font",
            "pending_bu",
            "https_literal_count",
            "fig_title_count",
            "figs_missing_any",
        ]:
            if k in r:
                print(f"  {k}: {r[k]}")
        if r.get("src_other"):
            print("  src_other:", r["src_other"])
        if r.get("cdn_hits"):
            print("  cdn_hits:", r["cdn_hits"])
        if r.get("https_outside_datauri_samples"):
            print("  https_outside:", r["https_outside_datauri_samples"][:5])
        if r.get("sections"):
            print("  sections:", r["sections"])
        if r.get("h4_counts"):
            print("  h4:", r["h4_counts"])
        if r.get("figs_short"):
            print("  short_figs:", len(r["figs_short"]), r["figs_short"][:8])
        miss_terms = [t for t, ok in r.get("term_present", {}).items() if not ok]
        print("  missing_terms:", miss_terms)
        if r.get("per_fig"):
            bad = [x for x in r["per_fig"] if x["missing"]]
            print("  figs_with_missing_blocks:", len(bad))
            for x in bad[:10]:
                print("   ", x["title"], "->", x["missing"])


if __name__ == "__main__":
    main()
