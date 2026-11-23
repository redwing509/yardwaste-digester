"""jADM1_BSM runner for a Q-05b packaged-influent point.

Does not edit the jADM1_BSM source tree. Reuses Q-05 influent scaling.
Integration is refused unless YWSIM_ALLOW_INTEGRATION=1.
"""
from __future__ import annotations

import csv
import os
import re
import subprocess
from pathlib import Path

from adm1_sweep_pyadm1 import INFLUENT_KEYS, load_packaged_influent, scale_influent

DEFAULT_JADM1 = Path(os.environ.get("JADM1_BIN", "/workspace/digester-tools/bin/jadm1-bsm"))
DEFAULT_INITIAL = Path(
    os.environ.get(
        "PYADM1_INITIAL",
        "/workspace/digester-tools/src/PyADM1/src/digester_initial.csv",
    )
)
DEFAULT_JADM1_COMMIT = "dda4fb23b8f645d77737b8fdca1022830773f05b"

# Official PyADM1 digester_initial.csv header (one data row).
PYADM1_INIT_FIELDS = [
    "S_su", "S_aa", "S_fa", "S_va", "S_bu", "S_pro", "S_ac", "S_h2", "S_ch4",
    "S_IC", "S_IN", "S_I", "X_xc", "X_ch", "X_pr", "X_li", "X_su", "X_aa",
    "X_fa", "X_c4", "X_pro", "X_ac", "X_h2", "X_I", "S_cation", "S_anion",
    "S_H_ion", "S_va_ion", "S_bu_ion", "S_pro_ion", "S_ac_ion", "S_hco3_ion",
    "S_co2", "S_nh3", "S_nh4_ion", "S_gas_h2", "S_gas_ch4", "S_gas_co2",
]

# jADM1_BSM 42-state layout (0-based), from BSM2Defaults / StateVariables.
JADM1_INIT_FROM_PYADM1 = [
    "S_su", "S_aa", "S_fa", "S_va", "S_bu", "S_pro", "S_ac", "S_h2", "S_ch4",
    "S_IC", "S_IN", "S_I", "X_xc", "X_ch", "X_pr", "X_li", "X_su", "X_aa",
    "X_fa", "X_c4", "X_pro", "X_ac", "X_h2", "X_I", "S_cation", "S_anion",
    "S_va_ion", "S_bu_ion", "S_pro_ion", "S_ac_ion", "S_hco3_ion", "S_nh3",
    "S_gas_h2", "S_gas_ch4", "S_gas_co2",
]


def _require_allow():
    if os.environ.get("YWSIM_ALLOW_INTEGRATION") != "1":
        raise RuntimeError("refusing jADM1 integration unless YWSIM_ALLOW_INTEGRATION=1")


def load_pyadm1_initial(path=DEFAULT_INITIAL) -> dict:
    path = Path(path)
    with path.open(newline="") as fh:
        rows = list(csv.reader(fh))
    if len(rows) < 2:
        raise ValueError(f"expected header + data in {path}")
    header = [c.strip() for c in rows[0]]
    values = [float(c) for c in rows[1]]
    if header != PYADM1_INIT_FIELDS:
        raise ValueError(f"unexpected digester_initial header: {header}")
    if len(values) != len(header):
        raise ValueError("digester_initial row length mismatch")
    return dict(zip(header, values))


def jadm1_initial_vector(t_c: float, initial=None) -> list:
    """Map official PyADM1 initial state to jADM1's 42-entry vector."""
    initial = initial if initial is not None else load_pyadm1_initial()
    vec = [float(initial[name]) for name in JADM1_INIT_FROM_PYADM1]
    vec.append(0.0)  # 35 Q_D, set by influent
    vec.append(float(t_c))  # 36 T_D, digester temperature in deg C
    vec.extend([0.0, 0.0, 0.0])  # 37-39 q_ch4, q_gas, pH (computed)
    vec.append(float(initial["S_co2"]))  # 40
    vec.append(float(initial["S_nh4_ion"]))  # 41
    if len(vec) != 42:
        raise RuntimeError(f"expected 42 states, got {len(vec)}")
    return vec


def jadm1_influent_vector(feed: str, conc_scale: float, q_m3_d: float, packaged=None) -> list:
    """Packaged + scaled + unit-converted influent as a 42-entry jADM1 vector.

    S_IC / S_IN are already kmol/m3 after scale_influent().
    """
    inf = scale_influent(feed, conc_scale, packaged=packaged)
    vec = []
    for key in INFLUENT_KEYS:
        # INFLUENT_KEYS uses S_cation / S_anion, which scale_influent preserves.
        vec.append(float(inf[key]))
    # 26-34: ions and gas in influent are unused / zero in BSM2Defaults.Influent
    vec.extend([0.0] * 9)
    vec.append(float(q_m3_d))  # 35
    vec.append(0.0)  # 36 T set by digester
    vec.extend([0.0] * 5)  # 37-41
    if len(vec) != 42:
        raise RuntimeError(f"expected 42 influent entries, got {len(vec)}")
    return vec


def write_delimited_row(path: Path, values, delim=";") -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Trailing delimiter is tolerated (empty field after the last value).
    line = delim.join(f"{v:.16g}" for v in values) + delim + "\n"
    path.write_text(line)


def write_semicolon_row(path: Path, values) -> None:
    """jADM1 StateVariables.readVar / default CSVReader split on ';'."""
    write_delimited_row(path, values, delim=";")


def parse_steady_result(text: str) -> list:
    """Parse jADM1 Main.runSteady() text (stdout or steady_result.csv)."""
    effluent = {}
    finish = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("Simulation time"):
            parts = [p.strip() for p in line.split(";")]
            # "...; Finish; 200.0"
            if "Finish" in parts:
                i = parts.index("Finish")
                if i + 1 < len(parts):
                    finish = float(parts[i + 1])
        m = re.match(
            r"State no;\s*(\d+);\s*Influent;\s*([^;]+);\s*Effluent;\s*([^;]+)",
            line,
        )
        if m:
            effluent[int(m.group(1))] = float(m.group(3))
    if len(effluent) < 42:
        raise ValueError(f"expected 42 effluent states, got {len(effluent)}: {sorted(effluent)}")
    vec = [effluent[i] for i in range(1, 43)]
    return {"finish_d": finish, "x": vec}


def parse_dynamic_output(text: str, t_days: float, step_d=None) -> dict:
    """Parse jADM1 Main.runDynamic() dynamic_output.csv (time + 42 states).

    Each row is labelled with the step *start* time and holds the state at
    start + step. A one-line influent file is also read one extra time
    because CSVReader only sets `finished` after the empty read that
    follows the last line, so the official CLI performs a second
    continuation step. The state at t_days is the unique row whose
    label + step equals t_days, not the last row.
    """
    step = float(t_days) if step_d is None else float(step_d)
    end = float(t_days)
    rows = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [p for p in line.split(";") if p != ""]
        if len(parts) < 43:
            raise ValueError(f"expected time + 42 states, got {len(parts)}: {line[:120]}")
        rows.append([float(p) for p in parts[:43]])
    if not rows:
        raise ValueError("dynamic_output.csv is empty")
    chosen = None
    for row in rows:
        if abs(row[0] + step - end) <= 1e-9:
            if chosen is not None:
                raise ValueError(f"multiple rows correspond to t={end}")
            chosen = row
    if chosen is None:
        raise ValueError(
            f"no row with label+step == {end} (step={step}, labels={[r[0] for r in rows]})"
        )
    return {
        "finish_d": chosen[0] + step,
        "x": chosen[1:],
        "n_rows": len(rows),
        "row_label": chosen[0],
        "step_d": step,
        "labels": [r[0] for r in rows],
    }


def metrics_from_x(x) -> dict:
    if len(x) < 40:
        raise ValueError("incomplete state vector")
    s_ac = float(x[6])
    s_ch4 = float(x[8])
    s_gas_ch4 = float(x[33])
    q_head = float(x[38])
    if q_head < 0:
        q_head = 0.0
    return {
        "S_ac_eff_mg_L": s_ac * 1000.0,
        "S_ch4_eff_mg_L": s_ch4 * 1000.0,
        "pH": float(x[39]),
        "CH4_kgCOD_d": q_head * s_gas_ch4,
        "Sgas_ch4": s_gas_ch4,
        "_q_gas_headspace": q_head,
        "Qgas_ch4_m3_d": float(x[37]),
        "T_C": float(x[36]),
    }


def run_jadm1_point(
    feed: str,
    t_c: float,
    q_m3_d: float,
    conc_scale: float,
    t_days: int,
    workdir: Path,
    jadm1_bin=DEFAULT_JADM1,
    initial_csv=DEFAULT_INITIAL,
    packaged=None,
    timeout_s=7200,
):
    _require_allow()
    workdir = Path(workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    init_path = workdir / "initial.csv"
    inf_path = workdir / "influent.csv"
    write_semicolon_row(init_path, jadm1_initial_vector(t_c, initial=load_pyadm1_initial(initial_csv)))
    # jADM1_BSM Main.java sets `steady = true` only *after* runSteady(), so
    # checkArgs() treats `-in` as a dynamic file whenever `-steady` is used
    # (and also when `-steady` is omitted, because runSteady is the default).
    # The official CLI therefore ignores a steady influent file. A one-line
    # comma-separated `-dynamic` influent with `-step` = t_days applies the
    # same influent via Model.setInfluent and integrates with the same DAE
    # model. The CLI also performs a second, unrequested continuation step
    # (see parse_dynamic_output); the official metric is the state at
    # t_days, not the continuation. `-init` is unaffected (it does not
    # test the steady flag). Dynamic `-in` is split on comma, not semicolon.
    write_delimited_row(
        inf_path,
        jadm1_influent_vector(feed, conc_scale, q_m3_d, packaged=packaged),
        delim=",",
    )
    cmd = [
        str(jadm1_bin),
        "-dynamic",
        "-s", "0.0",
        "-f", str(float(t_days)),
        "-step", str(float(t_days)),
        "-init", str(init_path),
        "-in", str(inf_path),
    ]
    env = os.environ.copy()
    env["JAVA_TOOL_OPTIONS"] = env.get("JAVA_TOOL_OPTIONS", "")
    proc = subprocess.run(
        cmd,
        cwd=workdir,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    (workdir / "stdout.txt").write_text(proc.stdout or "")
    (workdir / "stderr.txt").write_text(proc.stderr or "")
    (workdir / "cmd.txt").write_text(" ".join(cmd) + "\n")
    if proc.returncode != 0:
        raise RuntimeError(
            f"jADM1_BSM exited {proc.returncode}: {(proc.stderr or proc.stdout or '')[-2000:]}"
        )
    result_file = workdir / "dynamic_output.csv"
    if not result_file.is_file():
        raise RuntimeError(
            f"jADM1_BSM did not write {result_file}: {(proc.stderr or proc.stdout or '')[-2000:]}"
        )
    parsed = parse_dynamic_output(result_file.read_text(), t_days)
    if parsed["finish_d"] is None or abs(parsed["finish_d"] - float(t_days)) > 1e-6:
        raise RuntimeError(
            f"jADM1 finish time {parsed['finish_d']} != requested {t_days}"
        )
    metrics = metrics_from_x(parsed["x"])
    metrics["status"] = "ok"
    metrics["t_days"] = float(t_days)
    metrics["finish_d"] = parsed["finish_d"]
    metrics["row_label"] = parsed["row_label"]
    metrics["n_output_rows"] = parsed["n_rows"]
    metrics["returncode"] = proc.returncode
    return metrics
