from pathlib import Path
import json
import pytest

ROOT = Path(__file__).resolve().parents[1]

from efficient_reasoning.evaluation.statistics import bootstrap_ci


def test_bootstrap_ci_is_deterministic():
    values = [0.0, 0.5, 1.0, 1.0]
    assert bootstrap_ci(values, seed=1, samples=100) == bootstrap_ci(values, seed=1, samples=100)
    lo, hi = bootstrap_ci(values, seed=1, samples=100)
    assert 0.0 <= lo <= hi <= 1.0


def test_analysis_rejects_duplicate_task_seed_strategy(tmp_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("analyze_results", ROOT / "scripts" / "analyze_results.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    load_rows = module.load_rows

    row = {
        "experiment_id": "EXP-001", "run_id": "r1", "timestamp": "t", "strategy": "c0_single",
        "model": "m", "model_pool": ["m"], "selected_candidate_id": "c0-0",
        "generation_config": {}, "config_path": "c", "benchmark": {"name": "b", "version": "1", "sha256": "x"},
        "seed": 42, "task_id": "t1",
        "budget": {
            "model_calls": 1, "failed_model_calls": 0, "retries": 0, "input_tokens": 1, "output_tokens": 1,
            "total_generated_tokens": 1, "model_latency_seconds": 1.0, "execution_latency_seconds": 1.0,
            "graph_latency_seconds": 0.0, "strategy_wall_clock_seconds": 2.0, "cost_proxy": 0.0,
            "cost_proxy_status": "available",
            "execution_steps": 1, "candidate_count": 1, "budget_violated": False, "violation_reason": None,
        },
        "metrics": {"hidden_pass_rate": 1.0}, "environment": {}, "status": "completed",
        "error": None, "evaluation": {"hidden_pass_rate": 1.0}, "candidates": [], "trace": [], "notes": {},
    }
    path = tmp_path / "results.jsonl"
    path.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n")
    with pytest.raises(ValueError, match="Duplicate task-seed-strategy"):
        load_rows(path)
