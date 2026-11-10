"""Download every real dataset used by the reproduction scripts.

Usage:
    python scripts/download_data.py              # everything (~450 MB)
    python scripts/download_data.py --minimal    # boundaries + PM2.5 + population
    python scripts/download_data.py --landuse    # add ESA WorldCover tiles

Files are cached in <repo>/geodata/ and skipped when already present.
Set PFR_GEODATA to use a different directory.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEO = os.environ.get("PFR_GEODATA", os.path.join(ROOT, "geodata"))
os.makedirs(GEO, exist_ok=True)

OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA = {"User-Agent": "paper-figure-repro/1.0 (research; contact via GitHub)"}

DATAV = ["100000", "110000", "230000", "230100", "310000", "320000",
         "330000", "410000", "410100", "430000", "610000", "620000", "654000"]

FILES = [
    # (filename, url, minimum MB)
    ("gadm41_CHN_1.json",
     "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_CHN_1.json", 3),
    ("gadm41_CHN_3.json",
     "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_CHN_3.json", 8),
    ("CHAP_PM2.5_Y1K_2020_V4.nc",
     "https://zenodo.org/records/6398971/files/CHAP_PM2.5_Y1K_2020_V4.nc?download=1", 5),
    ("worldpop_2020_1km.tif",
     "https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/2020/CHN/"
     "chn_ppp_2020_1km_Aggregated.tif", 40),
    ("soilgrids_ph_1km.tif",
     "https://files.isric.org/soilgrids/latest/data_aggregated/1000m/phh2o/"
     "phh2o_0-5cm_mean_1000.tif", 60),
    ("worldclim_prec.zip",
     "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_prec.zip", 6),
]
LANDUSE = [
    ("worldcover_N33E111.tif",
     "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
     "ESA_WorldCover_10m_2021_v200_N33E111_Map.tif", 100),
    ("worldcover_N30E120.tif",
     "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
     "ESA_WorldCover_10m_2021_v200_N30E120_Map.tif", 70),
    ("worldcover_N45E126.tif",
     "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
     "ESA_WorldCover_10m_2021_v200_N45E126_Map.tif", 40),
]


def download(name, url, min_mb):
    dst = os.path.join(GEO, name)
    need = min_mb * 1024 * 1024
    if os.path.exists(dst) and os.path.getsize(dst) > need:
        print(f"[skip] {name} ({os.path.getsize(dst)/1e6:.1f} MB)")
        return True
    tmp = dst + ".part"
    print(f"[get ] {name}")
    try:
        req = urllib.request.Request(url, headers=UA)
        with OPENER.open(req, timeout=300) as r, open(tmp, "wb") as f:
            total = int(r.headers.get("Content-Length") or 0)
            got, t0 = 0, time.time()
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
                got += len(chunk)
                if total and got % (8 << 20) < (1 << 20):
                    print(f"       {got/1e6:6.1f}/{total/1e6:.1f} MB "
                          f"({got/max(1e-6, time.time()-t0)/1e6:.1f} MB/s)")
        if os.path.getsize(tmp) < need:
            raise RuntimeError(f"incomplete ({os.path.getsize(tmp)/1e6:.1f} MB)")
        os.replace(tmp, dst)
        print(f"[ ok ] {name} ({os.path.getsize(dst)/1e6:.1f} MB)")
        return True
    except Exception as e:  # noqa: BLE001
        if os.path.exists(tmp):
            os.remove(tmp)
        print(f"[fail] {name}: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minimal", action="store_true",
                    help="boundaries + PM2.5 + population only")
    ap.add_argument("--landuse", action="store_true",
                    help="also download the three WorldCover tiles")
    args = ap.parse_args()

    ok = True
    for code in DATAV:
        ok &= download(f"datav_{code}.json",
                       f"https://geo.datav.aliyun.com/areas_v3/bound/{code}_full.json", 0.01)
    files = FILES if args.minimal else FILES + LANDUSE
    for name, url, mb in files:
        ok &= download(name, url, mb)
    if args.landuse and args.minimal:
        for name, url, mb in LANDUSE:
            ok &= download(name, url, mb)

    print("\nDEM tiles (AWS terrarium) are downloaded on demand by scripts/geo.py.")
    print("Output directory:", os.path.join(ROOT, "outputs"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
