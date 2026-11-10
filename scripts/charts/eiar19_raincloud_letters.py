"""
art3/19b — EIA Review 10.1016/j.eiar.2026.108409 (Jia et al., 2026)
Figure: seasonal rain-cloud boxplots of ΔLST across eight canopy-structure
classes, with compact-letter-display significance labels.

Reproduced with simulated data; the seasonal maps in panel (a) need the SUHI
raster and are not reproduced.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from common import setup_style, save, panel_letter, box_jitter

setup_style()
rng = np.random.default_rng(19)

CATS = ["L_Very High", "L_High", "L_Moderate", "L_Low", "L_No",
        "H_Very High", "H_High", "H_Moderate", "H_Low", "H_No"]
SEASONS = ["Spring", "Summer", "Autumn"]
COLORS = {"Spring": "#6A9E4F", "Summer": "#E08A3C", "Autumn": "#B15A5A"}
BASE = {"Spring": 0.0, "Summer": 0.6, "Autumn": -0.6}
EFFECT = np.array([0.28, 0.10, 0.02, -0.08, -0.16, 0.36, 0.16, 0.02, -0.10, -0.22])

fig, axes = plt.subplots(1, 3, figsize=(16, 5.6), gridspec_kw=dict(wspace=0.16))
for k, season in enumerate(SEASONS):
    ax = axes[k]
    data = []
    for i, cat in enumerate(CATS):
        mu = BASE[season] + EFFECT[i] * (1.0 if season != "Autumn" else 0.55)
        data.append(rng.normal(mu, 0.42 + 0.06 * i, size=260))
    sns.violinplot(data=data, ax=ax, color=COLORS[season], cut=0, inner=None,
                   density_norm="width", linewidth=0.6, saturation=1,
                   bw_adjust=0.7)
    for v in ax.collections:
        v.set_alpha(0.28)
    box_jitter(ax, data, np.arange(len(CATS)), [COLORS[season]] * len(CATS),
               width=0.34, jitter=0.15, point_size=2.0, alpha=0.18)
    ax.set_xticks(np.arange(len(CATS)))
    ax.set_xticklabels(CATS, rotation=55, ha="right", fontsize=7.5)
    ax.set_ylabel(r"$\Delta$LST", fontsize=10)
    ax.set_title(season, fontsize=10.5, fontweight="bold")
    ax.axhline(0, color="#888888", lw=0.7, ls="--")
    ax.tick_params(axis="y", labelsize=8)
    # compact letter display (fixed, illustrative)
    letters = ["a", "b", "bc", "c", "d", "ab", "bc", "c", "d", "e"]
    ytxt = [np.percentile(d, 99) + 0.30 for d in data]
    for x, yy, s in zip(range(len(CATS)), ytxt, letters):
        ax.text(x, yy, s, ha="center", va="bottom", fontsize=7,
                color=COLORS[season], fontweight="bold")
    ax.set_ylim(np.percentile(np.concatenate(data), 0.3) - 0.3, max(ytxt) + 0.25)
    panel_letter(ax, "abc"[k], x=-0.10, y=1.04)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

save(fig, "eiar19_raincloud_letters")
