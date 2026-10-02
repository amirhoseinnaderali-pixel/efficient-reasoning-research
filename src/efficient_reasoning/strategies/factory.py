from .strategies import Single,BestOfN,SequentialRefinement,MultiModel,MultiModelChain,ExecutionFeedback,GraphAggregation
def build_strategy(name,cfg,adapter,budget,evaluator,adapters=None):
    common=dict(adapter=adapter,budget=budget,evaluator=evaluator,adapters=adapters); t=cfg['type']
    if t=='single': return Single(**common)
    if t=='best_of_n': return BestOfN(**common,n=int(cfg.get('n',4)))
    if t=='sequential_refinement': return SequentialRefinement(**common,depth=int(cfg.get('depth',3)))
    if t=='multi_model': return MultiModel(**common)
    if t=='multi_model_chain': return MultiModelChain(**common)
    if t=='execution_feedback': return ExecutionFeedback(**common,max_iterations=int(cfg.get('max_iterations',3)))
    if t=='graph_aggregation': return GraphAggregation(**common,n=int(cfg.get('n',4)),graph=cfg.get('graph',{}))
    raise ValueError(t)
