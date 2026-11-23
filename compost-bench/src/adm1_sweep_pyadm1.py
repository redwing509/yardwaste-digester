"""Official PyADM1 runner for a Q-05 packaged-influent sweep point.

Does not edit the official PyADM1 source tree. Reuses load_official() from
the Q-02 harness. Temperature only updates Ka and Henry KH, not biological
rates. Integration is refused unless YWSIM_ALLOW_INTEGRATION=1.
"""
from __future__ import annotations

import math
from pathlib import Path

from adm1_fullstate_pyadm1 import (
    COMMIT,
    DEFAULT_PYADM1,
    COD_CH4,
    COD_H2,
    P_ATM,
    R_BAR,
    STEP_D,
    _require_allow,
    load_official,
)

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
INFLUENT_FILE = CONFIG_DIR / "q05-packaged-influent.json"
STATE_NAMES = [
    "S_su", "S_aa", "S_fa", "S_va", "S_bu", "S_pro", "S_ac", "S_h2", "S_ch4",
    "S_IC", "S_IN", "S_I", "X_xc", "X_ch", "X_pr", "X_li", "X_su", "X_aa",
    "X_fa", "X_c4", "X_pro", "X_ac", "X_h2", "X_I", "S_cation", "S_anion",
    "S_H_ion", "S_va_ion", "S_bu_ion", "S_pro_ion", "S_ac_ion", "S_hco3_ion",
    "S_co2", "S_nh3", "S_nh4_ion", "S_gas_h2", "S_gas_ch4", "S_gas_co2",
]
INFLUENT_KEYS = [
    "S_su", "S_aa", "S_fa", "S_va", "S_bu", "S_pro", "S_ac", "S_h2", "S_ch4",
    "S_IC", "S_IN", "S_I", "X_xc", "X_ch", "X_pr", "X_li", "X_su", "X_aa",
    "X_fa", "X_c4", "X_pro", "X_ac", "X_h2", "X_I", "S_cation", "S_anion",
]


def load_packaged_influent(path=INFLUENT_FILE):
    import json
    return json.loads(Path(path).read_text())


def scale_influent(feed: str, conc_scale: float, packaged=None) -> dict:
    """Return influent in official PyADM1 units (kg COD/m3, kmol C or N/m3).

    EXPOsan 1.5.3 stores S_IC and S_IN as kg C/m3 and kg N/m3. Convert those
    two fields with the pinned component molecular weights. COD keys are
    already kg COD/m3. Inorganic C/N and ions are not scaled.
    """
    packaged = packaged if packaged is not None else load_packaged_influent()
    if feed not in packaged["feeds"]:
        raise ValueError(f"unknown feed {feed!r}")
    base = packaged["feeds"][feed]
    scale = float(conc_scale)
    out = {k: float(v) for k, v in base.items()}
    for key in packaged["cod_keys"]:
        if key not in out:
            raise KeyError(f"COD key {key} missing from feed {feed}")
        out[key] = out[key] * scale
    conv = packaged.get("pyadm1_unit_conversion") or {}
    for field in ("S_IC", "S_IN"):
        mw = float(conv[field]["divide_by_MW"])
        if mw <= 0:
            raise ValueError(f"invalid MW for {field}")
        out[field] = out[field] / mw
    return out


def temperature_constants(t_c: float, R=R_BAR, t_base=298.15) -> dict:
    """Official PyADM1 T-dependent physicochemical constants only."""
    t_ad = 273.15 + float(t_c)
    inv = (1.0 / t_base) - (1.0 / t_ad)
    return {
        "T_ad": t_ad,
        "T_op": t_ad,
        "K_w": 10 ** -14.0 * math.exp((55900 / (100 * R)) * inv),
        "K_a_co2": 10 ** -6.35 * math.exp((7646 / (100 * R)) * inv),
        "K_a_IN": 10 ** -9.25 * math.exp((51965 / (100 * R)) * inv),
        "p_gas_h2o": 0.0313 * math.exp(5290 * inv),
        "K_H_co2": 0.035 * math.exp((-19410 / (100 * R)) * inv),
        "K_H_ch4": 0.0014 * math.exp((-14240 / (100 * R)) * inv),
        "K_H_h2": 7.8e-4 * math.exp((-4180 / (100 * R)) * inv),
    }


def apply_temperature(ns: dict, t_c: float) -> dict:
    constants = temperature_constants(t_c, R=float(ns["R"]), t_base=float(ns["T_base"]))
    ns.update(constants)
    return constants


def _gas_rates(ns: dict, t_op: float) -> dict:
    s_h2 = float(ns["S_gas_h2"])
    s_ch4 = float(ns["S_gas_ch4"])
    s_co2 = float(ns["S_gas_co2"])
    p_h2 = s_h2 * R_BAR * t_op / COD_H2
    p_ch4 = s_ch4 * R_BAR * t_op / COD_CH4
    p_co2 = s_co2 * R_BAR * t_op
    p_h2o = float(ns["p_gas_h2o"])
    p_gas = p_h2 + p_ch4 + p_co2 + p_h2o
    k_p = float(ns["k_p"])
    q_head = k_p * (p_gas - P_ATM)
    if q_head < 0:
        q_head = 0.0
    q_atm = q_head * p_gas / P_ATM if P_ATM else 0.0
    ch4_kgcod_d = q_head * s_ch4
    co2_kgc_d = q_head * s_co2 * 12.0
    return {
        "Sgas_h2": s_h2,
        "Sgas_ch4": s_ch4,
        "Sgas_co2": s_co2,
        "pgas_h2": p_h2,
        "pgas_ch4": p_ch4,
        "pgas_co2": p_co2,
        "Pgas": p_gas,
        "_pgas_h2o": p_h2o,
        "_q_gas_headspace": q_head,
        "Qgas": q_atm,
        "CH4_kgCOD_d": ch4_kgcod_d,
        "CO2_kgC_d": co2_kgc_d,
        "S_ac_eff_mg_L": float(ns["S_ac"]) * 1000.0,
        "S_ch4_eff_mg_L": float(ns["S_ch4"]) * 1000.0,
        "pH": float(ns["pH"]),
    }


def run_sweep_pyadm1(
    feed: str,
    t_c: float,
    q_m3_d: float,
    conc_scale: float,
    t_days: int,
    pyadm1_path=DEFAULT_PYADM1,
    step_d=STEP_D,
    packaged=None,
):
    _require_allow()
    import numpy as np
    import pandas as pd

    influent = scale_influent(feed, conc_scale, packaged=packaged)
    ns = load_official(pyadm1_path)
    constants = apply_temperature(ns, t_c)
    ns["q_ad"] = float(q_m3_d)
    times = np.arange(0.0, float(t_days) + 1e-12, step_d)
    rows = []
    for t in times:
        row = {"time": float(t), "Q": float(q_m3_d)}
        for key in INFLUENT_KEYS:
            row[key] = float(influent[key])
        rows.append(row)
    ns["influent_state"] = pd.DataFrame(rows)
    ns["setInfluent"](0)
    simulate = ns["simulate"]
    dae = ns["DAESolve"]
    solvermethod = "DOP853"
    t0 = 0.0
    n = 0
    t = ns["influent_state"]["time"]
    for u in t[1:]:
        n += 1
        ns["setInfluent"](n)
        ns["state_input"] = [
            ns["S_su_in"], ns["S_aa_in"], ns["S_fa_in"], ns["S_va_in"], ns["S_bu_in"],
            ns["S_pro_in"], ns["S_ac_in"], ns["S_h2_in"], ns["S_ch4_in"], ns["S_IC_in"],
            ns["S_IN_in"], ns["S_I_in"], ns["X_xc_in"], ns["X_ch_in"], ns["X_pr_in"],
            ns["X_li_in"], ns["X_su_in"], ns["X_aa_in"], ns["X_fa_in"], ns["X_c4_in"],
            ns["X_pro_in"], ns["X_ac_in"], ns["X_h2_in"], ns["X_I_in"],
            ns["S_cation_in"], ns["S_anion_in"],
        ]
        sim = simulate([t0, float(u)], solvermethod)
        for i, name in enumerate(STATE_NAMES):
            ns[name] = sim[i][-1]
        dae()
        ns["S_nh4_ion"] = ns["S_IN"] - ns["S_nh3"]
        ns["S_co2"] = ns["S_IC"] - ns["S_hco3_ion"]
        ns["state_zero"] = [ns[name] for name in STATE_NAMES]
        t0 = float(u)

    rates = _gas_rates(ns, constants["T_op"])
    pred = {
        "S_su": float(ns["S_su"]), "S_aa": float(ns["S_aa"]), "S_fa": float(ns["S_fa"]),
        "S_va": float(ns["S_va"]), "S_bu": float(ns["S_bu"]), "S_pro": float(ns["S_pro"]),
        "S_ac": float(ns["S_ac"]), "S_h2": float(ns["S_h2"]), "S_ch4": float(ns["S_ch4"]),
        "S_IC": float(ns["S_IC"]), "S_IN": float(ns["S_IN"]), "S_I": float(ns["S_I"]),
        "pH": rates["pH"],
        **rates,
        "_feed": feed,
        "_T_C": float(t_c),
        "_q_m3_d": float(q_m3_d),
        "_conc_scale": float(conc_scale),
        "_step_d": step_d,
        "_t_days": int(t_days),
        "_solver": "DOP853+DAESolve",
        "_pyadm1_path": str(Path(pyadm1_path).resolve()),
        "_commit": COMMIT,
        "_temperature_constants": constants,
        "_conversions": {
            "S_ac_eff_mg_L": "S_ac kgCOD/m3 * 1000",
            "S_ch4_eff_mg_L": "S_ch4 kgCOD/m3 * 1000",
            "CH4_kgCOD_d": "q_gas_headspace * S_gas_ch4",
            "CO2_kgC_d": "q_gas_headspace * S_gas_co2 * 12",
        },
    }
    return pred
