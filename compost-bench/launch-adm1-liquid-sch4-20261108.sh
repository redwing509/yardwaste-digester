#!/bin/bash
# Public launcher for one liquid S_ch4 benchmark comparison (Compost Bench harness).
# Does not git commit, push, open a PR, or publish.
# Does not create the result directory until run_once.py accepts an absolute
# path outside this git checkout and outside sim/results.
set -euo pipefail

STAGE="$(cd "$(dirname "$0")" && pwd)"
PY="${YWSIM_PYTHON:-python3}"
CPU="${YWSIM_CPU:-0}"
OUT="${YWSIM_RESULT_DIR:-}"
CONFIG="$STAGE/config/adm1_liquid_sch4_20261108.json"

case "$CPU" in
  ''|*[!0-9]*)
    echo "YWSIM_CPU must be one non-negative integer" >&2
    exit 2
    ;;
esac

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
export YWSIM_CPU="$CPU"
export PYTHONUNBUFFERED=1

if command -v taskset >/dev/null 2>&1; then
  exec nice -n 19 taskset -c "$CPU" "$PY" "$STAGE/src/run_once.py" "$CONFIG"
fi
exec nice -n 19 "$PY" "$STAGE/src/run_once.py" "$CONFIG"
