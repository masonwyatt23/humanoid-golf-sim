"""Subprocess worker for realism_check --env v5. Runs in the TRAINER's repo (its `env`/`train` packages collide with this repo's `env`), so it imports nothing from this repo.
Usage: python _v5_worker.py <trainer_repo> <ckpt_base> <club_len> <seed0> <n> <out.json> [arm_dist=0.6]. arm_dist>0 builds the Trainer's train.v5_train_b.BEnv (what Stage B2-B4/C train with); arm_dist==0 builds TrainEnv (Stage A; at arm_dist 0 a policy can tap at address, so B/C results at 0 are artifacts). Deterministic rollouts, tether 0, friction nominal, as scripts/v5_eval_ckpt.py."""
import sys, json, math
repo, ck, L, seed0, n, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
ARM = float(sys.argv[7]) if len(sys.argv) > 7 else 0.6
# optional argv[8]: Trainer's Stage G+ strike gate (V5GolfEnv.strike_gate_nx). 'off'/absent = None (default). Mirrors train/v5_train_g.py GEnv: e.env.strike_gate_nx = nx on the V5GolfEnv; a head-ball contact only counts if face normal n_x >= nx AND head v_x > 0 AND v.n > 0, else FOUL (ball disabled, episode terminates; contact stays False).
GATE = None if len(sys.argv) <= 8 or sys.argv[8].lower() in ('off', 'none', '') else float(sys.argv[8])
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
grf = []; orig = e._log_seg
def seg():
    orig(); fl, fr = e.foot_forces(); grf.append((fl, fr))
e._log_seg = seg
eps = []
for i in range(n):
    grf.clear(); o, _ = te.reset(seed=seed0 + i); done = False; info = {}
    while not done:
        a = model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, term, trunc, info = te.step(a); done = term or trunc
    L_ = e.log; tc = e.t_contact; t = np.array(L_["t"])
    imp = int(np.argmax(t >= tc)) if tc is not None and (t >= tc).any() else len(t) - 1
    shx = {}
    if e.contact and getattr(e, "shot", None):
        _s = e.shot; _r = _s["shot"]; shx = dict(azimuth_deg=_s.get("azimuth_deg"), backspin_rpm=_s.get("backspin_rpm"), sidespin_rpm=_s.get("sidespin_rpm"), env_carry_m=_r.carry_m, env_total_m=_r.total_m, env_descent_deg=_r.descent_deg, env_lateral_m=_r.lateral_carry_m)
    eps.append(dict(shot_extra=shx, t=L_["t"], pelvis_dps=L_["pelvis"], thorax_dps=L_["thorax"], arm_dps=L_["lead_arm"], club_dps=L_["club"], xfactor_deg=L_["xfactor_deg"], lead_share=L_["lead_share"],
                    grf=[list(map(float, g)) for g in grf], lead=e.lead, impact_idx=imp, contact=bool(e.contact), ep=info.get("ep"), foul=bool(info.get("foul", False)), seed=seed0 + i,
                    shot={k: info.get(k) for k in ("club_speed_mph", "ball_speed_mph", "launch_deg", "spin_rpm", "smash", "carry_m_noroll", "total_m_model", "lateral_carry_m")}))
json.dump(dict(strike_gate_nx=GATE, arm_dist=ARM, env_class=("BEnv" if ARM > 0 else "TrainEnv"), bw_N=bw, dt=0.005, club_len=L, eps=eps), open(out, "w"))
