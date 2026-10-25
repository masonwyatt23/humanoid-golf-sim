# V16y_s402 / V17f_s422 configs (for the Repo Agent). Scores are local, not official.
- *_args.json are verbatim copies of results/v5_runs/stageV16y_s402/args.json and stageV17f_s422/args.json (the full parsed train.v5_train_j args). Keys: results/v5_runs/stageV12U_ref_s1/tuned_keys_flat.json.
- Lineage: V12U keys -> V16s 100k (from V16f 100k <- ... <- V13h 50k) -> V16y (recipe U14). V17f is recipe U14 or U16; see init_ck in its args.
- Robustness gate gain (.96/.92/.92) comes from toe strike / gear effect, not face control (results/v17_face, dy_frame_check_V17.md). Officially FAIL 13/4/2 on t/c; the v5 D-plane row fails.
- (port) init_ck checkpoints are not in git; official grades are in results/overnight/V14_GRADE.md.
