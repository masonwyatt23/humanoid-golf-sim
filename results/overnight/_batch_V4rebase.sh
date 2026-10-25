#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# V4 single re-baseline (Evaluator 2026-10-24 ET): Trainer V4a_s80 / V4b_s81 (--env_v4) + cross-head refs K32a_s72 200k and K34a_s78 200k (best K34 by the Trainer's own
# v3d realistic-head default-tee JSONs). RO export 54b49c6 (env code unchanged 54b49c6..HEAD). Per V4 checkpoint: v4 MAIN (V3_HEAD=v4, V3_TEE=1.5in, gating),
# v4 crown INFO (V3_TEE=crown: 'v4 head, 1.6 in crown tee (equator at sourced crown)'), v3c and v3d at 1.5in on the v4 head (continuity). Refs: v4 main + v4 crown only.
# One job at a time, taskset -c 0-1, 2 workers, BLAS threads 2. Layout/keys pre-check per checkpoint (_precheck_layout.py); a v4 address mismatch makes the worker exit -> FAILED line, checkpoint stopped.
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}; O=results/overnight; PY=${HGS_PY:-python3}; X4=${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_54b49c6
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE V3_FACE_H
run() { # tag ck harness teeenv teetag
  J=$O/realism_v5_${1}_${5}_${3}_gateoff_gp_arm06.json; [ -s $J ] && { echo "SKIP $1 $3 $5"; return 0; }
  H="--harness $3"; [ $3 = v3c ] && H=""
  echo "START $1 $3 $5 $(date +%T)"; V3_HEAD=v4 V3_TEE=$4 taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$1/$2 --v5-repo $X4 $H --json $J.tmp > ${J%.json}.txt 2>$O/_batch_V4rebase_${1}_${3}_$5.err; rc=$?
  if [ $rc -eq 0 ] && [ -s $J.tmp ]; then mv $J.tmp $J; else echo "FAILED $1 $3 $5 rc=$rc: $(grep -h 'mismatch\|Error\|SystemExit' $O/_batch_V4rebase_${1}_${3}_$5.err | tail -1)"; fi; echo "END $1 $3 $5 rc=$rc $(date +%T)"; return $rc
}
for p in "V4a_s80_50k ckpt_50000 full" "V4a_s80_100k ckpt_100000 full" "V4a_s80_150k ckpt_150000 full" "V4a_s80_200k ckpt_200000 full" \
         "V4b_s81_50k ckpt_50000 full" "V4b_s81_100k ckpt_100000 full" "V4b_s81_150k ckpt_150000 full" "V4b_s81_200k ckpt_200000 full" "V4b_s81_250k ckpt_250000 full" "V4b_s81_300k ckpt_300000 full" \
         "K32a_s72_200k ckpt_200000 ref" "K34a_s78_200k ckpt_200000 ref"; do set -- $p
  echo "PRECHECK $1 $(taskset -c 0-1 $PY $O/_precheck_layout.py $O/_evalsnap/$1/$2 $X4 ${HGS_TRAINER_REPO:?set HGS_TRAINER_REPO to the Trainer checkout} 2>/dev/null | tail -1)"
  run $1 $2 v4 1.5in 15in || { echo "BLOCKER $1: v4 main failed, checkpoint stopped"; continue; }
  run $1 $2 v4 crown crown16
  [ $3 = full ] && { run $1 $2 v3c 1.5in 15in; run $1 $2 v3d 1.5in 15in; }
done; echo ALLDONE $(date +%T)
