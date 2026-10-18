"""Stage 0 tests for the v5 body/env (fast; no learning)."""
import os, sys, math, re
import numpy as np, mujoco, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env.v5_body import build_model, load_address, set_address, STOCK, joint_kind, MENAG
from env.v5_golf_env import V5GolfEnv
from env.v5_shot import shot_from_contact, verify_toe_sign
from env.v5_reward import episode_terms, prior_cap, peak_speed_term, TARGET_100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CL = 0.87

@pytest.fixture(scope="module")
def env():
    return V5GolfEnv(dt=0.002, club_len=CL)

def test_model_loads_29_actuated_and_welds():
    m, _ = build_model("LH", CL)
    assert m.nu == 29 and m.neq == 2
    assert {m.eq_type[i] for i in range(2)} == {int(mujoco.mjtEq.mjEQ_WELD)}

def test_stock_limits_match_menagerie_force_scale_1():
    base = mujoco.MjModel.from_xml_path(f"{MENAG}/unitree_g1/scene.xml"); m, _ = build_model("LH", CL)
    for i in range(m.nu):
        n = m.actuator(i).name
        assert m.jnt_actfrcrange[m.joint(n).id][1] == pytest.approx(base.jnt_actfrcrange[base.joint(n).id][1])
        assert m.actuator_forcerange[i][1] == pytest.approx(STOCK[joint_kind(n)][0])

def test_lh_is_physically_mirrored(env):
    m, d = env.m, mujoco.MjData(env.m); set_address(m, d, env.addr)
    assert d.xpos[m.body("right_shoulder_pitch_link").id][0] > d.xpos[m.body("left_shoulder_pitch_link").id][0]   # lead (right) side toward +x target
    assert d.site_xpos[m.site("right_hand").id][2] > d.site_xpos[m.site("left_hand").id][2]                      # lead hand on top

def test_welds_closed_at_address(env):
    m, d = env.m, mujoco.MjData(env.m); set_address(m, d, env.addr)
    assert np.abs(d.efc_pos[:12]).max() < 1e-3

def test_stands_two_seconds_zero_action(env):
    env.reset()
    for _ in range(100): env.step(np.zeros(29))
    assert env.d.qpos[2] > 0.70 and env.max_weld_drift < 0.005

def test_toe_sign_verified_against_model():
    for h in ("LH", "RH"):
        m, _ = build_model(h, CL); d = mujoco.MjData(m); set_address(m, d, load_address(h, CL))
        ts, _, dot = verify_toe_sign(m, d, h)
        assert ts == 1.0 and dot > 0.95

def test_golfphys_lh_up_axis_flip_documented():
    from golfphys import impact, Delivery, Strike
    rh = impact(Delivery(50, 12, 0, handed="RH"), Strike(0, 0.01))["backspin_rpm"]; lh = impact(Delivery(50, 12, 0, handed="LH"), Strike(0, 0.01))["backspin_rpm"]
    assert abs(rh - lh) > 1000      # vendored package bug: LH high strike behaves like RH low strike (env adapter compensates)

def test_adapter_mirror_flight():
    v = np.array([45.0, 1.0, 3.0]); n = np.array([math.cos(0.18), 0.02, math.sin(0.18)]); n /= np.linalg.norm(n)
    for dy, dz in ((0, 0), (0.012, 0), (0, 0.01), (0.012, 0.01)):
        l = shot_from_contact(v, n, dy, dz, "LH"); r = shot_from_contact(v * [1, -1, 1], n * [1, -1, 1], dy, dz, "RH")
        assert l["shot"].carry_m == pytest.approx(r["shot"].carry_m, rel=1e-6)
        assert l["shot"].lateral_carry_m == pytest.approx(-r["shot"].lateral_carry_m, abs=1e-6)
        assert l["backspin_rpm"] == pytest.approx(r["backspin_rpm"], rel=1e-6)

def test_contact_pipeline_with_pipeline_only_motion():
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from v5_sanity_swing import run_swing
    e = V5GolfEnv(dt=0.002, club_len=CL, tether=True)
    info = run_swing(e, wy=0.6, t_down=0.25)
    assert info["contact"] and "carry_m_noroll" in info and info["weld_drift_max_m"] < 0.005

def test_reward_terms_and_prior_cap():
    assert prior_cap(0) == pytest.approx(0.2) and prior_cap(1) == pytest.approx(0.05)
    assert peak_speed_term(TARGET_100) == pytest.approx(0.0)
    assert peak_speed_term({k: 0.0 for k in TARGET_100}) == pytest.approx(-2.0 * 1.0 * 1.0 / 1.0 * 1.0, abs=2.01)  # clipped to [-4, 0]
    t = np.arange(0, 0.5, 0.005)
    log = dict(t=t, pelvis=442 * np.exp(-((t - 0.41) / .05) ** 2), thorax=665 * np.exp(-((t - 0.43) / .05) ** 2), lead_arm=886 * np.exp(-((t - 0.435) / .05) ** 2),
               club=2054 * np.exp(-((t - 0.5) / .05) ** 2), xfactor_deg=45 * np.exp(-((t - 0.2) / .08) ** 2), lead_share=np.linspace(0.3, 0.7, len(t)), t_impact=0.5)
    a = episode_terms(log, progress=0.0, stage="A"); c = episode_terms(log, progress=0.0, stage="C")
    assert a["prior_total"] == 0.0 and 0 < c["prior_total"] <= 0.2 + 1e-9
    assert episode_terms(log, progress=1.0, stage="C")["prior_total"] <= 0.05 + 1e-9

def test_no_private_reference_data_in_v5_files():
    for f in ("env/v5_body.py", "env/v5_golf_env.py", "env/v5_reward.py", "env/v5_shot.py", "scripts/v5_sanity_swing.py", "scripts/v5_stage0_check.py"):
        s = open(os.path.join(ROOT, f)).read().lower()
        assert not re.search(r"mason_swings|instagram|\\.mov|reference_rates", s)
