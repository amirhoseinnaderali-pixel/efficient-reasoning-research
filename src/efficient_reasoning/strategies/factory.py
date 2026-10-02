from .strategies import (
    BestOfN,
    ExecutionFeedback,
    GraphAggregation,
    MultiModel,
    MultiModelChain,
    SequentialRefinement,
    Single,
)


def build_strategy(name, cfg, adapter, budget, evaluator, adapters=None, generation=None, seed=42):
    common = dict(adapter=adapter, budget=budget, evaluator=evaluator, adapters=adapters, generation=generation, seed=seed)
    t = cfg["type"]
    if t == "single":
        return Single(**common)
    if t == "best_of_n":
        return BestOfN(**common, n=int(cfg["n"]))
    if t == "sequential_refinement":
        return SequentialRefinement(**common, depth=int(cfg["depth"]))
    if t == "multi_model":
        return MultiModel(**common)
    if t == "multi_model_chain":
        return MultiModelChain(**common)
    if t == "execution_feedback":
        return ExecutionFeedback(**common, max_iterations=int(cfg["max_iterations"]))
    if t == "graph_aggregation":
        return GraphAggregation(**common, n=int(cfg["n"]), graph=cfg["graph"])
    raise ValueError(f"Unknown strategy type: {t}")
