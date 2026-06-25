#!/usr/bin/env python3
"""Minimal loader for one sequence of the bed-adhesion failure-onset dataset.

Usage:
    python scripts/load_sample.py data/P1/BlackMoai
"""
import os, sys, json, glob
import numpy as np
from PIL import Image


def load_sequence(seqdir):
    """Return a dict with the prompt, the onset label, and the GT masks."""
    bbox = json.load(open(os.path.join(seqdir, "bbox.json")))["bbox"]  # [x1,y1,x2,y2]
    onset = int(open(os.path.join(seqdir, "onset.txt")).read().strip())
    points = None
    pf = os.path.join(seqdir, "points.json")
    if os.path.exists(pf):
        points = json.load(open(pf))  # {"pos": [[x,y],...], "neg": [...]}

    masks = {}
    for p in sorted(glob.glob(os.path.join(seqdir, "masks", "frame_*.png"))):
        if p.endswith("_overlay.png"):
            continue
        fidx = int(os.path.basename(p)[6:-4])
        masks[fidx] = np.asarray(Image.open(p)) > 127  # bool HxW, True = object
        # equivalently: np.load(p[:-4] + "_mask.npz")["mask"]
    return {"bbox": bbox, "points": points, "onset": onset, "masks": masks}


if __name__ == "__main__":
    seqdir = sys.argv[1] if len(sys.argv) > 1 else "data/P1/BlackMoai"
    s = load_sequence(seqdir)
    print(f"sequence : {seqdir}")
    print(f"bbox     : {s['bbox']}")
    print(f"points   : {s['points']}")
    print(f"onset    : frame {s['onset']}")
    print(f"GT masks : {len(s['masks'])} frames -> {sorted(s['masks'])}")
    f0 = sorted(s["masks"])[0]
    m = s["masks"][f0]
    print(f"mask[{f0}] : shape={m.shape} object_px={int(m.sum())}")
