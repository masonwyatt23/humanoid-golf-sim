"""Skip tests that need third-party / private reference data untracked at the tip.

On 2026-10-18 the CMU (cmu_64_*.npz), MultiSense (multisense_*), mason*.npz and
CaddieSet-converter files were untracked at the tip (they remain in git history and
on the original author's disk). Tests listed below need them and are skipped cleanly
when the files are absent; they run unchanged when the files are restored locally.
"""
from pathlib import Path
import pytest

REFS = Path(__file__).resolve().parents[1] / "data" / "references"
_NEEDS = {
    "mason": REFS / "mason_v2_p1_s03.npz",
    "multisense": REFS / "multisense_P19_s20.npz",
    "cmu": REFS / "cmu_64_01.npz",
}
_DATA_TESTS = {
    "test_mason_elbow_address_stats.py": None,
    "test_mason_elbow_camera_bias.py": None,
    "test_mason_keyframe_targets.py": None,
    "test_mirror_references.py": None,
    "test_refset_timing_audit.py::test_real_set_mirror_pairs_and_events_consistent": None,
    "test_remine_slowmo_v3.py::test_v3_files_tagged_and_slowmo_metadata": None,
    "test_unified_refset.py": None,
    "test_wrist_elbow_event_targets.py": None,
}


# Tests that load the Unitree G1 meshes from MuJoCo Menagerie (not vendored; BSD-3). Skipped when the
# assets are absent (Menagerie must be cloned as `menagerie/` next to this repo, or set MENAGERIE_DIR; see README).
_MENAG_TESTS = tuple("test_v5_stage0.py::" + n for n in (
    "test_model_loads_29_actuated_and_welds", "test_stock_limits_match_menagerie_force_scale_1",
    "test_lh_is_physically_mirrored", "test_welds_closed_at_address", "test_stands_two_seconds_zero_action",
    "test_toe_sign_verified_against_model", "test_contact_pipeline_with_pipeline_only_motion"))
MENAG_REASON = "MuJoCo Menagerie not found next to repo or via MENAGERIE_DIR; see README"


def _menagerie_present():
    import os
    root = os.environ.get("MENAGERIE_DIR") or str(Path(__file__).resolve().parents[2] / "menagerie")
    return (Path(root) / "unitree_g1" / "assets").is_dir() and (Path(root) / "unitree_g1" / "scene.xml").is_file()


def pytest_collection_modifyitems(config, items):
    if not _menagerie_present():
        mskip = pytest.mark.skip(reason=MENAG_REASON)
        for it in items:
            nid = it.nodeid.split("tests/", 1)[-1]
            if any(nid == k or nid.startswith(k + "[") for k in _MENAG_TESTS):
                it.add_marker(mskip)
    missing = [k for k, p in _NEEDS.items() if not p.exists()]
    if not missing:
        return
    skip = pytest.mark.skip(reason="reference data untracked at tip (%s); held locally" % ",".join(missing))
    for it in items:
        nid = it.nodeid.split("tests/", 1)[-1]
        if any(nid == k or nid.startswith(k) for k in _DATA_TESTS):
            it.add_marker(skip)


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: long-running integration test (needs local checkpoints; skipped when absent). CI: -m \"not slow\"")
