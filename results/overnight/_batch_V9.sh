#!/bin/bash
# Paths come from env: HGS_EVAL_REPO, HGS_TRAINER_REPO, HGS_RO_ROOT (dir of read-only exports), HGS_PY (interpreter, default python3).
# V9 official grading (Evaluator 2026-10-24 ET): V9a_s91 150k, V9a_s91 100k (init V8a_s90 300k), V8a_s90 300k; keys stageV8_ref_s1, --env_v4 --tee_mode 1.5in.
# RO export f7cbc55 (Trainer HEAD; contains ac13405, c46db64, 35f321b; env geometry unchanged vs 79d86eb (only reward terms in train/v5_train_j.py)). Same per-checkpoint rows as _batch_V4rebase.sh: v4 MAIN 1.5in (gating),
# v4 crown INFO, v3c and v3d at 1.5in. One job at a time, taskset -c 0-1, 2 workers, BLAS threads 2. Layout pre-check per checkpoint; a v4 address mismatch stops the checkpoint.
cd ${HGS_EVAL_REPO:?set HGS_EVAL_REPO to the evaluator checkout}; O=results/overnight; PY=${HGS_PY:-python3}; X4=${HGS_RO_ROOT:?set HGS_RO_ROOT to the dir holding _ro_trainer_<hash> exports}/_ro_trainer_f7cbc55
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2; unset V3_FRICTION_RANGE V3_FACE_H
run() { # tag ck harness teeenv teetag
  J=$O/realism_v5_${1}_${5}_${3}_gateoff_gp_arm06.json; [ -s $J ] && { echo "SKIP $1 $3 $5"; return 0; }
  H="--harness $3"; [ $3 = v3c ] && H=""
  echo "START $1 $3 $5 $(date +%T)"; V3_HEAD=v4 V3_TEE=$4 taskset -c 0-1 $PY $O/_run_j_gateoff_gp_v3.py $O/_evalsnap/$1/$2 --v5-repo $X4 $H --json $J.tmp > ${J%.json}.txt 2>$O/_batch_V9_${1}_${3}_$5.err; rc=$?
  if [ $rc -eq 0 ] && [ -s $J.tmp ]; then mv $J.tmp $J; else echo "FAILED $1 $3 $5 rc=$rc: $(grep -h 'mismatch\|Error\|SystemExit' $O/_batch_V9_${1}_${3}_$5.err | tail -1)"; fi; echo "END $1 $3 $5 rc=$rc $(date +%T)"; return $rc
}
for p in "V9a_s91_150k ckpt_150000 full" "V9a_s91_100k ckpt_100000 full" "V8a_s90_300k ckpt_300000 full"; do set -- $p
  PC=$(taskset -c 0-1 $PY $O/_precheck_layout.py $O/_evalsnap/$1/$2 $X4 ${HGS_TRAINER_REPO:?set HGS_TRAINER_REPO to the Trainer checkout} 2>/dev/null | tail -1); echo "PRECHECK $1 $PC"
  case "$PC" in LAYOUT_OK*) ;; *) echo "BLOCKER $1: layout pre-check not OK, checkpoint stopped"; continue;; esac
  run $1 $2 v4 1.5in 15in || { echo "BLOCKER $1: v4 main failed, checkpoint stopped"; continue; }
  run $1 $2 v4 crown crown16
  [ $3 = full ] && { run $1 $2 v3c 1.5in 15in; run $1 $2 v3d 1.5in 15in; }
done; echo ALLDONE $(date +%T)
