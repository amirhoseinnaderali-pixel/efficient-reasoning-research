# Efficient Reasoning in Language Models

Research infrastructure for studying how inference-time computational budget should be allocated across reasoning strategies.

## Research Question

> Under a fixed inference-time compute budget, which reasoning strategy provides the best objective correctness/compute trade-off?

This is an empirical question. No strategy is assumed to be superior before controlled measurement.

## Conditions

- **C0** — Single generation
- **C1** — Independent sampling / verifier-assisted Best-of-N
- **C2** — Sequential refinement
- **C3** — Multi-model generation / verifier-assisted selection
- **C4** — Multi-model sequential refinement
- **C5** — Execution-based feedback
- **C6** — Graph-based aggregation

## EXP-001 status

**IMPLEMENTED — NOT EXECUTED.**

The framework now enforces explicit call/token/time/execution/candidate budgets, separates visible selection from hidden final scoring, blocks mock adapters from real experiment configs, validates result schemas, and records reproducibility metadata.

The current 5-task transparent benchmark is a **pilot validation benchmark**, not sufficient by itself for a substantive empirical claim. Expand/freeze the benchmark and model configuration before treating EXP-001 as publication evidence.

## Objective evaluation

Real generated code is executed through Docker with no network, bounded resources, isolated writable `/tmp`, dropped Linux capabilities, no-new-privileges, and timeouts. The framework fails closed if Docker is unavailable.

## Statistical analysis

Results are analyzed per task-seed pair. The repository supports aggregate hidden pass rate, compute dimensions, bootstrap confidence intervals, and paired differences against C0. No single arbitrary score replaces the underlying dimensions.

## Mock validation

```bash
python scripts/run_experiment.py --config configs/default.yaml --mock
```

Mock outputs are stored only under `results/validation/` and are explicitly **software validation only**.

## Real EXP-001 commands

```bash
python scripts/validate_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/evaluate_results.py --input results/raw/EXP-001
python scripts/aggregate_results.py --input results/raw/EXP-001 --output results/tables/exp001.csv
python scripts/analyze_results.py --input results/raw/EXP-001 --output results/tables/exp001_statistics.json
```

## Prior Work

See [`docs/prior_work.md`](docs/prior_work.md) and [`docs/research_lineage.md`](docs/research_lineage.md). Previous repositories are read-only research artifacts; this repository reimplements concepts behind common interfaces rather than copying source trees.

## Reproducibility

Every real run captures git SHA, configuration hash, benchmark hash/version, seed, model pool, generation parameters, environment metadata, and budget usage. Results use unique batch files and cannot silently overwrite existing runs.

## Current Readiness

**READY WITH CONDITIONS for a real EXP-001 execution.** The software framework is methodologically guarded, but the 5-task pilot benchmark must be replaced or expanded and the exact real model pool must be frozen before experimental conclusions are admissible.
