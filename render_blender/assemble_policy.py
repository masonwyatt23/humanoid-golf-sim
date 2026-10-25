"""Frames (build_and_render.py --clip policy) -> mp4 with HUD + title/end cards, for exported POLICY rollouts (export_policy_trajectory.py).
    python render_blender/assemble_policy.py FRAMES_DIR OUT.mp4 --traj <local-path>/policy/stock_imit20.json --kind stock|power [--fps 12] [--res 1280x720]
All on-screen numbers (club mph, launch, carry yd/m) are from the ONE rolled-out episode in the json; the 100-episode gate means are shown separately in a caption.
Labels: 'SCRIPT-DISTILLED POLICY' = behaviour-cloned imitation of the scripted v3 swing (not a swing learned independently; not learned from any person). No 'learned' claims."""
import json, subprocess, argparse, os, tempfile
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("frames"); ap.add_argument("out"); ap.add_argument("--traj", required=True); ap.add_argument("--kind", choices=["stock", "power"], required=True)
ap.add_argument("--fps", type=int, default=12); ap.add_argument("--res", default="1280x720"); ap.add_argument("--out-fps", type=int, default=24); a = ap.parse_args()
J = json.loads(Path(a.traj).read_text()); S = J["summary"]; G = J.get("gate_means") or {}; W, H = map(int, a.res.split("x"))
mph = S["impact_club_speed"] * 2.23694; carry_m = S["carry"]; carry_yd = S.get("carry_yd", carry_m * 1.09361); launch = S["launch_elev_deg"]; seed = J["rollout_seed"]; model = J["model"]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
tmp = Path(tempfile.mkdtemp())
def tf(text):   # textfile avoids ffmpeg drawtext escaping problems (':' '%' quotes)
    p = tmp / f"t{len(list(tmp.iterdir()))}.txt"; p.write_text(text); return str(p)
def dt(text, x, y, size, color="white", en=None, box=0.45):
    e = f":enable='{en}'" if en else ""
    return f"drawtext=fontfile={FONT}:textfile={tf(text)}:x={x}:y={y}:fontsize={size}:fontcolor={color}:box=1:boxcolor=black@{box}:boxborderw=8{e}"
if a.kind == "stock":
    label = f"SCRIPT-DISTILLED POLICY ({model}) | STOCK motors force_scale 1 | simulation | club mph and carry in yards"
    sub = "Stock actuators (force_scale 1). Behaviour-cloned from the scripted v3 swing; reproduces the script, not a new swing."
    card_head = "SCRIPT-DISTILLED POLICY, stock motors"; col = "0xffdd66"
else:
    label = f"SCRIPT-DISTILLED POLICY ({model}) | HYPOTHETICAL POWER TIER, impact gain 1.2 | no spin model | simulation"
    sub = "HYPOTHETICAL power tier: boosted actuators + impact gain 1.2, no spin model (backspin hand-set). Not a real robot or human."
    card_head = "SCRIPT-DISTILLED POLICY, HYPOTHETICAL power tier"; col = "0xff7070"
gm = ""
if G.get("mean_carry_yd") is not None:
    gm = f"This swing: seed {seed} (median of seeds {J['candidate_seeds'][0][0]}-{J['candidate_seeds'][-1][0]}, deterministic).  GATE MEANS, SEPARATE (100 eps, det): carry {G['mean_carry_yd']:.0f} yd, club {G['peak_club_mph_mean']:.1f} mph, launch {G['launch_elev_mean_deg']:.1f} deg"
imp_t = 5.5
f = [dt("LEFT-HANDED DRIVER  |  MuJoCo sim + Blender  |  generic humanoid (not an official model)", 24, 18, 20),
     dt(f"THIS SWING: CLUB {mph:.1f} mph", 24, 60, 30, "0x66ccff", f"gte(t,{imp_t+1.0})"),
     dt(f"LAUNCH {launch:.1f} deg", 24, 106, 30, "0x66ccff", f"gte(t,{imp_t+1.6})"),
     dt(f"CARRY {carry_yd:.0f} yd ({carry_m:.0f} m)", 24, 152, 30, "0xffdd66", f"gte(t,{imp_t+5.0})"),
     dt(gm, 24, "h-84", 14, "0xdddddd"), dt(sub, 24, "h-60", 14, "0xcccccc"), dt(label, 24, "h-34", 14, col, box=0.7)]
body = tmp / "body.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps), "-i", os.path.join(a.frames, "f%05d.png"), "-vf", ",".join(f) + ",fps=%d" % a.out_fps, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(body)], check=True)
def card(name, lines, secs):
    vf = []; y = 140
    for i, (txt, size, c) in enumerate(lines):
        vf.append(f"drawtext=fontfile={FONT}:textfile={tf(txt)}:x=64:y={y}:fontsize={size}:fontcolor={c}"); y += int(size * 1.9)
    p = tmp / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=0x0d1117:s={W}x{H}:r={a.out_fps}:d={secs}", "-vf", ",".join(vf), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(p)], check=True); return p
title = card("title", [("Humanoid golf: " + card_head, 36 if a.kind == "stock" else 28, "white"), ("MuJoCo physics, left-handed, generic humanoid (not an official robot model). Simulation only.", 22, "0xcccccc"),
    (f"Policy: {model} (behaviour-cloned from the scripted v3 swing)", 24, col), ("Stock motors, force_scale 1" if a.kind == "stock" else "HYPOTHETICAL power tier: impact gain 1.2, no spin model", 26, col),
    (f"Seed {seed}: club {mph:.1f} mph, launch {launch:.1f} deg, carry {carry_yd:.0f} yd / {carry_m:.0f} m (this one swing)", 22, "white")], 3)
end = card("end", [("What you just saw", 36, "white"), ("- Body motion, club and ball launch: from the MuJoCo simulation (deterministic policy rollout).", 16, "white"),
    ("- Policy = behaviour-cloned imitation of the scripted swing; it reproduces the script, not a new swing.", 16, "white"),
    (f"- This clip is ONE swing (seed {seed}), the median of 8 seeds; gate means are quoted separately on screen.", 16, "white"),
    ("- Ball flight after the sim episode ends: analytic drag+Magnus; spin is ASSUMED.", 16, "white"),
    ("- Stock motors (force_scale 1). Simulation only." if a.kind == "stock" else "- HYPOTHETICAL power tier (boosted actuators, impact gain 1.2, no spin model): not evidence of human/robot performance.", 16, "0xff6060" if a.kind == "power" else "white"),
    (f"- Rendered with Blender (EEVEE) at {W}x{H}, {a.fps} fps source (duplicated to {a.out_fps}).", 16, "0xcccccc")], 5)
lst = tmp / "l.txt"; lst.write_text("".join(f"file '{p}'\n" for p in (title, body, end)))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", a.out], check=True); print("wrote", a.out)
