# Reproducibility

Every real run records:

- experiment ID and unique run ID
- seed schedule and task ID
- repository git SHA when available
- configuration SHA-256
- benchmark SHA-256 and benchmark version
- Python version, platform, CPU count, and selected package versions
- full configured model pool and generation parameters
- all budget counters and budget-violation state
- result status and error state

Results are written with exclusive file creation under a unique batch filename, so a previous result file cannot be silently overwritten.

For repeated experiments, `project.seeds` provides deterministic paired seeds. The per-task generation seed is derived from the configured seed and a stable SHA-256 hash of the task ID, avoiding Python's process-randomized `hash()`.

EXP-001 records the immutable Docker image digest, explicit `linux/amd64` platform, and strict sandbox settings in `configs/experiments/exp001_fixed_budget.yaml`. The repository does not claim that the image has been pre-pulled locally; image availability is an environment condition checked before execution.

The completed EXP-001 study used the frozen benchmark, real model execution path, and objective sandboxed evaluation described by the protocol. Its recorded empirical results are reported in the project README and research report.

The `EXECUTION_SMOKE_TEST` is a separate one-task execution-path check. It is not EXP-001 and its artifacts are excluded from final experiment statistics.

The readiness scripts remain fail-closed for future reruns: a fresh execution still requires the external model credentials, Docker environment, and the materialized benchmark to match the frozen specification.
