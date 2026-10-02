import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from efficient_reasoning.aggregation.graph import build_graph, select_by_graph


def test_graph_builds():
    g = build_graph(
        ["def add(a,b): return a+b", "def sum(a,b): return a+b", "unrelated text"],
        1,
    )
    assert len(g["nodes"]) == 3 and g["edges"]
    i, _ = select_by_graph(["same same", "same same", "different"], 1)
    assert i in (0, 1)


def test_c6_graph_is_stable_across_hash_seeds():
    script = (
        "import json; "
        "from efficient_reasoning.aggregation.graph import select_by_graph; "
        "i,g=select_by_graph(["
        "'alpha beta gamma', "
        "'alpha beta delta', "
        "'epsilon zeta eta'"
        "], 1); "
        "print(json.dumps({'selected': i, 'degree': g['degree'], 'edges': g['edges']}, sort_keys=True))"
    )
    env_a = os.environ.copy()
    env_b = os.environ.copy()
    env_a["PYTHONHASHSEED"] = "1"
    env_b["PYTHONHASHSEED"] = "999"
    env_a["PYTHONPATH"] = str(ROOT / "src")
    env_b["PYTHONPATH"] = str(ROOT / "src")
    a = subprocess.check_output([sys.executable, "-c", script], env=env_a, text=True).strip()
    b = subprocess.check_output([sys.executable, "-c", script], env=env_b, text=True).strip()
    assert json.loads(a) == json.loads(b)
