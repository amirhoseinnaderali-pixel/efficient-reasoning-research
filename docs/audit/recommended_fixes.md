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

## Required before real EXP-001

1. Expand or replace the 5-task pilot with a sufficiently large, version-pinned benchmark.
2. Freeze the exact real model identifiers, primary model, multi-model pool, generation parameters, and provider configuration.
3. Pre-pull and pin the Docker execution image by digest.
4. Run all configured seeds on the same task distribution.
5. Treat only completed, budget-valid rows as experimental evidence.
