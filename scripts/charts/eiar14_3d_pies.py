"""
art3/14b — EIA Review 10.1016/j.eiar.2026.108383 (Yang et al., 2026)
Figure: three floating 3D pie/cylinder charts showing the composition of
cropping systems in 2001, 2010 and 2020.

Matplotlib has no native 3D pie; the cylinders are built from an elliptical
top surface + side walls (a 2.5D projection), which reproduces the look of the
original panel. Map panel (c) is not reproduced.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon, Ellipse, Patch

from common import setup_style, save

setup_style()

CATS = ["Wheat Monoculture System", "Wheat-Soybean System",
        "Wheat-Winter-Summer Maize Rotation System",
        "Wheat-Winter-Summer Maize Double System", "Rice Monoculture System",
        "Other"]
COLS = ["#B2182B", "#D6604D", "#F4A582", "#FDBB84", "#4C86C6", "#7BAF6A"]
DATA = {
    2001: [0.13, 0.05, 0.48, 0.24, 0.06, 0.04],
    2010: [0.09, 0.04, 0.34, 0.31, 0.10, 0.12],
    2020: [0.07, 0.03, 0.27, 0.31, 0.13, 0.19],
}


def pts_arc(cx, cy, r, t1, t2, ay=0.42, n=60):
    t = np.linspace(t1, t2, n)
    return np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t) * ay])


def draw_pie3d(ax, values, colors, cx=0.5, cy=0.50, r=0.28, h=0.16, ay=0.42):
    start = 90.0
    edges = []
    a = start
    for v in values:
        edges.append((a, a - v * 360))
        a -= v * 360
    # side walls back-to-front
    for (t1, t2), c in sorted(zip(edges, colors),
                              key=lambda z: np.sin(np.deg2rad((z[0][0] + z[0][1]) / 2))):
        top = pts_arc(cx, cy + h, r, np.deg2rad(t1), np.deg2rad(t2), ay)
        bot = pts_arc(cx, cy, r, np.deg2rad(t1), np.deg2rad(t2), ay)
        poly = np.vstack([top, bot[::-1]])
        ax.add_patch(Polygon(poly, closed=True, facecolor=c, edgecolor="#333333",
                             lw=0.5, alpha=0.95, zorder=2))
    for (t1, t2), c, v in zip(edges, colors, values):
        arc = pts_arc(cx, cy + h, r, np.deg2rad(t1), np.deg2rad(t2), ay)
        poly = np.vstack([[cx, cy + h], arc])
        ax.add_patch(Polygon(poly, closed=True, facecolor=c, edgecolor="white",
                             lw=0.8, zorder=4))
    # percentages for the three largest sectors
    mids = [( (t1 + t2) / 2, v) for (t1, t2), v in zip(edges, values)]
    for tmid, v in sorted(mids, key=lambda z: -z[1])[:3]:
        ang = np.deg2rad(tmid)
        xt = cx + 0.72 * r * np.cos(ang)
        yt = cy + h + 0.72 * r * np.sin(ang) * ay
        ax.text(xt, yt, f"{v*100:.1f}%", ha="center", va="center", fontsize=8,
                fontweight="bold", zorder=5,
                path_effects=[pe.withStroke(linewidth=2, foreground="white")])


fig, axes = plt.subplots(3, 1, figsize=(7.2, 8.4))
for ax, (year, vals) in zip(axes, DATA.items()):
    ax.set_xlim(0, 1); ax.set_ylim(0.28, 0.78); ax.axis("off")
    draw_pie3d(ax, vals, COLS)
    ax.text(0.5, 0.50, str(year), ha="center", va="center", fontsize=13,
            fontweight="bold", zorder=8)
    ax.text(0.02, 0.95, f"{year}", fontsize=10, fontweight="bold")

handles = [Patch(facecolor=c, edgecolor="white", label=l)
           for c, l in zip(COLS, CATS)]
fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=8,
           bbox_to_anchor=(0.5, 0.00))
fig.subplots_adjust(bottom=0.14, hspace=0.05)
save(fig, "eiar14_3d_pies")
