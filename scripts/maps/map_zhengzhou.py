"""
art3/00 — EIA Review 10.1016/j.eiar.2026.108402, study area figure.

Rebuilt with REAL data:
  - China / Henan / Zhengzhou boundaries: DataV (GCJ-02 -> WGS84)
  - basemap: Esri World Light Gray Base (Web Mercator)
  - districts: DataV 410100 (12 districts, real geometry)
The 500 m sampling grid and PPFR grid values are not public; a neutral 1 km
reference grid is drawn instead.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon as MplPoly
from matplotlib.path import Path as MplPath
import geopandas as gpd
from pyproj import Transformer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from geo import (datav, to3857, mosaic, crop_to_bbox, north_arrow,
                 scalebar, scalebar_deg)
from common import setup_style, save, panel_letter

setup_style()
TR = Transformer.from_crs(4326, 3857, always_xy=True)

# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #
china = datav("100000")                     # provinces, real geometry
henan = datav("410000")                     # prefecture cities
zz = datav("410100")                        # 12 districts
zz3857 = to3857(zz)
union = zz3857.geometry.union_all()
bbox = (112.66, 34.20, 114.30, 35.04)

base, ext = mosaic("gray", 10, bbox, workers=8)
base, ext = crop_to_bbox(base, ext, bbox)
# the light-gray base is very faint: increase line contrast
g = base.astype(np.float32).mean(2)
d = np.clip((238.0 - g) / 40.0, 0, 1)
base = np.repeat((255 - d * 230)[..., None], 3, axis=2).astype(np.uint8)

fig = plt.figure(figsize=(11.2, 7.05))
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.75], height_ratios=[1, 1],
                      wspace=0.06, hspace=0.10, left=0.005, right=0.995,
                      top=0.99, bottom=0.02)

# --------------------------------------------------------------------------- #
# (left-top) China
# --------------------------------------------------------------------------- #
axc = fig.add_subplot(gs[0, 0])
china.plot(ax=axc, facecolor="#F7F7F7", edgecolor="#AAAAAA", lw=0.35, zorder=2)
henan.plot(ax=axc, facecolor="#D62728", edgecolor="#D62728", lw=0.2, zorder=3)
axc.set_xlim(72, 136); axc.set_ylim(17, 55)
axc.set_aspect("equal"); axc.axis("off"); axc.set_xlabel(""); axc.set_ylabel("")
axc.text(73.5, 52.5, "China", fontsize=13, fontweight="bold")
north_arrow(axc, x=0.10, y=0.80, size=0.05)
scalebar_deg(axc, (72, 17, 136, 55), km=3000, x=0.10, y=0.08)
# south china sea inset
axs = axc.inset_axes([0.70, 0.02, 0.28, 0.30])
china.plot(ax=axs, facecolor="#F2F2F2", edgecolor="#888888", lw=0.3)
axs.set_xlim(105, 125); axs.set_ylim(2, 24)
axs.set_aspect("equal"); axs.set_xticks([]); axs.set_yticks([]); axs.set_xlabel(""); axs.set_ylabel("")
axs.add_patch(plt.Rectangle((105, 2), 20, 22, fill=False, ec="#555555", lw=0.6))

# --------------------------------------------------------------------------- #
# (left-bottom) Henan
# --------------------------------------------------------------------------- #
axh = fig.add_subplot(gs[1, 0])
henan.plot(ax=axh, facecolor="#F7F7F7", edgecolor="#999999", lw=0.4)
zz.plot(ax=axh, facecolor="#2F6DB5", edgecolor="#2F6DB5", lw=0.2)
axh.set_xlim(110.2, 116.8); axh.set_ylim(31.2, 36.5)
axh.set_aspect("equal"); axh.axis("off"); axh.set_xlabel(""); axh.set_ylabel("")
axh.text(110.5, 36.1, "Henan Province", fontsize=12, fontweight="bold")
scalebar_deg(axh, (110.2, 31.2, 116.8, 36.5), km=300, x=0.10, y=0.10)

# --------------------------------------------------------------------------- #
# (right) Zhengzhou
# --------------------------------------------------------------------------- #
axm = fig.add_subplot(gs[:, 1])
axm.imshow(base, extent=(ext[0], ext[2], ext[1], ext[3]), origin="upper", zorder=0)
# 1 km reference grid clipped to the city
x0, y0 = TR.transform(bbox[0], bbox[1])
x1, y1 = TR.transform(bbox[2], bbox[3])
step = 1000.0
xs = np.arange(np.floor(x0 / step) * step, x1 + step, step)
ys = np.arange(np.floor(y0 / step) * step, y1 + step, step)
clip = MplPoly(np.array(union.exterior.coords), closed=True, transform=axm.transData)
for x in xs:
    ln, = axm.plot([x, x], [y0, y1], color="#555555", lw=0.22, alpha=0.22, zorder=3)
    ln.set_clip_path(clip)
for y in ys:
    ln, = axm.plot([x0, x1], [y, y], color="#555555", lw=0.22, alpha=0.22, zorder=3)
    ln.set_clip_path(clip)
zz3857.plot(ax=axm, facecolor="none", edgecolor="#111111", lw=1.4, zorder=5)
# district labels
labels = {"惠济区": "Huiji", "金水区": "Jinshui", "中原区": "Zhongyuan",
          "二七区": "Erqi", "管城回族区": "Guancheng", "上街区": "Shangjie",
          "中牟县": "Zhongmou", "巩义市": "Gongyi", "荥阳市": "Xingyang",
          "新密市": "Xinmi", "新郑市": "Xinzheng", "登封市": "Dengfeng"}
for _, row in zz3857.iterrows():
    p = row.geometry.representative_point()
    name = labels.get(row["name"], row["name"])
    axm.text(p.x, p.y, name, fontsize=9.5, fontstyle="italic", ha="center",
             va="center", zorder=8,
             path_effects=[pe.withStroke(linewidth=2.6, foreground="white")])
axm.set_xlim(x0, x1); axm.set_ylim(y0, y1)
axm.set_aspect("equal"); axm.axis("off"); axm.set_xlabel(""); axm.set_ylabel("")
axm.text(0.985, 0.945, "Zhengzhou City", transform=axm.transAxes, ha="right",
         va="top", fontsize=12, fontweight="bold")
north_arrow(axm, x=0.04, y=0.84, size=0.045)
scalebar(axm, (x0, y0, x1, y1), km=18, x=0.70, y=0.06)
axm.text(0.02, 0.02, "Study unit", transform=axm.transAxes, ha="left",
         fontsize=7)

# degree ticks (top/right)
for lon in np.arange(112.8, 114.31, 0.1):
    xt, _ = TR.transform(lon, bbox[1])
    axm.text(xt, y1 + (y1 - y0) * 0.004, f"{lon:.1f}°E", ha="center",
             va="bottom", fontsize=5.4, clip_on=False)
for lat in np.arange(34.3, 35.01, 0.1):
    _, yt = TR.transform(bbox[0], lat)
    axm.text(x1 + (x1 - x0) * 0.004, yt, f"{lat:.1f}°N", ha="left",
             va="center", fontsize=6.2, rotation=90, clip_on=False)

panel_letter(axc, "a", x=-0.02, y=1.02, size=10)
panel_letter(axh, "b", x=-0.02, y=1.02, size=10)

save(fig, "art3_00_zhengzhou_real")
