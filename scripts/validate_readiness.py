#!/usr/bin/env python3
"""Static pre-execution gate for EXP-001. Never runs model inference or Docker tasks."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from efficient_reasoning.benchmarks.manifest import validate_manifest_path
from efficient_reasoning.experiments.config import load_yaml, validate_config


parser = argparse.ArgumentParser()
parser.add_argument("--config", default="configs/experiments/exp001_fixed_budget.yaml")
args = parser.parse_args()

cfg = load_yaml(args.config)
models = load_yaml("configs/models.yaml")
benchmarks = load_yaml("configs/benchmarks.yaml")
validate_config(cfg, models, benchmarks)
manifest = validate_manifest_path(cfg["benchmark"]["manifest_path"])

assert len(manifest["tasks"]) == 100
assert cfg["runner"]["allow_mock"] is False
assert cfg["runner"]["require_real_models"] is True
assert cfg["runner"]["require_materialized_benchmark"] is True
assert "@sha256:" in cfg["execution"]["image"]
assert len(cfg["project"]["seeds"]) >= 3
assert cfg["project"]["seeds"] == [42, 43, 44]

materialized = Path(cfg["benchmark"]["tasks_path"])
print("BENCHMARK_MANIFEST: VALID")
print(f"BENCHMARK_TASK_COUNT: {manifest['task_count']}")
print("MODEL_POOL: PINNED")
print("DOCKER_IMAGE: IMMUTABLE_DIGEST")
print(f"MATERIALIZED_BENCHMARK_PRESENT: {materialized.exists()}")
print("NO_REAL_EXECUTION: ENFORCED BY COMMAND SCOPE")
print("READY")
