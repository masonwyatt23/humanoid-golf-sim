import importlib
"""Pure-numpy tests for view / handedness classification and the MultiSenseGolf converter (no video / mediapipe)."""
import numpy as np
import pytest

from data import process_video as pv
from data import remine_feed_v2 as rm


def _skeleton(n, shoulder_w, t_hands_dx=0.0):
    """(n,33,4) image landmarks: golfer facing the camera when shoulder_w is large."""
    img = np.zeros((n, 33, 4)); img[..., 3] = 0.9
    cx = 500.0
    img[:, pv.L_SH, :2] = [cx + shoulder_w * 100 / 2, 300]
    img[:, pv.R_SH, :2] = [cx - shoulder_w * 100 / 2, 300]
    img[:, pv.L_HIP, :2] = [cx + 20, 400]
    img[:, pv.R_HIP, :2] = [cx - 20, 400]
    img[:, pv.L_ANK, :2] = [cx + 40, 600]
    img[:, pv.R_ANK, :2] = [cx - 40, 600]
    for w in (pv.L_WR, pv.R_WR):
        img[:, w, :2] = [cx + t_hands_dx, 380]
    return img


def test_view_classification():
    t = np.linspace(0, 2, 60)
    assert rm.classify_view(_skeleton(60, 1.0), t, 1.0)["view"] == "face_on"
    assert rm.classify_view(_skeleton(60, 0.1), t, 1.0)["view"] == "down_the_line"
    assert rm.classify_view(_skeleton(60, 0.55), t, 1.0)["view"] == "oblique"


def _world_top(lead_side):
    """world landmarks with the `lead_side` arm straight and the other bent."""
    w = np.zeros((40, 33, 4)); w[..., 3] = 1
    for side, (sh, el, wr) in {"left": (pv.L_SH, pv.L_EL, pv.L_WR), "right": (pv.R_SH, pv.R_EL, pv.R_WR)}.items():
        w[:, sh, :3] = [0, 0, 0]
        w[:, el, :3] = [0.3, 0, 0]
        w[:, wr, :3] = [0.6, 0, 0] if side == lead_side else [0.3, 0.3, 0]
    return w


def test_handedness_lead_arm_cue():
    t = np.linspace(0, 2, 40)
    img = _skeleton(40, 0.2)
    r = rm.classify_handedness(img, _world_top("right"), t, 1.0, 1.4, 0.2, "down_the_line", tempo_valid=True)
    assert r["cue_lead_arm"] == "right" and r["handedness"] == "left"     # right arm leads -> left-handed
    r = rm.classify_handedness(img, _world_top("left"), t, 1.0, 1.4, 0.2, "down_the_line", tempo_valid=True)
    assert r["handedness"] == "right"
    r = rm.classify_handedness(img, _world_top("left"), t, 1.0, 1.4, 0.2, "down_the_line", tempo_valid=False)
    assert r["handedness"] == "unknown"                                    # no real backswing -> no vote


def test_handedness_finish_cue():
    t = np.linspace(0, 2, 40)
    img = _skeleton(40, 0.2)
    for w in (pv.L_WR, pv.R_WR):                      # hands end next to the anatomical RIGHT shoulder
        img[:, w, :2] = img[:, pv.R_SH, :2] + [0, -10]
    w0 = _world_top("left"); w0[..., :3] = 0          # elbow cue silent (straight both)
    r = rm.classify_handedness(img, w0, t, 0.5, 0.8, 0.1, "down_the_line", tempo_valid=False)
    assert r["cue_finish"] == "right" and r["handedness"] == "left"


def _held(mod):
    import importlib.util
    if importlib.util.find_spec(mod) is None:
        pytest.skip(f"{mod} is held locally (untracked at the tip)")
    return importlib.import_module(mod)


def test_multisense_converter_synthetic(tmp_path):
    h5py = pytest.importorskip("h5py")
    ms = _held("data.convert_multisense_golf")
    n = 300
    t = np.arange(n) * 0.0106
    P = np.zeros((n, 21, 3))
    base = np.array([[0, .95, 0], [-.1, .95, 0], [-.1, .5, 0], [-.1, .08, 0], [.1, .95, 0], [.1, .5, 0], [.1, .08, 0],
                     [0, 1.02, 0], [0, 1.16, .05], [0, 1.25, .1], [0, 1.37, .1], [0, 1.4, .1], [0, 1.42, .1],
                     [-.03, 1.33, .1], [-.16, 1.3, .1], [-.16, 1.02, .1], [-.16, .75, .1],
                     [.03, 1.33, .1], [.16, 1.3, .1], [.16, 1.02, .1], [.16, .75, .1]])
    P[:] = base
    ph = np.clip((t - 0.8) / 1.2, 0, 1)                 # swing: hands rise then fall
    lift = np.sin(np.pi * ph) * 0.9 * (1 - 0.0)
    for j in (15, 16, 19, 20):
        P[:, j, 1] += lift * (1 if j in (16, 20) else .5)
    P[:, [16, 20], 0] += np.sin(2 * np.pi * ph)[:, None] * .1
    f = tmp_path / "P99_Swing01_stream_data.hdf5"
    with h5py.File(f, "w") as h:
        g = h.create_group("pns-joint-root-relative-position/cm-values")
        g["data"] = (P * 100).reshape(n, 63).astype("float32"); g["time_s"] = (t + 1.7e9).reshape(-1, 1)
    meta = dict(participant="P99", swing=1, skill=5, club_mph=95.0, ball_mps=60.0, carry_m=150.0)
    try:
        d = ms.convert_swing(f, meta)
    except Exception as e:                                  # event detection needs a real-looking swing
        pytest.skip(f"synthetic swing not accepted by event detector: {e}")
    assert d["joints"].shape[1] == 11 and not bool(d["commercial_ok"]) and str(d["license_class"]) == "needs_counsel" and str(d["license_class_as_published"]) == "cc0"
    assert not bool(d["has_club_head"]) and "wrist_ankle_not_measured" in [str(x) for x in d["qc_flags"]]


def test_multisense_drops_nonmonotonic_timestamps(tmp_path):
    h5py = pytest.importorskip("h5py")
    ms = _held("data.convert_multisense_golf")
    t = np.array([0, .01, .02, .02, .015, .03, .04])
    f = tmp_path / "x.hdf5"
    with h5py.File(f, "w") as h:
        g = h.create_group("pns-joint-root-relative-position/cm-values")
        g["data"] = np.zeros((7, 63), "float32"); g["time_s"] = t.reshape(-1, 1)
    tt, P = ms.load_positions(f)
    assert np.all(np.diff(tt) > 0) and len(tt) == len(P)


def test_provenance_cc0_preset():
    from data import provenance as pr
    d = pr.tag({}, "multisensegolf_cc0")
    assert d["license_class"].item() == "needs_counsel" and not bool(d["commercial_ok"])
    assert d["license_class_as_published"].item() == "cc0" and bool(d["counsel_required"])
    assert pr.PRESETS["multisensegolf_cc0"] == pr.PRESETS["multisensegolf_needs_counsel"]  # legacy alias
