"""Stage G (warm start from Stage F ckpts). Stage F reached det contact 1.0 at 51-69 mph (tether 0, arm 0.6) but every FAST strike was backward/closed
(face normal up/back, v.n < 0 -> carry 0), and every FORWARD strike was a 5-12 mph tap (carry ~0.5-1.6 m). Two changes:
 1. ENV strike-geometry gate (V5GolfEnv.strike_gate_nx = 0.25): a head-ball contact only counts if face normal n_x >= 0.25, head v_x > 0 and v.n > 0.
    Otherwise it is a FOUL: ball disabled, episode ends, reward -3 (worse than a miss -2). Backward chops can no longer be scored as contact.
 2. Speed for FORWARD strikes now has a gradient from 0 mph: +4*clip(mph/hi,0,1)*fwd*valid on top of F's gentle gate (which started at hi-40 = 30-45 mph,
    so taps got nothing), plus dense SWEEP shaping inside 0.6 m of the tee after arming: 0.006*max(v_x,0)*horizontality - 0.004*max(-v_z - 0.5*max(v_x,0), 0)
    (horizontality = 1 - |v_z|/|v|), i.e. reward a shallow head path moving toward the target, penalise a steep downward chop.
 Everything else (rewards, curriculum, det eval at arm 0.6 and 0 with the gate ON, STOP_REACHED at contact>=0.9 & carry>30 m) is Stage F.
 Also writes EVAL_READY.json when det (arm 0.6) contact >= 0.9 and median carry > 10 m (hand-off threshold to the style evaluator)."""
import argparse, json, os, numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
import train.v5_train_f as F
from train.v5_train_b import newest

GATE_NX = 0.25

class GEnv(F.EEnv):
    def __init__(self, dt=0.002, seed=0):
        super().__init__(dt=dt, seed=seed); self.env.strike_gate_nx = GATE_NX
    def step(self, a):
        e = self.env; was = e.contact; p = self.progress
        o, r, term, trunc, info = super().step(a)
        if info.get("foul"):
            r -= 3.0
            if term or trunc: info.setdefault("ep", {})["foul"] = True
        hs = e.head_site; v = e._vel_site(hs)[3:]
        if np.all(np.isfinite(v)) and float(np.linalg.norm(v)) < 62.0 and e.armed and not e.contact and not e.foul:
            if float(np.linalg.norm(e.tee - e.d.site_xpos[hs])) < 0.6:
                sp = float(np.linalg.norm(v)); hz = 1.0 - min(abs(float(v[2])) / max(sp, 1e-6), 1.0)
                r += 0.006 * max(float(v[0]), 0.0) * hz - 0.004 * max(-float(v[2]) - 0.5 * max(float(v[0]), 0.0), 0.0)
        if e.contact and not was and "club_speed_mph" in info:
            hi = float(np.interp(p, [0.0, 0.3, 0.7, 1.0], [50.0, 70.0, 85.0, 85.0])); mph = info["club_speed_mph"]
            valid = float(np.clip(info["ball_speed_mph"] / max(1.2 * mph, 1e-6), 0.0, 1.0))
            r += 4.0 * float(np.clip(mph / hi, 0.0, 1.0)) * getattr(self, "fwd", 0.0) * valid
        if (term or trunc) and "ep" in info: info["ep"].setdefault("foul", bool(e.foul))
        return o, r, term, trunc, info


class CurrG(F.CurrE):
    env_cls = GEnv   # det eval runs with the gate ON (fouls count as no contact)
    def det_eval(self, n=12):
        super().det_eval(n)
        try:
            row = json.loads(open(os.path.join(self.out, "eval.jsonl")).read().strip().splitlines()[-1]); a6 = row["arm0.6"]
            if a6["contact"] >= 0.9 and a6["carry_med"] > 10.0 and not os.path.exists(os.path.join(self.out, "EVAL_READY.json")):
                ck = os.path.join(self.out, f"evalready_{self.num_timesteps}"); self.model.save(ck); self.training_env.save(ck + "_vecnorm.pkl")
                row["ckpt"] = ck; open(os.path.join(self.out, "EVAL_READY.json"), "w").write(json.dumps(row))
        except Exception: pass

def make(rank, seed, dt):
    def f(): return GEnv(dt=dt, seed=seed * 100 + rank + 61)
    return f

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=3_000_000)
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageG")
    ap.add_argument("--init_ck", default=None, help="checkpoint base path without .zip"); ap.add_argument("--ent", type=float, default=0.004)
    ap.add_argument("--log_std", type=float, default=-1.5); ap.add_argument("--log_std_end", type=float, default=-2.3); ap.add_argument("--std_end", type=float, default=0.7)
    ap.add_argument("--tether0", type=float, default=0.0); ap.add_argument("--tether_end", type=float, default=0.3); ap.add_argument("--resume", action="store_true"); ap.add_argument("--ck_every", type=int, default=100_000)
    a = ap.parse_args()
    out = f"results/v5_runs/{a.tag}_s{a.seed}"; os.makedirs(out, exist_ok=True)
    venv = SubprocVecEnv([make(i, a.seed, a.dt) for i in range(a.workers)])
    step0, ck = newest(out) if a.resume else (0, None)
    if ck:
        venv = VecNormalize.load(ck.replace(".zip", "_vecnorm.pkl"), venv); venv.training = True; model = PPO.load(ck, env=venv, device="cpu")
    else:
        venv = VecNormalize(venv, norm_obs=True, norm_reward=True, clip_obs=10.0)
        model = PPO("MlpPolicy", venv, n_steps=1024, batch_size=512, n_epochs=8, learning_rate=3e-4, gamma=0.99, gae_lambda=0.95, ent_coef=a.ent, seed=a.seed,
                    policy_kwargs=dict(net_arch=[256, 256], log_std_init=a.log_std), device="cpu", verbose=0)
        src = PPO.load(a.init_ck + ".zip", device="cpu"); model.policy.load_state_dict(src.policy.state_dict()); model.policy.log_std.data.fill_(a.log_std)
        old = VecNormalize.load(a.init_ck + "_vecnorm.pkl", venv); venv.obs_rms = old.obs_rms
    json.dump(vars(a), open(os.path.join(out, "args.json"), "w"))
    cb = CurrG(a.steps, out, a.ck_every, a.tag); cb.base = 0; cb.total_all = a.steps; cb.scratch_tether = True; cb.last_ck = step0
    cb.t0_, cb.t_end, cb.ls0, cb.ls1, cb.std_end, cb.ent0 = a.tether0, a.tether_end, a.log_std, a.log_std_end, a.std_end, a.ent
    model.learn(a.steps - (model.num_timesteps if ck else 0), callback=cb, reset_num_timesteps=not ck)
    model.save(os.path.join(out, "final")); venv.save(os.path.join(out, "final_vecnorm.pkl"))
