import json
from pathlib import Path
from golfphys.params import load_params
from data.golfphys_spin_audit import proposed_params, load_rows, stats

R = Path(__file__).resolve().parent.parent / "data/references/golfphys_spin_audit.json"


def test_defaults_unchanged_and_opt_in():
    base = load_params(); p = proposed_params()
    assert abs(base.s_t - 0.8657) < 1e-3 and base.s_t_slope == 0.0
    assert p.s_t != base.s_t and json.load(open(R))["proposal"]["opt_in"] is True


def test_split_by_source_and_heldout_improves():
    rows = load_rows()
    assert all(r["label"].startswith("measured") for r in rows)
    held = [r for r in rows if r["split"] == "held_out"]
    assert held and all("female" in r["group"] for r in held)
    assert stats(held, proposed_params())["rmse_rpm"] < stats(held, load_params())["rmse_rpm"]
