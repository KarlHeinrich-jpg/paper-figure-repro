"""
art3/16 — EIA Review 10.1016/j.eiar.2026.108409 (Jia et al., 2026)
Figure: the SCTZ framework (Structure–Canopy–Thermal–Zoning) drawn as three
interlocking rings around a central node, with the UAV/LiDAR/Sentinel workflow
on the left.

Simplified schematic reproduction: ring topology, labels and colour coding are
rebuilt with matplotlib patches; custom icons are omitted.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, FancyArrowPatch

from common import setup_style, save

setup_style()

GREEN, PINK, BLUE = "#6FA96C", "#B579A8", "#5B93C4"
GREEN_L, PINK_L, BLUE_L = "#DCEBD8", "#EFDCE9", "#D9E6F2"


def arc(ax, r, color, start, end, width=0.05, lw=2.2):
    ax.add_patch(Wedge((0, 0), r, start, end, width=width, facecolor="none",
                       edgecolor=color, lw=lw))


fig, ax = plt.subplots(figsize=(9.5, 9.5))
ax.set_xlim(-1.9, 1.9); ax.set_ylim(-1.9, 1.9)
ax.set_aspect("equal"); ax.axis("off")

ax.add_patch(Circle((0, 0), 0.42, facecolor="white", edgecolor="black", lw=2.4,
                    zorder=6))
ax.text(0, 0.08, "SCTZ", ha="center", va="center", fontsize=18, fontweight="bold",
        zorder=7)
ax.text(0, -0.15, "Framework", ha="center", va="center", fontsize=10, zorder=7)

arc(ax, 0.74, GREEN, 25, 145)
arc(ax, 0.74, PINK, 185, 305)
arc(ax, 0.74, BLUE, 310, 385)
ax.add_patch(Circle((0, 0), 1.02, fill=False, ec="#C9C9C9", lw=0.8, ls=(0, (3, 2))))
ax.add_patch(Circle((0, 0), 1.22, fill=False, ec="#E0E0E0", lw=0.8, ls=(0, (3, 2))))

for ang, txt, col in [(88, "Structure", GREEN), (238, "Thermal", PINK),
                      (345, "Model", BLUE)]:
    a = np.deg2rad(ang)
    ax.text(1.00 * np.cos(a), 1.00 * np.sin(a), txt, fontsize=12, fontweight="bold",
            color=col, ha="center", va="center",
            bbox=dict(boxstyle="circle,pad=0.32", fc="white", ec=col, lw=1.3),
            zorder=9)
for ang, num, col in [(60, "1", GREEN), (205, "2", PINK), (355, "3", BLUE)]:
    a = np.deg2rad(ang)
    ax.add_patch(Circle((0.62 * np.cos(a), 0.62 * np.sin(a)), 0.08,
                        facecolor=col, edgecolor="white", lw=1.0, zorder=8))
    ax.text(0.62 * np.cos(a), 0.62 * np.sin(a), num, color="white", fontsize=8,
            ha="center", va="center", zorder=9, fontweight="bold")

# structure bubbles (top)
for x, y, t in [(-0.30, 1.42, "Vars"), (0.18, 1.56, "Height"),
                (0.62, 1.36, "Diversity"), (0.86, 1.08, "Heterogeneity"),
                (-0.72, 1.16, "VCI"), (1.02, 0.80, "CRR"), (-0.10, 1.18, "FHD")]:
    ax.add_patch(Circle((x, y), 0.13, facecolor=GREEN_L, edgecolor="white", lw=1.2,
                        zorder=4))
    ax.text(x, y, t, ha="center", va="center", fontsize=7.5, color="#2E4F2C",
            zorder=5)

# thermal / model bubbles (bottom/right)
for x, y, t, c in [(-1.05, -1.30, "UTFVI\n& SUHI", PINK_L),
                   (-0.45, -1.50, "Thermal\nscenario", PINK_L),
                   (0.55, -1.48, "Zoning", PINK_L),
                   (1.10, -1.18, "Seasonal\nvariation", PINK_L),
                   (1.58, 0.10, "Modeling\nMapping\nInteraction", BLUE_L)]:
    ax.add_patch(Circle((x, y), 0.15, facecolor=c, edgecolor="white", lw=1.2,
                        zorder=4))
    ax.text(x, y, t, ha="center", va="center", fontsize=6.8, color="#45334F",
            zorder=5)

# workflow on the left arc
workflow = ["Point-cloud\nacquisition", "Parameters\nestimation",
            "RS-feature\nextraction", "Parameters\nupscaling",
            "Thermal stress\nquantification", "Temperature\nretrieval"]
angles = np.linspace(128, 232, len(workflow))
for i, (ang, t) in enumerate(zip(angles, workflow)):
    a = np.deg2rad(ang)
    x, y = 1.52 * np.cos(a), 1.52 * np.sin(a)
    ax.text(x, y, t, fontsize=7, ha="center", va="center", color="#333333",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9),
            zorder=6)
for i in range(len(workflow) - 1):
    a1, a2 = np.deg2rad(angles[i]), np.deg2rad(angles[i + 1])
    ax.add_patch(FancyArrowPatch((1.30 * np.cos(a1), 1.30 * np.sin(a1)),
                                 (1.30 * np.cos(a2), 1.30 * np.sin(a2)),
                                 arrowstyle="-|>", mutation_scale=7, lw=0.8,
                                 color="#555555",
                                 connectionstyle="arc3,rad=0.12", zorder=3))
ax.text(-1.86, 0.02, "UAV–LiDAR · Sentinel · Landsat\ncanopy structure &\nthermal environment dataset",
        fontsize=6.8, rotation=90, ha="center", va="center", color="#555555")

ax.add_patch(FancyArrowPatch((-0.22, 0.18), (-0.22, -0.18), arrowstyle="<|-|>",
                             mutation_scale=10, lw=2.0, color=GREEN, zorder=5))
ax.add_patch(FancyArrowPatch((0.22, 0.18), (0.22, -0.18), arrowstyle="<|-|>",
                             mutation_scale=10, lw=2.0, color=PINK, zorder=5))
ax.text(-0.50, 0.58, "Contribution", fontsize=8, rotation=32, color="#3F7A3B")
ax.text(0.18, -0.62, "Response", fontsize=8, rotation=-32, color="#8E4F80")
save(fig, "eiar16_sctz_framework")
