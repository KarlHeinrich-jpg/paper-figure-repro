"""Run every figure script and report failures.

    python scripts/run_all.py            # charts + maps
    python scripts/run_all.py --charts   # only statistical figures
    python scripts/run_all.py --maps     # only geodata maps
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEO = os.environ.get("PFR_GEODATA", os.path.join(ROOT, "geodata"))
OUT = os.environ.get("PFR_OUT", os.path.join(ROOT, "outputs"))


def scripts(sub):
    d = os.path.join(HERE, sub)
    return sorted(os.path.join(d, f) for f in os.listdir(d)
                  if f.endswith(".py"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--charts", action="store_true")
    ap.add_argument("--maps", action="store_true")
    args = ap.parse_args()
    run_charts = args.charts or not (args.charts or args.maps)
    run_maps = args.maps or not (args.charts or args.maps)

    os.makedirs(OUT, exist_ok=True)
    env = {**os.environ, "PFR_GEODATA": GEO, "PFR_OUT": OUT}
    todo = []
    if run_charts:
        todo += scripts("charts")
    if run_maps:
        if not os.path.isdir(GEO) or not os.listdir(GEO):
            print("! geodata missing — run: python scripts/download_data.py")
        todo += scripts("maps")

    failed, t0 = [], time.time()
    for p in todo:
        print(f"\n=== {os.path.relpath(p, ROOT)}")
        r = subprocess.run([sys.executable, p], cwd=ROOT, env=env,
                           capture_output=True, text=True)
        tail = ((r.stdout or "").strip().splitlines()[-1:] +
                (r.stderr or "").strip().splitlines()[-1:])
        print(" | ".join(tail) if tail else "(no output)")
        if r.returncode:
            failed.append((p, (r.stderr or "")[-600:]))

    print(f"\n{len(todo) - len(failed)}/{len(todo)} scripts OK in "
          f"{time.time() - t0:.1f}s; outputs -> {OUT}")
    for p, err in failed:
        print(f"[FAIL] {os.path.relpath(p, ROOT)}\n{err}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
