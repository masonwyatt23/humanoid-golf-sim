"""Zero-pad a 116-dim JEnv policy to the DREnv --goal_obs layout (obs + GOAL_DIM=8 at the END), WITHOUT training.
First-layer input weights of BOTH mlp_extractor nets get zero columns for the 8 goal dims; VecNormalize obs_rms gets mean 0 / var 1 there.
Result ignores the goal exactly (zero weights). Optimizer state is re-initialised (not used for inference). LOCAL, NOT OFFICIAL.
Usage: PYTHONPATH=. python scripts/goal0_pad_snapshot.py <src_ckpt_base> <dst_dir> [verify_seeds=4]
Both paths are local (checkpoints are not in git); write <dst_dir> outside the repo. The output snapshot must not be committed."""
import sys, os, json, pickle, copy, shutil
import numpy as np, torch
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.dr_goal import DREnv, GOAL_DIM
from train.v5_train_j import JEnv
src, dst = sys.argv[1], sys.argv[2]; NV = int(sys.argv[3]) if len(sys.argv) > 3 else 4
os.makedirs(dst, exist_ok=True); step = src.rsplit("_", 1)[1]; out = os.path.join(dst, f"ckpt_{step}")
m = PPO.load(src, device="cpu"); n0 = m.observation_space.shape[0]; n1 = n0 + GOAL_DIM
obs1 = spaces.Box(-np.inf, np.inf, (n1,), np.float32)
pol = m.policy_class(obs1, m.action_space, m.lr_schedule, **m.policy_kwargs)
sd = m.policy.state_dict(); sd2 = {}
for k, v in sd.items():
    if v.ndim == 2 and v.shape[1] == n0 and k.endswith(("policy_net.0.weight", "value_net.0.weight")):
        v = torch.cat([v, torch.zeros(v.shape[0], GOAL_DIM, dtype=v.dtype)], 1)
    sd2[k] = v
pol.load_state_dict(sd2, strict=True); m.policy = pol; m.observation_space = obs1; m.save(out)
vn = pickle.load(open(src + "_vecnorm.pkl", "rb")); r = vn.obs_rms
r.mean = np.concatenate([r.mean, np.zeros(GOAL_DIM)]); r.var = np.concatenate([r.var, np.ones(GOAL_DIM)]); vn.observation_space = obs1
vn.venv = None; vn.class_attributes = {}; vn.returns = None; pickle.dump(vn, open(out + "_vecnorm.pkl", "wb"))
A = json.load(open(os.path.join(os.path.dirname(src), "args.json"))); A.update(goal_obs=True, tag="V10l_goal0", goal0_pad_of=src, note="zero-padded copy, ignores goal, no goal training. LOCAL, NOT OFFICIAL")
json.dump(A, open(os.path.join(dst, "args.json"), "w"))
# ---- verify: original policy on JEnv vs padded policy on DREnv(goal_obs) with non-zero goals, same seeds, deterministic
keys = {tuple(k.split("|")): v for k, v in json.load(open(A["keys"])).items()}
W = ('xf_hard','grf_lo','grf_w','xf_cap_lo','xf_cap_w','track_floor','ord2_w','launch_w','desc_w','dloft_w','spin_lo_w','smash_w','spin_w','spin_hi','spin_scale','fine_grf','launch_hi','dl_lo','dl_hi','aoa_lo','spd_w','ctrl_dt','early_w','aim_w','foot_w','plant_term','strike_w','grfd_w','post_t','tc_w','smash2_w','ctr2_w','pel_w','pel_t_w','pel_dps','pel_t_lo','pel_t_hi','sep_w','ctr_w','env_v4','tee_mode')
def mk(cls, goal):
    def f():
        if goal: cls.goal_obs = True
        e = cls(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"])
        if goal: cls.goal_obs = False; e.goal_obs = True
        e.configure(res_mult=json.loads(A['res_mult']), **{k: A.get(k) for k in W}); e.rsi = (1.0, 0.0, 0.0); e.env.arm_dist = 0.6; e.target_len = 1.15; e.target_tether = 0.0; e.env.friction_rand = False; e.track_w = 0.0; return e
    return f
GOALS = [dict(club="driver", target_carry=c, target_dir=d, shape=s, bend=b, handedness="LH") for c, d, s, b in ((230, 0, "straight", 0), (250, 3, "draw", 4), (210, -4, "fade", -5), (240, 1, "draw", 2))]
mx = 0.0; nst = 0
m0 = PPO.load(src, device="cpu"); m1 = PPO.load(out, device="cpu")
v0 = VecNormalize.load(src + "_vecnorm.pkl", DummyVecEnv([mk(JEnv, False)])); v1 = VecNormalize.load(out + "_vecnorm.pkl", DummyVecEnv([mk(DREnv, True)]))
for V in (v0, v1): V.training = False; V.norm_reward = False
for i in range(NV):
    e0 = mk(JEnv, False)(); e1 = mk(DREnv, True)(); e1.set_goal(GOALS[i % len(GOALS)])
    o0, _ = e0.reset(seed=7000 + i); o1, _ = e1.reset(seed=7000 + i); assert o1.shape == (n1,) and np.array_equal(o0, o1[:n0])
    d = False; st = 0
    while not d:
        a0, _ = m0.predict(v0.normalize_obs(o0[None]), deterministic=True); a1, _ = m1.predict(v1.normalize_obs(o1[None]), deterministic=True)
        mx = max(mx, float(np.abs(a0 - a1).max())); o0, r0, t0, tr0, i0 = e0.step(a0[0]); o1, r1, t1, tr1, i1 = e1.step(a1[0]); st += 1; d = t0 or tr0
        assert (t0 or tr0) == (t1 or tr1) and r0 == r1
    nst += st; print(f"seed {7000+i} goal {GOALS[i % len(GOALS)]} steps {st} contact {i0.get('contact')} ep.goal {i1.get('ep',{}).get('goal')}", flush=True)
print(json.dumps(dict(verify_seeds=NV, steps=nst, max_abs_action_diff=mx, n_obs=n1)))
json.dump(dict(verify_seeds=list(range(7000, 7000 + NV)), steps=nst, max_abs_action_diff=mx), open(os.path.join(dst, "verify.json"), "w"))
