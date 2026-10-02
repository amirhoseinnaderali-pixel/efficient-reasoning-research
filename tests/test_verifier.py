import pytest

from efficient_reasoning.verification.sandbox import DockerExecutor, MockExecutor


def test_mock_executor_is_explicitly_not_a_real_sandbox():
    executor = MockExecutor()
    task = {"tests": {"visible": [{"expected": 1}], "hidden": [{"expected": 1}]}}
    result = executor.run("irrelevant", task, "visible")
    assert result.error is None
    assert result.total == 1


def test_docker_executor_fails_closed_without_docker(monkeypatch):
    monkeypatch.setattr("efficient_reasoning.verification.sandbox.shutil.which", lambda name: None)
    with pytest.raises(RuntimeError, match="Docker CLI is required"):
        DockerExecutor()


def test_docker_timeout_attempts_explicit_container_cleanup(monkeypatch):
    import subprocess

    calls = []
    monkeypatch.setattr("efficient_reasoning.verification.sandbox.shutil.which", lambda name: "/usr/bin/docker")

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if len(calls) == 1:
            raise subprocess.TimeoutExpired(cmd, 0.01)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("efficient_reasoning.verification.sandbox.subprocess.run", fake_run)
    executor = DockerExecutor(timeout_seconds=1, memory_mb=256, cpus=1.0, image="python:3.12-slim-bookworm@sha256:" + "0" * 64, platform="linux/amd64", pid_limit=64)
    result = executor.run(
        "def f():\n    return 1",
        {"entry_point": "f", "tests": {"visible": {"setup": "", "assertions": ["assert candidate() == 1"]}}},
        suite="visible",
    )
    assert result.error == "timeout"
    assert calls[0][0:2] == ["docker", "run"]
    assert "--name" in calls[0]
    assert calls[1][:3] == ["docker", "rm", "-f"]
    assert calls[1][3] == calls[0][calls[0].index("--name") + 1]
