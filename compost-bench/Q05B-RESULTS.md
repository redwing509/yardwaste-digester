# Q-05b official results

**Written:** Sun 22 Nov 2026, 6:04:31 PM PST (America/Los_Angeles, UTC-8),
after the official jADM1_BSM integrations finished.

The agreement rule was frozen in `PRE-REGISTERED-BAND-Q05B.md` at commit
`1216299` (5:59:11 PM PST), **before any jADM1_BSM integration** of the
three points. This file records the official score. It does **not** change
`PRE-REGISTERED-BAND-Q05.md`. The official Q-05 result remains **FAIL**.

James authorized the build (widget t1275s6543) and, if this frozen rule
passed and the review set had no must-fix, a public push and merge
(t1276u).

## Official verdict

- **Q-05b study: PASS**
- Overall brewery siding: **SIDES_WITH_QSDSAN**
- Packaged BSM2 centre sanity: **PASS** (CH4 agrees with both frozen
  references; liquids agree with both)
- Steam-table closeness: **QSDSAN_CLOSER** (see `STEAM-TABLE-Q05B.md`)
- **Q-05 FAIL unchanged**

Third model: jADM1_BSM commit
`dda4fb23b8f645d77737b8fdca1022830773f05b` (Apache-2.0, Pettigrew, FAU),
unpatched gas phase, run under Eclipse Temurin 17.0.21.1+2 and Apache
Commons Math 3.5, DAE mode, 200 d. Official files:
`/workspace/ywsim-results/q05b-jadm1/` and the copy
`config/q05b-official-results.json`.

A first attempt that used `-steady -in` was archived under
`attempt-1-ignored-influent/`. jADM1_BSM `Main.java` sets the `steady`
flag only after `runSteady()`, so `-in` is ignored and the default BSM2
feed is kept. The official run used the documented workaround: one-line
comma-separated `-dynamic` influent with `-step = t_days`, which applies
the packaged feed through `Model.setInfluent` and integrates `[0, 200]`
once with the same unpatched DAE model. The upstream tree was not edited.

## Numbers

`CH4_kgCOD_d` is `q_gas_headspace * S_gas_ch4` (jADM1 states 38 and 33).
Relative error is |third − reference| / |reference|.

### `DGS:bsm2:T35:Q170:s1` (anchor) — liquids PASS; CH4 AGREES_WITH_BOTH

| Metric | jADM1_BSM | PyADM1 | qsdsan | vs PyADM1 | vs qsdsan |
| --- | ---: | ---: | ---: | ---: | ---: |
| S_ac_eff_mg_L | 197.629716 | 197.823185 | 198.646376 | 0.098% | 0.512% |
| S_ch4_eff_mg_L | 55.088776 | 55.091116 | 55.153307 | 0.004% | 0.117% |
| pH | 7.465538 | 7.465818 | 7.467192 | 0.000280 | 0.001654 |
| CH4_kgCOD_d | 4553.039725 | 4699.352035 | 4552.889679 | 3.113% | 0.0033% |

The liquid acetate and methane values match Rosen & Jeppsson 2006 Table 6
(opened S_ac 0.1976297169375 kg COD/m3, S_ch4 0.0550887764460 kg COD/m3)
to about 10⁻⁹ kg COD/m3. That is a supporting observation, not a change
of the Q-05b rule, which scores this key against the frozen Q-05 packaged
centre rows.

### `DGS:brewery:T35:Q170:s1` — liquids PASS; **SIDES_WITH_QSDSAN**

| Metric | jADM1_BSM | PyADM1 | qsdsan | vs PyADM1 | vs qsdsan |
| --- | ---: | ---: | ---: | ---: | ---: |
| S_ac_eff_mg_L | 41.615161 | 41.608245 | 41.551276 | 0.017% | 0.154% |
| S_ch4_eff_mg_L | 41.356553 | 41.373642 | 41.399030 | 0.041% | 0.103% |
| pH | 6.745763 | 6.745906 | 6.747014 | 0.000142 | 0.001251 |
| CH4_kgCOD_d | 966.775130 | 892.885072 | 966.790195 | **8.275%** | 0.0016% |

### `DGS:brewery:T30:Q68:s0.5` — liquids PASS; **SIDES_WITH_QSDSAN**

| Metric | jADM1_BSM | PyADM1 | qsdsan | vs PyADM1 | vs qsdsan |
| --- | ---: | ---: | ---: | ---: | ---: |
| S_ac_eff_mg_L | 21.740959 | 21.194880 | 21.154040 | 2.576% | 2.775% |
| S_ch4_eff_mg_L | 45.220710 | 45.265500 | 45.262449 | 0.099% | 0.092% |
| pH | 6.714522 | 6.731829 | 6.733556 | 0.017307 | 0.019034 |
| CH4_kgCOD_d | 196.187826 | 185.792009 | 196.155265 | **5.595%** | 0.0166% |

## Interpretation (does not reopen Q-05)

jADM1_BSM implements the Rosen / Jeppsson water-vapor formula (the same
closed form as official PyADM1), yet its methane mass rate agrees with
QSDsan to 0.002–0.017% and misses official PyADM1 by 5.6–8.3% on the two
brewery points, which is the same side of the Q-05 5% band as QSDsan.
The packaged centre methane is also within 0.004% of QSDsan and 3.11% of
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
