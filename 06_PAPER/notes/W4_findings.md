# W4 发现：DART CCIW 下载、库内核对、样本外框架

生成时间：2026-08-16T13:59:17+08:00
脚本：`00_INDEX/download_dart_cciw.py`

## 1. DART 如何脚本化下载

查询页表单 `GET /dart/cs/php/rpt/wqm_hourly.php`，字段：`year`, `proj`, `startdate`, `days`, `outputFormat`, 可选 `datalink=1`。

勾选 Generate Query Result Link Only 后返回的脚本 URL 模式：

```
https://cbr.washington.edu/dart/cs/php/rpt/wqm_hourly.php?sc=1&year=2011&proj=CCIW&startdate=01%2F01&days=365&outputFormat=csv
```

关键参数 **`sc=1`**（script call）。无 `sc=1` 时服务器 302 到 Drupal wrapper HTML。

本次下载：成功 15 年（2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025）。提前停止：False。
失败记录：无。

礼貌策略：先通 2011 一年，再按年扩展；年与年之间暂停 3 s；HTTP 403/429/503 不重试死循环。
Windows 上 Python `urllib` 对本站全年 CSV 会报 `SSLError: ASN1 NOT_ENOUGH_DATA`，脚本改走 `curl.exe --http1.1`（已验证 200 + `text/csv`）。

## 2. 库内 CCIW vs DART（2011–2015）

库内文件：`02_LIBRARY/06_examples/v5.0_beta/Bonneville_TDG/CCIW_TDG_Temp_2011-2015.csv`
（头注释：CWMS，由 `6_TDG_data_to_W2npt_v2.py` 于 2017-12-21 生成）。
JDAY 纪元：Excel 序列，**40544 = 2011-01-01**（原点 1899-12-30）。与 `w2_con.csv` TMSTRT 一致。

时间对齐（已用 2011-04-01 逐点核实）：

- DART `Date` + `Hour` 100…2400 为该日历日的小时终止时刻（Pacific Timestamp 比库内标签晚 1 小时）。
- 库内 `Datetime` 的小时 h 对应 DART Hour `(h+1)*100`。
- 例：库内 `4/1/2011 0:00` TDG=111.9 ↔ DART Hour 100 / `2011-04-01 01:00:00-07` TDG=111.88。

小时配对（双方 TDG 均有效）：

- n = 17805
- MAE = 0.026537，RMSE = 0.04124，bias = -0.000613
- |Δ|≤0.051（1 位小数修约带）匹配率 = 0.994945
- 四舍五入（half-up）到 1 位后匹配率 = 0.941196
- |Δ|>0.15 的点数 = 56；|Δ|>1 的点数 = 5；max |Δ| = 1.9
- 分年：
  - 2011: n=1613, MAE=0.027371, 匹配率=0.984501, |Δ|>0.15=16, max|Δ|=0.39
  - 2012: n=3648, MAE=0.030641, 匹配率=0.982182, |Δ|>0.15=40, max|Δ|=1.9
  - 2013: n=3987, MAE=0.025267, 匹配率=1.0, |Δ|>0.15=0, max|Δ|=0.05
  - 2014: n=4196, MAE=0.025541, 匹配率=1.0, |Δ|>0.15=0, max|Δ|=0.05
  - 2015: n=4361, MAE=0.024914, 匹配率=1.0, |Δ|>0.15=0, max|Δ|=0.05

库内有效小时 17808 / 总小时 43825（缺失率 0.593657）。
DART 2011–2015 有效小时 17924 / 43824。
库内有效但未配上 DART：0；DART 有效但库内无对应：0。

日均配对：n = 755，MAE = 0.020363，匹配率 = 0.978808。

**结论：** 库内 CCIW 与 2026 年下载的 DART 原始小时值在重叠期高度一致：MAE 约 0.03%、绝大多数点落在 1 位小数修约带内。少数 |Δ|>0.15 的点共 56 个（其中 |Δ|>1 的 5 个，几乎全在 2011–2012；2013–2015 匹配率 = 1.0），更像 CWMS（2017 提取）与 DART（2026 下载）之间的事后修订，而不是示例被改写。**没有证据表明官方示例附带观测被实质性改过。**

冬季大量 −999 / 空值是监测季节性，不是库内独有的删改。

## 3. 2016–2025 超标与可达范围（样本外数据已就绪，NSE 未做）

2016–2025 的 DART CCIW 小时 TDG/Spill 已下载并完成超标统计；**没有**计算样本外 NSE——模型尚未跑 2016 以后，不能假装有预报技能。

2011–2015（DART，有效小时）：>115% = 68.9746%，>120% = 14.6842%，最大 TDG = 138.53%。
2016–2025（DART，有效小时）：>115% = 67.4754%，>120% = 21.2%，最大 TDG = 132.59%，有效小时 n = 40434。

样本外十年的超 120% 比例（21.2%）**高于**示例期（14.7%），封顶问题没有随时间消失。2015 年有效小时中 0% 超过 120%（年最大 118.97%），2017 年则有 46.9%（年最大 131.38%）。

| 年 | 有效小时 | >115% 占有效小时 % | >120% 占有效小时 % | 年最大 TDG % |
|---:|---:|---:|---:|---:|
| 2011 | 1638 | 69.2918 | 15.5067 | 129.08 |
| 2012 | 3676 | 73.123 | 39.5267 | 138.53 |
| 2013 | 4044 | 75.0742 | 9.7428 | 130.7 |
| 2014 | 4204 | 73.4776 | 12.6308 | 124.67 |
| 2015 | 4362 | 55.3645 | 0.0 | 118.97 |
| 2016 | 4383 | 66.8948 | 5.7951 | 123.27 |
| 2017 | 4710 | 71.0191 | 46.9214 | 131.38 |
| 2018 | 3519 | 50.0142 | 15.6579 | 131.02 |
| 2019 | 4486 | 69.8618 | 9.2733 | 123.68 |
| 2020 | 4166 | 74.2199 | 25.3 | 124.93 |
| 2021 | 4027 | 70.5736 | 7.7477 | 122.0 |
| 2022 | 3278 | 77.3948 | 30.4454 | 132.59 |
| 2023 | 3378 | 77.2943 | 22.4097 | 125.17 |
| 2024 | 4322 | 61.9852 | 12.3554 | 121.69 |
| 2025 | 4165 | 56.4466 | 35.6783 | 123.12 |

这直接服务创新点 2 的「可达范围 / 封顶」叙事：观测中超过 120% 的点在 TDGTA 目标带外，结构上不可能被控制器复现。

百分比分母是**有效小时**，不是日历小时。CCIW 冬季常缺测。

## 4. 泄流对照（TDGTA ON vs DART vs QGT 输入）

模型时段：w2_con.csv TMSTRT=40544 TMEND=40909 → 2011-01-01 through 2012-01-01. TDGTarget_output.csv therefore covers ~2011 only, not 2011–2015.

列映射：Q1=厂房 POWR1，Q2–Q19=溢洪道 SB1–SB18，Q20=OTHER。泄流 = (Q2–Q20)/28.316846592 kcfs。
C 列：R = 当日 TDG 超目标、控制器进入再分配；U = 迭代后仍超；空 = 未切流量。

配对日数 365。
控制器标志：R=116，U=0，空白=249。

TDGTA 泄流 vs DART 日均 Spill：n=365，MAE=57.555189 kcfs，bias=-48.782125，r=0.237349。
QGT 输入 vs DART：r=0.868638（输入文件大体跟着实际泄流）。
控制器相对 QGT 输入：MAE=50.501534 kcfs，|Δspill|>1 kcfs 的天数 = 116（与 R 日数相同）。
再分配日（R/U）：DART 均泄 173.8573 kcfs vs TDGTA 39.2308 kcfs，r=-0.596447。
空白日：DART 19.8623 vs TDGTA 11.0719。

**结论：** 控制器在 R 日把泄流从与实测相近的 QGT 方案大幅砍向厂房。QGT 对 DART 的相关远高于 TDGTA 对 DART。这是创新点 2 的独立证据：TDGTA ON 的低偏差/封顶，部分来自「把泄流调成与 2011 年实际运行不同的方案」，而不是单纯把物理过程拟合得更好。

## 5. 文件

- 原始小时：`06_PAPER/data/dart_cciw/cciw_hourly_YYYY.csv`
- 下载日志：`06_PAPER/data/dart_cciw/download_log.json`
- 统计：`06_PAPER/analysis/w4_cciw_vs_dart.json`
- 图：`06_PAPER/analysis/w4_cciw_vs_dart_scatter.png`、`w4_cciw_vs_dart_timeseries.png`、`w4_tdg_gt120_annual.png`、`w4_tdg_annual_max.png`、`w4_spill_tdgta_vs_dart.png`、`w4_spill_scatter.png`

数据引用：Columbia River DART, Columbia Basin Research, University of Washington. Hourly Water Quality Measurements. https://cbr.washington.edu/dart/query/wqm_hourly （下载于 2026-08-16）。原始观测来自 USACE NWD。


## 人工下载步骤（若脚本被拦）

1. 打开 https://cbr.washington.edu/dart/query/wqm_hourly
2. Output Format 选 **CSV File**；Year 选目标年；Site 选 **CCIW**。
3. Start Date 填 `01/01`；Hours 选 **365 Days (8760 hours)**（闰年再补 12/31 一天）。
4. 勾选 **Generate Query Result Link Only** 再 Submit，页面会给出带 `sc=1` 的脚本 URL。
5. 或不勾选直接 Submit，浏览器下载 `wqmhourly_*.csv`。
6. 把文件存到 `06_PAPER/data/dart_cciw/cciw_hourly_YYYY.csv`。
7. 备选：USACE NWD Water Control Data / dataquery
   https://www.nwd.usace.army.mil/CRWM/Water-Control-Data/
   站点 Cascade Island / Bonneville tailwater，参数 TDG%、Spill。
