from __future__ import annotations

import random
import statistics
from collections import defaultdict


def mean(values):
    return statistics.fmean(values) if values else None


def _cluster_means(values, clusters):
    values = list(values)
    clusters = list(clusters)
    if len(values) != len(clusters):
        raise ValueError("values and clusters must have equal length")
    grouped = defaultdict(list)
    for value, cluster in zip(values, clusters):
        grouped[cluster].append(value)
    return [statistics.fmean(grouped[key]) for key in sorted(grouped)]


def bootstrap_ci(values, seed=1234, samples=5000, clusters=None):
    """Percentile bootstrap CI; with clusters, resample clusters rather than rows."""
    if clusters is not None:
        values = _cluster_means(values, clusters)
    else:
        values = list(values)
    if not values:
        return None
    if len(values) == 1:
        return [values[0], values[0]]
    rng = random.Random(seed)
    means = []
    for _ in range(samples):
        draw = [values[rng.randrange(len(values))] for _ in values]
        means.append(statistics.fmean(draw))
    means.sort()
    lo = means[int(0.025 * (len(means) - 1))]
    hi = means[int(0.975 * (len(means) - 1))]
    return [lo, hi]


def paired_task_deltas(rows, strategy, baseline="c0_single"):
    """Return one paired delta per task after averaging available seeds."""
    by_task_strategy = defaultdict(list)
    for row in rows:
        if row.get("status") != "completed" or not row.get("evaluation"):
            continue
        key = (row["task_id"], row["strategy"])
        by_task_strategy[key].append(row["evaluation"]["hidden_pass_rate"])

    deltas = []
    for task_id in sorted({row["task_id"] for row in rows}):
        candidate = by_task_strategy.get((task_id, strategy), [])
        base = by_task_strategy.get((task_id, baseline), [])
        if candidate and base:
            deltas.append(
                statistics.fmean(candidate) - statistics.fmean(base)
            )
    return deltas
