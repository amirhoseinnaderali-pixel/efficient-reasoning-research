from __future__ import annotations

from ..core import TaskEvaluation


class ObjectiveEvaluator:
    """Objective evaluator; hidden labels are never exposed to strategies."""

    def __init__(self, executor, budget):
        self.executor = executor
        self.budget = budget

    def evaluate_visible(self, code, task):
        result = self.executor.run(code, task, "visible", timeout_seconds=self.budget.remaining_latency_seconds)
        self.budget.add_execution_step(result.latency_seconds)
        return result

    def evaluate_hidden(self, code, task) -> TaskEvaluation:
        result = self.executor.run(code, task, "hidden", timeout_seconds=self.budget.remaining_latency_seconds)
        self.budget.add_execution_step(result.latency_seconds)
        return TaskEvaluation(
            task_id=task["id"],
            visible_passed=None,
            visible_total=None,
            hidden_passed=result.passed,
            hidden_total=result.total,
            executable=result.error is None,
            error=result.error,
            latency_seconds=result.latency_seconds,
            execution_steps=1,
        )

    def evaluate_final(self, code, task) -> TaskEvaluation:
        """Final scoring uses only the held-out hidden suite."""
        return self.evaluate_hidden(code, task)
