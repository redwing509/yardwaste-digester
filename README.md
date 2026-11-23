# Yard-Waste Digester

Plans and research for a profitable yard-waste-only anaerobic digester (Pacific Northwest focus), plus an open DIY build spec and control code.

- `plan/PLAN.md` - profitability plan: process trains, best grass blend (40-50% grass by VS), PNW siting and economics. Figures are marked sourced vs estimate.
- `diy/` - off-the-shelf DIY digester spec, BOM, build guide, safety notes and Compost Bench control code.
- `compost-bench/` - Compost Bench ADM1 liquid S_ch4 benchmark harness (defects open; not validated).

Status: research / design. Not engineering-reviewed. Do not build without a qualified review.

## Compost Bench

Compost Bench is the yard-waste digester control code and its test harness.

- Control code: [`diy/src/digester/`](diy/src/digester/) (controller, simulator, dashboard, and sizing), with tests in [`diy/tests/`](diy/tests/).
- ADM1 liquid S_ch4 benchmark harness: [`compost-bench/`](compost-bench/) (`src/adm1_sch4_benchmark.py`, `src/run_once.py`, `tests/`, and `launch-adm1-liquid-sch4-20261108.sh`).

Harness defects are open and this work is not validated. The S_ch4 comparison is a published BSM2 benchmark point, not a yard-waste prediction, and it has no pass/fail band. See [`compost-bench/README.md`](compost-bench/README.md) for how to run it, its requirements, and its honest limits.

## Improvements welcome

This project is free and open source under the MIT license. You can use the code, and you can request improvements by opening a GitHub [issue](https://github.com/redwing509/yardwaste-digester/issues/new) or a pull request from a fork. Every proposed change is reviewed before it is merged. See [CONTRIBUTING.md](CONTRIBUTING.md).
## Coding process

Models and contributors writing code should follow the adopted coding process in [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/superpowers-adopted/](docs/superpowers-adopted/). The official review set, frozen pass rules, and owner merge approval still come first.
