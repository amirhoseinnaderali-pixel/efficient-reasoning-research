from __future__ import annotations

import time
from dataclasses import dataclass

from ..core import BudgetSnapshot, GenerationResult


class BudgetExceeded(RuntimeError):
    """Raised when a run crosses a declared experimental budget."""


@dataclass
class Budget:
    max_model_calls: int
    max_generated_tokens: int
    max_latency_seconds: float
    max_execution_steps: int
    max_candidates: int
    max_input_tokens: int | None = None
    model_calls: int = 0
    failed_model_calls: int = 0
    retries: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    model_latency_seconds: float = 0.0
    execution_latency_seconds: float = 0.0
    graph_latency_seconds: float = 0.0
    execution_steps: int = 0
    candidate_count: int = 0
    cost_proxy: float = 0.0
    violation_reason: str | None = None
    _started_at: float = 0.0

    def __post_init__(self) -> None:
        self._started_at = time.perf_counter()

    @property
    def strategy_wall_clock_seconds(self) -> float:
        return time.perf_counter() - self._started_at

    @property
    def remaining_generated_tokens(self) -> int:
        return max(0, self.max_generated_tokens - self.output_tokens)

    @property
    def remaining_latency_seconds(self) -> float:
        return max(0.0, self.max_latency_seconds - self.strategy_wall_clock_seconds)

    def _violate(self, message: str) -> None:
        self.violation_reason = message
        raise BudgetExceeded(message)

    def invalidate(self, message: str) -> None:
        self.violation_reason = message
        raise BudgetExceeded(message)

    def check_wall_clock(self) -> None:
        if self.strategy_wall_clock_seconds > self.max_latency_seconds:
            self._violate("max_latency_seconds exceeded")

    def reserve_call(self) -> None:
        self.check_wall_clock()
        if self.model_calls + 1 > self.max_model_calls:
            self._violate("max_model_calls exceeded")
        self.model_calls += 1

    def record_generation(self, result: GenerationResult) -> None:
        self.input_tokens += max(0, int(result.input_tokens or 0))
        self.output_tokens += max(0, int(result.output_tokens or 0))
        self.model_latency_seconds += max(0.0, float(result.latency_seconds or 0.0))
        self.cost_proxy += float(result.cost_proxy or 0.0)
        if self.max_input_tokens is not None and self.input_tokens > self.max_input_tokens:
            self._violate("max_input_tokens exceeded")
        if self.output_tokens > self.max_generated_tokens:
            self._violate("max_generated_tokens exceeded")
        self.check_wall_clock()

    def record_failed_call(self, latency_seconds: float) -> None:
        self.failed_model_calls += 1
        self.model_latency_seconds += max(0.0, float(latency_seconds))
        self.check_wall_clock()

    def record_retry(self) -> None:
        self.retries += 1

    def add_execution_step(self, latency_seconds: float = 0.0) -> None:
        if self.execution_steps + 1 > self.max_execution_steps:
            self._violate("max_execution_steps exceeded")
        self.execution_steps += 1
        self.execution_latency_seconds += max(0.0, float(latency_seconds))
        self.check_wall_clock()

    def add_candidate(self) -> None:
        if self.candidate_count + 1 > self.max_candidates:
            self._violate("max_candidates exceeded")
        self.candidate_count += 1

    def add_graph_latency(self, seconds: float) -> None:
        self.graph_latency_seconds += max(0.0, float(seconds))
        self.check_wall_clock()

    def snapshot(self) -> BudgetSnapshot:
        return BudgetSnapshot(
            model_calls=self.model_calls,
            failed_model_calls=self.failed_model_calls,
            retries=self.retries,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            total_generated_tokens=self.output_tokens,
            model_latency_seconds=self.model_latency_seconds,
            execution_latency_seconds=self.execution_latency_seconds,
            graph_latency_seconds=self.graph_latency_seconds,
            strategy_wall_clock_seconds=self.strategy_wall_clock_seconds,
            cost_proxy=self.cost_proxy,
            execution_steps=self.execution_steps,
            candidate_count=self.candidate_count,
            budget_violated=self.violation_reason is not None,
            violation_reason=self.violation_reason,
        )
