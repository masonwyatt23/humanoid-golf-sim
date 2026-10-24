"""harness v3d (opt-in) re-grading rules; v3c stays the default."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from eval import harness_v3d as H

def test_spin_band_speed_matched():
    assert H.spin_status(3600, 74) == "pass" and H.spin_status(3600, 90) == "warn"      # 70-85 mph only
    assert H.spin_status(1900, 74) == "warn" and H.spin_status(1900, 90) == "pass"
    assert H.spin_status(3900, 74) == "warn" and H.spin_status(4062, 74) == "fail" and H.spin_status(1100, 74) == "fail"
    assert H.spin_status(3600, 74, v3d=False) == "warn"

def test_pelvis_floor():
    assert H.pelvis_status(250) == "pass" and H.pelvis_status(249.9) == "warn" and H.pelvis_status(None) == "skip"

def test_sequence_rules():
    assert H.sequence_status(dict(pelvis=100, thorax=40, arm=25))[0] == "pass"
    assert H.sequence_status(dict(pelvis=100, thorax=40, arm=40))[0] == "pass"           # thorax/arm tie
    assert H.sequence_status(dict(pelvis=100, thorax=30, arm=55))[0] == "pass"           # 25 ms inversion
    assert H.sequence_status(dict(pelvis=100, thorax=20, arm=55))[0] == "warn"           # 35 ms inversion
    assert H.sequence_status(dict(pelvis=112, thorax=48, arm=12))[0] == "warn"           # arm->club < 20 ms
    assert H.sequence_status(dict(pelvis=30, thorax=40, arm=25))[0] == "warn"            # pelvis not first

def _rob(p10, med, spin=(2600, 2200, 2900)):
    sh = dict(club_speed_mph=dict(median=med, p10=p10, p90=med, status=dict(median="pass", p10="pass", p90="pass")),
              spin_rpm=dict(median=spin[0], p10=spin[1], p90=spin[2], status={}))
    return dict(status="pass", values=dict(contact_frac=1.0, start_direction_pass_frac=1.0, lead_foot_plant_pass_frac=1.0, shot=sh))

def test_club_p10_gate():
    assert H._regrade_robust(_rob(70, 74))["status"] == "pass"                           # 0.946
    r = H._regrade_robust(_rob(60, 74)); assert r["status"] == "fail" and "0.93" in r["why"][0]

def _mk(spin):
    C = {"shot/spin_rpm": dict(status="warn", values=spin), "shot/club_speed_mph": dict(status="pass", values=74.0),
         "swing/peak_speed_pelvis_deg_s": dict(status="warn", values=300.0),
         "swing/kinematic_sequence_timing_ms_before_club_peak": dict(status="warn", values=dict(pelvis=100, thorax=40, arm=30)),
         "swing/kinematic_sequence_order": dict(status="warn", values={}), "mine/robustness": _rob(71, 74)}
    return dict(checks=C)

def test_spin_band_only_flag():
    r = H.apply_v3d_flagged(_mk(3500)); assert r["verdict"] == "not a pass (spin-band-only)" and r["spin_band_only"]
    r = H.apply_v3d_flagged(_mk(2800)); assert r["verdict"] == "PASS" and not r["spin_band_only"]
    assert H.apply_v3d_flagged(_mk(4100))["verdict"] == "FAIL"

FILES = sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results/v5_runs/stageJK_harness_summary/*_v3c_gateoff_gp_arm06.json")))
@pytest.mark.skipif(not FILES, reason="v3c JSONs absent")
def test_v3c_spin_fallback_reproduces_v3c():
    for f in FILES:
        r = json.load(open(f)); C = r["checks"]
        if "shot/spin_rpm" not in C: continue   # no true-contact episode (e.g. K32a 100k at tee 0 with args face_h 0.053: all off-face misses)
        assert H.spin_status(C["shot/spin_rpm"]["values"], C["shot/club_speed_mph"]["values"], v3d=False) == C["shot/spin_rpm"]["status"], f
        rs = C["mine/robustness"]["values"]["shot"]; cm = rs["club_speed_mph"]["median"]
        for q in ("median", "p10", "p90"): assert H.spin_status(rs["spin_rpm"][q], cm, v3d=False) == rs["spin_rpm"]["status"][q], (f, q)
