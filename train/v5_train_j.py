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
    res_scale = 1.0; track_w = 1.0; bs_floor = 1.0; xf_cap_w = 0.08; xf_cap_lo = 60.0; ord_w = 1.5; track_floor = 0.3; grf_w = 0.15; ctr_w = 2.0; spin_w = 1.0; spin_cap = 1.0; spd_top = 1.0; shear_w = 0.0; shear_hi = 0.65; log_shear = True; _shr = 0.0; shr_max = 0.0; slow_w = 0.0; slow_lo = 66.0; dlh_w = 0.0; _cprev = False; ord2_w = 0.0; launch_w = 0.0; launch_hi = 14.0; dl_lo = 12.0; dl_hi = 18.0; aoa_lo = -6.0; spd_w = 0.0; res_mult = None; ctrl_dt = None; pel_w = 0.0; pel_t_w = 0.0; pel_dps = 400.0; pel_t_lo = 0.10; sep_w = 0.0; early_w = 0.0; aim_w = 0.0; foot_w = 0.0; plant_term = 0.0; grfd_w = 0.0; post_t = 0.0; init_qn = 0.0; init_qvn = 0.0; fr_rand = False; ball_tol = 0.0; fr_lo = 0.9; fr_hi = 1.1; strike_w = 0.0; tc_w = 0.0; smash2_w = 0.0; ctr2_w = 0.0; _off = None; _ft = None; f_lift = 0.0; f_slip = 0.0; pel_t_hi = 0.15; fine_grf = False; smash_w = 0.0; spin_hi = 3000.0; spin_scale = 2000.0; desc_w = 0.0; dloft_w = 0.0; spin_lo_w = 0.0; xf_hard = 0.0; grf_lo = 2.0; rsi = (0.4, 0.3, 0.3); ref_keys = None; t_down = 0.27; k_ease = 1.6; grf_term = 6.0
    def __init__(self, dt=0.002, seed=0, keys=None, res_scale=1.0, t_down=0.27):
        super().__init__(dt=dt, seed=seed, planar=False); self.ref_keys = keys; self.res_scale = res_scale; self.t_down = t_down; self.ref = None
        self.target_len = 1.15; self.target_tether = 0.0; self.prior_w = 0.0; self.env.friction_rand = False; self.env.detail_info = True; self._slead = 0.0; self._sl_ep = 0.0; _orig = self.env._log_seg; _e = self.env
        def _seg():   # 5 ms-resolution lead-foot vertical force (what the harness measures); control-step samples miss impulses
            _orig(); fl, fr = _e.foot_forces(); v_ = (fl if _e.lead == "left" else fr) / self.bw; self._slead = max(self._slead, v_); self._sjump = max(getattr(self, '_sjump', 0.0), abs(v_ - getattr(self, '_slast', v_))); self._slast = v_
            self._sl_ep = max(self._sl_ep, v_)
            if self.shear_w > 0 or self.log_shear:   # K27: lead-foot shear/vertical (harness v3c info row; ref <=0.65-0.75)
                import mujoco as _mj; gid = _e.sole_geoms[_e.lead]; fv = np.zeros(6); fn = 0.0; ft = np.zeros(3)
                if _e.fast_env:   # STEP2(1): reuse the cached lead-sole contact forces (same contacts/order/values)
                    for fr_, fv_ in _e._sole_contacts()[1]: w_ = fr_.T @ fv_[:3]; fn += fv_[0]; ft += w_ - fv_[0] * fr_[0]
                for i in (range(0) if _e.fast_env else range(_e.d.ncon)):
                    c = _e.d.contact[i]
                    if (c.geom1 == gid and c.geom2 == _e.floor) or (c.geom2 == gid and c.geom1 == _e.floor):
                        _mj.mj_contactForce(_e.m, _e.d, i, fv); fr_ = c.frame.reshape(3, 3); w_ = fr_.T @ fv[:3]; fn += fv[0]; ft += w_ - fv[0] * fr_[0]
                self._shr = float(np.linalg.norm(ft[:2]) / fn) if fn > 0.2 * self.bw else 0.0
        self.env._log_seg = _seg; self.rng2 = np.random.default_rng(seed + 12345)
        n = self.env.observation_space.shape[0] + EXTRA; self.observation_space = spaces.Box(-np.inf, np.inf, (n,), np.float32)
    def _sole(self):
        e = self.env; sid = e.m.site(f"{e.lead}_sole_site").id; P = e.d.site_xpos[sid]; R = e.d.site_xmat[sid].reshape(3, 3); hx = float(e.m.site_size[sid][0])
        return (float(P[0]), float(P[1]), float((P - hx * R[:, 0])[2]), float((P + hx * R[:, 0])[2]), float(np.arctan2(R[1, 0], R[0, 0])))
    def configure(self, **kw):
        for k, v in kw.items():
            if v is not None: setattr(self, k, v)
        if getattr(self, 'stance_obs', None) and not getattr(self, '_stance_dim', False):   # V18: --stance_obs (default off) appends 4 obs dims (see _xobs); resize the space once
            self._stance_dim = True; n = self.observation_space.shape[0] + 4; self.observation_space = spaces.Box(-np.inf, np.inf, (n,), np.float32)
    def _ensure_ref(self):
        e = self.env
        if self.xf_hard > 0 and (self.ref is None or self.ref_len != e.club_len):   # HARD X-factor cap: waist_yaw target clipped to address + xf_hard deg (also bounds the reference)
            wi = [j for j, n in enumerate(e.names) if n.startswith("waist_yaw")][0]; e.jhi[wi] = min(e.jhi[wi], e.q_addr[wi] + np.radians(self.xf_hard))
        if self.ref is None or self.ref_len != e.club_len:
            self.ref = SwingRef(e.names, e.q_addr, e.lead, e.jlo, e.jhi, keys=self.ref_keys, t_down=self.t_down); self.ref.memo = bool(getattr(e, "fast_env", False)); self.ref_len = e.club_len; self.home = e.q_addr.copy()
    def _xobs(self, o):
        t = self.env.d.time; r = self.ref
        x = np.concatenate([o, [r.u(t), r.downswing_phase(t), 1.0 if t < r.t_dstart else 0.0, float(np.clip((r.t_imp - t) / 0.3, -1.0, 1.0))]]).astype(np.float32)
        if getattr(self, 'stance_obs', None):   # V18 --stance_obs: ball xy minus lead / trail sole xy (world, x10 m); spread diag: lead-sole shift after the reset perturbation drives strike dy
            e = self.env; b_ = e.d.qpos[e.ball_q:e.ball_q + 2]; tr_ = 'left' if e.lead == 'right' else 'right'
            sp_ = lambda n_: e.d.site_xpos[e.m.site(f"{n_}_sole_site").id][:2]
            x = np.concatenate([x, 10.0 * (b_ - sp_(e.lead)), 10.0 * (b_ - sp_(tr_))]).astype(np.float32)
        return x
    def reset(self, **kw):
        if getattr(self, 'fast_env', None): self.env.fast_env = True   # STEP2(1) --fast_env (identical rewards/info/obs; scripts/fast_env_equiv.py)
        if getattr(self, 'env_v4', None) and not getattr(self.env, 'env_v4', False): self.env.set_env_v4(True); self.ref = None   # v4 re-baseline (new address -> rebuild the reference on the new q_addr)
        elif getattr(self, 'head', None) and not getattr(self.env, 'env_v4', False) and self.head != getattr(self.env, 'head', 'box'): self.env.set_head(self.head)   # K34 --head realistic (default None/box = unchanged)
        self.env.face_h = getattr(self, 'face_h', None); self.env.tee_dz = float(getattr(self, 'tee_dz', None) or 0.0); self.env.tee_mode = getattr(self, 'tee_mode', None); ta_ = getattr(self, 'tee_anneal', None)
        if ta_: self.env.tee_mode = None; self.env.tee_dz = self.env.crown_tee_dz() * max(0.0, 1.0 - float(getattr(self, 'progress', 0.0)) / float(ta_))   # K33c: crown tee -> old tee curriculum over the first ta_ fraction of training
        self.env.ball_dx = float(getattr(self, 'ball_dx', None) or 0.0); self.env.off_face = False; self.env.friction_rand = False; self.env.ball_tol = float(self.ball_tol)   # K24: tee +-ball_tol; floor friction drawn below in [fr_lo, fr_hi] (Orchestrator: 0.9-1.1)
        if self.fr_rand: self.env.m.geom_friction[self.env.floor, 0] = self.rng2.uniform(self.fr_lo, self.fr_hi)
        out = super().reset(**kw); e = self.env; self._ensure_ref(); e.q_addr = self.home.copy(); r = self.ref
        self._ft = None; self.f_lift = 0.0; self.f_slip = 0.0; self._plant_break = False; self.shr_max = 0.0; self._shr = 0.0; self._off = None; self._g = 1.0; self._ph = (0.0, 0.0, 0); self._ph_run = 0; self._addr = None; self._air_run = 0; self.f_air = 0
        u = self.rng2.random(); mode = 0 if u < self.rsi[0] else 1 if u < self.rsi[0] + self.rsi[1] else 2
        t_start = 0.0 if mode == 0 else r.t_dstart if mode == 1 else r.t_dstart + self.rng2.uniform(0.3, 0.7) * r.t_down
        e.act_scale[:] = 0.0; self.mode = mode; ok = True
        while e.d.time < t_start - 1e-6:
            e.q_addr = r.q(e.d.time); _, _, term, tr, _i = e.step(np.zeros(len(self.home)))
            if term or tr or e.contact or e.foul: ok = False; break
        if not ok:
            out = super().reset(**kw); e.q_addr = self.home.copy(); self.mode = 0
        self._nom = bool(getattr(self, 'nom_frac', None)) and self.mode == 0 and self.rng2.random() < self.nom_frac   # V15: noiseless address starts (harness nominal row), default off
        if self._nom: self.env.m.geom_friction[self.env.floor, 0] = 1.0
        _hs_on = bool(self.mode == 0 and not self._nom and getattr(self, 'hstart_frac', None) and self.rng2.random() < self.hstart_frac)
        if self.mode == 0 and not self._nom and not _hs_on and (self.init_qn > 0 or self.init_qvn > 0):   # K24: perturbed start at address (robustness gate)
            nr_ = getattr(self, 'noise_ramp', None); sc_ = min(1.0, max(0.2, float(getattr(self, 'progress', 0.0)) / float(nr_))) if nr_ else 1.0   # V5: start-noise curriculum (20% -> 100% by fraction noise_ramp)
            e.d.qpos[e.qa] += self.rng2.uniform(-sc_ * self.init_qn, sc_ * self.init_qn, len(e.qa)); e.d.qvel[e.da] += self.rng2.uniform(-sc_ * self.init_qvn, sc_ * self.init_qvn, len(e.da))
            import mujoco; mujoco.mj_forward(e.m, e.d); out = (e._obs(), {})
        self._hs = None
        if _hs_on:   # V18: harness-v4-style perturbed start (Evaluator _j_worker_gp_v3 magnitudes/streams) on seeds 10000..899999 (never the gating seeds 7000-7023), replaces the trainer noise above; default off
            import mujoco; sd_ = int(self.rng2.integers(10000, 900000)); self._hs = sd_
            e.m.geom_friction[e.floor, 0] = np.random.default_rng(sd_ + 0xF41C).uniform(0.7, 1.05); rg_ = np.random.default_rng(sd_ + 0x5EED); nq_ = len(e.qa)
            e.d.qpos[e.qa] += np.radians(1.5) * rg_.uniform(-1, 1, nq_); e.d.qvel[e.da] += 0.05 * rg_.uniform(-1, 1, nq_); mujoco.mj_forward(e.m, e.d); out = (e._obs(), {})
        e.q_addr = r.q(e.d.time); self.nstep = 6; self.trk_sum = 0.0; self.trk_n = 0; self._cprev = False; self._sl_ep = 0.0; self._slead = 0.0; self.prev_a = None
        return self._xobs(e._obs()), {}
    def step(self, a):
        e = self.env; r = self.ref; e.q_addr = r.q(e.d.time); e.act_scale[:] = 0.2 * self.res_scale
        if self.ctrl_dt: e.sub = int(round(self.ctrl_dt / e.dt))   # K14b: control rate
        if self.res_mult:   # K14a: per-joint-kind residual authority multipliers, e.g. {"hip_yaw": 0.25, "waist_yaw": 0.25}
            if getattr(self, "_rm_vec", None) is None:
                kinds = [n.replace("left_", "").replace("right_", "").replace("_joint", "") for n in e.names]; self._rm_vec = np.array([self.res_mult.get(k, 1.0) for k in kinds])
            e.act_scale[:] *= self._rm_vec
        self._slead = 0.0; self._sjump = 0.0
        o, rew, term, trunc, info = super().step(a)
        if getattr(self, 'res_l2_w', None): rew -= self.res_l2_w * float(np.mean(np.square(np.clip(np.asarray(a, float), -1, 1))))   # V8: anti-drift, L2 on the residual action (default off)
        if self.grfd_w > 0 and (not e.contact or e.after < 0.2): rew -= self.grfd_w * float(np.clip((self._sjump - 0.3) / 0.5, 0.0, 3.0))   # K24: frame-to-frame lead GRF jumps (re-landing spikes)
        if getattr(self, '_plant_break', False): rew -= 5.0 * max(self.foot_w, 1.0); term = True; trunc = False; info['plant_break'] = True
        if self._addr is None:   # K16: lead-foot reference = ADDRESS pose (Evaluator 08835a4 metric)
            self._addr = self._sole()
        if e.d.time >= r.t_top and (not e.contact or e.after < self.post_t):   # top -> impact (+ post_t s of follow-through, K24): slip/yaw vs address, whole-foot airborne (zero lead GRF or heel AND toe up)
            x, y, zh, zt, yw = self._sole(); x0, y0, zh0, zt0, yw0 = self._addr
            sl = float(np.hypot(x - x0, y - y0)); tn = abs(float((np.degrees(yw - yw0) + 180.0) % 360.0 - 180.0))
            gl = float(e.foot_forces()[0 if e.lead == "left" else 1]); air = (gl <= 1.0) or (zh > zh0 + 0.005 and zt > zt0 + 0.005)
            self._air_run = self._air_run + 1 if air else 0
            self.f_slip = max(self.f_slip, sl); self.f_lift = max(self.f_lift, tn); self.f_air = max(self.f_air, self._air_run)
            if not e.contact: self.shr_max = max(self.shr_max, self._shr)
            if self.shear_w > 0: rew -= self.shear_w * float(np.clip((self._shr - self.shear_hi) / 0.2, 0.0, 3.0))
            if self.foot_w > 0:
                rew -= self.foot_w * (float(np.clip(sl / 0.05, 0.0, 4.0)) + float(np.clip(tn / 20.0, 0.0, 4.0)) + 1.5 * float(air))
                if self.plant_term > 0 and (self._air_run >= 3 or sl > self.plant_term * 0.05 or tn > self.plant_term * 20.0): self._plant_break = True
        if getattr(self, 'plant_h_w', None) and self.mode == 0 and e.d.time >= r.t_dstart and not e.contact:   # V9: harness-matched plant (window ref t_dstart -> impact, vs address; Evaluator pass = slip<=3 cm, turn<=12 deg, airborne<1.8 ctrl steps)
            x_, y_, zh_, zt_, yw_ = self._sole(); x0_, y0_, zh0_, zt0_, yw0_ = self._addr; gl_ = float(e.foot_forces()[0 if e.lead == 'left' else 1])
            air_ = (gl_ <= 1.0) or (zh_ > zh0_ + 0.005 and zt_ > zt0_ + 0.005); self._ph_run = self._ph_run + 1 if air_ else 0
            self._ph = (max(self._ph[0], float(np.hypot(x_ - x0_, y_ - y0_))), max(self._ph[1], abs(float((np.degrees(yw_ - yw0_) + 180.0) % 360.0 - 180.0))), max(self._ph[2], self._ph_run))
            if getattr(self, 'turn_m_w', None): rew -= self.turn_m_w * float(np.clip((abs(float((np.degrees(yw_ - yw0_) + 180.0) % 360.0 - 180.0)) - getattr(self, 'turn_tgt', 6.5)) / 2.0, 0.0, 3.0))   # V12: dense lead-foot turn margin (top->impact, mode 0, default off)
        if getattr(self, 'turn_m_w', None) and not getattr(self, 'plant_h_w', None) and self.mode == 0 and e.d.time >= r.t_dstart and not e.contact and getattr(self, '_addr', None) is not None:   # turn margin without plant_h_w (same formula; commands that set plant_h_w use the in-block line above, unchanged)
            rew -= self.turn_m_w * float(np.clip((abs(float((np.degrees(self._sole()[4] - self._addr[4]) + 180.0) % 360.0 - 180.0)) - getattr(self, 'turn_tgt', 6.5)) / 2.0, 0.0, 3.0))
        err = e.d.qpos[e.qa] - r.q(e.d.time); rmse = float(np.sqrt(np.mean(err ** 2))); self.trk_sum += rmse; self.trk_n += 1
        t_ = e.d.time; tw = max(self.track_w, self.bs_floor) if t_ < r.t_dstart else max(self.track_w, self.track_floor)   # backswing/hold tracking floor (Stage J v3): full-swing episodes lost the backswing once tracking annealed to 0
        rew += 0.1 * tw * float(np.exp(-(rmse / 0.25) ** 2))
        if e.armed and not e.contact:   # X-factor cap: 82-112 deg seen in det evals; kseq-v2/public target 40-65
            xf = abs(float(e.log["xfactor_deg"][-1])) if len(e.log["xfactor_deg"]) else 0.0; rew -= self.xf_cap_w * float(np.clip((xf - self.xf_cap_lo) / 20.0, 0.0, 2.0))
        rew -= self.grf_w * float(np.clip((self._slead if self.fine_grf else self.prev_lead) - self.grf_lo, 0.0, 6.0))   # extra lead-foot impulse penalty (harness measured 3.4-3.9 BW vs 0.8-1.7)
        if e.contact and not self._cprev and not info.get('ep', {}).get('unstable'):   # centred strike + spin cap
            if getattr(self, 'plant_h_w', None) and self.mode == 0: sl_, tn_, ar_ = self._ph; rew -= self.plant_h_w * (float(np.clip((sl_ - 0.025) / 0.01, 0.0, 3.0)) + float(np.clip((tn_ - 10.0) / 3.0, 0.0, 3.0)) + float(np.clip((ar_ - 1.0) / 1.0, 0.0, 3.0)))   # V9: applied once at impact
            dzs_ = getattr(self, 'dz_gate', None); self._g = (0.0 if abs(info['dz']) > getattr(self, 'dz_zero', 0.015) else float(np.exp(-(info['dz'] / dzs_) ** 2))) if dzs_ else 1.0   # V6: multiplicative strike-height gate on strike/carry rewards (default off = 1)
            self._off = float(np.hypot(info['dy'], info['dz'])); q_ = max(0.0, 1 - np.hypot(info['dy'], info['dz']) / self.hit_tol); rew += self._g * self.ctr_w * q_ - self.spin_w * float(np.clip((info.get('spin_rpm', 0.0) - self.spin_hi) / self.spin_scale, 0.0, self.spin_cap))  
            if getattr(self, 'edge_w', 0.0) > 0 and abs(info['dz']) > getattr(self, 'edge_dz', 0.0265): rew -= self.edge_w   # K31c: strike off the face (driver face ~53 mm tall, Data Agent DRIVER_FACE_OFFCENTRE_REFS) = miss; shaping only, ball model unchanged
            if getattr(self, 'loc_w', 0.0) > 0 and getattr(self, 'loc_noclip', None): rew -= self.loc_w * (abs(info['dz'] - self.loc_dz) / 0.01 + float(np.clip(abs(info['dy'] - self.loc_dy) / 0.015, 0.0, 4.0)))   # V7: dz part unclipped, dy part clipped separately (large dy no longer saturates dz)
            elif getattr(self, 'loc_w', 0.0) > 0: rew -= self.loc_w * float(np.clip(abs(info['dz'] - self.loc_dz) / 0.01 + abs(info['dy'] - self.loc_dy) / 0.015, 0.0, 4.0))   # K31: per-episode strike-location target (gear effect is in vendored golfphys; offset from target is penalised every seed)
            if getattr(self, 'dz_lin_w', None): rew -= self.dz_lin_w * abs(info['dz'] - getattr(self, 'dz_tgt', 0.0015)) / 0.01   # V7: separate unclipped strike-height term (no dy dependence)
            if getattr(self, 'smash3_w', None) and self.mode == 0: rew += self.smash3_w * float(np.clip((float(info.get('smash', 0.0)) - getattr(self, 'smash3_lo', 1.30)) / (getattr(self, 'smash3_hi', 1.48) - getattr(self, 'smash3_lo', 1.30)), 0.0, 1.0))   # V17: smash/ball-speed term live up to 1.48 (smash_w/smash2_w saturate at 1.30/1.35); address starts, default off
            if getattr(self, 'heel8_w', None) and self.mode == 0 and not getattr(self, '_nom', False) and info['dy'] < -0.008: rew -= self.heel8_w * (1.0 + float(np.clip((-0.008 - info['dy']) / 0.008, 0.0, 3.0)))   # V18: one-sided heel-tail penalty (dy < -8 mm) on noisy address starts; default off
            if getattr(self, 'dy_lin_w', None): rew -= self.dy_lin_w * min(abs(info['dy'] - getattr(self, 'dy_tgt', 0.0)) / 0.015, 10.0)   # V7: separate heel-toe term
            if getattr(self, 'launch_lo_w', None): rew -= self.launch_lo_w * float(np.clip((getattr(self, 'launch_lo', 12.0) - float(info.get('launch_deg', 0.0))) / 2.0, 0.0, 3.0))   # V8: launch floor (t/c)
            if getattr(self, 'lat_w', None) and self.mode == 0 and float(info.get('carry_m_noroll', 0.0) or 0.0) > 1.0: rew -= self.lat_w * float(np.clip((100.0 * abs(float(info.get('lateral_carry_m', 0.0) or 0.0)) / float(info['carry_m_noroll']) - getattr(self, 'lat_tgt', 10.0)) / 3.5, 0.0, 3.0))   # V13: lateral per 100 (harness start-direction pass <=13.5) on address starts, default off; TESTED AND RETIRED: did not lift start direction
            if getattr(self, 'sd_w', None) and self.mode == 0: rew -= self.sd_w * float(np.clip((abs(float(info.get('azimuth_deg', 0.0))) - 3.0) / 4.0, 0.0, 3.0))   # V8: start direction on address (noisy) starts
            if self.slow_w > 0: rew -= self.slow_w * float(np.clip((self.slow_lo - float(info.get('club_speed_mph', 0.0))) / 10.0, 0.0, 3.0))   # K25: low-club-speed penalty
            if self.dlh_w > 0: rew -= self.dlh_w * float(np.clip((float(info.get('dynamic_loft_deg', 0.0)) - self.dl_hi) / 2.0, 0.0, 4.0))   # K25: hard de-loft above dl_hi # was hard-coded 3000/2000 (spin_hi/spin_scale unused until K23)
            if self.spd_w > 0: rew += self._g * self.spd_w * float(np.clip((float(info.get('club_speed_mph', 0.0)) - 60.0) / 20.0, 0.0, self.spd_top))   # K27: spd_top>1 uncaps above 80 mph
            if self.smash_w > 0: rew += self._g * self.smash_w * float(np.clip((float(info.get('smash', 0.0)) - 1.1) / 0.2, 0.0, 1.0))
            if self.launch_w > 0:   # launch window 10-14 deg, penalise < 9 deg
                la = float(info.get('launch_deg', 0.0)); rew += self._g * self.launch_w * (float(la >= 10.0 and la <= self.launch_hi) + 0.5 * float(np.clip(1.0 - min(abs(la - 10.0), abs(la - self.launch_hi)) / 4.0, 0.0, 1.0)) * float(not (10.0 <= la <= self.launch_hi))) - self.launch_w * float(np.clip((9.0 - la) / 5.0, 0.0, 1.0))
            if self.desc_w > 0:     # descent angle toward driver ~35-40 deg (shallow 11-13 deg gives total/carry ~2); needs carry to count
                dsc = float(info.get('descent_deg', 0.0)); rew += self._g * self.desc_w * float(np.clip((dsc - 12.0) / 22.0, 0.0, 1.0)) * float(info.get('carry_m_noroll', 0.0) > 15.0)
            if self.dloft_w > 0:    # dynamic loft 12-18 deg and non-steep attack angle
                dl = float(info.get('dynamic_loft_deg', 0.0)); rew += self._g * self.dloft_w * float(np.clip(1.0 - max(self.dl_lo - dl, dl - self.dl_hi, 0.0) / 5.0, 0.0, 1.0)) - 0.5 * self.dloft_w * float(np.clip((self.aoa_lo - float(info.get('aoa_deg', 0.0))) / 6.0, 0.0, 1.0))
            if self.spin_lo_w > 0:  # spin band 1800-3000 rpm
                sp = float(info.get('spin_rpm', 0.0)); rew -= self.spin_lo_w * float(np.clip((1800.0 - sp) / 1800.0, 0.0, 1.0))
        self._cprev = bool(e.contact)
        if self.ord2_w > 0 and "ep" in info and info["ep"].get("contact"):   # proximal-to-distal separation: thorax peak >=~2 samples before arm, arm before club
            L = e.log; n_ = max(int(np.searchsorted(np.array(L["t"]), e.t_contact, side="right")), 2); tt = np.array(L["t"][:n_])
            pk = {k: float(tt[int(np.argmax(L[k][:n_]))]) for k in ("pelvis", "thorax", "lead_arm", "club")}
            g1 = float(np.clip((pk["lead_arm"] - pk["thorax"]) / 0.04, -1.0, 1.0)); g2 = float(np.clip((pk["club"] - pk["lead_arm"]) / 0.04, -1.0, 1.0)); g0 = float(np.clip((pk["thorax"] - pk["pelvis"]) / 0.04, -1.0, 1.0))
            rew += self.ord2_w * (g0 + g1 + g2) / 3.0
            if self.early_w > 0:   # K15: keep lead-arm speed low 150-40 ms before the club peak (kill the early arm hump)
                av_ = np.abs(np.array(L["lead_arm"][:n_])); w_ = (tt >= pk["club"] - 0.15) & (tt <= pk["club"] - 0.04)
                if w_.any(): rew -= self.early_w * float(np.clip((av_[w_].max() / max(av_.max(), 1e-6) - 0.6) / 0.3, 0.0, 1.0))
            if self.sep_w > 0: rew += self.sep_w * float(np.clip((pk["club"] - pk["lead_arm"] - getattr(self,"sep_lo",0.005)) / getattr(self,"sep_span",0.015), -1.0, 1.0))   # K9: arm peak >= ~1 harness sample before club peak
        if (self.pel_w > 0 or self.pel_t_w > 0) and "ep" in info and info["ep"].get("contact"):   # K7: pelvis peak speed toward pel_dps and pelvis peak 100-150 ms before club peak
            L = e.log; n_ = max(int(np.searchsorted(np.array(L["t"]), e.t_contact, side="right")), 2); tt = np.array(L["t"][:n_]); pv = np.abs(np.array(L["pelvis"][:n_])); cv = np.abs(np.array(L["club"][:n_]))
            dt_ = float(tt[int(np.argmax(cv))] - tt[int(np.argmax(pv))])
            rew += self.pel_w * float(np.clip(pv.max() / self.pel_dps, 0.0, 1.0)) + self.pel_t_w * float(np.clip(1.0 - max(self.pel_t_lo - dt_, dt_ - self.pel_t_hi, 0.0) / 0.08, 0.0, 1.0))
        if getattr(self, "miss_w", 0.0) and "ep" in info and not info["ep"].get("contact"): rew -= self.miss_w   # V5: whiff / off-face miss penalty at episode end
        if getattr(self, "miss0_w", None) and self.mode == 0 and "ep" in info and not info["ep"].get("contact"): rew -= self.miss0_w   # V10: extra miss penalty on noisy address starts (harness contact-under-noise gate)
        if "ep" in info and info["ep"].get("contact"): rew += self.ord_w * float(info["ep"].get("seq", 0.0))   # extra pelvis->thorax->arm->club order credit on real strikes
        if "ep" in info and e.contact: info["ep"].update(descent=float(info.get("descent_deg", 0.0)), land_mps=float(info.get("landing_speed_mps", 0.0)), spin=float(info.get("spin_rpm", 0.0)), smash=float(info.get("smash", 0.0)), dloft=float(info.get("dynamic_loft_deg", 0.0)), aoa=float(info.get("aoa_deg", 0.0)), lead_fine=float(self._sl_ep), tot_over_carry=float(info.get("total_m_model", 0.0)) / max(float(info.get("carry_m_noroll", 0.0)), 1e-3))
        if "ep" in info:
            info["ep"].update(foot_lift=self.f_lift, foot_turn=self.f_lift, foot_slip=self.f_slip, foot_air=self.f_air, shear_ratio=self.shr_max)
            if e.contact:
                az = float(info.get("azimuth_deg", 0.0)); fpth = float(info.get("face_yaw_deg", 0.0)) - float(info.get("club_path_deg", 0.0)); info["ep"].update(az=az, face_path=fpth)
                if self.tc_w > 0 and float(info.get("carry_m_noroll", 0.0)) > 15.0:   # K20: total/carry <= 1.25 (band 1.04-1.25)
                    tc_ = float(info.get("total_m_model", 0.0)) / max(float(info.get("carry_m_noroll", 0.0)), 1e-3); rew -= self.tc_w * float(np.clip((tc_ - 1.22) / 0.1, 0.0, 3.0))
                if self.strike_w > 0 or self.smash2_w > 0 or self.ctr2_w > 0:   # K18: square, non-glancing strike (Evaluator: face -3.5 vs path +22.9, AoA -19, toe/high)
                    pth = float(info.get("club_path_deg", 0.0)); aoa = float(info.get("aoa_deg", 0.0)); sm = float(info.get("smash", 0.0))
                    rew -= self.strike_w * (min(abs(fpth) / 8.0, 3.0) + min(max(abs(pth - 2.0) - 3.0, 0.0) / 8.0, 2.0) + min(max(-1.0 - aoa, aoa - 3.0, 0.0) / 4.0, 3.0))
                    rew += getattr(self, '_g', 1.0) * self.smash2_w * float(np.clip((sm - 0.9) / 0.45, 0.0, 1.0)) - self.ctr2_w * min((self._off or 0.0) / 0.01, 3.0)
                    info["ep"].update(path=pth, aoa_k18=aoa, off=self._off)
                if self.aim_w > 0: rew += getattr(self, '_g', 1.0) * self.aim_w * (0.5 * float(np.clip(1 - abs(az) / 7.0, 0, 1)) + 0.5 * float(np.clip(1 - abs(fpth) / 5.0, 0, 1))) - self.aim_w * float(np.clip((abs(az) - 7.0) / 8.0, 0, 1))
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
                   xf_deg=med("xf_deg") if c and "xf_deg" in c[0] else None, seq=float(np.mean([x.get("seq", 0.0) for x in c])) if c else 0.0, az_abs_med=float(np.median([abs(x.get('az', 0.0)) for x in c])) if c else 0.0, face_path_abs_med=float(np.median([abs(x.get('face_path', 0.0)) for x in c])) if c else 0.0, foot_lift_max=float(max([x.get('foot_lift', 0.0) for x in res])), foot_slip_max=float(max([x.get('foot_slip', 0.0) for x in res])))
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
        e_ = JEnv(dt=dt, seed=seed * 100 + rank + 191, keys=keys, res_scale=rs, t_down=td); e_.configure(**(extra or {}))
        bad = {k: (v, getattr(e_, k, '<missing>')) for k, v in (extra or {}).items() if v is not None and not (getattr(e_, k, '<missing>') is v or (isinstance(v, (int, float, str, bool, tuple)) and getattr(e_, k, '<missing>') == v) or (isinstance(v, (dict, list)) and getattr(e_, k, '<missing>') == v))}
        if bad: raise SystemExit(f"FLAG GUARD: configured flags not live in JEnv (abort): {bad}")   # STEP2 honesty guard: every non-default flag must be set on the live env
        return e_
    return f

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=3_000_000); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageJ"); ap.add_argument("--keys", default="results/v5_runs/stageJ_ref/tuned_keys.json")
    ap.add_argument("--res_scale", type=float, default=1.0); ap.add_argument("--t_down", type=float, default=0.27); ap.add_argument("--T0", type=float, default=30.0)
    ap.add_argument("--track_hold", type=int, default=400_000); ap.add_argument("--track_len", type=int, default=1_200_000); ap.add_argument("--track_end", type=float, default=0.2)
    ap.add_argument("--ent", type=float, default=0.003); ap.add_argument("--log_std", type=float, default=-1.0); ap.add_argument("--log_std_end", type=float, default=-1.6); ap.add_argument("--std_end", type=float, default=0.7)
    ap.add_argument("--rate_w", type=float, default=0.05); ap.add_argument("--resume", action="store_true"); ap.add_argument("--reset_stall", action="store_true"); ap.add_argument("--init_ck", default=None)
    ap.add_argument("--smash3_w", type=float, default=None); ap.add_argument("--smash3_lo", type=float, default=None); ap.add_argument("--smash3_hi", type=float, default=None)
    ap.add_argument("--nom_frac", type=float, default=None); ap.add_argument("--stance_obs", action="store_true", default=None, help="V18: append ball-minus-lead/trail-sole xy to the obs (+4 dims; default off)"); ap.add_argument("--heel8_w", type=float, default=None, help="V18: one-sided heel-tail penalty, dy<-8 mm on noisy address starts (default off)"); ap.add_argument("--hstart_frac", type=float, default=None, help="V18: fraction of noisy address starts drawn harness-v4-style on seeds 10000-899999 (default off)")
    ap.add_argument("--lat_w", type=float, default=None, help="TESTED AND RETIRED (V13: did not lift start direction); default off"); ap.add_argument("--lat_tgt", type=float, default=None, help="TESTED AND RETIRED; used only with --lat_w")
    ap.add_argument("--turn_m_w", type=float, default=None); ap.add_argument("--turn_tgt", type=float, default=None)
    ap.add_argument("--miss0_w", type=float, default=None)
    ap.add_argument("--plant_term", type=float, default=None); ap.add_argument("--strike_w", type=float, default=None); ap.add_argument("--grfd_w", type=float, default=None); ap.add_argument("--post_t", type=float, default=None); ap.add_argument("--init_qn", type=float, default=None); ap.add_argument("--fr_rand", action="store_true"); ap.add_argument("--ball_tol", type=float, default=None); ap.add_argument("--fr_lo", type=float, default=None); ap.add_argument("--spin_cap", type=float, default=None); ap.add_argument("--spd_top", type=float, default=None); ap.add_argument("--shear_w", type=float, default=None); ap.add_argument("--shear_hi", type=float, default=None); ap.add_argument("--slow_w", type=float, default=None); ap.add_argument("--slow_lo", type=float, default=None); ap.add_argument("--dlh_w", type=float, default=None); ap.add_argument("--fr_hi", type=float, default=None); ap.add_argument("--init_qvn", type=float, default=None); ap.add_argument("--tc_w", type=float, default=None); ap.add_argument("--smash2_w", type=float, default=None); ap.add_argument("--ctr2_w", type=float, default=None); ap.add_argument("--pel_w", type=float, default=None); ap.add_argument("--pel_t_w", type=float, default=None); ap.add_argument("--res_mult", type=str, default=None); ap.add_argument("--ctrl_dt", type=float, default=None); ap.add_argument("--ctr_w", type=float, default=None); ap.add_argument("--aim_w", type=float, default=None); ap.add_argument("--foot_w", type=float, default=None); ap.add_argument("--early_w", type=float, default=None); ap.add_argument("--sep_w", type=float, default=None); ap.add_argument("--sep_lo", type=float, default=None); ap.add_argument("--loc_w", type=float, default=None); ap.add_argument("--edge_w", type=float, default=None); ap.add_argument("--tee_dz", type=float, default=None, help="K32: raise the teed ball by this many m (default 0 = unchanged). 0.020 puts the ball equator at the crown of the sim head box at address (golf.com/Golf Digest/Golf Monthly: equator ~ crown). NOTE the realism harness worker does not pass this flag yet"); ap.add_argument("--h_every", type=int, default=100_000, help="checkpoint interval (default 100k, unchanged)"); ap.add_argument("--tee_mode", type=str, default=None, choices=[None, "crown", "1.5in"], help="v4: '1.5in' = ball bottom 38.1 mm above ground (1.5 in tee, any head). K33: 'crown' = derive the tee offset from the active head geometry so the ball equator is level with the crown/top of the face at address (GOLF.com, Golf Digest, Golf Monthly); respects --face_h; overrides --tee_dz; default None = old tee (or --tee_dz if given). Derived value is printed"); ap.add_argument("--fast_env", action="store_true", help="STEP2(1): cached sole-contact forces, preallocated segment-log buffers, memoised reference q(t). Identical reward/info/obs traces (scripts/fast_env_equiv.py md5). Default off"); ap.add_argument("--env_v4", action="store_true", help="v4 re-baseline env: realistic head (--head realistic geometry) + lie 58.5 (Data Agent JSON) + swingweight compensation (butt weight from the shaft mass, total 300 g) + v4 address solve (env/models/v5_address_LH_*_v4.json, scripts/v4_address_solve.py). Default off = unchanged. See TRAINING_NOTES v4 env (re-baseline)"); ap.add_argument("--head", type=str, default=None, choices=[None, "box", "realistic"], help="K34: club head geometry. Default None = current 64 mm sim box (unchanged). realistic = sourced 460 cc head (Data Agent driver-head-refs bf9827b; data/driver_head_460cc_refs.json): 54x105 mm face, 62 mm crown, FP 20 mm, CG 40 mm back/31 mm high/35 mm from shaft, 200 g, Izz~4500, Iv~3000 g cm2; off-face (|dz|>27 or |dy|>52.5 mm) = miss; ball re-aligned to the new face centre at the same default tee height; see results/TRAINING_NOTES.md K34"); ap.add_argument("--plant_h_w", type=float, default=None, help="V9: harness-matched lead-foot plant penalty at impact on address starts (slip>2.5cm, turn>10deg, air>1 step; default off)"); ap.add_argument("--res_l2_w", type=float, default=None, help="V8: per-step penalty on mean squared residual action (default off)"); ap.add_argument("--launch_lo_w", type=float, default=None); ap.add_argument("--launch_lo", type=float, default=None); ap.add_argument("--sd_w", type=float, default=None, help="V8: |azimuth|>3 deg penalty on address starts (default off)"); ap.add_argument("--loc_noclip", action="store_true", default=None, help="V7: loc term with unclipped dz part, dy clipped separately (default off)"); ap.add_argument("--dz_lin_w", type=float, default=None, help="V7: unclipped |dz-dz_tgt| penalty per 10 mm (default off)"); ap.add_argument("--dz_tgt", type=float, default=None); ap.add_argument("--dy_lin_w", type=float, default=None, help="V7: |dy-dy_tgt| penalty per 15 mm, cap 10 (default off)"); ap.add_argument("--dy_tgt", type=float, default=None); ap.add_argument("--dz_gate", type=float, default=None, help="V6: strike/carry rewards x exp(-(dz/dz_gate)^2), 0 if |dz|>dz_zero (default off)"); ap.add_argument("--dz_zero", type=float, default=None); ap.add_argument("--rsi_full", type=float, default=None, help="V6: fraction of training episodes started at address (default None = 0.4/0.3/0.3 unchanged); rest split evenly top/mid-downswing"); ap.add_argument("--noise_ramp", type=float, default=None, help="V5: start-noise curriculum, init_qn/init_qvn scaled 0.2->1.0 over this fraction of training (default off)"); ap.add_argument("--miss_w", type=float, default=None, help="V5: penalty for an episode with no (on-face) contact (default off)"); ap.add_argument("--tee_anneal", type=float, default=None, help="K33c curriculum: start at the crown tee (from active head geometry) and anneal tee_dz linearly to 0 (old tee) by this fraction of training; default None = off"); ap.add_argument("--ball_dx", type=float, default=None, help="K32: move the ball along +x (target) by this many m; default 0 = unchanged"); ap.add_argument("--face_h", type=float, default=None, help="K31: real driver face height in m (e.g. 0.053). Contact with |dz| > face_h/2 from face centre = off-face miss (foul, ball disabled). Default None = current head box (64 mm), unchanged"); ap.add_argument("--edge_dz", type=float, default=None); ap.add_argument("--loc_dy", type=float, default=None); ap.add_argument("--loc_dz", type=float, default=None); ap.add_argument("--sep_span", type=float, default=None); ap.add_argument("--pel_t_lo", type=float, default=None); ap.add_argument("--pel_t_hi", type=float, default=None); ap.add_argument("--pel_dps", type=float, default=None); ap.add_argument("--lr", type=float, default=3e-4); ap.add_argument("--sel_k4", action="store_true"); ap.add_argument("--launch_hi", type=float, default=None); ap.add_argument("--dl_lo", type=float, default=None); ap.add_argument("--dl_hi", type=float, default=None); ap.add_argument("--aoa_lo", type=float, default=None); ap.add_argument("--spd_w", type=float, default=None); ap.add_argument("--fine_grf", action="store_true"); ap.add_argument("--smash_w", type=float, default=None); ap.add_argument("--spin_w", type=float, default=None); ap.add_argument("--spin_hi", type=float, default=None); ap.add_argument("--spin_scale", type=float, default=None); ap.add_argument("--desc_sel", action="store_true"); ap.add_argument("--launch_w", type=float, default=None); ap.add_argument("--desc_w", type=float, default=None); ap.add_argument("--dloft_w", type=float, default=None); ap.add_argument("--spin_lo_w", type=float, default=None); ap.add_argument("--snap_every", type=int, default=0); ap.add_argument("--ord2_w", type=float, default=None); ap.add_argument("--no_stop", action="store_true"); ap.add_argument("--T_step", type=float, default=5.0); ap.add_argument("--carry_min", type=float, default=0.0); ap.add_argument("--xf_hard", type=float, default=None); ap.add_argument("--grf_lo", type=float, default=None)
    ap.add_argument("--grf_w", type=float, default=None); ap.add_argument("--xf_cap_lo", type=float, default=None); ap.add_argument("--xf_cap_w", type=float, default=None); ap.add_argument("--track_floor", type=float, default=None)
    a = ap.parse_args()
    keys = {tuple(k.split("|")): v for k, v in json.load(open(a.keys)).items()} if a.keys and a.keys != "none" else None
    extra = dict(fast_env=(True if a.fast_env else None), stance_obs=a.stance_obs, heel8_w=a.heel8_w, hstart_frac=a.hstart_frac, smash3_w=a.smash3_w, smash3_lo=a.smash3_lo, smash3_hi=a.smash3_hi, nom_frac=a.nom_frac, lat_w=a.lat_w, lat_tgt=a.lat_tgt, turn_m_w=a.turn_m_w, turn_tgt=a.turn_tgt, miss0_w=a.miss0_w, plant_h_w=a.plant_h_w, res_l2_w=a.res_l2_w, launch_lo_w=a.launch_lo_w, launch_lo=a.launch_lo, sd_w=a.sd_w, loc_noclip=a.loc_noclip, dz_lin_w=a.dz_lin_w, dz_tgt=a.dz_tgt, dy_lin_w=a.dy_lin_w, dy_tgt=a.dy_tgt, dz_gate=a.dz_gate, dz_zero=a.dz_zero, rsi=((a.rsi_full, (1 - a.rsi_full) / 2, (1 - a.rsi_full) / 2) if a.rsi_full is not None else None), noise_ramp=a.noise_ramp, miss_w=a.miss_w, env_v4=(True if a.env_v4 else None), head=a.head, tee_anneal=a.tee_anneal, tee_mode=a.tee_mode, tee_dz=a.tee_dz, ball_dx=a.ball_dx, face_h=a.face_h, edge_w=a.edge_w, edge_dz=a.edge_dz, loc_w=a.loc_w, loc_dy=a.loc_dy, loc_dz=a.loc_dz, sep_lo=a.sep_lo, sep_span=a.sep_span, plant_term=a.plant_term, strike_w=a.strike_w, grfd_w=a.grfd_w, post_t=a.post_t, init_qn=a.init_qn, fr_rand=(True if a.fr_rand else None), ball_tol=a.ball_tol, fr_lo=a.fr_lo, spin_cap=a.spin_cap, spd_top=a.spd_top, shear_w=a.shear_w, shear_hi=a.shear_hi, slow_w=a.slow_w, slow_lo=a.slow_lo, dlh_w=a.dlh_w, fr_hi=a.fr_hi, init_qvn=a.init_qvn, tc_w=a.tc_w, smash2_w=a.smash2_w, ctr2_w=a.ctr2_w, xf_hard=a.xf_hard, grf_lo=a.grf_lo, grf_w=a.grf_w, xf_cap_lo=a.xf_cap_lo, xf_cap_w=a.xf_cap_w, ord2_w=a.ord2_w, launch_w=a.launch_w, launch_hi=a.launch_hi, dl_lo=a.dl_lo, dl_hi=a.dl_hi, aoa_lo=a.aoa_lo, spd_w=a.spd_w, pel_w=a.pel_w, pel_t_w=a.pel_t_w, pel_dps=a.pel_dps, pel_t_lo=a.pel_t_lo, sep_w=a.sep_w, early_w=a.early_w, aim_w=a.aim_w, foot_w=a.foot_w, ctr_w=a.ctr_w, res_mult=(json.loads(a.res_mult) if a.res_mult else None), ctrl_dt=a.ctrl_dt, pel_t_hi=a.pel_t_hi, smash_w=a.smash_w, spin_w=a.spin_w, spin_hi=a.spin_hi, spin_scale=a.spin_scale, fine_grf=(True if a.fine_grf else None), desc_w=a.desc_w, dloft_w=a.dloft_w, spin_lo_w=a.spin_lo_w, track_floor=a.track_floor)
    out = f"results/v5_runs/{a.tag}_s{a.seed}"; os.makedirs(out, exist_ok=True)
    assert all(hasattr(a, k) for k in ('plant_h_w', 'res_l2_w', 'noise_ramp', 'miss_w')) and 'noise_ramp' in extra and 'plant_h_w' in extra   # V9: guard (V5-V8 flags were parsed but never reached the env)
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
    cb = CurrJ(a.steps, out, 10**12, a.tag); cb.base = 0; cb.total_all = a.steps; cb.stop = False; cb.planar = False; cb.act_end, cb.prior_w, cb.rate_w = 1.0, 0.0, a.rate_w; cb.h_every = a.h_every; cb.h_last = step0
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
