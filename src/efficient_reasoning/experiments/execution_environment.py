from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .readiness import FROZEN_DOCKER_IMAGE, FROZEN_PLATFORM, validate_frozen_exp001_config, validate_frozen_manifest, validate_materialized_benchmark, git_state


def _run_capture(command: list[str], cwd: Path) -> tuple[bool, str]:
    try:
        proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip()[:500]
    return True, proc.stdout.strip()


def check_docker(cfg: dict[str, Any], root: Path) -> list[str]:
    failures: list[str] = []
    if shutil.which("docker") is None:
        return ["Docker CLI is missing"]
    ok, detail = _run_capture(["docker", "info", "--format", "{{.ServerVersion}}"], root)
    if not ok:
        failures.append("Docker daemon is unreachable")
    elif not detail:
        failures.append("Docker daemon returned no server information")
    image = str(cfg["execution"].get("image", ""))
    if image != FROZEN_DOCKER_IMAGE:
        failures.append("Docker image is not the frozen immutable EXP-001 image")
    platform = cfg["execution"].get("platform")
    if platform != FROZEN_PLATFORM:
        failures.append("Docker platform is not linux/amd64")
    if cfg["execution"].get("network") != "none":
        failures.append("Docker network policy must be none")
    if cfg["execution"].get("sandbox_policy") != "docker_strict_v1":
        failures.append("Sandbox policy must be docker_strict_v1")
    for key in ("memory_mb", "cpus", "pid_limit", "timeout_seconds"):
        if key not in cfg["execution"]:
            failures.append(f"Docker sandbox constraint missing: execution.{key}")
    return failures


def check_model_access(cfg: dict[str, Any], models_cfg: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not cfg.get("runner", {}).get("require_real_models"):
        failures.append("EXP-001 does not require real models")
    for name in cfg.get("models", []):
        spec = models_cfg.get("models", {}).get(name, {})
        if spec.get("adapter") == "mock" or spec.get("provider") == "mock":
            failures.append(f"Mock model configuration is not allowed: {name}")
    if not os.getenv("OPENAI_API_KEY"):
        failures.append("OPENAI_API_KEY is missing")
    return failures


def collect_execution_environment_failures(root: Path, cfg: dict[str, Any], models_cfg: dict[str, Any], benchmarks_cfg: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    report: dict[str, Any] = {}

    try:
        validate_frozen_exp001_config(cfg, models_cfg, benchmarks_cfg)
        report["configuration"] = "valid"
    except Exception as exc:
        failures.append(f"configuration: {exc}")
        report["configuration"] = "invalid"

    try:
        manifest = validate_frozen_manifest(root / cfg["benchmark"]["manifest_path"])
        validate_materialized_benchmark(manifest, root / cfg["benchmark"]["tasks_path"])
        report["benchmark"] = "materialized_and_integrity_checked"
    except Exception as exc:
        failures.append(f"benchmark: {exc}")
        report["benchmark"] = "not_ready"

    failures.extend(check_docker(cfg, root))
    report["docker_cli"] = shutil.which("docker") is not None
    report["docker_daemon"] = "unknown" if not report["docker_cli"] else "checked_without_exposing_details"

    model_failures = check_model_access(cfg, models_cfg)
    failures.extend(model_failures)
    report["openai_api_key_present"] = bool(os.getenv("OPENAI_API_KEY"))

    sha, dirty, branch = git_state(root)
    report["git_sha"] = sha
    report["git_branch"] = branch
    report["git_worktree_clean"] = not dirty
    if sha is None:
        failures.append("git: repository SHA could not be determined")
    if dirty:
        failures.append("git: working tree is dirty; commit the audited state before real execution")

    if cfg.get("runner", {}).get("allow_mock") is not False:
        failures.append("runner.allow_mock must be false for EXP-001")
    if cfg.get("runner", {}).get("require_materialized_benchmark") is not True:
        failures.append("runner.require_materialized_benchmark must be true")

    return failures, report
