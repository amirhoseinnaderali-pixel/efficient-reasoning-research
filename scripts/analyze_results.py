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
from efficient_reasoning.evaluation.statistics import bootstrap_ci, holm_bonferroni, mean, paired_sign_flip_pvalue, paired_task_deltas


def load_rows(path: Path):
    files = [path] if path.is_file() else sorted(path.rglob("*.jsonl"))
    rows = []
    seen = set()
    for file in files:
        if "validation" in file.parts:
            continue
        for line in file.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                validate_result(row)
                key = (row["task_id"], row["seed"], row["strategy"])
                if key in seen:
                    raise ValueError(f"Duplicate task-seed-strategy result: {key}")
                seen.add(key)
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

    for strategy in sorted(by_strategy):
        group_rows = [r for r in rows if r["strategy"] == strategy]
        values = by_strategy[strategy]
        available_costs = [
            r["budget"]["cost_proxy"]
            for r in group_rows
            if r["budget"]["cost_proxy_status"] == "available"
        ]
        report["strategies"][strategy] = {
            "n_rows": len(values),
            "mean_hidden_pass_rate": mean(values),
            "bootstrap_95_ci": bootstrap_ci(values, clusters=[r["task_id"] for r in group_rows]),
            "cost_proxy_available_rows": len(available_costs),
            "mean_cost_proxy_if_complete": (
                mean(available_costs) if len(available_costs) == len(group_rows) else None
            ),
            "cost_proxy_status": (
                "available" if len(available_costs) == len(group_rows)
                else "unavailable_or_partial"
            ),
        }

    raw_pvalues = {}
    task_deltas_by_strategy = {}
    for strategy in sorted(by_strategy):
        if strategy == args.baseline:
            continue
        task_deltas = paired_task_deltas(rows, strategy, baseline=args.baseline)
        task_deltas_by_strategy[strategy] = task_deltas
        raw_pvalues[strategy] = (
            paired_sign_flip_pvalue(task_deltas) if task_deltas else None
        )

    valid_pvalues = {k: v for k, v in raw_pvalues.items() if v is not None}
    adjusted_pvalues = holm_bonferroni(valid_pvalues)

    for strategy, task_deltas in task_deltas_by_strategy.items():
        report["paired_vs_baseline"][strategy] = {
            "baseline": args.baseline,
            "n_task_pairs": len(task_deltas),
            "mean_delta_hidden_pass_rate": mean(task_deltas),
            "bootstrap_95_ci": bootstrap_ci(task_deltas, seed=5678) if task_deltas else None,
            "paired_sign_flip_p": raw_pvalues[strategy],
            "holm_adjusted_p": adjusted_pvalues.get(strategy),
            "cluster_unit": "task",
        }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
