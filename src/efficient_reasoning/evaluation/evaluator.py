from __future__ import annotations
from ..core import TaskEvaluation

class ObjectiveEvaluator:
    def __init__(self, executor, budget):
        self.executor = executor
        self.budget = budget

    def evaluate(self, code, task, include_hidden=True):
        self.budget.add_execution_step()
        v = self.executor.run(code, task, "visible")
        if not include_hidden:
            return TaskEvaluation(task["id"], v.passed, v.total, 0, 0, v.error is None, v.error, v.latency_seconds, 1)
        self.budget.add_execution_step()
        h = self.executor.run(code, task, "hidden")
        return TaskEvaluation(task["id"], v.passed, v.total, h.passed, h.total, h.error is None, h.error or v.error, v.latency_seconds + h.latency_seconds, 2)
