import csv
from pathlib import Path
import pytest

D = Path(__file__).resolve().parents[1] / "data" / "references" / "research_bands"
FILES = ["slow_speed_driver_total_carry.csv", "driver_70_85mph_launch_rows.csv",
         "driver_dispersion_bands.csv", "lead_foot_plant_bands.csv"]


@pytest.mark.parametrize("name", FILES)
def test_rows_have_url_and_label(name):
    with open(D / name, newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows
    for r in rows:
        assert r["url"].startswith("http"), r.get("id")
        assert r["measurement_type"].strip(), r.get("id")
        assert "/workspace" not in ",".join(v or "" for v in r.values())


def test_readme_exists():
    assert (D.parents[2] / "docs" / "research_bands" / "README.md").exists()
