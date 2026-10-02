import pytest

from efficient_reasoning.budgeting.budget import Budget, BudgetExceeded
from efficient_reasoning.core import GenerationResult


def test_budget_accounting():
    budget = Budget(2, 10, 10, 2, 3, max_input_tokens=10)
    budget.reserve_call()
    budget.record_generation(GenerationResult("x", "m", 2, 4, 0.1, 0.25))
    budget.add_candidate()
    snapshot = budget.snapshot().to_dict()
    assert snapshot["model_calls"] == 1
    assert snapshot["output_tokens"] == 4
    assert snapshot["total_generated_tokens"] == 4
    assert snapshot["input_tokens"] == 2
    assert snapshot["cost_proxy"] == 0.25
    assert snapshot["cost_proxy_status"] == "available"


def test_budget_marks_missing_cost_as_unavailable():
    budget = Budget(2, 10, 10, 2, 3)
    budget.reserve_call()
    budget.record_generation(GenerationResult("x", "m", 2, 4, 0.1, None))
    snapshot = budget.snapshot()
    assert snapshot.cost_proxy is None
    assert snapshot.cost_proxy_status == "unavailable"


def test_budget_rejects_output_limit():
    budget = Budget(1, 1, 10, 2, 2)
    budget.reserve_call()
    with pytest.raises(BudgetExceeded):
        budget.record_generation(GenerationResult("x", "m", 0, 2))


def test_budget_rejects_input_limit():
    budget = Budget(1, 100, 10, 2, 2, max_input_tokens=2)
    budget.reserve_call()
    with pytest.raises(BudgetExceeded):
        budget.record_generation(GenerationResult("x", "m", 3, 1))


def test_budget_limits_are_distinct():
    budget = Budget(2, 100, 10, 2, 2)
    budget.reserve_call()
    budget.record_generation(GenerationResult("x", "m", 0, 1, 0.0, 0.0))
    budget.add_candidate()
    budget.add_execution_step(0.01)
    snapshot = budget.snapshot()
    assert snapshot.model_calls == 1
    assert snapshot.output_tokens == 1
    assert snapshot.execution_steps == 1
    assert snapshot.model_latency_seconds == 0.0
    assert snapshot.execution_latency_seconds == 0.01
    assert snapshot.cost_proxy_status == "available"


def test_candidate_budget_is_checked_before_model_call():
    from efficient_reasoning.strategies.base import ReasoningStrategy
    class Dummy(ReasoningStrategy):
        def solve(self, problem, context=None):
            return None
    class Adapter:
        provider = "mock"
        config = {}
        def __init__(self):
            self.called = False
        def generate(self, *args, **kwargs):
            self.called = True
            raise AssertionError("model call must not occur")
    adapter = Adapter()
    strategy = Dummy(adapter, Budget(1, 10, 10, 1, 0))
    with pytest.raises(BudgetExceeded, match="max_candidates exceeded"):
        strategy._generate(adapter, "prompt", "task", 0)
    assert not adapter.called


def test_execution_step_budget_is_checked_before_executor_call():
    from efficient_reasoning.evaluation.evaluator import VisibleEvaluator
    class Executor:
        def __init__(self):
            self.called = False
        def run(self, *args, **kwargs):
            self.called = True
            raise AssertionError("executor call must not occur")
    executor = Executor()
    evaluator = VisibleEvaluator(executor, Budget(1, 10, 10, 0, 1))
    with pytest.raises(BudgetExceeded, match="max_execution_steps exceeded"):
        evaluator.evaluate_visible("code", {"tests": {"visible": []}})
    assert not executor.called
