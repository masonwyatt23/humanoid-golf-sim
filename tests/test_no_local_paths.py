"""Committed shell scripts (and the harness v5 files) must not hard-code machine paths or a fixed interpreter: paths come from env vars
(HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT, HGS_PY) or args. Flagged by the Repo Agent for results/overnight/_batch_*.sh."""
import re, subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
LOCAL = re.compile(r"(?<![\w$}])/(?:workspace|home|root|Users|mnt|tmp)/[\w.\-]")
FIXED_PY = re.compile(r"(?<![\w$}])/[\w./\-]*/bin/python[\d.]*\b")
V5_FILES = ["eval/harness_v5.py", "eval/topk_grade.py", "docs/HARNESS_V5_SPEC.md", "data/references/club_bands_v5.json", "tests/test_harness_v5.py",
            "results/overnight/_run_j_gateoff_gp_v3.py"]

def tracked(pattern):
    try: out = subprocess.run(["git", "ls-files", pattern], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    except Exception: pytest.skip("not a git checkout")
    return out

def offenders(text):
    return [m.group(0) for m in LOCAL.finditer(text)] + [m.group(0) for m in FIXED_PY.finditer(text)]

def test_regexes_catch_examples():
    assert offenders("cd /workspace/artifacts/x; PY=/opt/venv/bin/python")
    assert not offenders('cd "${HGS_EVAL_REPO:?set}"; PY=${HGS_PY:-python3}; X=$O/_evalsnap/a')

def test_tracked_shell_scripts_have_no_machine_paths():
    sh = tracked("*.sh"); assert sh, "expected tracked .sh files"
    bad = {f: offenders((ROOT / f).read_text(errors="ignore")) for f in sh}
    bad = {f: v for f, v in bad.items() if v}
    assert not bad, f"machine paths / fixed interpreter in shell scripts: {bad}"

def test_v5_files_have_no_machine_paths():
    bad = {f: offenders((ROOT / f).read_text()) for f in V5_FILES if (ROOT / f).exists()}
    assert not {f: v for f, v in bad.items() if v}, bad
