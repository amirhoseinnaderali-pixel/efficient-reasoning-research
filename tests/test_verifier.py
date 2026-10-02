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
