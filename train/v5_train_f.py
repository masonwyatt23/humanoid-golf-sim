"""Stage F (warm start E s0 ckpt_900000: det contact 1.0, 58.9 mph, carry 0 because a hammer-like downward chop with the face normal pointing UP/back (n=[.22,.55,.8], v=[11,-13,-20], v.n<0)). Adds dense FACE/PATH shaping inside 0.8 m of tee after arming: 0.03*(n_x - |n_y|) face squared toward target, 0.01*clip(v.n,-20,30) signed (so negative v.n is penalised), saves best ckpt by det contact*carry (best_det.zip). Stage E docstring follows.
Stage E (warm start B3 s0 ckpt_1000000/1200000: det contact 1.0 @ ~63 mph at tether 0, arm 0.6, but carry 0 = backward/closed strike). Differences vs D: base policy already swings fast (so keep contact base +1.0, forward bonus 6*fwd on top, backward strike only mildly negative -0.5), additive speed bonus with gentle gate (lo=hi-40, hi 50->70->85), carry+launch-window bonus, small UNGATED order/xfactor prior (x0.5 floor on flail factor), action-rate 0.02, lead-foot >2BW penalty + terminate at 3.5 BW (stomp) after 400 steps of arming.
(stage D docstring follows)
Stage D (own policy, stock torque, 1.15 m club, public-only, arm_dist 0.6). Warm start from B4 s1 ckpt_3000000 (tether-free, contact 1.0, ~37 mph, but BACKWARD strike, carry 0).
Changes vs Stage C (whose multiplicative speed gate removed the dense signal and let instability dominate):
 1. Contact reward is ADDITIVE: (-1.5 + 6.5*fwd)*(0.3+0.7q), fwd = clip(v.n/|v|,0,1)*[v_x>0] (head velocity along the face normal toward target, +x) at contact, so a backward strike (diagnosed in D v1: head flicks up 0.6 m to arm, then drops back onto the ball moving -x) is ~ -1.5 (about a miss's -2), a forward one ~ +5.
 2. (v3: backward strike -3+8*fwd, worse than a miss; arm_back gate)  Speed bonus (additive, needs fwd): 4*clip((mph-lo)/(hi-lo),0,1)*fwd*valid*flail_ff, hi rises 30->60->85 mph (p 0->.3->.7), lo=hi-25. Carry bonus additive: 8*min(carry/100,1)*launch_window + 2*min(carry/30,1), lateral penalty.
 3. Dense forward-strike shaping after the arm gate (head within 1 m of tee, before contact): 0.004*forward head speed + 0.01*(v.face_normal) when within 0.6 m and v_x>0.
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

ARM_BACK = 0.0   # E: B3 s0 base arms by distance only (no arm_back); was 0.35 in D v3
ARM_BACK_UNUSED = 0.35   # D v3: v2 diagnosis - policy 'backswings' toward +x (target side), arms, and hits with the back of the head moving -x; arming now requires head 0.35 m behind the tee (-x)

class EEnv(BEnv):
    def __init__(self, dt=0.002, seed=0):
        super().__init__(dt=dt, seed=seed)
        e = self.env; e.log_segments = True; e.arm_back = ARM_BACK; self.back_max = 0.0
        self.bw = float(np.sum(e.m.body_mass)) * 9.81; self.z0 = None; self.gpeak = 0.0; self.lgpeak = 0.0; self.prev_a = None
    def reset(self, **kw):
        o = super().reset(**kw); self.z0 = float(self.env.d.qpos[2]); self.gpeak = 0.0; self.lgpeak = 0.0; self.prev_a = None; self.back_max = 0.0; return o
    def step(self, a):
        e = self.env; was = e.contact; p = self.progress; a = np.clip(np.asarray(a, float), -1, 1)
        da = 0.0 if self.prev_a is None else float(np.mean((a - self.prev_a) ** 2)); self.prev_a = a.copy()
        o, _, term, trunc, info = e.step(a)
        hs = e.head_site; v = e._vel_site(hs)[3:]
        unstable = (not np.all(np.isfinite(v))) or float(np.linalg.norm(v)) > 62.0 or float(np.max(np.abs(e.d.qvel))) > 60.0
        if unstable: v = np.zeros(3); term = True
        r = -0.02 * da
        rel = e.tee - e.d.site_xpos[hs]; dist = float(np.linalg.norm(rel))
        if ARM_BACK > 0 and not e.armed and not e.contact:
            bk = max(0.0, float(e.tee[0] - e.d.site_xpos[hs][0])); bk = min(bk, 0.5); r += 0.5 * max(0.0, bk - self.back_max); self.back_max = max(self.back_max, bk)   # dense backswing-direction shaping
        if e.armed and not e.contact and dist < 1.0:
            nrm = e.d.geom_xmat[e.head_geom].reshape(3, 3)[:, 0]   # face normal (toward the ball)
            if dist < 0.8: r += 0.03 * (float(nrm[0]) - abs(float(nrm[1]))) + 0.01 * float(np.clip(np.dot(v, nrm), -20.0, 30.0)) * (1.0 if dist < 0.6 else 0.0)
            r += 0.004 * max(0.0, float(v[0])) + (0.01 * max(0.0, float(np.dot(v, nrm))) if dist < 0.6 and v[0] > 0 else 0.0)
        if e.armed and not self.was_armed and not unstable: r += 1.0; self.was_armed = True
        fl, fr = e.foot_forces(); lead = (fl if e.lead == "left" else fr) / self.bw; self.lgpeak = max(self.lgpeak, lead); self.gpeak = max(self.gpeak, (fl + fr) / self.bw)
        r -= 0.03 * min(max(lead - 2.0, 0.0), 4.0)
        if lead > 3.5 and not e.contact and e.armed: r -= 3.0; term = True   # stomp termination
        if e.d.qpos[2] > 0.8 * self.z0 and float(e.d.xmat[e.pel].reshape(3, 3)[2, 2]) > 0.85: r += 0.01
        L = e.log; peaks = None; ff, ex = 1.0, 0.0; pr_raw = {}; fwd = None
        if len(L["t"]) > 3:
            pk = {k: float(np.max(L[k])) for k in ("pelvis", "thorax", "lead_arm", "club")}; ff, ex = flail_factor(pk); peaks = pk
        hi = float(np.interp(p, [0.0, 0.3, 0.7, 1.0], [50.0, 70.0, 85.0, 85.0]))
        if e.contact and not was and not unstable:
            q = max(0.0, 1 - np.hypot(info["dy"], info["dz"]) / self.hit_tol); pv = e.prev_v
            nrm = np.asarray(e.ball_hit_info["face_normal"]); fwd = float(np.clip(np.dot(pv, nrm) / max(float(np.linalg.norm(pv)), 1e-6), 0.0, 1.0)) * (1.0 if pv[0] > 0 else 0.0); self.fwd = fwd
            mph = info["club_speed_mph"]; valid = float(np.clip(info["ball_speed_mph"] / max(1.2 * mph, 1e-6), 0.0, 1.0))
            lw = launch_win(info["launch_deg"]); qq = 0.3 + 0.7 * q
            r += (1.0 - 1.5 * (1.0 - fwd) + 6.0 * fwd) * qq
            r += 4.0 * float(np.clip((mph - (hi - 40.0)) / 40.0, 0.0, 1.0)) * fwd * valid * ff
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
                    pr = min((1.5 * pr_raw["xf"] + 1.0 * pr_raw["seq"] + 1.0 * pr_raw["lag"]) * max(ff, 0.5), 3.0)
                except Exception: pr = 0.0
            r += pr
            info["ep"] = dict(contact=bool(e.contact) and not unstable, fell=bool(info["fell"]), unstable=bool(unstable), club_mph=info.get("club_speed_mph", 0.0), carry=info.get("carry_m_noroll", 0.0),
                              lat=info.get("lateral_carry_m", 0.0), launch=info.get("launch_deg", 0.0), peak_head_mph=self.peak / 0.44704, club_len=e.club_len, tether=e.tether_strength, prior=pr,
                              fwd=getattr(self, "fwd", 0.0) if e.contact else 0.0, lead_grf_peak_bw=self.lgpeak, flail_ratio=ex, **pr_raw)
        return o, r, term, trunc, info

class CurrE(CurrC):
    stop = False
    def _on_step(self):
        ok = super()._on_step()
        return ok and not self.stop
    def det_eval(self, n=12):
        vn = self.training_env; row = dict(step=self.num_timesteps, hi_gate=self.cur[3])
        for ad in (0.6, 0.0):
            env = getattr(self, "env_cls", EEnv)(seed=999); env.env.arm_dist = ad; env.hit_tol = self.cur[2]; env.target_len = 1.15; env.target_tether = 0.0; env.env.friction_rand = False
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
        sc = a6["contact"] * a6["carry_med"]
        if sc > getattr(self, "best_sc", 0.0):
            self.best_sc = sc; self.model.save(os.path.join(self.out, "best_det")); self.training_env.save(os.path.join(self.out, "best_det_vecnorm.pkl")); open(os.path.join(self.out, "best_det.json"), "w").write(json.dumps(row))
        if a6["contact"] >= 0.9 and a6["carry_med"] > 30.0 and self.num_timesteps >= 200_000:
            self.stop = True; open(os.path.join(self.out, "STOP_REACHED"), "w").write(json.dumps(row))

def make(rank, seed, dt):
    def f(): return EEnv(dt=dt, seed=seed * 100 + rank + 41)
    return f

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--steps", type=int, default=3_000_000)
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--dt", type=float, default=0.002); ap.add_argument("--tag", default="stageF")
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
    cb = CurrE(a.steps, out, a.ck_every, a.tag); cb.base = 0; cb.total_all = a.steps; cb.scratch_tether = True; cb.last_ck = step0
    cb.t0_, cb.t_end, cb.ls0, cb.ls1, cb.std_end, cb.ent0 = a.tether0, a.tether_end, a.log_std, a.log_std_end, a.std_end, a.ent
    model.learn(a.steps - (model.num_timesteps if ck else 0), callback=cb, reset_num_timesteps=not ck)
    model.save(os.path.join(out, "final")); venv.save(os.path.join(out, "final_vecnorm.pkl"))
