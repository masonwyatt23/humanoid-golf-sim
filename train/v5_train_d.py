"""Stage D (own policy, stock torque, 1.15 m club, public-only, arm_dist 0.6). Warm start from B4 s1 ckpt_3000000 (tether-free, contact 1.0, ~37 mph, but BACKWARD strike, carry 0).
Changes vs Stage C (whose multiplicative speed gate removed the dense signal and let instability dominate):
 1. Contact reward is ADDITIVE: (1 + 4*fwd)*(0.3+0.7q) where fwd = clip(head_v_x/|head_v|,0,1) at the contact substep (target direction = +x), so a backward strike earns ~1, a forward one ~5.
 2. Speed bonus (additive, needs fwd): 4*clip((mph-lo)/(hi-lo),0,1)*fwd*valid*flail_ff, hi rises 30->60->85 mph (p 0->.3->.7), lo=hi-25. Carry bonus additive: 8*min(carry/100,1)*launch_window + 2*min(carry/30,1), lateral penalty.
 3. Dense forward-strike shaping after the arm gate (head within 1 m of tee, before contact): 0.006*closing speed toward ball + 0.004*forward head speed.
 4. Action-rate penalty 0.02*mean((a-a_prev)^2); lead-foot >2 BW penalty; fall/unstable -10; alive/upright bonus.
 5. Capped X-factor (40-65) + order + lag prior (additive, min(.,3)), times flail factor (1 up to 1.3x kseq-v2 100 mph segment peaks, 0 at 2.0x).
 6. Deterministic eval every 100k with tether 0 at arm_dist 0.6 AND 0 -> eval.jsonl (impact mph, carry no-roll, launch, lateral, forward-strike fraction).
 Stop early when arm 0.6 det contact>=0.9 and median carry>30 m. Resumable (--resume)."""
import argparse, json, os, numpy as np, torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from train.v5_train_b import BEnv, newest
from train.v5_train_c import CurrC, hi_at, launch_win, xf_win, flail_factor
from env.v5_reward import episode_terms

class DEnv(BEnv):
    def __init__(self, dt=0.002, seed=0):
        super().__init__(dt=dt, seed=seed)
        e = self.env; e.log_segments = True
        self.bw = float(np.sum(e.m.body_mass)) * 9.81; self.z0 = None; self.gpeak = 0.0; self.lgpeak = 0.0; self.prev_a = None
    def reset(self, **kw):
        o = super().reset(**kw); self.z0 = float(self.env.d.qpos[2]); self.gpeak = 0.0; self.lgpeak = 0.0; self.prev_a = None; return o
    def step(self, a):
        e = self.env; was = e.contact; p = self.progress; a = np.clip(np.asarray(a, float), -1, 1)
        da = 0.0 if self.prev_a is None else float(np.mean((a - self.prev_a) ** 2)); self.prev_a = a.copy()
        o, _, term, trunc, info = e.step(a)
        hs = e.head_site; v = e._vel_site(hs)[3:]
        unstable = (not np.all(np.isfinite(v))) or float(np.linalg.norm(v)) > 62.0 or float(np.max(np.abs(e.d.qvel))) > 60.0
        if unstable: v = np.zeros(3); term = True
        r = -0.02 * da
        rel = e.tee - e.d.site_xpos[hs]; dist = float(np.linalg.norm(rel))
        if e.armed and not e.contact and dist < 1.0:
            r += 0.006 * max(0.0, float(np.dot(v, rel / max(dist, 1e-6)))) + 0.004 * max(0.0, float(v[0]))
        if e.armed and not self.was_armed and not unstable: r += 1.0; self.was_armed = True
        fl, fr = e.foot_forces(); lead = (fl if e.lead == "left" else fr) / self.bw; self.lgpeak = max(self.lgpeak, lead); self.gpeak = max(self.gpeak, (fl + fr) / self.bw)
        r -= 0.03 * min(max(lead - 2.0, 0.0), 4.0)
        if e.d.qpos[2] > 0.8 * self.z0 and float(e.d.xmat[e.pel].reshape(3, 3)[2, 2]) > 0.85: r += 0.01
        L = e.log; peaks = None; ff, ex = 1.0, 0.0; pr_raw = {}; fwd = None
        if len(L["t"]) > 3:
            pk = {k: float(np.max(L[k])) for k in ("pelvis", "thorax", "lead_arm", "club")}; ff, ex = flail_factor(pk); peaks = pk
        hi = hi_at(p)
        if e.contact and not was and not unstable:
            q = max(0.0, 1 - np.hypot(info["dy"], info["dz"]) / self.hit_tol); pv = e.prev_v
            fwd = float(np.clip(pv[0] / max(float(np.linalg.norm(pv)), 1e-6), 0.0, 1.0)); self.fwd = fwd
            mph = info["club_speed_mph"]; valid = float(np.clip(info["ball_speed_mph"] / max(1.2 * mph, 1e-6), 0.0, 1.0))
            lw = launch_win(info["launch_deg"]); qq = 0.3 + 0.7 * q
            r += (1.0 + 4.0 * fwd) * qq
            r += 4.0 * float(np.clip((mph - (hi - 25.0)) / 25.0, 0.0, 1.0)) * fwd * valid * ff
            r += (8.0 * min(info["carry_m_noroll"] / 100.0, 1.0) * lw + 2.0 * min(info["carry_m_noroll"] / 30.0, 1.0)) * qq
            r -= 3.0 * min(abs(info["lateral_carry_m"]) / 20.0, 1.0)
        if info["fell"] or unstable: r -= 10.0
        if unstable and e.contact and not was: r = -5.0
        if trunc and not e.contact: r -= 2.0 + (min(max(ex - 1.3, 0.0), 2.0) if ex else 0.0)
        if term or trunc:
            pr = 0.0
            if len(L["t"]) > 3 and e.contact and not unstable:
                try:
                    lg = dict(L); lg["t_impact"] = e.t_contact
                    rw = episode_terms(lg, progress=p, stage="C")["raw_prior_terms"]; xf_max = float(np.max(np.abs(L["xfactor_deg"])))
                    pr_raw = dict(seq=rw["sequence"] / 1.5, lag=rw["lag"], xf=xf_win(xf_max) if rw["xfactor"] > 0 else 0.0, xf_deg=xf_max)
                    pr = min((1.5 * pr_raw["xf"] + 1.0 * pr_raw["seq"] + 1.0 * pr_raw["lag"]) * ff, 3.0)
                except Exception: pr = 0.0
            r += pr
            info["ep"] = dict(contact=bool(e.contact) and not unstable, fell=bool(info["fell"]), unstable=bool(unstable), club_mph=info.get("club_speed_mph", 0.0), carry=info.get("carry_m_noroll", 0.0),
                              lat=info.get("lateral_carry_m", 0.0), launch=info.get("launch_deg", 0.0), peak_head_mph=self.peak / 0.44704, club_len=e.club_len, tether=e.tether_strength, prior=pr,
                              fwd=getattr(self, "fwd", 0.0) if e.contact else 0.0, lead_grf_peak_bw=self.lgpeak, flail_ratio=ex, **pr_raw)
        return o, r, term, trunc, info

class CurrD(CurrC):
    stop = False
    def _on_step(self):
        ok = super()._on_step()
        return ok and not self.stop
    def det_eval(self, n=12):
        vn = self.training_env; row = dict(step=self.num_timesteps, hi_gate=self.cur[3])
        for ad in (0.6, 0.0):
            env = DEnv(seed=999); env.env.arm_dist = ad; env.hit_tol = self.cur[2]; env.target_len = 1.15; env.target_tether = 0.0; env.env.friction_rand = False
            res = []
            for _ in range(n):
                o, _i = env.reset(seed=4000 + len(res)); done = False; info = {}
                while not done:
                    act, _s = self.model.predict(vn.normalize_obs(o[None]), deterministic=True)
                    o, r, te, tr, info = env.step(act[0]); done = te or tr
                res.append(info["ep"])
            c = [x for x in res if x["contact"]]; med = lambda k: float(np.median([x[k] for x in c])) if c else 0.0
            row[f"arm{ad}"] = dict(contact=len(c) / n, fell=float(np.mean([x["fell"] for x in res])), impact_mph_med=med("club_mph"), impact_mph_max=float(max([x["club_mph"] for x in c])) if c else 0.0,
                                  carry_med=med("carry"), launch_med=med("launch"), lat_abs=float(np.mean([abs(x["lat"]) for x in c])) if c else 0.0,
                                  fwd_strike_frac=float(np.mean([x["fwd"] > 0.5 and x["carry"] > 0 for x in c])) if c else 0.0, lead_grf_bw=float(np.mean([x["lead_grf_peak_bw"] for x in res])))
        open(os.path.join(self.out, "eval.jsonl"), "a").write(json.dumps(row) + "\n")
        a6 = row["arm0.6"]
        if a6["contact"] >= 0.9 and a6["carry_med"] > 30.0 and self.num_timesteps >= 200_000:
            self.stop = True; open(os.path.join(self.out, "STOP_REACHED"), "w").write(json.dumps(row))

def make(rank, seed, dt):
    def f(): return DEnv(dt=dt, seed=seed * 100 + rank + 41)
    return f

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=3_000_000)
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageD")
    ap.add_argument("--init_ck", default=None, help="checkpoint base path without .zip"); ap.add_argument("--ent", type=float, default=0.003)
    ap.add_argument("--log_std", type=float, default=-1.8); ap.add_argument("--log_std_end", type=float, default=-2.3); ap.add_argument("--std_end", type=float, default=0.7)
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
    cb = CurrD(a.steps, out, a.ck_every, a.tag); cb.base = 0; cb.total_all = a.steps; cb.scratch_tether = True; cb.last_ck = step0
    cb.t0_, cb.t_end, cb.ls0, cb.ls1, cb.std_end, cb.ent0 = a.tether0, a.tether_end, a.log_std, a.log_std_end, a.std_end, a.ent
    model.learn(a.steps - (model.num_timesteps if ck else 0), callback=cb, reset_num_timesteps=not ck)
    model.save(os.path.join(out, "final")); venv.save(os.path.join(out, "final_vecnorm.pkl"))
