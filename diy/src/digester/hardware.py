"""Hardware abstraction. Real drivers import Pi libraries lazily so the package
runs (simulator, tests) on any machine.

Outputs are FAIL-SAFE by wiring convention (see BUILD.md):
  heater, pumps   : relay energized = ON; de-energized (power loss, crash) = OFF
  gas_to_use valve: normally-closed solenoid, energized = gas goes to use (boiler)
  flare_vent valve: normally-OPEN solenoid, energized = CLOSED. De-energized = gas
                    routed to flare / safe vent. So any power loss vents to flare.
"""
import time


class Readings(dict):
    """dict of sensor name -> value, with a timestamp."""
    def __init__(self, ts=None, **kw):
        super().__init__(**kw)
        self.ts = time.time() if ts is None else ts


SENSOR_KEYS = [
    "temp_bay1", "temp_bay2", "temp_bay3", "temp_percolate",
    "ph_percolate", "percolate_level_pct", "gas_pressure_kpa",
    "biogas_ch4_pct", "biogas_h2s_ppm", "gas_flow_m3_total",
    "ambient_ch4_pct_lel", "ambient_h2s_ppm", "hw_gas_alarm",
]

OUTPUT_KEYS = ["heater", "pump_bay1", "pump_bay2", "pump_bay3",
               "flare_vent_closed", "gas_to_use"]


class Outputs:
    def __init__(self):
        self.state = {k: False for k in OUTPUT_KEYS}

    def set(self, name, on):
        if name not in self.state:
            raise KeyError(name)
        self.state[name] = bool(on)

    def all_safe(self):
        for k in self.state:
            self.state[k] = False   # de-energize everything => heaters/pumps off, flare path open


class PiHardware:  # pragma: no cover - needs real hardware
    """Raspberry Pi drivers. Pin/bus map lives in BUILD.md section 'Wiring'."""
    RELAY_MAP = {"heater": 1, "pump_bay1": 2, "pump_bay2": 3, "pump_bay3": 4,
                 "flare_vent_closed": 5, "gas_to_use": 6}

    def __init__(self, ds18b20_ids, i2c_bus=1):
        import glob
        from smbus2 import SMBus  # pip install smbus2
        self._glob = glob
        self.bus = SMBus(i2c_bus)
        self.ds_ids = ds18b20_ids  # {"temp_bay1": "28-xxxx", ...}
        self.outputs = Outputs()

    def _ds18b20(self, dev):
        with open(f"/sys/bus/w1/devices/{dev}/w1_slave") as f:
            lines = f.read().splitlines()
        if not lines[0].endswith("YES"):
            raise IOError("DS18B20 CRC fail")
        return int(lines[1].split("t=")[1]) / 1000.0

    def read(self):
        r = Readings()
        for key, dev in self.ds_ids.items():
            r[key] = self._ds18b20(dev)
        # pH via Atlas EZO-pH (I2C addr 0x63): write 'R', wait 900 ms, read.
        from smbus2 import i2c_msg
        self.bus.i2c_rdwr(i2c_msg.write(0x63, b"R"))
        time.sleep(0.9)
        msg = i2c_msg.read(0x63, 31)
        self.bus.i2c_rdwr(msg)
        raw = bytes(msg)
        if raw[0] != 1:
            raise IOError("EZO-pH not ready/error")
        r["ph_percolate"] = float(raw[1:].split(b"\x00")[0])
        # Remaining analog/UART sensors: implement per chosen part, see BUILD.md.
        raise NotImplementedError("finish analog/UART drivers for your exact parts; run --sim until then")

    def apply(self, outputs):
        raise NotImplementedError("map outputs to your relay HAT driver; see BUILD.md")
