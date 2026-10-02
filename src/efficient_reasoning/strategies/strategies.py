from ..core import Candidate,StrategyResult
from ..generation.parsing import extract_code
from ..aggregation.graph import select_by_graph
from .base import ReasoningStrategy

def prompt(task): return f"You are solving a programming benchmark task. Return only Python code.\n\nProblem:\n{task['problem']}\n\nFunction name: {task['entry_point']}"
class Single(ReasoningStrategy):
    name='c0_single'
    def solve(self,p,context=None):
        r=self._generate(self.adapter,prompt(p),p['id']); c=Candidate(extract_code(r.text),r.model,r,'c0-0'); return StrategyResult(self.name,c.text,[c],[{'step':'generate'}])
class BestOfN(ReasoningStrategy):
    name='c1_best_of_n'
    def __init__(self,*a,n=4,**k): super().__init__(*a,**k); self.n=n
    def solve(self,p,context=None):
        cs=[]
        for i in range(self.n):
            r=self._generate(self.adapter,prompt(p)+f'\nIndependent candidate {i}.',p['id']); c=Candidate(extract_code(r.text),r.model,r,f'c1-{i}')
            if self.evaluator: ev=self.evaluator.evaluate(c.text,p,include_hidden=False); c.visible_pass=ev.visible_passed; c.visible_score=ev.visible_pass_rate
            cs.append(c)
        c=max(cs,key=lambda x:(x.visible_pass if x.visible_pass is not None else 0,x.candidate_id)); return StrategyResult(self.name,c.text,cs,[{'selection':'visible_tests'}],{'selection_set':'visible'})
class SequentialRefinement(ReasoningStrategy):
    name='c2_sequential_refinement'
    def __init__(self,*a,depth=3,**k): super().__init__(*a,**k); self.depth=depth
    def solve(self,p,context=None):
        cs=[]; cur=prompt(p)
        for i in range(self.depth):
            if i: cur=f"Refine this solution for the same task. Return only corrected code.\nProblem: {p['problem']}\nPrevious:\n{cs[-1].text}"
            r=self._generate(self.adapter,cur,p['id']); cs.append(Candidate(extract_code(r.text),r.model,r,f'c2-{i}'))
        return StrategyResult(self.name,cs[-1].text,cs,[{'depth':self.depth}])
class MultiModel(ReasoningStrategy):
    name='c3_multi_model'
    def solve(self,p,context=None):
        cs=[Candidate(extract_code((r:=self._generate(a,prompt(p),p['id'])).text),r.model,r,f'c3-{i}') for i,a in enumerate(self.adapters)]
        if self.evaluator:
            for c in cs: ev=self.evaluator.evaluate(c.text,p,include_hidden=False); c.visible_pass=ev.visible_passed; c.visible_score=ev.visible_pass_rate
            chosen=max(cs,key=lambda x:(x.visible_pass or 0,x.candidate_id))
        else: chosen=cs[0]
        return StrategyResult(self.name,chosen.text,cs,[{'models':[c.model for c in cs]}])
class MultiModelChain(ReasoningStrategy):
    name='c4_multi_model_chain'
    def solve(self,p,context=None):
        cs=[]; cur=prompt(p)
        for i,a in enumerate(self.adapters):
            if i: cur=f"Review and improve this code. Return only corrected code.\nProblem: {p['problem']}\nCurrent:\n{cs[-1].text}"
            r=self._generate(a,cur,p['id']); cs.append(Candidate(extract_code(r.text),r.model,r,f'c4-{i}'))
        return StrategyResult(self.name,cs[-1].text,cs,[{'chain':True}])
class ExecutionFeedback(ReasoningStrategy):
    name='c5_execution_feedback'
    def __init__(self,*a,max_iterations=3,**k): super().__init__(*a,**k); self.max_iterations=max_iterations
    def solve(self,p,context=None):
        cs=[]; cur=prompt(p)
        for i in range(self.max_iterations):
            r=self._generate(self.adapter,cur,p['id']); c=Candidate(extract_code(r.text),r.model,r,f'c5-{i}'); cs.append(c)
            if not self.evaluator: break
            ev=self.evaluator.evaluate(c.text,p,include_hidden=False); c.visible_pass=ev.visible_passed; c.visible_score=ev.visible_pass_rate
            if ev.visible_passed==ev.visible_total: break
            cur=f"Debug this code from execution feedback. Return only corrected code.\nProblem: {p['problem']}\nCandidate:\n{c.text}\nFeedback: {ev.error or 'visible tests failed'}"
        return StrategyResult(self.name,cs[-1].text,cs,[{'iterations':len(cs)}])
class GraphAggregation(ReasoningStrategy):
    name='c6_graph_aggregation'
    def __init__(self,*a,n=4,graph=None,**k): super().__init__(*a,**k); self.n=n; self.graph=graph or {}
    def solve(self,p,context=None):
        cs=[Candidate(extract_code((r:=self._generate(self.adapter,prompt(p)+f'\nGenerate candidate {i}.',p['id'])).text),r.model,r,f'c6-{i}') for i in range(self.n)]
        idx,g=select_by_graph([c.text for c in cs],int(self.graph.get('k',2))); chosen=cs[idx]
        if self.evaluator:
            for c in cs: ev=self.evaluator.evaluate(c.text,p,include_hidden=False); c.visible_pass=ev.visible_passed; c.visible_score=ev.visible_pass_rate
        return StrategyResult(self.name,chosen.text,cs,[{'graph':g}],{'graph_selector':'degree_centrality'})
