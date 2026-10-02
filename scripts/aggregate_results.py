#!/usr/bin/env python3
import argparse,csv,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args(); ps=[Path(a.input)] if Path(a.input).is_file() else sorted(Path(a.input).glob('*.jsonl')); rows=[json.loads(l) for q in ps for l in q.read_text().splitlines() if l.strip()]; g={}
for x in rows:
 k=x['strategy']; e=x.get('evaluation') or {}; b=x.get('budget') or {}; z=g.setdefault(k,{'n':0,'rate':0,'calls':0,'tokens':0,'lat':0}); z['n']+=1; z['rate']+=e.get('hidden_pass_rate',0); z['calls']+=b.get('model_calls',0); z['tokens']+=b.get('output_tokens',0); z['lat']+=b.get('latency_seconds',0)
out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
with out.open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['strategy','n','mean_hidden_pass_rate','model_calls','output_tokens','latency_seconds']);
 for k,z in sorted(g.items()): w.writerow([k,z['n'],z['rate']/z['n'],z['calls'],z['tokens'],z['lat']])
print(out)
