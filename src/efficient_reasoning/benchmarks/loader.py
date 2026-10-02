from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_TASK_FIELDS = {"id", "problem", "entry_point", "tests"}
REQUIRED_TEST_SUITES = {"visible", "hidden"}


def validate_task(task: dict[str, Any], line_number: int) -> None:
    missing = REQUIRED_TASK_FIELDS - task.keys()
    if missing:
        raise ValueError(f"Task line {line_number} missing fields: {sorted(missing)}")
    if not isinstance(task["tests"], dict) or REQUIRED_TEST_SUITES - task["tests"].keys():
        raise ValueError(f"Task {task['id']} must contain visible and hidden test suites")
    for suite in REQUIRED_TEST_SUITES:
        if not isinstance(task["tests"][suite], list) or not task["tests"][suite]:
            raise ValueError(f"Task {task['id']} has an empty or invalid {suite} suite")
        for test_index, case in enumerate(task["tests"][suite]):
            if not isinstance(case, dict) or "expected" not in case:
                raise ValueError(f"Task {task['id']} {suite} case {test_index} is malformed")
    if not task["entry_point"] or not task["id"]:
        raise ValueError(f"Task line {line_number} has an empty id or entry_point")


def load_tasks(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    tasks = []
    seen = set()
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
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
