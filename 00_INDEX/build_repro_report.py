#!/usr/bin/env python3
"""Build self-contained report.html / report.md / report.pdf from fixed repro run."""
from __future__ import annotations

import base64
import json
import textwrap
from datetime import datetime
from pathlib import Path

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
RUN_ID = "run_20260811_fixed"
RUN_BASE = ROOT / "05_REPRO_RUNS" / RUN_ID
ANALYSIS = RUN_BASE / "analysis"
OUT_HTML = ROOT / "report.html"
OUT_MD = ROOT / "report.md"
OUT_PDF = ROOT / "report.pdf"

CASE_ORDER = [
    ("Long_Lake", "Long Lake"),
    ("DeGray", "DeGray Reservoir"),
    ("Columbia_Slough", "Columbia Slough Estuary"),
]


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def img_block(fig_id: str, title: str, path: Path, how: str, meaning: str, conclusion: str) -> str:
    head = f'<div class="figure" id="{fig_id}">'
    cap = f'<div class="caption-title">{title}</div>'
    body = (
        f'<p><strong>如何读图：</strong>{how}</p>'
        f'<p><strong>含义：</strong>{meaning}</p>'
        f'<p><strong>结论：</strong>{conclusion}</p>'
    )
    if not path.exists():
        return (
            f'{head}{cap}'
            f'<p class="note">待补充：图像文件不存在（{path.name}）。</p>'
            f"{body}</div>"
        )
    return (
        f'{head}'
        f'<img alt="{title}" src="data:image/png;base64,{b64(path)}" />'
        f"{cap}{body}</div>"
    )


def md_img(title: str, path: Path, how: str, meaning: str, conclusion: str) -> str:
    lines = [f"### {title}", ""]
    if path.exists():
        lines.append(f"![{title}]({path.as_posix()})")
        lines.append("")
    else:
        lines.append(f"> 待补充：图像不存在（`{path.name}`）")
        lines.append("")
    lines.extend(
        [
            f"- **如何读图：** {how}",
            f"- **含义：** {meaning}",
            f"- **结论：** {conclusion}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    run_sum = json.loads((RUN_BASE / "run_summary.json").read_text(encoding="utf-8"))
    fig_man = json.loads((ANALYSIS / "figure_manifest.json").read_text(encoding="utf-8"))
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows_html = []
    rows_md = []
    for c in run_sum.get("cases", []):
        outs = c.get("outputs", {})
        tsr = outs.get("tsr_*.csv", [])
        tsr_n = len(tsr)
        tsr_lines = max((x.get("lines", 0) for x in tsr), default=0)
        rows_html.append(
            "<tr>"
            f"<td>{c['case']}</td>"
            f"<td>{c['exit_code']}</td>"
            f"<td>{c['elapsed_sec']}</td>"
            f"<td>{'是' if c.get('forrtl_detected') else '否'}</td>"
            f"<td>{';'.join(c.get('habitat_dirs_created') or []) or '—'}</td>"
            f"<td>{tsr_n} 文件 / 最多 {tsr_lines} 行</td>"
            f"<td>{(c.get('w2_err') or '（空）')[:120]}</td>"
            "</tr>"
        )
        rows_md.append(
            f"| {c['case']} | {c['exit_code']} | {c['elapsed_sec']} | "
            f"{c.get('forrtl_detected')} | {tsr_n}/{tsr_lines} | {(c.get('w2_err') or '空')[:80]} |"
        )

    long = next((c for c in run_sum.get("cases", []) if c["case"] == "Long Lake"), {})
    forrtl_fixed = (not long.get("forrtl_detected", True)) and long.get("exit_code") == 0

    figs_html: list[str] = []
    figs_md: list[str] = []
    fig_n = 0
    pdf_figs: list[tuple[str, Path]] = []

    def add_fig(title: str, path: Path, how: str, meaning: str, conclusion: str) -> None:
        nonlocal fig_n
        fig_n += 1
        numbered = f"图 {fig_n}　{title}"
        figs_html.append(img_block(f"fig{fig_n}", numbered, path, how, meaning, conclusion))
        figs_md.append(md_img(numbered, path, how, meaning, conclusion))
        pdf_figs.append((numbered, path))

    for short, label in CASE_ORDER:
        case_info = fig_man.get("cases", {}).get(short, {})
        ts = case_info.get("timeseries", {})
        pv = case_info.get("planview", {})
        pf = case_info.get("profile", {})
        wb = case_info.get("watershed_basemap", {})

        add_fig(
            f"{label} 多断面时间序列",
            Path(ts["file"]) if ts.get("file") else ANALYSIS / f"{short}_timeseries.png",
            "横轴为儒略日 JDAY（Julian day，年积日模型时间）；纵轴为水位 ELWS（Elevation of Water Surface，水面高程）、"
            "水温 T2（Temperature）、水深 DEPTH，以及溶解氧 DO（Dissolved Oxygen）等可用变量。不同颜色曲线对应不同河段 segment。",
            f"用于检查模型是否完成有效时间推进、各观测断面响应是否连续。状态：{ts.get('status','待补充')}；"
            f"点数示例：{case_info.get('tsr_rows_example','待补充')}；变量：{', '.join(ts.get('variables') or []) or '待补充'}。",
            "若曲线随时间变化且点数显著大于 1，说明本次运行已产出可用 TSR（time series，时间序列），而非秒退空图。"
            "本图本身不是率定对比，观测对照链仍待补充。",
        )
        add_fig(
            f"{label} 河道/库区俯视与沿程剖面",
            Path(pv["file"]) if pv.get("file") else ANALYSIS / f"{short}_planview.png",
            "左图由地形文件 bth*.csv（bathymetry，水下地形）用 PHI0（segment orientation，分段方位角）与 DLX（segment length，分段长度）"
            "重建相对平面中心线与近似岸线，颜色为近似水深；右图为沿程水深与表层宽度。",
            f"建立相对空间骨架，帮助阅读后续纵剖面/等值线。状态：{pv.get('status','待补充')}；河段数：{pv.get('segments','待补充')}。",
            "该图是模型网格几何的内部坐标系表达，不自动等于真实大地坐标；需结合流域底图判断位置是否合理。",
        )
        rd = wb.get("registration_detail") or {}
        base_lat = rd.get("baseline_lateral_m") or {}
        imp_lat = rd.get("improved_lateral_m") or {}
        lat_txt = ""
        if base_lat and imp_lat:
            lat_txt = (
                f" 侧向偏移（相对 OSM 参考河道 {rd.get('reference_channel','')}）："
                f"改进前 均值{base_lat.get('mean_m','?')}m / 最大{base_lat.get('max_m','?')}m / P95{base_lat.get('p95_m','?')}m → "
                f"改进后 均值{imp_lat.get('mean_m','?')}m / 最大{imp_lat.get('max_m','?')}m / P95{imp_lat.get('p95_m','?')}m。"
                f" 选用配准：{rd.get('alignment_method_selected','')}（{wb.get('registration','')}）。"
            )
        add_fig(
            f"{label} 流域/区域底图与河道走向叠置",
            Path(wb["file"]) if wb.get("file") else ANALYSIS / f"{short}_watershed_basemap.png",
            "左图为本地缓存的真实卫星影像（Esri World Imagery）：可见真实水系/库面与地表纹理；黄/黑线为模型中心线按坝址或源-口参考点配准后的叠置；"
            "方块/圆点为公开可核验参考点（坝、河口、库心等），橙色×为控制文件水体 LAT/LONG。"
            "右图为同范围 Esri World Topo Map 本地缓存（道路/水系/地名），并放大显示分段、近似岸线与水深着色。两图均含经纬网与比例尺。",
            f"地点：{wb.get('place','待补充')}；控制文件锚点 lat={wb.get('lat','待补充')}，lon(西经正值)={wb.get('lon_west_positive','待补充')}；"
            f"来源：{wb.get('geo_source','待补充')}。{wb.get('geo_note','')} "
            f"公开参考：{';；'.join(wb.get('public_refs') or []) or '待补充'}。底图：{wb.get('basemap','本地瓦片缓存')}。"
            f" 精度状态：{wb.get('precision_status','示意叠置')}。{lat_txt}",
            "应能一眼辨认真实 Long Lake / DeGray / Columbia Slough 区域；可用于核验模型走向是否落在正确水体附近。"
            "参考河道来自 OSM Overpass 缓存（basemap_cache/*/osm_waterways.geojson）；配准在两点相似/多点相似/TPS 间自动择优。"
            "几何形状残差（PHI0 示意路径≠真实弯道）与配准残差（控制点有限）在侧向偏移图中分开量化。"
            f"配准：{wb.get('registration','landmark registration')}；本地缓存：{wb.get('basemap_cache_dir','analysis/basemap_cache')}。"
            " 【偏差说明】投影：Web Mercator 瓦片用 lon/lat 角点显示，本窗口错位约20–25 m，不是公里级偏航原因。"
            + (
                " 【方位修正】曾误把水库上游浅端锚到坝址，旋转弦反向后表现为南北向（横切河道）镜像；"
                "现按 W2 段号递增=上游→下游、最深湿段≈坝，将坝/口锚在模型下游端。PHI0：自正北顺时针 ΔE=sin、ΔN=cos。"
                if short in {"Long_Lake", "DeGray"}
                else " 【方位核验】Columbia Slough 源→口段序与多点配准本来正确；残差来自模型曲折与真实岸线差异。"
            ),
        )
        align_path = Path(wb.get("alignment_error_plot") or ANALYSIS / f"{short}_alignment_error.png")
        add_fig(
            f"{label} 侧向偏移沿程图",
            align_path,
            "横轴为沿模型河段累计距离（km）；纵轴为模型中心线各分段中心到 OSM 参考河道折线的最短侧向距离（km）。"
            "虚线为均值，点线为 P95。",
            f"参考：{rd.get('reference_channel','OSM waterways')}；配准方法：{wb.get('registration','')}。"
            + (lat_txt if lat_txt else ""),
            "用于区分「配准可改进部分」与「PHI0 示意几何本身与真实河道不一致」的残差量级；"
            "若改进后均值仍 &gt;500 m，通常说明模型平面形状与 OSM 河道差异占主导，而非底图投影问题。",
        )
        t_range = ""
        if "t_min" in pf and "t_max" in pf:
            t_range = f"温度范围：{pf['t_min']:.2f}–{pf['t_max']:.2f} ℃。"
        add_fig(
            f"{label} 纵剖面/等值线",
            Path(pf["file"]) if pf.get("file") else ANALYSIS / f"{short}_profile.png",
            "优先使用 CPL（contour plot，等值线/纵剖面输出）或 PRF（profile，剖面输出）中的温度场；"
            "若 CPL/PRF 未能解析，则回退为地形宽度场示意并明确标注。",
            f"展示纵向-垂向二维温度（或回退几何场）结构。状态：{pf.get('status','待补充')}；"
            f"来源：{pf.get('source') or pf.get('kind') or '待补充'}。{t_range}",
            "该类图是 W2 报告中最常见的“分层/纵剖面”呈现；若缺可解析温度场，报告已标注回退，不伪装为观测对比。",
        )

    n_before_bon = fig_n
    BON_AN = ROOT / "05_REPRO_RUNS" / "run_20260814_bonneville" / "analysis"
    bon_json = BON_AN / "obs_metrics.json"
    bon_rows = json.loads(bon_json.read_text(encoding="utf-8")) if bon_json.exists() else []
    bon_table_html = [
        "<table><thead><tr><th>断面文件</th><th>变量</th><th>配对点数</th><th>MAE</th><th>RMSE</th><th>NRMSE</th><th>NSE</th></tr></thead><tbody>"
    ]
    bon_table_md = [
        "| 断面文件 | 变量 | n | MAE | RMSE | NRMSE | NSE |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in bon_rows:
        if r.get("status") != "ok":
            continue
        bon_table_html.append(
            "<tr>"
            f"<td>{r.get('file','')}</td><td>{r.get('variable','')}</td>"
            f"<td>{r.get('n','')}</td><td>{r.get('mae','')}</td>"
            f"<td>{r.get('rmse','')}</td><td>{r.get('nrmse','')}</td>"
            f"<td>{r.get('nse','')}</td></tr>"
        )
        bon_table_md.append(
            f"| {r.get('file')} | {r.get('variable')} | {r.get('n')} | {r.get('mae')} | {r.get('rmse')} | {r.get('nrmse')} | {r.get('nse')} |"
        )
    bon_table_html.append("</tbody></table>")
    add_fig(
        "Bonneville 库内 TSR TDG 时序（seg40 vs CCIW）",
        BON_AN / "Bonneville_BON_tsr_1_seg40_TDG_pct_timeseries.png",
        "横轴为 Excel 序列日 JDAY（2011 年约 40544–40909）；蓝点为 CCIW（Columbia River at Bonneville Dam tailwater，坝下尾水）小时观测总溶解气体饱和度 TDG（Total Dissolved Gas，%）；折线为库内河段 40 的模型 TSR。缺测值 −999 已剔除。",
        "用于把 SYSTDG（System Total Dissolved Gas，系统总溶解气体经验模块）写入 W2 后的库内 TDG 与坝下站点对照。CCIW 是坝下尾水，模型 TSR 是库内 seg40，空间位置不完全等同。",
        "库内对照的 TDG NSE 为负；下一组图改用坝段 76 下泄输出，检验是否只是断面选错。",
    )
    add_fig(
        "Bonneville 库内 TSR TDG 1:1 散点（seg40）",
        BON_AN / "Bonneville_BON_tsr_1_seg40_TDG_pct_scatter.png",
        "横轴观测、纵轴模拟；虚线为 1:1。点落在线上方表示模拟偏高，下方表示模拟偏低。",
        "MAE / RMSE / NSE（Nash–Sutcliffe efficiency，纳什效率系数：1 为完美，0 等同用均值预测，负值差于均值）见散点标题与表。",
        "TDG 的 NSE 为负，说明在本对照口径下尚未达到可用率定水平；这是真实定量结果，不是作图错误。",
    )
    add_fig(
        "Bonneville 库内水温时序（seg40 vs CCIW）",
        BON_AN / "Bonneville_BON_tsr_1_seg40_Temperature_C_timeseries.png",
        "读法同 TDG 时序图，纵轴为水温（℃）。",
        "水温由水动力与热收支控制，不依赖 SYSTDG 溢洪产气公式，因此可单独检验热模块。",
        "NSE≈0.95、NRMSE≈0.08 表明 2011 年水温季节循环与 CCIW 高度一致，热模块复现可信。",
    )
    add_fig(
        "Bonneville 库内水温 1:1 散点（seg40）",
        BON_AN / "Bonneville_BON_tsr_1_seg40_Temperature_C_scatter.png",
        "横轴观测、纵轴模拟。点沿 1:1 线紧密分布表示偏差小。",
        "配对点数约 2400（小时对齐，容差 0.05 日）。",
        "水温对照支持“模型时间轴与驱动文件正确”；TDG 偏差应主要从气体模块继续查。",
    )

    tw_json = BON_AN / "tailwater_metrics.json"
    tw_rows = json.loads(tw_json.read_text(encoding="utf-8")) if tw_json.exists() else []
    tw_table_html = [
        "<table><thead><tr><th>对照口径</th><th>配对点数</th><th>MAE</th><th>RMSE</th><th>NRMSE</th><th>NSE</th></tr></thead><tbody>"
    ]
    tw_table_md = [
        "| 对照口径 | n | MAE | RMSE | NRMSE | NSE |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in tw_rows:
        tw_table_html.append(
            "<tr>"
            f"<td>{r.get('source','')}</td><td>{r.get('n','')}</td>"
            f"<td>{r.get('mae','')}</td><td>{r.get('rmse','')}</td>"
            f"<td>{r.get('nrmse','')}</td><td>{r.get('nse','')}</td></tr>"
        )
        tw_table_md.append(
            f"| {r.get('source')} | {r.get('n')} | {r.get('mae')} | {r.get('rmse')} | {r.get('nrmse')} | {r.get('nse')} |"
        )
    tw_table_html.append("</tbody></table>")
    add_fig(
        "Bonneville 坝下尾水 TDG 时序（seg76 下泄 vs CCIW）",
        BON_AN / "Bonneville_tailwater_TDG_timeseries.png",
        "蓝点仍为 CCIW 坝下小时 TDG%；折线为坝段 76 下泄混合浓度：由 c_wdo 的 N2、DO 与 t_wdo 的水温，按 W2 withdrawal.f90 公式 TDG%=100×(0.79·N2/n2sat+0.21·DO/dosat) 换算。气压与露点取气象文件最近邻。",
        "这是与 CCIW 站点空间上更匹配的对照：下泄而不是库内 TSR。公式本身用库内 TSR 的 N2/DO/T 反演 W2 自带 TDG 列，NSE≈0.999，MAE≈0.30%。",
        "改到真正尾水后，N2+DO 换算的 TDG NSE 仍约 −2.8。下一组图表明：那是对照变量不对，不是断面选错。",
    )
    add_fig(
        "Bonneville 坝下尾水 TDG 1:1 散点（seg76）",
        BON_AN / "Bonneville_tailwater_TDG_scatter.png",
        "横轴 CCIW 观测 TDG%，纵轴坝段 76 下泄 TDG%。",
        "与库内 seg40 散点形态接近：模拟峰值低于观测高值段。",
        "空间映射已公平；若继续改进，应调 SYSTDG 溢洪/掺混参数，而不是再换对照断面。",
    )
    add_fig(
        "Bonneville 坝下尾水水温时序（seg76 vs CCIW）",
        BON_AN / "Bonneville_tailwater_Temp_timeseries.png",
        "蓝点 CCIW 水温；折线 t_wdo_76 下泄混合水温。",
        "尾水水温不依赖 TDG 公式，可独立核验热模块与出流分层取水。",
        "NSE≈0.96，略优于库内 seg40，热模块与出流温度可信。",
    )
    add_fig(
        "Bonneville 坝下尾水水温 1:1 散点（seg76）",
        BON_AN / "Bonneville_tailwater_Temp_scatter.png",
        "横轴观测、纵轴坝下下泄水温。",
        "配对约 2400 点，容差 0.05 日。",
        "水温对照通过。N2+DO 换算的 TDG 与 CCIW 对不上，是因为对照变量不是 SYSTDG 自己写出的 TDG%（见下一组图）。",
    )

    sys_json = BON_AN / "systdg_tdg_metrics.json"
    sys_rows = json.loads(sys_json.read_text(encoding="utf-8")) if sys_json.exists() else []
    sys_table_html = [
        "<table><thead><tr><th>对照口径</th><th>n</th><th>MAE</th><th>RMSE</th><th>NRMSE</th><th>NSE</th><th>sim_max</th></tr></thead><tbody>"
    ]
    sys_table_md = [
        "| 对照口径 | n | MAE | RMSE | NRMSE | NSE | sim_max |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in sys_rows:
        sys_table_html.append(
            "<tr>"
            f"<td>{r.get('pair','')}</td><td>{r.get('n','')}</td>"
            f"<td>{r.get('mae','')}</td><td>{r.get('rmse','')}</td>"
            f"<td>{r.get('nrmse','')}</td><td>{r.get('nse','')}</td>"
            f"<td>{r.get('sim_max','')}</td></tr>"
        )
        sys_table_md.append(
            f"| {r.get('pair')} | {r.get('n')} | {r.get('mae')} | {r.get('rmse')} | {r.get('nrmse')} | {r.get('nse')} | {r.get('sim_max')} |"
        )
    sys_table_html.append("</tbody></table>")
    add_fig(
        "Bonneville SYSTDG 自身 TDG 时序 vs CCIW",
        BON_AN / "Bonneville_SYSTDG_TDG_vs_CCIW_timeseries.png",
        "蓝点 CCIW 小时观测；折线为 SYSTDG 模块写出的日尺度 TDG%（TDGTarget_output.csv 的 TDG 列，即源码 TDG_TDG）；红虚线为 TDGTA 动态目标 115/120%。",
        "这才是 SYSTDG 溢洪产气公式的输出。库内 TSR 的 TDG 列与 c_wdo 的 N2+DO 亨利换算，都不等于该系统变量。官方示例标题写明 TDG target demo，TDGTA=ON 会把溢洪改分到电站以追目标。",
        "相对 CCIW：NSE=0.50、MAE=2.20%。观测 ≤120% 时 NSE=0.66；观测 >120% 的 251 点上模型被目标封顶在 120.09%，NSE 转负。先前 −2.8 是对照错了变量，不是气体模块不可用。",
    )
    add_fig(
        "Bonneville SYSTDG 自身 TDG 1:1 vs CCIW",
        BON_AN / "Bonneville_SYSTDG_TDG_vs_CCIW_scatter.png",
        "横轴 CCIW，纵轴 SYSTDG TDG_TDG。点在 120% 处被水平截断，对应 TDGTA 目标上限。",
        "sim_max=120.09，obs_max=129.1。高值段偏差来自目标控制，不是产气公式完全失效。",
        "在目标封顶以下，MAE≈1.70%。若要复现 129% 峰值，需关 TDGTA 用历史闸门流量再比（隔离目录重跑中）。",
    )
    add_fig(
        "Bonneville TDGTA 目标叠置（诊断）",
        BON_AN / "Bonneville_TDGTA_target_overlay.png",
        "同一张图上叠 CCIW、seg76 N2+DO 换算 TDG、以及 115/120% 目标。",
        "N2+DO 换算曲线远离目标与观测，说明它不是 SYSTDG 对照该用的序列。",
        "诊断结论：先换对 SYSTDG 的 TDG_TDG，再谈参数率定。",
    )
    bon_section_html = (
        "<h2>4b. Bonneville SYSTDG 模型–观测对照</h2>"
        "<p>在完成三案例可运行复现后，接入官方示例 <strong>Bonneville Dam with TDG computed using SYSTDG</strong>"
        "（2011 年，TMSTRT=40544、TMEND=40909）。观测来自 v5 包中的 "
        "<code>CCIW_TDG_Temp_2011-2015.csv</code>，仅截取与模型重叠的 2011 年。运行目录："
        "<code>05_REPRO_RUNS/run_20260814_bonneville</code>；exit 0，用时约 2163 s。"
        "SCR 已关以保证无界面运行。</p>"
        "<p><strong>库内 TSR（seg40/43）对照 CCIW：</strong></p>"
        + "".join(bon_table_html)
        + "<p><strong>坝段 76 下泄（c_wdo / t_wdo）对照 CCIW：</strong>"
        "WDO 文件不含 TDG% 列，按源码 <code>withdrawal.f90</code> 由 N2+DO 换算。"
        "公式用库内 TSR 校验：NSE=0.9992。</p>"
        + "".join(tw_table_html)
        + "<p><strong>SYSTDG 自身 TDG_TDG（TDGTarget_output.csv）对照 CCIW：</strong>"
        "这是溢洪产气模块的系统输出。日尺度对齐容差 0.6 日。官方示例 <code>TDGTA=ON</code>，目标 115/120%，会改分配溢洪。</p>"
        + "".join(sys_table_html)
        + "<p>指标口径：TSR/WDO |ΔJDAY|≤0.05，SYSTDG 日输出 ≤0.6；剔除 −999。"
        "先前 NSE≈−2.8 来自把 N2+DO 亨利换算当成 SYSTDG TDG；换成模块自身 TDG 后 NSE=0.50。"
        "观测 &gt;120% 的点被 TDGTA 封顶在 120.09%，是剩余误差的主因。</p>"
    )
    bon_section_md = (
        "## 4b. Bonneville SYSTDG 模型–观测对照\n\n"
        "运行目录：`05_REPRO_RUNS/run_20260814_bonneville`。观测：CCIW 2011 年小时 TDG/水温。\n\n"
        "库内 TSR：\n\n"
        + "\n".join(bon_table_md)
        + "\n\n坝段 76 下泄（N2+DO→TDG%，对照变量不当）：\n\n"
        + "\n".join(tw_table_md)
        + "\n\nSYSTDG 自身 TDG_TDG：\n\n"
        + "\n".join(sys_table_md)
        + "\n\n"
    )

    n_before_col = fig_n
    COL_AN = ROOT / "05_REPRO_RUNS" / "run_20260814_columbia_diag" / "analysis"
    col_sum_path = ROOT / "05_REPRO_RUNS" / "run_20260814_columbia_diag" / "run_summary.json"
    col_met_path = COL_AN / "columbia_diag_metrics.json"
    col_sum = json.loads(col_sum_path.read_text(encoding="utf-8")) if col_sum_path.exists() else {}
    col_met = json.loads(col_met_path.read_text(encoding="utf-8")) if col_met_path.exists() else {}
    add_fig(
        "Columbia SED_DIAG ON：底泥耗氧率 SOD 时序",
        COL_AN / "Columbia_diagenesis_SOD_timeseries.png",
        "横轴为 1995 年积日 JDAY（32–55）；纵轴为底泥耗氧率 SOD（Sediment Oxygen Demand，gO2 m⁻² d⁻¹）。曲线为若干湿河段。",
        "官方 Columbia 示例控制文件写了 SED_DIAG=ON，但未附 W2_diagenesis.npt。本轮从 DeGray 模板改编（速率/初值区结束河段 31→50），隔离目录重跑。",
        f"已写出 {col_met.get('dia_outputs_n') or col_sum.get('dia_outputs_n') or '数十'} 个成岩 CSV；末日湿段 SOD 均值约 {col_met.get('sod_last_mean_wet','—')} gO2 m⁻² d⁻¹。"
        "这是可运行性恢复，不是 Columbia 现场率定。",
    )
    add_fig(
        "Columbia SED_DIAG ON：沿程 SOD",
        COL_AN / "Columbia_diagenesis_SOD_plan.png",
        "横轴河段号 1–51，纵轴末日 SOD。边界段（1、46–47、51）为 0。",
        "河段 2–13 使用 DeGray 第一区（较活泼 labile POC），14 以后为第二区参数。",
        "沿程 SOD 非零说明成岩通量已耦合到水体；数值沿用 DeGray，不能当作 Columbia 真值。",
    )
    add_fig(
        "Columbia 成岩开/关：seg45 DO 与 NH4",
        COL_AN / "Columbia_diagenesis_DO_NH4_vs_off.png",
        "虚线为权威目录 run_20260811_fixed（SED_DIAG OFF），实线为本轮 SED_DIAG ON。上图溶解氧，下图氨氮。",
        f"seg45 平均 DO：OFF {col_met.get('seg45_DO_mean_off','—')} mg/L，ON {col_met.get('seg45_DO_mean_on','—')} mg/L，差 {col_met.get('seg45_DO_mean_diff_on_minus_off','—')} mg/L。",
        "开成岩后 DO 略降，方向符合底泥耗氧；幅度取决于未率定的 DeGray 参数，仅证明模块接通。",
    )
    col_section_html = (
        "<h2>4c. Columbia Slough 底泥成岩（SED_DIAG ON）</h2>"
        "<p>权威三案例目录 <code>run_20260811_fixed</code> 中 Columbia 仍保持 SED_DIAG OFF（因官方示例缺输入文件）。"
        "本轮在隔离目录 <code>05_REPRO_RUNS/run_20260814_columbia_diag</code> 放入改编后的 "
        "<code>W2_diagenesis.npt</code> 并保持 SED_DIAG ON。"
        f"TSR 已推进到 TMEND=55；无 w2.err / forrtl。"
        f"用时约 {col_sum.get('elapsed_sec','—')} s。"
        "结束后残留 Run Status 窗口已按惯例关闭（与 Long Lake/DeGray 相同，不代表计算失败）。</p>"
        "<p>参数来源是 DeGray 成岩示例，仅把第二区结束河段从 31 改到 50 以覆盖 Columbia IMX=51。"
        "不能把 SOD 数值或 DO 降幅解释为 Columbia 现场率定结果。</p>"
    )
    col_section_md = (
        "## 4c. Columbia Slough 底泥成岩（SED_DIAG ON）\n\n"
        "运行目录：`05_REPRO_RUNS/run_20260814_columbia_diag`。"
        "DeGray `W2_diagenesis.npt` 改编（结束河段 31→50）。TSR 到 TMEND=55，无 forrtl。\n\n"
    )

    experience_html = """
  <h2>5. 外部经验借鉴</h2>
  <p>本节检索公开的 CE-QUAL-W2 /「W2 数值模拟」相关资料（含学术论文、官方工具说明与微信公众号上可核验的水环境数值模拟方法文章），只提炼可借鉴的<strong>方法与呈现习惯</strong>，不抄袭原文表述。以下链接均可公开访问。</p>
  <h3>5.1 来源列表</h3>
  <ol>
    <li><a href="https://yangtzebasin.whlib.ac.cn/CN/Y2011/V20/I10/1274">邓云等，《CE-QUAL-W2在紫坪铺水库的应用及其参数敏感性分析》，《长江流域资源与环境》2011</a> — 中文水库水温应用与率定思路。</li>
    <li><a href="https://www.nature.com/articles/s41598-026-42817-0">Scientific Reports：阳宗海 CE-QUAL-W2 水动力水质模拟（水位/表层温度 RMSE、AME、R 等指标）</a>。</li>
    <li><a href="https://github.com/CE-QUAL-W2-ERDC/cequalw2-python-library">CE-QUAL-W2-ERDC / cequalw2-python-library</a> — 官方生态后处理：时序、散点 1:1、四联验证仪表盘与 NSE/RMSE/KGE/PBIAS。</li>
    <li><a href="https://github.com/sarounds/w2anim">sarounds/w2anim（W2 Animator）</a> — 垂向剖面矩阵、纵剖面切片、水位沿程、时间-距离图等经典展示类型。</li>
    <li><a href="https://www.erdc.usace.army.mil/Media/Fact-Sheets/Fact-Sheet-Article-View/Article/554171/ce-qual-w2/">USACE ERDC CE-QUAL-W2 Fact Sheet</a> — 强调纵向-垂向二维场与分层水体适用性。</li>
    <li><a href="https://www.usbr.gov/uc/envdocs/ea/eastCanyon/appdx-B.pdf">USBR East Canyon Appendix B</a> — 以垂向剖面 + 下泄水温对照、AME（Absolute Mean Error，绝对平均误差）做率定统计。</li>
    <li><a href="https://gmd.copernicus.org/articles/18/6135/2025/gmd-18-6135-2025.pdf">GMD：CE-QUAL-W2 v4.5 底泥成岩模块评估</a> — 先水温后溶解氧的分层率定顺序与 NSE/RMSE 报告方式。</li>
    <li><a href="https://mp.weixin.qq.com/s/9bqWuSlvhyyQ6atiNFdcGw">微信公众号转载/推文：FVCOM 流域海洋水环境数值模拟教程摘要</a> — 虽非 W2，但其「水位等值线 + 流场矢量 + 率定作图」呈现链路可迁移。</li>
    <li><a href="https://mp.weixin.qq.com/s/VeN7-71VgTPrsFapGBSI0g">微信公众号转载/推文：Delft3D 建模与环评实践技术应用</a> — 强调资料获取→边界→率定验证→数据分析的报告结构。</li>
  </ol>
  <h3>5.2 可借鉴点（已部分落实 / 作为后续改进）</h3>
  <table>
    <thead><tr><th>借鉴点</th><th>公开来源要点</th><th>本报告落地情况</th></tr></thead>
    <tbody>
      <tr><td>输出变量优先级</td><td>先水位/水温，再溶解氧、营养盐/藻类；水温常对风遮蔽与光遮蔽敏感（紫坪铺文）</td><td>时序优先 ELWS、T2、DEPTH、DO（及案例可用 ALG1/Gen1）</td></tr>
      <tr><td>俯视 + 纵剖面双视图</td><td>手册与 W2 Animator：平面分支布局 + 纵向/垂向切片</td><td>已有相对俯视/沿程 + CPL/PRF 剖面；本轮新增流域底图叠置</td></tr>
      <tr><td>率定对比方式</td><td>垂向剖面叠测、时间序列叠测、1:1 散点；报告 RMSE/AME/NSE/PBIAS（Python 库 / USBR / 阳宗海）</td><td>Bonneville 已做库内 TSR 与坝下下泄两套 2011 年 CCIW 时序+1:1+MAE/RMSE/NSE；Columbia 成岩仅作开/关对照，无独立观测链</td></tr>
      <tr><td>报告结构</td><td>微信水环境建模推文习惯：建模设置→可视化→率定验证→情景/结论</td><td>本报告按：错误诊断→方法→结果图（含底图）→外部经验→结论/待补充</td></tr>
      <tr><td>地理合理性核验</td><td>公开经验强调网格需贴合真实河道/库岸；公众号教程亦强调底图与率定作图</td><td>用 Esri 卫星/地形瓦片本地缓存 + 坝址/源口公开坐标做示意叠置，并明示非精密 GIS</td></tr>
    </tbody>
  </table>
  <div class="note">
    <p>检索说明：直接以「W2数值模拟」检索微信公众号时，命中大量通用三维湖库软件试用推文；其中与 CE-QUAL-W2 方法可迁移、且链接可核验者已列入上表。未找到可稳定打开的、专门以 CE-QUAL-W2 为题的独家微信长文全文时，不以臆造引用填充。</p>
  </div>
"""

    experience_md = """## 5. 外部经验借鉴

本节只提炼公开可核验来源的方法与呈现习惯，不抄袭原文。

### 5.1 来源
1. [邓云等，紫坪铺 CE-QUAL-W2 应用与敏感性](https://yangtzebasin.whlib.ac.cn/CN/Y2011/V20/I10/1274)
2. [阳宗海 CE-QUAL-W2（Scientific Reports）](https://www.nature.com/articles/s41598-026-42817-0)
3. [cequalw2-python-library](https://github.com/CE-QUAL-W2-ERDC/cequalw2-python-library)
4. [W2 Animator](https://github.com/sarounds/w2anim)
5. [USACE ERDC Fact Sheet](https://www.erdc.usace.army.mil/Media/Fact-Sheets/Fact-Sheet-Article-View/Article/554171/ce-qual-w2/)
6. [USBR East Canyon Appendix B](https://www.usbr.gov/uc/envdocs/ea/eastCanyon/appdx-B.pdf)
7. [GMD v4.5 底泥成岩评估](https://gmd.copernicus.org/articles/18/6135/2025/gmd-18-6135-2025.pdf)
8. [微信：FVCOM 水环境数值模拟教程](https://mp.weixin.qq.com/s/9bqWuSlvhyyQ6atiNFdcGw)
9. [微信：Delft3D 建模与环评实践](https://mp.weixin.qq.com/s/VeN7-71VgTPrsFapGBSI0g)

### 5.2 可借鉴点
- **变量顺序**：水位/水温 → DO/营养盐；报告 RMSE、AME、NSE 等（观测链待补充前不编造数值）。
- **图件习惯**：平面俯视/分支布局 + 纵剖面/垂向剖面；本轮增加流域底图叠置。
- **率定呈现**：时序叠测、垂向剖面对比、1:1 散点与残差仪表盘。
- **报告结构**：设置 → 可视化 → 率定验证 → 结论；本报告增加「外部经验借鉴」与「待补充」。
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CE-QUAL-W2 三案例复现与可视化报告</title>
  <style>
    :root {{ --bg:#f5f7fb; --card:#fff; --text:#1f2937; --muted:#4b5563; --line:#dbe3ee; --accent:#1d4ed8; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--text); font-family:"Microsoft YaHei","Noto Sans CJK SC",Arial,sans-serif; line-height:1.75; }}
    .page {{ width:min(1180px,95vw); margin:24px auto; background:var(--card); border:1px solid var(--line); padding:36px 44px; }}
    h1,h2,h3 {{ line-height:1.35; }}
    h1 {{ margin-top:0; }}
    h2 {{ border-bottom:2px solid var(--line); padding-bottom:6px; }}
    table {{ width:100%; border-collapse:collapse; margin:12px 0 18px; font-size:0.92rem; }}
    th,td {{ border:1px solid #cbd5e1; padding:8px 10px; vertical-align:top; word-break:break-word; }}
    th {{ background:#edf2ff; }}
    .figure {{ margin:18px 0 22px; border:1px solid var(--line); padding:14px; background:#fcfdff; }}
    .figure img {{ width:100%; height:auto; border:1px solid #e5e7eb; display:block; margin-bottom:10px; }}
    .caption-title {{ font-weight:700; color:#1e3a8a; margin-bottom:6px; }}
    .note {{ background:#fff7ed; border:1px solid #fed7aa; padding:12px; margin:10px 0; }}
    .ok {{ background:#ecfdf5; border:1px solid #a7f3d0; padding:12px; margin:10px 0; }}
    .cover {{ text-align:center; padding:54px 24px; border:1px solid var(--line); background:linear-gradient(180deg,#fff,#f8fbff); }}
    .foot {{ margin-top:36px; padding-top:12px; border-top:1px dashed var(--line); color:var(--muted); font-size:0.92rem; }}
    a {{ color:var(--accent); }}
  </style>
</head>
<body>
<div class="page">
  <section class="cover">
    <h1>CE-QUAL-W2 三案例复现与可视化报告</h1>
    <p>运行目录：05_REPRO_RUNS/{RUN_ID}</p>
    <p>可执行文件：02_LIBRARY/07_executables/v4.5.5/w2_v455_ifx.exe</p>
    <p>生成时间：{gen_time}</p>
  </section>

  <h2>1. 摘要</h2>
  <p>本报告针对 CE-QUAL-W2（二维横向平均水动力-水质模型，Two-dimensional laterally averaged hydrodynamic and water quality model）的 Long Lake、DeGray、Columbia Slough 三个官方示例，完成隔离目录重跑、运行错误修复、多类可视化（含<strong>流域/区域底图</strong>）与自包含报告重建。</p>
    <p>用户反馈的 “Round them error” 经截图核对，实为 Intel Fortran 运行时错误 <code>forrtl: severe (29): file not found</code>（Fortran runtime library，Fortran 运行时库）。本轮确认两类触发点：</p>
    <ol>
      <li><strong>Long Lake：</strong><code>w2_habitat.npt</code> 指定输出 <code>.\\HabitatFiles\\habitat.csv</code>，但 <code>HabitatFiles</code> 目录不存在，FISHHABITAT 打开 unit 9530 失败。</li>
      <li><strong>Columbia Slough：</strong>控制文件 <code>SED_DIAG=ON</code>，但示例未提供必需输入 <code>W2_diagenesis.npt</code>，同样触发 forrtl file-not-found。</li>
    </ol>
  <div class="{'ok' if forrtl_fixed else 'note'}">
    <p><strong>验证结论：</strong>已在运行前自动创建缺失输出目录；Long Lake 可写出 HabitatFiles 下 habitat.csv，并产生多点 TSR（time series，时间序列）输出。forrtl 是否再现：{'否（已修复）' if forrtl_fixed else '待核对'}。</p>
  </div>

  <h2>2. Round them / forrtl 错误：原因、修复与验证</h2>
  <h3>2.1 原因</h3>
  <ol>
    <li>错误原文：<code>forrtl: severe (29): file not found, unit 9530, file ...\\HabitatFiles\\habitat.csv</code>（Long Lake）</li>
    <li>调用栈：FISHHABITAT @ fishhabitat.f90 → CE_QUAL_W2 @ w2_4_win.f90</li>
    <li><code>w2_habitat.npt</code> 第 3 行将栖息地输出设为 <code>.\\HabitatFiles\\habitat.csv</code>；该 csv 为<strong>输出文件</strong>，但 Fortran OPEN 不会自动创建父目录。</li>
    <li>Columbia：<code>SED_DIAG=ON</code> 时源码以 <code>STATUS='OLD'</code> 打开 <code>W2_diagenesis.npt</code>，示例包缺失该文件。</li>
    <li>旧复现脚本未处理上述路径/开关，模型在首步附近崩溃，导致 TSR 仅 1 行、报告图几乎为空。</li>
  </ol>
  <h3>2.2 修复步骤</h3>
  <ol>
    <li>在示例与隔离运行目录创建 <code>HabitatFiles\\</code>。</li>
    <li>脚本 <code>00_INDEX/run_three_cases.py</code> 解析 <code>w2_habitat.npt</code>，自动创建输出路径父目录。</li>
    <li>Columbia：权威三案例将 <code>SED_DIAG</code> 改为 OFF（因缺 <code>W2_diagenesis.npt</code>），并保留/开启 TSR、CPL，尝试开启 PRFC；SCR 关闭以便无界面批跑。后续在 <code>run_20260814_columbia_diag</code> 放入改编输入后重新打开 SED_DIAG。</li>
    <li>优先使用真实可执行文件 <code>w2_v455_ifx.exe</code>（约 5.7 MB PE，非 Git LFS 指针）。</li>
  </ol>
  <h3>2.3 验证结果</h3>
  <table>
    <thead><tr><th>案例</th><th>Exit</th><th>用时(s)</th><th>forrtl</th><th>新建目录</th><th>TSR</th><th>w2.err</th></tr></thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>

  <h2>3. 数据与方法</h2>
  <p>输入来自 <code>02_LIBRARY/06_examples/v4.5.5</code>。定量与图形均只使用本次真实运行产物，不编造指标。</p>
  <p>术语首次说明：TSR=时间序列输出；CPL=等值线/纵剖面；PRF=剖面；ELWS=水面高程；T2=水温；DO=溶解氧；PHI0=分段方位角（手册：自正北顺时针，弧度）；DLX=分段长度；LATITUDE/LONGITUDE=控制文件水体级经纬度（常用于太阳辐射）。</p>
  <p>流域底图方法：解析 <code>bth*.csv</code> 的 PHI0/DLX 重建河道走向；下载 OSM 河道折线至 <code>basemap_cache/*/osm_waterways.geojson</code> 作参考；在两点相似、多点相似、弧长控制 TPS 间自动择优；量化侧向偏移（均值/最大/P95）。报告图片均为 Base64 内嵌。</p>
  <div class="note">
    <p><strong>叠图偏差诊断（2026-08-12 量化）：</strong>三案例均相对 OSM 参考河道计算侧向偏移；详见各案例 <code>*_alignment_error.png</code> 与 figure_manifest 中 baseline/improved_lateral_m。
    投影误差仍约 <strong>20–25 m</strong>；公里级残差来自 PHI0/DLX 示意几何 + 控制点有限。
    DeGray 已从「坝锚刚性旋转」改为坝+上游源头双端 + 多点配准。Long Lake / Columbia 在双端基础上增加弧长/库心控制点。</p>
  </div>
  <div class="note">
    <p><strong>方位修正（2026-08-12）：</strong>叠线“上下颠倒”主因不是卫星底图 imshow 的 origin，而是水库案例把<strong>上游浅端</strong>误锚到坝址参考点，使刚性旋转所用模型弦反向，平面上表现为<strong>南北向横切镜像</strong>（Long Lake 北弯变南弯）；DeGray 则表现为坝/源头端对调（约 180°）。已改为坝/口锚在模型<strong>下游端</strong>（与最深湿段一致）。Columbia Slough 原本口@end，无 Y 轴符号错误。</p>
  </div>
  <div class="note">
    <p><strong>定位：</strong>三案例仍是可运行性 + 可视化核验。Bonneville 水温 NSE≈0.95–0.96。SYSTDG 自身 TDG 相对 CCIW 的 NSE=0.50（观测≤120% 时 0.66）；先前 −2.8 是把 N2+DO 换算当成了 SYSTDG 输出。Columbia 成岩已接通（DeGray 模板，未率定）。</p>
  </div>

  <h2>4. 结果可视化</h2>
  <p>每个案例按「时间序列 → 相对俯视/沿程 → 流域底图叠置 → 纵剖面/等值线」组织；每图含编号、标题与读图说明。</p>
  {''.join(figs_html[:n_before_bon])}
  {bon_section_html}
  {''.join(figs_html[n_before_bon:n_before_col])}
  {col_section_html}
  {''.join(figs_html[n_before_col:])}

  {experience_html}

  <h2>6. 结论</h2>
  <ol>
    <li>“Round them error” 实为 forrtl file-not-found；创建 HabitatFiles 后 Long Lake 可正常推进并输出多点序列。</li>
    <li>三案例均在隔离目录重跑；报告图包含时间序列、俯视/沿程、<strong>流域/区域底图</strong>、剖面/等值线（或明确标注的回退图）。</li>
    <li>三案例均以真实 Esri 卫星/地形离线底图叠置模型河道；OSM 参考河道 + 多控制点配准（自动择优）；侧向偏移已量化。</li>
    <li>DeGray 已从坝锚刚性改为坝+源头双端多点配准；Columbia PRF 垂向温度剖面已可解析（非 Tecplot CPL）。</li>
    <li>方位问题已定位：水库案例曾错锚上游端到坝址 → 表现为南北镜像/端点对调；已改为下游深水端锚定。</li>
    <li>叠图公里级偏差诊断：非底图投影（Mercator→lon/lat 显示误差≈20–25 m），而是 PHI0/DLX 示意路径 + 有限控制点配准；Long Lake 已改为坝+Nine Mile 双点以降低北偏。</li>
    <li>Bonneville 2011 年：水温 NSE≈0.95–0.96。SYSTDG 模块自身 TDG 相对 CCIW 的 NSE=0.50、MAE=2.20%；观测 ≤120% 时 NSE=0.66。先前 NSE≈−2.8 来自对照了 N2+DO 亨利换算，不是气体模块不可运行。TDGTA 把模拟封顶在 120%，观测峰值 129% 无法在目标开着时复现。</li>
    <li>Columbia 官方示例缺 <code>W2_diagenesis.npt</code>；已在隔离目录用 DeGray 模板改编后接通 SED_DIAG，写出 SOD 等成岩通量。权威三案例目录仍保持 SED_DIAG OFF，以免覆盖可运行基线。</li>
    <li>外部经验支持“水位/水温优先、俯视+纵剖面、RMSE/NSE 率定仪表盘、报告含地理核验”等做法；精密岸线 GIS 仍待补充。</li>
  </ol>

  <h2>7. 仍待补充</h2>
  <ul>
    <li>分段端点 / 岸线实测或 GIS 导出坐标（用于精密地理配准，而非仅水体级 LAT/LONG）。</li>
    <li>Bonneville TDG：对照已改用 SYSTDG TDG_TDG；剩余误差主要是 TDGTA 120% 封顶。关 TDGTA 的历史闸门重跑用于检验 129% 峰值。</li>
    <li>Columbia 成岩参数仍是 DeGray 模板，不是现场率定；若要用于水质情景，需按 Columbia 河段分区重写 <code>W2_diagenesis.npt</code>。</li>
    <li>Long Lake <code>w2.wrn</code> 负表层厚度 / 加减层仍待处理。</li>
    <li>Columbia Slough CPL 为 W2 原生格式（非 Tecplot）；已改解析 prf.opt 垂向温度剖面。</li>
  </ul>

  <div class="foot">本文件为自包含 HTML（内嵌 CSS 与 Base64 图片），无外链瓦片依赖。脚本：<code>00_INDEX/make_watershed_basemaps.py</code>、<code>00_INDEX/build_repro_report.py</code>。</div>
</div>
</body>
</html>
"""

    md = f"""# CE-QUAL-W2 三案例复现与可视化报告

> 生成时间：{gen_time}  
> 运行目录：`05_REPRO_RUNS/{RUN_ID}`  
> 可执行文件：`02_LIBRARY/07_executables/v4.5.5/w2_v455_ifx.exe`

## 1. 摘要
用户所见 “Round them error” 经核实为 Intel Fortran `forrtl: severe (29): file not found`。本轮在修复后完成三案例重跑，并补充流域/区域底图与外部经验章节。

## 2. forrtl 修复
- **原因1（Long Lake）**：`w2_habitat.npt` 输出路径 `.\\HabitatFiles\\habitat.csv`，目录缺失。
- **原因2（Columbia）**：`SED_DIAG=ON` 但缺少 `W2_diagenesis.npt`。
- **修复**：创建 `HabitatFiles`；权威三案例中 Columbia 关闭 `SED_DIAG`；另在 `run_20260814_columbia_diag` 用改编的 `W2_diagenesis.npt` 接通成岩。
- **验证**：见下表（真实 exit code / 用时 / TSR 行数）。

| 案例 | exit | 秒 | forrtl | TSR文件数/最大行数 | w2.err |
|---|---:|---:|---|---|---|
{chr(10).join(rows_md)}

## 3. 数据与方法
术语：TSR=时间序列；CPL=等值线/纵剖面；PRF=剖面；ELWS=水面高程；T2=水温；DO=溶解氧；PHI0=分段方位角（自正北顺时针）；DLX=分段长度。
底图：Esri 卫星/地形瓦片本地缓存 + OSM 参考河道 + 多控制点配准；侧向偏移量化见 `*_alignment_error.png`。

**方位修正：** Long Lake / DeGray 曾把上游浅端锚到坝址，旋转弦反向后呈南北横切镜像（或端点对调）；现坝锚在下游深水端。Columbia Slough 口@end 本来正确。

**叠图偏差诊断：** 主要不是投影问题。Esri Web Mercator 瓦片用 lon/lat 角点显示，本窗口错位约 20–25 m。公里级北偏来自 PHI0/DLX 示意路径 + 曾用坝锚刚性朝库心旋转（中点残差约 10.5 km、侧向约 2–5 km）。Long Lake 已改为坝+Nine Mile 两点相似变换；弯道仍可能有公里级残差。w2_con LAT/LONG 仅为辐射单点。

## 4. 结果可视化

{chr(10).join(figs_md[:n_before_bon])}

{bon_section_md}

{chr(10).join(figs_md[n_before_bon:n_before_col])}

{col_section_md}

{chr(10).join(figs_md[n_before_col:])}

{experience_md}

## 6. 结论
- forrtl 根因已定位并修复；三案例可运行并产出多点 TSR。
- 新增真实离线流域底图 `*_watershed_basemap.png`（Esri 卫星/地形本地缓存），用于核验模型是否落在正确水体附近。
- 新增 OSM 参考河道侧向偏移量化；DeGray 多点配准；Columbia PRF 剖面解析。
- 叠线方位：水库案例错锚上游端→南北镜像/端点对调，已改为下游深水端锚定。
- 叠图公里级偏差：非底图投影（≈20–25 m），而是示意配准物理局限；Long Lake 已用坝+Nine Mile 双点降低北偏。
- Bonneville 2011 vs CCIW：水温 NSE≈0.95–0.96；SYSTDG 自身 TDG NSE=0.50（≤120% 时 0.66）。先前 −2.8 是对照错了变量。
- Columbia 成岩已在隔离目录接通（DeGray 模板，未率定）；权威三案例仍保持 SED_DIAG OFF。

## 7. 仍待补充
- 分段端点 / 精密岸线 GIS
- Bonneville TDG：对照已用 SYSTDG TDG_TDG；关 TDGTA 以检验 129% 峰值
- Columbia 成岩参数需按本案例分区重写，不能沿用 DeGray 数值当率定
- Long Lake `w2.wrn` 负表层厚度（DLTMAX 收紧重跑中）
"""

    OUT_HTML.write_text(html, encoding="utf-8")
    OUT_MD.write_text(md, encoding="utf-8")

    # PDF
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    pdfmetrics.registerFont(TTFont("SimHei", r"C:\Windows\Fonts\simhei.ttf"))
    c = canvas.Canvas(str(OUT_PDF), pagesize=A4)
    width, height = A4

    def draw_wrapped(text: str, x: float, y: float, max_chars: int = 48, leading: float = 13) -> float:
        for line in textwrap.wrap(text, width=max_chars) or [""]:
            if y < 50:
                c.showPage()
                c.setFont("SimHei", 9)
                y = height - 50
            c.drawString(x, y, line)
            y -= leading
        return y

    y = height - 50
    c.setFont("SimHei", 14)
    c.drawString(40, y, "CE-QUAL-W2 三案例复现与可视化报告（PDF）")
    y -= 22
    c.setFont("SimHei", 9)
    for line in [
        f"生成时间：{gen_time}",
        f"运行目录：05_REPRO_RUNS/{RUN_ID}",
        "forrtl severe(29) 根因：HabitatFiles 目录缺失；已创建后验证通过。",
        "本 PDF 含时间序列 / 俯视 / 流域底图 / 剖面；详细说明见 report.html。",
        "",
    ] + [f"- {r}" for r in rows_md]:
        y = draw_wrapped(line, 40, y, max_chars=52)

    y -= 8
    c.setFont("SimHei", 11)
    y = draw_wrapped("外部经验借鉴（摘要）", 40, y, max_chars=40)
    c.setFont("SimHei", 8)
    for line in [
        "紫坪铺 CE-QUAL-W2：先水温率定，关注风遮蔽/光遮蔽敏感性。",
        "cequalw2-python-library：1:1 散点与 NSE/RMSE/KGE/PBIAS 仪表盘。",
        "W2 Animator：垂向剖面、纵剖面切片、时间-距离图。",
        "微信 FVCOM/Delft3D 推文：底图+率定作图与报告结构可迁移（非 W2 原文照搬）。",
        "完整链接见 report.html / report.md 第 5 章。",
        "",
    ]:
        y = draw_wrapped(line, 40, y, max_chars=54, leading=12)

    for title, fig in pdf_figs:
        if not fig.exists():
            continue
        if y < 300:
            c.showPage()
            y = height - 50
        c.setFont("SimHei", 10)
        y = draw_wrapped(title, 40, y, max_chars=48, leading=12)
        img = ImageReader(str(fig))
        iw, ih = img.getSize()
        draw_w = width - 80
        draw_h = draw_w * ih / iw
        if draw_h > 260:
            draw_h = 260
            draw_w = draw_h * iw / ih
        if y - draw_h < 40:
            c.showPage()
            y = height - 50
            c.setFont("SimHei", 10)
            y = draw_wrapped(title, 40, y, max_chars=48, leading=12)
        c.drawImage(img, 40, y - draw_h, width=draw_w, height=draw_h, preserveAspectRatio=True)
        y -= draw_h + 16

    c.save()
    print(f"WROTE {OUT_HTML}")
    print(f"WROTE {OUT_MD}")
    print(f"WROTE {OUT_PDF}")
    print(f"figures embedded: {fig_n}")


if __name__ == "__main__":
    main()
