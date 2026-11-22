"""No-publish runner for the single liquid S_ch4 benchmark comparison.

Row-level resume and dedup only. The ODE solver state is not checkpointed:
an abandoned run is integrated again. A finished row with the same dedup key
is not integrated again. This process does not call git, gh, ssh, or ai-job.
"""
import csv
import fcntl
import hashlib
import json
import os
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

STAGE_ID = "adm1-liquid-sch4-benchmark-20261108"
SOURCE_COMMIT = "acb83b818a716f974c05665f897ff60713e5850e"
REQUIRED_PYTHON = os.environ.get("YWSIM_PYTHON") or shutil.which("python3") or sys.executable
DEFAULT_RESULT_DIR_NAME = "results/adm1-liquid-sch4"
DONE_STATUS = "run, not validated"
BUSY_EXIT = 75

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "adm1_sch4_benchmark.py"


class ConfigError(Exception):
    pass


class Busy(Exception):
    pass


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def dedup_key(model_sha, runner_sha):
    payload = {
        "stage_id": STAGE_ID,
        "source_commit": SOURCE_COMMIT,
        "Q_m3_d": 170,
        "T_C": 35,
        "t_days": 200,
        "method": "BDF",
        "t_eval_step_d": 5,
        "state_reset_hook": "reset_cache",
        "variable": "S_ch4",
        "phase": "liquid_effluent",
        "published_kg_COD_m3": "0.0550887764460",
        "model_sha256": model_sha,
        "runner_sha256": runner_sha,
    }
    return hashlib.sha256(canonical(payload).encode()).hexdigest()


def load_config(path):
    with open(path) as handle:
        cfg = json.load(handle)
    if not isinstance(cfg, dict):
        raise ConfigError("config must be an object")
    if "grid" in cfg:
        raise ConfigError("refusing a sweep grid; this stage is one benchmark point")
    expected = {
        "stage_id": STAGE_ID,
        "model": "adm1_sch4_benchmark",
        "source_commit": SOURCE_COMMIT,
        "max_runs": 1,
        "publish": False,
    }
    for key, value in expected.items():
        if cfg.get(key) != value:
            raise ConfigError(f"config {key} must be {value!r}")
    point = cfg.get("point")
    if point != {
        "Q_m3_d": 170,
        "T_C": 35,
        "t_days": 200,
        "method": "BDF",
        "t_eval_step_d": 5,
        "state_reset_hook": "reset_cache",
    }:
        raise ConfigError("config point is not the single section 7 benchmark case")
    benchmark = cfg.get("benchmark")
    if not isinstance(benchmark, dict):
        raise ConfigError("config benchmark must be an object")
    for key, value in {
        "variable": "S_ch4",
        "phase": "liquid_effluent",
        "published_value": "0.0550887764460",
        "published_unit": "kg COD/m3",
        "comparison_unit": "mg COD/L",
        "unit_factor_mg_L_per_kg_m3": 1000,
    }.items():
        if benchmark.get(key) != value:
            raise ConfigError(f"config benchmark.{key} does not match the published Sch4 row")
    echo = cfg.get("identity_echo")
    if not isinstance(echo, dict) or echo.get("role") != "identity_echo_not_a_new_comparison":
        raise ConfigError("identity echo must be labelled as not a new comparison")
    if echo.get("variable") != "S_ac":
        raise ConfigError("identity echo variable must stay S_ac")
    model_sha = sha256_file(MODEL_PATH)
    if cfg.get("model_sha256") != model_sha:
        raise ConfigError("config model_sha256 does not match src/adm1_sch4_benchmark.py")
    allowed = {
        "stage_id", "model", "source_commit", "max_runs", "publish", "point",
        "benchmark", "identity_echo", "model_sha256", "default_output_dir",
        "citation", "not_compared", "notes",
    }
    unknown = set(cfg) - allowed
    if unknown:
        raise ConfigError(f"refusing unknown config keys {sorted(unknown)}")
    if cfg.get("default_output_dir") != DEFAULT_RESULT_DIR_NAME:
        raise ConfigError("default output directory does not match the dated stage path")
    return cfg


def assert_safe_result_dir(result_dir, stage_dir):
    path = Path(result_dir)
    if not path.is_absolute():
        raise ConfigError("result directory must be absolute")
    path = path.resolve()
    stage_dir = Path(stage_dir).resolve()
    if path == stage_dir or stage_dir in path.parents or path in stage_dir.parents:
        raise ConfigError("result directory must be outside the stage source directory")
    parts = path.parts
    for index in range(len(parts) - 1):
        if parts[index] == "sim" and parts[index + 1] == "results":
            raise ConfigError("refusing to write sim/results")
    for parent in (path, *path.parents):
        if (parent / ".git").exists():
            raise ConfigError(f"refusing to write results inside git work tree {parent}")
    return path


def cap_resources(cpu_id):
    """Pin this process to one CPU and absolute nice 19."""
    cpu_id = int(cpu_id)
    if cpu_id < 0:
        raise ConfigError("YWSIM_CPU must be >= 0")
    try:
        os.sched_setaffinity(0, {cpu_id})
        os.setpriority(os.PRIO_PROCESS, 0, 19)
    except OSError as exc:
        raise ConfigError(f"cannot hold 1 CPU nice 19 on cpu {cpu_id}: {exc}") from exc
    nice = os.getpriority(os.PRIO_PROCESS, 0)
    affinity = sorted(os.sched_getaffinity(0))
    if nice < 19 or affinity != [cpu_id]:
        raise ConfigError(f"resource cap not held: nice={nice} affinity={affinity}")
    return {"nice": nice, "affinity": affinity, "cpu_count": 1}


class RunLock:
    def __init__(self, path):
        self.path = Path(path)
        self.handle = None

    def acquire(self, run_id):
        self.handle = open(self.path, "a+")
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self.handle.close()
            self.handle = None
            raise Busy("another S_ch4 run holds the lock") from exc
        self.handle.seek(0)
        self.handle.truncate()
        self.handle.write(
            f"pid={os.getpid()}\nrun_id={run_id}\n"
            f"utc={datetime.now(timezone.utc).isoformat()}\n"
        )
        self.handle.flush()
        os.fsync(self.handle.fileno())

    def release(self):
        if self.handle is not None:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close()
            self.handle = None


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic_write(path, text):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    with os.fdopen(fd, "w") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def append_log(log_path, row):
    log_path = Path(log_path)
    new = not log_path.exists()
    with open(log_path, "a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "utc", "run_id", "dedup_key", "action", "params", "outputs", "status", "exit_code",
        ])
        if new:
            writer.writeheader()
        writer.writerow(row)
        handle.flush()
        os.fsync(handle.fileno())


def _matching_records(result_dir, key):
    found = []
    log_path = result_dir / "log.csv"
    if log_path.exists():
        with open(log_path, newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("dedup_key") == key:
                    found.append(("log", row))
    runs = result_dir / "runs"
    if runs.is_dir():
        for path in sorted(runs.glob("*.json")):
            with open(path) as handle:
                record = json.load(handle)
            if record.get("dedup_key") == key:
                found.append(("json", record))
    return found


def completed_output(result_dir, key):
    for kind, record in _matching_records(result_dir, key):
        if kind == "json" and record.get("status") == DONE_STATUS and record.get("outputs"):
            return record
        if kind == "log" and record.get("status") == DONE_STATUS and record.get("outputs"):
            return {
                "run_id": record["run_id"],
                "outputs": json.loads(record["outputs"]),
                "status": DONE_STATUS,
                "from_log": True,
            }
    return None


def execute(config_path, result_dir, *, model_run=None, apply_caps=True, cpu_id=0, stage_dir=None):
    stage_dir = Path(stage_dir or HERE.parent)
    cfg = load_config(config_path)
    result_dir = assert_safe_result_dir(result_dir, stage_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    model_sha = sha256_file(MODEL_PATH)
    runner_sha = sha256_file(HERE / "run_once.py")
    key = dedup_key(model_sha, runner_sha)
    run_id = str(uuid.uuid4())
    caps = cap_resources(cpu_id) if apply_caps else {"nice": None, "affinity": None, "cpu_count": None, "applied": False}
    if apply_caps:
        caps["applied"] = True
    lock = RunLock(result_dir / "LOCK")
    try:
        lock.acquire(run_id)
    except Busy:
        receipt = {
            "action": "busy", "exit_code": BUSY_EXIT, "run_id": run_id,
            "dedup_key": key, "result_dir": str(result_dir),
        }
        print(canonical(receipt), flush=True)
        return BUSY_EXIT
    try:
        prior = completed_output(result_dir, key)
        if prior is not None:
            if not _log_has_completed(result_dir, key):
                append_log(result_dir / "log.csv", {
                    "utc": _utc_now(),
                    "run_id": prior.get("run_id", run_id),
                    "dedup_key": key,
                    "action": "dedup_repair",
                    "params": canonical(cfg["point"]),
                    "outputs": json.dumps(prior["outputs"], sort_keys=True),
                    "status": DONE_STATUS,
                    "exit_code": 0,
                })
            receipt = {
                "action": "dedup_skip",
                "exit_code": 0,
                "run_id": prior.get("run_id", run_id),
                "dedup_key": key,
                "result_dir": str(result_dir),
                "status": DONE_STATUS,
            }
            atomic_write(result_dir / "latest.json", json.dumps(receipt, indent=2, sort_keys=True) + "\n")
            print(canonical(receipt), flush=True)
            return 0
        _abandon_stale(result_dir, key)
        params = cfg["point"]
        record = {
            "action": "running",
            "run_id": run_id,
            "dedup_key": key,
            "pid": os.getpid(),
            "parent_pid": os.getppid(),
            "utc_start": _utc_now(),
            "source_commit": SOURCE_COMMIT,
            "model_sha256": model_sha,
            "runner_sha256": runner_sha,
            "config_sha256": sha256_file(config_path),
            "python": sys.executable,
            "caps": caps,
            "params": params,
            "status": "running",
            "stage_id": STAGE_ID,
        }
        runs = result_dir / "runs"
        runs.mkdir(exist_ok=True)
        record_path = runs / f"{run_id}.json"
        atomic_write(record_path, json.dumps(record, indent=2, sort_keys=True) + "\n")
        try:
            if model_run is None:
                assert_integration_allowed()
                sys.path.insert(0, str(HERE))
                from adm1_sch4_benchmark import run as model_run
            outputs = model_run(Q=params["Q_m3_d"], T_C=params["T_C"], t_days=params["t_days"])
        except Exception as exc:
            record.update({
                "action": "failed",
                "status": "failed",
                "utc_end": _utc_now(),
                "error": repr(exc)[:500],
                "exit_code": 1,
            })
            atomic_write(record_path, json.dumps(record, indent=2, sort_keys=True) + "\n")
            append_log(result_dir / "log.csv", {
                "utc": record["utc_end"],
                "run_id": run_id,
                "dedup_key": key,
                "action": "failed",
                "params": canonical(params),
                "outputs": json.dumps({"error": record["error"]}),
                "status": "failed",
                "exit_code": 1,
            })
            print(canonical({"action": "failed", "exit_code": 1, "run_id": run_id, "error": record["error"]}), flush=True)
            return 1
        record.update({
            "action": "completed",
            "status": DONE_STATUS,
            "utc_end": _utc_now(),
            "outputs": outputs,
            "exit_code": 0,
        })
        atomic_write(record_path, json.dumps(record, indent=2, sort_keys=True) + "\n")
        append_log(result_dir / "log.csv", {
            "utc": record["utc_end"],
            "run_id": run_id,
            "dedup_key": key,
            "action": "completed",
            "params": canonical(params),
            "outputs": json.dumps(outputs, sort_keys=True),
            "status": DONE_STATUS,
            "exit_code": 0,
        })
        atomic_write(result_dir / "latest.json", json.dumps(record, indent=2, sort_keys=True) + "\n")
        print(canonical({"action": "completed", "exit_code": 0, "run_id": run_id, "dedup_key": key, "status": DONE_STATUS}), flush=True)
        return 0
    finally:
        lock.release()


def _log_has_completed(result_dir, key):
    log_path = result_dir / "log.csv"
    if not log_path.exists():
        return False
    with open(log_path, newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("dedup_key") == key and row.get("status") == DONE_STATUS:
                return True
    return False


def _abandon_stale(result_dir, key):
    runs = result_dir / "runs"
    if not runs.is_dir():
        return
    for path in runs.glob("*.json"):
        with open(path) as handle:
            record = json.load(handle)
        if record.get("dedup_key") == key and record.get("status") == "running":
            record["status"] = "abandoned"
            record["action"] = "abandoned"
            record["abandoned_utc"] = _utc_now()
            atomic_write(path, json.dumps(record, indent=2, sort_keys=True) + "\n")


def assert_runtime_python():
    if os.environ.get("YWSIM_REQUIRE_RUNTIME") != "1":
        return
    if os.path.realpath(sys.executable) != os.path.realpath(REQUIRED_PYTHON):
        raise ConfigError(
            f"refusing {sys.executable}; runtime python is {REQUIRED_PYTHON}"
        )


def assert_integration_allowed():
    """Unit tests must never start the 200-day integration.

    The public launcher sets YWSIM_ALLOW_INTEGRATION=1. The unit-test
    process, and any subprocess it starts, leave that variable unset.
    """
    if os.environ.get("YWSIM_ALLOW_INTEGRATION") != "1":
        raise ConfigError(
            "refusing the 200-day integration unless YWSIM_ALLOW_INTEGRATION=1"
        )


def cli(argv):
    try:
        assert_runtime_python()
        assert_integration_allowed()
        if len(argv) != 2:
            raise ConfigError("usage: run_once.py CONFIG.json")
        result_dir = os.environ.get("YWSIM_RESULT_DIR")
        if not result_dir:
            raise ConfigError("set YWSIM_RESULT_DIR to an absolute path outside this git checkout")
        cpu_raw = os.environ.get("YWSIM_CPU", "0")
        if not cpu_raw.isdigit():
            raise ConfigError("YWSIM_CPU must be a single non-negative integer")
        return execute(argv[1], result_dir, cpu_id=int(cpu_raw))
    except (ConfigError, ValueError) as exc:
        print(canonical({"action": "rejected", "exit_code": 2, "error": str(exc)}), flush=True)
        return 2


if __name__ == "__main__":
    sys.exit(cli(sys.argv))
