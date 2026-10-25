#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# v3c (default) then LIVE v3d (--harness v3d) independent scores of K29a/b 400k + all K30 snapshots (read-only exports 6c18fd0 / 4a955d8; snaps md5'd in _evalsnap_md5_K29_K30.txt); worker with strike dy/dz (4bb0801)
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}; O=results/overnight
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE
for p in "c79bac2 K31a_s68_200k ckpt_200000" "6c18fd0 K29a_s64_400k ckpt_400000" "6c18fd0 K29b_s65_400k ckpt_400000" "4a955d8 K30a_s66_100k ckpt_100000" "4a955d8 K30a_s66_200k ckpt_200000" "4a955d8 K30a_s66_300k ckpt_300000" \
         "4a955d8 K30b_s67_100k ckpt_100000" "4a955d8 K30b_s67_200k ckpt_200000" "4a955d8 K30b_s67_300k ckpt_300000" "4a955d8 K30b_s67_400k ckpt_400000"; do set -- $p
 for H in v3c v3d; do
 J=$O/realism_v5_${2}_dtfix_newchecks_${H}_gateoff_gp_arm06.json; T=${J%.json}.txt
 [ -s $J ] && { echo SKIP $2 $H; continue; }
 X=""; [ $H = v3d ] && X="--harness v3d"
 echo "START $2 $H $(date +%H:%M:%S)"; taskset -c 0-1 ${HGS_PY:-python3} $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$2/$3 --v5-repo ${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_$1 $X --json $J.tmp > $T.tmp 2>$O/_batch_v3cd_K29_K30_${2}_$H.err; rc=$?
 if [ $rc -eq 0 ] && [ -s $J.tmp ]; then mv $J.tmp $J; mv $T.tmp $T; else echo "FAILED $2 $H rc=$rc (tmp kept)"; fi; echo "END $2 $H rc=$rc $(date +%H:%M:%S)"
 done
done; echo ALLDONE
