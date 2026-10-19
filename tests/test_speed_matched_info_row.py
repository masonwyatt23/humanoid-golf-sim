"""The INFO-ONLY row mine/total_over_carry_speed_matched (golfphys model, info only, not gating) must never change the overall verdict or the pass/warn/fail/n_checks counts."""
import pytest
from eval import swing_realism as sr

def _row(st): return dict(status=st, passed=(st == "pass"), values=None, why=[], ref=None, tag="derived")

@pytest.mark.parametrize("statuses,verdict", [(["pass", "pass", "skip"], "PASS"), (["pass", "warn", "skip"], "WARN"), (["pass", "warn", "fail"], "FAIL")])
@pytest.mark.parametrize("ball_mph,actual", [(90.0, 1.36), (95.0, 1.0), (0.0, None)])   # real info row, info row with an 'impossible' actual, and the skip form
def test_info_row_does_not_change_verdict_or_counts(statuses, verdict, ball_mph, actual):
    C = {f"c{i}": _row(s) for i, s in enumerate(statuses)}; before = sr.summarize(C)
    k, v = sr.info_total_over_carry_speed_matched(ball_mph, actual); C2 = dict(C); C2[k] = v; after = sr.summarize(C2)
    assert before["verdict"] == after["verdict"] == verdict
    for f in ("n_pass", "n_warn", "n_fail", "n_checks"): assert before[f] == after[f], f
    assert v["status"] in ("info", "skip") and v["gating"] is False and not v["passed"]

def test_row_label_and_caveat():
    k, v = sr.info_total_over_carry_speed_matched(90.0, 1.36)
    assert k == "mine/total_over_carry_speed_matched (golfphys model, info only, not gating)" and v["status"] == "info"
    w = v["why"][0]; assert "normal turf" in w and "tour speeds" in w and "UNCALIBRATED" in w and "does not affect the verdict" in w
    x = v["values"]; assert x["ball_mph"] == 90.0 and x["actual_total_over_carry"] == 1.36
    assert 7 <= x["at_launch_deg"] <= 16 and 1800 <= x["at_backspin_rpm"] <= 3000 and x["min_total_over_carry"] > 1.0

def test_sweep_minimum_is_a_minimum():
    from eval.golfphys_total import golfphys_total
    b = sr.speed_matched_min_total_over_carry(90.0)
    for la, sp in ((7, 1800), (12, 2400), (16, 3000), (b["at_launch_deg"], b["at_backspin_rpm"])):
        assert golfphys_total(90.0, la, sp)["total_over_carry"] >= b["min_total_over_carry"] - 1e-12
