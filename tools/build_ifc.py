#!/usr/bin/env python3
"""
Generate a real IFC (BIM) model of the 8220 Hawthorne second-floor project.
Two building storeys with perimeter walls + floor slabs, dimensioned from the
survey. Output opens in Revit, ArchiCAD, Bonsai/BlenderBIM, or free IFC viewers.
Massing-level BIM — NOT a permit set.
"""
import numpy as np, os
import ifcopenshell
from ifcopenshell.api import run

FT = 0.3048  # feet -> metres
PLINTH, S1H, S2H, TH = 1.5*FT, 11.0*FT, 10.0*FT, 0.7*FT
HX0,HX1,HY0,HY1 = 9.5*FT,50.5*FT,20.0*FT,84.0*FT
S2X0,S2X1,S2Y0,S2Y1 = 12.0*FT,48.0*FT,34.0*FT,84.0*FT

model = run("project.create_file")
proj = run("root.create_entity", model, ifc_class="IfcProject", name="8220 Hawthorne Ave - 2nd Floor Addition")
run("unit.assign_unit", model)
ctx = run("context.add_context", model, context_type="Model")
body = run("context.add_context", model, context_type="Model",
           context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)

site = run("root.create_entity", model, ifc_class="IfcSite", name="Lot 5 Blk D - Biscayne Beach 3rd Sec")
bldg = run("root.create_entity", model, ifc_class="IfcBuilding", name="8220 Hawthorne Ave")
g = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")
s = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Second Floor (NEW)")
run("aggregate.assign_object", model, relating_object=proj, products=[site])
run("aggregate.assign_object", model, relating_object=site, products=[bldg])
run("aggregate.assign_object", model, relating_object=bldg, products=[g, s])

def mat(x, y, z, rot=False):
    m = np.eye(4)
    if rot:
        m[0,0], m[0,1], m[1,0], m[1,1] = 0, -1, 1, 0
    m[0,3], m[1,3], m[2,3] = x, y, z
    return m

def wall(storey, x, y, z, length, height, rot=False, name="Wall"):
    w = run("root.create_entity", model, ifc_class="IfcWall", name=name)
    rep = run("geometry.add_wall_representation", model, context=body,
              length=length, height=height, thickness=TH)
    run("geometry.assign_representation", model, product=w, representation=rep)
    run("geometry.edit_object_placement", model, product=w, matrix=mat(x, y, z, rot))
    run("spatial.assign_container", model, relating_structure=storey, products=[w])
    return w

def slab(storey, x0, x1, y0, y1, z, name="Slab"):
    try:
        sl = run("root.create_entity", model, ifc_class="IfcSlab", name=name)
        poly = [(0,0), (x1-x0,0), (x1-x0,y1-y0), (0,y1-y0)]
        rep = run("geometry.add_slab_representation", model, context=body,
                  depth=TH, polyline=poly)
        run("geometry.assign_representation", model, product=sl, representation=rep)
        run("geometry.edit_object_placement", model, product=sl, matrix=mat(x0, y0, z))
        run("spatial.assign_container", model, relating_structure=storey, products=[sl])
    except Exception as e:
        print("slab skipped:", e)

def storey_shell(storey, x0, x1, y0, y1, zb, h, tag):
    slab(storey, x0, x1, y0, y1, zb, f"{tag} Floor Slab")
    wall(storey, x0, y0, zb, x1-x0, h, name=f"{tag} Wall S")
    wall(storey, x0, y1-TH, zb, x1-x0, h, name=f"{tag} Wall N")
    wall(storey, x0, y0, zb, y1-y0, h, rot=True, name=f"{tag} Wall W")
    wall(storey, x1-TH, y0, zb, y1-y0, h, rot=True, name=f"{tag} Wall E")

storey_shell(g, HX0, HX1, HY0, HY1, PLINTH, S1H, "L1")
ROOF_Z = PLINTH + S1H + TH
storey_shell(s, S2X0, S2X1, S2Y0, S2Y1, ROOF_Z, S2H, "L2")
slab(s, S2X0, S2X1, HY1, HY1+9*FT, ROOF_Z, "Bay Terrace")

OUT = os.path.join(os.path.dirname(__file__), "..", "cad")
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, "8220_hawthorne_2story.ifc")
model.write(path)
print("wrote IFC:", path, "| storeys:", len(model.by_type("IfcBuildingStorey")),
      "| walls:", len(model.by_type("IfcWall")), "| slabs:", len(model.by_type("IfcSlab")))
