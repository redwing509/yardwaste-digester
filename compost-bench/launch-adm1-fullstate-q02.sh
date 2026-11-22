#!/bin/bash
# Q-02 full-state three-way ADM1 comparison launcher.
# Does not git commit, push, or open a PR.
set -euo pipefail

STAGE="$(cd "$(dirname "$0")" && pwd)"
PY="${YWSIM_PYTHON:-python3}"
CPU="${YWSIM_CPU:-0}"
OUT="${YWSIM_RESULT_DIR:-}"

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
export PYTHONPATH="$STAGE/src${PYTHONPATH:+:$PYTHONPATH}"

if command -v taskset >/dev/null 2>&1; then
  exec nice -n 19 taskset -c "$CPU" "$PY" "$STAGE/src/run_fullstate.py" "$@"
fi
exec nice -n 19 "$PY" "$STAGE/src/run_fullstate.py" "$@"
