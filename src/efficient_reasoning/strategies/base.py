from __future__ import annotations

import time
from abc import ABC, abstractmethod

from ..budgeting.budget import Budget
from ..core import GenerationResult, StrategyResult


class ReasoningStrategy(ABC):
    def __init__(self, adapter, budget: Budget, evaluator=None, adapters=None, generation=None, seed: int = 42):
        self.adapter = adapter
        self.budget = budget
        self.evaluator = evaluator
        self.adapters = adapters or [adapter]
        self.generation = generation or {}
        self.seed = seed

    @abstractmethod
    def solve(self, problem, context=None) -> StrategyResult:
        raise NotImplementedError

    def _generate(self, adapter, prompt: str, task_id: str, candidate_index: int = 0) -> GenerationResult:
        self.budget.reserve_call()
        adapter.config["task_id"] = task_id
        remaining = self.budget.remaining_generated_tokens
        if remaining <= 0:
            raise RuntimeError("No generated-token budget remains")
        requested = int(self.generation.get("max_output_tokens_per_call", remaining))
        max_tokens = min(requested, remaining)
        remaining_latency = self.budget.remaining_latency_seconds
        if remaining_latency <= 0:
            raise RuntimeError("No wall-clock budget remains")
        timeout_seconds = min(float(self.generation.get("timeout_seconds", 120.0)), remaining_latency)
        seed = self.seed + candidate_index
        started = time.perf_counter()
        try:
            result = adapter.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=float(self.generation.get("temperature", 0.2)),
                timeout_seconds=max(0.1, timeout_seconds),
                seed=seed,
                top_p=float(self.generation.get("top_p", 1.0)),
            )
        except Exception:
            self.budget.record_failed_call(time.perf_counter() - started)
            raise
        usage_reported = bool(result.metadata.get("usage_reported", adapter.provider == "mock"))
        if not usage_reported:
            self.budget.invalidate("provider token usage unavailable; run is scientifically ineligible")
        self.budget.record_generation(result)
        self.budget.add_candidate()
        return result
