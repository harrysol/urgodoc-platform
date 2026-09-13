# Source drawings

The architect's sheet the model is traced from.

| File | What it is |
|---|---|
| `A-1_full_sheet.png` | Sheet **A-1 "BACKGROUND"** complete, with title block: 8220 Hawthorne Ave, Miami Beach FL 33141 |
| `A-1_existing_unit_floor_plan.png` | The same sheet zoomed to the plan — this is what `tools/house_data.py` is traced from |

Scale on the sheet is **1/4" = 1'-0"**, but the supplied copies carry no legible
dimension strings, so the trace was calibrated by area against the 2,874 sf
public record (see [../16](../16-second-floor-design.md) §1). If you obtain a
dimensioned copy or a tape-measured as-built, update the coordinates in
`tools/house_data.py` and re-run the three tools — the plans, renders, GLB and
interactive viewer all regenerate from that one file.
