"""Strike-gate flag plumbing for eval.realism_check --env v5 (default OFF; value forwarded to _v5_worker as argv[8])."""
import os
import argparse, re
from pathlib import Path
from eval import realism_check as RC

def _a(g=None):
    return argparse.Namespace(club_len=1.15, eps_per_seed=2, strike_gate_nx=g)

def test_default_off():
    assert RC.worker_args(_a(), "/r", "/c", 0.6, 4000)[-1] == "off"
    assert "OFF" in RC.gate_label(None)

def test_on_forwarded():
    args = RC.worker_args(_a(0.25), "/r", "/c", 0.6, 4000)
    assert args[-1] == "0.25" and args[-2] == "0.6" and "0.25" in RC.gate_label(0.25)

def test_worker_mirrors_trainer_definition():
    w = Path(RC.ROOT, "eval", "_v5_worker.py").read_text()
    assert "e.env.strike_gate_nx = GATE" in w and "'off'" in w
    tr = os.environ.get("HGS_TRAINER_REPO")
    t = Path(tr, "env", "v5_golf_env.py") if tr else None
    if t is not None and t.exists():  # condition the Trainer's env applies (documented in the worker docstring)
        assert re.search(r"n_\[0\] >= self\.strike_gate_nx and v_\[0\] > 0 and float\(np\.dot\(v_, n_\)\) > 0", t.read_text())
