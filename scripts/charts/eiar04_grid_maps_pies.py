"""
art3/04 — EIA Review 10.1016/j.eiar.2026.108402 (Li et al., 2026)
Figure: three grid-cell LISA cluster maps (pre-/during-/post-flood) + three
pie charts of driver composition.

The original maps use a 500 m grid over Zhengzhou with real PPFR values. Exact
maps cannot be rebuilt (no grid data / boundary file), so this script recreates
the *cartographic grammar*: irregular study-area mask, categorical grid cells,
district labels, scale bar and north arrow.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle

from common import setup_style, save, panel_letter, add_north_arrow, add_scalebar, blob

setup_style()
rng = np.random.default_rng(5)

CLASSES = ["High-High", "Low-Low", "High-Low", "Low-High", "Not significant"]
COLS = ["#D73027", "#4575B4", "#FEE090", "#1A9850", "#DDDDDD"]
PIE_LABELS = ["Precipitation", "Elevation", "River density", "NDVI",
              "Road density", "Building density", "Impervious surface ratio",
              "Shannon index", "Night light index", "Population density",
              "Proportion of youth", "Proportion of females", "GEO"]
WATER = "#C9E6F2"


def make_grid(ax, seed, title):
    rng = np.random.default_rng(seed)
    # near-rectangular study area with a clipped NE corner (Zhengzhou-like)
    verts = np.array([[0.10, 0.06], [0.88, 0.06], [0.88, 0.72], [0.72, 0.94],
                      [0.10, 0.94], [0.10, 0.06]])
    nx, ny = 17, 15
    xs = np.linspace(0.05, 0.95, nx)
    ys = np.linspace(0.04, 0.96, ny)
    from matplotlib.path import Path
    path = Path(verts)
    field = rng.normal(size=(ny, nx))
    for _ in range(4):
        field = (field + np.roll(field, 1, 0) + np.roll(field, 1, 1) +
                 np.roll(field, -1, 0) + np.roll(field, -1, 1)) / 5
    th = np.quantile(field, [0.32, 0.58, 0.72, 0.86])
    cls = np.digitize(field, th)
    cls = np.where(cls == 3, 0, cls)
    cls = np.where(cls == 2, 2, cls)
    cls = np.where(cls == 1, 1, cls)
    cls = np.where((cls == 0) & (rng.random(field.shape) < 0.18), 3, cls)
    cell = 0.90 / nx
    for iy, y in enumerate(ys):
        for ix, x in enumerate(xs):
            if not path.contains_point((x, y)):
                continue
            ax.add_patch(Rectangle((x - cell / 2, y - cell * 0.435), cell, cell * 0.87,
                                   facecolor=COLS[cls[iy, ix]], edgecolor="none",
                                   zorder=2))
    # internal district boundaries
    for pts in [
        np.array([[0.10, 0.60], [0.35, 0.58], [0.52, 0.63], [0.88, 0.60]]),
        np.array([[0.10, 0.36], [0.33, 0.38], [0.57, 0.34], [0.88, 0.37]]),
        np.array([[0.42, 0.06], [0.44, 0.36], [0.42, 0.60], [0.44, 0.94]]),
        np.array([[0.68, 0.06], [0.70, 0.37], [0.68, 0.60], [0.70, 0.94]]),
    ]:
        ax.plot(pts[:, 0], pts[:, 1], color="#333333", lw=0.8, zorder=6)
    for dx, dy, name in [(0.33, 0.78, "Huiji"), (0.79, 0.78, "Jinshui"),
                         (0.33, 0.49, "Zhongyuan"), (0.32, 0.20, "Erqi"),
                         (0.79, 0.20, "Guancheng")]:
        ax.text(dx, dy, name, fontsize=8, fontstyle="italic", zorder=7,
                ha="center", color="#111111",
                path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    ax.plot(verts[:, 0], verts[:, 1], color="black", lw=1.2, zorder=8)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=11, fontweight="bold", pad=6)
    add_north_arrow(ax, x=0.06, y=0.89, size=0.04)
    add_scalebar(ax, x0=0.68, y0=0.03, length=0.22, label="0   10   20 km")


fig = plt.figure(figsize=(15.5, 10.5))
gs = fig.add_gridspec(2, 3, height_ratios=[1.55, 1.0], hspace=0.12, wspace=0.06)
stages = ["Pre-flood stage", "During-flood stage", "Post-flood stage"]
for i in range(3):
    ax = fig.add_subplot(gs[0, i])
    make_grid(ax, 30 + i, stages[i])
    panel_letter(ax, "abc"[i], x=-0.06, y=1.02, size=11)

# pies with leader lines
shares = [
    [21.88, 3.65, 3.65, 1.01, 7.43, 41.93, 2.30, 0.13, 4.46, 4.46, 0.33, 14.45],
    [24.51, 3.64, 1.01, 3.65, 14.18, 40.24, 1.15, 0.14, 3.38, 5.71, 0.41, 9.59],
    [8.17, 1.08, 6.41, 0.68, 43.08, 33.42, 2.16, 0.54, 2.77, 3.85, 1.15, 0.00],
]
pie_cols = ["#4575B4", "#74ADD1", "#ABD9E9", "#F5F5F5", "#D73027", "#F46D43",
            "#FDAE61", "#FFFFBF", "#A6D96A", "#1A9850", "#66BD63", "#B8E186"]
for i in range(3):
    ax = fig.add_subplot(gs[1, i])
    vals = [v for v in shares[i]]
    wedges, _ = ax.pie(vals, colors=pie_cols[:len(vals)], startangle=90,
                       counterclock=False, radius=1.0,
                       wedgeprops=dict(edgecolor="white", lw=0.8))
    # annotate the largest 5 sectors
    idx = np.argsort(vals)[::-1][:5]
    for r, k in enumerate(idx):
        w = wedges[k]
        ang = np.deg2rad((w.theta1 + w.theta2) / 2)
        x, y = np.cos(ang) * 1.02, np.sin(ang) * 1.02
        xt, yt = np.cos(ang) * 1.55, np.sin(ang) * 1.55 + (0.12 if r % 2 else -0.10)
        ax.annotate(f"{PIE_LABELS[k]}\n{vals[k]:.2f}%", xy=(x, y), xytext=(xt, yt),
                    fontsize=6.6, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6, color="#555555",
                                    shrinkA=0, shrinkB=2),
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none",
                              alpha=0.85))
    ax.set_xlim(-1.9, 1.9); ax.set_ylim(-1.9, 1.9)
    ax.axis("off")
    panel_letter(ax, "def"[i], x=0.03, y=0.95, size=11)

handles = [plt.Rectangle((0, 0), 1, 1, fc=c, ec="white", label=l)
           for c, l in zip(COLS, CLASSES)]
fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=8.5,
           bbox_to_anchor=(0.5, 0.005))
save(fig, "eiar04_grid_maps_pies")
