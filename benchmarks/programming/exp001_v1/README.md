# EXP-001 benchmark materialization

This directory is intentionally empty until the frozen HumanEval source is materialized by:

```bash
python scripts/materialize_exp001_benchmark.py \
  --manifest benchmarks/manifests/exp001_v1.json \
  --output benchmarks/programming/exp001_v1/tasks.jsonl
```

The materializer downloads the exact upstream `openai/human-eval` archive at the commit recorded in the manifest, verifies the archive SHA-256, verifies every selected task/test hash, removes doctest input/output examples from the model-facing prompt, and writes a deterministic 100-task derived benchmark.

Real EXP-001 execution refuses to proceed unless this file exists and matches the manifest.
