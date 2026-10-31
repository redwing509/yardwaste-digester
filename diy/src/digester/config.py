"""Default configuration. All setpoints conservative; edit config.json to override.

Values marked [E] are engineering estimates for a first build, not sourced limits.
"""
from dataclasses import dataclass, field, asdict
import json


@dataclass
class Config:
    # Temperature control (mesophilic)
    temp_setpoint_c: float = 36.5          # middle of 35-38 C band
    temp_low_alarm_c: float = 32.0         # [E]
    temp_high_alarm_c: float = 40.0        # [E] mesophiles stress above ~40 C
    temp_high_trip_c: float = 45.0         # [E] heater hard cutoff (software); install a mechanical high-limit too
    pid_kp: float = 0.25                   # output fraction per deg C [E], tune on site
    pid_ki: float = 0.002
    pid_kd: float = 0.0
    heater_cycle_s: int = 300              # time-proportioning window; long to spare relays

    # Percolate recirculation (per bay)
    bays: list = field(default_factory=lambda: ["bay1", "bay2", "bay3"])
    recirc_interval_min: int = 360         # 4x/day [E]; literature used 2x/day pilots
    recirc_duration_s: int = 300           # [E] size to ~0.3 of percolate volume per day (FPR 0.3)
    pump_max_run_s: int = 900              # dry-run / stuck-relay guard
    percolate_low_level_pct: float = 15.0  # stop pumps below this (pump protection)
    percolate_high_level_pct: float = 90.0

    # Process alarms
    ph_low_alarm: float = 6.5              # VFA souring indicator [E]
    ph_low_pause_recirc: float = 6.0       # stop feeding acid percolate onto fresh bays [E]
    ph_high_alarm: float = 8.3             # ammonia risk with high-grass blends [E]
    ch4_biogas_low_pct: float = 45.0       # poor gas quality alarm [E]

    # Safety (ambient air in the equipment room / container)
    ambient_ch4_warn_pct_lel: float = 10.0  # common detector low alarm level
    ambient_ch4_trip_pct_lel: float = 20.0  # trip well below LEL [E]
    ambient_h2s_warn_ppm: float = 5.0
    ambient_h2s_trip_ppm: float = 10.0
    gas_pressure_high_alarm_kpa: float = 1.5  # [E] keep below water-seal relief setting
    gas_pressure_trip_kpa: float = 2.0        # [E] must be below bag/tank rating
    gas_pressure_vacuum_trip_kpa: float = -0.3  # vacuum = air ingress risk
    max_sensor_age_s: int = 60             # stale data => trip (fail safe)

    # Logging / web
    log_path: str = "digester_log.csv"
    log_interval_s: int = 60
    web_host: str = "127.0.0.1"            # local only by default
    web_port: int = 8080

    @classmethod
    def load(cls, path=None):
        cfg = cls()
        if path:
            with open(path) as f:
                for k, v in json.load(f).items():
                    if not hasattr(cfg, k):
                        raise KeyError(f"unknown config key {k}")
                    setattr(cfg, k, v)
        cfg.validate()
        return cfg

    def validate(self):
        assert 30 <= self.temp_setpoint_c <= 40, "setpoint outside mesophilic range"
        assert self.temp_setpoint_c < self.temp_high_alarm_c < self.temp_high_trip_c
        assert self.ambient_ch4_warn_pct_lel < self.ambient_ch4_trip_pct_lel <= 25
        assert self.ambient_h2s_warn_ppm < self.ambient_h2s_trip_ppm
        assert self.gas_pressure_high_alarm_kpa < self.gas_pressure_trip_kpa
        assert self.recirc_duration_s <= self.pump_max_run_s

    def to_dict(self):
        return asdict(self)
