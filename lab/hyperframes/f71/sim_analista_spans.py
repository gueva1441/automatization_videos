import json,sys,types,re
from pathlib import Path
class Any_(types.ModuleType):
    def __getattr__(self,k): return (Path('data') if k=='DATA_DIR' else Path('logs')) if k.endswith('_DIR') else types.SimpleNamespace()
sys.modules['config']=Any_('config')
sys.path.insert(0,'.')
import anchor_timing as A
try:
    from tts_normalizer import normalize_pool_forms
except Exception:
    from script_engine.m02_5_normalizer_gate import normalize_pool_forms
T='123bbb64-9fca-4395-8bf4-57d60e219ef1'
s=json.load(open(f'data/scripts/{T}.json',encoding='utf-8'))
nz=json.load(open(f'data/scripts/_steps/{T}/01b_narration_normalized.json',encoding='utf-8'))
spans={c['chapter_number']:[sp for sp in c['spans_applied'] if sp.get('decision')=='applied' and sp.get('category')!='f5_pool_forms'] for c in nz['chapters']}
orig={c['chapter_number']:c['narration_original'] for c in nz['chapters']}
def norm_anchor(a,n):
    t=a
    for sp in sorted(spans[n],key=lambda s:len(s['original']),reverse=True):
        if sp['original'] in t: t=t.replace(sp['original'],sp['suggested'],1)
    return normalize_pool_forms(t)
tot_ok=0
for i,ch in enumerate(s['chapters']):
    n=i+1; cid=f"ch{n:02d}"
    ips=ch.get('image_prompts') or ch.get('supplemental_image_prompts') or []
    anchors=[(ip.get('narration_anchor') or '').strip() for ip in ips]
    w=json.load(open(f'output/audio/{T}/{cid}_timestamps.json',encoding='utf-8'))
    w=w if isinstance(w,list) else w.get('words',[])
    rn=[A._norm(x['word']) for x in w if A._norm(x['word'])]
    cur=0; ok=True; notin=0; by={}
    for ai,a in enumerate(anchors):
        if a not in orig[n]: notin+=1
        nd=A._first_n_tokens(norm_anchor(a,n),3); f=-1; m=None
        for L in (3,2):
            for k in range(cur,len(rn)-L+1):
                if rn[k:k+L]==nd[:L]: f=k;m=L;break
            if f>=0:break
        if f<0:
            ok=False; print(cid,'FAIL',ai,repr(a[:50]),nd,'|',' '.join(rn[cur:cur+10])); break
        by[m]=by.get(m,0)+1; cur=f+1
    print(cid,'OK' if ok else 'NO',len(anchors),'anclas · por trigrama/bigrama',by,'· anclas no literales en la narración:',notin)
