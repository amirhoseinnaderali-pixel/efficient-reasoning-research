from __future__ import annotations
import json, os, time, urllib.request
from abc import ABC, abstractmethod
from typing import Any
from ..core import GenerationResult

class BaseModelAdapter(ABC):
    def __init__(self, model: str, **kwargs: Any): self.model=model; self.config=kwargs
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int=1000, temperature: float=0.2) -> GenerationResult: ...

def _post_json(url,payload,headers,timeout=120.0):
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers=headers,method='POST')
    with urllib.request.urlopen(req,timeout=timeout) as resp: return json.loads(resp.read().decode())

class MockAdapter(BaseModelAdapter):
    def __init__(self, model='mock-coder', **kwargs): super().__init__(model,**kwargs); self.calls=0
    def generate(self,prompt,max_tokens=1000,temperature=0.2):
        self.calls += 1; task=self.config.get('task_id','')
        code={
          'add_two_numbers':'def add_two_numbers(a, b):\n    return a + b',
          'is_palindrome':'def is_palindrome(s):\n    return s == s[::-1]',
          'count_vowels':"def count_vowels(s):\n    return sum(1 for ch in s if ch.lower() in 'aeiou')",
          'max_subarray':'def max_subarray(nums):\n    best = cur = nums[0]\n    for x in nums[1:]:\n        cur = max(x, cur + x)\n        best = max(best, cur)\n    return best',
          'two_sum':'def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]'
        }.get(task,'def answer(*args):\n    return None')
        if self.config.get('make_first_wrong') and self.calls==1 and task=='add_two_numbers': code='def add_two_numbers(a, b):\n    return a - b'
        return GenerationResult(code,self.model,input_tokens=len(prompt.split()),output_tokens=len(code.split()))

class OpenAICompatibleAdapter(BaseModelAdapter):
    def generate(self,prompt,max_tokens=1000,temperature=0.2):
        base=self.config.get('base_url','https://api.openai.com/v1').rstrip('/'); key=self.config.get('api_key') or os.getenv('OPENAI_API_KEY')
        if not key: raise RuntimeError('OPENAI_API_KEY is required')
        payload={'model':self.model,'messages':[{'role':'user','content':prompt}],'max_tokens':max_tokens,'temperature':temperature}
        t=time.perf_counter(); data=_post_json(base+'/chat/completions',payload,{'Authorization':f'Bearer {key}','Content-Type':'application/json'}); dt=time.perf_counter()-t
        usage=data.get('usage',{}); return GenerationResult(data['choices'][0]['message']['content'],self.model,usage.get('prompt_tokens',0),usage.get('completion_tokens',0),dt,metadata={'provider':'openai_compatible'})

class OllamaAdapter(BaseModelAdapter):
    def generate(self,prompt,max_tokens=1000,temperature=0.2):
        base=self.config.get('base_url','http://localhost:11434').rstrip('/')
        payload={'model':self.model,'messages':[{'role':'user','content':prompt}],'stream':False,'options':{'temperature':temperature,'num_predict':max_tokens}}
        t=time.perf_counter(); data=_post_json(base+'/api/chat',payload,{'Content-Type':'application/json'}); dt=time.perf_counter()-t
        return GenerationResult(data.get('message',{}).get('content',''),self.model,int(data.get('prompt_eval_count') or 0),int(data.get('eval_count') or 0),dt,metadata={'provider':'ollama'})

class GoogleAdapter(BaseModelAdapter):
    def generate(self,prompt,max_tokens=1000,temperature=0.2):
        key=self.config.get('api_key') or os.getenv('GOOGLE_API_KEY')
        if not key: raise RuntimeError('GOOGLE_API_KEY is required')
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={key}"
        payload={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'maxOutputTokens':max_tokens,'temperature':temperature}}
        t=time.perf_counter(); data=_post_json(url,payload,{'Content-Type':'application/json'}); dt=time.perf_counter()-t
        parts=data.get('candidates',[{}])[0].get('content',{}).get('parts',[]); text=''.join(p.get('text','') for p in parts); u=data.get('usageMetadata',{})
        return GenerationResult(text,self.model,int(u.get('promptTokenCount') or 0),int(u.get('candidatesTokenCount') or 0),dt,metadata={'provider':'google'})
