---
name: paper-figure-repro
description: 复刻期刊论文插图的可复用 Python skill。先做逐图可复现性审计（A/B/C），统计图用 matplotlib/seaborn 重建版式，地图用真实边界/DEM/影像/土地利用（DataV、GADM、Esri、AWS DEM、ESA WorldCover、CHAP PM2.5、WorldPop、WorldClim、SoilGrids）重画，并输出原图对照与复现报告。触发词：复刻论文图、论文插图复现、期刊图片复现、figure reproduction、reproduce paper figures、SHAP 蜂巢图、玫瑰图、研究区地图复刻、真实地理数据画图、论文配图重画。
---

# paper-figure-repro — 论文插图复现

把公众号/期刊里看到的图，拆成**可复现性判定 + 可运行代码 + 真实数据底图**三部分，
交付一组 PNG/PDF、一份逐图清单和一份诚实的复现报告。

## 何时用

- 看到一篇论文/推文的图，想在自己的论文、汇报或教程里重画。
- 需要判断“这张图到底能不能复现、缺什么数据”。
- 需要研究区地图、DEM、土地利用、PM2.5、人口等**真实地理底图**，而不是手绘示意。
- 需要 SHAP 蜂巢/玫瑰/donut、GeoShapley 条形+饼图、分裂小提琴、Moran 散点、
  雨云图、极坐标年图、双轴时序、双变量地图等成品配方。

## 不适用

- 只想要“长得像”的装饰图，不关心数据来源 → 直接用绘图库即可。
- 需要逐像素复刻手绘插画/照片/软件 UI → 这是设计工作，不是数据图。
- 没有原始数据却要求“数值一模一样” → 只能做版式复刻，必须明确标注模拟值。

## 快速开始

```bash
git clone <this-repo> && cd paper-figure-repro
python -m pip install -r requirements.txt

python scripts/download_data.py          # 下载边界/DEM/PM2.5/人口/气候/土壤/土地覆盖
python scripts/run_all.py --charts       # 20 张统计图（含 SHAP）
python scripts/run_all.py --maps         # 6 张真实地理数据地图
```

单张运行：

```bash
python scripts/charts/art1_shap_beeswarm_rose.py
python scripts/maps/map_zhengzhou.py
```

输出默认写到 `outputs/`（PNG 300 dpi + PDF）。可用环境变量改路径：

```bash
PFR_GEODATA=/data/geo PFR_OUT=/tmp/figs python scripts/maps/map_china_dem.py
```

## 复现工作流

### 1. 建清单

把每张原图编号（文章/图片序号），记录：图型、面板数、坐标轴、图例、色带、
是否有地图/照片/插画。产出 `docs/figure_inventory.csv` 同款表。

### 2. 判定 A / B / C

| 级别 | 判据 | 交付 |
|------|------|------|
| **A** | 只依赖数值矩阵；图型有成熟库 | 可运行脚本 + 模拟/真实数据 |
| **B** | 需要未公开的 shp/栅格/问卷原始记录 | 真实底图模板 + 明确的缺失说明 |
| **C** | 手绘插画、照片、软件 UI | 不画，写清原因 |

判定要具体到“缺哪一层数据”，不要笼统说“数据不可得”。

### 3. 取真实数据（地图类）

`scripts/geo.py` 已封装：

| 数据 | 函数 / 文件 | 说明 |
|------|-------------|------|
| 中国省/市/区县 | `geo.datav("410100")` | 阿里云 DataV，自动 GCJ-02→WGS84 |
| 全球行政区 | `geo.gadm(level=1/3)` | GADM 4.1，WGS84 |
| 地形 | `geo.mosaic("dem", z, bbox)` | AWS terrarium 瓦片，返回高程+extent |
| 影像/浅灰底图 | `geo.mosaic("img"/"gray", ...)` | Esri World Imagery / Light Gray，Web Mercator |
| 土地利用 | `landuse.read_landuse("zhengzhou", bbox, geom)` | ESA WorldCover 10 m，6 类重分类 |
| PM2.5 | `geodata/CHAP_PM2.5_Y1K_2020_V4.nc` | CHAP 1 km 年值，xarray 读取 |
| 人口 | `geodata/worldpop_2020_1km.tif` | WorldPop 1 km |
| 气候 | `geodata/worldclim_prec.zip` | WorldClim 2.1 10 m |
| 土壤 pH | `geodata/soilgrids_ph_1km.tif` | SoilGrids 1 km |

下载脚本会跳过已存在文件；DEM 瓦片按需下载并缓存。

### 4. 重建图形

- 统计图：从 `scripts/charts/` 选最接近的配方，替换顶部数据生成块为
  `pd.read_excel/pd.read_csv`，保留 `FEATURES / positions / colors` 等常量。
- SHAP 类：`build_data()` 换成真实 `X, y`；模型与 `shap.TreeExplainer` 不用改。
- 地图：从 `scripts/maps/` 选模板，替换 `datav(...)` 的 adcode、`bbox`、`zoom`；
  主题栅格换成自己的 `.tif`，`imshow` 的 extent 顺序是 **(left, right, bottom, top)**。
- 字型：`common.setup_style()` 统一 Times New Roman + SimSun，PDF 可编辑。

### 5. 验收与报告

- `python scripts/run_all.py` 必须全绿。
- 每张图输出 PNG（300 dpi）+ PDF；地图同时保留 `compare_real.png` 式对照。
- 报告写清：哪些是真实数据、哪些是模拟值、哪些字段缺失、复现到哪一层。
- **绝不**把模拟值写成“复现了论文结论”。

## 图表配方（scripts/charts）

| 脚本 | 图型 |
|------|------|
| `art1_shap_beeswarm_rose.py` | 多分类 SHAP 蜂巢 + 玫瑰 + 五层同心环 |
| `eiar03_importance_bars_pies.py` | 三效应堆叠条 + 影线饼图 |
| `eiar04_grid_maps_pies.py` | 格网 LISA + 饼图 |
| `eiar05_priority_grid.py` | 优先级格网示意 |
| `eiar08_hourly_boxplots.py` | 逐小时箱线 + 均值线 |
| `eiar10_shap_beeswarm_dependence.py` | SHAP 蜂巢 + 依赖图（LOWESS+CI+R²） |
| `eiar13_violin_stackedbar.py` | 分裂小提琴 + 堆叠条 |
| `eiar14_3d_pies.py` | 2.5D 饼柱 |
| `eiar15_obstacle_degree_bars.py` | 障碍度分组条 |
| `eiar16_sctz_framework.py` | 同心环框架 |
| `eiar18_bivariate_moran.py` | 双变量 Moran + 置换检验 |
| `eiar19_raincloud_letters.py` | 雨云图 + 显著性字母 |
| `eiar20_bubble_matrix_dependence.py` | 气泡矩阵 + 18 依赖图 |
| `eiar5_connectivity_timeseries.py` | 9 流域双轴时序 |
| `eiar5_landcover_diverging_bars.py` | 发散条形 |
| `frameworks_montage.py` | 四类概念框架 |
| `jcp8_driver_smallmultiples.py` | 10 面板小倍数 |
| `jcp9_region_bars_map.py` | 区域条形 + 定位图 |
| `jcp10_zone_polar_drivers.py` | 9 极坐标年图 |

## 地图配方（scripts/maps）

| 脚本 | 真实数据 |
|------|----------|
| `map_zhengzhou.py` | DataV 12 区 + Esri 浅灰 + 1 km 格网 |
| `map_shanghai.py` | DataV 16 区 + WorldCover 土地覆盖 |
| `map_harbin.py` | DataV 18 区 + Esri 影像 + 树冠斑块 |
| `map_china_dem.py` | AWS DEM + GADM 省界 + Albers |
| `map_china_bivariate.py` | DEM 派生坡度 + 3×3 双变量 |
| `map_shanghai_pm25.py` | CHAP PM2.5 + WorldPop 人口 |

## 强制规则

1. **先判定，再画图**。不判定就开画，等于把“示意图”冒充“复现”。
2. **真实数据与模拟数据分开标注**。图注、README、报告三处都要写。
3. **不搬运原图**。仓库只放自己的渲染结果；原论文图/公众号图有版权。
4. **不伪造主题值**。没有 PPFR 格网就写“缺失”，不要用随机场冒充。
5. **地图必须对齐**：DataV 是 GCJ-02，先转 WGS84；Esri 瓦片是 Web Mercator，
   `imshow` extent 用米制 `(L,R,B,T)`；DEM 用 terrarium 解码。
6. **产出可编辑**：PDF `fonttype=42`，文字能在 Illustrator/Inkscape 里改。

## 常见坑

- `ax.imshow(..., extent=(L,B,R,T))` 是错的，正确顺序是 `(L,R,B,T)`。
- WorldPop 的 nodata=0，先转 NaN，再做归一化。
- CHAP 的 lat 是降序，切片后记得 `[::-1]`。
- 中国地图用 Albers：`+proj=aea +lat_1=25 +lat_2=47 +lon_0=105`。
- 长标签在窄面板里会跨面板，先算 `wspace` 或把图例移出。
- 全局代理若失效，下载函数已显式禁用代理；GDAL `/vsicurl/` 仍会读环境变量。

## 目录

```
paper-figure-repro/
├─ SKILL.md
├─ README.md
├─ requirements.txt
├─ scripts/
│  ├─ common.py          # 字体/配色/模拟数据/面板字母
│  ├─ geo.py             # 瓦片/边界/经纬网/比例尺
│  ├─ landuse.py         # WorldCover → 6 类
│  ├─ download_data.py
│  ├─ run_all.py
│  ├─ charts/            # 20 个统计图脚本
│  └─ maps/              # 6 个真实地图脚本
├─ docs/
│  ├─ figure_inventory.csv
│  └─ DATA_SOURCES.md
├─ examples/             # 12 张成品缩略图
└─ geodata/              # 下载缓存（gitignore）
```

## 验收清单

- [ ] `run_all.py` 全绿，PNG+PDF 都存在且非空
- [ ] 每张图有“真实/模拟”标注
- [ ] 地图边界与底图对齐（看海岸线/河流）
- [ ] 面板字母、比例尺、指北针、经纬网齐全
- [ ] 报告列出缺失数据与不可复现项
- [ ] 没有提交 `geodata/`、`outputs/`、原论文截图
