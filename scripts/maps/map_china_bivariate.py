"""
art3/12 — EIA Review 10.1016/j.eiar.2026.108344.
Bivariate elevation × slope map of China, rebuilt from the real DEM with a
3×3 colour matrix (matching the original legend) and four zoom insets.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import ListedColormap
from rasterio.warp import reproject, Resampling, calculate_default_transform
from rasterio.transform import from_bounds
from rasterio.features import geometry_mask
from pyproj import Transformer
import shapely

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from geo import mosaic, gadm, north_arrow, scalebar
from common import setup_style, save

setup_style()
ALBERS = "+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +datum=WGS84 +units=m +no_defs"
bbox = (73.0, 17.0, 136.0, 54.0)
prov = gadm(1)
china_geom = prov.geometry.union_all()

elev, ext = mosaic("dem", 7, bbox, workers=12)
h, w = elev.shape
dst_tr, dw, dh = calculate_default_transform("EPSG:3857", ALBERS, w, h, *ext,
                                             resolution=2000)
dem = np.full((dh, dw), np.nan, dtype=np.float32)
reproject(elev, dem, src_transform=from_bounds(*ext, w, h), src_crs="EPSG:3857",
          dst_transform=dst_tr, dst_crs=ALBERS, resampling=Resampling.bilinear,
          src_nodata=np.nan, dst_nodata=np.nan)
geom_alb = shapely.transform(china_geom, lambda xy: np.column_stack(
    Transformer.from_crs(4326, ALBERS, always_xy=True).transform(xy[:, 0], xy[:, 1])))
mask = geometry_mask([geom_alb], out_shape=dem.shape, transform=dst_tr, invert=True)
dem = np.where(mask, dem, np.nan)

# slope in degrees
filled = np.where(np.isnan(dem), np.nanmedian(dem), dem)
gy, gx = np.gradient(filled, 2000.0, 2000.0)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))

elev_cls = np.digitize(dem, [500, 2000])          # 0 low, 1 mid, 2 high
slope_cls = np.digitize(slope, [2, 10])           # 0 low, 1 mid, 2 high
biv = elev_cls * 3 + slope_cls
biv = np.where(np.isnan(dem), np.nan, biv)

PAL = [
    ["#F0FFF0", "#9CCFE8", "#4A90D9"],   # low elevation
    ["#F5F5B0", "#BDBDB0", "#5F9E9E"],   # mid
    ["#E8E83A", "#4F7A3A", "#2E5E2E"],   # high
]
colors = [PAL[i][j] for i in range(3) for j in range(3)]
cmap = ListedColormap(colors)
cmap.set_bad((1, 1, 1, 0))

# hillshade
hs = np.zeros_like(dem)
slope_r = np.radians(np.clip(slope, 0, 90))
aspect = np.arctan2(-gx, gy)
az, alt = np.radians(315), np.radians(45)
hs = np.sin(alt) * np.sin(slope_r) + np.cos(alt) * np.cos(slope_r) * np.cos(az - aspect)
hs = np.clip(hs, 0, 1)

L = dst_tr.c; T = dst_tr.f; R = L + dst_tr.a * dw; B = T + dst_tr.e * dh
extent = (L, R, B, T)
fig = plt.figure(figsize=(11.2, 7.4))
ax = fig.add_axes([0.02, 0.12, 0.96, 0.84])
ax.imshow(biv, extent=extent, origin="upper", cmap=cmap, vmin=-0.5, vmax=8.5,
          interpolation="nearest", zorder=1)
# hillshade overlay on land only
shade = np.where(np.isnan(biv), 1.0, 0.72 + 0.38 * hs)
ax.imshow(shade, extent=extent, origin="upper", cmap="gray", vmin=0, vmax=1,
          alpha=0.10, zorder=2)
prov.to_crs(ALBERS).plot(ax=ax, facecolor="none", edgecolor="#FFFFFF", lw=0.45,
                         alpha=0.9, zorder=3)
prov.to_crs(ALBERS).plot(ax=ax, facecolor="none", edgecolor="#555555", lw=0.22,
                         alpha=0.55, zorder=4)
pb = prov.to_crs(ALBERS).total_bounds
ax.set_xlim(pb[0] - 60000, pb[2] + 60000)
ax.set_ylim(pb[1] - 60000, pb[3] + 60000)
ax.axis("off")

# graticule
tr = Transformer.from_crs(4326, ALBERS, always_xy=True)
for lon in range(70, 141, 10):
    lats = np.linspace(15, 55, 160)
    X, Y = tr.transform(np.full_like(lats, lon), lats)
    ax.plot(X, Y, color="#555555", lw=0.4, ls="--", alpha=0.5, zorder=5)
for lat in range(20, 51, 10):
    lons = np.linspace(70, 140, 220)
    X, Y = tr.transform(lons, np.full_like(lons, lat))
    ax.plot(X, Y, color="#555555", lw=0.4, ls="--", alpha=0.5, zorder=5)

# bivariate legend
leg = fig.add_axes([0.035, 0.135, 0.10, 0.15])
for i in range(3):
    for j in range(3):
        leg.add_patch(Rectangle((j, i), 0.96, 0.96,
                                facecolor=PAL[i][j], edgecolor="#555555", lw=0.4))
leg.set_xlim(-0.2, 3.2); leg.set_ylim(-0.2, 3.2)
leg.set_xticks([]); leg.set_yticks([])
leg.text(-0.35, 1.5, "Elevation", rotation=90, ha="right", va="center", fontsize=7)
leg.text(1.5, 3.45, "Slope  Low → High", ha="center", va="bottom", fontsize=7)
leg.text(-0.45, 2.6, "High", ha="right", va="center", fontsize=6.5)
leg.text(-0.45, 0.4, "Low", ha="right", va="center", fontsize=6.5)
for s in leg.spines.values():
    s.set_visible(False)
leg.add_patch(Rectangle((0, -0.55), 2.96, 0.28, facecolor="white",
                        edgecolor="#555555", hatch="///", lw=0.3))
leg.text(1.5, -0.41, "Not Available", ha="center", va="center", fontsize=5.5)

north_arrow(ax, x=0.955, y=0.86, size=0.04)
scalebar(ax, extent, km=600, x=0.82, y=0.05, color="#222222")

# zoom insets
zooms = [(102.5, 28.5, "b"), (111.5, 36.0, "c"), (124.0, 46.5, "d"),
         (117.5, 29.5, "e")]
for lon, lat, letter in zooms:
    x, y = tr.transform(lon, lat)
    ww = 260000
    ins = fig.add_axes([0.20 + 0.19 * "bcde".index(letter), 0.135, 0.13, 0.13])
    ins.imshow(biv, extent=extent, origin="upper", cmap=cmap, vmin=-0.5, vmax=8.5,
               interpolation="nearest")
    ins.imshow(shade, extent=extent, origin="upper", cmap="gray", vmin=0, vmax=1,
               alpha=0.15)
    ins.set_xlim(x - ww, x + ww); ins.set_ylim(y - ww, y + ww)
    ins.set_xticks([]); ins.set_yticks([])
    for s in ins.spines.values():
        s.set_linewidth(0.7)
    ins.text(0.02, 0.96, letter, transform=ins.transAxes, va="top", fontsize=9,
             fontweight="bold")
    ax.add_patch(Rectangle((x - ww, y - ww), 2 * ww, 2 * ww, fill=False,
                           ec="#111111", lw=0.7, zorder=8))

# South China Sea inset
axs = fig.add_axes([0.90, 0.135, 0.085, 0.11])
prov.to_crs(4326).plot(ax=axs, facecolor="#EDEDED", edgecolor="#888888", lw=0.3)
axs.set_xlim(105, 125); axs.set_ylim(2, 24); axs.set_aspect("equal")
axs.set_xticks([]); axs.set_yticks([]); axs.set_xlabel(""); axs.set_ylabel("")
axs.add_patch(Rectangle((105, 2), 20, 22, fill=False, ec="#333333", lw=0.7))

save(fig, "art3_12_china_bivariate_real")
