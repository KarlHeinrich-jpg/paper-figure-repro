"""
art3/13 — EIA Review 10.1016/j.eiar.2026.108344 (Kong et al., 2026)
"Understanding the village-scale expansion of rural settlements in China from a
topographic perspective"

Reproduced: (d) split violins of rural-settlement area by bivariate LISA class
for 1980 vs 2020; (e) horizontal stacked bars of class composition by year.
Maps (a-c) are not reproducible without the settlement vector data.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch

from common import setup_style, save, panel_letter, light_grid

setup_style()
rng = np.random.default_rng(13)

CLASSES = ["ALL", "H-H", "H-M", "H-L", "M-H", "M-M", "M-L", "L-H", "L-M", "L-L"]
N = 900
rows = []
for c in CLASSES:
    for year, shift in [(1980, 0.0), (2020, 6.0)]:
        base = {"ALL": 30, "H-H": 42, "H-M": 24, "H-L": 14, "M-H": 20,
                "M-M": 12, "M-L": 9, "L-H": 7, "L-M": 5, "L-L": 4}[c]
        vals = np.clip(rng.lognormal(mean=np.log(base + shift), sigma=0.36, size=N), 1, 180)
        rows.append(pd.DataFrame({"class": c, "year": year, "area": vals}))
df = pd.concat(rows, ignore_index=True)

fig = plt.figure(figsize=(15, 10))
gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 1.0], hspace=0.34)

ax = fig.add_subplot(gs[0])
sns.violinplot(data=df, x="class", y="area", hue="year", split=True, cut=0,
               inner="box", density_norm="width", linewidth=0.7,
               palette={1980: "#E1393F", 2020: "#3BA99C"}, ax=ax,
               hue_order=[1980, 2020])
ax.set_ylim(0, 165)
ax.set_xlabel("")
ax.set_ylabel("Area (ha)", fontsize=11)
ax.tick_params(axis="x", labelsize=9)
for label in ax.get_xticklabels():
    label.set_fontweight("bold")
leg = ax.legend(title="", loc="upper right", frameon=False, fontsize=9,
                ncol=2, bbox_to_anchor=(1.0, 1.02))
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
light_grid(ax, "y", "#E8E8E8")
ax.text(0.005, 1.02, "Rural settlement area by LISA class",
        transform=ax.transAxes, fontsize=10, fontweight="bold")
panel_letter(ax, "d", x=-0.045, y=1.02)

# ---- stacked bars --------------------------------------------------------- #
ax2 = fig.add_subplot(gs[1])
years = [1980, 1990, 1995, 2000, 2005, 2010, 2015, 2020]
cats = ["L-L", "L-M", "L-H", "M-L", "M-M", "M-H", "H-L", "H-M", "H-H"]
cols = ["#9E1C20", "#C0392B", "#E26B5E", "#F2C14E", "#F7E3A1", "#DCE9F5",
        "#A9C7E8", "#6B9BD1", "#2F5E9E"]
rng2 = np.random.default_rng(4)
shares = np.array([
    [0.18, 0.09, 0.08, 0.10, 0.12, 0.10, 0.10, 0.12, 0.11],
    [0.17, 0.09, 0.08, 0.10, 0.12, 0.10, 0.10, 0.12, 0.12],
    [0.16, 0.09, 0.09, 0.10, 0.12, 0.10, 0.10, 0.12, 0.12],
    [0.15, 0.08, 0.09, 0.10, 0.12, 0.11, 0.10, 0.12, 0.13],
    [0.13, 0.08, 0.09, 0.10, 0.12, 0.11, 0.11, 0.12, 0.14],
    [0.10, 0.07, 0.09, 0.09, 0.12, 0.12, 0.11, 0.13, 0.17],
    [0.07, 0.06, 0.08, 0.09, 0.11, 0.12, 0.12, 0.14, 0.21],
    [0.05, 0.05, 0.07, 0.08, 0.10, 0.12, 0.12, 0.15, 0.26],
])
shares = shares / shares.sum(1, keepdims=True)
left = np.zeros(len(years))
for c, col in zip(cats, cols):
    vals = shares[:, cats.index(c)]
    ax2.barh(years, vals, left=left, color=col, edgecolor="white", height=0.72,
             label=c)
    left += vals
ax2.set_yticks(years)
ax2.set_yticklabels(years, fontsize=9)
ax2.set_xlim(0, 1)
ax2.set_xlabel("Proportion of total area", fontsize=10)
ax2.set_ylabel("Year", fontsize=10)
ax2.legend(loc="upper center", bbox_to_anchor=(1.09, 0.5), frameon=False,
           fontsize=8, title="Class")
for s in ["top", "right"]:
    ax2.spines[s].set_visible(False)
panel_letter(ax2, "e", x=-0.045, y=1.03)
ax2.text(-0.045, 1.10, "", transform=ax2.transAxes)

save(fig, "eiar13_violin_stackedbar")
