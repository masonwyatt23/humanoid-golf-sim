"""Stage C (own policy, stock torque, real 1.15 m club, public-only data, arm_dist 0.6). Fixes vs B4 (taps / contact-gated exploit / flail), per Evaluator findings:
 1. IMPACT-SPEED GATE on every contact-linked reward: gate = clip((mph - lo)/(hi - lo), 0, 1), hi rises 30 -> 60 -> 85 mph (p 0 -> .3 -> .7), lo = hi/2. A 10-30 mph tap earns ~nothing.
    Contact reward only with forward-valid strike (ball_speed/(1.2*club) -> 0 for backward hits) and a LAUNCH WINDOW 7-16 deg (linear decay to 0 over 8 deg) on the carry term.
 2. FLAIL CAP: factor = 1 up to 1.3x the kseq-v2 100 mph segment targets (pelvis 442, thorax 665, arm 886, club 2054 deg/s), linearly to 0 at 2.0x; multiplies contact + prior reward;
    a miss with a flail gets an extra penalty.
 3. Lead-foot vertical force penalty above 2 BW (per control step, capped); fall/unstable -10 and alive bonus kept from B4. foot_forces() is the contact-frame NORMAL component, so it is >= 0 by
    construction (a foot cannot 'pull'; min 0 = airborne/unloaded).
 4. X-factor window 40-65 deg at top (requires thorax speed to rise afterward) + pelvis->thorax->arm->club peak order + soft lag, all gated by the speed gate; segments logged at the env default (every 2 substeps = 4 ms at dt 0.002).
 5. Speed + contact curricula; deterministic eval every 100k (12 eps, tether 0, IMPACT-time club speed = head-site velocity at the contact substep) -> eval.jsonl.
 Resumable (--resume). Warm start (--init, own B4 policy) with optional tether assist, or scratch with tether."""
import argparse, json, os, math, numpy as np, torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from train.v5_train_b import BEnv, CurrB, newest
from env.v5_reward import episode_terms, TARGET_100

def hi_at(p): return float(np.interp(p, [0.0, 0.3, 0.7, 1.0], [30.0, 60.0, 85.0, 85.0]))
def gate(mph, p):
    hi = hi_at(p); lo = 0.5 * hi
    return float(np.clip((mph - lo) / max(hi - lo, 1e-6), 0.0, 1.0))
def launch_win(deg): return 1.0 if 7.0 <= deg <= 16.0 else float(max(0.0, 1.0 - min(abs(deg - 7.0), abs(deg - 16.0)) / 8.0))
def xf_win(x, lo=40.0, hi=65.0):
    if lo <= x <= hi: return 1.0
    return float(max(0.0, 1.0 - (lo - x if x < lo else x - hi) / 25.0))
def flail_factor(peaks):
    ex = max(peaks[k] / TARGET_100[k] for k in TARGET_100)
    return float(np.clip((2.0 - ex) / 0.7, 0.0, 1.0)), ex

class CEnv(BEnv):
    def __init__(self, dt=0.002, seed=0):
        super().__init__(dt=dt, seed=seed)
        e = self.env; e.log_segments = True
        self.bw = float(np.sum(e.m.body_mass)) * 9.81; self.z0 = None; self.gpeak = 0.0; self.lgpeak = 0.0
    def reset(self, **kw):
        o = super().reset(**kw); self.z0 = float(self.env.d.qpos[2]); self.gpeak = 0.0; self.lgpeak = 0.0; return o
    def step(self, a):
        e = self.env; was = e.contact; p = self.progress
        o, _, term, trunc, info = e.step(a)
        hs = e.head_site; v = e._vel_site(hs)[3:]
        unstable = (not np.all(np.isfinite(v))) or float(np.linalg.norm(v)) > 62.0 or float(np.max(np.abs(e.d.qvel))) > 60.0
        if unstable: v = np.zeros(3); term = True
        vf = max(0.0, float(v[0])); r = 0.0
        if e.armed and not e.contact and np.linalg.norm(e.d.site_xpos[hs] - e.tee) < 1.0: r += 0.005 * vf    # approach shaping only after a real backswing
        if e.armed and not self.was_armed and not unstable: r += 1.0; self.was_armed = True
        fl, fr = e.foot_forces(); lead = (fl if e.lead == "left" else fr) / self.bw; self.lgpeak = max(self.lgpeak, lead); self.gpeak = max(self.gpeak, (fl + fr) / self.bw)
        r -= 0.03 * min(max(lead - 2.0, 0.0), 4.0)
        if e.d.qpos[2] > 0.8 * self.z0 and float(e.d.xmat[e.pel].reshape(3, 3)[2, 2]) > 0.85: r += 0.01
        L = e.log; peaks = None; ff, ex = 1.0, 0.0; g = 0.0; pr_raw = {}; seqlag = 0.0
        if len(L["t"]) > 3:
            pk = {k: float(np.max(L[k])) for k in TARGET_100}; ff, ex = flail_factor(pk); peaks = pk
        if e.contact and not was and not unstable:
            q = max(0.0, 1 - np.hypot(info["dy"], info["dz"]) / self.hit_tol)
            mph = info["club_speed_mph"]; valid = float(np.clip(info["ball_speed_mph"] / max(1.2 * mph, 1e-6), 0.0, 1.0))
            g = gate(mph, p) * valid * ff
            lw = launch_win(info["launch_deg"])
            base = (0.3 - 0.25 * min(p / 0.3, 1.0)) * valid
            r += base + g * ((3.0 + 5.0 * min(mph / 100.0, 1.3)) * (0.3 + 0.7 * q) + 8.0 * min(info["carry_m_noroll"] / 100.0, 1.0) * lw * (0.3 + 0.7 * q)
                             - 3.0 * min(abs(info["lateral_carry_m"]) / 20.0, 1.0))
        if info["fell"] or unstable: r -= 10.0
        if unstable and e.contact and not was: r = -5.0
        if trunc and not e.contact: r -= 2.0 + (min(max(ex - 1.3, 0.0), 2.0) if ex else 0.0)
        if term or trunc:
            pr = 0.0
            if len(L["t"]) > 3 and e.contact and not unstable:
                try:
                    lg = dict(L); lg["t_impact"] = e.t_contact
                    et = episode_terms(lg, progress=p, stage="C"); rw = et["raw_prior_terms"]
                    xf_max = float(np.max(np.abs(L["xfactor_deg"])))
                    pr_raw = dict(seq=rw["sequence"] / 1.5, lag=rw["lag"], xf=xf_win(xf_max) if rw["xfactor"] > 0 else 0.0, xf_deg=xf_max)
                    pr = (1.5 * pr_raw["xf"] + 1.0 * pr_raw["seq"] + 1.0 * pr_raw["lag"]) * float(np.clip(gate(info["club_speed_mph"], p), 0, 1)) * ff
                    pr = min(pr, 3.0)
                except Exception: pr = 0.0
            r += pr
            info["ep"] = dict(contact=bool(e.contact) and not unstable, fell=bool(info["fell"]), unstable=bool(unstable), club_mph=info.get("club_speed_mph", 0.0), carry=info.get("carry_m_noroll", 0.0),
                              lat=info.get("lateral_carry_m", 0.0), launch=info.get("launch_deg", 0.0), peak_head_mph=self.peak / 0.44704, club_len=e.club_len, tether=e.tether_strength, prior=pr,
                              grf_peak_bw=self.gpeak, lead_grf_peak_bw=self.lgpeak, flail_ratio=ex, peaks=peaks, **pr_raw)
        return o, r, term, trunc, info

class CurrC(CurrB):
    def _apply(self):
        p = self.num_timesteps / self.total_all
        tth = round(float(np.clip(self.t0_ * (1 - p / self.t_end), 0, 1)), 2)
        cur = (1.15, tth, round(0.03 - 0.015 * min(p, 1.0), 3), round(hi_at(p)))
        if cur != self.cur:
            self.cur = cur
            for i in range(self.training_env.num_envs):
                for k, val in (("target_len", cur[0]), ("target_tether", cur[1]), ("hit_tol", cur[2]), ("progress", min(p, 1.0))):
                    self.training_env.env_method("__setattr__", k, val, indices=[i])
    def _on_step(self):
        if self.n_calls % 256 == 0:
            p = min(self.num_timesteps / self.total_all / self.std_end, 1.0)
            self.model.policy.log_std.data.fill_(self.ls0 + (self.ls1 - self.ls0) * p); self.model.ent_coef = self.ent0 * (1 - p)
        before = self.last_ck
        ok = super()._on_step()
        if self.last_ck != before: self.det_eval()
        return ok
    def det_eval(self, n=12):
        env = CEnv(seed=999); env.hit_tol = self.cur[2]; env.target_len = 1.15; env.target_tether = 0.0; env.env.friction_rand = False
        vn = self.training_env; res = []
        for _ in range(n):
            o, _i = env.reset(seed=4000 + len(res)); done = False; info = {}
            while not done:
                a, _s = self.model.predict(vn.normalize_obs(o[None]), deterministic=True)
                o, r, te, tr, info = env.step(a[0]); done = te or tr
            res.append(info["ep"])
        c = [x for x in res if x["contact"]]; med = lambda k: float(np.median([x[k] for x in c])) if c else 0.0
        row = dict(step=self.num_timesteps, hi_gate=self.cur[3], det_contact=len(c) / n, det_fell=float(np.mean([x["fell"] for x in res])), det_impact_mph_med=med("club_mph"),
                   det_impact_mph_max=float(max([x["club_mph"] for x in c])) if c else 0.0, det_carry_med=med("carry"), det_lat_abs=float(np.mean([abs(x["lat"]) for x in c])) if c else 0.0,
                   det_launch_med=med("launch"), det_lead_grf_bw=float(np.mean([x["lead_grf_peak_bw"] for x in res])), det_flail_ratio=float(np.mean([x["flail_ratio"] for x in res])),
                   det_xf_deg=med("xf_deg") if c and "xf_deg" in c[0] else None)
        open(os.path.join(self.out, "eval.jsonl"), "a").write(json.dumps(row) + "\n")

def make(rank, seed, dt):
    def f(): return CEnv(dt=dt, seed=seed * 100 + rank + 21)
    return f

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=3_000_000)
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageC")
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
    cb = CurrC(a.steps, out, 100_000, a.tag); cb.base = 0; cb.total_all = a.steps; cb.scratch_tether = True; cb.last_ck = step0
    cb.t0_, cb.t_end, cb.ls0, cb.ls1, cb.std_end, cb.ent0 = a.tether0, a.tether_end, a.log_std, a.log_std_end, a.std_end, a.ent
    model.learn(a.steps - (model.num_timesteps if ck else 0), callback=cb, reset_num_timesteps=not ck)
    model.save(os.path.join(out, "final")); venv.save(os.path.join(out, "final_vecnorm.pkl"))
