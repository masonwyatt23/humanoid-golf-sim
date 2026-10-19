"""Subprocess worker for realism_check --env v5. Runs in the TRAINER's repo (its `env`/`train` packages collide with this repo's `env`), so it imports nothing from this repo.
Usage: python _v5_worker.py <trainer_repo> <ckpt_base> <club_len> <seed0> <n> <out.json> [arm_dist=0.6]. arm_dist>0 builds the Trainer's train.v5_train_b.BEnv (what Stage B2-B4/C train with); arm_dist==0 builds TrainEnv (Stage A; at arm_dist 0 a policy can tap at address, so B/C results at 0 are artifacts). Deterministic rollouts, tether 0, friction nominal, as scripts/v5_eval_ckpt.py."""
import sys, json, math
repo, ck, L, seed0, n, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
ARM = float(sys.argv[7]) if len(sys.argv) > 7 else 0.6
# optional argv[8]: Trainer's Stage G+ strike gate (V5GolfEnv.strike_gate_nx). 'off'/absent = None (default). Mirrors train/v5_train_g.py GEnv: e.env.strike_gate_nx = nx on the V5GolfEnv; a head-ball contact only counts if face normal n_x >= nx AND head v_x > 0 AND v.n > 0, else FOUL (ball disabled, episode terminates; contact stays False).
GATE = None if len(sys.argv) <= 8 or sys.argv[8].lower() in ('off', 'none', '') else float(sys.argv[8])
# optional argv[9]: 'seg1' = log segment speeds/GRF at EVERY physics substep (realism_check --timing-res-ms). Logging only reads state (mj_objectVelocity, contact forces); dynamics and actions are unchanged.
SEG1 = len(sys.argv) > 9 and sys.argv[9] == 'seg1'
sys.path.insert(0, repo)
import numpy as np, mujoco
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train import TrainEnv
if ARM > 0:
    from train.v5_train_b import BEnv
def mk():
    e = (BEnv if ARM > 0 else TrainEnv)(dt=0.002, seed=123); e.env.arm_dist = ARM; e.env.strike_gate_nx = GATE; e.target_len = L; e.target_tether = 0.0; e.env.friction_rand = False; return e
vn = VecNormalize.load(ck + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False
model = PPO.load(ck, device="cpu"); te = mk(); e = te.env; e.log_segments = True
bw = float(sum(e.m.body_mass[i] for i in range(e.m.nbody) if e.m.body(i).name not in ("ball",)) * 9.81)
grf = []; sub = []; foot = []; orig = e._log_seg
def seg():
    orig(); fl, fr = e.foot_forces(); grf.append((fl, fr)); sub.append(int(e.sub_count))
    sid = e.m.site(f"{e.lead}_sole_site").id; P = e.d.site_xpos[sid]; R = e.d.site_xmat[sid].reshape(3, 3); hx = float(e.m.site_size[sid][0])   # lead sole: centre xyz + heel/toe z + yaw (atan2 of sole +x in world xy)
    yaw = float(np.arctan2(R[1, 0], R[0, 0])); foot.append([float(P[0]), float(P[1]), float(P[2]), float((P - hx * R[:, 0])[2]), float((P + hx * R[:, 0])[2]), yaw])
e._log_seg = seg
eps = []; SEG_DEF = int(e.seg_every)   # default logging cadence (2 substeps = 4 ms at dt 0.002), captured once before any seg1 override
for i in range(n):
    grf.clear(); sub.clear(); foot.clear(); e.seg_every = SEG_DEF; o, _ = te.reset(seed=seed0 + i); e.seg_every = SEG_DEF; seg_def = SEG_DEF; done = False; info = {}
    if SEG1: e.seg_every = 1
    while not done:
        a = model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, term, trunc, info = te.step(a); done = term or trunc
    L_ = e.log; tc = e.t_contact; t = np.array(L_["t"])
    imp = int(np.argmax(t >= tc)) if tc is not None and (t >= tc).any() else len(t) - 1
    shx = {}
    if e.contact and getattr(e, "shot", None):
        _s = e.shot; _r = _s["shot"]; shx = dict(azimuth_deg=_s.get("azimuth_deg"), backspin_rpm=_s.get("backspin_rpm"), sidespin_rpm=_s.get("sidespin_rpm"), env_carry_m=_r.carry_m, env_total_m=_r.total_m, env_descent_deg=_r.descent_deg, env_lateral_m=_r.lateral_carry_m)
    eps.append(dict(shot_extra=shx, foot_length_m=0.20, t=L_["t"], pelvis_dps=L_["pelvis"], thorax_dps=L_["thorax"], arm_dps=L_["lead_arm"], club_dps=L_["club"], xfactor_deg=L_["xfactor_deg"], lead_share=L_["lead_share"],
                    grf=[list(map(float, g)) for g in grf], lead_foot=[list(f_) for f_ in foot], t_top=None, lead=e.lead, impact_idx=imp, contact=bool(e.contact), ep=info.get("ep"), foul=bool(info.get("foul", False)), seed=seed0 + i, t_contact=tc, sub=list(sub), seg_every=int(e.seg_every), seg_every_default=int(seg_def),
                    shot={k: info.get(k) for k in ("club_speed_mph", "ball_speed_mph", "launch_deg", "spin_rpm", "smash", "carry_m_noroll", "total_m_model", "lateral_carry_m")}))
json.dump(dict(strike_gate_nx=GATE, arm_dist=ARM, env_class=("BEnv" if ARM > 0 else "TrainEnv"), bw_N=bw, dt=float(e.dt) * SEG_DEF, dt_note="declared = sim dt x default seg_every (4 ms at dt 0.002); the harness MEASURES the interval from t (dt fix 2026-10-19; was hard-coded 0.005)", club_len=L, foot_length_m=0.20, eps=eps), open(out, "w"))
