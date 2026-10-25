#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# V16b (Evaluator 2026-10-25 ET): v5/dplane fix re-run. v4 1.5in main row with --harness v5, held-out off (--heldout-dr 0); D-plane now graded on the perturbed
# v4 robustness episodes (seeds 7000-7023). Same exports as the original grades: V18f 4d22d58a (V16), V18d 2a511cb9 (V15), V16y eafa270c (V14). One job at a time, taskset -c 0-1, 2 workers, BLAS threads 2.
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO}; O=results/overnight; PY=${HGS_PY:-python3}; R=${HGS_RO_ROOT:?set HGS_RO_ROOT}
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE V3_FACE_H
for p in "V18f_s530_50k 4d22d58a" "V18d_s511_50k 2a511cb9" "V16y_s402_50k eafa270c"; do set -- $p
  while pgrep -f "_run_j_gateoff" >/dev/null; do sleep 10; done
  J=$O/realism_v5_${1}_15in_v5dplane_gateoff_gp_arm06.json; [ -s $J ] && { echo "SKIP $1"; continue; }
  echo "START $1 $(date +%T)"; V3_HEAD=v4 V3_TEE=1.5in taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$1/ckpt_50000 --v5-repo $R/_ro_trainer_$2 --harness v5 --heldout-dr 0 --json $J.tmp > ${J%.json}.txt 2>$O/_batch_V16b_$1.err; rc=$?
  [ $rc -eq 0 ] && [ -s $J.tmp ] && mv $J.tmp $J; echo "END $1 rc=$rc $(date +%T)"
done; echo ALLDONE
