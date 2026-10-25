import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "data/references/amateur_launch_wedge_cg_refs.json", encoding="utf-8"))
G = json.load(open(ROOT / "data/references/goalcond_club_shot_shape_dr_refs.json", encoding="utf-8"))
LABELS = ("measured", "spec", "rule", "derived", "model", "estimate", "manufacturer", "gap", "reference", "patent")


def test_schema():
    assert len(D["rows"]) >= 100
    assert not any("professional" in r["quantity"] or "single test example" in r["quantity"] for r in D["rows"])   # held at port
    for r in D["rows"]:
        assert r["label"].startswith(LABELS) and isinstance(r["n"], int) and r["n"] >= 1
        assert r["source_url"].startswith("http") and r["author_date"] and r["confidence"] in ("high", "medium", "low")
        if r["n"] == 1:
            assert "n=1" in r["range"], (r["quantity"], r["range"])
        if r["label"] == "gap":
            assert "GAP" in r["note"] and r["confidence"] == "low"


def test_no_model_names_or_vendor_tables():
    pat = re.compile(r"Vokey|Cutter|PING|Titleist|Callaway|TaylorMade|Hireko|Ex\.\d", re.I)
    for r in D["rows"]:
        for f in ("nominal", "range", "claim", "note", "quantity", "club"):
            assert not pat.search(r[f]), (r["quantity"], f)
    assert not any("trackman.com" in r["source_url"] or "hirekogolf" in r["source_url"] for r in D["rows"])


def test_r2201_consistency_and_speed_coverage():
    a = [r for r in D["rows"] if r["section"] == "A_amateur_launch_by_handicap" and r["quantity"].endswith("clubhead speed")]
    speeds = [float(r["nominal"]) for r in a]
    assert len(a) == 16 and min(speeds) < 60 and max(speeds) > 95   # amateur CONGU 1-4 only (professional group held)
    q = {r["quantity"] + "|" + r["club"]: float(r["nominal"]) for r in D["rows"] if r["section"] == "A_amateur_launch_by_handicap" and r["label"] != "gap" and re.fullmatch(r"-?[\d.]+", r["nominal"])}
    for g in ("male", "female"):
        for club in ("driver", "6-iron"):
            for k in ("CONGU cat 1 (<=5.4)", "CONGU cat 2 (5.5-12.4)"):
                sm = q[f"{g} {k} ball speed|{club}"] / q[f"{g} {k} clubhead speed|{club}"]
                assert 1.2 < sm < 1.5


def test_reference_resolves_and_wedge_cg_band():
    names = {r["quantity"] for r in G["rows"]}
    for r in D["rows"]:
        for p in re.findall(r"see goalcond_club_shot_shape_dr_refs: (.+)", r["nominal"]):
            assert p in names
    cg = [float(r["nominal"]) for r in D["rows"] if r["quantity"].startswith("CG height") and r["label"] == "patent claim" and re.fullmatch(r"[\d.]+", r["nominal"])]
    assert cg and all(15 <= x <= 24 for x in cg)
    assert len(D["rows"]) == 131 and not any("playcutter" in r["source_url"] for r in D["rows"])   # clubmaker rows held pending counsel
