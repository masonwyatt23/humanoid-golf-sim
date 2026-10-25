"""Harness v4.1 probe (NON-GATING info, no policy rollouts): foot residuals before/after re-grounding, root shift and clubhead shift relative to the
ball at the 24 v4 robustness address states (seeds 7000-7023). Reproduces the worker's address path (results/overnight/_j_worker_gp_v3.py: mk(),
v4 1.5in tee, PERT reset hook, joint/velocity noise from rng(seed + 0x5EED), friction_range from rng(seed + 0xF41C)) and eval/reground.py.
The address state does not depend on the policy weights; only the snapshot's args.json (env config) is read.

Usage (paths from args/env, none hardcoded):
  HGS_RO_TRAINER=<read-only Trainer export, e.g. _ro_trainer_b663c9f6>  python _probe_v41_residuals.py <snapshot ckpt path (args.json beside it)> [--out JSON]
Output: per-seed records + summary (median/max) in mm / deg."""
import sys, os, json, argparse
ap = argparse.ArgumentParser(); ap.add_argument("ck"); ap.add_argument("--trainer", default=os.environ.get("HGS_RO_TRAINER"))
ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "v41_reground_residuals.json")); a = ap.parse_args()
if not a.trainer: raise SystemExit("set HGS_RO_TRAINER or --trainer")
HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, a.trainer)
import numpy as np, mujoco
from train.v5_train_j import JEnv
import importlib.util as _iu   # this worktree's harness modules by file (the Trainer export has its own eval package first on sys.path)
def _load(n):
    sp = _iu.spec_from_file_location("hgs_" + n, os.path.join(HERE, "eval", n + ".py")); m = _iu.module_from_spec(sp); sp.loader.exec_module(m); return m
default_perturb = _load("robust_grf").default_perturb; _RGM = _load("reground"); sole_poses, reground = _RGM.sole_poses, _RGM.reground
A = json.load(open(os.path.join(os.path.dirname(a.ck), "args.json")))
CFG = ('xf_hard', 'grf_lo', 'grf_w', 'xf_cap_lo', 'xf_cap_w', 'track_floor', 'ord2_w', 'launch_w', 'desc_w', 'dloft_w', 'spin_lo_w', 'smash_w', 'spin_w', 'spin_hi', 'spin_scale', 'fine_grf',
       'launch_hi', 'dl_lo', 'dl_hi', 'aoa_lo', 'spd_w', 'pel_w', 'pel_t_w', 'pel_dps', 'pel_t_lo', 'pel_t_hi', 'sep_w', 'ctr_w', 'ctrl_dt',
       'tee_dz', 'ball_dx', 'face_h', 'tee_mode', 'stance_obs')
c = {k: A.get(k) for k in CFG}; c['head'] = None; c['env_v4'] = True; c['tee_mode'] = None   # worker: HEAD v4, V3_TEE 1.5in
keys = {tuple(k.split("|")): v for k, v in json.load(open(os.path.join(a.trainer, A["keys"]))).items()} if A.get("keys") and A["keys"] != "none" else None
te = JEnv(dt=0.002, seed=123, keys=keys, res_scale=A["res_scale"], t_down=A["t_down"]); te.configure(res_mult=(json.loads(A['res_mult']) if A.get('res_mult') else None), **c)
te.rsi = (1.0, 0.0, 0.0); e = te.env; e.arm_dist = 0.6; e.strike_gate_nx = None; te.target_len = 1.15; te.target_tether = 0.0; e.friction_rand = False; te.track_w = 0.0
te.tee_dz = 0.0; te.tee_mode = '1.5in'; te.reset(seed=0)
P = default_perturb("v4"); _r0 = e.reset
def _rp(*x, **k): e.friction_rand = bool(P['friction_rand']); e.ball_tol = float(P['ball_tol_m']); return _r0(*x, **k)
e.reset = _rp
fb = e.m.joint("floating_base_joint"); bq = int(fb.qposadr[0])
def head_rel_ball(): return e.d.site_xpos[e.head_site] - e.tee
rows = []
for i in range(P['n']):
    s = P['seed0'] + i; te.reset(seed=s)
    if P.get('friction_range'): lo, hi = P['friction_range']; e.m.geom_friction[e.floor, 0] = np.random.default_rng(s + 0xF41C).uniform(lo, hi)
    rg = np.random.default_rng(s + 0x5EED); nq = len(e.qa)
    dq = np.radians(P['joint_deg']) * rg.uniform(-1, 1, nq); dv = P['joint_vel'] * rg.uniform(-1, 1, nq)
    mujoco.mj_forward(e.m, e.d); T = sole_poses(e.m, e.d); h0 = head_rel_ball().copy()
    e.d.qpos[e.qa] += dq; e.d.qvel[e.da] += dv; mujoco.mj_forward(e.m, e.d); h1 = head_rel_ball().copy()
    R = reground(e.m, e.d, T); h2 = head_rel_ball().copy()
    lat = lambda d: max(abs(x[1]) for x in d)
    rows.append(dict(seed=s, iters=R['iters'],
        before=dict(pos_mm=1e3 * R['before']['pos_max_m'], rot_deg=R['before']['rot_max_deg'], lat_mm=1e3 * lat(R['before']['dxyz_m'])),
        after=dict(pos_mm=1e3 * R['after']['pos_max_m'], rot_deg=R['after']['rot_max_deg'], lat_mm=1e3 * lat(R['after']['dxyz_m'])),
        root_shift_mm=1e3 * float(np.linalg.norm(R['base_shift_m'])),
        clubhead_shift_rel_ball_mm=dict(reground_vs_v4=1e3 * float(np.linalg.norm(h2 - h1)), reground_vs_unperturbed=1e3 * float(np.linalg.norm(h2 - h0)), v4_vs_unperturbed=1e3 * float(np.linalg.norm(h1 - h0)))))
def mm(v): v = np.asarray(v, float); return dict(median=float(np.median(v)), max=float(v.max()))
S = {f"{w}_{k}": mm([r[w][k] for r in rows]) for w in ("before", "after") for k in ("pos_mm", "rot_deg", "lat_mm")}
S["root_shift_mm"] = mm([r["root_shift_mm"] for r in rows])
for k in rows[0]["clubhead_shift_rel_ball_mm"]: S[f"clubhead_shift_rel_ball_mm_{k}"] = mm([r["clubhead_shift_rel_ball_mm"][k] for r in rows])
out = dict(note="Harness v4.1 probe, NON-GATING info. Address states only (no policy). Max over both soles; lateral = |world y|. Clubhead = env head site (face centre) minus ball centre.",
           script="results/overnight/_probe_v41_residuals.py", trainer_export=os.path.basename(os.path.normpath(a.trainer)), snapshot_args=os.path.join(*a.ck.split(os.sep)[-2:]),
           perturb={k: P[k] for k in ("joint_deg", "joint_vel", "ball_tol_m", "friction_rand", "friction_range", "seed0", "n")}, harness="v4 1.5in, arm 0.6, club 1.15, gate off", summary=S, per_seed=rows)
json.dump(out, open(a.out, "w"), indent=1); print(json.dumps(S, indent=1))
