"""Entry point.  python -m digester.main --sim [--hours 48] [--web]"""
import argparse, threading, time
from .config import Config
from .controller import Controller
from .datalog import CsvLogger
from .simulator import SimPlant
from . import web


def run_sim(cfg, hours, dt=10.0, use_web=False, quiet=False):
    plant = SimPlant()
    t = [0.0]
    ctl = Controller(cfg, clock=lambda: t[0])
    log = CsvLogger(cfg.log_path)
    state = {"ctl": ctl, "last": plant.read(), "lock": threading.Lock()}
    srv = web.serve(state, cfg.web_host, cfg.web_port) if use_web else None
    next_log = 0.0
    while t[0] < hours * 3600:
        r = plant.read()
        r.ts = t[0]
        with state["lock"]:
            state["last"] = r
            out = ctl.step(r)
        plant.step(out, dt)
        if t[0] >= next_log:
            log.log(r, ctl, t=t[0])
            next_log += cfg.log_interval_s
        t[0] += dt
        if use_web:
            time.sleep(0.01)
    log.close()
    if srv:
        srv.shutdown()
    if not quiet:
        print(ctl.status(r))
    return ctl, plant


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true", help="run against the simulator")
    ap.add_argument("--config")
    ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--web", action="store_true")
    a = ap.parse_args()
    cfg = Config.load(a.config)
    if not a.sim:
        raise SystemExit("Real hardware mode: finish PiHardware drivers (src/digester/hardware.py) "
                         "and have the install reviewed first. Use --sim.")
    run_sim(cfg, a.hours, use_web=a.web)


if __name__ == "__main__":
    main()
