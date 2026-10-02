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

The real experiment requires external model access, `OPENAI_API_KEY`, a reachable Docker daemon, and the materialized benchmark matching the frozen manifest. `scripts/validate_readiness.py` and `scripts/validate_execution_environment.py` fail closed when these prerequisites are absent.

The `EXECUTION_SMOKE_TEST` is a separate one-task execution-path check. It is not EXP-001 and its artifacts are excluded from final experiment statistics.

No real EXP-001 model inference or benchmark execution has been performed during preparation.
