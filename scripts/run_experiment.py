#!/usr/bin/env python3
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from efficient_reasoning.experiments.runner import run
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--mock',action='store_true');a=p.parse_args();print(run(a.config,a.mock))
