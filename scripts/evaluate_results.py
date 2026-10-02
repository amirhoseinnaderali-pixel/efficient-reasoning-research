#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from efficient_reasoning.logging.schema import validate_result

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
args = parser.parse_args()
root = Path(args.input)
files = [root] if root.is_file() else sorted(root.rglob("*.jsonl"))
for path in files:
    if "validation" in path.parts:
        continue
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    for row in rows:
        validate_result(row)
    completed = [row for row in rows if row.get("status") == "completed" and row.get("evaluation")]
    complete_hidden = sum(row["evaluation"]["hidden_pass_rate"] == 1.0 for row in completed)
    print(f"{path}: completed={len(completed)} all-hidden-pass={complete_hidden}/{len(completed)}")
