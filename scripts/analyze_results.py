#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from efficient_reasoning.logging.schema import validate_result
from efficient_reasoning.evaluation.statistics import bootstrap_ci, mean


def load_rows(path: Path):
    files = [path] if path.is_file() else sorted(path.rglob("*.jsonl"))
    rows = []
    for file in files:
        if "validation" in file.parts:
            continue
        for line in file.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                validate_result(row)
                if row.get("status") == "completed" and row.get("evaluation"):
                    rows.append(row)
    return rows



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--baseline", default="c0_single")
    args = parser.parse_args()

    rows = load_rows(Path(args.input))
    by_strategy = defaultdict(list)
    by_pair = {}
    for row in rows:
        rate = row["evaluation"]["hidden_pass_rate"]
        by_strategy[row["strategy"]].append(rate)
        by_pair[(row["seed"], row["task_id"], row["strategy"])] = rate

    report = {"n_completed_rows": len(rows), "strategies": {}, "paired_vs_baseline": {}}
    for strategy, values in sorted(by_strategy.items()):
        report["strategies"][strategy] = {
            "n_rows": len(values),
            "mean_hidden_pass_rate": mean(values),
            "bootstrap_95_ci": bootstrap_ci(values),
        }

    baseline_pairs = {
        (seed, task): value
        for (seed, task, strategy), value in by_pair.items()
        if strategy == args.baseline
    }
    for strategy in sorted(by_strategy):
        if strategy == args.baseline:
            continue
        deltas = []
        for key, value in by_pair.items():
            seed, task, candidate_strategy = key
            if candidate_strategy == strategy and (seed, task) in baseline_pairs:
                deltas.append(value - baseline_pairs[(seed, task)])
        report["paired_vs_baseline"][strategy] = {
            "baseline": args.baseline,
            "n_pairs": len(deltas),
            "mean_delta_hidden_pass_rate": mean(deltas),
            "bootstrap_95_ci": bootstrap_ci(deltas, seed=5678) if deltas else None,
        }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(out)


if __name__ == "__main__":
    main()
