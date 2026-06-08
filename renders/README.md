# Renders — 3D Massing Study

Conceptual 3D massing of 8220 Hawthorne Ave with a proposed second floor, built
from the **boundary survey** (Lot 60′×150′, canal-front, Flood AE / BFE 8.0′).

> ⚠️ **Concept massing only — not to scale, not a permit document and not a
> photoreal render of the actual house.** It shows volume, placement, the
> flood-raised floor, the stepped-back second story, pool, deck and canal. For
> photoreal images of *your* house, run a real photo through one of the AI tools
> in [../docs/05](../docs/05-ai-3d-rendering-guide.md). For stamped drawings, you
> need a licensed architect/engineer ([../docs/04](../docs/04-architect-shortlist.md)).

## Files

| File | What it is |
|------|-----------|
| `interactive-3d-model.html` | **Best one.** Open in any browser → orbit/zoom the model and click **"Toggle Second Floor"** to compare existing vs. proposed. Correct depth + lighting. |
| `existing_street.png` | Existing one-story, viewed from Hawthorne Ave |
| `proposed_street.png` | Proposed two-story, viewed from Hawthorne Ave |
| `existing_aerial.png` | Existing, aerial ¾ (canal at rear) |
| `proposed_aerial.png` | Proposed w/ second floor, aerial ¾ |

## How to view the interactive model

Just open `interactive-3d-model.html` in Chrome/Safari/Edge (it loads three.js
from a CDN, so you need internet the first time). Drag to orbit, scroll to zoom,
right-drag to pan.

## How to regenerate the static PNGs

```bash
pip install numpy matplotlib
python3 tools/render_massing.py    # writes PNGs into renders/
```

## What the model assumes (edit in `tools/render_massing.py`)

- Front setback ~20′, side setbacks ~7.5′ (verify against Miami Beach code)
- Ground floor raised to BFE 8.0′ (flood AE)
- Second story stepped back ~8′ from the front, rooftop terrace over the step
- House footprint ~41′×64′ (≈ existing 2,874 sf) — refine once the architect
  confirms partial vs. full second floor
