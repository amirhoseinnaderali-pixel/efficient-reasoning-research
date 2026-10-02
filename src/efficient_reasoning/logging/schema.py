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
    if result["status"] in {"completed", "validation_only"}:
        if result["evaluation"] is None:
            raise ValueError("Completed result must contain final evaluation")
        if result["model"] is None or result["selected_candidate_id"] is None:
            raise ValueError("Completed result must record the selected model and candidate")
    if result["status"] == "ineligible_budget" and not result["budget"].get("budget_violated"):
        raise ValueError("Budget-ineligible result must record budget_violated=true")
