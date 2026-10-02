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

The 5-task transparent benchmark remains validation-only. EXP-001 now uses a frozen 100-task HumanEval-derived manifest with source/test hashes and a deterministic visible/hidden split.

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

Prepare and validate the frozen inputs first:

```bash
python scripts/materialize_exp001_benchmark.py \
  --manifest benchmarks/manifests/exp001_v1.json \
  --output benchmarks/programming/exp001_v1/tasks.jsonl
python scripts/validate_readiness.py
```

Only after the preparation gate has passed should the real experiment command be used:

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

## Readiness and execution status

The **research configuration** is frozen: EXP-001 uses a 100-task HumanEval-derived manifest, exact dated model snapshots, an immutable Docker image digest, paired seeds `[42, 43, 44]`, explicit strategy model pools, and hard preflight validation.

Local **runtime readiness is environment-dependent** and is not implied by the repository state. Use:

```bash
python scripts/validate_readiness.py
python scripts/validate_execution_environment.py
```

Both commands fail closed when a real prerequisite is missing. The one-task `EXECUTION_SMOKE_TEST` is a separate execution-path check; it is not EXP-001.

**EXP-001: NOT EXECUTED.** No empirical result is claimed.
