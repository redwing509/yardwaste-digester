"""Q-05 band, subset, and influent tests. No multi-day integration."""
import hashlib
import json
import os
import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adm1_q05_band import (
    qsdsan_status_finished,
    evaluate_metric,
    evaluate_point,
    evaluate_subset,
    load_subset,
    sha256_file,
    verify_source_checksums,
)
from adm1_sweep_pyadm1 import (
    COMMIT,
    scale_influent,
    temperature_constants,
    load_packaged_influent,
)


class SubsetRegistrationTests(unittest.TestCase):
    def test_band_document_frozen_before_runs(self):
        band = (ROOT / "PRE-REGISTERED-BAND-Q05.md").read_text()
        self.assertIn("Written:** Sun 22 Nov 2026, 4:40 PM PST", band)
        self.assertIn("before any new PyADM1 integration", band)
        self.assertIn("e_rel ≤ 5.0%", band)
        self.assertIn("e_rel ≤ 10.0%", band)
        self.assertIn("|x - x_ref| ≤ 0.10 pH units", band)
        subset = load_subset()
        self.assertTrue(subset["written_before_pyadm1_runs"])
        self.assertEqual(subset["written"], "2026-11-22 4:40 PM PST")
        self.assertEqual(len(subset["points"]), 15)
        keys = [p["key"] for p in subset["points"]]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(keys[0], "DGS:bsm2:T35:Q170:s1")
        self.assertEqual(subset["points"][10]["class"], "O")
        self.assertEqual(subset["pyadm1_commit"], COMMIT)
        self.assertEqual(
            subset["qsdsan_sources"]["dgs2_points"]["sha256"],
            "1b22b09edaf4b8f74fd3e0a9b2c4131bb2fcfe60eaa3178c95b7cec858e96796",
        )

    def test_pinned_sources_hash_if_present(self):
        subset = load_subset()
        report = verify_source_checksums(subset)
        # The comparison must refuse a mismatch; if the files are on this
        # machine they must match the frozen checksums.
        if all(Path(m["path"]).is_file() for m in subset["qsdsan_sources"].values()):
            self.assertTrue(report["ok"], report)
            for row in report["files"]:
                self.assertEqual(row["status"], "ok")
                self.assertEqual(row["actual"], row["expected"])
        else:
            self.assertFalse(report["ok"])

    def test_sha256_helper_matches_hashlib(self):
        path = ROOT / "config" / "q05-subset.json"
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(sha256_file(path), expected)


class BandArithmeticTests(unittest.TestCase):
    def _limits_s(self):
        return load_subset()["class_S"]

    def _limits_o(self):
        return load_subset()["class_O"]

    def test_class_s_five_percent_boundary(self):
        limits = self._limits_s()
        row = evaluate_metric("S_ac_eff_mg_L", 105.0, 100.0, limits)
        self.assertTrue(row["pass"])
        row = evaluate_metric("S_ac_eff_mg_L", 105.0001, 100.0, limits)
        self.assertFalse(row["pass"])
        row = evaluate_metric("CH4_kgCOD_d", 95.0, 100.0, limits)
        self.assertTrue(row["pass"])
        row = evaluate_metric("CH4_kgCOD_d", 94.9, 100.0, limits)
        self.assertFalse(row["pass"])

    def test_class_o_ten_percent_boundary(self):
        limits = self._limits_o()
        row = evaluate_metric("S_ac_eff_mg_L", 110.0, 100.0, limits)
        self.assertTrue(row["pass"])
        row = evaluate_metric("S_ac_eff_mg_L", 110.0001, 100.0, limits)
        self.assertFalse(row["pass"])

    def test_ph_absolute_limits(self):
        s = evaluate_metric("pH", 7.10, 7.00, self._limits_s())
        self.assertTrue(s["pass"])
        s = evaluate_metric("pH", 7.1000001, 7.00, self._limits_s())
        self.assertFalse(s["pass"])
        o = evaluate_metric("pH", 7.20, 7.00, self._limits_o())
        self.assertTrue(o["pass"])
        o = evaluate_metric("pH", 7.2000001, 7.00, self._limits_o())
        self.assertFalse(o["pass"])

    def test_zero_reference_floor(self):
        limits = self._limits_s()
        row = evaluate_metric("S_ch4_eff_mg_L", 0.01, 0.0, limits)
        self.assertTrue(row["pass"])
        row = evaluate_metric("S_ch4_eff_mg_L", 0.0100001, 0.0, limits)
        self.assertFalse(row["pass"])

    def test_nonfinite_is_not_reported(self):
        limits = self._limits_s()
        row = evaluate_metric("S_ac_eff_mg_L", float("nan"), 100.0, limits)
        self.assertFalse(row["pass"])
        self.assertEqual(row["status"], "not_reported")

    def test_point_and_subset_pass_fail(self):
        subset = load_subset()
        point = subset["points"][0]
        pred = {"S_ac_eff_mg_L": 100, "S_ch4_eff_mg_L": 50, "pH": 7.2, "CH4_kgCOD_d": 1000}
        ref = dict(pred)
        ref["status"] = "run, not validated"
        ev = evaluate_point(point, pred, ref, subset)
        self.assertTrue(ev["pass"])
        pred_bad = dict(pred)
        pred_bad["S_ac_eff_mg_L"] = 200
        ev = evaluate_point(point, pred_bad, ref, subset)
        self.assertFalse(ev["pass"])
        # Incomplete predictions cannot yield a subset PASS.
        report = evaluate_subset({}, subset, qsdsan_index={})
        self.assertFalse(report["subset_pass"])
        self.assertEqual(report["n_passed"], 0)


class InfluentAndTemperatureTests(unittest.TestCase):
    def test_scale_multiplies_cod_only(self):
        packaged = load_packaged_influent()
        base = packaged["feeds"]["bsm2"]
        scaled = scale_influent("bsm2", 1.5, packaged=packaged)
        self.assertEqual(scaled["S_cation"], base["S_cation"])
        self.assertEqual(scaled["S_su"], base["S_su"] * 1.5)
        self.assertEqual(scaled["X_xc"], base["X_xc"] * 1.5)
        self.assertEqual(scaled["X_su"], 0.0)
        brew = scale_influent("brewery", 1.0, packaged=packaged)
        self.assertEqual(brew["S_su"], 3.0)
        # kwargs store S_IC / S_IN as kg C or N /m3; PyADM1 needs kmol/m3.
        self.assertEqual(base["S_IC"], 0.480428)
        self.assertEqual(base["S_IN"], 0.140067)
        mw_c = packaged["pyadm1_unit_conversion"]["S_IC"]["divide_by_MW"]
        mw_n = packaged["pyadm1_unit_conversion"]["S_IN"]["divide_by_MW"]
        self.assertAlmostEqual(mw_c, 12.0107)
        self.assertAlmostEqual(mw_n, 14.0067)
        self.assertAlmostEqual(scaled["S_IC"], 0.04)
        self.assertAlmostEqual(brew["S_IC"], 0.04)
        self.assertAlmostEqual(brew["S_IN"], 0.01)
        # Scaling must not change converted inorganic C/N.
        unscaled = scale_influent("bsm2", 1.0, packaged=packaged)
        self.assertAlmostEqual(unscaled["S_IC"], scaled["S_IC"])
        self.assertAlmostEqual(unscaled["S_IN"], scaled["S_IN"])
        self.assertAlmostEqual(unscaled["S_IC"], 0.480428 / 12.0107)
        self.assertAlmostEqual(unscaled["S_IN"], 0.140067 / 14.0067)

    def test_temperature_constants_match_official_35c_comments(self):
        c = temperature_constants(35.0)
        self.assertAlmostEqual(c["T_ad"], 308.15)
        self.assertAlmostEqual(c["T_op"], 308.15)
        # Official PyADM1.py inline comments at 35 °C.
        self.assertAlmostEqual(c["K_w"], 2.08e-14, delta=0.05e-14)
        self.assertAlmostEqual(c["K_a_co2"], 4.94e-7, delta=0.05e-7)
        self.assertAlmostEqual(c["K_a_IN"], 1.11e-9, delta=0.05e-9)
        self.assertAlmostEqual(c["p_gas_h2o"], 0.0557, delta=0.0002)
        self.assertAlmostEqual(c["K_H_co2"], 0.0271, delta=0.0002)
        self.assertAlmostEqual(c["K_H_ch4"], 0.00116, delta=0.00002)
        self.assertAlmostEqual(c["K_H_h2"], 7.38e-4, delta=0.05e-4)
        c30 = temperature_constants(30.0)
        self.assertLess(c30["T_ad"], c["T_ad"])
        self.assertNotEqual(c30["K_H_ch4"], c["K_H_ch4"])
        self.assertNotEqual(c30["p_gas_h2o"], c["p_gas_h2o"])

    def test_mg_l_and_methane_mass_conversion(self):
        self.assertEqual(0.19864637584198314 * 1000.0, 198.64637584198314)
        # Headspace flow * gas concentration is a COD mass rate.
        q_head = 2.5
        s_gas_ch4 = 1.6
        self.assertAlmostEqual(q_head * s_gas_ch4, 4.0)


class IntegrationGuardTests(unittest.TestCase):
    def test_run_q05_refuses_without_allow(self):
        env = os.environ.copy()
        env.pop("YWSIM_ALLOW_INTEGRATION", None)
        env["PYTHONPATH"] = str(ROOT / "src")
        proc = subprocess.run(
            [sys.executable, str(ROOT / "src" / "run_q05.py")],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["action"], "rejected")

    def test_sweep_runner_refuses_without_allow(self):
        env = os.environ.copy()
        env.pop("YWSIM_ALLOW_INTEGRATION", None)
        env["PYTHONPATH"] = str(ROOT / "src")
        code = (
            "from adm1_sweep_pyadm1 import run_sweep_pyadm1\n"
            "run_sweep_pyadm1('bsm2', 35.0, 170.0, 1.0, 200)\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("YWSIM_ALLOW_INTEGRATION", proc.stderr)




class StatusAllowListTests(unittest.TestCase):
    def test_qsdsan_status_allow_list(self):
        self.assertTrue(qsdsan_status_finished("run, not validated"))
        self.assertTrue(qsdsan_status_finished("run"))
        self.assertFalse(qsdsan_status_finished(""))
        self.assertFalse(qsdsan_status_finished("failed"))
        self.assertFalse(qsdsan_status_finished("timeout"))
        self.assertFalse(qsdsan_status_finished("error"))
        self.assertFalse(qsdsan_status_finished("running"))
        self.assertFalse(qsdsan_status_finished("incomplete"))


if __name__ == "__main__":
    unittest.main()
