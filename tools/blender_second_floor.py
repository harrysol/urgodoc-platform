#!/usr/bin/env python3
"""
8220 Hawthorne Ave - second floor, modeled to the house's ACTUAL massing:
low recessed left/center (with entry colonnade) + taller projecting right block,
white stucco, black-framed windows with mullions+sills, flat roofs, second floor
stepped back with a west bay terrace. Real LiDAR scale. Renders + exports GLB.
"""
import bpy, math, os
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

LOT_W, LOT_D = 60.0, 150.0
PL, S1, S2, RF = 1.5, 11.0, 10.0, 0.6
# ground masses (front articulation): right block projects forward, left recessed
LX0,LX1, LY0,LY1 = 6,32, 24,72     # left/center mass (recessed front)
RX0,RX1, RY0,RY1 = 32,54, 18,74    # right block (projects forward, taller)
RH = 12.5                           # right block height (taller)
ROOFL = PL+S1+RF                    # left roof top
ROOFR = PL+RH+RF                    # right roof top
# second floor on the (higher) roof, stepped back, over center+right
S2X0,S2X1, S2Y0,S2Y1 = 16,50, 34,74

def M(n,c,r=0.7,me=0.0,tr=0.0,bump=0.0):
    m=bpy.data.materials.new(n); m.use_nodes=True; nt=m.node_tree; b=nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value=(*c,1); b.inputs["Roughness"].default_value=r
    b.inputs["Metallic"].default_value=me
    if "Transmission Weight" in b.inputs: b.inputs["Transmission Weight"].default_value=tr
    if bump:
        nz=nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value=50
        bp=nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value=bump
        nt.links.new(nz.outputs["Fac"],bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"],b.inputs["Normal"])
    return m
STUCCO=M("stucco",(0.93,0.92,0.89),0.8,bump=0.04); TRIM=M("trim",(0.04,0.04,0.05),0.4,me=0.6)
GLASS=M("glass",(0.07,0.12,0.16),0.05,tr=0.9); WOOD=M("wood",(0.5,0.34,0.19),0.45)
TRAV=M("trav",(0.84,0.79,0.71),0.6,bump=0.02); WATER=M("water",(0.02,0.2,0.28),0.02)
POOL=M("pool",(0.05,0.42,0.58),0.02); GRASS=M("grass",(0.22,0.4,0.14),0.95,bump=0.03)
HEDGE=M("hedge",(0.16,0.33,0.12),0.9,bump=0.08); ROAD=M("road",(0.3,0.3,0.32),0.85)
LEAF=M("leaf",(0.15,0.34,0.11),0.8); TRUNK=M("trunk",(0.34,0.26,0.16),0.9)

def box(x0,x1,y0,y1,z0,z1,m,n="b"):
    bpy.ops.mesh.primitive_cube_add(size=1); o=bpy.context.active_object; o.name=n
    o.scale=((x1-x0)/2,(y1-y0)/2,(z1-z0)/2); o.location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)
    o.data.materials.append(m); return o
def plane(x0,x1,y0,y1,z,m,n="p"):
    bpy.ops.mesh.primitive_plane_add(size=1); o=bpy.context.active_object; o.name=n
    o.scale=((x0-x1)/-2,(y1-y0)/2,1); o.location=((x0+x1)/2,(y0+y1)/2,z); o.data.materials.append(m); return o

def window(axis,pos,a0,a1,z0,z1,reveal=0.35):
    """one window: black frame + sill + 2x3 mullion grid + glass, recessed."""
    w=a1-a0; h=z1-z0
    if axis=='y':
        box(a0-reveal,a1+reveal,pos-0.3,pos+0.3,z0-reveal,z1+reveal,TRIM,"frame")
        box(a0,a1,pos-0.12,pos+0.12,z0,z1,GLASS,"glass")
        box(a0-reveal,a1+reveal,pos-0.35,pos+0.1,z0-reveal-0.25,z0-reveal,TRAV,"sill")
        for vx in [a0+w/3,a0+2*w/3]: box(vx-0.06,vx+0.06,pos-0.16,pos+0.16,z0,z1,TRIM,"mull")
        box(a0,a1,pos-0.16,pos+0.16,z0+h/2-0.05,z0+h/2+0.05,TRIM,"mull")
    else:
        box(pos-0.3,pos+0.3,a0-reveal,a1+reveal,z0-reveal,z1+reveal,TRIM,"frame")
        box(pos-0.12,pos+0.12,a0,a1,z0,z1,GLASS,"glass")
        for vy in [a0+w/3,a0+2*w/3]: box(pos-0.16,pos+0.16,vy-0.06,vy+0.06,z0,z1,TRIM,"mull")
        box(pos-0.16,pos+0.16,a0,a1,z0+h/2-0.05,z0+h/2+0.05,TRIM,"mull")

def wins_along(axis,pos,a0,a1,z0,z1,n,gap=2.0):
    seg=(a1-a0)/n
    for i in range(n): window(axis,pos,a0+i*seg+gap/2,a0+(i+1)*seg-gap/2,z0,z1)

def railing(x0,x1,y,z):
    box(x0,x1,y-0.1,y+0.1,z+3.2,z+3.45,WOOD,"rt")
    box(x0,x1,y-0.05,y+0.05,z+0.2,z+3.2,GLASS,"rg")
    for gx in [x0+(x1-x0)*t/8 for t in range(9)]: box(gx-0.07,gx+0.07,y-0.1,y+0.1,z,z+3.4,TRIM,"po")
def palm(x,y,h=20):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55,depth=h,location=(x,y,h/2)); bpy.context.active_object.data.materials.append(TRUNK)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=4.5,location=(x,y,h)); c=bpy.context.active_object; c.scale=(1,1,0.45); c.data.materials.append(LEAF)

# ---- site ----
plane(-200,260,-120,150,0,GRASS,"grass"); plane(0,LOT_W,-60,0,0.02,ROAD,"st")
plane(-260,320,150,520,-0.5,WATER,"bay"); box(0,LOT_W,148.5,150.5,-1.2,1.4,TRAV,"sea")
plane(12,48,86,140,0.05,TRAV,"deck"); box(18,40,96,124,-1,0.15,POOL,"pool")
box(2.5,4,22,140,0,3,HEDGE,"hW"); box(56,57.5,18,140,0,3,HEDGE,"hE"); plane(12,48,2,18,0.04,ROAD,"drive")

# ---- ground: two articulated masses ----
box(LX0-1.2,RX1+1.2,min(LY0,RY0)-1.2,RY1+1.2,0,PL,TRAV,"plinth")
box(LX0,LX1,LY0,LY1,PL,PL+S1,STUCCO,"leftmass")
box(LX0-0.6,LX1+0.6,LY0-0.6,LY1+0.6,PL+S1,ROOFL,TRIM,"fasciaL")
box(RX0,RX1,RY0,RY1,PL,PL+RH,STUCCO,"rightblock")
box(RX0-0.6,RX1+0.6,RY0-0.6,RY1+0.6,PL+RH,ROOFR,TRIM,"fasciaR")
# entry: recessed wall + colonnade across the left/center front
for cx in [LX0+3+ i*2.3 for i in range(8)]:
    if cx<LX1-2: box(cx-0.22,cx+0.22,LY0-3,LY0-2.6,PL,PL+S1,STUCCO,"col")
box(LX0+9,LX1-9,LY0-0.2,LY0+0.2,PL,PL+7.5,WOOD,"door")
# windows
wins_along('y',LY0,LX0+2,LX1-2,PL+3,PL+8.5,2)              # left/center front
wins_along('y',RY0,RX0+2,RX1-2,PL+3,PL+9,2)               # right block front (big)
wins_along('x',RX1,RY0+5,RY1-5,PL+3,PL+9,3)               # right block east side
wins_along('y',RY1,RX0+2,RX1-2,PL+3,PL+9.5,2)             # right block bay side
wins_along('x',LX0,LY0+4,LY1-4,PL+3,PL+8,2)               # left west side

# ---- second floor on the roof, stepped back ----
ZB=ROOFR
box(S2X0,S2X1,S2Y0,S2Y1,ZB,ZB+S2,STUCCO,"story2")
box(S2X0-0.6,S2X1+0.6,S2Y0-0.6,S2Y1+0.6,ZB+S2,ZB+S2+RF,TRIM,"fascia2")
wins_along('y',S2Y0,S2X0+2,S2X1-2,ZB+2.5,ZB+8,3)          # street side
wins_along('y',S2Y1,S2X0+2,S2X1-2,ZB+2,ZB+8.5,4)          # bay side (the view)
wins_along('x',S2X1,S2Y0+4,S2Y1-4,ZB+2.5,ZB+8,2)
box(S2X0,S2X1,S2Y1-0.2,S2Y1+0.2,ZB+8.4,ZB+9.3,WOOD,"woodband")
plane(LX0,S2X1,LY0,S2Y0,ROOFL+0.05,TRAV,"frontterr")      # rooftop terrace over step
box(S2X0,S2X1,S2Y1,S2Y1+9,ZB,ZB+0.5,WOOD,"bayterr"); railing(S2X0,S2X1,S2Y1+9,ZB)
for px,py in [(7,12),(53,14),(5,66),(55,70),(10,132),(46,134)]: palm(px,py)

# ---- light + sky ----
wd=bpy.data.worlds.new("W"); sc.world=wd; wd.use_nodes=True; wn=wd.node_tree.nodes; wl=wd.node_tree.links
sky=wn.new("ShaderNodeTexSky"); sky.sky_type='MULTIPLE_SCATTERING'
for a,v in (("sun_elevation",math.radians(11)),("sun_rotation",math.radians(95)),("air_density",1.5),("dust_density",2.5)):
    try: setattr(sky,a,v)
    except: pass
wn["Background"].inputs["Strength"].default_value=0.85; wl.new(sky.outputs[0],wn["Background"].inputs[0])
su=bpy.data.lights.new("s",'SUN'); su.energy=4.0; su.angle=math.radians(1.2); su.color=(1,0.87,0.68)
so=bpy.data.objects.new("s",su); sc.collection.objects.link(so); so.rotation_euler=(math.radians(70),0,math.radians(-32))

# ---- export GLB (the editable/orbitable 3D) ----
CAD=os.path.join(os.path.dirname(__file__),"..","cad"); os.makedirs(CAD,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=os.path.join(CAD,"8220_hawthorne_detailed.glb"),export_format='GLB')

# ---- render ----
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=100
try: bpy.context.view_layer.cycles.use_denoising=True
except: pass
sc.render.resolution_x=1600; sc.render.resolution_y=1000
try: sc.view_settings.view_transform='AgX'
except: pass
sc.view_settings.exposure=-0.5
def cam(n,loc,look):
    cd=bpy.data.cameras.new(n); cd.lens=33; o=bpy.data.objects.new(n,cd); sc.collection.objects.link(o); o.location=loc
    t=bpy.data.objects.new(n+"t",None); sc.collection.objects.link(t); t.location=look
    c=o.constraints.new('TRACK_TO'); c.target=t; c.track_axis='TRACK_NEGATIVE_Z'; c.up_axis='UP_Y'; return o
OUT=os.path.join(os.path.dirname(__file__),"..","renders","blender"); os.makedirs(OUT,exist_ok=True)
for n,(loc,look) in {"01_bay_hero":((86,132,24),(30,55,12)),"02_street":((24,-30,15),(30,52,9)),
                     "03_aerial":((-26,-18,72),(30,66,5))}.items():
    sc.camera=cam(n,loc,look); sc.render.filepath=os.path.join(OUT,n+".png"); bpy.ops.render.render(write_still=True); print("rendered",n)
print("DONE")
