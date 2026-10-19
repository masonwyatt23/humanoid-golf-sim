"""Kinematic-sequence peaks at fine resolution: det episodes of a JEnv ckpt with segment logging every physics substep (2 ms); peak times of pelvis/thorax/lead_arm/club angular speed up to impact.
Usage: python scripts/v5_peaks_fine.py <ckpt_base> [n_eps=8] [seed0=4000]"""
import sys, json, os, numpy as np
ck = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 8; s0 = int(sys.argv[3]) if len(sys.argv) > 3 else 4000; sys.path.insert(0, os.getcwd())
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
A = json.load(open(os.path.join(os.path.dirname(ck), "args.json")))
keys = {tuple(k.split("|")): v for k, v in json.load(open(A["keys"])).items()}
W = ('xf_hard','grf_lo','grf_w','xf_cap_lo','xf_cap_w','track_floor','ord2_w','launch_w','desc_w','dloft_w','spin_lo_w','smash_w','spin_w','spin_hi','spin_scale','fine_grf','launch_hi','dl_lo','dl_hi','aoa_lo','spd_w','ctrl_dt')
def mk():
    e = JEnv(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(res_mult=(json.loads(A["res_mult"]) if A.get("res_mult") else None), **{k: A.get(k) for k in W}); return e
vn = VecNormalize.load(ck + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False
model = PPO.load(ck, device="cpu"); te = mk(); e = te.env; e.seg_every = 1
rows = []
for i in range(n):
    o, _ = te.reset(seed=s0 + i); e.seg_every = 1; done = False; info = {}
    while not done:
        a = model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, t1, t2, info = te.step(a); done = t1 or t2
    L = e.log; t = np.array(L["t"]); nn = int(np.searchsorted(t, e.t_contact, side="right")) if e.t_contact else len(t)
    pk = {k: float(t[:nn][int(np.argmax(np.abs(np.array(L[k][:nn]))))]) for k in ("pelvis", "thorax", "lead_arm", "club")}
    rows.append(dict(seed=s0 + i, mph=info.get("club_speed_mph"), dt_ms=1000 * float(np.median(np.diff(t[:nn]))), **{f"{k}_before_club_ms": round(1000 * (pk["club"] - pk[k]), 1) for k in ("pelvis", "thorax", "lead_arm")},
                     order_ok=bool(pk["pelvis"] < pk["thorax"] < pk["lead_arm"] < pk["club"])))
med = {k: float(np.median([r[k] for r in rows])) for k in ("dt_ms", "pelvis_before_club_ms", "thorax_before_club_ms", "lead_arm_before_club_ms")}
out = dict(ckpt=ck, n=n, median=med, order_ok_frac=float(np.mean([r["order_ok"] for r in rows])), eps=rows)
print(json.dumps(dict(median=med, order_ok_frac=out["order_ok_frac"])))
if len(sys.argv) > 4: json.dump(out, open(sys.argv[4], "w"), indent=1)
