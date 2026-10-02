from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def load_tasks(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
