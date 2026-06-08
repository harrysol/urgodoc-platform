#!/usr/bin/env python3
"""
Schematic floor plans + elevations for 8220 Hawthorne Ave second-floor addition.
Conceptual / schematic design — NOT construction documents.

Footprint & data from survey + listing:
  Lot 60'x150' canal/bay-front; existing 1-story ~2,874 sf; Flood AE / BFE 8.0'.
Outputs PNGs to renders/plans/.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, FancyArrow
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "renders", "plans")
os.makedirs(OUT, exist_ok=True)

WALL = 2.2          # exterior wall lineweight (pts)
PART = 1.3          # partition lineweight
DOOR_C = "#c44"
WIN_C = "#2a7bb8"
INK = "#222"

def room(ax, x, y, w, h, name, area=None, fc="#fbfaf6"):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor="none", zorder=0))
    label = name if area is None else f"{name}\n{area} sf"
    ax.text(x + w/2, y + h/2, label, ha="center", va="center",
            fontsize=7.5, color=INK, zorder=5)

def wall(ax, x0, y0, x1, y1, lw=WALL):
    ax.plot([x0, x1], [y0, y1], color=INK, lw=lw, solid_capstyle="butt", zorder=4)

def door(ax, x, y, w, horiz=True, swing=1):
    """opening of width w with a swing arc; (x,y)=hinge corner."""
    if horiz:
        ax.add_patch(Arc((x, y), 2*w, 2*w, angle=0, theta1=0 if swing>0 else 270,
                         theta2=90 if swing>0 else 360, color=DOOR_C, lw=0.9, zorder=5))
        ax.plot([x, x+swing*w], [y, y], color=DOOR_C, lw=0.9, zorder=5)
    else:
        ax.add_patch(Arc((x, y), 2*w, 2*w, angle=0, theta1=0, theta2=90,
                         color=DOOR_C, lw=0.9, zorder=5))
        ax.plot([x, x], [y, y+w], color=DOOR_C, lw=0.9, zorder=5)

def window(ax, x0, y0, x1, y1):
    ax.plot([x0, x1], [y0, y1], color=WIN_C, lw=3.2, solid_capstyle="butt", zorder=6)

def north(ax, x, y):
    ax.add_patch(FancyArrow(x, y, 0, 6, width=0.4, head_width=2, head_length=2.2,
                            color=INK, zorder=8))
    ax.text(x, y+9, "N", ha="center", fontsize=9, fontweight="bold")

def scalebar(ax, x, y, ft=10):
    ax.plot([x, x+ft], [y, y], color=INK, lw=2)
    for t in (0, ft):
        ax.plot([x+t, x+t], [y-0.6, y+0.6], color=INK, lw=2)
    ax.text(x+ft/2, y-2.4, f"{ft} ft", ha="center", fontsize=7)

def titleblock(ax, title, sub):
    ax.text(2, -8, title, fontsize=12, fontweight="bold")
    ax.text(2, -11.5, sub, fontsize=8, color="#555")
    ax.text(2, -14.5, "8220 Hawthorne Ave, Miami Beach FL 33141  ·  SCHEMATIC DESIGN  ·  "
            "NOT FOR CONSTRUCTION  ·  dimensions approximate", fontsize=7, color="#888")

def frame(title, sub, xlim, ylim):
    fig, ax = plt.subplots(figsize=(9.5, 12), dpi=140)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    titleblock(ax, title, sub)
    return fig, ax

# ===================== GROUND FLOOR (existing, reconfigured) =====================
# Footprint 44 (x) x 64 (y). Front y=0 (Hawthorne), bay y=64.
W, D = 44, 64
fig, ax = frame("GROUND FLOOR PLAN", "Existing ~2,874 sf · 3 bed + den / 3 bath · new stair to 2nd floor",
                (-6, 52), (-16, 80))
# slab outline
ax.add_patch(Rectangle((0, 0), W, D, facecolor="#f4f2ec", edgecolor="none"))
# rooms (front -> bay)
room(ax, 0, 0, 16, 18, "BEDROOM 2", 215)
room(ax, 28, 0, 16, 18, "BEDROOM 3", 215)
room(ax, 16, 0, 12, 12, "ENTRY\nFOYER", 110, fc="#eef2f6")
room(ax, 16, 12, 12, 14, "STAIR\nUP", 70, fc="#f0ead8")
room(ax, 0, 18, 14, 14, "DEN /\nOFFICE", 175)
room(ax, 30, 18, 14, 18, "KITCHEN", 235)
room(ax, 14, 26, 16, 10, "HALL / DINING", 150, fc="#fbfaf6")
room(ax, 0, 32, 14, 12, "BATH /\nLAUNDRY", 150, fc="#eef2f6")
room(ax, 4, 36, 36, 28, "GREAT ROOM\n(LIVING / DINING)\n— opens to pool & bay —", 900, fc="#fbfaf6")
# exterior walls
for (x0,y0,x1,y1) in [(0,0,W,0),(W,0,W,D),(W,D,0,D),(0,D,0,0)]:
    wall(ax, x0,y0,x1,y1)
# a few partitions
wall(ax,16,0,16,18,PART); wall(ax,28,0,28,18,PART); wall(ax,16,12,28,12,PART)
wall(ax,0,18,W,18,PART); wall(ax,30,18,30,36,PART); wall(ax,14,18,14,44,PART)
wall(ax,0,32,14,32,PART); wall(ax,4,36,W,36,PART)
# doors
door(ax,22,0,3,horiz=True,swing=1)          # front entry
door(ax,16,28,3,horiz=False)                # to great room
door(ax,18,12,3,horiz=True)
# windows (exterior glazing) — lots toward bay
window(ax,6,64,38,64)                        # rear wall to bay/pool (big glass)
window(ax,2,0,12,0); window(ax,32,0,42,0)    # front bedrooms
window(ax,0,40,0,60); window(ax,W,40,W,60)   # side great-room glazing
# pool reference (dashed, beyond rear)
ax.add_patch(Rectangle((10,70),24,6, fill=False, ls="--", ec="#2a7bb8"))
ax.text(22,73,"POOL / DECK / BAY  ▶", ha="center", fontsize=7, color="#2a7bb8")
north(ax, 48, 60); scalebar(ax, 0, -4)
ax.text(W/2,-1.5,"HAWTHORNE AVE  ·  circular driveway / 2 cars", ha="center", fontsize=7, color="#666")
fig.savefig(os.path.join(OUT,"ground_floor.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

# ===================== SECOND FLOOR (NEW) =====================
# Stepped back from street: footprint x 6..40 (34), y 18..64 (46) ≈ 1,200 sf
fig, ax = frame("SECOND FLOOR PLAN (NEW)", "New ~1,200 sf · primary suite + guest + office · west bay terrace",
                (-6, 52), (-16, 84))
ax.add_patch(Rectangle((6,18), 34, 46, facecolor="#f4f2ec", edgecolor="none"))
# front rooftop terrace over the stepped-back portion (open below = setback)
ax.add_patch(Rectangle((0,0), W, 18, facecolor="#eaf0f4", edgecolor="none"))
ax.text(W/2,9,"ROOFTOP TERRACE\n(over stepped-back area)", ha="center", va="center",
        fontsize=7, color="#3a6b8a")
# rooms
room(ax, 6, 18, 14, 16, "BEDROOM 4 /\nGUEST", 220)
room(ax, 24, 18, 16, 16, "OFFICE /\nLOFT", 250, fc="#eef2f6")
room(ax, 18, 34, 10, 8, "STAIR /\nLANDING", 70, fc="#f0ead8")
room(ax, 6, 42, 22, 22, "PRIMARY\nBEDROOM", 480, fc="#fbfaf6")
room(ax, 28, 42, 12, 12, "PRIMARY\nBATH", 140, fc="#eef2f6")
room(ax, 28, 54, 12, 10, "W.I.\nCLOSET", 110, fc="#f3f3ee")
# exterior walls (the 2nd-floor box)
for (x0,y0,x1,y1) in [(6,18,40,18),(40,18,40,64),(40,64,6,64),(6,64,6,18)]:
    wall(ax, x0,y0,x1,y1)
wall(ax,6,34,40,34,PART); wall(ax,20,18,20,34,PART); wall(ax,28,42,28,64,PART)
wall(ax,6,42,28,42,PART); wall(ax,28,54,40,54,PART)
door(ax,16,42,3,horiz=True)
# big west-facing glass to terrace
window(ax,8,64,38,64)
window(ax,6,46,6,60); window(ax,40,46,40,60)
# bay terrace (cantilever toward water)
ax.add_patch(Rectangle((6,64),34,9, facecolor="#e8d8bf", edgecolor="#9c7d4f"))
ax.text(23,68.5,"WEST BAY TERRACE  ·  glass rail  ·  ◀ sunset views", ha="center",
        fontsize=7, color="#7a5a2a")
north(ax, 48, 60); scalebar(ax, 0, -4)
fig.savefig(os.path.join(OUT,"second_floor.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

# ===================== ELEVATIONS =====================
fig, ax = plt.subplots(figsize=(12, 9), dpi=140)
ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-6, 120); ax.set_ylim(-10, 46)

def elevation(ox, title, bay=False):
    g = 0; pl = 2; s1 = pl+11; rf1 = s1+0.8; s2 = rf1+10; rf2 = s2+0.8
    # grade
    ax.plot([ox-2, ox+46], [g, g], color="#5a4", lw=2)
    # BFE dashed
    ax.plot([ox-2, ox+46], [pl, pl], color="#b00", lw=0.8, ls="--")
    ax.text(ox+46.5, pl, "BFE 8.0'", fontsize=6, color="#b00", va="center")
    # first story (full width 44)
    ax.add_patch(Rectangle((ox,pl),44,s1-pl, facecolor="#f3f1ea", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((ox-0.7,s1),45.4,rf1-s1, facecolor="#222", ec="none"))  # fascia
    # second story stepped back (x +6..40 width 34) sitting on roof
    ax.add_patch(Rectangle((ox+6,rf1),34,s2-rf1, facecolor="#f5f3ec", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((ox+5.3,s2),35.4,rf2-s2, facecolor="#222", ec="none"))
    # windows
    if bay:
        # big glass both floors + terrace rail
        ax.add_patch(Rectangle((ox+3,pl+2),38,7, facecolor="#bcd3e6", ec="#2a6", lw=0.5))
        ax.add_patch(Rectangle((ox+9,rf1+2),28,6.5, facecolor="#bcd3e6", ec="#2a6", lw=0.5))
        ax.add_patch(Rectangle((ox+6,rf1),34,0.5, facecolor="#c8a978"))  # terrace edge
        ax.plot([ox+6,ox+40],[rf1+3.4,rf1+3.4], color="#9fc3dd", lw=1.2)  # glass rail top
        for gx in range(0,35,4):
            ax.plot([ox+6+gx,ox+6+gx],[rf1,rf1+3.4], color="#9fc3dd", lw=0.4)
    else:
        for wx in (4,16,30):
            ax.add_patch(Rectangle((ox+wx,pl+3),8,5.5, facecolor="#cfe0ee", ec="#357", lw=0.5))
        # entry column screen
        for cx in range(18,29,2):
            ax.plot([ox+cx,ox+cx],[pl,s1], color="#888", lw=1.4)
        for wx in (9,25):
            ax.add_patch(Rectangle((ox+wx,rf1+2.5),9,5, facecolor="#cfe0ee", ec="#357", lw=0.5))
    # height dim
    ax.annotate("", (ox+47,g),(ox+47,rf2), arrowprops=dict(arrowstyle="<->",color="#777",lw=0.8))
    ax.text(ox+48,rf2/2, f"~{rf2:.0f}' to top", fontsize=6, color="#777", rotation=90, va="center")
    ax.text(ox+22,-4, title, ha="center", fontsize=10, fontweight="bold")

elevation(0, "FRONT ELEVATION (Hawthorne Ave)")
elevation(66, "REAR ELEVATION (Bay / West)", bay=True)
ax.text(60, 44, "8220 Hawthorne Ave — SCHEMATIC ELEVATIONS — second floor on existing flat roof (stepped back) — NOT FOR CONSTRUCTION",
        ha="center", fontsize=8, color="#555")
fig.savefig(os.path.join(OUT,"elevations.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

print("wrote ground_floor.png, second_floor.png, elevations.png ->", OUT)
