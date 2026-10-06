import pytest

from efficient_reasoning.budgeting.budget import Budget
from efficient_reasoning.core import GenerationResult
from efficient_reasoning.strategies.base import ReasoningStrategy


class FailingAdapter:
    config = {}

    def generate(self, prompt, **kwargs):
        del prompt, kwargs
        raise RuntimeError("provider unavailable")


class Dummy(ReasoningStrategy):
    def solve(self, problem, context=None):
        return None


def test_failed_model_call_is_counted():
    budget = Budget(1, 100, 10, 1, 1)
    strategy = Dummy(FailingAdapter(), budget)
    with pytest.raises(RuntimeError, match="provider unavailable"):
        strategy._generate(strategy.adapter, "prompt", "task")
    assert budget.model_calls == 1
    assert budget.failed_model_calls == 1
