# CE-QUAL-W2 三案例复现与可视化报告

> 生成时间：2026-08-16 11:18:47  
> 运行目录：`05_REPRO_RUNS/run_20260811_fixed`  
> 可执行文件：`02_LIBRARY/07_executables/v4.5.5/w2_v455_ifx.exe`

## 1. 摘要
用户所见 “Round them error” 经核实为 Intel Fortran `forrtl: severe (29): file not found`。本轮在修复后完成三案例重跑，并补充流域/区域底图与外部经验章节。

## 2. forrtl 修复
- **原因1（Long Lake）**：`w2_habitat.npt` 输出路径 `.\HabitatFiles\habitat.csv`，目录缺失。
- **原因2（Columbia）**：`SED_DIAG=ON` 但缺少 `W2_diagenesis.npt`。
- **修复**：创建 `HabitatFiles`；权威三案例中 Columbia 关闭 `SED_DIAG`；另在 `run_20260814_columbia_diag` 用改编的 `W2_diagenesis.npt` 接通成岩。
- **验证**：见下表（真实 exit code / 用时 / TSR 行数）。

| 案例 | exit | 秒 | forrtl | TSR文件数/最大行数 | w2.err |
|---|---:|---:|---|---|---|
| Long Lake | 0 | 302.46 | False | 8/2391 | 空 |
| DeGray Reservoir with sediment diagenesis and vertical algae migration | 0 | 1274.4 | False | 1/2944 | 空 |
| Columbia Slough Estuary | 0 | 323.25 | False | 3/117 | 空 |

## 3. 数据与方法
术语：TSR=时间序列；CPL=等值线/纵剖面；PRF=剖面；ELWS=水面高程；T2=水温；DO=溶解氧；PHI0=分段方位角（自正北顺时针）；DLX=分段长度。
底图：Esri 卫星/地形瓦片本地缓存 + OSM 参考河道 + 多控制点配准；侧向偏移量化见 `*_alignment_error.png`。

**方位修正：** Long Lake / DeGray 曾把上游浅端锚到坝址，旋转弦反向后呈南北横切镜像（或端点对调）；现坝锚在下游深水端。Columbia Slough 口@end 本来正确。

**叠图偏差诊断：** 主要不是投影问题。Esri Web Mercator 瓦片用 lon/lat 角点显示，本窗口错位约 20–25 m。公里级北偏来自 PHI0/DLX 示意路径 + 曾用坝锚刚性朝库心旋转（中点残差约 10.5 km、侧向约 2–5 km）。Long Lake 已改为坝+Nine Mile 两点相似变换；弯道仍可能有公里级残差。w2_con LAT/LONG 仅为辐射单点。

## 4. 结果可视化

### 图 1　Long Lake 多断面时间序列

![图 1　Long Lake 多断面时间序列](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Long_Lake_timeseries.png)

- **如何读图：** 横轴为儒略日 JDAY（Julian day，年积日模型时间）；纵轴为水位 ELWS（Elevation of Water Surface，水面高程）、水温 T2（Temperature）、水深 DEPTH，以及溶解氧 DO（Dissolved Oxygen）等可用变量。不同颜色曲线对应不同河段 segment。
- **含义：** 用于检查模型是否完成有效时间推进、各观测断面响应是否连续。状态：ok；点数示例：2390；变量：ELWS(m), T2(C), DEPTH(m), Gen1。
- **结论：** 若曲线随时间变化且点数显著大于 1，说明本次运行已产出可用 TSR（time series，时间序列），而非秒退空图。本图本身不是率定对比，观测对照链仍待补充。

### 图 2　Long Lake 河道/库区俯视与沿程剖面

![图 2　Long Lake 河道/库区俯视与沿程剖面](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Long_Lake_planview.png)

- **如何读图：** 左图由地形文件 bth*.csv（bathymetry，水下地形）用 PHI0（segment orientation，分段方位角）与 DLX（segment length，分段长度）重建相对平面中心线与近似岸线，颜色为近似水深；右图为沿程水深与表层宽度。
- **含义：** 建立相对空间骨架，帮助阅读后续纵剖面/等值线。状态：ok；河段数：37。
- **结论：** 该图是模型网格几何的内部坐标系表达，不自动等于真实大地坐标；需结合流域底图判断位置是否合理。

### 图 3　Long Lake 流域/区域底图与河道走向叠置

![图 3　Long Lake 流域/区域底图与河道走向叠置](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Long_Lake_watershed_basemap.png)

- **如何读图：** 左图为本地缓存的真实卫星影像（Esri World Imagery）：可见真实水系/库面与地表纹理；黄/黑线为模型中心线按坝址或源-口参考点配准后的叠置；方块/圆点为公开可核验参考点（坝、河口、库心等），橙色×为控制文件水体 LAT/LONG。右图为同范围 Esri World Topo Map 本地缓存（道路/水系/地名），并放大显示分段、近似岸线与水深着色。两图均含经纬网与比例尺。
- **含义：** 地点：Long Lake / Lake Spokane, Spokane River, Washington, USA；控制文件锚点 lat=47.8，lon(西经正值)=117.8；来源：w2_con.csv。控制文件水体 LATITUDE/LONGITUDE（太阳辐射用单点，非分段端点） 公开参考：Long Lake Dam ~47.8372, -117.8397 (Wikipedia / GNIS Long Lake Dam);；Nine Mile Dam (US) ~47.7748, -117.5447 (DamLookup / NID WA00068);；Lake Spokane center ~47.8315, -117.7626 (WDFW Lake Spokane);；w2_con LAT/LONG ~47.8000, -117.8000 (case w2_con.csv solar site)。底图：Esri World Imagery + Esri World Topo Map (local cache: basemap_cache/Long_Lake/)。 精度状态：示意叠置（真实底图 + OSM 参考河道 + 多控制点配准）。可信任：区域是否正确、端点方位是否大致合理、侧向偏移量级（相对 OSM）。不可信任：弯道与岸线的精密贴合、米级绝对位置。。 侧向偏移（相对 OSM 参考河道 OSM merged Spokane/Long Lake/Lake Spokane (112 pts clipped)）：改进前 均值722.3m / 最大1847.3m / P951652.4m → 改进后 均值722.3m / 最大1847.3m / P951652.4m。 选用配准：baseline_two_point（two_point_similarity）。
- **结论：** 应能一眼辨认真实 Long Lake / DeGray / Columbia Slough 区域；可用于核验模型走向是否落在正确水体附近。参考河道来自 OSM Overpass 缓存（basemap_cache/*/osm_waterways.geojson）；配准在两点相似/多点相似/TPS 间自动择优。几何形状残差（PHI0 示意路径≠真实弯道）与配准残差（控制点有限）在侧向偏移图中分开量化。配准：two_point_similarity；本地缓存：I:\Projects\20260810-CE-QUAL-W2\05_REPRO_RUNS\run_20260811_fixed\analysis\basemap_cache\Long_Lake。 【偏差说明】投影：Web Mercator 瓦片用 lon/lat 角点显示，本窗口错位约20–25 m，不是公里级偏航原因。 【方位修正】曾误把水库上游浅端锚到坝址，旋转弦反向后表现为南北向（横切河道）镜像；现按 W2 段号递增=上游→下游、最深湿段≈坝，将坝/口锚在模型下游端。PHI0：自正北顺时针 ΔE=sin、ΔN=cos。

### 图 4　Long Lake 侧向偏移沿程图

![图 4　Long Lake 侧向偏移沿程图](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Long_Lake_alignment_error.png)

- **如何读图：** 横轴为沿模型河段累计距离（km）；纵轴为模型中心线各分段中心到 OSM 参考河道折线的最短侧向距离（km）。虚线为均值，点线为 P95。
- **含义：** 参考：OSM merged Spokane/Long Lake/Lake Spokane (112 pts clipped)；配准方法：two_point_similarity。 侧向偏移（相对 OSM 参考河道 OSM merged Spokane/Long Lake/Lake Spokane (112 pts clipped)）：改进前 均值722.3m / 最大1847.3m / P951652.4m → 改进后 均值722.3m / 最大1847.3m / P951652.4m。 选用配准：baseline_two_point（two_point_similarity）。
- **结论：** 用于区分「配准可改进部分」与「PHI0 示意几何本身与真实河道不一致」的残差量级；若改进后均值仍 &gt;500 m，通常说明模型平面形状与 OSM 河道差异占主导，而非底图投影问题。

### 图 5　Long Lake 纵剖面/等值线

![图 5　Long Lake 纵剖面/等值线](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Long_Lake_profile.png)

- **如何读图：** 优先使用 CPL（contour plot，等值线/纵剖面输出）或 PRF（profile，剖面输出）中的温度场；若 CPL/PRF 未能解析，则回退为地形宽度场示意并明确标注。
- **含义：** 展示纵向-垂向二维温度（或回退几何场）结构。状态：ok；来源：cpl1.opt。温度范围：2.52–6.03 ℃。
- **结论：** 该类图是 W2 报告中最常见的“分层/纵剖面”呈现；若缺可解析温度场，报告已标注回退，不伪装为观测对比。

### 图 6　DeGray Reservoir 多断面时间序列

![图 6　DeGray Reservoir 多断面时间序列](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/DeGray_timeseries.png)

- **如何读图：** 横轴为儒略日 JDAY（Julian day，年积日模型时间）；纵轴为水位 ELWS（Elevation of Water Surface，水面高程）、水温 T2（Temperature）、水深 DEPTH，以及溶解氧 DO（Dissolved Oxygen）等可用变量。不同颜色曲线对应不同河段 segment。
- **含义：** 用于检查模型是否完成有效时间推进、各观测断面响应是否连续。状态：ok；点数示例：2943；变量：ELWS(m), T2(C), DEPTH(m), DO, ALG1。
- **结论：** 若曲线随时间变化且点数显著大于 1，说明本次运行已产出可用 TSR（time series，时间序列），而非秒退空图。本图本身不是率定对比，观测对照链仍待补充。

### 图 7　DeGray Reservoir 河道/库区俯视与沿程剖面

![图 7　DeGray Reservoir 河道/库区俯视与沿程剖面](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/DeGray_planview.png)

- **如何读图：** 左图由地形文件 bth*.csv（bathymetry，水下地形）用 PHI0（segment orientation，分段方位角）与 DLX（segment length，分段长度）重建相对平面中心线与近似岸线，颜色为近似水深；右图为沿程水深与表层宽度。
- **含义：** 建立相对空间骨架，帮助阅读后续纵剖面/等值线。状态：ok；河段数：32。
- **结论：** 该图是模型网格几何的内部坐标系表达，不自动等于真实大地坐标；需结合流域底图判断位置是否合理。

### 图 8　DeGray Reservoir 流域/区域底图与河道走向叠置

![图 8　DeGray Reservoir 流域/区域底图与河道走向叠置](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/DeGray_watershed_basemap.png)

- **如何读图：** 左图为本地缓存的真实卫星影像（Esri World Imagery）：可见真实水系/库面与地表纹理；黄/黑线为模型中心线按坝址或源-口参考点配准后的叠置；方块/圆点为公开可核验参考点（坝、河口、库心等），橙色×为控制文件水体 LAT/LONG。右图为同范围 Esri World Topo Map 本地缓存（道路/水系/地名），并放大显示分段、近似岸线与水深着色。两图均含经纬网与比例尺。
- **含义：** 地点：DeGray Lake / Reservoir, Caddo River, Arkansas, USA；控制文件锚点 lat=34.2，lon(西经正值)=93.3；来源：w2_con.csv。控制文件水体 LATITUDE/LONGITUDE（太阳辐射用单点，非分段端点） 公开参考：DeGray Dam ~34.2140, -93.1113 (TopoQuest / USGS GNIS De Gray Dam);；Caddo River head (NW) ~34.3520, -93.3480 (OSM Caddo River / reservoir NW extent);；DeGray Lake (GNIS) ~34.2520, -93.1992 (TopoQuest / USGS GNIS De Gray Lake);；w2_con LAT/LONG ~34.2000, -93.3000 (case w2_con.csv solar site)。底图：Esri World Imagery + Esri World Topo Map (local cache: basemap_cache/DeGray/)。 精度状态：示意叠置（真实底图 + OSM 参考河道 + 多控制点配准）。可信任：区域是否正确、端点方位是否大致合理、侧向偏移量级（相对 OSM）。不可信任：弯道与岸线的精密贴合、米级绝对位置。。 侧向偏移（相对 OSM 参考河道 OSM merged Caddo/DeGray/De Gray (199 pts clipped)）：改进前 均值12271.3m / 最大26989.3m / P9525447.0m → 改进后 均值331.3m / 最大1148.3m / P951082.0m。 选用配准：tps_arc（tps_5pt）。
- **结论：** 应能一眼辨认真实 Long Lake / DeGray / Columbia Slough 区域；可用于核验模型走向是否落在正确水体附近。参考河道来自 OSM Overpass 缓存（basemap_cache/*/osm_waterways.geojson）；配准在两点相似/多点相似/TPS 间自动择优。几何形状残差（PHI0 示意路径≠真实弯道）与配准残差（控制点有限）在侧向偏移图中分开量化。配准：tps_5pt；本地缓存：I:\Projects\20260810-CE-QUAL-W2\05_REPRO_RUNS\run_20260811_fixed\analysis\basemap_cache\DeGray。 【偏差说明】投影：Web Mercator 瓦片用 lon/lat 角点显示，本窗口错位约20–25 m，不是公里级偏航原因。 【方位修正】曾误把水库上游浅端锚到坝址，旋转弦反向后表现为南北向（横切河道）镜像；现按 W2 段号递增=上游→下游、最深湿段≈坝，将坝/口锚在模型下游端。PHI0：自正北顺时针 ΔE=sin、ΔN=cos。

### 图 9　DeGray Reservoir 侧向偏移沿程图

![图 9　DeGray Reservoir 侧向偏移沿程图](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/DeGray_alignment_error.png)

- **如何读图：** 横轴为沿模型河段累计距离（km）；纵轴为模型中心线各分段中心到 OSM 参考河道折线的最短侧向距离（km）。虚线为均值，点线为 P95。
- **含义：** 参考：OSM merged Caddo/DeGray/De Gray (199 pts clipped)；配准方法：tps_5pt。 侧向偏移（相对 OSM 参考河道 OSM merged Caddo/DeGray/De Gray (199 pts clipped)）：改进前 均值12271.3m / 最大26989.3m / P9525447.0m → 改进后 均值331.3m / 最大1148.3m / P951082.0m。 选用配准：tps_arc（tps_5pt）。
- **结论：** 用于区分「配准可改进部分」与「PHI0 示意几何本身与真实河道不一致」的残差量级；若改进后均值仍 &gt;500 m，通常说明模型平面形状与 OSM 河道差异占主导，而非底图投影问题。

### 图 10　DeGray Reservoir 纵剖面/等值线

![图 10　DeGray Reservoir 纵剖面/等值线](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/DeGray_profile.png)

- **如何读图：** 优先使用 CPL（contour plot，等值线/纵剖面输出）或 PRF（profile，剖面输出）中的温度场；若 CPL/PRF 未能解析，则回退为地形宽度场示意并明确标注。
- **含义：** 展示纵向-垂向二维温度（或回退几何场）结构。状态：ok；来源：cpl.opt。温度范围：6.50–7.40 ℃。
- **结论：** 该类图是 W2 报告中最常见的“分层/纵剖面”呈现；若缺可解析温度场，报告已标注回退，不伪装为观测对比。

### 图 11　Columbia Slough Estuary 多断面时间序列

![图 11　Columbia Slough Estuary 多断面时间序列](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Columbia_Slough_timeseries.png)

- **如何读图：** 横轴为儒略日 JDAY（Julian day，年积日模型时间）；纵轴为水位 ELWS（Elevation of Water Surface，水面高程）、水温 T2（Temperature）、水深 DEPTH，以及溶解氧 DO（Dissolved Oxygen）等可用变量。不同颜色曲线对应不同河段 segment。
- **含义：** 用于检查模型是否完成有效时间推进、各观测断面响应是否连续。状态：ok；点数示例：116；变量：ELWS(m), T2(C), DEPTH(m), DO。
- **结论：** 若曲线随时间变化且点数显著大于 1，说明本次运行已产出可用 TSR（time series，时间序列），而非秒退空图。本图本身不是率定对比，观测对照链仍待补充。

### 图 12　Columbia Slough Estuary 河道/库区俯视与沿程剖面

![图 12　Columbia Slough Estuary 河道/库区俯视与沿程剖面](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Columbia_Slough_planview.png)

- **如何读图：** 左图由地形文件 bth*.csv（bathymetry，水下地形）用 PHI0（segment orientation，分段方位角）与 DLX（segment length，分段长度）重建相对平面中心线与近似岸线，颜色为近似水深；右图为沿程水深与表层宽度。
- **含义：** 建立相对空间骨架，帮助阅读后续纵剖面/等值线。状态：ok；河段数：51。
- **结论：** 该图是模型网格几何的内部坐标系表达，不自动等于真实大地坐标；需结合流域底图判断位置是否合理。

### 图 13　Columbia Slough Estuary 流域/区域底图与河道走向叠置

![图 13　Columbia Slough Estuary 流域/区域底图与河道走向叠置](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Columbia_Slough_watershed_basemap.png)

- **如何读图：** 左图为本地缓存的真实卫星影像（Esri World Imagery）：可见真实水系/库面与地表纹理；黄/黑线为模型中心线按坝址或源-口参考点配准后的叠置；方块/圆点为公开可核验参考点（坝、河口、库心等），橙色×为控制文件水体 LAT/LONG。右图为同范围 Esri World Topo Map 本地缓存（道路/水系/地名），并放大显示分段、近似岸线与水深着色。两图均含经纬网与比例尺。
- **含义：** 地点：Columbia Slough (Fairview Lake → Willamette), Portland, Oregon, USA；控制文件锚点 lat=45.6，lon(西经正值)=122.6；来源：w2_con.csv。控制文件水体 LATITUDE/LONGITUDE（太阳辐射用单点，非分段端点） 公开参考：Slough mouth (Willamette) ~45.6433, -122.7686 (Wikipedia Columbia Slough);；Slough source (Fairview Lk) ~45.5500, -122.4567 (Wikipedia Columbia Slough);；w2_con LAT/LONG ~45.6000, -122.6000 (case w2_con.csv solar site)。底图：Esri World Imagery + Esri World Topo Map (local cache: basemap_cache/Columbia_Slough/)。 精度状态：示意叠置（真实底图 + OSM 参考河道 + 多控制点配准）。可信任：区域是否正确、端点方位是否大致合理、侧向偏移量级（相对 OSM）。不可信任：弯道与岸线的精密贴合、米级绝对位置。。 侧向偏移（相对 OSM 参考河道 OSM merged Columbia Slough/Slough (730 pts clipped)）：改进前 均值554.0m / 最大2123.6m / P951953.5m → 改进后 均值554.0m / 最大2123.6m / P951953.5m。 选用配准：baseline_two_point（two_point_similarity）。
- **结论：** 应能一眼辨认真实 Long Lake / DeGray / Columbia Slough 区域；可用于核验模型走向是否落在正确水体附近。参考河道来自 OSM Overpass 缓存（basemap_cache/*/osm_waterways.geojson）；配准在两点相似/多点相似/TPS 间自动择优。几何形状残差（PHI0 示意路径≠真实弯道）与配准残差（控制点有限）在侧向偏移图中分开量化。配准：two_point_similarity；本地缓存：I:\Projects\20260810-CE-QUAL-W2\05_REPRO_RUNS\run_20260811_fixed\analysis\basemap_cache\Columbia_Slough。 【偏差说明】投影：Web Mercator 瓦片用 lon/lat 角点显示，本窗口错位约20–25 m，不是公里级偏航原因。 【方位核验】Columbia Slough 源→口段序与多点配准本来正确；残差来自模型曲折与真实岸线差异。

### 图 14　Columbia Slough Estuary 侧向偏移沿程图

![图 14　Columbia Slough Estuary 侧向偏移沿程图](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Columbia_Slough_alignment_error.png)

- **如何读图：** 横轴为沿模型河段累计距离（km）；纵轴为模型中心线各分段中心到 OSM 参考河道折线的最短侧向距离（km）。虚线为均值，点线为 P95。
- **含义：** 参考：OSM merged Columbia Slough/Slough (730 pts clipped)；配准方法：two_point_similarity。 侧向偏移（相对 OSM 参考河道 OSM merged Columbia Slough/Slough (730 pts clipped)）：改进前 均值554.0m / 最大2123.6m / P951953.5m → 改进后 均值554.0m / 最大2123.6m / P951953.5m。 选用配准：baseline_two_point（two_point_similarity）。
- **结论：** 用于区分「配准可改进部分」与「PHI0 示意几何本身与真实河道不一致」的残差量级；若改进后均值仍 &gt;500 m，通常说明模型平面形状与 OSM 河道差异占主导，而非底图投影问题。

### 图 15　Columbia Slough Estuary 纵剖面/等值线

![图 15　Columbia Slough Estuary 纵剖面/等值线](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260811_fixed/analysis/Columbia_Slough_profile.png)

- **如何读图：** 优先使用 CPL（contour plot，等值线/纵剖面输出）或 PRF（profile，剖面输出）中的温度场；若 CPL/PRF 未能解析，则回退为地形宽度场示意并明确标注。
- **含义：** 展示纵向-垂向二维温度（或回退几何场）结构。状态：ok_prf_vertical；来源：prf.opt。温度范围：4.50–4.50 ℃。
- **结论：** 该类图是 W2 报告中最常见的“分层/纵剖面”呈现；若缺可解析温度场，报告已标注回退，不伪装为观测对比。


## 4b. Bonneville SYSTDG 模型–观测对照

运行目录：`05_REPRO_RUNS/run_20260814_bonneville`。观测：CCIW 2011 年小时 TDG/水温。

库内 TSR：

| 断面文件 | 变量 | n | MAE | RMSE | NRMSE | NSE |
|---|---|---:|---:|---:|---:|---:|
| BON_tsr_1_seg40.csv | TDG_pct | 1614 | 6.8404 | 8.1503 | 0.3809 | -2.7516 |
| BON_tsr_1_seg40.csv | Temperature_C | 2433 | 1.1414 | 1.3325 | 0.0775 | 0.9529 |
| BON_tsr_2_seg43.csv | TDG_pct | 1614 | 6.8765 | 8.1772 | 0.3821 | -2.7764 |
| BON_tsr_2_seg43.csv | Temperature_C | 2433 | 1.1461 | 1.3476 | 0.0783 | 0.9519 |

坝段 76 下泄（N2+DO→TDG%，对照变量不当）：

| 对照口径 | n | MAE | RMSE | NRMSE | NSE |
|---|---:|---:|---:|---:|---:|
| TSR_seg40_formula_vs_W2_TDG | 8759 | 0.3012 | 0.3044 | 0.0085 | 0.9992 |
| c_wdo_76_TDG_vs_CCIW | 1614 | 6.8783 | 8.2075 | 0.3835 | -2.8044 |
| t_wdo_76_T_vs_CCIW | 2433 | 1.1023 | 1.2905 | 0.075 | 0.9559 |

SYSTDG 自身 TDG_TDG：

| 对照口径 | n | MAE | RMSE | NRMSE | NSE | sim_max |
|---|---:|---:|---:|---:|---:|---:|
| SYSTDG_TDG_vs_CCIW | 1614 | 2.1957 | 2.9756 | 0.139 | 0.5 | 120.09 |
| SYSTDG_TDG_vs_CCIW_obsGT120 | 251 | 4.9001 | 5.6791 | 0.631 | -8.4963 | 120.09 |
| SYSTDG_TDG_vs_CCIW_obsLE120 | 1363 | 1.6976 | 2.1319 | 0.1733 | 0.6598 | 120.09 |



### 图 16　Bonneville 库内 TSR TDG 时序（seg40 vs CCIW）

![图 16　Bonneville 库内 TSR TDG 时序（seg40 vs CCIW）](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_BON_tsr_1_seg40_TDG_pct_timeseries.png)

- **如何读图：** 横轴为 Excel 序列日 JDAY（2011 年约 40544–40909）；蓝点为 CCIW（Columbia River at Bonneville Dam tailwater，坝下尾水）小时观测总溶解气体饱和度 TDG（Total Dissolved Gas，%）；折线为库内河段 40 的模型 TSR。缺测值 −999 已剔除。
- **含义：** 用于把 SYSTDG（System Total Dissolved Gas，系统总溶解气体经验模块）写入 W2 后的库内 TDG 与坝下站点对照。CCIW 是坝下尾水，模型 TSR 是库内 seg40，空间位置不完全等同。
- **结论：** 库内对照的 TDG NSE 为负；下一组图改用坝段 76 下泄输出，检验是否只是断面选错。

### 图 17　Bonneville 库内 TSR TDG 1:1 散点（seg40）

![图 17　Bonneville 库内 TSR TDG 1:1 散点（seg40）](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_BON_tsr_1_seg40_TDG_pct_scatter.png)

- **如何读图：** 横轴观测、纵轴模拟；虚线为 1:1。点落在线上方表示模拟偏高，下方表示模拟偏低。
- **含义：** MAE / RMSE / NSE（Nash–Sutcliffe efficiency，纳什效率系数：1 为完美，0 等同用均值预测，负值差于均值）见散点标题与表。
- **结论：** TDG 的 NSE 为负，说明在本对照口径下尚未达到可用率定水平；这是真实定量结果，不是作图错误。

### 图 18　Bonneville 库内水温时序（seg40 vs CCIW）

![图 18　Bonneville 库内水温时序（seg40 vs CCIW）](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_BON_tsr_1_seg40_Temperature_C_timeseries.png)

- **如何读图：** 读法同 TDG 时序图，纵轴为水温（℃）。
- **含义：** 水温由水动力与热收支控制，不依赖 SYSTDG 溢洪产气公式，因此可单独检验热模块。
- **结论：** NSE≈0.95、NRMSE≈0.08 表明 2011 年水温季节循环与 CCIW 高度一致，热模块复现可信。

### 图 19　Bonneville 库内水温 1:1 散点（seg40）

![图 19　Bonneville 库内水温 1:1 散点（seg40）](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_BON_tsr_1_seg40_Temperature_C_scatter.png)

- **如何读图：** 横轴观测、纵轴模拟。点沿 1:1 线紧密分布表示偏差小。
- **含义：** 配对点数约 2400（小时对齐，容差 0.05 日）。
- **结论：** 水温对照支持“模型时间轴与驱动文件正确”；TDG 偏差应主要从气体模块继续查。

### 图 20　Bonneville 坝下尾水 TDG 时序（seg76 下泄 vs CCIW）

![图 20　Bonneville 坝下尾水 TDG 时序（seg76 下泄 vs CCIW）](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_tailwater_TDG_timeseries.png)

- **如何读图：** 蓝点仍为 CCIW 坝下小时 TDG%；折线为坝段 76 下泄混合浓度：由 c_wdo 的 N2、DO 与 t_wdo 的水温，按 W2 withdrawal.f90 公式 TDG%=100×(0.79·N2/n2sat+0.21·DO/dosat) 换算。气压与露点取气象文件最近邻。
- **含义：** 这是与 CCIW 站点空间上更匹配的对照：下泄而不是库内 TSR。公式本身用库内 TSR 的 N2/DO/T 反演 W2 自带 TDG 列，NSE≈0.999，MAE≈0.30%。
- **结论：** 改到真正尾水后，N2+DO 换算的 TDG NSE 仍约 −2.8。下一组图表明：那是对照变量不对，不是断面选错。

### 图 21　Bonneville 坝下尾水 TDG 1:1 散点（seg76）

![图 21　Bonneville 坝下尾水 TDG 1:1 散点（seg76）](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_tailwater_TDG_scatter.png)

- **如何读图：** 横轴 CCIW 观测 TDG%，纵轴坝段 76 下泄 TDG%。
- **含义：** 与库内 seg40 散点形态接近：模拟峰值低于观测高值段。
- **结论：** 空间映射已公平；若继续改进，应调 SYSTDG 溢洪/掺混参数，而不是再换对照断面。

### 图 22　Bonneville 坝下尾水水温时序（seg76 vs CCIW）

![图 22　Bonneville 坝下尾水水温时序（seg76 vs CCIW）](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_tailwater_Temp_timeseries.png)

- **如何读图：** 蓝点 CCIW 水温；折线 t_wdo_76 下泄混合水温。
- **含义：** 尾水水温不依赖 TDG 公式，可独立核验热模块与出流分层取水。
- **结论：** NSE≈0.96，略优于库内 seg40，热模块与出流温度可信。

### 图 23　Bonneville 坝下尾水水温 1:1 散点（seg76）

![图 23　Bonneville 坝下尾水水温 1:1 散点（seg76）](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_tailwater_Temp_scatter.png)

- **如何读图：** 横轴观测、纵轴坝下下泄水温。
- **含义：** 配对约 2400 点，容差 0.05 日。
- **结论：** 水温对照通过。N2+DO 换算的 TDG 与 CCIW 对不上，是因为对照变量不是 SYSTDG 自己写出的 TDG%（见下一组图）。

### 图 24　Bonneville SYSTDG 自身 TDG 时序 vs CCIW

![图 24　Bonneville SYSTDG 自身 TDG 时序 vs CCIW](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_SYSTDG_TDG_vs_CCIW_timeseries.png)

- **如何读图：** 蓝点 CCIW 小时观测；折线为 SYSTDG 模块写出的日尺度 TDG%（TDGTarget_output.csv 的 TDG 列，即源码 TDG_TDG）；红虚线为 TDGTA 动态目标 115/120%。
- **含义：** 这才是 SYSTDG 溢洪产气公式的输出。库内 TSR 的 TDG 列与 c_wdo 的 N2+DO 亨利换算，都不等于该系统变量。官方示例标题写明 TDG target demo，TDGTA=ON 会把溢洪改分到电站以追目标。
- **结论：** 相对 CCIW：NSE=0.50、MAE=2.20%。观测 ≤120% 时 NSE=0.66；观测 >120% 的 251 点上模型被目标封顶在 120.09%，NSE 转负。先前 −2.8 是对照错了变量，不是气体模块不可用。

### 图 25　Bonneville SYSTDG 自身 TDG 1:1 vs CCIW

![图 25　Bonneville SYSTDG 自身 TDG 1:1 vs CCIW](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_SYSTDG_TDG_vs_CCIW_scatter.png)

- **如何读图：** 横轴 CCIW，纵轴 SYSTDG TDG_TDG。点在 120% 处被水平截断，对应 TDGTA 目标上限。
- **含义：** sim_max=120.09，obs_max=129.1。高值段偏差来自目标控制，不是产气公式完全失效。
- **结论：** 在目标封顶以下，MAE≈1.70%。若要复现 129% 峰值，需关 TDGTA 用历史闸门流量再比（隔离目录重跑中）。

### 图 26　Bonneville TDGTA 目标叠置（诊断）

![图 26　Bonneville TDGTA 目标叠置（诊断）](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_bonneville/analysis/Bonneville_TDGTA_target_overlay.png)

- **如何读图：** 同一张图上叠 CCIW、seg76 N2+DO 换算 TDG、以及 115/120% 目标。
- **含义：** N2+DO 换算曲线远离目标与观测，说明它不是 SYSTDG 对照该用的序列。
- **结论：** 诊断结论：先换对 SYSTDG 的 TDG_TDG，再谈参数率定。


## 4c. Columbia Slough 底泥成岩（SED_DIAG ON）

运行目录：`05_REPRO_RUNS/run_20260814_columbia_diag`。DeGray `W2_diagenesis.npt` 改编（结束河段 31→50）。TSR 到 TMEND=55，无 forrtl。



### 图 27　Columbia SED_DIAG ON：底泥耗氧率 SOD 时序

![图 27　Columbia SED_DIAG ON：底泥耗氧率 SOD 时序](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_columbia_diag/analysis/Columbia_diagenesis_SOD_timeseries.png)

- **如何读图：** 横轴为 1995 年积日 JDAY（32–55）；纵轴为底泥耗氧率 SOD（Sediment Oxygen Demand，gO2 m⁻² d⁻¹）。曲线为若干湿河段。
- **含义：** 官方 Columbia 示例控制文件写了 SED_DIAG=ON，但未附 W2_diagenesis.npt。本轮从 DeGray 模板改编（速率/初值区结束河段 31→50），隔离目录重跑。
- **结论：** 已写出 40 个成岩 CSV；末日湿段 SOD 均值约 0.775163829787234 gO2 m⁻² d⁻¹。这是可运行性恢复，不是 Columbia 现场率定。

### 图 28　Columbia SED_DIAG ON：沿程 SOD

![图 28　Columbia SED_DIAG ON：沿程 SOD](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_columbia_diag/analysis/Columbia_diagenesis_SOD_plan.png)

- **如何读图：** 横轴河段号 1–51，纵轴末日 SOD。边界段（1、46–47、51）为 0。
- **含义：** 河段 2–13 使用 DeGray 第一区（较活泼 labile POC），14 以后为第二区参数。
- **结论：** 沿程 SOD 非零说明成岩通量已耦合到水体；数值沿用 DeGray，不能当作 Columbia 真值。

### 图 29　Columbia 成岩开/关：seg45 DO 与 NH4

![图 29　Columbia 成岩开/关：seg45 DO 与 NH4](I:/Projects/20260810-CE-QUAL-W2/05_REPRO_RUNS/run_20260814_columbia_diag/analysis/Columbia_diagenesis_DO_NH4_vs_off.png)

- **如何读图：** 虚线为权威目录 run_20260811_fixed（SED_DIAG OFF），实线为本轮 SED_DIAG ON。上图溶解氧，下图氨氮。
- **含义：** seg45 平均 DO：OFF 6.501637931034483 mg/L，ON 6.287155172413794 mg/L，差 -0.2144827586206897 mg/L。
- **结论：** 开成岩后 DO 略降，方向符合底泥耗氧；幅度取决于未率定的 DeGray 参数，仅证明模块接通。


## 5. 外部经验借鉴

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
