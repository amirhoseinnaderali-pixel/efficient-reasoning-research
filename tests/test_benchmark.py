from efficient_reasoning.benchmarks.loader import load_tasks


def test_validation_benchmark_schema():
    ts = load_tasks("benchmarks/programming/smoke_tasks.jsonl")
    assert len(ts) == 5
    assert all(t["entry_point"] and t["tests"]["visible"] and t["tests"]["hidden"] for t in ts)


def test_exp001_frozen_task_hash_contract():
    from efficient_reasoning.benchmarks.exp001 import canonical_task_hash, fetch_official_source
    from efficient_reasoning.benchmarks.manifest import load_manifest

    manifest = load_manifest("benchmarks/manifests/exp001_v1.json")
    source = fetch_official_source(manifest)
    row = next(x for x in source if x["task_id"] == "HumanEval/0")
    assert canonical_task_hash(row) == manifest["tasks"][0]["task_sha256"]
