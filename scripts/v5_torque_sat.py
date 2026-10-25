"""Torque/speed saturation check on a JEnv ckpt (det, seed 4000): stock torque self.tau, rated speed self.vmax; samples every 5 ms (each _derate) over the 300 ms before impact."""
import sys, json, os, numpy as np
ck = sys.argv[1]; sys.path.insert(0, os.getcwd())
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
A = json.load(open(os.path.join(os.path.dirname(ck), "args.json")))
keys = {tuple(k.split("|")): v for k, v in json.load(open(A["keys"])).items()}
W = ('xf_hard','grf_lo','grf_w','xf_cap_lo','xf_cap_w','track_floor','ord2_w','launch_w','desc_w','dloft_w','spin_lo_w','smash_w','spin_w','spin_hi','spin_scale','fine_grf','launch_hi','dl_lo','dl_hi','aoa_lo','spd_w','stance_obs','env_v4','fast_env','tee_mode')
def mk():
    e = JEnv(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(**{k: A.get(k) for k in W}); return e
vn = VecNormalize.load(ck + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False
model = PPO.load(ck, device="cpu"); te = mk()
b = te
while not hasattr(b, "_derate") or not hasattr(b, "tau"): b = b.env
m, d = b.m, b.d; names = [b.m.actuator(i).name for i in range(b.m.nu)]
rec = []; orig = b._log_seg
def der():
    orig(); rec.append((bool(b.contact), np.abs(b.d.actuator_force).copy() / b.tau, np.abs(b.d.qvel[b.da]) / b.vmax))
b._log_seg = der
o, _ = te.reset(seed=4000); rec.clear(); done = False; info = {}
while not done:
    a = model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, t1, t2, info = te.step(a); done = t1 or t2
print("nrec", len(rec), "first contact idx", next(i for i, r in enumerate(rec) if r[0]), "maxF", max(r[1].max() for r in rec), "type", type(b).__name__, b is te.env)
ic = next(i for i, r in enumerate(rec) if r[0]); W_ = rec[max(0, ic - 60):ic]
F = np.array([r[1] for r in W_]); V = np.array([r[2] for r in W_]); H = np.minimum(1, F + V)  # torque used + speed derate (1 = no headroom)
print("mph", round(info.get("club_speed_mph", 0), 1), "samples", len(F))
for i in np.argsort(-(F >= 0.97).mean(0) - H.mean(0))[:16]:
    print(f"{names[i]:28s} tau {b.tau[i]:5.0f} peak|F|/tau {F[:,i].max():.2f} sat(>=0.97) {(F[:,i]>=0.97).mean():.2f} peak qd/vmax {V[:,i].max():.2f} mean(F+V) {H[:,i].mean():.2f}")
