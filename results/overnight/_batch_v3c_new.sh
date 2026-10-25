#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# v3c independent scores of new Trainer checkpoints (read-only exports)
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}; O=results/overnight
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE
for p in "a1d67c8 K23b_s52_300k ckpt_300000" "5cb4d43 K25b_s56_400k ckpt_400000" "9225b4a K27a_s59_400k ckpt_400000" "493dae5_k27ref K27b_s60_400k ckpt_400000" "493dae5_k27ref K27c_s61_300k ckpt_300000"; do set -- $p
 J=$O/realism_v5_${2}_dtfix_newchecks_v3c_gateoff_gp_arm06.json; T=${J%.json}.txt
 [ -s $J ] && { echo SKIP $2; continue; }
 echo "START $2 $(date +%H:%M:%S)"; taskset -c 0-1 ${HGS_PY:-python3} $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$2/$3 --v5-repo ${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_$1 --json $J > $T 2>$O/_batch_v3c_new_$2.err; echo "END $2 rc=$? $(date +%H:%M:%S)"
done; echo ALLDONE
