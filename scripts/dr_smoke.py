import sys, json, hashlib, numpy as np; sys.path.insert(0, '.')
from train.v5_train_j import JEnv; from train.dr_goal import DREnv
A = json.load(open("results/v5_runs/_snap/V10l_s104_100000/args.json")); keys = {tuple(k.split("|")): v for k, v in json.load(open(A["keys"])).items()}
cfg = dict(env_v4=True, tee_mode="1.5in", fast_env=True, init_qn=0.03, init_qvn=0.06, fr_rand=True, ball_tol=0.012, fr_lo=0.65, fr_hi=1.05, rsi=(0.95, 0.025, 0.025))
def trace(cls, extra={}, n=3):
    e = cls(dt=0.002, seed=10491, keys=keys, res_scale=0.3, t_down=A["t_down"]); e.configure(**cfg); e.configure(**extra); h = hashlib.md5(); rng = np.random.default_rng(0); logs = []
    for k in range(n):
        o, _ = e.reset(seed=5000 + k); h.update(o.tobytes()); d = False
        while not d:
            o, r, te, tr, inf = e.step(rng.uniform(-1, 1, e.action_space.shape)); h.update(o.tobytes()); h.update(np.float64(r).tobytes()); d = te or tr
        logs.append({k_: inf["ep"].get(k_) for k_ in ("contact", "dr", "goal")})
    return h.hexdigest(), o.shape, logs
print("JEnv      ", trace(JEnv)[:2]); print("DREnv off ", trace(DREnv)[:2])
for st in (0, 2): print("DREnv dr st", st, trace(DREnv, dict(dr=True, dr_stage=st)))
e = DREnv(dt=0.002, seed=1, keys=keys, res_scale=0.3, t_down=A["t_down"]); e.configure(**cfg, goal_obs=True); e.set_goal(dict(club="driver", target_carry=150, target_dir=2, shape="draw", bend=4, handedness="LH")); o, _ = e.reset(seed=3); print("goal obs", o.shape, e.observation_space.shape, o[-8:])
try: DREnv(dt=0.002, seed=900001, keys=keys)
except SystemExit as x: print("guard ok:", x)
