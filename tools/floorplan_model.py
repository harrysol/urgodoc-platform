#!/usr/bin/env python3
"""
Build the 3D model of 8220 Hawthorne Ave from the TRACED sheet-A-1 floor plan
(tools/house_data.py) plus the proposed second floor, and render it.

Outputs
  renders/plans/a1_existing_traced.png    ground floor, traced + dimensioned
  renders/plans/a1_second_floor.png       proposed second floor plan
  renders/plans/a1_stacking.png           2nd floor over the existing bearing walls
  renders/plans/a1_section.png            height stack / section diagram
  renders/v2/hero_canal.png               3D from the canal (rear)
  renders/v2/street.png                   3D from Hawthorne Ave (front)
  renders/v2/aerial.png                   3D aerial three-quarter
  renders/v2/existing_street.png          3D existing one-story, same camera
  cad/8220_hawthorne_from_plan.glb        model export

No Blender / GPU needed: a small perspective painter's-algorithm rasteriser
draws into matplotlib, so this runs anywhere numpy + matplotlib + trimesh do.

    python3 tools/floorplan_model.py
"""
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Rectangle, FancyArrow

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import house_data as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANS = os.path.join(ROOT, "renders", "plans")
V2 = os.path.join(ROOT, "renders", "v2")
CAD = os.path.join(ROOT, "cad")
for d in (PLANS, V2, CAD):
    os.makedirs(d, exist_ok=True)

# --------------------------------------------------------------- palette
STUCCO   = "#eceae4"
STUCCO2  = "#e2dfd7"
TRIM     = "#22242a"
GLASS    = "#33495c"
WOOD     = "#b08654"
DECK     = "#c2a274"
WATER    = "#3f7f9c"
POOLW    = "#3fa8cf"
GRASS    = "#8fae6b"
ROAD     = "#9c9c9e"
ROOFC    = "#cfcdc6"
NEW      = "#f6f2ea"

# ============================================================ 3D scene helpers
FACES = []          # (verts Nx3 float, rgb color str, edge color or None, lw)

def quad(p0, p1, p2, p3, color, edge=None, lw=0.4):
    FACES.append((np.array([p0, p1, p2, p3], float), color, edge, lw))

def poly(pts, color, edge=None, lw=0.4):
    FACES.append((np.array(pts, float), color, edge, lw))

def prism(outline, z0, z1, color, top=None, edge=None, lw=0.4):
    """Extrude a closed 2-D outline [(x,y),...] between z0 and z1."""
    n = len(outline)
    for i in range(n):
        x0, y0 = outline[i]; x1, y1 = outline[(i + 1) % n]
        quad((x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1), color, edge, lw)
    poly([(x, y, z1) for x, y in outline], top or color, edge, lw)

def box(x0, x1, y0, y1, z0, z1, color, edge=None, lw=0.4):
    prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, color, edge=edge, lw=lw)

def slab(x0, x1, y0, y1, z, color, n=1):
    """A horizontal plane, optionally subdivided so painter sorting behaves."""
    xs = np.linspace(x0, x1, n + 1); ys = np.linspace(y0, y1, n + 1)
    e = (xs[1] - xs[0]) * 0.004 + 0.02          # overlap: kills anti-alias seams
    for i in range(n):
        for j in range(n):
            quad((xs[i]-e, ys[j]-e, z), (xs[i+1]+e, ys[j]-e, z),
                 (xs[i+1]+e, ys[j+1]+e, z), (xs[i]-e, ys[j+1]+e, z), color)

def opening(wall, a0, a1, sill, head, xmin, xmax, ymin, ymax, base=0.0,
            glass=GLASS, frame=TRIM, out=0.09):
    """Glass panel + frame, sitting just proud of a wall face."""
    z0, z1 = base + sill, base + head
    f = 0.30                                    # frame width
    if wall in ("N", "S"):
        y = ymin - out if wall == "N" else ymax + out
        yf = ymin - out * 0.6 if wall == "N" else ymax + out * 0.6
        quad((a0-f, yf, z0-f), (a1+f, yf, z0-f), (a1+f, yf, z1+f), (a0-f, yf, z1+f), frame)
        quad((a0, y, z0), (a1, y, z0), (a1, y, z1), (a0, y, z1), glass)
        for k in range(1, max(1, int((a1 - a0) // 5))):
            m = a0 + (a1 - a0) * k / max(1, int((a1 - a0) // 5))
            quad((m-.07, y, z0), (m+.07, y, z0), (m+.07, y, z1), (m-.07, y, z1), frame)
    else:
        x = xmin - out if wall == "W" else xmax + out
        xf = xmin - out * 0.6 if wall == "W" else xmax + out * 0.6
        quad((xf, a0-f, z0-f), (xf, a1+f, z0-f), (xf, a1+f, z1+f), (xf, a0-f, z1+f), frame)
        quad((x, a0, z0), (x, a1, z0), (x, a1, z1), (x, a0, z1), glass)
        for k in range(1, max(1, int((a1 - a0) // 5))):
            m = a0 + (a1 - a0) * k / max(1, int((a1 - a0) // 5))
            quad((x, m-.07, z0), (x, m+.07, z0), (x, m+.07, z1), (x, m-.07, z1), frame)

# ------------------------------------------------------------------ rasteriser
def render(path, eye, target, fov=38.0, size=(1600, 1000), sky=("#cfe6f2", "#8dc3e0"),
           sun=(-0.45, -0.6, 0.66), title=None):
    eye = np.array(eye, float); target = np.array(target, float)
    fwd = target - eye; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    sun = np.array(sun, float); sun /= np.linalg.norm(sun)
    f = 1.0 / math.tan(math.radians(fov) / 2)
    aspect = size[0] / size[1]

    drawn = []
    for verts, color, edge, lw in FACES:
        rel = verts - eye
        cam = np.column_stack([rel @ right, rel @ up, rel @ fwd])
        if (cam[:, 2] <= 0.25).any():
            continue
        sx = f / aspect * cam[:, 0] / cam[:, 2]
        sy = f * cam[:, 1] / cam[:, 2]
        n = np.cross(verts[1] - verts[0], verts[2] - verts[0])
        ln = np.linalg.norm(n)
        shade = 1.0
        if ln > 1e-9:
            n = n / ln
            shade = 0.60 + 0.40 * abs(float(n @ sun))
            if abs(n[2]) < 0.2:                      # vertical faces read flatter
                shade = 0.55 + 0.45 * abs(float(n @ sun))
        rgb = np.array(matplotlib.colors.to_rgb(color)) * shade
        drawn.append((float(cam[:, 2].mean()), np.column_stack([sx, sy]),
                      np.clip(rgb, 0, 1), edge, lw))
    drawn.sort(key=lambda t: -t[0])

    fig = plt.figure(figsize=(size[0] / 100, size[1] / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
    ax.axis("off")
    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    ax.imshow(grad, extent=[-1, 1, -1, 1], aspect="auto", origin="lower",
              cmap=matplotlib.colors.LinearSegmentedColormap.from_list("s", [sky[1], sky[0]]),
              zorder=0)
    for _, pts, rgb, edge, lw in drawn:
        ax.add_patch(MplPolygon(pts, closed=True, facecolor=rgb,
                                edgecolor=edge, linewidth=lw if edge else 0, zorder=1))
    if title:
        ax.text(-0.985, -0.96, title, fontsize=11, color="#1c1c1c", zorder=5,
                bbox=dict(boxstyle="round,pad=0.45", fc="#ffffffcc", ec="none"))
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", os.path.relpath(path, ROOT))

# ============================================================ build the scene
def build_site():
    slab(-14, H.LOT_W + 14, -6, H.LOT_D, -0.02, GRASS, n=12)
    slab(-40, H.LOT_W + 40, H.LOT_D, H.LOT_D + 60, 0.06, WATER, n=1)  # canal (rear)
    box(-14, H.LOT_W + 14, H.LOT_D - 1.2, H.LOT_D, -0.4, 1.0, "#c9c5bc")   # seawall cap
    slab(-14, H.LOT_W + 14, -30, -6, 0.0, ROAD, n=3)                  # Hawthorne Ave
    # driveway + entry walk at the street end
    slab(6, 34, -6, 16, 0.02, "#b6b3ae", n=3)
    # pool + deck between the house and the canal
    box(13, 41, 110, 132, 0.0, 0.55, DECK)
    box(17.5, 36.5, 113.5, 128.5, 0.0, 0.62, "#dcd8cf")     # coping
    box(18, 36, 114, 128, 0.0, 0.68, POOLW)                 # water, proud of coping
    for (px, py) in [(4, 104), (54, 100), (6, 132), (52, 134), (2, 40), (57, 46)]:
        box(px - 0.5, px + 0.5, py - 0.5, py + 0.5, 0, 9, "#6b5942")
        for k, r in enumerate([5.5, 4.2, 2.8]):
            box(px - r, px + r, py - r, py + r, 9 + k * 2.2, 11 + k * 2.2, "#4e7a3a")
    for hx in (0.0, H.LOT_W):                                          # side hedges
        box(hx - 1.2, hx + 1.2, 10, H.LOT_D - 8, 0, 4.5, "#54793f")

# house sits inside the lot: west wall 5.6' off the west line, front 20' back
OX, OY = 5.65, 20.0            # offset of house origin within the lot
def hx(x): return OX + x
def hy(y): return OY + (H.D - y)      # plan Y runs to the street, world Y to canal

def env(poly2d):
    return [(hx(x), hy(y)) for x, y in poly2d]

def build_house(second=True, roof=True):
    e1 = env(H.ENVELOPE_1)
    # plinth + ground storey
    prism(e1, 0.0, H.FF1, "#d8d5cd")
    prism(e1, H.FF1, H.EAVE1, STUCCO, edge="#c8c5bd", lw=0.35)
    xs = [p[0] for p in e1]; ys = [p[1] for p in e1]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    # ground-floor glazing (N in plan = canal = max world Y)
    for wall, a0, a1, sl, hh in H.OPENINGS_1:
        if wall == "N":                       # plan-rear = canal = max world Y
            opening("S", hx(a0), hx(a1), sl, hh, x0, x1, y0, hy(0.0), base=H.FF1)
        elif wall == "W":
            opening("W", hy(a1), hy(a0), sl, hh, hx(0.0), x1, y0, y1, base=H.FF1)
        elif wall == "E":
            opening("E", hy(a1), hy(a0), sl, hh, x0, hx(48.7), y0, y1, base=H.FF1)
        elif wall in ("S1", "F", "S2"):       # plan-street = min world Y
            yy = hy({"S1": 58.3, "F": 53.7, "S2": 72.1}[wall])
            opening("N", hx(a0), hx(a1), sl, hh, x0, x1, yy, yy, base=H.FF1)
    # one-storey roof: only where there is no second floor above
    if roof:
        if second:
            # the street end stays one storey: Y 42.0 .. 72.1
            ring = [(0.0, 42.0), (48.7, 42.0), (48.7, 72.1), (36.6, 72.1),
                    (36.6, 53.7), (28.7, 53.7), (28.7, 49.4), (17.5, 49.4),
                    (17.5, 58.3), (0.0, 58.3)]
            prism(env(ring), H.EAVE1, H.EAVE1 + 1.1, ROOFC, edge="#b9b6ae", lw=0.35)
            prism(env(ring), H.EAVE1 + 1.1, H.EAVE1 + 2.9, STUCCO2,
                  top="#b7b4ac", edge="#bab7af", lw=0.35)      # street-end parapet
        else:
            prism(e1, H.EAVE1, H.EAVE1 + 1.1, ROOFC, edge="#b9b6ae", lw=0.35)
            prism(e1, H.EAVE1 + 1.1, H.EAVE1 + 2.9, STUCCO2, top="#b7b4ac",
                  edge="#bab7af", lw=0.35)

    # entry colonnade at the street end (reads in the listing photo)
    cy0, cy1 = hy(72.1) - 7.0, hy(72.1)
    for i in range(5):
        px = hx(2.0 + i * 8.0)
        box(px - 0.55, px + 0.55, cy0 + 0.4, cy0 + 1.5, 0, H.EAVE1 - 0.4, STUCCO2)
    box(hx(0.0), hx(36.6), cy0, cy1, H.EAVE1 - 0.4, H.EAVE1 + 0.5, ROOFC)
    box(hx(0.0), hx(36.6), cy0, cy1, -0.01, 0.35, "#cdc8bd")

    if not second:
        return

    # ---------------------------------------------------------- second floor
    e2 = env(H.ENVELOPE_2)
    xs2 = [p[0] for p in e2]; ys2 = [p[1] for p in e2]
    a0x, a1x, a0y, a1y = min(xs2), max(xs2), min(ys2), max(ys2)
    prism(e2, H.EAVE1, H.FF2, "#dedbd3")                       # floor band
    # solid volume, minus the two terraces which are carved as open decks
    # conditioned volume = the 2nd-floor rectangle minus the two open terraces
    solid = [(0.0, 13.0), (16.0, 13.0), (16.0, 0.0), (48.7, 0.0), (48.7, 28.0),
             (38.0, 28.0), (38.0, 42.0), (0.0, 42.0)]
    prism(env(solid), H.FF2, H.FF2 + H.PLATE2, NEW, edge="#cfcbc2", lw=0.35)
    # terrace decks + glass guardrails
    for tx0, tx1, ty0, ty1 in [(0.0, 16.0, 0.0, 13.0), (38.0, 48.7, 28.0, 42.0)]:
        p = env([(tx0, ty0), (tx1, ty0), (tx1, ty1), (tx0, ty1)])
        prism(p, H.FF2, H.FF2 + 0.25, DECK)
        for i in range(len(p)):
            ax_, ay_ = p[i]; bx_, by_ = p[(i + 1) % len(p)]
            quad((ax_, ay_, H.FF2 + 0.25), (bx_, by_, H.FF2 + 0.25),
                 (bx_, by_, H.FF2 + 3.6), (ax_, ay_, H.FF2 + 3.6), "#9dc3d6")
    # second-floor glazing
    for wall, a0, a1, sl, hh in H.OPENINGS_2:
        if wall == "N":
            opening("S", hx(a0), hx(a1), sl, hh, a0x, a1x, a0y, hy(0.0), base=H.FF2)
        elif wall == "S":
            yy = hy(42.0)
            opening("N", hx(a0), hx(a1), sl, hh, a0x, a1x, yy, yy, base=H.FF2)
        elif wall == "W":
            opening("W", hy(a1), hy(a0), sl, hh, hx(0.0), a1x, a0y, a1y, base=H.FF2)
        elif wall == "E":
            opening("E", hy(a1), hy(a0), sl, hh, a0x, hx(48.7), a0y, a1y, base=H.FF2)
    # flat roof + parapet over the conditioned part
    if roof:
        prism(env(solid), H.FF2 + H.PLATE2, H.ROOF, ROOFC, edge="#b9b6ae", lw=0.35)
        prism(env(solid), H.ROOF, H.PARAPET, STUCCO2, edge="#c2bfb7", lw=0.35)
        # deep shade eyebrow over the canal glass
        box(hx(15.0), hx(39.0), hy(0.0) - 0.2, hy(0.0) + 3.4,
            H.FF2 + H.PLATE2 - 0.9, H.FF2 + H.PLATE2, "#e6e2da")

# ------------------------------------------------------------------- 3D views
def views():
    global FACES
    cam = [
        ("hero_canal.png", (26, 176, 30), (30, 74, 11), 40,
         "PROPOSED — from the canal (rear). Primary suite + terrace face the water."),
        ("street.png", (-8, -44, 19), (28, 58, 9), 42,
         "PROPOSED — from Hawthorne Ave. Second floor stops 30' back; SE corner steps back."),
        ("aerial.png", (-30, -20, 106), (30, 86, 2), 52,
         "PROPOSED — aerial three-quarter. 1,632 sf second floor on the traced footprint."),
    ]
    for name, eye, tgt, fov, cap in cam:
        FACES = []; build_site(); build_house(second=True)
        render(os.path.join(V2, name), eye, tgt, fov, title=cap)
    FACES = []; build_site(); build_house(second=False)
    render(os.path.join(V2, "existing_street.png"), (-8, -44, 19), (28, 58, 9), 42,
           title="EXISTING — one storey, footprint traced from sheet A-1 (2,870 sf).")
    FACES = []; build_site(); build_house(second=False)
    render(os.path.join(V2, "existing_canal.png"), (26, 176, 30), (30, 74, 11), 40,
           title="EXISTING — from the canal.")

# ============================================================== 2-D plan sheets
def plan_axes(ax, title, sub):
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-9, H.W + 9); ax.set_ylim(H.D + 9, -13)     # Y down = canal on top
    ax.text(-8, -9.5, title, fontsize=15, weight="bold", color="#16181d")
    ax.text(-8, -5.5, sub, fontsize=8.5, color="#5c6168")

def draw_outline(ax, outline, lw=2.6, fc="#ffffff", ec="#16181d", z=2, alpha=1.0):
    ax.add_patch(MplPolygon(outline, closed=True, facecolor=fc, edgecolor=ec,
                            linewidth=lw, zorder=z, alpha=alpha))

def _ft(v):
    w = int(v); i = int(round((v - w) * 12))
    if i == 12: w, i = w + 1, 0
    return f"{w}'-{i}\""

def label_room(ax, name, x0, x1, y0, y1, fs=7.6, color="#16181d", sub=None):
    """Name + dimension, auto-shrunk and stacked so narrow rooms do not collide."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, d = x1 - x0, y1 - y0
    dim = sub if sub else f"{_ft(w)} x {_ft(d)}  ·  {w*d:,.0f} sf"
    rot = 90 if (d > w * 1.9 and w < 11) else 0
    span = d if rot else w
    fs = min(fs, max(4.6, span * 0.68))
    fs2 = fs * 0.76
    off = (fs + 1.6) * 0.155 * (1 if rot == 0 else 1)
    if rot:
        ax.text(cx - off, cy, name, ha="center", va="center", fontsize=fs,
                color=color, zorder=6, rotation=90)
        ax.text(cx + off, cy, dim, ha="center", va="center", fontsize=fs2,
                color="#7b8189", zorder=6, rotation=90)
    else:
        ax.text(cx, cy - off, name, ha="center", va="center", fontsize=fs,
                color=color, zorder=6)
        ax.text(cx, cy + off, dim, ha="center", va="center", fontsize=fs2,
                color="#7b8189", zorder=6)

def northarrow(ax, x, y):
    ax.annotate("", xy=(x, y - 7), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color="#16181d", lw=1.4))
    ax.text(x, y - 9.4, "CANAL", ha="center", fontsize=6, color="#16181d")
    ax.text(x, y - 6.6, "(rear)", ha="center", fontsize=5, color="#7b8189")

def scalebar(ax, x, y):
    for i in range(4):
        ax.add_patch(Rectangle((x + i * 5, y), 5, 1.1, facecolor="#16181d" if i % 2 == 0 else "#fff",
                               edgecolor="#16181d", lw=0.7, zorder=6))
    ax.text(x, y + 3.6, "0", fontsize=5.5, ha="center"); ax.text(x + 20, y + 3.6, "20'", fontsize=5.5, ha="center")

def plan_existing():
    fig, ax = plt.subplots(figsize=(9, 12), dpi=170)
    plan_axes(ax, "EXISTING GROUND FLOOR — traced from sheet A-1",
              "8220 Hawthorne Ave, Miami Beach FL 33141  ·  48'-8\" x 72'-1\" envelope  ·  "
              f"{H.AREA_1:,.0f} sf  ·  scale calibrated to the 2,874 sf record — verify with a tape")
    draw_outline(ax, H.ENVELOPE_1, fc="#f7f6f3")
    for name, x0, x1, y0, y1 in H.ROOMS_1:
        fc = "#fdf3e3" if name == "WORK AREA" else "#ffffff"
        ax.add_patch(MplPolygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True,
                                facecolor=fc, edgecolor="#b9bec4", linewidth=0.9, zorder=3))
        label_room(ax, name, x0, x1, y0, y1)
    for wx0, wy0, wx1, wy1, bearing in H.WALLS_1:
        ax.plot([wx0, wx1], [wy0, wy1], color="#16181d" if bearing else "#8a9098",
                lw=2.4 if bearing else 1.2, zorder=5, solid_capstyle="butt")
    ax.add_patch(MplPolygon([(35.5, 11.0), (48.7, 11.0), (48.7, 22.8), (35.5, 22.8)], closed=True,
                            fill=False, edgecolor="#d08a20", lw=1.6, ls=(0, (5, 3)), zorder=7))
    ax.text(49.9, 16.9, "WORK AREA\n(A-1 permit scope)", fontsize=5.8, color="#d08a20", va="center")
    northarrow(ax, H.W + 4.5, H.D + 2); scalebar(ax, 0, H.D + 3)
    ax.text(H.W / 2, H.D + 12.5, "← HAWTHORNE AVE (front)", ha="center", fontsize=6.5, color="#7b8189")
    fig.savefig(os.path.join(PLANS, "a1_existing_traced.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig); print("wrote renders/plans/a1_existing_traced.png")

KIND_FC = {"room": "#ffffff", "wet": "#e8f1f6", "circ": "#f2efe8", "terrace": "#e6efdc"}

def plan_second():
    fig, ax = plt.subplots(figsize=(9, 12), dpi=170)
    plan_axes(ax, "PROPOSED SECOND FLOOR — scheme A, 'canal house'",
              f"{H.AREA_2_COND:,.0f} sf conditioned + {H.AREA_2_TERRACE:,.0f} sf terrace  ·  "
              f"total after addition {H.AREA_1 + H.AREA_2_COND:,.0f} sf  ·  FAR 0.50 on the 9,000 sf lot")
    ax.add_patch(MplPolygon(H.ENVELOPE_1, closed=True, facecolor="#f4f3f0",
                            edgecolor="#c8ccd1", linewidth=1.0, ls=(0, (4, 3)), zorder=1))
    draw_outline(ax, H.ENVELOPE_2, fc="#fbfaf7")
    for name, x0, x1, y0, y1, kind in H.ROOMS_2:
        ax.add_patch(MplPolygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True,
                                facecolor=KIND_FC[kind], edgecolor="#b9bec4",
                                linewidth=0.9, zorder=3,
                                ls="-" if kind != "terrace" else (0, (3, 2))))
        if name == "STAIR":
            continue          # the tread run + UP arrow label it
        label_room(ax, name, x0, x1, y0, y1, fs=7.2,
                   color="#3f6b2e" if kind == "terrace" else "#16181d")
    # stair treads
    s = H.STAIR
    n = s["risers"] - 1
    for i in range(n):
        yy = s["y_bottom"] - (s["y_bottom"] - s["y_top"]) * i / n
        ax.plot([s["x0"], s["x1"]], [yy, yy], color="#8a9098", lw=0.7, zorder=6)
    ax.annotate("", xy=(35.5, 28.8), xytext=(35.5, 41.4),
                arrowprops=dict(arrowstyle="-|>", color="#16181d", lw=1.2), zorder=7)
    ax.text(34.0, 35, "UP 17R", fontsize=5.2, color="#16181d", rotation=90,
            va="center", ha="center", zorder=7)
    ax.plot([H.FRONT_BEAM_Y * 0 + 0, H.W], [42, 42], color="#c0392b", lw=2.2, zorder=8)
    ax.text(H.W / 2, 44.4, "NEW BEAM LINE  —  bears at X = 0 / 17'-6\" / 36'-7\" / 48'-8\"",
            ha="center", fontsize=5.8, color="#c0392b")
    northarrow(ax, H.W + 4.5, H.D + 2); scalebar(ax, 0, H.D + 3)
    fig.savefig(os.path.join(PLANS, "a1_second_floor.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig); print("wrote renders/plans/a1_second_floor.png")

def plan_stacking():
    fig, ax = plt.subplots(figsize=(9, 12), dpi=170)
    plan_axes(ax, "STACKING / LOAD PATH — new floor over existing bearing walls",
              "Green = new load lands on an existing CBS wall.  Red = new beam line, no wall below.")
    draw_outline(ax, H.ENVELOPE_1, fc="#f7f6f3")
    for name, x0, x1, y0, y1 in H.ROOMS_1:
        ax.text((x0+x1)/2, (y0+y1)/2, name, ha="center", va="center", fontsize=5.6,
                color="#aeb4ba", zorder=3)
    ax.add_patch(MplPolygon(H.ENVELOPE_2, closed=True, facecolor="#2e6fb7", alpha=0.16,
                            edgecolor="#2e6fb7", linewidth=2.0, zorder=4))
    ax.text(24, 21, "SECOND FLOOR ABOVE", ha="center", fontsize=8, color="#2e6fb7",
            weight="bold", zorder=6)
    # perimeter that lands on existing exterior walls
    for (a, b) in [((0, 0), (48.7, 0)), ((0, 0), (0, 42)), ((48.7, 0), (48.7, 42))]:
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#2e8b45", lw=4.2, zorder=7,
                solid_capstyle="butt")
    ax.plot([0, 48.7], [42, 42], color="#c0392b", lw=4.2, zorder=7, solid_capstyle="butt")
    for wx0, wy0, wx1, wy1, bearing in H.WALLS_1:
        if bearing:
            ax.plot([wx0, wx1], [wy0, wy1], color="#2e8b45", lw=2.4, zorder=7,
                    ls=(0, (6, 3)), solid_capstyle="butt")
    for x in (0, 17.5, 36.6, 48.7):
        ax.plot([x], [42], marker="s", ms=7, color="#c0392b", zorder=9)
        ax.text(x, 46.5, "COL", ha="center", fontsize=5.2, color="#c0392b")
    ax.text(24, 49.5, "max clear span 19'-1\"  →  ordinary steel, no transfer truss",
            ha="center", fontsize=6.2, color="#c0392b")
    northarrow(ax, H.W + 4.5, H.D + 2); scalebar(ax, 0, H.D + 3)
    fig.savefig(os.path.join(PLANS, "a1_stacking.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig); print("wrote renders/plans/a1_stacking.png")

def section():
    fig, ax = plt.subplots(figsize=(12, 7.2), dpi=170)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-14, 100); ax.set_ylim(-8, 33)
    ax.text(-13, 31.5, "HEIGHT STACK — does two storeys fit under the cap?",
            fontsize=14, weight="bold", color="#16181d")

    def stack(x, ff1, label, cap=24.0, ok=True):
        ff2 = ff1 + H.FLOOR_TO_FLOOR
        top = ff2 + H.PLATE2 + 0.9 + 2.5
        ax.add_patch(Rectangle((x, -3), 34, 3, facecolor="#d8cfc0", edgecolor="none"))
        ax.add_patch(Rectangle((x, 0), 34, ff1, facecolor="#cdcac2", edgecolor="#16181d", lw=0.8))
        ax.add_patch(Rectangle((x, ff1), 34, H.FLOOR_TO_FLOOR, facecolor="#ecebe6",
                               edgecolor="#16181d", lw=0.8))
        ax.add_patch(Rectangle((x + 3, ff2), 28, H.PLATE2, facecolor="#f7f3ea",
                               edgecolor="#16181d", lw=0.8))
        ax.add_patch(Rectangle((x + 3, ff2 + H.PLATE2), 28, 3.4, facecolor="#dedbd3",
                               edgecolor="#16181d", lw=0.8))
        ax.plot([x - 5, x + 40], [cap, cap], color="#c0392b", lw=1.6, ls=(0, (6, 3)))
        ax.text(x + 40.5, cap, f" {cap:.0f}' height cap\n (verify with Planning)",
                fontsize=6.2, color="#c0392b", va="center")
        for z, t in [(0, "grade"), (ff1, f"FF1  +{ff1:.1f}'"), (ff2, f"FF2  +{ff2:.1f}'"),
                     (top, f"parapet  +{top:.1f}'")]:
            ax.plot([x - 4, x], [z, z], color="#7b8189", lw=0.6)
            ax.text(x - 4.4, z, t, fontsize=6.2, ha="right", va="center", color="#3b4046")
        ax.plot([x - 2, x + 40], [H.BFE - 3.5, H.BFE - 3.5], color="#2e6fb7", lw=1.2)
        ax.text(x + 40.5, H.BFE - 3.5, " BFE 8.0' NGVD\n (grade assumed 4.5' NGVD)",
                fontsize=6, color="#2e6fb7", va="center")
        ax.text(x + 17, -6.6, label, ha="center", fontsize=8.5,
                color="#2e8b45" if ok else "#c0392b", weight="bold")
        ax.text(x + 17, top + 2.2, f"{top:.1f}' to top of parapet", ha="center",
                fontsize=7.5, color="#2e8b45" if ok else "#c0392b", weight="bold")

    stack(0, H.FF1, "A — slab stays put  (addition under 50% of value)  ✓ FITS", ok=True)
    stack(50, 4.5, "B — 'substantial improvement' forces the slab up to BFE  ✗ BUSTS THE CAP",
          ok=False)
    fig.text(0.5, 0.015,
             "The go / no-go question is not structural, it is this: if the addition is priced at or above "
             "50% of the structure's value, FEMA / Miami Beach can require the whole house to come up to "
             "BFE — and then two storeys no longer fit under the height cap.",
             ha="center", fontsize=8.5, color="#3b4046")
    fig.savefig(os.path.join(PLANS, "a1_section.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig); print("wrote renders/plans/a1_section.png")

# ------------------------------------------------------------------ GLB export
def export_glb():
    try:
        import trimesh
    except ImportError:
        print("trimesh not installed — skipping GLB"); return
    scene = trimesh.Scene()
    def add(name, x0, x1, y0, y1, z0, z1, rgb):
        if x1 <= x0 or y1 <= y0 or z1 <= z0: return
        m = trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])
        m.visual.vertex_colors = np.tile(np.array(rgb + [255], np.uint8), (len(m.vertices), 1))
        scene.add_geometry(m, node_name=name)
    WH, DK, GL, RF = [236, 234, 228], [178, 132, 84], [70, 100, 125], [205, 203, 196]
    # ground floor as rooms (so the GLB carries the real plan, not one box)
    for name, x0, x1, y0, y1 in H.ROOMS_1:
        add("F1_" + name.replace(" ", "_").replace(".", ""), hx(x0), hx(x1), hy(y1), hy(y0),
            H.FF1, H.EAVE1, WH)
    for name, x0, x1, y0, y1, kind in H.ROOMS_2:
        z1 = H.FF2 + (0.3 if kind == "terrace" else H.PLATE2)
        add("F2_" + name.replace(" ", "_").replace("/", "_").replace(".", ""),
            hx(x0), hx(x1), hy(y1), hy(y0), H.FF2, z1, DK if kind == "terrace" else WH)
    add("F2_roof", hx(0), hx(48.7), hy(42), hy(0), H.FF2 + H.PLATE2, H.PARAPET, RF)
    out = os.path.join(CAD, "8220_hawthorne_from_plan.glb")
    scene.export(out)
    print("wrote", os.path.relpath(out, ROOT))

if __name__ == "__main__":
    plan_existing(); plan_second(); plan_stacking(); section()
    views(); export_glb()
