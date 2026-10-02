from __future__ import annotations

from dataclasses import dataclass, field, asdict
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
    visible_score: float | None = None
    visible_pass: int | None = None


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
    input_tokens: int
    output_tokens: int
    total_generated_tokens: int
    latency_seconds: float
    cost_proxy: float
    execution_steps: int
    candidate_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TaskEvaluation:
    task_id: str
    visible_passed: int
    visible_total: int
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
    def visible_pass_rate(self) -> float:
        return self.visible_passed / self.visible_total if self.visible_total else 0.0
