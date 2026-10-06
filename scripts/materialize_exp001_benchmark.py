#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from efficient_reasoning.benchmarks.exp001 import materialize

p = argparse.ArgumentParser(description="Materialize the frozen EXP-001 benchmark from the pinned upstream source.")
p.add_argument("--manifest", default="benchmarks/manifests/exp001_v1.json")
p.add_argument("--output", default="benchmarks/programming/exp001_v1/tasks.jsonl")
a = p.parse_args()
print(materialize(a.manifest, a.output))
