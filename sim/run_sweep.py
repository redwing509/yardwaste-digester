"""Parameter-sweep runner. Usage: nice -n 19 python sim/run_sweep.py sim/sweeps/X.json
Appends one row per run to sim/results/log.csv (status: run, not validated)."""
import sys, json, csv, itertools, importlib, datetime, os, subprocess
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, 'models'))
spec = json.load(open(sys.argv[1])); mod = importlib.import_module(spec['model'])
log = os.path.join(here, 'results', 'log.csv'); new = not os.path.exists(log)
commit = subprocess.run(['git', '-C', here, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
keys = list(spec['grid'])
with open(log, 'a', newline='') as f:
    w = csv.writer(f)
    if new: w.writerow(['utc', 'commit', 'model', 'params', 'outputs', 'status'])
    for combo in itertools.product(*spec['grid'].values()):
        p = dict(zip(keys, combo))
        try: out, st = mod.run(**p), 'run, not validated'
        except Exception as e: out, st = {'error': repr(e)[:200]}, 'failed'
        w.writerow([datetime.datetime.utcnow().isoformat(timespec='seconds'), commit, spec['model'], json.dumps(p), json.dumps(out), st]); f.flush()
        print(p, out, st, flush=True)
