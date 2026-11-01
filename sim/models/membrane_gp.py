"""Single-stage complete-mixing CO2/CH4 gas permeation (solution-diffusion,
Weller-Steiner well-mixed model, binary).

SOURCED (from ../membranes CSVs): feed CH4 70.5% (ANMBR-A02, verified
row); CO2/CH4 selectivity >30 (EVONIK-M01 vendor claim, UNVERIFIED by r11
re-check). Verification target: Air Liquide multi-stage claim >98% CH4
recovery, 96.5-99% CH4 (RV-AIRLIQ-E01, verified) - a single stage is NOT
expected to meet both at once.
ASSUMPTIONS (labelled): binary gas (H2S/H2O/N2 ignored), isothermal, no
pressure drop, pressure ratio and stage cut swept.
Output status: run, not validated.
"""
from math import sqrt


def _y(x, a, r):
    # permeate CO2 fraction y for retentate CO2 fraction x (complete mixing)
    A = (a - 1) * r
    B = -((a - 1) * (x + r) + 1)
    C = a * x
    return (-B - sqrt(B * B - 4 * A * C)) / (2 * A) if A else C / -B

def run(x_feed_CO2=0.295, alpha=30.0, pr=0.1, theta=0.35):
    lo, hi = 1e-6, x_feed_CO2
    for _ in range(200):
        x = (lo + hi) / 2
        y = _y(x, alpha, pr)
        th = (x_feed_CO2 - x) / (y - x)
        lo, hi = (x, hi) if th > theta else (lo, x)
    ch4_ret = 1 - x
    th_ach = (x_feed_CO2 - x) / (y - x)
    if abs(th_ach - theta) > 1e-4:
        raise ValueError(f'stage cut {theta} not reached (got {th_ach:.4f})')
    rec = (1 - theta) * ch4_ret / (1 - x_feed_CO2)
    return {'retentate_CH4_pct': round(100 * ch4_ret, 2),
            'CH4_recovery_pct': round(100 * rec, 2),
            'permeate_CO2_pct': round(100 * y, 2),
            'stage_cut_achieved': round(th_ach, 4)}
