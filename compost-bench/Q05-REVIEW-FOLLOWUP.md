# Q-05 CodeRabbit follow-up (no official rescore)

**Written:** Sun 22 Nov 2026, after the CodeRabbit CLI review of `13d653d`.
Official r2 results in `YWSIM_RESULT_DIR` were not rescored. The frozen band is unchanged. The Q-05 verdict remains **FAIL** (13/15; Q-02 anchor PASS).

## Findings addressed in this follow-up

1. **Resume identity (real).** A later resume could reuse a stale `status=ok` row after the harness, subset, or packaged influent changed. `_reusable_ok_keys` now skips a cached row unless `_run_identity` and the point parameters both match this run. Official r2 used a fresh directory, so every ok row was new; this did not affect the recorded 13/15.

2. **Short official `simulate()` (real latent).** Official `simulate()` returns only `r.y` and does not check `r.success` or the requested endpoint. The sweep runner now wraps `solve_ivp` and fails the point if the integration is short or unsuccessful. Official r2: all 15 rows were `status=ok`, `t_days` was 200 or 400, `step_d` was 0.25, and runtimes (about 17–43 s, with 400-day points taking longer) are consistent with full integrations. No official point is known to have been short.

3. **Grid endpoint (real latent).** `np.arange` can omit `t_days` when that horizon is not an integer number of steps. Official r2 horizons 200 and 400 are divisible by 0.25 (801 and 1601 points). The grid helper now always appends the exact endpoint. No official rescore.

The recorded FAIL, the brewery CH4 diagnosis, and the S_IC/S_IN erratum are unchanged.
