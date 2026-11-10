"""
art3/15c — EIA Review 10.1016/j.eiar.2026.108383 (Yang et al., 2026)
"Spatial-temporal assessment and optimization of ecological cropland
utilization: a case study of China's Huang-Huai-Hai region"

Reproduced: five panels (2001, 2005, 2010, 2015, 2020) of grouped horizontal
bars showing the obstacle degree (%) of four indicators for four rotation
systems (RAS/WAMS/CMS/WSRS). Map and radar insets are not reproducible.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, save, panel_letter, light_grid

setup_style()
rng = np.random.default_rng(17)

YEARS = [2001, 2005, 2010, 2015, 2020]
SYS = ["RAS", "WAMS", "CMS", "WSRS"]
IND = ["Partial Factor Productivity\nof Nitrogen (PFPN)", "SOC Change Rate (ΔSOC)",
       "Soil Organic Carbon Density (SOC)", "Total Grain Production (TGP)"]
COLS = ["#2E6DB4", "#E8833A", "#3E9E5A", "#D62728"]

fig = plt.figure(figsize=(14, 8))
gs = fig.add_gridspec(2, 3, hspace=0.42, wspace=0.38)
axes = []
for i, year in enumerate(YEARS):
    ax = fig.add_subplot(gs[i // 3, i % 3])
    axes.append(ax)
    y = np.arange(len(SYS))[::-1]
    for k in range(4):
        vals = rng.uniform(2, 34, len(SYS)) * (1 + 0.02 * (year - 2001))
        vals[int(rng.integers(0, 4))] = rng.uniform(28, 38)
        ax.barh(y + (1.5 - k) * 0.18, vals, height=0.16, color=COLS[k],
                edgecolor="white", lw=0.4, label=IND[k] if i == 0 else None)
    ax.set_yticks(y)
    ax.set_yticklabels(SYS, fontsize=8, fontweight="bold")
    ax.set_xlim(0, 40)
    ax.set_xlabel("Obstacle Degree (%)", fontsize=8.5)
    ax.set_title(f"{year}: Obstacle Degree (%)", fontsize=9, fontweight="bold",
                 loc="left")
    light_grid(ax, "x", "#E6E6E6")
    ax.tick_params(labelsize=7)
    panel_letter(ax, "abcde"[i], x=-0.02, y=1.06, size=10)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

# legend panel
axl = fig.add_subplot(gs[1, 2])
axl.axis("off")
handles = [plt.Rectangle((0, 0), 1, 1, fc=c) for c in COLS]
axl.legend(handles, IND, loc="center left", frameon=False, fontsize=9,
           handlelength=1.4, title="Indicator")
save(fig, "eiar15_obstacle_degree_bars")
