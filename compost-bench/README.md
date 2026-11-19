# Compost Bench

Compost Bench is the yard-waste digester control code and its test harness.

- Control code (already in this repository): `diy/src/digester/` (controller, simulator, dashboard, sizing) with tests in `diy/tests/`.
- This directory is the ADM1 liquid S_ch4 benchmark harness: `src/`, `tests/`, `config/`, and `launch-adm1-liquid-sch4-20261108.sh`.

## Honest limits

- Harness defects are open and this work is not validated. Status stays `run, not validated`. There is no pass/fail band on S_ch4.
- This stage compares one published BSM2 ADM1 steady-state value (Rosen & Jeppsson 2006, section 7, state 9, liquid effluent S_ch4). It is not a yard-waste feed prediction and not a DIY leach-bed result.
- Known open defect: if you run the unit tests with `YWSIM_REQUIRE_RUNTIME=1` and `YWSIM_PYTHON` pointing at the same interpreter that is running the tests, `test_runtime_python_guard` can proceed into the real 200-day integration. Do not run the tests that way. Run the unit tests without those variables set.
- Another open defect is a global import-order assertion in the test module. Treat listed defects as unfixed.

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

## Dependency licenses

These packages are not vendored here. Install them yourself.

- NumPy: BSD-3-Clause
- exposan 1.5.x and QSDsan 1.5.x: NCSA (University of Illinois/NCSA Open Source License)
- BioSTEAM and ThermoSTEAM: MIT / NCSA

NCSA and MIT are compatible with this repository's MIT license.

## License

MIT, same as the repository.
