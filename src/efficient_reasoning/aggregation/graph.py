from __future__ import annotations
import math,re
from collections import Counter

def _tfidf(texts):
    docs=[re.findall(r'[A-Za-z_][A-Za-z0-9_]*',t.lower()) for t in texts]; df=Counter(); [df.update(set(d)) for d in docs]; n=len(docs); out=[]
    for d in docs:
        tf=Counter(d); vec={}
        for term,c in tf.items(): vec[term]=(c/max(1,len(d)))*(math.log((1+n)/(1+df[term]))+1)
        out.append(vec)
    return out

def _cos(a,b):
    keys=set(a)|set(b); da=sum(a.get(k,0.0)*a.get(k,0.0) for k in keys); db=sum(b.get(k,0.0)*b.get(k,0.0) for k in keys)
    return 0.0 if da==0 or db==0 else sum(a.get(k,0.0)*b.get(k,0.0) for k in keys)/(math.sqrt(da)*math.sqrt(db))

def build_graph(texts,k=2):
    vecs=_tfidf(texts); deg=[0.0]*len(texts); edges=[]
    for i in range(len(texts)):
        sims=sorted(((j,_cos(vecs[i],vecs[j])) for j in range(len(texts)) if j!=i),key=lambda x:x[1],reverse=True)[:k]
        for j,s in sims: edges.append({'source':i,'target':j,'weight':s}); deg[i]+=s
    return {'nodes':list(range(len(texts))),'edges':edges,'degree':deg,'method':'tfidf-cosine'}

def select_by_graph(texts,k=2):
    g=build_graph(texts,k); return max(range(len(texts)),key=lambda i:g['degree'][i]),g
