from __future__ import annotations
from dataclasses import dataclass
from ..core import BudgetSnapshot, GenerationResult
class BudgetExceeded(RuntimeError): pass
@dataclass
class Budget:
    max_model_calls:int; max_generated_tokens:int; max_latency_seconds:float; max_execution_steps:int; max_candidates:int
    model_calls:int=0; input_tokens:int=0; output_tokens:int=0; latency_seconds:float=0.0; execution_steps:int=0; candidate_count:int=0
    def reserve_call(self):
        if self.model_calls+1>self.max_model_calls: raise BudgetExceeded('max_model_calls exceeded')
        self.model_calls+=1
    def record_generation(self,r:GenerationResult):
        self.input_tokens+=int(r.input_tokens or 0); self.output_tokens+=int(r.output_tokens or 0); self.latency_seconds+=float(r.latency_seconds or 0)
        if self.output_tokens>self.max_generated_tokens: raise BudgetExceeded('max_generated_tokens exceeded')
        if self.latency_seconds>self.max_latency_seconds: raise BudgetExceeded('max_latency_seconds exceeded')
    def add_execution_step(self):
        if self.execution_steps+1>self.max_execution_steps: raise BudgetExceeded('max_execution_steps exceeded')
        self.execution_steps+=1
    def add_candidate(self):
        if self.candidate_count+1>self.max_candidates: raise BudgetExceeded('max_candidates exceeded')
        self.candidate_count+=1
    def snapshot(self,cost_proxy=0.0):
        return BudgetSnapshot(self.model_calls,self.input_tokens,self.output_tokens,self.output_tokens,self.latency_seconds,cost_proxy,self.execution_steps,self.candidate_count)
