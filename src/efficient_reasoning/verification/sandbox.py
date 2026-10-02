from __future__ import annotations
import base64,json,shutil,subprocess,time
from dataclasses import dataclass
from typing import Any
@dataclass
class ExecutionResult:
    passed:int; total:int; error:str|None; latency_seconds:float; steps:int=1
    @property
    def pass_rate(self): return self.passed/self.total if self.total else 0.0
class MockExecutor:
    def __init__(self,expected_pass_rate=1.0): self.expected_pass_rate=expected_pass_rate
    def run(self,code,task,suite='visible'):
        total=len(task['tests'][suite]); passed=int(round(total*self.expected_pass_rate)); return ExecutionResult(passed,total,None,0.0,1)
class DockerExecutor:
    def __init__(self,timeout_seconds=3,memory_mb=256,cpus=1.0,image='python:3.12-slim'):
        if not shutil.which('docker'): raise RuntimeError('Docker CLI is required for the real execution backend')
        self.timeout_seconds=timeout_seconds; self.memory_mb=memory_mb; self.cpus=cpus; self.image=image
    def run(self,code,task,suite='visible'):
        payload={'code':code,'entry_point':task['entry_point'],'tests':task['tests'][suite]}; enc=base64.b64encode(json.dumps(payload).encode()).decode()
        runner="""import base64,json,sys,traceback
p=json.loads(base64.b64decode(sys.argv[1]).decode())
open('/tmp/solution.py','w').write(p['code'])
ns={}
try:
 exec(compile(p['code'],'/tmp/solution.py','exec'),ns,ns); fn=ns[p['entry_point']]; passed=0
 for t in p['tests']:
  got=fn(*t.get('args',[]),**t.get('kwargs',{}))
  if got==t['expected']: passed+=1
 print(json.dumps({'passed':passed,'total':len(p['tests'])}))
except Exception:
 print(traceback.format_exc(),file=sys.stderr); print(json.dumps({'passed':0,'total':len(p['tests'])})); sys.exit(2)
"""
        cmd=['docker','run','--rm','--network','none','--cpus',str(self.cpus),'--memory',f'{self.memory_mb}m','--pids-limit','64','--read-only','--tmpfs','/tmp:rw,nosuid,nodev,noexec,size=64m','--security-opt','no-new-privileges','--cap-drop','ALL',self.image,'python','-c',runner,enc]
        t=time.perf_counter()
        try: proc=subprocess.run(cmd,text=True,capture_output=True,timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired: return ExecutionResult(0,len(task['tests'][suite]),'timeout',time.perf_counter()-t,1)
        dt=time.perf_counter()-t
        try: data=json.loads(proc.stdout.strip().splitlines()[-1]); passed,total=int(data['passed']),int(data['total'])
        except Exception: passed,total=0,len(task['tests'][suite])
        err=proc.stderr.strip() or (f'container exit {proc.returncode}' if proc.returncode else None)
        return ExecutionResult(passed,total,err,dt,1)
