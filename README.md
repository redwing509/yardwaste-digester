# Yard-Waste Digester

Plans and research for a profitable yard-waste-only anaerobic digester (Pacific Northwest focus), plus an open DIY build spec and control code.

- `plan/PLAN.md` - profitability plan: process trains, best grass blend (40-50% grass by VS), PNW siting and economics. Figures are marked sourced vs estimate.
- `diy/` - off-the-shelf DIY digester spec, BOM, build guide, safety notes and Compost Bench control code.
- `compost-bench/` - Compost Bench ADM1 liquid S_ch4 benchmark harness (harness defects fixed; scientific validation still open, so results are not scientifically validated).

Status: research / design. Not engineering-reviewed. Do not build without a qualified review.

## Compost Bench

Compost Bench is the yard-waste digester control code and its test harness.

- Control code: [`diy/src/digester/`](diy/src/digester/) (controller, simulator, dashboard, and sizing), with tests in [`diy/tests/`](diy/tests/).
- ADM1 liquid S_ch4 benchmark harness: [`compost-bench/`](compost-bench/) (`src/adm1_sch4_benchmark.py`, `src/run_once.py`, `tests/`, and `launch-adm1-liquid-sch4-20261108.sh`).

Both previously reported harness defects are fixed. Hermes job `20261124-150134-digester-harness-defects-readonly` and a controller spot-check on a fresh clone of main (`a5893a9`) confirmed the two fixes: the import-order test now runs in a fresh subprocess, and `run_once.py`, `run_fullstate.py`, and the ADM1/Q-05 entry points refuse to run without `YWSIM_ALLOW_INTEGRATION=1`, which only the launchers set. Scientific validation remains open: official Q-05 is a FAIL against the pre-registered 5% band (see [`compost-bench/Q05-RESULTS-R2.md`](compost-bench/Q05-RESULTS-R2.md)). Results are therefore not scientifically validated. The one-point S_ch4 comparison is a published BSM2 benchmark point, not a yard-waste prediction. See [`compost-bench/README.md`](compost-bench/README.md) for how to run the harness, its requirements, and its honest limits.

## Improvements welcome

This project is free and open source under the MIT license. You can use the code, and you can request improvements by opening a GitHub [issue](https://github.com/redwing509/yardwaste-digester/issues/new) or a pull request from a fork. Every proposed change is reviewed before it is merged. See [CONTRIBUTING.md](CONTRIBUTING.md).
