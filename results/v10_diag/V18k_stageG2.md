# V18k (heel8 80, hstart 1.0, ball_tol .01) and stageG2 first rows. LOCAL, NOT OFFICIAL
- V18k (warm V18i 150k, V12X keys): 50k 13/5/1 .88/.79/.79; 100k 13/5/1 .92/.88/.83, nominal dz +4.7 mm, tc90 1.77. No trigger.
- face_log_h V18k 100k (GATING seeds 7000-7023): D-plane .478 (11/23 contacts). Heel strikes (dy<-8 mm) still 7/23, plus 6 toe misses (dy +12..+21 mm). That is wider strike spread, not centring; heel8 at 80 did not move the heel tail. Start direction not solved (gear-effect misses).
- stageG2 (padded V18i 150k, goal_w 3, lr 1e-5, no DR; local harness v5, heldout and goal task are non-gating):
  - 125k: v4 13 pass/1 fail .92/.88/.83 | heldout .50/.33/.12 | goal contact 24/24, carry pass .12 (median 16.2 m), direction pass .38 (median 9.9 deg)
  - 250k: v4 13/1 .88/.79/.83 | heldout .46/.33/.12 | goal contact 24/24, carry .12 (16.1 m), direction .38 (9.6 deg)

Label (port): LOCAL, Trainer-only, not official; V18k and stageG2 grades are not backed by committed harness JSONs (face_log_h V18k from results/v17_face/faceh_V18k_s580_100000.csv). stageG2 goal-task rows are local, non-gating, and its training command is not in the repo.
