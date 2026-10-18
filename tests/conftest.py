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


def pytest_collection_modifyitems(config, items):
    missing = [k for k, p in _NEEDS.items() if not p.exists()]
    if not missing:
        return
    skip = pytest.mark.skip(reason="reference data untracked at tip (%s); held locally" % ",".join(missing))
    for it in items:
        nid = it.nodeid.split("tests/", 1)[-1]
        if any(nid == k or nid.startswith(k) for k in _DATA_TESTS):
            it.add_marker(skip)
