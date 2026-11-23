"""CLI for the Q-05 PyADM1 subset rerun and code-to-code comparison.

Writes JSON under YWSIM_RESULT_DIR (must be an absolute path outside this
git checkout). Does not call git, open a PR, or publish.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from adm1_fullstate_band import three_way
from adm1_q05_band import evaluate_subset, load_subset, verify_source_checksums

STAGE = HERE.parent


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
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
    tmp.replace(path)


def _load_json(path):
    p = Path(path)
    if not p.is_file():
        return None
    return json.loads(p.read_text())


def score_q02_anchor(official_dir: Path) -> dict:
    pred_q = _load_json(official_dir / "qsdsan_predictions.json")
    pred_p = _load_json(official_dir / "pyadm1_predictions.json")
    if pred_q is None or pred_p is None:
        return {"pass": False, "status": "official Q-02 result files missing", "dir": str(official_dir)}
    report = three_way(pred_q, pred_p)
    report["official_dir"] = str(official_dir)
    report["status"] = "three-way PASS" if report["three_way_pass"] else "three-way FAIL"
    report["pass"] = bool(report["three_way_pass"])
    return report


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _run_identity() -> dict:
    """Current harness identity. Resume only if a cached row matches this."""
    repo = STAGE.parent
    ident = {
        "subset_sha256": _sha256(STAGE / "config" / "q05-subset.json"),
        "packaged_sha256": _sha256(STAGE / "config" / "q05-packaged-influent.json"),
        "sweep_sha256": _sha256(HERE / "adm1_sweep_pyadm1.py"),
        "band_sha256": _sha256(HERE / "adm1_q05_band.py"),
        "run_q05_sha256": _sha256(HERE / "run_q05.py"),
    }
    try:
        ident["harness_git_head"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(repo), text=True
        ).strip()
    except Exception:
        ident["harness_git_head"] = None
    return ident


def _params_match(rec: dict, point: dict) -> bool:
    for key in ("feed", "T_C", "Q", "conc_scale", "t_days", "class"):
        if rec.get(key) != point.get(key):
            return False
    return True


def _reusable_ok_keys(points_path: Path, points: list, identity: dict) -> set:
    """Skip only ok rows whose params and harness identity match this run."""
    want = {p["key"]: p for p in points}
    have = set()
    if not points_path.is_file():
        return have
    for line in points_path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = rec.get("key")
        if rec.get("status") != "ok" or key not in want:
            continue
        if rec.get("_run_identity") != identity:
            continue
        if not _params_match(rec, want[key]):
            continue
        have.add(key)
    return have


def _append_jsonl(path: Path, rec: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
        fh.flush()


def _run_one(point: dict) -> dict:
    from adm1_sweep_pyadm1 import run_sweep_pyadm1

    t0 = time.time()
    rec = {
        "key": point["key"],
        "feed": point["feed"],
        "T_C": point["T_C"],
        "Q": point["Q"],
        "conc_scale": point["conc_scale"],
        "t_days": point["t_days"],
        "class": point["class"],
        "status": "failed",
        "_run_identity": _run_identity(),
    }
    try:
        pred = run_sweep_pyadm1(
            feed=point["feed"],
            t_c=point["T_C"],
            q_m3_d=point["Q"],
            conc_scale=point["conc_scale"],
            t_days=point["t_days"],
        )
        rec.update({
            "status": "ok",
            "S_ac_eff_mg_L": pred["S_ac_eff_mg_L"],
            "S_ch4_eff_mg_L": pred["S_ch4_eff_mg_L"],
            "pH": pred["pH"],
            "CH4_kgCOD_d": pred["CH4_kgCOD_d"],
            "CO2_kgC_d": pred["CO2_kgC_d"],
            "Qgas": pred["Qgas"],
            "_q_gas_headspace": pred["_q_gas_headspace"],
            "_commit": pred["_commit"],
            "_solver": pred["_solver"],
            "prediction": pred,
        })
    except Exception as exc:
        rec["error"] = repr(exc)
    rec["runtime_s"] = time.time() - t0
    rec["written_at"] = _now()
    return rec


def main(argv):
    if os.environ.get("YWSIM_ALLOW_INTEGRATION") != "1":
        print(json.dumps({
            "action": "rejected",
            "exit_code": 2,
            "error": "refusing the Q-05 integration unless YWSIM_ALLOW_INTEGRATION=1",
        }))
        return 2
    result_dir = os.environ.get("YWSIM_RESULT_DIR")
    if not result_dir:
        print("set YWSIM_RESULT_DIR to an absolute path outside this git checkout", file=sys.stderr)
        return 2
    _refuse_inside_checkout(result_dir, STAGE)
    out = Path(result_dir)
    out.mkdir(parents=True, exist_ok=True)

    subset = load_subset()
    checksums = verify_source_checksums(subset)
    _json(out / "source_checksums.json", checksums)
    if not checksums["ok"]:
        summary = {"written_at": _now(), "status": "FAIL source checksum", "checksums": checksums}
        _json(out / "SUMMARY.json", summary)
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        return 1

    anchor = score_q02_anchor(Path(subset["q02_anchor"]["official_results"]))
    _json(out / "q02_anchor.json", anchor)

    workers = int(os.environ.get("YWSIM_WORKERS", "1"))
    if workers < 1:
        raise SystemExit("YWSIM_WORKERS must be >= 1")
    only = argv[1:]
    points = [p for p in subset["points"] if not only or p["key"] in only]
    points_path = out / "pyadm1_points.jsonl"
    identity = _run_identity()
    have = _reusable_ok_keys(points_path, points, identity)
    todo = [p for p in points if p["key"] not in have]
    summary = {
        "written_at": _now(),
        "status": "running",
        "n_subset": len(subset["points"]),
        "n_selected": len(points),
        "n_already": len(points) - len(todo),
        "n_todo": len(todo),
        "workers": workers,
        "q02_anchor_pass": anchor.get("pass"),
        "run_identity": identity,
    }
    _json(out / "SUMMARY.json", summary)

    results = []
    if todo and workers == 1:
        for point in todo:
            rec = _run_one(point)
            slim = {k: v for k, v in rec.items() if k != "prediction"}
            _append_jsonl(points_path, slim)
            _json(out / "predictions" / (point["key"].replace(":", "_") + ".json"), rec)
            results.append(rec)
            print(json.dumps({
                "key": rec["key"], "status": rec["status"], "runtime_s": rec.get("runtime_s"),
            }), flush=True)
    elif todo:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futs = {pool.submit(_run_one, p): p["key"] for p in todo}
            for fut in as_completed(futs):
                rec = fut.result()
                slim = {k: v for k, v in rec.items() if k != "prediction"}
                _append_jsonl(points_path, slim)
                _json(out / "predictions" / (rec["key"].replace(":", "_") + ".json"), rec)
                results.append(rec)
                print(json.dumps({
                    "key": rec["key"], "status": rec["status"], "runtime_s": rec.get("runtime_s"),
                }), flush=True)

    # Reload all finished predictions for scoring.
    predictions = {}
    pred_dir = out / "predictions"
    if pred_dir.is_dir():
        for path in pred_dir.glob("*.json"):
            rec = json.loads(path.read_text())
            if rec.get("status") == "ok" and rec.get("key"):
                point = next((p for p in points if p["key"] == rec["key"]), None)
                if point is None:
                    continue
                ident = rec.get("_run_identity")
                if ident is not None and ident != identity:
                    continue
                if ident is None and not _params_match(rec, point):
                    continue
                if ident is None:
                    # Legacy official r2 rows have no identity stamp; accept
                    # them only when this run's parameters still match.
                    pass
                predictions[rec["key"]] = rec
    # jsonl fallback if a prediction file is missing but slim row exists
    if points_path.is_file():
        for line in points_path.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("status") != "ok" or rec.get("key") in predictions:
                continue
            point = next((p for p in points if p["key"] == rec["key"]), None)
            if point is None:
                continue
            ident = rec.get("_run_identity")
            if ident is not None and ident != identity:
                continue
            if ident is None and not _params_match(rec, point):
                continue
            predictions[rec["key"]] = rec

    comparison = evaluate_subset(predictions, subset)
    comparison["written_at"] = _now()
    _json(out / "comparison.json", comparison)

    q05_pass = bool(anchor.get("pass")) and bool(comparison.get("subset_pass"))
    summary = {
        "written_at": _now(),
        "status": "Q-05 PASS" if q05_pass else "Q-05 FAIL",
        "q05_pass": q05_pass,
        "q02_anchor_pass": anchor.get("pass"),
        "subset_pass": comparison.get("subset_pass"),
        "n_points": comparison.get("n_points"),
        "n_passed": comparison.get("n_passed"),
        "missing": comparison.get("missing"),
        "workers": workers,
        "run_identity": identity,
    }
    _json(out / "SUMMARY.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0 if q05_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
