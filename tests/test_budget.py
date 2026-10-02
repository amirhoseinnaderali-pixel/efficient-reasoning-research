import pytest
from efficient_reasoning.budgeting.budget import Budget, BudgetExceeded
from efficient_reasoning.core import GenerationResult

def test_budget_accounting():
    b=Budget(2,10,10,2,3); b.reserve_call(); b.record_generation(GenerationResult('x','m',2,4,0.1)); b.add_candidate(); s=b.snapshot()
    assert (s.model_calls,s.output_tokens,s.total_generated_tokens)==(1,4,4)

def test_budget_rejects_output_limit():
    b=Budget(1,1,10,2,2); b.reserve_call()
    with pytest.raises(BudgetExceeded): b.record_generation(GenerationResult('x','m',0,2))
