# 14 — Polycam House Scan

A real LiDAR scan of the house (Polycam, GLB) was captured and added here.

## Files — `cad/scan/`
| File | Notes |
|------|-------|
| `house_scan_raw.glb` | Original scan: 60k verts / 100k faces, textured |
| `house_scan_clean.glb` | Stray fragments removed (478 floaters), 43k verts |
| `scan_*.png` / `scanclean_*.png` | Blender renders (3/4, front, aerial) |

## Real-world measurements (LiDAR = true scale)
- Bounding box ≈ **51.4 × 50.0 ft footprint, 15.3 ft tall** (one storey + roof).
- Confirms the lot/footprint order of magnitude used in the schematic.

## Honest quality assessment
The capture is **partial and holey** — incomplete walls/roof, gaps, fragments.
Usable to confirm scale and as a rough reference, but **not** a clean base model
to build the addition on yet.

## How to get a scan we CAN build on
Re-capture with Polycam (LiDAR mode), going slowly and thoroughly:
1. **One room at a time**, move slowly; keep walls/floor/ceiling all in frame.
2. **Full overlap** — sweep every surface, including corners and ceilings; do a
   second pass.
3. **Walk the full path** room-to-room without stopping the capture so rooms link.
4. **Good even lighting**; avoid pointing at mirrors/large glass (they break scans).
5. For the **exterior**, orbit the whole house slowly at 2 heights (eye level + raised).
6. Export **GLTF/GLB** again and re-upload.

With a complete scan, the model can be cleaned, measured room-by-room, and the
second-floor addition aligned to the *real* house instead of an estimated footprint.
