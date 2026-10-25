"""Default-path baseline check (read-only). Confirms that the default env, reward and CLI are unchanged after a port.

Run from the repo root:
    OMP_NUM_THREADS=2 PYTHONPATH=. python scripts/default_baseline_check.py [--strike-ckpt CKPT --strike-ref CSV]

Checks (expected values are for the current default harness/env; update them only with a deliberate, documented change):
  1. head   sha256 over V5 model arrays (LH, L=0.87 and 1.15) + V5GolfEnv seed 1 after 200 zero-action steps (tee, qpos);
            the realistic head's face limits and crown tee dz (mm).
  2. reward JEnv with results/v5_runs/stageK32_ref_s1/tuned_keys_flat.json, res_scale 0.5, t_down 0.3; seeds 1,2,3;
            reset(seed=s), actions rng.uniform(-0.3, 0.3) with np.random.default_rng(s) until done; md5 of json.dumps(rewards).
  3. guard  train/v5_train_j.py parsed with `--keys none` (no training): every flag in `extra` that defaults off is None,
            and make() builds an env without the FLAG GUARD tripping.
  4. strike (optional; the checkpoint is not in git) scripts/strike_log.py on the K32a 200k checkpoint must be
            byte-identical to a reference CSV. Pass --strike-ckpt / --strike-ref, or set HGS_K32A_CKPT / HGS_K32A_STRIKE_REF.
Exit code 0 only if every check that ran matched.
"""
import argparse, hashlib, json, os, subprocess, sys, tempfile, filecmp
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
EXP_HEAD = "c92f4d05804c18a09eb4c11b473839ad17ae221719b3077b63083f08ec29eb3a"
EXP_REALISTIC = ((0.027, 0.0525), 4.13)
EXP_REWARD = ("fe76b45d3ef9bcaa82a2650097f87218", 111, 47.29053746950751)
OFF_KEYS = ['fast_env', 'plant_h_w', 'res_l2_w', 'launch_lo_w', 'launch_lo', 'sd_w', 'loc_noclip', 'dz_lin_w', 'dz_tgt', 'dy_lin_w', 'dy_tgt', 'dz_gate', 'dz_zero', 'rsi', 'noise_ramp', 'miss_w', 'miss0_w']


def check_head():
    from env.v5_body import build_model
    from env.v5_golf_env import V5GolfEnv
    h = hashlib.sha256()
    for L in (0.87, 1.15):
        m, _ = build_model("LH", L)
        for a in ('body_mass', 'body_inertia', 'body_ipos', 'geom_size', 'geom_pos', 'geom_quat', 'geom_type', 'qpos0', 'site_pos'):
            h.update(np.ascontiguousarray(getattr(m, a)).tobytes())
    e = V5GolfEnv(); e.reset(seed=1)
    for _ in range(200): e.step(np.zeros(e.action_space.shape))
    h.update(np.asarray(e.tee).tobytes()); h.update(e.d.qpos.tobytes())
    e2 = V5GolfEnv(head="realistic"); e2.reset(seed=1); real = (tuple(e2.face_limits()), round(e2._crown_tee_dz() * 1e3, 2))
    print("head", h.hexdigest(), "realistic", real)
    return h.hexdigest() == EXP_HEAD and real == EXP_REALISTIC


def check_reward():
    from train.v5_train_j import JEnv
    keys = {tuple(k.split('|')): v for k, v in json.load(open(os.path.join(ROOT, 'results/v5_runs/stageK32_ref_s1/tuned_keys_flat.json'))).items()}
    out = []
    for seed in (1, 2, 3):
        e = JEnv(seed=seed, keys=keys, res_scale=0.5, t_down=0.3); o, _ = e.reset(seed=seed); rng = np.random.default_rng(seed); done = False; R = []
        while not done:
            o, r, te, tr, info = e.step(rng.uniform(-0.3, 0.3, e.action_space.shape)); R.append(float(r)); done = te or tr
        out.append(R)
    got = (hashlib.md5(json.dumps(out).encode()).hexdigest(), sum(map(len, out)), sum(sum(x) for x in out))
    print("reward", *got)
    return got == EXP_REWARD


def check_guard():
    src = open(os.path.join(ROOT, 'train/v5_train_j.py')).read(); i = src.index('    venv = SubprocVecEnv(')
    src = src[:i] + "    _G['extra'] = extra; _G['env'] = make(0, a.seed, a.dt, keys, a.res_scale, a.t_down, extra)()\n"
    G = {'__name__': '__main__'}; G['_G'] = G; cwd = os.getcwd(); argv = sys.argv
    try:
        os.chdir(tempfile.mkdtemp()); sys.argv = ['v5_train_j', '--keys', 'none']   # the script makes its results dir relative to cwd
        exec(compile(src, 'v5_train_j', 'exec'), G)
    except SystemExit as e:
        print("guard FLAG GUARD tripped:", e); return False
    finally:
        os.chdir(cwd); sys.argv = argv
    ok = all(G['extra'][k] is None for k in OFF_KEYS) and not getattr(G['env'].env, 'fast_env', False)
    print("guard passed; off-by-default keys None:", ok)
    return ok


def check_strike(ckpt, ref):
    out = os.path.join(tempfile.mkdtemp(), 'strike.csv')
    subprocess.run([sys.executable, os.path.join(ROOT, 'scripts/strike_log.py'), out, ckpt], cwd=ROOT, check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, OMP_NUM_THREADS=os.environ.get('OMP_NUM_THREADS', '2')))
    same = filecmp.cmp(out, ref, shallow=False); print("strike_log byte-identical:", same); return same


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--strike-ckpt', default=os.environ.get('HGS_K32A_CKPT')); ap.add_argument('--strike-ref', default=os.environ.get('HGS_K32A_STRIKE_REF'))
    ap.add_argument('--only', choices=['head', 'reward', 'guard', 'strike'])
    a = ap.parse_args(); os.chdir(ROOT); res = {}
    for name, fn in (('head', check_head), ('reward', check_reward), ('guard', check_guard)):
        if a.only in (None, name): res[name] = fn()
    if a.only in (None, 'strike'):
        if a.strike_ckpt and a.strike_ref: res['strike'] = check_strike(a.strike_ckpt, a.strike_ref)
        elif a.only == 'strike': sys.exit("set --strike-ckpt/--strike-ref or HGS_K32A_CKPT/HGS_K32A_STRIKE_REF")
        else: print("strike skipped (set HGS_K32A_CKPT and HGS_K32A_STRIKE_REF to run it)")
    print("RESULT", "OK" if all(res.values()) else "MISMATCH", res); sys.exit(0 if all(res.values()) else 1)
