from efficient_reasoning.benchmarks.loader import load_tasks


def test_validation_benchmark_schema():
    ts = load_tasks("benchmarks/programming/smoke_tasks.jsonl")
    assert len(ts) == 5
    assert all(t["entry_point"] and t["tests"]["visible"] and t["tests"]["hidden"] for t in ts)

def test_exp001_frozen_task_hash_contract():
    from efficient_reasoning.benchmarks.exp001 import canonical_task_hash

    row = {"task_id": "a", "prompt": "b", "entry_point": "c"}
    assert canonical_task_hash(row) == "101565441abb6a3f0d7f727724293a360a74e730de74238eaff47312563778dc"
