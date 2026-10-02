from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


SHA256_HEX = 64
REQUIRED_MANIFEST_KEYS = {
    "benchmark_id",
    "version",
    "task_count",
    "provenance",
    "selection_policy",
    "evaluation_split_policy",
    "category_distribution",
    "tasks",
    "integrity",
}


def manifest_content_sha256(manifest: dict[str, Any]) -> str:
    body = {k: v for k, v in manifest.items() if k != "integrity"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_manifest(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise ValueError(f"Benchmark manifest is missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_MANIFEST_KEYS - data.keys()
    if missing:
        raise ValueError(f"Benchmark manifest missing fields: {sorted(missing)}")
    expected = data["integrity"].get("manifest_content_sha256")
    actual = manifest_content_sha256(data)
    if expected != actual:
        raise ValueError(f"Benchmark manifest integrity mismatch: expected {expected}, got {actual}")
    return data


def validate_manifest(manifest: dict[str, Any]) -> None:
    if int(manifest["task_count"]) != len(manifest["tasks"]):
        raise ValueError("Manifest task_count does not match tasks array")
    if int(manifest["task_count"]) < 100:
        raise ValueError("EXP-001 requires at least 100 tasks")
    ids = [t.get("task_id") for t in manifest["tasks"]]
    if any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("Manifest contains invalid task IDs")
    if len(ids) != len(set(ids)):
        raise ValueError("Manifest contains duplicate task IDs")
    categories = {k: int(v) for k, v in manifest["category_distribution"].items()}
    counts: dict[str, int] = {}
    for task in manifest["tasks"]:
        category = task.get("category")
        if category is None:
            raise ValueError(f"Task {task['task_id']} has no category")
        counts[category] = counts.get(category, 0) + 1
        if task.get("difficulty") == "invented":
            raise ValueError("Invented difficulty labels are prohibited")
        for field in ("task_sha256", "test_sha256"):
            value = task.get(field)
            if not isinstance(value, str) or len(value) != SHA256_HEX:
                raise ValueError(f"Task {task['task_id']} has invalid {field}")
        if int(task.get("assertion_count", 0)) < 2:
            raise ValueError(f"Task {task['task_id']} has fewer than two assertions")
    if categories != counts:
        raise ValueError(f"Manifest category distribution mismatch: declared {categories}, observed {counts}")
    split = manifest["evaluation_split_policy"]
    if split.get("no_objective_selection_on_hidden") is not True:
        raise ValueError("Manifest must explicitly prohibit hidden-objective selection")
    policy = manifest["selection_policy"]
    if policy.get("exclude_tasks_with_fewer_than_two_top_level_asserts") is not True:
        raise ValueError("Manifest must state the minimum-assertion exclusion rule")
    source = manifest["provenance"]
    required_source = {"canonical_source", "source_commit", "source_path", "source_archive_sha256"}
    if required_source - source.keys():
        raise ValueError("Manifest provenance is incomplete")
    if not source["source_commit"] or not source["source_archive_sha256"]:
        raise ValueError("Manifest source must be immutable and hash-locked")


def validate_manifest_path(path: str | Path) -> dict[str, Any]:
    manifest = load_manifest(path)
    validate_manifest(manifest)
    return manifest
