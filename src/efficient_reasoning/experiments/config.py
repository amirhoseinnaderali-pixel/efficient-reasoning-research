from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

STRATEGY_TYPES = {
    "single",
    "best_of_n",
    "sequential_refinement",
    "multi_model",
    "multi_model_chain",
    "execution_feedback",
    "graph_aggregation",
}


def load_yaml(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return data


def validate_config(cfg: dict[str, Any], models_cfg: dict[str, Any], benchmarks_cfg: dict[str, Any], *, allow_mock: bool = False) -> None:
    required = {"project", "benchmark", "budget", "execution", "models", "strategies", "runner", "generation"}
    missing = required - cfg.keys()
    if missing:
        raise ValueError(f"Missing config sections: {sorted(missing)}")

    budget = cfg["budget"]
    for key in ("max_model_calls", "max_generated_tokens", "max_latency_seconds", "max_execution_steps", "max_candidates"):
        if budget[key] <= 0:
            raise ValueError(f"Invalid budget: {key} must be > 0")
    if budget.get("max_input_tokens") is not None and budget["max_input_tokens"] <= 0:
        raise ValueError("max_input_tokens must be > 0 when present")

    generation = cfg["generation"]
    if int(generation["max_output_tokens_per_call"]) <= 0:
        raise ValueError("generation.max_output_tokens_per_call must be > 0")
    if float(generation["timeout_seconds"]) <= 0:
        raise ValueError("generation.timeout_seconds must be > 0")
    if not 0.0 <= float(generation["temperature"]):
        raise ValueError("generation.temperature must be non-negative")
    if not 0.0 < float(generation["top_p"]) <= 1.0:
        raise ValueError("generation.top_p must be in (0, 1]")

    benchmark_name = cfg["benchmark"]["name"]
    benchmark_spec = benchmarks_cfg.get("benchmarks", {}).get(benchmark_name)
    if benchmark_spec is None:
        raise ValueError(f"Unknown benchmark: {benchmark_name}")
    if Path(cfg["benchmark"]["tasks_path"]).resolve() != Path(benchmark_spec["path"]).resolve():
        raise ValueError("benchmark.tasks_path does not match configs/benchmarks.yaml")

    models = cfg["models"]
    if not isinstance(models, list) or not models:
        raise ValueError("At least one model must be explicitly configured")
    unknown_models = [m for m in models if m not in models_cfg.get("models", {})]
    if unknown_models:
        raise ValueError(f"Unknown model configuration(s): {unknown_models}")
    if not allow_mock and any(models_cfg["models"][m].get("adapter") == "mock" for m in models):
        raise ValueError("Mock adapters are validation-only and cannot be used for EXP-001")

    strategies = cfg["strategies"]
    for name, spec in strategies.items():
        if spec.get("type") not in STRATEGY_TYPES:
            raise ValueError(f"Unknown strategy type for {name}: {spec.get('type')}")
        strategy_type = spec["type"]
        if strategy_type in {"best_of_n", "graph_aggregation"}:
            n = int(spec["n"])
            if n <= 0 or n > budget["max_candidates"] or n > budget["max_model_calls"]:
                raise ValueError(f"{name}.n exceeds declared candidate/call budget")
        if strategy_type == "sequential_refinement":
            depth = int(spec["depth"])
            if depth <= 0 or depth > budget["max_model_calls"]:
                raise ValueError(f"{name}.depth exceeds declared call budget")
        if strategy_type == "execution_feedback":
            iters = int(spec["max_iterations"])
            if iters <= 0 or iters > budget["max_model_calls"]:
                raise ValueError(f"{name}.max_iterations exceeds declared call budget")
        if strategy_type in {"multi_model", "multi_model_chain"} and len(models) < 2:
            raise ValueError(f"{name} requires at least two configured models")
        if strategy_type == "graph_aggregation":
            graph = spec["graph"]
            if graph.get("method") != "tfidf_cosine":
                raise ValueError("Only explicit graph method 'tfidf_cosine' is currently supported")
            if not 1 <= int(graph["k"]) < int(spec["n"]):
                raise ValueError("graph.k must satisfy 1 <= k < n")

    if cfg["runner"].get("max_retries") != 0:
        raise ValueError("EXP-001 requires max_retries=0 until retry accounting is explicitly designed")
    seeds = cfg["project"].get("seeds")
    if not seeds:
        raise ValueError("project.seeds must contain at least one deterministic seed")
    if len(set(seeds)) != len(seeds):
        raise ValueError("project.seeds must be unique")

    execution = cfg["execution"]
    if not allow_mock and execution.get("backend") != "docker":
        raise ValueError("Real experiments must use the Docker execution backend")
    if execution.get("network") != "none":
        raise ValueError("Experiments require network=none for generated-code execution")
    if int(execution.get("timeout_seconds", 0)) <= 0:
        raise ValueError("Execution timeout must be positive")
