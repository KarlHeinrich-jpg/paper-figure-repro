"""
art3/18b — EIA Review 10.1016/j.eiar.2026.108409 (Jia et al., 2026)
"Unraveling the 3D structure of urban green spaces: key drivers of cooling
effects across urban heat scenarios"

Reproduced: bivariate Moran scatterplot (Hmax vs p95) with density-coloured
points and a permutation-test histogram (999 permutations).
Maps (a) are not reproducible without the canopy-height rasters.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, save, panel_letter

setup_style()
rng = np.random.default_rng(18)

n = 4200
rho = 0.48
x = rng.normal(size=n)
# spatial lag with imposed bivariate Moran's I ~ rho
noise = rng.normal(size=n)
y = rho * x + np.sqrt(1 - rho ** 2) * noise
y = y + 0.25 * np.sin(2.2 * x)          # nonlinearity to mimic the fan shape
y = (y - y.mean()) / y.std()

fig = plt.figure(figsize=(7.6, 9.4))
gs = fig.add_gridspec(2, 1, height_ratios=[2.25, 1.0], hspace=0.30)

ax = fig.add_subplot(gs[0])
hb = ax.hexbin(x, y, gridsize=55, cmap="viridis", mincnt=1, linewidths=0,
               bins="log")
# regression line + CI
b1, b0 = np.polyfit(x, y, 1)
xs = np.linspace(x.min(), x.max(), 100)
pred = b0 + b1 * xs
resid = y - (b0 + b1 * x)
se = resid.std() * np.sqrt(1 / len(x) + (xs - x.mean()) ** 2 /
                           ((x - x.mean()) ** 2).sum())
ax.plot(xs, pred, color="black", lw=2.0)
ax.fill_between(xs, pred - 1.96 * se, pred + 1.96 * se, color="black", alpha=0.15,
                lw=0)
ax.axhline(0, color="grey", ls="--", lw=0.8)
ax.axvline(0, color="grey", ls="--", lw=0.8)
ax.set_xlim(-3.2, 4.6); ax.set_ylim(-3.6, 4.4)
ax.set_xticks(range(-2, 5))
ax.set_yticks(range(-3, 5))
ax.set_xlabel("Standardized Hmax", fontsize=10)
ax.set_ylabel("Spatial lag of p95", fontsize=10)
ax.set_title("Bivariate moran scatterplot (Hmax vs p95)", fontsize=10.5,
             fontweight="bold", pad=8)
ax.text(0.97, 0.94, "$I_b$=0.48, $p$<0.001", transform=ax.transAxes,
        ha="right", fontsize=9)
panel_letter(ax, "b", x=-0.14, y=1.02)
cb = fig.colorbar(hb, ax=ax, fraction=0.045, pad=0.02)
cb.set_label("Count (log)", fontsize=8)
cb.ax.tick_params(labelsize=7)

# ---- permutation test ----------------------------------------------------- #
ax2 = fig.add_subplot(gs[1])
perm = rng.normal(0, 0.0028, 999)
ax2.hist(perm, bins=36, color="#CFCFCF", edgecolor="none")
ax2.set_xlim(-0.010, 0.010)
ax2.set_xlabel("Bivariate Moran's I (permuted)", fontsize=9)
ax2.set_ylabel("Frequency", fontsize=9)
ax2.set_title("Permutation test for bivariate Moran's I (nsim=999)",
              fontsize=9.5, pad=6)
ax2.text(0.97, 0.78, "Observed I = 0.48\nTwo-sided p = 0.001",
         transform=ax2.transAxes, ha="right", fontsize=8.5)
ax2.tick_params(labelsize=7)
for s in ["top", "right"]:
    ax2.spines[s].set_visible(False)

save(fig, "eiar18_bivariate_moran")
