# 数据源与许可

本仓库不提交任何原始数据文件；`scripts/download_data.py` 从下列公开源按需下载，
缓存到 `geodata/`（已 gitignore）。使用前请自行核对各源的许可条款。

| 数据 | 用途 | 源 / 下载 | 许可（以源站为准） |
|------|------|-----------|-------------------|
| 中国省/市/区县边界 | 研究区定位、区县图 | 阿里云 DataV.GeoAtlas：`https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json`；入口 `https://datav.aliyun.com/portal/school/atlas/area_selector` | 免费在线底图服务；请遵守 DataV 使用条款。坐标为 GCJ-02，脚本已转 WGS84 |
| 全球行政区 | 全国/跨省地图 | GADM 4.1：`https://geodata.ucdavis.edu/gadm/gadm4.1/json/` | 学术/非商业免费；引用 GADM。`https://gadm.org/license.html` |
| 卫星影像 | 哈尔滨等研究区底图 | Esri World Imagery：`https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer` | Esri 主协议；仅在线调用，**不要缓存再分发瓦片** |
| 浅灰底图 | 郑州/上海底图 | Esri World Light Gray Base | 同上 |
| 地形 DEM | 中国 DEM、坡度、双变量 | AWS Open Data Terrain Tiles（Mapzen terrarium）：`https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png` | Open Data；源含 SRTM/NED 等，引用 AWS Terrain Tiles / Mapzen |
| 土地覆盖 | 上海/郑州/哈尔滨土地利用 | ESA WorldCover 2021 v200 10 m：`https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/` | **CC BY 4.0**；引用 Zanaga et al. (2022) |
| 1 km PM2.5 | 上海 PM2.5/暴露 | ChinaHighPM2.5（CHAP），Zenodo 6398971：`https://zenodo.org/records/6398971` | **CC BY 4.0**（Zenodo 元数据） |
| 1 km 人口 | 上海暴露、人口图 | WorldPop 2020 China 1 km：`https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/2020/CHN/` | WorldPop 通常为 CC BY 4.0；以源站为准 |
| 气候 | 降水面板 | WorldClim 2.1 10 m：`https://geodata.ucdavis.edu/climate/worldclim/2_1/base/` | 免费；引用 Fick & Hijmans (2017) |
| 土壤 pH | 全国 pH 面板 | SoilGrids 1 km（ISRIC）：`https://files.isric.org/soilgrids/latest/data_aggregated/1000m/phh2o/` | **CC BY 4.0**；引用 Poggio et al. (2021) |

## 版权边界

- 仓库**不包含**原论文插图、公众号图片、论文补充数据。
- `examples/` 仅包含本仓库代码的渲染结果；其中地图底图来自 Esri/WorldCover 等，
  再分发时请同时遵守对应许可。
- `docs/figure_inventory.csv` 只记录论文 DOI、图型与复现判定，不复制图件。

## 引用建议

如果用到具体数据层，请按各源要求引用；仓库层面的引用见 `README.md`。
