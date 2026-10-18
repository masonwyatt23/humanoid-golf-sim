"""Stage B4 (own policy, stock torque, real 1.15 m club, public-only data). Fixes vs B3 (contact 0.18-0.24, falls 50%, deterministic speed 0.5-18 mph vs stochastic ~30):
 1. slower SOFT pelvis tether anneal (start --tether0, linear to 0 by --tether_end fraction of training) instead of B3's s0 tether 0 from step 0;
 2. alive/upright stability reward (+0.01/ctrl step while pelvis height and uprightness ok), fall/unstable penalty -10;
 3. lead/any-foot GRF spike penalty: per ctrl step, -0.02*min(max(F/BW - 2.5, 0), 4) (evaluator saw 3-7 BW spikes; sole solref 0.004 is stiff -> model left UNCHANGED so the
    evaluator's env still matches; penalty only);
 4. log_std anneal (--log_std -> --log_std_end linear over --std_end of training) and entropy coef anneal to 0, so the policy MEAN carries the speed;
 5. deterministic eval every 100k steps (12 eps, tether 0, current club/tol) -> eval.jsonl;
 Speed-at-impact (forward-valid gated), no-roll carry, kseq-v2 sequence/X-factor prior (B3 terms) are kept unchanged. Resumable (--resume)."""
import argparse, json, os, time, numpy as np, torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from train.v5_train_b import BEnv, CurrB, newest

class B4Env(BEnv):
    def __init__(self, dt=0.002, seed=0):
        super().__init__(dt=dt, seed=seed)
        e = self.env; self.bw = float(np.sum(e.m.body_mass)) * 9.81; self.z0 = None; self.gpeak = 0.0
    def reset(self, **kw):
        o = super().reset(**kw); self.z0 = float(self.env.d.qpos[2]); self.gpeak = 0.0; return o
    def step(self, a):
        o, r, term, trunc, info = super().step(a)
        e = self.env
        fl, fr = e.foot_forces(); g = (fl + fr) / self.bw; self.gpeak = max(self.gpeak, g)
        r -= 0.02 * min(max(g - 2.5, 0.0), 4.0)
        up = float(e.d.xmat[e.pel].reshape(3, 3)[2, 2])
        if e.d.qpos[2] > 0.8 * self.z0 and up > 0.85: r += 0.01
        if info.get("fell") or (info.get("ep") and info["ep"]["unstable"]): r -= 5.0     # on top of B3's -5 -> -10 total
        if "ep" in info: info["ep"]["grf_peak_bw"] = self.gpeak
        return o, r, term, trunc, info

class CurrB4(CurrB):
    def _apply(self):
        p = self.num_timesteps / self.total_all
        tth = round(float(np.clip(self.t0_ * (1 - p / self.t_end), 0, 1)), 2)
        cur = (1.15, tth, round(0.03 - 0.015 * min(p, 1.0), 3))
        if cur != self.cur:
            self.cur = cur
            for i in range(self.training_env.num_envs):
                for k, val in (("target_len", cur[0]), ("target_tether", cur[1]), ("hit_tol", cur[2]), ("progress", min(p, 1.0))):
                    self.training_env.env_method("__setattr__", k, val, indices=[i])
    def _on_step(self):
        if self.n_calls % 256 == 0:
            p = min(self.num_timesteps / self.total_all / self.std_end, 1.0)
            ls = self.ls0 + (self.ls1 - self.ls0) * p
            self.model.policy.log_std.data.fill_(ls); self.model.ent_coef = self.ent0 * (1 - p)
        before = self.last_ck
        ok = super()._on_step()
        if self.last_ck != before: self.det_eval()
        return ok
    def det_eval(self, n=12):
        env = B4Env(seed=999); env.hit_tol = self.cur[2]; env.target_len = 1.15; env.target_tether = 0.0
        vn = self.training_env; res = []
        for _ in range(n):
            o, _i = env.reset(); done = False; info = {}
            while not done:
                a, _s = self.model.predict(vn.normalize_obs(o[None]), deterministic=True)
                o, r, te, tr, info = env.step(a[0]); done = te or tr
            res.append(info["ep"])
        c = [x for x in res if x["contact"]]
        row = dict(step=self.num_timesteps, det_contact=len(c) / n, det_fell=float(np.mean([x["fell"] for x in res])), det_club_mph=float(np.mean([x["club_mph"] for x in c])) if c else 0.0,
                   det_club_mph_max=float(max([x["club_mph"] for x in c])) if c else 0.0, det_carry=float(np.mean([x["carry"] for x in c])) if c else 0.0,
                   det_lat=float(np.mean([abs(x["lat"]) for x in c])) if c else 0.0, det_grf_peak_bw=float(np.mean([x["grf_peak_bw"] for x in res])))
        open(os.path.join(self.out, "eval.jsonl"), "a").write(json.dumps(row) + "\n")

def make(rank, seed, dt):
    def f(): return B4Env(dt=dt, seed=seed * 100 + rank + 11)
    return f

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=3_000_000)
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageB4")
    ap.add_argument("--init", default=None); ap.add_argument("--ent", type=float, default=0.005)
    ap.add_argument("--log_std", type=float, default=-1.0); ap.add_argument("--log_std_end", type=float, default=-2.3); ap.add_argument("--std_end", type=float, default=0.7)
    ap.add_argument("--tether0", type=float, default=1.0); ap.add_argument("--tether_end", type=float, default=0.6); ap.add_argument("--resume", action="store_true")
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
        if a.init:
            src = PPO.load(os.path.join(a.init, "final.zip"), device="cpu"); model.policy.load_state_dict(src.policy.state_dict()); model.policy.log_std.data.fill_(a.log_std)
            old = VecNormalize.load(os.path.join(a.init, "final_vecnorm.pkl"), venv); venv.obs_rms = old.obs_rms
    json.dump(vars(a), open(os.path.join(out, "args.json"), "w"))
    cb = CurrB4(a.steps, out, 100_000, a.tag); cb.base = 0; cb.total_all = a.steps; cb.scratch_tether = True; cb.last_ck = step0
    cb.t0_, cb.t_end, cb.ls0, cb.ls1, cb.std_end, cb.ent0 = a.tether0, a.tether_end, a.log_std, a.log_std_end, a.std_end, a.ent
    model.learn(a.steps - (model.num_timesteps if ck else 0), callback=cb, reset_num_timesteps=not ck)
    model.save(os.path.join(out, "final")); venv.save(os.path.join(out, "final_vecnorm.pkl"))
