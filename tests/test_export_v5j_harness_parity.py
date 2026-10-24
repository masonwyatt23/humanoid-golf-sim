"""Regression: render_blender/export_v5j_trajectory.py must build JEnv exactly like the v3 scoring worker
(results/overnight/_j_worker_gp_v3.py), so the exported club speed matches the realism harness.
Bug fixed in 4e5d9f3: the path-free exporter (8dcb9af) passed only 7 configure() keys and no res_mult, so K25b_s56 400k
exported at 21.7 mph vs the harness's 72.2 mph.

EXPORTER_PATH (env) overrides the exporter file under test (used to confirm these tests FAIL on the pre-fix copy).
Slow test env: HGS_SNAP_DIR (dir holding K25b_s56_400000/), HGS_TRAINER_EXPORT (read-only Trainer export, e.g. _ro_trainer_5cb4d43),
HGS_PYTHON (interpreter with mujoco + stable_baselines3). Defaults are siblings of this repo; skipped cleanly when absent."""
import ast, json, os, subprocess, sys, tempfile
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPORTER = Path(os.environ.get("EXPORTER_PATH", ROOT / "render_blender" / "export_v5j_trajectory.py"))
WORKER = ROOT / "results" / "overnight" / "_j_worker_gp_v3.py"
# Explicit fallback (worker may be untracked on main): v3 worker configure() keys as of 47f30f8 / 4e5d9f3.
WORKER_KEYS_EXPLICIT = {"res_mult", "xf_hard", "grf_lo", "grf_w", "xf_cap_lo", "xf_cap_w", "track_floor", "ord2_w", "launch_w", "desc_w",
                        "dloft_w", "spin_lo_w", "smash_w", "spin_w", "spin_hi", "spin_scale", "fine_grf", "launch_hi", "dl_lo", "dl_hi", "aoa_lo",
                        "spd_w", "pel_w", "pel_t_w", "pel_dps", "pel_t_lo", "pel_t_hi", "sep_w", "ctr_w", "ctrl_dt"}


def configure_keys(path):
    """Keyword names passed to <x>.configure(...) in a script: explicit kwargs plus **{k: ... for k in <tuple or module-level tuple>}."""
    tree = ast.parse(Path(path).read_text())
    consts = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, (ast.Tuple, ast.List)):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    consts[t.id] = n.value
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "configure"]
    assert len(calls) == 1, f"expected exactly one configure() call in {path}, found {len(calls)}"
    keys = set()
    for kw in calls[0].keywords:
        if kw.arg is not None:
            keys.add(kw.arg); continue
        v = kw.value
        assert isinstance(v, ast.DictComp) and len(v.generators) == 1, "unsupported **kwargs form in configure()"
        it = v.generators[0].iter
        if isinstance(it, ast.Name):
            it = consts[it.id]
        keys |= {ast.literal_eval(e) for e in it.elts}
    return keys


def test_exporter_configure_keys_match_v3_worker():
    exp = configure_keys(EXPORTER)
    ref = configure_keys(WORKER) if WORKER.exists() else WORKER_KEYS_EXPLICIT
    assert exp == ref, f"missing in exporter: {sorted(ref - exp)}; extra: {sorted(exp - ref)}"


def test_explicit_key_list_matches_worker():
    if not WORKER.exists():
        pytest.skip("v3 worker not in this checkout")
    assert configure_keys(WORKER) == WORKER_KEYS_EXPLICIT


def test_exporter_has_no_machine_paths():
    assert "/workspace/" not in EXPORTER.read_text()


# ---------------- slow integration ----------------
CK_NAME = "K25b_s56_400000"
_V3C = "realism_v5_K25b_s56_400k_dtfix_newchecks_v3c_gateoff_gp_arm06.json"
# full (per-episode) JSON: $HGS_V3C_JSON, else results/overnight/ (Evaluator-local); the committed slim copy has no per-episode rows
V3C_JSON = Path(os.environ.get("HGS_V3C_JSON", ROOT / "results" / "overnight" / _V3C))
SEED = 4000


def _snap_ckpt():
    cands = [os.environ.get("HGS_SNAP_DIR")] if os.environ.get("HGS_SNAP_DIR") else [
        ROOT.parent / "humanoid-golf-scott" / "results" / "v5_runs" / "_snap", ROOT.parent / "humanoid-golf-scott" / "results" / "v5_runs" / "_evalsnap"]
    for c in cands:
        b = Path(c) / CK_NAME / "ckpt_400000"
        if b.with_suffix(".zip").exists() and Path(str(b) + "_vecnorm.pkl").exists() and (b.parent / "args.json").exists():
            return b
    return None


@pytest.mark.slow
def test_exported_club_speed_matches_harness_K25b_seed4000():
    ck = _snap_ckpt()
    tr = Path(os.environ.get("HGS_TRAINER_EXPORT", ROOT.parent / "_ro_trainer_5cb4d43"))
    py = os.environ.get("HGS_PYTHON", sys.executable)
    if ck is None or not (tr / "train" / "v5_train_j.py").exists() or not WORKER.exists() or not V3C_JSON.exists():
        pytest.skip("K25b checkpoint, Trainer export, v3 worker or v3c JSON absent")
    if "episodes" not in json.load(open(V3C_JSON)).get("golfphys_total", {}):
        pytest.skip("v3c JSON has no per-episode rows (slim copy)")
    A = json.load(open(ck.parent / "args.json"))
    if A.get("keys") and A["keys"] != "none" and not (tr / A["keys"]).exists():
        pytest.skip("reference keys file absent in Trainer export")
    if subprocess.run([py, "-c", "import mujoco, stable_baselines3"], capture_output=True).returncode:
        pytest.skip("interpreter lacks mujoco/stable_baselines3 (set HGS_PYTHON)")
    env = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", PYTHONPATH=str(ROOT), V5_REPO=str(tr))
    with tempfile.TemporaryDirectory() as td:
        # live harness episode: the same worker + argv the v3 wrapper uses (club 1.15, arm 0.6, gate off), seed 4000, 1 episode
        w = Path(td) / "w.json"
        subprocess.run([py, str(WORKER), str(tr), str(ck), "1.15", str(SEED), "1", str(w), "0.6", "off"], env=env, check=True, capture_output=True, timeout=900)
        hep = json.load(open(w))["eps"][0]["shot"]
        # tie the live episode to the committed v3c JSON (per-episode golfphys row for seed 4000)
        row = next(r for r in json.load(open(V3C_JSON))["golfphys_total"]["episodes"] if r["seed"] == SEED)
        assert abs(hep["carry_m_noroll"] * 1.0936133 - row["env_carry_yd"]) < 0.5, "live harness episode no longer reproduces the v3c JSON"
        out = Path(td) / "x.npz"
        r = subprocess.run([py, str(EXPORTER), str(ck), "--out", str(out), "--seed", str(SEED)], env=env, capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-2000:]
        exp = json.load(open(out.with_suffix(".json")))["episode"]["club_speed_mph"]
    harn = hep["club_speed_mph"]
    print(f"exported {exp:.3f} mph vs harness {harn:.3f} mph")
    assert abs(exp - harn) <= max(1.0, 0.02 * harn), f"exported {exp:.2f} mph vs harness {harn:.2f} mph"
