#!/usr/bin/env python3
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',required=True);a=p.parse_args(); ps=[Path(a.input)] if Path(a.input).is_file() else sorted(Path(a.input).glob('*.jsonl'))
for path in ps:
 rows=[json.loads(l) for l in path.read_text().splitlines() if l.strip()]; ok=sum(1 for x in rows if (x.get('evaluation') or {}).get('hidden_pass_rate',0)==1); print(f'{path}: runs={len(rows)} all-hidden-pass={ok}/{len(rows)}')
