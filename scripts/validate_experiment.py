#!/usr/bin/env python3
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from efficient_reasoning.experiments.runner import load_yaml
p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();c=load_yaml(a.config)
need=['benchmark','budget','execution','strategies','runner']; miss=[x for x in need if x not in c]
if miss: raise SystemExit('Missing: '+','.join(miss))
for q in [c['benchmark']['tasks_path'],'configs/models.yaml']:
 if not Path(q).exists(): raise SystemExit('Missing path: '+q)
if c['budget']['max_model_calls']<=0 or c['budget']['max_generated_tokens']<=0: raise SystemExit('Invalid budget')
print('VALID')
