"""Stage B from-scratch-own-policy PPO for the v5 env (stock force_scale 1, real 1.15 m club, NO script teacher; optional warm start from our own Stage A policy).
Public-only data. Why Stage A stayed a tap (see results/TRAINING_NOTES.md): contact reward 3*q*min(mph/80,1) + 15*carry/250 gave ~1 reward for a 19 mph tap and a tiny
gradient vs the dense PEAK-ANYWHERE head-speed progress term (0.05/m/s) that is satisfied by a fast wave far from the ball; tol 0.01 m made q ~0 for faster (sloppier) swings.
Stage B reward: speed AT contact (uncapped to 1.3x100 mph) * soft quality floor, golfphys no-roll carry (target 100 m), lateral penalty, approach-speed shaping only
within 1 m of the tee, small peak-progress, capped/annealed public-only sequence/X-factor/weight-shift prior (stage 'C' terms, SPEED_GAP numbers), miss penalty.
Resumable: --resume loads the newest ckpt_* of the run dir."""
import argparse, glob, json, os, re, time, numpy as np
import torch; torch.set_num_threads(1)
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from train.v5_train import TrainEnv, Curr
from env.v5_reward import episode_terms, prior_cap

ARM_DIST = 0.6      # Stage B2: ball contact disabled until head >= 0.6 m from tee (Stage A tap = head started 0.06 m from ball and hit it in 80 ms, no backswing)
PRIOR_SCALE = 6.0   # prior_total is capped to <=0.20 (annealed to 0.05) -> at most 1.2 reward, small vs contact terms ~10-20


class BEnv(TrainEnv):
    def __init__(self, dt=0.002, seed=0):
        super().__init__(dt=dt, seed=seed, arm_dist=ARM_DIST)
        self.env.log_segments = True; self.was_armed = False; self.progress = 0.0; self.ball_tol_unused = 0.0
    def reset(self, **kw):
        o = super().reset(**kw); self.was_armed = False; return o
    def step(self, a):
        e = self.env; was = e.contact
        o, _, term, trunc, info = e.step(a)
        hs = e.head_site
        v = e._vel_site(hs)[3:]
        unstable = (not np.all(np.isfinite(v))) or float(np.linalg.norm(v)) > 62.0 or float(np.max(np.abs(e.d.qvel))) > 60.0
        if unstable: v = np.zeros(3); term = True
        vf = max(0.0, float(v[0])); r = 0.01 * max(0.0, vf - self.peak); self.peak = max(self.peak, vf)
        if not e.contact and np.linalg.norm(e.d.site_xpos[hs] - e.tee) < 1.0: r += 0.01 * vf
        if e.armed and not self.was_armed and not unstable: r += 1.0; self.was_armed = True    # one-off bonus for completing a backswing
        if e.contact and not was and not unstable:
            q = max(0.0, 1 - np.hypot(info["dy"], info["dz"]) / self.hit_tol)
            mph = info["club_speed_mph"]
            r += 8.0 * min(mph / 100.0, 1.3) * (0.3 + 0.7 * q) + 10.0 * min(info["carry_m_noroll"] / 100.0, 1.0) * (0.3 + 0.7 * q) - 3.0 * min(abs(info["lateral_carry_m"]) / 20.0, 1.0)
        if info["fell"] or unstable: r -= 5.0
        if unstable and e.contact and not was: r = -5.0
        if trunc and not e.contact: r -= 2.0
        if term or trunc:
            pr = 0.0; L = e.log
            if len(L["t"]) > 3 and e.contact and not unstable:
                try:
                    lg = dict(L); lg["t_impact"] = e.t_contact
                    pr = episode_terms(lg, progress=self.progress, stage="C")["prior_total"]
                except Exception: pr = 0.0
            r += PRIOR_SCALE * pr
            info["ep"] = dict(contact=bool(e.contact) and not unstable, fell=bool(info["fell"]), unstable=bool(unstable), club_mph=info.get("club_speed_mph", 0.0),
                              carry=info.get("carry_m_noroll", 0.0), lat=info.get("lateral_carry_m", 0.0), peak_head_mph=self.peak / 0.44704, club_len=e.club_len,
                              tether=e.tether_strength, prior=pr)
        return o, r, term, trunc, info


class CurrB(Curr):
    """Tether stays 0, club 1.15 (Stage A final state); tolerance 0.03 -> 0.015; prior cap progress."""
    def _apply(self):
        p = (self.base + self.num_timesteps) / self.total_all
        tth = round(float(np.clip(1 - p / 0.3, 0, 1)), 2) if self.scratch_tether else 0.0
        cur = (1.15, tth, round(0.03 - 0.015 * min(p, 1.0), 3))
        if cur != self.cur:
            self.cur = cur
            for i in range(self.training_env.num_envs):
                for k, val in (("target_len", cur[0]), ("target_tether", cur[1]), ("hit_tol", cur[2]), ("progress", min(p, 1.0))):
                    self.training_env.env_method("__setattr__", k, val, indices=[i])


def make(rank, seed, dt):
    def f(): return BEnv(dt=dt, seed=seed * 100 + rank + 7)
    return f


def newest(out):
    cks = [(int(re.search(r"ckpt_(\d+)\.zip", p).group(1)), p) for p in glob.glob(os.path.join(out, "ckpt_*.zip"))]
    return max(cks) if cks else (0, None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=3_000_000)
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageB")
    ap.add_argument("--init", default=None, help="Stage A run dir to warm-start from (own policy)"); ap.add_argument("--ent", type=float, default=0.003)
    ap.add_argument("--log_std", type=float, default=-1.0); ap.add_argument("--resume", action="store_true"); ap.add_argument("--scratch_tether", action="store_true")
    a = ap.parse_args()
    out = f"results/v5_runs/{a.tag}_s{a.seed}"; os.makedirs(out, exist_ok=True)
    venv = SubprocVecEnv([make(i, a.seed, a.dt) for i in range(a.workers)])
    step0, ck = newest(out) if a.resume else (0, None)
    if ck:
        venv = VecNormalize.load(ck.replace(".zip", "_vecnorm.pkl"), venv); venv.training = True
        model = PPO.load(ck, env=venv, device="cpu"); model.ent_coef = a.ent
    else:
        venv = VecNormalize(venv, norm_obs=True, norm_reward=True, clip_obs=10.0)
        model = PPO("MlpPolicy", venv, n_steps=1024, batch_size=512, n_epochs=8, learning_rate=3e-4, gamma=0.99, gae_lambda=0.95, ent_coef=a.ent, seed=a.seed,
                    policy_kwargs=dict(net_arch=[256, 256], log_std_init=a.log_std), device="cpu", verbose=0)
        if a.init:
            src = PPO.load(os.path.join(a.init, "final.zip"), device="cpu")
            model.policy.load_state_dict(src.policy.state_dict()); model.policy.log_std.data.fill_(a.log_std)
            old = VecNormalize.load(os.path.join(a.init, "final_vecnorm.pkl"), venv); venv.obs_rms = old.obs_rms   # obs stats only; reward norm fresh
    json.dump(vars(a), open(os.path.join(out, "args.json"), "w"))
    cb = CurrB(a.steps, out, 100_000, a.tag); cb.base = 0; cb.total_all = a.steps; cb.scratch_tether = a.scratch_tether; cb.last_ck = step0
    if ck: cb.base = 0
    model.learn(a.steps - (model.num_timesteps if ck else 0), callback=cb, reset_num_timesteps=not ck)
    model.save(os.path.join(out, "final")); venv.save(os.path.join(out, "final_vecnorm.pkl"))
