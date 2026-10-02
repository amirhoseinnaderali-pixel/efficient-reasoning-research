from efficient_reasoning.benchmarks.loader import load_tasks


def test_validation_benchmark_schema():
    ts = load_tasks("benchmarks/programming/smoke_tasks.jsonl")
    assert len(ts) == 5
    assert all(t["entry_point"] and t["tests"]["visible"] and t["tests"]["hidden"] for t in ts)
