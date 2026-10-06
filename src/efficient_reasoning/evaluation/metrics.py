from __future__ import annotations


def correctness_per_compute(correctness, compute):
    return None if compute <= 0 else correctness / compute


def pareto_front(points, x_key="compute", y_key="correctness"):
    out = []
    for p in points:
        dominated = any(
            q is not p
            and q[x_key] <= p[x_key]
            and q[y_key] >= p[y_key]
            and (q[x_key] < p[x_key] or q[y_key] > p[y_key])
            for q in points
        )
        if not dominated:
            out.append(p)
    return out
