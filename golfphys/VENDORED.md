# Vendored module: golfphys

Copied unmodified from local branch `golfphys` (head 0c2bca2; commits bf9d2f4, 98d73b6, 0c2bca2), authored by the PureGolf Data Agent.
Files: `golfphys/*.py`, `data/references/golfphys_coefficients.json`, `docs/GOLF_PHYSICS_SIM.md`, `tests/test_golfphys.py`.
Also vendored: `data/references/golfphys_validation.json`, `data/references/roll_aoa_validation.json` (needed by the tests). Not vendored: `docs/GOLF_PHYSICS_VALIDATION.md` (see the branch). Model-only; see its doc for calibration status.
No local edits; env-specific corrections live in `env/v5_shot.py`, never in this package.

## Update (2026-10-18): re-vendored from local branch `golfphys-lh-fix` commit 357bc0c (Data Agent)
Files updated unmodified from that commit: `golfphys/contact.py`, `golfphys/impact.py`, `tests/test_golfphys.py` (LH/RH mirror regression test included). This fixes the LH high/low-strike sign bug (face-up axis was handedness-dependent). The env adapter's LH high-offset negation in `env/v5_shot.py` was removed accordingly (otherwise the sign would flip twice). Not vendored: realism-check files from the parent commit 4050d8f.
