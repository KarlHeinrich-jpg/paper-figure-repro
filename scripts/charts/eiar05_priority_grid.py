"""
art3/05 — EIA Review 10.1016/j.eiar.2026.108402 (Li et al., 2026)
Figure: conceptual comparison of "static homogeneous" vs "stage-specific,
dynamically adjustable" priority units on a 4x4 grid.

This is a schematic (no data), reproduced with matplotlib patches.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import matplotlib.gridspec as gridspec

from common import setup_style, save

setup_style()
rng = np.random.default_rng(8)
COL = {"R": "#D95F5F", "G": "#4F9B5A", "C": "#F5F0C9"}
LABEL = {"R": "Precipitation-dominated unit", "G": "Road density-dominated unit",
         "C": "Building density-dominated unit"}
PRIO_COL = {"H": "#2C4F8F", "M": "#4C86C6", "L": "#A8C4E0"}


def grid_cells(ax, x0, y0, w, h, n=4, colors=None, circles=False, seed=0,
               uniform=False):
    rng = np.random.default_rng(seed)
    cw, ch = w / n, h / n
    for r in range(n):
        for c in range(n):
            key = colors[r][c] if colors is not None else "C"
            ax.add_patch(Rectangle((x0 + c * cw, y0 + (n - 1 - r) * ch), cw, ch,
                                   facecolor=COL[key], edgecolor="#333333", lw=0.7))
            if circles:
                size = "M" if uniform else rng.choice(["H", "M", "L"],
                                                      p=[0.30, 0.35, 0.35])
                rad = {"H": 0.36, "M": 0.25, "L": 0.14}[size]
                ax.add_patch(Circle((x0 + c * cw + cw / 2, y0 + (n - 1 - r) * ch + ch / 2),
                                    rad * cw, facecolor=PRIO_COL[size],
                                    edgecolor="#1F3557", lw=0.8, zorder=3))


fig = plt.figure(figsize=(13, 9.6))
gs = gridspec.GridSpec(3, 4, width_ratios=[1.05, 0.10, 1.0, 1.0],
                       wspace=0.10, hspace=0.10, figure=fig)
# column headers
fig.text(0.30, 0.965, "New mechanism:", fontsize=11, fontweight="bold", ha="left")
fig.text(0.36, 0.942, "Stage-specific and dynamically adjustable prioritization",
         fontsize=11.5, fontweight="bold", ha="left")
ax0 = fig.add_subplot(gs[:, 0])
ax0.set_xlim(0, 1); ax0.set_ylim(0, 1); ax0.set_box_aspect(1); ax0.axis("off")
ax0.set_title("Old mechanism:\nStatic and homogeneous", fontsize=12,
              fontweight="bold", loc="left", pad=10)
grid_cells(ax0, 0.28, 0.50, 0.46, 0.46, circles=True, seed=1, uniform=True)
ax0.text(0.05, 0.35, "Same priority everywhere", fontsize=9, style="italic")

# stage labels + grids
stages = ["Pre-flood stage", "During-flood stage", "Post-flood stage"]
for i, stage in enumerate(stages):
    a1 = fig.add_subplot(gs[i, 2])
    a2 = fig.add_subplot(gs[i, 3])
    cols1 = rng.choice(list("RGC"), size=(4, 4), p=[0.35, 0.35, 0.30])
    cols2 = cols1.copy()
    # refine some cells' priority only (colours stay)
    grid_cells(a1, 0.03, 0.03, 0.94, 0.94, colors=cols1)
    grid_cells(a2, 0.03, 0.03, 0.94, 0.94, colors=cols2, circles=True, seed=10 + i)
    for a in (a1, a2):
        a.set_xlim(0, 1); a.set_ylim(0, 1); a.set_xticks([]); a.set_yticks([])
        a.set_box_aspect(1)
    if i == 0:
        a1.text(0.5, 1.10, "Step 1: Intervention\ncategorization", ha="center",
                va="bottom", fontsize=10, fontweight="bold", transform=a1.transAxes)
        a2.text(0.5, 1.10, "Step 2: Unit priority\nrefinement", ha="center",
                va="bottom", fontsize=10, fontweight="bold", transform=a2.transAxes)
    a1.text(-0.10, 0.5, stage, rotation=90, va="center", ha="center",
            fontsize=10, fontweight="bold", transform=a1.transAxes)

# vertical dividers
for x in [0.288]:
    fig.add_artist(plt.Line2D([x, x], [0.07, 0.93], color="black", lw=1.0))
handles = [Rectangle((0, 0), 1, 1, fc=COL[k], ec="#333333", label=LABEL[k])
           for k in ["C", "R", "G"]]
handles += [Circle((0, 0), 1, fc=PRIO_COL["H"], ec="#1F3557",
                   label="High-priority intervention unit"),
            Circle((0, 0), 1, fc=PRIO_COL["M"], ec="#1F3557",
                   label="Medium-priority intervention unit"),
            Circle((0, 0), 1, fc=PRIO_COL["L"], ec="#1F3557",
                   label="Low-priority intervention unit")]
fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.02, 0.01),
           frameon=False, fontsize=8.5, handlelength=1.4)
save(fig, "eiar05_priority_grid_schematic")
