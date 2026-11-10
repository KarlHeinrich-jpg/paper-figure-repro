"""Real geodata helpers: boundaries, DEM tiles, Esri basemaps, graticules.

All downloads are cached under geodata/tiles/. No proxy is used (the local
proxy in this environment is dead; direct connections to these CDNs work).
"""
from __future__ import annotations

import math
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import numpy as np
from PIL import Image
import geopandas as gpd
from shapely.ops import transform as shp_transform
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEO = os.environ.get("PFR_GEODATA", os.path.join(ROOT, "geodata"))
TILES = os.path.join(GEO, "tiles")
os.makedirs(TILES, exist_ok=True)

R = 6378137.0
WORLD = math.pi * R  # 20037508.34

URL = {
    "dem": "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    "img": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "gray": "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    "street": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    "topo": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
}

_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _get(url, timeout=60, tries=3):
    last = None
    for k in range(tries):
        try:
            with _opener.open(url, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(0.8 * (k + 1))
    raise RuntimeError(f"download failed: {url} ({last})")


def deg2num(lon, lat, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(max(min(lat, 85.05112878), -85.05112878))
    y = (1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n
    return int(x), int(y)


def num2deg(x, y, z):
    n = 2 ** z
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lon, lat


def tile_extent(z, x0, y0, x1, y1):
    """Mercator extent of the tile block x0..x1, y0..y1 (inclusive)."""
    res = 2 * WORLD / (256 * 2 ** z)
    left = -WORLD + x0 * 256 * res
    right = -WORLD + (x1 + 1) * 256 * res
    top = WORLD - y0 * 256 * res
    bottom = WORLD - (y1 + 1) * 256 * res
    return left, bottom, right, top


def _tile_path(kind, z, x, y):
    d = os.path.join(TILES, kind, str(z), str(x))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{y}.png")


def _fetch_tile(kind, z, x, y):
    p = _tile_path(kind, z, x, y)
    if not os.path.exists(p) or os.path.getsize(p) < 200:
        tpl = URL[kind]
        if kind == "dem":
            u = tpl.format(z=z, x=x, y=y)
        else:
            u = tpl.format(z=z, x=x, y=y)
        data = _get(u)
        with open(p, "wb") as f:
            f.write(data)
    return p


def mosaic(kind, z, bbox, workers=10):
    """Return (array, extent) for a lon/lat bbox at zoom z.

    kind: dem | img | gray | street | topo
    returns uint8 RGB (H,W,3) or float32 elevation for dem.
    """
    west, south, east, north = bbox
    x0, y0 = deg2num(west, north, z)
    x1, y1 = deg2num(east, south, z)
    xs = range(x0, x1 + 1)
    ys = range(y0, y1 + 1)
    jobs = [(x, y) for y in ys for x in xs]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        paths = list(ex.map(lambda p: _fetch_tile(kind, z, *p), jobs))
    w, h = len(list(xs)), len(list(ys))
    out = np.zeros((h * 256, w * 256, 3), dtype=np.uint8)
    for (x, y), p in zip(jobs, paths):
        im = Image.open(p).convert("RGB").resize((256, 256))
        arr = np.asarray(im, dtype=np.uint8)
        out[(y - y0) * 256:(y - y0 + 1) * 256,
            (x - x0) * 256:(x - x0 + 1) * 256] = arr
    ext = tile_extent(z, x0, y0, x1, y1)
    if kind == "dem":
        elev = out[..., 0].astype(np.float32) * 256 + out[..., 1].astype(np.float32) + \
               out[..., 2].astype(np.float32) / 256.0 - 32768.0
        return elev, ext
    return out, ext


def crop_to_bbox(arr, ext, bbox):
    """Crop a mosaic to a lon/lat bbox; adjusts extent."""
    tr = Transformer.from_crs(4326, 3857, always_xy=True)
    x0, y0 = tr.transform(bbox[0], bbox[1])
    x1, y1 = tr.transform(bbox[2], bbox[3])
    L, B, Rr, T = ext
    h, w = arr.shape[:2]
    c0 = max(0, int((x0 - L) / (Rr - L) * w))
    c1 = min(w, int((x1 - L) / (Rr - L) * w) + 1)
    r0 = max(0, int((T - y1) / (T - B) * h))
    r1 = min(h, int((T - y0) / (T - B) * h) + 1)
    return arr[r0:r1, c0:c1], (L + (Rr - L) * c0 / w, T - (T - B) * r1 / h,
                               L + (Rr - L) * c1 / w, T - (T - B) * r0 / h)


def hillshade(elev, ext, az=315, alt=45, vert_exag=1.5):
    h, w = elev.shape
    dx = (ext[2] - ext[0]) / w
    dy = (ext[3] - ext[1]) / h
    gy, gx = np.gradient(elev * vert_exag, dy, dx)
    slope = np.pi / 2 - np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    az_r, alt_r = np.radians(az), np.radians(alt)
    hs = np.sin(alt_r) * np.sin(slope) + np.cos(alt_r) * np.cos(slope) * \
         np.cos(az_r - aspect)
    return np.clip(hs, 0, 1)


# --------------------------------------------------------------------------- #
# boundaries
# --------------------------------------------------------------------------- #
_GCJ_A = 6378245.0
_GCJ_EE = 0.00669342162296594323


def _tf_lat(x, y):
    r = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * np.sqrt(np.abs(x))
    r += (20.0 * np.sin(6.0 * x * np.pi) + 20.0 * np.sin(2.0 * x * np.pi)) * 2.0 / 3.0
    r += (20.0 * np.sin(y * np.pi) + 40.0 * np.sin(y / 3.0 * np.pi)) * 2.0 / 3.0
    r += (160.0 * np.sin(y / 12.0 * np.pi) + 320 * np.sin(y * np.pi / 30.0)) * 2.0 / 3.0
    return r


def _tf_lon(x, y):
    r = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * np.sqrt(np.abs(x))
    r += (20.0 * np.sin(6.0 * x * np.pi) + 20.0 * np.sin(2.0 * x * np.pi)) * 2.0 / 3.0
    r += (20.0 * np.sin(x * np.pi) + 40.0 * np.sin(x / 3.0 * np.pi)) * 2.0 / 3.0
    r += (150.0 * np.sin(x / 12.0 * np.pi) + 300.0 * np.sin(x / 30.0 * np.pi)) * 2.0 / 3.0
    return r


def wgs2gcj(lon, lat):
    dlat = _tf_lat(lon - 105.0, lat - 35.0)
    dlon = _tf_lon(lon - 105.0, lat - 35.0)
    rad = math.radians(lat)
    magic = 1 - _GCJ_EE * math.sin(rad) ** 2
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((_GCJ_A * (1 - _GCJ_EE)) / (magic * sqrtmagic) * math.pi)
    dlon = (dlon * 180.0) / (_GCJ_A / sqrtmagic * math.cos(rad) * math.pi)
    return lon + dlon, lat + dlat


def gcj2wgs(lon, lat):
    wlon, wlat = lon, lat
    for _ in range(6):
        glon, glat = wgs2gcj(wlon, wlat)
        wlon += lon - glon
        wlat += lat - glat
    return wlon, wlat


def datav(adcode, to_wgs=True):
    p = os.path.join(GEO, f"datav_{adcode}.json")
    if not os.path.exists(p):
        data = _get(f"https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json")
        with open(p, "wb") as f:
            f.write(data)
    g = gpd.read_file(p).to_crs(4326)
    if to_wgs:
        g["geometry"] = g.geometry.apply(
            lambda geom: shp_transform(lambda x, y, z=None: gcj2wgs(x, y), geom))
    return g


def gadm(level=3, to_wgs=True):
    p = os.path.join(GEO, f"gadm41_CHN_{level}.json")
    if not os.path.exists(p):
        data = _get(f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_CHN_{level}.json",
                    timeout=180)
        with open(p, "wb") as f:
            f.write(data)
    return gpd.read_file(p).to_crs(4326)


def to3857(g):
    return g.to_crs(3857)


# --------------------------------------------------------------------------- #
# cartography helpers
# --------------------------------------------------------------------------- #
def graticule(ax, bbox, step, color="#666666", lw=0.45, ls="--", labels=True,
              fontsize=7, sides=("top", "right")):
    tr = Transformer.from_crs(4326, 3857, always_xy=True)
    west, south, east, north = bbox
    lons = np.arange(math.ceil(west / step) * step, east + 1e-9, step)
    lats = np.arange(math.ceil(south / step) * step, north + 1e-9, step)
    for lon in lons:
        ys = np.linspace(south, north, 60)
        xs = np.full_like(ys, lon)
        X, Y = tr.transform(xs, ys)
        ax.plot(X, Y, color=color, lw=lw, ls=ls, zorder=6, alpha=0.8)
        if labels and "top" in sides:
            xt, yt = tr.transform(lon, north)
            ax.text(xt, yt, f"{lon:.2f}°E", ha="center", va="bottom", fontsize=fontsize,
                    zorder=8)
    for lat in lats:
        xs = np.linspace(west, east, 60)
        ys = np.full_like(xs, lat)
        X, Y = tr.transform(xs, ys)
        ax.plot(X, Y, color=color, lw=lw, ls=ls, zorder=6, alpha=0.8)
        if labels and "right" in sides:
            xt, yt = tr.transform(east, lat)
            ax.text(xt, yt, f"{lat:.2f}°N", ha="left", va="center", fontsize=fontsize,
                    rotation=90, zorder=8)


def north_arrow(ax, x=0.06, y=0.90, size=0.055):
    ax.annotate("N", xy=(x, y + size * 1.7), xycoords="axes fraction",
                ha="center", va="bottom", fontsize=10, fontweight="bold", zorder=20)
    ax.annotate("", xy=(x, y + size * 1.35), xytext=(x, y), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.2), zorder=20)


def scalebar(ax, extent, km=18, x=0.68, y=0.06, color="black", label=None):
    """Scale bar for a Mercator (metre) axes."""
    L, B, Rr, T = extent
    length = km * 1000.0
    x0 = L + (Rr - L) * x
    y0 = B + (T - B) * y
    ax.plot([x0, x0 + length], [y0, y0], color=color, lw=3,
            solid_capstyle="butt", zorder=25, clip_on=False)
    for frac in (0, 0.5, 1.0):
        ax.plot([x0 + length * frac] * 2, [y0, y0 + (T - B) * 0.008],
                color=color, lw=1, zorder=25, clip_on=False)
    ax.text(x0, y0 + (T - B) * 0.014, "0", ha="center", va="bottom",
            fontsize=6.5, zorder=25, color=color)
    ax.text(x0 + length / 2, y0 + (T - B) * 0.014, f"{km/2:.0f}",
            ha="center", va="bottom", fontsize=6.5, zorder=25, color=color)
    ax.text(x0 + length, y0 + (T - B) * 0.014, f"{km:g} km", ha="left",
            va="bottom", fontsize=6.5, zorder=25, color=color)


def scalebar_deg(ax, bbox, km=2000, x=0.10, y=0.08, color="black"):
    """Approximate scale bar for a lon/lat axes (at the bbox mid-latitude)."""
    W, S, E, N = bbox
    midlat = math.radians((S + N) / 2)
    deg = km / (111.32 * math.cos(midlat))
    x0 = W + (E - W) * x
    y0 = S + (N - S) * y
    ax.plot([x0, x0 + deg], [y0, y0], color=color, lw=3, solid_capstyle="butt",
            zorder=25, clip_on=False)
    for frac in (0, 0.5, 1.0):
        ax.plot([x0 + deg * frac] * 2, [y0, y0 + (N - S) * 0.008],
                color=color, lw=1, zorder=25, clip_on=False)
    for frac, txt, ha in [(0, "0", "center"), (0.5, f"{km/2:.0f}", "center"),
                          (1.0, f"{km:g} km", "left")]:
        ax.text(x0 + deg * frac, y0 + (N - S) * 0.014, txt, ha=ha, va="bottom",
                fontsize=6.5, zorder=25)


def taiwan():
    """Taiwan province polygon (DataV 710000), WGS84."""
    g = datav("100000")
    tw = g[g["name"].astype(str).str.contains("台湾")]
    return tw.to_crs(4326)


def china_provinces():
    """All DataV province polygons, including Taiwan / HK / Macao."""
    g = datav("100000")
    g = g[g["name"].astype(str).str.strip().ne("") & g.geometry.notna()]
    return g.to_crs(4326)
