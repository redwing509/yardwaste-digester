# Simulation research pipeline (yard-waste digester + membranes)

Goal: improve each process in [../membranes/](../membranes/) with free, open-source
simulators. **All outputs are "run, not validated".** Parameters come from cited
sources or are labelled ASSUMPTION in each model's docstring. No numbers are invented.

## Simulator inventory (checked Oct 31, 2026)
| Simulator | License | Status on box | Used for | Why |
|---|---|---|---|---|
| [QSDsan](https://github.com/QSD-Group/QSDsan) 1.5.3 + EXPOsan | NCSA (open) | installed (`/workspace/venv-ywsim`) | ADM1 digestion (PO1/PO4), AnMBR unit (`qs.sanunits.AnMBR`) | ADM1 verified against the BSM2 MATLAB/Simulink benchmark; has AnMBR, HTL and struvite modules; active (pushed Oct 2026) |
| [BioSTEAM](https://github.com/BioSTEAMDevelopmentGroup/biosteam) 2.54 | MIT | installed (QSDsan dependency) | techno-economics (TEA/LCA) layer | built-in TEA, so pricing gaps can be tested as sensitivities |
| Built-in gas-permeation model (`models/membrane_gp.py`) | MIT (this repo) | runs | CO2/CH4 membrane upgrading (AIRLIQ/EVONIK) | standard well-mixed solution-diffusion model; no open package found that is lighter |
| [Cantera](https://github.com/Cantera/cantera) 3.2 | BSD-3 | installed | gas thermo, and later the HTC/torrefaction gas phase | well-maintained; HTC liquid chemistry is NOT covered |
| [DWSIM](https://github.com/DanWBR/dwsim) | GPL-3.0 | not installed (.NET/Mono GUI) | full flowsheets, RNG compression | heavy GUI; consider later on mail |
| [PyADM1](https://github.com/CaptainFerMag/PyADM1) | MIT | not installed | ADM1 cross-check | a second ADM1 code to compare against QSDsan |
| OpenFOAM | GPL-3.0 | not installed | CFD of mixing and fouling | out of scope until there is a geometry |

## Processes -> baseline models
| Process (DB id) | Model | Status |
|---|---|---|
| Digestion core (PO1-01, PO4-01) | `models/adm1_cstr.py`: BSM2 ADM1 benchmark, HRT sweep | baseline queued |
| Small-flow modular membrane upgrading | `models/membrane_small.py`: 1 / 2R / 2RR layouts, compressor energy | run, not validated |
| Membrane biogas upgrading (AIRLIQ-M01, EVONIK-M01) | `models/membrane_gp.py`: selectivity, pressure ratio and stage-cut sweep | baseline queued |
| AnMBR (VEOLIA-M02, MICRODYN-M01) | QSDsan AnMBR | planned: needs sourced flux and fouling data (GAP-07) |
| HTC process water + UF/RO (TORAY-M03, DUPONT-M01) | ADM1 on HTC process water | planned: needs a sourced feed COD split (GAP-04) |
| NH3 contactor and struvite (PO4-01) | QSDsan/EXPOsan modules | planned |
| Torrefaction condensate VFA (PO3-01) | none suitable yet | open |

## Small-system focus (James, Oct 31, 2026)
Priority is the DIY leach-bed (`../diy/`) and the $50k-100k small unit (`../small-unit/`): ~1-6 m3/h biogas.
- **Deprioritized (large-plant only):** multi-stage industrial membrane upgrading packages (smallest found 30-60 Nm3/h), AnMBR plants (economic size 90+ m3/day) and leachate UF/RO (30+ m3/day). See [SMALL-MEMBRANES.md](SMALL-MEMBRANES.md).
- `models/membrane_small.py` + `sweeps/membrane_small.json`: modular 1/2-stage layouts at small flows, purity/recovery and compressor energy (lower bound). Run, not validated.

## Running
    nice -n 19 /workspace/venv-ywsim/bin/python sim/run_sweep.py sim/sweeps/<name>.json
Each run appends one row to `results/log.csv` with the commit, the parameters, the outputs and the status.

## Known issues (retro review, Oct 31, 2026)
- ADM1 benchmark check (issue #3): a local 200-day run at Q=170 (HRT 20 d, 35 C) gave effluent S_ac of about 199 mg COD/L. The BSM2 ADM1 steady-state output is S_ac = 197.63 mg COD/L (Rosen & Jeppsson 2006, sec. 7, https://iwa-mia.org/wp-content/uploads/2019/04/bmadm1_report061127.pdf), about 0.7% apart. The earlier 89.3 figure was exposan's `default_init_conds` start value, mislabelled as the benchmark. Other states not yet compared. Shorter runs may not have reached steady state (hypothesis, not checked). Status: run, not validated.
- The membrane model is single-stage and binary, and it raises an error if the requested stage cut isn't reached.
