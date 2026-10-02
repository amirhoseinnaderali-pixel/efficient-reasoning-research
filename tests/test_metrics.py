from efficient_reasoning.evaluation.metrics import pareto_front

def test_pareto():
 pts=[{'compute':1,'correctness':.5},{'compute':2,'correctness':.6},{'compute':3,'correctness':.55}]; f=pareto_front(pts); assert pts[0] in f and pts[1] in f and pts[2] not in f
