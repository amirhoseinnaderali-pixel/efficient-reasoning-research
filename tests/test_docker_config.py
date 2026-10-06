from pathlib import Path

from efficient_reasoning.experiments.config import load_yaml, validate_config

ROOT = Path(__file__).resolve().parents[1]


def test_exp001_uses_immutable_docker_digest():
    models = load_yaml(ROOT / "configs/models.yaml")
    benchmarks = load_yaml(ROOT / "configs/benchmarks.yaml")
    cfg = load_yaml(ROOT / "configs/experiments/exp001_fixed_budget.yaml")
    validate_config(cfg, models, benchmarks)
    image = cfg["execution"]["image"]
    assert image.endswith("@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e")
    assert cfg["execution"]["network"] == "none"
    assert cfg["execution"]["platform"] == "linux/amd64"
    assert cfg["execution"]["sandbox_policy"] == "docker_strict_v1"


def test_runner_passes_frozen_pid_limit_to_docker(monkeypatch):
    import efficient_reasoning.experiments.runner as runner

    seen = {}

    class FakeDocker:
        def __init__(self, **kwargs):
            seen.update(kwargs)

    monkeypatch.setattr(runner, "DockerExecutor", FakeDocker)
    executor = runner.make_executor({
        "backend": "docker", "timeout_seconds": 3, "memory_mb": 256, "cpus": 1.0,
        "pid_limit": 37, "image": "python:3.12-slim-bookworm@sha256:" + "0" * 64, "platform": "linux/amd64",
    })
    assert isinstance(executor, FakeDocker)
    assert seen["pid_limit"] == 37
