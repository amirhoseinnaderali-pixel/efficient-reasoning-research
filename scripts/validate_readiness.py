#!/usr/bin/env python3
"""Fail-closed static and environment gate for real EXP-001 execution."""
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

    print(f"GIT_SHA: {report.get('git_sha') or 'UNKNOWN'}")
    print(f"GIT_BRANCH: {report.get('git_branch') or 'UNKNOWN'}")
    print(f"GIT_WORKTREE_CLEAN: {report.get('git_worktree_clean')}")
    print(f"MODEL_ACCESS_CREDENTIAL_PRESENT: {report.get('openai_api_key_present')}")
    print(f"DOCKER_CLI_PRESENT: {report.get('docker_cli')}")
    print(f"BENCHMARK_STATUS: {report.get('benchmark')}")
    print(f"CONFIGURATION_STATUS: {report.get('configuration')}")
    print(f"EXP001_READINESS_FAILURE_COUNT: {len(failures)}")
    if failures:
        for failure in failures:
            print(f"NOT_READY: {failure}")
        print("NOT READY")
        return 1
    print("READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
