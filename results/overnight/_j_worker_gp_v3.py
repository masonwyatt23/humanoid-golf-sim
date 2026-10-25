"""v3 copy of _j_worker_gp.py (adds the optional perturb= token; otherwise identical). Stage J worker for the Evaluator's realism harness (branch scott-e a4157b6+): same CLI/JSON as eval/_v5_worker.py but builds train.v5_train_j.JEnv (reference-guided residual env) and reads
res_scale/keys/t_down from the run's args.json. Usage: python scripts/v5_eval_j_worker.py <repo> <ckpt_base> <club_len> <seed0> <n> <out.json> [arm_dist=0.6] [gate_nx|off]

DT FIX 2026-10-19 (independently verified; README_arm_dist.md "dt correction"): JEnv runs MuJoCo at dt=0.002 with sub = round(CTRL_DT 0.02 / 0.002) = 10
substeps per control step and logs segments every seg_every = max(1, round(0.005 / 0.002)) = round(2.5) = 2 substeps (Python banker's rounding) = 4 ms.
This wrapper used to DECLARE dt=0.005 and the harness hard-coded 0.005, so every timing was inflated x1.25. Now: traces are the raw logged samples
(no resampling/interpolation), the declared dt is sim dt x default seg_every, and eval/realism_check MEASURES the interval from the logged sim time.
Also passes res_mult / ctrl_dt (K14a/K14b dynamics; both None for K7-K12, so K7-K12 rollouts are unchanged) and the Trainer's full configure list
(reward-only keys, no effect on actions). Pre-fix copy: _j_worker_gp_pre_dtfix.py."""
import sys, json, os
repo, ck, L, seed0, n, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
ARM = float(sys.argv[7]) if len(sys.argv) > 7 else 0.6
GATE = None if len(sys.argv) <= 8 or sys.argv[8].lower() in ('off', 'none', '') else float(sys.argv[8])
# optional argv[9]: 'seg1' = log segment speeds/GRF at EVERY physics substep (realism_check --timing-res-ms). Logging only reads state (mj_objectVelocity, contact forces); dynamics and actions are unchanged.
SEG1 = 'seg1' in sys.argv[9:]
# v3 (2026-10-19, PROVISIONAL robustness gate): optional argv token perturb=<json> {joint_deg, joint_vel, ball_tol_m, friction_rand}: perturb the state
# at address after reset (joint noise from rng(seed + 0x5EED)); ball offset and floor friction via the env's own ball_tol / friction_rand options.
PERT = next((json.loads(a_[8:]) for a_ in sys.argv[9:] if a_.startswith('perturb=')), None)
sys.path.insert(0, repo)
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from train.v5_train_j import JEnv
A = json.load(open(os.path.join(os.path.dirname(ck), "args.json")))
# Harness v5 goal obs (Trainer a2c1c7a / main 3c7119db, train.dr_goal.DREnv): runs trained with --goal_obs (args.json goal_obs true) get obs 116+8 and are
# rolled out in DREnv with goal_obs=True and DR OFF (dr stays False). Goals per episode from env V5_GOALS (JSON list, cycled; set_goal before each reset).
# Runs without goal_obs (all stageDR runs so far, every J/K/V run) take the JEnv path below unchanged.
GOAL_OBS = bool(A.get('goal_obs'))
GOALS = json.loads(os.environ['V5_GOALS']) if (GOAL_OBS and os.environ.get('V5_GOALS')) else None
# Impact logging (harness v5, env V5_IMPACT_LOG=1; Trainer f253d5d DREnv --impact_log): WORLD-frame impact keys (+ = left) on the contact step.
# Used only if the export's DREnv has impact_log; else IMPACT_OK False and the harness shows n/a. Reward untouched (Trainer: reward md5 identical on/off).
IMPACT_REQ = os.environ.get('V5_IMPACT_LOG', '0') == '1'
try:
    from train.dr_goal import DREnv as _GEnv
except Exception: _GEnv = None
IMPACT_OK = bool(IMPACT_REQ and _GEnv is not None and hasattr(_GEnv, 'impact_log'))
USE_DR = GOAL_OBS or IMPACT_OK
keys = {tuple(k.split("|")): v for k, v in json.load(open(os.path.join(repo, A["keys"]))).items()} if A.get("keys") and A["keys"] != "none" else None
CFG = ('xf_hard', 'grf_lo', 'grf_w', 'xf_cap_lo', 'xf_cap_w', 'track_floor', 'ord2_w', 'launch_w', 'desc_w', 'dloft_w', 'spin_lo_w', 'smash_w', 'spin_w', 'spin_hi', 'spin_scale', 'fine_grf',
       'launch_hi', 'dl_lo', 'dl_hi', 'aoa_lo', 'spd_w', 'pel_w', 'pel_t_w', 'pel_dps', 'pel_t_lo', 'pel_t_hi', 'sep_w', 'ctr_w', 'ctrl_dt',
       'tee_dz', 'ball_dx', 'face_h', 'tee_mode', 'stance_obs')   # stance_obs: Trainer 92703d2e --stance_obs (+4 obs dims), forwarded only when args.json sets it (None/absent -> skipped, old snapshots unchanged); as scripts/v5_eval_j_worker.py (a17ae69) + K31/K32 geometry keys (Evaluator 2026-10-24). configure() skips None, so runs whose args.json lacks a key (or has null) are unchanged
# Tee override (harness-controlled, env V3_TEE): unset/'args' = args.json value; '0' (or any float) = that tee_dz in m; 'crown' = ball centre at the head-box
# crown height at address (derived from sim head geometry; crown-level per GOLF.com / Golf Digest / Golf Monthly advice). HOOK: if the Trainer's env
# exposes crown_tee_dz() / tee_mode='crown', it is used and cross-checked against tee_geometry() below (see _tee_crown()).
V3_TEE = os.environ.get('V3_TEE', 'args').strip().lower(); V3_FACE_H = os.environ.get('V3_FACE_H')   # V3_FACE_H: 'none' = head box, float = m; unset = args.json
# Head override (env V3_HEAD, 2026-10-24, Trainer a9d917e --head realistic): unset/'args' = args.json 'head' (absent/None -> 'box'); 'box' | 'realistic'.
# realistic: env.set_head('realistic') is called (stop if the env lacks it) and face_limits()/address geometry are cross-checked against the
# Data Agent JSON (data/driver_head_460cc_refs.json in the scored repo) with 0.5 mm tolerance; mismatch -> SystemExit (as _tee_crown).
V3_HEAD = os.environ.get('V3_HEAD', 'args').strip().lower()
HEAD = (('v4' if A.get('env_v4') else (A.get('head') or 'box')) if V3_HEAD in ('args', '') else V3_HEAD)   # args.json env_v4 (Trainer 54b49c6 --env_v4) -> v4
# v4 tee mapping (Evaluator 2026-10-24): MAIN/gating row = Trainer tee_mode '1.5in' (ball centre 59.435 mm), forced whatever args.json says;
# the Trainer's v4 DEFAULT tee (equator at the 62 mm crown) = the 1.6 in crown INFO row (V3_TEE=crown). args value recorded in TEE_INFO.
if HEAD == 'v4' and V3_TEE in ('args', ''): V3_TEE = '1.5in'
if HEAD not in ('box', 'realistic', 'v4'): raise SystemExit(f"V3_HEAD/args head {HEAD!r} not in box|realistic")
HEAD_TOL_M = 5e-4
TEE_ARGS = dict(tee_dz=A.get('tee_dz'), ball_dx=A.get('ball_dx'), face_h=A.get('face_h'), tee_mode=A.get('tee_mode'))
def _cfg():
    c = {k: A.get(k) for k in CFG}
    c['head'] = HEAD if HEAD == 'realistic' else None
    if HEAD == 'v4': c['env_v4'] = True   # Trainer flag --env_v4 (JEnv.reset -> env.set_env_v4(True)); pending Trainer commit   # JEnv.reset() calls env.set_head(self.head) when set; None = unchanged box path
    if V3_TEE not in ('args', ''): c['tee_mode'] = None   # harness-chosen tee overrides any args tee_mode
    if V3_FACE_H is not None: c['face_h'] = None if V3_FACE_H.lower() in ('none', '') else float(V3_FACE_H)
    return c
def tee_geometry(env_):
    """Static address geometry (call right after reset): ball centre / bottom z, crown z as the Trainer's _crown_tee_dz() defines it (box: face-centre site + 0.5*H*up_z, H = face_h if set else head-box height; realistic/v4: env _head_geo crown_z), sole z. crown_above_sole_m (Data Agent cross-check) stays shell geometry."""
    d_, m_ = env_.d, env_.m; g_ = env_.head_geom; R_ = d_.geom_xmat[g_].reshape(3, 3); h_ = m_.geom_size[g_]; S_ = d_.site_xpos[env_.head_site]
    up_ = np.cross(R_[:, 0], R_[:, 1]); up_ = up_ if up_[2] >= 0 else -up_; rb_ = float(m_.geom_size[env_.ball_geom][0]); P_ = d_.geom_xpos[g_]
    cz = [float((P_ + R_ @ (np.array([a_, b_, c_]) * h_))[2]) for a_ in (-1, 1) for b_ in (-1, 1) for c_ in (-1, 1)]
    G_ = dict(ball_centre_z_m=float(env_.tee[2]), ball_bottom_z_m=float(env_.tee[2]) - rb_, ball_radius_m=rb_, head_half_height_m=float(h_[2]), face_centre_z_m=float(S_[2]),
                crown_z_m=float(S_[2] + (0.5 * env_.face_h if getattr(env_, 'face_h', None) is not None else h_[2]) * up_[2]), crown_boxtop_z_m=float(S_[2] + h_[2] * up_[2]), crown_maxcorner_z_m=max(cz), sole_min_z_m=min(cz), face_up=up_.tolist(), ball_minus_face_centre_along_up_m=float(np.dot(env_.tee - S_, up_)), head='box')
    if getattr(env_, 'head', 'box') == 'realistic':   # realistic head: 'head' geom is the 80 mm contact-plate envelope, so crown/sole come from the head_shell box (top = crown) and the face half-height from face_limits()
        sh_ = m_.geom('head_shell').id; Ps_ = d_.geom_xpos[sh_]; Rs_ = d_.geom_xmat[sh_].reshape(3, 3); hs_ = m_.geom_size[sh_]
        zs_ = [float((Ps_ + Rs_ @ (np.array([a_, b_, c_]) * hs_))[2]) for a_ in (-1, 1) for b_ in (-1, 1) for c_ in (-1, 1)]
        fl_ = env_.face_limits()
        hg_ = getattr(env_, '_head_geo', None) or {}; czr_ = float(hg_['crown_z']) if 'crown_z' in hg_ else max(zs_)
        G_.update(head='realistic', crown_z_m=czr_, crown_source=('env _head_geo crown_z (Trainer _crown_tee_dz definition: sole clearance + sourced crown height)' if 'crown_z' in hg_ else 'head_shell max corner (env lacks _head_geo crown_z)'), crown_maxcorner_z_m=max(zs_), crown_shell_maxcorner_z_m=max(zs_), face_formula_crown_z_m=float(S_[2] + float(fl_[0]) * up_[2]), sole_min_z_m=min(zs_), head_half_height_m=float(fl_[0]), plate_half_height_m=float(h_[2]),
                  face_centre_above_sole_m=float(S_[2]) - min(zs_), crown_above_sole_m=max(zs_) - min(zs_), ball_xy_m=[float(env_.tee[0]), float(env_.tee[1])], face_centre_xy_m=[float(S_[0]), float(S_[1])])
    return G_
_CFG_V = _cfg()
def mk():
    e = (_GEnv if USE_DR else JEnv)(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); e.configure(res_mult=(json.loads(A['res_mult']) if A.get('res_mult') else None), **{k: _CFG_V[k] for k in CFG})
    if IMPACT_OK: e.impact_log = True
    if GOAL_OBS: e.goal_obs = True; e._grow_obs()   # == DREnv.configure(goal_obs=True) (sets the flag, grows obs by 8); kept off the single configure() call the parity tests pin
    e.rsi = (1.0, 0.0, 0.0); e.env.arm_dist = ARM; e.env.strike_gate_nx = GATE; e.target_len = L; e.target_tether = 0.0; e.env.friction_rand = False; e.track_w = 0.0; return e
vn = VecNormalize.load(ck + "_vecnorm.pkl", DummyVecEnv([mk])); vn.training = False; vn.norm_reward = False
model = PPO.load(ck, device="cpu"); te = mk(); e = te.env; e.log_segments = True
def _head_check():
    """Realistic head: cross-check env face_limits() and address geometry against the repo's Data Agent JSON (0.5 mm). Returns head info for the run."""
    if HEAD == 'v4': raise SystemExit('internal: use _v4_check for v4')
    if HEAD == 'box': return dict(mode='box', source='sim head box 90x110x64 mm (env default; unchanged)', face_limits_m=(e.face_limits() if hasattr(e, 'face_limits') else None))
    if not hasattr(e, 'set_head') or not hasattr(e, 'face_limits'): raise SystemExit("V3_HEAD=realistic but the scored env has no set_head()/face_limits()")
    if getattr(e, 'head', 'box') != 'realistic': e.set_head('realistic')
    import re as _re
    jp = os.path.join(repo, 'data', 'driver_head_460cc_refs.json'); rows = {r_['quantity']: r_ for r_ in json.load(open(jp))['rows']}
    num = lambda q: float(_re.search(r"[-+]?\d+(\.\d+)?", rows[q]['nominal']).group(0)) * 1e-3
    te.tee_dz = 0.0; tm_ = te.tee_mode if hasattr(te, 'tee_mode') else None; te.tee_mode = None; te.reset(seed=0); g_ = tee_geometry(e); fl = e.face_limits()
    fh = e.face_h if e.face_h is not None else num('face height')   # read AFTER reset (JEnv.reset sets env.face_h); a face_h override (args/V3_FACE_H) replaces the JSON face height
    exp = dict(face_half_h_m=0.5 * fh, face_half_w_m=0.5 * num('face width'), crown_above_sole_m=num('sole-to-crown (crown height when soled)'),
                                                                        face_centre_above_sole_m=num('face-centre height when soled'))
    got = dict(face_h_override_m=None, face_half_h_m=float(fl[0]), face_half_w_m=float(fl[1]), crown_above_sole_m=g_['crown_above_sole_m'], face_centre_above_sole_m=g_['face_centre_above_sole_m'])
    got['face_h_override_m'] = e.face_h; bad = {k: (got[k], exp[k]) for k in exp if abs(got[k] - exp[k]) > HEAD_TOL_M}
    if bad: raise SystemExit(f"head geometry mismatch (env vs Data Agent JSON, tol 0.5 mm): {bad}")
    te.tee_mode = tm_
    return dict(mode='realistic', source=f"env realistic head (Trainer a9d917e+), cross-checked vs {os.path.relpath(jp, repo)} (Data Agent driver-head-refs)", face_limits_m=[float(fl[0]), float(fl[1])],
                expected=exp, measured=got, tol_m=HEAD_TOL_M, geometry_tee0=g_, estimates=[q for q, r_ in rows.items() if 'estimate' in r_['nominal']],
                compromises="lie kept 56 deg (sourced 58.5); swingweight +1.8% (Trainer TRAINING_NOTES K34)")
def _v4_measure():
    """v4 env cross-check probe: face-centre height above GROUND, CFZ (face centre projected along target x onto the vertical shaft-axis plane,
    shortest distance to the shaft axis; US 12,649,090 def.), lie (shaft vs ground), Izz of the head mass box about its up axis, ball-centre heights
    at the 1.5 in and 1.6 in (crown) tees, face_limits(). Returns (measured, geometry)."""
    te.tee_dz = 0.0; te.tee_mode = '1.5in'; te.reset(seed=0); g_ = tee_geometry(e); b15 = float(e.tee[2])
    S = np.array(e.d.site_xpos[e.head_site]); cb = e.m.geom_bodyid[e.head_geom]; a_ = np.array(e.d.xmat[cb]).reshape(3, 3)[:, 2]; a_ = a_ / np.linalg.norm(a_)
    p0 = np.array(e.d.xpos[cb]); ez = np.array([0.0, 0.0, 1.0]); ex = np.array([1.0, 0.0, 0.0]); n_ = np.cross(a_, ez); n_ /= np.linalg.norm(n_)
    t_ = float(np.dot(S - p0, n_) / np.dot(ex, n_)); q_ = S - t_ * ex; w_ = q_ - p0; cfz = float(np.linalg.norm(w_ - np.dot(w_, a_) * a_))
    lie = float(np.degrees(np.arcsin(abs(a_[2]))))
    hm = e.m.geom('head_mass').id; hh = np.array(e.m.geom_size[hm]); mass = float(e._head_geo['spec']['mass'])
    izz = mass * (hh[0] ** 2 + hh[1] ** 2) / 3.0 * 1e7   # box about its local up axis (head axes x, toe, up), g cm2
    te.tee_mode = None; te.reset(seed=0); b0 = float(e.tee[2]); te.tee_mode = 'crown'; te.reset(seed=0); b16 = float(e.tee[2]); g16 = tee_geometry(e); te.tee_mode = None
    fl = e.face_limits()
    meas = dict(face_centre_z_ground_m=float(S[2]), cfz_m=cfz, lie_deg=lie, izz_gcm2=izz, tee_15in_ball_centre_m=b15, tee_16in_ball_centre_m=b16,
                face_half_h_m=float(fl[0]), face_half_w_m=float(fl[1]))
    return meas, dict(crown_tee_ball_z_m=b16, default_tee_ball_z_m=b0, tee_15in=g_, tee_crown=g16, crown_z_m=g16['crown_z_m'], sole_min_z_m=g16['sole_min_z_m'])
def _v4_check():
    import importlib.util as _iu   # harness module from THIS worktree (sys.path[0] is the scored repo)
    _sp = _iu.spec_from_file_location('harness_v4_eval', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'eval', 'harness_v4.py'))
    _hm = _iu.module_from_spec(_sp); _sp.loader.exec_module(_hm); V4_SPEC, check_v4, STATUS_PENDING = _hm.V4_SPEC, _hm.check_v4, _hm.STATUS_PENDING
    if not hasattr(e, 'set_env_v4'): raise SystemExit(f"V3_HEAD=v4 requested but the scored env has no set_env_v4() ({STATUS_PENDING}; Trainer v4 address solve not in this export)")
    if not getattr(e, 'env_v4', False): e.set_env_v4(True)
    meas, geo = _v4_measure(); bad = check_v4(meas)
    from env.v5_body import V4 as _V4, sw_compensation as _swc   # scored repo's V4 dict
    aj = os.path.join(repo, 'env', 'models', f"v5_address_{e.handed}_{int(round(L * 100))}_v4.json"); AJ = json.load(open(aj))
    sw = _swc(e.handed, e.club_len, AJ.get('lie_deg')); sole = geo['sole_min_z_m']; crown = geo['crown_z_m']
    xchk = dict(json_lie_deg=(AJ.get('lie_deg'), meas['lie_deg'], 0.1), json_fc_z_ground_m=(AJ.get('face_centre_z_ground_m'), meas['face_centre_z_ground_m'], 5e-4),
                json_ball_z_m=(AJ['ball_pos'][2], geo['crown_tee_ball_z_m'], 5e-4), dict_fc_z_ground_m=(_V4['fc_z_ground'], meas['face_centre_z_ground_m'], 5e-4),
                dict_fc_shaft_m=(_V4['fc_shaft'], meas['cfz_m'], 5e-4), dict_izz_gcm2=(_V4['izz'] * 1e7, meas['izz_gcm2'], 0.01 * _V4['izz'] * 1e7),
                dict_sole_clear_m=(_V4['sole_clear'], sole, 5e-4), dict_tee15_bottom_m=(_V4['tee_15in_bottom'], meas['tee_15in_ball_centre_m'] - float(e.m.geom_size[e.ball_geom][0]), 5e-4),
                json_v4_params=(AJ.get('v4_params'), dict(_V4), 0))
    for k_, (x_, y_, t_) in xchk.items():
        ok_ = (x_ == y_) if t_ == 0 else (x_ is not None and abs(float(x_) - float(y_)) <= t_)
        if not ok_: bad[k_] = (y_, x_, t_)
    geo.update(address_json=os.path.relpath(aj, repo), sole_clear_measured_m=sole, crown_above_ground_m=crown, swingweight=dict(m_butt_g=sw['m_butt'] * 1e3, z_box_m=sw['z_box'], z_real_m=sw['z_real']),
               v4_dict=dict(_V4), address_json_lie_deg=AJ.get('lie_deg'), address_json_ball_pos=AJ['ball_pos'])
    if bad: raise SystemExit(f"v4 address mismatch vs V4_SPEC (eval/harness_v4.py): {bad}")
    return dict(mode='v4', source='Trainer v4 env (env_v4 / set_env_v4), cross-checked vs eval/harness_v4.V4_SPEC', face_limits_m=[meas['face_half_h_m'], meas['face_half_w_m']],
                measured=meas, expected={k: v['value'] for k, v in V4_SPEC.items()}, geometry=geo, check='passed')
HEAD_INFO = _v4_check() if HEAD == 'v4' else _head_check()
def _tee_crown():
    te.tee_dz = 0.0; te.reset(seed=0); g0 = tee_geometry(e); mine = g0['crown_z_m'] - g0['ball_centre_z_m']; trainer = None
    if HEAD == 'realistic' and not hasattr(e, 'crown_tee_dz'): raise SystemExit('realistic head crown tee needs the env crown_tee_dz()')
    if hasattr(e, 'crown_tee_dz'): trainer = float(e.crown_tee_dz())
    elif hasattr(te, 'crown_tee_dz'): trainer = float(te.crown_tee_dz())
    if trainer is not None and abs(trainer - mine) > 5e-4: raise SystemExit(f"crown tee mismatch: Trainer {trainer} vs harness {mine}")
    return (trainer if trainer is not None else mine), dict(harness_m=mine, trainer_m=trainer, source=('Trainer env crown_tee_dz (cross-checked)' if trainer is not None else 'harness tee_geometry(): crown_z - ball_centre_z at address, tee_dz 0'), geometry_tee0=g0)
TEE_SRC = None
if V3_TEE == '1.5in':
    if HEAD != 'v4' and not hasattr(e, 'set_env_v4'): raise SystemExit("V3_TEE=1.5in needs the env tee_mode '1.5in' (pending Trainer flag)")
    te.tee_dz = 0.0; te.tee_mode = '1.5in'; TEE_SRC = dict(source="env tee_mode '1.5in' (ball bottom 38.1 mm above ground)")
elif V3_TEE == 'crown' and HEAD == 'v4': te.tee_dz = 0.0; te.tee_mode = 'crown'; TEE_SRC = dict(source='v4 env crown tee (1.6 in; checked in tee_info.head)', label='v4 head, 1.6 in crown tee (equator at sourced crown)')
elif V3_TEE == 'crown': _tdz, TEE_SRC = _tee_crown(); te.tee_dz = float(_tdz)
elif V3_TEE not in ('args', ''): te.tee_dz = float(V3_TEE)   # set directly so 0.0 also overrides an args value
te.reset(seed=0); TEE_GEOM = tee_geometry(e)
TEE_INFO = dict(head=HEAD_INFO, mode=V3_TEE, args_env_v4=A.get('env_v4'), args_tee_mode=A.get('tee_mode'), args=TEE_ARGS, tee_dz_used_m=float(getattr(e, 'tee_dz', 0.0) or 0.0), ball_dx_used_m=float(getattr(e, 'ball_dx', 0.0) or 0.0), face_h_used_m=getattr(e, 'face_h', None),
                tee_mode_used=getattr(te, 'tee_mode', None), crown=TEE_SRC, geometry=TEE_GEOM,
                note="tee/ball geometry read after reset at the address pose (seed 0, no perturbation)")
from env.v5_body import build_model as _bm; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))); from eval.robust_grf import nominal_floor_mu, FLOOR_MU_NOTE
FRIC0 = nominal_floor_mu(_bm, e.handed, e.club_len, e._dt_arg, e.force_scale, e.addr)   # model value, NOT a post-draw read of e.m (construction reset already randomised it)
if PERT: e.friction_rand = bool(PERT.get('friction_rand', False)); e.ball_tol = float(PERT.get('ball_tol_m', 0.0))
if PERT:   # K24+ JEnv.reset() forces env.friction_rand=False and env.ball_tol=JEnv.ball_tol before every reset; re-assert the requested values
    _fr_, _bt_, _r0_ = bool(PERT.get('friction_rand', False)), float(PERT.get('ball_tol_m', 0.0)), e.reset   # at the V5GolfEnv level so the draws use the env rng exactly as before
    def _reset_pert(*a_, **k_):
        e.friction_rand = _fr_; e.ball_tol = _bt_; return _r0_(*a_, **k_)
    e.reset = _reset_pert
bw = float(sum(e.m.body_mass[i] for i in range(e.m.nbody) if e.m.body(i).name not in ("ball",)) * 9.81)
grf = []; sub = []; foot = []; grf_h = []; orig = e._log_seg
import mujoco as _mj
def _sole_xyz():   # v3c (logging only): world-frame contact force (N) on each sole from the floor; contact frame rows = normal, t1, t2
    F = {s: np.zeros(3) for s in e.sole_geoms}; fv = np.zeros(6)
    for k_ in range(e.d.ncon):
        c = e.d.contact[k_]
        for s, gid in e.sole_geoms.items():
            if (c.geom1 == gid and c.geom2 == e.floor) or (c.geom2 == gid and c.geom1 == e.floor):
                _mj.mj_contactForce(e.m, e.d, k_, fv); f = np.asarray(c.frame).reshape(3, 3).T @ fv[:3]; F[s] += f if c.geom1 == e.floor else -f
    return [float(np.hypot(F[s][0], F[s][1])) for s in ('left', 'right')], [float(abs(F[s][2])) for s in ('left', 'right')]
def seg():
    orig(); fl, fr = e.foot_forces(); grf.append((fl, fr)); sub.append(int(e.sub_count)); grf_h.append(_sole_xyz()[0])
    sid = e.m.site(f"{e.lead}_sole_site").id; P = e.d.site_xpos[sid]; R = e.d.site_xmat[sid].reshape(3, 3); hx = float(e.m.site_size[sid][0])   # lead sole: centre xyz + heel/toe z + yaw (atan2 of sole +x in world xy)
    yaw = float(np.arctan2(R[1, 0], R[0, 0])); foot.append([float(P[0]), float(P[1]), float(P[2]), float((P - hx * R[:, 0])[2]), float((P + hx * R[:, 0])[2]), yaw])
e._log_seg = seg
# v3d side-by-side face-edge model (logging only, dynamics unchanged): at contact, also run the env's own golfphys shot_from_contact with the
# SAME club velocity / face normal / dy but dz = 0 (CENTRE strike in height) -> 'strike_centre'. The harness feeds this to data/driver_face_offcentre.
from env.v5_shot import shot_from_contact as _sfc
_HIT = {}; _dc0 = e._do_contact
def _do_contact_log(cpos):
    _dc0(cpos)
    try:
        h = e.ball_hit_info; c = _sfc(np.array(e.prev_v, float), np.array(h["face_normal"], float), float(h["dy"]), 0.0, handed=e.handed, toe_sign=e.toe_sign, ball_z=float(e.tee[2]))
        _HIT["centre"] = dict(dz_used_m=0.0, dy_m=float(h["dy"]), smash=float(c["smash"]), spin_rpm=float(c["shot"].spin_rpm), backspin_rpm=float(c["backspin_rpm"]), launch_deg=float(c["launch_deg"]),
                              ball_speed_mph=float(c["ball_speed"]) / 0.44704, carry_m_noroll=float(c["shot"].carry_m))
    except Exception as ex_: _HIT["centre"] = dict(error=repr(ex_))
e._do_contact = _do_contact_log
def _goal_reset(i):   # DREnv.reset with dr=False == goal swap + JEnv.reset; called via JEnv.reset so evaluation seeds (incl. held-out 910000+) bypass the TRAINING seed guard
    if GOAL_OBS and GOALS: te.set_goal(GOALS[i % len(GOALS)])
    if GOAL_OBS and te._next_goal is not None: te.goal = te._next_goal
    return JEnv.reset(te, seed=seed0 + i)
_H2B = None; _LAT = 0; _ABUF = []
def _h2_apply(seed):   # harness v5-heldout-2 (opt-in): one new DR dimension per episode; restores the base model first
    global _H2B, _LAT, _ABUF
    import mujoco as _mj2
    from eval.harness_v5 import sample_heldout2 as _s2
    m_ = e.m; cb = m_.body("club").id
    if _H2B is None: _H2B = (m_.opt.gravity.copy(), e.tau.copy(), m_.geom_quat[e.head_geom].copy(), float(m_.body_mass[cb]), m_.body_ipos[cb].copy(), m_.body_inertia[cb].copy(), m_.body_mass.copy(), m_.body_inertia.copy())
    g0, t0, q0, M0, ip0, in0, bm0, bi0 = _H2B
    m_.body_mass[:] = bm0; m_.body_inertia[:] = bi0
    m_.opt.gravity[:] = g0; e.tau[:] = t0; m_.geom_quat[e.head_geom] = q0; m_.body_mass[cb] = M0; m_.body_ipos[cb] = ip0; m_.body_inertia[cb] = in0; _LAT = 0; _ABUF = []
    d_ = _s2(seed, dict(PERT['heldout2'])); v = d_['value']; k = d_['dim']
    if k == 'slope_grade':
        t = np.arctan(v); G = float(np.linalg.norm(g0)); az = d_['slope_az_rad']; m_.opt.gravity[:] = (G * np.sin(t) * np.cos(az), G * np.sin(t) * np.sin(az), -G * np.cos(t))
    elif k == 'torque_scale': e.tau[:] = t0 * v
    elif k == 'latency_steps': _LAT = int(v)
    elif k == 'loft_deg':
        q = np.zeros(4); _mj2.mju_axisAngle2Quat(q, np.array([0.0, 1.0, 0.0]), np.radians(v)); qo = np.zeros(4); _mj2.mju_mulQuat(qo, q0, q); m_.geom_quat[e.head_geom] = qo
    elif k.startswith('seg_'):   # segment mass + inertia x f on the Trainer's SEG bodies (train.dr_goal.SEG, same name match as DREnv)
        from train.dr_goal import SEG as _SEG
        names = sum((tuple(_SEG[g]) for g in {'seg_trunk': ('trunk',), 'seg_thighcalf': ('thigh', 'calf'), 'seg_foot': ('foot',)}[k]), ()); hit = []
        for b in range(m_.nbody):
            nm = m_.body(b).name
            if any(nm == s_ or nm.endswith(s_) and nm.startswith(("left_", "right_")) for s_ in names): m_.body_mass[b] = bm0[b] * v; m_.body_inertia[b] = bi0[b] * v; hit.append(nm)
        d_ = dict(d_, bodies=hit)
    elif k == 'head_g':
        dm = (v - 200.0) / 1000.0; hp = m_.geom_pos[e.head_geom]; m_.body_mass[cb] = M0 + dm; m_.body_ipos[cb] = (M0 * ip0 + dm * hp) / (M0 + dm); m_.body_inertia[cb] = in0 * (M0 + dm) / M0
    return d_
def _lat(a):   # delay actions by _LAT control steps (zeros until the buffer fills), as DREnv's latency
    if not _LAT: return a
    _ABUF.append(np.asarray(a, np.float32).copy())
    return _ABUF.pop(0) if len(_ABUF) > _LAT else np.zeros_like(_ABUF[-1])
eps = []; SEG_DEF = int(e.seg_every)   # default logging cadence (2 substeps = 4 ms at dt 0.002), captured once before any seg1 override
for i in range(n):
    grf.clear(); sub.clear(); foot.clear(); grf_h.clear(); e.seg_every = SEG_DEF; o, _ = (_goal_reset(i) if USE_DR else te.reset(seed=seed0 + i)); e.seg_every = SEG_DEF; seg_def = SEG_DEF; done = False; info = {}
    if SEG1: e.seg_every = 1
    pinfo = None
    if PERT:   # perturb the address state (actuated joints only), then refresh derived quantities and the observation
        import mujoco
        if PERT.get('friction_range'):   # v3b gate: fixed-range floor mu from its own rng (joint-noise rng untouched)
            lo_, hi_ = (float(v) for v in PERT['friction_range']); e.m.geom_friction[e.floor, 0] = np.random.default_rng(seed0 + i + 0xF41C).uniform(lo_, hi_)
        elif os.environ.get('V3_FRICTION_RANGE'):   # ablation only (info): fixed-range floor mu from its own rng, joint-noise rng untouched
            lo_, hi_ = (float(v) for v in os.environ['V3_FRICTION_RANGE'].split(',')); e.m.geom_friction[e.floor, 0] = np.random.default_rng(seed0 + i + 0xF41C).uniform(lo_, hi_)
        rg = np.random.default_rng(seed0 + i + 0x5EED); nq = len(e.qa)
        if PERT.get('heldout2'):   # v5-heldout-2: new dims only, state noise nominal
            dq = np.zeros(nq); dv = np.zeros(nq); _h2 = _h2_apply(seed0 + i)
        elif PERT.get('heldout'):   # harness v5 held-out DR (eval/harness_v5.py sample_heldout; ranges disjoint from training). Absent = v3/v4 path below, unchanged.
            from eval.harness_v5 import sample_heldout as _sh
            dq, dv, _mu, _bxy = _sh(seed0 + i, nq, PERT['heldout']); e.m.geom_friction[e.floor, 0] = _mu
            e.tee[:2] = np.array(e.addr["ball_pos"], float)[:2] + _bxy; e.d.qpos[e.ball_q:e.ball_q + 2] = e.tee[:2]
        else:
            dq = np.radians(float(PERT.get('joint_deg', 0.0))) * rg.uniform(-1, 1, nq); dv = float(PERT.get('joint_vel', 0.0)) * rg.uniform(-1, 1, nq)
        e.d.qpos[e.qa] += dq; e.d.qvel[e.da] += dv; mujoco.mj_forward(e.m, e.d); o = te._xobs(e._obs())
        pinfo = dict(heldout2=(_h2 if PERT.get('heldout2') else None), joint_deg_max=float(np.degrees(np.abs(dq)).max()), joint_vel_max=float(np.abs(dv).max()), ball_xy_off_m=[float(x) for x in (e.tee[:2] - np.array(e.addr["ball_pos"], float)[:2])], floor_mu=float(e.m.geom_friction[e.floor, 0]))
    _HIT.clear(); _IMP = None
    while not done:
        a = model.predict(vn.normalize_obs(o[None]), deterministic=True)[0][0]; o, r, term, trunc, info = te.step(_lat(a)); done = term or trunc
        if IMPACT_OK and _IMP is None and 'impact_face_world_deg' in info: _IMP = {k_: float(v_) for k_, v_ in info.items() if k_.startswith('impact_')}
    L_ = e.log; tc = e.t_contact; t = np.array(L_["t"])
    imp = int(np.argmax(t >= tc)) if tc is not None and (t >= tc).any() else len(t) - 1
    shx = {}
    if e.contact and getattr(e, "shot", None):
        _s = e.shot; _r = _s["shot"]; shx = dict(azimuth_deg=_s.get("azimuth_deg"), backspin_rpm=_s.get("backspin_rpm"), sidespin_rpm=_s.get("sidespin_rpm"), env_carry_m=_r.carry_m, env_total_m=_r.total_m, env_descent_deg=_r.descent_deg, env_lateral_m=_r.lateral_carry_m)
    eps.append(dict(impact=_IMP, goal=((info.get("ep") or {}).get("goal") or (dict(te.goal) if GOAL_OBS and te.goal else None)), goal_obs_block=([float(x) for x in o[-8:]] if GOAL_OBS else None), shot_extra=shx, foot_length_m=0.20, t=L_["t"], pelvis_dps=L_["pelvis"], thorax_dps=L_["thorax"], arm_dps=L_["lead_arm"], club_dps=L_["club"], xfactor_deg=L_["xfactor_deg"], lead_share=L_["lead_share"],
                    grf=[list(map(float, g)) for g in grf], grf_h=[list(map(float, g)) for g in grf_h], lead_foot=[list(f_) for f_ in foot], t_top=getattr(getattr(te, "ref", None), "t_dstart", None), lead=e.lead, impact_idx=imp, contact=bool(e.contact), ep=info.get("ep"), foul=bool(info.get("foul", False)), seed=seed0 + i, t_contact=tc, sub=list(sub), seg_every=int(e.seg_every), seg_every_default=int(seg_def), perturb=pinfo, strike=(dict(dy_m=float(e.ball_hit_info["dy"]), dz_m=float(e.ball_hit_info["dz"]), frame="clubhead site (face centre), dy toward toe, dz along face up; env v5_golf_env._do_contact", centre=_HIT.get("centre")) if (e.contact and getattr(e, "ball_hit_info", None)) else None),
                    shot={k: info.get(k) for k in ("club_speed_mph", "ball_speed_mph", "launch_deg", "spin_rpm", "smash", "carry_m_noroll", "total_m_model", "lateral_carry_m")}))
json.dump(dict(tee_info=TEE_INFO, perturb_spec=PERT, floor_mu_nominal=FRIC0, floor_mu_note=FLOOR_MU_NOTE, strike_gate_nx=GATE, arm_dist=ARM, env_class=("DREnv" if USE_DR else "JEnv"), impact_log=dict(requested=IMPACT_REQ, supported=IMPACT_OK, frame="world, + = left (+y); Trainer f253d5d"), bw_N=bw, dt=float(e.dt) * SEG_DEF, dt_note="declared = sim dt x default seg_every (4 ms at dt 0.002); harness measures it from t (dt fix)", club_len=L, foot_length_m=0.20, eps=eps), open(out, "w"), default=float)
