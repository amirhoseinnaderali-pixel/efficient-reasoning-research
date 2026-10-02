from pathlib import Path

from efficient_reasoning.benchmarks.exp001 import split_assertions, strip_doctest_examples
from efficient_reasoning.benchmarks.manifest import validate_manifest_path
from efficient_reasoning.experiments.config import load_yaml, validate_config

ROOT = Path(__file__).resolve().parents[1]


def test_exp001_manifest_is_frozen_and_has_100_tasks():
    manifest = validate_manifest_path(ROOT / "benchmarks/manifests/exp001_v1.json")
    assert manifest["task_count"] == 100
    assert len({t["task_id"] for t in manifest["tasks"]}) == 100
    assert sum(manifest["category_distribution"].values()) == 100


def test_doctest_examples_are_not_model_visible():
    prompt = '''def solve(x):\n    """Return x + 1.\n\n    >>> solve(1)\n    2\n    """\n    return x + 1\n'''
    transformed = strip_doctest_examples(prompt)
    assert ">>>" not in transformed
    assert "    2" not in transformed
    assert "Return x + 1" in transformed


def test_assertion_split_is_deterministic():
    source = """def check(candidate):\n    assert candidate(1) == 2\n    assert candidate(2) == 3\n    assert candidate(3) == 4\n    assert candidate(4) == 5\n"""
    visible1, hidden1, count1 = split_assertions(source)
    visible2, hidden2, count2 = split_assertions(source)
    assert count1 == 4
    assert visible1 == visible2 and hidden1 == hidden2
    assert len(visible1) == 2 and len(hidden1) == 2
    assert all("candidate(3)" not in x for x in visible1)
    assert any("candidate(3)" in x for x in hidden1)


def test_exp001_config_requires_real_pinned_inputs():
    models = load_yaml(ROOT / "configs/models.yaml")
    benchmarks = load_yaml(ROOT / "configs/benchmarks.yaml")
    cfg = load_yaml(ROOT / "configs/experiments/exp001_fixed_budget.yaml")
    validate_config(cfg, models, benchmarks)
    assert cfg["runner"]["allow_mock"] is False
    assert "@sha256:" in cfg["execution"]["image"]
    assert cfg["project"]["seeds"] == [42, 43, 44]

def test_assertion_split_supports_nested_loop_assertions():
    source = """def check(candidate):
    assert candidate(1) == 2
    for x in range(2, 4):
        assert candidate(x) == x + 1
"""
    visible, hidden, count = split_assertions(source)
    assert count == 2
    assert len(visible) == 1
    assert len(hidden) == 1
    assert "for x in range(2, 4)" in hidden[0]
    assert "assert candidate(x) == x + 1" in hidden[0]
