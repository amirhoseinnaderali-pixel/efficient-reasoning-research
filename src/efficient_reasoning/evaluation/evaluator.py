from __future__ import annotations

from ..budgeting.budget import BudgetExceeded
from ..core import TaskEvaluation


class VisibleEvaluator:
    """Strategy-side evaluator exposing only the permitted visible suite."""

    def __init__(self, executor, budget):
        self.executor = executor
        self.budget = budget

    def evaluate_visible(self, code, task):
        self.budget.ensure_execution_step_available()
        remaining = self.budget.remaining_latency_seconds
        if remaining <= 0:
            raise BudgetExceeded("No wall-clock budget remains before visible evaluation")
        result = self.executor.run(code, task, "visible", timeout_seconds=remaining)
        self.budget.add_execution_step(result.latency_seconds)
        return result


class ObjectiveEvaluator:
    """Final objective evaluator; hidden labels are not exposed to strategies."""

    def __init__(self, executor, budget):
        self.executor = executor
        self.budget = budget

    def evaluate_hidden(self, code, task) -> TaskEvaluation:
        self.budget.ensure_execution_step_available()
        remaining = self.budget.remaining_latency_seconds
        if remaining <= 0:
            raise BudgetExceeded("No wall-clock budget remains before hidden evaluation")
        result = self.executor.run(code, task, "hidden", timeout_seconds=remaining)
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
