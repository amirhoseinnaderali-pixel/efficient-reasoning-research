#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from efficient_reasoning.logging.schema import validate_result


parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

root = Path(args.input)
files = [root] if root.is_file() else sorted(root.rglob("*.jsonl"))
rows = []
for file in files:
    if "validation" in file.parts:
        continue
    for line in file.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            validate_result(row)
            if row.get("status") == "completed":
                rows.append(row)

out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow([
        "strategy", "n", "mean_hidden_pass_rate", "mean_model_calls", "mean_input_tokens",
        "mean_output_tokens", "mean_model_latency_seconds", "mean_execution_latency_seconds",
        "mean_graph_latency_seconds", "mean_strategy_wall_clock_seconds", "mean_execution_steps",
    ])
    for strategy in sorted({row["strategy"] for row in rows}):
        group = [row for row in rows if row["strategy"] == strategy]
        n = len(group)
        avg = lambda key: sum(row["metrics"][key] for row in group) / n if n else 0.0
        writer.writerow([
            strategy, n,
            avg("hidden_pass_rate"), avg("model_calls"), avg("input_tokens"), avg("output_tokens"),
            avg("model_latency_seconds"), avg("execution_latency_seconds"), avg("graph_latency_seconds"),
            avg("strategy_wall_clock_seconds"), avg("execution_steps"),
        ])
print(out)
