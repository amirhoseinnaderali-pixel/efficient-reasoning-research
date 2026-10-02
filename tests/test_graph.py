from efficient_reasoning.aggregation.graph import build_graph,select_by_graph

def test_graph_builds():
 g=build_graph(['def add(a,b): return a+b','def sum(a,b): return a+b','unrelated text'],1); assert len(g['nodes'])==3 and g['edges']
 i,_=select_by_graph(['same same','same same','different'],1); assert i in (0,1)
