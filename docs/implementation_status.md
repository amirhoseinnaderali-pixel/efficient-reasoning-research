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
- No Docker sandbox run has been executed in the audit environment because Docker is unavailable there.
- No empirical conclusion about strategy quality has been made.

## Research limitations still present

1. The transparent benchmark contains only 5 tasks, which is too small for a substantive research claim or stable statistical conclusion.
2. Real model selection must be frozen, documented, and run on the same task-seed pairs before interpretation.
3. The Docker image should be pinned by digest for publication-grade replication.
4. Provider-specific token accounting is only as reliable as each provider's usage metadata; missing usage must make a run ineligible rather than silently impute it.

## Next experiment

The natural next step is to replace the 5-task pilot with a sufficiently large, version-pinned programming benchmark while preserving the same visible/hidden protocol, then execute the pre-registered C0-C6 EXP-001 across all configured seeds.
