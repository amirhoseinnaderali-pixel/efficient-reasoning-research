from __future__ import annotations

import base64
import json
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass


PINNED_DEFAULT_IMAGE = "python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e"


@dataclass
class ExecutionResult:
    passed: int
    total: int
    error: str | None
    latency_seconds: float
    steps: int = 1

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


class MockExecutor:
    def __init__(self, expected_pass_rate: float = 1.0):
        self.expected_pass_rate = expected_pass_rate

    def run(self, code, task, suite="visible", timeout_seconds=None):
        del code, timeout_seconds
        suite_data = task["tests"][suite]
        total = len(suite_data if isinstance(suite_data, list) else suite_data["assertions"])
        passed = int(round(total * self.expected_pass_rate))
        return ExecutionResult(passed, total, None, 0.0, 1)


class DockerExecutor:
    def __init__(
        self,
        timeout_seconds=3,
        memory_mb=256,
        cpus=1.0,
        image=PINNED_DEFAULT_IMAGE,
        platform="linux/amd64",
        pid_limit=64,
    ):
        if not shutil.which("docker"):
            raise RuntimeError("Docker CLI is required for the real execution backend; safe execution cannot be emulated on the host")
        if "@sha256:" not in image:
            raise ValueError("Real Docker execution requires an immutable image@sha256 digest")
        digest = image.split("@sha256:", 1)[1]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Docker image digest must be a lowercase SHA-256 digest")
        self.timeout_seconds = float(timeout_seconds)
        self.memory_mb = int(memory_mb)
        self.cpus = float(cpus)
        self.image = image
        self.platform = platform
        self.pid_limit = int(pid_limit)

    @staticmethod
    def _suite_total(suite_data):
        return len(suite_data if isinstance(suite_data, list) else suite_data.get("assertions", []))

    def run(self, code, task, suite="visible", timeout_seconds=None):
        suite_data = task["tests"][suite]
        payload = {"code": code, "entry_point": task["entry_point"], "tests": suite_data}
        enc = base64.b64encode(json.dumps(payload).encode()).decode()
        runner = r'''import base64,json,sys,traceback
p=json.loads(base64.b64decode(sys.argv[1]).decode())
open('/tmp/solution.py','w').write(p['code'])
ns={}
try:
    exec(compile(p['code'],'/tmp/solution.py','exec'),ns,ns)
    fn=ns[p['entry_point']]
    suite=p['tests']
    passed=0
    if isinstance(suite, list):
        for t in suite:
            got=fn(*t.get('args',[]),**t.get('kwargs',{}))
            if got==t['expected']:
                passed+=1
        total=len(suite)
    else:
        setup=suite.get('setup','')
        assertions=suite.get('assertions',[])
        total=len(assertions)
        for assertion in assertions:
            local=dict(ns)
            local['candidate']=fn
            if setup:
                exec(compile(setup,'/tmp/harness_setup.py','exec'),local,local)
            try:
                exec(compile(assertion,'/tmp/assertion.py','exec'),local,local)
                passed+=1
            except Exception:
                pass
    print(json.dumps({'passed':passed,'total':total}))
except Exception:
    print(traceback.format_exc(),file=sys.stderr)
    total=len(p['tests']) if isinstance(p['tests'],list) else len(p['tests'].get('assertions',[]))
    print(json.dumps({'passed':0,'total':total}))
    sys.exit(2)
'''
        effective_timeout = min(self.timeout_seconds, float(timeout_seconds)) if timeout_seconds is not None else self.timeout_seconds
        if effective_timeout <= 0:
            return ExecutionResult(0, self._suite_total(suite_data), "execution budget exhausted before sandbox launch", 0.0, 1)
        container_name = f"efficient-reasoning-{uuid.uuid4().hex[:16]}"
        cmd = [
            "docker", "run", "--rm", "--init", "--name", container_name, "--network", "none", "--platform", self.platform,
            "--cpus", str(self.cpus), "--memory", f"{self.memory_mb}m", "--pids-limit", str(self.pid_limit),
            "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=64m",
            "--security-opt", "no-new-privileges", "--cap-drop", "ALL", "--security-opt", "seccomp=default",
            "--ulimit", "fsize=1048576:1048576",
            self.image, "python", "-c", runner, enc,
        ]
        started = time.perf_counter()
        try:
            proc = subprocess.run(cmd, text=True, capture_output=True, timeout=effective_timeout)
        except subprocess.TimeoutExpired:
            try:
                subprocess.run(
                    ["docker", "rm", "-f", container_name],
                    text=True,
                    capture_output=True,
                    timeout=10,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError):
                pass
            return ExecutionResult(0, self._suite_total(suite_data), "timeout", time.perf_counter() - started, 1)
        except OSError as exc:
            return ExecutionResult(0, self._suite_total(suite_data), f"sandbox launch failed: {exc}", time.perf_counter() - started, 1)
        latency = time.perf_counter() - started
        stdout_lines = proc.stdout.strip().splitlines()
        try:
            data = json.loads(stdout_lines[-1])
            passed = int(data["passed"])
            total = int(data["total"])
        except (IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            passed, total = 0, self._suite_total(suite_data)
        error = proc.stderr.strip() or (f"container exit {proc.returncode}" if proc.returncode else None)
        return ExecutionResult(passed, total, error, latency, 1)
