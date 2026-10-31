"""Simple plant model for testing the controller without hardware. Not a process model
to predict yield; it only produces plausible, controllable signals."""
import random
from .hardware import Readings, Outputs


class SimPlant:
    def __init__(self, ambient_c=-5.0, seed=1):
        self.rng = random.Random(seed)
        self.t = 0.0
        self.ambient_c = ambient_c
        self.temps = {"temp_bay1": 20.0, "temp_bay2": 20.0, "temp_bay3": 20.0, "temp_percolate": 20.0}
        self.ph = 7.2
        self.level = 60.0
        self.pressure = 0.5
        self.flow_total = 0.0
        self.faults = {}   # name -> forced value, for tests (e.g. ambient_ch4_pct_lel=30)
        self.dead_sensors = set()

    def step(self, outputs: Outputs, dt):
        self.t += dt
        heat_w = 6000.0 if outputs.state["heater"] else 0.0   # [E] 6 kW heater
        for k in self.temps:
            loss = (self.temps[k] - self.ambient_c) * 0.00002 * dt
            gain = heat_w * 0.0000015 * dt
            self.temps[k] += gain - loss
        pumping = any(outputs.state[f"pump_bay{i}"] for i in (1, 2, 3))
        self.level += (-0.05 if pumping else 0.02) * dt / 10
        self.level = max(0.0, min(100.0, self.level))
        warm = self.temps["temp_percolate"] > 30
        gas_rate = 0.0003 * dt if warm else 0.00003 * dt   # m3
        self.flow_total += gas_rate
        if outputs.state["flare_vent_closed"] and not outputs.state["gas_to_use"]:
            self.pressure += gas_rate * 2
        else:
            self.pressure = max(0.2, self.pressure - 0.01 * dt / 10)

    def read(self):
        n = lambda s: self.rng.gauss(0, s)
        r = Readings(ts=self.t,
                     ph_percolate=self.ph + n(0.02),
                     percolate_level_pct=self.level,
                     gas_pressure_kpa=self.pressure + n(0.01),
                     biogas_ch4_pct=55 + n(0.5),
                     biogas_h2s_ppm=300 + n(10),
                     gas_flow_m3_total=self.flow_total,
                     ambient_ch4_pct_lel=max(0.0, n(0.3)),
                     ambient_h2s_ppm=max(0.0, n(0.2)),
                     hw_gas_alarm=False)
        for k, v in self.temps.items():
            r[k] = v + n(0.05)
        r.update(self.faults)
        for k in self.dead_sensors:
            r[k] = None
        return r
