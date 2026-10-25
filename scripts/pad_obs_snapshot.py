"""Zero-pad a JEnv policy by K obs dims at the END (V18 --stance_obs, K=4), no training. First-layer weights of both mlp nets get zero columns; VecNormalize mean 0 / var 1 there.
Verifies padded policy on JEnv(stance_obs) == original on JEnv, same seeds, deterministic. LOCAL. Usage: PYTHONPATH=. python scripts/pad_obs_snapshot.py <src_ckpt_base> <dst_dir> [K=4] [verify=4]"""
import sys, os, json, pickle, numpy as np, torch
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
src, dst = sys.argv[1], sys.argv[2]; K = int(sys.argv[3]) if len(sys.argv) > 3 else 4; NV = int(sys.argv[4]) if len(sys.argv) > 4 else 4
os.makedirs(dst, exist_ok=True); out = os.path.join(dst, os.path.basename(src))
m = PPO.load(src, device="cpu"); n0 = m.observation_space.shape[0]; obs1 = spaces.Box(-np.inf, np.inf, (n0 + K,), np.float32)
pol = m.policy_class(obs1, m.action_space, m.lr_schedule, **m.policy_kwargs); sd2 = {}
for k, v in m.policy.state_dict().items():
    if v.ndim == 2 and v.shape[1] == n0 and k.endswith(("policy_net.0.weight", "value_net.0.weight")): v = torch.cat([v, torch.zeros(v.shape[0], K, dtype=v.dtype)], 1)
    sd2[k] = v
pol.load_state_dict(sd2, strict=True); m.policy = pol; m.observation_space = obs1; m.save(out)
vn = pickle.load(open(src + "_vecnorm.pkl", "rb")); r = vn.obs_rms; r.mean = np.concatenate([r.mean, np.zeros(K)]); r.var = np.concatenate([r.var, np.ones(K)]); vn.observation_space = obs1
vn.venv = None; vn.class_attributes = {}; vn.returns = None; pickle.dump(vn, open(out + "_vecnorm.pkl", "wb"))
A = json.load(open(os.path.join(os.path.dirname(src), "args.json"))); A.update(stance_obs=True, pad_of=src, note=f"zero-padded +{K} obs dims (stance_obs), no training. LOCAL"); json.dump(A, open(os.path.join(dst, "args.json"), "w"))
keys = {tuple(k.split("|")): v for k, v in json.load(open("results/v5_runs/stageV12X_ref_s1/tuned_keys_flat.json")).items()}
def mk(st):
    def f():
        e = JEnv(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(res_mult=json.loads(A['res_mult']), env_v4=True, tee_mode='1.5in', stance_obs=(True if st else None)); e.rsi = (1.0, 0.0, 0.0); e.track_w = 0.0; return e
    return f
m0 = PPO.load(src, device="cpu"); m1 = PPO.load(out, device="cpu"); v0 = VecNormalize.load(src + "_vecnorm.pkl", DummyVecEnv([mk(False)])); v1 = VecNormalize.load(out + "_vecnorm.pkl", DummyVecEnv([mk(True)]))
for V in (v0, v1): V.training = False; V.norm_reward = False
mx = 0.0
for i in range(NV):
    e0, e1 = mk(False)(), mk(True)(); o0, _ = e0.reset(seed=7000 + i); o1, _ = e1.reset(seed=7000 + i); assert np.array_equal(o0, o1[:n0]); d = False
    while not d:
        a0, _ = m0.predict(v0.normalize_obs(o0[None]), deterministic=True); a1, _ = m1.predict(v1.normalize_obs(o1[None]), deterministic=True); mx = max(mx, float(np.abs(a0 - a1).max()))
        o0, _, t0, tr0, _ = e0.step(a0[0]); o1, _, t1, tr1, _ = e1.step(a1[0]); d = t0 or tr0
print(json.dumps(dict(verify=NV, max_abs_action_diff=mx, n_obs=n0 + K))); json.dump(dict(verify_seeds=NV, max_abs_action_diff=mx), open(os.path.join(dst, "verify.json"), "w"))
