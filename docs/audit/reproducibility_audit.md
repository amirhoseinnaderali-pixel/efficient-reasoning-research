# Reproducibility Audit

## Implemented

- Stable configuration hashing.
- Benchmark SHA-256 and version capture.
- Git SHA capture.
- Python/platform/package metadata.
- Explicit model pool and generation parameters.
- Explicit repeated seeds.
- Stable task-seed seed derivation using SHA-256.
- Unique result batch identifiers and exclusive file creation.
- Machine-readable JSONL results.
- Statistical analysis operating on task-seed pairs.

## Remaining condition

The runtime environment must provide the already-frozen model identifiers, API credentials, Docker daemon, and materialized benchmark. Docker image availability is checked as an environment prerequisite; the repository does not claim that the image is pre-pulled.
