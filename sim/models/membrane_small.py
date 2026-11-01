"""Small-flow, modular-stage CO2/CH4 membrane upgrading + compressor energy.

Wraps membrane_gp.run (single-stage well-mixed model) into stage layouts:
  '1'    one stage
  '2R'   stage-1 retentate fed to stage 2 (no recompression); both permeates
         leave the system (vented/flared)
  '2RR'  as 2R, but stage-2 permeate is recycled to the compressor suction
         (fixed-point iteration), so the compressor handles feed + recycle

SIZES (from this repo's specs, all [E] there, not measured):
  DIY leach-bed: ~17 m3 CH4/day at 4 wet t/week (diy/SPEC.md sec. 3)
  small unit: 17/4 m3 CH4/day per wet t/week (small-unit/econ.py), 12 t/wk base
  biogas CH4 fraction 55% (diy simulator default, [E]) -> x_feed_CO2 0.45
SOURCED: CH4 LHV 35.8 MJ/m3 (diy sizing constant). Sanity-check range for
small membrane upgrading electricity 0.21-0.33 kWh/m3 raw biogas at 5 m3/h
(MDPI Membranes 11(12):938, 2021); 0.26 kWh/Nm3 commercial 100-750 Nm3/h
(Bright PurePac Compact page).
ASSUMPTIONS (labelled): binary CO2/CH4 (no N2/O2/H2S/H2O), permeate at
1.013 bar, adiabatic compression k=1.3, suction 298 K, isentropic*motor
efficiency 0.65, intercooled equal-ratio stages when ratio > 4, no
membrane area/permeance (so no module count or cost; GAP), same stage cut
in every stage. Output status: run, not validated.
"""
from math import ceil, log

from membrane_gp import run as stage

R, T1, K, ETA, P_ATM, VM = 8.314, 298.0, 1.3, 0.65, 1.013, 22.414e-3
LHV = 35.8  # MJ/m3 CH4
CH4_PER_TPW = 17 / 4  # m3 CH4/day per wet t/week [E in spec]


def comp_kwh_per_m3(p_feed_bar):
    r = p_feed_bar / P_ATM
    n = max(1, ceil(log(r) / log(4)))
    rs = r ** (1 / n)
    j_mol = n * K / (K - 1) * R * T1 * (rs ** ((K - 1) / K) - 1) / ETA
    return j_mol / VM / 3.6e6, n


def _layout(layout, x, alpha, pr, theta):
    s1 = stage(x, alpha, pr, theta)
    x1 = 1 - s1['retentate_CH4_pct'] / 100
    if layout == '1':
        return 1 - x1, s1['CH4_recovery_pct'] / 100, 0.0
    s2 = stage(x1, alpha, pr, theta)
    x2 = 1 - s2['retentate_CH4_pct'] / 100
    rec = (s1['CH4_recovery_pct'] / 100) * (s2['CH4_recovery_pct'] / 100)
    return 1 - x2, rec, None


def run(t_per_week=4.0, layout='1', alpha=30.0, p_feed_bar=8.0, theta=0.35,
        ch4_frac=0.55):
    x_feed = 1 - ch4_frac
    biogas = CH4_PER_TPW * t_per_week / ch4_frac  # m3/day raw biogas
    pr = P_ATM / p_feed_bar
    if layout in ('1', '2R'):
        purity, rec, _ = _layout(layout, x_feed, alpha, pr, theta)
        comp_flow = biogas
    elif layout == '2RR':
        rcy, xm = 0.0, x_feed
        for _ in range(100):
            mix = biogas + rcy
            s1 = stage(xm, alpha, pr, theta)
            x1 = 1 - s1['retentate_CH4_pct'] / 100
            s2 = stage(x1, alpha, pr, theta)
            y2 = s2['permeate_CO2_pct'] / 100
            new = mix * (1 - theta) * theta
            xm = (biogas * x_feed + new * y2) / (biogas + new)
            if abs(new - rcy) < 1e-9:
                break
            rcy = new
        purity = s2['retentate_CH4_pct'] / 100
        prod = (biogas + rcy) * (1 - theta) ** 2
        rec = prod * purity / (biogas * ch4_frac)
        comp_flow = biogas + rcy
    else:
        raise ValueError(f'unknown layout {layout}')
    kwh_m3, n_comp = comp_kwh_per_m3(p_feed_bar)
    kwh_day = kwh_m3 * comp_flow
    ch4_prod = biogas * ch4_frac * rec
    return {'biogas_m3_h': round(biogas / 24, 3),
            'CH4_purity_pct': round(100 * purity, 2),
            'CH4_recovery_pct': round(100 * rec, 2),
            'compressor_stages': n_comp,
            'compressor_kW': round(kwh_day / 24, 3),
            'kWh_per_m3_raw_biogas': round(kwh_day / biogas, 3),
            'kWh_per_m3_CH4_product': round(kwh_day / ch4_prod, 3) if ch4_prod else None,
            'parasitic_pct_of_product_LHV': round(100 * kwh_day * 3.6 / (ch4_prod * LHV), 2) if ch4_prod else None}
