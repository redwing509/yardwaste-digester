"""Control loop: alarms, latched safety interlocks, PID heating, recirculation.

Safety philosophy (conservative):
  * Software is a SECOND layer. A hard-wired gas detector relay and a mechanical
    high-temperature limit must break heater/pump power independently (BUILD.md).
  * Any missing/stale/implausible safety reading => TRIP (fail safe).
  * A trip is LATCHED: outputs stay safe until a person clears the cause and calls
    reset() (web button requires the trip condition to be gone).
  * TRIP state = heater off, all pumps off, gas_to_use closed, flare/vent path open.
"""
import time
from .pid import PID
from .hardware import Outputs

SAFETY_KEYS = ["ambient_ch4_pct_lel", "ambient_h2s_ppm", "gas_pressure_kpa", "hw_gas_alarm"]
TEMP_KEYS = ["temp_bay1", "temp_bay2", "temp_bay3", "temp_percolate"]

PLAUSIBLE = {
    "ambient_ch4_pct_lel": (-5, 101), "ambient_h2s_ppm": (-1, 2000),
    "gas_pressure_kpa": (-20, 20), "ph_percolate": (0, 14),
    "temp_bay1": (-40, 90), "temp_bay2": (-40, 90), "temp_bay3": (-40, 90), "temp_percolate": (-40, 90),
    "percolate_level_pct": (-5, 105), "biogas_ch4_pct": (0, 100),
}


class Controller:
    def __init__(self, cfg, clock=time.time):
        self.cfg = cfg
        self.clock = clock
        self.outputs = Outputs()
        self.pid = PID(cfg.pid_kp, cfg.pid_ki, cfg.pid_kd)
        self.tripped = False
        self.trip_reasons = []
        self.alarms = []
        self.heater_duty = 0.0
        self._window_start = None
        self._last_t = None
        self._next_recirc = {b: 0.0 for b in cfg.bays}  # first recirc at start
        self._pump_started = {}
        self._bay_idx = 0
        self.paused_bays = set()   # operator: bay open for loading/unloading

    # ---------- checks ----------
    def _valid(self, r, k):
        v = r.get(k)
        if v is None:
            return False
        if isinstance(v, bool):
            return True
        lo, hi = PLAUSIBLE.get(k, (float("-inf"), float("inf")))
        return lo <= v <= hi

    def safety_trips(self, r, now):
        c, why = self.cfg, []
        if now - getattr(r, "ts", now) > c.max_sensor_age_s:
            why.append("stale sensor data")
        for k in SAFETY_KEYS + TEMP_KEYS:
            if not self._valid(r, k):
                why.append(f"sensor fault: {k}")
        if r.get("hw_gas_alarm") is True:
            why.append("hard-wired gas detector alarm")
        g = lambda k: r.get(k) if self._valid(r, k) else None
        if (v := g("ambient_ch4_pct_lel")) is not None and v >= c.ambient_ch4_trip_pct_lel:
            why.append(f"ambient CH4 {v:.1f}% LEL >= {c.ambient_ch4_trip_pct_lel}")
        if (v := g("ambient_h2s_ppm")) is not None and v >= c.ambient_h2s_trip_ppm:
            why.append(f"ambient H2S {v:.1f} ppm >= {c.ambient_h2s_trip_ppm}")
        if (v := g("gas_pressure_kpa")) is not None:
            if v >= c.gas_pressure_trip_kpa:
                why.append(f"gas overpressure {v:.2f} kPa")
            if v <= c.gas_pressure_vacuum_trip_kpa:
                why.append(f"gas vacuum {v:.2f} kPa (air ingress risk)")
        for k in TEMP_KEYS:
            if (v := g(k)) is not None and v >= c.temp_high_trip_c:
                why.append(f"over-temperature {k} {v:.1f} C")
        return why

    def process_alarms(self, r):
        c, a = self.cfg, []
        g = lambda k: r.get(k) if self._valid(r, k) else None
        if (v := g("ambient_ch4_pct_lel")) is not None and v >= c.ambient_ch4_warn_pct_lel:
            a.append("WARN ambient CH4")
        if (v := g("ambient_h2s_ppm")) is not None and v >= c.ambient_h2s_warn_ppm:
            a.append("WARN ambient H2S")
        if (v := g("gas_pressure_kpa")) is not None and v >= c.gas_pressure_high_alarm_kpa:
            a.append("WARN gas pressure high")
        if (v := g("ph_percolate")) is None:
            a.append("pH sensor fault")
        else:
            if v < c.ph_low_alarm:
                a.append(f"pH low {v:.2f} (VFA build-up?)")
            if v > c.ph_high_alarm:
                a.append(f"pH high {v:.2f} (ammonia?)")
        if (v := g("biogas_ch4_pct")) is not None and v < c.ch4_biogas_low_pct:
            a.append(f"biogas CH4 low {v:.0f}%")
        temps = [r[k] for k in TEMP_KEYS if self._valid(r, k)]
        if temps and min(temps) < c.temp_low_alarm_c:
            a.append(f"temperature low {min(temps):.1f} C")
        if temps and max(temps) > c.temp_high_alarm_c:
            a.append(f"temperature high {max(temps):.1f} C")
        if (v := g("percolate_level_pct")) is not None:
            if v < c.percolate_low_level_pct:
                a.append("percolate level low")
            if v > c.percolate_high_level_pct:
                a.append("percolate level high")
        return a

    # ---------- main step ----------
    def step(self, r):
        now = self.clock()
        dt = 1.0 if self._last_t is None else max(1e-3, now - self._last_t)
        self._last_t = now
        trips = self.safety_trips(r, now)
        if trips:
            if not self.tripped:
                self.trip_reasons = trips
            self.tripped = True
        self.alarms = self.process_alarms(r)
        if self.tripped:
            self.outputs.all_safe()
            self.pid.reset()
            self.heater_duty = 0.0
            self._pump_started.clear()
            return self.outputs
        # gas path: closed flare path, gas to use (boiler) while healthy
        self.outputs.set("flare_vent_closed", True)
        self.outputs.set("gas_to_use", True)
        self._heat(r, now, dt)
        self._recirc(r, now)
        return self.outputs

    def _heat(self, r, now, dt):
        c = self.cfg
        t = min(r[k] for k in TEMP_KEYS)  # control on the coldest point
        tmax = max(r[k] for k in TEMP_KEYS)
        self.heater_duty = self.pid.update(c.temp_setpoint_c, t, dt)
        if tmax >= c.temp_high_alarm_c:
            self.heater_duty = 0.0
        if self._window_start is None or now - self._window_start >= c.heater_cycle_s:
            self._window_start = now
        on = (now - self._window_start) < self.heater_duty * c.heater_cycle_s
        self.outputs.set("heater", on and self.heater_duty > 0.02)

    def _recirc(self, r, now):
        c = self.cfg
        level_ok = r["percolate_level_pct"] > c.percolate_low_level_pct
        ph = r.get("ph_percolate") if self._valid(r, "ph_percolate") else None
        acid = ph is not None and ph < c.ph_low_pause_recirc
        # stop running pumps that hit limits
        for bay, started in list(self._pump_started.items()):
            ran = now - started
            if ran >= c.recirc_duration_s or not level_ok or bay in self.paused_bays:
                self.outputs.set(f"pump_{bay}", False)
                del self._pump_started[bay]
            if ran >= c.pump_max_run_s:
                self.alarms.append(f"pump {bay} max run exceeded")
        # one pump at a time
        if self._pump_started or not level_ok or acid:
            if acid:
                self.alarms.append("recirculation paused: pH too low")
            return
        for _ in range(len(c.bays)):
            bay = c.bays[self._bay_idx % len(c.bays)]
            self._bay_idx += 1
            if bay in self.paused_bays:
                continue
            if now >= self._next_recirc[bay]:
                self.outputs.set(f"pump_{bay}", True)
                self._pump_started[bay] = now
                self._next_recirc[bay] = now + c.recirc_interval_min * 60
                break

    def reset(self, r):
        """Operator reset. Refused while any trip condition is still present."""
        still = self.safety_trips(r, self.clock())
        if still:
            return False, still
        self.tripped = False
        self.trip_reasons = []
        return True, []

    def status(self, r):
        return {"tripped": self.tripped, "trip_reasons": self.trip_reasons,
                "alarms": self.alarms, "heater_duty": round(self.heater_duty, 3),
                "outputs": dict(self.outputs.state),
                "readings": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()},
                "paused_bays": sorted(self.paused_bays)}
