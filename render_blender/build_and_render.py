"""Blender (bpy) cinematic renderer for the MuJoCo humanoid golf sim.
    <blender-python> render_blender/build_and_render.py --clip test --res 1280x720 --out golf_render/test [--frames 0-5]
Drives a procedural humanoid with the REAL per-body world poses exported from the MuJoCo sim (swing_v3.npz): shoulders/elbows/wrists/hips/knees/ankles/torso
positions, the club (pose of right_wrist body), and the sim ball motion.  Cosmetic: all surfaces/materials/hands-fingers/head, the course, sky, trees,
camera moves, slow-motion time remap, ball trail styling.  The body is a GENERIC humanoid with Figure/Optimus-like proportions (not an official model)."""
import sys, os, math, argparse, json
import numpy as np
import bpy, bmesh
from mathutils import Vector, Quaternion, Matrix

ap = argparse.ArgumentParser(); ap.add_argument("--clip", default="test"); ap.add_argument("--res", default="1280x720"); ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--out", default="golf_render/test"); ap.add_argument("--frames", default=""); ap.add_argument("--samples", type=int, default=16)
ap.add_argument("--npz", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "swing_v3.npz")); ap.add_argument("--threads", type=int, default=3)
ap.add_argument("--body_map", default="", help="JSON role->body-name overrides, e.g. '{\"pelvis\":\"pelvis\",\"head\":\"head\"}'"); ap.add_argument("--tag", default="")
ap.add_argument("--worker", type=int, default=0); ap.add_argument("--nworkers", type=int, default=1); ap.add_argument("--engine", default="eevee"); ap.add_argument("--save_blend", default="")
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
RW, RH = map(int, a.res.split("x"))
D = np.load(a.npz); NAMES = [str(s) for s in D["body_names"]]; XP, XQ, T, BALL = D["xpos"], D["xquat"], D["t"], D["ball"]
NS = len(T); IMP = int(D["impact_idx"]); bi = {n: i for i, n in enumerate(NAMES)}
# role -> body name in the exported npz. Override with --body_map for a newer body (spine/pelvis yaw/head). Optional roles (pelvis, spine, head) are used when present.
BM = dict(r_sh="right_shoulder", r_el="right_elbow", r_wr="right_wrist", l_sh="left_shoulder", l_el="left_elbow", l_hand="left_hand",
          r_hip="right_hip", r_kn="right_knee", r_an="right_ankle", l_hip="left_hip", l_kn="left_knee", l_an="left_ankle", root="torso", chest="chest", club="right_wrist")
if a.body_map: BM.update(json.loads(a.body_map))
CLUB_SHAFT_LEN = float(np.abs(D["club_shaft_fromto"][5])) if "club_shaft_fromto" in D.files else 1.1
Y_BODY = -0.14   # cosmetic: torso/legs/head sit behind the (real) arm plane y=0 so arms don't pass through the chest

# ---------------------------------------------------------------- helpers
def P(i, name): return XP[i, bi[name]]
def quat_np(i, name): w, x, y, z = XQ[i, bi[name]]; return Quaternion((w, x, y, z))
def lerp_pose(f, name):
    i = int(min(max(math.floor(f), 0), NS - 2)); u = min(max(f - i, 0.0), 1.0)
    return (1 - u) * XP[i, bi[name]] + u * XP[i + 1, bi[name]], quat_np(i, name).slerp(quat_np(i + 1, name), u)
def lerp_ball(f):
    i = int(min(max(math.floor(f), 0), NS - 2)); u = min(max(f - i, 0.0), 1.0); return (1 - u) * BALL[i] + u * BALL[i + 1]

def mat(name, color, rough=0.4, metal=0.0, emit=None, emit_s=0.0, coat=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    for k in ("Coat Weight",):
        if k in b.inputs: b.inputs[k].default_value = coat
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = emit_s
    return m

def capsule_mesh(name, r0, r1, n=24, rings=10):
    """unit-length (z 0..1) tapered capsule, radius r0 at z=0 to r1 at z=1 (scale z by the bone length)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); prof = []
    for k in range(rings + 1):  # bottom hemisphere cap (flattened to unit length scale: caps are shallow)
        a_ = -math.pi / 2 + (math.pi / 2) * k / rings; prof.append((r0 * math.cos(a_), -0.0 + 0.0 + r0 * 0.0 + (r0 * math.sin(a_)) * 0.5))
    for k in range(rings + 1):
        a_ = (math.pi / 2) * k / rings; prof.append((r1 * math.cos(a_), 1.0 + (r1 * math.sin(a_)) * 0.5))
    rows = []
    for rr, zz in prof:
        rows.append([bm.verts.new((rr * math.cos(2 * math.pi * j / n), rr * math.sin(2 * math.pi * j / n), zz)) for j in range(n)])
    for r in range(len(rows) - 1):
        for j in range(n): 
            try: bm.faces.new((rows[r][j], rows[r][(j + 1) % n], rows[r + 1][(j + 1) % n], rows[r + 1][j]))
            except ValueError: pass
    bm.normal_update(); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me

def obj(name, me, m, parent=None):
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if m is not None: o.data.materials.append(m)
    return o

def prim(kind, name, m, size=(1, 1, 1), seg=32):
    if kind == "sphere": bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=1)
    elif kind == "cube": bpy.ops.mesh.primitive_cube_add(size=2)
    elif kind == "cyl": bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=1, depth=2)
    elif kind == "cone": bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=1, depth=2)
    o = bpy.context.active_object; o.name = name; o.scale = size
    bpy.ops.object.shade_smooth(); 
    if m is not None: o.data.materials.append(m)
    return o

def align_segment(o, p0, p1, radial=1.0):
    d = Vector(p1) - Vector(p0); L = d.length
    o.location = Vector(p0); o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()) if L > 1e-6 else Quaternion()
    o.scale = (radial, radial, max(L, 1e-4))

# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y = RW, RH; sc.render.fps = a.fps
sc.render.engine = "BLENDER_EEVEE"
try: sc.eevee.taa_render_samples = a.samples
except Exception: pass
for k, v in (("use_gtao", True), ("use_bloom", True), ("use_shadow_jitter_viewport", False), ("use_raytracing", False), ("use_shadows", True)):
    if hasattr(sc.eevee, k):
        try: setattr(sc.eevee, k, v)
        except Exception: pass
sc.render.threads_mode = "FIXED"; sc.render.threads = a.threads
sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
sc.view_settings.look = "AgX - Punchy" if sc.view_settings.view_transform == "AgX" else "None"
try: sc.view_settings.look = "AgX - Punchy"
except Exception: pass

# sky + sun
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; nt = w.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
sky = nt.nodes.new("ShaderNodeTexSky"); bg = nt.nodes.new("ShaderNodeBackground"); out = nt.nodes.new("ShaderNodeOutputWorld")
try: sky.sky_type = "NISHITA"; sky.sun_elevation = math.radians(28); sky.sun_rotation = math.radians(200); sky.altitude = 5; sky.air_density = 1.0; sky.dust_density = 1.2
except Exception: sky.sky_type = "HOSEK_WILKIE"
bg.inputs["Strength"].default_value = 1.6
nt.links.new(sky.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.5; sun.angle = math.radians(1.5); so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(58), math.radians(8), math.radians(160))
fill = bpy.data.lights.new("fill", "AREA"); fill.energy = 120; fill.size = 4; fo = bpy.data.objects.new("fill", fill); sc.collection.objects.link(fo); fo.location = (-3, -3, 3); fo.rotation_euler = (math.radians(60), 0, math.radians(-40))

# grass: striped fairway + rough, procedural
gm = bpy.data.materials.new("grass"); gm.use_nodes = True; g = gm.node_tree; bsdf = g.nodes["Principled BSDF"]
tc = g.nodes.new("ShaderNodeTexCoord"); sep = g.nodes.new("ShaderNodeSeparateXYZ"); g.links.new(tc.outputs["Object"], sep.inputs[0])
wave = g.nodes.new("ShaderNodeTexWave"); wave.wave_type = "BANDS"; wave.bands_direction = "X"; wave.inputs["Scale"].default_value = 0.35; wave.inputs["Distortion"].default_value = 0.0
g.links.new(tc.outputs["Object"], wave.inputs["Vector"])
noise = g.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 180; noise.inputs["Detail"].default_value = 8; g.links.new(tc.outputs["Object"], noise.inputs["Vector"])
ramp = g.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = (0.035, 0.20, 0.03, 1); ramp.color_ramp.elements[1].color = (0.075, 0.32, 0.05, 1)
g.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
mix = g.nodes.new("ShaderNodeMixRGB"); mix.blend_type = "MULTIPLY"; mix.inputs["Fac"].default_value = 0.55; g.links.new(ramp.outputs["Color"], mix.inputs[1]); g.links.new(noise.outputs["Color"], mix.inputs[2])
# rough: darker beyond |y|>22 m via gradient on y
gr = g.nodes.new("ShaderNodeMath"); gr.operation = "ABSOLUTE"; g.links.new(sep.outputs["Y"], gr.inputs[0])
lim = g.nodes.new("ShaderNodeMath"); lim.operation = "SMOOTH_MIN" if False else "GREATER_THAN"; lim.inputs[1].default_value = 24.0; g.links.new(gr.outputs[0], lim.inputs[0])
rough = g.nodes.new("ShaderNodeMixRGB"); rough.inputs["Color2"].default_value = (0.03, 0.12, 0.02, 1); g.links.new(lim.outputs[0], rough.inputs["Fac"]); g.links.new(mix.outputs["Color"], rough.inputs["Color1"])
g.links.new(rough.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.85
bpy.ops.mesh.primitive_plane_add(size=1); gp = bpy.context.active_object; gp.name = "ground"; gp.scale = (900, 300, 1); gp.location = (150, 0, 0); gp.data.materials.append(gm)
# tee box mat, tee, markers, flag, trees
tee_m = mat("teebox", (0.03, 0.2, 0.03), 0.9)
b_ = prim("cube", "teebox", tee_m, (1.4, 0.8, 0.01)); b_.location = (0.2, 0, 0.0)
tee = prim("cone", "tee", mat("tee", (0.95, 0.9, 0.8), 0.5), (0.008, 0.008, 0.02)); tee.location = (BALL[0][0], BALL[0][1], 0.02); tee.rotation_euler = (math.pi, 0, 0)
white = mat("white", (0.9, 0.9, 0.9), 0.4)
for dx in (50, 100):
    pm = prim("cyl", f"post{dx}", white, (0.05, 0.05, 0.4)); pm.location = (dx, -5, 0.4)
    bpy.ops.object.text_add(location=(dx, -5.1, 1.0), rotation=(math.radians(90), 0, math.radians(0))); tx = bpy.context.active_object; tx.data.body = f"{dx}m"; tx.data.size = 1.2; tx.data.extrude = 0.05; tx.data.materials.append(white); tx.data.align_x = "CENTER"
pin = prim("cyl", "pin", mat("pin", (0.9, 0.9, 0.9), 0.3), (0.012, 0.012, 1.2)); pin.location = (112, 0, 1.2)
bpy.ops.mesh.primitive_plane_add(size=1); fl = bpy.context.active_object; fl.scale = (0.3, 0.001, 0.2); fl.location = (112.3, 0, 2.2); fl.data.materials.append(mat("flag", (0.9, 0.05, 0.05), 0.6, emit=(0.5, 0.0, 0.0), emit_s=0.3))
green = prim("cyl", "green", mat("green", (0.06, 0.4, 0.07), 0.9), (16, 16, 0.01)); green.location = (113, 0, 0.005)
rng = np.random.default_rng(7); leaf = mat("leaf", (0.02, 0.13, 0.03), 0.9); trunk = mat("trunk", (0.12, 0.07, 0.04), 0.9)
for k in range(110):
    x = rng.uniform(-60, 380); y = rng.choice([-1, 1]) * rng.uniform(34, 90); h = rng.uniform(7, 15)
    tr = prim("cyl", "tr", trunk, (0.25, 0.25, h * 0.25), seg=8); tr.location = (x, y, h * 0.25)
    cn = prim("cone", "cn", leaf, (h * 0.28, h * 0.28, h * 0.5), seg=10); cn.location = (x, y, h * 0.7)

# ---------------------------------------------------------------- humanoid (generic, Figure/Optimus-like proportions)
shell = mat("shell", (0.88, 0.89, 0.92), 0.28, 0.0, coat=1.0); dark = mat("graphite", (0.03, 0.03, 0.035), 0.35, 0.8)
accent = mat("accent", (0.0, 0.55, 1.0), 0.3, emit=(0.0, 0.5, 1.0), emit_s=2.0); glass = mat("visor", (0.0, 0.0, 0.0), 0.05, 0.0, emit=(0.0, 0.25, 0.45), emit_s=0.6)
skin_joint = dark
def seg(name, r0, r1, m=shell): return obj(name, capsule_mesh(name, r0, r1), m)
R = {}
R["r_uarm"] = seg("r_uarm", 0.047, 0.040); R["r_farm"] = seg("r_farm", 0.040, 0.030)
R["l_uarm"] = seg("l_uarm", 0.047, 0.040); R["l_farm"] = seg("l_farm", 0.040, 0.030)
R["r_thigh"] = seg("r_thigh", 0.075, 0.055); R["r_shin"] = seg("r_shin", 0.055, 0.04); R["l_thigh"] = seg("l_thigh", 0.075, 0.055); R["l_shin"] = seg("l_shin", 0.055, 0.04)
R["neck"] = seg("neck", 0.04, 0.04, dark); R["spine"] = seg("spine", 0.10, 0.075, dark)
joints = {}
for jn, r in (("r_sh", .062), ("l_sh", .062), ("r_el", .045), ("l_el", .045), ("r_hip", .08), ("l_hip", .08), ("r_kn", .06), ("l_kn", .06), ("r_an", .045), ("l_an", .045), ("r_wr", .036), ("l_wr", .036)):
    joints[jn] = prim("sphere", jn, dark, (r, r, r), seg=24)
torso = prim("sphere", "torso", shell, (0.17, 0.11, 0.24), seg=48)  # chest (barrel), centred above waist
pelvis = prim("sphere", "pelvis", shell, (0.15, 0.10, 0.12), seg=40)
core = prim("sphere", "chestcore", accent, (0.032, 0.012, 0.032), seg=16)   # glowing "core" disc on the sternum
head = prim("sphere", "head", shell, (0.095, 0.105, 0.115), seg=48); visor = prim("sphere", "visor", glass, (0.078, 0.06, 0.07), seg=32)
shoe = {s: prim("cube", f"{s}_foot", dark, (0.05, 0.12, 0.03)) for s in ("r", "l")}
for s in shoe.values():
    bv = s.modifiers.new("b", "BEVEL"); bv.width = 0.02; bv.segments = 3
# hands: palm + 4 fingers wrapping + thumb, parented to an empty so we only move the empty
def make_hand(name):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); parts = []
    palm = prim("cube", name + "_palm", dark, (0.03, 0.017, 0.04)); palm.location = (0, 0.028, 0); parts.append(palm)
    bv = palm.modifiers.new("b", "BEVEL"); bv.width = 0.012; bv.segments = 3
    for k in range(4):   # fingers: ring segments wrapping around the grip (grip radius 0.017), spaced along the shaft (z)
        for sg in range(3):
            ang = math.radians(-110 + 60 * sg); r = 0.026
            f = prim("sphere", f"{name}_f{k}{sg}", shell if sg < 2 else dark, (0.011, 0.011, 0.010), seg=12)
            f.location = (r * math.sin(ang) * 1.0, r * math.cos(ang) * 1.0 * -1 + 0.0, -0.032 + 0.0 + (k - 1.5) * 0.022); parts.append(f)
    th = prim("sphere", name + "_th", shell, (0.012, 0.012, 0.03), seg=12); th.location = (0.02, -0.012, 0.03); th.rotation_euler = (0.4, 0.2, 0); parts.append(th)
    for p in parts: p.parent = e
    return e
hands = {"r": make_hand("hand_r"), "l": make_hand("hand_l")}
# club: grip, shaft, head (driver-like), face
grip_m = mat("grip", (0.02, 0.02, 0.02), 0.7); shaft_m = mat("shaft", (0.08, 0.08, 0.09), 0.25, 0.9); head_m = mat("clubhead", (0.01, 0.01, 0.012), 0.2, 0.6, coat=1.0)
club = bpy.data.objects.new("club", None); sc.collection.objects.link(club)
grip = prim("cyl", "grip", grip_m, (0.0155, 0.0155, 0.15)); grip.location = (0, 0, -0.15); grip.parent = club
shaft = prim("cyl", "shaft", shaft_m, (0.006, 0.006, 0.47)); shaft.location = (0, 0, -0.30 - 0.4); shaft.scale = (0.006, 0.006, 0.4); shaft.parent = club
shaft.location = (0, 0, -0.7)
ch = prim("sphere", "chead", head_m, (0.055, 0.058, 0.04), seg=48); ch.location = (0, 0, -1.12); ch.parent = club
cf = prim("cube", "cface", mat("face", (0.55, 0.55, 0.58), 0.3, 0.9), (0.002, 0.04, 0.026)); cf.location = (0.052, 0, -1.115); cf.rotation_euler = (0, math.radians(11), 0); cf.parent = club   # face on +x side (toward target)
cs = prim("cube", "csole", mat("cstripe", (0.0, 0.5, 1.0), 0.3, emit=(0, 0.5, 1), emit_s=3), (0.04, 0.004, 0.004)); cs.location = (0, 0, -1.145); cs.parent = club
# ball, trail
ball = prim("sphere", "ball", mat("ball", (0.98, 0.98, 0.98), 0.35), (0.02135,) * 3, seg=32)
trail_m = mat("trail", (1.0, 0.85, 0.2), 0.3, emit=(1.0, 0.6, 0.1), emit_s=6.0)
cu = bpy.data.curves.new("trail", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.06; cu.bevel_resolution = 3; cu.materials.append(trail_m)
trail = bpy.data.objects.new("trail", cu); sc.collection.objects.link(trail)
# camera
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 42; cam.data.sensor_width = 36; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 4.0
tgt = bpy.data.objects.new("tgt", None); sc.collection.objects.link(tgt)
cam.data.dof.focus_object = tgt
tc_ = cam.constraints.new("TRACK_TO"); tc_.target = tgt; tc_.track_axis = "TRACK_NEGATIVE_Z"; tc_.up_axis = "UP_Y"

# ---------------------------------------------------------------- pose the figure for sim sample-time f
def by(p): return Vector((p[0], p[1], p[2]))
def body(p): return Vector((p[0], p[1] + Y_BODY, p[2]))
def pose(f):
    rsh, rel, rwr = lerp_pose(f, BM["r_sh"])[0], lerp_pose(f, BM["r_el"])[0], None
    rwr, rq = lerp_pose(f, BM["r_wr"]); lsh = lerp_pose(f, BM["l_sh"])[0]; lel = lerp_pose(f, BM["l_el"])[0]; lh = lerp_pose(f, BM["l_hand"])[0]
    # arms (real chain) -- shoulders shifted to the front plane so they sit on the chest
    sd0 = rq @ Vector((0, 0, -1))
    for s, sh, el, wr in (("r", rsh, rel, rwr), ("l", lsh, lel, lh)):
        sh_, el_, wr_ = by(sh), by(el), by(wr)
        if s == "l":   # COSMETIC: the sim's left arm is a long passive chain (0.5+0.38 m); draw a normal-length left arm reaching the lower grip hand instead
            wr_ = by(rwr) + sd0 * 0.16; dv = wr_ - sh_; d = dv.length; Lh = max(0.31, d / 2 + 0.01)
            hint = Vector((0, 0.5, -1.0)); hv = hint - hint.dot(dv.normalized()) * dv.normalized(); hv.normalize()
            el_ = sh_ + dv / 2 + hv * math.sqrt(max(Lh * Lh - (d / 2) ** 2, 0.0))
        align_segment(R[f"{s}_uarm"], sh_, el_); align_segment(R[f"{s}_farm"], el_, wr_)
        joints[f"{s}_sh"].location = sh_; joints[f"{s}_el"].location = el_; joints[f"{s}_wr"].location = wr_
    # legs (real hips/knees/ankles, torso offset behind arms)
    for s in ("r", "l"):
        hp, kn, an = body(lerp_pose(f, BM[s+'_hip'])[0]), body(lerp_pose(f, BM[s+'_kn'])[0]), body(lerp_pose(f, BM[s+'_an'])[0])
        align_segment(R[f"{s}_thigh"], hp, kn); align_segment(R[f"{s}_shin"], kn, an)
        joints[f"{s}_hip"].location = hp; joints[f"{s}_kn"].location = kn; joints[f"{s}_an"].location = an
        shoe[s].location = an + Vector((0.03 if True else 0, 0.06, -0.035))
    hipc = body(lerp_pose(f, BM["root"])[0]) + Vector((0, 0, -0.05)); chest = body(lerp_pose(f, BM["chest"])[0]) + Vector((0, 0, 0.30))
    pelvis.location = hipc + Vector((0, 0, 0.0)); torso.location = chest + Vector((0, 0.0, 0.0)); torso.rotation_mode = "QUATERNION"; torso.rotation_quaternion = lerp_pose(f, BM["chest"])[1]
    align_segment(R["spine"], hipc, chest + Vector((0, 0, -0.1)))
    if "pelvis" in BM and BM["pelvis"] in bi:   # newer body: real pelvis orientation + position
        pp, pq = lerp_pose(f, BM["pelvis"]); pelvis.location = body(pp); pelvis.rotation_mode = "QUATERNION"; pelvis.rotation_quaternion = pq
    core.location = chest + Vector((0, 0.108, 0.03))
    nb = chest + Vector((0, 0, 0.2)); hc = chest + Vector((0, 0.01, 0.40)); align_segment(R["neck"], nb, hc + Vector((0, 0, -0.06)))
    if "head" in BM and BM["head"] in bi: hc = body(lerp_pose(f, BM["head"])[0])
    head.location = hc; visor.location = hc + Vector((0, 0.065, 0.005))
    # club: pose of the right_wrist body (origin = top of grip), shaft along local -z
    club.rotation_mode = "QUATERNION"; club.location = by(rwr); club.rotation_quaternion = rq
    # hands: top hand at the grip top (right wrist), lower hand 0.12 m below along shaft
    sd = rq @ Vector((0, 0, -1)); 
    for s, off in (("r", 0.05), ("l", 0.16)):
        h = hands[s]; h.rotation_mode = "QUATERNION"; h.location = by(rwr) + sd * off
        h.rotation_quaternion = rq @ Quaternion((0, 0, 1), math.radians(0 if s == "r" else 180))
    return rwr

# ---------------------------------------------------------------- timeline: video seconds -> sim sample index (float)
FPS = a.fps
def remap(tv):
    """video time -> sim sample index. Segments are (t0,t1,f0,f1) piecewise-linear (slow-mo around impact; real sim samples are 5 ms)."""
    for t0, t1, f0, f1 in SEG:
        if tv <= t1: return f0 + (f1 - f0) * (tv - t0) / (t1 - t0) if t1 > t0 else f0
    return SEG[-1][3]
def smooth(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ev(k0, k1, u): return k0 + (k1 - k0) * smooth(u)
LAST = NS - 1
if a.clip == "test":      # v1: 12 s (frames 0-287 @24fps reused)
    SEG = [(0, 3.0, 0, 0), (3.0, 7.0, 0, 168), (7.0, 8.6, 168, 188), (8.6, 12.0, 188, 188 + 3.4 * 200 * 0.62)]; KINDS = ["orbit", "swing", "impact", "chase"]
elif a.clip == "test2":   # v2: 17.8 s. same first 8.6 s as v1; chase now follows the ball to landing + hold; DTL orbit slow-mo replay
    SEG = [(0, 3.0, 0, 0), (3.0, 7.0, 0, 168), (7.0, 8.6, 168, 188), (8.6, 12.6, 188, LAST), (12.6, 13.8, LAST, LAST), (13.8, 17.8, 112, 196)]
    KINDS = ["orbit", "swing", "impact", "chase", "land", "dtl"]
elif a.clip == "policy":  # 17 s cut for exported policy rollouts: sample offsets are relative to the rollout's own impact index (IMP), not the hard-coded scripted-v3 indices
    _s0, _s1, _d0 = max(IMP - 7, 1), IMP + 13, max(IMP - 63, 0)
    SEG = [(0, 2.0, 0, 0), (2.0, 5.5, 0, _s0), (5.5, 7.5, _s0, _s1), (7.5, 12.5, _s1, LAST), (12.5, 14.0, LAST, LAST), (14.0, 17.0, _d0, min(IMP + 21, LAST))]
    KINDS = ["orbit", "swing", "impact", "chase", "land", "dtl"]
else:                     # 30 s hero cut
    SEG = [(0, 5.0, 0, 0), (5.0, 10.0, 0, 168), (10.0, 12.5, 168, 188), (12.5, 20.0, 188, LAST), (20.0, 22.5, LAST, LAST), (22.5, 30.0, 112, 196)]
    KINDS = ["orbit", "swing", "impact", "chase", "land", "dtl"]
TOTAL = SEG[-1][1]
def kind_at(tv):
    for k, (t0, t1, f0, f1) in enumerate(SEG):
        if tv <= t1: return KINDS[k], (tv - t0) / max(t1 - t0, 1e-6)
    return KINDS[-1], 1.0
def camera_for(tv, f):
    """returns (cam_loc, target). Shots: establishing orbit, face-on swing, impact macro, ball chase to landing, landing hold, down-the-line orbit replay."""
    c = Vector((0.2, 0.0, 1.0)); kind, u = kind_at(tv); b = Vector(lerp_ball(f))
    if kind == "orbit":
        ang = math.radians(ev(150, 215, u)); r = ev(4.6, 3.1, u)
        return Vector((c.x + r * math.cos(ang), c.y + r * math.sin(ang), ev(1.7, 1.15, u))), Vector((0.25, -0.05, 0.85))
    if kind == "swing":
        ang = math.radians(ev(90, 48, u)); r = ev(4.0, 3.6, u)
        return Vector((0.35 + r * math.cos(ang), r * math.sin(ang), ev(1.15, 1.0, u))), Vector((0.2, 0.0, 1.0))
    if kind == "impact":
        return Vector((ev(1.0, 0.1, u), ev(-1.7, -1.2, u), 0.32)), Vector((0.45, 0.0, 0.1))
    LAND = Vector(BALL[LAST])
    if kind == "chase":   # starts low behind the tee, sweeps to the side/ahead as the ball flies, ends framing the landing zone
        side = ev(-3.0, -16.0, u); back = ev(-7.0, -22.0, u); h = ev(1.2, 5.5, u)
        # camera tracks along x (lagging the ball) so the ball stays mid-frame; blends toward the landing spot at the end
        lag = Vector((b.x + back * (1 - smooth(u)) - 12 * smooth(u), side, h))
        return lag, b.lerp(Vector((b.x, b.y, max(b.z * 0.8, 0.3))), 0.0) if u < 0.9 else b
    if kind == "land":    # hold on landing spot, slow orbit to show it rolled to rest
        ang = math.radians(ev(-100, -40, u)); return Vector((LAND.x + 9 * math.cos(ang), LAND.y + 9 * math.sin(ang), 1.6)), Vector((LAND.x, LAND.y, 0.2))
    # dtl: down-the-line (camera behind the golfer on the target line, looking down it) orbiting toward face-on
    ang = math.radians(ev(180, 235, u)); r = ev(5.2, 4.6, u)
    return Vector((0.2 + r * math.cos(ang), r * math.sin(ang), ev(1.5, 1.3, u))), Vector((0.2, 0.0, 1.0))

def update_trail(f):
    i = int(min(max(f, 0), NS - 1))
    if i <= IMP + 1 or i < 2: pts = []
    else: idx = list(range(IMP, i + 1, 4)); pts = [BALL[k] for k in idx if BALL[k][2] > -0.02]
    cu.splines.clear()
    if len(pts) >= 2:
        sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
        for k, p_ in enumerate(pts): sp.points[k].co = (p_[0], p_[1], max(p_[2], 0.02), 1)

fr = list(range(int(round(TOTAL * FPS))))
if a.frames:
    lo, hi = a.frames.split("-"); fr = [i for i in fr if int(lo) <= i <= int(hi)]
fr = fr[a.worker::a.nworkers]
os.makedirs(a.out, exist_ok=True)
if a.save_blend: bpy.ops.wm.save_as_mainfile(filepath=a.save_blend)
import time
for fi in fr:
    if os.path.exists(os.path.join(a.out, f"f{fi:05d}.png")): continue
    tv = fi / FPS; f = remap(tv)
    # subtle address waggle-free idle: tiny breathing so the establishing shot is not frozen
    pose(f); ball.location = lerp_ball(f); update_trail(f)
    kd_, _u = kind_at(tv); k_ = 4.0 if kd_ in ("chase", "land") else 1.0   # COSMETIC: ball drawn 4x larger in the distance shots so it is visible
    ball.scale = (0.02135 * k_,) * 3; cu.bevel_depth = (0.06 if a.clip not in ("hero", "policy") else 0.035) * (2.0 if kd_ in ("chase", "land") else 1.0)
    cl, tg = camera_for(tv, f); cam.location = cl; tgt.location = tg
    sc.render.filepath = os.path.join(a.out, f"f{fi:05d}.png"); t0 = time.time()
    bpy.ops.render.render(write_still=True); print(f"frame {fi} tv={tv:.2f} sim_idx={f:.1f} {time.time()-t0:.1f}s", flush=True)
