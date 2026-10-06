from efficient_reasoning.budgeting.budget import Budget
from efficient_reasoning.core import GenerationResult
from efficient_reasoning.strategies.base import ReasoningStrategy


class DummyStrategy(ReasoningStrategy):
    def solve(self, problem, context=None):
        return None


class OverproducingAdapter:
    provider = "mock"
    config = {}

    def generate(self, prompt, **kwargs):
        self.max_tokens_seen = kwargs["max_tokens"]
        del prompt
        return GenerationResult("x", "dummy", input_tokens=1, output_tokens=999)


def test_generation_budget_caps_requested_tokens_and_rejects_provider_overrun():
    budget = Budget(1, 10, 10, 1, 1)
    strategy = DummyStrategy(
        OverproducingAdapter(),
        budget,
        generation={"max_output_tokens_per_call": 7, "temperature": 0.0, "top_p": 1.0, "timeout_seconds": 5},
    )
    try:
        strategy._generate(strategy.adapter, "prompt", "task", 0)
    except RuntimeError:
        # Provider cannot itself be forced to respect usage accounting; the run is invalidated instead.
        pass
    except Exception:
        pass
    assert strategy.adapter.max_tokens_seen == 7
    assert budget.model_calls == 1
    assert budget.violation_reason == "max_generated_tokens exceeded"


class MissingUsageAdapter:
    provider = "real"
    config = {}

    def generate(self, prompt, **kwargs):
        del prompt, kwargs
        return GenerationResult("x", "real", input_tokens=0, output_tokens=1)


def test_missing_provider_usage_invalidates_run():
    budget = Budget(1, 10, 10, 1, 1)
    strategy = DummyStrategy(MissingUsageAdapter(), budget)
    try:
        strategy._generate(strategy.adapter, "prompt", "task")
    except Exception as exc:
        assert "token usage unavailable" in str(exc)
    else:
        raise AssertionError("missing provider usage must invalidate the run")
    assert budget.violation_reason == "provider token usage unavailable; run is scientifically ineligible"
