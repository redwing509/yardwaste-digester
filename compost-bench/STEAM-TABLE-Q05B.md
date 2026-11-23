# Q-05b steam-table check

**Written:** Sun 22 Nov 2026, 6:02:55 PM PST (America/Los_Angeles, UTC-8),
after the method was frozen in `PRE-REGISTERED-BAND-Q05B.md` at `1216299`
(5:59:11 PM PST) and before the official 200-day jADM1_BSM score was
recorded. This file reports the formula comparison. It does **not** change
the Q-05 band and does not overturn the official Q-05 FAIL.

## Method (frozen)

- Primary reference: IAPWS R7-97(2012) Region 4 saturation pressure,
  Eqs. 29–31 / Table 34, implemented in `src/iapws_if97_psat.py`.
- Rosen / PyADM1 / jADM1_BSM form:
  `p = 0.0313 * exp(5290 * (1/298.15 - 1/T))` bar, T in kelvin.
- QSDsan 1.5.3: `process_models.create_adm1_cmps().H2O.Psat(T)` in Pa,
  converted with `qsdsan.utils.auom` to bar, the same call used by
  `AnaerobicCSTR.p_vapor`.
- Temperatures: 303.15 K and 308.15 K exactly (30.00 °C and 35.00 °C).

Implementation check: p_sat(T_c = 647.096 K) = 22.0640000003 MPa against
the published IF97 identity 22.064 MPa.

## Official values

| T | IAPWS-IF97 (bar) | Rosen / PyADM1 (bar) | \|Rosen−IF97\| | qsdsan H2O.Psat (bar) | \|qsdsan−IF97\| | closer |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 30.00 °C | 0.042466883405 | 0.041940746701 | 0.000526137 | 0.042469708368 | 0.000002825 | QSDSAN |
| 35.00 °C | 0.056286201441 | 0.055667745075 | 0.000618456 | 0.056290161067 | 0.000003960 | QSDSAN |

**Overall closeness: QSDSAN_CLOSER.**

The qsdsan values match the ~0.04247 / 0.05629 bar figures already quoted
in `Q05-CH4-DIAGNOSTIC.md`. The Rosen form is about 0.00053–0.00062 bar
low, which is the same offset diagnosed after Q-05. That diagnosis is not
reopened; this table is the pre-registered physical-accuracy check of the
two formulas.

No separate NIST Chemistry WebBook table row was retrieved in this pass.
The IF97 critical-point identity above is the corroboration required by
the frozen method. A later named IAPWS-95 / NIST tabulation, if added,
would have to disagree with IF97 by more than 0.00005 bar before it would
be flagged, and it would still not decide ADM1 siding.
