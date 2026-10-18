"""
Compare policies trained on different pure-swing styles.

Usage:
    python -m eval.compare_styles [--episodes 20] [--styles scott rory] \
        [--models-dir models] [--out-dir eval/results] [--seed 0]

Writes eval/results/style_comparison.md and .json. Styles without a model are
listed as "no model" and never given numbers.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List

STYLES = ["scott", "scheffler", "rory", "average"]


def _f(x, fmt):
    return "n/a" if x != x else format(x, fmt)  # NaN-safe


def make_table(results: List[Dict]) -> str:
    hdr = ("| Style | Episodes | Contact rate | Mean dist (m) | Std dist (m) | Max dist (m) "
           "| Dist CV | Club path dispersion (m) | True contact | Carry (landed) | Peak ball speed (m/s) | DTW style match (rad) |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    rows = []
    for r in results:
        if r.get("status") == "no_model":
            rows.append(f"| {r['style']} | – | no model | – | – | – | – | – | – | – | – | – |")
        else:
            rows.append(
                f"| {r['style']} | {r['episodes']} | {r['contact_rate']*100:.0f}% "
                f"| {_f(r['mean_distance'], '.2f')} | {_f(r['std_distance'], '.2f')} "
                f"| {_f(r['max_distance'], '.2f')} | {_f(r['cv_distance'], '.3f')} "
                f"| {_f(r['path_dispersion'], '.4f')} | {r.get('true_contact_rate', float('nan'))*100:.0f}% "
                f"| {_f(r.get('mean_carry_landed', float('nan')), '.2f')} ({r.get('carry_landed_rate', float('nan'))*100:.0f}% landed) "
                f"| {_f(r.get('mean_peak_ball_speed', float('nan')), '.2f')} "
                f"| {_f(r['style_match_dtw'], '.3f') if r.get('style_match_dtw') is not None else 'n/a'} |")
    return "\n".join([hdr] + rows)


def best(results: List[Dict]) -> str:
    ok = [r for r in results if "mean_distance" in r]
    if not ok:
        return "No trained models found; nothing to rank."
    d = max(ok, key=lambda r: r["mean_distance"])
    c = max(ok, key=lambda r: r["contact_rate"])
    s = min((r for r in ok if r["path_dispersion"] == r["path_dispersion"]),
            key=lambda r: r["path_dispersion"], default=None)
    lines = [f"- Best mean distance: {d['style']} ({d['mean_distance']:.2f} m)",
             f"- Best contact rate: {c['style']} ({c['contact_rate']*100:.0f}%)"]
    if s:
        lines.append(f"- Most consistent club path: {s['style']} ({s['path_dispersion']:.4f} m)")
    return "\n".join(lines)


def from_leaderboard(lb_path="results/leaderboard.json", out_dir="eval/results"):
    """Generate the multi-model comparison from the leaderboard results (so it cannot go stale). Called by eval.leaderboard."""
    root = Path(__file__).resolve().parent.parent
    lb = json.loads((root / lb_path).read_text())
    rows = []
    for c in lb["models"]:
        for mode, v in c.get("modes", {}).items():
            if "contact_rate" not in v:
                continue
            rows.append({"model": "/".join(c["names"]), "steps": c["steps"], "mode": mode, "handedness": c.get("env_kwargs", {}).get("handedness", "right"),
                         "scripted": bool(c.get("scripted")), **{k: v[k] for k in ("episodes", "contact_rate", "mean_distance", "std_distance", "max_distance", "mean_carry",
                         "landed_fraction", "lateral_std", "left_miss_rate", "right_miss_rate", "peak_club_mph_mean", "peak_club_mph_max", "peak_club_pct_target_max",
                         "path_dispersion", "cv_distance") if k in v}})
    f = lambda x, fmt: "n/a" if x is None or x != x else format(x, fmt)
    L = ["# Multi-model comparison (GENERATED from results/leaderboard.json by eval.compare_styles.from_leaderboard - do not edit by hand)", "",
         f"Env fingerprint `{lb['env_fingerprint']}`, {lb['episodes']} episodes/mode, seeds {lb['seed_base']}+. Distance = final ball x; carry = first landing (mean over all episodes; 0 if never landed); +y = left, miss = |y| > {lb['lateral_threshold_m']} m.",
         f"Best trained: **{' / '.join(lb['best_model'] or ['none (no row passes smash + swing-realism gates)'])}**; best left-handed: **{' / '.join(lb['best_left']) if lb.get('best_left') else 'n/a'}**; best overall incl. scripted baseline: **{' / '.join(lb['best_overall'] or ['none (no row passes smash + swing-realism gates)'])}**.", "",
         "| Model | Steps | Hand | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) | Landed | Lateral std (m) | Left | Right | Peak club mph (mean/max) | % of 120 mph (max) |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['model']}{' (scripted)' if r['scripted'] else ''} | {r['steps']} | {r['handedness']} | {r['mode'][:5]} | {r['contact_rate']*100:.0f}% | {f(r['mean_distance'], '.2f')} | {f(r['max_distance'], '.2f')} | {f(r['mean_carry'], '.2f')} | {r['landed_fraction']*100:.0f}% | {f(r['lateral_std'], '.2f')} | {r['left_miss_rate']*100:.0f}% | {r['right_miss_rate']*100:.0f}% | {f(r['peak_club_mph_mean'], '.1f')} / {f(r['peak_club_mph_max'], '.1f')} | {f(r['peak_club_pct_target_max'], '.1f')}% |")
    out = root / out_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "style_comparison.md").write_text("\n".join(L) + "\n")
    (out / "style_comparison.json").write_text(json.dumps({"generated_from": lb_path, "env_fingerprint": lb["env_fingerprint"], "rows": rows}, indent=1))
    return out / "style_comparison.md"


def main(argv=None):
    p = argparse.ArgumentParser(description="Regenerate eval/results/style_comparison.{md,json} from results/leaderboard.json "
                                            "(run `python -m eval.leaderboard` first to refresh the leaderboard itself).")
    p.parse_args(argv)
    print("wrote", from_leaderboard())


if __name__ == "__main__":
    main()
