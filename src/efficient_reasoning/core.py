from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class GenerationResult:
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_seconds: float = 0.0
    cost_proxy: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Candidate:
    text: str
    model: str
    generation: GenerationResult
    candidate_id: str
    visible_pass: int | None = None
    visible_total: int | None = None
    visible_latency_seconds: float = 0.0


@dataclass
class StrategyResult:
    strategy: str
    answer: str
    candidates: list[Candidate] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    notes: dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetSnapshot:
    model_calls: int
    failed_model_calls: int
    retries: int
    input_tokens: int
    output_tokens: int
    total_generated_tokens: int
    model_latency_seconds: float
    execution_latency_seconds: float
    graph_latency_seconds: float
    strategy_wall_clock_seconds: float
    cost_proxy: float
    execution_steps: int
    candidate_count: int
    budget_violated: bool
    violation_reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TaskEvaluation:
    task_id: str
    visible_passed: int | None
    visible_total: int | None
    hidden_passed: int
    hidden_total: int
    executable: bool
    error: str | None
    latency_seconds: float
    execution_steps: int

    @property
    def hidden_pass_rate(self) -> float:
        return self.hidden_passed / self.hidden_total if self.hidden_total else 0.0

    @property
    def visible_pass_rate(self) -> float | None:
        if self.visible_total in (None, 0):
            return None
        return self.visible_passed / self.visible_total
