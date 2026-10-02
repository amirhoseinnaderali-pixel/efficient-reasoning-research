#!/usr/bin/env python3
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',required=True);a=p.parse_args(); ps=[Path(a.input)] if Path(a.input).is_file() else sorted(Path(a.input).glob('*.jsonl'))
for q in ps:
 xs=[json.loads(l) for l in q.read_text().splitlines() if l.strip()]; print(q.name)
 by={}
 for x in xs: by.setdefault(x['strategy'],[]).append(x)
 for k,v in sorted(by.items()): print(k,len(v),sum((x.get('evaluation') or {}).get('hidden_pass_rate',0) for x in v)/len(v))
