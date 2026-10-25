"""Training-DR slope check (LOCAL, NOT OFFICIAL): DREnv dr=True at a given curriculum stage with V10l 100k (deterministic) or zero action;
per episode logs the DR slope draw, QACC warnings, fell, contact. Env: HGS_V10L_CKPT (required; checkpoint not in git). Usage: PYTHONPATH=. python scripts/slope_train_check.py <zero|v10l> <stage> <n> [plumb]  (4th arg 'plumb' = DREnv --plumb_addr on)"""
import sys, json, numpy as np, mujoco
pol, stage, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); FIX = (sys.argv[4] == 'plumb') if len(sys.argv) > 4 else False
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.dr_goal import DREnv
import os
CK = os.environ.get("HGS_V10L_CKPT") or sys.exit("set HGS_V10L_CKPT to the local V10l 100k checkpoint base (<local-path>/V10l_s104_100000/ckpt_100000; args.json must sit beside it)")
A = json.load(open(os.path.join(os.path.dirname(CK), "args.json")))
keys = {tuple(k.split("|")): v for k, v in json.load(open(A["keys"])).items()}
W = ('xf_hard','grf_lo','grf_w','xf_cap_lo','xf_cap_w','track_floor','ord2_w','launch_w','desc_w','dloft_w','spin_lo_w','smash_w','spin_w','spin_hi','spin_scale','fine_grf','launch_hi','dl_lo','dl_hi','aoa_lo','spd_w','ctrl_dt','early_w','aim_w','foot_w','plant_term','strike_w','grfd_w','post_t','tc_w','smash2_w','ctr2_w','pel_w','pel_t_w','pel_dps','pel_t_lo','pel_t_hi','sep_w','ctr_w','env_v4','tee_mode')
def mk():
    e = DREnv(dt=0.002, seed=5, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(res_mult=json.loads(A['res_mult']), **{k: A.get(k) for k in W})
    e.rsi = (1.0, 0.0, 0.0); e.env.arm_dist = 0.6; e.target_len = 1.15; e.target_tether = 0.0; e.track_w = 0.0; e.dr = True; e.dr_stage = stage
    if FIX: e.configure(plumb_addr=True)
    return e
if pol == "v10l": model = PPO.load(CK, device="cpu"); vn = VecNormalize.load(CK + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False
e = mk(); rows = []
for i in range(N):
    o, _ = e.reset(seed=1000 + i); d = e.env.d; w0 = int(d.warning[mujoco.mjtWarning.mjWARN_BADQACC].number); done = False; info = {}
    while not done:
        a = np.zeros(e.action_space.shape) if pol == "zero" else model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]
        o, r, te, tr, info = e.step(a); done = te or tr
    sl = e.dr_log.get("slope", (0.0, 0.0))[0]
    rows.append(dict(slope=sl, qacc=int(d.warning[mujoco.mjtWarning.mjWARN_BADQACC].number) - w0, fell=bool(info.get("fell")), contact=bool(info.get("contact"))))
def summ(rs, nm):
    if rs: print(f"  {nm}: n {len(rs)} contact {np.mean([r['contact'] for r in rs]):.2f} fell {np.mean([r['fell'] for r in rs]):.2f} qacc_eps {np.mean([r['qacc'] > 0 for r in rs]):.2f}")
print(f"{pol} stage {stage} N {N} plumb_addr {FIX}")
summ(rows, "all"); summ([r for r in rows if r["slope"] == 0], "no slope"); summ([r for r in rows if 0 < r["slope"] <= 0.02], "slope 0-2%"); summ([r for r in rows if 0.02 < r["slope"] <= 0.045], "slope 2-4.5%"); summ([r for r in rows if r["slope"] > 0.045], "slope 4.5-7%")
