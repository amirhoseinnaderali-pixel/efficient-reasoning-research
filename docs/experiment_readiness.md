# EXP-001 Pre-Experiment Readiness

This document records the frozen inputs and gates for the first real controlled experiment. It does **not** report any model inference, benchmark score, Docker execution result, or experimental finding.

## Frozen configuration

The experimental design is frozen to:

- 100-task HumanEval-derived benchmark `humaneval-stratified-100-v1`;
- dated OpenAI model snapshots in `configs/models.yaml`;
- seeds `[42, 43, 44]`;
- fixed C0-C6 strategy set;
- explicit call/token/latency/execution/candidate budgets;
- visible-selection / hidden-final-evaluation separation;
- immutable Docker image digest and `linux/amd64` execution platform;
- strict Docker sandbox policy; and
- no mock execution in the real experiment.

## Static configuration state

The manifest, model pool, generation configuration, Docker image digest, seeds, strategy matrix, and budget values are validated as frozen configuration. This is **repository readiness**, not proof that the current machine can execute the experiment.

## Runtime readiness gate

Run:

```bash
python scripts/validate_readiness.py
```

The gate is fail-closed. It exits non-zero if the materialized benchmark is absent or inconsistent, Docker is unavailable, the Docker daemon is unreachable, the API credential is missing, the frozen configuration has drifted, or another real-execution prerequisite is absent.

Environment-only checks are also available:

```bash
python scripts/validate_execution_environment.py
```

Neither command performs model inference or benchmark execution.

## Benchmark

EXP-001 uses `humaneval-stratified-100-v1`, locked by `benchmarks/manifests/exp001_v1.json`.

The manifest locks 100 unique HumanEval task IDs, category counts, assertion counts, canonical task/test hashes, the upstream HumanEval source commit, and the canonical archive SHA-256. The repository does not regenerate or replace this benchmark during hardening.

The model-facing prompt is the deterministic `strip_doctest_examples_v1` view. The canonical test source remains hash-locked. Hidden assertions never enter a strategy context.

The materialized benchmark must already exist at `benchmarks/programming/exp001_v1/tasks.jsonl` and must match the manifest provenance and per-task hashes before real execution.

## Model pool

The frozen real pool is exactly:

| Condition family | Model IDs |
|---|---|
| C0/C1/C2/C5/C6 | `gpt-4.1-mini-2025-04-14` |
| C3/C4 | `gpt-4.1-mini-2025-04-14`, `gpt-4.1-2025-04-14` |

No mock adapter is accepted for real EXP-001 execution.

## Execution environment

The frozen image is:

`python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e`

The sandbox is `docker_strict_v1`: network disabled, explicit CPU/memory/PID limits, read-only root filesystem, isolated writable `/tmp`, dropped Linux capabilities, `no-new-privileges`, seccomp default, timeout, and subprocess cleanup.

## Smoke test

After the runtime gate passes, the real execution path can be exercised with:

```bash
python scripts/run_execution_smoke_test.py
```

This is explicitly labeled `EXECUTION_SMOKE_TEST`, uses one task / one C0-style generation / one seed, and is stored outside EXP-001 results. It is not an EXP-001 run and does not produce EXP-001 evidence.

## Current experiment status

**EXP-001: NOT EXECUTED.**

The repository may be configuration-complete while the current machine remains runtime-`NOT READY`. No empirical superiority claim is made until the controlled experiment is actually executed and analyzed.
