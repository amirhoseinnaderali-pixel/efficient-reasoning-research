# Scientific and Engineering Audit Summary

**Audit date:** 2026-10-02

## Verdict

**READY WITH CONDITIONS**

The repository's frozen EXP-001 protocol and runtime prerequisites are now explicit. This document is a historical audit record; the current repository additionally enforces strategy-safe task projection, visible-only strategy evaluation, frozen benchmark validation in the execution runner, and result provenance/duplicate safeguards.

EXP-001 should **not yet be treated as empirical evidence** because it has not been executed. The 5-task `transparent-python-mini-v1` benchmark remains validation-only.

## Strengths

- C0-C6 share a common generation interface.
- Model calls, input/output tokens, execution steps, model/execution/graph latency, wall-clock time, candidates, and cost proxy are separate accounting dimensions.
- Output-token and call ceilings are checked before/after generation; provider over-reporting invalidates the run.
- Visible verifier use is explicit for C1/C3/C5; C6 cannot use objective test results for graph selection.
- Final correctness is hidden-suite-only.
- Real execution fails closed when Docker is unavailable.
- Results are schema-validated and written to unique batch files.
- Repeated paired seeds, per-task results, bootstrap CIs, and paired differences are supported.
- Mock validation is isolated from experimental result paths.

## Critical Issues Found and Repaired

### 1. Budget ceilings were previously enforced too late
The previous generation path could request a full per-call token allowance even when little budget remained, then discover the overrun afterward. It also conflated latency and model-only timing.

**Repair:** remaining-token and remaining-wall-clock budgets are used before each call; separate model, execution, graph, and total wall-clock counters are recorded; budget violations produce `ineligible_budget`.

### 2. Final evaluation duplicated visible-test work
C1/C3/C5 could run visible tests during strategy execution and then rerun the visible suite during final evaluation.

**Repair:** final scoring is hidden-only. Visible execution is now strategy-side compute and is never duplicated by the final evaluator.

### 3. C6 was evaluating candidates after graph selection
That was unnecessary verifier work and made the graph condition look more symmetric than it actually was.

**Repair:** C6 graph selection is now purely text-based and occurs without any objective test access.

### 4. Mock components could enter the real EXP-001 path
The original EXP-001 config explicitly listed a mock model, making accidental non-empirical execution possible.

**Repair:** real experiment validation rejects mock adapters; mock validation is a separate path and is marked `validation_only`.

### 5. Result files could be silently overwritten
The prior runner wrote a fixed filename.

**Repair:** result batches use unique names and exclusive file creation.

### 6. Reproducibility metadata was incomplete
Configuration hash, benchmark hash/version, paired seed schedule, and selected package metadata were missing.

**Repair:** these are now captured in every result.

## Moderate Issues Remaining

- The 5-task benchmark is too small for a substantive claim.
- Cross-provider token counts are reported but are not assumed to represent identical computational work.
- The frozen Docker image digest and dated model IDs are configuration inputs; actual environment availability still has to be checked before execution.

## Minor Issues

- The benchmark is intentionally transparent and small, so it is not representative of broad programming distributions.
- The current statistical layer is intentionally lightweight bootstrap/paired analysis rather than a full hierarchical model.

## Audit evidence

- Baseline: 7 tests passed before the audit.
- Post-fix: **25 tests passed**.
- Python compile check: passed.
- All EXP-001/002/003 configs: `VALID`.
- Mock smoke: **35 validation-only rows**.
- Real Docker execution: not run because Docker is unavailable in the audit environment.
- Real EXP-001: **not executed**.
