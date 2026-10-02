from efficient_reasoning.aggregation.graph import build_graph
from efficient_reasoning.budgeting.budget import Budget, BudgetExceeded
from efficient_reasoning.core import GenerationResult
from efficient_reasoning.evaluation.evaluator import ObjectiveEvaluator, VisibleEvaluator
from efficient_reasoning.logging.schema import validate_result
from efficient_reasoning.models.adapters import MockAdapter
from efficient_reasoning.strategies.strategies import BestOfN, GraphAggregation
from efficient_reasoning.verification.sandbox import MockExecutor


TASK = {
    "id": "add_two_numbers",
    "problem": "return the sum",
    "entry_point": "add_two_numbers",
    "tests": {
        "visible": [{"args": [1, 2], "expected": 3}],
        "hidden": [{"args": [2, 5], "expected": 7}],
    },
}


class TrackingExecutor(MockExecutor):
    def __init__(self):
        super().__init__()
        self.suites = []

    def run(self, code, task, suite="visible", timeout_seconds=None):
        self.suites.append(suite)
        return super().run(code, task, suite, timeout_seconds)


class RecordingAdapter(MockAdapter):
    def __init__(self, model="mock", **kwargs):
        super().__init__(model, **kwargs)
        self.seeds = []

    def generate(self, *args, **kwargs):
        self.seeds.append(kwargs.get("seed"))
        return super().generate(*args, **kwargs)


def test_best_of_n_uses_visible_only_for_selection_and_hidden_is_never_called():
    executor = TrackingExecutor()
    budget = Budget(8, 200, 10, 12, 8)
    evaluator = VisibleEvaluator(executor, budget)
    final_evaluator = ObjectiveEvaluator(executor, budget)
    strategy = BestOfN(
        RecordingAdapter(task_id=TASK["id"]),
        budget,
        evaluator,
        n=2,
        generation={"max_output_tokens_per_call": 50, "temperature": 0.0, "top_p": 1.0, "timeout_seconds": 5},
        seed=10,
    )
    result = strategy.solve(TASK)
    assert executor.suites == ["visible", "visible"]
    assert all(candidate.visible_total == 1 for candidate in result.candidates)
    final_evaluator.evaluate_final(result.answer, TASK)
    assert executor.suites[-1] == "hidden"


def test_graph_selection_does_not_call_objective_verifier():
    executor = TrackingExecutor()
    budget = Budget(8, 200, 10, 12, 8)
    evaluator = VisibleEvaluator(executor, budget)
    strategy = GraphAggregation(
        MockAdapter(task_id=TASK["id"]),
        budget,
        evaluator,
        n=4,
        graph={"method": "tfidf_cosine", "k": 2},
        generation={"max_output_tokens_per_call": 50, "temperature": 0.0, "top_p": 1.0, "timeout_seconds": 5},
        seed=10,
    )
    strategy.solve(TASK)
    assert executor.suites == []


def test_graph_rejects_unconfigured_method():
    try:
        build_graph(["a", "b"], k=1, method="hidden_test_score")
    except ValueError:
        return
    raise AssertionError("unsupported graph method must fail loudly")


def test_seed_sequence_is_explicit_and_deterministic():
    budget = Budget(4, 100, 10, 4, 4)
    adapter = RecordingAdapter(task_id=TASK["id"])
    strategy = BestOfN(
        adapter,
        budget,
        evaluator=None,
        n=2,
        generation={"max_output_tokens_per_call": 20, "temperature": 0.0, "top_p": 1.0, "timeout_seconds": 5},
        seed=123,
    )
    strategy.solve(TASK)
    assert adapter.seeds == [123, 124]


def test_result_schema_rejects_malformed_rows():
    try:
        validate_result({"status": "completed"})
    except ValueError:
        return
    raise AssertionError("malformed result must fail schema validation")

def test_result_schema_requires_reproducibility_provenance():
    row = {
        "experiment_id": "EXP-001",
        "run_id": "r1",
        "timestamp": "2026-10-02T00:00:00Z",
        "strategy": "c0_single",
        "model": "m",
        "model_pool": ["m"],
        "selected_candidate_id": "c0-0",
        "generation_config": {},
        "config_path": "c",
        "benchmark": {"name": "b", "version": "1", "sha256": "x"},
        "seed": 42,
        "task_id": "t1",
        "budget": {
            "model_calls": 1,
            "failed_model_calls": 0,
            "retries": 0,
            "input_tokens": 1,
            "output_tokens": 1,
            "total_generated_tokens": 1,
            "model_latency_seconds": 0.1,
            "execution_latency_seconds": 0.1,
            "graph_latency_seconds": 0.0,
            "strategy_wall_clock_seconds": 0.2,
            "cost_proxy": 0.0,
            "cost_proxy_status": "available",
            "execution_steps": 1,
            "candidate_count": 1,
            "budget_violated": False,
            "violation_reason": None,
        },
        "metrics": {"hidden_pass_rate": 1.0},
        "environment": {
            "git_sha": "a" * 40,
            "config_sha256": "b" * 64,
            "benchmark_sha256": "x",
            "python": "3.12",
            "platform": "test",
            "model_config": {"m": {"model_id": "m"}},
            "execution": {"backend": "docker"},
        },
        "status": "completed",
        "error": None,
        "evaluation": {
            "hidden_passed": 1,
            "hidden_total": 1,
            "hidden_pass_rate": 1.0,
            "executable": True,
            "error": None,
            "error_kind": None,
            "latency_seconds": 0.1,
            "execution_steps": 1,
        },
        "candidates": [],
        "trace": [],
        "notes": {},
    }
    validate_result(row)
    row["environment"].pop("git_sha")
    try:
        validate_result(row)
    except ValueError:
        return
    raise AssertionError("result provenance must require git_sha")
