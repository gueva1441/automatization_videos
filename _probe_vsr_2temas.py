import scrapetube, itertools, re
from script_engine.youtube_scanner import _proxies_dict, detect_language
px = _proxies_dict()

def parse_count(txt):
    if not txt: return 0
    t = txt.lower().replace(",", "").replace("subscribers","").replace("subscriber","").replace("views","").replace("view","")
    m = re.search(r"([\d.]+)\s*([kmb])?", t)
    return int(float(m.group(1)) * {"k":1e3,"m":1e6,"b":1e9,"":1}[m.group(2) or ""]) if m else 0
def chan_id(v):
    try: return v["longBylineText"]["runs"][0]["navigationEndpoint"]["browseEndpoint"]["browseId"]
    except: return None
def chan_name(v):
    try: return v["longBylineText"]["runs"][0]["text"]
    except: return ""

subs_cache={}
def resolver_subs(cid,name):
    if cid in subs_cache: return subs_cache[cid]
    try:
        for c in itertools.islice(scrapetube.get_search(name, limit=5, results_type="channel", proxies=px),5):
            if c.get("channelId")==cid:
                subs_cache[cid]=parse_count(c.get("videoCountText",{}).get("simpleText")); return subs_cache[cid]
    except: pass
    subs_cache[cid]=None; return None

def probar(query):
    print(f"\n{'='*70}\nTEMA: {query}\n{'='*70}")
    vids=[v for v in itertools.islice(scrapetube.get_search(query,limit=15,proxies=px),15)
          if detect_language(v["title"]["runs"][0]["text"])=="en"][:8]
    rows=[]
    for v in vids:
        t=v["title"]["runs"][0]["text"]
        vw=parse_count(v.get("viewCountText",{}).get("simpleText") or v.get("shortViewCountText",{}).get("simpleText"))
        cid,nm=chan_id(v),chan_name(v)
        s=resolver_subs(cid,nm) if cid else None
        rows.append((t[:36],vw,s,(vw/s if s else None)))
    rows.sort(key=lambda r:(r[3] or -1),reverse=True)
    print(f"{'titulo':36} {'views':>10} {'subs':>11} {'VSR':>6}")
    print("-"*68)
    for t,vw,s,vsr in rows:
        print(f"{t:36} {vw:>10,} {(f'{s:,}' if s else '?'):>11} {(f'{vsr:.1f}x' if vsr else '?'):>6}")

probar("deep sea mystery discovery unexplained")
probar("abandoned soviet secret facility")
