# _probe_puertas_historia.py — corre varias puertas, tabula lo accionable, rankea canales
# Correr:  python -X utf8 _probe_puertas_historia.py
import scrapetube, itertools, json, re
from collections import Counter, defaultdict

# --- proxy opcional (descomentá si lo necesitás) ---
# from script_engine.youtube_scanner import _proxies_dict
# PX = _proxies_dict()
PX = None

# --- PUERTAS candidatas de tu nicho (editá / agregá libremente) ---
PUERTAS = [
    "declassified medical experiments",
    "soviet cold war cover ups",
    "abandoned facility disaster",
    "dark history forgotten event",
    "government secret experiments",
    "unexplained historical tragedy",
]
PER_PUERTA = 8   # cuántos resultados por puerta

def _txt(node, *path, default=""):
    cur = node
    for k in path:
        if isinstance(cur, dict): cur = cur.get(k, {})
        else: return default
    return cur if isinstance(cur, str) else default

def length_to_sec(s):
    if not s: return 0
    p = [int(x) for x in s.split(":") if x.isdigit()]
    if len(p) == 3: return p[0]*3600 + p[1]*60 + p[2]
    if len(p) == 2: return p[0]*60 + p[1]
    return p[0] if p else 0

def views_to_int(s):
    m = re.search(r"[\d,]+", s or "")
    return int(m.group().replace(",", "")) if m else 0

def parse(v):
    title = _txt(v, "title", "runs", default="") or (v.get("title", {}).get("runs", [{}])[0].get("text", "") if v.get("title") else "")
    # title.runs[0].text robusto:
    try: title = v["title"]["runs"][0]["text"]
    except Exception: title = "<sin titulo>"
    try: channel = v["ownerText"]["runs"][0]["text"]
    except Exception: channel = "?"
    try: cid = v["ownerText"]["runs"][0]["navigationEndpoint"]["browseEndpoint"]["browseId"]
    except Exception: cid = "?"
    length = v.get("lengthText", {}).get("simpleText", "")
    views  = v.get("viewCountText", {}).get("simpleText", "")
    age    = v.get("publishedTimeText", {}).get("simpleText", "")
    cc     = any(b.get("metadataBadgeRenderer", {}).get("label") == "CC" for b in v.get("badges", []))
    verified = any(b.get("metadataBadgeRenderer", {}).get("style") == "BADGE_STYLE_TYPE_VERIFIED" for b in v.get("ownerBadges", []))
    try: snippet = " ".join(r.get("text","") for s in v.get("detailedMetadataSnippets",[]) for r in s.get("snippetText",{}).get("runs",[]))
    except Exception: snippet = ""
    return dict(title=title, channel=channel, cid=cid, length=length, sec=length_to_sec(length),
                views=views, v=views_to_int(views), age=age, cc=cc, verified=verified, snippet=snippet[:90])

canales = Counter()
canal_cid = {}
print(f"{'PUERTA':<34} {'DUR':>6} {'VIEWS':>11} CC V  {'EDAD':<13} CANAL")
print("-"*120)

for puerta in PUERTAS:
    try:
        res = scrapetube.get_search(puerta, limit=PER_PUERTA) if PX is None else \
              scrapetube.get_search(puerta, limit=PER_PUERTA, proxies=PX)
        for v in itertools.islice(res, PER_PUERTA):
            r = parse(v)
            canales[r["channel"]] += 1
            canal_cid[r["channel"]] = r["cid"]
            print(f"{puerta[:33]:<34} {r['length']:>6} {r['views']:>11} "
                  f"{'Y' if r['cc'] else '-'}  {'Y' if r['verified'] else '-'}  "
                  f"{r['age']:<13} {r['channel'][:30]}")
    except Exception as e:
        print(f"{puerta[:33]:<34} ERROR: {e}")
    print()

print("\n" + "="*60)
print("CANALES QUE MAS APARECEN (semilla de Mode B):")
print("="*60)
for ch, n in canales.most_common(15):
    print(f"  {n:>2}x  {ch[:40]:<42} {canal_cid.get(ch,'')}")