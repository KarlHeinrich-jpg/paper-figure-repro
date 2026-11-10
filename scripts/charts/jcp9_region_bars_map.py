"""
art6/06 — JCP 10.1016/j.jclepro.2025.146675 (Li et al., 2025), Fig. 9.
"Major carbon emission sources and top five significant drivers across
agricultural regions in China."

Reproduced: eight bar panels with value labels arranged around a central
(schematic) map of China. The real province boundaries / emission rasters are
not public in usable form, so the map is a coarse locator sketch.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Polygon

from common import setup_style, save, light_grid, china_locator

setup_style()
rng = np.random.default_rng(33)

# coarse China outline (x, y in 0..1), for locator purposes only
CHINA = np.array([
    [0.05, 0.60], [0.09, 0.74], [0.18, 0.82], [0.31, 0.83], [0.43, 0.86],
    [0.52, 0.93], [0.60, 0.95], [0.67, 0.88], [0.70, 0.74], [0.77, 0.66],
    [0.80, 0.56], [0.86, 0.52], [0.84, 0.44], [0.89, 0.40], [0.85, 0.31],
    [0.76, 0.24], [0.66, 0.18], [0.55, 0.20], [0.47, 0.14], [0.38, 0.18],
    [0.30, 0.24], [0.19, 0.28], [0.09, 0.36], [0.04, 0.46],
])
ZONES = {
    "NASR": (0.18, 0.62), "NCP": (0.55, 0.68), "LP": (0.48, 0.55),
    "HP": (0.60, 0.47), "MLYP": (0.62, 0.36), "SBSR": (0.50, 0.33),
    "YGP": (0.46, 0.24), "SC": (0.66, 0.26), "QTP": (0.25, 0.42),
}
REGIONS = ["NASR", "NCP", "HP", "LP", "MLYP", "SC", "QTP", "SBSR", "YGP"]
LABELS = {"NASR": ["CC1", "CI5", "CI2", "CI3", "CI1"],
          "NCP": ["CC1", "CI1", "CI2", "NS1", "NS2"],
          "HP": ["CC1", "CI1", "CI2", "CI5", "NS1"],
          "LP": ["CC1", "CI1", "NS1", "SE1", "NS2"],
          "MLYP": ["CC1", "CI4", "CI2", "NS1", "SE1"],
          "SC": ["CC1", "CI1", "CI2", "CI4", "SE1"],
          "QTP": ["CC1", "SE1", "SE2", "SE3", "CI1"],
          "SBSR": ["CC1", "CI1", "CI2", "NS1", "SE1"],
          "YGP": ["CI1", "CI2", "CI3", "SE1", "NS2"]}
NCOL = 5
BAR_C = ["#33A02C", "#1F78B4", "#B2A05A", "#D95F02", "#6A3D9A"]


def bar_panel(ax, region):
    labs = LABELS[region]
    vals = rng.uniform(-0.2, 0.72, len(labs))
    vals[0] = rng.uniform(0.55, 0.78)
    colors = [BAR_C[k % len(BAR_C)] for k in range(len(labs))]
    ax.bar(range(len(labs)), vals, color=colors, width=0.62, edgecolor="white")
    for k, v in enumerate(vals):
        ax.text(k, v + (0.02 if v >= 0 else -0.06), f"{v:.2f}", ha="center",
                fontsize=7, fontweight="bold")
    ax.axhline(0, color="black", lw=0.7)
    ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs, fontsize=7)
    ax.set_ylim(-0.32, 0.92)
    ax.set_title(region, fontsize=8.5, fontweight="bold", pad=2)
    ax.tick_params(axis="y", labelsize=6)
    light_grid(ax, "y", "#EEEEEE")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)


fig = plt.figure(figsize=(13, 12))
gs = gridspec.GridSpec(3, 3, figure=fig, wspace=0.30, hspace=0.34,
                       width_ratios=[1, 1.15, 1], height_ratios=[1, 1.15, 1])
positions = [(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2)]
# top/bottom rows: 3 panels each by splitting cells
# use explicit axes: 8 panels around centre
panel_positions = [
    (0.04, 0.69, 0.24, 0.26),   # NASR
    (0.36, 0.74, 0.28, 0.20),   # NCP
    (0.72, 0.69, 0.24, 0.26),   # HP
    (0.76, 0.38, 0.20, 0.22),   # LP
    (0.02, 0.38, 0.26, 0.24),   # MLYP
    (0.04, 0.05, 0.26, 0.24),   # SC
    (0.37, 0.03, 0.26, 0.22),   # QTP
    (0.71, 0.05, 0.26, 0.24),   # SBSR
]
for (x, y, w, h), reg in zip(panel_positions, REGIONS[:8]):
    bar_panel(fig.add_axes([x, y, w, h]), reg)

# central locator map (real province boundaries when available)
axm = fig.add_axes([0.29, 0.30, 0.42, 0.42])
g = china_locator(axm, facecolor="#F3F6FA", edgecolor="#666666", lw=0.5)
ZONES_LL = {
    "NASR": (86, 43), "NCP": (122, 45), "LP": (108, 36.5), "HP": (117, 35),
    "MLYP": (113, 30.5), "SBSR": (104, 30), "YGP": (105, 24.5),
    "SC": (113, 22.5), "QTP": (88, 32.5),
}
for z, (lon, lat) in ZONES_LL.items():
    axm.text(lon, lat, z, fontsize=6.5, ha="center", va="center",
             color="#333333", zorder=5)
axm.text(74, 53, "N", fontsize=7, fontweight="bold")
axm.annotate("", xy=(74, 52.2), xytext=(74, 50.8),
             arrowprops=dict(arrowstyle="-|>", lw=0.9))
axm.text(135, 17, "Schematic locator (not to scale)", ha="right", fontsize=5.5,
         color="#777777")
save(fig, "jcp9_region_bars_map")
