# 8220 Hawthorne Ave — Second-Floor Addition Project

Project workspace for adding a **second floor** to the single-family home at
**8220 Hawthorne Ave, Miami Beach, FL 33141**.

> ⚠️ **Read this first.** AI tools can give you concept designs and photorealistic
> 3D renderings cheaply and fast. They **cannot** produce the signed-and-sealed
> drawings Miami-Dade legally requires for a permit. A vertical addition in a
> High-Velocity Hurricane Zone (HVHZ) **must** be designed/stamped by a
> Florida-licensed architect and structural engineer. The realistic money-saver
> is: use AI for the **concept + renderings**, then hand a clear, well-defined
> brief to a licensed architect so you pay them for stamped drawings, not for
> figuring out what you want. See [docs/05](docs/05-ai-3d-rendering-guide.md).

## The property at a glance

| Item | Value |
|------|-------|
| Address | 8220 Hawthorne Ave, Miami Beach, FL 33141 |
| Legal | Lot 5, Block D, Biscayne Beach 3rd Section (PB 47, Pg 103) |
| Type | Single-family residence (CBS), 3 bed / 2 bath, ~2,874 sq ft, built 1955 |
| Lot | **60′ × 150′ ≈ 9,000 sq ft — canal-front (rear on a canal), pool + deck** |
| Flood | **Zone AE, Base Flood Elevation 8.0′** (FIRM 12086C0307L) |
| Jurisdiction | City of Miami Beach + Miami-Dade County (HVHZ) |
| Last sale | ~$1.12M (2015) |

*Lot/flood data above is **confirmed from the boundary survey**. Still verify the
exact zoning district, max height, setbacks and FAR with
[Miami Beach Planning](https://www.miamibeachfl.gov/city-hall/planning/) — see
[docs/01](docs/01-property-analysis.md).*

## 3D model + second-floor design

The model is now built from the architect's sheet **A-1 "EXISTING UNIT FLOOR
PLAN"**, so it carries the house's real rooms instead of an assumed box.

- Open **[`renders/interactive-3d-v2.html`](renders/interactive-3d-v2.html)** to
  orbit the model, toggle the second floor, and switch to *Cutaway plan* to see
  both floor plates with the bearing walls and the new beam line.
- Static views in [`renders/v2/`](renders/v2/), schematic sheets in
  [`renders/plans/`](renders/plans/).
- The design and the reasoning behind it:
  **[docs/16 — Second-Floor Design](docs/16-second-floor-design.md)**.

**Scheme A, "canal house"** — 1,632 sf conditioned + 358 sf terrace: primary
suite and terrace on the canal, two more bedrooms toward the street, the
street-facing corner cut away so the house still reads as one storey from
Hawthorne Ave. The stair is a 17-riser straight run against an existing wall in
the living room. Three of the four second-floor edges land directly on existing
CBS walls; the fourth needs one beam with a 19'-1" maximum clear span.

**The catch is flood, not structure.** At +23.9' to the top of the parapet the
addition fits under a 24' cap — *but only if the existing slab stays where it
is*. If the job is priced at or above 50% of the structure's value it becomes a
"substantial improvement", the slab has to come up to BFE 8.0', and the stack
grows to +27.4' — over the cap. Confirm the district's real height limit and
the 50% valuation **before** paying for schematic design.

**Concept massing only — not photoreal, not for permit.** See
[renders/README](renders/README.md).

## How to use this repo

1. **[docs/01 — Property Analysis](docs/01-property-analysis.md)** — what we know,
   what to verify, how to pull the survey/plat/flood data.
2. **[docs/02 — Zoning & Permits](docs/02-zoning-permits-miami.md)** — Miami Beach
   single-family rules, height/setback/FAR, HVHZ, flood/FEMA, permit path.
3. **[docs/03 — Feasibility](docs/03-feasibility-second-floor.md)** — can the 1955
   structure carry a second floor? Key engineering questions.
4. **[docs/04 — Architect Shortlist](docs/04-architect-shortlist.md)** — vetted
   Miami / Miami Beach firms that do vertical additions, with how to vet them.
5. **[docs/05 — AI & 3D Rendering](docs/05-ai-3d-rendering-guide.md)** — the tools
   and a repeatable workflow to generate your own concept renderings.
6. **[docs/06 — Budget, Timeline & Process](docs/06-budget-timeline-process.md)** —
   ballpark costs, schedule, and the step order so nothing stalls.
7. **[docs/07 — Site Photos & Findings](docs/07-site-photos.md)** — what the actual
   listing photos show and how it shapes the design (build up for the bay views).
8. **[docs/16 — Second-Floor Design](docs/16-second-floor-design.md)** — **the
   design**, drawn on the traced A-1 floor plan: room program, load path, stair,
   and the flood/height go-no-go.

## Status checklist

- [x] Pull official property record + survey + flood zone *(survey reviewed: Lot 60×150, canal-front, Flood AE / BFE 8.0)*
- [ ] Confirm zoning district, max height, setbacks, FAR/lot coverage *(incl. waterfront setback)*
- [ ] Resolve south-line paver/fence encroachment noted on survey
- [x] Generate concept massing *(see `renders/`)*
- [x] Trace the real floor plan from sheet A-1 and rebuild the model on it *(docs/16)*
- [x] Design the second floor — scheme A, 1,632 sf *(docs/16)*
- [ ] **Tape-measure the house** to confirm or rescale the A-1 trace
- [ ] **Get the 50%-of-value number** — it decides whether the slab must come up to BFE
- [ ] Confirm the house is one legal single-family dwelling (sheet A-1 says "unit A")
- [ ] Shortlist 3 architects, request fee proposals
- [ ] Structural feasibility review (can foundation/walls take a 2nd story?)
- [ ] Select architect → schematic design → permit set (signed/sealed)
- [ ] Permit submittal to City of Miami Beach
