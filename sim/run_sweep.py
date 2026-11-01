"""Parameter-sweep runner. Usage: nice -n 19 python sim/run_sweep.py sim/sweeps/X.json
Appends one row per run to sim/results/log.csv (status: run, not validated).
Exits 1 if any run failed (failures are still logged)."""
import csv
import datetime
import importlib
import itertools
import json
import os
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, 'models'))
with open(sys.argv[1]) as fh:
    spec = json.load(fh)
mod = importlib.import_module(spec['model'])
os.makedirs(os.path.join(here, 'results'), exist_ok=True)
log = os.path.join(here, 'results', 'log.csv')
new = not os.path.exists(log)
commit = subprocess.run(['git', '-C', here, 'rev-parse', '--short', 'HEAD'],
                        capture_output=True, text=True, check=False).stdout.strip()
keys = list(spec['grid'])
failed = 0
with open(log, 'a', newline='') as f:
    w = csv.writer(f)
    if new:
        w.writerow(['utc', 'commit', 'model', 'params', 'outputs', 'status'])
    for combo in itertools.product(*spec['grid'].values()):
        p = dict(zip(keys, combo))
        try:
            out, st = mod.run(**p), 'run, not validated'
        except Exception as e:  # noqa: BLE001 - log every model error, keep sweeping
            out, st = {'error': repr(e)[:200]}, 'failed'
            failed += 1
        ts = datetime.datetime.now(datetime.UTC).isoformat(timespec='seconds')
        w.writerow([ts, commit, spec['model'], json.dumps(p), json.dumps(out), st])
        f.flush()
        print(p, out, st, flush=True)
sys.exit(1 if failed else 0)
