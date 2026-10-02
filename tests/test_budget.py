import pytest

from efficient_reasoning.budgeting.budget import Budget, BudgetExceeded
from efficient_reasoning.core import GenerationResult


def test_budget_accounting():
    budget = Budget(2, 10, 10, 2, 3, max_input_tokens=10)
    budget.reserve_call()
    budget.record_generation(GenerationResult("x", "m", 2, 4, 0.1))
    budget.add_candidate()
    snapshot = budget.snapshot().to_dict()
    assert snapshot["model_calls"] == 1
    assert snapshot["output_tokens"] == 4
    assert snapshot["total_generated_tokens"] == 4
    assert snapshot["input_tokens"] == 2


def test_budget_rejects_output_limit():
    budget = Budget(1, 1, 10, 2, 2)
    budget.reserve_call()
    with pytest.raises(BudgetExceeded):
        budget.record_generation(GenerationResult("x", "m", 0, 2))
    assert budget.violation_reason == "max_generated_tokens exceeded"


def test_budget_rejects_input_limit():
    budget = Budget(1, 100, 10, 2, 2, max_input_tokens=2)
    budget.reserve_call()
    with pytest.raises(BudgetExceeded):
        budget.record_generation(GenerationResult("x", "m", 3, 1))


def test_budget_limits_are_distinct():
    budget = Budget(2, 100, 10, 2, 2)
    budget.reserve_call()
    budget.record_generation(GenerationResult("x", "m", 0, 1))
    budget.add_candidate()
    budget.add_execution_step(0.01)
    snapshot = budget.snapshot()
    assert snapshot.model_calls == 1
    assert snapshot.output_tokens == 1
    assert snapshot.execution_steps == 1
    assert snapshot.model_latency_seconds == 0.0
    assert snapshot.execution_latency_seconds == 0.01
