"""V18 SPREAD DIAG + STATE (env STATE_OUT=json): also records body state at takeaway (t=T_WAIT) and at the top: lead/trail sole xy, pelvis xyz, leg joint error vs reference, ball-minus-head. LOCAL.
V18 SPREAD DIAG (from face_log_h.py, which is unchanged): same rollouts, plus per-episode perturbation components (ball offset x/y vs nominal, joint qpos offsets per actuated joint, qvel offsets, floor mu). Seeds via env SEEDS=a-b (default 7000-7023 = GATING). LOCAL. Original: LOCAL face/path log, HARNESS-NOISE mode (V18; from face_log.py): perturbed starts mimic the Evaluator v4 worker (_j_worker_gp_v3.py): env reset(seed), ball_tol 0.01 via env, floor mu U(0.7,1.05) from rng(seed+0xF41C), joint noise radians(1.5)*U(-1,1) and vel 0.05*U(-1,1) from rng(seed+0x5EED) on actuated joints. Outputs face_world (= -face_yaw, LH env). Original: LOCAL face/path log (V17, from turn_log.py): adds impact face_yaw_deg, club_path_deg, azimuth_deg, strike dy at contact. Original: LOCAL turn log (V13, not the harness): same rollouts as scripts/strike_log.py (nominal + 24 trainer-randomised starts, seeds 7000-7023), plus per-episode lead-foot
turn (max |yaw| vs address) and slip (max xy vs address) from ref t_dstart to impact, contact, and strike dy/dz. strike_log.py itself is left byte-identical (baseline check).
Original note: Per-swing strike location log (read-only; vendored golfphys unchanged). For each checkpoint: nominal (friction 1.0, no noise) + 24 perturbed seeds 7000-7023
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
out = csv.writer(open(sys.argv[1], 'w')); out.writerow(['ckpt', 'case', 'seed', 'floor_mu', 'contact', 'club_mph', 'y_high_mm', 'x_toe_mm', 'backspin_rpm', 'launch_deg', 'total_over_carry', 'turn_deg', 'slip_cm', 'face_yaw', 'club_path', 'azimuth', 'dy_mm', 'spin_axis', 'ball_dx_mm', 'ball_dy_mm', 'dq_json', 'dqd_json'])
SA = []
for ck in sys.argv[2:]:
    a = json.load(open(ck.rsplit('/', 1)[0] + '/args.json')); keys = {tuple(k.split('|')): v for k, v in json.load(open(a['keys'])).items()}
    def mk():
        e = JEnv(seed=999, keys=keys, res_scale=a['res_scale'], t_down=a['t_down']); e.configure(**{k: a.get(k) for k in EX}); e.configure(res_mult=json.loads(a['res_mult']) if a.get('res_mult') else None)
        e.configure(env_v4=a.get('env_v4')); e.configure(head=__import__('os').environ.get('HEAD'), tee_mode=__import__('os').environ.get('TEE_MODE')); e.configure(tee_dz=(float(__import__('os').environ['TEE_DZ']) if __import__('os').environ.get('TEE_DZ') else a.get('tee_dz')), face_h=float(__import__('os').environ['FACE_H']) if __import__('os').environ.get('FACE_H') else None); e.rsi = (1.0, 0.0, 0.0); e.prior_w = 0.0; e.env.arm_dist = 0.6; e.hit_tol = 0.02; e.target_len = 1.15; e.target_tether = 0.0; e.speed_T = a['T0']; return e
    vn = VecNormalize.load(ck + '_vecnorm.pkl', DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False; m = PPO.load(ck, device='cpu'); e = vn.venv.envs[0]
    e.rsi = (1.0, 0.0, 0.0); name = ck.split('/')[-2]
    for case, seed in [('nominal', 0)] + [('perturbed', s) for s in range(int(__import__('os').environ.get('SEEDS','7000-7023').split('-')[0]), int(__import__('os').environ.get('SEEDS','7000-7023').split('-')[1]) + 1)]:
        pert = case == 'perturbed'
        e.configure(fr_rand=False, init_qn=0.0, init_qvn=0.0, ball_tol=0.01 if pert else 0.0); e.env.friction_rand = False
        last.clear(); e.env.m.geom_friction[e.env.floor, 0] = 1.0; o, _ = e.reset(seed=seed); E0 = e.env; b_ = E0.d.qpos[E0.ball_q:E0.ball_q + 2].copy()
        if not pert: BN = b_.copy()
        DQ = np.zeros(len(E0.qa)); DQD = np.zeros(len(E0.da))
        if pert:
            import mujoco; E_ = e.env; E_.m.geom_friction[E_.floor, 0] = np.random.default_rng(seed + 0xF41C).uniform(0.7, 1.05)
            rg = np.random.default_rng(seed + 0x5EED); nq = len(E_.qa); DQ = np.radians(1.5) * rg.uniform(-1, 1, nq); DQD = 0.05 * rg.uniform(-1, 1, nq); E_.d.qpos[E_.qa] += DQ; E_.d.qvel[E_.da] += DQD
            mujoco.mj_forward(E_.m, E_.d); o = e._xobs(E_._obs()); done = False
        done = False; mu = None
        try: mu = float(e.env.m.geom_friction[e.env.floor, 0])
        except Exception: pass
        tn = sl = 0.0; e.env.detail_info = True; FI = {}; ST = {}
        while not done:
            act, _s = m.predict(vn.normalize_obs(o[None]), deterministic=True); o, r, te, tr, info = e.step(act[0]); done = te or tr
            E1 = e.env; t1 = E1.d.time
            for tag_, tt_ in (('tw', 0.10), ('top', e.ref.t_top)):
                if tag_ not in ST and t1 >= tt_:
                    sp = lambda n_: E1.d.site_xpos[E1.m.site(f"{n_}_sole_site").id][:2].tolist()
                    ST[tag_] = dict(lead=sp(E1.lead), trail=sp('left' if E1.lead == 'right' else 'right'), pel=E1.d.xpos[E1.pel].tolist(), legerr=(E1.d.qpos[E1.qa] - e.ref.q(t1))[:12].tolist(), bh=(E1.d.qpos[E1.ball_q:E1.ball_q + 3] - E1.d.site_xpos[E1.head_site]).tolist())
            if 'face_yaw_deg' in info and not FI: FI.update(fy=info['face_yaw_deg'], cp=info['club_path_deg'], az=info.get('azimuth_deg'), dy=info.get('dy'), ax=info.get('spin_axis_deg'))
            if e._addr is not None and e.env.d.time >= e.ref.t_dstart and not e.env.contact:
                x_, y_, _, _, yw_ = e._sole(); x0_, y0_, _, _, yw0_ = e._addr; tn = max(tn, abs(float((np.degrees(yw_ - yw0_) + 180.0) % 360.0 - 180.0))); sl = max(sl, float(np.hypot(x_ - x0_, y_ - y0_)))
        ep = info.get('ep', {}); r = last.get('r') if not getattr(e.env, 'off_face', False) else None
        out.writerow([name, case, seed, mu, bool(r), round(ep.get('club_mph', 0), 2), round(r['y_high_m'] * 1e3, 2) if r else '', round(r['x_toe_m'] * 1e3, 2) if r else '', round(r['backspin_rpm']) if r else '', round(r['launch_deg'], 2) if r else '', round(ep.get('tc', 0) or 0, 3), round(tn, 2), round(100 * sl, 2)] + [(round(float(FI[k]) * (1e3 if k == 'dy' else 1), 2) if FI.get(k) is not None else '') for k in ('fy', 'cp', 'az', 'dy', 'ax')] + [round(1e3 * (b_[0] - BN[0]), 3), round(1e3 * (b_[1] - BN[1]), 3), json.dumps([round(float(x), 5) for x in DQ]), json.dumps([round(float(x), 5) for x in DQD])]); SA.append(dict(seed=seed, case=case, dy=FI.get('dy'), contact=bool(r), st=ST))
json.dump(SA, open(__import__('os').environ['STATE_OUT'], 'w'))
