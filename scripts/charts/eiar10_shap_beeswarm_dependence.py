"""
art3/10 — EIA Review 10.1016/j.eiar.2026.108402 (Li et al., 2026)
Figure: SHAP beeswarm with factor-family background bars + 8 dependence plots
with LOWESS trend, 95% CI band and R^2.

Faithful: model family (boosted trees), SHAP values, group colour bands
(BE / SE / ME), dual-encoding beeswarm, dependence panels with trend band.
Simulated: all values (survey-derived PPFR data are not public).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from statsmodels.nonparametric.smoothers_lowess import lowess
from catboost import CatBoostRegressor
import shap

from common import setup_style, save, panel_letter, PAL

setup_style()
RNG = np.random.default_rng(3)

GROUPS = {
    "BE": ["D_stops", "D_building", "ratio_midhigh", "D_pop", "Adt_CBD", "R",
           "House_price", "LU_mix", "ratio_oldchild", "RD_main", "Prop_serv",
           "POI_mix"],
    "SE": ["GDP", "G", "ratio_male", "ratio_outerpop", "D_consume", "M", "B",
           "governfund", "balance_ratio", "Adt_CC"],
    "ME": ["rain", "pres", "temp", "wind_s", "wet"],
}
GROUP_COLOR = {"BE": "#F6C9CE", "SE": "#F3D3A2", "ME": "#BFD7EA"}
FEATURES = GROUPS["BE"] + GROUPS["SE"] + GROUPS["ME"]
GROUP_OF = {f: g for g, fs in GROUPS.items() for f in fs}

CMAP = LinearSegmentedColormap.from_list(
    "bpr", ["#2E6FD0", "#7E6BC4", "#C4478E", "#E0246E"])


def make_data(n=1500):
    rng = np.random.default_rng(12)
    p = len(FEATURES)
    cov = 0.30 ** np.abs(np.subtract.outer(np.arange(p), np.arange(p)))
    X = rng.multivariate_normal(np.zeros(p), cov, size=n)
    y = np.zeros(n)
    for j, f in enumerate(FEATURES):
        a = rng.uniform(0.45, 1.05) if GROUP_OF[f] == "BE" else rng.uniform(0.08, 0.40)
        w = rng.uniform(0.8, 2.2)
        ph = rng.uniform(0, 2 * np.pi)
        y += a * (np.sin(w * X[:, j] + ph) + 0.25 * X[:, j] ** 2)
    # a few pairwise interactions
    i1, i2 = FEATURES.index("D_stops"), FEATURES.index("D_pop")
    y += 0.5 * X[:, i1] * np.tanh(X[:, i2])
    i3, i4 = FEATURES.index("House_price"), FEATURES.index("LU_mix")
    y += 0.45 * np.cos(1.4 * X[:, i3]) * X[:, i4]
    y += rng.normal(scale=0.25, size=n)
    return pd.DataFrame(X, columns=FEATURES), y


X, y = make_data()
model = CatBoostRegressor(iterations=300, depth=5, learning_rate=0.08,
                          verbose=0, random_seed=42)
model.fit(X, y)
expl = shap.TreeExplainer(model)
SV = expl.shap_values(X)
mean_abs = np.abs(SV).mean(0)
order = np.argsort(mean_abs)[::-1]

# --------------------------------------------------------------------------- #
# figure layout: left beeswarm | 2x4 dependence | colorbar
# --------------------------------------------------------------------------- #
fig = plt.figure(figsize=(14, 11))
gs = gridspec.GridSpec(1, 3, width_ratios=[1.05, 2.0, 0.055], wspace=0.30,
                       figure=fig)
axb = fig.add_subplot(gs[0, 0])


def beeswarm_offsets(v, nbins=90, width=0.34):
    v = np.asarray(v)
    lo, hi = v.min(), v.max()
    if lo == hi:
        return np.zeros_like(v)
    counts, edges = np.histogram(v, bins=nbins, range=(lo, hi))
    idx = np.clip(np.digitize(v, edges) - 1, 0, len(counts) - 1)
    out = np.zeros_like(v, dtype=float)
    for i in range(len(counts)):
        sel = np.where(idx == i)[0]
        if len(sel) == 0:
            continue
        w = counts[i] / counts.max() * width
        vals = np.linspace(-w, w, len(sel))
        RNG.shuffle(vals)
        out[sel] = vals
    return out


n = len(FEATURES)
ypos = np.arange(n)[::-1]
for rank, j in enumerate(order):
    yy = n - 1 - rank
    axb.barh(yy, mean_abs[j], height=0.78, color=GROUP_COLOR[GROUP_OF[FEATURES[j]]],
             edgecolor="none", zorder=0)
for rank, j in enumerate(order):
    yy = n - 1 - rank
    col = X.iloc[:, j].to_numpy(float)
    col = (col - col.min()) / (col.max() - col.min() + 1e-9)
    axb.scatter(SV[:, j], yy + beeswarm_offsets(SV[:, j]), c=col, cmap=CMAP,
                s=6, alpha=0.9, lw=0, rasterized=True, zorder=2)
axb.axvline(0, color="white", lw=1.4, zorder=1)
axb.set_yticks(ypos)
axb.set_yticklabels([FEATURES[j] for j in order], fontsize=8)
axb.set_xlabel("Shapley Value Contribution (Beeswarm)", fontsize=10, fontweight="bold")
axb.set_title("Mean Shapley Value (Feature Importance)", fontsize=10,
              fontweight="bold", pad=18)
panel_letter(axb, "a", x=-0.02, y=1.04)
handles = [plt.Rectangle((0, 0), 1, 1, fc=GROUP_COLOR[g], ec="none", label=g)
           for g in ["BE", "SE", "ME"]]
axb.legend(handles=handles, loc="lower right", fontsize=8, frameon=False,
           handlelength=1.2, title="Group")
for s in ["top", "right"]:
    axb.spines[s].set_visible(False)

# --------------------------------------------------------------------------- #
# dependence panels
# --------------------------------------------------------------------------- #
dep = [FEATURES[j] for j in order[:8]]
inner = gridspec.GridSpecFromSubplotSpec(4, 2, subplot_spec=gs[0, 1],
                                         hspace=0.62, wspace=0.30)
for k, f in enumerate(dep):
    ax = fig.add_subplot(inner[k // 2, k % 2])
    j = FEATURES.index(f)
    xv = X[f].to_numpy(float)
    sv = SV[:, j]
    cnorm = (xv - xv.min()) / (xv.max() - xv.min() + 1e-9)
    ax.scatter(xv, sv, c=cnorm, cmap=CMAP, s=6, alpha=0.55, lw=0, rasterized=True)
    # LOWESS trend + bootstrap-free CI from binned residual spread
    lw = lowess(sv, xv, frac=0.33, return_sorted=True)
    ax.plot(lw[:, 0], lw[:, 1], color="#B2182B", lw=1.8, zorder=3,
            label="Trendline")
    bins = np.linspace(xv.min(), xv.max(), 14)
    bc = 0.5 * (bins[1:] + bins[:-1])
    sd = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (xv >= lo) & (xv < hi)
        sd.append(sv[m].std() if m.sum() > 4 else np.nan)
    sd = np.array(sd)
    ax.fill_between(bc, np.interp(bc, lw[:, 0], lw[:, 1]) - 1.96 * sd,
                    np.interp(bc, lw[:, 0], lw[:, 1]) + 1.96 * sd,
                    color="#F4A6A0", alpha=0.35, lw=0, label="95% CI", zorder=1)
    fit = np.interp(xv, lw[:, 0], lw[:, 1])
    r2 = np.corrcoef(fit, sv)[0, 1] ** 2
    ax.axhline(0, color="#999999", lw=0.7, ls="--")
    ax.text(0.97, 0.06, f"$R^2$={r2:.2f}", transform=ax.transAxes, ha="right",
            fontsize=8)
    ax.set_title(f, fontsize=9, fontweight="bold", loc="left", pad=2)
    ax.set_xlabel(f, fontsize=8)
    ax.set_ylabel("Total SHAP Value", fontsize=8)
    ax.set_xlim(xv.min() - 0.03 * np.ptp(xv), xv.max() + 0.03 * np.ptp(xv))
    ax.tick_params(labelsize=7)
    if k == 0:
        ax.legend(loc="upper right", fontsize=7, frameon=False, handlelength=1.4)
        panel_letter(ax, "b", x=-0.30, y=1.22, size=11)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)

# colourbar
cax = fig.add_subplot(gs[0, 2])
cb = fig.colorbar(ScalarMappable(norm=Normalize(0, 1), cmap=CMAP), cax=cax)
cb.set_ticks([0, 1])
cb.set_ticklabels(["Low", "High"])
cb.set_label("Feature value", rotation=90, labelpad=8, fontsize=9)
cax.text(1.35, 1.0, "High", rotation=90, va="top", ha="center", fontsize=7)
cax.text(1.35, 0.0, "Low", rotation=90, va="bottom", ha="center", fontsize=7)
cb.ax.tick_params(labelsize=1, length=0)
cb.outline.set_visible(False)

save(fig, "eiar10_shap_beeswarm_dependence")
