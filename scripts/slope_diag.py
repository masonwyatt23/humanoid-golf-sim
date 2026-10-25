"""Heldout-2 slope instability diagnostic (LOCAL, NOT OFFICIAL). Gravity-tilt slope as in DREnv._apply_model_dr, applied before reset.
Per episode: QACC (mjWARN_BADQACC) warning count + first time, min foot-floor contact dist at reset and over the first 0.2 s, fell, contact, pelvis tilt.
Env: HGS_V10L_CKPT (required; checkpoint not in git). Usage: PYTHONPATH=. python scripts/slope_diag.py <policy: zero|v10l> <grades comma> <n per grade> [plumb]  (4th arg 'plumb' = DREnv --plumb_addr on)"""
import sys, json, math, numpy as np, mujoco
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.dr_goal import DREnv
import os
CK = os.environ.get("HGS_V10L_CKPT") or sys.exit("set HGS_V10L_CKPT to the local V10l 100k checkpoint base (<local-path>/V10l_s104_100000/ckpt_100000; args.json must sit beside it)")
A = json.load(open(os.path.join(os.path.dirname(CK), "args.json")))
keys = {tuple(k.split("|")): v for k, v in json.load(open(A["keys"])).items()}
W = ('xf_hard','grf_lo','grf_w','xf_cap_lo','xf_cap_w','track_floor','ord2_w','launch_w','desc_w','dloft_w','spin_lo_w','smash_w','spin_w','spin_hi','spin_scale','fine_grf','launch_hi','dl_lo','dl_hi','aoa_lo','spd_w','ctrl_dt','early_w','aim_w','foot_w','plant_term','strike_w','grfd_w','post_t','tc_w','smash2_w','ctr2_w','pel_w','pel_t_w','pel_dps','pel_t_lo','pel_t_hi','sep_w','ctr_w','env_v4','tee_mode')
pol, grades, N = sys.argv[1], [float(x) for x in sys.argv[2].split(",")], int(sys.argv[3]); SETTLE = (sys.argv[4] == 'plumb') if len(sys.argv) > 4 else False
def mk():
    e = DREnv(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(res_mult=json.loads(A['res_mult']), **{k: A.get(k) for k in W})
    e.rsi = (1.0, 0.0, 0.0); e.env.arm_dist = 0.6; e.target_len = 1.15; e.target_tether = 0.0; e.env.friction_rand = False; e.track_w = 0.0
    if SETTLE: e.configure(plumb_addr=True)
    return e
if pol == "v10l":
    model = PPO.load(CK, device="cpu"); vn = VecNormalize.load(CK + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False
e = mk(); e.reset(seed=1); m = e.env.m; G0 = m.opt.gravity.copy(); rng = np.random.default_rng(0); out = {}
def foot_min(env):
    d = env.d; best = 9.0
    for i in range(d.ncon):
        c = d.contact[i]
        if env.floor in (c.geom1, c.geom2): best = min(best, c.dist)
    return best
for g in grades:
    rows = []
    for i in range(N):
        az = rng.uniform(0, 2 * math.pi); t = math.atan(g); G = float(np.linalg.norm(G0))
        e._slope_g = (G * math.sin(t) * math.cos(az), G * math.sin(t) * math.sin(az), -G * math.cos(t))
        m.opt.gravity[:] = e._slope_g
        o, _ = e.reset(seed=920000 + i); assert e.env.m is m and np.allclose(m.opt.gravity, e._slope_g); pl = getattr(e, 'plumb_log', None); d = e.env.d; w0 = int(d.warning[mujoco.mjtWarning.mjWARN_BADQACC].number); pen0 = foot_min(e.env); pen = pen0; t_first = None; done = False; info = {}; k = 0
        while not done:
            a = np.zeros(e.action_space.shape) if pol == "zero" else model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]
            o, r, te, tr, info = e.step(a); k += 1; done = te or tr
            if k <= 10: pen = min(pen, foot_min(e.env))
            if t_first is None and d.warning[mujoco.mjtWarning.mjWARN_BADQACC].number > w0: t_first = round(float(d.time), 3)
        rows.append(dict(az=round(math.degrees(az)), qacc=int(d.warning[mujoco.mjtWarning.mjWARN_BADQACC].number) - w0, t_qacc=t_first, contact=bool(info.get("contact")), fell=bool(info.get("fell")), foul=bool(info.get("foul")),
                         pen0_mm=round(pen0 * 1e3, 2), pen10_mm=round(pen * 1e3, 2), steps=k, plumb=pl))
    m.opt.gravity[:] = G0
    q = [r_ for r_ in rows if r_["qacc"] > 0]
    out[g] = dict(n=N, contact=sum(r_["contact"] for r_ in rows), fell=sum(r_["fell"] for r_ in rows), qacc_eps=len(q), rows=rows)
    print(f"{pol} plumb_addr={SETTLE} grade {g}: contact {out[g]['contact']}/{N} fell {out[g]['fell']} qacc_eps {len(q)}", flush=True)
    for r_ in rows: print("   ", r_)
