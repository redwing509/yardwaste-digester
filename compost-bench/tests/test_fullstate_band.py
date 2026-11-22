"""Band arithmetic tests. No 200-day integration."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adm1_fullstate_band import (
    CLASS_LIMITS,
    evaluate_code,
    evaluate_code_to_code,
    load_reference,
    three_way,
)


class BandRegistrationTests(unittest.TestCase):
    def test_band_document_and_table_are_present(self):
        band = (ROOT / "PRE-REGISTERED-BAND-Q02.md").read_text()
        self.assertIn("Written:** Sat 21 Nov 2026, 11:12 PM PST", band)
        self.assertIn("before any", band)
        self.assertIn("new Q-02 200-day full-state runs were started", band)
        self.assertIn("e_rel <= 1.0%", band)
        ref = load_reference()
        self.assertEqual(ref["table6"]["S_ac"]["value"], "0.197629716937552")
        self.assertEqual(ref["table6"]["S_ch4"]["value"], "0.055088776445959")
        self.assertEqual(ref["class_limits"]["A"], 0.01)
        self.assertEqual(ref["class_limits"]["D"], 0.05)

    def test_class_a_one_percent_boundary(self):
        ref = load_reference()
        sac = float(ref["table6"]["S_ac"]["value"])
        preds = {name: float(meta["value"]) for name, meta in ref["table6"].items()}
        preds["S_ac"] = sac * 1.01
        ok, rows, _ = evaluate_code(preds, ref)
        row = next(r for r in rows if r["variable"] == "S_ac")
        self.assertTrue(row["pass"])
        self.assertTrue(ok)
        preds["S_ac"] = sac * 1.0100001
        ok, rows, _ = evaluate_code(preds, ref)
        row = next(r for r in rows if r["variable"] == "S_ac")
        self.assertFalse(row["pass"])
        self.assertFalse(ok)

    def test_class_d_qgas_five_percent(self):
        ref = load_reference()
        q = Decimal(ref["table6"]["Qgas"]["value"])
        preds = {name: float(meta["value"]) for name, meta in ref["table6"].items()}
        preds["Qgas"] = q * Decimal("1.05")
        ok, rows, _ = evaluate_code(preds, ref)
        self.assertTrue(next(r for r in rows if r["variable"] == "Qgas")["pass"])
        preds["Qgas"] = q * Decimal("1.06")
        ok, rows, _ = evaluate_code(preds, ref)
        self.assertFalse(next(r for r in rows if r["variable"] == "Qgas")["pass"])
        self.assertFalse(ok)

    def test_missing_required_is_fail_optional_is_ok(self):
        ref = load_reference()
        preds = {name: float(meta["value"]) for name, meta in ref["table6"].items()}
        del preds["S_ch4"]
        ok, rows, miss = evaluate_code(preds, ref)
        self.assertFalse(ok)
        self.assertEqual(miss, ["S_ch4"])
        preds["S_ch4"] = float(ref["table6"]["S_ch4"]["value"])
        del preds["S_ac-"]
        ok, rows, miss = evaluate_code(preds, ref)
        self.assertTrue(ok)
        self.assertEqual(miss, [])
        self.assertEqual(next(r for r in rows if r["variable"] == "S_ac-")["status"], "not_reported")

    def test_three_way_and_code_to_code(self):
        ref = load_reference()
        a = {name: float(meta["value"]) for name, meta in ref["table6"].items()}
        b = dict(a)
        report = three_way(a, b, ref)
        self.assertTrue(report["three_way_pass"])
        b["S_ac"] = a["S_ac"] * 1.02
        report = three_way(a, b, ref)
        self.assertFalse(report["three_way_pass"])
        self.assertFalse(report["code_to_code_pass"])
        # 2% is still inside the 5% class-B/D bands but not class A
        self.assertTrue(report["qsdsan_pass"])  # 0% vs table
        self.assertFalse(report["pyadm1_pass"])  # 2% vs table on S_ac

    def test_source_files_do_not_publish(self):
        for rel in (
            "src/adm1_fullstate_band.py",
            "src/run_fullstate.py",
            "launch-adm1-fullstate-q02.sh",
        ):
            blob = (ROOT / rel).read_text()
            self.assertNotIn("git push", blob)
            self.assertNotIn("gh pr", blob)
            self.assertNotIn("ssh ", blob)
            self.assertNotIn("pip install", blob)


if __name__ == "__main__":
    unittest.main(verbosity=2)
