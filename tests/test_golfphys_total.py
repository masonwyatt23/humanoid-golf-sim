"""eval/golfphys_total.py vs published TrackMan carry/total optimizer rows (data/references/roll_aoa_validation.json) and structural properties."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
from eval.golfphys_total import golfphys_total as G
ROWS = [x for x in json.load(open(ROOT / "data/references/roll_aoa_validation.json"))["datapoints"] if x["id"].startswith(("tm_carry_", "tm_total_")) and x.get("total_yd") and x.get("carry_yd")]

def test_matches_trackman_rows():
    d = [(G(x["ball_mph"], x["launch_deg"], x["spin_rpm"]), x) for x in ROWS]
    assert len(d) >= 40
    assert max(abs(r["carry_yd"] - x["carry_yd"]) for r, x in d) < 8
    assert max(abs(r["total_yd"] - x["total_yd"]) for r, x in d) < 20
    assert abs(sum(r["total_yd"] - x["total_yd"] for r, x in d) / len(d)) < 5
    assert max(abs(r["total_over_carry"] - x["total_yd"] / x["carry_yd"]) for r, x in d) < 0.15

def test_roll_adds_distance_and_noroll_carry_equals_carry():
    r = G(160, 12, 2500)
    assert r["total_yd"] > r["carry_yd"] and r["noroll_carry_yd"] == r["carry_yd"] and 1.05 < r["total_over_carry"] < 1.2

def test_sidespin_sign_roundtrip_and_symmetry():
    a, b = G(160, 12, 2500, 500), G(160, 12, 2500, -500)
    assert abs(a["sidespin_rpm"] - 500) < 1e-6 and abs(b["sidespin_rpm"] + 500) < 1e-6 and abs(a["total_yd"] - b["total_yd"]) < 1.0

def test_low_launch_slow_ball_rolls_much_more():       # shallow descent -> large roll; this is why a 59 yd-carry shot reads total/carry >> 1.25
    assert G(85, 12, 2500)["total_over_carry"] > 1.4
