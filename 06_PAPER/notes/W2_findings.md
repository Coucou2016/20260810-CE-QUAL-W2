# W2 发现：数值健康记录（NHR）与 DLTMAX 扫描

日期：2026-08-15  
任务：论文方案 `PAPER_PLAN_20260815.md` 创新点 3 / W2  
不修改方案主文件结论；本笔记给出扫描后的改写建议。

---

## 1. 源码机理（行号相对于 `02_LIBRARY/05_source/github_v4.5/model/w2_model_source/`）

### 1.1 exit 0 掩盖时间步回退

`w2_4_win.f90` Task 2.2.6 Autostepping：

- **L1415–1424**：若 `H1(KT,I) < 0` 且 `DLT > DLTMIN`，写 `w2.wrn`（`Negative surface layer thickness` / `time step reduced to DLTMIN`），`CURMAX = DLTMIN`，`GO TO 220` **重算该步**。
- **L1425–1435**：仅当已经在 DLTMIN 上仍失败，才写 `w2.err`（`Unstable water surface elevation`）并 `GO TO 230`。
- **L1483–1524 / 220 CONTINUE**：把状态滚回 `SZ/SU/...`，必要时再写 `DLT<DLTMIN set DLT=DLTMIN`（L1486），然后 `GO TO 210`。
- **`endsimulation.F90` L26–27, L62–66**：无 `ERROR_OPEN` 则 `Normal termination`；无 `WARNING_OPEN` 则 **删除** `w2.wrn`。因此干净运行可能根本没有 wrn 文件，而带警告的运行仍以 **exit 0 + Normal termination** 结束。

SNP 尾部（`endsimulation.F90` L38–42）另有 `NIT`、`# of violations`（`NV`）、平均时间步。`NV` 在每次时间步回退时累加（L1490），**不能**单独当作负厚度次数：CFL/粘性限制也会增加 `NV`。

### 1.2 层增减是几何阈值，不是截断误差

`layeraddsub.F90`：

| 位置 | 条件 |
|---|---|
| L241 | 加层：`ZMIN < −0.85*H(KT-1) .AND. KT /= 2` |
| L242 | 减层：`ZMIN > 0.60*H(KT) .AND. KT < KTMAX` |
| L243–250 | `KTWB == KMX-1` 且 `SLOPE>0` 且单层时禁止减层；若 `ZMIN > 0.99*H(KT)` 写 **Low water**（L245–246） |
| L767 | 加层循环复检：`−0.80*H(KT-1)`（与 L241 的 0.85 构成滞回） |
| L1277 | 减层循环复检：`0.60*H(KT)` |

### 1.3 DLTINTER 插值（扫描前未写入方案、但决定实验含义）

`update.F90` **L152–163**：`DLTINTER == '      ON'` 时

```
DLTMAXX = DLTMAX(k) + (DLTMAX(k+1)-DLTMAX(k)) / (DLTD(k+1)-DLTD(k)) * (JDAY-DLTD(k))
```

Long Lake 官方 `w2_con.csv`（已读列含义，非盲替换）：

| 列 | DLTD | DLTMAX | DLTF |
|---|---:|---:|---:|
| 0 | 1 | 5 | 0.9 |
| 1 | 1.2 | 800 | 0.9 |
| 2 | **30** | **100**（扫描旋钮） | 0.9 |
| 3 | 40 | **1800** | 0.9 |
| 4 | 175 | 60 | 0.2 |
| 5 | 193 | 100 | 0.2 |

`NDLT=6`，`DLTMIN=0.1 s`，`DLTINTER=ON`，`TMEND=240`。  
官方协议下，**第 30–40 天并不是 DLTMAX=100 的平台**，而是从 100 s **线性插值到 1800 s**。只改第三列（与既有 `run_20260814_longlake_dlt` 相同）改变的是插值**起点**，不是窗内硬顶。

---

## 2. NHR 解析器

- 脚本：`00_INDEX/parse_nhr.py`
- 既有运行：`06_PAPER/analysis/nhr_existing_runs.json`（17 个含 `w2_con.csv` 的目录）
- 扫描：`06_PAPER/analysis/nhr_dlt_scan.json`
- 图：`06_PAPER/figures/nhr_dltmax_neg_thickness.png`、`nhr_dltmax_layers_dltmin.png`、`nhr_dltmax_heatmap.png`

解析字段：负表面层厚度（及当时 DLT、Z、H1、segment、NIT）、Add/Subtract layer 的次数与 JDAY、Low water、`DLT<DLTMIN` 提示、SNP 的 NIT/NV/平均时间步、TSR 的 DLT 轨迹（注意 TSR 是输出步抽样，**抓不到**单步 DLTMIN 回退；回退次数以 wrn 为准）。

---

## 3. 既有运行 NHR（不重跑）

只列**已完成**案例（`completed=true`，或 SNP Normal termination）。未完成的 `run_20260811*` / `diag_*` 多数卡在 HabitatFiles / 成岩文件，NHR 不完整，不参与结论。

| 运行 | 负厚度 | Add | Sub | Low water | DLTMIN 提示 | exit0 掩盖回退 |
|---|---:|---:|---:|---:|---:|---|
| Long Lake 基线 `run_20260811_fixed` | **1** | 3 | 3 | 0 | 2 | **是**（JDAY 31.936, H1=−27.1 m, DLT=74 s → DLTMIN） |
| Long Lake DLTMAX20 `run_20260814_longlake_dlt` | **5** | 3 | 3 | 0 | 10 | **是** |
| Columbia `run_20260811_fixed`（SED_DIAG OFF） | 0 | 7 | 8 | 0 | 0 | 否 |
| Columbia 成岩 `run_20260814_columbia_diag` | 0 | 7 | 8 | 0 | 0 | 否 |
| DeGray `run_20260811_fixed` | 0 | 0 | 0 | 0 | 0 | 否（无 wrn） |
| Bonneville ON `run_20260814_bonneville` | 0 | 42 | 43 | 0 | 0 | 否 |
| Bonneville OFF `run_20260814_bonneville_notarget` | 0 | 48 | 49 | 0 | 0 | 否 |

要点：

- **H1<0 回退目前只在 Long Lake 出现**。Columbia / DeGray / Bonneville 完成运行的负厚度计数均为 0。
- 层增减在河口/坝址案例很频繁（Columbia 15 次、Bonneville 80+ 次），这是水位季节波动触发阈值，**本身不是错误**；NHR 应报告，但不能与负厚度回退混成一个“不健康”分数。
- 基线 vs DLTMAX20 的 1→5 被本次扫描在独立目录中复现（见下）。

---

## 4. Long Lake 扫描矩阵

目录：`05_REPRO_RUNS/run_20260815_ll_dlt_scan/dltmax_{20,50,100,200}[_interoff]/`  
Exe：`w2_v455_ifx.exe`；SCR=OFF；HabitatFiles 已建；8/8 达到 JDAY 239.943，exit 0，约 320–388 s/点，并行 3。  
只改 DLTD=30 对应的 DLTMAX 第三列；DLTF 第三列保持官方 0.9。第二组把 `DLTINTER` 改为 OFF（阶跃 DLTMAX，窗内不再插向 1800 s）。

### 4.1 负厚度计数（创新点 3 的核心表）

| DLTMAX@JDAY30 | DLTINTER=ON（官方插值 → 1800 s） | DLTINTER=OFF（窗内真封顶） |
|---:|---:|---:|
| 20 s | **5** | **0** |
| 50 s | **4** | **0** |
| 100 s（官方） | **1** | **0** |
| 200 s | **5** | **0** |

Add/Sub layer 在 8 个点上**全是 3 / 3**（JDAY 约 14.6 / 25.4 / 30.7 减层，33.9 / 47.8 / 54.7 加层）。低水位警告全 0。

### 4.2 窗内实际 DLT（TSR 抽样，JDAY 30–40）

| 点 | 窗内 DLT min–max (s) | 负厚度事件发生时的 DLT (s) |
|---|---|---|
| ON 20 | 27–231 | 240, 89, 214, 188, 233（**不是 20**） |
| ON 50 | 57–254 | 140, 194, 181, 190 |
| ON 100 | 54–227 | 74 |
| ON 200 | 53–230 | 115, 191, 240, 127, 207 |
| OFF 20 | **20–20** | （无事件） |
| OFF 50 | **50–50** | （无） |
| OFF 100 | **100–100** | （无） |
| OFF 200 | 109–200 | （无） |

`DLTINTER=ON` 时，把“DLTMAX 收到 20 s”**并不**把不稳定窗的时间步收到 20 s；窗内 DLT 仍可到 230 s，因为 day-40 结点仍是 1800 s。此前 1→5 的实验属于这一协议，不是“CFL 更严导致更不稳”的干净检验。

`DLTINTER=OFF` 时窗内 DLT 才等于设定值；四个点负厚度均为 0。同一套几何阈值下，**真正限制时间步可以消掉 H1<0**。因此“减小时间步更不稳”**不能**写成普遍命题。

### 4.3 SNP 的 NV 与负厚度不是一回事

INTER ON、官方 100：NIT=226804，NV=2395（1.06%），负厚度 1。  
INTER OFF、20 s：NIT=216840，NV=16803（约 8%），负厚度 **0**。  
关掉插值后 CFL 回退变多（NV↑），但几何失败（H1<0）消失。NHR 必须把 **H1<0 回退** 与 **一般时间步 violation** 分开报。

### 4.4 非单调性判定

- **官方 DLTINTER=ON、只动 day-30 结点**：计数 5–4–1–5，**非单调**；官方 100 s 是谷底。收紧到 20/50 与放宽到 200 **都会增加**负厚度。方向与“减小时间步更稳”的直觉相反——但机制是**改变了 800→knot 与 knot→1800 两段插值斜率**，从而改变 Z(I) 轨迹，不是“更小的局部 Δt 更差”。
- **DLTINTER=OFF（真·DLTMAX）**：0–0–0–0，无非单调、也无“更紧更差”。
- 既有完成案例里，Columbia / DeGray / Bonneville **没有** H1<0，谈不上对 DLTMAX 非单调。

### 4.5 Columbia 对照（较小扫描）

`05_REPRO_RUNS/run_20260815_columbia_dlt_scan/dltmax_{120,360,720}/`  
官方已是 `NDLT=1, DLTINTER=OFF, DLTMAX=360`。三点均到达 JDAY=55，负厚度 **0 / 0 / 0**，Add/Sub **7 / 8**（与 `run_20260811_fixed` 基线相同）。层增减 JDAY 几乎不变，只是 NIT 随 DLTMAX 缩放。  
结论：在无 H1<0 的案例上，DLTMAX 不是层事件计数的有效旋钮；创新点 3 的非单调性不能写成跨案例定律。

---

## 5. 对创新点 3 的建议（诚实分级）

| 主张 | 扫描后 | 建议 |
|---|---|---|
| exit 0 掩盖 DLTMIN 回退 | **加强**。INTER ON 四点均 Normal termination + exit 0，wrn 中 1–5 次负厚度；H1 可到 −113 m。 | 保留为硬结果；NHR 必报。 |
| 警告数对 DLTMAX 非单调 | **有条件加强**：仅 Long Lake + 官方 `DLTINTER=ON` 结点扫描（5/4/1/5）。 | 可写，但必须写清是**插值结点**不是窗内硬顶。 |
| “减小时间步更不稳”为普遍几何结论 | **降级**。INTER OFF 四点全 0；Columbia/DeGray 基线即 0。 | 改为：H1<0 对 **DLT 历史/插值路径** 敏感；DLTMAX 在 DLTINTER=ON 时不是用户以为的那个旋钮。 |
| NHR 作为报告项 | **加强**。同一套技能指标、exit 0，回退次数可差 0 vs 5。 | 作为创新点 3 的**主交付**，比“非单调定律”更站得住。 |

一句话：创新点 3 **不要整段砍掉**，但要把“非单调定律”降为 Long Lake / DLTINTER=ON 的诊断发现，把 **NHR（负厚度回退次数 + 是否掩盖在 exit 0 里 + DLTINTER 状态）** 升为主张。

---

## 6. 限制

1. 负厚度扫描目前 **n=1 个水域（Long Lake）**。Columbia 有层增减无 H1<0；DeGray 连 wrn 都没有。不能外推到“所有 W2 应用”。
2. DLTF 未做二维扫描（第三列保持 0.9）。INTER OFF 已足够说明“真 DLTMAX”与“插值结点”的差别。
3. TSR 的 DLT 轨迹是输出步抽样，不能代表处于 DLTMIN 的时长占比；该占比需要插桩（方案 T4）或 wrn 事件计数作为下限。
4. INTER OFF 改变的不只是 30–40 天：1.2–30 天也不再从 800 插到 100。零事件是**整条 DLT 日程**的结果，不是单纯“窗内 100 s 封顶”的分离效应。
5. 未改网格、层厚阈值或 `layeraddsub` 源码；几何阈值假说仍是机理叙述，不是本次扫描的独立操纵因子。
6. 并行最多 3 个 exe；Long Lake 单点 5–7 分钟。Columbia 对照 `run_20260815_columbia_dlt_scan/` 三点（DLTMAX=120/360/720，官方已是 DLTINTER=OFF）全部到达 TMEND=55：负厚度 **0/0/0**，Add/Sub **7/8** 三次完全相同。层增减次数对 DLTMAX 不敏感，H1<0 非单调不是跨案例现象。

---

## 7. 复算入口

```text
python 00_INDEX/parse_nhr.py --existing --out 06_PAPER/analysis/nhr_existing_runs.json
python 00_INDEX/run_ll_dlt_scan.py --interoff
python 06_PAPER/analysis/plot_nhr_scan.py
```
