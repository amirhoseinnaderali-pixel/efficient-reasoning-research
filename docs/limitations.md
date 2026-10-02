# Limitations

- The current transparent benchmark has only 5 tasks and 4 tests per task. It is suitable for framework validation, not a final research claim.
- Cross-provider token counts come from provider usage metadata and should not be treated as perfectly interchangeable semantic compute.
- Hardware/network latency can vary across environments; wall-clock is reported as an observed dimension, not a universal compute unit.
- The Docker image is configured by tag in the pilot configuration. Publication-grade replication should pin a digest before execution.
- C1/C3 use visible objective tests for selection. Their results therefore answer a different question than purely generation-only aggregation and must be interpreted as verifier-assisted strategies.
- Mock validation uses canned outputs and a fake executor. It provides software evidence only.
