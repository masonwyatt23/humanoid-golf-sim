import json
from pathlib import Path

D = json.load(open(Path(__file__).resolve().parent.parent / "data/references/driver_head_460cc_refs.json", encoding="utf-8"))


def test_rows_sourced_and_labelled():
    assert len(D["rows"]) >= 20
    for r in D["rows"]:
        assert r["label"] and r["confidence"] in ("high", "medium", "low") and r["source_url"]
        if "estimate" in str(r["nominal"]):
            assert "estimate" in r["label"] or "derived" in r["label"]


def test_rule_limits_and_tee():
    r36 = D.get("rule36_heads")   # per-model rule36.net rows are held locally (third-party table); aggregates only in rows
    if r36 is not None:
        assert all(x["moi_gcm2"] <= 5900 and x["cc"] <= 470 for x in r36)
    assert "rule36_heads_held" in D or r36 is not None
    tee = [r for r in D["rows"] if r["quantity"].startswith("recommended tee height")][0]
    assert abs(float(tee["nominal"]) - (62 - 42.67 / 2)) < 0.1
    s = D["sim_head"]
    assert abs(s["crown_z_mm"] - s["ball_centre_z_mm"] - 21.4) < 0.5 and s["crown_z_mm"] > 71.12


def _row(prefix):
    return [r for r in D["rows"] if r["quantity"].startswith(prefix)][0]


def test_face_centre_height_sourced_and_consistent():
    fc = _row("face-centre height above ground")
    assert fc["label"].startswith("derived") and "estimate" not in fc["nominal"] and "patents.us" in fc["source_url"]
    v = float(fc["nominal"])
    assert 27 <= v <= 31 and fc["range"].startswith("27-31")
    # route A: Zup - CGZ for the narrowest patent example (23-27, -4..-3) brackets the nominal
    assert 23 + 3 <= v <= 27 + 4
    # route B: (lowest face point 2-6 + face top 50-58.5) / 2
    assert 2 + 50 / 2 <= v <= 6 + 58.5 / 2
    crown = float(_row("sole-to-crown")["nominal"])
    assert v < crown / 2 + 0.5


def test_shaft_offset_mo_i_heel_toe_and_tee_check():
    cfz = _row("face-centre to shaft-axis distance")
    assert 35 <= float(cfz["nominal"]) <= 45 and cfz["label"].startswith("manufacturer")
    izz = _row("MOI vertical axis Izz, modern")
    assert float(izz["nominal"]) <= 5900 + 100
    assert "127" in _row("heel-to-toe")["range"]
    tee_top = 1.5 * 25.4
    centre = tee_top + 42.67 / 2
    assert abs(centre - 59.4) < 0.1 and centre < 62  # equator just below the 62 mm crown
    assert "ground level" in _row("tee check")["table_or_page"]


def test_no_per_model_rows_in_git():
    import re
    for r in D["rows"]:
        txt = r["range"]
        assert not re.search(r"919THI|719MW|460R|455R|440R|G440|E723|Ex\.\d", txt), r["quantity"]
    assert "rule36_heads" not in D
    izz = _row("MOI vertical axis Izz, modern")
    assert izz["range"].startswith("4800-5900") and "typo" in izz["note"]
    assert "single manufacturer" in _row("face-centre to shaft-axis distance")["note"]
    assert "2.1 b" in _row("face centre definition")["table_or_page"]
