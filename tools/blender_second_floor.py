#!/usr/bin/env python3
"""
Blender (bpy) model of 8220 Hawthorne Ave with a second floor built ON the
existing flat roof. Conceptual massing with real materials + physical sky.

Run:  python3 tools/blender_second_floor.py
Outputs photoreal-ish renders into renders/blender/.

Geometry from the survey + listing photos:
  - Lot 60' (x) x 150' (y). Front (y=0)=Hawthorne Ave, rear (y=150)=open bay/west.
  - Existing: low white one-story, FLAT ROOF, ~41'x64' footprint, pool+deck on bay.
  - Proposed: stepped-back 2nd-floor volume on the flat roof + bay-facing terrace.
NOT to scale for permit; massing/visualization only.
"""
import bpy, math, os

# ---------------- scene reset ----------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------- params (feet) ----------------
LOT_W, LOT_D = 60.0, 150.0
PLINTH = 1.5                       # modest finished-floor lift above grade
S1H, S2H = 11.0, 10.0
HX0, HX1 = 9.5, 50.5               # house footprint x
HY0, HY1 = 20.0, 84.0             # house footprint y (front->bay)
ROOF = 0.6
# second floor: stepped back from street, sits on the flat roof
S2X0, S2X1 = 12.0, 48.0
S2Y0, S2Y1 = 34.0, HY1            # opened toward the bay (rear)

def mat(name, color, rough=0.7, metal=0.0, transmission=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    if emit and "Emission Strength" in b.inputs:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = emit
    return m

STUCCO = mat("stucco", (0.93, 0.92, 0.89), rough=0.85)
TRIM   = mat("trim",   (0.06, 0.06, 0.07), rough=0.5)
GLASS  = mat("glass",  (0.05, 0.09, 0.12), rough=0.05, transmission=0.85)
WOOD   = mat("wood",   (0.55, 0.40, 0.24), rough=0.6)
TRAV   = mat("trav",   (0.85, 0.80, 0.72), rough=0.7)
WATER  = mat("water",  (0.02, 0.22, 0.30), rough=0.04, metal=0.0)
POOL   = mat("pool",   (0.05, 0.45, 0.62), rough=0.03)
GRASS  = mat("grass",  (0.30, 0.45, 0.18), rough=0.95)
ROADM  = mat("road",   (0.30, 0.30, 0.32), rough=0.9)
RAILG  = mat("railglass", (0.6, 0.75, 0.85), rough=0.05, transmission=0.9)

def box(x0, x1, y0, y1, z0, z1, m, name="box"):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object; o.name = name
    o.scale = ((x1-x0)/2, (y1-y0)/2, (z1-z0)/2)
    o.location = ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)
    o.data.materials.append(m)
    return o

def plane(x0, x1, y0, y1, z, m, name="plane"):
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.active_object; o.name = name
    o.scale = ((x1-x0)/2, (y1-y0)/2, 1)
    o.location = ((x0+x1)/2, (y0+y1)/2, z)
    o.data.materials.append(m)
    return o

# ---------------- ground / context ----------------
plane(-200, 260, -120, 150, 0.0, GRASS, "grass")
plane(-20, LOT_W+20, -60, 0, 0.02, ROADM, "street")
plane(-260, 320, 150, 520, -0.6, WATER, "bay")
box(0, LOT_W, 149, 150.6, -1.2, 1.6, TRAV, "seawall")

# pool + deck on the bay side
plane(8, 52, 88, 138, 0.05, TRAV, "pooldeck")
box(18, 40, 96, 122, -1.0, 0.18, POOL, "pool")

# ---------------- existing one-story (white, flat roof) ----------------
box(HX0-1.5, HX1+1.5, HY0-1.5, HY1+1.5, 0.0, PLINTH, TRAV, "plinth")
box(HX0, HX1, HY0, HY1, PLINTH, PLINTH+S1H, STUCCO, "story1")
# thin dark fascia + flat roof slab
box(HX0-0.6, HX1+0.6, HY0-0.6, HY1+0.6, PLINTH+S1H, PLINTH+S1H+ROOF, TRIM, "fascia1")
ROOF_Z = PLINTH + S1H + ROOF      # top of existing flat roof — 2nd floor sits here

# window bands (front + bay) on first story, with dark recessed frames
def windows(x0, x1, y, z0, z1, depth=0.3):
    box(x0-0.3, x1+0.3, y-depth-0.15, y+depth+0.15, z0-0.4, z1+0.4, TRIM, "winframe")
    box(x0, x1, y-depth, y+depth, z0, z1, GLASS, "win")
windows(HX0+4, HX1-4, HY0, PLINTH+3.0, PLINTH+8.5)          # front glazing
windows(HX0+4, HX1-4, HY1, PLINTH+3.0, PLINTH+8.5)          # bay glazing

# front driveway pavers + entry colonnade (matches the photo's column screen)
plane(13, 47, 0, 19, 0.03, ROADM, "driveway")
for cx in range(19, 30, 2):
    box(cx-0.25, cx+0.25, HY0-0.4, HY0+0.4, PLINTH, PLINTH+S1H, STUCCO, "col")
box(22.5, 25.5, HY0-0.2, HY0+0.2, PLINTH, PLINTH+7, WOOD, "frontdoor")

# ---------------- proposed SECOND FLOOR on the flat roof ----------------
box(S2X0, S2X1, S2Y0, S2Y1, ROOF_Z, ROOF_Z+S2H, STUCCO, "story2")
box(S2X0-0.6, S2X1+0.6, S2Y0-0.6, S2Y1+0.6, ROOF_Z+S2H, ROOF_Z+S2H+ROOF, TRIM, "fascia2")
# black window reveals on the second floor (street + bay)
windows(S2X0+3, S2X1-3, S2Y0, ROOF_Z+2.5, ROOF_Z+8.0)      # street-facing
windows(S2X0+3, S2X1-3, S2Y1, ROOF_Z+2.5, ROOF_Z+8.0)      # bay-facing (the view)
# wood-accent band wrapping the bay face of the 2nd floor
box(S2X0, S2X1, S2Y1-0.25, S2Y1+0.25, ROOF_Z+8.2, ROOF_Z+9.4, WOOD, "woodband")

# rooftop terrace over the stepped-back (street) portion
plane(HX0, HX1, HY0, S2Y0, ROOF_Z+0.05, TRAV, "frontterrace")
# PRIMARY-SUITE TERRACE cantilevered toward the bay
box(S2X0, S2X1, HY1, HY1+9, ROOF_Z, ROOF_Z+0.5, WOOD, "bayterrace")
box(S2X0, S2X1, HY1+8.6, HY1+9.0, ROOF_Z, ROOF_Z+3.4, RAILG, "bayrail")

# ---------------- sky + sun (golden hour over the bay/west) ----------------
world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
wn = world.node_tree.nodes; wl = world.node_tree.links
sky = wn.new("ShaderNodeTexSky"); sky.sky_type = 'MULTIPLE_SCATTERING'
for attr, val in (("sun_elevation", math.radians(12)),
                  ("sun_rotation", math.radians(95)),
                  ("air_density", 2.0), ("dust_density", 2.5)):
    try: setattr(sky, attr, val)
    except Exception: pass
bg = wn.get("Background"); bg.inputs["Strength"].default_value = 1.0
wl.new(sky.outputs[0], bg.inputs[0])

bg.inputs["Strength"].default_value = 0.6
sun = bpy.data.lights.new("sun", 'SUN'); sun.energy = 3.0
sun.angle = math.radians(1.5)
sunobj = bpy.data.objects.new("sun", sun); scene.collection.objects.link(sunobj)
sunobj.rotation_euler = (math.radians(68), 0, math.radians(-35))

# ---- a few palms for scale/context ----
TRUNK = mat("trunk", (0.34, 0.26, 0.16), rough=0.9)
LEAF  = mat("leaf",  (0.16, 0.34, 0.12), rough=0.8)
def palm(x, y, h=18):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=h, location=(x, y, h/2))
    bpy.context.active_object.data.materials.append(TRUNK)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=4.5, location=(x, y, h))
    c = bpy.context.active_object; c.scale = (1, 1, 0.5); c.data.materials.append(LEAF)
for (px, py) in [(5,12),(55,14),(4,70),(56,78),(13,128),(47,131),(6,100)]:
    palm(px, py)

# ---------------- render settings ----------------
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 48
try: bpy.context.view_layer.cycles.use_denoising = True
except Exception: pass
scene.render.resolution_x = 1280
scene.render.resolution_y = 860
scene.render.film_transparent = False
try: scene.view_settings.view_transform = 'AgX'
except Exception: scene.view_settings.view_transform = 'Filmic'
scene.view_settings.exposure = -0.7
scene.view_settings.look = 'AgX - Medium High Contrast' if False else 'None'

def add_cam(name, loc, look):
    cam = bpy.data.cameras.new(name); cam.lens = 35
    o = bpy.data.objects.new(name, cam); scene.collection.objects.link(o)
    o.location = loc
    d = (look[0]-loc[0], look[1]-loc[1], look[2]-loc[2])
    o.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), d[2]),  # not exact; refined below
                        0, math.atan2(d[1], d[0]) - math.pi/2)
    # use track-to via constraint for reliable aim
    tgt = bpy.data.objects.new(name+"_t", None); scene.collection.objects.link(tgt)
    tgt.location = look
    c = o.constraints.new('TRACK_TO'); c.target = tgt
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return o

OUT = os.path.join(os.path.dirname(__file__), "..", "renders", "blender")
os.makedirs(OUT, exist_ok=True)

cams = {
    "01_bay_hero":  ((78, 138, 26), (30, 60, 12)),    # from the water, 3/4, golden hour
    "02_street":    ((-2, -36, 16), (30, 55, 9)),     # from Hawthorne Ave, 3/4
    "03_aerial":    ((-30, -22, 78), (30, 72, 6)),    # high aerial overview
}
for name, (loc, look) in cams.items():
    cam = add_cam(name, loc, look)
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("rendered", name)
print("DONE")
