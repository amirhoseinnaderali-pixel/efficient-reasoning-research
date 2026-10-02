from __future__ import annotations
import json,platform,subprocess,time
from pathlib import Path
import yaml
from ..benchmarks.loader import load_tasks
from ..budgeting.budget import Budget
from ..evaluation.evaluator import ObjectiveEvaluator
from ..models.adapters import MockAdapter,OllamaAdapter,OpenAICompatibleAdapter,GoogleAdapter
from ..strategies.factory import build_strategy
from ..verification.sandbox import DockerExecutor,MockExecutor

def load_yaml(path): return yaml.safe_load(Path(path).read_text())
def _git_sha():
    try: return subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    except Exception: return None
def make_adapter(spec,task_id,mock):
    if mock or spec.get('adapter')=='mock': return MockAdapter(spec.get('name','mock-coder'),task_id=task_id)
    cls={'ollama':OllamaAdapter,'openai_compatible':OpenAICompatibleAdapter,'google':GoogleAdapter}[spec['adapter']]; return cls(spec['name'],**{k:v for k,v in spec.items() if k not in {'adapter','name'}})
def make_executor(cfg,mock):
    return MockExecutor() if mock or cfg.get('backend')=='mock' else DockerExecutor(int(cfg.get('timeout_seconds',3)),int(cfg.get('memory_mb',256)),float(cfg.get('cpus',1.0)),cfg.get('image','python:3.12-slim'))
def run(config_path,mock=False):
    cfg=load_yaml(config_path); tasks=load_tasks(cfg['benchmark']['tasks_path']); mc=load_yaml('configs/models.yaml'); requested=cfg.get('models') or mc.get('active_models') or ['mock']
    specs=[mc['models'][x] if isinstance(x,str) else x for x in requested]; rows=[]
    for task in tasks:
        for sname,scfg in cfg['strategies'].items():
            budget=Budget(**cfg['budget']); executor=make_executor(cfg['execution'],mock); evaluator=ObjectiveEvaluator(executor,budget)
            try:
                ads=[make_adapter(s,task['id'],mock) for s in specs]; strat=build_strategy(sname,scfg,ads[0],budget,evaluator,ads); result=strat.solve(task); ev=evaluator.evaluate(result.answer,task); status='completed'; err=None
            except Exception as exc:
                result=None; ev=None; status='failed'; err=f'{type(exc).__name__}: {exc}'
            snap=budget.snapshot(sum((c.generation.cost_proxy or 0) for c in (result.candidates if result else [])))
            rows.append({'experiment_id':cfg.get('runner',{}).get('experiment_id','MOCK-SMOKE' if mock else 'UNSPECIFIED'),'run_id':f"{task['id']}__{sname}__{int(time.time()*1000)}",'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':status,'error':err,'task_id':task['id'],'strategy':sname,'model':specs[0].get('name','mock'),'budget':snap.__dict__,'evaluation':None if ev is None else {'visible_passed':ev.visible_passed,'visible_total':ev.visible_total,'hidden_passed':ev.hidden_passed,'hidden_total':ev.hidden_total,'hidden_pass_rate':ev.hidden_pass_rate,'executable':ev.executable,'error':ev.error,'latency_seconds':ev.latency_seconds,'execution_steps':ev.execution_steps},'candidates':[] if not result else [{'candidate_id':c.candidate_id,'model':c.model,'text':c.text,'visible_pass':c.visible_pass,'visible_score':c.visible_score} for c in result.candidates],'trace':[] if not result else result.trace,'notes':{} if not result else result.notes,'environment':{'python':platform.python_version(),'platform':platform.platform(),'git_sha':_git_sha(),'mock':mock}})
    outdir=Path(cfg.get('runner',{}).get('output_dir','results/raw')); outdir.mkdir(parents=True,exist_ok=True); out=outdir/('mock_smoke.jsonl' if mock else f"{cfg.get('runner',{}).get('experiment_id','experiment').lower()}.jsonl"); out.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n'); return out
