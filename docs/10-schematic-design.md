# 10 — Schematic Design Package (the real project)

A coherent **schematic design** for the second-floor addition, built from the
boundary survey + listing photos. This is the actual project concept — floor
plans, elevations and a 3D model — at the level you hand to an architect to
develop and stamp.

> ⚠️ **Schematic / conceptual. NOT construction documents and NOT a permit set.**
> Dimensions are approximate. The signed-and-sealed drawings and HVHZ structural
> design must come from a Florida-licensed architect + engineer
> ([docs/04](04-architect-shortlist.md)).

## Design concept

- **Build the new floor on the existing flat roof** (the photos confirm a flat/
  low-slope roof — the cheapest, cleanest way to go up), **stepped back ~8–10 ft
  from the street** so the low horizontal front facade is preserved.
- **Orient the second floor to the water:** the primary suite opens west to a
  **cantilevered bay terrace** with a glass rail — capturing the open-bay sunset
  views that are wasted at ground level today.
- Keep the existing **white-stucco tropical-modern** language: black-framed impact
  glass, thin flat-roof fascia, the entry column screen, wood accents.
- Ground floor is **reconfigured, not expanded** — the new stair is carved out of
  the central core; the great room keeps opening to the pool/bay.

## Program & areas (approximate)

| Level | Spaces | Area |
|-------|--------|------|
| Ground (existing) | 2 bedrooms, den/office, kitchen, great room, baths, new stair | ~2,874 sf |
| **Second (new)** | Primary suite (bed + bath + WIC) **+ west bay terrace**, guest bedroom, office/loft, stair | **~1,200 sf** |
| **Total** | | **~4,050 sf** |

(Second-floor footprint ~34′ × 46′, set back from the street; rooftop terrace over
the stepped-back portion.)

## Drawings — `renders/plans/`

| File | Sheet |
|------|-------|
| `ground_floor.png` | Ground floor plan (reconfigured, new stair) |
| `second_floor.png` | New second floor plan (primary suite + bay terrace) |
| `elevations.png` | Front (Hawthorne) + rear (bay/west) elevations, BFE 8.0′ noted |

## 3D model — `renders/blender/`

Articulated massing model (white stucco, glass, entry colonnade, bay terrace,
pool, palms) rendered with physical sky/sun:
- `01_bay_hero.png` — from the water, golden hour (the view-driven concept)
- `02_street.png` — from Hawthorne Ave
- `03_aerial.png` — aerial overview

Regenerate: `python3 tools/floor_plans.py` and `python3 tools/blender_second_floor.py`.

## Next step
Hand this package + the survey + the listing photos to the 3 architects
([docs/04](04-architect-shortlist.md)) as the brief. For a **photoreal** version
of the front, run your photo through the AI tools in
[docs/08](08-photoreal-render-howto.md) / [docs/09](09-open-source-repos.md).
