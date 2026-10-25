"""STEP2(1) equivalence check (read-only): V10l 100k policy (deterministic) and random actions on 3 seeds, 3 episodes each, with env.fast_env off vs on.
Prints the md5 of the full (reward, terminated, truncated, info, obs) trace for each and asserts they are identical. Usage: python scripts/fast_env_equiv.py [CKPT]"""
import sys, json, hashlib, pickle, numpy as np; sys.path.insert(0, '.')
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
CK = sys.argv[1] if len(sys.argv) > 1 else 'results/v5_runs/_snap/V10l_s104_100000/ckpt_100000'
A = json.load(open(CK.rsplit('/', 1)[0] + '/args.json'))
SKIP = {'seed', 'steps', 'init_ck', 'workers', 'dt', 'tag', 'keys', 'res_scale', 't_down', 'T0', 'res_mult', 'lr', 'ent', 'log_std', 'log_std_end', 'std_end', 'track_hold', 'track_len', 'track_end', 'h_every', 'snap_every', 'T_step', 'carry_min', 'no_stop', 'sel_k4', 'desc_sel', 'rate_w'}
def mk(fast):
    def f():
        keys = {tuple(k.split('|')): v for k, v in json.load(open(A['keys'])).items()}
        e = JEnv(seed=999, keys=keys, res_scale=A['res_scale'], t_down=A['t_down']); e.configure(**{k: v for k, v in A.items() if k not in SKIP})
        e.configure(res_mult=json.loads(A['res_mult']) if A.get('res_mult') else None); e.rsi = (1.0, 0.0, 0.0); e.prior_w = 0.0; e.env.arm_dist = 0.6; e.hit_tol = 0.02; e.target_len = 1.15; e.speed_T = A['T0']
        e.env.fast_env = fast; return e
    return f
def clean(x):
    if isinstance(x, dict): return {k: clean(v) for k, v in sorted(x.items())}
    if isinstance(x, (list, tuple)): return [clean(v) for v in x]
    if isinstance(x, np.ndarray): return x.tobytes()
    if isinstance(x, (np.floating, np.integer, np.bool_)): return x.item()
    return x
res = {}
for fast in (False, True):
    vn = VecNormalize.load(CK + '_vecnorm.pkl', DummyVecEnv([mk(fast)])); vn.training = False; m = PPO.load(CK, device='cpu'); e = vn.venv.envs[0]
    h = hashlib.md5(); nst = 0; rsum = 0.0
    for seed in (4000, 7000, 7001):
        rng = np.random.default_rng(seed)
        for ep in range(3):
            o, _ = e.reset(seed=seed * 10 + ep); done = False
            while not done:
                a = m.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0] if ep < 2 else rng.uniform(-1, 1, e.action_space.shape)
                o, r, te, tr, info = e.step(a); done = te or tr; nst += 1; rsum += r
                h.update(pickle.dumps((float(r), te, tr, clean(info), o.tobytes())))
    res[fast] = h.hexdigest(); print('fast_env', fast, 'steps', nst, 'reward sum', rsum, 'trace md5', res[fast], flush=True)
assert res[False] == res[True], 'MISMATCH'
print('IDENTICAL')
