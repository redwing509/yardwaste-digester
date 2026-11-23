# Q-05b official results

**Official r2 results written at:** Sun 22 Nov 2026, 6:10:53 PM PST
(America/Los_Angeles, UTC-8).

The agreement rule was frozen in `PRE-REGISTERED-BAND-Q05B.md` at commit
`1216299` (5:59:11 PM PST), **before any jADM1_BSM integration** of the
three points. This file records the official score. It does **not** change
`PRE-REGISTERED-BAND-Q05.md`. The official Q-05 result remains **FAIL**.

James authorized the build (widget t1275s6543) and, if this frozen rule
passed and the review set had no must-fix, a public push and merge
(t1276u).

## Official verdict (r2)

- **Q-05b study: PASS**
- Overall brewery siding: **SIDES_WITH_QSDSAN**
- Packaged BSM2 centre sanity: **PASS** (CH4 agrees with both frozen
  references; liquids agree with both)
- Steam-table closeness: **QSDSAN_CLOSER** (see `STEAM-TABLE-Q05B.md`)
- **Q-05 FAIL unchanged**

Third model: jADM1_BSM commit
`dda4fb23b8f645d77737b8fdca1022830773f05b` (Apache-2.0, Pettigrew, FAU),
unpatched gas phase, run under Eclipse Temurin 17.0.21.1+2 and Apache
Commons Math 3.5, DAE mode. Official r2 files:
`/workspace/ywsim-results/q05b-jadm1-r2/` and the copy
`config/q05b-official-results.json`.

## How the official 200-day state was obtained

A first `-steady -in` attempt was invalid: jADM1_BSM `Main.java` sets the
`steady` flag only after `runSteady()`, so `-in` is ignored and the
default BSM2 feed is kept. That attempt was archived under
`/workspace/ywsim-results/q05b-jadm1/attempt-1-ignored-influent/`. The
upstream tree was not edited.

The official integrations used the documented CLI workaround: a one-line
comma-separated `-dynamic` influent with `-step = 200`. That applies the
packaged feed through `Model.setInfluent`. The same `CSVReader` also
leaves `finished` false until the empty read *after* the last line, so
the CLI performed a second, unrequested continuation step of 200 d.
Each `dynamic_output.csv` row is labelled with the step *start* time and
holds the state at start + step:

- label 0.0: state at **200 d** (the pre-registered horizon)
- label 200.0: state at **400 d** (must not be scored)

Official r1 (6:04:31 PM PST, `/workspace/ywsim-results/q05b-jadm1/`)
scored the last row (400 d). That directory is superseded and was not
edited except for a `SUPERSEDED.txt` pointer. Official r2 re-extracts the
200 d row from those same CSV files with the corrected parser. Java was
not rerun. The r1 and r2 verdicts are the same (PASS,
SIDES_WITH_QSDSAN); some liquid residuals, especially at the dilute
brewery point, are smaller at 200 d, as expected.

## Numbers (r2, state at 200 d)

`CH4_kgCOD_d` is `q_gas_headspace * S_gas_ch4` (jADM1 states 38 and 33).
Relative error is |third − reference| / |reference|.

### `DGS:bsm2:T35:Q170:s1` (anchor) — liquids PASS; CH4 AGREES_WITH_BOTH

| Metric | jADM1_BSM | PyADM1 | qsdsan | vs PyADM1 | vs qsdsan |
| --- | ---: | ---: | ---: | ---: | ---: |
| S_ac_eff_mg_L | 197.619959 | 197.823185 | 198.646376 | 0.103% | 0.517% |
| S_ch4_eff_mg_L | 55.088776 | 55.091116 | 55.153307 | 0.004% | 0.117% |
| pH | 7.465530 | 7.465818 | 7.467192 | 0.000288 | 0.001662 |
| CH4_kgCOD_d | 4553.039569 | 4699.352035 | 4552.889679 | 3.113% | 0.0033% |

The 200-day liquid acetate is 0.197619959 kg COD/m3, within about 0.005%
of the opened Rosen & Jeppsson 2006 Table 6 value 0.197629717 kg COD/m3.
That is a supporting observation, not a change of the Q-05b rule, which
scores this key against the frozen Q-05 packaged centre rows. (Official
r1 had quoted a 10⁻⁹ match; that was the 400-day row and is withdrawn.)

### `DGS:brewery:T35:Q170:s1` — liquids PASS; **SIDES_WITH_QSDSAN**

| Metric | jADM1_BSM | PyADM1 | qsdsan | vs PyADM1 | vs qsdsan |
| --- | ---: | ---: | ---: | ---: | ---: |
| S_ac_eff_mg_L | 41.613525 | 41.608245 | 41.551276 | 0.013% | 0.150% |
| S_ch4_eff_mg_L | 41.356552 | 41.373642 | 41.399030 | 0.041% | 0.103% |
| pH | 6.745803 | 6.745906 | 6.747014 | 0.000102 | 0.001211 |
| CH4_kgCOD_d | 966.775066 | 892.885072 | 966.790195 | **8.275%** | 0.0016% |

### `DGS:brewery:T30:Q68:s0.5` — liquids PASS; **SIDES_WITH_QSDSAN**

| Metric | jADM1_BSM | PyADM1 | qsdsan | vs PyADM1 | vs qsdsan |
| --- | ---: | ---: | ---: | ---: | ---: |
| S_ac_eff_mg_L | 21.212349 | 21.194880 | 21.154040 | 0.082% | 0.276% |
| S_ch4_eff_mg_L | 45.216853 | 45.265500 | 45.262449 | 0.107% | 0.101% |
| pH | 6.731203 | 6.731829 | 6.733556 | 0.000626 | 0.002353 |
| CH4_kgCOD_d | 196.168915 | 185.792009 | 196.155265 | **5.585%** | 0.0070% |

## Interpretation (does not reopen Q-05)

jADM1_BSM implements the Rosen / Jeppsson water-vapor formula (the same
closed form as official PyADM1), yet its methane mass rate agrees with
QSDsan to 0.002–0.007% and misses official PyADM1 by 5.6–8.3% on the two
brewery points, which is the same side of the Q-05 5% band as QSDsan.
The packaged centre methane is also within 0.0033% of QSDsan and 3.11% of
PyADM1 (inside the 5% band, so AGREES_WITH_BOTH).

Under the frozen rule this is a conclusive **SIDES_WITH_QSDSAN** result.
As the pre-registered interpretation said, that argues against a simple
account in which the Q-05 brewery methane gap is only the 0.0006 bar
Rosen-versus-thermo Psat difference. The steam-table check still finds
the qsdsan `H2O.Psat` formula closer to IAPWS-IF97 than the Rosen form
(see `STEAM-TABLE-Q05B.md`). A later, separately pre-registered study
could score `q_head` and `Pgas` across the three codes, or compare
PyADM1's 0.25 d `simulate()` + `DAESolve()` stepping to a single 200-day
integration. That is not required to close Q-05b, and it would not
convert the frozen Q-05 FAIL into a PASS.

## What was not done

- The official IWA/Lund BSM2 MATLAB/Simulink tree was not run (no MATLAB
  on the allowed hosts).
- ADM1jl was not the primary third model (heavy Julia stack; also uses
  Rosen Eq. 5.7).
- No official rescore of Q-05. No band edit.
