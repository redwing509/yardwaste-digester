"""Run the packaged QSDsan/EXPOsan BSM2 ADM1 case and map states to Table 6 units.

Uses the same numerical settings as adm1_sch4_benchmark.py (BDF, 200 d, 5 d
t_eval, reset_cache). Requires YWSIM_ALLOW_INTEGRATION=1.
"""
from decimal import Decimal

from adm1_sch4_benchmark import (
    POINT_Q_M3_D,
    POINT_T_C,
    POINT_T_DAYS,
    SIMULATE_METHOD,
    STATE_RESET_HOOK,
    T_EVAL_STEP_D,
    assert_benchmark_identity,
    assert_point,
    liquid_outlets,
)

# ADM1 / Rosen Table 3 gas constant and COD equivalents.
R_BAR = 0.083145  # bar.M^-1.K^-1
T_BASE = 298.15
T_AD = 308.15
P_ATM = 1.013  # bar
# pgas,h2o = 0.0313 * exp(5290 * (1/T_base - 1/T_ad))
import math
P_GAS_H2O = 0.0313 * math.exp(5290.0 * (1.0 / T_BASE - 1.0 / T_AD))
COD_CH4 = 64.0  # kg COD / kmol CH4
COD_H2 = 16.0   # kg COD / kmol H2
C_MW = 12.0107
N_MW = 14.0067

LIQUID_COD = [
    "S_su", "S_aa", "S_fa", "S_va", "S_bu", "S_pro", "S_ac", "S_h2", "S_ch4", "S_I",
    "X_c", "X_ch", "X_pr", "X_li", "X_su", "X_aa", "X_fa", "X_c4", "X_pro", "X_ac", "X_h2", "X_I",
]
# Table 6 name <- qsdsan iconc / state name when different
X_NAME = {"X_c": "X_c"}  # qsdsan uses X_c for composites (Rosen XC)


def _require_allow():
    import os
    if os.environ.get("YWSIM_ALLOW_INTEGRATION") != "1":
        raise RuntimeError("refusing the 200-day integration unless YWSIM_ALLOW_INTEGRATION=1")


def run_qsdsan(Q=170, T_C=35, t_days=200):
    """Integrate and return Table 6 unit predictions plus raw accessors."""
    _require_allow()
    assert_point(Q, T_C, t_days)
    import numpy as np
    from exposan.adm import system as adm_system

    adm_system.Q = Q
    adm_system.Temp = 273.15 + T_C
    system = adm_system.create_system()
    unit = system.path[0]
    hrt = unit.V_liq / Q
    temperature_K = getattr(unit, "T", None)
    if temperature_K is None:
        raise RuntimeError("reactor did not expose T")
    assert_benchmark_identity(hrt, temperature_K)
    liquid_outlets(unit)
    system.simulate(
        state_reset_hook=STATE_RESET_HOOK,
        t_span=(0, t_days),
        t_eval=np.arange(0, t_days + T_EVAL_STEP_D, T_EVAL_STEP_D),
        method=SIMULATE_METHOD,
    )
    biogas, effluent, ids = liquid_outlets(unit)
    # After simulate(), unit.state is a dict in Table-6-like units for COD
    # (kg COD/m3). iconc for those components is 1000x (mg/L) and is not used
    # here. S_IC / S_IN in state are kg C or N / m3 and are divided by MW.
    if not isinstance(unit.state, dict):
        raise RuntimeError(f"expected unit.state to be a dict after simulate, got {type(unit.state)}")
    st = {k: float(v) for k, v in unit.state.items()}

    pred = {}
    for name in ("S_su", "S_aa", "S_fa", "S_va", "S_bu", "S_pro", "S_ac", "S_h2", "S_ch4", "S_I"):
        pred[name] = st[name]
    pred["S_IC"] = st["S_IC"] / C_MW
    pred["S_IN"] = st["S_IN"] / N_MW
    pred["X_c"] = st["X_c"]
    for name in ("X_ch", "X_pr", "X_li", "X_su", "X_aa", "X_fa", "X_c4", "X_pro", "X_ac", "X_h2", "X_I"):
        pred[name] = st[name]
    pred["S_cat"] = st["S_cat"]
    pred["S_an"] = st["S_an"]
    pred["Qad"] = float(Q)
    pred["Top"] = float(T_C)
    pH = getattr(effluent, "_pH", None)
    if pH is None:
        pH = getattr(effluent, "pH", None)
    pred["pH"] = None if pH is None else float(pH)
    if pred["pH"] is not None:
        pred["SH+"] = 10.0 ** (-pred["pH"])

    # Gas: state values are molar (M = kmol/m3)
    s_h2_m = float(st["S_h2_gas"])
    s_ch4_m = float(st["S_ch4_gas"])
    s_co2_m = float(st["S_IC_gas"])
    pred["Sgas_h2"] = s_h2_m * COD_H2
    pred["Sgas_ch4"] = s_ch4_m * COD_CH4
    pred["Sgas_co2"] = s_co2_m
    T = float(temperature_K)
    pred["pgas_h2"] = s_h2_m * R_BAR * T
    pred["pgas_ch4"] = s_ch4_m * R_BAR * T
    pred["pgas_co2"] = s_co2_m * R_BAR * T
    pred["Pgas"] = pred["pgas_h2"] + pred["pgas_ch4"] + pred["pgas_co2"] + P_GAS_H2O
    q_head = float(unit._q_gas)
    # Table 6 Qgas is at atmospheric pressure, not headspace pressure.
    pred["Qgas"] = q_head * pred["Pgas"] / P_ATM
    pred["_q_gas_headspace"] = q_head
    pred["_P_gas_unit"] = float(unit._P_gas)
    pred["_pgas_h2o"] = P_GAS_H2O
    pred["_HRT_d"] = float(hrt)
    pred["_T_K"] = T
    pred["_outlets"] = ids
    pred["_conversions"] = {
        "S_IC": "iconc['S_IC'] / 12.0107 kg C m-3 -> kmole C m-3",
        "S_IN": "iconc['S_IN'] / 14.0067 kg N m-3 -> kmole N m-3",
        "Sgas_ch4": "state S_ch4_gas [M] * 64 kg COD/kmol",
        "Sgas_h2": "state S_h2_gas [M] * 16 kg COD/kmol",
        "Sgas_co2": "state S_IC_gas [M] as kmole C m-3",
        "pgas_i": "S_i[M] * 0.083145 bar M-1 K-1 * T",
        "Qgas": "unit._q_gas * Pgas / 1.013 bar (atmospheric, Rosen Table 6 note)",
    }
    return pred
