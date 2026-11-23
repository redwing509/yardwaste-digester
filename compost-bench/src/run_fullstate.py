"""CLI for the Q-02 three-way ADM1 comparison.

Writes JSON under YWSIM_RESULT_DIR (must be an absolute path outside this
git checkout). Does not call git, open a PR, or publish.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from adm1_fullstate_band import three_way, evaluate_code, load_reference


def _refuse_inside_checkout(result_dir, stage):
    result = Path(result_dir).resolve()
    stage = Path(stage).resolve()
    if stage in result.parents or result == stage:
        raise SystemExit("YWSIM_RESULT_DIR must be outside the git checkout")
    if result.as_posix().endswith("/sim/results") or "/sim/results/" in result.as_posix():
        raise SystemExit("refusing sim/results")
    git = stage
    while git != git.parent:
        if (git / ".git").exists():
            try:
                result.relative_to(git)
            except ValueError:
                break
            else:
                raise SystemExit("YWSIM_RESULT_DIR must be outside the git checkout")
        git = git.parent


def _now():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %I:%M %p %Z")


def _json(path, payload):
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
    tmp.replace(path)


def main(argv):
    if os.environ.get("YWSIM_ALLOW_INTEGRATION") != "1":
        print(json.dumps({"action": "rejected", "exit_code": 2,
                          "error": "refusing the 200-day integration unless YWSIM_ALLOW_INTEGRATION=1"}))
        return 2
    result_dir = os.environ.get("YWSIM_RESULT_DIR")
    if not result_dir:
        print("set YWSIM_RESULT_DIR to an absolute path outside this git checkout", file=sys.stderr)
        return 2
    stage = HERE.parent
    _refuse_inside_checkout(result_dir, stage)
    out = Path(result_dir)
    out.mkdir(parents=True, exist_ok=True)
    codes = argv[1:] or ["qsdsan", "pyadm1", "compare"]
    pred_q = pred_p = None
    summary = {"written_at": _now(), "codes": codes, "status": "run, pending band evaluation"}

    if "qsdsan" in codes or "compare" in codes:
        from adm1_fullstate_qsdsan import run_qsdsan
        pred_q = run_qsdsan()
        _json(out / "qsdsan_predictions.json", pred_q)
        ok, rows, miss = evaluate_code(pred_q)
        _json(out / "qsdsan_vs_table6.json", {"pass": ok, "missing_required": miss, "rows": rows})
        summary["qsdsan_pass"] = ok

    if "pyadm1" in codes or "compare" in codes:
        from adm1_fullstate_pyadm1 import run_pyadm1
        pred_p = run_pyadm1()
        _json(out / "pyadm1_predictions.json", pred_p)
        ok, rows, miss = evaluate_code(pred_p)
        _json(out / "pyadm1_vs_table6.json", {"pass": ok, "missing_required": miss, "rows": rows})
        summary["pyadm1_pass"] = ok

    if "compare" in codes:
        if pred_q is None or pred_p is None:
            raise SystemExit("compare needs both codes")
        report = three_way(pred_q, pred_p)
        report["written_at"] = _now()
        report["status"] = "three-way PASS" if report["three_way_pass"] else "three-way FAIL"
        _json(out / "three_way_report.json", report)
        summary["three_way_pass"] = report["three_way_pass"]
        summary["status"] = report["status"]

    _json(out / "SUMMARY.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if "compare" in codes and not summary.get("three_way_pass"):
        return 1
    if "qsdsan" in codes and not summary.get("qsdsan_pass", True):
        return 1
    if "pyadm1" in codes and not summary.get("pyadm1_pass", True):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
