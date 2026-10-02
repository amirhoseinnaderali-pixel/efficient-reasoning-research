# Implementation Status

## Built

- Common strategy interface for C0-C6.
- Explicit model-call, input-token, output-token, latency, execution-step, candidate, graph-time, and cost accounting.
- Per-call generation cap based on remaining token budget.
- Explicit generation parameters and deterministic seed schedule.
- Verifier-assisted visible selection isolated to C1/C3/C5.
- Hidden-only final evaluation through one objective evaluator.
- Graph selection with explicit method validation and no objective-test access.
- Fail-closed Docker execution with isolation controls.
- Structured result schema validation and unique batch result files.
- Reproducibility metadata including configuration and benchmark hashes.
- Repeated-seed and paired-analysis infrastructure with bootstrap confidence intervals.
- Scientific invariant tests, configuration validation, CI, and mock end-to-end validation.

## Validation-only evidence

The mock smoke path currently produces 35 task/strategy rows (5 tasks × 7 strategies × 1 seed). These rows are software-validation artifacts only. They are not model or benchmark evidence.

## Not Yet Executed

- No real C0-C6 EXP-001 model run has been executed.
- Docker CLI/daemon prerequisite checks passed in the final hosted audit; no sandboxed model execution was performed because the real-model credential gate remained blocked.
- No empirical conclusion about strategy quality has been made.

## Pre-execution blockers resolved

1. The 5-task smoke benchmark is now explicitly validation-only; EXP-001 is locked to a 100-task HumanEval-derived manifest.
2. The real model pool is frozen to exact dated OpenAI snapshots with model-specific generation parameters.
3. The Docker image is pinned to an immutable SHA-256 digest and strict sandbox policy.
4. The seed schedule `[42, 43, 44]` is frozen and paired across every task.

## Remaining operational preflight

The frozen 100-task benchmark is now materialized at `benchmarks/programming/exp001_v1/tasks.jsonl` and verified against the manifest, task/test hashes, ordering, provenance, and visible/hidden split policy. No model inference is part of materialization.

## Remaining operational preflight

The repository is benchmark-ready and configuration-valid. The execution smoke path is wired through the real model, Docker, budget, visible-evaluation, hidden-evaluation, and result-schema paths. The current execution runtime is blocked by the absent `OPENAI_API_KEY` and missing Docker CLI.

## Next experiment

After the preflight passes, execute the preregistered C0-C6 EXP-001 across all configured seeds. Interpret only real, stored, integrity-validated results.
