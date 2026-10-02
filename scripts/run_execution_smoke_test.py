#!/usr/bin/env python3
"""Run one real execution-path smoke test with both visible and hidden evaluation."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efficient_reasoning.benchmarks.loader import benchmark_sha256, load_tasks
from efficient_reasoning.experiments.config import load_yaml
from efficient_reasoning.experiments.execution_environment import collect_execution_environment_failures
from efficient_reasoning.budgeting.budget import Budget, BudgetExceeded
from efficient_reasoning.core import Candidate
from efficient_reasoning.evaluation.evaluator import InfrastructureExecutionError, ObjectiveEvaluator, VisibleEvaluator
from efficient_reasoning.logging.schema import validate_result
from efficient_reasoning.models.adapters import OpenAICompatibleAdapter
from efficient_reasoning.strategies.factory import build_strategy
from efficient_reasoning.verification.sandbox import DockerExecutor

SMOKE_LABEL = "EXECUTION_SMOKE_TEST"


def _task_seed(base_seed: int, task_id: str) -> int:
    return base_seed + int(hashlib.sha256(task_id.encode()).hexdigest()[:8], 16)


def _config_sha256(cfg: dict) -> str:
    encoded = json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _package_versions() -> dict[str, str]:
    out = {}
    for package in ("efficient-reasoning-research", "PyYAML", "pytest"):
        try:
            out[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            out[package] = "not-installed"
    return out


def _candidate_payload(candidate: Candidate) -> dict:
    return {
        "candidate_id": candidate.candidate_id,
        "model": candidate.model,
        "text": candidate.text,
        "visible_pass": candidate.visible_pass,
        "visible_total": candidate.visible_total,
        "visible_latency_seconds": candidate.visible_latency_seconds,
        "generation": {
            "input_tokens": candidate.generation.input_tokens,
            "output_tokens": candidate.generation.output_tokens,
            "latency_seconds": candidate.generation.latency_seconds,
            "cost_proxy": candidate.generation.cost_proxy,
            "metadata": candidate.generation.metadata,
        },
    }


def run_smoke_test() -> int:
    print(SMOKE_LABEL)
    cfg = load_yaml(ROOT / "configs/experiments/exp001_fixed_budget.yaml")
    models = load_yaml(ROOT / "configs/models.yaml")
    benchmarks = load_yaml(ROOT / "configs/benchmarks.yaml")

    failures, report = collect_execution_environment_failures(ROOT, cfg, models, benchmarks)
    if failures:
        for failure in failures:
            print(f"NOT_READY: {failure}")
        print("Smoke test aborted before real model/Docker execution.")
        return 1

    tasks = load_tasks(ROOT / cfg["benchmark"]["tasks_path"])
    task = tasks[0]
    model_name = cfg["strategies"]["c0_single"]["model_pool"][0]
    spec = models["models"][model_name]
    adapter = OpenAICompatibleAdapter(
        spec["name"],
        **{k: v for k, v in spec.items() if k not in {"adapter", "name"}},
    )

    budget = Budget(**cfg["budget"])
    executor = DockerExecutor(
        timeout_seconds=int(cfg["execution"]["timeout_seconds"]),
        memory_mb=int(cfg["execution"]["memory_mb"]),
        cpus=float(cfg["execution"]["cpus"]),
        image=cfg["execution"]["image"],
        platform=cfg["execution"]["platform"],
        pid_limit=int(cfg["execution"]["pid_limit"]),
    )
    visible_evaluator = VisibleEvaluator(executor, budget)
    final_evaluator = ObjectiveEvaluator(executor, budget)
    strategy_seed = _task_seed(42, task["id"])
    strategy = build_strategy(
        "c0_single",
        cfg["strategies"]["c0_single"],
        adapter,
        budget,
        visible_evaluator,
        [adapter],
        generation=cfg["generation"],
        seed=strategy_seed,
    )

    started = time.perf_counter()
    strategy_result = None
    visible_result = None
    evaluation = None
    status = "completed"
    error = None

    try:
        strategy_result = strategy.solve(
            {key: task[key] for key in ("id", "problem", "entry_point")}
        )
        visible_result = visible_evaluator.evaluate_visible(strategy_result.answer, task)
        candidate = strategy_result.candidates[0]
        candidate.visible_pass = visible_result.passed
        candidate.visible_total = visible_result.total
        candidate.visible_latency_seconds = visible_result.latency_seconds
        evaluation = final_evaluator.evaluate_final(strategy_result.answer, task)
        budget.check_wall_clock()
    except BudgetExceeded as exc:
        status = "ineligible_budget"
        error = f"BudgetExceeded: {exc}"
    except InfrastructureExecutionError as exc:
        status = "failed"
        error = f"infrastructure_execution_failure: {exc}"
    except Exception as exc:
        status = "failed"
        error = f"{type(exc).__name__}: {exc}"

    elapsed = time.perf_counter() - started
    snap = budget.snapshot().to_dict()
    config_hash = _config_sha256(cfg)
    bench_hash = benchmark_sha256(cfg["benchmark"]["tasks_path"])
    model_pool = [spec["model_id"]]

    environment = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": __import__("os").cpu_count(),
        "packages": _package_versions(),
        "git_sha": report["git_sha"],
        "config_sha256": config_hash,
        "benchmark_sha256": bench_hash,
        "benchmark_manifest_sha256": None,
        "benchmark_name": cfg["benchmark"]["name"],
        "benchmark_version": benchmarks["benchmarks"][cfg["benchmark"]["name"]]["version"],
        "mock_validation_only": False,
        "model_config": {model_name: spec},
        "execution": cfg["execution"],
    }

    metrics = {
        "hidden_pass_rate": None if evaluation is None else evaluation.hidden_pass_rate,
        "hidden_passed": None if evaluation is None else evaluation.hidden_passed,
        "hidden_total": None if evaluation is None else evaluation.hidden_total,
        "visible_pass_rate": None if visible_result is None else visible_result.pass_rate,
        "visible_passed": None if visible_result is None else visible_result.passed,
        "visible_total": None if visible_result is None else visible_result.total,
        "model_calls": snap["model_calls"],
        "input_tokens": snap["input_tokens"],
        "output_tokens": snap["output_tokens"],
        "total_generated_tokens": snap["total_generated_tokens"],
        "model_latency_seconds": snap["model_latency_seconds"],
        "execution_latency_seconds": snap["execution_latency_seconds"],
        "graph_latency_seconds": snap["graph_latency_seconds"],
        "strategy_wall_clock_seconds": snap["strategy_wall_clock_seconds"],
        "execution_steps": snap["execution_steps"],
        "candidate_count": snap["candidate_count"],
        "cost_proxy": snap["cost_proxy"],
    }

    row = {
        "experiment_id": "EXP-001-smoke-only",
        "run_id": f"{SMOKE_LABEL}__{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}__{uuid.uuid4().hex[:8]}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "strategy": "c0_single",
        "model": None if strategy_result is None else strategy_result.selected_model,
        "model_pool": model_pool,
        "selected_candidate_id": None if strategy_result is None else strategy_result.selected_candidate_id,
        "generation_config": {
            "global": cfg["generation"],
            "model_specific": {model_name: spec.get("generation_config", {})},
        },
        "config_path": "configs/experiments/exp001_fixed_budget.yaml",
        "benchmark": {
            "name": cfg["benchmark"]["name"],
            "version": environment["benchmark_version"],
            "sha256": bench_hash,
        },
        "seed": 42,
        "task_id": task["id"],
        "budget": snap,
        "metrics": metrics,
        "status": status,
        "error": error,
        "evaluation": None if evaluation is None else {
            "hidden_passed": evaluation.hidden_passed,
            "hidden_total": evaluation.hidden_total,
            "hidden_pass_rate": evaluation.hidden_pass_rate,
            "executable": evaluation.executable,
            "error": evaluation.error,
            "error_kind": evaluation.error_kind,
            "latency_seconds": evaluation.latency_seconds,
            "execution_steps": evaluation.execution_steps,
        },
        "candidates": [] if strategy_result is None else [_candidate_payload(c) for c in strategy_result.candidates],
        "trace": [] if strategy_result is None else strategy_result.trace,
        "notes": {
            "run_type": SMOKE_LABEL,
            "experiment_execution": False,
            "visible_evaluation_performed": visible_result is not None,
            "hidden_evaluation_performed": evaluation is not None,
            "elapsed_seconds": elapsed,
            "validation_only": False,
        },
        "environment": environment,
    }

    validate_result(row)
    output_dir = ROOT / "results" / "execution_smoke_test"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{row['run_id']}.json"
    output_path.write_text(json.dumps(row, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"SMOKE_TEST_RESULT: {output_path.relative_to(ROOT)}")
    print(f"SMOKE_STATUS: {status}")
    print(f"VISIBLE_PASS_RATE: {metrics['visible_pass_rate']}")
    print(f"HIDDEN_PASS_RATE: {metrics['hidden_pass_rate']}")
    return 0 if status == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(run_smoke_test())
