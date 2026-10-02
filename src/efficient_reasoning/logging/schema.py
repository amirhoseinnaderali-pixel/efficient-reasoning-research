from __future__ import annotations

from typing import Any


REQUIRED_RESULT_FIELDS = {
    "experiment_id",
    "run_id",
    "timestamp",
    "strategy",
    "model",
    "benchmark",
    "seed",
    "budget",
    "metrics",
    "environment",
    "status",
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
    if not isinstance(result["metrics"], dict):
        raise ValueError("Result metrics must be an object")
    if result["status"] not in {"completed", "failed", "ineligible_budget", "validation_only"}:
        raise ValueError(f"Unknown result status: {result['status']}")
