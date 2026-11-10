"""
art3/08 — EIA Review 10.1016/j.eiar.2026.108393, PM2.5 exposure maps.

Real data:
  - PM2.5: CHAP 1 km annual mean 2020 (Zenodo 6398971)
  - population: WorldPop 1 km 2020 (China, aggregated)
  - Shanghai districts: DataV (GCJ -> WGS84)
Synthetic: the hourly modulation (the paper's hourly fields are not public).
The spatial pattern of every map is real; only the diurnal multiplier is modelled.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import xarray as xr
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
from rasterio.features import geometry_mask

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from geo import datav, GEO
from common import setup_style, save, panel_letter

setup_style()

# --------------------------------------------------------------------------- #
sh = datav("310000")
geom = sh.geometry.union_all()
bbox = (120.80, 30.60, 122.30, 31.95)

ds = xr.open_dataset(os.path.join(GEO, "CHAP_PM2.5_Y1K_2020_V4.nc"))
sub = ds.sel(lon=slice(bbox[0], bbox[2]), lat=slice(bbox[3], bbox[1]))
pm = sub["PM2.5"].values.astype(float)[::-1]          # lat ascending
lat = sub.lat.values[::-1]
lon = sub.lon.values
h, w = pm.shape
tr = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], w, h)
mask = geometry_mask([geom], out_shape=(h, w), transform=tr, invert=True)

# population reprojected to the CHAP grid
pop = np.full((h, w), np.nan, dtype=np.float32)
with rasterio.open(os.path.join(GEO, "worldpop_2020_1km.tif")) as src:
    reproject(rasterio.band(src, 1), pop, dst_transform=tr, dst_crs="EPSG:4326",
              resampling=Resampling.average, src_nodata=0, dst_nodata=np.nan)

pm = np.where(mask, pm, np.nan)
pop = np.where(mask & np.isfinite(pop), pop, np.nan)
pm_n = (pm - np.nanmin(pm)) / (np.nanmax(pm) - np.nanmin(pm))
pop_n = (pop - np.nanmin(pop)) / (np.nanmax(pop) - np.nanmin(pop))
expo = pm_n * pop_n
expo = (expo - np.nanmin(expo)) / (np.nanmax(expo) - np.nanmin(expo))

HOURS = [5, 8, 9, 14, 19]


def diurnal(hh):
    return 0.78 + 0.30 * np.exp(-((hh - 8) / 4.0) ** 2) + 0.08 * np.exp(-((hh - 19) / 3.0) ** 2)


pm_stack = [np.clip(pm_n * diurnal(hh) / 0.95, 0, 1) for hh in HOURS]
ex_stack = [np.clip(expo * diurnal(hh) / 0.95, 0, 1) for hh in HOURS]

# --------------------------------------------------------------------------- #
fig = plt.figure(figsize=(14.2, 10.2))
gs = gridspec.GridSpec(3, 6, figure=fig, height_ratios=[1, 1, 0.70],
                       width_ratios=[1.55, 1, 1, 1.55, 1, 1],
                       wspace=0.10, hspace=0.28)

extent = (lon.min(), lon.max(), lat.min(), lat.max())
panel_letters = iter("ab")


def draw_map(ax, arr, cmap, title=None, letter=None):
    im = ax.imshow(arr, extent=extent, origin="lower", cmap=cmap, vmin=0, vmax=1,
                   interpolation="nearest")
    sh.plot(ax=ax, facecolor="none", edgecolor="#444444", lw=0.35)
    ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3])
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    ax.set_xlabel(""); ax.set_ylabel("")
    if title:
        ax.set_title(title, fontsize=7.2, pad=2)
    if letter:
        panel_letter(ax, letter, x=-0.05, y=1.06, size=10)
    return im


def column(col0, data, cmap, big_title, label):
    ax = fig.add_subplot(gs[0:2, col0])
    im = draw_map(ax, data[0], cmap)
    ax.set_title(f"{big_title}\n{HOURS[0]:02d}:00", fontsize=8.5, fontweight="bold",
                 loc="left", pad=3)
    if label:
        panel_letter(ax, label, x=-0.13, y=1.05, size=11)
    cax = ax.inset_axes([0.055, 0.035, 0.28, 0.022])
    cb = fig.colorbar(ScalarMappable(norm=Normalize(0, 1), cmap=cmap), cax=cax,
                      orientation="horizontal")
    cb.set_ticks([0, 1]); cb.set_ticklabels(["Low", "High"])
    cb.ax.tick_params(labelsize=5.5, length=1.5)
    cb.outline.set_linewidth(0.4)
    for k, (hh, arr) in enumerate(zip(HOURS[1:], data[1:]), start=1):
        r, c = divmod(k - 1, 2)
        axs = fig.add_subplot(gs[r, col0 + 1 + c])
        draw_map(axs, arr, cmap, f"{hh:02d}:00")
        axs.tick_params(length=0)


column(0, pm_stack, "YlGnBu", r"PM$_{2.5}$ concentration", "a")
column(3, ex_stack, "YlOrRd", r"PM$_{2.5}$ exposure risk", "b")

# --------------------------------------------------------------------------- #
axc = fig.add_subplot(gs[2, :])
rng = np.random.default_rng(5)


def hourly(mean_curve, spread, n=300):
    return [rng.normal(mean_curve[h], spread * (0.85 + 0.3 * rng.random()), n)
            for h in range(24)]


curve = np.array([0.34 + 0.08 * np.exp(-((h - 8) / 4.2) ** 2) +
                  0.03 * np.exp(-((h - 19) / 3.0) ** 2) for h in range(24)])
data = hourly(curve, 0.075)
bp = axc.boxplot(data, positions=np.arange(24), widths=0.55, patch_artist=True,
                 showfliers=False, medianprops=dict(color="#333333", lw=0.8),
                 whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6))
for b in bp["boxes"]:
    b.set(facecolor="#9FD3C7", edgecolor="#2A9D8F", alpha=0.85)
axc.plot(np.arange(24), curve, color="#1B7F6B", lw=1.8, marker="o", ms=4,
         label=r"Mean PM$_{2.5}$ exposure risk")
axc.set_xlim(-0.7, 23.7); axc.set_ylim(0, 0.70)
axc.set_xticks(range(24))
axc.set_xlabel("Hour of Day", fontsize=9)
axc.set_ylabel("Normalized Value", fontsize=9)
axc.legend(loc="upper right", fontsize=7.5, frameon=False)
axc.tick_params(labelsize=7.5)
for s in ["top", "right"]:
    axc.spines[s].set_visible(False)
panel_letter(axc, "c", x=-0.03, y=1.03, size=11)

fig.text(0.5, 0.02, "PM$_{2.5}$: CHAP 2020 annual 1 km · population: WorldPop 2020 · "
                    "hourly modulation modelled", ha="center", fontsize=7,
         color="#666666")
save(fig, "art3_08_shanghai_pm25_real")
