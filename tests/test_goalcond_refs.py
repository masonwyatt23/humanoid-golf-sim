import json
import math
import re
from pathlib import Path

import pytest

from data import shot_shape_model as m

ROOT = Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "data/references/goalcond_club_shot_shape_dr_refs.json", encoding="utf-8"))
LABELS = ("measured", "spec", "rule", "derived", "model", "estimate", "manufacturer", "gap", "reference")


def test_schema_every_row_has_label_n_source():
    assert len(D["rows"]) >= 50  # 105 built upstream; per-model (n=1) spec rows and TrackMan tour averages held pending counsel
    keys = {"section", "club", "quantity", "nominal", "range", "unit", "label", "n", "confidence", "source_url", "author_date", "table_or_page", "claim", "note"}
    for r in D["rows"]:
        assert keys <= set(r), r["quantity"]
        assert r["label"] and r["label"].split()[0].rstrip("(") in LABELS or r["label"].startswith(LABELS), r["label"]
        assert isinstance(r["n"], int) and r["n"] >= 1
        assert r["source_url"].startswith(("https://", "http://")) and r["author_date"]
        assert r["confidence"] in ("high", "medium", "low")


def test_n1_never_presented_as_range():
    for r in D["rows"]:
        if r["n"] == 1:
            assert "n=1" in r["range"], (r["quantity"], r["range"])
            if not r["label"].startswith(("model", "rule", "spec", "gap", "estimate", "measured")):
                assert re.fullmatch(r"\d+(\.\d+)?-\d+(\.\d+)?", r["range"]) is None


def test_gaps_flagged_low():
    for r in D["rows"]:
        if r["label"] == "gap":
            assert r["confidence"] == "low" and "GAP" in r["note"]


def test_no_model_names_or_ex_labels():
    pat = re.compile(r"i230|SM10|989|Launcher|Vokey|PING|Ping|Wishon|Ex\.\d", re.I)
    for r in D["rows"]:
        for f in ("nominal", "range", "claim", "note", "quantity", "club"):
            assert not pat.search(r[f]), (r["quantity"], f, r[f])
    assert "rows_held" not in D


@pytest.mark.skip(reason="held pending counsel: TrackMan tour-average rows are not tracked (counsel questions section 10)")
def test_tour_numbers_consistent():
    g = {(r["club"], r["quantity"]): r for r in D["rows"] if r["section"] == "2_launch"}
    cs = float(g[("7-iron", "PGA tour average club speed")]["nominal"])
    bs = float(g[("7-iron", "PGA tour average ball speed")]["nominal"])
    assert abs(bs / cs - float(g[("7-iron", "PGA tour average smash factor")]["nominal"])) < 0.01
    assert 60 <= float(g[("7-iron", "LPGA tour average club speed")]["nominal"]) <= 95


def test_groove_rules():
    g = {r["quantity"]: r for r in D["rows"] if r["quantity"].startswith("groove")}
    assert g["groove width max"]["nominal"] == "0.9" and g["groove depth max"]["nominal"] == "0.508"
    assert all(r["label"] == "rule" for r in g.values())


def test_spin_axis_model():
    assert m.LABEL == "model"
    assert m.spin_axis_deg(0, 25) == 0
    assert abs(m.spin_axis_deg(2, 25) - math.degrees(math.atan(math.tan(math.radians(2)) / math.tan(math.radians(25))))) < 1e-12
    assert m.spin_axis_deg(-3, 20) == -m.spin_axis_deg(3, 20)  # mirror symmetry (left-handed use)
    assert m.spin_axis_deg(3, 15) > m.spin_axis_deg(3, 30)  # lower spin loft -> more tilt per deg
    assert abs(m.total_obliqueness_deg(7, 23) - 24.0) < 0.2  # Tutelman worked example
    assert abs(m.horizontal_launch_deg(2, -5, 23) - 0.5) < 0.15
    # model-implied face share near the published 75% (iron) / 85% (driver)
    assert 0.72 <= m.face_share_of_start_direction(2, 0, 25) <= 0.80
    assert 0.84 <= m.face_share_of_start_direction(2, 0, 13) <= 0.90


def test_segment_fractions():
    s = {r["quantity"]: r for r in D["rows"] if r["quantity"].startswith("segment mass fraction, ")}
    tot = sum(float(r["nominal"]) * (1 if any(k in q for k in ("head", "trunk")) else 2) for q, r in s.items())
    assert abs(tot - 100.0) < 0.2


def test_driver_dr_rows_and_references():
    drv = json.load(open(ROOT / "data/references/driver_head_460cc_refs.json", encoding="utf-8"))
    names = {r["quantity"] for r in drv["rows"]}
    rows = [r for r in D["rows"] if r["section"] == "5_driver_dr"]
    assert len(rows) >= 10  # n=1 single-product shaft/adjustability rows held pending counsel
    for r in rows:
        for part in re.findall(r"see driver_head_460cc_refs: ([^;]+)", r["nominal"] + ";" + r["note"]):
            assert part.strip() in names, part
    q = {r["quantity"]: r for r in rows}
    assert q["max club length (Rules of Equipment)"]["nominal"] == "48"
    g10 = q["max club length under Model Local Rule G-10"]
    assert g10["nominal"] == "46" and "0.20" in g10["range"] and g10["label"].startswith("rule")
    assert 40 <= float(q["grip mass (stock men's)"]["nominal"]) <= 55


def test_closed_gaps_labelled():
    q = {r["quantity"]: r for r in D["rows"]}
    assert q["ball-turf kinetic friction (green), lower bound from one measurement"]["nominal"] == ">0.29"
    assert q["ball-turf kinetic friction (green), suggested value"]["label"].startswith("estimate")
    assert float(q["within-golfer stance-to-ball distance variability at ADDRESS (skilled)"]["nominal"]) == 11.0
    cg = q["7-iron CG height above sole/ground".replace("7-iron ", "")] if False else q["CG height above sole/ground"]
    assert cg["n"] == 4 and 17 <= float(cg["nominal"]) <= 19
