from __future__ import annotations

import base64
import json
import shutil
import subprocess
import time
from dataclasses import dataclass


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
        total = len(task["tests"][suite])
        passed = int(round(total * self.expected_pass_rate))
        return ExecutionResult(passed, total, None, 0.0, 1)


class DockerExecutor:
    def __init__(self, timeout_seconds=3, memory_mb=256, cpus=1.0, image="python:3.12-slim"):
        if not shutil.which("docker"):
            raise RuntimeError("Docker CLI is required for the real execution backend; safe execution cannot be emulated on the host")
        if not image:
            raise ValueError("A pinned Docker image reference is required")
        self.timeout_seconds = float(timeout_seconds)
        self.memory_mb = int(memory_mb)
        self.cpus = float(cpus)
        self.image = image

    def run(self, code, task, suite="visible", timeout_seconds=None):
        payload = {"code": code, "entry_point": task["entry_point"], "tests": task["tests"][suite]}
        enc = base64.b64encode(json.dumps(payload).encode()).decode()
        runner = r'''import base64,contextlib,io,json,sys,traceback
p=json.loads(base64.b64decode(sys.argv[1]).decode())
open('/tmp/solution.py','w').write(p['code'])
ns={}
try:
 exec(compile(p['code'],'/tmp/solution.py','exec'),ns,ns)
 fn=ns[p['entry_point']]
 passed=0
 sink=io.StringIO()
 with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
  for t in p['tests']:
   got=fn(*t.get('args',[]),**t.get('kwargs',{}))
   if got==t['expected']: passed+=1
 print(json.dumps({'passed':passed,'total':len(p['tests'])}))
except Exception:
 print(traceback.format_exc(),file=sys.stderr)
 print(json.dumps({'passed':0,'total':len(p['tests'])}))
 sys.exit(2)
'''
        effective_timeout = min(self.timeout_seconds, float(timeout_seconds)) if timeout_seconds is not None else self.timeout_seconds
        if effective_timeout <= 0:
            return ExecutionResult(0, len(task["tests"][suite]), "execution budget exhausted before sandbox launch", 0.0, 1)
        cmd = [
            "docker", "run", "--rm", "--init", "--network", "none",
            "--cpus", str(self.cpus), "--memory", f"{self.memory_mb}m", "--pids-limit", "64",
            "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=64m",
            "--security-opt", "no-new-privileges", "--cap-drop", "ALL", "--security-opt", "seccomp=default",
            "--ulimit", "fsize=1048576:1048576",
            self.image, "python", "-c", runner, enc,
        ]
        started = time.perf_counter()
        try:
            proc = subprocess.run(cmd, text=True, capture_output=True, timeout=effective_timeout)
        except subprocess.TimeoutExpired:
            return ExecutionResult(0, len(task["tests"][suite]), "timeout", time.perf_counter() - started, 1)
        except OSError as exc:
            return ExecutionResult(0, len(task["tests"][suite]), f"sandbox launch failed: {exc}", time.perf_counter() - started, 1)
        latency = time.perf_counter() - started
        stdout_lines = proc.stdout.strip().splitlines()
        try:
            data = json.loads(stdout_lines[-1])
            passed = int(data["passed"])
            total = int(data["total"])
        except (IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            passed, total = 0, len(task["tests"][suite])
        error = proc.stderr.strip() or (f"container exit {proc.returncode}" if proc.returncode else None)
        return ExecutionResult(passed, total, error, latency, 1)
