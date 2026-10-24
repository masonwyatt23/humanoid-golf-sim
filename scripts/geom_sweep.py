"""K32 diagnosis (read-only): nominal closed-loop swing of a checkpoint with geometry tweaks: tee height (env.tee_dz), ball fore/aft (env.ball_dx), and
reference impact keys (knee|lead|imp, il|* shaft-lean). Reports strike dz/dy (mm), backspin, launch, smash, club mph, AoA, dynamic loft. golfphys unchanged."""
import sys, json, numpy as np; sys.path.insert(0, '.')
import env.v5_golf_env as G
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
EX = 'sep_lo sep_span plant_term strike_w grfd_w post_t spin_cap spd_top shear_w shear_hi slow_w slow_lo dlh_w tc_w smash2_w ctr2_w xf_hard grf_lo grf_w xf_cap_lo xf_cap_w ord2_w launch_w launch_hi dl_lo dl_hi aoa_lo spd_w pel_w pel_t_w pel_dps pel_t_lo sep_w early_w aim_w foot_w ctr_w ctrl_dt pel_t_hi smash_w spin_w spin_hi spin_scale fine_grf desc_w dloft_w spin_lo_w track_floor'.split()
ck = sys.argv[1]; a = json.load(open(ck.rsplit('/', 1)[0] + '/args.json')); K0 = {tuple(k.split('|')): v for k, v in json.load(open(a['keys'])).items()}
last = {}; orig = G.shot_from_contact
def hook(*ar, **kw): r = orig(*ar, **kw); last['r'] = r; return r
G.shot_from_contact = hook
def run(tee_dz=0.0, ball_dx=0.0, kd=None):
    keys = dict(K0); keys.update(kd or {})
    e = JEnv(seed=999, keys=keys, res_scale=a['res_scale'], t_down=a['t_down']); e.configure(**{k: a.get(k) for k in EX}); e.configure(res_mult=json.loads(a['res_mult']) if a.get('res_mult') else None)
    e.rsi = (1.0, 0.0, 0.0); e.prior_w = 0.0; e.env.arm_dist = 0.6; e.hit_tol = 0.02; e.target_len = 1.15; e.target_tether = 0.0; e.speed_T = a['T0']
    e.tee_dz = tee_dz; e.ball_dx = ball_dx
    vn = VecNormalize.load(ck + '_vecnorm.pkl', DummyVecEnv([lambda: e])); vn.training = False; m = PPO.load(ck, device='cpu')
    last.clear(); o, _ = e.reset(seed=4000); done = False
    while not done:
        act, _s = m.predict(vn.normalize_obs(o[None]), deterministic=True); o, r, te, tr, info = e.step(act[0]); done = te or tr
    ep = info.get('ep', {}); r = last.get('r')
    if not r: return dict(contact=False)
    return dict(dz=round(r['y_high_m'] * 1e3, 1), dy=round(r['x_toe_m'] * 1e3, 1), spin=round(r['backspin_rpm']), launch=round(r['launch_deg'], 1), smash=round(r['smash'], 3), mph=round(ep.get('club_mph', 0), 1), aoa=round(ep.get('aoa', 0) or 0, 1), dloft=round(ep.get('dynamic_loft', ep.get('dloft', 0)) or 0, 1), carry=round(ep.get('carry', 0), 1))
print('base', run())
if len(sys.argv) > 2: print('K32 keys (knee -0.45, il elbow 0) + tee', run(kd={('knee','lead','imp'): -0.45, ('il','right_elbow_joint'): 0.0})); print('combo +tee 0.020', run(tee_dz=0.02, kd={('knee','lead','imp'): -0.45, ('il','right_elbow_joint'): 0.0})); sys.exit()
for t in (0.005, 0.010, 0.016, 0.020): print('tee_dz', t, run(tee_dz=t))
for x in (-0.03, 0.03): print('ball_dx', x, run(ball_dx=x))
kn = K0.get(('knee', 'lead', 'imp'))
if kn is not None:
    for v in (-0.67, -0.45): print('knee|lead|imp', v, run(kd={('knee', 'lead', 'imp'): v}))
for j in ('il|right_elbow_joint', 'il|right_wrist_yaw_joint'):
    kk = tuple(j.split('|'))
    if kk in K0: print(j, '-> 0', run(kd={kk: 0.0}))
