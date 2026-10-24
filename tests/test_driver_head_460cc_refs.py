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
