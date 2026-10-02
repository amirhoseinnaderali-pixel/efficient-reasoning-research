from __future__ import annotations

import time

from ..aggregation.graph import select_by_graph
from ..core import Candidate, StrategyResult
from ..generation.parsing import extract_code
from .base import ReasoningStrategy


def prompt(task: dict) -> str:
    return (
        "You are solving a programming benchmark task. Return only Python code.\n\n"
        f"Problem:\n{task['problem']}\n\n"
        f"Function name: {task['entry_point']}"
    )


class Single(ReasoningStrategy):
    name = "c0_single"

    def solve(self, p, context=None):
        r = self._generate(self.adapter, prompt(p), p["id"], 0)
        c = Candidate(extract_code(r.text), r.model, r, "c0-0")
        return StrategyResult(self.name, c.text, [c], [{"step": "generate"}], selected_candidate_id=c.candidate_id, selected_model=c.model)


class BestOfN(ReasoningStrategy):
    name = "c1_best_of_n"

    def __init__(self, *a, n: int = 4, **k):
        super().__init__(*a, **k)
        self.n = n

    def solve(self, p, context=None):
        cs = []
        for i in range(self.n):
            r = self._generate(self.adapter, prompt(p) + f"\nIndependent candidate {i}.", p["id"], i)
            c = Candidate(extract_code(r.text), r.model, r, f"c1-{i}")
            if self.evaluator is not None:
                ev = self.evaluator.evaluate_visible(c.text, p)
                c.visible_pass = ev.passed
                c.visible_total = ev.total
                c.visible_latency_seconds = ev.latency_seconds
            cs.append(c)
        chosen = max(cs, key=lambda x: (x.visible_pass if x.visible_pass is not None else -1, x.candidate_id))
        return StrategyResult(
            self.name,
            chosen.text,
            cs,
            [{"selection": "visible_tests", "selection_is_objective_verifier_assisted": True}],
            {"selection_set": "visible"},
            selected_candidate_id=chosen.candidate_id,
            selected_model=chosen.model,
        )


class SequentialRefinement(ReasoningStrategy):
    name = "c2_sequential_refinement"

    def __init__(self, *a, depth: int = 3, **k):
        super().__init__(*a, **k)
        self.depth = depth

    def solve(self, p, context=None):
        cs = []
        cur = prompt(p)
        for i in range(self.depth):
            if i:
                cur = (
                    "Refine this solution for the same task. Return only corrected code.\n"
                    f"Problem: {p['problem']}\nPrevious:\n{cs[-1].text}"
                )
            r = self._generate(self.adapter, cur, p["id"], i)
            cs.append(Candidate(extract_code(r.text), r.model, r, f"c2-{i}"))
        return StrategyResult(
            self.name,
            cs[-1].text,
            cs,
            [{"depth": self.depth}],
            selected_candidate_id=cs[-1].candidate_id,
            selected_model=cs[-1].model,
        )


class MultiModel(ReasoningStrategy):
    name = "c3_multi_model"

    def solve(self, p, context=None):
        cs = []
        for i, adapter in enumerate(self.adapters):
            r = self._generate(adapter, prompt(p), p["id"], i)
            cs.append(Candidate(extract_code(r.text), r.model, r, f"c3-{i}"))
        if self.evaluator is not None:
            for c in cs:
                ev = self.evaluator.evaluate_visible(c.text, p)
                c.visible_pass = ev.passed
                c.visible_total = ev.total
                c.visible_latency_seconds = ev.latency_seconds
            chosen = max(cs, key=lambda x: (x.visible_pass if x.visible_pass is not None else -1, x.candidate_id))
            selection = "visible_tests"
        else:
            chosen = cs[0]
            selection = "first_candidate"
        return StrategyResult(
            self.name,
            chosen.text,
            cs,
            [{"models": [c.model for c in cs], "selection": selection, "selection_is_objective_verifier_assisted": True}],
            selected_candidate_id=chosen.candidate_id,
            selected_model=chosen.model,
        )


class MultiModelChain(ReasoningStrategy):
    name = "c4_multi_model_chain"

    def solve(self, p, context=None):
        cs = []
        cur = prompt(p)
        for i, adapter in enumerate(self.adapters):
            if i:
                cur = (
                    "Review and improve this code. Return only corrected code.\n"
                    f"Problem: {p['problem']}\nCurrent:\n{cs[-1].text}"
                )
            r = self._generate(adapter, cur, p["id"], i)
            cs.append(Candidate(extract_code(r.text), r.model, r, f"c4-{i}"))
        return StrategyResult(
            self.name,
            cs[-1].text,
            cs,
            [{"chain": True}],
            selected_candidate_id=cs[-1].candidate_id,
            selected_model=cs[-1].model,
        )


class ExecutionFeedback(ReasoningStrategy):
    name = "c5_execution_feedback"

    def __init__(self, *a, max_iterations: int = 3, **k):
        super().__init__(*a, **k)
        self.max_iterations = max_iterations

    def solve(self, p, context=None):
        cs = []
        cur = prompt(p)
        for i in range(self.max_iterations):
            r = self._generate(self.adapter, cur, p["id"], i)
            c = Candidate(extract_code(r.text), r.model, r, f"c5-{i}")
            cs.append(c)
            if self.evaluator is None:
                break
            ev = self.evaluator.evaluate_visible(c.text, p)
            c.visible_pass = ev.passed
            c.visible_total = ev.total
            c.visible_latency_seconds = ev.latency_seconds
            if ev.passed == ev.total:
                break
            cur = (
                "Debug this code from execution feedback. Return only corrected code.\n"
                f"Problem: {p['problem']}\nCandidate:\n{c.text}\n"
                f"Feedback: visible tests passed {ev.passed}/{ev.total}; {ev.error or 'at least one visible test failed'}"
            )
        return StrategyResult(
            self.name,
            cs[-1].text,
            cs,
            [{"iterations": len(cs), "feedback_suite": "visible"}],
            selected_candidate_id=cs[-1].candidate_id,
            selected_model=cs[-1].model,
        )


class GraphAggregation(ReasoningStrategy):
    name = "c6_graph_aggregation"

    def __init__(self, *a, n: int = 4, graph=None, **k):
        super().__init__(*a, **k)
        self.n = n
        self.graph = graph or {}

    def solve(self, p, context=None):
        cs = []
        for i in range(self.n):
            r = self._generate(self.adapter, prompt(p) + f"\nGenerate candidate {i}.", p["id"], i)
            cs.append(Candidate(extract_code(r.text), r.model, r, f"c6-{i}"))
        method = self.graph.get("method")
        self.budget.check_wall_clock()
        started = time.perf_counter()
        idx, graph = select_by_graph([c.text for c in cs], int(self.graph["k"]), method=method)
        self.budget.add_graph_latency(time.perf_counter() - started)
        chosen = cs[idx]
        return StrategyResult(
            self.name,
            chosen.text,
            cs,
            [{"graph": graph, "selection_uses_objective_tests": False}],
            {"graph_selector": "degree_centrality", "graph_method": method},
            selected_candidate_id=chosen.candidate_id,
            selected_model=chosen.model,
        )
