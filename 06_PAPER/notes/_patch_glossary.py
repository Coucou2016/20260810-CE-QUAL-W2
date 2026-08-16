# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"I:\Projects\20260810-CE-QUAL-W2\06_PAPER\analysis\build_research_report.py")
text = p.read_text(encoding="utf-8")
start = text.index("    def build_glossary(self) -> None:")
end = text.index("    def build_background(self) -> None:")

new = r'''    def build_glossary(self) -> None:
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

'''

text = text[:start] + new + text[end:]
if '("封面", "cover")' not in text:
    text = text.replace(
        'toc = [\n            ("摘要", "abstract"),',
        'toc = [\n            ("封面", "cover"),\n            ("摘要", "abstract"),',
    )
    print("inserted cover in toc")
else:
    print("cover already in toc")

p.write_text(text, encoding="utf-8")
print("ok")
