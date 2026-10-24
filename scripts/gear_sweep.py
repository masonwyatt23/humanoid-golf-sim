"""Read-only check: does golfphys (as vendored, unchanged) change spin/launch with face strike location? Captures K28b 400k nominal contact
(club vel, face normal, dy/dz) from deterministic episodes, then re-calls env.v5_shot.shot_from_contact at swept offsets. No model changes."""
import sys, json, numpy as np; sys.path.insert(0, '.')
import env.v5_golf_env as G, env.v5_shot as S
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
ck = sys.argv[1]; a = json.load(open(ck.rsplit('/', 1)[0] + '/args.json'))
cap = []; orig = G.shot_from_contact
def hook(*ar, **kw): cap.append((ar, kw)); return orig(*ar, **kw)
G.shot_from_contact = hook
def mk():
    e = JEnv(seed=999, keys={tuple(k.split('|')): v for k, v in json.load(open(a['keys'])).items()}, res_scale=a['res_scale'], t_down=a['t_down']); EX='sep_lo sep_span plant_term strike_w grfd_w post_t ball_tol spin_cap spd_top shear_w shear_hi slow_w slow_lo dlh_w tc_w smash2_w ctr2_w xf_hard grf_lo grf_w xf_cap_lo xf_cap_w ord2_w launch_w launch_hi dl_lo dl_hi aoa_lo spd_w pel_w pel_t_w pel_dps pel_t_lo sep_w early_w aim_w foot_w ctr_w ctrl_dt pel_t_hi smash_w spin_w spin_hi spin_scale fine_grf desc_w dloft_w spin_lo_w track_floor'.split(); e.configure(**{k: a.get(k) for k in EX}); e.configure(res_mult=json.loads(a['res_mult']) if a.get('res_mult') else None); e.rsi = (1.0, 0.0, 0.0); e.prior_w = 0.0; e.env.arm_dist = 0.6; e.hit_tol = 0.02; e.target_len = 1.15; e.target_tether = 0.0; e.env.friction_rand = False; e.speed_T = a['T0']; return e
vn = VecNormalize.load(ck + '_vecnorm.pkl', DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False
m = PPO.load(ck, device='cpu'); e = vn.venv.envs[0]
for i in range(3):
    o, _ = e.reset(seed=4000 + i); done = False
    while not done:
        act, _s = m.predict(vn.normalize_obs(o[None]), deterministic=True); o, r, te, tr, info = e.step(act[0]); done = te or tr
print('capture mph', [round(float(np.linalg.norm(c[0][0]))/0.44704,1) for c in cap], 'ep', {k: info['ep'].get(k) for k in ('club_mph','spin','launch','contact')}); ar, kw = max(cap, key=lambda c: np.linalg.norm(c[0][0])); cv, n, dy0, dz0 = ar[:4]
print('nominal contact dy(toe)=%.1f mm dz(high)=%.1f mm club %.1f mph' % (dy0 * 1e3, dz0 * 1e3, np.linalg.norm(cv) / 0.44704), 'captures', len(cap))
print('dy_mm dz_mm backspin side launch ball_mph carry_m total/carry')
for dy in (-0.01, 0.0, 0.01, 0.02):
    for dz in (-0.005, 0.0, 0.005, 0.01, 0.015):
        r = S.shot_from_contact(cv, n, dy, dz, **kw); s = r['shot']
        print(int(dy * 1e3), int(dz * 1e3), round(r['backspin_rpm']), round(r['sidespin_rpm']), round(r['launch_deg'], 1), round(r['ball_speed'] / 0.44704, 1), round(s.carry_m, 1), round(getattr(s, 'total_m', 0) / max(s.carry_m, 1e-6), 3))
