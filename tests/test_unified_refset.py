import subprocess
from pathlib import Path
import numpy as np
from data import unified_refset as U

ROOT = Path(__file__).resolve().parents[1]
M = U.load_manifest()


def test_files_exist_tracked_and_commercial():
    tracked = set(subprocess.run(["git", "ls-files", "data/references"], cwd=ROOT, capture_output=True, text=True).stdout.split())
    for e in M["entries"]:
        assert (ROOT / e["path"]).exists()
        # CMU/MultiSense/mason*.npz were untracked at the tip on 2026-10-18 (still in git
        # history, held locally), so they are no longer required to be git-tracked.
        if e["source"] == "multisense" or e["source"] == "cmu" or "/mason" in e["path"]:
            assert e["path"] not in tracked
        elif tracked:
            assert e["path"] in tracked
        assert e["handedness"] == "left"
        if e["source"] == "multisense":
            # published as CC0 but participants identifiable -> needs counsel, not commercial-eligible
            assert e["license_class"] == "needs_counsel" and e["commercial_ok"] is False
            assert e["license_class_as_published"] == "cc0" and e["counsel_required"] is True
            assert "research_mocap_datasets_licenses" in e["license_note"]
        elif e["source"] == "cmu":
            # retagged 2026-10: CMU resale clause ("even in converted form") -> counsel_required
            assert e["license_class"] == "needs_counsel" and e["commercial_ok"] is False and e["counsel_required"] is True
        else:
            assert e["commercial_ok"]
        assert e["on_origin_main"] in (True, None)


def test_split_rules():
    ents = M["entries"]
    mason_val = [e for e in ents if e["source"] == "mason" and e["split"] == "val"]
    assert len(mason_val) >= 2
    for s in ("mason", "multisense", "cmu"):
        assert {e["split"] for e in ents if e["source"] == s} == {"train", "val"}
    groups = {}
    for e in ents:
        groups.setdefault(e["group"], set()).add(e["split"])
    assert all(len(v) == 1 for v in groups.values())  # no group straddles train/val
    # v2 swings that re-cut a v1 swing / v3 re-cuts share a group with the v3 slow-mo window
    slow = [e for e in ents if e["variant"] == "slowmo"]
    assert slow and all(e["weight_train"] == 0 for e in slow)


def test_split_is_deterministic():
    import copy
    ents = copy.deepcopy(M["entries"])
    for e in ents:
        e["split"] = None
    U.assign_splits(ents, U.load_sampling_config())
    assert [e["split"] for e in ents] == [e["split"] for e in M["entries"]]


def test_weights_normalised_and_configurable():
    ents, p = U.weights(M)
    assert abs(p.sum() - 1) < 1e-9
    tot = {}
    for e, pi in zip(ents, p):
        tot[e["source"]] = tot.get(e["source"], 0) + pi
    assert abs(tot["mason"] - 0.6) < 1e-6 and abs(tot["multisense"] - 0.2) < 1e-6 and abs(tot["cmu"] - 0.2) < 1e-6
    cfg = U.load_sampling_config(); cfg["source_weights"] = {"mason": 0.8, "multisense": 0.1, "cmu": 0.1}
    ents2, p2 = U.weights(M, cfg)
    assert abs(sum(pi for e, pi in zip(ents2, p2) if e["source"] == "mason") - 0.8) < 1e-6
    q = [e["quality"] for e in ents if e["source"] == "mason"]
    pm = [pi for e, pi in zip(ents, p) if e["source"] == "mason"]
    assert np.argmax(q) == np.argmax(pm)


def test_sample_and_loader_with_reference_dataset():
    rng = np.random.default_rng(0)
    seen = {U.sample(rng, M)["source"] for _ in range(200)}
    assert seen == {"mason", "multisense", "cmu"}
    ds = U.as_reference_dataset("val", M)
    assert len(ds) == len(U.split_entries(M, "val"))
    r = ds.sample()
    assert r["joints"].shape[1] == 11 and r["handedness"] == "left"
    cmu = next(U.load_ref(e) for e in M["entries"] if e["source"] == "cmu")
    raw = np.load(ROOT / cmu["path"].replace(str(ROOT) + "/", ""))["joints"]
    assert cmu["mirrored"] and not np.allclose(cmu["joints"], raw)
    assert len(list(U.iter_split(M, "val"))) > 0


def test_handedness_unverified_flags_do_not_change_sampling():
    flagged = {e["path"].split("/")[-1]: e for e in M["entries"] if e.get("handedness_unverified")}
    assert set(flagged) == {"mason_v2_p1_s11.npz", "mason_v2_p2_s10.npz"}
    for e in flagged.values():
        assert e["exclude_pending_verification"] is True and "nverified" in e["flag_note"]
    # flag only: flagged train entry keeps its weight, and the manifest rebuild logic still lists it
    assert flagged["mason_v2_p2_s10.npz"]["split"] == "train" and flagged["mason_v2_p2_s10.npz"]["weight_train"] > 0
    assert flagged["mason_v2_p1_s11.npz"]["split"] == "val"
    ents, _ = U.weights()
    assert "data/references/mason_v2_p2_s10.npz" in {e["path"] for e in ents}


def test_licence_flags_in_manifest():
    from data.provenance import commercial_cleared
    man = U.load_manifest()
    by = {}
    for e in man["entries"]:
        by.setdefault(e["source"], []).append(e)
    assert all(e["counsel_required"] for e in by["multisense"])
    assert not any(commercial_cleared(e) for e in by["multisense"])
    assert all(e["no_standalone_resale"] and e["acknowledgment_required"] and e["ack"] for e in by["cmu"])
    assert not any(commercial_cleared(e) for e in by["cmu"])  # CMU retagged counsel_required 2026-10
    assert all(e["counsel_required"] and not e["commercial_ok"] for e in by["cmu"])
    assert all("license_url" in e and "verification" in e for e in by["cmu"] + by["multisense"])
    s11 = [e for e in by["mason"] if e["path"].endswith("mason_v2_p1_s11.npz")][0]
    assert s11["needs_mason_confirmation"] and not s11["handedness_verified"] and s11["split"] == "val"


def test_face_path_stub_is_unverified():
    import json
    from pathlib import Path
    j = json.load(open(Path(__file__).resolve().parents[1] / "data/references/mason_impact_face_path_proxies.json"))
    assert j["unverified_all"] and "face_angle_deg" in j["unavailable"] and "club_path_deg" in j["unavailable"]


# ---- unified_v1 frozen / unified_v2 behaviour ---------------------------------------------------------------
import hashlib  # noqa: E402
import json  # noqa: E402

# v1 manifest = reconciled version (Data Agent licence annotations 1cdde9f + MultiSense needs_counsel tags). Sampling/weights
# are unchanged since unified_v1 was first published; imit2/imit3 depend on them. Do NOT regenerate; add a new version instead.
V1_MANIFEST_SHA256 = "572bc269ad9e21c0cb780dc499fef6257a29cb0d7c9f13a3d73c5de02ecb527b"  # updated 2026-10 for CMU retag (counsel_required)
V1_SAMPLING_SHA256 = "41daab0a8bdd16b94a19c03e2e9007a3c5fe86927f2f308a33d2e5bc462e5ad9"


def _sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_v1_files_frozen_by_hash():
    assert _sha("data/reference_sets/unified_v1.json") == V1_MANIFEST_SHA256
    assert _sha("data/reference_sets/unified_v1_sampling.json") == V1_SAMPLING_SHA256


def _strip_origin(m):
    # on_origin_main depends on live origin/main (these files were untracked at the tip
    # on 2026-10-18), so it is excluded from rebuild equality.
    m = dict(m)
    m["entries"] = [{k: v for k, v in e.items() if k != "on_origin_main"} for e in m["entries"]]
    return m


def test_v1_rebuild_reproduces_committed_manifest_and_default_loaders_are_v1():
    assert _strip_origin(U.build_manifest("unified_v1")) == _strip_origin(U.load_manifest())
    assert U.load_manifest()["version"] == "unified_v1" and U.load_sampling_config()["version"] == "unified_v1"
    assert "honor_exclusion_flags" not in U.load_sampling_config()


def test_v1_weights_unchanged_for_flagged_entries():
    ents, p = U.weights(U.load_manifest())
    paths = {e["path"] for e in ents}
    assert "data/references/mason_v2_p2_s10.npz" in paths and abs(p.sum() - 1) < 1e-9


V2 = U.load_manifest(version="unified_v2")
FLAGGED = {"data/references/mason_v2_p1_s11.npz", "data/references/mason_v2_p2_s10.npz"}


def test_v2_excludes_flagged_from_train_and_val():
    flagged = {e["path"]: e for e in V2["entries"] if e.get("exclude_pending_verification")}
    assert set(flagged) == FLAGGED
    assert all(e["split"] == "excluded" and e["weight_train"] == 0 for e in flagged.values())
    assert flagged["data/references/mason_v2_p1_s11.npz"]["split_v1"] == "val"
    assert flagged["data/references/mason_v2_p2_s10.npz"]["split_v1"] == "train"
    for split in ("train", "val"):
        assert not FLAGGED & {e["path"] for e in U.split_entries(V2, split)}
    ents, p = U.weights(V2)
    assert not FLAGGED & {e["path"] for e in ents}
    assert len(U.as_reference_dataset("val", V2)) == len(U.split_entries(V2, "val"))
    rng = np.random.default_rng(1)
    assert all(U.sample(rng, V2)["path"].split("/")[-1] not in {"mason_v2_p1_s11.npz", "mason_v2_p2_s10.npz"} for _ in range(100))


def test_v2_weights_sum_to_one_and_source_masses():
    assert abs(sum(e["weight_train"] for e in V2["entries"]) - 1) < 1e-4
    ents, p = U.weights(V2)
    assert abs(p.sum() - 1) < 1e-9
    tot = {}
    for e, pi in zip(ents, p):
        tot[e["source"]] = tot.get(e["source"], 0) + pi
    assert abs(tot["mason"] - 0.6) < 1e-6 and abs(tot["multisense"] - 0.2) < 1e-6 and abs(tot["cmu"] - 0.2) < 1e-6


def test_v2_equals_v1_except_exclusions_and_renormalisation():
    v1 = {e["path"]: e for e in U.load_manifest()["entries"]}
    assert set(v1) == {e["path"] for e in V2["entries"]}
    for e in V2["entries"]:
        o = v1[e["path"]]
        if e["path"] in FLAGGED:
            continue
        assert e["split"] == o["split"] and e["license_class"] == o["license_class"] and e["commercial_ok"] == o["commercial_ok"]
    assert _strip_origin(U.build_manifest("unified_v2")) == _strip_origin(V2)
    assert V2["version"] == "unified_v2" and U.load_sampling_config(version="unified_v2")["honor_exclusion_flags"] is True
    assert all(e["license_class"] == "needs_counsel" for e in V2["entries"] if e["source"] == "multisense")


def test_multisense_npz_tags_match_manifest_and_arrays_intact():
    from data import provenance as P
    for e in V2["entries"]:
        if e["source"] == "multisense":
            t = P.read_tags(ROOT / e["path"])
            assert t["license_class"] == "needs_counsel" and t["commercial_ok"] is False
            assert t["license_class_as_published"] == "cc0" and bool(t["counsel_required"])
            assert not P.commercial_cleared(t)
    assert P.include_commercial_only(sorted((ROOT / "data/references").glob("multisense_*.npz"))) == []


def test_retag_script_is_idempotent_and_preserves_arrays(tmp_path):
    import shutil
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    if not (ROOT / "scripts/retag_multisense.py").exists():
        pytest.skip("scripts/retag_multisense.py is held locally (untracked at the tip)")
    import retag_multisense as R
    src = ROOT / "data/references/multisense_P19_s20.npz"
    f = tmp_path / "multisense_P19_s20.npz"
    # make a legacy-tagged copy
    d = {k: v for k, v in np.load(src, allow_pickle=True).items()}
    d["license_class"] = np.array("cc0"); d["commercial_ok"] = np.array(True)
    for k in ("license_class_as_published", "counsel_required"):
        d.pop(k, None)
    np.savez(f, **d)
    assert R.retag_file(f) == "retagged" and R.retag_file(f) == "skipped"
    new = np.load(f, allow_pickle=True)
    assert str(new["license_class"]) == "needs_counsel" and not bool(new["commercial_ok"])
    for k in d:
        if k not in R.CHANGED:
            assert np.array_equal(new[k], d[k])
