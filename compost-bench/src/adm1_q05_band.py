"""Q-05 subset loading and frozen code-to-code band (no integration)."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
SUBSET_FILE = CONFIG_DIR / "q05-subset.json"
REQUIRED = ("S_ac_eff_mg_L", "S_ch4_eff_mg_L", "pH", "CH4_kgCOD_d")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_subset(path=SUBSET_FILE) -> dict:
    return json.loads(Path(path).read_text())


def verify_source_checksums(subset=None) -> dict:
    subset = subset if subset is not None else load_subset()
    report = {"ok": True, "files": []}
    for name, meta in subset["qsdsan_sources"].items():
        path = Path(meta["path"])
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


def load_qsdsan_index(subset=None) -> dict:
    subset = subset if subset is not None else load_subset()
    check = verify_source_checksums(subset)
    if not check["ok"]:
        raise RuntimeError("qsdsan source checksum failed: " + json.dumps(check))
    index = {}
    for src_name, meta in subset["qsdsan_sources"].items():
        if not src_name.endswith("_points"):
            continue
        with Path(meta["path"]).open() as fh:
            for line in fh:
                if not line.strip():
                    continue
                rec = json.loads(line)
                key = rec.get("key")
                if key:
                    index[key] = rec
    return index


def class_limits(point: dict, subset=None) -> dict:
    subset = subset if subset is not None else load_subset()
    cls = point["class"]
    if cls == "S":
        return subset["class_S"]
    if cls == "O":
        return subset["class_O"]
    raise ValueError(f"unknown class {cls!r}")


def _dec(value):
    if value is None:
        return None
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not d.is_finite():
        return None
    return d


def evaluate_metric(name: str, pred, ref, limits: dict) -> dict:
    row = {"metric": name, "predicted": pred, "reference": ref, "status": "ok"}
    x = _dec(pred)
    xref = _dec(ref)
    if x is None or xref is None:
        row["status"] = "not_reported"
        row["pass"] = False
        return row
    if name == "pH":
        err = abs(x - xref)
        limit = Decimal(str(limits["pH_abs"]))
        row["abs_err"] = format(err, "f")
        row["limit_abs"] = format(limit, "f")
        row["pass"] = bool(err <= limit)
        return row
    if name in ("S_ac_eff_mg_L", "S_ch4_eff_mg_L"):
        rel_key = name + "_rel"
        floor_key = "S_ac_abs_floor_mg_L" if name.startswith("S_ac") else "S_ch4_abs_floor_mg_L"
    elif name == "CH4_kgCOD_d":
        rel_key = "CH4_kgCOD_d_rel"
        floor_key = "CH4_abs_floor_kgCOD_d"
    else:
        raise ValueError(f"no rule for metric {name}")
    if xref == 0:
        err = abs(x - xref)
        floor = Decimal(str(limits[floor_key]))
        row["abs_err"] = format(err, "f")
        row["limit_abs"] = format(floor, "f")
        row["pass"] = bool(err <= floor)
        return row
    rel = abs(x - xref) / abs(xref)
    limit = Decimal(str(limits[rel_key]))
    row["rel_err"] = format(rel, "f")
    row["limit_rel"] = format(limit, "f")
    row["pass"] = bool(rel <= limit)
    return row


def evaluate_point(point: dict, pred: dict, qsdsan_row: dict, subset=None) -> dict:
    subset = subset if subset is not None else load_subset()
    limits = class_limits(point, subset)
    required = tuple(subset.get("required_metrics") or REQUIRED)
    rows = []
    ok = True
    status_txt = str(qsdsan_row.get("status") or "")
    if "failed" in status_txt.lower() or not status_txt:
        ok = False
    for name in required:
        row = evaluate_metric(name, pred.get(name), qsdsan_row.get(name), limits)
        rows.append(row)
        if not row.get("pass"):
            ok = False
    return {
        "key": point["key"],
        "class": point["class"],
        "pass": ok,
        "qsdsan_status": qsdsan_row.get("status"),
        "rows": rows,
    }


def evaluate_subset(predictions_by_key: dict, subset=None, qsdsan_index=None) -> dict:
    subset = subset if subset is not None else load_subset()
    qsdsan_index = qsdsan_index if qsdsan_index is not None else load_qsdsan_index(subset)
    points = []
    all_ok = True
    missing = []
    for point in subset["points"]:
        key = point["key"]
        if key not in qsdsan_index:
            all_ok = False
            missing.append(key)
            points.append({"key": key, "pass": False, "status": "qsdsan_row_missing"})
            continue
        pred = predictions_by_key.get(key)
        if not pred:
            all_ok = False
            missing.append(key)
            points.append({"key": key, "pass": False, "status": "pyadm1_missing"})
            continue
        ev = evaluate_point(point, pred, qsdsan_index[key], subset)
        points.append(ev)
        if not ev["pass"]:
            all_ok = False
    return {
        "subset_pass": all_ok,
        "n_points": len(subset["points"]),
        "n_passed": sum(1 for p in points if p.get("pass")),
        "missing": missing,
        "points": points,
    }
