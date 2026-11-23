"""Evaluate predictions against the pre-registered Q-02 band.

No integration lives here. The decision rule is frozen in
PRE-REGISTERED-BAND-Q02.md and config/rosen-jeppsson-2006-sec7-table6.json.
"""
from decimal import Decimal
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
CONFIG = HERE.parent / "config" / "rosen-jeppsson-2006-sec7-table6.json"
BAND_DOC = HERE.parent / "PRE-REGISTERED-BAND-Q02.md"
ZERO_ABS = Decimal("1e-12")
CLASS_LIMITS = {"A": Decimal("0.01"), "B": Decimal("0.05"), "C": Decimal("0.02"), "D": Decimal("0.05")}


def load_reference(path=CONFIG):
    with open(path) as handle:
        return json.load(handle)


def _dec(value):
    return Decimal(str(value))


def relative_error(predicted, reference):
    pred = _dec(predicted)
    ref = _dec(reference)
    if ref == 0:
        return None, abs(pred - ref)
    return abs(pred - ref) / abs(ref), abs(pred - ref)


def judge_one(name, predicted, meta):
    """Return a result dict for one variable. predicted may be None (not reported)."""
    required = bool(meta.get("required", True))
    klass = meta["class"]
    limit = CLASS_LIMITS[klass]
    ref = _dec(meta["value"])
    out = {
        "variable": name,
        "class": klass,
        "required": required,
        "unit": meta["unit"],
        "reference": format(ref, "f"),
        "limit_rel": format(limit, "f"),
    }
    if predicted is None:
        out.update({"predicted": None, "status": "not_reported",
                    "pass": (not required)})
        return out
    pred = _dec(predicted)
    rel, absdiff = relative_error(pred, ref)
    out["predicted"] = format(pred, "f")
    out["abs_diff"] = format(absdiff, "f")
    if ref == 0:
        ok = absdiff <= ZERO_ABS
        out["rel_err"] = None
        out["rule"] = "abs_diff <= 1e-12 because reference is zero"
    else:
        ok = rel <= limit
        out["rel_err"] = format(rel, "f")
        out["rule"] = f"rel_err <= {limit} (class {klass})"
    out["pass"] = bool(ok)
    out["status"] = "pass" if ok else "fail"
    return out


def evaluate_code(predictions, reference=None):
    """predictions: name -> number or None. Returns (overall_pass, rows, missing_required)."""
    reference = reference or load_reference()
    table = reference["table6"]
    rows = []
    missing = []
    ok = True
    for name, meta in table.items():
        row = judge_one(name, predictions.get(name, None), meta)
        rows.append(row)
        if meta.get("required", True) and not row["pass"]:
            ok = False
            if row["status"] == "not_reported":
                missing.append(name)
    return ok, rows, missing


def evaluate_code_to_code(pred_a, pred_b, reference=None):
    """Same class rules, but x_ref is the other code's value (Table 6 units)."""
    reference = reference or load_reference()
    table = reference["table6"]
    rows = []
    ok = True
    for name, meta in table.items():
        if not meta.get("required", True):
            continue
        a = pred_a.get(name)
        b = pred_b.get(name)
        if a is None or b is None:
            rows.append({"variable": name, "status": "not_reported", "pass": False})
            ok = False
            continue
        klass = meta["class"]
        limit = CLASS_LIMITS[klass]
        rel, absdiff = relative_error(a, b)
        if _dec(b) == 0:
            passed = absdiff <= ZERO_ABS
            rel_s = None
        else:
            passed = rel <= limit
            rel_s = format(rel, "f")
        rows.append({
            "variable": name,
            "class": klass,
            "a": format(_dec(a), "f"),
            "b": format(_dec(b), "f"),
            "rel_err": rel_s,
            "abs_diff": format(absdiff, "f"),
            "limit_rel": format(limit, "f"),
            "pass": bool(passed),
            "status": "pass" if passed else "fail",
        })
        if not passed:
            ok = False
    return ok, rows


def three_way(pred_qsdsan, pred_pyadm1, reference=None):
    reference = reference or load_reference()
    q_ok, q_rows, q_miss = evaluate_code(pred_qsdsan, reference)
    p_ok, p_rows, p_miss = evaluate_code(pred_pyadm1, reference)
    cc_ok, cc_rows = evaluate_code_to_code(pred_qsdsan, pred_pyadm1, reference)
    three = bool(q_ok and p_ok and cc_ok)
    return {
        "qsdsan_pass": q_ok,
        "pyadm1_pass": p_ok,
        "code_to_code_pass": cc_ok,
        "three_way_pass": three,
        "qsdsan_missing_required": q_miss,
        "pyadm1_missing_required": p_miss,
        "qsdsan_rows": q_rows,
        "pyadm1_rows": p_rows,
        "code_to_code_rows": cc_rows,
        "band_document": str(BAND_DOC),
        "reference_config": str(CONFIG),
    }
