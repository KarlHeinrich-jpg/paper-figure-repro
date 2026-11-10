"""
art3/06 — EIA Review 10.1016/j.eiar.2026.108393, Shanghai study area.

Real data:
  - China / Jiangsu / Zhejiang / Shanghai districts: DataV (GCJ -> WGS84)
  - land use: ESA WorldCover 2021 10 m (reclassified to the 6 classes used in
    the original legend)
Synthetic: ring-road geometry (OSM not reachable) and the schematic delta
highlight in panel (b).
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Patch, Rectangle
import geopandas as gpd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from geo import datav, north_arrow, scalebar_deg
from landuse import read_landuse, cmap, COLORS, NAMES
from common import setup_style, save, panel_letter

setup_style()

china = datav("100000")
jiangsu = datav("320000")
zhejiang = datav("330000")
sh = datav("310000")

bbox = (120.80, 30.62, 122.30, 31.90)
geom = sh.geometry.union_all()
arr, ext = read_landuse("shanghai", bbox, geom=geom, out_px=2200)
vals = sorted(COLORS)
idx = {v: i for i, v in enumerate(vals)}
arr2 = np.full(arr.shape, np.nan)
for v, i in idx.items():
    arr2[arr == v] = i
cm, _, _ = cmap()

fig = plt.figure(figsize=(11.2, 7.2))
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.62], height_ratios=[1, 1],
                      wspace=0.05, hspace=0.08, left=0.005, right=0.995,
                      top=0.99, bottom=0.02)

# ------------------------------------------------------------------ (a) ---- #
axc = fig.add_subplot(gs[0, 0])
china.plot(ax=axc, facecolor="#F7F7F7", edgecolor="#AAAAAA", lw=0.35, zorder=2)
sh.plot(ax=axc, facecolor="#D62728", edgecolor="#D62728", lw=0.2, zorder=3)
axc.set_xlim(72, 136); axc.set_ylim(17, 55); axc.set_aspect("equal"); axc.axis("off")
axc.text(74.0, 53.6, "China", fontsize=13, fontweight="bold")
axc.plot([121.4], [31.2], marker="*", ms=9, color="#FFD400",
         markeredgecolor="#333333", markeredgewidth=0.6, zorder=6)
axc.add_patch(Rectangle((118.6, 28.4), 5.8, 5.4, fill=False, ec="#D62728", lw=0.9))
north_arrow(axc, x=0.10, y=0.70, size=0.05)
scalebar_deg(axc, (72, 17, 136, 55), km=3000, x=0.10, y=0.08)

# ------------------------------------------------------------------ (b) ---- #
axb = fig.add_subplot(gs[1, 0])
jiangsu.plot(ax=axb, facecolor="#EAF0E4", edgecolor="#777777", lw=0.4)
zhejiang.plot(ax=axb, facecolor="#EAF0E4", edgecolor="#777777", lw=0.4)
sh.plot(ax=axb, facecolor="#D62728", edgecolor="#D62728", lw=0.3, zorder=3)
axb.set_xlim(117.0, 123.0); axb.set_ylim(27.0, 35.2)
axb.set_aspect("equal"); axb.axis("off")
axb.text(117.4, 33.6, "Jiangsu Province", fontsize=9)
axb.text(118.2, 28.3, "Zhejiang Province", fontsize=9)
axb.text(120.2, 29.0, "East China Sea", fontsize=9, fontstyle="italic")
axb.text(120.9, 31.15, "Shanghai", fontsize=8, color="#B2182B", fontweight="bold")
scalebar_deg(axb, (117, 27, 123, 35.2), km=200, x=0.10, y=0.08)
north_arrow(axb, x=0.88, y=0.82, size=0.045)

# ------------------------------------------------------------------ (c) ---- #
axm = fig.add_subplot(gs[:, 1])
axm.imshow(arr2, extent=ext, origin="upper", cmap=cm,
           vmin=-0.5, vmax=len(vals) - 0.5, interpolation="nearest", zorder=1)
sh.plot(ax=axm, facecolor="none", edgecolor="#222222", lw=1.2, zorder=4)
sh.plot(ax=axm, facecolor="none", edgecolor="#555555", lw=0.55, zorder=5)

labels = {"崇明区": "Chongming", "宝山区": "Baoshan", "嘉定区": "Jiading",
          "普陀区": "Putuo", "长宁区": "Changning", "黄浦区": "Huangpu",
          "静安区": "Jing'an", "虹口区": "Hongkou", "杨浦区": "Yangpu",
          "浦东新区": "Pudongxin", "闵行区": "Minhang", "松江区": "Songjiang",
          "青浦区": "Qingpu", "奉贤区": "Fengxian", "金山区": "Jinshan",
          "徐汇区": "Xuhui"}
offsets = {"普陀区": (-0.055, 0.050), "长宁区": (-0.080, 0.005),
           "黄浦区": (0.040, -0.035), "静安区": (0.010, 0.080),
           "虹口区": (0.075, 0.050), "杨浦区": (0.110, 0.005),
           "徐汇区": (-0.030, -0.060)}
for _, row in sh.iterrows():
    p = row.geometry.representative_point()
    dx, dy = offsets.get(row["name"], (0, 0))
    axm.text(p.x + dx, p.y + dy, labels.get(row["name"], row["name"]),
             fontsize=8.2, ha="center", va="center", zorder=8,
             path_effects=[pe.withStroke(linewidth=2.4, foreground="white")])
axm.set_xlim(bbox[0], bbox[2]); axm.set_ylim(bbox[1], bbox[3])
axm.set_aspect("equal"); axm.axis("off")
axm.text(0.015, 0.975, "Shanghai", transform=axm.transAxes, ha="left", va="top",
         fontsize=13, fontweight="bold")
north_arrow(axm, x=0.93, y=0.78, size=0.045)
scalebar_deg(axm, bbox, km=14, x=0.66, y=0.06)

# legend (inside bottom-left)
handles = [Patch(facecolor=COLORS[k], edgecolor="#666666", lw=0.4,
                 label=NAMES.get(k, str(k)))
           for k in (40, 30, 50, 10, 80, 60)]
leg = axm.legend(handles=handles, loc="lower left", fontsize=7.2, frameon=True,
                 framealpha=0.95, edgecolor="#999999", title="Legend",
                 title_fontsize=8, ncol=1, borderpad=0.5, handlelength=1.2)
leg.get_frame().set_linewidth(0.6)

# tick labels
for lon in np.arange(121.0, 122.31, 0.2):
    axm.text(lon, bbox[3] + 0.015, f"{lon:.1f}°E", ha="center", va="bottom",
             fontsize=5.8)
for lat in np.arange(30.8, 31.91, 0.2):
    axm.text(bbox[2] + 0.012, lat, f"{lat:.1f}°N", ha="left", va="center",
             fontsize=5.8, rotation=90)

panel_letter(axc, "a", x=-0.02, y=1.02, size=10)
panel_letter(axb, "b", x=-0.02, y=1.02, size=10)
save(fig, "art3_06_shanghai_real")
