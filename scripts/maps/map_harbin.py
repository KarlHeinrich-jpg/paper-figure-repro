"""
art3/17 — EIA Review 10.1016/j.eiar.2026.108409, Harbin study area.

Real data:
  - Heilongjiang / Harbin district boundaries: DataV (GCJ -> WGS84)
  - basemap: Esri World Imagery (Web Mercator)
  - urban green patches: ESA WorldCover tree-cover clusters (proxy for the
    sampling parks; the original park list is not public)
The photo insets (d) are replaced by a schematic plot layout.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle
from scipy import ndimage
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from geo import datav, mosaic, crop_to_bbox, north_arrow, scalebar, scalebar_deg
from landuse import GEO
from common import setup_style, save, panel_letter

setup_style()

hlj = datav("230000")
hb = datav("230100")
urban = {"道里区", "道外区", "南岗区", "香坊区", "松北区", "平房区"}
core = hb[hb["name"].isin(urban)]
bbox = (126.25, 45.35, 127.25, 46.02)

base, ext = mosaic("img", 10, bbox, workers=8)
base, ext = crop_to_bbox(base, ext, bbox)
base = (base.astype(np.float32) * 0.9 + 255 * 0.10).astype(np.uint8)  # slight wash

# green patches from WorldCover (10 m, decimated)
with rasterio.open(os.path.join(GEO, "worldcover_N45E126.tif")) as src:
    win = from_bounds(*bbox, transform=src.transform)
    w, h = 1600, int(1600 * (bbox[3] - bbox[1]) / (bbox[2] - bbox[0]))
    lu = src.read(1, window=win, out_shape=(h, w), resampling=Resampling.nearest)
green = (lu == 10)
lab, n = ndimage.label(green)
sizes = ndimage.sum(green, lab, range(1, n + 1))
# convert pixel area to km2 (approx)
px_km2 = ((bbox[2] - bbox[0]) * 111.32 * np.cos(np.radians(45.7)) / w) * \
         ((bbox[3] - bbox[1]) * 110.57 / h)
cands = [i + 1 for i, s in enumerate(sizes) if s * px_km2 > 0.10]
from shapely.geometry import Point
core_union = core.geometry.union_all()
pts = []
for i in cands:
    ys, xs = np.where(lab == i)
    cx = bbox[0] + xs.mean() / w * (bbox[2] - bbox[0])
    cy = bbox[3] - ys.mean() / h * (bbox[3] - bbox[1])
    if core_union.contains(Point(cx, cy)):
        pts.append((cx, cy))
pts = pts[:30]

fig = plt.figure(figsize=(11.2, 7.4))
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.62], height_ratios=[1, 1],
                      wspace=0.06, hspace=0.10, left=0.005, right=0.995,
                      top=0.99, bottom=0.02)

# ------------------------------------------------------------------ (a) ---- #
axa = fig.add_subplot(gs[0, 0])
hlj.plot(ax=axa, facecolor="#F4F4F4", edgecolor="#999999", lw=0.45)
hb.plot(ax=axa, facecolor="#8CBF7A", edgecolor="#555555", lw=0.5)
axa.set_xlim(121.0, 135.3); axa.set_ylim(43.3, 53.7)
axa.set_aspect("equal"); axa.axis("off")
axa.text(121.5, 53.0, "Heilongjiang, China", fontsize=10.5, fontweight="bold")
axa.plot([126.6], [45.8], marker="o", ms=6, mfc="#D62728", mec="#333333", mew=0.6)
axa.text(127.0, 45.15, "Harbin", fontsize=8, color="#B2182B")
scalebar_deg(axa, (121.0, 43.3, 135.3, 53.7), km=200, x=0.12, y=0.10)
scalebar(axa, axa.get_xlim()[0:2] + axa.get_xlim()[2:4], km=150, x=0.12, y=0.10) if False else None
north_arrow(axa, x=0.90, y=0.84, size=0.045)

# ------------------------------------------------------------------ (b) ---- #
axb = fig.add_subplot(gs[1, 0])
hb.plot(ax=axb, facecolor="#F4F4F4", edgecolor="#777777", lw=0.6)
core.plot(ax=axb, facecolor="#F2A6A6", edgecolor="#B2182B", lw=0.6)
axb.set_xlim(125.6, 130.4); axb.set_ylim(44.0, 46.8)
axb.set_aspect("equal"); axb.axis("off")
axb.text(125.8, 46.4, "Main urban areas of Harbin", fontsize=9.5, fontweight="bold")
axb.plot([126.62], [45.75], marker="o", ms=5, mfc="#D62728", mec="#333333", mew=0.5)
axb.text(126.75, 45.55, "Main urban\nareas", fontsize=7, color="#B2182B")

# ------------------------------------------------------------------ (c) ---- #
axm = fig.add_subplot(gs[:, 1])
axm.imshow(base, extent=(ext[0], ext[2], ext[1], ext[3]), origin="upper", zorder=0)
core.to_crs(3857).plot(ax=axm, facecolor="none", edgecolor="#FFFFFF", lw=1.4, zorder=4)
core.to_crs(3857).plot(ax=axm, facecolor="none", edgecolor="#444444", lw=0.6, zorder=5)
from pyproj import Transformer
TR = Transformer.from_crs(4326, 3857, always_xy=True)
for lon, lat in pts:
    x, y = TR.transform(lon, lat)
    axm.plot(x, y, marker="s", ms=4.2, mfc="#E31A1C", mec="#FFFFFF", mew=0.5,
             zorder=7)
axm.set_xlim(TR.transform(bbox[0], bbox[1])[0], TR.transform(bbox[2], bbox[3])[0])
axm.set_ylim(TR.transform(bbox[0], bbox[1])[1], TR.transform(bbox[2], bbox[3])[1])
axm.set_aspect("equal"); axm.axis("off")
axm.set_xlabel(""); axm.set_ylabel("")
labels = {"松北区": "Songbei", "道里区": "Daoli", "道外区": "Daowai",
          "香坊区": "Xiangfang", "南岗区": "Nangang", "平房区": "Pingfang"}
for _, row in core.iterrows():
    p = row.geometry.representative_point()
    x, y = TR.transform(p.x, p.y)
    axm.text(x, y, labels.get(row["name"], row["name"]), fontsize=9,
             ha="center", va="center", color="white", zorder=9,
             path_effects=[pe.withStroke(linewidth=2.2, foreground="#333333")])
axm.text(0.015, 0.975, "Harbin City", transform=axm.transAxes, ha="left",
         va="top", fontsize=12, fontweight="bold", color="white",
         path_effects=[pe.withStroke(linewidth=2.0, foreground="#333333")])
north_arrow(axm, x=0.93, y=0.78, size=0.045)
scalebar(axm, (TR.transform(bbox[0], bbox[1])[0], TR.transform(bbox[0], bbox[1])[1],
               TR.transform(bbox[2], bbox[3])[0], TR.transform(bbox[2], bbox[3])[1]),
         km=20, x=0.70, y=0.05, color="white")
# plot-layout inset (replaces the photo insets)
ins = axm.inset_axes([0.02, 0.02, 0.15, 0.18])
ins.set_facecolor("#F7F7F7")
for i in range(3):
    for j in range(3):
        ins.add_patch(Rectangle((i, j), 0.92, 0.92, fill=False, ec="#333333", lw=0.6))
ins.add_patch(Rectangle((0.05, 0.05), 2.85, 2.85, fill=False, ec="#D62728", lw=1.0))
ins.set_xlim(-0.2, 3.2); ins.set_ylim(-0.2, 3.2); ins.set_xticks([]); ins.set_yticks([])
ins.set_title("Sample plot layout", fontsize=6.5, pad=2)

panel_letter(axa, "a", x=-0.02, y=1.02, size=10)
panel_letter(axb, "b", x=-0.02, y=1.02, size=10)
save(fig, "art3_17_harbin_real")
