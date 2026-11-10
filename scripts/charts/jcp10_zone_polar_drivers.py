"""
art6/07 — JCP 10.1016/j.jclepro.2025.146675 (Li et al., 2025), Fig. 10.
"Changes in the influence intensity of cropland carbon emission drivers across
agricultural zones in China, 2001-2020."

Reproduced: nine polar ("radial year") panels, one per agricultural zone, with
years mapped to angle and standardised driver effects to radius. Non-linear
shapes are simulated.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib.pyplot as plt

from common import setup_style, save

setup_style()
rng = np.random.default_rng(35)

ZONES = [("MLYP", ["CC1", "CI1", "CI4", "NS3", "NH4", "CP1"]),
         ("HP", ["CC1", "CI1", "CI2", "NS1", "CI5", "NG2"]),
         ("YGP", ["CP4", "CP2", "SE2", "SE1", "CC1", "NC2"]),
         ("SC", ["CC1", "CI1", "CI2", "CI4", "CP1"]),
         ("SBSR", ["NG1", "CC1", "CI1", "CP1", "NC4"]),
         ("NCP", ["CC1", "CI1", "CP2", "CI2"]),
         ("NASR", ["CC1", "CI5", "CI2", "CI3", "CP1"]),
         ("LP", ["CC1", "NG1", "CI2", "SE4", "CP4"]),
         ("QTP", ["SE1", "SE2", "SE4", "CI4"]),
]
COLS = ["#4E9F6B", "#E0A33E", "#D6604D", "#7A5195", "#3F8F8C", "#B8860B"]
YEARS = np.arange(2001, 2021)
THETA = np.linspace(0, 2 * np.pi, len(YEARS), endpoint=False)


def smooth_curve(seed, n):
    r = np.random.default_rng(seed)
    v = 0.45 + 0.25 * np.sin(THETA + r.uniform(0, 6)) + 0.12 * np.sin(2 * THETA + r.uniform(0, 6))
    v += r.normal(0, 0.05, len(THETA))
    return np.clip(v, 0.05, 0.95)


fig = plt.figure(figsize=(13, 12.5))
for i, (zone, factors) in enumerate(ZONES):
    ax = fig.add_subplot(3, 3, i + 1, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    for k, f in enumerate(factors):
        v = smooth_curve(10 * i + k, len(THETA))
        ax.plot(THETA, v, color=COLS[k % len(COLS)], lw=1.1, label=f)
        ax.fill(THETA, v, color=COLS[k % len(COLS)], alpha=0.10, lw=0)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8"], fontsize=5)
    ax.set_xticks(THETA[::2])
    ax.set_xticklabels(YEARS[::2], fontsize=5.5, rotation=-30)
    ax.set_title(zone, fontsize=10, fontweight="bold", pad=14)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.30), ncol=2, fontsize=6.2,
              frameon=False, handlelength=1.0, columnspacing=0.7,
              labelspacing=0.2)
    ax.grid(color="#DDDDDD", lw=0.5)
fig.subplots_adjust(hspace=0.52, wspace=0.35, bottom=0.07, top=0.95)
fig.text(0.5, 0.005,
         "Fig. 10. Changes in the influence intensity of cropland carbon emission "
         "drivers across agricultural zones in China, 2001-2020.",
         ha="center", fontsize=8)
save(fig, "jcp10_zone_polar_drivers")
