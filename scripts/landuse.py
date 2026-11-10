"""WorldCover 10 m -> thematic land-use layer for a city bbox."""
import os
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask as rio_mask
from matplotlib.colors import ListedColormap

GEO = os.environ.get("PFR_GEODATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "geodata"))
TILES = {
    "shanghai": "worldcover_N30E120.tif",
    "zhengzhou": "worldcover_N33E111.tif",
    "harbin": "worldcover_N45E126.tif",
}
# original classes -> colours (Shanghai / Zhengzhou figures)
COLORS = {
    10: "#2E6B2E",   # Tree cover -> woodland
    20: "#7FAF5A",   # Shrub
    30: "#B7D9A0",   # Grassland
    40: "#F2E394",   # Cropland -> arable
    50: "#F2B6B0",   # Built-up -> construction
    60: "#E8E2C8",   # Bare -> unused
    70: "#FFFFFF",
    80: "#9CCFE8",   # Water
    90: "#7FC8C0",   # Wetland
    95: "#5FAF8A",
    100: "#A8C4A0",
}
NAMES = {10: "Woodland", 30: "Grassland", 40: "Arable land", 50: "Construction land",
         60: "Unused land", 80: "Water body", 90: "Wetland"}


def read_landuse(key, bbox, geom=None, out_px=1600):
    path = os.path.join(GEO, TILES[key])
    with rasterio.open(path) as src:
        win = rasterio.windows.from_bounds(bbox[0], bbox[1], bbox[2], bbox[3],
                                           transform=src.transform)
        h = int(out_px * (bbox[3] - bbox[1]) / (bbox[2] - bbox[0]))
        arr = src.read(1, window=win, out_shape=(h, out_px),
                       resampling=Resampling.nearest)
    if geom is not None:
        from rasterio.features import geometry_mask
        from rasterio.transform import from_bounds
        tr = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], out_px, h)
        m = geometry_mask([geom], out_shape=arr.shape, transform=tr, invert=True)
        arr = np.where(m, arr, 0)
    return arr, (bbox[0], bbox[2], bbox[1], bbox[3])


def cmap():
    vals = sorted(COLORS)
    cm = ListedColormap([COLORS[v] for v in vals])
    cm.set_bad((1, 1, 1, 0))
    return cm, vals, {v: i for i, v in enumerate(vals)}
