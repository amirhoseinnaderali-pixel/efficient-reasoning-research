#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from efficient_reasoning.experiments.config import load_yaml, validate_config

p = argparse.ArgumentParser()
p.add_argument("--config", required=True)
p.add_argument("--allow-mock", action="store_true")
a = p.parse_args()

cfg = load_yaml(a.config)
models = load_yaml("configs/models.yaml")
benchmarks = load_yaml("configs/benchmarks.yaml")
validate_config(cfg, models, benchmarks, allow_mock=a.allow_mock)
print("VALID")
