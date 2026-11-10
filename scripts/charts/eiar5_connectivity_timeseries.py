"""
art5/05 — EIA Review 10.1016/j.eiar.2024.107721 (Mu et al., 2025)
"Moving in the landscape: Omnidirectional connectivity dynamics in China from
1985 to 2020"

Reproduced: nine basin panels with dual y-axes: basin connectivity (black
squares), core connectivity (orange triangles) and core area (teal, right axis),
including dashed yearly averages, shaded trend bands and slope annotations.
Maps (art5/02-04) need the connectivity rasters and are not reproduced.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from common import setup_style, save, panel_letter

setup_style()
rng = np.random.default_rng(24)

YEARS = np.arange(1985, 2021)
PANELS = [
    ("Continental Basin (CB)", 5.68, 15.2, 1.15),
    ("Southwest Basin (SWB)", 56.0, 37.8, 0.69),
    ("Southeast Basin (SEB)", 56.5, 53.5, 0.17),
    ("Pearl River Basin (PRB)", 76.8, 43.2, 0.29),
    ("Yangtze River Basin (YZRB)", 56.2, 31.6, 0.94),
    ("Yellow River Basin (YRB)", 23.5, 13.6, 0.46),
    ("Huaihe River Basin (HuaiRB)", 55.9, 4.05, 0.017),
    ("Haihe River Basin (HaiRB)", 52.5, 15.6, 0.10),
    ("Songhua and Liaohe River Basin (SLRB)", 61.3, 31.3, 0.58),
]
C_BASIN = "#3B3B3B"
C_CORE = "#E07B39"
C_AREA = "#4FA894"


def walk(start, scale, trend, seed):
    rng = np.random.default_rng(seed)
    v = start + trend * np.arange(len(YEARS)) + np.cumsum(rng.normal(0, scale, len(YEARS)))
    return v


fig, axes = plt.subplots(3, 3, figsize=(14, 12))
axes = axes.ravel()
for i, (name, b0, c0, a0) in enumerate(PANELS):
    ax = axes[i]
    rng_i = np.random.default_rng(100 + i)
    basin = walk(b0, 0.035 * b0, rng_i.uniform(-0.004, 0.006) * b0, 200 + i)
    core = walk(c0, 0.05 * c0, rng_i.uniform(-0.01, 0.02) * c0, 300 + i)
    area = walk(a0, 0.03 * a0, rng_i.uniform(-0.004, 0.006) * a0, 400 + i)
    ax2 = ax.twinx()
    ax.plot(YEARS, basin, color=C_BASIN, lw=1.3, marker="s", ms=3.2, mfc="white",
            label="Basin connectivity", zorder=3)
    ax.plot(YEARS, core, color=C_CORE, lw=1.3, marker="^", ms=3.4, mfc="white",
            label="Core connectivity", zorder=3)
    ax2.plot(YEARS, area, color=C_AREA, lw=1.3, marker="v", ms=3.4, mfc="white",
             label=r"Core area (km$^2$)", zorder=3)
    # shaded trend bands
    for series, a in [(basin, ax), (core, ax), (area, ax2)]:
        a.fill_between(YEARS, series * 0.985, series * 1.015, color="grey", alpha=0.10,
                       lw=0)
    ax.axhline(basin.mean(), color=C_BASIN, ls="--", lw=0.8, alpha=0.8)
    ax.axhline(core.mean(), color=C_CORE, ls="--", lw=0.8, alpha=0.8)
    ax2.axhline(area.mean(), color=C_AREA, ls="--", lw=0.8, alpha=0.8)
    ax.axvline(1985, color=C_CORE, lw=1.2, alpha=0.7)
    # slope annotations (decorative, mimic the original labelling)
    sl_b = (basin[-1] - basin[0]) / 35 / basin.mean()
    sl_c = (core[-1] - core[0]) / 35 / core.mean()
    ax.text(0.03, 0.90, f"{sl_b:+.3f}", transform=ax.transAxes, color=C_BASIN,
            fontsize=8, fontweight="bold")
    ax.text(0.55, 0.55, f"{sl_c:+.3f}", transform=ax.transAxes, color=C_CORE,
            fontsize=8, fontweight="bold")
    ax.set_title(name, fontsize=9.5, fontweight="bold", loc="left", pad=4)
    ax.set_xlim(1983, 2022)
    ax.set_xticks([1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020])
    ax.tick_params(axis="x", rotation=55, labelsize=7)
    ax.tick_params(axis="y", labelsize=7)
    ax2.tick_params(axis="y", labelsize=7, colors=C_AREA)
    ax.set_ylabel("Connectivity", fontsize=8)
    ax2.set_ylabel(r"Core area ($\times 10^6$ km$^2$)", fontsize=8,
                   color=C_AREA)
    if i % 2 == 0:
        ax.yaxis.set_major_locator(plt.MaxNLocator(3))
    for s in ["top"]:
        ax.spines[s].set_visible(False)
        ax2.spines[s].set_visible(False)
    panel_letter(ax, "abcdefghi"[i], x=-0.02, y=1.05, size=10)

handles = [Line2D([0], [0], color=C_BASIN, marker="s", mfc="white", lw=1.3,
                  label="Basin connectivity"),
           Line2D([0], [0], color=C_CORE, marker="^", mfc="white", lw=1.3,
                  label="Core connectivity"),
           Line2D([0], [0], color=C_AREA, marker="v", mfc="white", lw=1.3,
                  label=r"Core area (km$^2$)"),
           Line2D([0], [0], color="grey", ls="--", lw=0.9, label="Yearly average")]
fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
           fontsize=9, bbox_to_anchor=(0.5, 0.005))
fig.subplots_adjust(bottom=0.10, hspace=0.55, wspace=0.40)
save(fig, "eiar5_connectivity_timeseries")
