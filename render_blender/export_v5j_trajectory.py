"""Export ONE deterministic JEnv (Stage J/K 'reference-guided residual with tracking assistance') rollout for build_and_render.py (same npz format as
export_policy_trajectory.py), for PREVIEW renders.  Run from anywhere with the golf venv:
    python render_blender/export_v5j_trajectory.py <ckpt_base> --out X.npz [--seed 4000] [--club-len 1.15] [--arm-dist 0.6]
Repo root = $V5_REPO if set, else the parent of render_blender/ (this file's package).
Env = the realism harness's J worker setup (results/overnight/_j_worker_gp.py): JEnv(dt=0.002), rsi=(1,0,0), arm_dist 0.6, club 1.15, tether 0,
friction nominal, track_w 0, strike gate OFF, deterministic policy.
Real (from the sim): every body's world pose and the ball, recorded EVERY physics step (2 ms) up to episode end (contact + 0.10 s), then linearly
resampled (positions; quaternions slerp/nlerp) onto a 5 ms grid because build_and_render's 'policy' cut assumes 5 ms samples.
Model (not sim): ball flight after contact = golfphys fly() from the env's own launch state (v_ball, omega_ball) at the tee (the same golfphys call the env
uses for carry), then bounce/roll to golfphys bounce_roll's rest point drawn as a straight ease (COSMETIC path; the rest point is the model's).
Bodies are held at their last simulated pose while the ball flies (episode has ended).  'club_vis' is a virtual body: origin 1.12 m up the shaft from the
real club-head centre, local -z along the real shaft (grip->head), local +x along the real face normal (renderer convention).
Scene is translated (no rotation) so the tee sits at the renderer's v1 tee (0.41, 0, z)."""
import argparse, json, os, sys
import numpy as np
CFG = ('xf_hard', 'grf_lo', 'grf_w', 'xf_cap_lo', 'xf_cap_w', 'track_floor', 'ord2_w', 'launch_w', 'desc_w', 'dloft_w', 'spin_lo_w', 'smash_w', 'spin_w', 'spin_hi', 'spin_scale', 'fine_grf', 'launch_hi', 'dl_lo', 'dl_hi', 'aoa_lo', 'spd_w', 'pel_w', 'pel_t_w', 'pel_dps', 'pel_t_lo', 'pel_t_hi', 'sep_w', 'ctr_w', 'ctrl_dt', 'tee_dz', 'ball_dx', 'face_h', 'tee_mode')  # (+K31/K32 geometry keys 2026-10-24; configure() skips None so old args are unchanged) CFG-FIX (Evaluator 2026-10-24): same configure() as results/overnight/_j_worker_gp_v3.py; the nopath exporter omitted res_mult + newer keys
# Repo root: V5_REPO env, else the directory that contains render_blender/ (no machine-path default).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TR = os.environ.get("V5_REPO", _ROOT)

def resample(t, X, tg):
    i = np.clip(np.searchsorted(t, tg) - 1, 0, len(t) - 2); u = ((tg - t[i]) / (t[i + 1] - t[i]))[:, None]
    sh = (-1,) + (1,) * (X.ndim - 1); u = u.reshape(sh)
    return (1 - u) * X[i] + u * X[i + 1], i, u

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ckpt"); ap.add_argument("--out", required=True); ap.add_argument("--seed", type=int, default=4000)
    ap.add_argument("--club-len", type=float, default=1.15); ap.add_argument("--arm-dist", type=float, default=0.6); a = ap.parse_args()
    a.ckpt = os.path.abspath(a.ckpt); a.out = os.path.abspath(a.out); sys.path.insert(0, TR); os.chdir(TR)
    import mujoco
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    from train.v5_train_j import JEnv
    from golfphys.flight import fly
    from golfphys.bounce import bounce_roll
    from golfphys.params import R_BALL
    from env.v5_shot import params
    ck = a.ckpt[:-4] if a.ckpt.endswith(".zip") else a.ckpt
    A = json.load(open(os.path.join(os.path.dirname(ck), "args.json")))
    keys = {tuple(k.split("|")): v for k, v in json.load(open(os.path.join(TR, A["keys"]))).items()} if A.get("keys") and A["keys"] != "none" else None
    def mk():
        e = JEnv(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(res_mult=(json.loads(A['res_mult']) if A.get('res_mult') else None), **{k: A.get(k) for k in CFG})
        e.rsi = (1.0, 0.0, 0.0); e.env.arm_dist = a.arm_dist; e.env.strike_gate_nx = None; e.target_len = a.club_len; e.target_tether = 0.0; e.env.friction_rand = False; e.track_w = 0.0; return e
    vn = VecNormalize.load(ck + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False
    model = PPO.load(ck, device="cpu"); te = mk(); e = te.env; m = e.m
    rec = dict(t=[], xpos=[], xquat=[], cv=[]); on = [False]; orig = mujoco.mj_step
    hg = m.geom("head").id; sg = m.geom("shaft").id
    def club_vis(d):
        hp = d.geom_xpos[hg].copy(); sdir = d.geom_xmat[sg].reshape(3, 3)[:, 2].copy()
        if np.dot(hp - d.geom_xpos[sg], sdir) < 0: sdir = -sdir          # grip -> head
        n = d.geom_xmat[hg].reshape(3, 3)[:, 0].copy(); x = n - np.dot(n, sdir) * sdir; x /= np.linalg.norm(x); z = -sdir; y = np.cross(z, x)
        q = np.zeros(4); mujoco.mju_mat2Quat(q, np.column_stack([x, y, z]).ravel()); return hp - sdir * 1.12, q
    def wrapped(mm, d, *args, **k):
        orig(mm, d, *args, **k)
        if on[0]:
            p, q = club_vis(d); rec["t"].append(d.time); rec["xpos"].append(np.vstack([d.xpos, p[None]])); rec["xquat"].append(np.vstack([d.xquat, q[None]]))
    mujoco.mj_step = wrapped
    try:
        o, _ = te.reset(seed=a.seed); on[0] = True; done = False; info = {}
        while not done:
            act = model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, t1, t2, info = te.step(act); done = t1 or t2
    finally:
        mujoco.mj_step = orig
    assert e.contact, "no contact in this rollout"
    names = [m.body(i).name for i in range(m.nbody)] + ["club_vis"]; bid = names.index("ball")
    t = np.array(rec["t"]); XP = np.array(rec["xpos"]); XQ = np.array(rec["xquat"])
    tg = np.arange(t[0], t[-1] + 1e-9, 0.005); XPr, i, u = resample(t, XP, tg)
    q0, q1 = XQ[i], XQ[i + 1]; q1 = np.where((np.sum(q0 * q1, -1) < 0)[..., None], -q1, q1); XQr = (1 - u) * q0 + u * q1; XQr /= np.linalg.norm(XQr, axis=-1, keepdims=True)
    imp = int(np.searchsorted(tg, e.t_contact))
    # ball: sim up to contact (held on tee), then golfphys flight from the env's own launch state, then roll ease to the model rest point
    sh = e.shot; tee = np.array(e.tee, float); p = params()
    fl = fly((0.0, 0.0, R_BALL + max(tee[2] - R_BALL, 0.0)), tuple(sh["v_ball"]), tuple(sh["omega_ball"]), p, dt=0.005, keep_traj=True)
    tr = np.array(fl.traj if hasattr(fl, "traj") else fl.trajectory, float)          # (t, x, y, z)
    b = bounce_roll(fl.land_pos, fl.land_vel, fl.land_spin, "normal"); rest = np.array([b["rest_x"], b["rest_y"], R_BALL])
    roll_s = 2.0; nroll = int(roll_s / 0.005); land = tr[-1, 1:4]; uu = np.linspace(0, 1, nroll + 1)[1:]; ease = 1 - (1 - uu) ** 2
    path = np.vstack([tr[:, 1:4], land[None] + ease[:, None] * (rest - land)[None]]) + np.array([tee[0], tee[1], 0.0])
    nb = imp + len(path); NS = max(nb, len(tg))
    XPf = np.concatenate([XPr, np.repeat(XPr[-1:], NS - len(tg), 0)]); XQf = np.concatenate([XQr, np.repeat(XQr[-1:], NS - len(tg), 0)])
    ball = np.zeros((NS, 3)); ball[:imp] = XPr[:imp, bid]; ball[imp:imp + len(path)] = path; ball[imp + len(path):] = path[-1]
    T = tg[0] + 0.005 * np.arange(NS)
    off = np.array([0.41, 0.0, 0.0]) - np.array([tee[0], tee[1], 0.0]); XPf = XPf + off; ball = ball + off
    out = dict(t=T, xpos=XPf, xquat=XQf, ball=ball, body_names=np.array(names), impact_idx=imp, club_head_geom_offset=np.array([0, 0, -1.12]), club_head_body="club_vis",
               club_shaft_fromto=np.array([0, 0, 0, 0, 0, -1.12]), v_sep=np.asarray(sh["v_ball"], float), scene_offset=off)
    np.savez(a.out, **out)
    r = sh["shot"]; ep = dict(club_speed_mph=info.get("club_speed_mph"), ball_speed_mph=info.get("ball_speed_mph"), launch_deg=info.get("launch_deg"), spin_rpm=info.get("spin_rpm"), smash=info.get("smash"),
              env_carry_yd=r.carry_m * 1.0936133, env_total_yd=r.total_m * 1.0936133, env_descent_deg=r.descent_deg, flight_path_carry_yd=float(np.hypot(*(land[:2]))) * 1.0936133, rest_from_tee_yd=float(np.hypot(*rest[:2])) * 1.0936133)
    js = dict(ckpt=os.path.abspath(ck), seed=a.seed, env="JEnv dt 0.002 rsi (1,0,0) arm_dist %.2f club %.2f tether 0 gate OFF deterministic" % (a.arm_dist, a.club_len), episode=ep, samples=int(NS), sim_samples=int(len(tg)), impact_idx=imp,
              sample_dt_s=0.005, recorded_dt_s=float(np.median(np.diff(t))), lead=e.lead, scene_offset=off.tolist(), notes=__doc__)
    open(os.path.splitext(a.out)[0] + ".json", "w").write(json.dumps(js, indent=1, default=float)); print(json.dumps(dict(ep=ep, NS=NS, sim=len(tg), imp=imp), default=float))
main()
