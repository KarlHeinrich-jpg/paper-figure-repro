"""Shared style / helpers for the WeChat paper-figure reproductions.

All data in these scripts is SIMULATED (fixed seed) because none of the source
papers publish their underlying datasets. The reproduction targets the figure
*structure, encoding and layout*, not the original numerical values.
"""
from __future__ import annotations

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Wedge
from matplotlib.path import Path
import matplotlib.patheffects as pe

OUT = os.environ.get("PFR_OUT", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"))
os.makedirs(OUT, exist_ok=True)

# --------------------------------------------------------------------------- #
# global style
# --------------------------------------------------------------------------- #
def setup_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "SimSun", "DejaVu Serif"],
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.linewidth": 0.8,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "axes.spines.top": True,
        "axes.spines.right": True,
        "savefig.dpi": 300,
        "figure.dpi": 150,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
    })


def save(fig, name, also_pdf=True):
    png = os.path.join(OUT, name + ".png")
    fig.savefig(png, dpi=300, pad_inches=0.12)
    if also_pdf:
        fig.savefig(os.path.join(OUT, name + ".pdf"))
    print("saved", png)


def panel_letter(ax, letter, x=-0.14, y=1.06, size=11):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=size,
            fontweight="bold", va="top", ha="right")


# --------------------------------------------------------------------------- #
# palettes used across the source articles
# --------------------------------------------------------------------------- #
PAL = {
    "red_blue": ["#2E5FA3", "#E8416B"],                 # GeoShapley bars
    "warm": ["#9E1C20", "#D73027", "#F46D43", "#FDAE61", "#FEE090"],
    "teal": ["#0B6E5A", "#2A9D8F", "#7FC8B5", "#C7E5D8"],
    "purple": ["#3B1F5C", "#6A3D87", "#B39DDB"],
    "rose": ["#4A1028", "#7B241C", "#A93226", "#CB4335", "#E67E22",
             "#F5B041", "#F7DC6F", "#76D7C4", "#1F618D", "#2874A6"],
    "shap": ["#1E6BD6", "#8E5BC6", "#E0246E"],          # low -> high feature value
}


# --------------------------------------------------------------------------- #
# simulated data generators
# --------------------------------------------------------------------------- #
def simulate_multiclass(n=600, p=20, k=5, seed=0, class_sep=1.0):
    """Latent-factor multiclass data with correlated features."""
    rng = np.random.default_rng(seed)
    cov = 0.55 ** np.abs(np.subtract.outer(np.arange(p), np.arange(p)))
    X = rng.multivariate_normal(np.zeros(p), cov, size=n)
    W = rng.normal(size=(p, k)) * class_sep
    logits = X @ W
    logits += rng.normal(scale=0.6, size=logits.shape)
    y = logits.argmax(axis=1)
    # make classes more balanced
    for c in range(k):
        idx = np.where(y == c)[0]
        need = n // k - len(idx)
        if need > 0:
            pool = np.setdiff1d(np.arange(n), idx)
            pick = rng.choice(pool, size=min(need, len(pool)), replace=False)
            y[pick] = c
    names = [f"F{i+1}" for i in range(p)]
    return X, y, names


def simulate_regression(n=800, p=8, seed=1, noise=0.4):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, p))
    beta = rng.uniform(-1.2, 1.2, size=p)
    y = X @ beta + noise * rng.normal(size=n) + 0.8 * np.sin(X[:, 0] * 1.5)
    return X, y, [f"X{i+1}" for i in range(p)]


# --------------------------------------------------------------------------- #
# chart helpers
# --------------------------------------------------------------------------- #
def box_jitter(ax, data_groups, positions, colors, width=0.42, jitter=0.12,
               point_size=2.2, alpha=0.28, showfliers=False, median_color="#222222"):
    bp = ax.boxplot(data_groups, positions=positions, widths=width, patch_artist=True,
                    showfliers=showfliers,
                    medianprops=dict(color=median_color, lw=1.0),
                    whiskerprops=dict(color="#333333", lw=0.7),
                    capprops=dict(color="#333333", lw=0.7),
                    boxprops=dict(lw=0.7))
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor("white")
        patch.set_edgecolor(c)
        patch.set_alpha(1)
    for grp, pos, c in zip(data_groups, positions, colors):
        xj = pos + np.random.default_rng(42).uniform(-jitter, jitter, size=len(grp))
        ax.scatter(xj, grp, s=point_size, color=c, alpha=alpha, lw=0, zorder=1)
    return bp


def significance_letters(ax, positions, y, letters, size=7, color="#333333"):
    for x, yv, s in zip(positions, y, letters):
        ax.text(x, yv, s, ha="center", va="bottom", fontsize=size, color=color)


def rounded_box(ax, xy, w, h, text, fc="#EAF2FB", ec="#2C5F8A", fs=8,
                lw=0.9, bold=False, radius=0.02, text_color="#111111"):
    x, y = xy
    patch = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.004,rounding_size={radius}",
                           linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=text_color, zorder=3)
    return patch


def arrow(ax, p1, p2, color="#333333", lw=0.9, style="-|>", rad=0.0, ls="-"):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=9,
                        linewidth=lw, color=color, connectionstyle=f"arc3,rad={rad}",
                        linestyle=ls, zorder=1, shrinkA=1, shrinkB=1)
    ax.add_patch(a)
    return a


def add_north_arrow(ax, x=0.08, y=0.92, size=0.05):
    ax.annotate("N", xy=(x, y + size * 1.5), ha="center", va="bottom",
                fontsize=7, fontweight="bold", xycoords="axes fraction")
    ax.annotate("", xy=(x, y + size * 1.2), xytext=(x, y),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0))


def add_scalebar(ax, x0=0.65, y0=0.07, length=0.20, label="0  100 km",
                 color="black", frac=True, height=0.008):
    if frac:
        ax.plot([x0, x0 + length], [y0, y0], color=color, lw=2.2,
                transform=ax.transAxes, solid_capstyle="butt", clip_on=False)
        ax.plot([x0 + length / 2, x0 + length / 2], [y0, y0 + height], color=color,
                lw=1.0, transform=ax.transAxes, clip_on=False)
        ax.text(x0 + length / 2, y0 + height * 1.6, label, ha="center", va="bottom",
                fontsize=6, transform=ax.transAxes)


def light_grid(ax, axis="y", color="#DDDDDD", lw=0.5):
    ax.grid(axis=axis, color=color, lw=lw, zorder=0)
    ax.set_axisbelow(True)


# --------------------------------------------------------------------------- #
# schematic map helpers (used only for "template" outputs)
# --------------------------------------------------------------------------- #
def blob(cx, cy, rng, base_r=0.25, n=64, aspect=1.0, wobble=0.18):
    """Random closed polygon used as a stand-in for administrative boundaries."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = base_r * (1 + wobble * np.sin(3 * t + rng.uniform(0, 6)) +
                  0.5 * wobble * np.sin(7 * t + rng.uniform(0, 6)))
    x = cx + r * np.cos(t) * aspect
    y = cy + r * np.sin(t)
    return np.column_stack([x, y])


def draw_blob(ax, verts, fc="#CFE3D3", ec="#334433", lw=0.7, hatch=None, alpha=1.0, z=1):
    ax.add_patch(plt.Polygon(verts, closed=True, facecolor=fc, edgecolor=ec,
                             lw=lw, hatch=hatch, alpha=alpha, zorder=z))


def raster_polygon(ax, verts, values, cmap, vmin=None, vmax=None, n=28, alpha=1.0):
    """Paint a coarse 'raster' clipped to a polygon (for schematic choropleths)."""
    from matplotlib.path import Path as MplPath
    from matplotlib.patches import PathPatch
    path = MplPath(verts)
    xs = np.linspace(min(v[0] for v in verts), max(v[0] for v in verts), n)
    ys = np.linspace(min(v[1] for v in verts), max(v[1] for v in verts), n)
    xx, yy = np.meshgrid(xs, ys)
    pts = np.column_stack([xx.ravel(), yy.ravel()])
    inside = path.contains_points(pts).reshape(xx.shape)
    mesh = ax.pcolormesh(xx, yy, np.ma.masked_where(~inside, values), cmap=cmap,
                         vmin=vmin, vmax=vmax, shading="nearest", alpha=alpha, zorder=1)
    ax.add_patch(plt.Polygon(verts, closed=True, facecolor="none",
                             edgecolor="#333333", lw=0.8, zorder=3))
    return mesh


# --------------------------------------------------------------------------- #
# real China boundary (local asset) with graceful fallback
# --------------------------------------------------------------------------- #
def china_gdf():
    """Province polygons including Taiwan, Hong Kong and Macao (DataV)."""
    try:
        from geo import china_provinces
        return china_provinces()
    except Exception:
        return None


def china_locator(ax, facecolor="#F4F6F8", edgecolor="#777777", lw=0.5):
    g = china_gdf()
    if g is None:
        return None
    g.plot(ax=ax, facecolor=facecolor, edgecolor=edgecolor, linewidth=lw)
    ax.set_xlim(72, 136)
    ax.set_ylim(16, 55)
    ax.set_aspect("equal")
    ax.axis("off")
    return g
