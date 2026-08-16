"""Build the P1 manuscript as a fully self-contained academic HTML file.

The converter intentionally uses only the Python standard library. It reads the
latest manuscript draft, checks key claims against the authoritative analysis
JSON files, converts Markdown tables to native HTML, and embeds every PNG under
``06_PAPER/figures`` as a Base64 data URI.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DRAFTS = ROOT / "06_PAPER" / "drafts"
ANALYSIS = ROOT / "06_PAPER" / "analysis"
FIGURES = ROOT / "06_PAPER" / "figures"
OUTPUT = DRAFTS / "P1_paper.html"


CSS = r"""
:root { color-scheme: light; --ink:#171717; --muted:#555; --rule:#777; --soft:#f5f5f2; --accent:#17365d; }
* { box-sizing:border-box; }
html { background:#e8e8e5; }
body {
  max-width: 980px; margin: 24px auto; padding: 64px 78px 80px;
  background:#fff; color:var(--ink);
  font-family:"Times New Roman", Times, "SimSun", "Songti SC", serif;
  font-size:16px; line-height:1.58; text-rendering:optimizeLegibility;
  box-shadow:0 2px 18px rgba(0,0,0,.09);
}
header.paper-head { text-align:center; border-bottom:1.5px solid var(--ink); padding-bottom:24px; margin-bottom:34px; }
h1 { font-size:27px; line-height:1.24; margin:0 0 18px; font-weight:700; }
.authors { font-size:18px; margin:7px 0; }
.affiliations, .paper-meta { color:var(--muted); font-size:14px; margin:4px 0; }
.pending { color:#8b1a1a; font-weight:700; }
h2 { font-size:22px; line-height:1.3; margin:38px 0 13px; border-bottom:1px solid #aaa; padding-bottom:5px; }
h3 { font-size:18px; line-height:1.35; margin:28px 0 9px; }
h4 { font-size:16px; line-height:1.35; margin:22px 0 7px; font-style:italic; }
p { margin:0 0 12px; text-align:justify; hyphens:auto; }
p.abstract { padding:0 18px; }
strong { font-weight:700; }
code {
  font-family:Consolas, "Courier New", monospace; font-size:.86em;
  background:#f2f2f2; padding:.08em .28em; border-radius:2px; overflow-wrap:anywhere;
}
.equation { text-align:center; margin:18px 0; font-style:italic; letter-spacing:.01em; }
ol, ul { margin:8px 0 15px 25px; padding-left:14px; }
li { margin:4px 0; padding-left:3px; }
.table-wrap { width:100%; overflow-x:auto; margin:16px 0 22px; }
table { width:100%; border-collapse:collapse; font-size:13.5px; line-height:1.35; }
th, td { border:1px solid #888; padding:6px 7px; vertical-align:top; }
th { background:#ececea; font-weight:700; text-align:center; }
tbody tr:nth-child(even) { background:#fafafa; }
td:not(:first-child) { font-variant-numeric:tabular-nums; }
figure { margin:18px auto 28px; text-align:center; break-inside:avoid; page-break-inside:avoid; }
figure img { display:block; width:auto; max-width:100%; height:auto; margin:0 auto; }
figcaption { margin:8px auto 0; max-width:92%; color:#333; font-size:13.5px; line-height:1.4; text-align:left; }
.figure-label { font-weight:700; }
.notice {
  border-left:4px solid var(--accent); background:var(--soft); padding:10px 14px;
  margin:17px 0; font-size:14px;
}
.references p, #references ~ p { padding-left:24px; text-indent:-24px; font-size:14px; text-align:left; }
hr { border:0; border-top:1px solid #aaa; margin:26px 0; }
a { color:inherit; text-decoration:none; }
@media (max-width:760px) {
  html { background:#fff; }
  body { margin:0; padding:30px 22px 50px; box-shadow:none; font-size:15px; }
  h1 { font-size:23px; } h2 { font-size:20px; }
}
@media print {
  @page { size:A4; margin:18mm 16mm 20mm; }
  html, body { background:#fff; }
  body { max-width:none; margin:0; padding:0; box-shadow:none; font-size:10.5pt; }
  h2, h3, h4 { break-after:avoid; page-break-after:avoid; }
  .table-wrap { overflow:visible; }
  table { font-size:8.2pt; }
}
"""


def load_json(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def require_text(text: str, values: list[str], label: str) -> None:
    normalized = text.replace("−", "-")
    missing = [value for value in values if value.replace("−", "-") not in normalized]
    if missing:
        raise ValueError(f"{label}: manuscript is missing JSON-backed value(s): {missing}")


def validate_authoritative_claims(text: str) -> None:
    """Fail fast if the draft no longer contains the JSON-backed hard bounds."""
    w3 = load_json("w3_tdgta_off_metrics.json")
    w1 = load_json("w1_provenance_metrics.json")
    w4 = load_json("w4_cciw_vs_dart.json")
    nhr = load_json("nhr_dlt_scan.json")
    sod = load_json("w7_columbia_sod_vs_almeida.json")

    on = {m["caliber"]: m for m in w3["metrics"] if m.get("run") == "ON"}
    require_text(
        text,
        [
            f"{on['A']['r2']:.4f}",
            f"{on['B']['nse']:+.4f}",
            f"{on['C']['nse']:.4f}",
            f"{w3['reachable_range']['obs_frac_gt_120'] * 100:.2f}%",
        ],
        "Bonneville",
    )
    dg = next(p for p in w1["degray"]["pairs"] if p["id"] == "DG_T2_vs_Tvolavg")
    col = next(p for p in w1["columbia"]["pairs"] if p["id"] == "COL_DO_I49_vs_I33")
    require_text(text, [f"{dg['r2']:.4f}", f"{dg['nse']:.4f}", f"{col['nse']:.4f}"], "Internal consistency")
    if w4["out_of_sample"]["computed_nse"] is not False:
        raise ValueError("Unexpected analysis state: out-of-sample NSE is no longer false")
    on_counts = nhr["monotonicity"]["DLTINTER_ON"]["neg_counts"]
    off_counts = nhr["monotonicity"]["DLTINTER_OFF"]["neg_counts"]
    require_text(text, ["/".join(map(str, on_counts)), "/".join(map(str, off_counts))], "NHR")
    sod_summary = sod.get("wet_cells_summary", sod.get("summary", sod))
    sod_blob = json.dumps(sod_summary)
    if "0.8955" not in sod_blob:
        raise ValueError("SOD JSON does not contain the manuscript's 0.8955 fraction")
    require_text(text, ["0.8955", "transplant"], "SOD transplant")


def slugify(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[^\w\u4e00-\u9fff]+", "-", value, flags=re.UNICODE).strip("-").lower()
    return value or "section"


def inline_markup(raw: str) -> str:
    """Convert the small inline-Markdown subset used by the manuscript."""
    tokens: list[str] = []

    def save_code(match: re.Match[str]) -> str:
        tokens.append(f"<code>{html.escape(match.group(1))}</code>")
        return f"\x00CODE{len(tokens)-1}\x00"

    raw = re.sub(r"`([^`]+)`", save_code, raw)
    raw = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", raw)  # no external dependency or URL
    escaped = html.escape(raw, quote=False)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", escaped)
    escaped = re.sub(r"(?<!_)_([^_\n]+?)_(?!_)", r"<em>\1</em>", escaped)
    for index, token in enumerate(tokens):
        escaped = escaped.replace(f"\x00CODE{index}\x00", token)
    return escaped


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def table_html(lines: list[str]) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    header = rows[0]
    body = rows[2:] if len(rows) > 1 and is_table_separator(lines[1]) else rows[1:]
    parts = ['<div class="table-wrap"><table><thead><tr>']
    parts.extend(f"<th>{inline_markup(cell)}</th>" for cell in header)
    parts.append("</tr></thead><tbody>")
    for row in body:
        parts.append("<tr>")
        row += [""] * (len(header) - len(row))
        parts.extend(f"<td>{inline_markup(cell)}</td>" for cell in row[: len(header)])
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def caption_for(raw: str, fallback: str) -> str:
    clean = re.sub(r"\s*File(?:s)?:.*$", "", raw, flags=re.IGNORECASE)
    clean = re.sub(r"\s*Companion.*$", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*Core panel:.*$", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*Sources?:.*$", "", clean, flags=re.IGNORECASE)
    if not clean.strip():
        clean = fallback
    return inline_markup(clean)


def figure_html(path: Path, caption: str, supplemental_number: int | None = None) -> str:
    if supplemental_number is not None:
        caption = (
            f'<span class="figure-label">Supplementary figure S{supplemental_number}.</span> '
            f"{inline_markup(caption)}"
        )
    return (
        f'<figure id="figure-{slugify(path.stem)}">'
        f'<img src="{data_uri(path)}" alt="{html.escape(path.stem)}">'
        f"<figcaption>{caption}</figcaption></figure>"
    )


def convert_markdown(text: str, figure_paths: list[Path]) -> tuple[str, set[str]]:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = text.replace("https://", "").replace("http://", "")
    lines = text.splitlines()
    by_name = {path.name: path for path in figure_paths}
    embedded: set[str] = set()
    out: list[str] = []
    paragraph: list[str] = []
    first_h1 = True
    i = 0

    def add_figures(raw_block: str) -> None:
        for name, path in by_name.items():
            if name in raw_block and name not in embedded:
                out.append(figure_html(path, caption_for(raw_block, path.stem.replace("_", " "))))
                embedded.add(name)

    def flush_paragraph() -> None:
        if not paragraph:
            return
        raw = " ".join(part.strip() for part in paragraph).strip()
        paragraph.clear()
        if raw:
            css_class = ' class="abstract"' if out and any('id="abstract"' in part for part in out[-3:]) else ""
            out.append(f"<p{css_class}>{inline_markup(raw)}</p>")
            add_figures(raw)

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            i += 1
            continue
        if stripped == r"\[":
            flush_paragraph()
            equation: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != r"\]":
                equation.append(lines[i].strip())
                i += 1
            eq = " ".join(equation)
            eq = (
                eq.replace(r"\mathrm{KGE}", "KGE")
                .replace(r"\sqrt", "√")
                .replace(r"\sigma", "σ")
                .replace(r"\mu", "μ")
                .replace(r"\alpha", "α")
                .replace(r"\beta", "β")
                .replace(r"\quad", " ")
                .replace(r"\,", " ")
                .replace("{", "")
                .replace("}", "")
                .replace("^2", "²")
                .replace("_s", "ₛ")
                .replace("_o", "ₒ")
            )
            out.append(f'<div class="equation">{html.escape(eq)}</div>')
            i += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            if level == 1 and first_h1:
                out.append(f"<h1>{inline_markup(title)}</h1>")
                first_h1 = False
            else:
                ident = slugify(title)
                out.append(f'<h{level} id="{ident}">{inline_markup(title)}</h{level}>')
            i += 1
            continue
        if re.fullmatch(r"-{3,}", stripped):
            flush_paragraph()
            out.append("<hr>")
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            flush_paragraph()
            block = [stripped, lines[i + 1].strip()]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            out.append(table_html(block))
            continue
        list_match = re.match(r"^(\d+\.)\s+(.+)$", stripped) or re.match(r"^([-+])\s+(.+)$", stripped)
        if list_match:
            flush_paragraph()
            ordered = list_match.group(1).endswith(".")
            tag = "ol" if ordered else "ul"
            start = int(list_match.group(1)[:-1]) if ordered else None
            items: list[str] = []
            while i < len(lines):
                current = lines[i].strip()
                match = re.match(r"^\d+\.\s+(.+)$", current) if ordered else re.match(r"^[-+]\s+(.+)$", current)
                if not match:
                    break
                item = match.group(1)
                items.append(item)
                i += 1
            start_attr = f' start="{start}"' if ordered and start != 1 else ""
            out.append(
                f"<{tag}{start_attr}>"
                + "".join(f"<li>{inline_markup(item)}</li>" for item in items)
                + f"</{tag}>"
            )
            for item in items:
                add_figures(item)
            continue
        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    return "\n".join(out), embedded


def choose_source() -> Path:
    v2 = DRAFTS / "P1_GMD_draft_v2.md"
    v1 = DRAFTS / "P1_GMD_draft_v1.md"
    if v2.exists():
        return v2
    if v1.exists():
        return v1
    raise FileNotFoundError("Neither P1_GMD_draft_v2.md nor P1_GMD_draft_v1.md exists")


def build(output: Path = OUTPUT) -> dict:
    source = choose_source()
    markdown = source.read_text(encoding="utf-8")
    validate_authoritative_claims(markdown)
    figures = sorted(FIGURES.glob("*.png"), key=lambda path: path.name.lower())
    if not figures:
        raise FileNotFoundError(f"No PNG figures found in {FIGURES}")

    body, embedded = convert_markdown(markdown, figures)
    remaining = [path for path in figures if path.name not in embedded]
    if remaining:
        gallery = ['<h2 id="supplementary-figure-gallery">Supplementary figure gallery</h2>']
        for number, path in enumerate(remaining, 1):
            gallery.append(figure_html(path, path.stem.replace("_", " "), number))
            embedded.add(path.name)
        body += "\n" + "\n".join(gallery)

    title_match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "CE-QUAL-W2 evaluation methods"
    # The first converted h1 is moved into the formal paper header.
    body = re.sub(r"^\s*<h1>.*?</h1>\s*", "", body, count=1, flags=re.DOTALL)
    body = body.replace(
        "No Zenodo DOI has been minted for this draft.",
        '<span class="pending">待补充：Zenodo DOI。</span>',
    )
    paper_header = f"""
<header class="paper-head">
  <h1>{inline_markup(title)}</h1>
  <p class="authors"><span class="pending">待补充：作者姓名</span></p>
  <p class="affiliations"><span class="pending">待补充：作者单位与通讯作者信息</span></p>
  <p class="paper-meta">Manuscript version: v2 · Target journal: <em>Geoscientific Model Development</em></p>
  <p class="paper-meta"><span class="pending">待补充：Zenodo DOI</span></p>
</header>"""
    notice = (
        '<aside class="notice"><strong>Interpretive constraint.</strong> '
        "Comparability is conditional on aligned variable provenance, controller state, and numerical health. "
        "Internal consistency is not observational skill; NHR results are not a universal timestep law.</aside>"
    )
    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
{CSS}
</style>
</head>
<body>
{paper_header}
{notice}
<main>
{body}
</main>
</body>
</html>
"""
    output.write_text(document, encoding="utf-8")
    return {
        "source": str(source),
        "output": str(output),
        "images": len(embedded),
        "bytes": output.stat().st_size,
        "pending": document.count("待补充"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = build(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
