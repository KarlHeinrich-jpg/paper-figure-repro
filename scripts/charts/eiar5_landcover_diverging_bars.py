"""
art5/06 — EIA Review 10.1016/j.eiar.2024.107721 (Mu et al., 2025)
Figure: nine horizontal diverging bar panels of land-cover "change ratio (%)"
binned into six classes (blue = decline, red = increase, grey = small change),
with bin ranges printed at the left of each bar.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, save, panel_letter

setup_style()
rng = np.random.default_rng(26)

TYPES = ["Cropland", "Forest", "Shrub", "Grassland", "Water", "Snow/Ice",
         "Barren", "Impervious", "Wetland"]
BINS = ["(10.9 - 88.7)", "(2.95 - 10.9)", "(-5.04 - 2.95)", "(-13 - -5.04)",
        "(-77.9 - -13)"]
C_NEG = "#2C7FB8"
C_MID = "#BFBFBF"
C_POS = "#E8416B"


def panel(ax, values, bins, title, xlim):
    y = np.arange(len(bins))
    for i, (v, b) in enumerate(zip(values, bins)):
        c = C_NEG if v < -0.5 else (C_POS if v > 0.5 else C_MID)
        yy = len(bins) - 1 - i
        ax.barh(yy, v, color=c, height=0.72, edgecolor="none")
        ax.text(-0.015, yy, b, transform=ax.get_yaxis_transform(),
                fontsize=6.5, ha="right", va="center")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks([])
    ax.set_ylim(-0.6, len(bins) - 0.4)
    ax.set_xlim(*xlim)
    ax.set_title(title, fontsize=9.5, fontweight="bold", loc="left", pad=4)
    ax.set_xlabel("Mean Value", fontsize=8)
    ax.set_ylabel("Change Ratio (%)", fontsize=8, labelpad=44)
    ax.tick_params(labelsize=7)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)


fig, axes = plt.subplots(3, 3, figsize=(13, 11))
axes = axes.ravel()
for i, t in enumerate(TYPES):
    vals = rng.normal(0, 3.2, len(BINS))
    vals = np.clip(vals, -14, 14)
    xlim = (-16, 6)
    if t == "Forest":
        xlim = (-30, 20)
    if t in ["Shrub", "Snow/Ice"]:
        xlim = (-2.5, 2.5)
    if t == "Impervious":
        xlim = (-1.6, 1.6)
    if t == "Wetland":
        xlim = (-1.2, 1.2)
    if t == "Water":
        xlim = (-1.0, 1.0)
    if t == "Barren":
        xlim = (-4.5, 4.5)
    panel(axes[i], vals, BINS, f"({chr(97+i)}) {t}", xlim)

fig.subplots_adjust(hspace=0.55, wspace=0.30, bottom=0.06)
save(fig, "eiar5_landcover_diverging_bars")
