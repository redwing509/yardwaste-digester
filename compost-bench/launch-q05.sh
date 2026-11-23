#!/bin/bash
# Q-05 PyADM1 subset rerun. Does not git commit, push, or open a PR.
set -euo pipefail

STAGE="$(cd "$(dirname "$0")" && pwd)"
PY="${YWSIM_PYTHON:-/workspace/digester-tools/envs/pyadm1/bin/python}"
OUT="${YWSIM_RESULT_DIR:-}"
WORKERS="${YWSIM_WORKERS:-2}"

if [[ -z "$OUT" ]]; then
  echo "set YWSIM_RESULT_DIR to an absolute path outside this git checkout" >&2
  exit 2
fi

if ! command -v "$PY" >/dev/null 2>&1 && [[ ! -x "$PY" ]]; then
  echo "runtime python is not executable: $PY" >&2
  exit 2
fi

export YWSIM_REQUIRE_RUNTIME=1
export YWSIM_ALLOW_INTEGRATION=1
export YWSIM_PYTHON="$PY"
export YWSIM_RESULT_DIR="$OUT"
export YWSIM_WORKERS="$WORKERS"
export PYTHONUNBUFFERED=1
export PYTHONPATH="$STAGE/src${PYTHONPATH:+:$PYTHONPATH}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1

exec nice -n 19 "$PY" "$STAGE/src/run_q05.py" "$@"
