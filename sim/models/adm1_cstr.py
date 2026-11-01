"""ADM1 baseline: anaerobic CSTR using QSDsan/EXPOsan `adm` benchmark.

SOURCED: kinetic/stoichiometric parameters, influent composition, reactor
volume (3400 m3 liquid) and Q=170 m3/d are the BSM2 ADM1 benchmark values
of Rosen & Jeppsson (2006) as packaged and verified in exposan.adm
(QSDsan, NCSA license). NOT yard-waste specific.
ASSUMPTION (labelled): sweeping Q (HRT) and temperature only; yard-waste
feed fractionation is an open gap (GAP-02), so no grass/leaf feed is used.
Check: benchmark steady-state S_ac = 197.63 mg COD/L (Rosen & Jeppsson
2006, sec. 7 output table: 0.1976297 kg COD/m3). 89.3 mg COD/L is only
exposan's default_init_conds start value, not the benchmark output.
Units: QSDsan ADM1 S_ch4 is measured as COD and S_IC as C, so imass*24
gives kg COD/d and kg C/d (checked Oct 31, 2026).
Output status: run, not validated.
"""
import numpy as np
from exposan.adm import system as S


def run(Q=170.0, T_C=35.0, t_days=200):
    S.Q = Q; S.Temp = 273.15 + T_C
    sys = S.create_system()
    AD = sys.path[0]
    sys.simulate(state_reset_hook='reset_cache', t_span=(0, t_days),
                 t_eval=np.arange(0, t_days + 5, 5), method='BDF')
    bg = AD.outs[0]; eff = AD.outs[1]
    ch4 = bg.imass['S_ch4'] * 24   # kg COD/d (QSDsan mass basis)
    co2 = bg.imass['S_IC'] * 24    # kg C/d
    return {'HRT_d': round(AD.V_liq / Q, 2), 'CH4_kgCOD_d': round(ch4, 2),
            'CO2_kgC_d': round(co2, 2),
            'S_ac_eff_mg_L': round(eff.iconc['S_ac'], 2)}
