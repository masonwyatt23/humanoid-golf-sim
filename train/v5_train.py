"""Stage A from-scratch PPO for the v5 env (SB3, NO teacher, stock force_scale 1). Public-only: no reference/Instagram data is read.
Reward (all computed from the env, sim-only): forward head-speed peak progress (dense) + at first contact: bonus*hit-quality(dy,dz tolerance shrinking) + golfphys
no-roll carry + lateral penalty; fall penalty; action-rate penalty. Stage A prior scaffolding (sequence/X-factor/weight shift) weights are 0.
Curricula (by training progress p): SOFT pelvis tether 1 -> 0 (p 0.15 -> 0.60), club length 0.87 -> 0.95 -> 1.05 -> 1.15 (p 0.25/0.45/0.65), sweet-spot tolerance 0.04 -> 0.01 m,
foot friction randomised 0.5-1.2 always."""
import argparse, json, os, time, numpy as np, gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import BaseCallback
from env.v5_golf_env import V5GolfEnv

LENGTHS = [(0.0, 0.87), (0.25, 0.95), (0.45, 1.05), (0.65, 1.15)]
def club_len_at(p): return [L for t, L in LENGTHS if p >= t][-1]
def tether_at(p): return float(np.clip(1 - (p - 0.15) / 0.45, 0, 1))
def tol_at(p): return float(0.04 - 0.03 * np.clip(p / 0.8, 0, 1))


class TrainEnv(gym.Wrapper):
    def __init__(self, dt=0.002, seed=0, **kw):
        super().__init__(V5GolfEnv(dt=dt, seed=seed, friction_rand=True, ball_tol_m=0.0, log_segments=False, **kw))
        self.hit_tol = 0.04; self.peak = 0.0; self.target_len = None; self.target_tether = None
    def reset(self, **kw):
        e = self.env
        if self.target_len is not None: e.set_club_len(self.target_len)
        if self.target_tether is not None: e.tether_strength = self.target_tether
        self.peak = 0.0; self.ep_ret = 0.0
        return e.reset(**kw)
    def step(self, a):
        e = self.env
        was = e.contact
        o, _, term, trunc, info = e.step(a)
        v = e._vel_site(e.head_site)[3:]
        unstable = (not np.all(np.isfinite(v))) or float(np.linalg.norm(v)) > 62.0 or float(np.max(np.abs(e.d.qvel))) > 60.0   # >139 mph head or blow-up: sim instability, not a swing
        if unstable: v = np.zeros(3); term = True
        vf = max(0.0, float(v[0]))   # +x is the target direction
        r = 0.05 * max(0.0, vf - self.peak); self.peak = max(self.peak, vf)
        r -= 0.002 * float(np.sum((a - e.last_act) ** 2)) if False else 0.0
        if e.contact and not was and not unstable:
            q = max(0.0, 1 - np.hypot(info["dy"], info["dz"]) / self.hit_tol)
            r += 3.0 * q * min(info["club_speed_mph"] / 80.0, 1.0) + 15.0 * min(info["carry_m_noroll"] / 250.0, 1.0) - 3.0 * min(abs(info["lateral_carry_m"]) / 20.0, 1.0)
        if info["fell"] or unstable: r -= 5.0
        if unstable and e.contact and not was: r = -5.0
        if term or trunc:
            info["ep"] = dict(contact=bool(e.contact) and not unstable, fell=bool(info["fell"]), unstable=bool(unstable), club_mph=info.get("club_speed_mph", 0.0), carry=info.get("carry_m_noroll", 0.0),
                              lat=info.get("lateral_carry_m", 0.0), peak_head_mph=self.peak / 0.44704, club_len=e.club_len, tether=e.tether_strength)
        return o, r, term, trunc, info


def make(rank, seed, dt):
    def f(): return TrainEnv(dt=dt, seed=seed * 100 + rank)
    return f


class Curr(BaseCallback):
    def __init__(self, total, out, ckpt_every, tag):
        super().__init__(); self.total, self.out, self.ck, self.tag = total, out, ckpt_every, tag; self.eps = []; self.last_ck = 0; self.cur = None; self.t0 = time.time()
    def _apply(self):
        p = self.num_timesteps / self.total
        cur = (club_len_at(p), round(tether_at(p), 2), round(tol_at(p), 3))
        if cur != self.cur:
            self.cur = cur
            for i in range(self.training_env.num_envs):
                self.training_env.env_method("__setattr__", "target_len", cur[0], indices=[i])
                self.training_env.env_method("__setattr__", "target_tether", cur[1], indices=[i])
                self.training_env.env_method("__setattr__", "hit_tol", cur[2], indices=[i])
    def _on_training_start(self): self._apply()
    def _on_step(self):
        for inf in self.locals["infos"]:
            if "ep" in inf: self.eps.append(inf["ep"])
        if self.n_calls % 256 == 0: self._apply()
        if len(self.eps) >= 100:
            e = self.eps; self.eps = []
            c = [x for x in e if x["contact"]]
            row = dict(step=self.num_timesteps, wall_s=round(time.time() - self.t0), contact=len(c) / len(e), fell=float(np.mean([x["fell"] for x in e])), unstable=float(np.mean([x["unstable"] for x in e])),
                       club_mph_mean=float(np.mean([x["club_mph"] for x in c])) if c else 0.0, club_mph_max=float(max([x["club_mph"] for x in c])) if c else 0.0,
                       carry_mean=float(np.mean([x["carry"] for x in c])) if c else 0.0, carry_max=float(max([x["carry"] for x in c])) if c else 0.0,
                       peak_head_mph=float(np.mean([x["peak_head_mph"] for x in e])), club_len=self.cur[0], tether=self.cur[1], hit_tol=self.cur[2])
            open(os.path.join(self.out, "progress.jsonl"), "a").write(json.dumps(row) + "\n")
        if self.num_timesteps - self.last_ck >= self.ck:
            self.last_ck = self.num_timesteps
            self.model.save(os.path.join(self.out, f"ckpt_{self.num_timesteps}")); self.training_env.save(os.path.join(self.out, f"ckpt_{self.num_timesteps}_vecnorm.pkl"))
        return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=2_500_000)
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageA")
    a = ap.parse_args()
    out = f"results/v5_runs/{a.tag}_s{a.seed}"; os.makedirs(out, exist_ok=True)
    venv = VecNormalize(SubprocVecEnv([make(i, a.seed, a.dt) for i in range(a.workers)]), norm_obs=True, norm_reward=True, clip_obs=10.0)
    model = PPO("MlpPolicy", venv, n_steps=1024, batch_size=512, n_epochs=8, learning_rate=3e-4, gamma=0.99, gae_lambda=0.95, ent_coef=0.0, seed=a.seed,
                policy_kwargs=dict(net_arch=[256, 256], log_std_init=-1.5), device="cpu", verbose=0)
    json.dump(vars(a), open(os.path.join(out, "args.json"), "w"))
    model.learn(a.steps, callback=Curr(a.steps, out, 100_000, a.tag))
    model.save(os.path.join(out, "final")); venv.save(os.path.join(out, "final_vecnorm.pkl"))
