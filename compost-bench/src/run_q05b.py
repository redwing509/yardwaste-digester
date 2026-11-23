"""CLI for the Q-05b jADM1_BSM third-model check and steam-table comparison.

Writes JSON under YWSIM_RESULT_DIR (must be an absolute path outside this
git checkout). Does not call git, open a PR, or publish.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from adm1_q05b_band import evaluate_study, load_study, verify_source_checksums
from iapws_if97_psat import P_C_MPA, T_C_K, psat_bar, psat_mpa, rosen_psat_bar

STAGE = HERE.parent


def _refuse_inside_checkout(result_dir, stage):
    result = Path(result_dir).resolve()
    stage = Path(stage).resolve()
    if stage in result.parents or result == stage:
        raise SystemExit("YWSIM_RESULT_DIR must be outside the git checkout")
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
    return datetime.now().astimezone().strftime("%Y-%m-%d %I:%M:%S %p %Z")


def _json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
    tmp.replace(path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def qsdsan_psat_bar(t_k: float) -> dict:
    """QSDsan 1.5.3 / EXPOsan ADM H2O.Psat in bar, as used by AnaerobicCSTR.p_vapor."""
    # Import inside the function so unit tests that do not need it stay light.
    from qsdsan import process_models as pc
    from qsdsan.utils import auom

    cmps = pc.create_adm1_cmps()
    p_pa = float(cmps.H2O.Psat(float(t_k)))
    p_bar = p_pa * float(auom("Pa").conversion_factor("bar"))
    return {
        "T_K": float(t_k),
        "Psat_Pa": p_pa,
        "Psat_bar": p_bar,
        "source": "qsdsan 1.5.3 create_adm1_cmps().H2O.Psat, Pa converted with auom to bar",
    }


def steam_table_report() -> dict:
    temps = [("30C", 303.15), ("35C", 308.15)]
    rows = []
    closer = []
    qsdsan_ok = True
    qsdsan_error = None
    for label, t in temps:
        if97 = psat_bar(t)
        rosen = rosen_psat_bar(t)
        try:
            qsd = qsdsan_psat_bar(t)
            q_bar = qsd["Psat_bar"]
        except Exception as exc:  # noqa: BLE001 — recorded as incomplete, not replaced
            qsdsan_ok = False
            qsdsan_error = f"{type(exc).__name__}: {exc}"
            qsd = None
            q_bar = None
        row = {
            "label": label,
            "T_C": t - 273.15,
            "T_K": t,
            "IF97_bar": if97,
            "rosen_bar": rosen,
            "rosen_abs_err_bar": abs(rosen - if97),
            "qsdsan": qsd,
            "qsdsan_bar": q_bar,
            "qsdsan_abs_err_bar": None if q_bar is None else abs(q_bar - if97),
        }
        if q_bar is None:
            row["closer"] = "INCOMPLETE"
        elif row["rosen_abs_err_bar"] < row["qsdsan_abs_err_bar"]:
            row["closer"] = "ROSEN_CLOSER"
        elif row["qsdsan_abs_err_bar"] < row["rosen_abs_err_bar"]:
            row["closer"] = "QSDSAN_CLOSER"
        else:
            row["closer"] = "TIE"
        closer.append(row["closer"])
        rows.append(row)
    if not qsdsan_ok:
        overall = "INCOMPLETE"
    elif all(c == "ROSEN_CLOSER" for c in closer):
        overall = "ROSEN_CLOSER"
    elif all(c == "QSDSAN_CLOSER" for c in closer):
        overall = "QSDSAN_CLOSER"
    elif all(c == "TIE" for c in closer):
        overall = "TIE"
    else:
        overall = "MIXED"
    return {
        "written_at": _now(),
        "method_document": "PRE-REGISTERED-BAND-Q05B.md",
        "if97": {
            "citation": "IAPWS R7-97(2012) Region 4, Eqs. 29-31 / Table 34",
            "critical_T_K": T_C_K,
            "critical_p_MPa_published": P_C_MPA,
            "critical_p_MPa_computed": psat_mpa(T_C_K),
        },
        "rows": rows,
        "overall_closer": overall,
        "qsdsan_ok": qsdsan_ok,
        "qsdsan_error": qsdsan_error,
        "notes": (
            "Closeness uses IAPWS-IF97 as the primary reference. "
            "This comparison does not change PRE-REGISTERED-BAND-Q05.md "
            "and does not overturn the official Q-05 FAIL."
        ),
    }


def run_points(result_dir: Path, study: dict) -> dict:
    from adm1_sweep_jadm1 import DEFAULT_JADM1_COMMIT, run_jadm1_point

    thirds = {}
    records = []
    for point in study["points"]:
        key = point["key"]
        work = result_dir / "runs" / key.replace(":", "_")
        rec = {
            "key": key,
            "feed": point["feed"],
            "T_C": point["T_C"],
            "Q": point["Q"],
            "conc_scale": point["conc_scale"],
            "t_days": point["t_days"],
            "third_model": "jADM1_BSM",
            "third_commit": DEFAULT_JADM1_COMMIT,
            "workdir": str(work),
        }
        try:
            metrics = run_jadm1_point(
                feed=point["feed"],
                t_c=point["T_C"],
                q_m3_d=point["Q"],
                conc_scale=point["conc_scale"],
                t_days=point["t_days"],
                workdir=work,
            )
            rec.update(metrics)
            thirds[key] = {m: metrics[m] for m in study["required_metrics"]}
            rec["status"] = "ok"
        except Exception as exc:  # noqa: BLE001 — recorded per point
            rec["status"] = "failed"
            rec["error"] = f"{type(exc).__name__}: {exc}"
        records.append(rec)
        _json(result_dir / "predictions" / f"{key.replace(':', '_')}.json", rec)
    return {"records": records, "thirds": thirds}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    only_steam = "--steam-only" in argv
    argv = [a for a in argv if a != "--steam-only"]
    result_dir = os.environ.get("YWSIM_RESULT_DIR")
    if not result_dir:
        raise SystemExit("set YWSIM_RESULT_DIR to an absolute path outside this git checkout")
    result_dir = Path(result_dir)
    if not result_dir.is_absolute():
        raise SystemExit("YWSIM_RESULT_DIR must be absolute")
    _refuse_inside_checkout(result_dir, STAGE)
    result_dir.mkdir(parents=True, exist_ok=True)

    study = load_study()
    check = verify_source_checksums(study)
    _json(result_dir / "source_checksums.json", check)
    if not check["ok"]:
        raise SystemExit("frozen Q-05 source checksum failed; refusing to score")

    if only_steam or os.environ.get("YWSIM_STEAM_ONLY") == "1":
        steam = steam_table_report()
        _json(result_dir / "steam_table.json", steam)
        print(json.dumps({"steam_overall_closer": steam["overall_closer"], "written_at": steam["written_at"]}, indent=2))
        return 0

    if os.environ.get("YWSIM_ALLOW_INTEGRATION") != "1":
        raise SystemExit("refusing jADM1 integration unless YWSIM_ALLOW_INTEGRATION=1")

    steam_path = result_dir / "steam_table.json"
    steam = None
    if steam_path.is_file():
        steam = json.loads(steam_path.read_text())
        if steam.get("overall_closer") in (None, "INCOMPLETE") or not steam.get("qsdsan_ok", False):
            steam = None
    if steam is None:
        steam = steam_table_report()
        _json(steam_path, steam)

    run = run_points(result_dir, study)
    _json(result_dir / "jadm1_points.json", run["records"])
    ev = evaluate_study(run["thirds"], study=study, require_checksums=True)
    ev["written_at"] = _now()
    ev["steam_table"] = {
        "overall_closer": steam.get("overall_closer"),
        "qsdsan_ok": steam.get("qsdsan_ok"),
        "path": str(steam_path),
    }
    ev["q05_fail_unchanged"] = True
    ev["band_commit_note"] = (
        "Rule frozen at feat/q05b-third-adm1:1216299 before any jADM1_BSM integration."
    )
    # Official merge eligibility also requires the steam table to have completed.
    if steam.get("overall_closer") in (None, "INCOMPLETE") or not steam.get("qsdsan_ok", False):
        ev["study_pass"] = False
        ev["merge_eligible"] = False
        ev["steam_incomplete"] = True
    _json(result_dir / "comparison.json", ev)
    summary = {
        "written_at": ev["written_at"],
        "centre_pass": ev["centre_pass"],
        "overall_siding": ev["overall_siding"],
        "study_pass": ev["study_pass"],
        "merge_eligible": ev["merge_eligible"],
        "steam_overall_closer": steam.get("overall_closer"),
        "q05_fail_unchanged": True,
        "points": [
            {
                "key": p["key"],
                "role": p["role"],
                "siding": p["siding"],
                "liquids_ok": p["liquids_ok"],
                "ch4_agrees_pyadm1": p["ch4_agrees_pyadm1"],
                "ch4_agrees_qsdsan": p["ch4_agrees_qsdsan"],
                "third": p["third"],
            }
            for p in ev["points"]
        ],
    }
    _json(result_dir / "SUMMARY.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if ev["study_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
