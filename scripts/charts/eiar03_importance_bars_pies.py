"""
art3/03 — EIA Review 10.1016/j.eiar.2026.108402 (Li et al., 2026)
"Assessing stage-dependent impacts of environmental factors on public-perceived
flood risk: Insights from a GeoXAI framework", Fig. (importance + factor pies).

Reproduced: (a-c) stacked horizontal importance bars with three GeoShapley
effect components for pre-/during-/post-flood stages; (d-f) hatched pie charts
of the three factor families.

Data are simulated; group shares are chosen to echo the reported pattern
(natural ~30-35%, build ~29-42%, socioeconomic ~23-37%).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from common import setup_style, save, panel_letter, light_grid

setup_style()
rng = np.random.default_rng(11)

FEATURES = [
    "Building density", "Precipitation", "GEO", "Population density",
    "Road density", "Impervious surface ratio", "Elevation", "River density",
    "Night light index", "NDVI", "Shannon index", "Proportion of females",
    "Proportion of youth",
]
C_NON = "#4C86C6"
C_INT = "#E8416B"
C_FIX = "#EFA17C"

# rank orders per stage (top -> bottom in the published panels)
orders = [
    ["Building density", "Precipitation", "GEO", "Population density", "Road density",
     "Impervious surface ratio", "Elevation", "River density", "Night light index",
     "NDVI", "Shannon index", "Proportion of females", "Proportion of youth"],
    ["Precipitation", "Night light index", "Road density", "Population density",
     "Building density", "GEO", "River density", "Elevation", "Proportion of youth",
     "Impervious surface ratio", "NDVI", "Shannon index", "Proportion of females"],
    ["Population density", "Road density", "Precipitation", "Building density",
     "Night light index", "GEO", "Elevation", "Proportion of females",
     "Impervious surface ratio", "NDVI", "Shannon index", "Proportion of youth",
     "River density"],
]
scales = [(0.027, 0.0010), (0.26, 0.010), (0.15, 0.006)]


def stacked_data(stage):
    n = len(FEATURES)
    scale, jitter = scales[stage]
    total = np.linspace(scale, scale * 0.34, n) + rng.uniform(-jitter, jitter, n)
    non = total * rng.uniform(0.38, 0.62, n)
    inter = total * rng.uniform(0.20, 0.35, n)
    fixed = np.clip(total - non - inter, 0, None)
    return non, inter, fixed


fig = plt.figure(figsize=(15, 8.6))
gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.0], hspace=0.30, wspace=0.55)
letters = list("abcdef")

for stage in range(3):
    ax = fig.add_subplot(gs[0, stage])
    non, inter, fixed = stacked_data(stage)
    y = np.arange(len(FEATURES))[::-1]
    ax.barh(y, non, color=C_NON, edgecolor="white", height=0.72, label="Non-spatial effect")
    ax.barh(y, inter, left=non, color=C_INT, edgecolor="white", height=0.72,
            label="Spatial interaction effect")
    ax.barh(y, fixed, left=non + inter, color=C_FIX, edgecolor="white", height=0.72,
            label="Spatial fixed effect")
    ax.set_yticks(y)
    ax.set_yticklabels(orders[stage], fontsize=7.5)
    ax.set_xlabel("mean(|GeoShapley|)", fontsize=9)
    ax.set_xlim(0, scales[stage][0] * 1.05)
    ax.xaxis.set_major_formatter(plt.FormatStrFormatter("%.3f"))
    light_grid(ax, "x")
    panel_letter(ax, letters[stage], x=-0.02, y=1.04, size=12)
    if stage == 0:
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3,
                  fontsize=7, frameon=False, handlelength=1.2, columnspacing=1.1)

# ---- hatched pies --------------------------------------------------------- #
pie_data = [(34.93, 41.94, 23.12), (33.70, 28.90, 37.40), (29.03, 33.61, 37.36)]
pie_colors = ["#D9D9D9", "#BDBDBD", "#8C8C8C"]
hatches = ["|||", "...", "///"]
pie_labels = ["Natural environment factors", "Build environment factors",
              "Socioeconomic factors"]
for stage in range(3):
    ax = fig.add_subplot(gs[1, stage])
    vals = pie_data[stage]
    wedges, _ = ax.pie(vals, colors=["white"]*3, startangle=90, counterclock=True,
                       wedgeprops=dict(edgecolor="black", lw=0.9))
    for w, h, c in zip(wedges, hatches, pie_colors):
        w.set_hatch(h)
        w.set_facecolor(c)
        w.set_alpha(0.55)
    # leader lines + boxed labels
    for i, (w, v) in enumerate(zip(wedges, vals)):
        ang = np.deg2rad((w.theta2 + w.theta1) / 2)
        x, y = np.cos(ang) * 0.95, np.sin(ang) * 0.95
        xt, yt = np.cos(ang) * 1.55, np.sin(ang) * 1.55
        ha = "left" if x >= 0 else "right"
        ax.annotate(f"{pie_labels[i]}\n{v:.2f}%", xy=(x, y), xytext=(xt, yt),
                    ha=ha, va="center", fontsize=7.5,
                    arrowprops=dict(arrowstyle="-", lw=0.7, color="black"),
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-1.7, 1.7)
    ax.set_aspect("equal")
    ax.axis("off")
    panel_letter(ax, letters[stage + 3], x=0.02, y=0.98, size=12)

save(fig, "eiar03_importance_bars_hatched_pies")
