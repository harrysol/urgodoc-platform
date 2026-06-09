# 15 - Photo-to-3D Reconstruction (VGGT)

Reconstructed the house in 3D from the listing photos using **VGGT** (Meta's
feed-forward multi-view 3D model, github.com/facebookresearch/vggt), run on CPU
in this environment.

## Result - `cad/vggt/`
| File | Notes |
|------|-------|
| `house_vggt.glb` / `.ply` | Colored 3D point cloud (~725k pts) from 8 photos |
| `house_vggt_views.png` | 3 novel-viewpoint renders |

Open the `.glb`/`.ply` in any 3D viewer (gltf-viewer.donmccurdy.com, MeshLab,
CloudCompare, Blender) and orbit it. Regenerate:
`python3 tools/vggt_reconstruct.py <photo1> <photo2> ...`

## What it reconstructed
Front facade + driveway + lawn + pool/rear, as an aligned colored point cloud -
a genuine multi-view reconstruction (not single-view depth, not the broken scan).
Built from front shots (03-06) + pool/rear shots (01,31,32,33).

## Honest limits
- It's a **point cloud**, not a watertight solid mesh (can be meshed with Poisson).
- Coverage = only what the photos saw, with overlap. Sides/roof/interior are
  sparse because the listing photos don't cover them with overlap.
- Scale is **relative** (not metric) - the LiDAR scan (docs/14) is the metric ref.

## Next options
1. **Mesh it** - Poisson surface reconstruction -> solid model.
2. **Add more photos** with overlap (or a Polycam video) for fuller coverage.
3. **Combine** with the designed second-floor model to show addition on the real house.
