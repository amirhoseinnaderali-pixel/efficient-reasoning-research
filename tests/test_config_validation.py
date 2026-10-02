from pathlib import Path

import pytest

from efficient_reasoning.experiments.config import load_yaml, validate_config


ROOT = Path(__file__).resolve().parents[1]


def test_all_experiment_configs_are_valid():
    models = load_yaml(ROOT / "configs/models.yaml")
    benchmarks = load_yaml(ROOT / "configs/benchmarks.yaml")
    for path in sorted((ROOT / "configs/experiments").glob("*.yaml")):
        validate_config(load_yaml(path), models, benchmarks)


def test_mock_is_not_valid_for_real_experiment():
    models = load_yaml(ROOT / "configs/models.yaml")
    benchmarks = load_yaml(ROOT / "configs/benchmarks.yaml")
    cfg = load_yaml(ROOT / "configs/default.yaml")
    with pytest.raises(ValueError, match="Mock adapters"):
        validate_config(cfg, models, benchmarks)
