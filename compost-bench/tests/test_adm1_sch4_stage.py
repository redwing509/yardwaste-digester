"""Fixture tests for the one-point S_ch4 stage, plus a real 1-CPU nice cap.

No QSDsan import and no 200-day integration. Arithmetic on the published
Sch4 constant is real. Dedup, resume, and config guards use a fake model.
"""
import csv
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CONFIG = ROOT / "config" / "adm1_liquid_sch4_20261108.json"
LAUNCH = ROOT / "launch-adm1-liquid-sch4-20261108.sh"
sys.path.insert(0, str(SRC))

import adm1_sch4_benchmark as bench
import run_once


class PublishedValueTests(unittest.TestCase):
    def test_table_row_and_acetate_factor(self):
        self.assertEqual(bench._dec_str(bench.PUBLISHED_SCH4_KG_COD_M3), "0.0550887764460")
        self.assertEqual(bench._dec_str(bench.PUBLISHED_SCH4_MG_COD_L), "55.0887764460")
        self.assertEqual(bench.PUBLISHED_SCH4_MG_COD_L, Decimal("0.0550887764460") * 1000)
        self.assertEqual(bench._dec_str(bench.PUBLISHED_SAC_MG_COD_L), "197.6297169375")

    def test_difference_has_no_pass_fail(self):
        out = bench.compare_liquid_sch4(50)
        self.assertEqual(out["variable"], "S_ch4")
        self.assertEqual(out["phase"], "liquid_effluent")
        self.assertEqual(out["pass_fail"], None)
        self.assertEqual(out["status"], "run, not validated")
        self.assertEqual(Decimal(out["signed_diff_mg_COD_L"]), Decimal("50") - Decimal("55.0887764460"))
        self.assertNotIn("init_condition_warning", out)

    def test_initial_condition_is_not_the_benchmark(self):
        out = bench.compare_liquid_sch4(55.5)
        self.assertIn("55.5", out["init_condition_warning"])
        self.assertNotEqual(Decimal(out["published_mg_COD_L"]), Decimal("55.5"))
        self.assertIsNone(out["pass_fail"])

    def test_identity_echo_is_labelled(self):
        echo = bench.identity_echo_sac(198.65)
        self.assertEqual(echo["role"], "identity_echo_not_a_new_comparison")
        self.assertEqual(echo["variable"], "S_ac")
        self.assertNotIn("pass_fail", echo)


class GuardTests(unittest.TestCase):
    def test_rejects_other_flows_before_importing_exposan(self):
        """This check runs in a fresh interpreter so it does not depend on
        whether another test already imported exposan (the old global
        import-order assertion).
        """
        script = textwrap.dedent("""
            import sys
            sys.path.insert(0, sys.argv[1])
            import adm1_sch4_benchmark as bench
            assert "exposan" not in sys.modules
            for kwargs in (
                {"Q": 113, "T_C": 35, "t_days": 200},
                {"Q": 85, "T_C": 35, "t_days": 200},
                {"Q": 170, "T_C": 55, "t_days": 200},
                {"Q": 170, "T_C": 35, "t_days": 10},
            ):
                try:
                    bench.run(**kwargs)
                except ValueError:
                    pass
                else:
                    raise SystemExit("expected ValueError")
            assert "exposan" not in sys.modules
        """)
        proc = subprocess.run(
            [sys.executable, "-c", script, str(SRC)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_hrt_and_temperature_identity(self):
        bench.assert_benchmark_identity(20, "308.15")
        bench.assert_benchmark_identity(Decimal("20") + Decimal("1e-12"), Decimal("308.15"))
        with self.assertRaises(RuntimeError):
            bench.assert_benchmark_identity(Decimal("20.001"), Decimal("308.15"))
        with self.assertRaises(RuntimeError):
            bench.assert_benchmark_identity(20, Decimal("308.16"))

    def test_liquid_outlet_refuses_biogas_and_missing_component(self):
        class Stream:
            def __init__(self, name, iconc):
                self.ID = name
                self.iconc = iconc

        class Unit:
            def __init__(self, outs):
                self.outs = outs

        good_eff = Stream("Effluent", {"S_ch4": 1, "S_ac": 2})
        biogas = Stream("Biogas", {"S_ch4": 9, "S_ac": 9})
        _bg, eff, ids = bench.liquid_outlets(Unit((biogas, good_eff)))
        self.assertIs(eff, good_eff)
        self.assertEqual(ids["effluent_id"], "Effluent")
        with self.assertRaises(RuntimeError):
            bench.liquid_outlets(Unit((biogas,)))
        with self.assertRaises(RuntimeError):
            bench.liquid_outlets(Unit((biogas, biogas)))
        same = Stream("Biogas", {"S_ch4": 1, "S_ac": 1})
        with self.assertRaises(RuntimeError):
            bench.liquid_outlets(Unit((biogas, same)))
        with self.assertRaises(RuntimeError):
            bench.liquid_outlets(Unit((biogas, Stream("Effluent", {"S_ac": 1}))))

    def test_noniterable_indexer_uses_catalog_not_membership(self):
        """Reproduce the live ChemicalIndexer TypeError without thermosteam.

        The probe failed because ``"S_ch4" not in iconc`` called __getitem__(0).
        This fixture defines neither __contains__ nor __iter__.
        """
        class Catalog:
            IDs = ("S_su", "S_ac", "S_ch4")

        class Indexer:
            def __init__(self, values):
                self.chemicals = Catalog()
                self._values = values
                self.keys = []

            def __getitem__(self, key):
                self.keys.append(key)
                if type(key) is not str:
                    raise TypeError(
                        "only strings, sequences of strings, and ellipsis are valid index keys"
                    )
                if key not in self.chemicals.IDs:
                    raise KeyError(key)
                return self._values.get(key, 0.0)

        iconc = Indexer({"S_ch4": 55.0, "S_ac": 198.0})
        with self.assertRaises(TypeError) as membership:
            "S_ch4" in iconc
        self.assertIn(
            "only strings, sequences of strings, and ellipsis are valid index keys",
            str(membership.exception),
        )
        self.assertEqual(iconc.keys, [0])
        with self.assertRaises(TypeError):
            iconc[0]
        iconc.keys.clear()

        class Stream:
            def __init__(self, name, concentrations):
                self.ID = name
                self.iconc = concentrations

        class Unit:
            def __init__(self, outs):
                self.outs = outs

        biogas = Stream("Biogas", Indexer({}))
        _bg, eff, ids = bench.liquid_outlets(Unit((biogas, Stream("Effluent", iconc))))
        self.assertEqual(ids["effluent_id"], "Effluent")
        self.assertEqual(iconc.keys, ["S_ch4", "S_ac"])
        self.assertEqual(eff.iconc["S_ch4"], 55.0)

        absent = Indexer({"S_ac": 1.0})
        absent.chemicals = type("Catalog", (), {"IDs": ("S_ac",)})()
        with self.assertRaises(RuntimeError) as missing:
            bench.liquid_outlets(Unit((biogas, Stream("Effluent", absent))))
        self.assertNotIsInstance(missing.exception, TypeError)
        self.assertNotIn(0, absent.keys)

    def test_real_indexer_when_installed_does_not_integrate(self):
        try:
            from exposan.adm import system as adm_system
        except ImportError:
            self.skipTest(
                "exposan is not installed; faithful non-iterable fixture covers the probed TypeError"
            )
        adm_system.Q = 170
        adm_system.Temp = 308.15
        unit = adm_system.create_system().path[0]
        bench.assert_benchmark_identity(unit.V_liq / 170, unit.T)
        iconc = unit.outs[1].iconc
        with self.assertRaises(TypeError) as membership:
            "S_ch4" in iconc
        self.assertIn(
            "only strings, sequences of strings, and ellipsis are valid index keys",
            str(membership.exception),
        )
        with self.assertRaises(TypeError):
            iconc[0]
        _bg, effluent, _ids = bench.liquid_outlets(unit)
        self.assertIsInstance(float(effluent.iconc["S_ch4"]), float)
        self.assertIsInstance(float(effluent.iconc["S_ac"]), float)

    def test_outlet_guard_is_before_simulate(self):
        import inspect
        source = inspect.getsource(bench.run)
        before, after = source.split("system.simulate", 1)
        self.assertIn("liquid_outlets(unit)", before)
        self.assertIn("liquid_outlets(unit)", after)
        model = (SRC / "adm1_sch4_benchmark.py").read_text()
        self.assertNotIn("in iconc", model)

    def test_sources_do_not_read_gas_mass_or_publish(self):
        model = (SRC / "adm1_sch4_benchmark.py").read_text()
        runner = (SRC / "run_once.py").read_text()
        launcher = LAUNCH.read_text()
        self.assertNotIn(".imass", model)
        self.assertNotIn("imass[", model)
        for blob in (model, runner, launcher):
            self.assertNotIn("git push", blob)
            self.assertNotIn("gh pr", blob)
            self.assertNotIn("ssh ", blob)
            self.assertNotIn("pip install", blob)
        self.assertIn("nice -n 19", launcher)
        self.assertIn('taskset -c "$CPU"', launcher)
        self.assertIn("YWSIM_PYTHON", launcher)
        self.assertIn("python3", launcher)
        self.assertIn("YWSIM_REQUIRE_RUNTIME=1", launcher)
        self.assertIn("adm1_liquid_sch4_20261108.json", launcher)
        self.assertNotIn("membrane", launcher)
        self.assertNotIn("adm1_baseline", launcher)


class ConfigTests(unittest.TestCase):
    def test_shipped_config_loads(self):
        cfg = run_once.load_config(CONFIG)
        self.assertEqual(cfg["max_runs"], 1)
        self.assertFalse(cfg["publish"])
        self.assertEqual(cfg["benchmark"]["published_value"], "0.0550887764460")

    def _mutate(self, directory, change):
        cfg = json.loads(CONFIG.read_text())
        change(cfg)
        path = Path(directory) / "bad.json"
        path.write_text(json.dumps(cfg))
        return path

    def test_rejects_old_sweep_and_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = Path(tmp) / "old.json"
            old.write_text(json.dumps({
                "model": "adm1_cstr",
                "grid": {"Q": [170, 113.3, 85], "T_C": [35]},
            }))
            with self.assertRaises(run_once.ConfigError):
                run_once.load_config(old)
            with self.assertRaises(run_once.ConfigError):
                run_once.load_config(self._mutate(tmp, lambda cfg: cfg.__setitem__("publish", True)))
            with self.assertRaises(run_once.ConfigError):
                run_once.load_config(self._mutate(
                    tmp, lambda cfg: cfg["benchmark"].__setitem__("published_value", "0.0555")
                ))
            with self.assertRaises(run_once.ConfigError):
                run_once.load_config(self._mutate(
                    tmp, lambda cfg: cfg["point"].__setitem__("Q_m3_d", 85)
                ))
            with self.assertRaises(run_once.ConfigError):
                run_once.load_config(self._mutate(tmp, lambda cfg: cfg.__setitem__("model_sha256", "0" * 64)))


class RunnerTests(unittest.TestCase):
    def _run(self, result, model):
        return run_once.execute(
            CONFIG, result, model_run=model, apply_caps=False, stage_dir=ROOT,
        )

    def test_dedup_resume_and_failure(self):
        calls = {"n": 0}

        def model(Q, T_C, t_days):
            self.assertEqual((Q, T_C, t_days), (170, 35, 200))
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("solver exploded")
            return {"comparison": {"simulated_mg_COD_L": "1"}, "status": "run, not validated"}

        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "out"
            self.assertEqual(self._run(result, model), 1)
            self.assertEqual(calls["n"], 1)
            self.assertEqual(self._run(result, model), 0)
            self.assertEqual(calls["n"], 2)
            self.assertEqual(self._run(result, model), 0)
            self.assertEqual(calls["n"], 2)
            with open(result / "log.csv", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row["status"] for row in rows], ["failed", "run, not validated"])
            self.assertEqual(rows[1]["exit_code"], "0")
            self.assertTrue(rows[0]["run_id"])
            self.assertTrue(rows[1]["run_id"])
            self.assertNotEqual(rows[0]["run_id"], rows[1]["run_id"])

    def test_abandoned_run_is_retried_and_completed_json_repairs_the_log(self):
        key = run_once.dedup_key(
            run_once.sha256_file(run_once.MODEL_PATH),
            run_once.sha256_file(SRC / "run_once.py"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "out"
            runs = result / "runs"
            runs.mkdir(parents=True)
            stale = {
                "run_id": "stale",
                "dedup_key": key,
                "status": "running",
                "action": "running",
            }
            (runs / "stale.json").write_text(json.dumps(stale))
            calls = {"n": 0}

            def model(Q, T_C, t_days):
                calls["n"] += 1
                return {"comparison": {"simulated_mg_COD_L": "2"}}

            self.assertEqual(self._run(result, model), 0)
            self.assertEqual(calls["n"], 1)
            self.assertEqual(json.loads((runs / "stale.json").read_text())["status"], "abandoned")

            orphan = result / "runs-orphan"
            # A completed receipt without a log must not integrate again.
            result2 = Path(tmp) / "repair"
            (result2 / "runs").mkdir(parents=True)
            done = {
                "run_id": "done-1",
                "dedup_key": key,
                "status": "run, not validated",
                "outputs": {"comparison": {"simulated_mg_COD_L": "3"}},
            }
            (result2 / "runs" / "done-1.json").write_text(json.dumps(done))

            def boom(Q, T_C, t_days):
                raise AssertionError("dedup should not integrate")

            self.assertEqual(self._run(result2, boom), 0)
            with open(result2 / "log.csv", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["action"], "dedup_repair")
            self.assertEqual(rows[0]["run_id"], "done-1")
            self.assertFalse(orphan.exists())

    def test_refuses_git_work_tree_sim_results_and_stage_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            with self.assertRaises(run_once.ConfigError):
                self._run(repo / "ywsim-results", lambda **kwargs: {})
            sim_results = Path(tmp) / "sim" / "results"
            with self.assertRaises(run_once.ConfigError):
                self._run(sim_results, lambda **kwargs: {})
            with self.assertRaises(run_once.ConfigError):
                self._run(ROOT / "not-results", lambda **kwargs: {})
            self.assertFalse((repo / "ywsim-results").exists())
            self.assertFalse(sim_results.exists())

    def test_busy_lock_exits_75(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "out"
            result.mkdir()
            ready = Path(tmp) / "ready"
            holder = textwrap.dedent("""
                import sys, time
                sys.path.insert(0, sys.argv[1])
                from run_once import RunLock
                lock = RunLock(sys.argv[2])
                lock.acquire("holder")
                open(sys.argv[3], "w").write("ready")
                time.sleep(60)
            """)
            proc = subprocess.Popen(
                [sys.executable, "-c", holder, str(SRC), str(result / "LOCK"), str(ready)],
            )
            try:
                for _ in range(50):
                    if ready.exists():
                        break
                    if proc.poll() is not None:
                        self.fail("lock holder exited early")
                    time_sleep()
                self.assertTrue(ready.exists())
                code = self._run(result, lambda **kwargs: (_ for _ in ()).throw(AssertionError("ran")))
                self.assertEqual(code, 75)
            finally:
                proc.kill()
                proc.wait(timeout=5)

    def test_runtime_python_guard(self):
        env = os.environ.copy()
        env["YWSIM_REQUIRE_RUNTIME"] = "1"
        env["YWSIM_PYTHON"] = "/nonexistent/compost-bench-runtime-python"
        env.pop("YWSIM_ALLOW_INTEGRATION", None)
        proc = subprocess.run(
            [sys.executable, str(SRC / "run_once.py"), str(CONFIG)],
            capture_output=True, text=True, env=env, check=False, timeout=15,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("/nonexistent/compost-bench-runtime-python", proc.stdout)
        self.assertNotIn("exposan", proc.stderr)

    def test_same_interpreter_cannot_start_200_day_run(self):
        """If YWSIM_REQUIRE_RUNTIME=1 and YWSIM_PYTHON is this interpreter,
        the unit-test process still must not start the 200-day integration.
        """
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["YWSIM_REQUIRE_RUNTIME"] = "1"
            env["YWSIM_PYTHON"] = sys.executable
            env["YWSIM_RESULT_DIR"] = str(Path(tmp) / "out")
            env.pop("YWSIM_ALLOW_INTEGRATION", None)
            proc = subprocess.run(
                [sys.executable, str(SRC / "run_once.py"), str(CONFIG)],
                capture_output=True, text=True, env=env, check=False, timeout=15,
            )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("YWSIM_ALLOW_INTEGRATION", proc.stdout)
        self.assertNotIn("exposan", proc.stderr)


def time_sleep():
    import time
    time.sleep(0.05)


class ResourceCapTests(unittest.TestCase):
    def test_one_cpu_nice_19_is_real(self):
        script = textwrap.dedent("""
            import json, sys
            sys.path.insert(0, sys.argv[1])
            from run_once import cap_resources
            print(json.dumps(cap_resources(0)))
        """)
        proc = subprocess.run(
            [sys.executable, "-c", script, str(SRC)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        info = json.loads(proc.stdout)
        self.assertEqual(info["affinity"], [0])
        self.assertGreaterEqual(info["nice"], 19)
        self.assertEqual(info["cpu_count"], 1)

    def test_missing_cpu_is_rejected_without_a_run(self):
        script = textwrap.dedent("""
            import sys
            sys.path.insert(0, sys.argv[1])
            from run_once import cap_resources
            cap_resources(99)
        """)
        proc = subprocess.run(
            [sys.executable, "-c", script, str(SRC)],
            capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(proc.returncode, 0)

    def test_launcher_syntax(self):
        subprocess.run(["bash", "-n", str(LAUNCH)], check=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
