from __future__ import annotations
import re

def extract_code(text: str) -> str:
    m = re.search(r"```(?:python|py)?\s*(.*?)```", text, flags=re.I | re.S)
    if m:
        return m.group(1).strip()
    lines = text.strip().splitlines()
    kept=[]; started=False
    for line in lines:
        if line.startswith(("def ", "class ", "import ", "from ")):
            started=True
        if started: kept.append(line)
    return "\n".join(kept).strip() or text.strip()
