exec(open(__import__('os').path.expanduser('~/sim3.py')).read().split('tot_ok=0')[0])
def replay(n, anchors):
    text=orig[n]; offs=[]
    cur=0
    for a in anchors:
        i=text.find(a,cur)
        if i<0: i=text.find(a[:40],cur)
        offs.append(i); cur=max(cur,i+1) if i>=0 else cur
    for sp in sorted(spans[n],key=lambda s:len(s['original']),reverse=True):
        o,nw=sp['original'],sp['suggested']; idx=text.find(o)
        if idx<0: continue
        text=text[:idx]+nw+text[idx+len(o):]
        d=len(nw)-len(o)
        offs=[ (x+d if x>=idx+len(o) else (idx if x>idx else x)) if x>=0 else x for x in offs]
    return [normalize_pool_forms(text[x:x+200]) if x>=0 else None for x in offs]
for i,ch in enumerate(s['chapters']):
    n=i+1; cid=f"ch{n:02d}"
    ips=ch.get('image_prompts') or ch.get('supplemental_image_prompts') or []
    anchors=[(ip.get('narration_anchor') or '').strip() for ip in ips]
    w=json.load(open(f'output/audio/{T}/{cid}_timestamps.json',encoding='utf-8'))
    w=w if isinstance(w,list) else w.get('words',[])
    rn=[A._norm(x['word']) for x in w if A._norm(x['word'])]
    segs=replay(n,anchors); cur=0; ok=True; by={}
    for ai,(a,sg) in enumerate(zip(anchors,segs)):
        if sg is None: ok=False; print(cid,'NO ENCONTRADA EN NARRACION',ai,repr(a[:50])); break
        nd=A._first_n_tokens(sg,3); f=-1;m=None
        for L in (3,2):
            for k in range(cur,len(rn)-L+1):
                if rn[k:k+L]==nd[:L]: f=k;m=L;break
            if f>=0:break
        if f<0: ok=False; print(cid,'FAIL',ai,nd,'|',' '.join(rn[cur:cur+8])); break
        by[m]=by.get(m,0)+1; cur=f+1
    print(cid,'OK' if ok else 'NO',len(anchors),by)
