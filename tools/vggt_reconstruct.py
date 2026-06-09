#!/usr/bin/env python3
"""
Reconstruct the house in 3D from multiple photos using Meta's VGGT
(feed-forward multi-view 3D). CPU mode. Outputs a colored point cloud (GLB/PLY)
and a novel-view render.
"""
import sys, os, numpy as np, torch
from vggt.models.vggt import VGGT
from vggt.utils.load_fn import load_and_preprocess_images

torch.manual_seed(0)
imgs = sys.argv[1:] or [f"/tmp/photos/img_0{n}.jpg" for n in (3,4,5,6)]
OUT = os.path.join(os.path.dirname(__file__), "..", "cad", "vggt"); os.makedirs(OUT, exist_ok=True)
print("images:", imgs)

model = VGGT.from_pretrained("facebook/VGGT-1B").to("cpu").eval()
images = load_and_preprocess_images(imgs).to("cpu")
print("input tensor:", tuple(images.shape))

with torch.no_grad():
    pred = model(images)
print("keys:", list(pred.keys()))

def sq(x):
    x = x.detach().cpu().float().numpy()
    return x[0] if x.ndim in (5,) else x      # drop batch if present

wp = sq(pred["world_points"])                  # [S,H,W,3]
conf = sq(pred["world_points_conf"])           # [S,H,W]
ims = pred["images"].detach().cpu().float().numpy()
ims = ims[0] if ims.ndim == 5 else ims         # [S,3,H,W]
S = wp.shape[0]
pts = wp.reshape(-1, 3)
col = np.transpose(ims, (0, 2, 3, 1)).reshape(-1, 3)
c = conf.reshape(-1)
thr = np.quantile(c, 0.5)                       # keep top 50% confident points
m = c > thr
pts, col = pts[m], np.clip(col[m], 0, 1)
print("kept points:", len(pts))

import trimesh
cols = (np.concatenate([col, np.ones((len(col),1))],1)*255).astype(np.uint8)
pc = trimesh.PointCloud(pts, colors=cols)
pc.export(os.path.join(OUT, "house_vggt.glb"))
pc.export(os.path.join(OUT, "house_vggt.ply"))
print("exported house_vggt.glb / .ply")

# novel-view renders
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
# center + scale
P = pts - pts.mean(0); sc = np.percentile(np.abs(P), 95); P = P/ (sc+1e-6)
idx = np.random.choice(len(P), min(80000, len(P)), replace=False)
fig = plt.figure(figsize=(13,6.5), facecolor="#111")
for i,(el,az) in enumerate([(12,-60),(20,-100)]):
    ax=fig.add_subplot(1,2,i+1,projection="3d",facecolor="#111")
    ax.scatter(P[idx,0],P[idx,2],-P[idx,1],c=col[idx],s=1.5,marker=".",linewidths=0)
    ax.view_init(elev=el,azim=az); ax.set_axis_off(); ax.set_box_aspect((1,1,0.8))
fig.suptitle("VGGT reconstruction from %d photos (novel viewpoints)"%S, color="white")
fig.savefig(os.path.join(OUT,"house_vggt_novelview.png"),dpi=130,bbox_inches="tight",facecolor="#111")
print("wrote novelview")
