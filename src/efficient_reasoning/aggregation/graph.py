from __future__ import annotations

import math
import re
from collections import Counter


def _tfidf(texts):
    docs = [re.findall(r"[A-Za-z_][A-Za-z0-9_]*", t.lower()) for t in texts]
    df = Counter()
    for doc in docs:
        df.update(set(doc))
    n = len(docs)
    out = []
    for doc in docs:
        tf = Counter(doc)
        vec = {}
        for term, count in tf.items():
            vec[term] = (count / max(1, len(doc))) * (math.log((1 + n) / (1 + df[term])) + 1)
        out.append(vec)
    return out


def _cos(a, b):
    keys = sorted(set(a) | set(b))
    da = sum(a.get(k, 0.0) ** 2 for k in keys)
    db = sum(b.get(k, 0.0) ** 2 for k in keys)
    if da == 0 or db == 0:
        return 0.0
    return sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys) / (math.sqrt(da) * math.sqrt(db))


def build_graph(texts, k=2, method="tfidf_cosine"):
    if method != "tfidf_cosine":
        raise ValueError(f"Unsupported graph method: {method}")
    if not texts:
        raise ValueError("Cannot build a graph from zero candidates")
    if not 1 <= k < len(texts):
        raise ValueError(f"k must satisfy 1 <= k < candidate_count; got k={k}, n={len(texts)}")
    vecs = _tfidf(texts)
    degree = [0.0] * len(texts)
    edges = []
    for i in range(len(texts)):
        sims = sorted(
            ((j, _cos(vecs[i], vecs[j])) for j in range(len(texts)) if j != i),
            key=lambda x: (-x[1], x[0]),
        )[:k]
        for j, similarity in sims:
            edges.append({"source": i, "target": j, "weight": similarity})
            degree[i] += similarity
    return {
        "nodes": list(range(len(texts))),
        "edges": edges,
        "degree": degree,
        "method": method,
        "k": k,
        "selection_uses_objective_tests": False,
    }


def select_by_graph(texts, k=2, method="tfidf_cosine"):
    graph = build_graph(texts, k=k, method=method)
    best = max(range(len(texts)), key=lambda i: (graph["degree"][i], -i))
    return best, graph
