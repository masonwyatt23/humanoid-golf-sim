"""Deterministic eval of a v5 B/C checkpoint: tether 0, friction nominal, club 1.15, arm_dist selectable (0 = what eval/_v5_worker.py uses via TrainEnv; 0.6 = what B2-B4/C train with).
club_mph = IMPACT-time head-site speed (prev_v at the contact substep) in both. Usage: v5_eval_b.py <ckpt_base> <arm_dist> [n] [seed0]"""
import sys, json, numpy as np
sys.path.insert(0, '.')
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_b import BEnv
from train.v5_train import TrainEnv
ck, ad, n, s0 = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 24, int(sys.argv[4]) if len(sys.argv) > 4 else 4000
def mk():
    e = BEnv(dt=0.002, seed=123); e.env.arm_dist = ad; e.target_len = 1.15; e.target_tether = 0.0; e.env.friction_rand = False; return e
vn = VecNormalize.load(ck + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False
m = PPO.load(ck, device="cpu"); te = mk(); rows = []
for i in range(n):
    o, _ = te.reset(seed=s0 + i); done = False
    while not done:
        a = m.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, t1, t2, info = te.step(a); done = t1 or t2
    rows.append(info["ep"])
c = [x for x in rows if x["contact"]]
print(json.dumps(dict(ckpt=ck, arm_dist=ad, n=n, contact=len(c)/n, fell=float(np.mean([x["fell"] for x in rows])),
  impact_mph_median=float(np.median([x["club_mph"] for x in c])) if c else 0, impact_mph_max=float(max([x["club_mph"] for x in c])) if c else 0,
  carry_median=float(np.median([x["carry"] for x in c])) if c else 0, lat_std=float(np.std([x["lat"] for x in c])) if c else 0)))
