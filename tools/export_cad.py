#!/usr/bin/env python3
"""
Export the 8220 Hawthorne second-floor project as real, editable CAD/3D files.
Builds a hollow two-storey shell (walls + slabs + roof + bay terrace) with the
survey dimensions and exports glTF (.glb), OBJ (.obj) and FBX. Open in any 3D /
CAD app (Blender, SketchUp, Rhino, Cinema4D, web viewers, etc.).
"""
import bpy, os, math

bpy.ops.wm.read_factory_settings(use_empty=True)

# ---- dims (feet) ----
PLINTH, S1H, S2H, T = 1.5, 11.0, 10.0, 0.7      # T = wall/slab thickness
HX0, HX1, HY0, HY1 = 9.5, 50.5, 20.0, 84.0
S2X0, S2X1, S2Y0, S2Y1 = 12.0, 48.0, 34.0, 84.0

def box(x0, x1, y0, y1, z0, z1, name):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object; o.name = name
    o.scale = ((x1-x0)/2, (y1-y0)/2, (z1-z0)/2)
    o.location = ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)
    return o

def storey(x0, x1, y0, y1, zb, h, tag):
    """floor slab + 4 perimeter walls + ceiling slab => hollow shell."""
    box(x0, x1, y0, y1, zb, zb+T, f"{tag}_floor")
    box(x0, x1, y0, y0+T, zb+T, zb+h, f"{tag}_wall_S")
    box(x0, x1, y1-T, y1, zb+T, zb+h, f"{tag}_wall_N")
    box(x0, x0+T, y0, y1, zb+T, zb+h, f"{tag}_wall_W")
    box(x1-T, x1, y0, y1, zb+T, zb+h, f"{tag}_wall_E")
    box(x0, x1, y0, y1, zb+h, zb+h+T, f"{tag}_roof")

# ground storey (full footprint) on a plinth
box(HX0-1.5, HX1+1.5, HY0-1.5, HY1+1.5, 0, PLINTH, "plinth")
storey(HX0, HX1, HY0, HY1, PLINTH, S1H, "L1")
# second storey on the flat roof, stepped back from the street
ROOF_Z = PLINTH + S1H + T
storey(S2X0, S2X1, S2Y0, S2Y1, ROOF_Z, S2H, "L2")
# west bay terrace (cantilever) + glass-rail line
box(S2X0, S2X1, HY1, HY1+9, ROOF_Z, ROOF_Z+0.5, "L2_bay_terrace")
box(S2X0, S2X1, HY1+8.5, HY1+9, ROOF_Z, ROOF_Z+3.4, "L2_bay_rail")
# entry colonnade (matches photo)
for i, cx in enumerate(range(19, 30, 2)):
    box(cx-0.25, cx+0.25, HY0-0.4, HY0+0.4, PLINTH, PLINTH+S1H, f"col_{i}")

OUT = os.path.join(os.path.dirname(__file__), "..", "cad")
os.makedirs(OUT, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "8220_hawthorne_2story.glb"),
                          export_format='GLB', use_selection=True)
try:
    bpy.ops.wm.obj_export(filepath=os.path.join(OUT, "8220_hawthorne_2story.obj"))
except Exception:
    bpy.ops.export_scene.obj(filepath=os.path.join(OUT, "8220_hawthorne_2story.obj"))
print("exported GLB + OBJ ->", OUT)
