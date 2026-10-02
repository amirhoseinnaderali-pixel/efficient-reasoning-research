from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from ..benchmarks.loader import benchmark_sha256, load_tasks
from ..benchmarks.manifest import validate_manifest_path
from .config import validate_config

FROZEN_EXP001_BENCHMARK = "humaneval-stratified-100-v1"
FROZEN_EXP001_VERSION = "1.0.0"
FROZEN_SEEDS = [42, 43, 44]
FROZEN_MODELS = {
    "primary_openai": {
        "provider": "openai",
        "adapter": "openai_compatible",
        "model_id": "gpt-4.1-mini-2025-04-14",
        "base_url": "https://api.openai.com/v1",
        "api_version": "chat_completions_v1",
        "supports_seed": True,
        "generation_config": {"temperature": 0.2, "top_p": 1.0, "max_tokens": 1200},
    },
    "secondary_openai": {
        "provider": "openai",
        "adapter": "openai_compatible",
        "model_id": "gpt-4.1-2025-04-14",
        "base_url": "https://api.openai.com/v1",
        "api_version": "chat_completions_v1",
        "supports_seed": True,
        "generation_config": {"temperature": 0.2, "top_p": 1.0, "max_tokens": 1200},
    },
}
FROZEN_DOCKER_IMAGE = "python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e"
FROZEN_PLATFORM = "linux/amd64"
FROZEN_SANDBOX_POLICY = "docker_strict_v1"
_FROZEN_DIGEST_RE = re.compile(r"^.+@sha256:[0-9a-f]{64}$")


def _same_generation(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    return actual == expected


def validate_frozen_exp001_config(cfg: dict[str, Any], models_cfg: dict[str, Any], benchmarks_cfg: dict[str, Any]) -> None:
    validate_config(cfg, models_cfg, benchmarks_cfg)
    if cfg.get("runner", {}).get("experiment_id") != "EXP-001":
        raise ValueError("readiness gate requires EXP-001")
    if cfg["project"].get("seeds") != FROZEN_SEEDS:
        raise ValueError(f"EXP-001 seeds must remain exactly {FROZEN_SEEDS}")
    if cfg["benchmark"].get("name") != FROZEN_EXP001_BENCHMARK:
        raise ValueError("EXP-001 benchmark identity changed")
    if str(benchmarks_cfg["benchmarks"][FROZEN_EXP001_BENCHMARK]["version"]) != FROZEN_EXP001_VERSION:
        raise ValueError("EXP-001 benchmark version changed")
    if cfg["benchmark"].get("manifest_path") != benchmarks_cfg["benchmarks"][FROZEN_EXP001_BENCHMARK]["manifest"]:
        raise ValueError("EXP-001 manifest path is not the frozen manifest")
    if cfg["benchmark"].get("tasks_path") != benchmarks_cfg["benchmarks"][FROZEN_EXP001_BENCHMARK]["path"]:
        raise ValueError("EXP-001 materialized benchmark path changed")
    if cfg.get("models") != list(FROZEN_MODELS):
        raise ValueError("EXP-001 top-level model list changed")
    if cfg["execution"].get("image") != FROZEN_DOCKER_IMAGE:
        raise ValueError("EXP-001 Docker image digest/configuration changed")
    if cfg["execution"].get("platform") != FROZEN_PLATFORM:
        raise ValueError("EXP-001 Docker platform changed")
    if cfg["execution"].get("network") != "none":
        raise ValueError("EXP-001 Docker network policy changed")
    if cfg["execution"].get("sandbox_policy") != FROZEN_SANDBOX_POLICY:
        raise ValueError("EXP-001 sandbox policy changed")

    for name, expected in FROZEN_MODELS.items():
        actual = models_cfg.get("models", {}).get(name)
        if actual is None:
            raise ValueError(f"Frozen model configuration missing: {name}")
        for key in ("provider", "adapter", "model_id", "base_url", "api_version", "supports_seed"):
            if actual.get(key) != expected[key]:
                raise ValueError(f"Frozen model field changed: {name}.{key}")
        if not _same_generation(actual.get("generation_config", {}), expected["generation_config"]):
            raise ValueError(f"Frozen generation configuration changed: {name}")


def validate_materialized_benchmark(manifest: dict[str, Any], tasks_path: str | Path) -> None:
    path = Path(tasks_path)
    if not path.exists():
        raise ValueError(f"Materialized EXP-001 benchmark is missing: {path}")
    if not path.is_file():
        raise ValueError(f"Materialized EXP-001 benchmark is not a file: {path}")

    actual_benchmark_sha256 = benchmark_sha256(path)
    expected_benchmark_sha256 = manifest["integrity"].get("materialized_benchmark_sha256")
    if actual_benchmark_sha256 != expected_benchmark_sha256:
        raise ValueError(
            "Materialized benchmark SHA-256 mismatch: "
            f"expected {expected_benchmark_sha256}, got {actual_benchmark_sha256}"
        )

    tasks = load_tasks(path)
    expected_count = int(manifest["task_count"])
    if len(tasks) != expected_count:
        raise ValueError(f"Materialized benchmark task count mismatch: expected {expected_count}, got {len(tasks)}")

    expected = {row["task_id"]: row for row in manifest["tasks"]}
    observed_ids = {task["id"] for task in tasks}
    if observed_ids != set(expected):
        missing = sorted(set(expected) - observed_ids)
        extra = sorted(observed_ids - set(expected))
        raise ValueError(f"Materialized benchmark IDs mismatch: missing={missing}, extra={extra}")

    for task in tasks:
        row = expected[task["id"]]
        metadata = task.get("metadata", {})
        checks = {
            "source_task_sha256": row["task_sha256"],
            "source_test_sha256": row["test_sha256"],
            "assertion_count": int(row["assertion_count"]),
        }
        for field, expected_value in checks.items():
            if metadata.get(field) != expected_value:
                raise ValueError(f"Materialized benchmark provenance mismatch for {task['id']}: {field}")
        if task.get("category") != row["category"]:
            raise ValueError(f"Materialized benchmark category mismatch for {task['id']}")
        if task.get("difficulty") != row["difficulty"]:
            raise ValueError(f"Materialized benchmark difficulty mismatch for {task['id']}")
        if task.get("source") != manifest["provenance"]["canonical_source"]:
            raise ValueError(f"Materialized benchmark source mismatch for {task['id']}")
        if task.get("source_version") != manifest["provenance"]["source_commit"]:
            raise ValueError(f"Materialized benchmark source commit mismatch for {task['id']}")
        if task.get("prompt_transform") != "strip_doctest_examples_v1":
            raise ValueError(f"Materialized benchmark prompt transform mismatch for {task['id']}")
        visible = task["tests"]["visible"].get("assertions", [])
        hidden = task["tests"]["hidden"].get("assertions", [])
        if len(visible) + len(hidden) != int(row["assertion_count"]):
            raise ValueError(f"Materialized benchmark assertion split mismatch for {task['id']}")
        if not visible or not hidden:
            raise ValueError(f"Materialized benchmark must have non-empty visible and hidden suites for {task['id']}")


def validate_frozen_manifest(manifest_path: str | Path) -> dict[str, Any]:
    manifest = validate_manifest_path(manifest_path)
    if manifest["benchmark_id"] != FROZEN_EXP001_BENCHMARK:
        raise ValueError("Unexpected EXP-001 benchmark manifest identity")
    if str(manifest["version"]) != FROZEN_EXP001_VERSION:
        raise ValueError("Unexpected EXP-001 benchmark manifest version")
    if int(manifest["task_count"]) != 100:
        raise ValueError("EXP-001 manifest must contain exactly 100 tasks")
    provenance = manifest["provenance"]
    if provenance.get("canonical_source") != "openai/human-eval":
        raise ValueError("EXP-001 canonical benchmark source changed")
    if provenance.get("source_commit") != "6d43fb980f9fee3c892a914eda09951f772ad10d":
        raise ValueError("EXP-001 HumanEval source commit changed")
    if not isinstance(provenance.get("source_archive_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", provenance["source_archive_sha256"]):
        raise ValueError("EXP-001 source archive SHA-256 is missing or invalid")
    return manifest


def git_state(root: Path) -> tuple[str | None, bool, str | None]:
    def run(*args: str) -> str:
        return subprocess.check_output(args, cwd=root, text=True, stderr=subprocess.DEVNULL).strip()

    try:
        sha = run("git", "rev-parse", "HEAD")
        branch = run("git", "branch", "--show-current")
        dirty = bool(run("git", "status", "--porcelain"))
        return sha, dirty, branch
    except (OSError, subprocess.CalledProcessError):
        return None, True, None
