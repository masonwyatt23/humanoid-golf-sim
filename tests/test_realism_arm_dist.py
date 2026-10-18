from eval.realism_check import resolve_arm_dist

def test_arm_dist_autodetect():
    assert resolve_arm_dist("/x/results/v5_runs/stageA_s0/final") == 0.0
    for p in ("/x/stageB4_s1/final", "/x/_stageB1_tap_failed/stageB_s0/ckpt_800000", "/x/stageC_s0/ckpt_100000", "/x/other"):
        assert resolve_arm_dist(p) == 0.6

def test_arm_dist_explicit_wins():
    assert resolve_arm_dist("/x/stageB4_s1/final", 0) == 0.0
    assert resolve_arm_dist("/x/stageA_s0/final", 0.6) == 0.6
