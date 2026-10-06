# Research Lineage

```text
Early fine-tuning / adaptation
        ↓
Prompt-time reasoning
        ↓
Iterative reasoning
        ↓
Multi-stage reasoning
        ↓
Multi-model refinement
        ↓
Execution feedback
        ↓
Controlled compute allocation
        ↓
Graph-based aggregation
        ↓
Unified research framework
```

| Prior project | Reused concept | New module | Experiment |
|---|---|---|---|
| `LLM_reasoning_solve_NQueen_with_no_code` | sequential refinement | `strategies.py::SequentialRefinement` | EXP-001 C2 |
| `codechain` | call/correctness accounting | budget + evaluation | EXP-001 |
| `Reasoning-Is-All-You-Need` | execution debugging | `ExecutionFeedback` | EXP-001 C5 |
| `multi-agent-react-sandbox` | isolated execution | `verification/sandbox.py` | EXP-001 |
| `graph_reasoning` | graph candidate aggregation | `aggregation/graph.py` | EXP-001 C6 / EXP-002 |
