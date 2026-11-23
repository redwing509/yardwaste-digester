#!/bin/bash
# Q-05b jADM1_BSM third-model check. Does not git commit, push, or open a PR.
set -euo pipefail

STAGE="$(cd "$(dirname "$0")" && pwd)"
PY="${YWSIM_PYTHON:-/workspace/venv-ywsim/bin/python}"
OUT="${YWSIM_RESULT_DIR:-}"

if [[ -z "$OUT" ]]; then
  echo "set YWSIM_RESULT_DIR to an absolute path outside this git checkout" >&2
  exit 2
fi

if [[ ! -x "$PY" ]]; then
  echo "runtime python is not executable: $PY" >&2
  exit 2
fi

export YWSIM_REQUIRE_RUNTIME=1
export YWSIM_ALLOW_INTEGRATION="${YWSIM_ALLOW_INTEGRATION:-1}"
export YWSIM_PYTHON="$PY"
export YWSIM_RESULT_DIR="$OUT"
export JADM1_BIN="${JADM1_BIN:-/workspace/digester-tools/bin/jadm1-bsm}"
export PYTHONUNBUFFERED=1
export PYTHONPATH="$STAGE/src${PYTHONPATH:+:$PYTHONPATH}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1

exec nice -n 19 "$PY" "$STAGE/src/run_q05b.py" "$@"
