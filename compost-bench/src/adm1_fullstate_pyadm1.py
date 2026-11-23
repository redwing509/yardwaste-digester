"""Run official PyADM1 simulate()+DAESolve() with constant Rosen Table 5 influent.

The official source tree is not edited. A pandas.DataFrame.append shim is
applied because pandas 2+ removed append. q_ad is set to 170 m3/d (the
official script defaults to 178.4674 from its dynamic influent file, which
is not the section 7 case). Steps are 0.25 d for 200 days. A single 200-day
BDF call without DAESolve is not used.
"""
import math
import os
import runpy
import sys
import types
from pathlib import Path

DEFAULT_PYADM1 = Path("/workspace/digester-tools/src/PyADM1/src/PyADM1.py")
COMMIT = "e7f806e1984a382ce6d6c17ad595561e3e8b293d"
STEP_D = 0.25
T_DAYS = 200
Q_M3_D = 170.0
R_BAR = 0.083145
T_OP = 308.15
P_ATM = 1.013
T_BASE = 298.15
T_AD = 308.15
P_GAS_H2O = 0.0313 * math.exp(5290.0 * (1.0 / T_BASE - 1.0 / T_AD))
COD_CH4 = 64.0
COD_H2 = 16.0

# Rosen & Jeppsson 2006 Table 5 constant influent.
TABLE5 = {
    "S_su": 0.01, "S_aa": 0.001, "S_fa": 0.001, "S_va": 0.001, "S_bu": 0.001,
    "S_pro": 0.001, "S_ac": 0.001, "S_h2": 1e-8, "S_ch4": 1e-5,
    "S_IC": 0.04, "S_IN": 0.01, "S_I": 0.02,
    "X_xc": 2.0, "X_ch": 5.0, "X_pr": 20.0, "X_li": 5.0,
    "X_su": 0.0, "X_aa": 0.01, "X_fa": 0.01, "X_c4": 0.01,
    "X_pro": 0.01, "X_ac": 0.01, "X_h2": 0.01, "X_I": 25.0,
    "S_cation": 0.04, "S_anion": 0.02,
}


def _require_allow():
    if os.environ.get("YWSIM_ALLOW_INTEGRATION") != "1":
        raise RuntimeError("refusing the 200-day integration unless YWSIM_ALLOW_INTEGRATION=1")


def _patch_pandas_append():
    import pandas as pd
    if hasattr(pd.DataFrame, "append"):
        return "native"
    def append(self, other, ignore_index=False, **kwargs):
        if isinstance(other, dict):
            other = pd.DataFrame([other])
        return pd.concat([self, other], ignore_index=ignore_index)
    pd.DataFrame.append = append
    return "shim"


def _stub_matplotlib():
    if "matplotlib.pyplot" in sys.modules:
        return
    mpl = types.ModuleType("matplotlib")
    plt = types.ModuleType("matplotlib.pyplot")
    sys.modules["matplotlib"] = mpl
    sys.modules["matplotlib.pyplot"] = plt


def load_official(pyadm1_path=DEFAULT_PYADM1):
    """Exec official definitions only (cut before the built-in dynamic loop)."""
    path = Path(pyadm1_path).resolve()
    text = path.read_text()
    marker = "## time array definition"
    if marker not in text:
        raise RuntimeError("official PyADM1.py no longer has the expected loop marker; refusing to guess")
    head = text.split(marker, 1)[0]
    _stub_matplotlib()
    shim = _patch_pandas_append()
    ns = {"__name__": "pyadm1_official_head", "__file__": str(path)}
    # Official script reads CSVs from the process cwd.
    cwd = os.getcwd()
    try:
        os.chdir(path.parent)
        exec(compile(head, str(path), "exec"), ns, ns)
    finally:
        os.chdir(cwd)
    ns["_append_shim"] = shim
    return ns


def run_pyadm1(pyadm1_path=DEFAULT_PYADM1, step_d=STEP_D, t_days=T_DAYS, q_m3_d=Q_M3_D):
    _require_allow()
    import numpy as np
    import pandas as pd

    ns = load_official(pyadm1_path)
    ns["q_ad"] = float(q_m3_d)
    times = np.arange(0.0, t_days + 1e-12, step_d)
    rows = []
    for t in times:
        row = {"time": float(t), **TABLE5, "Q": float(q_m3_d)}
        rows.append(row)
    ns["influent_state"] = pd.DataFrame(rows)
    # Re-bind setInfluent to the new frame (it closed over influent_state by global lookup).
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
        names = [
            "S_su", "S_aa", "S_fa", "S_va", "S_bu", "S_pro", "S_ac", "S_h2", "S_ch4",
            "S_IC", "S_IN", "S_I", "X_xc", "X_ch", "X_pr", "X_li", "X_su", "X_aa",
            "X_fa", "X_c4", "X_pro", "X_ac", "X_h2", "X_I", "S_cation", "S_anion",
            "S_H_ion", "S_va_ion", "S_bu_ion", "S_pro_ion", "S_ac_ion", "S_hco3_ion",
            "S_co2", "S_nh3", "S_nh4_ion", "S_gas_h2", "S_gas_ch4", "S_gas_co2",
        ]
        for i, name in enumerate(names):
            ns[name] = sim[i][-1]
        dae()
        # Official algebraic splits after DAESolve (S_co2, S_nh4_ion).
        ns["S_nh4_ion"] = ns["S_IN"] - ns["S_nh3"]
        ns["S_co2"] = ns["S_IC"] - ns["S_hco3_ion"]
        # Official script feeds the DAE-corrected state into the next step.
        # Without this, every 0.25 d interval restarts from the initial state.
        ns["state_zero"] = [ns[name] for name in names]
        t0 = float(u)

    # Algebraic gas law (same as official lines after DAESolve).
    s_h2 = float(ns["S_gas_h2"])
    s_ch4 = float(ns["S_gas_ch4"])
    s_co2 = float(ns["S_gas_co2"])
    p_h2 = s_h2 * R_BAR * T_OP / COD_H2
    p_ch4 = s_ch4 * R_BAR * T_OP / COD_CH4
    p_co2 = s_co2 * R_BAR * T_OP
    p_h2o = float(ns.get("p_gas_h2o", P_GAS_H2O))
    p_gas = p_h2 + p_ch4 + p_co2 + p_h2o
    k_p = float(ns["k_p"])
    q_head = k_p * (p_gas - P_ATM)
    if q_head < 0:
        q_head = 0.0
    q_atm = q_head * p_gas / P_ATM

    pred = {
        "S_su": float(ns["S_su"]), "S_aa": float(ns["S_aa"]), "S_fa": float(ns["S_fa"]),
        "S_va": float(ns["S_va"]), "S_bu": float(ns["S_bu"]), "S_pro": float(ns["S_pro"]),
        "S_ac": float(ns["S_ac"]), "S_h2": float(ns["S_h2"]), "S_ch4": float(ns["S_ch4"]),
        "S_IC": float(ns["S_IC"]), "S_IN": float(ns["S_IN"]), "S_I": float(ns["S_I"]),
        "X_c": float(ns["X_xc"]), "X_ch": float(ns["X_ch"]), "X_pr": float(ns["X_pr"]),
        "X_li": float(ns["X_li"]), "X_su": float(ns["X_su"]), "X_aa": float(ns["X_aa"]),
        "X_fa": float(ns["X_fa"]), "X_c4": float(ns["X_c4"]), "X_pro": float(ns["X_pro"]),
        "X_ac": float(ns["X_ac"]), "X_h2": float(ns["X_h2"]), "X_I": float(ns["X_I"]),
        "S_cat": float(ns["S_cation"]), "S_an": float(ns["S_anion"]),
        "Qad": float(q_m3_d), "Top": 35.0,
        "pH": float(ns["pH"]), "SH+": float(ns["S_H_ion"]),
        "S_va-": float(ns["S_va_ion"]), "S_bu-": float(ns["S_bu_ion"]),
        "S_pro-": float(ns["S_pro_ion"]), "S_ac-": float(ns["S_ac_ion"]),
        "S_hco3-": float(ns["S_hco3_ion"]), "S_co2": float(ns["S_co2"]),
        "S_nh3": float(ns["S_nh3"]), "S_nh4+": float(ns["S_nh4_ion"]),
        "Sgas_h2": s_h2, "Sgas_ch4": s_ch4, "Sgas_co2": s_co2,
        "pgas_h2": p_h2, "pgas_ch4": p_ch4, "pgas_co2": p_co2, "Pgas": p_gas,
        "Qgas": q_atm,
        "_q_gas_headspace": q_head,
        "_pgas_h2o": p_h2o,
        "_step_d": step_d,
        "_t_days": t_days,
        "_solver": "DOP853+DAESolve",
        "_append_shim": ns["_append_shim"],
        "_pyadm1_path": str(Path(pyadm1_path).resolve()),
        "_commit": COMMIT,
        "_q_ad_override": float(q_m3_d),
        "_conversions": {
            "Qgas": "k_p*(Pgas-Patm) * Pgas/Patm; Table 6 is atmospheric",
            "pgas_h2": "Sgas_h2 * R * T / 16",
            "pgas_ch4": "Sgas_ch4 * R * T / 64",
            "pgas_co2": "Sgas_co2 * R * T",
        },
    }
    return pred
