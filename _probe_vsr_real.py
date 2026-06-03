import scrapetube, itertools, re, threading, sys, traceback
from script_engine.youtube_scanner import _proxies_dict, detect_language
px = _proxies_dict()
QUERY = "soviet space disaster cover up"

def parse_count(txt):
    if not txt: return 0
    t = txt.lower().replace(",", "")
    t = t.replace("subscribers","").replace("subscriber","").replace("views","").replace("view","")
    m = re.search(r"([\d.]+)\s*([kmb])?", t)
    if not m: return 0
    return int(float(m.group(1)) * {"k":1e3,"m":1e6,"b":1e9,"":1}[m.group(2) or ""])

def chan_id(v):
    try: return v["longBylineText"]["runs"][0]["navigationEndpoint"]["browseEndpoint"]["browseId"]
    except: return None
def chan_name(v):
    try: return v["longBylineText"]["runs"][0]["text"]
    except: return ""

print(">>> buscando videos...")
vids = list(itertools.islice(scrapetube.get_search(QUERY, limit=15, proxies=px), 15))
vids = [v for v in vids if detect_language(v["title"]["runs"][0]["text"])=="en"][:8]
print(f"    {len(vids)} videos EN\n")

subs_cache = {}
def resolver_subs(cid, name):
    if cid in subs_cache: return subs_cache[cid]
    try:
        chans = list(itertools.islice(scrapetube.get_search(name, limit=5, results_type="channel", proxies=px), 5))
        for c in chans:
            if c.get("channelId")==cid:
                s = parse_count(c.get("videoCountText",{}).get("simpleText"))
                subs_cache[cid]=s; return s
    except Exception as e:
        print("   (subs err:", repr(e)[:50],")")
    subs_cache[cid]=None; return None

rows=[]
for v in vids:
    title = v["title"]["runs"][0]["text"]
    views = parse_count(v.get("viewCountText",{}).get("simpleText") or v.get("shortViewCountText",{}).get("simpleText"))
    cid, name = chan_id(v), chan_name(v)
    subs = resolver_subs(cid, name) if cid else None
    vsr = (views/subs) if subs else None
    rows.append((title[:38], views, subs, vsr))

rows.sort(key=lambda r: (r[3] or -1), reverse=True)
print(f"{'titulo':38} {'views':>10} {'subs':>11} {'VSR':>7}")
print("-"*70)
for t,vw,s,vsr in rows:
    print(f"{t:38} {vw:>10,} {(f'{s:,}' if s else '?'):>11} {(f'{vsr:.1f}x' if vsr else '?'):>7}")
