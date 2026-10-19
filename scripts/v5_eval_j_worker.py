"""Stage J worker for the Evaluator's realism harness (branch scott-e a4157b6+): same CLI/JSON as eval/_v5_worker.py but builds train.v5_train_j.JEnv (reference-guided residual env) and reads
res_scale/keys/t_down from the run's args.json. Usage: python scripts/v5_eval_j_worker.py <repo> <ckpt_base> <club_len> <seed0> <n> <out.json> [arm_dist=0.6] [gate_nx|off]"""
import sys, json, os
repo, ck, L, seed0, n, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
ARM = float(sys.argv[7]) if len(sys.argv) > 7 else 0.6
GATE = None if len(sys.argv) <= 8 or sys.argv[8].lower() in ('off', 'none', '') else float(sys.argv[8])
sys.path.insert(0, repo)
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
A = json.load(open(os.path.join(os.path.dirname(ck), "args.json")))
keys = {tuple(k.split("|")): v for k, v in json.load(open(os.path.join(repo, A["keys"]))).items()} if A.get("keys") and A["keys"] != "none" else None
def mk():
    e = JEnv(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(**{k: A.get(k) for k in ('xf_hard', 'grf_lo', 'grf_w', 'xf_cap_lo', 'xf_cap_w', 'track_floor', 'ord2_w', 'launch_w', 'desc_w', 'dloft_w', 'spin_lo_w', 'smash_w', 'spin_w', 'spin_hi', 'spin_scale', 'fine_grf', 'launch_hi', 'dl_lo', 'dl_hi', 'aoa_lo', 'spd_w', 'pel_w', 'pel_t_w', 'pel_dps', 'pel_t_lo', 'pel_t_hi', 'sep_w', 'ctr_w')}); e.rsi = (1.0, 0.0, 0.0); e.env.arm_dist = ARM; e.env.strike_gate_nx = GATE; e.target_len = L; e.target_tether = 0.0; e.env.friction_rand = False; e.track_w = 0.0; return e
vn = VecNormalize.load(ck + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False
model = PPO.load(ck, device="cpu"); te = mk(); e = te.env; e.log_segments = True
bw = float(sum(e.m.body_mass[i] for i in range(e.m.nbody) if e.m.body(i).name not in ("ball",)) * 9.81)
grf = []; orig = e._log_seg
def seg():
    orig(); fl, fr = e.foot_forces(); grf.append((fl, fr))
e._log_seg = seg
eps = []
for i in range(n):
    grf.clear(); o, _ = te.reset(seed=seed0 + i); done = False; info = {}
    while not done:
        a = model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, term, trunc, info = te.step(a); done = term or trunc
    L_ = e.log; tc = e.t_contact; t = np.array(L_["t"])
    imp = int(np.argmax(t >= tc)) if tc is not None and (t >= tc).any() else len(t) - 1
    eps.append(dict(t=L_["t"], pelvis_dps=L_["pelvis"], thorax_dps=L_["thorax"], arm_dps=L_["lead_arm"], club_dps=L_["club"], xfactor_deg=L_["xfactor_deg"], lead_share=L_["lead_share"],
                    grf=[list(map(float, g)) for g in grf], lead=e.lead, impact_idx=imp, contact=bool(e.contact), ep=info.get("ep"), foul=bool(info.get("foul", False)), seed=seed0 + i,
                    shot={k: info.get(k) for k in ("club_speed_mph", "ball_speed_mph", "launch_deg", "spin_rpm", "smash", "carry_m_noroll", "total_m_model", "lateral_carry_m")}))
json.dump(dict(strike_gate_nx=GATE, arm_dist=ARM, env_class="JEnv", bw_N=bw, dt=0.005, club_len=L, eps=eps), open(out, "w"), default=float)
