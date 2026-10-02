#!/usr/bin/env python3
"""Run one real execution-path smoke test; never runs EXP-001."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efficient_reasoning.benchmarks.loader import load_tasks
from efficient_reasoning.experiments.config import load_yaml
from efficient_reasoning.experiments.execution_environment import collect_execution_environment_failures
from efficient_reasoning.generation.parsing import extract_code
from efficient_reasoning.models.adapters import OpenAICompatibleAdapter
from efficient_reasoning.verification.sandbox import DockerExecutor

SMOKE_LABEL = "EXECUTION_SMOKE_TEST"


def _task_seed(base_seed: int, task_id: str) -> int:
    return base_seed + int(hashlib.sha256(task_id.encode()).hexdigest()[:8], 16)


def _prompt(task: dict) -> str:
    return (
        "You are solving a programming benchmark task. Return only Python code.\n\n"
        f"Problem:\n{task['problem']}\n\n"
        f"Function name: {task['entry_point']}"
    )


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
    model_name = cfg["models"][0]
    spec = models["models"][model_name]
    adapter = OpenAICompatibleAdapter(
        spec["name"],
        **{k: v for k, v in spec.items() if k not in {"adapter", "name"}},
    )
    seed = _task_seed(42, task["id"])
    generation = spec["generation_config"]
    started = time.perf_counter()
    result = adapter.generate(
        _prompt(task),
        max_tokens=int(generation["max_tokens"]),
        temperature=float(generation["temperature"]),
        timeout_seconds=float(cfg["generation"]["timeout_seconds"]),
        seed=seed,
        top_p=float(generation["top_p"]),
    )
    code = extract_code(result.text)
    executor = DockerExecutor(
        timeout_seconds=int(cfg["execution"]["timeout_seconds"]),
        memory_mb=int(cfg["execution"]["memory_mb"]),
        cpus=float(cfg["execution"]["cpus"]),
        image=cfg["execution"]["image"],
        platform=cfg["execution"]["platform"],
        pid_limit=int(cfg["execution"]["pid_limit"]),
    )
    execution = executor.run(code, task, suite="visible", timeout_seconds=cfg["execution"]["timeout_seconds"])
    elapsed = time.perf_counter() - started

    output_dir = ROOT / "results" / "execution_smoke_test"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{SMOKE_LABEL}__{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}__{uuid.uuid4().hex[:8]}.json"
    payload = {
        "run_type": SMOKE_LABEL,
        "experiment_id": "EXP-001-smoke-only",
        "experiment_execution": False,
        "task_id": task["id"],
        "strategy": "c0_single",
        "seed": 42,
        "derived_task_seed": seed,
        "model_id": spec["model_id"],
        "model_calls": 1,
        "execution_suite": "visible",
        "hidden_suite_used": False,
        "passed": execution.passed,
        "total": execution.total,
        "execution_error": execution.error,
        "model_latency_seconds": result.latency_seconds,
        "execution_latency_seconds": execution.latency_seconds,
        "elapsed_seconds": elapsed,
        "status": "completed",
        "git_sha": report["git_sha"],
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SMOKE_TEST_RESULT: {output_path.relative_to(ROOT)}")
    return 0 if execution.error is None else 2


if __name__ == "__main__":
    raise SystemExit(run_smoke_test())
