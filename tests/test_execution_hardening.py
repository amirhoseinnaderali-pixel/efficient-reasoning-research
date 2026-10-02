from __future__ import annotations

import ast
import json
import os
from pathlib import Path

import pytest

from efficient_reasoning.experiments.execution_environment import check_docker, check_model_access
from efficient_reasoning.evaluation.evaluator import VisibleEvaluator
from efficient_reasoning.experiments.readiness import validate_materialized_benchmark

ROOT = Path(__file__).resolve().parents[1]


def _manifest():
    return json.loads((ROOT / "benchmarks/manifests/exp001_v1.json").read_text())


def _task_from_manifest(manifest, index=0):
    row = manifest["tasks"][index]
    return {
        "id": row["task_id"],
        "problem": "def placeholder():\n    pass\n",
        "entry_point": "placeholder",
        "category": row["category"],
        "difficulty": row["difficulty"],
        "source": "openai/human-eval",
        "source_version": manifest["provenance"]["source_commit"],
        "prompt_transform": "strip_doctest_examples_v1",
        "metadata": {
            "source_task_sha256": row["task_sha256"],
            "source_test_sha256": row["test_sha256"],
            "assertion_count": row["assertion_count"],
        },
        "tests": {
            "visible": {"setup": "", "assertions": ["assert True"]},
            "hidden": {"setup": "", "assertions": ["assert True"]},
        },
    }


def test_missing_materialized_benchmark_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="missing"):
        validate_materialized_benchmark(_manifest(), tmp_path / "tasks.jsonl")


def test_mismatched_materialized_benchmark_fails_closed(tmp_path):
    manifest = _manifest()
    task = _task_from_manifest(manifest)
    task["metadata"]["test_sha256"] = "0" * 64
    out = tmp_path / "tasks.jsonl"
    out.write_text(json.dumps(task) + "\n")
    with pytest.raises(ValueError, match="task count mismatch"):
        validate_materialized_benchmark(manifest, out)


def test_missing_docker_cli_fails_environment_check(monkeypatch, tmp_path):
    import efficient_reasoning.experiments.execution_environment as env

    monkeypatch.setattr(env.shutil, "which", lambda _: None)
    cfg = {"execution": {"image": env.FROZEN_DOCKER_IMAGE, "platform": env.FROZEN_PLATFORM, "network": "none", "sandbox_policy": "docker_strict_v1", "memory_mb": 256, "cpus": 1.0, "pid_limit": 64, "timeout_seconds": 3}}
    failures = check_docker(cfg, tmp_path)
    assert failures == ["Docker CLI is missing"]


def test_missing_docker_daemon_fails_environment_check(monkeypatch, tmp_path):
    import efficient_reasoning.experiments.execution_environment as env

    monkeypatch.setattr(env.shutil, "which", lambda _: "/usr/bin/docker")
    monkeypatch.setattr(env, "_run_capture", lambda *_args, **_kwargs: (False, "daemon unavailable"))
    cfg = {"execution": {"image": env.FROZEN_DOCKER_IMAGE, "platform": env.FROZEN_PLATFORM, "network": "none", "sandbox_policy": "docker_strict_v1", "memory_mb": 256, "cpus": 1.0, "pid_limit": 64, "timeout_seconds": 3}}
    failures = check_docker(cfg, tmp_path)
    assert "Docker daemon is unreachable" in failures


def test_missing_api_key_fails_model_access(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    cfg = {"runner": {"require_real_models": True}, "models": ["primary_openai", "secondary_openai"]}
    models = {"models": {"primary_openai": {"adapter": "openai_compatible", "provider": "openai"}, "secondary_openai": {"adapter": "openai_compatible", "provider": "openai"}}}
    failures = check_model_access(cfg, models)
    assert "OPENAI_API_KEY is missing" in failures


def test_mock_configuration_cannot_satisfy_real_model_access(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "present-but-not-shown")
    cfg = {"runner": {"require_real_models": True}, "models": ["mock"]}
    models = {"models": {"mock": {"adapter": "mock", "provider": "mock"}}}
    failures = check_model_access(cfg, models)
    assert any("Mock model configuration" in failure for failure in failures)


def test_smoke_test_does_not_import_full_experiment_runner():
    tree = ast.parse((ROOT / "scripts/run_execution_smoke_test.py").read_text())
    imported_modules = set()
    called_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called_names.add(node.func.id)
    assert "efficient_reasoning.experiments.runner" not in imported_modules
    assert "run" not in called_names


def test_environment_validator_does_not_print_secret_value():
    source = (ROOT / "src/efficient_reasoning/experiments/execution_environment.py").read_text()
    assert "print(os.getenv" not in source
    assert "OPENAI_API_KEY" in source


def test_visible_evaluator_has_no_hidden_final_method():
    evaluator = VisibleEvaluator(object(), object())
    assert not hasattr(evaluator, "evaluate_hidden")
    assert not hasattr(evaluator, "evaluate_final")


def test_strategy_task_projection_excludes_tests():
    from efficient_reasoning.experiments.runner import _strategy_task

    task = {"id": "t1", "problem": "p", "entry_point": "f", "tests": {"visible": {}, "hidden": {}}}
    assert _strategy_task(task) == {"id": "t1", "problem": "p", "entry_point": "f"}


def test_result_schema_requires_provenance_fields():
    from efficient_reasoning.logging.schema import validate_result

    row = {
        "experiment_id": "EXP-001", "run_id": "r", "timestamp": "t", "strategy": "c0_single",
        "model": "m", "benchmark": {"name": "b", "version": "1", "sha256": "x"},
        "seed": 42, "budget": {}, "metrics": {}, "environment": {}, "status": "completed",
    }
    with pytest.raises(ValueError, match="Result missing fields"):
        validate_result(row)
