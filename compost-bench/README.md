# Compost Bench

Compost Bench is the yard-waste digester control code and its test harness.

- Control code (already in this repository): `diy/src/digester/` (controller, simulator, dashboard, sizing) with tests in `diy/tests/`.
- This directory is the ADM1 liquid S_ch4 benchmark harness: `src/`, `tests/`, `config/`, and `launch-adm1-liquid-sch4-20261108.sh`.

## Honest limits

- The one-point liquid S_ch4 helper still records a difference only. The Q-02 full-state comparison uses the pre-registered pass/fail band in `PRE-REGISTERED-BAND-Q02.md` (frozen 21 Nov 2026, 11:12 PM PST, before the new 200-day runs). Yard-waste and 55 °C claims are out of scope.
- This benchmark is the published BSM2 ADM1 steady-state case (Rosen & Jeppsson 2006, section 7). It is not a yard-waste feed prediction and not a DIY leach-bed result.
- The unit-test suite cannot start the 200-day integration: `run_once.py` and `run_fullstate.py` refuse unless `YWSIM_ALLOW_INTEGRATION=1`, which only the launchers set. The same-interpreter case is covered by `test_same_interpreter_cannot_start_200_day_run`.
- The old global import-order assertion (`exposan` not in `sys.modules`) now runs in a fresh subprocess, so it no longer depends on test order.

## Requirements

Control code (`diy/`):

- Python 3.10 or newer, standard library only for the simulator and unit tests
- `smbus2` on a Raspberry Pi when talking to real hardware

Harness integration run (this directory):

- Python 3.10 or newer
- `numpy` and `exposan` (which pulls in QSDsan, BioSTEAM, and ThermoSTEAM). See `requirements.txt`.

## How to run

Control-code simulator and tests, from `diy/`:

```
PYTHONPATH=src python3 -m digester.main --sim --hours 48 --web
python3 -m unittest discover -s tests -v
```

Harness unit tests (no QSDsan import and no 200-day integration), from this directory:

```
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Harness benchmark run (needs exposan). Set an absolute result directory *outside* this git checkout:

```
python3 -m pip install -r requirements.txt
export YWSIM_RESULT_DIR=$HOME/compost-bench-results
export YWSIM_PYTHON=python3
bash launch-adm1-liquid-sch4-20261108.sh
```

The launcher pins itself to one CPU at nice 19 when `taskset` is available.

Full-state three-way comparison (QSDsan, PyADM1, Rosen 2006 Table 6):

```
export YWSIM_RESULT_DIR=$HOME/compost-bench-results-q02
export YWSIM_PYTHON=/workspace/venv-ywsim/bin/python
bash launch-adm1-fullstate-q02.sh
```

PyADM1 is loaded from `/workspace/digester-tools/src/PyADM1` at commit e7f806e1. The official tree is not edited.


## Dependency licenses

These packages are not vendored here. Install them yourself.

- NumPy: BSD-3-Clause
- exposan 1.5.x and QSDsan 1.5.x: NCSA (University of Illinois/NCSA Open Source License)
- BioSTEAM and ThermoSTEAM: MIT / NCSA

NCSA and MIT are compatible with this repository's MIT license.

## License

MIT, same as the repository.
