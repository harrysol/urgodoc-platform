#!/usr/bin/env python3
"""
8220 Hawthorne Ave - second floor on the flat roof.
Refined Blender (bpy) model: recessed black-framed windows, glass-rail bay
terrace, PBR materials (stucco/glass/wood/travertine/water), landscaping, and
golden-hour physical-sky lighting. Conceptual visualization, real-scale.
Run: python3 tools/blender_second_floor.py
"""
import bpy, math, os

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---- dims (feet), real scale from LiDAR ----
LOT_W, LOT_D = 60.0, 150.0
PLINTH, S1H, S2H, ROOF = 1.5, 11.0, 10.0, 0.6
HX0, HX1, HY0, HY1 = 6.0, 54.0, 20.0, 74.0       # wide low base ~48x54
S2X0, S2X1, S2Y0, S2Y1 = 14.0, 46.0, 32.0, 74.0  # central upper, stepped back
ROOF_Z = PLINTH + S1H + ROOF

def mat(name, color, rough=0.7, metal=0.0, trans=0.0, bump=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Transmission Weight" in b.inputs: b.inputs["Transmission Weight"].default_value = trans
    if bump:
        n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 60
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

STUCCO=mat("stucco",(0.92,0.91,0.88),0.8,bump=0.05)
TRIM  =mat("trim",(0.05,0.05,0.06),0.4,metal=0.7)
GLASS =mat("glass",(0.06,0.11,0.14),0.05,trans=0.9)
WOOD  =mat("wood",(0.5,0.34,0.19),0.45)
TRAV  =mat("trav",(0.84,0.79,0.71),0.6,bump=0.03)
WATER =mat("water",(0.02,0.20,0.28),0.02)
POOL  =mat("pool",(0.05,0.42,0.58),0.02)
GRASS =mat("grass",(0.22,0.40,0.14),0.95,bump=0.04)
HEDGE =mat("hedge",(0.16,0.33,0.12),0.9,bump=0.1)
ROAD  =mat("road",(0.30,0.30,0.32),0.85)
LEAF  =mat("leaf",(0.15,0.34,0.11),0.8)
TRUNK =mat("trunk",(0.34,0.26,0.16),0.9)

def box(x0,x1,y0,y1,z0,z1,m,name="b"):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=bpy.context.active_object; o.name=name
    o.scale=((x1-x0)/2,(y1-y0)/2,(z1-z0)/2); o.location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)
    o.data.materials.append(m); return o

def plane(x0,x1,y0,y1,z,m,name="p"):
    bpy.ops.mesh.primitive_plane_add(size=1)
    o=bpy.context.active_object; o.name=name
    o.scale=((x1-x0)/2,(y1-y0)/2,1); o.location=((x0+x1)/2,(y0+y1)/2,z)
    o.data.materials.append(m); return o

def win_band(axis, pos, a0, a1, z0, z1, n=5, frame=0.35):
    """row of n recessed glass panels along an axis with black frames.
    axis 'y': wall runs along x at y=pos; axis 'x': wall runs along y at x=pos."""
    seg=(a1-a0)/n
    for i in range(n):
        c0=a0+i*seg+0.6; c1=a0+(i+1)*seg-0.6
        if axis=='y':
            box(c0-frame,c1+frame,pos-0.25,pos+0.25,z0-frame,z1+frame,TRIM,"wf")
            box(c0,c1,pos-0.18,pos+0.18,z0,z1,GLASS,"wg")
        else:
            box(pos-0.25,pos+0.25,c0-frame,c1+frame,z0-frame,z1+frame,TRIM,"wf")
            box(pos-0.18,pos+0.18,c0,c1,z0,z1,GLASS,"wg")

def railing(x0,x1,y,z):
    box(x0,x1,y-0.1,y+0.1,z+3.3,z+3.5,WOOD,"rail_top")
    box(x0,x1,y-0.06,y+0.06,z+0.2,z+3.3,GLASS,"rail_glass")
    for gx in [x0+(x1-x0)*t/6 for t in range(7)]:
        box(gx-0.08,gx+0.08,y-0.1,y+0.1,z,z+3.4,TRIM,"post")

def palm(x,y,h=20):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.6,depth=h,location=(x,y,h/2))
    bpy.context.active_object.data.materials.append(TRUNK)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=4.6,location=(x,y,h))
    c=bpy.context.active_object; c.scale=(1,1,0.45); c.data.materials.append(LEAF)

# ---------- ground / context ----------
plane(-200,260,-120,150,0.0,GRASS,"grass")
plane(0,LOT_W,-60,0,0.02,ROAD,"street")
plane(-260,320,150,520,-0.5,WATER,"bay")
box(0,LOT_W,148.5,150.5,-1.2,1.4,TRAV,"seawall")
plane(12,48,86,140,0.05,TRAV,"pooldeck")
box(18,40,96,124,-1.0,0.15,POOL,"pool")
# hedges along side lot lines + front
for hy in [(22,140)]:
    box(2.5,4.0,hy[0],hy[1],0,3.0,HEDGE,"hedge_W")
    box(56,57.5,hy[0],hy[1],0,3.0,HEDGE,"hedge_E")
plane(12,48,2,18,0.04,ROAD,"driveway")

# ---------- first story ----------
box(HX0-1.5,HX1+1.5,HY0-1.5,HY1+1.5,0,PLINTH,TRAV,"plinth")
box(HX0,HX1,HY0,HY1,PLINTH,PLINTH+S1H,STUCCO,"story1")
box(HX0-0.7,HX1+0.7,HY0-0.7,HY1+0.7,PLINTH+S1H,ROOF_Z,TRIM,"fascia1")
win_band('y',HY0,HX0+3,HX1-3,PLINTH+3,PLINTH+8.5,n=5)          # front
win_band('y',HY1,HX0+3,HX1-3,PLINTH+2.5,PLINTH+9,n=6)          # bay (big)
win_band('x',HX0,HY0+6,HY1-6,PLINTH+3,PLINTH+8,n=4)            # west side
win_band('x',HX1,HY0+6,HY1-6,PLINTH+3,PLINTH+8,n=4)            # east side
# entry colonnade
for cx in range(22,34,2):
    box(cx-0.25,cx+0.25,HY0-0.5,HY0+0.5,PLINTH,PLINTH+S1H,STUCCO,"col")
box(27,31,HY0-0.2,HY0+0.2,PLINTH,PLINTH+7.5,WOOD,"door")

# ---------- second story on the flat roof ----------
box(S2X0,S2X1,S2Y0,S2Y1,ROOF_Z,ROOF_Z+S2H,STUCCO,"story2")
box(S2X0-0.7,S2X1+0.7,S2Y0-0.7,S2Y1+0.7,ROOF_Z+S2H,ROOF_Z+S2H+ROOF,TRIM,"fascia2")
win_band('y',S2Y0,S2X0+2,S2X1-2,ROOF_Z+2.5,ROOF_Z+8,n=4)       # street side
win_band('y',S2Y1,S2X0+2,S2X1-2,ROOF_Z+2,ROOF_Z+8.5,n=5)       # bay side (view)
box(S2X0,S2X1,S2Y1-0.2,S2Y1+0.2,ROOF_Z+8.4,ROOF_Z+9.4,WOOD,"woodband")
# front rooftop terrace over the step + bay terrace cantilever
plane(HX0,HX1,HY0,S2Y0,ROOF_Z+0.05,TRAV,"frontterrace")
box(S2X0,S2X1,HY1,HY1+9,ROOF_Z,ROOF_Z+0.5,WOOD,"bayterrace")
railing(S2X0,S2X1,HY1+9,ROOF_Z)

for (px,py) in [(7,12),(53,14),(5,66),(55,70),(10,132),(46,134),(7,100)]:
    palm(px,py)

# ---------- sky + sun (golden hour over the bay/west) ----------
world=bpy.data.worlds.new("W"); scene.world=world; world.use_nodes=True
wn=world.node_tree.nodes; wl=world.node_tree.links
sky=wn.new("ShaderNodeTexSky"); sky.sky_type='MULTIPLE_SCATTERING'
for a,v in (("sun_elevation",math.radians(9)),("sun_rotation",math.radians(95)),
            ("air_density",1.6),("dust_density",3.0)):
    try: setattr(sky,a,v)
    except: pass
wn.get("Background").inputs["Strength"].default_value=0.8
wl.new(sky.outputs[0],wn.get("Background").inputs[0])
sun=bpy.data.lights.new("sun",'SUN'); sun.energy=4.2; sun.angle=math.radians(1.2)
sun.color=(1.0,0.86,0.66)
so=bpy.data.objects.new("sun",sun); scene.collection.objects.link(so)
so.rotation_euler=(math.radians(72),0,math.radians(-30))

# ---------- render ----------
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=110
try: bpy.context.view_layer.cycles.use_denoising=True
except: pass
scene.render.resolution_x=1600; scene.render.resolution_y=1000
try: scene.view_settings.view_transform='AgX'
except: pass
scene.view_settings.exposure=-0.5

def cam(name,loc,look):
    cd=bpy.data.cameras.new(name); cd.lens=33
    o=bpy.data.objects.new(name,cd); scene.collection.objects.link(o); o.location=loc
    t=bpy.data.objects.new(name+"t",None); scene.collection.objects.link(t); t.location=look
    c=o.constraints.new('TRACK_TO'); c.target=t; c.track_axis='TRACK_NEGATIVE_Z'; c.up_axis='UP_Y'
    return o

OUT=os.path.join(os.path.dirname(__file__),"..","renders","blender"); os.makedirs(OUT,exist_ok=True)
for name,(loc,look) in {
    "01_bay_hero":((86,132,24),(30,55,12)),
    "02_street":((22,-30,15),(30,52,9)),
    "03_aerial":((-26,-18,70),(30,66,5)),
}.items():
    scene.camera=cam(name,loc,look)
    scene.render.filepath=os.path.join(OUT,name+".png")
    bpy.ops.render.render(write_still=True); print("rendered",name)
print("DONE")
