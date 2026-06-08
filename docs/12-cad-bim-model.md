# 12 — CAD / BIM Model (generated here, from the repo approach)

You were right that a "repo that drives CAD" exists — the top one is
**[ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)** (~22k★), which
lets an AI build 3D models inside **Blender**; **[ifc-bonsai-mcp](https://github.com/Show2Instruct/ifc-bonsai-mcp)**
does the same for **IFC/BIM**. Those are just *bridges* that send Python into
Blender / IfcOpenShell — which we run **directly** here. So this repo generates
the actual CAD files itself:

## Files in `cad/`

| File | Format | Open with |
|------|--------|-----------|
| `8220_hawthorne_2story.ifc` | **IFC4 BIM**: 2 storeys (with elevations), 8 walls, 3 slabs, bay terrace, **11 named rooms (IfcSpace) with floor areas** | Revit, ArchiCAD, Bonsai/BlenderBIM, [free IFC viewer](https://viewer.ifcjs.io) / usBIM.viewer |
| `8220_hawthorne_2story.glb` | glTF 3D | Blender, [gltf-viewer](https://gltf-viewer.donmccurdy.com), Windows 3D Viewer, web |
| `8220_hawthorne_2story.obj` | OBJ 3D | SketchUp, Rhino, Cinema4D, MeshLab, almost anything |
| `cad_preview.png` | preview | quick look |

The **IFC** is the important one: it's a real **BIM** model with named building
storeys and wall/slab elements — the format an architect imports to start the
permit drawings, instead of redrawing from scratch.

## How it's built (open the scripts)

- `tools/export_cad.py` — Blender (`bpy`) builds a hollow two-storey shell
  (walls + slabs + roof + bay terrace + entry colonnade) and exports glTF/OBJ.
- `tools/build_ifc.py` — IfcOpenShell builds the IFC4 BIM (project → site →
  building → 2 storeys → walls/slabs + **IfcSpace rooms with names & areas**),
  dimensioned from the survey (lot 60×150, footprint ~41×64, second floor stepped
  back ~34×46, BFE-aware plinth). Rooms:
  - **Ground:** Bedroom 2, Foyer/Stair, Bedroom 3, Den/Office, Hall, Kitchen,
    Great Room (~1,066 sf).
  - **Second (new):** Bedroom 4/Guest, Office/Loft, Primary Bedroom, Primary
    Bath + WIC.

Edit the dimensions at the top of either script and re-run to regenerate.

## The honest scope
This is a **massing-level BIM/CAD model** — real, editable, correctly structured,
and a genuine head-start for the architect. It is **not** a stamped permit set:
HVHZ structural sizing, code compliance, MEP, and the signed/sealed drawings still
require the licensed architect + engineer ([docs/04](04-architect-shortlist.md)).

## If you want full AI-driven CAD on your own machine
Install **Blender** + **[blender-mcp](https://github.com/ahujasid/blender-mcp)**
(or **[ifc-bonsai-mcp](https://github.com/Show2Instruct/ifc-bonsai-mcp)** for BIM)
and connect it to Claude Desktop/Cursor — then you can refine this model by just
talking to it. For photo→3D mesh: **[Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2)**
or **[TripoSR](https://github.com/VAST-AI-Research/TripoSR)** (need a GPU).
