# render_blender: simulation render pipeline (not real footage)

Scripts that turn one recorded MuJoCo rollout into a Blender-rendered clip. **Everything rendered is a simulation of a generic procedural humanoid. It is not footage of a real person, and the body is not a likeness of anyone.**

What is real and what is not:
- **Real (from the sim):** per-body world poses, ball motion and launch for the **scripted** v3 swing (zero-residual config, seed 4000, evaluator env). This is the open-loop script, **not a learned policy**.
- **Assumed / analytic:** ball flight after the episode ends is the analytic drag + Magnus model (`env/ball_flight_analytic.py`) started from the sim's separation velocity; spin is assumed.
- **Cosmetic:** the humanoid mesh, course, lighting and camera moves are procedural scene dressing.

| File | Purpose |
|---|---|
| `export_trajectory.py` | Runs the scripted rollout in MuJoCo and writes `swing_v3.npz` (poses) and `swing_v3.json` (HUD numbers). Needs the project env (`mujoco`, `gymnasium`). |
| `build_and_render.py` | Builds the Blender scene from the `.npz` and renders PNG frames. Run with a Python that has `bpy` (Blender as a module). |
| `assemble.py` | Frames to mp4 with a HUD via ffmpeg (needs `ffmpeg`; HUD numbers from `swing_v3.json`). |

Usage sketch (paths are examples):
```
python -m render_blender.export_trajectory --seed 4000
<blender-python> render_blender/build_and_render.py --clip test --res 1280x720 --out golf_render/test
python render_blender/assemble.py golf_render/test out.mp4
```

Not committed on purpose: rendered frames, videos (`*.mp4` is gitignored; `results/videos/` is gitignored), `.blend` files and the exported `swing_v3.npz`/`swing_v3.json` (regenerate them with `export_trajectory.py`). The scripts are not run by the test suite or smoke test, and have not been re-verified after the paths were generalised for this commit.

## Policy rollouts (Stage 27+)
- `export_policy_trajectory.py`: rolls out a trained policy (deterministic) with the gate's env kwargs (`env_kwargs_full` + optional `--override`, e.g. `{"impact_gain": 1.2}`), records poses/club/ball in the same npz format, picks the MEDIAN-carry true-contact swing among N consecutive seeds, and writes the seed, all candidate carries and the separate 100-episode gate means to the json.
- `build_and_render.py --clip policy`: 17 s cut whose sample indices are relative to the rollout's own impact index.
- `assemble_policy.py`: HUD + title/end cards. On-screen numbers come from the one rolled-out episode; gate means are a separate caption. "Script-distilled policy" = behaviour-cloned from the scripted swing; power tier is labelled hypothetical (impact gain 1.2, no spin model).
Videos/frames/npz stay untracked.
