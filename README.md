# Efficient Reasoning in Language Models

Research infrastructure for studying how inference-time computational budget should be allocated across reasoning strategies.

## Research Question

> Under a fixed inference-time compute budget, which reasoning strategy provides the best objective correctness/compute trade-off?

The repository treats this as an empirical question. No strategy is assumed to be superior before controlled measurement.

## Motivation

The project synthesizes several prior prototypes into one measurable framework: prompt-time refinement, multi-stage agents, multi-model generation, execution feedback, and graph-based aggregation. The emphasis is on **objective correctness, explicit compute accounting, reproducibility, and scientific traceability** rather than demo behavior.

## Hypotheses

- **H1 — test-time allocation:** distributing a fixed budget differently across independent sampling, refinement, heterogeneous models, execution feedback, and aggregation may produce different correctness/compute frontiers.
- **H2 — objective verification:** execution-based evaluation provides a stronger primary signal for programming tasks than LLM-judge scores.
- **H3 — graph aggregation:** graph structure may expose useful cross-candidate information, but its value is a hypothesis to be measured.
- **H4 — training lineage:** prior fine-tuning/distillation work can inform model selection, but EXP-001 isolates inference-time strategies unless a training condition is explicitly configured.

## Prior Work

See [`docs/prior_work.md`](docs/prior_work.md) and [`docs/research_lineage.md`](docs/research_lineage.md). Existing repositories are treated as read-only artifacts; this repository reimplements ideas behind common interfaces instead of copying source trees.

## Experimental Framework

```text
problem
  |
  +--> model adapter(s)
  |
  +--> reasoning strategy
  |
  +--> budget tracker
  |
  +--> optional execution verifier
  |
  +--> structured result
  |
  +--> objective analysis / Pareto frontier
```

Common strategies:

- C0 — Single generation
- C1 — Best-of-N independent sampling
- C2 — Sequential refinement
- C3 — Multi-model generation
- C4 — Multi-model sequential chain
- C5 — Execution-based feedback
- C6 — Graph aggregation

## EXP-001 — Fixed-Budget Reasoning Benchmark

**Status:** IMPLEMENTED — NOT EXECUTED with external models.

The experiment is configured to compare all seven conditions under explicit budgets. It uses a small transparent programming benchmark with deterministic visible and hidden tests. Candidate selection can use visible tests while final correctness is measured on the held-out set.

Run with a real adapter only after the configuration has been validated:

```bash
python scripts/validate_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/evaluate_results.py --input results/raw
python scripts/aggregate_results.py --input results/raw --output results/tables/exp001.csv
```

A mock smoke test is intentionally separate from EXP-001 and is never presented as experimental evidence:

```bash
python scripts/run_experiment.py --config configs/default.yaml --mock
```

## Metrics

Primary:

- executable pass rate
- pass@1
- best-of-N pass rate where relevant

Secondary:

- model calls
- input tokens
- output tokens
- total generated tokens
- latency
- execution/debugging steps
- cost proxy when supplied by the adapter

The framework keeps these dimensions separate. It does not collapse them into an arbitrary single score.

## Reproducibility

Every run captures configuration, seed, environment, model configuration, benchmark version, and git SHA when available. Raw machine-readable results are written as JSONL.

## Current Status

- Framework: implemented
- Unit tests: implemented and runnable without external APIs
- CI configuration: implemented
- EXP-001: implemented, not executed with real models
- Controlled empirical results: **none yet**

## Results

No controlled result tables or figures are committed until real result files exist. Historical results from prior repositories are documented as historical evidence only.

## Limitations

The first benchmark is intentionally small. Model APIs, tokenizer accounting, hardware-dependent latency, and sandbox image availability can change across environments. The framework records these details rather than treating one compute dimension as universally equivalent to another.

## Future Experiments

- EXP-002 — graph construction and aggregation ablations
- EXP-003 — execution-feedback allocation under fixed call/token budgets
- broader benchmark adapters after the transparent benchmark is validated
- training/adaptation conditions as separate experiments rather than confounds inside EXP-001

## License

MIT
