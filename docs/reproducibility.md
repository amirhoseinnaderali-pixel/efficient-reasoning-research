# Reproducibility

Every run records:

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

The execution image is recorded as configured. For publication-grade replication, the Docker image should additionally be pre-pulled and pinned to a digest before the real run; the repository deliberately does not invent a digest.

The real experiment requires external model access and Docker. CI and `--mock` exercise software only.
