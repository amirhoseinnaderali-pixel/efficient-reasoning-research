#!/usr/bin/env python3
"""Validate the real execution environment without running EXP-001 or model inference."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from efficient_reasoning.experiments.config import load_yaml
from efficient_reasoning.experiments.execution_environment import collect_execution_environment_failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiments/exp001_fixed_budget.yaml")
    args = parser.parse_args()

    cfg = load_yaml(ROOT / args.config)
    models = load_yaml(ROOT / "configs/models.yaml")
    benchmarks = load_yaml(ROOT / "configs/benchmarks.yaml")
    failures, report = collect_execution_environment_failures(ROOT, cfg, models, benchmarks)

    print(f"EXECUTION_ENVIRONMENT_GIT_SHA: {report.get('git_sha') or 'UNKNOWN'}")
    print(f"EXECUTION_ENVIRONMENT_BRANCH: {report.get('git_branch') or 'UNKNOWN'}")
    print(f"WORKTREE_CLEAN: {report.get('git_worktree_clean')}")
    print(f"DOCKER_CLI_PRESENT: {report.get('docker_cli')}")
    print(f"DOCKER_DAEMON: {report.get('docker_daemon')}")
    print(f"OPENAI_API_KEY_PRESENT: {report.get('openai_api_key_present')}")
    print(f"CONFIGURATION: {report.get('configuration')}")
    print(f"BENCHMARK: {report.get('benchmark')}")
    if failures:
        for failure in failures:
            print(f"NOT_READY: {failure}")
        print("NOT READY")
        return 1
    print("READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
