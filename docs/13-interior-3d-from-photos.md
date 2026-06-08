# 13 — Interior 3D from Photos

Two ways to get interior 3D from photos. We have **36 listing photos**, so here's
what's actually possible with them vs. what needs a real capture.

## What we DID here — single-photo 3D (Depth-Anything-V2)

Open-source monocular depth (**[Depth-Anything-V2](https://github.com/DepthAnything/Depth-Anything-V2)**,
runs on CPU) → predicts depth → back-projects to a **colored 3D point cloud**.
Done on two of your real photos:

| Room | Files in `cad/interior/` |
|------|--------------------------|
| Kitchen (img_13) | `img_13_pointcloud.glb` / `.ply`, `img_13_depth.png`, `img_13_novelview.png` |
| Living room (img_10) | `img_10_pointcloud.glb` / `.ply`, `img_10_depth.png`, `img_10_novelview.png` |

~96k 3D points each. Open the `.glb`/`.ply` in any 3D viewer
([gltf-viewer](https://gltf-viewer.donmccurdy.com), MeshLab, Blender, CloudCompare)
and orbit it. Regenerate: `python3 tools/depth_to_3d.py /path/to/photo.jpg`.

**Honest limit:** this is **single-view 2.5D** — only the surfaces visible in that
one photo, no backsides, relative (not metric) scale. Great for a 3D impression of
a room; not a measured model.

## What it would take for a FULL walkable interior

A coherent, walk-through interior 3D needs **many overlapping photos or a video
walkthrough** — not single listing shots (those don't overlap, so they can't be
stitched). The real tools:

| Tool / repo | Notes |
|-------------|-------|
| **[COLMAP](https://github.com/colmap/colmap)** | Classic photogrammetry (SfM+MVS). Needs 100s of overlapping photos + GPU. |
| **[VGGT](https://github.com/facebookresearch/vggt)** / **[DUSt3R](https://github.com/naver/dust3r)** | Feed-forward dense 3D from images; SOTA, needs GPU. |
| **[gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting)** | Photoreal, explorable 3D scenes; needs COLMAP poses + GPU. |
| **Phone apps: Polycam / Luma / Scaniverse / KIRI** | Easiest by far — someone at the house records a walkthrough; get a full 3D scan in minutes. No code. |

> This Claude sandbox has **no GPU**, and listing photos lack the overlap these
> need — so a full interior scan must be captured at the house (a 2-minute phone
> video through Polycam/Luma is the realistic path), then reconstructed.

## Bottom line
- **From the photos we have:** room-by-room single-view 3D point clouds ✅ (done).
- **For a full walkable interior:** capture a video walkthrough at the house →
  run Polycam/Luma (easy) or COLMAP/Gaussian-Splatting on a GPU (advanced).
