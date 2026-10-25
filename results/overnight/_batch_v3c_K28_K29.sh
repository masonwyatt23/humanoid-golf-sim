#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# v3c independent scores of K28/K29 Trainer checkpoints (read-only exports; snaps md5'd in _evalsnap_md5_K28_K29.txt), priority order
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}; O=results/overnight
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE
for p in "dfc30a7 K28b_s63_400k ckpt_400000" "dfc30a7 K28b_s63_300k ckpt_300000" "dfc30a7 K28a_s62_400k ckpt_400000" "dfc30a7 K28a_s62_100k ckpt_100000" \
         "6c18fd0 K29b_s65_300k ckpt_300000" "6c18fd0 K29a_s64_300k ckpt_300000" \
         "dfc30a7 K28a_s62_200k ckpt_200000" "dfc30a7 K28a_s62_300k ckpt_300000" "dfc30a7 K28b_s63_100k ckpt_100000" "dfc30a7 K28b_s63_200k ckpt_200000" \
         "6c18fd0 K29a_s64_100k ckpt_100000" "6c18fd0 K29a_s64_200k ckpt_200000" "6c18fd0 K29b_s65_100k ckpt_100000" "6c18fd0 K29b_s65_200k ckpt_200000"; do set -- $p
 J=$O/realism_v5_${2}_dtfix_newchecks_v3c_gateoff_gp_arm06.json; T=${J%.json}.txt
 [ -s $J ] && { echo SKIP $2; continue; }
 echo "START $2 $(date +%H:%M:%S)"; taskset -c 0-1 ${HGS_PY:-python3} $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$2/$3 --v5-repo ${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_$1 --json $J.tmp > $T.tmp 2>$O/_batch_v3c_K28_K29_$2.err; rc=$?
 if [ $rc -eq 0 ] && [ -s $J.tmp ]; then mv $J.tmp $J; mv $T.tmp $T; else echo "FAILED $2 rc=$rc (tmp kept)"; fi; echo "END $2 rc=$rc $(date +%H:%M:%S)"
done; echo ALLDONE
