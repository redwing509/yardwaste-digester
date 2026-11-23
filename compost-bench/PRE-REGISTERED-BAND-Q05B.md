# Q-05b pre-registered third-model agreement rule

**Written:** Sun 22 Nov 2026, 5:57 PM PST (America/Los_Angeles, UTC-8), after
the official Q-05 FAIL and the brewery CH4 diagnosis were recorded, and
**before any new jADM1_BSM (or other third-ADM1) integration of the two
brewery points or the packaged BSM2 centre was started.**

This file freezes the third-model choice, the inputs, the decision rule, the
siding interpretation, and the steam-table method. It must not be edited to
fit later numbers. It does **not** change `PRE-REGISTERED-BAND-Q05.md`,
`config/q05-subset.json`, or the official Q-05 verdict. The official result
remains **Q-05 FAIL**, even if this third-model check later sides with one
code or finds that one vapor-pressure formula is closer to steam tables.

James authorized this build on 22 Nov 2026 (widget t1275s6543). James
t1276u said that if the work is verified accurate it may be pushed to the
public GitHub repo; that permission applies only if this frozen rule PASSES
and the full review set has no must-fix. A FAIL, MIXED, or INCONCLUSIVE
verdict is not a Q-05 rescore and is not a merge of this study to main.

All results remain model-only.

## Purpose

Q-05 compared official PyADM1 (commit
e7f806e1984a382ce6d6c17ad595561e3e8b293d) to stored QSDsan 1.5.3 / EXPOsan
1.5.3 rows on 15 packaged sweep points. Two Class S brewery points failed
the 5% band on `CH4_kgCOD_d` only. The diagnosis
(`Q05-CH4-DIAGNOSTIC.md`) attributed the gap to a ~0.0006 bar water-vapor
pressure formula difference that the shared `q_head = k_p*(Pgas-Patm)`
valve amplifies at low overpressure.

Q-05b adds a **third independent ADM1 implementation** with its own
gas-phase (including its own vapor-pressure and gas-flow law, not patched
to match either side) on:

1. `DGS:brewery:T35:Q170:s1` (Q-05 FAIL, 7.644%)
2. `DGS:brewery:T30:Q68:s0.5` (Q-05 FAIL, 5.283%)
3. `DGS:bsm2:T35:Q170:s1` (packaged BSM2 centre; Q-05 PASS, CH4 rel. 3.217%)
   as a sanity anchor.

It also compares both vapor-pressure formulas to IAPWS-IF97 (and a published
tabulated value) at 30.00 °C and 35.00 °C. That steam-table check is a
physical-accuracy comparison of the two *formulas*. It is not a third ADM1
integration and does not overturn Q-05.

## Third-model choice and independence

**Selected code:** jADM1_BSM, the BSM2-compatible Java ADM1 of Liam
Pettigrew, Lehrstuhl für Strömungsmechanik, Friedrich-Alexander-Universität
Erlangen-Nürnberg (FAU).

- Source: https://github.com/liampetti/jADM1_BSM
- Pinned commit: `dda4fb23b8f645d77737b8fdca1022830773f05b` (28 Mar 2017)
- License: Apache License 2.0 (`LICENSE.md`)
- Citation of the implementation family: Pettigrew, L., Hubert, S., Groß,
  F., Delgado, A. (2015), "Implementation of Dynamic Biological Process
  Models into a Reference Net Simulation Environment," 16. ASIM Dedicated
  Conference Simulation in Production and Logistics; and the BSM2-compatible
  code note in the jADM1_BSM README. The related Water Science and
  Technology paper (Pettigrew et al., 2017, doi:10.2166/wst.2017.227)
  describes a *modified* hydrolysis structure. That modified tree is
  `liampetti/jADM1`, **not** this study. Q-05b uses only `jADM1_BSM`.

**Own gas phase (unpatched):** `DAEModel.java` computes

```
p_gas_h2o = K_H_h2o_base * exp(5290 * (1/T_base - 1/T))
P_gas = p_gas_h2 + p_gas_ch4 + p_gas_co2 + p_gas_h2o
q_gas = k_P * (P_gas - P_atm);  if (q_gas < 0) q_gas = 0
```

with defaults `K_H_h2o_base = 0.0313` bar, `T_base = 298.15` K,
`k_P = 5.0e4` m3/d/bar, `P_atm = 1.013` bar, `kLa = 200` d⁻¹,
`V_liq = 3400` m3, `V_gas = 300` m3. This is the Rosen & Jeppsson / ADM1
Eq. (5.7)–(5.10) form, implemented in Java, not imported from PyADM1 or
QSDsan. The harness must not edit this formula, must not replace it with
`H2O.Psat`, and must not retune `k_P` or `P_atm`.

**Independence from the two Q-05 codes:**

- Not a rerun of PyADM1 or QSDsan, and not a version of either code
  family. PyADM1 is a Python port of BSM2 ADM1 (Sadrimajd / CaptainFerMag,
  MIT, pinned e7f806e1). QSDsan/EXPOsan is the BioSTEAM family (v1.5.3)
  whose `AnaerobicCSTR.p_vapor` uses `components.H2O.Psat(T)` from the
  thermo stack. jADM1_BSM is a separate Java implementation by a different
  group (FAU), with its own DAE residual, Apache Commons Math integrator,
  and I/O.
- Shared scientific ancestry with PyADM1 is the published BSM2 MATLAB
  ADM1 (Rosen & Jeppsson 2006). That is expected of a BSM2-compatible
  third implementation and does not make jADM1_BSM a PyADM1 fork. The
  point of the check is whether an independently written BSM2-style ADM1
  lands with PyADM1, with QSDsan, with both, or with neither, on the
  methane mass rate.

**Alternatives considered and not used:**

- Official IWA/Lund BSM2 MATLAB/Simulink (`wwtmodels/Benchmark-Simulation-Models`
  and `wwtmodels/Anaerobic-Digestion-Models`): this is the reference
  implementation, but it requires MATLAB/Simulink, which is not available
  on the allowed hosts, and the Simulink plant is not an Octave-runnable
  port with provenance.
- `liampetti/jADM1` (non-`_BSM`): modified hydrolysis and composites
  removed; not like-for-like with Q-05.
- `stamm-4m/model-adm1`: explicitly refactored from PyADM1; same code
  family; rejected.
- ADM1jl (Allen, Mazanko, Abdehagh, Eberl, *Processes* 2023, 11, 1899,
  doi:10.3390/pr11071899; SoftwareX 2024, 26, 101682): a peer-reviewed de
  novo Julia ODE implementation, also using Rosen Eq. (5.7). It was not
  chosen as the primary third model because it pulls a heavy
  DifferentialEquations.jl / Plots stack, while jADM1_BSM already provides
  a citable, runnable, BSM2-compatible gas phase on the box with OpenJDK.

## Frozen Q-05 references (inputs, not new runs)

The third model is scored against the official Q-05 r2 files, not against a
new PyADM1 or QSDsan integration. A Q-05b scorer must hash these files and
refuse to score if any checksum differs.

- Q-05 comparison: `/workspace/ywsim-results/q05-pyadm1-subset/comparison.json`
  SHA-256 `b8ec6efa01b5dd73bce08dfd22da89493069aa9b75bea7c258a9ffb3409f4885`
- Q-05 PyADM1 points: `/workspace/ywsim-results/q05-pyadm1-subset/pyadm1_points.jsonl`
  SHA-256 `09859e2207fca554b708d25dff39255f5bfe8621021d0cd71bd9680c1f13657d`
- Q-05 summary: `/workspace/ywsim-results/q05-pyadm1-subset/SUMMARY.json`
  SHA-256 `2dbd3e1e08f68bce18c01adc5d8fc189365898217fcd53c1efdda203317723e8`
- Packaged influent used by Q-05: `config/q05-packaged-influent.json`
  SHA-256 `c4881f9c1ed41e64e62a72f035924e6eca47b08e1489d120e86a88b394796644`
- Official PyADM1 initial state: `/workspace/digester-tools/src/PyADM1/src/digester_initial.csv`
  SHA-256 `3b2076def9b00cea22cc138af41822caa9ffc5416c126cf84f8d5239839cea3c`
  (PyADM1 commit e7f806e1984a382ce6d6c17ad595561e3e8b293d)

The original DGS2/DGS3 qsdsan source checksums in `config/q05-subset.json`
remain in force. The numeric references copied into `config/q05b-points.json`
are taken from the comparison file above (PyADM1 = `predicted`, qsdsan =
`reference`).

Recorded Q-05 `CH4_kgCOD_d` values, for identification only (the scorer
reads the hashed files):

| Key | PyADM1 | qsdsan | rel | Q-05 |
| --- | ---: | ---: | ---: | --- |
| `DGS:bsm2:T35:Q170:s1` | 4699.352 | 4552.890 | 3.217% | PASS |
| `DGS:brewery:T35:Q170:s1` | 892.885 | 966.790 | 7.644% | FAIL |
| `DGS:brewery:T30:Q68:s0.5` | 185.792 | 196.155 | 5.283% | FAIL |

## Same inputs

- Feeds: the same packaged EXPOsan `default_inf_kwargs` (bsm2) or
  `brewery_inf_kwargs` (brewery) as Q-05, including the documented S_IC /
  S_IN conversion to kmol C or N per m3 (÷ 12.0107 and ÷ 14.0067).
  Concentration scale multiplies only the COD keys listed in
  `q05-packaged-influent.json`. Inorganic C/N and ions are not scaled.
  jADM1 influent S_IC / S_IN must be in kmol/m3, same as official PyADM1.
- Q from the key, written to jADM1 influent index 35 (m3/d).
- T from the key, written to jADM1 *initial-state* index 36 (deg C). The
  influent temperature field is not the digester temperature in this code
  (`T_D` is "set by digester").
- `t_days` = 200. Solver: jADM1 DAE mode (default; do not pass `-ode`).
- `V_liq` = 3400 m3, `V_gas` = 300 m3, left at jADM1_BSM defaults, which
  already match Q-05.
- Initial liquid, ion, and gas states mapped from official
  `digester_initial.csv` (same file as Q-05 / Q-02):

  | jADM1 index | field | PyADM1 CSV column |
  | ---: | --- | --- |
  | 0–23 | S_su … X_I | S_su … X_I |
  | 24–25 | S_cat, S_an | S_cation, S_anion |
  | 26–31 | S_hva … S_nh3 | S_va_ion … S_nh3 (skip S_H_ion) |
  | 32–34 | S_gas_h2, S_gas_ch4, S_gas_co2 | same names |
  | 35 | Q_D | 0 (flow is set by influent) |
  | 36 | T_D | the point's T in deg C |
  | 37–41 | derived (q_ch4, q_gas, pH, S_co2, S_nh4) | 0 at start; S_co2 / S_nh4_ion from the CSV may be copied to 40 / 41 but are not required for the methane metric |

- Pinned third-code versions: jADM1_BSM `dda4fb23b8f645d77737b8fdca1022830773f05b`,
  Apache Commons Math 3.5 (the version declared in that repo's `pom.xml`),
  a Java 8+ runtime. Do not edit the jADM1_BSM source tree.

## Methane extractor

`CH4_kgCOD_d = q_gas_headspace * S_gas_ch4`

where `q_gas_headspace` is jADM1 state 38 (`gas_vol`, equal to `q_gas` after
`max(0, k_P*(P_gas-P_atm))`) in m3/d and `S_gas_ch4` is state 33 in kg COD/m3.
This is the same headspace mass-rate definition used by Q-05. Do **not** use
state 37 (`q_gas * p_gas_ch4 / P_gas`, a methane *volume* flow in m3/d) as
`CH4_kgCOD_d`.

Liquid metrics: `S_ac_eff_mg_L` = state 6 × 1000, `S_ch4_eff_mg_L` = state 8
× 1000, `pH` = state 39, all at t = 200 d.

## Decision rule (frozen)

Let x be the jADM1_BSM value and x_ref a frozen Q-05 value (PyADM1 or
qsdsan). If x_ref is not zero, e_rel = |x - x_ref| / |x_ref|. If x_ref is
zero, the metric agrees only if |x - x_ref| is at most the absolute floor
below. A missing required metric, a non-finite value, or a failed / missing
third-model run is a completeness failure for that point.

Required metrics: `S_ac_eff_mg_L`, `S_ch4_eff_mg_L`, `pH`, `CH4_kgCOD_d`.

All three Q-05b points are Q-05 Class S points. The agreement band is the
**same Class S rule already frozen in Q-05**, written a priori for this
study because the metric, the class, and the operating points are the same:

- `S_ac_eff_mg_L` and `S_ch4_eff_mg_L`: e_rel ≤ 5.0%; if x_ref is 0,
  |x - x_ref| ≤ 0.01 mg/L.
- `pH`: |x - x_ref| ≤ 0.10 pH units.
- `CH4_kgCOD_d`: e_rel ≤ 5.0%; if x_ref is 0, |x - x_ref| ≤ 1e-6 kg COD/d.

A third-model metric **agrees** with a reference code if and only if it
meets that rule against that code's frozen value.

### Per-point siding (CH4), after a liquid sanity check

The liquids (`S_ac_eff_mg_L`, `S_ch4_eff_mg_L`, `pH`) must agree with
**both** frozen PyADM1 and frozen qsdsan values. If they do not, the point
is **INCONCLUSIVE** and no CH4 siding is declared for that point.

If liquids pass, CH4 siding is:

- **SIDES_WITH_PYADM1** if CH4 agrees with PyADM1 and does not agree with qsdsan.
- **SIDES_WITH_QSDSAN** if CH4 agrees with qsdsan and does not agree with PyADM1.
- **AGREES_WITH_BOTH** if CH4 agrees with both.
- **AGREES_WITH_NEITHER** if CH4 agrees with neither.

### Packaged BSM2 centre (anchor)

The centre is a sanity check, not a brewery tie-breaker. It **PASSES** if
and only if:

1. Liquids agree with both frozen references, and
2. `CH4_kgCOD_d` agrees with at least one of the two frozen references.

If the centre fails, the study is incomplete: overall siding is
**INCONCLUSIVE** and Q-05b is not merge-eligible.

### Overall brewery siding

Computed only from the two brewery points, and only if the centre PASSES
and neither brewery point is INCONCLUSIVE:

- If both points have the same verdict, that is the overall siding.
- If the verdict set is a subset of {SIDES_WITH_PYADM1, AGREES_WITH_BOTH}
  and contains SIDES_WITH_PYADM1: overall **SIDES_WITH_PYADM1**.
- If the verdict set is a subset of {SIDES_WITH_QSDSAN, AGREES_WITH_BOTH}
  and contains SIDES_WITH_QSDSAN: overall **SIDES_WITH_QSDSAN**.
- If both are AGREES_WITH_BOTH: overall **AGREES_WITH_BOTH**.
- If both are AGREES_WITH_NEITHER: overall **AGREES_WITH_NEITHER**.
- Otherwise: **MIXED**.

Interpretation, written a priori:

- **SIDES_WITH_PYADM1** means an independent BSM2-compatible ADM1 lands
  with official PyADM1 on the methane mass rate at the failed brewery
  points. That supports the diagnosis that the Q-05 gap is the
  vapor-pressure / valve sensitivity (jADM1_BSM uses the same Rosen form
  as PyADM1), not a PyADM1-only bug. It does **not** make Q-05 a PASS.
- **SIDES_WITH_QSDSAN** means the third implementation lands with qsdsan,
  which would argue against a simple "Rosen-form vs thermo Psat" account
  and would need to be reported as such. It still does not make Q-05 a
  PASS.
- **AGREES_WITH_BOTH** is possible on a point whose two references are
  already near the 5% boundary (the dilute brewery gap is 5.283%). It is a
  completed, conclusive "no exclusive side" result, not a Q-05 pass.
- **AGREES_WITH_NEITHER** or **MIXED** or **INCONCLUSIVE** is a completed
  report but is not a conclusive siding.

## Steam-table method (formulas vs IAPWS-IF97)

This check does not use jADM1, PyADM1 integrations, or qsdsan integrations.
It evaluates the two *closed-form or library* vapor-pressure expressions at
T = 303.15 K and T = 308.15 K (30.00 °C and 35.00 °C exactly):

- PyADM1 / Rosen / Jeppsson / jADM1_BSM form:
  `p = 0.0313 * exp(5290 * (1/298.15 - 1/T))` bar, with T in kelvin.
- QSDsan 1.5.3 `components.H2O.Psat(T)` (Pa, converted to bar) from the
  already-installed `/workspace/venv-ywsim` environment. If that library
  call is unavailable, the check is INCOMPLETE, not silently replaced by
  another equation of state.

**Reference:** IAPWS R7-97(2012), *Revised Release on the IAPWS Industrial
Formulation 1997 for the Thermodynamic Properties of Water and Steam*,
Region 4 saturation-pressure equation (the formulation's Eqs. 29–31 /
Table 34). Coefficients, published and frozen here:

```
n1  =  0.11670521452767e4
n2  = -0.72421316703206e6
n3  = -0.17073846940092e2
n4  =  0.12020824702470e5
n5  = -0.32325550322333e7
n6  =  0.14915108613530e2
n7  = -0.48232657361591e4
n8  =  0.40511340542057e6
n9  = -0.23855557567849
n10 =  0.65017534844798e3
```

With T in kelvin, p* = 1 MPa:

```
theta = T + n9 / (T - n10)
A = theta**2 + n1*theta + n2
B = n3*theta**2 + n4*theta + n5
C = n6*theta**2 + n7*theta + n8
p_MPa = (2*C / (-B + sqrt(B**2 - 4*A*C)))**4
p_bar = p_MPa * 10
```

A published tabulated cross-check (NIST Chemistry WebBook saturation
pressure for water, or an equivalent IAPWS-95 / Wagner–Pruss tabulated
value with the source named) is reported at the same two temperatures. The
**closeness verdict uses IAPWS-IF97** as the primary reference. The
tabulated value is a corroboration; a disagreement larger than 0.00005 bar
between IF97 and the named table is flagged but does not by itself decide
which ADM1 formula is closer.

At each temperature, e_abs(formula) = |p_formula - p_IF97| in bar. The
formula with the smaller e_abs is **closer** at that temperature. Overall
steam-table closeness is:

- **ROSEN_CLOSER** if the Rosen / PyADM1 form is closer at both temperatures.
- **QSDSAN_CLOSER** if the qsdsan `H2O.Psat` form is closer at both.
- **MIXED** if the closer formula differs by temperature.
- **TIE** if e_abs values are equal at a temperature (exact equality).

This verdict is reported alongside Q-05b. It does not change the Q-05
band, does not convert a Q-05 FAIL into a PASS, and does not by itself
decide CH4 siding.

The IF97 implementation may be checked, before or after the 30/35 °C
official comparison is recorded, against the published IF97 identity that
p_sat(T_c = 647.096 K) = 22.064 MPa.

## Q-05b study PASS and merge eligibility

Q-05b **PASSES** (and is the "verified accurate" case for t1276u) if and
only if all of the following hold:

1. All three points produce finite required metrics from a jADM1_BSM run
   at the pinned commit, with checksums of the frozen Q-05 reference files
   matching this document.
2. The packaged BSM2 centre sanity check PASSES.
3. Both brewery points have a liquid sanity PASS (not INCONCLUSIVE).
4. Overall brewery siding is one of: SIDES_WITH_PYADM1, SIDES_WITH_QSDSAN,
   or AGREES_WITH_BOTH.
5. The steam-table comparison is completed and recorded under this method.
6. The Q-05 FAIL, and the text of `PRE-REGISTERED-BAND-Q05.md`, are
   unchanged.

If overall siding is AGREES_WITH_NEITHER, MIXED, or INCONCLUSIVE, or if
any completeness or centre check fails, the study is reported but is
**not** merge-eligible. In that case a clearly labeled open PR may still
be opened for public inspection; it must not be merged to main under
t1276u.

A Q-05b PASS does **not** overturn the frozen Q-05 FAIL.
