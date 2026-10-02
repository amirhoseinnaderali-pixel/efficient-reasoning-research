from __future__ import annotations
from abc import ABC,abstractmethod
from ..core import StrategyResult
class ReasoningStrategy(ABC):
    def __init__(self,adapter,budget,evaluator=None,adapters=None): self.adapter=adapter; self.budget=budget; self.evaluator=evaluator; self.adapters=adapters or [adapter]
    @abstractmethod
    def solve(self,problem,context=None)->StrategyResult: ...
    def _generate(self,adapter,prompt,task_id):
        self.budget.reserve_call(); adapter.config['task_id']=task_id; r=adapter.generate(prompt,max_tokens=min(1200,self.budget.max_generated_tokens)); self.budget.record_generation(r); self.budget.add_candidate(); return r
