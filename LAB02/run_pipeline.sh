#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON_BIN="${PYTHON_BIN:-python3}"
SEED="${SEED:-7}"
MODEL_OUT="${MODEL_OUT:-model.pkl}"
THRESHOLD="${THRESHOLD:-0.75}"
LOG_FILE="${LOG_FILE:-run.log}"

: > "${LOG_FILE}"

run_stage() {
  local stage_name="$1"
  shift
  if "$@" 2>&1 | tee -a "${LOG_FILE}"; then
    printf '[%s] PASS\n' "${stage_name}" | tee -a "${LOG_FILE}"
  else
    printf '[%s] FAIL\n' "${stage_name}" | tee -a "${LOG_FILE}"
    return 1
  fi
}

run_stage TEST "${PYTHON_BIN}" -m pytest tests -q
run_stage VALIDATE "${PYTHON_BIN}" pipeline.py --stage validate
run_stage TRAIN "${PYTHON_BIN}" pipeline.py --stage train --seed "${SEED}" --out "${MODEL_OUT}"
run_stage GATE "${PYTHON_BIN}" pipeline.py --stage gate --model "${MODEL_OUT}" --threshold "${THRESHOLD}"
