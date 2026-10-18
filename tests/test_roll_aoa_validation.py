import json, pytest
from pathlib import Path
from data import roll_aoa_validation as v, roll_aoa_addon as a
J = json.load(open(Path(__file__).resolve().parent.parent / "data/references/roll_aoa_validation.json"))

def test_labels_and_no_private():
    assert "MODEL-ONLY" in J["label"] and "MODEL-ONLY" in v.LABEL
    s = json.dumps(J); assert "imit_private" not in s and "mason_swings" not in s and "instagram" not in s.lower()

def test_every_datapoint_has_url_and_tag():
    for d in J["datapoints"]:
        assert d["url"].startswith("http") and d["tag"] in ("fetched", "snippet")
    c = J["counts"]; assert c["total"] == len(J["datapoints"]) == c["fetched"] + c["snippet"]
    assert c["fetched"] == sum(d["tag"] == "fetched" for d in J["datapoints"])

def test_json_matches_code_rebuild():
    dps = v.flag_tm_outliers(v.build_datapoints()); assert [d["id"] for d in dps] == [d["id"] for d in J["datapoints"]]
    assert v.stats(v.residuals(dps))["bias"] == J["stats_normal"]["ALL"]["roll_yd"]["bias"]

def test_trackman_rows_internally_consistent():
    tm = [d for d in J["datapoints"] if d["group"].startswith("tm_")]
    assert len(tm) == 60
    for d in tm: assert d["total_yd"] > d["carry_yd"] and d["ball_mph"] / d["club_mph"] < 1.52

def test_addon_defaults_unchanged():
    assert (a.BASE_ROLL_FRAC, a.DESC_COEF, a.SPIN_COEF) == (0.09, 0.045, 0.00012) and a.FIRMNESS == {"soft": 0.35, "normal": 1.0, "firm": 1.6, "very_firm": 2.0}

def test_residual_sign_convention_and_underprediction_at_low_speed():
    s = J["stats_normal"]
    assert s["group:tm_total_opt"]["roll_yd"]["bias"] < -15      # model under-predicts TrackMan total-optimizer roll
    assert s["club_mph:>=124"]["roll_yd"]["bias"] > 0            # and over-predicts at >=124 mph vs Foresight/long-drive
    assert abs(s["group:foresight"]["roll_yd"]["bias"]) < 3

def test_published_roll_is_roughly_constant_yards_not_proportional():
    sl = J["roll_vs_carry_slopes"]
    for g in ("foresight", "tm_carry_opt"): assert abs(sl[g]["slope_yd_roll_per_yd_carry"]) < 0.06
    assert a.BASE_ROLL_FRAC > 0.06

def test_firmness_multipliers_exceed_data_implied_range():
    f = J["firmness_check"]; assert f["data_implied_multiplier_given_base_roll"]["soft"] > a.FIRMNESS["soft"]; assert f["data_implied_multiplier_given_base_roll"]["firm"] < a.FIRMNESS["firm"]

def test_refit_not_supported_out_of_sample():
    r = J["refit_on_trackman_not_applied"]; assert r["held_out_other_sources"]["mae"] > r["held_out_default_model"]["mae"]

def test_tutelman_launch_good_env_spin_formula_poor_vs_chart():
    k = J["aoa_checks"]; assert k["tutelman_launch_residual_all"]["mae"] < 0.5; assert abs(k["env_formula_spin_residual_all"]["bias"]) > 500

def test_350_roll_needed():
    h = J["high_speed_evidence"]["roll_needed_for_350_total_yd"]; assert h["296"] == pytest.approx(26.3, abs=0.1) and h["293"] > h["296"] > h["299"]
