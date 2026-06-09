#!/usr/bin/env python3
"""
Combine the REAL house (VGGT photo-reconstruction point cloud) with the PROPOSED
second floor (clean geometry) in one model. Outputs a combined GLB + renders that
show the addition on the actual house.
"""
import numpy as np, trimesh, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "cad", "combined"); os.makedirs(OUT, exist_ok=True)
pc = trimesh.load("cad/vggt/house_vggt.ply")
P = np.asarray(pc.vertices); C = np.asarray(pc.colors)[:, :3] / 255.0

# orient to Z-up (VGGT up ~ -Y): world = (x, z, -y)
W = np.column_stack([P[:, 0], P[:, 2], -P[:, 1]]).astype(float)
ctr = np.median(W, 0); d = np.linalg.norm(W - ctr, axis=1)
keep = d < np.quantile(d, 0.92); W, C = W[keep], C[keep]      # trim outliers
W -= [W[:, 0].mean(), W[:, 1].mean(), W[:, 2].min()]          # ground at z=0, centered

# building extent (upper points = walls/roof, exclude ground plane)
ztop = np.percentile(W[:, 2], 97); zg = np.percentile(W[:, 2], 3)
bh = ztop - zg
bld = W[W[:, 2] > zg + 0.35 * bh]
bx0, bx1 = np.percentile(bld[:, 0], [8, 92])
by0, by1 = np.percentile(bld[:, 1], [8, 92])
print("building footprint (model units): x %.1f..%.1f  y %.1f..%.1f  roof z=%.1f" % (bx0, bx1, by0, by1, ztop))

# proposed second floor: stepped-back box on the roof + a terrace, scaled to building
ix, iy = (bx1 - bx0) * 0.16, (by1 - by0) * 0.16
sx0, sx1, sy0, sy1 = bx0 + ix, bx1 - ix, by0 + iy, by1 - iy
sh = bh * 0.85
def boxmesh(x0, x1, y0, y1, z0, z1, color):
    b = trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])
    b.visual.vertex_colors = np.tile((np.array(color + [255])).astype(np.uint8), (len(b.vertices), 1))
    return b
second = boxmesh(sx0, sx1, sy0, sy1, ztop, ztop + sh, [235, 235, 240])
terrace = boxmesh(sx0, sx1, by1, by1 + (by1 - by0) * 0.18, ztop, ztop + sh * 0.05, [200, 160, 110])

# combined GLB (real cloud + proposed geometry)
scene = trimesh.Scene()
cloud_cols = (np.concatenate([C, np.ones((len(C), 1))], 1) * 255).astype(np.uint8)
scene.add_geometry(trimesh.PointCloud(W, colors=cloud_cols), node_name="existing_house_real")
scene.add_geometry(second, node_name="proposed_second_floor")
scene.add_geometry(terrace, node_name="proposed_bay_terrace")
scene.export(os.path.join(OUT, "house_plus_second_floor.glb"))
print("exported house_plus_second_floor.glb")

# render 3 angles: real house (photo colors) + proposed floor (light, edged)
idx = np.random.choice(len(W), min(110000, len(W)), replace=False)
def draw_box(ax, x0, x1, y0, y1, z0, z1, col, a):
    v = np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]])
    fs = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    pc3 = Poly3DCollection([v[f] for f in fs], alpha=a, facecolor=col, edgecolor="#3a6ea5", linewidths=1.2)
    ax.add_collection3d(pc3)
fig = plt.figure(figsize=(16, 5.6), facecolor="#0d0d0f")
for i, (el, az) in enumerate([(12, -58), (18, -95), (22, -135)]):
    ax = fig.add_subplot(1, 3, i+1, projection="3d", facecolor="#0d0d0f")
    ax.scatter(W[idx,0], W[idx,1], W[idx,2], c=np.clip(C[idx]**0.65,0,1), s=2.0, marker=".", linewidths=0)
    draw_box(ax, sx0,sx1,sy0,sy1, ztop, ztop+sh, "#dfe6f0", 0.45)
    ax.view_init(elev=el, azim=az); ax.set_axis_off(); ax.set_box_aspect((1,1,0.8))
fig.suptitle("8220 Hawthorne - REAL house (from your photos) + PROPOSED second floor", color="white", fontsize=13)
fig.savefig(os.path.join(OUT, "house_plus_second_floor.png"), dpi=130, bbox_inches="tight", facecolor="#0d0d0f")
print("wrote render")
