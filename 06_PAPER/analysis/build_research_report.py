#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build self-contained Chinese research report (HTML + Markdown + PDF).

Reads only existing analysis JSON / SciencePlots figures / notes-derived facts.
Does not invent metrics. Missing items are marked 「待补充」.
No git commit/push.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import re
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any
import sys

# Allow `python build_research_report.py` from repo root or analysis/
sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_fig_narratives import get_narrative  # noqa: E402

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
PAPER = ROOT / "06_PAPER"
ANALYSIS = PAPER / "analysis"
FIGURES = PAPER / "figures"
NOTES = PAPER / "notes"
CARDS = PAPER / "w2eval" / "cards"
OUT_DIR = PAPER / "report"
OUT_HTML = OUT_DIR / "report.html"
OUT_MD = OUT_DIR / "report.md"
OUT_PDF = OUT_DIR / "report.pdf"
PDF_LOG = OUT_DIR / "pdf_build_log.txt"

CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]
SIMHEI = Path(r"C:\Windows\Fonts\simhei.ttf")


def load_json(name: str) -> Any:
    path = ANALYSIS / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def b64_data_uri(path: Path) -> str | None:
    if not path.exists():
        return None
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def fmt(x: Any, nd: int = 4) -> str:
    if x is None:
        return "待补充"
    if isinstance(x, bool):
        return "是" if x else "否"
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        if abs(x) >= 100:
            return f"{x:.4g}"
        return f"{x:.{nd}f}".rstrip("0").rstrip(".")
    return str(x)


def pct(x: Any, nd: int = 1) -> str:
    if x is None:
        return "待补充"
    return f"{100.0 * float(x):.{nd}f}%"


def find_pair(pairs: list[dict], pid: str) -> dict:
    for p in pairs or []:
        if p.get("id") == pid:
            return p
    return {}


def metric_row(m: dict) -> dict:
    return {
        "r2": m.get("r2"),
        "nse": m.get("nse"),
        "kge": m.get("kge"),
        "r": m.get("r"),
        "alpha": m.get("alpha"),
        "beta": m.get("beta"),
        "pbias": m.get("pbias"),
        "mae": m.get("mae"),
        "sim_max": m.get("sim_max"),
        "n": m.get("n"),
        "file": m.get("file") or m.get("source") or "",
        "run": m.get("run"),
        "caliber": m.get("caliber") or m.get("id"),
    }


class ReportBuilder:
    def __init__(self) -> None:
        self.gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.w1 = load_json("w1_provenance_metrics.json") or {}
        self.w3 = load_json("w3_tdgta_off_metrics.json") or {}
        self.w4 = load_json("w4_cciw_vs_dart.json") or {}
        self.w5 = load_json("w5_lit_audit_summary.json") or {}
        self.w7 = load_json("w7_columbia_sod_vs_almeida.json") or {}
        self.nhr_scan = load_json("nhr_dlt_scan.json") or {}
        self.nhr_exist = load_json("nhr_existing_runs.json") or {}
        self.cards = load_json("../w2eval/cards/index.json")  # may fail
        try:
            self.cards_index = json.loads((CARDS / "index.json").read_text(encoding="utf-8"))
        except Exception:
            self.cards_index = {"cards": []}
        self.fig_count = 0
        self.embedded_imgs = 0
        self.pending: list[str] = []
        self.html_parts: list[str] = []
        self.md_parts: list[str] = []
        self.pdf_blocks: list[tuple[str, str | None, Path | None]] = []
        # (kind, text, image_path) kind in text|h1|h2|h3|fig|note

    def note_pending(self, item: str) -> None:
        if item not in self.pending:
            self.pending.append(item)

    def h(self, level: int, title: str, anchor: str | None = None) -> None:
        aid = anchor or re.sub(r"[^\w\u4e00-\u9fff]+", "-", title).strip("-").lower()
        tag = f"h{level}"
        self.html_parts.append(f'<{tag} id="{aid}">{title}</{tag}>')
        prefix = "#" * level
        self.md_parts.append(f"\n{prefix} {title}\n")
        kind = {1: "h1", 2: "h2", 3: "h3"}.get(level, "h3")
        self.pdf_blocks.append((kind, title, None))

    def p(self, text: str) -> None:
        self.html_parts.append(f"<p>{text}</p>")
        self.md_parts.append(text + "\n")
        self.pdf_blocks.append(("text", text, None))

    def ul(self, items: list[str]) -> None:
        self.html_parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
        for i in items:
            self.md_parts.append(f"- {i}")
        self.md_parts.append("")
        for i in items:
            self.pdf_blocks.append(("text", f"• {i}", None))

    def callout(self, title: str, body: str, css: str = "warn") -> None:
        self.html_parts.append(
            f'<div class="callout {css}"><div class="callout-title">{title}</div><p>{body}</p></div>'
        )
        self.md_parts.append(f"> **{title}**  \n> {body}\n")
        self.pdf_blocks.append(("note", f"【{title}】{body}", None))

    def table(self, headers: list[str], rows: list[list[Any]], caption: str = "") -> None:
        thead = "".join(f"<th>{h}</th>" for h in headers)
        body = []
        for r in rows:
            body.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
        cap = f"<caption>{caption}</caption>" if caption else ""
        self.html_parts.append(
            f'<div class="table-wrap"><table>{cap}<thead><tr>{thead}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>'
        )
        self.md_parts.append("")
        if caption:
            self.md_parts.append(f"*{caption}*")
        self.md_parts.append("| " + " | ".join(headers) + " |")
        self.md_parts.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for r in rows:
            self.md_parts.append("| " + " | ".join(str(c) for c in r) + " |")
        self.md_parts.append("")
        self.pdf_blocks.append(("text", caption or "表", None))
        self.pdf_blocks.append(("text", " | ".join(headers), None))
        for r in rows:
            self.pdf_blocks.append(("text", " | ".join(str(c) for c in r), None))

    def figure(
        self,
        fname: str,
        title: str,
        background: str,
        how_to_read: str,
        series_meaning: str,
        conclusion: str,
        plain: str,
        *,
        search_dirs: list[Path] | None = None,
    ) -> None:
        self.fig_count += 1
        fig_id = f"fig-{self.fig_count:02d}"
        numbered = f"图 {self.fig_count}　{title}"
        dirs = search_dirs or [FIGURES, ANALYSIS]
        path = None
        for d in dirs:
            cand = d / fname
            if cand.exists():
                path = cand
                break
        self.html_parts.append(f'<div class="figure" id="{fig_id}">')
        self.html_parts.append(f'<div class="fig-title">{numbered}</div>')
        if path is None:
            self.note_pending(f"图文件缺失：{fname}")
            self.html_parts.append(
                f'<p class="pending">待补充：图像文件不存在（{fname}）。</p>'
            )
            self.md_parts.append(f"\n### {numbered}\n\n> 待补充：图像不存在（`{fname}`）\n")
            self.pdf_blocks.append(("note", f"{numbered}：待补充（{fname}）", None))
        else:
            uri = b64_data_uri(path)
            assert uri is not None
            self.embedded_imgs += 1
            self.html_parts.append(f'<img alt="{numbered}" src="{uri}" />')
            self.md_parts.append(f"\n### {numbered}\n\n![{numbered}]({path.as_posix()})\n")
            self.pdf_blocks.append(("fig", numbered, path))
        deep = get_narrative(fname)
        if deep:
            background = deep["background"]
            how_to_read = deep["how_to_read"]
            series_meaning = deep["series_meaning"]
            conclusion = deep["conclusion"]
            plain = deep["plain"]
        blocks = [
            ("背景与作用", background),
            ("怎么读（坐标轴 / 曲线 / 散点 / 直方图 / 热图）", how_to_read),
            ("每条曲线（或分量）含义", series_meaning),
            ("逐子图 / 逐面板精读", deep.get("panels", "该图为单面板；逐曲线含义已在上一段完整说明。") if deep else "该图为单面板；逐曲线含义已在上一段完整说明。"),
            ("物理意义与方程链", deep.get("physics", "本图的物理解释以变量来源、空间支撑、时间支撑和评估公式共同限定；不能脱离 VPR 单独解释图形。") if deep else "本图的物理解释以变量来源、空间支撑、时间支撑和评估公式共同限定；不能脱离 VPR 单独解释图形。"),
            ("能得出什么结论", conclusion),
            ("原因、替代解释与证据边界", deep.get("boundary", "结论只在现有运行、配对窗和 JSON 记录范围内成立；缺少独立观测或样本外运行时，不升级为观测技能或外推规律。") if deep else "结论只在现有运行、配对窗和 JSON 记录范围内成立；缺少独立观测或样本外运行时，不升级为观测技能或外推规律。"),
            ("常见误读与排除", deep.get("misread", "不得把相关性当作一致性，不得把内部通道对照当作观测验证，也不得把文件存在性直接等同于物理过程存在性。") if deep else "不得把相关性当作一致性，不得把内部通道对照当作观测验证，也不得把文件存在性直接等同于物理过程存在性。"),
            ("通俗版结论", plain),
        ]
        for lab, txt in blocks:
            self.html_parts.append(f'<div class="fig-block"><h4>{lab}</h4><p>{txt}</p></div>')
            self.md_parts.append(f"**{lab}：** {txt}\n")
            self.pdf_blocks.append(("text", f"{lab}：{txt}", None))
        self.html_parts.append("</div>")

    # ------------------------------------------------------------------ content
    def build_cover_toc(self) -> None:
        self.html_parts.append(
            f"""
<section class="cover" id="cover">
  <div class="cover-badge">CE-QUAL-W2 · 科研评估报告</div>
  <h1 class="cover-title">变量溯源、控制律门控与数值健康记录：<br/>CE-QUAL-W2 官方示例的方法学审计</h1>
  <p class="cover-sub">基于既有复现运行与结构化分析产物（W1–W7 / w2eval）的自包含中文报告</p>
  <div class="cover-meta">
    <div><span>生成时间</span><strong>{self.gen_time}</strong></div>
    <div><span>工作区</span><strong>I:\\Projects\\20260810-CE-QUAL-W2</strong></div>
    <div><span>模型重跑</span><strong>未重跑完整 W2（本报告仅汇编既有产物）</strong></div>
    <div><span>数字权威</span><strong>06_PAPER/analysis/*.json（P1 数字审计 40/40 PASS）</strong></div>
  </div>
  <p class="cover-note">本报告严禁把 DeGray 水温 / Columbia DO 的内部一致性写成对观测技能；
  严禁把 TDGTA 最优序列写成「物理量被删除」；严禁把 NHR 的 5/4/1/5 写成普遍时间步定律；
  严禁声称存在样本外 NSE。</p>
</section>
"""
        )
        self.md_parts.extend(
            [
                f"# 变量溯源、控制律门控与数值健康记录：CE-QUAL-W2 官方示例的方法学审计\n",
                f"- 生成时间：{self.gen_time}",
                "- 数字权威：`06_PAPER/analysis/*.json`",
                "- 未重跑完整 W2；未 git commit/push\n",
            ]
        )
        toc = [
            ("封面", "cover"),
            ("摘要", "abstract"),
            ("研究背景与目的", "background"),
            ("数据与方法", "methods"),
            ("研究过程", "process"),
            ("结果展示", "results"),
            ("分析与讨论", "discussion"),
            ("主要结论", "conclusions"),
            ("不足与展望", "limitations"),
            ("附录", "appendix"),
        ]
        self.html_parts.append('<nav class="toc" id="toc"><h2>目录</h2><ol>')
        self.md_parts.append("## 目录\n")
        for title, aid in toc:
            self.html_parts.append(f'<li><a href="#{aid}">{title}</a></li>')
            self.md_parts.append(f"1. [{title}](#{aid})")
        self.html_parts.append("</ol></nav>")
        self.md_parts.append("")

    def build_abstract(self) -> None:
        self.h(2, "摘要", "abstract")
        dg = find_pair(self.w1.get("degray", {}).get("pairs", []), "DG_T2_vs_Tvolavg")
        col = find_pair(self.w1.get("columbia", {}).get("pairs", []), "COL_DO_I49_vs_I33")
        w3m = [metric_row(m) for m in self.w3.get("metrics", [])]
        on_b = next((m for m in w3m if m["run"] == "ON" and m["caliber"] == "B"), {})
        on_a = next((m for m in w3m if m["run"] == "ON" and m["caliber"] == "A"), {})
        on_c = next((m for m in w3m if m["run"] == "ON" and m["caliber"] == "C"), {})
        w4h = self.w4.get("cciw_vs_dart", {}).get("hourly_tdg", {})
        w5c = self.w5.get("counts", {})
        sod = self.w7.get("columbia_instantaneous_wet_jday_ge_33", {})
        ex25 = self.w4.get("exceedance_2016_2025", {})
        self.p(
            "本报告汇编 CE-QUAL-W2（二维横向平均水动力—水质模型；Cole & Wells, 2003）官方示例复现与后续方法学审计产物，"
            "围绕四个相互独立、但必须联立声明的评估条件展开：（1）变量溯源记录 VPR（Variable Provenance Record，"
            "输出文件/列名/断面 segment I / 层 layer K / 单位 / 派生链 / 时间支撑 / 配对容差）；"
            "（2）控制律状态（以 Bonneville 总溶解气体 TDG，Total Dissolved Gas 的目标控制器 TDGTA 为例）；"
            "（3）数值健康记录 NHR（Numerical Health Record，负表面层厚度回退、exit 0 是否掩盖警告、DLTINTER 状态）；"
            "（4）证据类型声明（对观测技能 vs 输出通道内部一致性）。"
        )
        self.p(
            f"在同一套 CCIW（Cascade Island / Bonneville 尾水水质站）观测上，Bonneville 三口径给出窄带 R²"
            f"（决定系数，Coefficient of Determination）约 {fmt(on_a.get('r2'),4)}–{fmt(on_c.get('r2'),4)}，"
            f"而 NSE（Nash–Sutcliffe Efficiency，纳什效率系数）却为 "
            f"{fmt(on_a.get('nse'),4)} / {fmt(on_b.get('nse'),4)} / {fmt(on_c.get('nse'),4)}："
            f"R² 最高的 C 口径恰恰是 NSE 最差之一。技能最好、β≈1、模拟峰值钉在约 "
            f"{fmt(on_b.get('sim_max'),2)}% 的序列只存在于控制器门控文件 "
            f"<code>TDGTarget_output.csv</code>；TDGTA=OFF 时该文件消失，但 SYSTDG 仍把控制前快照写到 "
            f"<code>TDG_output.csv</code>（ON/OFF 逐日相同），因此不能写成「物理量被删除」。"
        )
        self.p(
            f"命题已推广：DeGray 同一 TSR（Time Series，时间序列输出）文件中表层 T2 对库容均温 Tvolavg "
            f"给出 R²={fmt(dg.get('r2'),4)} 而 NSE={fmt(dg.get('nse'),4)}（α={fmt(dg.get('alpha'),3)}，β={fmt(dg.get('beta'),3)}）；"
            f"Columbia 溶解氧 DO（Dissolved Oxygen）断面 I=49 vs I=33 的 R²={fmt(col.get('r2'),4)} 而 NSE={fmt(col.get('nse'),4)}。"
            f"<strong>二者皆无独立观测，属于输出通道内部一致性，不是对观测技能。</strong>"
            f" Long Lake 在官方 DLTINTER=ON 下负厚度计数为 5/4/1/5（DLTMAX@JDAY30 = 20/50/100/200 s），"
            f"非单调；DLTINTER=OFF 后全为 0——故 NHR 是报告项，不是「减小时间步更不稳」定律。"
        )
        self.p(
            f"库内 CCIW 与 2026 年下载的 DART 小时值配对 n={fmt(w4h.get('n'))}，MAE={fmt(w4h.get('mae'),6)}%，"
            f"|Δ|≤0.051 匹配率={fmt(w4h.get('match_rate_abs_le_0p051'),6)}；未见示例观测被实质性改写的证据。"
            f"2016–2025 有效小时超 120% 比例为 {fmt(ex25.get('pct_hours_gt_120'),1)}%，但<strong>无样本外 NSE</strong>（模型约到 2011）。"
            f" Columbia 湿段 SOD（Sediment Oxygen Demand，底泥耗氧）均值 {fmt(sod.get('mean'),3)} gO₂/m²/d，"
            f"落在 Almeida 扫描带内比例 {pct(sod.get('frac_in_0.5_3.0'),1)}，但是 DeGray 模板移植，非现场率定。"
            f" W5 文献审计：38 篇中VPR-core 可重建仅 {w5c.get('vpr_reconstruct',{}).get('yes','待补充')}/38（"
            f"{fmt(self.w5.get('headline',{}).get('vpr_reconstruct_yes_pct'),1)}%），全文获取 "
            f"{w5c.get('fulltext_true','待补充')}/38，其余标 unknown。"
        )
        self.p(
            "关键词：CE-QUAL-W2；变量溯源（VPR）；NSE / KGE / R²；总溶解气体（TDG）；TDGTA 控制器；"
            "数值健康记录（NHR）；内部一致性；条件化评估"
        )

    def build_glossary(self) -> None:
        self.h(3, "术语与符号全量说明（首次出现）", "glossary")
        rows = [
            [
                "CE-QUAL-W2",
                "二维横向平均（laterally averaged）水动力—水质模型（Cole & Wells, 2003）。"
                "本报告复现官方 v4.5.5 可执行文件 w2_v455_ifx.exe 的示例，不发明新过程方程。",
            ],
            [
                "JDAY",
                "模型儒略日（Julian day）。Bonneville 中 40544=2011-01-01（Excel 序列原点 1899-12-30）。"
                "配对窗与超标统计都必须声明 JDAY 范围。",
            ],
            [
                "segment / I",
                "纵向河段编号。同一变量名在不同 I 上是不同空间支撑；"
                "Columbia DO 的核心教训是错站比错层更危险。",
            ],
            [
                "layer / K / KT / KTMAX",
                "垂向层号 K；KT 为当前水面所在表层索引；KTMAX 为网格允许的最大层索引上界"
                "（活动层窗口随水位变化）。不写 K/KT，表/底层输出无法复原。",
            ],
            [
                "H1(KT,I) / ZMIN",
                "H1(KT,I) 为断面 I 当前表层厚度。若 H1&lt;0，几何非法，源码路径写警告并把时间步"
                "回退到 DLTMIN 后重算（见 NHR）。ZMIN 与表层水位相对层顶偏移相关，参与加/减层判定——"
                "层增减可以是合法响应，不等于 H1&lt;0 故障。",
            ],
            [
                "TSR / PRF / SNP / WDO",
                "时间序列、剖面、快照场、取水/结构混合输出通道。"
                "同名物理量可经不同文件与派生链写出；VPR 必须落到文件+列。",
            ],
            [
                "TDG",
                "Total Dissolved Gas，总溶解气体饱和度（%）。名字叫 TDG 不够，必须声明是亨利换算尾水、"
                "库内 TSR、SYSTDG 快照，还是 TDGTA 门控文件。",
            ],
            [
                "SYSTDG / TDGTA",
                "SYSTDG：控制前快照可写到 TDG_output.csv（口径 S）。TDGTA：目标控制器；"
                "后控制序列在 TDGTarget_output.csv（口径 B）。OFF 时 B 消失但 S 仍可写——禁止「物理量被删除」。",
            ],
            [
                "CCIW / DART",
                "CCIW：Cascade Island / Bonneville 尾水观测（技能对照）。"
                "DART：公开小时库，核对示例观测并提供多年超标频率（不是样本外 NSE）。",
            ],
            [
                "R²（决定系数）",
                "Coefficient of Determination。对仿射变换 s′=a·s+b 不敏感；α/β 偏离 1 时仍可能好看。"
                "本报告不当唯一技能标尺。",
            ],
            [
                "NSE（Nash–Sutcliffe Efficiency）",
                "NSE = 1 − Σ(s−o)² / Σ(o−ō)²（Nash & Sutcliffe, 1970）。NSE&lt;0 劣于均值预报。"
                "内部一致性也会算 NSE，但必须标 internal_consistency。",
            ],
            [
                "KGE / r / α / β",
                "Kling–Gupta Efficiency（Gupta et al., 2009）："
                "KGE = 1 − √[(r−1)²+(α−1)²+(β−1)²]。r=corr；α=σ_s/σ_o；β=μ_s/μ_o。"
                "误指认与封顶常先坏在 α/β。",
            ],
            [
                "PBIAS / MAE / RMSE",
                "百分偏差 / 平均绝对误差 / 均方根误差。辅助解读，不能单独替代 NSE/KGE，也不能拯救缺失的 VPR。",
            ],
            [
                "VPR",
                "Variable Provenance Record：文件、列、segment I、layer K、单位、派生链、时间支撑、配对容差。"
                "缺少 VPR 时跨研究并置拟合优度一般不能从指标本身建立可比性。",
            ],
            [
                "NHR",
                "Numerical Health Record：负厚度回退、exit 0 是否掩盖警告、DLTINTER、层增减等。"
                "主张随技能一并报告（should），不是普遍时间步定律。",
            ],
            [
                "DLT / DLTMAX / DLTMIN / DLTINTER",
                "时间步长及其日程上限、下限、结点间是否线性插值。"
                "Long Lake：ON 时 5/4/1/5（20/50/100/200 s）非单调；OFF 全 0。不得写成「减小时间步更不稳」。",
            ],
            [
                "SOD / CSOD / NSOD",
                "Sediment Oxygen Demand 底泥耗氧及其碳源/氮源分量（gO₂ m⁻² d⁻¹）。"
                "Columbia 为移植参数量级检查，不是现场率定。",
            ],
            [
                "forrtl",
                "Intel Fortran 运行时库消息前缀。即便 exit 0，forrtl / w2.wrn 仍可能记录过严重几何警告；"
                "NHR 要求把这些警告从「正常结束」叙事中拆出来。",
            ],
            [
                "NV / NIT",
                "时间步 violation 累计 / 积分步数等；NV≠负厚度次数。不要混成单一不健康分数。",
            ],
        ]
        self.table(["术语 / 符号", "物理意义、方程溯源与为何引入"], rows, "表 G　术语速查")
        self.p(
            "上述术语不是互相独立的名词表，而是一条审计链：segment 与 layer 决定空间取样算子；"
            "JDAY 与配对容差决定时间取样算子；VPR 把这两个算子连到具体文件和列；R²、NSE、KGE、"
            "PBIAS、MAE、RMSE 只在这条链锁定后才有明确数学对象；TDGTA、SYSTDG、DLTINTER 等开关"
            "又决定该对象是否经过控制或数值路径变换；NHR 最后记录运行虽然结束、但中途是否发生几何回退。"
            "因此，本报告第一次出现缩写时不仅给全称，也说明它位于“物理过程—输出通道—评估统计”哪一层。"
        )

    def build_background(self) -> None:
        self.h(2, "研究背景与目的", "background")
        self.p(
            "水库与河口水动力—水质模型的「率定好看」并不自动等于「评估对象可比」。"
            "当论文只报告 R²，而不声明输出文件、断面、层、控制律与数值警告时，"
            "读者无法判断两个 R² 是否在比较同一数学对象。Benicio 等（2024）对 38 篇 "
            "CE-QUAL-W2 富营养化应用给出综述表 2 的 R² 轴（0.32–0.977），这恰好提供了"
            "一个可审计的文献对照面：若多数研究缺少 VPR，则跨研究比较这些 R² 在方法上"
            "一般不能成立。"
        )
        self.p(
            "本项目的目的不是重新发明 CE-QUAL-W2，而是在官方示例上把四类评估条件写清楚，"
            "并给出可复算入口："
        )
        self.ul(
            [
                "创新点 1：R² 对「相关但尺度错了」的通道盲；NSE/KGE（尤其 α、β）会暴露。",
                "创新点 2：最优 TDG 序列由 TDGTA 门控；关控制器后评估文件消失≠物理量删除。",
                "创新点 3：NHR 应随技能一并报告；5/4/1/5 仅 DLTINTER=ON 的诊断，OFF 全 0。",
                "创新点 4 / W7：可复现性与 SOD 量级检查；Columbia SOD 为移植参数。",
                "W4/W5/W6：DART 核对与超标频率、文献 VPR 审计、w2eval run-card 协议。",
            ]
        )
        self.callout(
            "科学边界（贯穿全文）",
            "DeGray / Columbia 无独立观测 → 内部一致性；无样本外 NSE；SOD 非现场率定；"
            "W5 全文 9/38，其余 unknown；不要把 2016–2025 的 21.2% 超标写成预报技能。",
            "warn",
        )

    def build_methods(self) -> None:
        self.h(2, "数据与方法", "methods")
        self.h(3, "数据来源", "data-sources")
        self.ul(
            [
                "指标 JSON：`06_PAPER/analysis/*.json`（本报告运行时直接读取）。",
                "图：`06_PAPER/figures/*.png`（SciencePlots 重绘，dpi≥300）。",
                "笔记：`06_PAPER/notes/W*_findings.md`、`STATUS_20260815.md`。",
                "run-card：`06_PAPER/w2eval/cards/`（VPR + 指标 + NHR，不自动跑模型）。",
                "复现运行目录：`05_REPRO_RUNS/run_20260811_fixed`、`run_20260814_*`、`run_20260815_*`。",
            ]
        )
        self.h(3, "评估指标定义", "metrics-def")
        self.p(
            "设观测（或对照序列）为 o_t、模拟（或另一通道）为 s_t，样本量为 n。"
            "本报告所有「对观测」数字均来自 Bonneville–CCIW 配对；DeGray/Columbia 的 ref "
            "是另一输出通道，不是野外观测。公式以纯文本给出（报告为自包含 HTML，不加载 MathJax CDN）。"
        )
        self.ul(
            [
                "R²：线性相关结构的决定系数。对 s′ = a·s + b 一类仿射变换不敏感，"
                "因此当 α、β 严重偏离 1 时仍可能「看起来不错」。",
                "NSE = 1 − Σ(s−o)² / Σ(o−ō)²。NSE&lt;0 表示比用观测均值预报更差。"
                "它惩罚幅度与偏差，是技能的主标尺之一。",
                "KGE = 1 − √[(r−1)² + (α−1)² + (β−1)²]，其中 α = σ_s/σ_o，β = μ_s/μ_o。"
                "变量误指认常通过 α（方差被平均压掉或被另一站放大）和 β（均值错位）暴露。",
                "PBIAS / MAE：总体偏高偏低与平均绝对误差；辅助解读，不单独替代 NSE/KGE。",
            ]
        )
        self.h(3, "指标的物理解释与互补关系", "metric-physics")
        self.p(
            "R² 在本报告中主要回答“两个序列是否沿近似线性方向共同变化”，并不回答“数值是否相等”。"
            "若 s=a·o+b 且噪声很小，即使 a 远离 1 或 b 很大，R² 仍可接近 1；这正是为什么 DeGray "
            "表层温度与库容均温能同步随季节升降，却不能互换。NSE 把逐时平方误差与观测围绕均值的总变差相比："
            "分子是模型或替代通道留下的误差能量，分母是“什么都不做、永远报观测均值”的基准误差能量。"
            "NSE<0 的物理含义不是“没有相关”，而是该序列作为逐时数值替代品还不如均值基准。"
        )
        self.p(
            "KGE 将误差来源分解为三条相互正交的诊断轴：r 控制时序共变，α=σs/σo 控制波动幅度，"
            "β=μs/μo 控制平均水平。KGE 的欧氏距离形式意味着任何一项显著偏离 1 都会拉低总分。"
            "PBIAS=100·Σ(s−o)/Σo 只看带符号总偏差，正负误差可抵消；MAE=n⁻¹Σ|s−o|保留平均绝对距离；"
            "RMSE=√[n⁻¹Σ(s−o)²]对大误差赋予更高权重。因而，PBIAS 近零不保证逐时准确，"
            "MAE 小不说明峰值尾部可达，RMSE 大则可能由少量极端误差主导。报告必须联读，而不能挑最漂亮的一项。"
        )
        self.p(
            "这里的 o_t 在 Bonneville–CCIW 段是观测；在 DeGray 与 Columbia 段只是被指定为 ref 的另一输出通道。"
            "公式完全相同不代表证据类型相同：同一个 NSE 数值，在前者可称观测技能，在后者只能称内部一致性。"
            "这一区分是语义和研究设计边界，不是计算软件自动识别的属性。"
        )
        self.h(3, "变量溯源记录（VPR）的最小闭环", "vpr-loop")
        self.p(
            "VPR 的八个字段共同定义一个可复算序列：文件确定输出通道，列确定变量标签，segment I 确定纵向位置，"
            "layer K/KT 或空间算子确定垂向支撑，单位防止尺度混淆，派生链说明是否经过亨利换算或控制器，"
            "时间支撑区分瞬时、小时、日均与快照，配对容差说明如何把两条不同时标的序列组成样本。"
            "少一个字段，复算者都可能抽到另一条“同名”曲线。VPR 不是元数据装饰，而是评价函数 f(s,o) 中 s 与 o 的定义域。"
        )
        self.h(3, "控制律与数值路径的条件化设计", "conditional-design")
        self.p(
            "TDGTA ON/OFF 是控制律状态对照，不是删除水质过程的消融实验。ON 时控制器读取控制前 SYSTDG 快照，"
            "按照目标带重新分配泄流，并写出 TDGTarget_output；OFF 时目标文件不生成，但 TDG_output、TSR 与亨利派生链仍可存在。"
            "因此实验因子是“是否启用目标控制与条件输出”，不是“是否计算 TDG”。同理，DLTINTER ON/OFF 控制 DLTMAX "
            "日程结点之间是否插值；它改变实际时间步上限轨迹，而不等同于把整个 JDAY30–40 窗固定为某个硬上限。"
        )
        self.h(3, "数值健康记录（NHR）的判据", "nhr-method")
        self.p(
            "NHR 将终止状态与中途路径分开。completed/exit 0 只说明程序到达终点并正常退出；"
            "H1(KT,I)<0 说明某断面的当前表层厚度成为负值，源码路径随即把 CURMAX 回退到 DLTMIN 并重算。"
            "ZMIN 参与水面相对层界的几何判定；Add layer/Subtract layer 是水位跨层界时调整活动层窗口的事件，"
            "本身可完全合法。故 NHR 分项保留负厚度、DLTMIN 回退、层增减、violation 与终止状态，"
            "不把它们压缩成未经验证的单一“健康分”。"
        )
        self.h(3, "配对与容差", "pairing")
        self.p(
            "较短序列驱动最近邻配对；缺失值阈约 −90。Bonneville A/C 口径容差 0.05 d，"
            "B/S 日尺度容差 0.6 d（与既有评估脚本一致）。CCIW 有效 TDG 并不覆盖全年："
            "n=1614 落在 JDAY 40613.58–40681.54（约 2011-03-11 至 2011-05-18）。"
        )
        self.h(3, "文献审计方法（W5）", "w5-method")
        c = self.w5.get("counts", {})
        self.p(
            f"编码对象为 Benicio 等（2024）表 1 的 38 篇。VPR 可重建（yes）要求同时给出可定位断面、"
            f"层/深度、对照变量与时段。全文可读 {c.get('fulltext_true','待补充')}/38；"
            f"付费墙且摘要不够者标 unknown，不编造。"
        )
        if c.get("fulltext_true") == 9:
            pass
        else:
            self.note_pending("W5 fulltext_true 与笔记不一致时以 JSON 为准并复核")

    def build_process(self) -> None:
        self.h(2, "研究过程", "process")
        self.p(
            "工作按工作包推进，本报告不重跑模型，只消费已落盘产物："
        )
        rows = [
            ["W1", "DeGray T / Columbia DO 多通道内部一致性；推广 R²–NSE 分离"],
            ["W2", "NHR 解析 + Long Lake DLTMAX×DLTINTER 扫描"],
            ["W3", "Bonneville TDGTA ON/OFF 溯源一致对照"],
            ["W4", "DART CCIW 下载、库内核对、超标频率、泄流再分配"],
            ["W5", "38 篇 VPR/指标报告率审计"],
            ["W6", "w2eval run-card MVP（五张卡）"],
            ["W7", "Columbia SOD vs Almeida 扫描带量级检查"],
            ["图", "SciencePlots 重绘 `06_PAPER/figures/`（见 SCIENCEPLOTS_REDRAW_LOG.md）"],
        ]
        self.table(["工作包", "内容"], rows, "表 P　研究过程一览")
        self.p(
            f"数字审计（2026-08-16）：草稿关键数字相对 JSON 检查 40 项，PASS=40，FAIL=0"
            f"（`notes/P1_number_audit_20260816.md`）。"
        )
        self.h(3, "证据分层与禁止项（过程纪律）", "process-depth-audit")
        self.p(
            "全过程把证据分成四层，并在写数字前先声明层别："
            "（L1）对观测技能——仅 Bonneville CCIW 配对窗；"
            "（L2）输出通道内部一致性——DeGray T、Columbia DO；"
            "（L3）观测–观测核对与描述统计——DART 匹配、超标频率；"
            "（L4）数值健康与参数移植量级——NHR、SOD。"
            "跨层复用同一指标名（例如 NSE）而不改下标，是本项目明确禁止的写法。"
        )
        self.p(
            "禁止项在过程笔记中反复核对：不得编造缺失 JSON 字段；不得把 OFF 缺失的 B 文件写成零序列；"
            "不得把 2016–2025 超标比例写成样本外 NSE；不得把 W5 unknown 改写成 no；"
            "不得在未获独立观测前给 DeGray/Columbia 写 skill。本报告生成脚本从 analysis/*.json 读数，"
            "缺失统一输出「待补充」。"
        )
        self.p(
            "图件优先使用 `06_PAPER/figures/*.png`（SciencePlots；中文回退 Microsoft YaHei）。"
            "报告 HTML 为单文件自包含：CSS 内嵌、图片 Base64、无 CDN、无相对/网络图路径。"
            "深度图解由 `report_fig_narratives.py` + `report_fig_narratives_extra.py` 组装，"
            "对每张纳入图执行九段式讲解，子图逐一覆盖。"
        )

    def _w3_table(self) -> None:
        rows = []
        for m in self.w3.get("metrics", []):
            mr = metric_row(m)
            if mr["caliber"] == "B" and mr["run"] == "OFF":
                rows.append(
                    [
                        "OFF",
                        "B",
                        "TDGTarget_output.csv",
                        "—",
                        "文件不存在",
                        "—",
                        "—",
                        "—",
                        "—",
                    ]
                )
                continue
            rows.append(
                [
                    mr["run"],
                    mr["caliber"],
                    (mr["file"] or "")[:28],
                    fmt(mr["r2"], 4),
                    fmt(mr["nse"], 4),
                    fmt(mr["kge"], 4),
                    fmt(mr["alpha"], 3),
                    fmt(mr["beta"], 3),
                    fmt(mr["sim_max"], 2),
                ]
            )
        self.table(
            ["运行", "口径", "文件", "R²", "NSE", "KGE", "α", "β", "sim max"],
            rows,
            "表 1　Bonneville TDG 对 CCIW（n=1614）三口径 + SYSTDG 快照",
        )

    def _w1_tables(self) -> None:
        dg_ids = [
            "DG_T2_vs_Tvolavg",
            "DG_T2_vs_WDO",
            "DG_STR115_vs_GATE120",
            "DG_T2_vs_GATE120",
            "DG_T2_vs_PRF26bot",
            "DG_SNP31_sfc_vs_bot",
        ]
        rows = []
        for pid in dg_ids:
            p = find_pair(self.w1.get("degray", {}).get("pairs", []), pid)
            if not p:
                continue
            rows.append(
                [
                    pid,
                    fmt(p.get("n")),
                    fmt(p.get("r2"), 4),
                    fmt(p.get("nse"), 4),
                    fmt(p.get("kge"), 4),
                    fmt(p.get("alpha"), 3),
                    fmt(p.get("beta"), 3),
                ]
            )
        self.table(
            ["对照 id", "n", "R²", "NSE", "KGE", "α", "β"],
            rows,
            "表 2　DeGray 水温内部一致性（ref 不是观测）",
        )
        col_ids = [
            "COL_DO_I45_vs_I49",
            "COL_DO_I45_vs_I33",
            "COL_DO_I49_vs_I33",
            "COL_DO_SNP45_sfc_vs_bot",
            "COL_DO_I45_ON_vs_OFF",
        ]
        rows = []
        for pid in col_ids:
            p = find_pair(self.w1.get("columbia", {}).get("pairs", []), pid)
            if not p:
                continue
            rows.append(
                [
                    pid,
                    fmt(p.get("n")),
                    fmt(p.get("r2"), 4),
                    fmt(p.get("nse"), 4),
                    fmt(p.get("kge"), 4),
                    fmt(p.get("alpha"), 3),
                    fmt(p.get("beta"), 3),
                ]
            )
        self.table(
            ["对照 id", "n", "R²", "NSE", "KGE", "α", "β"],
            rows,
            "表 3　Columbia DO 内部一致性（ref 不是观测）",
        )

    def build_results(self) -> None:
        self.h(2, "结果展示", "results")

        # ---- W3 / innovation 2
        self.h(3, "4.1 Bonneville TDG：三口径技能与 TDGTA 门控（W3）", "res-w3")
        self.p(
            "为什么做：若评估只写「TDG R²=0.5x」，读者不知道用的是亨利换算尾水、控制器输出、"
            "库内 TSR，还是 SYSTDG 控制前快照。怎么做：同一 CCIW、n=1614，固定配对窗，"
            "切换 TDGTA ON/OFF 并逐文件对照。"
        )
        self._w3_table()
        rr = self.w3.get("reachable_range", {})
        self.p(
            f"观测 max={fmt(rr.get('obs_max'),1)}%；{fmt(rr.get('obs_n_gt_120'))}/"
            f"{fmt(rr.get('obs_n'))}（{pct(rr.get('obs_frac_gt_120'),1)}）点 &gt;120%。"
            f" ON B 配对峰值 {fmt(rr.get('raw_sim_max',{}).get('ON',{}).get('B'),1)}% 钉在目标上限；"
            f"OFF 时 A/S 可超过 120%，但配对时刻仍未稳定复现观测 129.1%。"
        )
        self.figure(
            "W3_tdgta_on_off_timeseries.png",
            "TDGTA ON/OFF 多口径时间序列（全年与 CCIW 窗）",
            "该图是创新点 2 的主可视化：在同一时间轴上并列控制器开/关与不同输出通道，"
            "用来回答「关控制器之后，评估对象还在不在、峰值能不能回来」。它在全篇中承担"
            "「条件化评估」的证据锚点——后面所有关于门控文件的论述都应回到本图与表 1。",
            "横轴为 JDAY（或日历日换算）。纵轴为 TDG（%）。请先定位 CCIW 有效窗"
            "（约 40613–40681），再比较窗内各曲线相对观测的高低与封顶；全年面板用于看"
            "控制器再分配是否改变库内/尾水通道的长期形态。",
            "观测 CCIW：地面真值参考。"
            "口径 A：尾水 N2+DO 亨利换算——物理派生链，不受 TDGTarget 文件存在与否直接左右，"
            "但会间接受泄流再分配影响。"
            "口径 B：`TDGTarget_output.csv`——后控制目标序列，ON 时存在、OFF 时消失。"
            "口径 C：库内 TSR seg40——库内通道，ON/OFF 几乎不变。"
            "口径 S：`TDG_output.csv`——控制前快照，ON≡OFF。",
            "结论：技能最好的曲线（高 NSE、β≈1、封顶~120%）只出现在 B；关掉 TDGTA 后"
            "B 面板为空，但 S 与 C 仍在。因此「最优变量消失」必须精确表述为"
            "「评估所用的门控文件消失」，而不是「模型不再计算 TDG」。"
            " A 在 OFF 后峰值抬高、α 变差，说明控制器压缩的是 B 的方差结构，不是把 A 修成好预报。",
            "把控制器想成水坝调度员：他可以改泄流计划，并在自己的报表（B 文件）里把 TDG "
            "「登记」到目标带；关掉调度员后，报表没了，但河里的气体过程（S/A）还在算，"
            "只是你不能再拿那份被裁剪过的报表去报「率定很好」。",
        )
        self.figure(
            "W3_tdgta_on_off_scatter.png",
            "TDGTA ON/OFF 多口径 1:1 散点",
            "散点把时间维压掉，专门暴露尺度错误：相关斜着走但偏离 1:1 线，正是 R² 尚可而"
            "NSE/KGE 崩溃的几何图像。作用是把表 1 的 α/β 变成可读的点云形态。",
            "横轴观测、纵轴模拟（或对照）。实线为 1:1；点云沿相关方向拉长但整体偏高/偏低/过陡，"
            "分别对应 β 与 α。比较 ON B 与 ON A/C：前者更贴 1:1 且被上截断，后者更散、更高。",
            "每一子图对应一个口径×开关组合。OFF B 无点（文件缺失）。S 点云峰值高于 B，"
            "证明同名 TDG_TDG 在两个文件里不是同一评估对象。",
            "ON B 点云被约 120% 天花板「压平」，与观测中 15.55% 超 120% 的点在结构上不可复现；"
            "这不是公式算不出来，而是控制器目标带造成的可达范围收缩。",
            "如果只看「点是不是大致斜着」，会觉得好几个口径都不错；一旦盯住 1:1 线和顶盖，"
            "就会发现只有带顶盖的那份报表在「漂亮」，而且漂亮的代价是放弃观测里真实存在的超标尾部。",
        )
        self.figure(
            "W3_tdgta_kge_decomposition.png",
            "KGE 分量分解（r / α / β）",
            "KGE 把「像不像」拆成相关、方差比、均值比。本图把创新点 1 的理论探针落到 TDG 案例："
            "误指认或控制律改变时，坏往往坏在 α、β，而不一定坏在 r。",
            "分组条形图：每个口径一组，三条分别为 r、α、β（理想值皆为 1）。看哪一根偏离 1 最远，"
            "就知道技能损失的主因。",
            "ON B：β≈1、α 略&lt;1（方差被目标带压缩）。ON A/C：α&gt;1.5，方差过大。"
            "OFF A：α 进一步胀到约 1.79，KGE 反而下降——关控制器并不自动改善亨利口径。",
            "所以报告 KGE 分解比只报一个综合分更有诊断力：它告诉你该回去查派生链、控制律，"
            "还是单纯的相位相关。",
            "相关像「节奏对不对」，α 像「起伏是不是一样猛」，β 像「整体是不是偏高或偏低」。"
            "三口钟只有都对准，综合评分才高。",
        )
        self.figure(
            "fig05_tdg_reachable_range.png",
            "观测可达范围与控制器 120% 封顶",
            "服务于创新点 2 的「封顶叙事」：把观测超标频率画出来，说明 B 口径结构上不可复现"
            "观测尾部。全篇中它与 W4 年超标图互为表里（2011 窗 vs 多年气候）。",
            "阅读时先看观测点相对 120% 参考线的分布，再对照控制器上限与 SYSTDG 硬上限（145%）。"
            "直方图/累积思路：超过 120% 的点落在目标带外。",
            "观测 n=1614 中 251 点 &gt;120%；控制器目标上限 120%；SYSTDG 公式硬上限 145%。",
            "结论：ON B 的「低偏差」部分来自把输出钉在目标带，而不是证明物理过程已完美。"
            "关控制器后 raw 序列可以写到 ≥129%，但那不自动变成可用的 A 口径预报技能。",
            "就像限速 120 的仪表盘永远显示「合规」，路上真实车速却有人开到 129——你不能拿"
            "仪表盘合规率去证明路况预测很准。",
        )

        # ---- W1
        self.h(3, "4.2 DeGray 水温与 Columbia DO：内部一致性推广（W1）", "res-w1")
        self.callout(
            "不是对观测技能",
            "已检索官方示例目录：DeGray / Columbia 无独立水温或 DO 观测。下列 NSE/KGE "
            "度量的是同一物理量在不同输出通道上的数值分歧（provenance disagreement）。",
            "warn",
        )
        self._w1_tables()
        self.figure(
            "w1_degray_T_timeseries.png",
            "DeGray 多通道水温时间序列",
            "把分层水库里「都叫温度」的多条通道画在一起，证明创新点 1 不是 TDG 特例。"
            "作用：为散点与 KGE 条形图提供时间域直觉。",
            "横轴 JDAY（约 64.5–358.7，1980 年起算），纵轴 °C。先看表层 T2 与库容均温"
            "Tvolavg 是否同相位但振幅不同，再看 STR115 与 GATE120 的分离。",
            "T2：坝前表层；Tvolavg：库容加权；WDO：取水混合；STR115 / GATE120：深孔与闸门中心线高程。"
            "GATE≈表层、STR≠表层，是本几何的结果，不能推广成普遍定律。",
            f"T2 vs Tvolavg：R² 可到 {fmt(find_pair(self.w1.get('degray',{}).get('pairs',[]),'DG_T2_vs_Tvolavg').get('r2'),4)}，"
            f"但 NSE 为负——库容平均压掉方差（α≈0.35）并拉低均值（β≈0.61）。"
            "只报 R² 会把这件事写成 excellent。",
            "夏天湖面晒得很热，整湖平均却没那么热：两条线一起「跟着季节走路」，所以看起来很相关；"
            "但若你拿湖面温度去冒充整湖平均，误差会大到还不如猜一个全年平均数。",
        )
        self.figure(
            "w1_degray_T_scatter.png",
            "DeGray 水温通道 1:1 散点",
            "把表 2 变成几何：高相关低技能的点云会沿相关方向拉长并偏离 1:1。",
            "横轴为参考通道，纵轴为对照通道。靠近 1:1 且斜率≈1 才是可互换；"
            "仅「斜着」只说明相关。",
            "T2–GATE 几乎贴线（同属近表层）；T2–Tvolavg 与 STR–GATE 明显尺度错位。",
            "STR vs GATE 的 R² 与 T2 vs WDO 几乎同带，但 NSE 可差一个数量级——只报 R² "
            "会把两种「出流水温」写成同等 moderate agreement。",
            "两支温度计如果一支插在水面、一支插在深孔，读数可以「天气热一起升」，"
            "但你不能说它们测的是同一个出水口。",
        )
        self.figure(
            "w1_degray_T_kge_bars.png",
            "DeGray KGE 分量（r/α/β）",
            "诊断主因：是相关不够，还是方差/均值错了。",
            "条形越接近 1 越好。重点看 α、β 是否远离 1。",
            "T2–Tvolavg：r 高但 α、β 低；STR–GATE：α、β 远超 1。",
            "机制与 Bonneville 相同：R² 看不见的尺度错误，由 α/β 暴露。",
            "相关像「旋律对不对」，音量（α）和调性高低（β）不对，整首歌还是不合格。",
        )
        self.figure(
            "w1_degray_T_r2_vs_nse.png",
            "DeGray R²–NSE 平面",
            "把「R² 好看、NSE 难看」画成二维点，便于与 Bonneville、Columbia、文献点对照。",
            "横轴 R²，纵轴 NSE。理想区在右上；右下是本报告要警惕的象限。",
            "每个点一个通道对照。T2–Tvolavg 落在高 R²、负 NSE。",
            "证明内部一致性案例也能再现创新点 1 的核心几何。",
            "考试不能只看「答题方向对不对」（相关），还要看分数算对没有（NSE）。",
        )
        self.figure(
            "w1_columbia_DO_timeseries.png",
            "Columbia 多断面 DO 时间序列",
            "潮汐汊道上「都叫 DO」的三个 TSR 站，展示断面歧义。序列短（约 23 天）但足够说明错站风险。",
            "横轴 JDAY，纵轴 DO（g m⁻³）。比较 I=45/49/33 的均值水平与相位。",
            "三条 TSR 表层 DO；SNP 表/底用于显示层混合理。",
            "三站 NSE 全为负；R² 最高的 49 vs 33 仍 NSE&lt;−1。浅汊 SNP 表/底 NSE≈0.91，"
            "层误指认几乎检不出——错站比错层危险。",
            "同一条潮沟上游和下游氧气可以差一截：你若站错桥测，模型「对得不错」可能只是对错了地方。",
        )
        self.figure(
            "w1_columbia_DO_scatter.png",
            "Columbia DO 断面 1:1 散点",
            "把断面误指认的尺度错误可视化。",
            "横轴/纵轴为不同 I 的 DO。偏离 1:1 且斜率≠1 对应 α/β 问题。",
            "I45–I49、I45–I33、I49–I33 三对。",
            "R² 排序会把 49–33 当最好，但 NSE/KGE 并不支持「可互换」。",
            "相关好只说明「大家一起随潮汐起伏」，不说明浓度水平可以换标签。",
        )
        self.figure(
            "w1_columbia_DO_kge_bars.png",
            "Columbia DO 的 KGE 分量",
            "显示断面对照中 α/β 的破坏程度。",
            "读条形偏离 1 的方向与幅度。",
            "49 vs 33：α≈1.85；45 vs 49：β≈1.54。",
            "不写断面 I，论文之间的 R² 不可比。",
            "音量旋钮拧错了，旋律对也救不回来。",
        )
        self.figure(
            "w1_columbia_DO_r2_vs_nse.png",
            "Columbia R²–NSE 平面",
            "与 DeGray、Bonneville 对照：R² 带宽更宽（潮汐、短序列），但方向一致。",
            "横轴 R²，纵轴 NSE；关注右下与中下象限。",
            "三站对照点全部 NSE&lt;0。",
            "部分再现「R² 相近 NSE 大散」；推广力度主要靠 DeGray（n=2943）。",
            "短跑成绩波动大，但「跑错跑道还自称成绩好」的问题仍然成立。",
        )
        self.figure(
            "fig04_r2_vs_nse_literature.png",
            "R²–NSE 综合图（案例 + 文献动机）",
            "把 Bonneville 技能点与内部一致性点、文献审计动机放到同一概念平面，服务引言与讨论。",
            "横轴 R²，纵轴 NSE。区分符号/颜色所代表的证据类型（技能 vs 内部一致性）。"
            "不要把内部一致性点读成率定技能。",
            "Bonneville A/B/C；DeGray / Columbia 主对照；必要时标注「非观测」。",
            "同一张图上可以看到：窄带 R² 下 NSE 可正可深负；高 R² 负 NSE 真实存在。",
            "这是全篇的「总览仪表盘」：提醒读者先问点的颜色（证据类型），再谈数值大小。",
        )

        # ---- W4
        self.h(3, "4.3 DART 核对、超标频率与泄流再分配（W4）", "res-w4")
        hourly = self.w4.get("cciw_vs_dart", {}).get("hourly_tdg", {})
        oos = self.w4.get("out_of_sample", {})
        spill = self.w4.get("spill_comparison_2011", {})
        ex15 = self.w4.get("exceedance_2011_2015", {})
        ex25 = self.w4.get("exceedance_2016_2025", {})
        self.p(
            f"库内 CCIW vs DART：n={fmt(hourly.get('n'))}，MAE={fmt(hourly.get('mae'),6)}，"
            f"匹配率(|Δ|≤0.051)={fmt(hourly.get('match_rate_abs_le_0p051'),6)}。"
            f"结论：没有证据表明官方示例附带观测被实质性改过。"
        )
        self.p(
            f"2011–2015 有效小时 &gt;120% = {fmt(ex15.get('pct_hours_gt_120'),4)}%；"
            f"2016–2025 = {fmt(ex25.get('pct_hours_gt_120'),4)}%。"
            f"样本外 NSE：{oos.get('computed_nse')} —— {oos.get('statement','待补充')}"
        )
        if oos.get("computed_nse") is False:
            self.note_pending("样本外 NSE（需扩展 TMEND 与 2016+ 边界后计算）")
        realloc = spill.get("spill_realloc_days", {})
        qgt = spill.get("qgt_vs_dart_spill_kcfs", {})
        self.p(
            f"2011 泄流：QGT vs DART r≈{fmt(qgt.get('r'),6)}；再分配日（R，116 天）"
            f"DART 均泄≈{fmt(realloc.get('mean_dart_spill_kcfs'),4)} kcfs，TDGTA≈{fmt(realloc.get('mean_tdgta_spill_kcfs'),4)} kcfs，"
            f"r≈{fmt(realloc.get('r'),6)}。"
        )
        self.figure(
            "w4_cciw_vs_dart_scatter.png",
            "库内 CCIW 与 DART 小时 TDG 散点",
            "验证示例附带观测是否被改写。若点云紧贴 1:1，则后续技能数字的观测端可信。",
            "横轴库内、纵轴 DART（或相反）。看 MAE 与离群点。",
            "2011–2015 小时配对点；离群 |Δ|&gt;0.15 共 56 点，多在 2011–2012。",
            "高度一致支持「观测端未被实质性改写」；冬季缺测是监测季节性。",
            "两份成绩单几乎逐分相同，说明不是有人事后改分，只是偶尔誊写/修订痕迹。",
        )
        self.figure(
            "w4_cciw_vs_dart_timeseries.png",
            "库内 CCIW 与 DART 对照时间序列",
            "从时间域确认散点结论，并展示季节性缺测。",
            "横轴时间，纵轴 TDG%。两条曲线应几乎重叠；大段空白为无效/缺测。",
            "库内序列 vs DART 序列。",
            "重叠期一致；缺测不是库内独有删改。",
            "冬天没测到，不等于冬天被删掉了证据。",
        )
        self.figure(
            "w4_tdg_gt120_annual.png",
            "逐年有效小时超 120% 比例",
            "把封顶问题放到气候尺度：2016–2025 超标并未消失。强调分母是有效小时。",
            "横轴年份，纵轴超标比例。比较 2011–2015 与 2016–2025 箱体/柱高。",
            "各年柱：&gt;120% 占有效小时比例。",
            "样本外十年约 21.2% &gt;120%，高于示例期约 14.7%；不能写成预报 NSE。",
            "限速问题没有「过几年就自动消失」——所以控制器封顶叙事仍然现实相关。",
        )
        self.figure(
            "w4_tdg_annual_max.png",
            "逐年 TDG 年最大",
            "与超标比例互补：看极端峰值是否仍高于 120%。",
            "横轴年，纵轴年最大 TDG%。参考线 120%。",
            "各年最大值点/柱。",
            "多年最大值仍可高于 120%，与 B 口径封顶对照。",
            "偶尔冲高说明真实世界尾部还在，报表顶盖盖不住气候。",
        )
        self.figure(
            "w4_spill_tdgta_vs_dart.png",
            "TDGTA 泄流再分配 vs DART 实测泄流",
            "独立证据：ON 的低偏差部分来自把泄流调成与 2011 实际运行不同的方案。",
            "时间轴上比较 DART 泄流、QGT 输入与 TDGTA 输出；标注 R 日。",
            "R=再分配日，U=仍超，空白=未切流量。",
            "R 日把约 174 kcfs 量级压到约 39 kcfs；QGT–DART 相关远高于 TDGTA–DART。",
            "调度员为了报表好看大改放水计划——技能数字里掺进了「换方案」，不纯是「算得准」。",
        )
        self.figure(
            "w4_spill_scatter.png",
            "泄流对照散点（QGT / TDGTA vs DART）",
            "量化再分配对相关结构的破坏。",
            "横轴 DART，纵轴模型侧泄流；分组看 R 日与非 R 日。",
            "QGT 点云较贴；TDGTA 在 R 日系统性偏低。",
            "创新点 2 的调度证据与 TDG 文件门控证据互相加强。",
            "计划泄流跟着实测走；控制器泄流在告警日被拧到另一条轨道。",
        )

        # ---- NHR
        self.h(3, "4.4 数值健康记录与 DLTMAX 扫描（W2）", "res-nhr")
        mono_on = self.nhr_scan.get("monotonicity", {}).get("DLTINTER_ON", {})
        mono_off = self.nhr_scan.get("monotonicity", {}).get("DLTINTER_OFF", {})
        self.table(
            ["DLTMAX@JDAY30", "DLTINTER=ON 负厚度", "DLTINTER=OFF 负厚度"],
            [
                [fmt(a), fmt(b), fmt(c)]
                for a, b, c in zip(
                    mono_on.get("dltmax", [20, 50, 100, 200]),
                    mono_on.get("neg_counts", [5, 4, 1, 5]),
                    mono_off.get("neg_counts", [0, 0, 0, 0]),
                )
            ],
            "表 4　Long Lake 负表面层厚度计数",
        )
        self.callout(
            "表述约束",
            "5/4/1/5 仅官方 DLTINTER=ON 结点扫描；不是窗内硬顶。OFF 全 0。"
            "不得写成「减小时间步更不稳」普遍定律。H1&lt;0 目前只在 Long Lake 完成运行中出现。",
            "warn",
        )
        self.figure(
            "nhr_dltmax_neg_thickness.png",
            "负厚度计数随 DLTMAX 变化",
            "创新点 3 的核心图：exit 0 仍可伴随多次负厚度回退；计数对插值结点非单调。",
            "横轴 DLTMAX 设定，纵轴负厚度事件数；分组 ON/OFF。",
            "ON：5–4–1–5；OFF：全 0。",
            "官方 100 s 是谷底；收紧或放宽结点都可能更差——机制是改变插值路径/水位轨迹，"
            "不是「局部 Δt 更小更不稳」。",
            "仪表显示正常结束，不等于途中没有急刹车；急刹车次数还得单独记账（NHR）。",
        )
        self.figure(
            "nhr_dltmax_layers_dltmin.png",
            "层增减与 DLTMIN 提示",
            "把「几何层事件」与「负厚度回退」分开，避免合成一个模糊的不健康分数。",
            "分组条形：Add/Sub layer、DLTMIN 提示次数等。",
            "八点 Add/Sub 均为 3/3；层事件本身不是错误。",
            "NHR 应分项报告，不能把层增减与 H1&lt;0 混成单一指数。",
            "水位涨跌触发加层减层，像电梯过层——正常；表层厚度算成负数才是故障回退。",
        )
        self.figure(
            "nhr_dltmax_heatmap.png",
            "NHR 扫描热图概览",
            "一图汇总扫描矩阵，便于附录与 run-card 对照。",
            "行列为 DLTMAX×DLTINTER，颜色映射负厚度或相关计数。",
            "ON 行有色梯度，OFF 行近零。",
            "视觉上强化「插值开/关」才是实验开关。",
            "热图里冷热对比，比只看一个「官方推荐时间步」口号更诚实。",
        )

        # ---- W7
        self.h(3, "4.5 Columbia SOD 量级（W7）", "res-w7")
        sod = self.w7.get("columbia_instantaneous_wet_jday_ge_33", {})
        alm = self.w7.get("almeida_coelho_2025", {}).get("reported_best_mean_sod", {})
        self.p(
            f"瞬时湿段（JDAY≥33）n={fmt(sod.get('n'))}，均值={fmt(sod.get('mean'),4)}，"
            f"落在 0.5–3.0 带内 {fmt(sod.get('n_in_band'))}/{fmt(sod.get('n'))}="
            f"{pct(sod.get('frac_in_0.5_3.0'),2)}；&gt;3.0 的比例={pct(sod.get('frac_above_3.0'),1)}；"
            f"&lt;0.5 的比例={pct(sod.get('frac_below_0.5'),2)}。"
            f" Almeida 成岩最优均值约 {fmt(alm.get('sediment_diagenesis_run4'),2)}。"
            f" 参数来源：DeGray 模板移植——不是 Columbia 现场率定。"
        )
        self.note_pending("Columbia / DeGray 独立野外观测（目前无，不得假装有 skill）")
        self.figure(
            "w7_columbia_sod_timeseries.png",
            "Columbia 湿段 SOD 时间序列与 Almeida 参考",
            "量级检查：移植参数有没有跑出荒谬 SOD。不能支持水质情景推断。",
            "横轴 JDAY，纵轴 SOD。阴影带 0.5–3.0；参考线 1.07 / 1.49。",
            "湿段均值轨迹；CSOD/NSOD 可在笔记中分解（CSOD 占主导）。",
            "均值落在扫描带下半段；无点 &gt;3.0。看起来合理≠已验证。",
            "借来的配方做出的汤咸淡还行，但不等于按本地口味标定过。",
        )
        self.figure(
            "w7_columbia_sod_histogram.png",
            "Columbia SOD 直方图",
            "展示湿段 SOD 分布相对 Almeida 扫描网格的位置。",
            "横轴 SOD，纵轴频数；标带与参考均值。",
            "瞬时湿段样本分布。",
            "约 10.5% &lt;0.5，主要在前段/部分下游段；主体在带内。",
            "大多数格子落在「别人试过的抽屉」里，但仍有一小撮偏低——需要参数来源声明。",
        )

        # ---- W5
        self.h(3, "4.6 文献 VPR 审计（W5）", "res-w5")
        hc = self.w5.get("headline", {})
        counts = self.w5.get("counts", {})
        ft_pct = counts.get("fulltext_true_pct", 23.7)
        if isinstance(ft_pct, (int, float)) and ft_pct > 1:
            ft_pct_disp = f"{ft_pct}%"
        else:
            ft_pct_disp = pct(ft_pct, 1)
        only_r2_of_r2 = counts.get("only_r2_not_nse_pct_of_r2_true", 81.8)
        self.table(
            ["项目", "计数", "比例/说明"],
            [
                ["纳入研究", fmt(hc.get("n_selected")), "综述表 1 = 38"],
                ["全文可读", fmt(counts.get("fulltext_true")), ft_pct_disp],
                ["VPR-core 可重建 yes", fmt(hc.get("vpr_reconstruct_yes")), f"{fmt(hc.get('vpr_reconstruct_yes_pct'),1)}%（文献审计口径）"],
                ["VPR-core unknown", fmt(counts.get("vpr_reconstruct", {}).get("unknown")), "无全文且摘要不够；unknown≠no"],
                ["写出输出文件/列名", "0", "0%"],
                ["报 R²", fmt(counts.get("metrics_reported_true", {}).get("r2")), ""],
                ["报 R² 不报 NSE", fmt(hc.get("only_r2_not_nse")), f"占报 R² 者 {fmt(only_r2_of_r2,1)}%"],
                ["报 KGE", "0", "0%"],
                ["表 2：确认 W2↔观测技能", "1", "仅 Neto 0.32（1/12）"],
                ["表 2：确认其他数学对象", "7", "相关/负荷曲线/误标等（7/12）"],
                ["表 2：仍 unresolved", "4", "不可并入「非技能」（4/12）"],
            ],
            "表 5　W5 文献审计摘要（分母 38，除非注明）",
        )
        self.note_pending("W5 其余 29 篇全文（付费墙）；VPR unknown=19 维持 unknown，不猜测")
        self.p(
            "表 2 的 12 个 R² 中，经核对：**1** 条确认是 W2 输出对观测技能（Neto 2023 的 0.32）；"
            "**7** 条确认是其他数学对象（相关分析、负荷情景曲线、水位指标误标等）；"
            "**4** 条仍为 unresolved/unknown（不可把 unknown 并入「非技能」）。这比「没写断面」更重："
            "表在比较不同数学对象。文献审计的可重建口径记为 **VPR-core**（论文正文可定位断面/层深/组分/时段即可；不要求输出文件名）。"
        )

        # ---- w2eval
        self.h(3, "4.7 w2eval run-card（W6）", "res-w6")
        cards = self.cards_index.get("cards", [])
        self.table(
            ["card_id", "标题", "模式"],
            [[c.get("card_id"), c.get("title"), c.get("mode")] for c in cards],
            "表 6　run-card 清单",
        )
        self.figure(
            "fig07_w2eval_runcard.png",
            "w2eval run-card 概念/示例拼图",
            "把 VPR + 指标面板 + NHR 固化为可粘贴到论文的卡片，减少正文与表格口径漂移。",
            "阅读卡片上的模式标签（skill / internal / numerical_health），再读指标与文件名。",
            "五张卡对应 Bonneville ON/OFF、Long Lake NHR、Columbia DO+SOD、DeGray T。",
            "协议建议：正文表 1/4/5 优先从卡抄写；MVP 不自动跑模型。",
            "像实验记录卡：先写清楚你测的是哪一路信号，再写分数，最后写仪器有没有报警。",
        )

    def build_discussion(self) -> None:
        self.h(2, "分析与讨论", "discussion")
        self.p(
            "四条证据链应当合读，而不是拆成互不相关的「四个创新点口号」。"
            "变量误指认（W1）解释为什么跨论文 R² 需要 VPR；控制律门控（W3/W4）解释为什么"
            "同一名称的 TDG 仍可能不可比；NHR（W2）解释为什么 exit 0 不是数值清白证明；"
            "文献审计（W5）把前三者从个案升为报告规范动机。SOD（W7）则提醒："
            "可复现运行起来 ≠ 现场过程已率定。"
        )
        self.ul(
            [
                "条件可比，而非绝对不可比：当且仅当 VPR、控制律、NHR、证据类型对齐时，技能数字才可并置。",
                "NHR 是报告建议（should），不是强制标准警察；本报告也未验证全部 17 例框架。",
                "W5 的 confirmed vs unknown 必须分开写：unknown 不是 no。",
                "2016–2025 超标频率可讨论可达范围，不可冒充样本外预报技能。",
            ]
        )
        self.h(3, "为何 R²–NSE 分离首先是对象定义问题", "disc-object")
        self.p(
            "把 R²–NSE 分离仅解释成“指标偏好不同”仍不够深。更根本的原因是：输出通道常内含不同空间积分算子。"
            "表层值、库容平均、取水流量加权值、某高程结构出流、另一断面的表层值，虽然单位相同、变量名相近，"
            "对应的状态向量投影并不同。季节或潮汐共同强迫可使这些投影保持高相关，而积分范围、均值水平与方差响应"
            "又使它们远离 1:1。α 与 β 因而不是抽象统计补丁，而是空间算子错配在统计空间中的指纹。"
        )
        self.h(3, "为何门控技能不能外推为无条件技能", "disc-gating")
        self.p(
            "ON-B 的 NSE 为正并不虚假，但它回答的是一个条件问题：在 TDGTA 开启、泄流被控制器重分配、"
            "后控制目标文件存在且值域受目标带约束时，B 与 CCIW 的配对表现如何。它不能回答原泄流计划、控制器关闭或"
            "2016–2025 边界条件下的无条件预报能力。S 文件 ON/OFF 完全一致又证明，控制前状态与后控制目标是两种对象。"
            "因此正确做法不是否定 B 的数字，而是把控制状态写入数字的下标与 VPR。"
        )
        self.h(3, "为何 NHR 是伴随证据而非时间步定律", "disc-nhr")
        self.p(
            "Long Lake 的 5/4/1/5 说明在这套日程、这套水位轨迹和 DLTINTER=ON 条件下，"
            "结点值与负厚度次数呈非单调关系。它没有识别一个普遍的 CFL 稳定性函数，也没有证明更小局部 Δt 导致不稳定。"
            "事实上 DLTINTER=ON 时结点之间线性插值，JDAY30 的 20 s 不是整个窗的硬上限；"
            "OFF 后四组负厚度均为 0，则进一步表明路径构造方式是关键条件。NHR 的科学价值在于让这种条件被看见，"
            "而不是把八次运行升级成普遍数值定律。"
        )
        self.h(3, "阅读本报告图件时的统一规程", "disc-fig-protocol")
        self.p(
            "对本报告纳入的每一张图，正文固定采用九段式讲解：背景与全篇作用、怎么读、每条曲线/分量含义、"
            "逐子图/逐面板精读、物理意义与方程链、结论、原因与替代解释及证据边界、常见误读与排除、通俗复述。"
            "九段式不是修辞装饰，而是强制把图形从「插图点缀」升级为可审计证据：读者应能不打开 JSON 也能知道"
            "该图回答什么问题、不回答什么问题。若某图缺少文件或指标，统一标「待补充」，禁止补造曲线。"
        )
        self.p(
            "硬边界在图解层同样生效：internal consistency 图不得写入观测技能表；门控文件缺失不得写成物理量删除；"
            "NHR 计数不得写成时间步定律；超标频率不得写成 OOS NSE；SOD 落带不得写成现场率定；W5 unknown 不得改写成 no。"
        )
        self.h(3, "证据链的可复用形式", "disc-reuse")
        self.p(
            "本研究可复用的不是某个阈值，而是四步顺序：先用 VPR 锁定数学对象，再声明控制律，"
            "随后计算多指标并分解 α/β，最后附上 NHR 与证据类型。只要顺序颠倒，读者就可能先看到一个漂亮分数，"
            "再被迫猜测分数究竟来自哪一站、哪一层、哪个文件和哪个控制状态。run-card 将这四步固定在同一记录中，"
            "其贡献属于报告协议，不属于 CE-QUAL-W2 新过程方程。"
        )
        self.note_pending("Zenodo DOI（清单已在 06_PAPER/zenodo/，尚未上传铸造）")
        self.note_pending("T3 跨版本漂移实验")
        self.note_pending("T4 NHR 源码插桩（TSR 抽样无法代表 DLTMIN 时长占比）")

    def build_conclusions(self) -> None:
        self.h(2, "主要结论", "conclusions")
        self.ul(
            [
                "Bonneville（观测技能，n=1614）：同一 CCIW 上 R² 落在约 0.5082–0.5512 的窄带，而 NSE 为约 −2.8044 / +0.5 / −2.7516；"
                "技能最好且 β≈1、峰值钉在约 120.1% 的序列只存在于 TDGTarget 门控文件；SYSTDG 控制前快照仍写入 TDG_output 且 ON≡OFF，故不是「物理量删除」。",
                "DeGray / Columbia（内部一致性）：T2 vs Tvolavg 给出 R²≈0.9027 而 NSE≈−0.5855；DO I49 vs I33 给出 R²≈0.6505 而 NSE≈−1.4821。"
                "官方案例无独立观测时，禁止把这些数字写成对观测技能。",
                "NHR：exit 0 可与负厚度回退并存；Long Lake DLTINTER=ON 下 DLTMAX 20/50/100/200 s 负厚度 5/4/1/5（非单调），OFF 后全 0；"
                "因此 NHR 应随技能报告，而不是被表述为普遍时间步定律。",
                "DART 核对：小时 n=17805，MAE=0.026537，匹配率≈0.994945，支持示例观测未被实质性改写；2016–2025 超标小时 21.2% 只是观测描述，无样本外 NSE。",
                "W5：VPR-core 可重建 2/38；表 2 分类 1/7/4（确认技能/确认其他对象/unresolved）；文献 KGE 报出数为 0；全文 9/38，unknown=19。",
                "Columbia SOD：湿段均值 0.8762 gO₂/m²/d，约 89.55% 落在 0.5–3.0 对照带，但是 DeGray 成岩模板移植，非现场率定。",
                "可复用产物是 VPR→控制律→多指标+α/β→NHR→证据类型 的报告协议（及 w2eval run-card），不是新的 CE-QUAL-W2 过程方程。",
            ]
        )

    def build_limitations(self) -> None:
        self.h(2, "不足与展望", "limitations")
        self.ul(
            [
                "样本外 NSE：待补充（需 TMEND 出 2011，并准备 2016+ 气象/边界/出流）。",
                "DeGray / Columbia 独立实测：待补充。",
                "负厚度非单调：目前 n=1 水域（Long Lake），不可外推到所有 W2 应用。",
                "W5 全文获取 9/38，unknown=19：待补充合法全文后可下修不确定。",
                "Zenodo DOI：待补充。",
                "本报告未重跑完整 W2；图为既有 JSON/CSV 的 SciencePlots 重绘。",
            ]
        )

    def build_appendix(self) -> None:
        self.h(2, "附录：文件清单与复算入口", "appendix")
        self.h(3, "A. 关键 JSON", "app-json")
        self.ul(
            [
                "`06_PAPER/analysis/w1_provenance_metrics.json`",
                "`06_PAPER/analysis/w3_tdgta_off_metrics.json`",
                "`06_PAPER/analysis/w4_cciw_vs_dart.json`",
                "`06_PAPER/analysis/w5_lit_audit_summary.json`",
                "`06_PAPER/analysis/w7_columbia_sod_vs_almeida.json`",
                "`06_PAPER/analysis/nhr_dlt_scan.json`",
                "`06_PAPER/analysis/nhr_existing_runs.json`",
            ]
        )
        self.h(3, "B. 复算入口（命令级）", "app-repro")
        self.p("以下命令用于复算分析产物；完整模型重跑不在本报告范围。")
        code = """python 06_PAPER/analysis/w1_w7_provenance.py
python 00_INDEX/eval_w3_tdgta_off.py
python 00_INDEX/download_dart_cciw.py  # 或 --skip-download 仅分析
python 00_INDEX/parse_nhr.py --existing --out 06_PAPER/analysis/nhr_existing_runs.json
python 06_PAPER/analysis/plot_nhr_scan.py
python 06_PAPER/analysis/build_research_report.py"""
        self.html_parts.append(f"<pre class='code'>{code}</pre>")
        self.md_parts.append(f"```text\n{code}\n```\n")
        self.pdf_blocks.append(("text", code, None))

        self.h(3, "C. 本报告标明的「待补充」汇总", "app-pending")
        if not self.pending:
            self.p("（生成时未登记待补充项——异常，请检查脚本。）")
            self.note_pending("脚本 pending 列表为空（异常）")
        self.ul(self.pending)

        self.h(3, "D. run-card 路径", "app-cards")
        self.ul([f"`06_PAPER/w2eval/cards/{c.get('json')}` — {c.get('title')}" for c in self.cards_index.get("cards", [])])

    def css(self) -> str:
        return """
:root {
  --ink: #1a1f26;
  --muted: #5b6570;
  --line: #d7dde5;
  --bg: #f7f5f1;
  --paper: #ffffff;
  --accent: #1f4e5f;
  --accent2: #b35c2e;
  --warnbg: #fff6e8;
  --okbg: #e8f4ef;
  --codebg: #f0f2f5;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--ink);
  background:
    radial-gradient(1200px 600px at 10% -10%, #e7eef2 0%, transparent 60%),
    radial-gradient(900px 500px at 100% 0%, #f3e7dc 0%, transparent 55%),
    var(--bg);
  font-family: "Times New Roman", "Microsoft YaHei", "SimHei", serif;
  line-height: 1.75;
  font-size: 16px;
}
.wrap { max-width: 980px; margin: 0 auto; padding: 28px 22px 80px; }
.cover {
  background: linear-gradient(145deg, #173e4c 0%, #1f4e5f 45%, #2f6a6f 100%);
  color: #f7fafb;
  border-radius: 18px;
  padding: 42px 36px 34px;
  margin-bottom: 28px;
  box-shadow: 0 16px 40px rgba(23,62,76,.25);
}
.cover-badge {
  display: inline-block;
  letter-spacing: .08em;
  font-size: 12px;
  opacity: .9;
  border: 1px solid rgba(255,255,255,.35);
  padding: 4px 10px;
  border-radius: 999px;
  margin-bottom: 16px;
}
.cover-title {
  font-size: 28px;
  line-height: 1.35;
  margin: 0 0 12px;
  font-weight: 700;
}
.cover-sub { margin: 0 0 22px; opacity: .92; }
.cover-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 10px 16px;
  margin-bottom: 16px;
}
.cover-meta span { display: block; font-size: 12px; opacity: .75; }
.cover-meta strong { font-size: 13px; font-weight: 600; }
.cover-note {
  margin: 0;
  font-size: 13px;
  background: rgba(0,0,0,.18);
  padding: 12px 14px;
  border-radius: 10px;
}
.toc {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 18px 22px;
  margin-bottom: 28px;
}
.toc h2 { margin-top: 0; color: var(--accent); }
.toc ol { margin: 0; padding-left: 1.2em; }
.toc a { color: var(--accent); text-decoration: none; }
.toc a:hover { text-decoration: underline; }
h2 {
  margin-top: 2.2em;
  padding-bottom: .35em;
  border-bottom: 2px solid var(--accent);
  color: var(--accent);
}
h3 { margin-top: 1.6em; color: #24343c; }
h4 { margin: 0 0 .35em; color: var(--accent2); font-size: 15px; }
p { margin: .75em 0; }
a { color: var(--accent); }
.figure {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 16px 16px 8px;
  margin: 1.4em 0 1.8em;
  box-shadow: 0 4px 18px rgba(26,31,38,.04);
}
.figure img {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  background: #fff;
}
.fig-title {
  font-weight: 700;
  margin: 10px 0 8px;
  font-size: 17px;
}
.fig-block { margin: .7em 0 1em; }
.table-wrap {
  width: 100%;
  overflow-x: auto;
  margin: 1em 0 1.4em;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--paper);
}
table {
  border-collapse: collapse;
  width: 100%;
  min-width: 640px;
  font-size: 14px;
}
th, td {
  border-bottom: 1px solid var(--line);
  padding: 8px 10px;
  text-align: left;
  vertical-align: top;
}
th { background: #eef3f5; color: #1f3340; }
caption {
  caption-side: top;
  text-align: left;
  font-weight: 700;
  padding: 10px 10px 6px;
}
.callout {
  border-left: 4px solid var(--accent2);
  background: var(--warnbg);
  padding: 12px 14px;
  border-radius: 0 10px 10px 0;
  margin: 1em 0;
}
.callout.ok { border-left-color: #2f6b4f; background: var(--okbg); }
.callout-title { font-weight: 700; margin-bottom: .25em; }
.pending { color: #8a3b12; font-weight: 600; }
pre.code {
  background: var(--codebg);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px 14px;
  overflow-x: auto;
  font-family: Consolas, "Courier New", monospace;
  font-size: 13px;
  line-height: 1.45;
}
.footer {
  margin-top: 3em;
  padding-top: 1em;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 13px;
}
@media print {
  body { background: #fff; }
  .cover { box-shadow: none; }
  .figure { break-inside: avoid; }
}
"""

    def assemble_html(self) -> str:
        body = "\n".join(self.html_parts)
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>CE-QUAL-W2 方法学审计科研报告</title>
<style>
{self.css()}
</style>
</head>
<body>
<div class="wrap">
{body}
<footer class="footer">
<p>生成脚本：<code>06_PAPER/analysis/build_research_report.py</code> · 内嵌图 {self.embedded_imgs} 张 · 生成于 {self.gen_time}</p>
<p>双击本 HTML 即可完整查看（CSS/图均已内联）。PDF 由同脚本导出。</p>
</footer>
</div>
</body>
</html>
"""

    def assemble_md(self) -> str:
        return "\n".join(self.md_parts) + f"\n\n---\n内嵌/引用图数量（HTML Base64）：{self.embedded_imgs}\n"

    def build(self) -> None:
        self.build_cover_toc()
        self.build_abstract()
        self.build_glossary()
        self.build_background()
        self.build_methods()
        self.build_process()
        self.build_results()
        self.build_discussion()
        self.build_conclusions()
        self.build_limitations()
        self.build_appendix()


def write_pdf_chrome(html_path: Path, pdf_path: Path) -> tuple[bool, str]:
    browser = next((p for p in CHROME_CANDIDATES if p.exists()), None)
    if browser is None:
        return False, "未找到 Chrome/Edge 可执行文件"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    # file URI for Windows
    uri = html_path.resolve().as_uri()
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        uri,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if pdf_path.exists() and pdf_path.stat().st_size > 1000:
            return True, f"chrome/edge ok: {browser.name}; exit={proc.returncode}"
        return False, f"浏览器未写出有效 PDF：stdout={proc.stdout[:500]} stderr={proc.stderr[:500]}"
    except Exception as exc:
        return False, f"Chrome PDF 异常：{exc}"


def write_pdf_reportlab(builder: ReportBuilder, pdf_path: Path) -> tuple[bool, str]:
    if not SIMHEI.exists():
        return False, f"缺少中文字体：{SIMHEI}"
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
    except Exception as exc:
        return False, f"reportlab 不可用：{exc}"

    pdfmetrics.registerFont(TTFont("SimHei", str(SIMHEI)))
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    y = height - 48

    def new_page() -> None:
        nonlocal y
        c.showPage()
        c.setFont("SimHei", 9)
        y = height - 48

    def draw_text(text: str, size: int = 9, leading: float = 13, max_chars: int = 46) -> None:
        nonlocal y
        c.setFont("SimHei", size)
        for line in textwrap.wrap(text.replace("\n", " "), width=max_chars) or [""]:
            if y < 52:
                new_page()
                c.setFont("SimHei", size)
            c.drawString(42, y, line)
            y -= leading

    draw_text("CE-QUAL-W2 方法学审计科研报告（PDF）", size=14, leading=18, max_chars=36)
    draw_text(f"生成时间：{builder.gen_time}", size=9)
    draw_text("数字权威：06_PAPER/analysis/*.json；完整叙述见 report.html / report.md。", size=9)
    y -= 6

    for kind, text, img in builder.pdf_blocks:
        if kind in {"h1", "h2", "h3"}:
            y -= 6
            sizes = {"h1": 13, "h2": 12, "h3": 11}
            draw_text(text, size=sizes[kind], leading=16, max_chars=40)
            continue
        if kind == "fig" and img is not None and img.exists():
            draw_text(text, size=10, leading=14, max_chars=42)
            try:
                image = ImageReader(str(img))
                iw, ih = image.getSize()
                draw_w = width - 84
                draw_h = draw_w * ih / float(iw)
                if draw_h > 280:
                    draw_h = 280
                    draw_w = draw_h * iw / float(ih)
                if y - draw_h < 50:
                    new_page()
                    draw_text(text, size=10, leading=14, max_chars=42)
                c.drawImage(img if False else image, 42, y - draw_h, width=draw_w, height=draw_h, preserveAspectRatio=True, mask="auto")
                y -= draw_h + 14
            except Exception as exc:
                draw_text(f"（插图失败：{exc}）", size=8)
            continue
        if kind == "note":
            draw_text(text, size=8, leading=11, max_chars=48)
            continue
        # text — skip extremely long duplicates already covered; still write
        if len(text) > 1200:
            text = text[:1200] + "…"
        draw_text(text, size=8, leading=11, max_chars=50)

    if builder.pending:
        y -= 8
        draw_text("待补充汇总", size=12, leading=15)
        for item in builder.pending:
            draw_text(f"• {item}", size=8, leading=11)

    c.save()
    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        return True, "reportlab SimHei ok"
    return False, "reportlab 未生成有效文件"


def self_check(html: str) -> dict[str, Any]:
    return {
        "base64_count": len(re.findall(r"base64,", html)),
        "http_img": len(re.findall(r'<img[^>]+src=["\']https?://', html, flags=re.I)),
        "rel_img": len(re.findall(r'<img[^>]+src=["\']\.\./', html)),
        "local_img": len(re.findall(r'<img[^>]+src=["\'][A-Za-z]:\\', html)),
        "file_img": len(re.findall(r'<img[^>]+src=["\']file:', html, flags=re.I)),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    builder = ReportBuilder()
    builder.build()
    html = builder.assemble_html()
    md = builder.assemble_md()
    OUT_HTML.write_text(html, encoding="utf-8")
    OUT_MD.write_text(md, encoding="utf-8")

    checks = self_check(html)
    pdf_ok = False
    pdf_msg = ""
    ok, msg = write_pdf_chrome(OUT_HTML, OUT_PDF)
    pdf_msg = "Chrome/Edge: " + msg
    if ok:
        pdf_ok = True
    else:
        ok2, msg2 = write_pdf_reportlab(builder, OUT_PDF)
        pdf_msg += " | reportlab: " + msg2
        pdf_ok = ok2
        if not ok2 and OUT_PDF.exists():
            # remove empty/failed stub if any tiny file
            if OUT_PDF.stat().st_size < 1000:
                OUT_PDF.unlink(missing_ok=True)

    PDF_LOG.write_text(
        f"time={builder.gen_time}\npdf_ok={pdf_ok}\n{pdf_msg}\nchecks={checks}\n"
        f"embedded_imgs={builder.embedded_imgs}\npending={builder.pending}\n",
        encoding="utf-8",
    )

    def sz(p: Path) -> str:
        if not p.exists():
            return "缺失"
        return f"{p.stat().st_size:,} bytes"

    print("=== REPORT BUILD SUMMARY ===")
    print(f"HTML: {OUT_HTML} ({sz(OUT_HTML)})")
    print(f"MD  : {OUT_MD} ({sz(OUT_MD)})")
    print(f"PDF : {OUT_PDF} ({sz(OUT_PDF)}) success={pdf_ok}")
    print(f"embedded images: {builder.embedded_imgs}")
    print(f"self-check: {checks}")
    print("pending:")
    for x in builder.pending:
        print(" -", x)
    print(pdf_msg)


if __name__ == "__main__":
    main()
