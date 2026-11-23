"""IAPWS-IF97 Region 4 saturation pressure (IAPWS R7-97(2012) Eqs. 29-31).

Coefficients are the published Table 34 values, copied into
PRE-REGISTERED-BAND-Q05B.md before any 30/35 C closeness verdict was recorded.
"""
from __future__ import annotations

import math

# IAPWS R7-97(2012) Table 34
N = (
    0.11670521452767e4,
    -0.72421316703206e6,
    -0.17073846940092e2,
    0.12020824702470e5,
    -0.32325550322333e7,
    0.14915108613530e2,
    -0.48232657361591e4,
    0.40511340542057e6,
    -0.23855557567849,
    0.65017534844798e3,
)
T_C_K = 647.096
P_C_MPA = 22.064
P_STAR_MPA = 1.0


def psat_mpa(t_k: float) -> float:
    """Saturation pressure in MPa at temperature T in kelvin."""
    t = float(t_k)
    n1, n2, n3, n4, n5, n6, n7, n8, n9, n10 = N
    theta = t + n9 / (t - n10)
    a = theta * theta + n1 * theta + n2
    b = n3 * theta * theta + n4 * theta + n5
    c = n6 * theta * theta + n7 * theta + n8
    disc = b * b - 4.0 * a * c
    if disc < 0:
        raise ValueError("IAPWS-IF97 region-4 discriminant is negative")
    p_over_pstar = (2.0 * c / (-b + math.sqrt(disc))) ** 4
    return p_over_pstar * P_STAR_MPA


def psat_bar(t_k: float) -> float:
    """Saturation pressure in bar (1 MPa = 10 bar)."""
    return psat_mpa(t_k) * 10.0


def rosen_psat_bar(t_k: float) -> float:
    """Rosen / Jeppsson / official PyADM1 / jADM1_BSM water-vapor pressure, bar."""
    t = float(t_k)
    return 0.0313 * math.exp(5290.0 * ((1.0 / 298.15) - (1.0 / t)))
