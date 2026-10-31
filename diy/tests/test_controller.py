import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from digester.config import Config
from digester.controller import Controller
from digester.hardware import Readings
from digester.pid import PID
from digester.simulator import SimPlant
from digester.sizing import size
from digester import main as dmain


def good(ts=0.0, **kw):
    r = Readings(ts=ts, temp_bay1=36.0, temp_bay2=36.0, temp_bay3=36.0, temp_percolate=36.0,
                 ph_percolate=7.2, percolate_level_pct=60.0, gas_pressure_kpa=0.5,
                 biogas_ch4_pct=55.0, biogas_h2s_ppm=300.0, gas_flow_m3_total=0.0,
                 ambient_ch4_pct_lel=0.0, ambient_h2s_ppm=0.0, hw_gas_alarm=False)
    r.update(kw)
    return r


class Clock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t


def ctl():
    c = Clock()
    return Controller(Config(), clock=c), c


SAFE = {"heater": False, "pump_bay1": False, "pump_bay2": False, "pump_bay3": False,
        "flare_vent_closed": False, "gas_to_use": False}


class TestPID(unittest.TestCase):
    def test_clamped(self):
        p = PID(1, 0.1, 0)
        self.assertEqual(p.update(36, 0, 1), 1.0)
        self.assertEqual(p.update(36, 80, 1), 0.0)

    def test_antiwindup(self):
        p = PID(0.25, 0.01, 0)
        for _ in range(10000):
            p.update(36, 10, 1)       # long saturation
        self.assertLess(p.integral * 0.01, 1.5)

    def test_bad_dt(self):
        with self.assertRaises(ValueError):
            PID(1, 0, 0).update(1, 0, 0)


class TestConfig(unittest.TestCase):
    def test_default_valid(self):
        Config().validate()

    def test_rejects_unsafe_setpoint(self):
        c = Config(); c.temp_setpoint_c = 55
        with self.assertRaises(AssertionError):
            c.validate()


class TestInterlocks(unittest.TestCase):
    def check_trip(self, **kw):
        c, clk = ctl()
        c.step(good())
        clk.t = 10
        out = c.step(good(ts=10, **kw))
        self.assertTrue(c.tripped, kw)
        self.assertEqual(out.state, SAFE)
        return c

    def test_ch4_leak(self): self.check_trip(ambient_ch4_pct_lel=25.0)
    def test_h2s(self): self.check_trip(ambient_h2s_ppm=15.0)
    def test_overpressure(self): self.check_trip(gas_pressure_kpa=2.5)
    def test_vacuum(self): self.check_trip(gas_pressure_kpa=-0.5)
    def test_hw_detector(self): self.check_trip(hw_gas_alarm=True)
    def test_overtemp(self): self.check_trip(temp_bay2=46.0)
    def test_missing_sensor(self): self.check_trip(ambient_ch4_pct_lel=None)
    def test_implausible_sensor(self): self.check_trip(gas_pressure_kpa=999.0)

    def test_stale_data(self):
        c, clk = ctl()
        clk.t = 500
        out = c.step(good(ts=0))
        self.assertTrue(c.tripped)
        self.assertEqual(out.state, SAFE)

    def test_latched_and_reset_refused_while_unsafe(self):
        c = self.check_trip(ambient_ch4_pct_lel=30.0)
        c.clock.t = 20
        out = c.step(good(ts=20))       # condition gone, still latched
        self.assertTrue(c.tripped)
        self.assertEqual(out.state, SAFE)
        ok, why = c.reset(good(ts=20, ambient_ch4_pct_lel=30.0))
        self.assertFalse(ok); self.assertTrue(why)
        ok, _ = c.reset(good(ts=20))
        self.assertTrue(ok)
        out = c.step(good(ts=20))
        self.assertTrue(out.state["flare_vent_closed"])

    def test_no_trip_when_healthy(self):
        c, _ = ctl()
        c.step(good())
        self.assertFalse(c.tripped)


class TestAlarms(unittest.TestCase):
    def test_ph_low_pauses_recirc(self):
        c, _ = ctl()
        out = c.step(good(ph_percolate=5.8))
        self.assertFalse(any(out.state[f"pump_bay{i}"] for i in (1, 2, 3)))
        self.assertTrue(any("pH low" in a for a in c.alarms))

    def test_warn_levels(self):
        c, _ = ctl()
        c.step(good(ambient_ch4_pct_lel=12.0, ambient_h2s_ppm=6.0, biogas_ch4_pct=40.0, ph_percolate=8.5))
        txt = " ".join(c.alarms)
        for s in ["ambient CH4", "ambient H2S", "CH4 low", "pH high"]:
            self.assertIn(s, txt)
        self.assertFalse(c.tripped)


class TestHeatAndRecirc(unittest.TestCase):
    def test_heater_on_when_cold_off_when_hot(self):
        c, _ = ctl()
        self.assertTrue(c.step(good(temp_bay1=25.0)).state["heater"])
        c2, _ = ctl()
        self.assertFalse(c2.step(good(temp_bay1=41.0, temp_bay2=41.0, temp_bay3=41.0, temp_percolate=41.0)).state["heater"])

    def test_one_pump_at_a_time_and_stops(self):
        c, clk = ctl()
        out = c.step(good())
        on = [k for k in ("pump_bay1", "pump_bay2", "pump_bay3") if out.state[k]]
        self.assertEqual(len(on), 1)
        clk.t = c.cfg.recirc_duration_s + 1
        out = c.step(good(ts=clk.t))
        self.assertFalse(out.state[on[0]])

    def test_low_level_stops_pump(self):
        c, clk = ctl()
        c.step(good())
        clk.t = 5
        out = c.step(good(ts=5, percolate_level_pct=5.0))
        self.assertFalse(any(out.state[f"pump_bay{i}"] for i in (1, 2, 3)))

    def test_paused_bay_skipped(self):
        c, _ = ctl()
        c.paused_bays = {"bay1"}
        out = c.step(good())
        self.assertFalse(out.state["pump_bay1"])


class TestSimulation(unittest.TestCase):
    def test_sim_warms_up_and_logs(self):
        d = tempfile.mkdtemp()
        cfg = Config(); cfg.log_path = os.path.join(d, "log.csv")
        ctl_, plant = dmain.run_sim(cfg, hours=48, quiet=True)
        self.assertFalse(ctl_.tripped)
        self.assertGreater(min(plant.temps.values()), 33.0)
        self.assertLess(max(plant.temps.values()), 40.0)
        self.assertGreater(sum(1 for _ in open(cfg.log_path)), 100)


class TestSizing(unittest.TestCase):
    def test_defaults(self):
        s = size()
        self.assertEqual(s["bays_to_build"], 3)
        self.assertGreater(s["ch4_m3_per_day"], 0)


if __name__ == "__main__":
    unittest.main()
