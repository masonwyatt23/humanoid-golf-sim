"""E2E check (LOCAL, NOT OFFICIAL): V10l_goal0 (zero-padded, ignores goal) on DREnv goal_obs + goal_sample + goal_w (+impact_log, dr optional) for N episodes,
through the trainer's make() (FLAG GUARD). Prints sampled goal, obs goal block, task-reward terms, total reward with vs without goal_w.
Env: HGS_GOAL0_CKPT (e.g. <local>/V10l_goal0_s104_100000/ckpt_100000). Usage: PYTHONPATH=. python scripts/goal_e2e_check.py [N=2] [dr]"""
import os, sys, json, numpy as np
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2; DRON = "dr" in sys.argv[2:]
sys.argv = [sys.argv[0]]
import train.v5_train_dr as T
from train.dr_goal import GOAL_DIM
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
CK = os.environ.get("HGS_GOAL0_CKPT") or sys.exit("set HGS_GOAL0_CKPT")
A = json.load(open(os.path.join(os.path.dirname(CK), "args.json"))); keys = {tuple(k.split("|")): v for k, v in json.load(open(A["keys"])).items()}
W = ('xf_hard','grf_lo','grf_w','xf_cap_lo','xf_cap_w','track_floor','ord2_w','launch_w','desc_w','dloft_w','spin_lo_w','smash_w','spin_w','spin_hi','spin_scale','fine_grf','launch_hi','dl_lo','dl_hi','aoa_lo','spd_w','ctrl_dt','early_w','aim_w','foot_w','plant_term','strike_w','grfd_w','post_t','tc_w','smash2_w','ctr2_w','pel_w','pel_t_w','pel_dps','pel_t_lo','pel_t_hi','sep_w','ctr_w','env_v4','tee_mode')
extra = dict({k: A.get(k) for k in W}, res_mult=json.loads(A["res_mult"]), fast_env=True)
def build(gw):
    dx = dict(goal_obs=True, goal_sample=True, goal_w=gw, impact_log=True, dr=(True if DRON else None), dr_stage=(2 if DRON else None))
    dx = {k: v for k, v in dx.items() if v}
    e = T.make(0, 7, 0.002, keys, A["res_scale"], A["t_down"], extra, dx)(); e.rsi = (1.0, 0.0, 0.0); return e
m = PPO.load(CK, device="cpu"); vn = VecNormalize.load(CK + "_vecnorm.pkl", DummyVecEnv([lambda: build(5.0)])); vn.training = False
out = []
for gw in (5.0, None):
    e = build(gw); R = []
    for i in range(N):
        o, _ = e.reset(seed=4242 + i); assert o.shape[0] == 116 + GOAL_DIM; gb = o[-GOAL_DIM:].round(3).tolist(); done = False; tot = 0.0
        while not done:
            o, r, te, tr, info = e.step(m.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]); tot += r; done = te or tr
        ep = info.get("ep", {}); R.append(tot)
        print(f"goal_w={gw} ep{i} goal={e.goal} obs_goal={gb} contact={info.get('contact')} carry={info.get('carry_m_noroll')} az={info.get('azimuth_deg')} "
              f"terms={ {k: v for k, v in ep.items() if k.startswith('goal_') and k != 'goal'} } impact={ {k: round(v, 2) for k, v in info.items() if k.startswith('impact_')} } ep_goal_logged={'goal' in ep} R={tot:.4f}", flush=True)
    out.append(R)
print("reward diff (goal_w 5 - off) per ep:", [round(a - b, 4) for a, b in zip(*out)])
