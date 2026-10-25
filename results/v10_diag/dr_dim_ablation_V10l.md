# DR per-dimension ablation on V10l 100k (LOCAL, NOT OFFICIAL)

scripts/dr_dim_ablation.py; DREnv one DR dimension at a time (slope off), breadth .35/.7/1.0 = stages 0/1/2 (high bands only at 1.0, full width); deterministic; address starts; n=24, seeds 500000-500023; plant = slip<=2.5 cm & turn<=10 deg vs address & lead-foot air<=1 ctrl step, window ADDRESS->impact (harness uses top->impact, so absolute plant here is stricter than the harness; compare rows relatively). 'none' = no noise at all (24 identical episodes); 'v4noise' = JEnv uniform start noise 0.03 rad / 0.06 rad/s (v4-gate style), no DR.

Command: `OMP_NUM_THREADS=1 PYTHONPATH=. nice -n 15 python scripts/dr_dim_ablation.py <ckpt_base> ALL 0.35,0.7,1.0 24 500000 out.jsonl` (also dims joint_legs, joint_upper, v4noise)

| ckpt | breadth | dim | contact | fell | plant | slip fail | turn fail | air fail | slip med cm | turn med deg | max abs z med | frac abs z>5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V10l_s104_100000 | 0.35 | none | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0004 |
| V10l_s104_100000 | 0.35 | joint | 0.96 | 0.00 | 0.38 | 0.04 | 0.62 | 0.04 | 2.2 | 10.5 | 6.0 | 0.0003 |
| V10l_s104_100000 | 0.35 | vel | 1.00 | 0.00 | 0.58 | 0.00 | 0.42 | 0.00 | 2.1 | 10.0 | 5.8 | 0.0003 |
| V10l_s104_100000 | 0.35 | mu | 1.00 | 0.00 | 0.62 | 0.00 | 0.38 | 0.00 | 2.1 | 10.0 | 5.7 | 0.0003 |
| V10l_s104_100000 | 0.35 | ball | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0003 |
| V10l_s104_100000 | 0.35 | head | 1.00 | 0.00 | 0.67 | 0.00 | 0.33 | 0.00 | 2.2 | 10.0 | 6.0 | 0.0003 |
| V10l_s104_100000 | 0.35 | loft | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0004 |
| V10l_s104_100000 | 0.35 | seg | 0.92 | 0.00 | 0.58 | 0.08 | 0.42 | 0.04 | 2.2 | 9.9 | 5.8 | 0.0003 |
| V10l_s104_100000 | 0.35 | tau | 1.00 | 0.00 | 0.58 | 0.00 | 0.42 | 0.00 | 2.2 | 10.0 | 5.9 | 0.0003 |
| V10l_s104_100000 | 0.35 | lat | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0003 |
| V10l_s104_100000 | 0.35 | all | 0.92 | 0.00 | 0.54 | 0.08 | 0.42 | 0.00 | 2.0 | 9.4 | 5.7 | 0.0003 |
| V10l_s104_100000 | 0.7 | none | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0004 |
| V10l_s104_100000 | 0.7 | joint | 0.92 | 0.00 | 0.21 | 0.29 | 0.62 | 0.04 | 2.1 | 12.0 | 5.8 | 0.0003 |
| V10l_s104_100000 | 0.7 | vel | 1.00 | 0.00 | 0.46 | 0.00 | 0.54 | 0.00 | 2.2 | 10.0 | 6.0 | 0.0003 |
| V10l_s104_100000 | 0.7 | mu | 1.00 | 0.00 | 0.50 | 0.00 | 0.50 | 0.00 | 2.1 | 10.0 | 5.7 | 0.0003 |
| V10l_s104_100000 | 0.7 | ball | 0.96 | 0.00 | 0.96 | 0.00 | 0.04 | 0.00 | 2.2 | 10.0 | 6.1 | 0.0003 |
| V10l_s104_100000 | 0.7 | head | 0.96 | 0.00 | 0.46 | 0.00 | 0.54 | 0.00 | 2.2 | 10.0 | 6.2 | 0.0004 |
| V10l_s104_100000 | 0.7 | loft | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0004 |
| V10l_s104_100000 | 0.7 | seg | 0.96 | 0.00 | 0.58 | 0.12 | 0.42 | 0.00 | 2.1 | 9.3 | 5.8 | 0.0003 |
| V10l_s104_100000 | 0.7 | tau | 1.00 | 0.00 | 0.79 | 0.00 | 0.21 | 0.00 | 2.1 | 9.9 | 5.7 | 0.0003 |
| V10l_s104_100000 | 0.7 | lat | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0002 |
| V10l_s104_100000 | 0.7 | all | 0.79 | 0.00 | 0.50 | 0.21 | 0.46 | 0.00 | 2.1 | 9.2 | 5.7 | 0.0002 |
| V10l_s104_100000 | 1.0 | none | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0004 |
| V10l_s104_100000 | 1.0 | joint | 0.75 | 0.04 | 0.17 | 0.62 | 0.62 | 0.38 | 2.8 | 11.4 | 5.9 | 0.0004 |
| V10l_s104_100000 | 1.0 | vel | 0.96 | 0.00 | 0.46 | 0.08 | 0.54 | 0.00 | 2.2 | 10.2 | 6.0 | 0.0003 |
| V10l_s104_100000 | 1.0 | mu | 0.96 | 0.00 | 0.62 | 0.00 | 0.38 | 0.00 | 2.1 | 9.9 | 5.4 | 0.0003 |
| V10l_s104_100000 | 1.0 | ball | 1.00 | 0.00 | 0.79 | 0.00 | 0.21 | 0.00 | 2.2 | 10.0 | 5.9 | 0.0003 |
| V10l_s104_100000 | 1.0 | head | 0.83 | 0.04 | 0.33 | 0.17 | 0.62 | 0.00 | 2.2 | 10.1 | 5.7 | 0.0003 |
| V10l_s104_100000 | 1.0 | loft | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0004 |
| V10l_s104_100000 | 1.0 | seg | 0.92 | 0.00 | 0.46 | 0.25 | 0.50 | 0.00 | 2.2 | 10.1 | 5.8 | 0.0003 |
| V10l_s104_100000 | 1.0 | tau | 1.00 | 0.00 | 0.92 | 0.00 | 0.08 | 0.00 | 2.1 | 9.3 | 5.8 | 0.0002 |
| V10l_s104_100000 | 1.0 | lat | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0003 |
| V10l_s104_100000 | 1.0 | all | 0.62 | 0.08 | 0.21 | 0.50 | 0.58 | 0.38 | 2.6 | 11.3 | 6.0 | 0.0006 |
| V10l_s104_100000 | 0.7 | joint_legs | 0.83 | 0.00 | 0.12 | 0.25 | 0.71 | 0.00 | 2.2 | 10.4 | 5.9 | 0.0003 |
| V10l_s104_100000 | 0.7 | joint_upper | 0.83 | 0.00 | 0.46 | 0.38 | 0.54 | 0.00 | 2.3 | 10.2 | 5.9 | 0.0003 |
| V10l_s104_100000 | 1.0 | joint_legs | 0.71 | 0.00 | 0.12 | 0.67 | 0.50 | 0.38 | 2.9 | 10.1 | 5.7 | 0.0002 |
| V10l_s104_100000 | 1.0 | joint_upper | 0.79 | 0.00 | 0.54 | 0.38 | 0.46 | 0.00 | 2.1 | 9.9 | 5.7 | 0.0003 |
| V10l_s104_100000 | 1.0 | v4noise | 0.88 | 0.00 | 0.21 | 0.33 | 0.62 | 0.08 | 2.3 | 11.7 | 5.9 | 0.0002 |
| stageDRc_s203 | 1.0 | v4noise | 0.71 | 0.00 | 0.12 | 0.54 | 0.71 | 0.21 | 2.7 | 13.6 | 6.2 | 0.0003 |
| stageDRd_s205 | 1.0 | v4noise | 0.21 | 0.08 | 0.08 | 0.88 | 0.79 | 0.17 | 3.3 | 15.9 | 5.0 | 0.0006 |
| stageDRc_s203 | 0.7 | none | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 2.7 | 11.6 | 4.8 | 0.0000 |
| stageDRc_s203 | 0.7 | all | 0.67 | 0.00 | 0.25 | 0.50 | 0.58 | 0.04 | 2.5 | 11.4 | 5.9 | 0.0003 |
| stageDRd_s205 | 0.7 | none | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 3.2 | 14.2 | 4.7 | 0.0000 |
| stageDRd_s205 | 0.7 | all | 0.25 | 0.08 | 0.00 | 0.83 | 0.83 | 0.17 | 2.8 | 13.0 | 4.9 | 0.0006 |
| V10l_s104_100000 | 0.7 | none | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 2.2 | 10.0 | 6.3 | 0.0004 |
| V10l_s104_100000 | 0.7 | all | 0.79 | 0.00 | 0.50 | 0.21 | 0.46 | 0.00 | 2.1 | 9.2 | 5.7 | 0.0002 |

## Findings

- V10l's nominal lead-foot turn is 10.0 deg (median) against a 10 deg limit: plant is knife-edge, so almost any perturbation flips ~40-60% of episodes to a turn fail.
- Worst dimension: joint offsets, driven by the LEG joints (hip/knee/ankle): plant .12 at breadth .7 and 1.0 (upper-body-only .46/.54); at 1.0 (high band .05-.06 rad) slip fails .62-.67 and air .38, contact .71-.75.
- Next: segment mass (1.0: plant .46, slip .25) and head mass (1.0: plant .33, contact .83); velocity offsets and friction cost ~.4-.5 plant via turn only (no slip/contact loss).
- Harmless: loft, latency (plant 1.00 at all breadths), ball offset (<=.7: .96; 1.0: .79), torque scale (.79-.92).
- Not an obs-normalisation mismatch: max |normalised obs| ~5.4-6.3 and |z|>5 fraction ~0.0003 are the same with and without DR.
- Low friction does not cause slip: mu-only rows have slip fails 0.00; its failures are turn only. Leg joint offsets change the stance itself (feet/legs start displaced), which shows up as slip and air -> physical, not friction-limited.
- DR snapshots stageDRc 250k / stageDRd 250k drifted on the NOMINAL swing: no-noise deterministic swing misses the ball (contact 0) with lead-foot turn 11.6 / 14.2 deg and slip 2.7 / 3.2 cm; under v4noise: contact .71 / .21, plant .12 / .08, turn med 13.6 / 15.9 deg vs V10l .88 / .21 / 11.7. Their failures are turn+slip (DRd also air).

## Recommendation

Next DR run: drop joint-offset high band and leg-joint offsets (or cap joint at breadth .35 = 0-0.0105 rad), keep loft, latency, torque, ball<=.7, mu and vel <=.7, seg/head mass <=.7; first make the nominal turn margin real (V10l sits at 10.0 deg). stageG: run WITHOUT DR (V10l training conditions) so goal learning is not confounded; stageG_cmd.txt edited accordingly.
