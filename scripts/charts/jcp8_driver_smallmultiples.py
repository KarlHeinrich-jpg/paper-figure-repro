"""
art6/05 — J. Cleaner Production 10.1016/j.jclepro.2025.146675 (Li et al., 2025)
"Decoding the spatiotemporal dynamics of cropland carbon emission drivers in
China: a machine learning-based analysis", Fig. 8.

Reproduced: ten-panel small multiples of the national driver trends (2001-2020)
with per-factor marker/colour codes and a legend per panel.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, save, panel_letter

setup_style()
rng = np.random.default_rng(31)
YEARS = np.arange(2001, 2021)
FACTORS = ["CC1", "CI1", "CI2", "CI3", "NS1", "NS2", "NS3", "SE1", "SE2", "SE3"]
COLS = ["#8C6D31", "#3F6E8C", "#4E9F6B", "#7A5195", "#B0555E",
        "#D08A3E", "#5B8F86", "#8E7CC3", "#C07A3E", "#5F9EA0"]
MARKERS = ["o", "s", "^", "v", "D", "P", "X", "*", "h", "<"]


def series(base, amp, seed):
    r = np.random.default_rng(seed)
    v = base + amp * np.sin(np.linspace(0, 2.5, len(YEARS)) + r.uniform(0, 3))
    v += np.cumsum(r.normal(0, amp * 0.08, len(YEARS)))
    return v


fig, axes = plt.subplots(5, 2, figsize=(13, 15), sharex=False)
axes = axes.ravel()
groups = [(0, 1, 2, 3), (4, 5, 6), (7, 8, 9), (0, 3), (1, 4)]
for i, ax in enumerate(axes):
    g = groups[i % len(groups)]
    for k, j in enumerate(g):
        ax.plot(YEARS, series(0.05 * (k + 1), 0.08 + 0.03 * k, seed=100 * i + j),
                color=COLS[j], marker=MARKERS[j], ms=3.4, lw=1.0,
                mfc="white" if j % 2 == 0 else COLS[j], label=FACTORS[j])
    ax.axhline(0, color="grey", lw=0.6, ls=":")
    ax.set_xlim(2000.5, 2020.5)
    ax.set_xticks(range(2001, 2021, 2))
    ax.tick_params(axis="x", rotation=90, labelsize=6.5)
    ax.tick_params(axis="y", labelsize=6.5)
    ax.set_ylabel("Coefficient", fontsize=7.5)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=6.5,
              frameon=False, handlelength=1.4, labelspacing=0.25)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    panel_letter(ax, "abcdefghij"[i], x=-0.09, y=1.05, size=9)

fig.text(0.5, 0.005,
         "Fig. 8. Trends in various drivers of cropland carbon emissions in China "
         "from 2001 to 2020 (National scale).", ha="center", fontsize=8)
fig.subplots_adjust(hspace=0.30, wspace=0.62, bottom=0.055, top=0.98)
save(fig, "jcp8_national_driver_smallmultiples")
