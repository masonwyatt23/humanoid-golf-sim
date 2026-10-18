"""realism: automated pass/warn/fail realism checks for swings and shots (stand-alone; imports nothing from env/, eval/, train/).
See docs/REALISM_CHECKS.md. Thresholds: data/references/realism_thresholds.json (each tagged published/derived/assumption/extrapolated/model)."""
from .checks import check_swing_realism, check_shot_realism, shot_from_gate_block, load_thresholds, targets_at_chs, PASS, WARN, FAIL

__all__ = ["check_swing_realism", "check_shot_realism", "shot_from_gate_block", "load_thresholds", "targets_at_chs", "PASS", "WARN", "FAIL"]
