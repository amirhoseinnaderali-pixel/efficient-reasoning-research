# Methodology

## Unit of comparison

One observation is a `(task, seed, strategy)` run. All strategies receive the same task and paired seed schedule.

## Common generation contract

`ReasoningStrategy._generate()` is the only path from a strategy to a model adapter. It enforces remaining model-call, output-token, candidate, and wall-clock budgets and records the generation parameters and per-candidate seed.

## Strategy conditions

### C0 — Single
One generation call; no visible-test selection.

### C1 — Best-of-N
N independent generations from the common model; visible tests may select the candidate. This is explicitly verifier-assisted Best-of-N.

### C2 — Sequential refinement
The previous candidate is fed back to the same model for a configured number of refinement rounds.

### C3 — Multi-model generation
One candidate per configured model. Visible tests select the final candidate. The heterogeneous model pool is part of the condition.

### C4 — Multi-model chain
Each model sees the previous candidate and returns a revision. No objective test result is used before final scoring.

### C5 — Execution feedback
The generated candidate is executed against visible tests; the resulting aggregate pass/fail signal is fed back into the next generation. The strategy can stop early when all visible tests pass.

### C6 — Graph aggregation
N candidates are generated from the primary model, a TF-IDF/cosine k-NN graph is built from candidate text, and the highest weighted degree candidate is selected. Objective test results are not available to the graph selector.

## Final evaluation

The strategy output is scored only against the hidden suite. The hidden suite is not passed to any strategy implementation.

## Interpretation

No condition is assigned a winner in advance. Efficiency analyses retain separate dimensions for calls, input/output tokens, model latency, verifier latency, graph latency, wall-clock time, and cost proxy.
