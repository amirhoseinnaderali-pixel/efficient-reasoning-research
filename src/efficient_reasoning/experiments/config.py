from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..benchmarks.manifest import validate_manifest_path

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

    exp_id = str(cfg["runner"].get("experiment_id", ""))
    is_exp001 = exp_id == "EXP-001"

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
    if is_exp001 and generation.get("seed_mode") != "task_seed_v1":
        raise ValueError("EXP-001 requires generation.seed_mode=task_seed_v1")

    benchmark_name = cfg["benchmark"]["name"]
    benchmark_spec = benchmarks_cfg.get("benchmarks", {}).get(benchmark_name)
    if benchmark_spec is None:
        raise ValueError(f"Unknown benchmark: {benchmark_name}")
    if Path(cfg["benchmark"]["tasks_path"]).resolve() != Path(benchmark_spec["path"]).resolve():
        raise ValueError("benchmark.tasks_path does not match configs/benchmarks.yaml")
    if is_exp001:
        manifest_path = cfg["benchmark"].get("manifest_path")
        if not manifest_path:
            raise ValueError("EXP-001 requires benchmark.manifest_path")
        if Path(manifest_path).resolve() != Path(benchmark_spec["manifest"]).resolve():
            raise ValueError("benchmark.manifest_path does not match configs/benchmarks.yaml")
        manifest = validate_manifest_path(manifest_path)
        if manifest["benchmark_id"] != benchmark_name or str(manifest["version"]) != str(benchmark_spec["version"]):
            raise ValueError("EXP-001 benchmark manifest identity/version mismatch")
        if int(manifest["task_count"]) != 100:
            raise ValueError("EXP-001 benchmark manifest must lock 100 tasks")

    models = cfg["models"]
    if not isinstance(models, list) or not models:
        raise ValueError("At least one model must be explicitly configured")
    unknown_models = [m for m in models if m not in models_cfg.get("models", {})]
    if unknown_models:
        raise ValueError(f"Unknown model configuration(s): {unknown_models}")
    if not allow_mock and any(models_cfg["models"][m].get("adapter") == "mock" for m in models):
        raise ValueError("Mock adapters are validation-only and cannot be used for EXP-001")

    strategies = cfg["strategies"]
    required_strategy_names = {"c0_single", "c1_best_of_n", "c2_sequential_refinement", "c3_multi_model", "c4_multi_model_chain", "c5_execution_feedback", "c6_graph_aggregation"}
    if is_exp001 and set(strategies) != required_strategy_names:
        raise ValueError("EXP-001 must declare exactly C0-C6")
    for name, spec in strategies.items():
        if spec.get("type") not in STRATEGY_TYPES:
            raise ValueError(f"Unknown strategy type for {name}: {spec.get('type')}")
        pool = spec.get("model_pool", models)
        if not isinstance(pool, list) or not pool:
            raise ValueError(f"{name}.model_pool must be a non-empty list")
        if any(m not in models for m in pool):
            raise ValueError(f"{name}.model_pool contains model not in top-level models: {pool}")
        if is_exp001 and len(set(pool)) != len(pool):
            raise ValueError(f"{name}.model_pool must be unique")
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
        if strategy_type in {"multi_model", "multi_model_chain"} and len(pool) < 2:
            raise ValueError(f"{name} requires at least two configured models in model_pool")
        if strategy_type == "graph_aggregation":
            graph = spec["graph"]
            if graph.get("method") != "tfidf_cosine":
                raise ValueError("Only explicit graph method 'tfidf_cosine' is currently supported")
            if not 1 <= int(graph["k"]) < int(spec["n"]):
                raise ValueError("graph.k must satisfy 1 <= k < n")
            if is_exp001 and graph.get("uses_objective_results") is not False:
                raise ValueError("C6 graph aggregation must not use objective results")
            if is_exp001 and graph.get("selection_input") != "candidate_text_only":
                raise ValueError("C6 selection input must be candidate_text_only")

    if cfg["runner"].get("max_retries") != 0:
        raise ValueError("EXP-001 requires max_retries=0 until retry accounting is explicitly designed")
    seeds = cfg["project"].get("seeds")
    if not seeds:
        raise ValueError("project.seeds must contain at least one deterministic seed")
    if len(set(seeds)) != len(seeds):
        raise ValueError("project.seeds must be unique")
    if is_exp001 and cfg["runner"].get("allow_mock") is not False:
        raise ValueError("EXP-001 runner.allow_mock must be false")

    execution = cfg["execution"]
    if not allow_mock and execution.get("backend") != "docker":
        raise ValueError("Real experiments must use the Docker execution backend")
    if execution.get("network") != "none":
        raise ValueError("Experiments require network=none for generated-code execution")
    if int(execution.get("timeout_seconds", 0)) <= 0:
        raise ValueError("Execution timeout must be positive")
    if is_exp001:
        image = str(execution.get("image", ""))
        if "@sha256:" not in image:
            raise ValueError("EXP-001 Docker image must use an immutable @sha256 digest")
        digest = image.split("@sha256:", 1)[1]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("EXP-001 Docker image digest must be a 64-character lowercase SHA-256")
        if not execution.get("platform"):
            raise ValueError("EXP-001 execution.platform must be explicit")
        if execution.get("sandbox_policy") != "docker_strict_v1":
            raise ValueError("EXP-001 requires docker_strict_v1 sandbox policy")

    if is_exp001:
        frozen_budget = {
            "max_model_calls": 8,
            "max_generated_tokens": 9600,
            "max_input_tokens": 40000,
            "max_latency_seconds": 300,
            "max_execution_steps": 12,
            "max_candidates": 8,
        }
        if {key: budget[key] for key in frozen_budget} != frozen_budget:
            raise ValueError("EXP-001 budget is not the frozen protocol budget")
        if cfg["models"] != ["primary_openai", "secondary_openai"]:
            raise ValueError("EXP-001 top-level model list is not frozen")
        frozen_strategy_specs = {
            "c0_single": {"type": "single", "model_pool": ["primary_openai"]},
            "c1_best_of_n": {"type": "best_of_n", "n": 4, "model_pool": ["primary_openai"]},
            "c2_sequential_refinement": {"type": "sequential_refinement", "depth": 3, "model_pool": ["primary_openai"]},
            "c3_multi_model": {"type": "multi_model", "model_pool": ["primary_openai", "secondary_openai"]},
            "c4_multi_model_chain": {"type": "multi_model_chain", "model_pool": ["primary_openai", "secondary_openai"]},
            "c5_execution_feedback": {"type": "execution_feedback", "max_iterations": 3, "model_pool": ["primary_openai"]},
            "c6_graph_aggregation": {
                "type": "graph_aggregation", "n": 4, "model_pool": ["primary_openai"],
                "graph": {"method": "tfidf_cosine", "k": 2, "embedding_model": "tfidf_builtin_v1", "selection_input": "candidate_text_only", "uses_objective_results": False},
            },
        }
        if cfg["strategies"] != frozen_strategy_specs:
            raise ValueError("EXP-001 strategy configuration is not the frozen C0-C6 protocol")
        if cfg["generation"] != {"max_output_tokens_per_call": 1200, "timeout_seconds": 120, "seed_mode": "task_seed_v1"}:
            raise ValueError("EXP-001 generation configuration is not frozen")

        frozen_model_ids = {
            "primary_openai": "gpt-4.1-mini-2025-04-14",
            "secondary_openai": "gpt-4.1-2025-04-14",
        }
        frozen_generation = {"temperature": 0.2, "top_p": 1.0, "max_tokens": 1200}
        for model_name in models:
            spec = models_cfg["models"][model_name]
            if model_name not in frozen_model_ids:
                raise ValueError(f"EXP-001 model {model_name} is not part of the frozen model pool")
            adapter = spec.get("adapter")
            if adapter != "openai_compatible":
                raise ValueError(f"EXP-001 model {model_name} must use the pinned OpenAI-compatible adapter")
            model_id = str(spec.get("model_id", spec.get("name", "")))
            if model_id != frozen_model_ids[model_name]:
                raise ValueError(f"EXP-001 model {model_name} must be exactly {frozen_model_ids[model_name]}")
            if spec.get("provider") != "openai" or spec.get("base_url") != "https://api.openai.com/v1":
                raise ValueError(f"EXP-001 model {model_name} provider/base URL is not frozen")
            if spec.get("api_version") != "chat_completions_v1":
                raise ValueError(f"EXP-001 model {model_name} API mode is not frozen")
            if not bool(spec.get("supports_seed")):
                raise ValueError(f"EXP-001 model {model_name} must support deterministic seed requests")
            if spec.get("generation_config") != frozen_generation:
                raise ValueError(f"EXP-001 model {model_name} generation configuration is not frozen")
