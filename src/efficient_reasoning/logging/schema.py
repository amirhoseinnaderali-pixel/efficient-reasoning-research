from __future__ import annotations

from typing import Any


REQUIRED_RESULT_FIELDS = {
    "experiment_id",
    "run_id",
    "timestamp",
    "strategy",
    "model",
    "model_pool",
    "selected_candidate_id",
    "generation_config",
    "config_path",
    "benchmark",
    "seed",
    "task_id",
    "budget",
    "metrics",
    "environment",
    "status",
    "error",
    "evaluation",
    "candidates",
    "trace",
    "notes",
}
REQUIRED_BUDGET_FIELDS = {
    "model_calls",
    "failed_model_calls",
    "retries",
    "input_tokens",
    "output_tokens",
    "total_generated_tokens",
    "model_latency_seconds",
    "execution_latency_seconds",
    "graph_latency_seconds",
    "strategy_wall_clock_seconds",
    "cost_proxy",
    "cost_proxy_status",
    "execution_steps",
    "candidate_count",
    "budget_violated",
    "violation_reason",
}


def validate_result(result: dict[str, Any]) -> None:
    missing = REQUIRED_RESULT_FIELDS - result.keys()
    if missing:
        raise ValueError(f"Result missing fields: {sorted(missing)}")
    if not isinstance(result["budget"], dict):
        raise ValueError("Result budget must be an object")
    missing_budget = REQUIRED_BUDGET_FIELDS - result["budget"].keys()
    if missing_budget:
        raise ValueError(f"Result budget missing fields: {sorted(missing_budget)}")
    if result["budget"]["cost_proxy_status"] not in {"available", "unavailable"}:
        raise ValueError("Unknown cost_proxy_status")
    if result["budget"]["cost_proxy_status"] == "available":
        if result["budget"]["cost_proxy"] is None:
            raise ValueError("Available cost proxy must be numeric")
    elif result["budget"]["cost_proxy"] is not None:
        raise ValueError("Unavailable cost proxy must be null")
    if not isinstance(result["metrics"], dict):
        raise ValueError("Result metrics must be an object")
    if not isinstance(result["benchmark"], dict) or not result["benchmark"].get("name") or not result["benchmark"].get("version") or not result["benchmark"].get("sha256"):
        raise ValueError("Result benchmark provenance is incomplete")
    if not isinstance(result["seed"], int):
        raise ValueError("Result seed must be an integer")
    environment = result["environment"]
    if not isinstance(environment, dict):
        raise ValueError("Result environment must be an object")
    for field in ("git_sha", "config_sha256", "benchmark_sha256", "python", "platform", "model_config", "execution"):
        if field not in environment:
            raise ValueError(f"Result environment provenance is missing: {field}")
    for field in ("git_sha", "config_sha256", "benchmark_sha256", "python", "platform"):
        if not isinstance(environment[field], str) or not environment[field]:
            raise ValueError(f"Result environment field must be a non-empty string: {field}")
    if environment["benchmark_sha256"] != result["benchmark"]["sha256"]:
        raise ValueError("Result benchmark SHA-256 does not match environment provenance")
    if not isinstance(environment["model_config"], dict) or not environment["model_config"]:
        raise ValueError("Result model metadata is missing")
    if not isinstance(environment["execution"], dict) or not environment["execution"]:
        raise ValueError("Result execution environment metadata is missing")
    if not isinstance(result["model_pool"], list) or not result["model_pool"]:
        raise ValueError("Result model_pool must be a non-empty list")
    if not isinstance(result["generation_config"], dict):
        raise ValueError("Result generation_config must be an object")
    if not isinstance(result["task_id"], str) or not result["task_id"]:
        raise ValueError("Result task_id must be a non-empty string")
    if not isinstance(result["run_id"], str) or not result["run_id"]:
        raise ValueError("Result run_id must be non-empty")
    if result["status"] not in {"completed", "failed", "ineligible_budget", "validation_only"}:
        raise ValueError(f"Unknown result status: {result['status']}")
    if not isinstance(result["candidates"], list) or not isinstance(result["trace"], list) or not isinstance(result["notes"], dict):
        raise ValueError("Result candidates/trace/notes have invalid types")
    evaluation = result["evaluation"]
    if evaluation is not None:
        error_kind = evaluation.get("error_kind")
        if error_kind not in {None, "candidate_execution", "infrastructure"}:
            raise ValueError("Unknown evaluation error_kind")
        if error_kind == "infrastructure":
            raise ValueError("Infrastructure evaluation failures must be recorded with status=failed")
    if result["status"] in {"completed", "validation_only"}:
        if result["evaluation"] is None:
            raise ValueError("Completed result must contain final evaluation")
        if result["model"] is None or result["selected_candidate_id"] is None:
            raise ValueError("Completed result must record the selected model and candidate")
    if result["status"] == "ineligible_budget" and not result["budget"].get("budget_violated"):
        raise ValueError("Budget-ineligible result must record budget_violated=true")
