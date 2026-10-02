# Efficient Reasoning in Language Models

Research infrastructure for studying how inference-time computational budget should be allocated across reasoning strategies.

## Research Question

> Under a fixed inference-time compute budget, how do different reasoning strategies compare in objective correctness and compute efficiency?

This is an empirical question. No strategy is assumed to be superior before controlled measurement.

## Conditions

- **C0** — Single generation
- **C1** — Independent sampling / verifier-assisted Best-of-N
- **C2** — Sequential refinement
- **C3** — Multi-model generation / verifier-assisted selection
- **C4** — Multi-model sequential refinement
- **C5** — Execution-based feedback
- **C6** — Graph-based aggregation

## Historical empirical evidence

The repository history was audited for committed raw runs, JSON/JSONL outputs, CSV tables, logs, plots, experiment configs, and execution records.

**Historical empirical result: none recovered.**

The only completed multi-condition execution recoverable from the repository is the **mock validation path**:

- 5-task validation benchmark
- C0–C6
- 1 validation seed
- mock/canned outputs
- 35 documented validation-only rows

Those rows are **software-validation artifacts, not model or benchmark evidence**. No real-model correctness, token usage, latency, or strategy comparison is claimed from them.

A separate real `EXECUTION_SMOKE_TEST` path was audited, but the final run stopped fail-closed before model inference because the real-model credential was unavailable in the hosted audit; the current execution runtime also lacks Docker CLI access.

See the full evidence audit and traceability record in [`docs/research_report.md`](docs/research_report.md).

## EXP-001 status

**IMPLEMENTED / SCIENTIFICALLY READY / NOT EXECUTED**

The current hardened EXP-001 is a **future research instrument**, not a historical result. It freezes a 100-task HumanEval-derived benchmark, paired seeds [42, 43, 44], explicit model pools, hard call/token/time/execution/candidate budgets, visible-selection / hidden-final separation, reproducibility metadata, and fail-closed readiness checks.

The 5-task transparent benchmark remains validation-only.

## Objective evaluation

Real generated code is intended to be executed through Docker with no network, bounded resources, isolated `/tmp`, dropped Linux capabilities, no-new-privileges, and timeouts. The framework fails closed if required execution infrastructure is unavailable.

## Statistical analysis

For real results, the repository supports per task-seed analysis, hidden pass rate, separate compute dimensions, bootstrap confidence intervals, and paired differences against C0. No arbitrary single score replaces the underlying dimensions.

Because no historical empirical rows are available, **no historical confidence interval, significance claim, or strategy ranking is reported**.

## Validation

The mock validation command is:

```bash
python scripts/run_experiment.py --config configs/default.yaml --mock
```

Mock results are explicitly validation-only. Real experimental results belong under `results/raw/EXP-00X/` and require real model adapters plus the controlled execution backend.

## Real EXP-001 commands

Prepare and validate the frozen inputs first:

```bash
python scripts/materialize_exp001_benchmark.py \
  --manifest benchmarks/manifests/exp001_v1.json \
  --output benchmarks/programming/exp001_v1/tasks.jsonl
python scripts/validate_readiness.py
```

Only after the preparation gate passes should the real experiment command be used:

```bash
python scripts/validate_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/evaluate_results.py --input results/raw/EXP-001
python scripts/aggregate_results.py --input results/raw/EXP-001 --output results/tables/exp001.csv
python scripts/analyze_results.py --input results/raw/EXP-001 --output results/tables/exp001_statistics.json
```

## Main observed findings

The recoverable historical evidence supports only these statements:

1. The multi-strategy framework has a working mock validation path and its CI history shows that path was executed.
2. The validation path is explicitly isolated from empirical result directories and is not suitable for model-performance claims.
3. The hardened EXP-001 protocol exists and has been audited, but it has not produced empirical strategy results.

There is therefore **no evidence in this repository that additional reasoning calls improve objective correctness, reduce compute cost, or create a better correctness/compute frontier**. Those remain open empirical questions.

## Conclusion

This repository currently demonstrates a validated research instrument and a clearly documented research question, but **not a completed empirical comparison of C0–C6**.

Any future claim about strategy quality must be derived from real, integrity-checked result files and recomputed analysis rather than from mock outputs, readiness checks, or documentation summaries.

## Limitations

- The 5-task transparent benchmark is validation-only.
- EXP-001's 100-task HumanEval-derived benchmark has no real run results yet.
- No historical real-model provider comparison is available.
- Configured budget ceilings are not observed compute measurements.
- Cross-provider token counts, hardware latency, and sandbox availability can vary by environment.
- Historical raw run metadata and result archives are absent from the visible repository tree.
- Validation-only artifacts cannot support hidden-test performance or strategy superiority claims.

## Prior Work

See [`docs/prior_work.md`](docs/prior_work.md) and [`docs/research_lineage.md`](docs/research_lineage.md). Previous repositories are treated as read-only research artifacts; this repository reimplements concepts behind common interfaces rather than copying source trees.

## Reproducibility and readiness

Every real run is designed to capture Git SHA, configuration hash, benchmark hash/version, seed, model pool, generation parameters, environment metadata, and budget usage. Result batches use unique names and are protected against silent overwrite.

Use:

```bash
python scripts/validate_readiness.py
python scripts/validate_execution_environment.py
```

The one-task `EXECUTION_SMOKE_TEST` is a separate execution-path check; it is not EXP-001 and its output is not included in EXP-001 statistics.

**EXP-001: NOT EXECUTED. No empirical result is claimed.**
