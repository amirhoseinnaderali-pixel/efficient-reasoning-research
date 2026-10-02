# Limitations

- The repository-owned 5-task transparent benchmark is **validation-only**. It is not EXP-001 evidence and is not used for the final research claim.
- EXP-001 uses the frozen 100-task HumanEval-derived manifest `humaneval-stratified-100-v1` with source/task/test provenance recorded in `benchmarks/manifests/exp001_v1.json`.
- Cross-provider token counts come from provider usage metadata and should not be treated as perfectly interchangeable semantic compute.
- Hardware and network latency can vary across environments; wall-clock time is reported as an observed dimension rather than a universal compute unit.
- EXP-001 uses the immutable Docker image digest recorded in its configuration. Local image availability and daemon access are environment prerequisites, not experimental results.
- C1/C3 use visible objective tests for selection. Their results therefore answer a verifier-assisted strategy question distinct from purely generation-only aggregation.
- Mock validation uses canned outputs and a fake executor. It provides software validation evidence only and is never experimental evidence.
- No real EXP-001 result is currently claimed or reported.
