# Q-05 pre-registered subset and code-to-code agreement band

**Written:** Sun 22 Nov 2026, 4:40 PM PST (America/Los_Angeles, UTC-8), after
the DGS2/DGS3 qsdsan result files were copied from vps3 for key-existence and
checksum pinning, and **before any new PyADM1 integration of those sweep
points was started.**

This file freezes the subset and the decision rule. It must not be edited to
fit later numbers. The qsdsan metric values in the copied JSONL files were
not used to choose the band or to drop a point. Those files were used only to
confirm that each listed key exists and to pin their SHA-256 checksums.

James authorized this build on 22 Nov 2026 (widget t1270s6510). All results
remain model-only. This is not a yard-waste feed prediction, not a 55 °C
prediction, and not a DIY leach-bed result. Temperature still changes only
the acid-base Ka and Henry KH constants, not biological rate constants, as
in the original DGS2/DGS3 sweeps.

## Purpose

DGS2 (450 points, vps3, 14 Nov 2026) and DGS3 (650 points, vps3, 20–21 Nov
2026) filled a packaged-ADM1 design grid in QSDsan 1.5.3 / EXPOsan 1.5.3.
Those fills were marked "run, not validated." Q-05 adds a second, independent
code (official PyADM1 commit e7f806e1984a382ce6d6c17ad595561e3e8b293d) on a
pre-chosen subset of the same points, plus a BSM2-anchored check that reuses
the Q-02 harness and its already-frozen band.

## Pinned qsdsan result files (copied read-only from vps3)

Copied 22 Nov 2026, 4:37–4:38 PM PST, into `/workspace/ywsim-results/` on
the box. The live vps3 copies were not modified. Fan runners and later
digester work on vps3 (DGS4/DGS5) were not touched.

- DGS2 points: `/workspace/ywsim-results/20261113-dgs2/points.jsonl`
  SHA-256 `1b22b09edaf4b8f74fd3e0a9b2c4131bb2fcfe60eaa3178c95b7cec858e96796`
- DGS2 summary: `/workspace/ywsim-results/20261113-dgs2/summary.json`
  SHA-256 `ae712a839c5b869ebe0b9c0ff9dcc7c98446839cf1e1eaf4ee46707d0189a2ea`
- DGS3 points: `/workspace/ywsim-results/20261120-dgs3/points.jsonl`
  SHA-256 `c702de89b2888f5d6d2db48d090b945d6756218f51a08c868ebad3c88d378c2a`
- DGS3 summary: `/workspace/ywsim-results/20261120-dgs3/summary.json`
  SHA-256 `d59769ff837cb514935716b6d9ea713d8aca65ff1b33aad0ab176a2032a64f05`

A Q-05 comparison must hash these files at run time and refuse to score if
any checksum differs.

## How the subset was chosen (a priori grid design)

The subset is a geometric sample of the packaged BSM2 / brewery grid, not a
cherry-pick of easy or hard metric values.

1. The packaged-BSM2 centre: `DGS:bsm2:T35:Q170:s1` (200 d, BDF). This is
   the same Q, T, V, and scale as Rosen & Jeppsson 2006 section 7, but it is
   **not** the Q-02 Table 5 influent: QSDsan `default_inf_kwargs` uses
   S_IC = 0.480428 kmol C/m3 and S_IN = 0.140067 kmol N/m3, whereas Q-02 /
   Table 5 uses 0.04 and 0.01. Code-to-code for this key is against the
   stored DGS2 row, not against Table 6.
2. Four BSM2 corners of the original 20261113 design-sweep ranges
   (T in {30, 40} °C, Q in {68, 255} m3/d, scale in {0.5, 1.5}), pairing
   low-T/long-HRT/dilute, high-T/short-HRT/concentrated, and the two mixed
   corners.
3. The packaged brewery feed at the centre and at the two extreme corners
   (low-T/long-HRT/dilute and high-T/short-HRT/concentrated).
4. Two interior points from the DGS2 finer mid-grid (T 32.5/37.5 °C,
   intermediate Q and scale).
5. Three DGS3 family A overload-boundary points at packaged BSM2: the
   official Q and T at scales 1.75 and 4.0, and the high-T/short-HRT corner
   at scale 4.0.
6. DGS3 family B rule, applied only to the DGS2 keys already listed above:
   if DGS3 contains a 400-day BDF rerun of that key, include that 400-day
   key. 800-day reruns are not included (runtime). Family C (LSODA/Radau)
   is excluded: those rows are a qsdsan solver study, not a like-for-like
   BDF comparison with official PyADM1 (`DOP853` + `DAESolve`).

Resolved 400-day keys present in the pinned DGS3 file (existence only):

- `DGS3B:bsm2:T40:Q255:s1.5:t400`
- `DGS3B:bsm2:T30:Q255:s1.5:t400`

### Frozen key list (15 points)

DGS2 (200 d, BDF):

1. `DGS:bsm2:T35:Q170:s1`
2. `DGS:bsm2:T30:Q68:s0.5`
3. `DGS:bsm2:T40:Q255:s1.5`
4. `DGS:bsm2:T30:Q255:s1.5`
5. `DGS:bsm2:T40:Q68:s0.5`
6. `DGS:brewery:T35:Q170:s1`
7. `DGS:brewery:T40:Q255:s1.5`
8. `DGS:brewery:T30:Q68:s0.5`
9. `DGS:bsm2:T32.5:Q113.3:s1.25`
10. `DGS:bsm2:T37.5:Q208:s0.75`

DGS3A (200 d, BDF):

11. `DGS3A:bsm2:T35:Q170:s1.75`
12. `DGS3A:bsm2:T35:Q170:s4`
13. `DGS3A:bsm2:T40:Q255:s4`

DGS3B (400 d, BDF):

14. `DGS3B:bsm2:T40:Q255:s1.5:t400`
15. `DGS3B:bsm2:T30:Q255:s1.5:t400`

## Same inputs (PyADM1 must match the sweep)

- Feeds: packaged EXPOsan `default_inf_kwargs` (bsm2) or
  `brewery_inf_kwargs` (brewery), both in kg/m3 in this EXPOsan 1.5.3
  build. `X_c` maps to PyADM1 `X_xc`. Missing `X_su` is 0. `S_cat` /
  `S_an` map to `S_cation` / `S_anion`. Concentration scale multiplies
  only the COD-like keys used by the DGS2 runner (`S_su`, `S_aa`, `S_fa`,
  `S_va`, `S_bu`, `S_pro`, `S_ac`, `S_h2`, `S_ch4`, `S_I`, `X_c`/`X_xc`,
  `X_ch`, `X_pr`, `X_li`, `X_su`, `X_aa`, `X_fa`, `X_c4`, `X_pro`, `X_ac`,
  `X_h2`, `X_I`). Inorganic C/N and ions are not scaled.
- Q, T, t_days, and BDF-vs-official-PyADM1 stepping as specified by the
  key. `V_liq` = 3400 m3, `V_gas` = 300 m3.
- Temperature: recompute official PyADM1 `T_ad` / `T_op` and the T-dependent
  `K_w`, `K_a_co2`, `K_a_IN`, `p_gas_h2o`, `K_H_co2`, `K_H_ch4`, and
  `K_H_h2` with the official formulas already in PyADM1.py. Do not change
  biological uptake or half-saturation constants. Do not edit the official
  PyADM1 source tree.
- Official PyADM1 method only: `simulate()` + `DAESolve()` at 0.25 d steps
  for `t_days` days, solver `DOP853`. A single multi-day BDF call without
  `DAESolve` is not a valid check.
- Initial state: official `digester_initial.csv` (same as Q-02). After 200
  or 400 days this is a start-up choice, not a change of influent.
- Pinned versions: QSDsan 1.5.3 / EXPOsan 1.5.3 / BioSTEAM 2.54.0 (stored
  rows); PyADM1 commit e7f806e1984a382ce6d6c17ad595561e3e8b293d.

## BSM2-anchored check (Q-02 harness)

Separately from the 15 sweep keys, Q-05 requires the already-frozen Q-02
three-way PASS against Rosen & Jeppsson 2006 Table 6 (section 7, Table 5
influent, Q = 170 m3/d, 35 °C, 200 d). The Q-02 band in
`PRE-REGISTERED-BAND-Q02.md` is not reopened. Official Q-02 results at
`/workspace/ywsim-results/q02-fullstate-r3/` may be re-scored against that
band; a new 200-day integration of the Table 5 case is not required if
those result files are present and the band still PASSES. This anchor is
the published-benchmark check. It is not a substitute for code-to-code
agreement on the 15 packaged-influent sweep keys.

## Decision rule for the 15 sweep points (frozen)

Compare PyADM1 to the stored qsdsan row for the same key, after converting
PyADM1 states into the JSONL units:

- `S_ac_eff_mg_L` = PyADM1 `S_ac` (kg COD/m3) × 1000
- `S_ch4_eff_mg_L` = PyADM1 `S_ch4` (kg COD/m3) × 1000
- `pH` = PyADM1 `pH`
- `CH4_kgCOD_d` = q_gas_headspace × `S_gas_ch4`
  (m3/d × kg COD/m3), where q_gas_headspace is `max(0, k_p * (Pgas - Patm))`
  as in official PyADM1. This is the methane COD mass leaving in the gas.

Let x be the PyADM1 value and x_ref the stored qsdsan value. If x_ref is
not zero, e_rel = |x - x_ref| / |x_ref|. If x_ref is zero, the metric
passes only if |x - x_ref| is at most the absolute floor below.

Required metrics: `S_ac_eff_mg_L`, `S_ch4_eff_mg_L`, `pH`, `CH4_kgCOD_d`.
A missing required metric on either side, a non-finite value, or a qsdsan
row whose status is not a finished run is a completeness FAIL for that
point.

**Class S** (standard 200 d DGS2 points, keys 1–10):

- `S_ac_eff_mg_L` and `S_ch4_eff_mg_L`: e_rel ≤ 5.0%; if x_ref is 0,
  |x - x_ref| ≤ 0.01 mg/L.
- `pH`: |x - x_ref| ≤ 0.10 pH units.
- `CH4_kgCOD_d`: e_rel ≤ 5.0%; if x_ref is 0, |x - x_ref| ≤ 1e-6 kg COD/d.

**Class O** (overload or extended-time points, keys 11–15: DGS3A scale
≥ 1.75, and DGS3B 400 d):

- `S_ac_eff_mg_L` and `S_ch4_eff_mg_L`: e_rel ≤ 10.0%; if x_ref is 0,
  |x - x_ref| ≤ 0.01 mg/L.
- `pH`: |x - x_ref| ≤ 0.20 pH units.
- `CH4_kgCOD_d`: e_rel ≤ 10.0%; if x_ref is 0, |x - x_ref| ≤ 1e-6 kg COD/d.

Justification, written a priori: Q-02 already uses a 1% band for well-specified
liquid COD states on the published BSM2 known-answer case, and 5% for
hydrogen and Qgas because Rosen §5.3 and §8.1 call those solver-sensitive.
The 15 sweep points are not a published known-answer vector. They change
T, HRT, concentration, and feed, and Class O includes overload and longer
integrations. A 5% engineering band on the reported liquid COD, pH (as an
absolute 0.10, which is tighter than 5% of a pH near 7), and methane mass
rate is therefore the code-to-code bar for the standard grid; 10% and 0.20
pH are reserved for the overload / 400-day points.

A point **PASSES** if and only if every required metric meets its class
rule. Q-05 **PASSES** if and only if:

1. The Q-02 BSM2-anchored three-way check PASSES, and
2. All 15 subset points PASS.

If only a proper subset of the 15 can be run, report those points and do
not declare a Q-05 PASS.

Optional extras (reported, not required for PASS): `CO2_kgC_d`,
`CH4_per_feedCOD`, gas partial pressures, liquid S_h2.
