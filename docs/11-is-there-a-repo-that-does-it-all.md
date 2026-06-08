# 11 — "Is there a repo that does it all?"

**Short answer: no single repo turns your address into a finished, permit-ready
project.** It can't legally exist — the final deliverable (stamped, code-
compliant construction drawings, HVHZ structural design) is a *regulated* product
only a Florida-licensed architect/engineer can sign. Anyone claiming "free AI does
your whole permitted addition" is wrong.

**But repos/tools automate the big pieces** — and that's exactly the pipeline this
project's own scripts already run for *this* house:
`tools/floor_plans.py` (plans) + `tools/blender_second_floor.py` (3D).

## Closest "does-a-lot" options, by job

### A. Describe it → get floor plans (homeowner-friendly, no CAD)
| Tool | Notes |
|------|-------|
| **Maket.ai** — https://www.maket.ai | Type what you want → residential floor plans in minutes. The most "all-in-one" for a homeowner. |
| **ArchitectGPT / ArchiPi** — https://www.architectgpt.io | Floor-plan creator + turns plans into furnished 3D/renders. |
| **Planner5D** — https://planner5d.com | AI floor plan + 3D, easy. |
| **Coohom** — https://www.coohom.com | Plan → 3D + photoreal renders. |

### B. Open-source floor-plan generators (research-grade, need ML setup + GPU)
| Repo | Notes |
|------|-------|
| **HouseDiffusion** — https://github.com/aminshabani/house_diffusion | Diffusion model → vector floor plans from a room graph. |
| **ChatHouseDiffusion** — https://github.com/ChatHouseDiffusion/chathousediffusion | **Text prompt → floor plan**, editable. |
| **Graph2Plan** — https://github.com/HanHan55/Graph2plan | Layout graph + boundary → floor plan. |
| **FloorplanGAN** — https://github.com/luozn15/FloorplanGAN | GAN vector floor plan generation. |

> These output *schematic* layouts, not permit drawings, and need Python/ML skills
> + a GPU. For a one-off house, the hosted tools in (A) are far easier.

### C. Photo/concept → photoreal images (covered in detail)
**Qwen-Image-Edit**, **FLUX.1 Kontext**, **ComfyUI**, **Nano Banana/Gemini** —
see [docs/08](08-photoreal-render-howto.md) and [docs/09](09-open-source-repos.md).

### D. The real 3D / BIM model (open source)
- **Blender** (https://www.blender.org) — what this repo uses for the 3D.
- **FreeCAD + BIM workbench** (https://www.freecad.org) — parametric building model.
- **SketchUp** (freemium) — easiest for homeowners to model an addition.

## The unavoidable last mile
A → D get you **design + visuals**. They do **not** get you a permit. The licensed
architect + structural engineer convert this into the **signed/sealed set** for
Miami Beach + HVHZ. That's the part that protects you legally and structurally —
and the only part you genuinely can't skip. Shortlist: [docs/04](04-architect-shortlist.md).

## What this repo already is
For 8220 Hawthorne specifically, the scripts here *are* your "repo that helps":
edit the parameters at the top of `tools/floor_plans.py` /
`tools/blender_second_floor.py` and re-run to regenerate the plans, elevations and
3D as the design changes.
