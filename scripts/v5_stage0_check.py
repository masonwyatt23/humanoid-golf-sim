"""Stage 0 go/no-go checks for the v5 body/env (no learning). Writes results/v5_stage0.json. Run: python scripts/v5_stage0_check.py"""
import sys, os, json, time, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, mujoco
from env.v5_body import build_model, load_address, set_address, STOCK, joint_kind, MENAG, mat2quat
from env.v5_golf_env import V5GolfEnv
from env.v5_shot import shot_from_contact, verify_toe_sign
from env.v5_reward import episode_terms
from v5_sanity_swing import run_swing, action_at
R = {}
CL = 0.87

def hold(dt, T=2.0, kp_scale=1.0, passive=False):
    e = V5GolfEnv(dt=dt, club_len=CL)
    e.reset(); d, m = e.d, e.m
    if passive:
        m.actuator_gainprm[:, 0] = 0; m.actuator_biasprm[:, :] = 0; m.jnt_actfrclimited[:] = 1
    foot0 = {s: d.site_xpos[m.site(f"{s}_sole_site").id].copy() for s in ("left", "right")}
    zs, drift, tilt, grf, touch, grf_all = [], 0.0, 0.0, [], [], []
    tfall = None
    n = int(T / CTRL_DT) if False else int(T / 0.02)
    for k in range(n):
        if passive:
            for _ in range(e.sub):
                d.qpos[e.ball_q:e.ball_q + 3] = e.tee; d.qvel[e.ball_v:e.ball_v + 6] = 0; mujoco.mj_step(m, d)
            e.steps += 1
        else:
            e.step(np.zeros(29))
        zs.append(d.qpos[2]); Rp = d.xmat[e.pel].reshape(3, 3); tilt = max(tilt, math.degrees(math.acos(np.clip(Rp[2, 2], -1, 1))))
        fl, fr = e.foot_forces(); grf.append(fl + fr)
        sn = lambda nm: float(d.sensordata[m.sensor_adr[m.sensor(nm).id]]); touch.append(sn('left_foot_touch') + sn('right_foot_touch'))
        tot_floor = 0.0; fv = np.zeros(6)
        for i in range(d.ncon):
            c = d.contact[i]
            if c.geom1 == e.floor or c.geom2 == e.floor:
                mujoco.mj_contactForce(m, d, i, fv); tot_floor += fv[0]
        grf_all.append(tot_floor)
        if tfall is None and d.qpos[2] < 0.45: tfall = d.time
    slip = max(float(np.linalg.norm(d.site_xpos[m.site(f"{s}_sole_site").id][:2] - foot0[s][:2])) for s in ("left", "right"))
    w = float(m.body_mass.sum() * 9.81)
    last = np.mean(grf[-25:])
    return dict(dt=dt, T=T, pelvis_z_start=float(zs[0]), pelvis_z_end=float(zs[-1]), max_tilt_deg=tilt, foot_slip_mm=1000 * slip, weld_drift_max_mm=1000 * e.max_weld_drift,
                grf_sum_N=float(last), weight_N=w, grf_over_weight=float(last / w), grf_all_floor_contacts_over_weight=float(np.mean(grf_all[-25:]) / w), touch_sensors_over_weight=float(np.mean(touch[-25:]) / w), club_head_floor_N=float(np.mean(grf_all[-25:]) - last), t_fall=tfall, fell=tfall is not None)

def mirror_kinematic():
    spec_m, _ = build_model("LH", CL); m = spec_m; d = mujoco.MjData(m)
    rng = np.random.default_rng(0); worst = 0.0
    names = [m.actuator(i).name for i in range(m.nu)]
    flip = lambda n: -1.0 if ("roll" in n or "yaw" in n) else 1.0
    for _ in range(20):
        d.qpos[:] = m.qpos0; d.qpos[0:7] = [0, 0, 0.8, 1, 0, 0, 0]
        q = {}
        for n in names:
            lo, hi = m.jnt_range[m.joint(n).id]; q[n] = rng.uniform(0.3 * lo, 0.3 * hi)
        def put(qd):
            d.qpos[:] = m.qpos0; d.qpos[0:7] = [0, 0, 0.8, 1, 0, 0, 0]
            for n, v in qd.items(): d.qpos[m.jnt_qposadr[m.joint(n).id]] = v
            mujoco.mj_kinematics(m, d)
            return {b: d.xpos[m.body(b).id].copy() for b in [m.body(i).name for i in range(m.nbody)] if b.startswith("left_")}, {b: d.xpos[m.body(b).id].copy() for b in [m.body(i).name for i in range(m.nbody)] if b.startswith("right_")}
        L1, R1 = put(q)
        qm = {}
        for n, v in q.items():
            o = n.replace("left_", "R_").replace("right_", "left_").replace("R_", "right_") if n.startswith(("left_", "right_")) else n
            qm[o] = v * flip(n)
        L2, R2 = put(qm)
        for b, p in L1.items():
            pm = R2[b.replace("left_", "right_")] * np.array([1, -1, 1]); worst = max(worst, float(np.linalg.norm(p - pm)))
    return dict(max_body_pos_mirror_err_m=worst)

def mirror_address():
    a, b = load_address("LH", CL), load_address("RH", CL)
    flip = lambda n: -1.0 if ("roll" in n or "yaw" in n) else 1.0
    diffs = []
    for n, v in a["joints"].items():
        o = n.replace("left_", "R_").replace("right_", "left_").replace("R_", "right_") if n.startswith(("left_", "right_")) else n
        diffs.append(abs(b["joints"][o] - flip(n) * v))
    cp = np.array(a["club_pos"]) * [1, -1, 1] - np.array(b["club_pos"])
    return dict(max_joint_diff_rad=float(max(diffs)), mean_joint_diff_rad=float(np.mean(diffs)), club_pos_mirror_err_m=float(np.linalg.norm(cp)),
                lead_arm_LH="right", lead_arm_RH="left", hand_err_mm_LH=a["hand_err_mm"], hand_err_mm_RH=b["hand_err_mm"])

def lead_hand_side_check():
    m, _ = build_model("LH", CL); d = mujoco.MjData(m); a = load_address("LH", CL); set_address(m, d, a)
    xr = d.site_xpos[m.site("right_hand").id][0]; xl = d.site_xpos[m.site("left_hand").id][0]
    pr = d.site_xpos[m.site("right_hand").id]; pl = d.site_xpos[m.site("left_hand").id]
    sh_r = d.xpos[m.body("right_shoulder_pitch_link").id]; sh_l = d.xpos[m.body("left_shoulder_pitch_link").id]
    facing = d.xmat[m.body("pelvis").id].reshape(3, 3)[:, 0]
    return dict(golfer_facing_xy=[float(facing[0]), float(facing[1])], target_dir="+x",
                right_shoulder_x=float(sh_r[0]), left_shoulder_x=float(sh_l[0]), lead_arm_is_right=bool(sh_r[0] > sh_l[0]),
                lead_hand_higher_on_shaft=bool(pr[2] > pl[2]), hand_sep_m=float(np.linalg.norm(pr - pl)))

def toe_and_flight_mirror():
    out = {}
    for h in ("LH", "RH"):
        m, _ = build_model(h, CL); d = mujoco.MjData(m); set_address(m, d, load_address(h, CL))
        ts, toe, dot = verify_toe_sign(m, d, h); out[h] = dict(toe_sign=ts, toe_geo=[round(float(x), 3) for x in toe], cos_with_golfphys_toe=dot)
    v = np.array([45.0, 1.0, 3.0]); n = np.array([math.cos(0.18), 0.02, math.sin(0.18)]); n /= np.linalg.norm(n)
    for case in ((0.0, 0.0), (0.012, 0.0), (0.0, 0.01), (0.012, 0.01)):
        l = shot_from_contact(v, n, case[0], case[1], "LH"); rv = v * [1, -1, 1]; rn = n * [1, -1, 1]
        r = shot_from_contact(rv, rn, case[0], case[1], "RH")
        out.setdefault("flight_mirror", []).append(dict(dy=case[0], dz=case[1], carry_LH=l["shot"].carry_m, carry_RH=r["shot"].carry_m, lat_LH=l["shot"].lateral_carry_m, lat_RH=r["shot"].lateral_carry_m,
                                                       backspin_LH=l["backspin_rpm"], backspin_RH=r["backspin_rpm"], side_LH=l["sidespin_rpm"], side_RH=r["sidespin_rpm"]))
    # raw golfphys (no env workaround), to document the LH 'up' flip
    from golfphys import impact, Delivery, Strike
    rh = impact(Delivery(50, 12, 0, handed="RH"), Strike(0.0, 0.01)); lh = impact(Delivery(50, 12, 0, handed="LH"), Strike(0.0, 0.01))
    out["golfphys_raw_high_strike_backspin"] = dict(RH=rh["backspin_rpm"], LH=lh["backspin_rpm"], note="should be equal; differs => LH up-axis flip in vendored impact_vec")
    return out

def actuator_limits():
    base = mujoco.MjModel.from_xml_path(f"{MENAG}/unitree_g1/scene.xml"); m, _ = build_model("LH", CL)
    rows = []; ok = True
    for i in range(m.nu):
        n = m.actuator(i).name; j = m.joint(n).id; bj = base.joint(n).id
        menag = float(base.jnt_actfrcrange[bj][1]); used = float(m.jnt_actfrcrange[j][1])
        rows.append(dict(joint=n, menagerie_actuatorfrcrange=menag, used_force_scale1=used, rated_speed_rad_s=STOCK[joint_kind(n)][1], forcerange=float(m.actuator_forcerange[i][1])))
        ok &= abs(menag - used) < 1e-9
    return dict(all_match_menagerie=ok, rows=rows)

def swings(dt, tether):
    e = V5GolfEnv(dt=dt, club_len=CL, tether=tether); best = None
    res = []
    for wy, td in ((0.6, 0.25), (1.0, 0.15), (1.4, 0.25), (1.4, 0.15)):
        info = run_swing(e, wy=wy, t_down=td)
        res.append(dict(wy=wy, t_down=td, contact=bool(e.contact), club_mph=info.get("club_speed_mph"), ball_mph=info.get("ball_speed_mph"), carry_m_noroll=info.get("carry_m_noroll"),
                        total_m_model=info.get("total_m_model"), launch=info.get("launch_deg"), spin=info.get("spin_rpm"), lateral=info.get("lateral_carry_m"), dy=info.get("dy"), dz=info.get("dz"),
                        pelvis_z_end=float(e.d.qpos[2]), weld_drift_mm=1000 * e.max_weld_drift))
    return res

def throughput():
    out = {}
    for dt in (0.0005, 0.001, 0.002):
        e = V5GolfEnv(dt=dt, club_len=CL, tether=False); e.reset(); rng = np.random.default_rng(1); t = time.time(); n = 0
        while time.time() - t < 3.0:
            e.step(rng.uniform(-0.15, 0.15, 29)); n += 1
            if n % 100 == 0: e.reset()
        out[str(dt)] = n / (time.time() - t)
    out["loadavg_1_5_15"] = list(os.getloadavg()); out["ncpu"] = os.cpu_count()
    return out

def reward_demo():
    e = V5GolfEnv(dt=0.001, club_len=CL, tether=True); info = run_swing(e, wy=1.0, t_down=0.15)
    L = {k: np.array(v) for k, v in e.log.items()}; L["t_impact"] = e.t_contact
    sh = e.shot["shot"] if e.contact else None
    res = {}
    for st in ("A", "C"):
        t = episode_terms(L, shot=sh, progress=0.0, stage=st); res[st] = dict(prior_total=t["prior_total"], prior_cap=t["prior_cap"], raw=t["raw_prior_terms"], peaks_degs=t["peaks_degs"], ballflight=t.get("ballflight"))
    res["cap_at_progress_1"] = episode_terms(L, shot=sh, progress=1.0, stage="C")["prior_cap"]
    return res

if __name__ == "__main__":
    m, _ = build_model("LH", CL)
    R["model"] = dict(nq=m.nq, nv=m.nv, nu=m.nu, nbody=m.nbody, ngeom=m.ngeom, neq=m.neq, nsensor=m.nsensor, total_mass_kg=float(m.body_mass.sum()), club_len_m=CL,
                      club_mass_kg=float(m.body_mass[m.body("club").id]), ball_mass_kg=float(m.body_mass[m.body("ball").id]), timestep=m.opt.timestep,
                      actuated_dof=m.nu, force_scale=1.0, joints=[m.actuator(i).name for i in range(m.nu)])
    R["actuator_limits"] = actuator_limits()
    R["handedness"] = lead_hand_side_check()
    R["mirror_kinematic_G1"] = mirror_kinematic(); R["mirror_address_LH_vs_RH"] = mirror_address()
    R["toe_sign_and_flight_mirror"] = toe_and_flight_mirror()
    R["hold_zero_action"] = [hold(dt, 2.0) for dt in (0.0005, 0.001, 0.002)]
    R["hold_zero_action_5s_dt0.001"] = hold(0.001, 5.0)
    R["passive_zero_torque_dt0.001"] = hold(0.001, 2.0, passive=True)
    R["sanity_swing"] = {f"dt{dt}_tether{t}": swings(dt, t) for dt in (0.0005, 0.001, 0.002) for t in (True, False)}
    R["throughput_steps_per_s"] = throughput()
    R["reward_demo"] = reward_demo()
    os.makedirs("results", exist_ok=True)
    json.dump(R, open("results/v5_stage0.json", "w"), indent=1, default=float)
    print(json.dumps({k: R[k] for k in ("hold_zero_action", "passive_zero_torque_dt0.001", "throughput_steps_per_s", "mirror_kinematic_G1", "mirror_address_LH_vs_RH", "handedness")}, indent=1, default=float))
