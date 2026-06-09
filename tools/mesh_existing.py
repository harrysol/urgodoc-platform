#!/usr/bin/env python3
"""
Turn the VGGT point cloud of the existing house into a leveled, cleaned, SOLID
surface mesh (colored). Output: cad/combined/existing_house_mesh.glb/.ply
"""
import numpy as np, os, open3d as o3d, trimesh

src = "cad/vggt/house_vggt.ply"
OUT = "cad/combined"; os.makedirs(OUT, exist_ok=True)
m = trimesh.load(src)
P = np.asarray(m.vertices); C = np.asarray(m.colors)[:, :3] / 255.0
# to Z-up (VGGT up ~ -Y)
P = np.column_stack([P[:,0], P[:,2], -P[:,1]]).astype(float)
# trim gross outliers
d = np.linalg.norm(P - np.median(P,0), axis=1); k = d < np.quantile(d,0.94)
P, C = P[k], C[k]

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(P)
pcd.colors = o3d.utility.Vector3dVector(np.clip(C,0,1))
# statistical outlier removal
pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
print("after outlier removal:", len(pcd.points))

# LEVEL: fit ground plane, rotate its normal to +Z
plane, inl = pcd.segment_plane(distance_threshold=0.01, ransac_n=3, num_iterations=1000)
n = np.array(plane[:3]); n = n/np.linalg.norm(n)
if n[2] < 0: n = -n
z = np.array([0,0,1.0]); v = np.cross(n,z); s = np.linalg.norm(v); c = np.dot(n,z)
if s > 1e-6:
    vx = np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    R = np.eye(3) + vx + vx@vx*((1-c)/(s*s))
    pcd.rotate(R, center=pcd.get_center())
pts = np.asarray(pcd.points); pts -= [pts[:,0].mean(), pts[:,1].mean(), pts[:,2].min()]
pcd.points = o3d.utility.Vector3dVector(pts)

# normals + Poisson surface
pcd.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=0.05, max_nn=30))
pcd.orient_normals_consistent_tangent_plane(30)
mesh, dens = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)
dens = np.asarray(dens)
mesh.remove_vertices_by_mask(dens < np.quantile(dens, 0.15))   # drop inferred/back balloon
mesh = mesh.crop(pcd.get_axis_aligned_bounding_box())
mesh.remove_degenerate_triangles(); mesh.remove_unreferenced_vertices()
mesh.compute_vertex_normals()
print("mesh verts", len(mesh.vertices), "tris", len(mesh.triangles))
o3d.io.write_triangle_mesh(os.path.join(OUT,"existing_house_mesh.ply"), mesh)
o3d.io.write_triangle_mesh(os.path.join(OUT,"existing_house_mesh.glb"), mesh)
# report dims (relative units)
b=np.asarray(mesh.vertices); print("bbox", b.max(0)-b.min(0))
print("wrote existing_house_mesh.glb/.ply")
