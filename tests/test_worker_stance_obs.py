"""Worker flag forwarding for Trainer --stance_obs (92703d2e): the eval worker must forward stance_obs from args.json, and only when set."""
import ast, os
W = os.path.join(os.path.dirname(__file__), "..", "results", "overnight", "_j_worker_gp_v3.py")

def _cfg_tuple():
    t = ast.parse(open(W).read())
    for n in ast.walk(t):
        if isinstance(n, ast.Assign) and any(getattr(x, "id", None) == "CFG" for x in n.targets):
            return tuple(ast.literal_eval(n.value))
    raise AssertionError("CFG not found")

def _configure(obj, kw):   # same rule as train.v5_train_j.JEnv.configure: None values are skipped
    for k, v in kw.items():
        if v is not None: setattr(obj, k, v)

def test_stance_obs_in_cfg():
    assert "stance_obs" in _cfg_tuple()

def test_old_snapshot_unchanged():
    class E: pass
    e = E(); A = {"tee_dz": 0.02}   # args.json without stance_obs
    _configure(e, {k: A.get(k) for k in _cfg_tuple()})
    assert not hasattr(e, "stance_obs")

def test_new_snapshot_forwarded():
    class E: pass
    e = E(); _configure(e, {k: {"stance_obs": True}.get(k) for k in _cfg_tuple()})
    assert e.stance_obs is True
