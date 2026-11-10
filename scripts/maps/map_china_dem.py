"""
art3/11 — EIA Review 10.1016/j.eiar.2026.108344.
China elevation map rebuilt with REAL SRTM/Mapzen DEM (AWS terrarium tiles,
~1.2 km mosaic) reprojected to an Albers equal-area grid, clipped by the
national boundary, with hillshade, provincial borders and curved graticules.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
import geopandas as gpd
import rasterio
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

print("downloading/mosaicking DEM …")
elev, ext = mosaic("dem", 7, bbox, workers=12)
h, w = elev.shape
src_tr = from_bounds(*ext, w, h)
dst_tr, dw, dh = calculate_default_transform("EPSG:3857", ALBERS, w, h, *ext,
                                             resolution=2000)
dem = np.full((dh, dw), np.nan, dtype=np.float32)
reproject(elev, dem, src_transform=src_tr, src_crs="EPSG:3857",
          dst_transform=dst_tr, dst_crs=ALBERS, resampling=Resampling.bilinear,
          src_nodata=np.nan, dst_nodata=np.nan)
geom_alb = shapely.transform(china_geom, lambda xy: np.column_stack(
    Transformer.from_crs(4326, ALBERS, always_xy=True).transform(xy[:, 0], xy[:, 1])))
mask = geometry_mask([geom_alb], out_shape=dem.shape, transform=dst_tr, invert=True)
dem = np.where(mask, dem, np.nan)
print("grid", dem.shape, "elev range", np.nanmin(dem), np.nanmax(dem))

# hillshade
valid = ~np.isnan(dem)
filled = np.where(valid, dem, np.nanmedian(dem))
gy, gx = np.gradient(filled, 2000.0, 2000.0)
slope = np.pi / 2 - np.arctan(np.hypot(gx, gy))
aspect = np.arctan2(-gx, gy)
az, alt = np.radians(315), np.radians(45)
hs = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)
hs = np.clip(hs, 0, 1)

colors = ["#1B7837", "#4C9B4A", "#8CC07A", "#D9EBC8", "#F7F7EF",
          "#DADAEB", "#B39DDB", "#8C6BB1", "#5E3C99", "#3F007D"]
cmap = LinearSegmentedColormap.from_list("dem", colors)
norm = Normalize(vmin=0, vmax=8627)
rgb = cmap(norm(dem))[..., :3]
rgb = np.clip(rgb * (0.55 + 0.55 * hs[..., None]), 0, 1)
rgb[~valid] = 1

L, B, R, T = dst_tr.c, dst_tr.f + dst_tr.e * dh, dst_tr.c + dst_tr.a * dw, dst_tr.f
extent = (L, B, R, T)
fig = plt.figure(figsize=(11.2, 7.2))
ax = fig.add_axes([0.02, 0.10, 0.96, 0.86])
ax.imshow(rgb, extent=(L, R, B, T), origin="upper", zorder=1)
prov.to_crs(ALBERS).plot(ax=ax, facecolor="none", edgecolor="#FFFFFF", lw=0.45,
                         alpha=0.85, zorder=3)
prov.to_crs(ALBERS).plot(ax=ax, facecolor="none", edgecolor="#6B6B6B", lw=0.25,
                         alpha=0.6, zorder=4)
pb = prov.to_crs(ALBERS).total_bounds
ax.set_xlim(pb[0] - 60000, pb[2] + 60000)
ax.set_ylim(pb[1] - 60000, pb[3] + 60000)
ax.axis("off")
ax.set_xlabel(""); ax.set_ylabel("")

# graticule
tr = Transformer.from_crs(4326, ALBERS, always_xy=True)
for lon in range(70, 141, 10):
    lats = np.linspace(15, 55, 160)
    X, Y = tr.transform(np.full_like(lats, lon), lats)
    ax.plot(X, Y, color="#555555", lw=0.45, ls="--", alpha=0.55, zorder=5)
    i = np.argmax(Y)
    ax.text(X[i], Y[i] - 25000, f"{lon}°E", fontsize=6.5, rotation=-18,
            ha="center", va="top", color="#333333", zorder=7)
for lat in range(20, 51, 10):
    lons = np.linspace(70, 140, 220)
    X, Y = tr.transform(lons, np.full_like(lons, lat))
    ax.plot(X, Y, color="#555555", lw=0.45, ls="--", alpha=0.55, zorder=5)
    i = 0
    ax.text(X[i] - 30000, Y[i], f"{lat}°N", fontsize=6.5, rotation=0,
            ha="right", va="center", color="#333333", zorder=7)

labels = [
    ("Tianshan Mountains", 84.0, 42.6, 0),
    ("Kunlun Mountains", 81.5, 36.3, 0),
    ("Qinghai-Tibet\nPlateau", 88.5, 31.4, 0),
    ("Tarim Basin", 83.5, 39.3, 0),
    ("Qilian Mountains", 99.0, 38.4, 0),
    ("Loess Plateau", 108.5, 36.6, 0),
    ("Inner Mongolia Plateau", 111.0, 43.6, 0),
    ("Greater Khingan Range", 122.5, 48.6, 62),
    ("Changbai Mountains", 128.0, 42.6, 45),
    ("Qinling-Daba\nMountains", 108.0, 33.3, 0),
    ("Yunnan-Guizhou\nPlateau", 104.5, 25.6, 0),
    ("Sichuan Basin", 105.5, 30.4, 0),
    ("North China Plain", 116.3, 36.6, 0),
    ("Altai Mountains", 89.0, 47.6, 28),
]
for txt, lon, lat, rot in labels:
    x, y = tr.transform(lon, lat)
    ax.text(x, y, txt, fontsize=7.2, ha="center", va="center", rotation=rot,
            color="#2E4F2C", zorder=9,
            path_effects=[pe.withStroke(linewidth=1.6, foreground="white")])

north_arrow(ax, x=0.955, y=0.84, size=0.04)
scalebar(ax, extent, km=600, x=0.74, y=0.055, color="#222222")

# colorbar
cax = fig.add_axes([0.07, 0.055, 0.34, 0.018])
cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=cax,
                  orientation="horizontal")
cb.set_ticks([100, 500, 1000, 2000, 3000, 4000, 5000, 6000, 8627])
cb.ax.tick_params(labelsize=6.5, length=2)
cb.outline.set_linewidth(0.5)
fig.text(0.055, 0.085, "Elevation / m", fontsize=7)

# South China Sea inset
axs = fig.add_axes([0.83, 0.10, 0.13, 0.16])
prov.to_crs(4326).plot(ax=axs, facecolor="#EDEDED", edgecolor="#888888", lw=0.3)
axs.set_xlim(105, 125); axs.set_ylim(2, 24); axs.set_aspect("equal")
axs.set_xticks([]); axs.set_yticks([]); axs.set_xlabel(""); axs.set_ylabel("")
axs.add_patch(plt.Rectangle((105, 2), 20, 22, fill=False, ec="#333333", lw=0.7))
axs.text(115, 4.2, "South China Sea Islands", fontsize=5, ha="center")

save(fig, "art3_11_china_dem_real")
