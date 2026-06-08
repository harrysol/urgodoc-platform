#!/usr/bin/env python3
"""
3D massing study for 8220 Hawthorne Ave, Miami Beach FL 33141.

Builds a conceptual (NOT permit-grade) 3D massing of the existing one-story
canal-front home and a proposed second-floor addition, from the real survey:
  - Lot: 60.0 ft wide (Hawthorne frontage) x 150.0 ft deep, rear on a CANAL
  - Flood Zone AE, Base Flood Elevation 8.0 ft (NGVD)
  - Existing: one-story CBS residence ~2,874 sf, pool + wood deck toward canal

Renders street-view and aerial views of EXISTING vs PROPOSED to PNG.
Dimensions are approximate for massing only.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ---- Site parameters (feet), origin at front-left corner on Hawthorne Ave ----
LOT_W, LOT_D = 60.0, 150.0          # width (x), depth (y); front y=0, canal y=150
SIDE_SETBACK = 7.5
FRONT_SETBACK = 20.0
GRADE = 0.0
BFE = 8.0                            # finished floor raised to base flood elevation
FF = BFE                            # ground-floor finished floor height above grade
STORY1_H = 11.0                     # first floor height
STORY2_H = 10.0                     # second floor height
STEP_BACK = 8.0                     # 2nd floor stepped back from front for code/aesthetics

# House footprint (approx from survey: front-central, ~2,800 sf)
HX0, HX1 = SIDE_SETBACK + 2, LOT_W - SIDE_SETBACK - 2     # ~44 ft wide
HY0, HY1 = FRONT_SETBACK, FRONT_SETBACK + 64             # 64 ft deep

# Second-floor footprint (stepped back from the front; partial coverage shown full)
S2X0, S2X1 = HX0, HX1
S2Y0, S2Y1 = HY0 + STEP_BACK, HY1

# Pool + deck toward canal
PX0, PX1, PY0, PY1 = 18, 42, 95, 118


def box(ax, x0, x1, y0, y1, z0, z1, color, alpha=1.0, edge="k", lw=0.6):
    """Draw a rectangular box as 6 quad faces."""
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    v = np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],
                  [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]])
    faces = [[v[0],v[1],v[2],v[3]], [v[4],v[5],v[6],v[7]],
             [v[0],v[1],v[5],v[4]], [v[2],v[3],v[7],v[6]],
             [v[1],v[2],v[6],v[5]], [v[0],v[3],v[7],v[4]]]
    pc = Poly3DCollection(faces, alpha=alpha, linewidths=lw, edgecolors=edge)
    pc.set_facecolor(color)
    ax.add_collection3d(pc)


def flat(ax, x0, x1, y0, y1, z, color, alpha=1.0):
    v = [[x0,y0,z],[x1,y0,z],[x1,y1,z],[x0,y1,z]]
    pc = Poly3DCollection([v], alpha=alpha, linewidths=0)
    pc.set_facecolor(color)
    ax.add_collection3d(pc)


def build(ax, proposed: bool):
    # Ground / lot
    flat(ax, 0, LOT_W, 0, LOT_D, GRADE, "#cfe3c0")            # grass
    flat(ax, 0, LOT_W, LOT_D, LOT_D + 18, GRADE, "#5fa8d3")   # canal water
    flat(ax, 0, LOT_W, -16, 0, GRADE, "#b9b9b9")              # Hawthorne Ave
    box(ax, PX0-5, PX1+5, PY1, PY1+12, GRADE, GRADE+0.6, "#c8a978", 1.0, edge="#9c7d4f", lw=0.4)  # wood deck
    box(ax, PX0, PX1, PY0, PY1, GRADE, GRADE+1.0, "#37a3d6", 1.0, edge="#2a7ba8", lw=0.4)         # pool
    # Raised finished-floor platform (flood AE / BFE 8.0)
    box(ax, HX0-2, HX1+2, HY0-2, HY1+2, GRADE, FF, "#d9d2c5", 1.0)
    # First story
    box(ax, HX0, HX1, HY0, HY1, FF, FF+STORY1_H, "#f3f1ea", 1.0)
    # Flat roof slab for first story (only where no second floor)
    if proposed:
        # Second story (stepped back), wood-accent tone
        box(ax, S2X0, S2X1, S2Y0, S2Y1, FF+STORY1_H, FF+STORY1_H+STORY2_H,
            "#e7d8bf", 1.0)
        # roof slab over second story
        flat(ax, S2X0, S2X1, S2Y0, S2Y1, FF+STORY1_H+STORY2_H, "#cfc7b6")
        # front terrace on top of stepped-back portion (rooftop over step)
        flat(ax, HX0, HX1, HY0, S2Y0, FF+STORY1_H, "#bfcad6")
    else:
        flat(ax, HX0, HX1, HY0, HY1, FF+STORY1_H, "#cfc7b6")


def style(ax, title):
    ax.set_box_aspect((LOT_W, LOT_D, 60))
    ax.set_xlim(0, LOT_W); ax.set_ylim(-16, LOT_D+18); ax.set_zlim(0, 60)
    ax.set_axis_off()
    ax.set_title(title, fontsize=13, fontweight="bold", pad=2)


def render(proposed, elev, azim, fname, title):
    fig = plt.figure(figsize=(9, 9), dpi=130)
    ax = fig.add_subplot(111, projection="3d")
    build(ax, proposed)
    style(ax, title)
    ax.view_init(elev=elev, azim=azim)
    fig.text(0.5, 0.035,
             "8220 Hawthorne Ave, Miami Beach FL 33141  |  Lot 60'x150', canal-front  |  "
             "Flood AE, BFE 8.0'  |  CONCEPT MASSING - not to scale, not for permit",
             ha="center", fontsize=8, color="#555")
    fig.savefig(fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", fname)


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "renders")
    os.makedirs(out, exist_ok=True)
    # Street view from Hawthorne Ave (front), 3/4 left
    render(False, 14, -70, f"{out}/existing_street.png",
           "EXISTING - One Story (from Hawthorne Ave)")
    render(True, 14, -70, f"{out}/proposed_street.png",
           "PROPOSED - Two Story (from Hawthorne Ave)")
    # Aerial 3/4 showing canal + pool
    render(False, 50, -60, f"{out}/existing_aerial.png",
           "EXISTING - Aerial (canal at rear)")
    render(True, 50, -60, f"{out}/proposed_aerial.png",
           "PROPOSED - Aerial w/ Second Floor (canal at rear)")
