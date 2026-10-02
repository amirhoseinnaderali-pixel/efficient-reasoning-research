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

Before a publication-grade real run, pin and pre-pull the Docker image by digest and freeze the exact provider/model identifiers. The repository does not invent either value.
