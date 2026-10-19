"""Stage J: REFERENCE-GUIDED RESIDUAL RL (not pure from-scratch). Local only, public references only (no Instagram/Mason data).
Action = PD target q_ref(t) (env/v5_ref.py: joint keyframes from the public joint trajectories / G1 mapping, ~100 mph-class downswing 0.27 s, optionally open-loop-tuned keyframes
from scripts/v5_ref_fit.py) + res_scale*0.2 rad * a, a in [-1,1] learned by PPO. Obs = Stage I obs (joint offsets are relative to the CURRENT reference pose) + [u, downswing phase, pre-top flag, time-to-impact].
Reference-state init: after reset the open-loop reference is rolled out (zero residual) to a sampled start point: full swing (address), top of backswing, or mid-downswing (p 0.4/0.3/0.3), so downswing credit is short.
Reward = Stage I/H reward (strike gate nx 0.25, additive speed bonus only for legal forward strikes with automatic promotion curriculum, carry bonus, GRF penalty, caps, order prior, fall/unstable)
 + tracking 0.1*track_w*exp(-(rmse/0.25)^2) per step. track_w anneals 1 -> track_end ONLY after tracking works (det eval fell<=0.25 & rmse<0.3 & steps>=track_hold), over --track_len steps.
Det eval every 100k (16 eps, full swing, arm 0.6, gate on, tether 0). Stall = 1M steps since training START (counted by step, persisted in curriculum.json; not the resume point) without promotion/best-score gain."""
import argparse, json, os, sys, time, numpy as np
import torch; torch.set_num_threads(1)
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
import train.v5_train_i as I
from train.v5_train_i import HEnv, CurrH, atomic_save, lock_at
from train.v5_train_b import newest
from env.v5_ref import SwingRef

EXTRA = 4

class JEnv(HEnv):
    res_scale = 1.0; track_w = 1.0; bs_floor = 1.0; xf_cap_w = 0.08; xf_cap_lo = 60.0; ord_w = 1.5; track_floor = 0.3; grf_w = 0.15; ctr_w = 2.0; spin_w = 1.0; _cprev = False; ord2_w = 0.0; launch_w = 0.0; launch_hi = 14.0; dl_lo = 12.0; dl_hi = 18.0; aoa_lo = -6.0; spd_w = 0.0; fine_grf = False; smash_w = 0.0; spin_hi = 3000.0; spin_scale = 2000.0; desc_w = 0.0; dloft_w = 0.0; spin_lo_w = 0.0; xf_hard = 0.0; grf_lo = 2.0; rsi = (0.4, 0.3, 0.3); ref_keys = None; t_down = 0.27; k_ease = 1.6; grf_term = 6.0
    def __init__(self, dt=0.002, seed=0, keys=None, res_scale=1.0, t_down=0.27):
        super().__init__(dt=dt, seed=seed, planar=False); self.ref_keys = keys; self.res_scale = res_scale; self.t_down = t_down; self.ref = None
        self.target_len = 1.15; self.target_tether = 0.0; self.prior_w = 0.0; self.env.friction_rand = False; self.env.detail_info = True; self._slead = 0.0; self._sl_ep = 0.0; _orig = self.env._log_seg; _e = self.env
        def _seg():   # 5 ms-resolution lead-foot vertical force (what the harness measures); control-step samples miss impulses
            _orig(); fl, fr = _e.foot_forces(); v_ = (fl if _e.lead == "left" else fr) / self.bw; self._slead = max(self._slead, v_)
            self._sl_ep = max(self._sl_ep, v_)
        self.env._log_seg = _seg; self.rng2 = np.random.default_rng(seed + 12345)
        n = self.env.observation_space.shape[0] + EXTRA; self.observation_space = spaces.Box(-np.inf, np.inf, (n,), np.float32)
    def configure(self, **kw):
        for k, v in kw.items():
            if v is not None: setattr(self, k, v)
    def _ensure_ref(self):
        e = self.env
        if self.xf_hard > 0 and (self.ref is None or self.ref_len != e.club_len):   # HARD X-factor cap: waist_yaw target clipped to address + xf_hard deg (also bounds the reference)
            wi = [j for j, n in enumerate(e.names) if n.startswith("waist_yaw")][0]; e.jhi[wi] = min(e.jhi[wi], e.q_addr[wi] + np.radians(self.xf_hard))
        if self.ref is None or self.ref_len != e.club_len:
            self.ref = SwingRef(e.names, e.q_addr, e.lead, e.jlo, e.jhi, keys=self.ref_keys, t_down=self.t_down); self.ref_len = e.club_len; self.home = e.q_addr.copy()
    def _xobs(self, o):
        t = self.env.d.time; r = self.ref
        return np.concatenate([o, [r.u(t), r.downswing_phase(t), 1.0 if t < r.t_dstart else 0.0, float(np.clip((r.t_imp - t) / 0.3, -1.0, 1.0))]]).astype(np.float32)
    def reset(self, **kw):
        out = super().reset(**kw); e = self.env; self._ensure_ref(); e.q_addr = self.home.copy(); r = self.ref
        u = self.rng2.random(); mode = 0 if u < self.rsi[0] else 1 if u < self.rsi[0] + self.rsi[1] else 2
        t_start = 0.0 if mode == 0 else r.t_dstart if mode == 1 else r.t_dstart + self.rng2.uniform(0.3, 0.7) * r.t_down
        e.act_scale[:] = 0.0; self.mode = mode; ok = True
        while e.d.time < t_start - 1e-6:
            e.q_addr = r.q(e.d.time); _, _, term, tr, _i = e.step(np.zeros(len(self.home)))
            if term or tr or e.contact or e.foul: ok = False; break
        if not ok:
            out = super().reset(**kw); e.q_addr = self.home.copy(); self.mode = 0
        e.q_addr = r.q(e.d.time); self.nstep = 6; self.trk_sum = 0.0; self.trk_n = 0; self._cprev = False; self._sl_ep = 0.0; self._slead = 0.0; self.prev_a = None
        return self._xobs(e._obs()), {}
    def step(self, a):
        e = self.env; r = self.ref; e.q_addr = r.q(e.d.time); e.act_scale[:] = 0.2 * self.res_scale
        self._slead = 0.0
        o, rew, term, trunc, info = super().step(a)
        err = e.d.qpos[e.qa] - r.q(e.d.time); rmse = float(np.sqrt(np.mean(err ** 2))); self.trk_sum += rmse; self.trk_n += 1
        t_ = e.d.time; tw = max(self.track_w, self.bs_floor) if t_ < r.t_dstart else max(self.track_w, self.track_floor)   # backswing/hold tracking floor (Stage J v3): full-swing episodes lost the backswing once tracking annealed to 0
        rew += 0.1 * tw * float(np.exp(-(rmse / 0.25) ** 2))
        if e.armed and not e.contact:   # X-factor cap: 82-112 deg seen in det evals; kseq-v2/public target 40-65
            xf = abs(float(e.log["xfactor_deg"][-1])) if len(e.log["xfactor_deg"]) else 0.0; rew -= self.xf_cap_w * float(np.clip((xf - self.xf_cap_lo) / 20.0, 0.0, 2.0))
        rew -= self.grf_w * float(np.clip((self._slead if self.fine_grf else self.prev_lead) - self.grf_lo, 0.0, 6.0))   # extra lead-foot impulse penalty (harness measured 3.4-3.9 BW vs 0.8-1.7)
        if e.contact and not self._cprev and not info.get('ep', {}).get('unstable'):   # centred strike + spin cap
            q_ = max(0.0, 1 - np.hypot(info['dy'], info['dz']) / self.hit_tol); rew += self.ctr_w * q_ - self.spin_w * float(np.clip((info.get('spin_rpm', 0.0) - 3000.0) / 2000.0, 0.0, 1.0))
            if self.spd_w > 0: rew += self.spd_w * float(np.clip((float(info.get('club_speed_mph', 0.0)) - 60.0) / 20.0, 0.0, 1.0))
            if self.smash_w > 0: rew += self.smash_w * float(np.clip((float(info.get('smash', 0.0)) - 1.1) / 0.2, 0.0, 1.0))
            if self.launch_w > 0:   # launch window 10-14 deg, penalise < 9 deg
                la = float(info.get('launch_deg', 0.0)); rew += self.launch_w * (float(la >= 10.0 and la <= self.launch_hi) + 0.5 * float(np.clip(1.0 - min(abs(la - 10.0), abs(la - self.launch_hi)) / 4.0, 0.0, 1.0)) * float(not (10.0 <= la <= self.launch_hi))) - self.launch_w * float(np.clip((9.0 - la) / 5.0, 0.0, 1.0))
            if self.desc_w > 0:     # descent angle toward driver ~35-40 deg (shallow 11-13 deg gives total/carry ~2); needs carry to count
                dsc = float(info.get('descent_deg', 0.0)); rew += self.desc_w * float(np.clip((dsc - 12.0) / 22.0, 0.0, 1.0)) * float(info.get('carry_m_noroll', 0.0) > 15.0)
            if self.dloft_w > 0:    # dynamic loft 12-18 deg and non-steep attack angle
                dl = float(info.get('dynamic_loft_deg', 0.0)); rew += self.dloft_w * float(np.clip(1.0 - max(self.dl_lo - dl, dl - self.dl_hi, 0.0) / 5.0, 0.0, 1.0)) - 0.5 * self.dloft_w * float(np.clip((self.aoa_lo - float(info.get('aoa_deg', 0.0))) / 6.0, 0.0, 1.0))
            if self.spin_lo_w > 0:  # spin band 1800-3000 rpm
                sp = float(info.get('spin_rpm', 0.0)); rew -= self.spin_lo_w * float(np.clip((1800.0 - sp) / 1800.0, 0.0, 1.0))
        self._cprev = bool(e.contact)
        if self.ord2_w > 0 and "ep" in info and info["ep"].get("contact"):   # proximal-to-distal separation: thorax peak >=~2 samples before arm, arm before club
            L = e.log; n_ = max(int(np.searchsorted(np.array(L["t"]), e.t_contact, side="right")), 2); tt = np.array(L["t"][:n_])
            pk = {k: float(tt[int(np.argmax(L[k][:n_]))]) for k in ("pelvis", "thorax", "lead_arm", "club")}
            g1 = float(np.clip((pk["lead_arm"] - pk["thorax"]) / 0.04, -1.0, 1.0)); g2 = float(np.clip((pk["club"] - pk["lead_arm"]) / 0.04, -1.0, 1.0)); g0 = float(np.clip((pk["thorax"] - pk["pelvis"]) / 0.04, -1.0, 1.0))
            rew += self.ord2_w * (g0 + g1 + g2) / 3.0
        if "ep" in info and info["ep"].get("contact"): rew += self.ord_w * float(info["ep"].get("seq", 0.0))   # extra pelvis->thorax->arm->club order credit on real strikes
        if "ep" in info and e.contact: info["ep"].update(descent=float(info.get("descent_deg", 0.0)), land_mps=float(info.get("landing_speed_mps", 0.0)), spin=float(info.get("spin_rpm", 0.0)), smash=float(info.get("smash", 0.0)), dloft=float(info.get("dynamic_loft_deg", 0.0)), aoa=float(info.get("aoa_deg", 0.0)), lead_fine=float(self._sl_ep), tot_over_carry=float(info.get("total_m_model", 0.0)) / max(float(info.get("carry_m_noroll", 0.0)), 1e-3))
        if "ep" in info: info["ep"].update(track_rmse=self.trk_sum / max(self.trk_n, 1), mode=self.mode)
        e.q_addr = r.q(e.d.time)
        return self._xobs(e._obs()), rew, term, trunc, info

class CurrJ(CurrH):
    def _apply(self):
        p = min(self.num_timesteps / self.total_all, 1.0)
        tw = 1.0 if self.anneal_start is None else float(1.0 - (1.0 - self.track_end) * np.clip((self.num_timesteps - self.anneal_start) / self.track_len, 0, 1))
        cur = (1.15, 0.0, round(0.03 - 0.01 * p, 3), self.T, round(tw, 3))
        if cur != self.cur:
            self.cur = cur
            for k, val in (("target_len", 1.15), ("target_tether", 0.0), ("hit_tol", cur[2]), ("progress", p), ("speed_T", float(self.T)), ("track_w", cur[4])):
                self.training_env.env_method("__setattr__", k, val)
    def det_eval(self, n=16):
        vn = self.training_env; env = JEnv(seed=999, keys=self.keys, res_scale=self.res_scale, t_down=self.t_down); env.configure(**self.extra); env.rsi = (1.0, 0.0, 0.0)
        env.prior_w, env.rate_w = 0.0, self.rate_w; env.env.arm_dist = 0.6; env.hit_tol = self.cur[2]; env.target_len = 1.15; env.target_tether = 0.0; env.env.friction_rand = False
        env.progress = self.num_timesteps / self.total_all; env.speed_T = self.T; env.track_w = self.cur[4]
        res = []
        for _ in range(n):
            o, _i = env.reset(seed=4000 + len(res)); done = False; info = {}
            while not done:
                act, _s = self.model.predict(vn.normalize_obs(o[None]), deterministic=True); o, r, te, tr, info = env.step(act[0]); done = te or tr
            res.append(info["ep"])
        c = [x for x in res if x["contact"]]; med = lambda k: float(np.median([x[k] for x in c])) if c else 0.0
        fwdc = [x for x in c if x["fwd"] > 0.5 and x["carry"] > 0]
        row = dict(step=self.num_timesteps, T=self.T, track_w=self.cur[4], contact=len(c) / n, foul=float(np.mean([x["foul"] for x in res])), fell=float(np.mean([x["fell"] or x["unstable"] for x in res])),
                   impact_mph_med=med("club_mph"), impact_mph_max=float(max([x["club_mph"] for x in c])) if c else 0.0, carry_med=med("carry"), carry_max=float(max([x["carry"] for x in c])) if c else 0.0,
                   launch_med=med("launch"), lat_abs=float(np.mean([abs(x["lat"]) for x in c])) if c else 0.0, fwd_strike_frac=len(fwdc) / n, lead_grf_bw=float(np.mean([x["lead_grf_peak_bw"] for x in res])),
                   flail=float(np.mean([x["flail_ratio"] for x in res])), track_rmse=float(np.mean([x.get("track_rmse", 0.0) for x in res])), hpeak_mph=float(np.mean([x.get("hpeak_mph", 0.0) for x in res])),
                   descent_med=med("descent"), spin_med=med("spin"), land_mps_med=med("land_mps"), dloft_med=med("dloft"), aoa_med=med("aoa"), tot_over_carry_med=med("tot_over_carry"),
                   lead_grf_fine=float(np.mean([x.get("lead_fine", 0.0) for x in c])) if c else 0.0, smash_med=med("smash"),
                   xf_deg=med("xf_deg") if c and "xf_deg" in c[0] else None, seq=float(np.mean([x.get("seq", 0.0) for x in c])) if c else 0.0)
        sc = row["contact"] * (float(np.median([x["carry"] for x in fwdc])) if fwdc else 0.0) * (min(1.0, max(row["descent_med"], 1.0) / 30.0) if self.desc_sel else 1.0) * ((0.4 + 0.6 * float(row["spin_med"] <= 3000.0)) * (0.6 + 0.4 * float(row["launch_med"] <= 16.0)) if self.sel_k4 else 1.0) + 0.001 * row["contact"] * row["impact_mph_med"]; row["best_score"] = sc
        if row["contact"] >= 0.9 and row["fwd_strike_frac"] >= 0.9 and row["impact_mph_med"] >= 0.8 * self.T and row["carry_med"] >= self.carry_min:
            self.T += self.T_step; self.last_promo = self.num_timesteps; row["promoted_to"] = self.T
        if self.anneal_start is None and self.num_timesteps >= self.track_hold and row["fell"] <= 0.25 and row["track_rmse"] < 0.3:
            self.anneal_start = self.num_timesteps; row["anneal_started"] = True
        if sc > getattr(self, "best_sc", 0.0) + 1e-3:
            self.best_sc = sc; self.last_promo = self.num_timesteps; atomic_save(self.model, self.training_env, self.out, "best_det"); open(os.path.join(self.out, "best_det.json"), "w").write(json.dumps(row))
        open(os.path.join(self.out, "eval.jsonl"), "a").write(json.dumps(row) + "\n")
        json.dump(dict(T=self.T, last_promo=self.last_promo, anneal_start=self.anneal_start, best_sc=getattr(self, "best_sc", 0.0)), open(os.path.join(self.out, "curriculum.json"), "w"))
        if row["contact"] >= 0.9 and row["carry_med"] > 30.0 and self.num_timesteps >= 200_000 and not getattr(self, "no_stop", False):
            self.stop = True; open(os.path.join(self.out, "STOP_REACHED"), "w").write(json.dumps(row))
        if self.num_timesteps - self.last_promo >= 1_000_000:      # steps since training START (num_timesteps is persisted across resumes); last_promo = last promotion/best-score gain
            self.stop = True; open(os.path.join(self.out, "STALLED"), "w").write(json.dumps(row))

def make(rank, seed, dt, keys, rs, td, extra=None):
    def f():
        e_ = JEnv(dt=dt, seed=seed * 100 + rank + 191, keys=keys, res_scale=rs, t_down=td); e_.configure(**(extra or {})); return e_
    return f

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=3_000_000); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageJ"); ap.add_argument("--keys", default="results/v5_runs/stageJ_ref/tuned_keys.json")
    ap.add_argument("--res_scale", type=float, default=1.0); ap.add_argument("--t_down", type=float, default=0.27); ap.add_argument("--T0", type=float, default=30.0)
    ap.add_argument("--track_hold", type=int, default=400_000); ap.add_argument("--track_len", type=int, default=1_200_000); ap.add_argument("--track_end", type=float, default=0.2)
    ap.add_argument("--ent", type=float, default=0.003); ap.add_argument("--log_std", type=float, default=-1.0); ap.add_argument("--log_std_end", type=float, default=-1.6); ap.add_argument("--std_end", type=float, default=0.7)
    ap.add_argument("--rate_w", type=float, default=0.05); ap.add_argument("--resume", action="store_true"); ap.add_argument("--reset_stall", action="store_true"); ap.add_argument("--init_ck", default=None)
    ap.add_argument("--lr", type=float, default=3e-4); ap.add_argument("--sel_k4", action="store_true"); ap.add_argument("--launch_hi", type=float, default=None); ap.add_argument("--dl_lo", type=float, default=None); ap.add_argument("--dl_hi", type=float, default=None); ap.add_argument("--aoa_lo", type=float, default=None); ap.add_argument("--spd_w", type=float, default=None); ap.add_argument("--fine_grf", action="store_true"); ap.add_argument("--smash_w", type=float, default=None); ap.add_argument("--spin_w", type=float, default=None); ap.add_argument("--spin_hi", type=float, default=None); ap.add_argument("--spin_scale", type=float, default=None); ap.add_argument("--desc_sel", action="store_true"); ap.add_argument("--launch_w", type=float, default=None); ap.add_argument("--desc_w", type=float, default=None); ap.add_argument("--dloft_w", type=float, default=None); ap.add_argument("--spin_lo_w", type=float, default=None); ap.add_argument("--snap_every", type=int, default=0); ap.add_argument("--ord2_w", type=float, default=None); ap.add_argument("--no_stop", action="store_true"); ap.add_argument("--T_step", type=float, default=5.0); ap.add_argument("--carry_min", type=float, default=0.0); ap.add_argument("--xf_hard", type=float, default=None); ap.add_argument("--grf_lo", type=float, default=None)
    ap.add_argument("--grf_w", type=float, default=None); ap.add_argument("--xf_cap_lo", type=float, default=None); ap.add_argument("--xf_cap_w", type=float, default=None); ap.add_argument("--track_floor", type=float, default=None)
    a = ap.parse_args()
    keys = {tuple(k.split("|")): v for k, v in json.load(open(a.keys)).items()} if a.keys and a.keys != "none" else None
    extra = dict(xf_hard=a.xf_hard, grf_lo=a.grf_lo, grf_w=a.grf_w, xf_cap_lo=a.xf_cap_lo, xf_cap_w=a.xf_cap_w, ord2_w=a.ord2_w, launch_w=a.launch_w, launch_hi=a.launch_hi, dl_lo=a.dl_lo, dl_hi=a.dl_hi, aoa_lo=a.aoa_lo, spd_w=a.spd_w, smash_w=a.smash_w, spin_w=a.spin_w, spin_hi=a.spin_hi, spin_scale=a.spin_scale, fine_grf=(True if a.fine_grf else None), desc_w=a.desc_w, dloft_w=a.dloft_w, spin_lo_w=a.spin_lo_w, track_floor=a.track_floor)
    out = f"results/v5_runs/{a.tag}_s{a.seed}"; os.makedirs(out, exist_ok=True)
    venv = SubprocVecEnv([make(i, a.seed, a.dt, keys, a.res_scale, a.t_down, extra) for i in range(a.workers)])
    step0, ck = newest(out) if a.resume else (0, None)
    if ck:
        venv = VecNormalize.load(ck.replace(".zip", "_vecnorm.pkl"), venv); venv.training = True; model = PPO.load(ck, env=venv, device="cpu")
    else:
        venv = VecNormalize(venv, norm_obs=True, norm_reward=True, clip_obs=10.0)
        model = PPO("MlpPolicy", venv, n_steps=1024, batch_size=512, n_epochs=8, learning_rate=a.lr, gamma=0.99, gae_lambda=0.95, ent_coef=a.ent, seed=a.seed,
                    policy_kwargs=dict(net_arch=[256, 256], log_std_init=a.log_std), device="cpu", verbose=0)
    if a.init_ck and not ck:
        src = PPO.load(a.init_ck + ".zip", device="cpu"); model.policy.load_state_dict(src.policy.state_dict()); model.policy.log_std.data.fill_(a.log_std)
        old = VecNormalize.load(a.init_ck + "_vecnorm.pkl", venv); venv.obs_rms = old.obs_rms
    json.dump(vars(a), open(os.path.join(out, "args.json"), "w"))
    cb = CurrJ(a.steps, out, 10**12, a.tag); cb.base = 0; cb.total_all = a.steps; cb.stop = False; cb.planar = False; cb.act_end, cb.prior_w, cb.rate_w = 1.0, 0.0, a.rate_w; cb.h_every = 100_000; cb.h_last = step0
    cb.keys, cb.res_scale, cb.t_down = keys, a.res_scale, a.t_down; cb.extra = extra; cb.desc_sel = a.desc_sel; cb.sel_k4 = a.sel_k4; cb.no_stop = a.no_stop; cb.T_step, cb.carry_min = a.T_step, a.carry_min; cb.track_hold, cb.track_len, cb.track_end = a.track_hold, a.track_len, a.track_end
    cb.T, cb.last_promo, cb.anneal_start, cb.best_sc = a.T0, 0, None, 0.0
    cj = os.path.join(out, "curriculum.json")
    if ck and os.path.exists(cj): d_ = json.load(open(cj)); cb.T, cb.last_promo, cb.anneal_start, cb.best_sc = d_["T"], d_["last_promo"], d_.get("anneal_start"), d_.get("best_sc", 0.0)
    if ck and a.reset_stall: cb.last_promo = model.num_timesteps
    cb.ls0, cb.ls1, cb.std_end, cb.ent0 = a.log_std, a.log_std_end, a.std_end, a.ent
    try: model.learn(a.steps - (model.num_timesteps if ck else 0), callback=cb, reset_num_timesteps=not ck)
    finally:
        try: atomic_save(model, venv, out, "final")
        except Exception as ex_: print("final save failed", ex_, file=sys.stderr)
