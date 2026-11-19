"""One BSM2 ADM1 steady-state comparison: liquid effluent S_ch4.

The published value is Rosen & Jeppsson (2006) section 7, state 9:
Sch4 = 0.0550887764460 kg COD/m3.
https://iwa-mia.org/wp-content/uploads/2019/04/bmadm1_report061127.pdf

Same liquid iconc basis already used for acetate in sim/models/adm1_cstr.py:
0.1976297 kg COD/m3 was treated as 197.63 mg COD/L, so the factor is 1000.
This is the BSM2 benchmark case (Q=170 m3/d, 35 C, HRT 20 d). It is not a
yard-waste feed, not a DIY leach-bed prediction, and not a pass/fail gate.

exposan default_init_conds uses S_ch4 = 0.0555 kg COD/m3 (55.5 mg COD/L).
That is an initial condition, the same class of mistake as acetate 89.3.
It is not the benchmark.

Gas-phase Sgas,ch4 (1.6256072099814 kg COD/m3) and biogas CH4_kgCOD_d are
different quantities and are not read here. S_IC and pH are not compared.
"""
from decimal import Decimal

PUBLISHED_SCH4_KG_COD_M3 = Decimal("0.0550887764460")
MG_L_PER_KG_M3 = Decimal("1000")
_MG_L_QUANTUM = Decimal("0.0000000001")
PUBLISHED_SCH4_MG_COD_L = (PUBLISHED_SCH4_KG_COD_M3 * MG_L_PER_KG_M3).quantize(_MG_L_QUANTUM)
EXPOSAN_DEFAULT_INIT_SCH4_MG_COD_L = Decimal("55.5")
PUBLISHED_SAC_KG_COD_M3 = Decimal("0.1976297169375")
PUBLISHED_SAC_MG_COD_L = (PUBLISHED_SAC_KG_COD_M3 * MG_L_PER_KG_M3).quantize(_MG_L_QUANTUM)

POINT_Q_M3_D = 170
POINT_T_C = 35
POINT_T_DAYS = 200
SIMULATE_METHOD = "BDF"
T_EVAL_STEP_D = 5
STATE_RESET_HOOK = "reset_cache"
BENCHMARK_HRT_D = Decimal("20")
BENCHMARK_T_K = Decimal("308.15")


def _dec_str(value):
    return format(Decimal(value), "f")


def assert_point(Q, T_C, t_days):
    """Reject every operating point except the section 7 benchmark case."""
    if type(Q) is not int or Q != POINT_Q_M3_D:
        raise ValueError("this stage accepts only Q=170 (int); other flows are not the benchmark")
    if type(T_C) is not int or T_C != POINT_T_C:
        raise ValueError("this stage accepts only T_C=35 (int)")
    if type(t_days) is not int or t_days != POINT_T_DAYS:
        raise ValueError("this stage accepts only t_days=200 (int), the documented acetate-check duration")


def assert_benchmark_identity(hrt_d, temperature_K):
    """Stop if the constructed reactor is not the 20 d / 35 C benchmark case.

    The 1e-9 band is binary representation noise on 20 and 308.15, not a
    scientific acceptance tolerance for S_ch4.
    """
    hrt = Decimal(str(hrt_d))
    temp = Decimal(str(temperature_K))
    if abs(hrt - BENCHMARK_HRT_D) > Decimal("1e-9"):
        raise RuntimeError(
            f"HRT {hrt_d} d is not the section 7 retention time of 20 d; "
            "refusing to compare S_ch4"
        )
    if abs(temp - BENCHMARK_T_K) > Decimal("1e-9"):
        raise RuntimeError(
            f"reactor temperature {temperature_K} K is not 308.15 K; "
            "refusing to compare S_ch4"
        )


def _catalog_ids(indexer):
    """Chemical IDs attached to a thermosteam indexer, if it has a catalog."""
    chemicals = getattr(indexer, "chemicals", None)
    if chemicals is None:
        chemicals = getattr(indexer, "_chemicals", None)
    if chemicals is None:
        return None
    return getattr(chemicals, "IDs", None)


def _has_component(indexer, component_id):
    """Whether a liquid component can be read by its string ID.

    thermosteam.ChemicalIndexer does not implement membership. ``component_id
    in indexer`` iterates with __getitem__(0) and raises TypeError: only
    strings, sequences of strings, and ellipsis are valid index keys.
    CompiledChemicals.IDs is the catalog. A mapping fixture may define
    __contains__ itself. This never uses an integer index.
    """
    if not isinstance(component_id, str):
        raise RuntimeError(f"component id must be a string, not {component_id!r}")
    ids = _catalog_ids(indexer)
    if ids is not None:
        return component_id in ids
    if getattr(type(indexer), "__contains__", None) is not None:
        return component_id in indexer
    raise RuntimeError(
        f"{type(indexer).__name__} has no chemical catalog; "
        f"refusing to test {component_id!r} by membership or an integer index"
    )


def _read_component(indexer, component_id):
    """String-key read. A missing catalog entry is a hard stop, not a zero."""
    if not _has_component(indexer, component_id):
        raise RuntimeError(
            f"liquid effluent catalog has no {component_id}; "
            "not substituting biogas mass flow, Sgas,ch4, S_IC, or pH"
        )
    try:
        return indexer[component_id]
    except TypeError as exc:
        raise RuntimeError(
            f"effluent iconc rejected string key {component_id!r}: {exc}"
        ) from exc


def liquid_outlets(unit):
    """Return (biogas, effluent) using the outlet order already used by adm1_cstr.py.

    S_ch4 is then read only from the effluent iconc by string key. A missing
    component or a biogas/effluent mix-up is a hard stop, not a fallback to
    biogas mass flow or to the gas-phase table row.
    """
    outs = getattr(unit, "outs", None)
    if outs is None or len(outs) != 2:
        raise RuntimeError("AnaerobicCSTR did not expose exactly two outlets; refusing to guess S_ch4")
    biogas, effluent = outs[0], outs[1]
    if effluent is biogas:
        raise RuntimeError("effluent outlet is the biogas outlet; refusing to read S_ch4")
    biogas_id = getattr(biogas, "ID", None)
    effluent_id = getattr(effluent, "ID", None)
    if biogas_id is not None and effluent_id == biogas_id:
        raise RuntimeError(f"refusing to read S_ch4 from biogas stream {effluent_id!r}")
    iconc = getattr(effluent, "iconc", None)
    if iconc is None:
        raise RuntimeError("liquid effluent has no iconc; refusing to guess S_ch4")
    _read_component(iconc, "S_ch4")
    _read_component(iconc, "S_ac")
    return biogas, effluent, {"biogas_id": biogas_id, "effluent_id": effluent_id}


def compare_liquid_sch4(simulated_mg_cod_l):
    """Difference against the published liquid concentration. No pass/fail threshold."""
    simulated = Decimal(str(simulated_mg_cod_l))
    diff = simulated - PUBLISHED_SCH4_MG_COD_L
    result = {
        "variable": "S_ch4",
        "phase": "liquid_effluent",
        "stream": "effluent",
        "accessor": "eff.iconc['S_ch4']",
        "simulated_mg_COD_L": _dec_str(simulated),
        "published_kg_COD_m3": _dec_str(PUBLISHED_SCH4_KG_COD_M3),
        "published_mg_COD_L": _dec_str(PUBLISHED_SCH4_MG_COD_L),
        "unit_factor_mg_L_per_kg_m3": "1000",
        "signed_diff_mg_COD_L": _dec_str(diff),
        "abs_diff_mg_COD_L": _dec_str(abs(diff)),
        "rel_diff": _dec_str(diff / PUBLISHED_SCH4_MG_COD_L),
        "citation": "Rosen & Jeppsson 2006, section 7, state 9 Sch4",
        "status": "run, not validated",
        "pass_fail": None,
    }
    if abs(simulated - EXPOSAN_DEFAULT_INIT_SCH4_MG_COD_L) < Decimal("0.000001"):
        result["init_condition_warning"] = (
            "simulated S_ch4 equals exposan default_init_conds S_ch4 "
            "(0.0555 kg COD/m3 = 55.5 mg COD/L). That initial condition is not "
            "the section 7 benchmark, the same class of mistake as acetate 89.3."
        )
    return result


def identity_echo_sac(simulated_mg_cod_l):
    """Acetate is already compared. Record it only to identify the integration."""
    simulated = Decimal(str(simulated_mg_cod_l))
    return {
        "role": "identity_echo_not_a_new_comparison",
        "variable": "S_ac",
        "accessor": "eff.iconc['S_ac']",
        "simulated_mg_COD_L": _dec_str(simulated),
        "published_kg_COD_m3": _dec_str(PUBLISHED_SAC_KG_COD_M3),
        "published_mg_COD_L": _dec_str(PUBLISHED_SAC_MG_COD_L),
        "note": (
            "Already compared in issue #3 and baseline221. "
            "baseline221 Q=170 recorded S_ac_eff_mg_L 198.65 after two-decimal rounding. "
            "This echo is not the stage result."
        ),
    }


def run(Q=170, T_C=35, t_days=200):
    """Integrate the packaged BSM2 ADM1 case and compare liquid S_ch4.

    Imports exposan only after the point guard, so a rejected point does not
    require QSDsan. The numerical settings match sim/models/adm1_cstr.py.
    """
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
        raise RuntimeError("reactor did not expose T; refusing to compare S_ch4")
    assert_benchmark_identity(hrt, temperature_K)
    # Reject a non-readable indexer before the 200-day integration.
    liquid_outlets(unit)
    system.simulate(
        state_reset_hook=STATE_RESET_HOOK,
        t_span=(0, t_days),
        t_eval=np.arange(0, t_days + T_EVAL_STEP_D, T_EVAL_STEP_D),
        method=SIMULATE_METHOD,
    )
    _biogas, effluent, ids = liquid_outlets(unit)
    comparison = compare_liquid_sch4(effluent.iconc["S_ch4"])
    return {
        "comparison": comparison,
        "identity_echo": identity_echo_sac(effluent.iconc["S_ac"]),
        "HRT_d": _dec_str(Decimal(str(hrt))),
        "T_K": _dec_str(Decimal(str(temperature_K))),
        "outlets": ids,
        "method": SIMULATE_METHOD,
        "t_days": t_days,
        "t_eval_step_d": T_EVAL_STEP_D,
        "state_reset_hook": STATE_RESET_HOOK,
        "Q_m3_d": Q,
        "T_C": T_C,
        "status": "run, not validated",
    }
