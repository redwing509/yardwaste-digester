"""Q-05b band, siding, and steam-table method tests. No multi-day integration."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adm1_q05b_band import (
    BOTH,
    INCONCLUSIVE,
    MIXED,
    NEITHER,
    SIDES_PY,
    SIDES_QSD,
    evaluate_point,
    evaluate_study,
    load_study,
    metric_agrees,
    overall_siding,
    sha256_file,
    verify_source_checksums,
)
from iapws_if97_psat import P_C_MPA, T_C_K, psat_bar, psat_mpa, rosen_psat_bar
from adm1_sweep_jadm1 import (
    jadm1_influent_vector,
    jadm1_initial_vector,
    metrics_from_x,
    parse_dynamic_output,
    parse_steady_result,
)


class RegistrationTests(unittest.TestCase):
    def test_band_document_frozen_before_runs(self):
        band = (ROOT / "PRE-REGISTERED-BAND-Q05B.md").read_text()
        self.assertIn("Written:** Sun 22 Nov 2026, 5:57 PM PST", band)
        self.assertIn("before any new jADM1_BSM", band)
        self.assertIn("dda4fb23b8f645d77737b8fdca1022830773f05b", band)
        self.assertIn("does **not** change `PRE-REGISTERED-BAND-Q05.md`", band)
        self.assertIn("Q-05 FAIL", band)
        self.assertIn("SIDES_WITH_PYADM1", band)
        self.assertIn("SIDES_WITH_QSDSAN", band)
        self.assertIn("IAPWS R7-97(2012)", band)
        self.assertIn("0.11670521452767e4", band)
        self.assertIn("liampetti/jADM1", band)
        self.assertIn("github.com/liampetti/jADM1_BSM", band)
        study = load_study()
        self.assertTrue(study["written_before_jadm1_runs"])
        self.assertEqual(study["written"], "2026-11-22 5:57 PM PST")
        self.assertTrue(study["q05_fail_unchanged"])
        self.assertEqual(study["third_model"]["commit"], "dda4fb23b8f645d77737b8fdca1022830773f05b")
        keys = [p["key"] for p in study["points"]]
        self.assertEqual(
            keys,
            [
                "DGS:bsm2:T35:Q170:s1",
                "DGS:brewery:T35:Q170:s1",
                "DGS:brewery:T30:Q68:s0.5",
            ],
        )
        self.assertEqual(study["points"][0]["role"], "anchor")
        self.assertEqual(study["points"][1]["role"], "brewery_fail")
        self.assertFalse(study["points"][1]["q05_pass"])
        self.assertTrue(study["points"][0]["q05_pass"])

    def test_q05_band_file_not_modified_by_this_study_text(self):
        q05 = (ROOT / "PRE-REGISTERED-BAND-Q05.md").read_text()
        self.assertIn("Written:** Sun 22 Nov 2026, 4:40 PM PST", q05)
        self.assertIn("e_rel ≤ 5.0%", q05)

    def test_pinned_sources_hash_if_present(self):
        study = load_study()
        report = verify_source_checksums(study)
        present = all(Path(row["path"]).is_file() for row in report["files"])
        if present:
            self.assertTrue(report["ok"], report)
            for row in report["files"]:
                self.assertEqual(row["status"], "ok")
                self.assertEqual(row["actual"], row["expected"])
        else:
            self.assertFalse(report["ok"])

    def test_frozen_numbers_match_comparison_file_when_present(self):
        study = load_study()
        path = Path(study["q05_sources"]["comparison"]["path"])
        if not path.is_file():
            self.skipTest("official Q-05 comparison file not on this machine")
        data = json.loads(path.read_text())
        by_key = {p["key"]: p for p in data["points"]}
        for point in study["points"]:
            rows = {r["metric"]: r for r in by_key[point["key"]]["rows"]}
            for metric in study["required_metrics"]:
                self.assertEqual(point["pyadm1"][metric], rows[metric]["predicted"])
                self.assertEqual(point["qsdsan"][metric], rows[metric]["reference"])

    def test_sha256_helper_matches_hashlib(self):
        path = ROOT / "config" / "q05b-points.json"
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(sha256_file(path), expected)


class BandArithmeticTests(unittest.TestCase):
    def limits(self):
        return load_study()["class_S"]

    def test_five_percent_boundary_agrees(self):
        lim = self.limits()
        # 5.000% is inside; 5.001% is not (same construction as Q-05).
        self.assertTrue(metric_agrees(105.0, 100.0, "CH4_kgCOD_d", lim)["agrees"])
        self.assertFalse(metric_agrees(105.001, 100.0, "CH4_kgCOD_d", lim)["agrees"])
        self.assertTrue(metric_agrees(7.10, 7.00, "pH", lim)["agrees"])
        self.assertFalse(metric_agrees(7.11, 7.00, "pH", lim)["agrees"])

    def test_recorded_q05_gaps_against_frozen_refs(self):
        """The already-known Q-05 gaps still fail/pass the 5% rule as recorded."""
        study = load_study()
        lim = self.limits()
        br = study["points"][1]
        # PyADM1 vs qsdsan on brewery centre CH4 is the official 7.644% FAIL.
        row = metric_agrees(br["pyadm1"]["CH4_kgCOD_d"], br["qsdsan"]["CH4_kgCOD_d"], "CH4_kgCOD_d", lim)
        self.assertFalse(row["agrees"])
        dilute = study["points"][2]
        row = metric_agrees(
            dilute["pyadm1"]["CH4_kgCOD_d"], dilute["qsdsan"]["CH4_kgCOD_d"], "CH4_kgCOD_d", lim
        )
        self.assertFalse(row["agrees"])
        centre = study["points"][0]
        row = metric_agrees(
            centre["pyadm1"]["CH4_kgCOD_d"], centre["qsdsan"]["CH4_kgCOD_d"], "CH4_kgCOD_d", lim
        )
        self.assertTrue(row["agrees"])


class SidingTests(unittest.TestCase):
    def _third_from(self, point, source, ch4=None):
        src = point[source]
        out = dict(src)
        if ch4 is not None:
            out["CH4_kgCOD_d"] = ch4
        return out

    def test_sides_with_pyadm1_when_matching_pyadm1_only(self):
        study = load_study()
        lim = study["class_S"]
        point = study["points"][1]
        ev = evaluate_point(self._third_from(point, "pyadm1"), point, lim)
        self.assertTrue(ev["liquids_ok"])
        self.assertEqual(ev["siding"], SIDES_PY)

    def test_sides_with_qsdsan_when_matching_qsdsan_only(self):
        study = load_study()
        lim = study["class_S"]
        point = study["points"][1]
        ev = evaluate_point(self._third_from(point, "qsdsan"), point, lim)
        self.assertTrue(ev["liquids_ok"])
        self.assertEqual(ev["siding"], SIDES_QSD)

    def test_both_when_midpoint_on_dilute_gap(self):
        study = load_study()
        lim = study["class_S"]
        point = study["points"][2]
        mid = 0.5 * (point["pyadm1"]["CH4_kgCOD_d"] + point["qsdsan"]["CH4_kgCOD_d"])
        ev = evaluate_point(self._third_from(point, "pyadm1", ch4=mid), point, lim)
        self.assertEqual(ev["siding"], BOTH)

    def test_neither_when_far_from_both(self):
        study = load_study()
        lim = study["class_S"]
        point = study["points"][1]
        ev = evaluate_point(self._third_from(point, "pyadm1", ch4=1.0), point, lim)
        self.assertTrue(ev["liquids_ok"])
        self.assertEqual(ev["siding"], NEITHER)

    def test_inconclusive_when_liquids_disagree(self):
        study = load_study()
        lim = study["class_S"]
        point = study["points"][1]
        third = self._third_from(point, "pyadm1")
        third["S_ac_eff_mg_L"] = 1000.0
        ev = evaluate_point(third, point, lim)
        self.assertFalse(ev["liquids_ok"])
        self.assertEqual(ev["siding"], INCONCLUSIVE)

    def test_overall_combination_rules(self):
        self.assertEqual(overall_siding([SIDES_PY, SIDES_PY]), SIDES_PY)
        self.assertEqual(overall_siding([SIDES_PY, BOTH]), SIDES_PY)
        self.assertEqual(overall_siding([BOTH, SIDES_QSD]), SIDES_QSD)
        self.assertEqual(overall_siding([BOTH, BOTH]), BOTH)
        self.assertEqual(overall_siding([NEITHER, NEITHER]), NEITHER)
        self.assertEqual(overall_siding([SIDES_PY, SIDES_QSD]), MIXED)
        self.assertEqual(overall_siding([NEITHER, SIDES_PY]), MIXED)
        self.assertEqual(overall_siding([INCONCLUSIVE, SIDES_PY]), INCONCLUSIVE)

    def test_study_pass_requires_centre_and_conclusive_siding(self):
        study = load_study()
        # Perfect copy of PyADM1 on all three points: centre pass, sides with PyADM1.
        thirds = {p["key"]: dict(p["pyadm1"]) for p in study["points"]}
        ev = evaluate_study(thirds, study=study, require_checksums=False)
        self.assertTrue(ev["centre_pass"])
        self.assertEqual(ev["overall_siding"], SIDES_PY)
        self.assertTrue(ev["study_pass"])
        self.assertTrue(ev["merge_eligible"])
        self.assertTrue(ev["q05_fail_unchanged"])

        # Broken centre CH4 (far from both) makes the study inconclusive.
        thirds[study["points"][0]["key"]] = dict(study["points"][0]["pyadm1"], CH4_kgCOD_d=1.0)
        ev = evaluate_study(thirds, study=study, require_checksums=False)
        self.assertFalse(ev["centre_pass"])
        self.assertEqual(ev["overall_siding"], INCONCLUSIVE)
        self.assertFalse(ev["study_pass"])

    def test_neither_overall_is_not_merge_eligible(self):
        study = load_study()
        thirds = {p["key"]: dict(p["pyadm1"]) for p in study["points"]}
        for p in study["points"]:
            if p["role"] == "brewery_fail":
                thirds[p["key"]] = dict(p["pyadm1"], CH4_kgCOD_d=1.0)
        ev = evaluate_study(thirds, study=study, require_checksums=False)
        self.assertTrue(ev["centre_pass"])
        self.assertEqual(ev["overall_siding"], NEITHER)
        self.assertFalse(ev["study_pass"])
        self.assertFalse(ev["merge_eligible"])


class IapwsMethodTests(unittest.TestCase):
    def test_critical_point_identity(self):
        self.assertAlmostEqual(psat_mpa(T_C_K), P_C_MPA, places=6)

    def test_coefficients_match_frozen_document(self):
        band = (ROOT / "PRE-REGISTERED-BAND-Q05B.md").read_text()
        self.assertIn("0.11670521452767e4", band)
        self.assertIn("-0.72421316703206e6", band)
        self.assertIn("0.65017534844798e3", band)

    def test_rosen_formula_reproduces_diagnosed_35c_value(self):
        # Diagnosis quoted 0.05567 bar at 35 C for the Rosen form. This is a
        # formula-identity check, not a steam-table closeness verdict.
        p = rosen_psat_bar(308.15)
        self.assertAlmostEqual(p, 0.05567, places=5)

    def test_if97_in_expected_physical_range_at_30_and_35(self):
        # Bounds only; the official closeness verdict is recorded after this
        # rule is committed.
        p30 = psat_bar(303.15)
        p35 = psat_bar(308.15)
        self.assertGreater(p30, 0.04)
        self.assertLess(p30, 0.05)
        self.assertGreater(p35, 0.05)
        self.assertLess(p35, 0.07)
        self.assertGreater(p35, p30)



class MappingTests(unittest.TestCase):
    def test_initial_vector_layout(self):
        vec = jadm1_initial_vector(30.0)
        self.assertEqual(len(vec), 42)
        self.assertEqual(vec[36], 30.0)
        self.assertEqual(vec[35], 0.0)
        # Official digester_initial S_ac and S_gas_ch4.
        self.assertAlmostEqual(vec[6], 0.089315)
        self.assertAlmostEqual(vec[33], 1.6535)

    def test_influent_uses_converted_sic_and_flow(self):
        vec = jadm1_influent_vector("brewery", 1.0, 170.0)
        self.assertEqual(len(vec), 42)
        self.assertEqual(vec[35], 170.0)
        # 0.480428 kg C/m3 / 12.0107 = 0.04 kmol C/m3
        self.assertAlmostEqual(vec[9], 0.480428 / 12.0107, places=12)
        self.assertAlmostEqual(vec[10], 0.140067 / 14.0067, places=12)
        self.assertEqual(vec[0], 3.0)  # brewery S_su unscaled
        scaled = jadm1_influent_vector("brewery", 0.5, 68.0)
        self.assertEqual(scaled[0], 1.5)
        self.assertEqual(scaled[35], 68.0)
        # Inorganic C is not scaled.
        self.assertEqual(scaled[9], vec[9])

    def test_parse_and_extractor(self):
        text = (
            "Simulation time; 10; Start; 0.0; Finish; 200.0\n"
            + "".join(
                f"State no; {i};\t Influent; 0.0;\t Effluent; {float(i)}\n"
                for i in range(1, 43)
            )
        )
        parsed = parse_steady_result(text)
        self.assertEqual(parsed["finish_d"], 200.0)
        self.assertEqual(len(parsed["x"]), 42)
        self.assertEqual(parsed["x"][0], 1.0)
        # indices 33 and 38 are 1-based states 34 and 39 → values 34 and 39
        x = [0.0] * 42
        x[6] = 0.0416
        x[8] = 0.0414
        x[33] = 1.5
        x[36] = 35.0
        x[38] = 600.0
        x[39] = 6.75
        m = metrics_from_x(x)
        self.assertAlmostEqual(m["S_ac_eff_mg_L"], 41.6)
        self.assertAlmostEqual(m["S_ch4_eff_mg_L"], 41.4)
        self.assertAlmostEqual(m["pH"], 6.75)
        self.assertAlmostEqual(m["CH4_kgCOD_d"], 900.0)
        self.assertEqual(m["T_C"], 35.0)

    def test_parse_dynamic_output_uses_last_row(self):
        lines = ["0.0;" + ";".join(str(i) for i in range(42)) + ";\n"]
        lines.append("200.0;" + ";".join(str(100 + i) for i in range(42)) + ";\n")
        parsed = parse_dynamic_output("".join(lines), 200.0)
        self.assertEqual(parsed["finish_d"], 200.0)
        self.assertEqual(parsed["x"][0], 100.0)
        self.assertEqual(parsed["x"][41], 141.0)
        self.assertEqual(parsed["n_rows"], 2)


if __name__ == "__main__":
    unittest.main()
