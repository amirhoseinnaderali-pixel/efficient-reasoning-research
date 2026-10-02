from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import time
import uuid
from pathlib import Path

from ..benchmarks.loader import benchmark_sha256, load_tasks
from ..benchmarks.manifest import validate_manifest_path
from .readiness import validate_materialized_benchmark
from ..budgeting.budget import Budget, BudgetExceeded
from ..evaluation.evaluator import ObjectiveEvaluator, VisibleEvaluator
from ..logging.schema import validate_result
from ..models.adapters import GoogleAdapter, MockAdapter, OllamaAdapter, OpenAICompatibleAdapter
from ..strategies.factory import build_strategy
from ..verification.sandbox import DockerExecutor, MockExecutor
from .config import load_yaml, validate_config


def _git_sha() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _package_versions() -> dict[str, str]:
    wanted = {"efficient-reasoning-research", "PyYAML", "pytest"}
    out = {}
    for package in wanted:
        try:
            out[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            out[package] = "not-installed"
    return out


def _environment() -> dict:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "packages": _package_versions(),
        "git_sha": _git_sha(),
    }


def make_adapter(spec, task_id, mock=False):
    if mock or spec.get("adapter") == "mock":
        return MockAdapter(spec.get("name", "mock-coder"), task_id=task_id)
    cls = {"ollama": OllamaAdapter, "openai_compatible": OpenAICompatibleAdapter, "google": GoogleAdapter}[spec["adapter"]]
    return cls(spec["name"], **{k: v for k, v in spec.items() if k not in {"adapter", "name"}})


def make_executor(cfg, mock=False):
    if mock:
        return MockExecutor()
    if cfg.get("backend") != "docker":
        raise RuntimeError(f"Unsupported real execution backend: {cfg.get('backend')}")
    return DockerExecutor(
        timeout_seconds=int(cfg["timeout_seconds"]),
        memory_mb=int(cfg["memory_mb"]),
        cpus=float(cfg["cpus"]),
        image=cfg["image"],
        platform=cfg.get("platform", "linux/amd64"),
        pid_limit=int(cfg["pid_limit"]),
    )


def _task_seed(base_seed: int, task_id: str) -> int:
    digest = hashlib.sha256(task_id.encode()).hexdigest()
    return base_seed + int(digest[:8], 16)


def _strategy_task(task: dict) -> dict:
    """Project the benchmark task to fields permitted inside strategy code."""
    return {key: task[key] for key in ("id", "problem", "entry_point")}


def _experiment_hash(cfg: dict) -> str:
    return _sha256_text(json.dumps(cfg, sort_keys=True, separators=(",", ":")))


def _write_batch(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        for row in rows:
            validate_result(row)
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def run(config_path, mock=False):
    cfg = load_yaml(config_path)
    model_cfg = load_yaml("configs/models.yaml")
    benchmark_cfg = load_yaml("configs/benchmarks.yaml")
    validate_config(cfg, model_cfg, benchmark_cfg, allow_mock=mock)
    manifest = None
    if cfg["runner"].get("require_materialized_benchmark"):
        manifest = validate_manifest_path(cfg["benchmark"]["manifest_path"])
        validate_materialized_benchmark(manifest, cfg["benchmark"]["tasks_path"])
    tasks = load_tasks(cfg["benchmark"]["tasks_path"])
    if manifest is not None and len(tasks) != int(manifest["task_count"]):
        raise RuntimeError("Materialized benchmark task count does not match frozen manifest")
    specs_by_name = {name: model_cfg["models"][name] for name in cfg["models"]}
    specs = list(specs_by_name.values())
    exp_hash = _experiment_hash(cfg)
    env_base = _environment()
    env_base.update(
        {
            "config_sha256": exp_hash,
            "benchmark_sha256": benchmark_sha256(cfg["benchmark"]["tasks_path"]),
            "benchmark_manifest_sha256": manifest["integrity"]["manifest_content_sha256"] if manifest else None,
            "benchmark_name": cfg["benchmark"]["name"],
            "benchmark_version": benchmark_cfg["benchmarks"][cfg["benchmark"]["name"]]["version"],
            "mock_validation_only": bool(mock),
        }
    )

    batch_id = f"{cfg['runner']['experiment_id']}__{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}__{uuid.uuid4().hex[:8]}"
    rows = []
    for seed in cfg["project"]["seeds"]:
        for task in tasks:
            for strategy_name, strategy_cfg in cfg["strategies"].items():
                budget = Budget(**cfg["budget"])
                executor = make_executor(cfg["execution"], mock)
                final_evaluator = ObjectiveEvaluator(executor, budget)
                visible_evaluator = VisibleEvaluator(executor, budget)
                adapter_cache = {name: make_adapter(spec, task["id"], mock) for name, spec in specs_by_name.items()}
                default_pool = cfg["models"]
                pool_names = strategy_cfg.get("model_pool", default_pool)
                adapters = [adapter_cache[name] for name in pool_names]
                primary = adapters[0]
                strategy_seed = _task_seed(int(seed), task["id"])
                result = None
                evaluation = None
                status = "completed"
                error = None
                try:
                    strategy = build_strategy(
                        strategy_name,
                        strategy_cfg,
                        primary,
                        budget,
                        visible_evaluator,
                        adapters,
                        generation=cfg["generation"],
                        seed=strategy_seed,
                    )
                    strategy_task = _strategy_task(task)
                    result = strategy.solve(strategy_task)
                    evaluation = final_evaluator.evaluate_final(result.answer, task)
                    budget.check_wall_clock()
                except BudgetExceeded as exc:
                    status = "ineligible_budget"
                    error = f"BudgetExceeded: {exc}"
                except Exception as exc:
                    status = "failed"
                    error = f"{type(exc).__name__}: {exc}"
                snap = budget.snapshot().to_dict()
                metrics = {
                    "hidden_pass_rate": None if evaluation is None else evaluation.hidden_pass_rate,
                    "hidden_passed": None if evaluation is None else evaluation.hidden_passed,
                    "hidden_total": None if evaluation is None else evaluation.hidden_total,
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
                    "experiment_id": cfg["runner"]["experiment_id"],
                    "run_id": f"{batch_id}__seed{seed}__{task['id']}__{strategy_name}",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "strategy": strategy_name,
                    "model": None if result is None else result.selected_model,
                    "model_pool": [specs_by_name[n]["model_id"] for n in strategy_cfg.get("model_pool", cfg["models"])],
                    "selected_candidate_id": None if result is None else result.selected_candidate_id,
                    "generation_config": {
                        "global": cfg["generation"],
                        "model_specific": {n: specs_by_name[n].get("generation_config", {}) for n in strategy_cfg.get("model_pool", cfg["models"])},
                    },
                    "config_path": str(config_path),
                    "benchmark": {"name": cfg["benchmark"]["name"], "version": env_base["benchmark_version"], "sha256": env_base["benchmark_sha256"]},
                    "seed": int(seed),
                    "task_id": task["id"],
                    "budget": snap,
                    "metrics": metrics,
                    "status": status if not mock else "validation_only",
                    "error": error,
                    "evaluation": None if evaluation is None else {
                        "hidden_passed": evaluation.hidden_passed,
                        "hidden_total": evaluation.hidden_total,
                        "hidden_pass_rate": evaluation.hidden_pass_rate,
                        "executable": evaluation.executable,
                        "error": evaluation.error,
                        "latency_seconds": evaluation.latency_seconds,
                        "execution_steps": evaluation.execution_steps,
                    },
                    "candidates": [] if result is None else [
                        {
                            "candidate_id": c.candidate_id,
                            "model": c.model,
                            "text": c.text,
                            "visible_pass": c.visible_pass,
                            "visible_total": c.visible_total,
                            "visible_latency_seconds": c.visible_latency_seconds,
                            "generation": {
                                "input_tokens": c.generation.input_tokens,
                                "output_tokens": c.generation.output_tokens,
                                "latency_seconds": c.generation.latency_seconds,
                                "cost_proxy": c.generation.cost_proxy,
                                "metadata": c.generation.metadata,
                            },
                        }
                        for c in result.candidates
                    ],
                    "trace": [] if result is None else result.trace,
                    "notes": {"validation_only": bool(mock), **({} if result is None else result.notes)},
                    "environment": env_base | {"model_config": {n: specs_by_name[n] for n in strategy_cfg.get("model_pool", cfg["models"])}, "execution": cfg["execution"]},
                }
                rows.append(row)

    output_dir = Path("results/validation") if mock else Path(cfg["runner"]["output_dir"])
    out = output_dir / f"{batch_id}.jsonl"
    if not mock and cfg["runner"].get("forbid_existing_output_overwrite") and out.exists():
        raise FileExistsError(f"Refusing to overwrite existing EXP-001 result file: {out}")
    _write_batch(out, rows)
    return out
