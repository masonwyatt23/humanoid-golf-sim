"""Stage J worker for the Evaluator's realism harness (branch scott-e d527e54+): same CLI/JSON as eval/_v5_worker.py but builds train.v5_train_j.JEnv.
Logs lead_foot (sole centre + ends) and shot_extra (azimuth/backspin/sidespin) so mine/start_direction and mine/lead_foot_plant gate; declares dt = sim_dt * seg_every and lets the harness MEASURE the interval (dt fix bbb9a7e).
Usage: python scripts/v5_eval_j_worker.py <repo> <ckpt_base> <club_len> <seed0> <n> <out.json> [arm_dist=0.6] [gate_nx|off] [seg1]"""
import sys, json, os
repo, ck, L, seed0, n, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
ARM = float(sys.argv[7]) if len(sys.argv) > 7 else 0.6
GATE = None if len(sys.argv) <= 8 or sys.argv[8].lower() in ('off', 'none', '') else float(sys.argv[8])
SEG1 = any(a.lower() == "seg1" for a in sys.argv[9:])
sys.path.insert(0, repo)
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
A = json.load(open(os.path.join(os.path.dirname(ck), "args.json")))
keys = {tuple(k.split("|")): v for k, v in json.load(open(os.path.join(repo, A["keys"]))).items()} if A.get("keys") and A["keys"] != "none" else None
W = ('xf_hard','grf_lo','grf_w','xf_cap_lo','xf_cap_w','track_floor','ord2_w','launch_w','desc_w','dloft_w','spin_lo_w','smash_w','spin_w','spin_hi','spin_scale','fine_grf','launch_hi','dl_lo','dl_hi','aoa_lo','spd_w','ctrl_dt','early_w','aim_w','foot_w','plant_term','strike_w','tc_w','smash2_w','ctr2_w','pel_w','pel_t_w','pel_dps','pel_t_lo','pel_t_hi','sep_w','ctr_w')
def mk():
    e = JEnv(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(res_mult=(json.loads(A['res_mult']) if A.get('res_mult') else None), **{k: A.get(k) for k in W}); e.rsi = (1.0, 0.0, 0.0); e.env.arm_dist = ARM; e.env.strike_gate_nx = GATE; e.target_len = L; e.target_tether = 0.0; e.env.friction_rand = False; e.track_w = 0.0; return e   # eval: full swing from address only (restored from pre-dc9052d)
vn = VecNormalize.load(ck + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False
model = PPO.load(ck, device="cpu"); te = mk(); e = te.env; e.log_segments = True; e.detail_info = True
bw = float(sum(e.m.body_mass[i] for i in range(e.m.nbody) if e.m.body(i).name not in ("ball",)) * 9.81)
grf = []; sub = []; foot = []; orig = e._log_seg
def seg():
    orig(); fl, fr = e.foot_forces(); grf.append((fl, fr)); sub.append(int(e.sub_count))
    sid = e.m.site(f"{e.lead}_sole_site").id; P = e.d.site_xpos[sid]; R = e.d.site_xmat[sid].reshape(3, 3); hx = float(e.m.site_size[sid][0])
    foot.append([float(P[0]), float(P[1]), float(P[2]), float((P - hx * R[:, 0])[2]), float((P + hx * R[:, 0])[2]), float(np.arctan2(R[1, 0], R[0, 0]))])
e._log_seg = seg
eps = []; SEG_DEF = int(e.seg_every)
for i in range(n):
    grf.clear(); sub.clear(); foot.clear(); e.seg_every = SEG_DEF; o, _ = te.reset(seed=seed0 + i); e.seg_every = SEG_DEF; done = False; info = {}
    if SEG1: e.seg_every = 1
    while not done:
        a = model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, term, trunc, info = te.step(a); done = term or trunc
    L_ = e.log; tc = e.t_contact; t = np.array(L_["t"])
    imp = int(np.argmax(t >= tc)) if tc is not None and (t >= tc).any() else len(t) - 1
    shx = {}
    if e.contact and getattr(e, "shot", None):
        _s = e.shot; _r = _s["shot"]; shx = dict(azimuth_deg=_s.get("azimuth_deg"), backspin_rpm=_s.get("backspin_rpm"), sidespin_rpm=_s.get("sidespin_rpm"), env_carry_m=_r.carry_m, env_total_m=_r.total_m, env_descent_deg=_r.descent_deg, env_lateral_m=_r.lateral_carry_m)
    eps.append(dict(shot_extra=shx, t=L_["t"], pelvis_dps=L_["pelvis"], thorax_dps=L_["thorax"], arm_dps=L_["lead_arm"], club_dps=L_["club"], xfactor_deg=L_["xfactor_deg"], lead_share=L_["lead_share"],
                    grf=[list(map(float, g)) for g in grf], lead_foot=[list(f_) for f_ in foot], t_top=None, lead=e.lead, impact_idx=imp, contact=bool(e.contact), ep=info.get("ep"), foul=bool(info.get("foul", False)), seed=seed0 + i, t_contact=tc, sub=list(sub), seg_every=int(e.seg_every), seg_every_default=SEG_DEF,
                    shot={k: info.get(k) for k in ("club_speed_mph", "ball_speed_mph", "launch_deg", "spin_rpm", "smash", "carry_m_noroll", "total_m_model", "lateral_carry_m")}))
json.dump(dict(strike_gate_nx=GATE, arm_dist=ARM, env_class="JEnv", bw_N=bw, dt=float(e.dt) * SEG_DEF, dt_note="declared = sim dt x default seg_every (4 ms at dt 0.002); the harness MEASURES the interval from t (dt fix 2026-10-19)", club_len=L, eps=eps), open(out, "w"), default=float)
