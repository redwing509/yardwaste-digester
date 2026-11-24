# Compost Bench

Compost Bench is the yard-waste digester control code and its test harness.

- Control code (already in this repository): `diy/src/digester/` (controller, simulator, dashboard, sizing) with tests in `diy/tests/`.
- This directory is the ADM1 liquid S_ch4 benchmark harness: `src/`, `tests/`, `config/`, and `launch-adm1-liquid-sch4-20261108.sh`.

## Honest limits

- Both previously reported harness defects are fixed (Hermes job `20261124-150134-digester-harness-defects-readonly` and a controller spot-check on a fresh clone of main `a5893a9`). Scientific validation remains open: official Q-05 is a FAIL against the pre-registered 5% band (`Q05-RESULTS-R2.md`). Results are not scientifically validated.
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

Q-05 packaged design-sweep subset (PyADM1 vs stored QSDsan DGS2/DGS3 rows),
with the Q-02 BSM2 Table 6 check as the anchor. The subset and band were
frozen in `PRE-REGISTERED-BAND-Q05.md` on 22 Nov 2026, 4:40 PM PST, before
any new PyADM1 sweep integrations. Official r2 is recorded in
`Q05-RESULTS-R2.md` (FAIL). See also `Q05-ERRATUM-SIC-SIN-UNITS.md` and
`Q05-CH4-DIAGNOSTIC.md`:

```
export YWSIM_RESULT_DIR=$HOME/compost-bench-results-q05
export YWSIM_PYTHON=/workspace/digester-tools/envs/pyadm1/bin/python
export YWSIM_WORKERS=2
bash launch-q05.sh
```



Q-05b third independent ADM1 check (jADM1_BSM) of the two Q-05 brewery
methane FAILs plus the packaged BSM2 centre, and an IAPWS-IF97 steam-table
check of both vapor-pressure formulas. The rule was frozen in
`PRE-REGISTERED-BAND-Q05B.md` on 22 Nov 2026, 5:57 PM PST, before any
jADM1_BSM integration of those points. Official r2 result (state at 200 d, re-extracted after r1 scored a 400 d
continuation): `Q05B-RESULTS.md` (PASS, SIDES_WITH_QSDSAN). Steam table:
`STEAM-TABLE-Q05B.md` (QSDSAN_CLOSER). The Q-05 FAIL is not overturned.

```
export YWSIM_RESULT_DIR=$HOME/compost-bench-results-q05b
export YWSIM_PYTHON=/workspace/venv-ywsim/bin/python
export JADM1_BIN=/workspace/digester-tools/bin/jadm1-bsm
bash launch-q05b.sh
```

## Dependency licenses

These packages are not vendored here. Install them yourself.

- NumPy: BSD-3-Clause
- exposan 1.5.x and QSDsan 1.5.x: NCSA (University of Illinois/NCSA Open Source License)
- BioSTEAM and ThermoSTEAM: MIT / NCSA

NCSA and MIT are compatible with this repository's MIT license.

## License

MIT, same as the repository.
