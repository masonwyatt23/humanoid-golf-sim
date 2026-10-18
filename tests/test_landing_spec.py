import json
from pathlib import Path
R = Path(__file__).resolve().parent.parent
S = json.load(open(R / "data/schemas/landing_shot_row.schema.json"))
X = json.load(open(R / "data/references/landing_shot_row_example.json"))

def test_example_has_required_and_known_fields():
    assert all(k in X for k in S["required"])
    assert set(X) <= set(S["properties"])
    for sec in ("impact", "flight", "landing"):
        assert set(X[sec]) <= set(S["properties"][sec]["properties"]), sec

def test_example_labelled_illustrative_and_consistent():
    assert "ILLUSTRATIVE" in X["label"] and X["shot_id"].startswith("EXAMPLE")
    assert X["landing"]["descent_angle_deg"] > 0 and X["landing"]["x_m"] == X["carry_m"]

def test_jsonschema_if_available():
    try:
        import jsonschema
    except ImportError:
        return
    jsonschema.validate(X, S)

def test_spec_doc_names_every_field():
    d = (R / "docs/ENV_LANDING_LOGGING_SPEC.md").read_text()
    for sec in ("impact", "flight", "landing"):
        for k in S["properties"][sec]["properties"]:
            assert k in d, (sec, k)
