# Renders

Two generations of model live here. Use **`v2/`** — it is built from the real
floor plan.

> ⚠️ **Concept massing only — not a permit document.** The floor-plan trace is
> scaled to the 2,874 sf public record, not measured on site. A vertical addition
> in the Miami-Dade HVHZ must be designed and sealed by a Florida-licensed
> architect and structural engineer ([../docs/04](../docs/04-architect-shortlist.md)).

## Start here

**[`interactive-3d-v2.html`](interactive-3d-v2.html)** — open in any browser
(also published at <https://claude.ai/code/artifact/b27dd04d-43c9-4ae5-8c26-ba5e6b7331e0>).
Orbit/zoom/pan, toggle the second floor and the roofs, and switch to
**Cutaway plan** to see both floor plates stacked with the bearing walls (green)
and the one new beam line (red). Loads three.js from a CDN, so it needs internet
the first time.

## `v2/` — modelled from sheet A-1

| File | What it is |
|---|---|
| `v2/hero_canal.png` | Proposed, from the canal — primary suite + terrace on the water |
| `v2/street.png` | Proposed, from Hawthorne Ave — the second floor reads as set back |
| `v2/aerial.png` | Proposed, aerial three-quarter |
| `v2/existing_street.png` | Existing one storey, same camera — the A/B comparison |
| `v2/existing_canal.png` | Existing, from the canal |

## `plans/` — schematic sheets

| File | What it is |
|---|---|
| `plans/a1_existing_traced.png` | Ground floor traced from sheet A-1, dimensioned |
| `plans/a1_second_floor.png` | **Proposed second floor, scheme A** |
| `plans/a1_stacking.png` | New floor over the existing bearing walls — the load path |
| `plans/a1_section.png` | Height stack: does two storeys fit under the cap? |
| `plans/ground_floor.png`, `plans/second_floor.png`, `plans/elevations.png` | earlier study (pre-A-1) |

## Earlier massing study (superseded)

`interactive-3d-model.html`, `existing_*.png`, `proposed_*.png`, `blender/`,
`photomontage/` — built before sheet A-1 was available, from an assumed
41' × 64' box. Kept for comparison; prefer `v2/`.

`artifact-viewer.html` is the same page without the `<html>/<head>/<body>`
skeleton, for publishing as an Artifact; both are generated from one template.

## Regenerate

```bash
pip install numpy matplotlib trimesh
python3 tools/house_data.py         # prints the room schedule + area maths
python3 tools/floorplan_model.py    # plans + 3D renders + cad/8220_hawthorne_from_plan.glb
python3 tools/build_viewer.py       # interactive-3d-v2.html + artifact-viewer.html
```

All three read `tools/house_data.py`, so the plans, the renders, the GLB and the
viewer cannot drift apart — change a dimension in one place and re-run.
