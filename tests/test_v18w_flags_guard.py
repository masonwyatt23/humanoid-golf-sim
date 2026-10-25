"""V18w reproducibility flags (tail_frac, tail_pool, reground_frac, plant_warn_w/_turn, plant_d_w; init_opt, init_retrms, spd_cur):
all default off, env flags are covered by the FLAG GUARD, and configs/V18w_s661_args.json only uses CLI args that exist on main."""
import json, os, sys, tempfile
from pathlib import Path
import pytest
pytest.importorskip("mujoco"); pytest.importorskip("stable_baselines3")
ROOT = Path(__file__).resolve().parents[1]
NEW_ENV = ['tail_frac', 'tail_pool', 'reground_frac', 'plant_warn_w', 'plant_warn_turn', 'plant_d_w']


def _run(argv):
    src = (ROOT / 'train/v5_train_j.py').read_text(); i = src.index('    venv = SubprocVecEnv(')
    src = src[:i] + "    _G['a'] = a; _G['extra'] = extra; _G['make'] = make; _G['env'] = make(0, a.seed, a.dt, keys, a.res_scale, a.t_down, extra)()\n"
    G = {'__name__': '__main__'}; G['_G'] = G; cwd, old = os.getcwd(), sys.argv
    sys.path.insert(0, str(ROOT))
    try:
        os.chdir(tempfile.mkdtemp()); sys.argv = ['v5_train_j', '--keys', 'none'] + argv
        exec(compile(src, 'v5_train_j', 'exec'), G)
    finally:
        os.chdir(cwd); sys.argv = old
    return G


def test_defaults_off():
    G = _run([])
    assert all(G['extra'][k] is None for k in NEW_ENV)
    a = G['a']; assert a.init_opt is False and a.init_retrms is False and a.spd_cur is None


def test_env_flags_live_and_guarded():
    pool = str(ROOT / 'results/v10_diag/tail/tail_pool_20000_99999.npy')
    G = _run(['--tail_frac', '0.21', '--tail_pool', pool, '--reground_frac', '0.5', '--plant_warn_w', '1', '--plant_warn_turn', '11', '--plant_d_w', '1'])
    e = G['env']
    while not hasattr(e, 'tail_frac'): e = e.env   # Monitor -> JEnv
    assert (e.tail_frac, e.tail_pool, e.reground_frac, e.plant_warn_w, e.plant_d_w) == (0.21, pool, 0.5, 1.0, 1.0)
    J = G['JEnv']; orig = J.configure
    for k in NEW_ENV:   # if configure() ever drops one of these flags, the FLAG GUARD must abort
        J.configure = lambda self, _k=k, **kw: orig(self, **{x: v for x, v in kw.items() if x != _k})
        try:
            with pytest.raises(SystemExit, match="FLAG GUARD"):
                G['make'](0, 0, 0.002, None, 0.5, 0.3, G['extra'])()
        finally:
            J.configure = orig


def test_v18w_args_all_cli():
    src = (ROOT / 'train/v5_train_j.py').read_text()
    keys = json.loads((ROOT / 'configs/V18w_s661_args.json').read_text())
    missing = [k for k in keys if f'"--{k}"' not in src]
    assert not missing, missing
