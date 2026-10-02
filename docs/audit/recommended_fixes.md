# Recommended Fixes

## Completed in this audit

- Enforce remaining token/wall-clock budgets before generation.
- Count failed model calls and separate latency dimensions.
- Make final evaluation hidden-only.
- Remove C6 verifier calls before/after graph selection.
- Reject mock adapters in real experiment configs.
- Validate benchmark/task/result schemas.
- Prevent silent result overwrite.
- Add reproducibility hashes, seeds, environment metadata, and generation parameters.
- Add statistical bootstrap and paired-comparison support.
- Add scientific invariant tests.
- Harden Docker execution and fail closed.
- Separate validation-only artifacts from experimental result paths.
- Freeze EXP-001's 100-task benchmark, exact model IDs, generation settings, budgets, seeds, strategy matrix, and immutable Docker image digest.
- Add separate readiness/environment validators and an explicitly isolated `EXECUTION_SMOKE_TEST` path.

## Required before real EXP-001

1. Materialize the already frozen 100-task benchmark and pass the integrity gate without changing its provenance.
2. Provide the exact frozen model configuration and a real `OPENAI_API_KEY`.
3. Provide a reachable Docker daemon capable of the configured `linux/amd64` strict sandbox.
4. Optionally complete the one-task `EXECUTION_SMOKE_TEST`; it is separate from EXP-001 evidence.
5. Run all configured seeds on the same frozen task distribution.
6. Treat only completed, budget-valid rows as experimental evidence.
