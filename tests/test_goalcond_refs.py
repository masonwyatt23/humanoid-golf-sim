import json
import math
import re
from pathlib import Path

import pytest

from data import shot_shape_model as m

ROOT = Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "data/references/goalcond_club_shot_shape_dr_refs.json", encoding="utf-8"))
LABELS = ("measured", "spec", "rule", "derived", "model", "estimate", "manufacturer", "gap")


def test_schema_every_row_has_label_n_source():
    assert len(D["rows"]) >= 50  # 105 built upstream; per-model (n=1) spec rows and TrackMan tour averages held pending counsel
    keys = {"section", "club", "quantity", "nominal", "range", "unit", "label", "n", "confidence", "source_url", "author_date", "table_or_page", "claim", "note"}
    for r in D["rows"]:
        assert keys <= set(r), r["quantity"]
        assert r["label"] and r["label"].split()[0].rstrip("(") in LABELS or r["label"].startswith(LABELS), r["label"]
        assert isinstance(r["n"], int) and r["n"] >= 1
        assert r["source_url"].startswith("https://") and r["author_date"]
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
