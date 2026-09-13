# 16 — Second-Floor Design, Drawn on the Real Floor Plan

Everything before this document guessed at the house's shape. The architect's
sheet **A-1 "EXISTING UNIT FLOOR PLAN" (scale 1/4"=1'-0")** changes that: we now
have the actual room layout, so the second floor can be designed against real
walls instead of a rectangle.

| | Before (docs/10) | Now |
|---|---|---|
| Footprint | assumed 41' × 64' box | traced stepped outline, **48'-8" × 72'-1"** |
| Rooms | invented | the nine rooms on A-1 |
| Load path | "stack it on the walls" | four real bearing lines + one new beam |
| Stair | not located | straight run in the living room, 17R, it fits |

Regenerate everything with:

```bash
pip install numpy matplotlib trimesh
python3 tools/floorplan_model.py    # plans, 3D renders, GLB
python3 tools/build_viewer.py       # renders/interactive-3d-v2.html
```

---

## 1. What the trace says

Sheet A-1 carries no legible dimension strings, so the trace was calibrated by
scaling the polygon until its enclosed area matched the **2,874 sf** on the
public record. That gives **0.0657 ft per traced pixel**, and every number below
follows from it.

> ⚠️ **This calibration is the weakest link in the whole package.** One tape
> measure across the living room either confirms it or rescales all of it.
> Do that before anything else.

Ground floor as traced (`renders/plans/a1_existing_traced.png`):

| Room | Size | Area |
|---|---|---|
| Sunroom | 25'-10" × 19'-10" | 511 sf |
| Guest bedroom | 17'-6" × 38'-6" | 674 sf |
| Living room | 19'-1" × 27'-7" | 527 sf |
| Kitchen | 12'-1" × 22'-0" | 266 sf |
| Utility room | 12'-1" × 18'-5" | 223 sf |
| Master BR | 14'-11" × 11'-0" | 164 sf |
| W.I.C. | 7'-7" × 20'-2" | 154 sf |
| Work area *(A-1 permit scope)* | 13'-2" × 11'-10" | 156 sf |
| Dining room | 14'-11" × 8'-11" | 133 sf |

Three things worth flagging from the sheet itself:

- **No bathrooms are drawn.** A-1 is a *background* sheet for a small work-area
  permit, not a full as-built. The record says 2 baths; they are in there
  somewhere, most likely inside that unusually deep 38'-6" "guest bedroom".
- The **"WORK AREA"** dashed box is a kitchenette/utility alcove off the master —
  it is the scope of *that* permit, not of this project.
- The title block reads **8220 Hawthorne Ave-**`A`, i.e. a *unit*. Confirm the
  house is a single legal single-family dwelling before adding floor area;
  a duplex/efficiency history changes the zoning and parking analysis.

## 2. Which way the house faces

The canal is at the rear (survey) and the rear wall carries four large windows
plus the sunroom — so the plan's top edge is taken as the **canal/rear** and the
bottom, with the utility room and entry, as **Hawthorne Ave**. Confirm against
the survey's north arrow; if it is flipped, the design mirrors but nothing else
changes.

## 3. Scheme A — "canal house"

`renders/plans/a1_second_floor.png` · `renders/v2/*.png` · `renders/interactive-3d-v2.html`

**1,632 sf conditioned + 358 sf of terrace**, sitting on the canal half of the
footprint and stopping 30'-1" short of the street.

| | |
|---|---|
| Primary bedroom | 22'-0" × 20'-0" · 440 sf · full-width glass to the canal |
| Primary bath / W.I.C. | 128 sf / 107 sf |
| Canal terrace | 16'-0" × 13'-0" · 208 sf, over the sunroom |
| Study | 16'-0" × 9'-0" · 144 sf |
| Bedroom 2 / Bedroom 3 | 210 sf / 140 sf, each with a bath |
| Gallery | 6'-0" wide, runs the width |
| Laundry / mech | 52 sf, central so no run is long |
| Front terrace | 10'-8" × 14'-0" · 150 sf, cuts the street-facing mass |

Four moves do the work:

1. **Bedrooms go up, living stays down.** The ground floor keeps its two best
   rooms — the 511 sf sunroom and the 527 sf living room — and loses only a
   3'-7" strip of living room to the stair. The master, W.I.C. and work area
   downstairs are freed for a proper family room / guest suite.
2. **The primary suite takes the water.** 20 ft of glass under a 3'-0" eyebrow
   that shades it in summer, opening to a recessed terrace over the sunroom.
   Recessed, not cantilevered: cheaper, and it survives a hurricane better.
3. **The street elevation stays low.** The second floor stops at Y = 42'-0" and
   the SE corner is cut away for the front terrace, so from Hawthorne Ave you
   read a one-storey house with something behind it. Compare
   `renders/v2/existing_street.png` with `renders/v2/street.png`.
4. **It lands at almost exactly FAR 0.50.** 2,874 + 1,632 = **~4,500 sf** on the
   9,000 sf lot. That is a suspiciously round number to be at — treat it as a ceiling to
   design down from, not a target, until Planning confirms the district's cap.

## 4. The structure actually works out

`renders/plans/a1_stacking.png`

The second-floor perimeter sits on existing CBS wherever it can:

| Second-floor edge | Below it |
|---|---|
| Rear (canal), Y = 0 | existing exterior wall ✅ |
| West, X = 0 | existing exterior wall ✅ |
| East, X = 48'-8" | existing exterior wall ✅ |
| **Front, Y = 42'-0"** | **nothing — new beam** ❌ |

Three of four edges are a direct load path. The fourth needs one new beam across
the house, and the plan hands it supports almost for free: the traced partitions
at **X = 17'-6"** (guest bedroom / living) and **X = 36'-7"** (living / kitchen)
both cross Y = 42'-0". With columns at 0 / 17'-6" / 36'-7" / 48'-8" the longest
clear span is **19'-1"** — ordinary rolled steel, no transfer truss, no
sixty-foot girder. Four new footings through the slab, not a new frame.

Interior partitions at X = 25'-10", X = 33'-10" and Y = 19'-10" give the engineer
further intermediate bearing if the joist spans want shortening.

None of this is a substitute for an engineer's investigation — 1955 footings
still have to be dug up and looked at, and HVHZ uplift on a now-taller building
is its own calculation. It does mean the answer is likely "reinforce", not
"demolish the roof and start a new frame".

## 5. The stair fits, exactly

Floor-to-floor **10'-6"** → **17 risers @ 7.41"**, 16 treads @ 10½" = a **14'-0"
run**. Placed as a straight flight against the existing living/kitchen spine wall
(X = 33'-0" to 36'-7"), bottom riser at Y = 42'-0" in the living room, rising
toward the canal and landing inside the second-floor footprint. It costs the
living room a 3'-7" strip and no room at all on the plan's critical path.

An open-riser flight with a glass rail here also lets the new upstairs gallery
borrow light down into the middle of a deep house — the one thing the existing
plan is short of.

## 6. The real go / no-go is flood, not structure

`renders/plans/a1_section.png`

| | Scheme A — slab stays | Scheme B — slab forced up to BFE |
|---|---|---|
| FF1 | +1.0' above grade | +4.5' (BFE 8.0 + 1' freeboard) |
| FF2 | +11.5' | +15.0' |
| Top of parapet | **+23.9'** | **+27.4'** |
| Against a 24' cap | fits, with 1" to spare | **busts it by 3'-5"** |

The house is in **Flood Zone AE, BFE 8.0' NGVD**. If the addition is priced at or
above **50% of the structure's value**, it is a *substantial improvement* and
Miami Beach can require the **whole house** to come up to BFE. Raise the slab
3'-6" and the two-storey stack no longer fits under the height cap — and the
project turns into a tear-down-and-rebuild, a completely different budget.

So the order of operations is not negotiable:

1. **Tape-measure the house** → confirm or rescale this whole package.
2. **Miami Beach Planning** → the district, its *actual* max height, second-floor
   side/rear setbacks, waterfront setback, FAR cap.
3. **A flood/valuation read** → what does 50% of structure value come to, and
   what does this addition cost? If those two numbers are close, redesign around
   them *now*, not after schematic design.
4. Only then: structural investigation, architect, permit set.

Steps 2 and 3 cost a phone call and a few hundred dollars. They decide whether
scheme A is buildable at all.

## 7. What this is not

Concept massing built from a traced background sheet and a public square-footage
figure. Not measured, not engineered, not a permit document. Every dimension
needs verifying on site, and a vertical addition in the Miami-Dade HVHZ must be
designed and sealed by a Florida-licensed architect and structural engineer —
see [docs/04](04-architect-shortlist.md).
