"""Subprocess worker for realism_check --env v5. Runs in the TRAINER's repo (its `env`/`train` packages collide with this repo's `env`), so it imports nothing from this repo.
Usage: python _v5_worker.py <trainer_repo> <ckpt_base> <club_len> <seed0> <n> <out.json>. Deterministic rollouts, tether 0, friction nominal, as scripts/v5_eval_ckpt.py."""
import sys, json, math
repo, ck, L, seed0, n, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
sys.path.insert(0, repo)
import numpy as np, mujoco
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train import TrainEnv
def mk():
    e = TrainEnv(dt=0.002, seed=123); e.target_len = L; e.target_tether = 0.0; e.env.friction_rand = False; return e
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
    eps.append(dict(t=L_["t"], pelvis_dps=L_["pelvis"], thorax_dps=L_["thorax"], arm_dps=L_["lead_arm"], club_dps=L_["club"], xfactor_deg=L_["xfactor_deg"], lead_share=L_["lead_share"],
                    grf=[list(map(float, g)) for g in grf], lead=e.lead, impact_idx=imp, contact=bool(e.contact), ep=info.get("ep"), seed=seed0 + i,
                    shot={k: info.get(k) for k in ("club_speed_mph", "ball_speed_mph", "launch_deg", "spin_rpm", "smash", "carry_m_noroll", "total_m_model", "lateral_carry_m")}))
json.dump(dict(bw_N=bw, dt=0.005, club_len=L, eps=eps), open(out, "w"))
