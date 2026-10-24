"""Per-swing strike location log (read-only; vendored golfphys unchanged). For each checkpoint: nominal (friction 1.0, no noise) + 24 perturbed seeds 7000-7023
with the TRAINER env's randomisation (friction U(0.7,1.05), joint pos noise 0.026 rad ~1.5 deg, joint vel 0.05 rad/s, ball +-1 cm). NOTE: approximates, not identical to, the
Evaluator's v3c gate perturbation. Logs y_high_m/x_toe_m returned by env/v5_shot.shot_from_contact, plus spin/launch/club mph."""
import sys, json, csv, numpy as np; sys.path.insert(0, '.')
import env.v5_golf_env as G
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
EX = 'sep_lo sep_span plant_term strike_w grfd_w post_t spin_cap spd_top shear_w shear_hi slow_w slow_lo dlh_w tc_w smash2_w ctr2_w xf_hard grf_lo grf_w xf_cap_lo xf_cap_w ord2_w launch_w launch_hi dl_lo dl_hi aoa_lo spd_w pel_w pel_t_w pel_dps pel_t_lo sep_w early_w aim_w foot_w ctr_w ctrl_dt pel_t_hi smash_w spin_w spin_hi spin_scale fine_grf desc_w dloft_w spin_lo_w track_floor'.split()
last = {}; orig = G.shot_from_contact
def hook(*ar, **kw): r = orig(*ar, **kw); last['r'] = r; return r
G.shot_from_contact = hook
out = csv.writer(open(sys.argv[1], 'w')); out.writerow(['ckpt', 'case', 'seed', 'floor_mu', 'contact', 'club_mph', 'y_high_mm', 'x_toe_mm', 'backspin_rpm', 'launch_deg', 'total_over_carry'])
for ck in sys.argv[2:]:
    a = json.load(open(ck.rsplit('/', 1)[0] + '/args.json')); keys = {tuple(k.split('|')): v for k, v in json.load(open(a['keys'])).items()}
    def mk():
        e = JEnv(seed=999, keys=keys, res_scale=a['res_scale'], t_down=a['t_down']); e.configure(**{k: a.get(k) for k in EX}); e.configure(res_mult=json.loads(a['res_mult']) if a.get('res_mult') else None)
        e.configure(face_h=float(__import__('os').environ['FACE_H']) if __import__('os').environ.get('FACE_H') else None); e.rsi = (1.0, 0.0, 0.0); e.prior_w = 0.0; e.env.arm_dist = 0.6; e.hit_tol = 0.02; e.target_len = 1.15; e.target_tether = 0.0; e.speed_T = a['T0']; return e
    vn = VecNormalize.load(ck + '_vecnorm.pkl', DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False; m = PPO.load(ck, device='cpu'); e = vn.venv.envs[0]
    name = ck.split('/')[-2]
    for case, seed in [('nominal', 4000)] + [('perturbed', s) for s in range(7000, 7024)]:
        pert = case == 'perturbed'
        e.configure(fr_rand=pert, fr_lo=0.7, fr_hi=1.05, init_qn=0.026 if pert else 0.0, init_qvn=0.05 if pert else 0.0, ball_tol=0.01 if pert else 0.0); e.env.friction_rand = False
        last.clear(); e.env.m.geom_friction[e.env.floor, 0] = 1.0; o, _ = e.reset(seed=seed); done = False
        mu = None
        try: mu = float(e.env.m.geom_friction[e.env.floor, 0])
        except Exception: pass
        while not done:
            act, _s = m.predict(vn.normalize_obs(o[None]), deterministic=True); o, r, te, tr, info = e.step(act[0]); done = te or tr
        ep = info.get('ep', {}); r = last.get('r') if not getattr(e.env, 'off_face', False) else None
        out.writerow([name, case, seed, mu, bool(r), round(ep.get('club_mph', 0), 2), round(r['y_high_m'] * 1e3, 2) if r else '', round(r['x_toe_m'] * 1e3, 2) if r else '', round(r['backspin_rpm']) if r else '', round(r['launch_deg'], 2) if r else '', round(ep.get('tc', 0) or 0, 3)])
