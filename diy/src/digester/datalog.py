import csv, os, time
from .hardware import SENSOR_KEYS, OUTPUT_KEYS


class CsvLogger:
    FIELDS = ["time_iso"] + SENSOR_KEYS + OUTPUT_KEYS + ["tripped", "alarms"]

    def __init__(self, path):
        self.path = path
        new = not os.path.exists(path)
        self.f = open(path, "a", newline="")
        self.w = csv.DictWriter(self.f, fieldnames=self.FIELDS, extrasaction="ignore")
        if new:
            self.w.writeheader()

    def log(self, readings, ctl, t=None):
        row = {"time_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t or time.time()))}
        row.update({k: readings.get(k) for k in SENSOR_KEYS})
        row.update({k: int(v) for k, v in ctl.outputs.state.items()})
        row["tripped"] = int(ctl.tripped)
        row["alarms"] = "; ".join(ctl.alarms + ctl.trip_reasons)
        self.w.writerow(row)
        self.f.flush()

    def close(self):
        self.f.close()
