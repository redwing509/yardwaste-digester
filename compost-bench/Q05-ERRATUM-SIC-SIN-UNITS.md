# Q-05 erratum: packaged S_IC / S_IN units in the frozen band

**Written:** Sun 22 Nov 2026, 5:16 PM PST (America/Los_Angeles, UTC-8).

This is an erratum. It does **not** edit `PRE-REGISTERED-BAND-Q05.md`.
The frozen decision rule, keys, limits, and SHA-256 pins are unchanged.

## What is wrong in the frozen text

`PRE-REGISTERED-BAND-Q05.md` lines 57–62 say that QSDsan
`default_inf_kwargs` uses `S_IC = 0.480428 kmol C/m3` and
`S_IN = 0.140067 kmol N/m3`, and therefore that the packaged-BSM2 centre
`DGS:bsm2:T35:Q170:s1` is not the Q-02 / Table 5 influent (0.04 / 0.01).

Those stored numbers are **kg C/m3 and kg N/m3**, not kmol/m3. EXPOsan
1.5.3 sets them as `0.04 * C_mw` and `0.01 * N_mw` with
`C_mw = 12.0107` and `N_mw = 14.0067`. Dividing recovers 0.04 kmol C/m3
and 0.01 kmol N/m3, the same values as Table 5.

The “same inputs” section of the band already required packaged kwargs
“in kg/m3”. Commit `abae8c4` implemented that conversion in the runner
and in `config/q05-packaged-influent.json`. The band file itself was
left untouched.

## What does not change

- Key 1 is still scored against the pinned DGS2 row, not against
  Rosen & Jeppsson Table 6. The Q-02 Table 6 check remains the separate
  BSM2-anchored reuse of the already-frozen Q-02 band.
- After the conversion, the packaged-bsm2 state vector matches the Q-02
  Table 5 influent. That is a wording correction, not a new subset choice
  and not a change to the pass/fail rule.
