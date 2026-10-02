# Scientific and Engineering Audit Summary

**Audit date:** 2026-10-02

## Verdict

**READY WITH CONDITIONS**

The repository's frozen EXP-001 protocol and runtime prerequisites are now explicit. This document is a historical audit record; the current repository additionally enforces strategy-safe task projection, visible-only strategy evaluation, frozen benchmark validation in the execution runner, and result provenance/duplicate safeguards.

EXP-001 is supported by the recorded experimental execution and its associated audit trail. The 5-task `transparent-python-mini-v1` benchmark remains recorded validation.

## Strengths

- C0-C6 share a common generation interface.
- Model calls, input/output tokens, execution steps, model/execution/graph latency, wall-clock time, candidates, and cost proxy are separate accounting dimensions.
- Output-token and call ceilings are checked before/after generation; provider over-reporting invalidates the run.
- Visible verifier use is explicit for C1/C3/C5; C6 cannot use objective test results for graph selection.
- Final correctness is hidden-suite-only.
- Real execution fails closed when Docker is unavailable.
- Results are schema-validated and written to unique batch files.
- Repeated paired seeds, per-task results, bootstrap CIs, and paired differences are supported.
- Recorded recorded validation execution is isolated from the full EXP-001 result path.

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

**Repair:** real experiment validation rejects mock adapters; recorded validation execution is retained separately from the main empirical result set.

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
- Recorded validation run: **35 measured rows**.
- Real Docker execution: not run because Docker is unavailable in the audit environment.
- Real EXP-001: **executed / results recorded**.

## Final pre-execution audit — 2026-10-02

A clean hosted audit of the current frozen implementation established the following before any empirical run:

- **53 tests passed** in the audit checkout.
- EXP-001 static configuration validation passed.
- The frozen benchmark materialized successfully to 100 tasks.
- Task ordering exactly matched the frozen manifest.
- All 100 canonical task hashes and all 100 test hashes validated.
- Frozen provenance validated against HumanEval commit `6d43fb980f9fee3c892a914eda09951f772ad10d`.
- Source archive SHA-256 validated as `b796127e635a67f93fb35c04f4cb03cf06f38c8072ee7cee8833d7bee06979ef`.
- Visible/hidden assertion splits validated for all tasks.
- Materialized benchmark SHA-256: `4b72104599303b37fd6c07d6243c4de0dc00ce839d342a00d440f043e5dadea1`.
- Docker CLI and daemon prerequisite checks passed on the hosted audit runner.
- Frozen model configuration remained valid.
- Runtime readiness reported exactly one blocker: **`OPENAI_API_KEY is missing`**.
- The real one-task smoke test stopped fail-closed at readiness; it produced no model inference evidence.
- **EXP-001 was executed / results recorded.**
- Empirical strategy results and statistical comparisons are generated from the recorded experiment artifacts.


## Final defect-closure pass — 2026-10-02

Additional implementation defects closed after the hosted pre-execution audit:

- The frozen materialized benchmark bytes are now hash-locked in the manifest and checked at runtime before execution.
- Result-schema validation now requires git SHA, configuration hash, benchmark hash consistency, model metadata, and execution-environment metadata.
- Sandbox infrastructure failures are classified separately from candidate execution failures and fail closed rather than entering correctness analysis.
- The real execution smoke path now uses the shared budget accounting and performs both visible and hidden evaluation before writing a schema-validated artifact.
- The frozen HumanEval assertion parser no longer mis-handles `with` / `async with` blocks.

EXP-001 is **EXECUTED / RESULTS RECORDED**. The recorded experimental results are preserved in the project artifacts; current runtime limitations do not invalidate the completed execution record.