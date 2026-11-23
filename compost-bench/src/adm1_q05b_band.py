"""Q-05b subset loading and frozen third-model agreement band (no integration)."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
POINTS_FILE = CONFIG_DIR / "q05b-points.json"
REQUIRED = ("S_ac_eff_mg_L", "S_ch4_eff_mg_L", "pH", "CH4_kgCOD_d")
LIQUIDS = ("S_ac_eff_mg_L", "S_ch4_eff_mg_L", "pH")
SIDES_PY = "SIDES_WITH_PYADM1"
SIDES_QSD = "SIDES_WITH_QSDSAN"
BOTH = "AGREES_WITH_BOTH"
NEITHER = "AGREES_WITH_NEITHER"
INCONCLUSIVE = "INCONCLUSIVE"
MIXED = "MIXED"
CONCLUSIVE = frozenset({SIDES_PY, SIDES_QSD, BOTH})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_study(path=POINTS_FILE) -> dict:
    return json.loads(Path(path).read_text())


def _resolve_source_path(meta: dict, study_path: Path) -> Path:
    path = Path(meta["path"])
    if path.is_absolute():
        return path
    # Relative paths in the config are from compost-bench/.
    return (study_path.resolve().parent.parent / path).resolve()


def verify_source_checksums(study=None) -> dict:
    study = study if study is not None else load_study()
    study_path = POINTS_FILE
    report = {"ok": True, "files": []}
    for name, meta in study["q05_sources"].items():
        path = _resolve_source_path(meta, study_path)
        row = {"name": name, "path": str(path), "expected": meta["sha256"]}
        if not path.is_file():
            row["status"] = "missing"
            report["ok"] = False
        else:
            actual = sha256_file(path)
            row["actual"] = actual
            if actual.lower() != meta["sha256"].lower():
                row["status"] = "mismatch"
                report["ok"] = False
            else:
                row["status"] = "ok"
        report["files"].append(row)
    return report


def _dec(x) -> Decimal:
    try:
        return Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"non-numeric value {x!r}") from exc


def metric_agrees(x, x_ref, metric: str, limits: dict) -> dict:
    """Apply the frozen Class S rule to one metric against one reference."""
    out = {"metric": metric, "x": x, "x_ref": x_ref, "agrees": False, "status": "ok"}
    try:
        xv = _dec(x)
        rv = _dec(x_ref)
    except ValueError:
        out["status"] = "non_finite"
        return out
    if not (xv.is_finite() and rv.is_finite()):
        out["status"] = "non_finite"
        return out
    if metric == "pH":
        err = abs(xv - rv)
        out["abs_err"] = format(err, "f")
        out["agrees"] = err <= _dec(limits["pH_abs"])
        return out
    if metric in ("S_ac_eff_mg_L", "S_ch4_eff_mg_L"):
        rel_lim = _dec(limits[f"{metric}_rel"])
        floor = _dec(limits["S_ac_abs_floor_mg_L"] if "S_ac" in metric else limits["S_ch4_abs_floor_mg_L"])
    elif metric == "CH4_kgCOD_d":
        rel_lim = _dec(limits["CH4_kgCOD_d_rel"])
        floor = _dec(limits["CH4_abs_floor_kgCOD_d"])
    else:
        raise KeyError(metric)
    if rv == 0:
        err = abs(xv - rv)
        out["abs_err"] = format(err, "f")
        out["agrees"] = err <= floor
        return out
    rel = abs(xv - rv) / abs(rv)
    out["rel_err"] = format(rel, "f")
    out["agrees"] = rel <= rel_lim
    return out


def point_by_key(study, key: str) -> dict:
    for p in study["points"]:
        if p["key"] == key:
            return p
    raise KeyError(key)


def evaluate_point(third: dict, point: dict, limits: dict) -> dict:
    """Score one third-model point against frozen PyADM1 and qsdsan values."""
    rows = {"pyadm1": {}, "qsdsan": {}}
    complete = True
    for metric in REQUIRED:
        if metric not in third or third[metric] is None:
            complete = False
            rows["pyadm1"][metric] = {"metric": metric, "agrees": False, "status": "missing"}
            rows["qsdsan"][metric] = {"metric": metric, "agrees": False, "status": "missing"}
            continue
        rows["pyadm1"][metric] = metric_agrees(third[metric], point["pyadm1"][metric], metric, limits)
        rows["qsdsan"][metric] = metric_agrees(third[metric], point["qsdsan"][metric], metric, limits)
        if rows["pyadm1"][metric]["status"] != "ok" or rows["qsdsan"][metric]["status"] != "ok":
            complete = False
    liquids_ok = complete and all(
        rows["pyadm1"][m]["agrees"] and rows["qsdsan"][m]["agrees"] for m in LIQUIDS
    )
    agr_py = bool(complete and rows["pyadm1"]["CH4_kgCOD_d"]["agrees"])
    agr_q = bool(complete and rows["qsdsan"]["CH4_kgCOD_d"]["agrees"])
    if not complete or not liquids_ok:
        siding = INCONCLUSIVE
    elif agr_py and not agr_q:
        siding = SIDES_PY
    elif agr_q and not agr_py:
        siding = SIDES_QSD
    elif agr_py and agr_q:
        siding = BOTH
    else:
        siding = NEITHER
    centre_ch4_ok = agr_py or agr_q
    return {
        "key": point["key"],
        "role": point["role"],
        "complete": complete,
        "liquids_ok": liquids_ok,
        "ch4_agrees_pyadm1": agr_py,
        "ch4_agrees_qsdsan": agr_q,
        "centre_ch4_ok": centre_ch4_ok,
        "siding": siding,
        "rows": rows,
        "third": {m: third.get(m) for m in REQUIRED},
    }


def overall_siding(brewery_verdicts) -> str:
    """Combine two brewery siding labels. INCONCLUSIVE is handled by the caller."""
    v = list(brewery_verdicts)
    if any(x == INCONCLUSIVE for x in v):
        return INCONCLUSIVE
    if len(v) != 2:
        return INCONCLUSIVE
    a, b = v[0], v[1]
    if a == b:
        return a
    s = {a, b}
    if s <= {SIDES_PY, BOTH} and SIDES_PY in s:
        return SIDES_PY
    if s <= {SIDES_QSD, BOTH} and SIDES_QSD in s:
        return SIDES_QSD
    return MIXED


def evaluate_study(thirds: dict, study=None, require_checksums=True) -> dict:
    """thirds maps key -> dict of required metrics from the third model."""
    study = study if study is not None else load_study()
    if require_checksums:
        check = verify_source_checksums(study)
        if not check["ok"]:
            raise RuntimeError("Q-05b frozen source checksum failed: " + json.dumps(check))
    limits = study["class_S"]
    points = []
    for point in study["points"]:
        key = point["key"]
        third = thirds.get(key) or {}
        points.append(evaluate_point(third, point, limits))
    by_role = {p["role"]: [] for p in points}
    for p in points:
        by_role.setdefault(p["role"], []).append(p)
    anchors = [p for p in points if p["role"] == "anchor"]
    breweries = [p for p in points if p["role"] == "brewery_fail"]
    centre = anchors[0] if len(anchors) == 1 else None
    centre_pass = bool(
        centre
        and centre["complete"]
        and centre["liquids_ok"]
        and centre["centre_ch4_ok"]
    )
    brewery_complete = len(breweries) == 2 and all(p["complete"] for p in breweries)
    if not centre_pass:
        overall = INCONCLUSIVE
    else:
        overall = overall_siding([p["siding"] for p in breweries])
    study_pass = bool(
        centre_pass
        and brewery_complete
        and all(p["liquids_ok"] for p in breweries)
        and overall in CONCLUSIVE
        and study.get("q05_fail_unchanged", True)
    )
    return {
        "centre_pass": centre_pass,
        "overall_siding": overall,
        "study_pass": study_pass,
        "merge_eligible": study_pass,
        "q05_fail_unchanged": bool(study.get("q05_fail_unchanged", True)),
        "points": points,
    }
