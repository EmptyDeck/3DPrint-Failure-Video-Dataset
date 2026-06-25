# Bed-Adhesion Failure-Onset Dataset for FDM 3D Printing

A benchmark of **30 real FDM 3D-printing failure sequences** for **streaming
failure-onset detection** (change-point detection) and **prompted object
segmentation**. Each sequence is a bed-synchronized timelapse in which a normally
printing part stays nearly stationary in-frame; the first frame at which the part
visibly moves is the **failure onset** — the target change-point.

This repository contains the **annotations, ground-truth masks, and metadata**
needed to reproduce our experiments, plus the single source frame for each
annotated mask (for inspection). **Full raw videos are *not* included** (tens of GB
each); obtain them from the external hosts listed in
[`metadata/sequences.csv`](metadata/sequences.csv) (see
[Obtaining the videos and frames](#obtaining-the-videos-and-frames)).

Every file is small — the largest single file is ~1.7 MB, well under GitHub's
100 MB per-file limit.

---

## Dataset at a glance

| Property | Value |
|---|---|
| Sequences (total) | **30** |
| &nbsp;&nbsp;Environment **P1** (printer 1) | 20 — 1024×768, 1 fps, bed-mounted |
| &nbsp;&nbsp;Environment **P2** (printer 2) | 10 — 1920×1080, 1 fps, bed-mounted |
| Videos | 30 (one per sequence, externally hosted) |
| Total frames (sum over sequences) | **261,583** (P1 149,125 · P2 112,458) |
| Onset labels (`t_gt`) | 30 (one integer per sequence) |
| Bounding-box prompts | 30 |
| Point prompts | 30 |
| Ground-truth masks | **300** (10 per sequence; PNG + NPZ) |
| Onset range (frames) | 49 → 15,161 (median 4,742) |
| Early-failure sequences (onset < 700) | 7 |

The two environments differ in **printer, camera, resolution, and capture axis**.
This separation is deliberate: a configuration tuned on one environment is
cross-applied to the other to measure **environment transfer**.

---

## Repository structure

```
dataset_release/
├── README.md
├── metadata/
│   └── sequences.csv          # one row per sequence: env, resolution, fps,
│                              # n_frames, onset_frame, n_normal_baseline,
│                              # n_gt_masks, video_url
├── scripts/
│   └── load_sample.py         # minimal loader: prompt + onset + GT masks
└── data/
    ├── P1/<sequence>/         # 20 sequences, 1024×768
    └── P2/<sequence>/         # 10 sequences, 1920×1080
        ├── bbox.json          # {"bbox": [x1, y1, x2, y2]}  float pixel coords
        ├── points.json        # {"pos": [[x,y],...], "neg": [[x,y],...]}
        ├── onset.txt          # single integer: ground-truth onset frame t_gt
        └── masks/             # 10 annotated frames, evenly spaced over [0, ~onset]
            ├── frame_XXXXXX.png         # binary GT mask, 255=object 0=background
            ├── frame_XXXXXX_mask.npz    # same mask as bool array: np.load(f)['mask']
            ├── frame_XXXXXX_overlay.png # mask overlaid on the source frame (viz)
            ├── frame_XXXXXX_frame.jpg   # the source video frame at this index
            └── masks_info.json          # frame_indices, n_masks, resolution, files
```

> **Files per annotated frame.** `frame_XXXXXX.png` and `frame_XXXXXX_mask.npz`
> hold the *same* GT mask in two forms (1-bit PNG and a lossless boolean array).
> `frame_XXXXXX_overlay.png` and `frame_XXXXXX_frame.jpg` are convenience copies of
> the visualization and the single source frame at that index — they let you inspect
> the masks without downloading the full video. Mask PNG/NPZ and source frames exist
> for all 300 annotated frames; overlays exist for 207 of them.

### File reference

| File | Purpose |
|---|---|
| `bbox.json` | The **single prompt**: one bounding box on the printed part at frame 0 — the only required user input. `[x1, y1, x2, y2]` in pixel coordinates. |
| `points.json` | Alternative **point prompt** (positive/negative click points). Used only in the bbox-vs-points ablation. |
| `onset.txt` | **Ground-truth failure-onset frame `t_gt`** — the change-point label. Frames `[0, t_gt)` are the *normal* baseline. |
| `masks/frame_XXXXXX.png` | **Ground-truth object mask** at frame `XXXXXX`, full native resolution, `uint8` PNG with `255 = object`, `0 = background`. |
| `masks/frame_XXXXXX_mask.npz` | The same mask as a lossless boolean array. Load with `np.load(path)["mask"]` → `bool` array `(H, W)`. |
| `masks/frame_XXXXXX_overlay.png` | The GT mask overlaid on the source frame, for visual inspection. |
| `masks/frame_XXXXXX_frame.jpg` | The single source video frame at index `XXXXXX` (the frame the mask annotates). |
| `masks/masks_info.json` | Annotated `frame_indices`, mask count, resolution, and a per-frame file legend. |
| `metadata/sequences.csv` | Per-sequence metadata and statistics, plus the `video_url` column for external video sources. |

> **Note on segmentation eval.** The 10th mask is at frame 0 (the prompt frame).
> Our 9-frame segmentation evaluation drops frame 0 and scores the remaining 9.

---

## What is *not* included (and why)

| Excluded | Reason | Where to get it |
|---|---|---|
| Full timelapse videos (`*_timelapse.mp4`) | 0.07–13 GB each, ~120 GB total | External hosts, `metadata/sequences.csv → video_url` |
| All non-annotated frames | 261k frames; only the 300 annotated frames are shipped | Decode the video at 1 fps (see below) |
| Baseline derived caches (`delta_cache/`, per-config `*_masks.npz`, `.color_cache_hue.npz`) | Pipeline by-products, reproducible from masks + video | Recompute with the baseline pipeline |

---

## Obtaining the videos and frames

1. Open [`metadata/sequences.csv`](metadata/sequences.csv) and read the `video_url`
   column for the sequence you want (videos are hosted externally, e.g. on YouTube).
2. Download the video for each sequence.
3. The videos are **1 fps**, so **frame index = timestamp in seconds**. Extract
   frames with `ffmpeg`:

   ```bash
   # all frames -> frame_000000.jpg, frame_000001.jpg, ...
   ffmpeg -i <sequence>_timelapse.mp4 -vsync 0 -start_number 0 frame_%06d.jpg

   # or only the frames that have a GT mask (indices in masks/masks_info.json),
   # e.g. frame 789 at 1 fps:
   ffmpeg -i <video>.mp4 -vf "select=eq(n\,789)" -vframes 1 frame_000789.jpg
   ```

A GT mask `masks/frame_000789.png` aligns pixel-exact with the decoded video frame
789 at native resolution. The shipped `masks/frame_000789_frame.jpg` is that exact
frame, so you can sanity-check alignment before downloading the full video.

---

## Quick start

```bash
python scripts/load_sample.py data/P1/BlackMoai
```

```python
from scripts.load_sample import load_sequence
s = load_sequence("data/P2/P2RedVase")
s["bbox"]    # [x1, y1, x2, y2] prompt at frame 0
s["onset"]   # ground-truth onset frame (int)
s["masks"]   # {frame_index: bool HxW array, True = object}

# masks can also be read directly from the lossless .npz:
import numpy as np
m = np.load("data/P2/P2RedVase/masks/frame_000000_mask.npz")["mask"]  # bool (H, W)
```

---

## Tasks and evaluation protocol

- **Streaming failure-onset detection (primary).** Feed frames `0, 1, 2, …` one at
  a time; a detector may use only the past (causal). Score latency-aware against
  `t_gt`: reward firing at `t_gt`, penalize alarms before `t_gt` (false positives)
  and a never-fire miss.
- **Cross-environment transfer.** Tune on P1 and test on P2 (and vice versa) — the
  two environments differ in printer, camera, resolution, and axis.
- **Prompted segmentation quality.** Using the frame-0 `bbox`/`points` prompt,
  produce masks and compare against the 9 GT masks (frame 0 excluded) per sequence.
- **Early-failure stress.** 7 sequences have onset < 700 (very short normal
  baseline), stressing detectors that need warm-up statistics.

---

## Per-sequence statistics

See [`metadata/sequences.csv`](metadata/sequences.csv) for the complete table.
Columns: `sequence, env, resolution, fps, n_frames, onset_frame,
n_normal_baseline, n_gt_masks, video_url`.

| Env | #seq | Resolution | FPS | Frames | GT masks |
|---|---:|---|---:|---:|---:|
| P1 | 20 | 1024×768 | 1 | 149,125 | 200 |
| P2 | 10 | 1920×1080 | 1 | 112,458 | 100 |
| **All** | **30** | — | 1 | **261,583** | **300** |

---

## License & citation

Annotations and metadata in this repository are released for research use. Video
content is hosted externally under its own terms. _Citation / license details to
be added on publication._
