# EXP-001 Execution Environment

This document describes the prerequisites for a **real** EXP-001 execution. It does not report successful environment access unless the validation commands actually establish it.

## Required environment

- Python 3.12-compatible runtime.
- Docker CLI and a reachable Docker daemon.
- Docker execution platform configured as `linux/amd64`.
- The exact immutable image configured by EXP-001:
  `python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e`
- Docker sandbox policy `docker_strict_v1`: network disabled, bounded CPU/memory/PID resources, read-only root, isolated writable `/tmp` with `nosuid,nodev,noexec`, dropped capabilities, `no-new-privileges`, seccomp default, timeout, and subprocess cleanup.
- `OPENAI_API_KEY` in the environment. The validators only report whether it is present; they never print the credential.
- The exact frozen OpenAI model IDs in `configs/models.yaml`.
- The materialized 100-task benchmark at `benchmarks/programming/exp001_v1/tasks.jsonl`, matching the frozen manifest hashes and provenance.
- A clean Git worktree with the audited commit recorded in Git.

## Static readiness validation

Run from the repository root:

```bash
python scripts/validate_readiness.py
```

This command validates configuration, benchmark integrity/materialization, Docker prerequisites, model credential presence, and Git state. It does **not** run model inference, Docker benchmark execution, or EXP-001.

## Environment-only validation

```bash
python scripts/validate_execution_environment.py
```

This performs the same real-execution prerequisite checks without executing a benchmark task.

## Execution smoke test

After the environment gate passes:

```bash
python scripts/run_execution_smoke_test.py
```

The smoke test is explicitly labeled `EXECUTION_SMOKE_TEST`, uses exactly one task, one C0-style generation, one seed, the real configured model, the real Docker executor, shared budget accounting, and both visible and hidden evaluation. It writes a schema-validated artifact under `results/execution_smoke_test/`.

**The smoke test is not EXP-001. Its output is not included in EXP-001 statistics or evidence.**

## Final hosted pre-execution audit — 2026-10-02

The final clean audit checkout reported:

- frozen configuration: valid;
- materialized benchmark: present and integrity-checked;
- Docker CLI: present;
- Docker daemon check: reachable;
- model credential: **absent**;
- current assistant execution runtime Docker CLI: **absent**;
- readiness: **NOT READY** with exactly one blocker, `OPENAI_API_KEY is missing`;
- real one-task smoke test: fail-closed at the readiness boundary.

No model inference, Docker benchmark execution, or EXP-001 evidence was produced.

## EXP-001 status

EXP-001 has **not** been executed. No empirical result is implied by readiness validation or the smoke-test infrastructure.
