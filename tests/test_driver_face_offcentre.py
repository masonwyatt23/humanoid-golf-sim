import json
from pathlib import Path
import pytest
from data.driver_face_offcentre import face_edge_adjust, status

C = dict(smash=1.449, spin_rpm=2568, launch_deg=14.55, ball_speed_mph=107.2, centre_dz_mm=0.0)


def test_refs_labelled():
    d = json.load(open(Path(__file__).resolve().parent.parent / "data/references/driver_face_offcentre_refs.json"))
    assert all(r["url"] and r["label"] for r in d["rows"])


def test_gate_tiers():
    assert status(0) == "measured_range" and status(-13) == "info_outside_measured"
    assert status(-15) == "info_outside_measured" and status(-22) == "warn" and status(-25) == "warn" and status(-31) == "fail"
    r = face_edge_adjust(C, -31)
    assert r["valid"] is False and r["within_sim_box"] is True
    assert face_edge_adjust(C, -33)["within_sim_box"] is False


def test_capped_and_linear():
    a, b = face_edge_adjust(C, -12.7), face_edge_adjust(C, -25)
    assert abs(a["spin_rpm_capped"] - b["spin_rpm_capped"]) < 1e-6
    assert abs(b["spin_rpm_linear"] - 3497) < 5 and abs(face_edge_adjust(C, -22)["spin_rpm_linear"] - 3386) < 5
    assert b["smash"] < a["smash"] < C["smash"]


def test_rejects_non_centre_input():
    with pytest.raises(ValueError):
        face_edge_adjust(dict(C, centre_dz_mm=-10.0), -10)
    with pytest.raises(ValueError):
        face_edge_adjust({k: v for k, v in C.items() if k != "centre_dz_mm"}, -10)
    face_edge_adjust(dict({k: v for k, v in C.items() if k != "centre_dz_mm"}, y_high_m=0.0), -10)


def test_r2207_table():
    from data.driver_face_offcentre import r2207_ratio
    assert abs(r2207_ratio(0) - 1.0) < 1e-9 and r2207_ratio(-15) < 0.96 and r2207_ratio(-25) < r2207_ratio(-21)
    d = json.load(open(Path(__file__).resolve().parent.parent / "data/references/driver_face_offcentre_refs.json"))
    r = [x for x in d["rows"] if x["id"].startswith("r2207_fig")]
    assert len(r) == 2 and all(x["label"] == "derived from digitized figure, approximate" for x in r)  # raw digitized CSV is held locally, not needed
