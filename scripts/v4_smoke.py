"""v4 re-baseline smoke test (read-only; no training). For each checkpoint, 25 seeds (nominal 4000 + perturbed 7000-7023, strike_log.py randomisation):
v5 box (checkpoint's own args tee/face_h), v4 (--env_v4, default tee = equator at the 62 mm crown) and v4_1.5in (--tee_mode 1.5in), each as policy = deterministic PPO policy (closed loop) and ref = the
checkpoint's reference keys played open-loop (zero residual action). Usage: python scripts/v4_smoke.py OUT.csv CKPT [CKPT...]"""
import sys, json, csv, numpy as np; sys.path.insert(0, '.')
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
EX = 'sep_lo sep_span plant_term strike_w grfd_w post_t spin_cap spd_top shear_w shear_hi slow_w slow_lo dlh_w tc_w smash2_w ctr2_w xf_hard grf_lo grf_w xf_cap_lo xf_cap_w ord2_w launch_w launch_hi dl_lo dl_hi aoa_lo spd_w pel_w pel_t_w pel_dps pel_t_lo sep_w early_w aim_w foot_w ctr_w ctrl_dt pel_t_hi smash_w spin_w spin_hi spin_scale fine_grf desc_w dloft_w spin_lo_w track_floor'.split()
out = csv.writer(open(sys.argv[1], 'w')); out.writerow(['ckpt', 'env', 'mode', 'case', 'seed', 'contact', 'off_face', 'foul', 'dz_mm', 'dy_mm', 'spin_rpm', 'launch_deg', 'smash', 'club_mph', 'min_head_ball_mm'])
for ck in sys.argv[2:]:
    a = json.load(open(ck.rsplit('/', 1)[0] + '/args.json')); keys = {tuple(k.split('|')): v for k, v in json.load(open(a['keys'])).items()}
    for envv in ('v5box', 'v4', 'v4_1.5in'):
        def mk():
            e = JEnv(seed=999, keys=keys, res_scale=a['res_scale'], t_down=a['t_down']); e.configure(**{k: a.get(k) for k in EX}); e.configure(res_mult=json.loads(a['res_mult']) if a.get('res_mult') else None)
            if envv.startswith('v4'): e.configure(env_v4=True, tee_mode=('1.5in' if envv == 'v4_1.5in' else None))
            else: e.configure(tee_dz=a.get('tee_dz'), face_h=a.get('face_h'))
            e.rsi = (1.0, 0.0, 0.0); e.prior_w = 0.0; e.env.arm_dist = 0.6; e.hit_tol = 0.02; e.target_len = 1.15; e.target_tether = 0.0; e.speed_T = a['T0']; return e
        vn = VecNormalize.load(ck + '_vecnorm.pkl', DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False; m = PPO.load(ck, device='cpu'); e = vn.venv.envs[0]
        for mode in ('policy', 'ref'):
            for case, seed in [('nominal', 4000)] + [('perturbed', s) for s in range(7000, 7024)]:
                pert = case == 'perturbed'
                e.configure(fr_rand=pert, fr_lo=0.7, fr_hi=1.05, init_qn=0.026 if pert else 0.0, init_qvn=0.05 if pert else 0.0, ball_tol=0.01 if pert else 0.0); e.env.friction_rand = False
                e.env.m.geom_friction[e.env.floor, 0] = 1.0; o, _ = e.reset(seed=seed); done = False; info = {}
                while not done:
                    act = m.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0] if mode == 'policy' else np.zeros(e.action_space.shape)
                    o, r, te, tr, info = e.step(act); done = te or tr
                off = bool(getattr(e.env, 'off_face', False)); c = bool(info.get('contact')); fi = getattr(e.env, 'foul_info', {}) if off else {}
                dz = info.get('dz', fi.get('off_face_dz')); dy = info.get('dy', fi.get('off_face_dy'))
                out.writerow([ck.split('/')[-2], envv, mode, case, seed, c, off, bool(getattr(e.env, 'foul', False)), round(dz * 1e3, 2) if dz is not None else '', round(dy * 1e3, 2) if dy is not None else '',
                              round(info['spin_rpm']) if c else '', round(info['launch_deg'], 2) if c else '', round(info['smash'], 3) if c else '', round(info['club_speed_mph'], 2) if c else '', round(e.env.min_dist * 1e3, 1)])
