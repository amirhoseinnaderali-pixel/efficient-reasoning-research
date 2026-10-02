from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_TASK_FIELDS = {"id", "problem", "entry_point", "tests"}
REQUIRED_TEST_SUITES = {"visible", "hidden"}


def _validate_suite(task_id: str, suite: str, value: Any) -> None:
    # Legacy validation-only tasks use a list of structured cases.
    if isinstance(value, list):
        if not value:
            raise ValueError(f"Task {task_id} has an empty {suite} suite")
        for idx, case in enumerate(value):
            if not isinstance(case, dict) or "expected" not in case:
                raise ValueError(f"Task {task_id} {suite} legacy case {idx} is malformed")
        return
    # EXP-001 tasks use a source-locked assertion suite.
    if isinstance(value, dict) and isinstance(value.get("assertions"), list) and value["assertions"]:
        if not all(isinstance(x, str) and x.strip() for x in value["assertions"]):
            raise ValueError(f"Task {task_id} {suite} assertions are malformed")
        return
    raise ValueError(f"Task {task_id} {suite} suite is malformed")


def validate_task(task: dict[str, Any], line_number: int) -> None:
    missing = REQUIRED_TASK_FIELDS - task.keys()
    if missing:
        raise ValueError(f"Task line {line_number} missing fields: {sorted(missing)}")
    if not isinstance(task["tests"], dict) or REQUIRED_TEST_SUITES - task["tests"].keys():
        raise ValueError(f"Task {task['id']} must contain visible and hidden test suites")
    for suite in REQUIRED_TEST_SUITES:
        _validate_suite(task["id"], suite, task["tests"][suite])
    if not task["entry_point"] or not task["id"]:
        raise ValueError(f"Task line {line_number} has an empty id or entry_point")


def load_tasks(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    tasks = []
    seen = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        task = json.loads(line)
        validate_task(task, line_number)
        if task["id"] in seen:
            raise ValueError(f"Duplicate task id: {task['id']}")
        seen.add(task["id"])
        tasks.append(task)
    if not tasks:
        raise ValueError(f"Benchmark contains no tasks: {path}")
    return tasks


def benchmark_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
