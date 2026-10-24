"""v4 re-baseline address solve (kinematic IK only, no training): realistic head, lie V4_LIE_DEG (58.5, Data Agent JSON), swingweight compensation.
Reuses env/v5_body.solve_address (the same least-squares IK that produced env/models/v5_address_*.json in Stage 0: hands on the grip, feet flat, stance 0.28,
ball (0.10, 0.50), CoM over the feet, same joint prior). Writes env/models/v5_address_<H>_<L>_v4.json and prints joint deltas vs the v5 address and the
sole/face angles measured by FK. Re-run if v5_body.FACE_CENTRE_H_M changes.  Usage: python scripts/v4_address_solve.py [club_len=1.15] [--quick]"""
import sys, json, math, numpy as np, mujoco; sys.path.insert(0, '.')
import env.v5_body as B
L = float(([a for a in sys.argv[1:] if not a.startswith('--')] or ['1.15'])[0]); quick = '--quick' in sys.argv
a = B.solve_address("LH", L, quick=quick, v4=True)
path = B.addr_path("LH", L).replace(".json", "_v4.json"); json.dump(a, open(path, "w"), indent=1); print("wrote", path)
old = B.load_address("LH", L)
m, _ = B.build_model("LH", L, addr=a, head="v4", lie_deg=B.V4_LIE_DEG, sw_comp=True); d = mujoco.MjData(m); B.set_address(m, d, a)
R = d.geom_xmat[m.geom("head").id].reshape(3, 3); n = R[:, 0]; toe = R[:, 1]
Rs = d.geom_xmat[m.geom("head_shell").id].reshape(3, 3); sh = d.xmat[m.body("club").id].reshape(3, 3)[:, 2]
fc = d.site_xpos[m.site("clubhead").id]
rep = dict(cost=a["cost"], old_cost=old["cost"], hand_err_mm=a["hand_err_mm"], foot_z_mm=a["foot_z_mm"],
           shaft_lie_deg=math.degrees(math.asin(abs(sh[2]))), loft_deg=math.degrees(math.asin(n[2])), face_yaw_deg=math.degrees(math.atan2(n[1], n[0])),
           toe_tilt_deg=math.degrees(math.asin(toe[2])), sole_tilt_deg=math.degrees(math.acos(min(1.0, Rs[:, 2][2]))),
           shell_zmin_mm=1e3 * min((d.geom_xpos[m.geom("head_shell").id] + Rs @ (m.geom_size[m.geom("head_shell").id] * np.array([i, j, k])))[2] for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)),
           face_ctr=fc.tolist(), ball=a["ball_pos"], ball_minus_face_mm=(1e3 * (np.array(a["ball_pos"]) - fc)).tolist(),
           pelvis_delta_mm=(1e3 * (np.array(a["pelvis_pos"]) - np.array(old["pelvis_pos"]))).tolist(), pelvis_pitch_delta_deg=math.degrees(a["pelvis_pitch"] - old["pelvis_pitch"]),
           pelvis_roll_delta_deg=math.degrees(a["pelvis_roll"] - old["pelvis_roll"]), club_pos_delta_mm=(1e3 * (np.array(a["club_pos"]) - np.array(old["club_pos"]))).tolist(),
           joint_delta_deg={k: round(math.degrees(a["joints"][k] - old["joints"][k]), 2) for k in a["joints"]})
print(json.dumps(rep, indent=1)); json.dump(rep, open(path.replace(".json", "_report.json"), "w"), indent=1)
