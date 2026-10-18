"""The sim.validation scaffold imports and does not disturb existing sim imports."""
import importlib


def test_sim_validation_imports():
    m = importlib.import_module("sim.validation")
    assert m.__doc__ and "validation" in m.__doc__.lower()


def test_existing_sim_modules_still_import():
    for name in ("sim.golf_simulator", "sim.course", "sim.validate_simulator"):
        importlib.import_module(name)
