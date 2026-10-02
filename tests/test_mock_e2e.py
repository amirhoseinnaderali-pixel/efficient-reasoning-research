from efficient_reasoning.budgeting.budget import Budget
from efficient_reasoning.evaluation.evaluator import ObjectiveEvaluator, VisibleEvaluator
from efficient_reasoning.models.adapters import MockAdapter
from efficient_reasoning.strategies.strategies import Single
from efficient_reasoning.verification.sandbox import MockExecutor


def test_mock_e2e():
    t = {
        "id": "add_two_numbers",
        "problem": "write add_two_numbers",
        "entry_point": "add_two_numbers",
        "tests": {"visible": [{"args": [1, 2], "expected": 3}], "hidden": [{"args": [2, 5], "expected": 7}]},
    }
    budget = Budget(2, 100, 10, 4, 2)
    evaluator = VisibleEvaluator(MockExecutor(), budget)
    final_evaluator = ObjectiveEvaluator(evaluator.executor, budget)
    result = Single(MockAdapter(task_id=t["id"]), budget, evaluator).solve(t)
    evaluation = final_evaluator.evaluate_final(result.answer, t)
    assert evaluation.hidden_passed == 1
    assert budget.execution_steps == 1
