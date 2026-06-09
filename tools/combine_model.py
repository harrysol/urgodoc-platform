#!/usr/bin/env python3
"""
Combine the REAL existing house (VGGT photo point cloud, one story) with a
DETAILED proposed SECOND FLOOR (windows + bay terrace) on its roof.
Outputs a combined GLB + multi-angle render.
"""
import numpy as np, trimesh, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT = os.path.join(os.path.dirname(__file__), "..", "cad", "combined"); os.makedirs(OUT, exist_ok=True)
pc = trimesh.load("cad/vggt/house_vggt.ply")
P = np.asarray(pc.vertices); C = np.asarray(pc.colors)[:, :3] / 255.0
W = np.column_stack([P[:,0], P[:,2], -P[:,1]]).astype(float)          # to Z-up
d = np.linalg.norm(W - np.median(W,0), axis=1); k = d < np.quantile(d,0.92)
W, C = W[k], C[k]
W -= [W[:,0].mean(), W[:,1].mean(), W[:,2].min()]

ztop = np.percentile(W[:,2],97); zg = np.percentile(W[:,2],3); bh = ztop-zg
bld = W[W[:,2] > zg+0.35*bh]
bx0,bx1 = np.percentile(bld[:,0],[8,92]); by0,by1 = np.percentile(bld[:,1],[8,92])
sz = max(bx1-bx0, by1-by0)
ix,iy = (bx1-bx0)*0.16, (by1-by0)*0.16
sx0,sx1,sy0,sy1 = bx0+ix, bx1-ix, by0+iy, by1-iy
sh = bh*0.9
z0, z1 = ztop, ztop+sh
print("roof z=%.2f  2nd-floor box x %.2f..%.2f y %.2f..%.2f h=%.2f"%(ztop,sx0,sx1,sy0,sy1,sh))

def boxmesh(x0,x1,y0,y1,za,zb,color):
    b=trimesh.creation.box(bounds=[[x0,y0,za],[x1,y1,zb]])
    b.visual.vertex_colors=np.tile((np.array(color+[255])).astype(np.uint8),(len(b.vertices),1)); return b

WHITE=[238,238,242]; DARK=[30,33,40]; GLASS=[60,90,120]; WOOD=[170,120,70]
meshes=[("second_floor", boxmesh(sx0,sx1,sy0,sy1,z0,z1,WHITE)),
        ("roof_fascia",  boxmesh(sx0-0.01*sz,sx1+0.01*sz,sy0-0.01*sz,sy1+0.01*sz,z1,z1+0.06*sh,DARK)),
        ("bay_terrace",  boxmesh(sx0,sx1,sy1,sy1+0.16*(by1-by0),z0,z0+0.04*sh,WOOD))]
# windows on front (sy0) and bay (sy1) faces
t=0.012*sz; nwin=4
for kk in range(nwin):
    wx0=sx0+(sx1-sx0)*(kk+0.18)/nwin; wx1=sx0+(sx1-sx0)*(kk+0.82)/nwin
    meshes.append(("win_front_%d"%kk, boxmesh(wx0,wx1, sy0-t, sy0+t, z0+0.28*sh, z0+0.72*sh, DARK)))
    meshes.append(("win_bay_%d"%kk,   boxmesh(wx0,wx1, sy1-t, sy1+t, z0+0.22*sh, z0+0.8*sh, GLASS)))

scene=trimesh.Scene()
cc=(np.concatenate([C,np.ones((len(C),1))],1)*255).astype(np.uint8)
scene.add_geometry(trimesh.PointCloud(W,colors=cc),node_name="existing_house_real")
for nm,m in meshes: scene.add_geometry(m,node_name=nm)
scene.export(os.path.join(OUT,"house_plus_second_floor.glb"))
print("exported house_plus_second_floor.glb")

# render
def face(ax,x0,x1,y0,y1,za,zb,col,a,ec="#2f5d92"):
    v=np.array([[x0,y0,za],[x1,y0,za],[x1,y1,za],[x0,y1,za],[x0,y0,zb],[x1,y0,zb],[x1,y1,zb],[x0,y1,zb]])
    fs=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]
    ax.add_collection3d(Poly3DCollection([v[f] for f in fs],alpha=a,facecolor=col,edgecolor=ec,linewidths=1.0))
idx=np.random.choice(len(W),min(120000,len(W)),replace=False)
fig=plt.figure(figsize=(16,5.6),facecolor="#0d0d0f")
for i,(el,az) in enumerate([(12,-58),(16,-95),(20,-135)]):
    ax=fig.add_subplot(1,3,i+1,projection="3d",facecolor="#0d0d0f")
    ax.scatter(W[idx,0],W[idx,1],W[idx,2],c=np.clip(C[idx]**0.65,0,1),s=2.0,marker=".",linewidths=0)
    face(ax,sx0,sx1,sy0,sy1,z0,z1,"#e8edf5",0.55)                       # second floor
    for kk in range(nwin):
        wx0=sx0+(sx1-sx0)*(kk+0.18)/nwin; wx1=sx0+(sx1-sx0)*(kk+0.82)/nwin
        face(ax,wx0,wx1,sy0-t,sy0+t,z0+0.28*sh,z0+0.72*sh,"#1e2128",0.95,ec="#1e2128")
    face(ax,sx0,sx1,sy1,sy1+0.16*(by1-by0),z0,z0+0.04*sh,"#aa7846",0.8,ec="#7a5a2a")  # terrace
    ax.view_init(elev=el,azim=az); ax.set_axis_off(); ax.set_box_aspect((1,1,0.8))
fig.suptitle("8220 Hawthorne - existing house (your photos) + PROPOSED second floor (windows + bay terrace)",color="white",fontsize=12)
fig.savefig(os.path.join(OUT,"house_plus_second_floor.png"),dpi=130,bbox_inches="tight",facecolor="#0d0d0f")
print("wrote render")
