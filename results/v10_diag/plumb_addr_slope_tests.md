# --plumb_addr slope tests (LOCAL, NOT OFFICIAL)

Code: 66ec75f (main ea0b69da). Checkpoint V10l_s104_100000/ckpt_100000 (not in git). Seeds 920000+i, n=6 per cell; same slope azimuths off vs on.

Commands (repo root):
```
export HGS_V10L_CKPT=<local>/V10l_s104_100000/ckpt_100000
OMP_NUM_THREADS=1 PYTHONPATH=. python scripts/slope_diag.py {zero|v10l} 0,0.03,0.07,0.09 6          # flag off
OMP_NUM_THREADS=1 PYTHONPATH=. python scripts/slope_diag.py {zero|v10l} 0,0.03,0.07,0.09 6 plumb    # flag on
OMP_NUM_THREADS=1 PYTHONPATH=. python scripts/slope_diag.py v10l 0.005,0.01,0.02 6 [plumb]
```
(The original runs used the pre-rename 4th arg `1`, which already set plumb_addr=True in slope_diag.py.)

| policy | slope | plumb_addr | contact | fell | QACC eps |
|---|---|---|---|---|---|
| v10l | 0.0 | off | 6/6 | 0 | 0 |
| v10l | 0.0 | on | 6/6 | 0 | 0 |
| v10l | 0.005 | off | 3/6 | 0 | 0 |
| v10l | 0.005 | on | 5/6 | 0 | 0 |
| v10l | 0.01 | off | 2/6 | 2 | 0 |
| v10l | 0.01 | on | 6/6 | 0 | 0 |
| v10l | 0.02 | off | 2/6 | 2 | 0 |
| v10l | 0.02 | on | 2/6 | 0 | 0 |
| v10l | 0.03 | off | 1/6 | 2 | 0 |
| v10l | 0.03 | on | 1/6 | 1 | 0 |
| v10l | 0.07 | off | 0/6 | 4 | 0 |
| v10l | 0.07 | on | 1/6 | 4 | 0 |
| v10l | 0.09 | off | 0/6 | 5 | 0 |
| v10l | 0.09 | on | 1/6 | 4 | 0 |
| zero | 0.0 | off | 6/6 | 0 | 0 |
| zero | 0.0 | on | 6/6 | 0 | 0 |
| zero | 0.03 | off | 3/6 | 0 | 0 |
| zero | 0.03 | on | 2/6 | 1 | 0 |
| zero | 0.07 | off | 0/6 | 4 | 0 |
| zero | 0.07 | on | 1/6 | 4 | 0 |
| zero | 0.09 | off | 0/6 | 5 | 0 |
| zero | 0.09 | on | 1/6 | 2 | 0 |

Sole-IK failures (flag on, sole error > 1 mm):

- v10l slope 0.07 az 309 deg: sole error [9.3822, 11.0249] mm, club lift 8.92 mm, contact False, fell True
- v10l slope 0.07 az 263 deg: sole error [29.7355, 17.2111] mm, club lift 4.07 mm, contact False, fell True
- v10l slope 0.07 az 311 deg: sole error [7.6708, 9.8305] mm, club lift 9.07 mm, contact False, fell True
- v10l slope 0.09 az 241 deg: sole error [45.8099, 24.1153] mm, club lift 3.99 mm, contact False, fell True
- v10l slope 0.09 az 233 deg: sole error [41.6415, 16.8387] mm, club lift 3.39 mm, contact False, fell True
- zero slope 0.07 az 309 deg: sole error [9.3822, 11.0249] mm, club lift 8.92 mm, contact False, fell True
- zero slope 0.07 az 263 deg: sole error [29.7355, 17.2111] mm, club lift 4.07 mm, contact False, fell True
- zero slope 0.07 az 311 deg: sole error [7.6708, 9.8305] mm, club lift 9.07 mm, contact False, fell True
- zero slope 0.09 az 241 deg: sole error [45.8099, 24.1153] mm, club lift 3.99 mm, contact False, fell True
- zero slope 0.09 az 233 deg: sole error [41.6415, 16.8387] mm, club lift 3.39 mm, contact False, fell True

Caveats:

- V10l was never trained on slopes; remaining failures at >=2% look like the policy, not the env setup
- 6-DOF leg IK fails (sole error 8-46 mm) for some slope azimuths, probably joint limits; feet not flat in those episodes
- club lift up to ~12 mm at 7-9% changes face-to-ball height at address
- mid-swing RSI starts (modes 1/2) are not corrected
- leg offsets (6-40 deg) are held for the whole swing via the reference
- target (contact at 7% within 0.15 of flat for V10l) NOT met: 1/6 vs 6/6
