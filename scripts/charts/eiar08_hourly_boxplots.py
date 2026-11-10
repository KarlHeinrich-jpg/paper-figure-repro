"""
art3/08c + art3/09c — EIA Review 10.1016/j.eiar.2026.108393 (Song et al., 2026)
"Toward equitable air environment: Hourly spatiotemporal hotspot evolution and
impact mechanisms of urban PM2.5 exposure"

Reproduced: hourly box-and-whisker + mean-line panels for (a) PM2.5 concentration
vs resident population and (b) PM2.5 exposure risk. Maps above them (art3/08a-b,
09a-b) are not reproduced (need gridded PM2.5 / population rasters).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, save, panel_letter, light_grid, box_jitter

setup_style()
rng = np.random.default_rng(21)
H = np.arange(24)


def hourly_box(base, amp, spread, phase=8, n=420):
    mean = base + amp * np.exp(-((H - phase) ** 2) / 20) + 0.08 * np.sin(H / 2.4)
    data = [rng.normal(mean[h], spread * (0.85 + 0.3 * rng.random()), n) for h in H]
    return mean, data


# panel a: concentration (blue-grey) and population (teal)
mean_c, data_c = hourly_box(0.52, 0.22, 0.10, phase=8)
mean_p, data_p = hourly_box(0.48, 0.12, 0.11, phase=9)

fig, axes = plt.subplots(1, 2, figsize=(15, 5.4), gridspec_kw=dict(wspace=0.22))

ax = axes[0]
bp1 = ax.boxplot(data_c, positions=H - 0.20, widths=0.34, patch_artist=True,
                 showfliers=False, manage_ticks=False, medianprops=dict(color="#333333", lw=0.8),
                 whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7))
for b in bp1["boxes"]:
    b.set(facecolor="#9FB1C9", edgecolor="#5B6F8A", alpha=0.85)
bp2 = ax.boxplot(data_p, positions=H + 0.20, widths=0.34, patch_artist=True,
                 showfliers=False, manage_ticks=False, medianprops=dict(color="#333333", lw=0.8),
                 whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7))
for b in bp2["boxes"]:
    b.set(facecolor="#9FD3C7", edgecolor="#2A9D8F", alpha=0.85)
ax.plot(H, mean_c, color="#2E4D6B", lw=1.8, marker="o", ms=4,
        label=r"Mean PM$_{2.5}$ concentration")
ax.plot(H, mean_p, color="#1B7F6B", lw=1.8, marker="s", ms=4,
        label="Mean resident population")
ax.set_xlim(-0.8, 23.8)
ax.set_ylim(0, 1.05)
ax.set_xticks(H)
ax.set_xlabel("Hour of Day", fontsize=10)
ax.set_ylabel("Normalized Value", fontsize=10)
ax.legend(loc="upper right", fontsize=8, frameon=False)
panel_letter(ax, "a", x=-0.06, y=1.05)
light_grid(ax, "y", "#E5E5E5")

# panel b: exposure risk (single teal boxes)
mean_r, data_r = hourly_box(0.33, 0.06, 0.06, phase=12)
ax = axes[1]
bp = ax.boxplot(data_r, positions=H, widths=0.55, patch_artist=True,
                showfliers=False, manage_ticks=False, medianprops=dict(color="#333333", lw=0.8),
                whiskerprops=dict(lw=0.7), capprops=dict(lw=0.7))
for b in bp["boxes"]:
    b.set(facecolor="#9FD3C7", edgecolor="#2A9D8F", alpha=0.8)
ax.plot(H, mean_r, color="#1B7F6B", lw=1.8, marker="o", ms=4,
        label=r"Mean PM$_{2.5}$ exposure risk")
ax.set_xlim(-0.8, 23.8)
ax.set_ylim(0, 0.85)
ax.set_xticks(H)
ax.set_xlabel("Hour of Day", fontsize=10)
ax.set_ylabel("Normalized Value", fontsize=10)
ax.legend(loc="upper right", fontsize=8, frameon=False)
ax.text(0.015, 0.97, "PM$_{2.5}$ exposure risk", transform=ax.transAxes,
        fontsize=9, va="top", fontweight="bold")
panel_letter(ax, "b", x=-0.08, y=1.05)
light_grid(ax, "y", "#E5E5E5")

save(fig, "eiar08_hourly_boxplots")
