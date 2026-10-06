from efficient_reasoning.experiments.runner import _environment, _experiment_hash, _task_seed


def test_reproducibility_metadata_is_present():
    env = _environment()
    assert env["python"]
    assert env["platform"]
    assert "packages" in env


def test_config_hash_and_task_seed_are_stable():
    cfg = {"a": 1, "b": [2, 3]}
    assert _experiment_hash(cfg) == _experiment_hash(cfg)
    assert _task_seed(42, "task-x") == _task_seed(42, "task-x")
    assert _task_seed(42, "task-x") != _task_seed(43, "task-x")
