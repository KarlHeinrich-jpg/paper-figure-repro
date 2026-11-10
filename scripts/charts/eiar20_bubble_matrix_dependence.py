"""
art3/20 — EIA Review 10.1016/j.eiar.2026.108409 (Jia et al., 2026)
Figure: (a) bubble interaction matrices for three seasons with values printed
in the upper triangle; (b) 3x6 SHAP/partial-dependence panels with LOWESS
smooth and CI.

Reproduced structurally with simulated canopy-height data.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as pe
from statsmodels.nonparametric.smoothers_lowess import lowess

from common import setup_style, save, panel_letter

setup_style()
rng = np.random.default_rng(20)

VARS = ["Hmax", "p95", "MOCH", "CRR", "FHD", "VCI"]
SEASON_COL = ["#5FA05A", "#E08A3C", "#B15A5A"]   # green, orange, red
SEASON_LIGHT = ["#C9E1C3", "#F6D7B4", "#E7C3C3"]

fig = plt.figure(figsize=(15, 12))
outer = gridspec.GridSpec(2, 1, height_ratios=[1.0, 1.85], hspace=0.26,
                          figure=fig)

# ---------------- (a) bubble matrices ------------------------------------- #
top = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[0], wspace=0.28)
for s in range(3):
    ax = fig.add_subplot(top[0, s])
    vals = rng.uniform(0.06, 0.18, size=(6, 6))
    for i in range(6):
        for j in range(i + 1, 6):
            v = vals[i, j]
            ax.scatter(j, 5 - i, s=120 + v * 5200, color=SEASON_COL[s],
                       alpha=0.35 + 2.5 * v, edgecolors="white", lw=0.6)
            ax.text(j, 5 - i, f"{v:.3f}", ha="center", va="center", fontsize=5.8,
                    color="white" if v > 0.12 else "#222222",
                    path_effects=[pe.withStroke(linewidth=1.4, foreground="white")])
    for i in range(6):
        ax.scatter(i, 5 - i, s=120 + vals[i, i] * 5200,
                   color=SEASON_COL[s], alpha=0.9, edgecolors="white", lw=0.6)
    ax.set_xticks(range(6)); ax.set_xticklabels(VARS, fontsize=7.5, rotation=0)
    ax.set_yticks(range(6)); ax.set_yticklabels(VARS[::-1], fontsize=7.5)
    ax.set_xlim(-0.7, 5.7); ax.set_ylim(-0.7, 5.7)
    ax.set_aspect("equal")
    ax.set_title(["Spring", "Summer", "Autumn"][s], fontsize=9.5,
                 fontweight="bold", loc="left")
    panel_letter(ax, "a", x=-0.14, y=1.04) if s == 0 else None
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)

# ---------------- (b) 3 x 6 dependence ------------------------------------ #
bottom = gridspec.GridSpecFromSubplotSpec(3, 6, subplot_spec=outer[1],
                                          hspace=0.62, wspace=0.42)
for s in range(3):
    for j, var in enumerate(["Hmax", "p95", "MOCH", "CRR", "FHD", "VCI"]):
        ax = fig.add_subplot(bottom[s, j])
        n = 260
        x = rng.uniform(5, 25, n) if var == "Hmax" else rng.normal(0, 1, n)
        j = ["Hmax", "p95", "MOCH", "CRR", "FHD", "VCI"].index(var)
        amp = 0.55 + 0.22 * j
        w = [0.55, 0.9, 1.3, 1.7, 2.1, 0.7][j]
        ph = [0.0, 0.6, 1.1, 1.6, 2.1, 2.6][s]
        y = (amp * (np.sin(w * x + ph) + 0.3 * np.cos(0.5 * x + j)) +
             rng.normal(0, 0.30, n))
        ax.scatter(x, y, s=6, color=SEASON_COL[s], alpha=0.28, lw=0)
        lw = lowess(y, x, frac=0.45, return_sorted=True)
        ax.plot(lw[:, 0], lw[:, 1], color=SEASON_COL[s], lw=1.6)
        ax.fill_between(lw[:, 0], lw[:, 1] - 0.28, lw[:, 1] + 0.28,
                        color=SEASON_LIGHT[s], alpha=0.55, lw=0)
        ax.axhline(0, color="#AAAAAA", lw=0.6, ls="--")
        ax.set_title(var, fontsize=8, fontweight="bold", loc="right", pad=2)
        ax.set_ylim(-1.9, 1.9)
        ax.set_xticklabels(ax.get_xticks(), fontsize=6)
        ax.tick_params(labelsize=6)
        if j == 5:
            ax.set_ylabel("Total SHAP Value", fontsize=7)
        if s == 2:
            ax.set_xlabel(var, fontsize=7)
        if s == 0 and j == 0:
            panel_letter(ax, "b", x=-0.45, y=1.25)

save(fig, "eiar20_bubble_matrix_dependence")
