from efficient_reasoning.budgeting.budget import Budget
from efficient_reasoning.evaluation.evaluator import ObjectiveEvaluator
from efficient_reasoning.models.adapters import MockAdapter
from efficient_reasoning.strategies.factory import build_strategy
from efficient_reasoning.verification.sandbox import MockExecutor


TASK = {
    "id": "add_two_numbers",
    "problem": "return the sum",
    "entry_point": "add_two_numbers",
    "tests": {"visible": [{"args": [1, 2], "expected": 3}], "hidden": [{"args": [2, 5], "expected": 7}]},
}
GEN = {"max_output_tokens_per_call": 50, "temperature": 0.0, "top_p": 1.0, "timeout_seconds": 5}


def test_all_conditions_fit_the_common_contract_and_budget():
    specs = {
        "c0_single": {"type": "single"},
        "c1_best_of_n": {"type": "best_of_n", "n": 2},
        "c2_sequential_refinement": {"type": "sequential_refinement", "depth": 2},
        "c3_multi_model": {"type": "multi_model"},
        "c4_multi_model_chain": {"type": "multi_model_chain"},
        "c5_execution_feedback": {"type": "execution_feedback", "max_iterations": 2},
        "c6_graph_aggregation": {"type": "graph_aggregation", "n": 2, "graph": {"method": "tfidf_cosine", "k": 1}},
    }
    for name, cfg in specs.items():
        budget = Budget(8, 500, 30, 12, 8)
        evaluator = ObjectiveEvaluator(MockExecutor(), budget)
        adapters = [MockAdapter("mock-a", task_id=TASK["id"]), MockAdapter("mock-b", task_id=TASK["id"])]
        strategy = build_strategy(name, cfg, adapters[0], budget, evaluator, adapters, generation=GEN, seed=5)
        result = strategy.solve(TASK)
        assert result.strategy == name
        assert result.answer
        assert budget.model_calls <= 8
        assert budget.candidate_count <= 8
        assert budget.execution_steps <= 12
        evaluator.evaluate_final(result.answer, TASK)
        assert budget.execution_steps <= 12
