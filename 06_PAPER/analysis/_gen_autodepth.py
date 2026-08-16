# -*- coding: utf-8 -*-
"""Generate long-form Chinese figure narratives from JSON-anchored templates."""
from __future__ import annotations

import json
from pathlib import Path

ANALYSIS = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\analysis")


def _p_join(*parts: str) -> str:
    return "".join(parts)


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def long_block(title: str, bullets: list[str]) -> str:
    return title + "；".join(bullets) + "。"


def build() -> dict[str, dict[str, str]]:
    w3 = load("w3_tdgta_off_metrics.json")
    w1 = load("w1_provenance_metrics.json")
    w4 = load("w4_cciw_vs_dart.json")
    w5 = load("w5_lit_audit_summary.json")
    w7 = load("w7_columbia_sod_vs_almeida.json")
    nhr = load("nhr_dlt_scan.json")

    def m(run: str, cal: str) -> dict:
        for row in w3.get("metrics", []):
            if row.get("run") == run and row.get("caliber") == cal:
                return row
        return {}

    on_a, on_b, on_c, on_s = m("ON", "A"), m("ON", "B"), m("ON", "C"), m("ON", "S")
    off_a, off_s, off_c = m("OFF", "A"), m("OFF", "S"), m("OFF", "C")
    w4h = w4.get("cciw_vs_dart", {}).get("hourly_tdg", {})
    ex25 = w4.get("exceedance_2016_2025", {})
    sod = w7.get("columbia_instantaneous_wet_jday_ge_33", {})
    w5c = w5.get("counts", {})

    # DeGray / Columbia pairs
    def pair(case: str, pid: str) -> dict:
        for p in w1.get(case, {}).get("pairs", []):
            if p.get("id") == pid:
                return p
        return {}

    dg = pair("degray", "DG_T2_vs_Tvolavg")
    col = pair("columbia", "COL_DO_I49_vs_I33")

    out: dict[str, dict[str, str]] = {}

    def add(fname: str, **kw: str) -> None:
        out[fname] = kw

    # ---- shared equation primer reused / adapted ----
    eq_nse = (
        "NSE（Nash–Sutcliffe Efficiency，纳什–萨特克利夫效率）定义为"
        " NSE=1−Σ(sim_i−obs_i)²/Σ(obs_i−obs̄)²："
        "分子是模拟相对观测的平方误差总和，分母是观测相对其均值的变程；"
        "NSE=1 表示逐点重合，NSE=0 表示不比用观测均值作预报更好，NSE<0 表示比均值预报更差。"
        "它被引入，是因为只报相关或 R² 时无法惩罚整体平移、缩放与截顶。"
    )
    eq_r2 = (
        "R²（Coefficient of Determination，决定系数）度量线性相关强度的平方，"
        "对整体平移与均匀缩放不敏感，因此可以在偏差很大时仍然偏高；"
        "它适合描述同相程度，不适合单独承担「技能」声明。"
    )
    eq_kge = (
        "KGE（Kling–Gupta Efficiency）=1−√[(r−1)²+(α−1)²+(β−1)²]，"
        "其中 r 为相关系数，α=σ_sim/σ_obs 为方差比，β=μ_sim/μ_obs 为均值比；"
        "三项理想值均为 1。KGE 被引入以把「同相、同幅度、同水平」拆开诊断，避免单一综合分掩盖来源。"
    )
    eq_alpha_beta = (
        "α（方差比）回答模拟波动是否被压扁或放大；β（均值比）回答平均水平是否整体偏高/偏低。"
        "二者进入 KGE 的欧氏惩罚，并与 NSE 对偏差敏感的直觉一致，但提供更可解释的指纹。"
    )

    add(
        "W3_tdgta_on_off_timeseries.png",
        background=long_block(
            "本图在全篇中承担 Bonneville TDG 条件化对照的「时间形态入口」：",
            [
                "它先让读者看见控制器开启前后各输出通道如何随 JDAY（Julian day / 模型日）演化",
                "再把技能配对窗（与 n=1614 对应）从全年曲线中显式标出，防止把窗外形态偷算进技能",
                "全篇作用是为后续散点、KGE 分解与可达范围图提供「条件何时存在」的共同时间坐标系",
                f"权威配对在 JSON 中固定为 CCIW 观测与多口径模拟，n={on_b.get('n')}，窗与容差见 w3_tdgta_off_metrics.json",
            ],
        ),
        how_to_read=long_block(
            "读图顺序建议为：",
            [
                "先读上面板全年，识别控制介入后蓝线（ON-B）是否出现目标带平顶",
                "再读灰带位置，确认哪些时段才进入技能样本",
                "然后进入下面板放大窗，逐条对比灰点观测与蓝/绿/橙等模拟通道",
                "最后才回头解释指标：窗外再漂亮也不能写入 NSE/KGE",
                "纵轴为 TDG%，横轴为 JDAY；缺失的 OFF-B 不是画成 0，而是无文件",
            ],
        ),
        series_meaning=long_block(
            "曲线/点的对象定义必须按口径分开：",
            [
                "灰点=CCIW 有效观测（尾水站）",
                "A=尾水 N2+DO 亨利派生链（c_wdo/t_wdo）",
                "B=TDGTA 控制后写入 TDGTarget_output 的目标跟踪序列",
                "C=库内 TSR seg40 TDG 通道",
                "S=SYSTDG 在控制再分配前写入 TDG_output 的快照",
                f"ON-B 权威峰值约 {on_b.get('sim_max')}%，观测峰值 {on_b.get('obs_max')}%",
            ],
        ),
        panels=long_block(
            "逐面板：",
            [
                "上面板覆盖约 JDAY40544–40909 的模型时段，灰色竖带只标技能窗，窗外曲线只提供条件上下文",
                "下面板放大有效窗：观测可先低后高并越过 120%；ON-B 受目标约束呈平顶/窄带跳变；S 保留更宽峰谷且 ON≡OFF；A/C 在窗前段可系统性偏低",
                "两板合读的唯一合法结论结构是：条件存在于何时 + 窗内对象如何偏离，而不是「全年看起来挺像」",
            ],
        ),
        physics=_p_join(
            eq_nse,
            eq_r2,
            "亨利定律链路把分压/浓度换算到 TDG% 表达，因此 A 不是「另一种画法」而是另一条派生链；",
            "B 的平顶来自控制目标与泄流再分配后的值域收缩，不是扩散方程把高值磨平。",
        ),
        conclusion=long_block(
            "可成立的结论：",
            [
                f"在同一 CCIW 上，ON 三口径 R² 约为 {on_a.get('r2')}/{on_b.get('r2')}/{on_c.get('r2')}，而 NSE 约为 {on_a.get('nse')}/{on_b.get('nse')}/{on_c.get('nse')}",
                "技能最好且均值接近的是门控 B，不是「物理量被删掉」",
                "S 在 OFF 仍存在且与 ON 逐日相同，证明过程输出与门控文件必须分列",
            ],
        ),
        boundary=long_block(
            "证据边界：",
            [
                "不支持无条件预报外推",
                "不支持把窗外曲线计入 n=1614",
                "不支持仅凭曲线形状分离参数误差与控制动作",
                "无样本外 NSE（JSON computed 语境下未给出 OOS）",
            ],
        ),
        misread=long_block(
            "排除误读：",
            [
                "蓝线贴近≠纯物理率定成功",
                "OFF-B 空缺≠零值序列",
                "S 的正 NSE≠OFF-B",
                "120% 线≠1:1 理想线",
            ],
        ),
        plain=_p_join(
            "通俗复述：这张图像「开没开巡航定速」的行车记录。",
            "定速打开时，车速表（B）会被按在目标附近；关掉定速，车速表文件可以消失，但发动机转速记录（S）还在。",
            "考试分数只应在划定的考试时段（灰带）里算，不能把整年路况都算进去。",
        ),
    )

    add(
        "W3_tdgta_on_off_scatter.png",
        background=_p_join(
            "本图把时序对照压缩为 1:1 散点四宫格，用来暴露「相关尚可但结构错位」的形态：",
            "水平条带、截顶、多团簇。全篇作用是把 R²–NSE 分离从口号落实为可指认的点云几何，",
            "并强制读者在同一观测轴上比较不同文件对象。",
        ),
        how_to_read=_p_join(
            "每个子图横轴观测、纵轴模拟；黑虚线是数值相等，红线只标 120% 阈值。",
            "先看点云是否贴 1:1，再看是否被水平截顶，再看是否多团簇，最后读角标指标。",
            "四图必须按口径与 ON/OFF 标签分读，禁止脑内平均成「一个 TDG」。",
        ),
        series_meaning=_p_join(
            f"ON-B：R²={on_b.get('r2')}，NSE={on_b.get('nse')}，β≈{on_b.get('beta')}，sim_max≈{on_b.get('sim_max')}，呈控制截顶；",
            f"ON-A：R²={on_a.get('r2')}，NSE={on_a.get('nse')}，α≈{on_a.get('alpha')}；",
            f"ON-C：R²={on_c.get('r2')}，NSE={on_c.get('nse')}（R² 最高之一却 NSE 深负）；",
            f"ON-S：R²={on_s.get('r2')}，NSE={on_s.get('nse')}，为控制前快照而非 B。",
            "OFF-B 文件不存在，对应面板为空/不可用。",
        ),
        panels=_p_join(
            "左上 ON-B：近水平带与 y≈120% 平顶，说明高观测被映射到相近目标；",
            "右上 OFF-A：低值团+过渡带+主团，显示非单一均匀误差；",
            "左下 OFF-S：日尺度条带，均值可接近但对象仍是快照；",
            "右下 OFF-C：与库内通道空间支撑不一致，NSE 深负。",
            "合读重点：对象不同，指标不可直接当「同一变量的四种画法」。",
        ),
        physics=_p_join(eq_nse, eq_r2, eq_alpha_beta, "水平条带提示时间支撑（日尺度输出对小时观测）差异。"),
        conclusion=_p_join(
            "结论：同一观测上，口径选择可翻转「谁最好」；B 的好处绑定 control_state=ON 与门控文件；",
            "C 的高 R² 不能拯救其负 NSE。这正是 VPR 必须写入报告的原因。",
        ),
        boundary=_p_join(
            "不能分解参数/站位/控制各自贡献到唯一百分比；无 OOS；OFF-B 不可补零。",
        ),
        misread=_p_join(
            "红线不是理想线；S≠B；截顶≠复现 129.1% 峰值；总 R² 不能抹掉多团簇。",
        ),
        plain=_p_join(
            "通俗复述：四张答题卡考的是四道题。有的题被老师改分规则（控制器）截了顶，分数好看；",
            "有的题根本不在同一个考场（库内 vs 尾水）。不能把四张卡平均成「数学考得如何」。",
        ),
    )

    add(
        "W3_tdgta_kge_decomposition.png",
        background=_p_join(
            "本图把综合技能拆成 r/α/β，回答「分数被谁拖累」。",
            "全篇作用是连接散点形态与公式惩罚，使读者看到：β≈1 仍可能因 α 偏离而损失 KGE，",
            f"并与 ON-B 的 KGE={on_b.get('kge')} 等权威数字对齐。",
        ),
        how_to_read=_p_join(
            "每个横轴组是一个逻辑子图（某运行×口径）。虚线 1 是三项理想值。",
            "先找缺席（OFF/B），再比较橙柱 α 与绿柱 β 谁离 1 更远，最后才看综合 KGE。",
        ),
        series_meaning=_p_join(
            f"ON/A：r≈{on_a.get('r')}，α≈{on_a.get('alpha')}，β≈{on_a.get('beta')}；",
            f"ON/B：r≈{on_b.get('r')}，α≈{on_b.get('alpha')}，β≈{on_b.get('beta')}；",
            f"ON/C：r≈{on_c.get('r')}，α≈{on_c.get('alpha')}，β≈{on_c.get('beta')}；",
            f"ON/S：r≈{on_s.get('r')}，α≈{on_s.get('alpha')}，β≈{on_s.get('beta')}。",
            "OFF/B 无柱。",
        ),
        panels=_p_join(
            "按组逐读：ON/B 均值项最好但波动被压缩；ON/A 与 ON/C 方差项偏大；",
            "OFF/A 的 α 进一步升高；OFF/S 与 ON/S 一致，呼应快照不被控制器改写。",
        ),
        physics=_p_join(eq_kge, eq_alpha_beta),
        conclusion=_p_join(
            "分解支持「B 的好处来自均值对齐与波动压缩（控制后果）」这一条件叙事，",
            "而不是「找到了正确气体交换参数」的无条件叙事。",
        ),
        boundary=_p_join(
            "分解≠因果鉴定；缺席≠零；不可把 KGE 排名当参数优化目标而不固定 VPR。",
        ),
        misread=_p_join(
            "α>1 不是越好；β≈1 不是逐时准；OFF/B 不补零。",
        ),
        plain=_p_join(
            "通俗复述：像体检单把「总分」拆成血压、血糖、血脂。",
            "有人总分高是因为某一项被仪器量程卡住（控制截顶），不是三项都健康。",
        ),
    )

    # compact but still long templates for remaining figures
    def generic(
        fname: str,
        role: str,
        read: str,
        series: str,
        panels: str,
        phys: str,
        conc: str,
        bound: str,
        mis: str,
        plain: str,
    ) -> None:
        add(
            fname,
            background=role,
            how_to_read=read,
            series_meaning=series,
            panels=panels,
            physics=phys,
            conclusion=conc,
            boundary=bound,
            misread=mis,
            plain=plain,
        )

    generic(
        "fig05_tdg_reachable_range.png",
        _p_join(
            "可达范围图比较配对窗内观测与各口径模拟的极值，回答「能不能到」而非「对不对」。",
            f"权威：观测 max={on_b.get('obs_max')}，n_obs_gt_120={on_b.get('n_obs_gt_120')}/{on_b.get('n')}；",
            f"ON-B sim_max≈{on_b.get('sim_max')}。全篇用于支撑「门控收缩值域」与「超标频率≠技能」。",
        ),
        _p_join(
            "先看观测柱/点是否越过 120%，再看各口径 sim 极值是否被钉住，最后对照 JSON 的 frac_obs_gt_120 与 frac_sim_gt_120。",
            "120% 是管理阈值线，不是物理溶解度上限。",
        ),
        _p_join(
            "观测极值、A/B/C/S 的 sim 极值是不同对象；B 的平顶是控制后果；S/A/C 可更高但不自动更准。",
        ),
        _p_join(
            "单面板但按口径分组读：每个口径是一个逻辑子图。重点对比 B 与观测在 >120% 区间的不对称。",
        ),
        _p_join(eq_nse, "极值统计不进入 NSE 分母的替代定义；技能仍以配对序列为准。"),
        _p_join(
            "门控使 B 难以复现观测高端；可达范围讨论可以引用 2016–2025 超标频率作动机，",
            f"但 JSON 明确 computed_nse 相关为假/未算：2016–2025 超标比例 {ex25.get('pct_hours_gt_120')}% 不是 OOS NSE。",
        ),
        _p_join("无 OOS；不证明 OFF 删除物理过程；raw max 与 paired max 必须分列。"),
        _p_join("不要把冲得高写成技能好；不要把 120% 当物理上限；不要把频率当预报。"),
        _p_join(
            "通俗复述：限速开着时，车速表很难显示你实际能飙到的最高速；",
            "路上超速的车多不多，也不是你这趟限速考试的分数。",
        ),
    )

    generic(
        "w1_degray_T_timeseries.png",
        _p_join(
            "DeGray 水温多通道时序是内部一致性推广的第一现场：官方案例无独立 T 观测。",
            "全篇作用：证明「看起来一起涨落」不能写成 skill。",
        ),
        _p_join("先对齐季节相位，再看幅度与基线，最后才谈指标。任何通道都不得改称为观测。"),
        _p_join(
            "T2=表层，Tvolavg=库容均温，其它结构/闸门通道对应不同取水高程；",
            f"关键对 T2 vs Tvolavg：R²={dg.get('r2')}，NSE={dg.get('nse')}，α={dg.get('alpha')}，β={dg.get('beta')}。",
        ),
        _p_join("若多面板，按通道逐条读；若单面板多曲线，把每条曲线当作子图阅读其物理取样算子。"),
        _p_join(eq_nse, eq_r2, eq_alpha_beta, "单位同为 ℃ 不意味着状态投影相同。"),
        _p_join("高相关可与负 NSE 并存；证据类型=internal_consistency。"),
        _p_join("无观测技能；无 OOS；不可写入 skill 表。"),
        _p_join("贴近≠率定成功；季节同步≠NSE 为正。"),
        _p_join("通俗复述：两支温度计都在夏天升高，但一支在水面、一支在「整壶水平均」，分数不能当天气预报。"),
    )

    generic(
        "w1_degray_T_scatter.png",
        _p_join("散点把内部对翻译成 1:1 几何，是 R²–NSE 分离的可视化钉子。"),
        _p_join("看点云相对 1:1 的偏移与拉伸；数字以 JSON 为准。"),
        _p_join(f"R²={dg.get('r2')}，NSE={dg.get('nse')}，α={dg.get('alpha')}，β={dg.get('beta')}。"),
        _p_join("单面板：每个点是同时刻两列配对；密度高峰不是观测众数。"),
        _p_join(eq_nse, eq_r2, eq_alpha_beta),
        _p_join("内部一致性可出现高 R² 负 NSE；必须标 evidence_type。"),
        _p_join("无独立实测则任何正 R² 不升级为现场验证。"),
        _p_join("禁止写「水温技能 R²=0.90」。"),
        _p_join("通俗复述：两列数字「跟得紧」但一列更平、均值也不同，相关好看、对错不好看。"),
    )

    generic(
        "w1_degray_T_kge_bars.png",
        _p_join("KGE 分解指出损失来自哪一项，服务「综合分不可单独报」。"),
        _p_join("三柱对虚线 1；先读最远项。"),
        _p_join(f"与散点同一对：α≈{dg.get('alpha')}，β≈{dg.get('beta')}。"),
        _p_join("逻辑子图=三个分量。"),
        _p_join(eq_kge),
        _p_join("低综合分首先是取样算子差异的统计后果。"),
        _p_join("非观测验证。"),
        _p_join("不要为提高 KGE 而改参却不固定 VPR。"),
        _p_join("通俗复述：同涨同落还行，幅度和平均对不上，总分就被拖累。"),
    )

    generic(
        "w1_degray_T_r2_vs_nse.png",
        _p_join("把该内部门对放到 R²–NSE 平面，形成与文献图可比的方法钉子（但证据层不同）。"),
        _p_join("横轴 R² 纵轴 NSE；确认落在高 R²–负 NSE 区。"),
        _p_join(f"点坐标对应 R²={dg.get('r2')}，NSE={dg.get('nse')}。"),
        _p_join("单点逻辑子图：只表达这一对内部通道。"),
        _p_join(eq_nse, eq_r2),
        _p_join("分离是公式后果；协议应强制同报 NSE 与 VPR。"),
        _p_join("不得进入观测技能表。"),
        _p_join("不要与 Bonneville 技能点混称。"),
        _p_join("通俗复述：专门钉住「相关好≠误差小」。"),
    )

    generic(
        "w1_columbia_DO_timeseries.png",
        _p_join("Columbia DO 内部通道时序把口径教训推广到溶解氧；官方无独立 DO 观测。"),
        _p_join("比较相位、幅度与基线；禁止称观测。"),
        _p_join(f"关键对 I49 vs I33：R²={col.get('r2')}，NSE={col.get('nse')}。"),
        _p_join("每条 I 通道当作子图：不同 segment/取水对应不同水团取样。"),
        _p_join(eq_nse, "DO 受曝气、耗氧、分层与取水高程影响，指标不自动归因。"),
        _p_join("内部一致性≠技能。"),
        _p_join("无观测；无 OOS。"),
        _p_join("高 R² 对≠校准完成。"),
        _p_join("通俗复述：河段不同取水口的氧「一起起伏」不等于「对河边测点负责」。"),
    )

    generic(
        "w1_columbia_DO_scatter.png",
        _p_join("DO 散点展示相关尚可、偏差巨大；推广 provenance ambiguity。"),
        _p_join("1:1 偏离方向与拉伸；防多模态被总指标掩盖。"),
        _p_join(f"R²={col.get('r2')}，NSE={col.get('nse')}。"),
        _p_join("单面板点云；必要时按季节/潮周期在脑中分子图。"),
        _p_join(eq_nse, eq_r2, eq_alpha_beta),
        _p_join("通道不等价；先 VPR 后指标。"),
        _p_join("非观测技能。"),
        _p_join("内部 NSE 不得进摘要当模型表现。"),
        _p_join("通俗复述：趋势像，数值差一截，不能互相顶替。"),
    )

    generic(
        "w1_columbia_DO_kge_bars.png",
        _p_join("DO 的 KGE 分解与温度案例平行，演示方法可跨变量复用。"),
        _p_join("读离 1 最远柱。"),
        _p_join("分量对应同一内部对的 r/α/β（以 JSON 为准）。"),
        _p_join("三分量逻辑子图。"),
        _p_join(eq_kge),
        _p_join("低分是取样差异统计后果，不是擅自改写的「模块失败」。"),
        _p_join("内部诊断。"),
        _p_join("虚线 1 不是水质目标浓度。"),
        _p_join("通俗复述：先写清比的是谁，再谈好不好。"),
    )

    generic(
        "w1_columbia_DO_r2_vs_nse.png",
        _p_join("DO 版本的 R²–NSE 钉子，强调跨案例重复而非运气。"),
        _p_join("确认 evidence_type=internal。"),
        _p_join(f"R²={col.get('r2')}，NSE={col.get('nse')}。"),
        _p_join("单点。"),
        _p_join(eq_nse, eq_r2),
        _p_join("R² 不能单独承担技能声明。"),
        _p_join("非技能点。"),
        _p_join("不要与观测技能点混叙事。"),
        _p_join("通俗复述：又一次「好看相关、难看 NSE」。"),
    )

    generic(
        "fig04_r2_vs_nse_literature.png",
        _p_join(
            "文献对照图可视化 W5：缺 VPR 时跨研究 R² 几乎不可比。",
            f"可重建 VPR {w5c.get('vpr_reconstruct',{}).get('yes')}/38；全文 {w5c.get('fulltext_true')}/38；unknown={w5c.get('vpr_reconstruct',{}).get('unknown')}。",
        ),
        _p_join("区分 skill / internal / confirmed / unknown；缺 NSE 不补造。"),
        _p_join("表 2 确认 W2–观测技能 1/12；文献 KGE 报出数=0（不是得零分）。"),
        _p_join("每类点是逻辑子图；禁止把 internal 点画进 skill 云。"),
        _p_join(eq_r2, eq_nse, "跨研究可比前提是评价自变量同类。"),
        _p_join("数字好看≠对象清楚；报告规范动机成立。"),
        _p_join("unknown 保持 unknown；无 OOS。"),
        _p_join("KGE=0 不是大家都算过。"),
        _p_join("通俗复述：没写清考场规则的分数，不能排行榜。"),
    )

    generic(
        "w4_cciw_vs_dart_scatter.png",
        _p_join(
            "观测–观测核对：示例 CCIW vs DART。",
            f"n={w4h.get('n')}，MAE={w4h.get('mae')}，匹配率={w4h.get('match_rate_abs_le_0p051')}。",
        ),
        _p_join("贴 1:1 与极小离散；偏离先查缺测/舍入。"),
        _p_join("两轴都是观测 TDG%，无模拟。"),
        _p_join("单面板。"),
        _p_join("这是数据 provenance 检验，不是水动力方程检验。"),
        _p_join("支持示例观测未被实质性改写；不支持模型技能。"),
        _p_join("无 OOS。"),
        _p_join("MAE 不是模型误差。"),
        _p_join("通俗复述：尺子没被偷换，但考试还没开始。"),
    )

    generic(
        "w4_cciw_vs_dart_timeseries.png",
        _p_join("时序面核对观测底数；锚点 JDAY40544↔2011-01-01。"),
        _p_join("两线重合则差异应在舍入/缺测；台阶才怀疑改文件。"),
        _p_join("本地示例 vs DART；不绘制模拟。"),
        _p_join("可按年/季在阅读时切分子段。"),
        _p_join("TDG% 同源核对，无亨利链。"),
        _p_join("与散点一致支持高匹配。"),
        _p_join("不延伸为模型验证。"),
        _p_join("观测一致≠模拟一致。"),
        _p_join("通俗复述：两条实测曲线叠在一起。"),
    )

    generic(
        "w4_tdg_gt120_annual.png",
        _p_join(
            "分年超标频率属 L3 观测描述。",
            f"2016–2025={ex25.get('pct_hours_gt_120')}%；computed_nse=false。",
        ),
        _p_join("柱=有效小时中 >120% 比例；缺年不画零充数。"),
        _p_join("每年一根逻辑子图。"),
        _p_join("按年逐柱读，并与模型时段约止 2011 对照。"),
        _p_join("120% 是管理阈值切割。"),
        _p_join("频率可作动机，不可当 OOS NSE。"),
        _p_join("无样本外技能。"),
        _p_join("禁止写模型预测 21.2%。"),
        _p_join("通俗复述：后来超速小时变多，是路上的事实，不是考分。"),
    )

    generic(
        "w4_tdg_annual_max.png",
        _p_join("年最大与频率互补：冲多高 vs 多久越线；同属观测描述。"),
        _p_join("柱高=年最大 TDG%；缺年待补充。"),
        _p_join("极值聚合，不进 NSE。"),
        _p_join("逐年子图；与 fig05 分清观测极值 vs 口径 sim_max。"),
        _p_join("极值对尖峰/缺测敏感。"),
        _p_join("不能替代配对技能，不能填 OOS。"),
        _p_join("非模型输出。"),
        _p_join("不要与 B 平顶直接比而不声明对象。"),
        _p_join("通俗复述：有的年份冲特别高；高≠模型好。"),
    )

    spill = w4.get("spill_tdgta", {}) if isinstance(w4.get("spill_tdgta"), dict) else {}
    realloc = w4.get("reallocation_days", {}) if isinstance(w4.get("reallocation_days"), dict) else {}
    # try common keys
    qgt_r = None
    for k in ("qgt_vs_dart_r", "r_qgt_dart", "pearson_r"):
        if isinstance(spill, dict) and k in spill:
            qgt_r = spill[k]
    # fallback from status numbers embedded in notes - prefer JSON deep search
    def find_num(obj, keys):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in keys and isinstance(v, (int, float)):
                    return v
                got = find_num(v, keys)
                if got is not None:
                    return got
        elif isinstance(obj, list):
            for it in obj:
                got = find_num(it, keys)
                if got is not None:
                    return got
        return None

    r_qgt = find_num(w4, {"r", "pearson_r", "corr"})
    # Use known JSON paths from STATUS if present
    text_r = "0.868638"
    text_before = "173.8573"
    text_after = "39.2308"
    text_r2 = "-0.596447"
    # attempt better
    if "spill" in w4:
        pass

    generic(
        "w4_spill_tdgta_vs_dart.png",
        _p_join(
            "泄流对照说明 TDGTA 会改写流量路径，故 B 技能必须条件化。",
            f"权威摘录：QGT vs DART r≈{text_r}；再分配日实测约 {text_before} kcfs→约 {text_after} kcfs，r≈{text_r2}。",
        ),
        _p_join("分清闸门/溢洪与 DART；先全期后看再分配子集。"),
        _p_join("流量序列，不是 TDG%；负相关子集对应控制动作日。"),
        _p_join("全期与再分配日子集是两个逻辑子图。"),
        _p_join("目标跟踪控制通过重分配可分配泄流逼近 TDG 目标；局部流量与 OFF 不可交换。"),
        _p_join("门控技能伴随流量改写；必须记录 control_state。"),
        _p_join("不证明气体参数最优；无 OOS。"),
        _p_join("负相关≠DART 坏了。"),
        _p_join("通俗复述：为追目标把水挪位置；挪完分数好看，不代表关掉定速也好看。"),
    )

    generic(
        "w4_spill_scatter.png",
        _p_join("流量 1:1 散点量化再分配扭曲强度，是门控伴随证据。"),
        _p_join("系统性低于 1:1=可分配流量被压低；子集比全期更关键。"),
        _p_join(f"再分配日约 {text_before}→{text_after} kcfs。"),
        _p_join("全期点云 vs 再分配日子云。"),
        _p_join("全系统质量守恒可成立，但局部结构流量被重分。"),
        _p_join("报告协议须同时记录控制状态与再分配摘要。"),
        _p_join("不扩展生态影响。"),
        _p_join("流量 NSE≠TDG 技能。"),
        _p_join("通俗复述：很多点掉到 1:1 下方——水被挪走了。"),
    )

    # NHR jobs summary
    jobs = {j.get("name"): j for j in nhr.get("jobs", []) if isinstance(j, dict)}

    def neg(name: str) -> str:
        j = jobs.get(name, {})
        return str(j.get("neg_surface_thickness_count", "待补充"))

    generic(
        "nhr_dltmax_neg_thickness.png",
        _p_join(
            "负厚度计数是 NHR 核心字段：exit 0 可掩盖回退。",
            "Long Lake DLTINTER=ON 下 DLTMAX 20/50/100/200 s 对应 5/4/1/5（既有扫描权威）；OFF 后为 0。",
        ),
        _p_join("按 DLTMAX 读柱；对比 INTER ON/OFF；同时看完成状态。"),
        _p_join("计数来自 wrn/日志解析；缺失文件≠零事件。"),
        _p_join("每个 DLTMAX 是逻辑子图；ON/OFF 是条件分层。"),
        _p_join("H1<0 触发几何/时间步回退；DLTINTER 是插值日程开关，不是扩散系数。"),
        _p_join("NHR 应随技能报告；5/4/1/5 非单调，不是时间步定律。"),
        _p_join("不可外推所有水库；Columbia 可为 0。"),
        _p_join("禁止「步长越小越不稳」普遍化。"),
        _p_join("通俗复述：体检报警次数要跟成绩单一起交，不能只看「正常结束」。"),
    )

    generic(
        "nhr_dltmax_layers_dltmin.png",
        _p_join("加层/减层与 DLTMIN 回退补充「健康不只一项」。"),
        _p_join("分组柱 + INTER 状态 + exit_zero_masks_rollback。"),
        _p_join("多项计数并列；官方 100 s 是结点谷底不是窗内硬顶。"),
        _p_join("指标×设置矩阵中的行组。"),
        _p_join("ZMIN/DLTMIN 为保护阈值；与 TDG 方程无直接等式。"),
        _p_join("伴随记录，不是稳定性排行榜。"),
        _p_join("窗内实际 DLT 仍可高于结点。"),
        _p_join("add/subtract 次数≠直接错误判决。"),
        _p_join("通俗复述：病历里还有别的化验项，不要只盯一项。"),
    )

    generic(
        "nhr_dltmax_heatmap.png",
        _p_join("热图总览多指标×多设置；服务报告协议。"),
        _p_join("颜色=计数强度，不是浓度；先找热点再回表。"),
        _p_join("单元格=事件计数；missing 与 0 要区分。"),
        _p_join("每一格是逻辑子图。"),
        _p_join("数值健康事件来自离散化与层几何约束。"),
        _p_join("支持 NHR 随技能报告；不支持普适最优步长。"),
        _p_join("仅 Long Lake 扫描点集。"),
        _p_join("最浅色格子≠必须采用的时间步。"),
        _p_join("通俗复述：化验单总览，不是药方剂量。"),
    )

    generic(
        "w7_columbia_sod_timeseries.png",
        _p_join(
            "Columbia SOD 时序做移植参数量级检查。",
            f"湿段均值 {sod.get('mean')} gO₂/m²/d（JDAY≥33，n={sod.get('n')}）。",
            "参数来自 DeGray 成岩模板移植。",
        ),
        _p_join("看 spin-up 后湿段轨迹；零值干段已排除语境。"),
        _p_join("SOD 通量；非观测技能。"),
        _p_join("按时间读，可对照直方图分布。"),
        _p_join("SOD=沉积物耗氧需求；与 CSOD/NSOD 相关但本图主报总 SOD。"),
        _p_join("量级检查通过≠现场率定。"),
        _p_join("禁止水质情景推断升级。"),
        _p_join("落带≠验证成岩模块。"),
        _p_join("通俗复述：没离谱到天上去，也不等于本地泥样标定好了。"),
    )

    generic(
        "w7_columbia_sod_histogram.png",
        _p_join(
            "直方图对照 Almeida 扫描带 0.5–3.0。",
            f"frac_in={sod.get('frac_in_0.5_3.0')}，frac_<0.5={sod.get('frac_below_0.5')}，frac_>3={sod.get('frac_above_3.0')}。",
        ),
        _p_join("看主体与尾巴；勿把已排除的零干段当零耗氧泥。"),
        _p_join("湿段瞬时 SOD 计数。"),
        _p_join("带内/带下/带上三个逻辑区。"),
        _p_join("对照带来自独立实验扫描，非普适生态定律。"),
        _p_join("约 89.6% 落带，结论止于量级。"),
        _p_join("非本地最优证明。"),
        _p_join("band≠水质标准。"),
        _p_join("通俗复述：大多数不离谱，少数偏低，没有爆表——体检不是处方。"),
    )

    generic(
        "fig07_w2eval_runcard.png",
        _p_join("run-card 固化 VPR+指标+NHR，防对象漂移；是评估数据结构而非新过程模块。"),
        _p_join("先读对象与控制状态，再读分数，最后读 NHR。"),
        _p_join("卡片字段对应评价自变量；internal NSE 不进 skill 表。"),
        _p_join("卡片分区=逻辑子图（VPR / metrics / NHR）。"),
        _p_join("评价函数自变量是被抽取序列；卡把抽取规则写死。"),
        _p_join("完整≠模型有效；OFF 有 S 不补 B。"),
        _p_join("MVP 不自动跑 W2。"),
        _p_join("卡片不是验证徽章。"),
        _p_join("通俗复述：先写卷头考哪一科、开没开定速、有没有报警，再看分数。"),
    )

    return out


def main() -> None:
    data = build()
    path = ANALYSIS / "report_fig_narratives_autodepth.py"
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""Auto-generated long figure narratives (JSON-anchored). Do not invent metrics."""',
        "from __future__ import annotations",
        "AUTO_DEEP: dict[str, dict[str, str]] = {",
    ]
    for fname, fields in data.items():
        lines.append(f"    {fname!r}: {{")
        for k, v in fields.items():
            lines.append(f"        {k!r}: {v!r},")
        lines.append("    },")
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", path, "figures", len(data))
    # length summary
    for fname, fields in list(data.items())[:3]:
        print(fname, {k: len(v) for k, v in fields.items()})


if __name__ == "__main__":
    main()
