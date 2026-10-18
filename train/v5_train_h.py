"""Stage H (Orchestrator-directed; Mason's standing approval): STAGED SPEED CURRICULUM + soft kseq-v2 order prior + reduced-DoF-first option + GRF cap/rate penalty. Local only.
Why G stalled as 6-19 mph taps: contact base (1+6*fwd ~ 7) dwarfed the speed bonus (4*mph/85 ~ 0.7 for a 14 mph tap), so there was no gradient from tap to swing, and whiffs/flails were
not separated from slow legal strikes. H changes:
 1. Strike gate ON (env foul -> -3, as G). Contact reward is SMALL (1.0*qq); the speed reward is ADDITIVE and only on LEGAL forward strikes:
    6*clip(mph*fwd*valid / T, 0, 1.3) (+carry bonus 4*min(carry/30,1)*launch window). Never paid on a whiff/foul/miss (-2) or fall/unstable (-10).
 2. T (speed target, mph) starts at --T0 (20) and goes up +5 at a time ONLY after a deterministic eval (arm 0.6, gate on, 16 eps, tether 0) shows contact>=0.9, forward-strike frac>=0.9
    and median impact speed >= 0.8*T (automatic promotion, at most one per eval = 100k steps). T is persisted in curriculum.json (resume-safe). No promotion for 1M steps -> STALLED file + stop.
 3. Soft kseq-v2 order/lag/X-factor prior (episode_terms stage C raw terms, public numbers) paid at episode end UNGATED by contact (also on whiffs/fouls, using the last log sample as t_impact),
    weight 0.5, multiplied by the flail factor (1 up to 1.3x the 100 mph segment peaks, 0 at 2.0x) + -1.5*(excess over 1.3x, clipped 2) when no contact. Not a script copy.
 4. Lead-foot vertical GRF: >2 BW penalty (0.03/step), force-RATE penalty 0.02*max(|dF|/step - 1 BW, 0) (clipped), stomp termination >4 BW. Peak is measured after 0.1 s (the first-steps settle transient reads ~3.04 BW in every G eval).
 5. --planar: reduced-DoF-first. Roll joints (hip, ankle, waist, wrist), wrist yaw and shoulder yaw have their action scale multiplied by lock_scale: 0.25 until progress 0.2, ramp to 1.0 at 0.6 (progressive 3D unlock).
 6. Checkpoint writer: atomic (vecnorm first, .zip last via os.replace), try/except with ckpt.log, latest.zip/latest_vecnorm.pkl rolling copy, final save in finally; best_det written by contact*fwd_carry*min(1,mph/60).
Deterministic eval every 100k steps at arm_dist 0.6 with the strike gate on -> eval.jsonl."""
import argparse, json, os, shutil, sys, time, numpy as np
import torch; torch.set_num_threads(1)
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
import train.v5_train_f as F
from train.v5_train import Curr
from train.v5_train_b import newest
from train.v5_train_c import launch_win, xf_win, flail_factor
from env.v5_reward import episode_terms, TARGET_100

GATE_NX = 0.25
LOCK_NAMES = ("hip_roll", "ankle_roll", "waist_roll", "wrist_roll", "wrist_yaw", "shoulder_yaw")

def lock_at(p):  return float(np.interp(p, [0.0, 0.2, 0.6, 1.0], [0.25, 0.25, 1.0, 1.0]))

class HEnv(F.EEnv):
    planar = False
    def __init__(self, dt=0.002, seed=0, planar=False):
        super().__init__(dt=dt, seed=seed); self.env.strike_gate_nx = GATE_NX; self.speed_T = 20.0; self.lock_scale = 1.0; self.planar = planar; self.prev_lead = 0.0; self.nstep = 0
        self.lock_idx = [i for i, n in enumerate(self.env.names) if any(k in n for k in LOCK_NAMES)]
    def _apply_lock(self):
        s = self.lock_scale if self.planar else 1.0
        self.env.act_scale[:] = 1.0; self.env.act_scale[self.lock_idx] = s
    def reset(self, **kw):
        o = super().reset(**kw); self._apply_lock(); self.prev_lead = 0.0; self.nstep = 0; self.fwd = 0.0; return o
    def step(self, a):
        e = self.env; was = e.contact; a = np.clip(np.asarray(a, float), -1, 1); self.nstep += 1
        da = 0.0 if self.prev_a is None else float(np.mean((a - self.prev_a) ** 2)); self.prev_a = a.copy()
        o, _, term, trunc, info = e.step(a)
        hs = e.head_site; v = e._vel_site(hs)[3:]
        unstable = (not np.all(np.isfinite(v))) or float(np.linalg.norm(v)) > 62.0 or float(np.max(np.abs(e.d.qvel))) > 60.0
        if unstable: v = np.zeros(3); term = True
        r = -0.02 * da
        rel = e.tee - e.d.site_xpos[hs]; dist = float(np.linalg.norm(rel))
        if e.armed and not e.contact and not e.foul and dist < 1.0:
            nrm = e.d.geom_xmat[e.head_geom].reshape(3, 3)[:, 0]
            if dist < 0.8: r += 0.03 * (float(nrm[0]) - abs(float(nrm[1]))) + 0.01 * float(np.clip(np.dot(v, nrm), -20.0, 30.0)) * (1.0 if dist < 0.6 else 0.0)
            if dist < 0.6 and not unstable:   # G's dense sweep shaping: shallow forward path good, steep chop bad
                sp = float(np.linalg.norm(v)); hz = 1.0 - min(abs(float(v[2])) / max(sp, 1e-6), 1.0)
                r += 0.006 * max(float(v[0]), 0.0) * hz - 0.004 * max(-float(v[2]) - 0.5 * max(float(v[0]), 0.0), 0.0)
        if e.armed and not self.was_armed and not unstable: r += 1.0; self.was_armed = True
        fl, fr = e.foot_forces(); lead = (fl if e.lead == "left" else fr) / self.bw
        if self.nstep > 5:
            self.lgpeak = max(self.lgpeak, lead); self.gpeak = max(self.gpeak, (fl + fr) / self.bw)
            r -= 0.03 * min(max(lead - 2.0, 0.0), 4.0) + 0.02 * min(max(abs(lead - self.prev_lead) - 1.0, 0.0), 4.0)
            if lead > 4.0 and not e.contact and e.armed: r -= 3.0; term = True
        self.prev_lead = lead
        if e.d.qpos[2] > 0.8 * self.z0 and float(e.d.xmat[e.pel].reshape(3, 3)[2, 2]) > 0.85: r += 0.01
        L = e.log; ff, ex = 1.0, 0.0
        if len(L["t"]) > 3:
            pk = {k: float(np.max(L[k])) for k in TARGET_100}; ff, ex = flail_factor(pk)
        if e.contact and not was and not unstable:
            q = max(0.0, 1 - np.hypot(info["dy"], info["dz"]) / self.hit_tol); pv = e.prev_v; qq = 0.3 + 0.7 * q
            nrm = np.asarray(e.ball_hit_info["face_normal"]); fwd = float(np.clip(np.dot(pv, nrm) / max(float(np.linalg.norm(pv)), 1e-6), 0.0, 1.0)) * (1.0 if pv[0] > 0 else 0.0); self.fwd = fwd
            mph = info["club_speed_mph"]; valid = float(np.clip(info["ball_speed_mph"] / max(1.2 * mph, 1e-6), 0.0, 1.0)); lw = launch_win(info["launch_deg"])
            r += 1.0 * qq
            r += 6.0 * float(np.clip(mph * fwd * valid / max(self.speed_T, 1.0), 0.0, 1.3)) * qq
            r += (4.0 * min(info["carry_m_noroll"] / 30.0, 1.0) * lw + 4.0 * min(info["carry_m_noroll"] / 100.0, 1.0)) * qq
            r -= 3.0 * min(abs(info["lateral_carry_m"]) / 20.0, 1.0)
        if e.foul: r -= 3.0
        if info["fell"] or unstable: r -= 10.0
        if unstable and e.contact and not was: r = -5.0
        if trunc and not e.contact: r -= 2.0 + (min(max(ex - 1.3, 0.0), 2.0) if ex else 0.0) * 0.75
        if term or trunc:
            pr = 0.0; pr_raw = {}
            if len(L["t"]) > 8 and not unstable:
                try:
                    lg = dict(L); lg["t_impact"] = e.t_contact if e.contact else None
                    rw = episode_terms(lg, progress=self.progress, stage="C")["raw_prior_terms"]; xf_max = float(np.max(np.abs(L["xfactor_deg"])))
                    pr_raw = dict(seq=rw["sequence"] / 1.5, lag=rw["lag"], xf=xf_win(xf_max) if rw["xfactor"] > 0 else 0.0, xf_deg=xf_max)
                    pr = 0.5 * min((1.5 * pr_raw["xf"] + 1.0 * pr_raw["seq"] + 1.0 * pr_raw["lag"]), 3.0) * ff   # UNGATED by contact
                except Exception: pr = 0.0
            r += pr
            info["ep"] = dict(contact=bool(e.contact) and not unstable, foul=bool(e.foul), fell=bool(info["fell"]), unstable=bool(unstable), club_mph=info.get("club_speed_mph", 0.0), carry=info.get("carry_m_noroll", 0.0),
                              lat=info.get("lateral_carry_m", 0.0), launch=info.get("launch_deg", 0.0), peak_head_mph=self.peak / 0.44704, club_len=e.club_len, tether=e.tether_strength, prior=pr,
                              fwd=getattr(self, "fwd", 0.0) if e.contact else 0.0, lead_grf_peak_bw=self.lgpeak, flail_ratio=ex, **pr_raw)
        return o, r, term, trunc, info

def atomic_save(model, venv, out, name):
    tmp = os.path.join(out, "tmp_save"); model.save(tmp + ".zip"); venv.save(tmp + "_vecnorm.pkl")
    shutil.copyfile(tmp + "_vecnorm.pkl", os.path.join(out, name + "_vecnorm.pkl.tmp")); os.replace(os.path.join(out, name + "_vecnorm.pkl.tmp"), os.path.join(out, name + "_vecnorm.pkl"))
    os.replace(tmp + ".zip", os.path.join(out, name + ".zip")); os.remove(tmp + "_vecnorm.pkl")

class CurrH(Curr):
    def _apply(self):
        p = min(self.num_timesteps / self.total_all, 1.0)
        cur = (1.15, 0.0, round(0.03 - 0.01 * p, 3), self.T, round(lock_at(p), 2))
        if cur != self.cur:
            self.cur = cur
            for i in range(self.training_env.num_envs):
                for k, val in (("target_len", 1.15), ("target_tether", 0.0), ("hit_tol", cur[2]), ("progress", p), ("speed_T", float(self.T)), ("lock_scale", cur[4])):
                    self.training_env.env_method("__setattr__", k, val, indices=[i])
    def _on_step(self):
        if self.n_calls % 256 == 0:
            p = min(self.num_timesteps / self.total_all / self.std_end, 1.0)
            self.model.policy.log_std.data.fill_(self.ls0 + (self.ls1 - self.ls0) * p); self.model.ent_coef = self.ent0 * (1 - p)
        ok = super()._on_step()      # progress.jsonl + _apply; its own ckpt writer is disabled (ck huge)
        if self.num_timesteps - self.h_last >= self.h_every:
            self.h_last = self.num_timesteps
            try: atomic_save(self.model, self.training_env, self.out, f"ckpt_{self.num_timesteps}"); atomic_save(self.model, self.training_env, self.out, "latest"); open(os.path.join(self.out, "ckpt.log"), "a").write(f"{time.ctime()} saved {self.num_timesteps}\n")
            except Exception as ex_: open(os.path.join(self.out, "ckpt.log"), "a").write(f"{time.ctime()} SAVE FAILED {self.num_timesteps}: {ex_!r}\n")
            try: self.det_eval()
            except Exception as ex_: open(os.path.join(self.out, "ckpt.log"), "a").write(f"{time.ctime()} EVAL FAILED {self.num_timesteps}: {ex_!r}\n")
        return ok and not self.stop
    def det_eval(self, n=16):
        vn = self.training_env; env = HEnv(seed=999, planar=self.planar); env.lock_scale = lock_at(min(self.num_timesteps / self.total_all, 1.0)); env.env.arm_dist = 0.6
        env.hit_tol = self.cur[2]; env.target_len = 1.15; env.target_tether = 0.0; env.env.friction_rand = False; env.progress = self.num_timesteps / self.total_all
        res = []
        for _ in range(n):
            o, _i = env.reset(seed=4000 + len(res)); done = False; info = {}
            while not done:
                act, _s = self.model.predict(vn.normalize_obs(o[None]), deterministic=True); o, r, te, tr, info = env.step(act[0]); done = te or tr
            res.append(info["ep"])
        c = [x for x in res if x["contact"]]; med = lambda k: float(np.median([x[k] for x in c])) if c else 0.0
        fwdc = [x for x in c if x["fwd"] > 0.5 and x["carry"] > 0]
        row = dict(step=self.num_timesteps, T=self.T, lock=self.cur[4], contact=len(c) / n, foul=float(np.mean([x["foul"] for x in res])), fell=float(np.mean([x["fell"] or x["unstable"] for x in res])),
                   impact_mph_med=med("club_mph"), impact_mph_max=float(max([x["club_mph"] for x in c])) if c else 0.0, carry_med=med("carry"), carry_max=float(max([x["carry"] for x in c])) if c else 0.0,
                   launch_med=med("launch"), lat_abs=float(np.mean([abs(x["lat"]) for x in c])) if c else 0.0, fwd_strike_frac=len(fwdc) / n, lead_grf_bw=float(np.mean([x["lead_grf_peak_bw"] for x in res])),
                   flail=float(np.mean([x["flail_ratio"] for x in res])), xf_deg=med("xf_deg") if c and "xf_deg" in c[0] else None, seq=float(np.mean([x.get("seq", 0.0) for x in c])) if c else 0.0)
        sc = row["contact"] * (float(np.median([x["carry"] for x in fwdc])) if fwdc else 0.0) * min(1.0, row["impact_mph_med"] / 60.0); row["best_score"] = sc
        # automatic promotion
        if row["contact"] >= 0.9 and row["fwd_strike_frac"] >= 0.9 and row["impact_mph_med"] >= 0.8 * self.T:
            self.T += 5; self.last_promo = self.num_timesteps; row["promoted_to"] = self.T
        open(os.path.join(self.out, "eval.jsonl"), "a").write(json.dumps(row) + "\n")
        json.dump(dict(T=self.T, last_promo=self.last_promo), open(os.path.join(self.out, "curriculum.json"), "w"))
        if sc > getattr(self, "best_sc", 0.0):
            self.best_sc = sc; atomic_save(self.model, self.training_env, self.out, "best_det"); open(os.path.join(self.out, "best_det.json"), "w").write(json.dumps(row))
        if row["contact"] >= 0.9 and row["carry_med"] > 30.0 and self.num_timesteps >= 200_000:
            self.stop = True; open(os.path.join(self.out, "STOP_REACHED"), "w").write(json.dumps(row))
        if self.num_timesteps - self.last_promo >= 1_000_000:
            self.stop = True; open(os.path.join(self.out, "STALLED"), "w").write(json.dumps(row))

def make(rank, seed, dt, planar):
    def f(): return HEnv(dt=dt, seed=seed * 100 + rank + 81, planar=planar)
    return f

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=3_000_000)
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageH"); ap.add_argument("--planar", action="store_true")
    ap.add_argument("--init_ck", default=None); ap.add_argument("--ent", type=float, default=0.004); ap.add_argument("--T0", type=float, default=20.0)
    ap.add_argument("--log_std", type=float, default=-1.5); ap.add_argument("--log_std_end", type=float, default=-2.0); ap.add_argument("--std_end", type=float, default=0.7)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    out = f"results/v5_runs/{a.tag}_s{a.seed}"; os.makedirs(out, exist_ok=True)
    venv = SubprocVecEnv([make(i, a.seed, a.dt, a.planar) for i in range(a.workers)])
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
    cb = CurrH(a.steps, out, 10**12, a.tag); cb.base = 0; cb.total_all = a.steps; cb.stop = False; cb.planar = a.planar; cb.h_every = 100_000; cb.h_last = step0
    cb.T, cb.last_promo = a.T0, step0
    cj = os.path.join(out, "curriculum.json")
    if ck and os.path.exists(cj): d_ = json.load(open(cj)); cb.T, cb.last_promo = d_["T"], max(d_["last_promo"], step0 - 0)
    cb.ls0, cb.ls1, cb.std_end, cb.ent0 = a.log_std, a.log_std_end, a.std_end, a.ent
    try:
        model.learn(a.steps - (model.num_timesteps if ck else 0), callback=cb, reset_num_timesteps=not ck)
    finally:
        try: atomic_save(model, venv, out, "final")
        except Exception as ex_: print("final save failed", ex_, file=sys.stderr)
