from efficient_reasoning.evaluation.statistics import bootstrap_ci


def test_bootstrap_ci_is_deterministic():
    values = [0.0, 0.5, 1.0, 1.0]
    assert bootstrap_ci(values, seed=1, samples=100) == bootstrap_ci(values, seed=1, samples=100)
    lo, hi = bootstrap_ci(values, seed=1, samples=100)
    assert 0.0 <= lo <= hi <= 1.0
