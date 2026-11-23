# Q-05 official r2 result (recorded)

**Written:** Sun 22 Nov 2026, 5:16 PM PST (America/Los_Angeles, UTC-8).

This records the official comparison. It does not change
`PRE-REGISTERED-BAND-Q05.md` or rescore the run.

- Official result directory: `/workspace/ywsim-results/q05-pyadm1-subset/`
  (outside this checkout). `SUMMARY.json` written 22 Nov 2026, 4:49 PM PST.
- Verdict: **Q-05 FAIL**. 13 of 15 points passed. The Q-02 BSM2-anchored
  check passed.
- The only failures are brewery Class S `CH4_kgCOD_d` against the 5%
  relative limit:
  - `DGS:brewery:T35:Q170:s1`: 892.885 vs 966.790, rel 7.644%
  - `DGS:brewery:T30:Q68:s0.5`: 185.792 vs 196.155, rel 5.283%
- All 15 points passed liquid S_ac, S_ch4, and pH. The third brewery
  point `DGS:brewery:T40:Q255:s1.5` passed CH4 at 3.520%.
- A first attempt at 4:42 PM PST used raw EXPOsan S_IC / S_IN values as
  if they were already kmol/m3. It was stopped, archived under
  `/workspace/ywsim-results/q05-pyadm1-logs/attempt-1-incomplete/`, and
  is not part of the official score. The conversion is in `abae8c4`.
  See `Q05-ERRATUM-SIC-SIN-UNITS.md`.
- Why the brewery CH4 rate diverges while liquids agree is diagnosed in
  `Q05-CH4-DIAGNOSTIC.md` (vapor-pressure / gas-valve sensitivity, not a
  mapping or extractor bug). The FAIL stands.
