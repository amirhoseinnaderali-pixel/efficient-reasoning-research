from __future__ import annotations

import ast
import copy
import gzip
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from typing import Any


OFFICIAL_ARCHIVE_URL = (
    "https://raw.githubusercontent.com/amirhoseinnaderali-pixel/efficient-reasoning-research/"
    "refs/tags/does-not-exist/data/HumanEval.jsonl.gz"
)
# Runtime URL is assembled from the pinned upstream commit in the manifest.


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_task_hash(task: dict[str, Any]) -> str:
    payload = {
        "task_id": task["task_id"],
        "prompt": task["prompt"],
        "entry_point": task["entry_point"],
    }
    # Preserve the historical manifest hash contract: insertion order is task_id, prompt, entry_point.
    return sha256_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def test_source_hash(test_source: str) -> str:
    return sha256_text(test_source)


def strip_doctest_examples(prompt: str) -> str:
    """Remove interactive doctest examples from a benchmark prompt.

    The benchmark oracle remains unchanged. Only example input/output pairs are
    removed from the model-facing prompt to prevent answer leakage.
    """
    lines = prompt.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*>>>\s", line):
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if re.match(r"^\s*>>>\s", nxt):
                    break
                if not nxt.strip():
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out).rstrip() + "\n"


def _check_function(test_source: str) -> ast.FunctionDef:
    tree = ast.parse(test_source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "check":
            return node
    raise ValueError("Test source does not define check(candidate)")


def _validate_check_structure(test_source: str) -> ast.FunctionDef:
    check = _check_function(test_source)

    def validate_statements(statements: list[ast.stmt]) -> None:
        for node in statements:
            if isinstance(node, ast.Assert):
                continue
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                continue
            if isinstance(node, (ast.Pass, ast.Return)):
                continue
            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "print":
                    continue
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    continue
                raise ValueError(
                    f"Unsupported executable setup in check(candidate): {ast.unparse(node)}"
                )
            if isinstance(node, (ast.For, ast.AsyncFor, ast.If, ast.While, ast.With, ast.AsyncWith, ast.Try)):
                if isinstance(node, (ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith)):
                    validate_statements(node.body)
                    validate_statements(node.orelse)
                elif isinstance(node, ast.If):
                    validate_statements(node.body)
                    validate_statements(node.orelse)
                else:
                    validate_statements(node.body)
                    validate_statements(node.orelse)
                    validate_statements(node.finalbody)
                    for handler in node.handlers:
                        validate_statements(handler.body)
                continue
            raise ValueError(
                f"Unsupported executable setup in check(candidate): {ast.unparse(node)}"
            )

    validate_statements(check.body)
    return check


def _assert_nodes(check: ast.FunctionDef) -> list[ast.Assert]:
    nodes: list[ast.Assert] = []

    class Collector(ast.NodeVisitor):
        def visit_Assert(self, node: ast.Assert) -> None:
            nodes.append(node)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            return

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            return

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            return

    collector = Collector()
    for node in check.body:
        collector.visit(node)
    return nodes


def _assertion_blocks(check: ast.FunctionDef, assertion_count: int) -> list[str]:
    blocks: list[str] = []

    for target_index in range(assertion_count):
        counter = 0

        class IsolateAssertions(ast.NodeTransformer):
            def visit_Assert(self, node: ast.Assert) -> ast.stmt:
                nonlocal counter
                current_index = counter
                counter += 1
                if current_index == target_index:
                    return node
                return ast.copy_location(ast.Pass(), node)

            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
                return node

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
                return node

            def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
                return node

        body = copy.deepcopy(check.body)
        transformed = [IsolateAssertions().visit(node) for node in body]
        module = ast.fix_missing_locations(ast.Module(body=transformed, type_ignores=[]))
        blocks.append(ast.unparse(module))

    return blocks


def split_assertions(test_source: str) -> tuple[list[str], list[str], int]:
    check = _validate_check_structure(test_source)
    nodes = _assert_nodes(check)
    if len(nodes) < 2:
        raise ValueError("Each EXP-001 task must have at least two assertions")
    blocks = _assertion_blocks(check, len(nodes))
    cut = (len(blocks) + 1) // 2
    visible = blocks[:cut]
    hidden = blocks[cut:]
    return visible, hidden, len(blocks)


def _module_setup(test_source: str) -> str:
    tree = ast.parse(test_source)
    kept: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "check":
            continue
        kept.append(node)
    if not kept:
        return ""
    return "\n\n".join(ast.unparse(n) for n in kept) + "\n"


def build_materialized_task(source_task: dict[str, Any], category: str, difficulty: str) -> dict[str, Any]:
    visible, hidden, assertion_count = split_assertions(source_task["test"])
    problem = strip_doctest_examples(source_task["prompt"])
    return {
        "id": source_task["task_id"],
        "problem": problem,
        "entry_point": source_task["entry_point"],
        "category": category,
        "difficulty": difficulty,
        "source": "openai/human-eval",
        "source_version": source_task["source_version"],
        "prompt_transform": "strip_doctest_examples_v1",
        "tests": {
            "visible": {"setup": _module_setup(source_task["test"]), "assertions": visible},
            "hidden": {"setup": _module_setup(source_task["test"]), "assertions": hidden},
        },
        "metadata": {
            "source_task_sha256": canonical_task_hash(source_task),
            "source_test_sha256": test_source_hash(source_task["test"]),
            "assertion_count": assertion_count,
        },
    }


def fetch_official_source(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    commit = manifest["provenance"]["source_commit"]
    url = f"https://raw.githubusercontent.com/openai/human-eval/{commit}/data/HumanEval.jsonl.gz"
    req = urllib.request.Request(url, headers={"User-Agent": "efficient-reasoning-research/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        archive = resp.read()
    expected = manifest["provenance"]["source_archive_sha256"]
    actual = sha256_bytes(archive)
    if actual != expected:
        raise RuntimeError(f"Official HumanEval archive hash mismatch: expected {expected}, got {actual}")
    rows = []
    for line in gzip.decompress(archive).decode("utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    if len(rows) != 164:
        raise RuntimeError(f"Expected 164 HumanEval source tasks, found {len(rows)}")
    return rows


def materialize(manifest_path: str | Path, output_path: str | Path) -> Path:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    rows = fetch_official_source(manifest)
    by_id = {r["task_id"]: r for r in rows}
    selected = manifest["tasks"]
    materialized = []
    for entry in selected:
        source = by_id.get(entry["task_id"])
        if source is None:
            raise RuntimeError(f"Manifest task missing from source: {entry['task_id']}")
        source = dict(source)
        source["source_version"] = manifest["provenance"]["source_commit"]
        if canonical_task_hash(source) != entry["task_sha256"]:
            raise RuntimeError(f"Task hash mismatch: {entry['task_id']}")
        if test_source_hash(source["test"]) != entry["test_sha256"]:
            raise RuntimeError(f"Test hash mismatch: {entry['task_id']}")
        task = build_materialized_task(source, entry["category"], entry["difficulty"])
        materialized.append(task)
    if len(materialized) != manifest["task_count"]:
        raise RuntimeError("Materialized task count does not match manifest")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in materialized), encoding="utf-8", newline="\n")
    return out
