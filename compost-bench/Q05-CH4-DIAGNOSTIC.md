# Q-05 diagnostic: why brewery CH4 mass rate diverges while liquids agree

**Written:** Sun 22 Nov 2026, 5:12 PM PST (America/Los_Angeles, UTC-8), after
the official Q-05 r2 comparison was scored.

This note is a post-run diagnosis. It does **not** change
`PRE-REGISTERED-BAND-Q05.md`, `config/q05-subset.json`, or any recorded
verdict. The official result remains **Q-05 FAIL**. No rescore was performed.

Diagnostic reruns (same pinned official PyADM1 e7f806e1 and the same QSDsan
1.5.3 / EXPOsan 1.5.3 construction used by DGS2) were written only under
`/workspace/ywsim-results/q05-pyadm1-logs/ch4-diagnostic/` and were not mixed
into the official result directory.

## Recorded FAIL (unchanged)

Class S CH4_kgCOD_d, 5% relative limit:

| Key | PyADM1 | DGS qsdsan | rel | band |
| --- | ---: | ---: | ---: | --- |
| `DGS:brewery:T35:Q170:s1` | 892.885 | 966.790 | 7.644% | FAIL |
| `DGS:brewery:T30:Q68:s0.5` | 185.792 | 196.155 | 5.283% | FAIL |
| `DGS:brewery:T40:Q255:s1.5` | 2086.530 | 2162.666 | 3.520% | PASS |
| `DGS:bsm2:T35:Q170:s1` (centre) | 4699.352 | 4552.890 | 3.217% | PASS |

All 15 points passed liquid S_ac, S_ch4, and pH. The Q-02 BSM2-anchored
check passed. 13/15 points passed overall.

## What was tested

Five official keys were re-integrated to recover fields the official
comparison files did not store (particulate COD, qsdsan `q_gas`, vapor
pressure, and both methane extractors). The diagnostic PyADM1 CH4_kgCOD_d
matched the official r2 files exactly. The diagnostic qsdsan
`bg.imass["S_ch4"]*24` matched the pinned DGS2 JSONL exactly (residuals
~1e-8 kg COD/d).

## Hypotheses and evidence

### 1. Influent mapping bug — rejected

Component-wise brewery (and BSM2) influent COD keys match between the Q-05
packaged pin and live EXPOsan `brewery_inf_kwargs` / `default_inf_kwargs`.
The only apparent numeric differences are the already-documented unit
conversions:

- EXPOsan stores S_IC / S_IN as kg C or N per m3 (0.480428 / 0.140067).
  PyADM1 is given 0.04 kmol C/m3 and 0.01 kmol N/m3 (`/ 12.0107` and
  `/ 14.0067`).
- `S_cat` / `S_an` vs `S_cation` / `S_anion` are the same 0.04 / 0.02
  values under different names.
- Missing `X_su` in the EXPOsan dict is 0, as the frozen band required.

Feed COD agrees: brewery s1 is 6.801 kg/m3 on both sides; BSM2 s1 is
57.096 kg/m3. This is not a kg/m3 vs mg/L mix-up (that would have missed
by 1000×). Because the mapping is consistent with the pre-registered
“same packaged inputs” rule, this diagnosis does **not** propose a
James-approved rerun to fix a harness mapping bug.

### 2. Methane extractor mismatch (`q_head * S_gas_ch4` vs `imass*24`) — rejected

On the diagnostic qsdsan runs, `q_gas_headspace * Sgas_ch4` and
`bg.imass["S_ch4"]*24` agree to about 0.004% (BSM2 centre: 4553.051 vs
4552.890). The official comparison is like-for-like on this metric.

Using atmospheric flow instead (`Qgas * Sgas_ch4`) makes every point
worse and is not the DGS definition.

### 3. Unconverted liquid / particulate COD — rejected

Every COD state, including composites, inerts, and biomass, agrees
typically to ≪ 0.3% (S_ac at the BSM2 centre is the largest liquid
offset, 0.414%, already inside the Class S band). Effluent total COD
agrees to about 0.004% or better. The missing methane is not sitting in
the liquid.

### 4. Gas-flow valve sensitivity to a small vapor-pressure difference — accepted

Both codes use the same ADM1 pipe-resistance law, `q_head = k_p * (Pgas - Patm)`
with `k_p = 50000 m3/d/bar` and `Patm = 1.013 bar`, and
`CH4_kgCOD_d = q_head * Sgas_ch4`.

Gas-phase methane concentration agrees to ~0.1%. Partial pressures of CH4
and CO2 also agree to ~0.1%. The CH4 mass-rate gap is almost entirely
`q_head`, and `q_head` is almost entirely `(Pgas - Patm)`.

Water vapor is the one systematic offset:

- Official PyADM1 (Rosen / Jeppsson form already in `PyADM1.py`):
  `p_gas_h2o = 0.0313 * exp(5290 * (1/298.15 - 1/T))`
  giving 0.04194 / 0.05567 / 0.07322 bar at 30 / 35 / 40 °C.
- QSDsan `AnaerobicCSTR.p_vapor`: `components.H2O.Psat(T)` (thermo
  saturation pressure, Pa converted to bar), giving 0.04247 / 0.05629 /
  0.07385 bar at the same temperatures (~0.0005–0.0006 bar higher).

Because outflow depends on the **overpressure** above 1.013 bar, a 0.0006 bar
vapor difference is negligible when Pgas is well above atmospheric (BSM2
centre, overpressure ~0.058 bar, CH4 rel 3.22%, inside 5%) and is
amplified when biogas production is low and Pgas only just exceeds Patm
(brewery centre, overpressure ~0.013–0.014 bar, CH4 rel 7.64%; dilute
brewery T30, overpressure ~0.0027 bar, CH4 rel 5.28%). The high-load
brewery corner, with a larger overpressure (~0.032 bar), stays inside the
band (3.52%).

The sign also flips with operating point (PyADM1 CH4 is 3.22% high at the
BSM2 centre and 3.5–7.6% low on the brewery points). That is consistent
with a small absolute Pgas offset riding on a changing overpressure, not
with a one-sided feed-mapping error.

`k_L_a` in official PyADM1 is 200 d⁻¹. A qsdsan attribute was not
exposed on the unit in this diagnostic; liquid S_ch4 and Sgas_ch4 already
agree tightly, so a large kLa mismatch is unlikely to be the main term.

## COD recovery (supporting, not a rescore)

At the BSM2 and brewery centres, qsdsan `(CH4 + Q * COD_eff) / (Q * COD_in)`
is 1.000. PyADM1 is 1.015 and 0.936 at those two centres; the leftover is
the same methane offset already scored. The dilute brewery T30 point
over-recovers in both codes (PyADM1 1.053, qsdsan 1.097), consistent with
digesting the shared `default_init_conds` inventory at a very low OLR
(0.068 kg COD/m3/d, 200 d, HRT 50 d). Liquids still agree there.

## Conclusion

The brewery CH4 failures are a real code-to-code difference in the ADM1
gas outflow rate, driven by a ~0.0006 bar water-vapor pressure formula
difference that the `k_p*(Pgas-Patm)` valve amplifies when overpressure is
small. They are not a Q-05 influent-mapping or extractor bug.

- Verdict stays **FAIL**.
- The frozen band is not moved.
- No silent harness change and no official rescore.

An optional later comparison that pinned a shared vapor-pressure formula,
or that scored `q_head` and `Pgas` explicitly, would be a new
pre-registered study and would need James's OK. It is not required to
close this diagnosis.
