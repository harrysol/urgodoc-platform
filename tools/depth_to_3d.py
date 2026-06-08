#!/usr/bin/env python3
"""
Photo -> 3D (single-view 2.5D) using Depth-Anything-V2 (open-source, runs on CPU).
Takes one interior photo, predicts depth, back-projects to a colored 3D point
cloud, exports GLB, and renders a novel viewpoint to prove the 3D-ness.

This is single-view reconstruction: only surfaces visible in the photo, no
backsides. A full walkable interior needs many overlapping photos / a video
(COLMAP, VGGT, or Gaussian Splatting) + a GPU.
"""
import sys, os, numpy as np
from PIL import Image
import torch
from transformers import pipeline
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/photos/img_13.jpg"
OUT = os.path.join(os.path.dirname(__file__), "..", "cad", "interior")
os.makedirs(OUT, exist_ok=True)
tag = os.path.splitext(os.path.basename(SRC))[0]

img = Image.open(SRC).convert("RGB")
W0, H0 = img.size
scale = 760.0 / W0
img = img.resize((int(W0*scale), int(H0*scale)))
W, H = img.size
print(f"image {W}x{H}; loading Depth-Anything-V2-Small ...")

pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf",
                device="cpu")
out = pipe(img)
disp = np.array(out["predicted_depth"].squeeze().cpu().numpy(), dtype=np.float32)
# resize disparity to image size
disp = np.array(Image.fromarray(disp).resize((W, H)))
d = (disp - disp.min()) / (disp.max() - disp.min() + 1e-6)   # 0..1, 1=closest

# save a colored depth map
plt.figure(figsize=(7, H/W*7)); plt.imshow(d, cmap="turbo"); plt.axis("off")
plt.title("Depth-Anything-V2 depth map"); plt.tight_layout()
plt.savefig(os.path.join(OUT, f"{tag}_depth.png"), dpi=130, bbox_inches="tight"); plt.close()

# back-project to 3D
NEAR, FAR = 0.6, 7.0
Z = NEAR + (1.0 - d) * (FAR - NEAR)            # metres (relative scale)
FOV = np.radians(72)
fx = (W/2) / np.tan(FOV/2); fy = fx
cx, cy = W/2, H/2
us, vs = np.meshgrid(np.arange(W), np.arange(H))
st = 2
us, vs, Zs = us[::st, ::st], vs[::st, ::st], Z[::st, ::st]
X = (us - cx) * Zs / fx
Y = -(vs - cy) * Zs / fy
pts = np.stack([X.ravel(), Y.ravel(), -Zs.ravel()], axis=1)
cols = (np.array(img)[::st, ::st].reshape(-1, 3)).astype(np.uint8)
cols = np.concatenate([cols, np.full((len(cols), 1), 255, np.uint8)], axis=1)
print("points:", len(pts))

pc = trimesh.PointCloud(pts, colors=cols)
pc.export(os.path.join(OUT, f"{tag}_pointcloud.glb"))
pc.export(os.path.join(OUT, f"{tag}_pointcloud.ply"))

# novel-view render (two rotated angles) to show parallax / real 3D
idx = np.random.choice(len(pts), min(60000, len(pts)), replace=False)
P, C = pts[idx], np.clip(cols[idx, :3] / 255.0, 0, 1)
fig = plt.figure(figsize=(13, 6.5), facecolor="#111")
for i, (el, az) in enumerate([(6, -55), (14, -85)]):
    ax = fig.add_subplot(1, 2, i+1, projection="3d", facecolor="#111")
    ax.scatter(P[:,0], P[:,2], P[:,1], c=C, s=2.6, marker=".", linewidths=0)
    ax.view_init(elev=el, azim=az); ax.set_axis_off(); ax.set_box_aspect((1,1,0.7))
fig.suptitle(f"{tag}: 3D point cloud reconstructed from ONE photo (two novel viewpoints)",
             color="white", fontsize=12)
fig.savefig(os.path.join(OUT, f"{tag}_novelview.png"), dpi=130, bbox_inches="tight",
            facecolor="#111"); plt.close()
print("wrote depth, glb, ply, novelview ->", OUT)
