"""
Conceptual-framework diagrams from the linked papers, redrawn with matplotlib
patches (no bitmaps).

Panels:
  a  EIA Review 10.1016/j.eiar.2026.108402 — GeoXAI flood-risk workflow
  b  EIA Review 10.1016/j.eiar.2026.108402 — BERT two-stage text pipeline
  c  EIA Review 10.1016/j.eiar.2026.108393 — PM2.5 exposure 3-step framework
  d  JCP 10.1016/j.jclepro.2025.146675 — cropland carbon emission framework

Schematic reproductions: grouping and arrow topology follow the originals;
icons/photos and exact copy are simplified.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

from common import setup_style, save, rounded_box, arrow, panel_letter

setup_style()

BLUE = ("#E8F1FB", "#2C5F8A")
ORANGE = ("#FDEBDC", "#B85C1E")
GREEN = ("#E7F3E8", "#3C7A46")
PINK = ("#FBE9EC", "#A33B4A")
GREY = ("#F4F4F4", "#666666")


def label(ax, x, y, s, fs=8.5, color="#111111"):
    ax.text(x, y, s, fontsize=fs, fontweight="bold", ha="left", va="center",
            color=color, zorder=6)


def mini_maps(ax, x, y, w, h, n=3, vertical=False):
    for k in range(n):
        xx = x + (0 if vertical else k * (w + 0.012))
        yy = y + (k * (h + 0.012) if vertical else 0)
        ax.add_patch(Rectangle((xx, yy), w, h, facecolor="#F7F7F7",
                               edgecolor="#AAAAAA", lw=0.5, zorder=2))
        ax.add_patch(Circle((xx + w * 0.5, yy + h * 0.5), min(w, h) * 0.26,
                            facecolor=("#C94C4C", "#3B7DD8", "#E8B33C")[k % 3],
                            alpha=0.55, edgecolor="none", zorder=3))


fig = plt.figure(figsize=(16, 12.5))
gs = fig.add_gridspec(2, 2, wspace=0.05, hspace=0.08, figure=fig)
axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]
for ax in axes:
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

# ------------------------------------------------------------------ (a) ---- #
ax = axes[0]
ax.add_patch(Rectangle((0.005, 0.50), 0.485, 0.49, fill=False, ec="#444444",
                       lw=0.9, ls="--"))
ax.add_patch(Rectangle((0.505, 0.50), 0.49, 0.49, fill=False, ec="#444444",
                       lw=0.9, ls="--"))
ax.add_patch(Rectangle((0.005, 0.005), 0.485, 0.47, fill=False, ec="#444444",
                       lw=0.9, ls="--"))
ax.add_patch(Rectangle((0.505, 0.005), 0.49, 0.47, fill=False, ec="#444444",
                       lw=0.9, ls="--"))
label(ax, 0.02, 0.965, "Step 1: The quantification of PPFR", 8)
rounded_box(ax, (0.03, 0.84), 0.13, 0.075, "Weibo\nDataset", *BLUE, fs=7)
rounded_box(ax, (0.20, 0.84), 0.15, 0.075, "BERT models", *GREY, fs=7)
rounded_box(ax, (0.03, 0.66), 0.34, 0.09, "Public-perceived flood risk (PPFR)",
            *ORANGE, fs=7.5)
mini_maps(ax, 0.05, 0.54, 0.09, 0.075)
arrow(ax, (0.095, 0.84), (0.095, 0.75))
arrow(ax, (0.275, 0.84), (0.23, 0.75))

label(ax, 0.02, 0.455, "Step 2: Influencing factors", 8)
rounded_box(ax, (0.02, 0.32), 0.44, 0.095,
            "Natural environment\nPrecipitation · Elevation · NDVI", *GREEN, fs=7)
rounded_box(ax, (0.02, 0.19), 0.44, 0.095,
            "Build environment\nRoad · Building · Impervious · Shannon", *PINK, fs=7)
rounded_box(ax, (0.02, 0.06), 0.44, 0.095,
            "Socioeconomic + spatial proxy\nNight light · Population · u, v",
            *BLUE, fs=7)

label(ax, 0.52, 0.965, "Step 3: Geospatial explainable AI", 8)
rounded_box(ax, (0.52, 0.86), 0.20, 0.07, "PPFE dataset\nindependent / dependent",
            *BLUE, fs=6.6)
rounded_box(ax, (0.52, 0.75), 0.20, 0.07, "Multicollinearity\nVIF test", *GREY,
            fs=6.6)
rounded_box(ax, (0.52, 0.64), 0.20, 0.07, "Spatial autocorrelation\nGlobal Moran's I",
            *GREY, fs=6.6)
rounded_box(ax, (0.52, 0.51), 0.20, 0.07, "GeoShapley\nexplanation", *PINK, fs=6.8)
rounded_box(ax, (0.77, 0.865), 0.21, 0.065, "Model evaluation\n$R^2$ · MAE · RMSE",
            *BLUE, fs=6.4)
rounded_box(ax, (0.77, 0.70), 0.21, 0.13,
            "Fast and lightweight\nAutoML\nhyperparameter tuning\n5-fold CV ×50",
            *ORANGE, fs=6.4)
rounded_box(ax, (0.77, 0.53), 0.21, 0.10, "Regression module\nOLS · GWR · XGBoost",
            *GREEN, fs=6.8)
arrow(ax, (0.62, 0.86), (0.62, 0.82))
arrow(ax, (0.62, 0.75), (0.62, 0.71))
arrow(ax, (0.62, 0.64), (0.62, 0.58))
arrow(ax, (0.72, 0.665), (0.77, 0.60))
arrow(ax, (0.875, 0.70), (0.875, 0.665))
arrow(ax, (0.875, 0.83), (0.875, 0.865))
arrow(ax, (0.77, 0.575), (0.72, 0.55))

label(ax, 0.52, 0.455, "Step 4: Impact assessment results", 8)
for k, (t, y) in enumerate([("Nonlinear effects", 0.34), ("Feature importance", 0.24),
                            ("Spatial fixed effects", 0.14), ("Spatial heterogeneity", 0.04)]):
    rounded_box(ax, (0.52, y), 0.26, 0.075, t, *GREY, fs=6.6)
    ax.plot([0.78, 0.80], [y + 0.037, y + 0.037], color="#777777", lw=0.7)
mini_maps(ax, 0.82, 0.05, 0.045, 0.10, n=3, vertical=True)
panel_letter(ax, "a", x=0.0, y=1.00)

# ------------------------------------------------------------------ (b) ---- #
ax = axes[1]
ax.add_patch(Rectangle((0.005, 0.52), 0.60, 0.46, fill=False, ec="#444444",
                       lw=0.9, ls="--"))
ax.add_patch(Rectangle((0.005, 0.02), 0.60, 0.46, fill=False, ec="#444444",
                       lw=0.9, ls="--"))
label(ax, 0.02, 0.945, "Stage I : Text Classification", 8)
rounded_box(ax, (0.02, 0.81), 0.15, 0.09, "Text classification\ndataset\n(5 classes)",
            *BLUE, fs=6.3)
rounded_box(ax, (0.20, 0.79), 0.10, 0.17, "Chinese-\nRoBERTa\nwww-ext", *PINK, fs=6.4)
rounded_box(ax, (0.34, 0.83), 0.23, 0.09, "Fine-tuning\nAdamW · CE · linear decay",
            *GREY, fs=6.4)
rounded_box(ax, (0.34, 0.71), 0.23, 0.075, "Evaluation\nAcc 95.54 · F1 95.56",
            *GREY, fs=6.4)
arrow(ax, (0.17, 0.855), (0.20, 0.875))
arrow(ax, (0.30, 0.875), (0.34, 0.875))
arrow(ax, (0.455, 0.83), (0.455, 0.785))

label(ax, 0.02, 0.455, "Stage II : Location entity extraction", 8)
rounded_box(ax, (0.02, 0.31), 0.15, 0.09, "Location entity\ndataset\n(BIO tags)",
            *BLUE, fs=6.3)
rounded_box(ax, (0.20, 0.29), 0.10, 0.17, "Chinese-\nRoBERTa\nwww-ext", *PINK, fs=6.4)
rounded_box(ax, (0.34, 0.33), 0.23, 0.09, "Fine-tuning\nAdamW · CE · linear decay",
            *GREY, fs=6.4)
rounded_box(ax, (0.34, 0.21), 0.23, 0.075, "Evaluation\nAcc 99.18 · F1 80.30",
            *GREY, fs=6.4)
arrow(ax, (0.17, 0.355), (0.20, 0.375))
arrow(ax, (0.30, 0.375), (0.34, 0.375))
arrow(ax, (0.455, 0.33), (0.455, 0.285))

rounded_box(ax, (0.64, 0.74), 0.14, 0.09, "Best classification\nmodel", *GREY, fs=6.5)
ax.scatter([0.855], [0.785], marker="D", s=250, facecolor="#F7F7F7",
           edgecolor="#555555", zorder=4)
ax.text(0.86, 0.785, "Flood-risk\nlocation\nentity?", ha="center", va="center",
        fontsize=5.4, zorder=5)
rounded_box(ax, (0.935, 0.76), 0.05, 0.05, "End", *GREY, fs=6.5)
arrow(ax, (0.78, 0.785), (0.826, 0.785))
arrow(ax, (0.884, 0.785), (0.935, 0.785))
ax.text(0.912, 0.802, "No", fontsize=5.5)
rounded_box(ax, (0.64, 0.52), 0.14, 0.09, "Best location\nextraction model",
            *GREY, fs=6.5)
rounded_box(ax, (0.64, 0.35), 0.14, 0.075, "Flood-risk location\n(Baidu API)",
            *ORANGE, fs=6.3)
rounded_box(ax, (0.64, 0.19), 0.14, 0.07, "Flood-risk point", *GREEN, fs=6.8)
arrow(ax, (0.71, 0.74), (0.71, 0.61))
ax.text(0.715, 0.60, "Yes", fontsize=6)
arrow(ax, (0.71, 0.52), (0.71, 0.425))
arrow(ax, (0.71, 0.35), (0.71, 0.26))
ax.text(0.72, 0.45, "Step 4", fontsize=5.5, color="#666666")
ax.text(0.72, 0.30, "Step 5", fontsize=5.5, color="#666666")
panel_letter(ax, "b", x=0.0, y=1.00)

# ------------------------------------------------------------------ (c) ---- #
ax = axes[2]
ax.add_patch(Rectangle((0.01, 0.01), 0.98, 0.97, fill=False, ec="#444444", lw=0.9))
rounded_box(ax, (0.06, 0.88), 0.88, 0.07,
            "Data: PM$_{2.5}$ monitoring · built/social/meteorological environment · "
            "mobile signal", *GREY, fs=7.6)
rounded_box(ax, (0.06, 0.70), 0.88, 0.09,
            "Step 1: PM$_{2.5}$ exposure risk assessment", *BLUE, fs=8.5)
rounded_box(ax, (0.06, 0.50), 0.88, 0.09,
            "Step 2: Spatial inequality identification", *GREEN, fs=8.5)
rounded_box(ax, (0.06, 0.22), 0.88, 0.075,
            "Step 3: Impact mechanisms analysis", *ORANGE, fs=8.5)
for x, t in [(0.17, "Gini coefficient\n(overall inequality)"),
             (0.50, "Bivariate spatial\nautocorrelation"),
             (0.83, "XGBoost + SHAP\n(nonlinear / importance)")]:
    rounded_box(ax, (x - 0.135, 0.33), 0.27, 0.09, t, *PINK, fs=6.5)
arrow(ax, (0.50, 0.88), (0.50, 0.79))
arrow(ax, (0.50, 0.70), (0.50, 0.59))
for x in (0.17, 0.50, 0.83):
    arrow(ax, (x, 0.50), (x, 0.42))
    arrow(ax, (x, 0.33), (x, 0.295))
rounded_box(ax, (0.14, 0.07), 0.72, 0.075,
            "Precision mitigation and equitable management strategies", *GREY, fs=7.6)
arrow(ax, (0.50, 0.22), (0.50, 0.145))
panel_letter(ax, "c", x=0.0, y=1.00)

# ------------------------------------------------------------------ (d) ---- #
ax = axes[3]
ax.add_patch(Rectangle((0.01, 0.01), 0.98, 0.97, fill=False, ec="#444444", lw=0.9))
rounded_box(ax, (0.03, 0.70), 0.15, 0.22,
            "Natural\nElements\n\nTemperature\nPrecipitation\nTopography\nSolar radiation",
            *GREEN, fs=6.2)
rounded_box(ax, (0.25, 0.76), 0.16, 0.12, "Crop Growth\n(rice / upland)", *GREEN, fs=6.8)
rounded_box(ax, (0.25, 0.60), 0.16, 0.12, "Agricultural\nInput", *ORANGE, fs=6.8)
rounded_box(ax, (0.25, 0.44), 0.16, 0.12, "Energy\nConsumption", *ORANGE, fs=6.8)
rounded_box(ax, (0.25, 0.28), 0.16, 0.12, "Microbial\nRespiration", *BLUE, fs=6.8)
rounded_box(ax, (0.48, 0.80), 0.16, 0.10, "Indirect carbon\nemissions", *PINK, fs=6.8)
rounded_box(ax, (0.48, 0.64), 0.16, 0.10, "CO$_2$ / N$_2$O", *GREY, fs=6.8)
rounded_box(ax, (0.48, 0.48), 0.16, 0.10, "Crop residue\nburning", *ORANGE, fs=6.8)
rounded_box(ax, (0.48, 0.32), 0.16, 0.10, "Direct carbon\nemissions", *PINK, fs=6.8)
rounded_box(ax, (0.72, 0.72), 0.20, 0.14,
            "Human activities /\nsocioeconomic\ndevelopment", *ORANGE, fs=6.8)
rounded_box(ax, (0.72, 0.46), 0.20, 0.12,
            "Farm management\n(fertilizer, water,\nstraw return)", *GREEN, fs=6.2)
rounded_box(ax, (0.72, 0.22), 0.20, 0.12,
            "Subsurface system\n(groundwater, SOC,\ndrought)", *BLUE, fs=6.2)
for x1, y1, x2, y2 in [(0.18, 0.84, 0.25, 0.82), (0.18, 0.76, 0.25, 0.66),
                       (0.41, 0.82, 0.48, 0.85), (0.41, 0.66, 0.48, 0.69),
                       (0.41, 0.50, 0.48, 0.53), (0.41, 0.34, 0.48, 0.37),
                       (0.64, 0.85, 0.72, 0.79), (0.64, 0.69, 0.72, 0.52),
                       (0.64, 0.37, 0.72, 0.52), (0.64, 0.55, 0.72, 0.52)]:
    arrow(ax, (x1, y1), (x2, y2))
ax.text(0.50, 0.16, "Interactions: CO$_2$ | CH$_4$ | N$_2$O", fontsize=7,
        ha="center", style="italic")
panel_letter(ax, "d", x=0.0, y=1.00)

save(fig, "frameworks_montage")
