"""
art1 — Journal-figure reproduction:
"Environmental gradients explain nearshore microplastic distribution patterns:
 insights from machine learning models"

Figure reproduced: 5-class SHAP beeswarm panels (a–e) with an inset Nightingale
rose chart per class + a nested 5-ring donut summarising the top-10 feature
contributions in each class.

What is faithful here: model family (CatBoost, MultiClass), SHAP TreeExplainer,
beeswarm jitter algorithm, panel layout, inset rose, nested donut, colour logic
(feature value -> colour, |SHAP| -> order).
What is NOT: the numbers. The paper's survey data are not public, so the design
matrix is simulated (fixed seed) and feature names are borrowed from the paper
for readability.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as pe
from matplotlib.patches import Wedge, Patch
from matplotlib.colors import Normalize
from matplotlib import cm
from catboost import CatBoostClassifier
import shap

from common import setup_style, save, panel_letter, PAL

setup_style()
RNG = np.random.default_rng(2026)

FEATURES = [
    "pH mean", "pH max", "Salinity mean", "Salinity max", r"$\mathrm{NO_2}$ mean",
    r"$\mathrm{NO_3}$ max", "Oil mean", "Oil max", "TP mean", "TP max",
    "DO mean", "DO max", r"$\mathrm{NH_4^+}$ mean", r"$\mathrm{NH_4^+}$ max",
    r"$\mathrm{PO_4^{3-}}$ mean", r"$\mathrm{PO_4^{3-}}$ max", "TN mean",
    "TN max", r"$\mathrm{NO_3}$ mean", "Oil mg",
]
K = 5


# --------------------------------------------------------------------------- #
# 1. simulated design matrix + CatBoost model + SHAP
# --------------------------------------------------------------------------- #
def build_data(n=700, p=len(FEATURES), seed=7):
    rng = np.random.default_rng(seed)
    cov = 0.45 ** np.abs(np.subtract.outer(np.arange(p), np.arange(p)))
    X = rng.multivariate_normal(np.zeros(p), cov, size=n)
    # class structure: different subsets of features dominate each class
    W = np.zeros((p, K))
    drivers = [[0, 2, 4, 8, 12], [1, 3, 5, 9, 13],
               [2, 6, 10, 14, 16], [0, 7, 11, 15, 17], [1, 8, 12, 18, 19]]
    zipf = np.array([2.2, 1.5, 1.05, 0.75, 0.5])
    for c, idx in enumerate(drivers):
        W[idx, c] = rng.uniform(0.9, 1.5, size=len(idx)) * zipf
    logits = X @ W + rng.normal(scale=0.7, size=(n, K))
    y = logits.argmax(1)
    X = pd.DataFrame(X, columns=FEATURES)
    return X, y


Xtr, ytr = build_data(seed=7)
Xva, yva = build_data(seed=99)
model = CatBoostClassifier(loss_function="MultiClass", iterations=160, depth=4,
                           learning_rate=0.12, verbose=0, random_seed=42)
model.fit(Xtr, ytr)

explainer = shap.TreeExplainer(model)
sv = explainer.shap_values(Xva)
if isinstance(sv, np.ndarray) and sv.ndim == 3:
    sv = [sv[:, :, k] for k in range(sv.shape[2])]
sv = [np.asarray(s) for s in sv]
print("SHAP list:", len(sv), sv[0].shape)

mean_abs = np.array([np.abs(s).mean(0) for s in sv])          # (K, p)
global_imp = mean_abs.mean(0)
order_global = np.argsort(global_imp)[::-1]
top10 = order_global[:10]
rose_colors = PAL["rose"]

# --------------------------------------------------------------------------- #
# 2. beeswarm jitter (same algorithm as in the source tutorial)
# --------------------------------------------------------------------------- #
def simple_beeswarm(x_values, nbins=100, width=0.25):
    x_values = np.asarray(x_values)
    hist_range = (np.min(x_values), np.max(x_values))
    if hist_range[0] == hist_range[1]:
        hist_range = (hist_range[0] - 0.1, hist_range[1] + 0.1)
    counts, edges = np.histogram(x_values, bins=nbins, range=hist_range)
    max_count = counts.max() if counts.max() > 0 else 1
    y_values = np.zeros_like(x_values, dtype=float)
    bin_idx = np.clip(np.digitize(x_values, edges) - 1, 0, len(counts) - 1)
    for i in range(len(counts)):
        idxs = np.where(bin_idx == i)[0]
        if len(idxs) == 0:
            continue
        current_width = (counts[i] / max_count) * width
        ys = np.linspace(-current_width, current_width, len(idxs))
        RNG.shuffle(ys)
        y_values[idxs] = ys
    return y_values


# --------------------------------------------------------------------------- #
# 3. panel drawing
# --------------------------------------------------------------------------- #
def draw_beeswarm(ax, k, letter):
    s = sv[k]
    imp = mean_abs[k]
    order = np.argsort(imp)[::-1]
    n = len(order)
    for rank, j in enumerate(order):
        yy = n - 1 - rank
        col = Xva.iloc[:, j].to_numpy(float)
        col = (col - col.min()) / (col.max() - col.min() + 1e-9)
        yoff = simple_beeswarm(s[:, j], nbins=100, width=0.30)
        ax.scatter(s[:, j], yy + yoff, c=col, cmap="Spectral_r", vmin=0, vmax=1,
                   s=7, alpha=1, edgecolors="none", rasterized=True)
    ax.axvline(0, color="grey", lw=1.6, zorder=0)
    ax.set_yticks(range(n))
    ax.set_yticklabels([FEATURES[j] for j in order[::-1]], fontsize=8)
    ax.set_xlabel("Feature Impact model output (SHAP)", fontsize=10, fontweight="bold")
    ax.set_ylim(-0.8, n - 0.2)
    panel_letter(ax, letter, x=-0.17, y=1.03, size=10)
    ax.text(0.97, 0.03, f"Class {k}", transform=ax.transAxes, fontsize=12,
            fontweight="bold", ha="right", va="bottom")
    if letter == "a":
        ax.text(-0.17, 1.10, "Features", transform=ax.transAxes, fontsize=10,
                fontweight="bold")
    ax.tick_params(axis="x", labelsize=8)

    # ---- inset rose: top-10 global features' relative contribution in class k
    inset = ax.inset_axes([0.52, -0.08, 0.44, 0.72], polar=True)
    inset.set_theta_offset(np.pi / 2)
    inset.set_theta_direction(-1)
    contrib = mean_abs[k][top10]
    contrib = contrib / (contrib.sum() + 1e-12)
    ang = 2 * np.pi / 10
    for i, (c, j) in enumerate(zip(contrib, top10)):
        inset.bar(i * ang, c * 0.86, width=ang * 0.92, bottom=0.14,
                  color=rose_colors[i], edgecolor="white", linewidth=0.4)
    # label the 5 largest petals with leader lines, alternating radius
    for rank, i in enumerate(np.argsort(contrib)[::-1][:5]):
        theta = i * ang
        r_tip = 0.14 + contrib[i] * 0.86
        r_lab = 1.06 + 0.09 * (rank % 2)
        inset.annotate(f"{contrib[i]*100:.1f}%", xy=(theta, r_tip),
                       xytext=(theta + 0.05 * (-1) ** rank, r_lab),
                       ha="center", va="center", fontsize=6.5, fontweight="bold",
                       color="#111111",
                       arrowprops=dict(arrowstyle="-", lw=0.45, color="#777777",
                                       shrinkA=0, shrinkB=1),
                       bbox=dict(boxstyle="round,pad=0.10", fc="white",
                                 ec="none", alpha=0.8))
    inset.set_ylim(0, 1.22)
    inset.set_xticks([]); inset.set_yticks([])
    inset.spines["polar"].set_visible(False)
    inset.axis("off")


def draw_nested_donut(ax):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.62, 1.50)
    radii = [1.00, 0.84, 0.68, 0.52, 0.36]
    ring_w = 0.14
    start = 90.0
    for k in range(K):
        contrib = mean_abs[k][top10]
        contrib = contrib / (contrib.sum() + 1e-12)
        theta1 = start
        for i, c in enumerate(contrib):
            theta2 = theta1 - c * 360
            ax.add_patch(Wedge((0, 0), radii[k], theta2, theta1, width=ring_w,
                               facecolor=rose_colors[i], edgecolor="white", lw=0.6))
            theta1 = theta2
    ax.text(0, 1.12, "SHAP summary for different classes\n"
                     "with contribution for CatBoost % (Validation_Set)\nCatboost",
            ha="center", va="bottom", fontsize=12.5, fontweight="bold")
    handles = [Patch(facecolor=rose_colors[i], edgecolor="white",
                     label=FEATURES[j]) for i, j in enumerate(top10)]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0),
              ncol=3, frameon=False, title="Rosechart Feature Contribution %",
              handlelength=1.8, handleheight=1.1, fontsize=8,
              title_fontsize=10.5, columnspacing=0.8, labelspacing=0.25)


# --------------------------------------------------------------------------- #
# 4. figure
# --------------------------------------------------------------------------- #
def main():
    fig = plt.figure(figsize=(18, 14.5))
    gs = gridspec.GridSpec(2, 3, figure=fig, wspace=0.30, hspace=0.20)
    letters = list("abcde")
    for k in range(5):
        ax = fig.add_subplot(gs[k // 3, k % 3])
        draw_beeswarm(ax, k, letters[k])
    ax_f = fig.add_subplot(gs[1, 2])
    draw_nested_donut(ax_f)
    save(fig, "art1_shap_beeswarm_rose_donut")


if __name__ == "__main__":
    main()
