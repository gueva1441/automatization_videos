# _probe_puertas_v2.py — sourcing profundo (top-N alto) + filtro ANTES de rankear
# Correr:  python -X utf8 _probe_puertas_v2.py
import scrapetube, itertools, re
from collections import Counter

# from script_engine.youtube_scanner import _proxies_dict
# PX = _proxies_dict()
PX = None

# puertas que RINDEN (saqué las flojas: dark history / government secret)
PUERTAS = [
    "declassified medical experiments",
    "soviet cold war cover ups",
    "abandoned facility disaster",
    "unexplained historical tragedy",
]
PER_PUERTA = 20          # ← SOURCING: top-20 (antes 8) para llegar a lo chico

# filtros de FORMATO (antes de rankear)
MIN_SEC, MAX_SEC = 5*60, 50*60     # 5–50 min: saca compilaciones 1-2h y shorts
MIN_VIEWS        = 1_000           # saca canal muerto / subida sin tracción
SMALL_MAX_VIEWS  = 200_000         # ← "joya chica": tracción real pero NO gigante

def length_to_sec(s):
    p = [int(x) for x in (s or "").split(":") if x.isdigit()]
    if len(p) == 3: return p[0]*3600 + p[1]*60 + p[2]
    if len(p) == 2: return p[0]*60 + p[1]
    return p[0] if p else 0

def views_to_int(s):
    m = re.search(r"[\d,]+", s or ""); return int(m.group().replace(",", "")) if m else 0

def parse(v):
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
    return dict(title=title, channel=channel, cid=cid, length=length, sec=length_to_sec(length),
                views=views, v=views_to_int(views), age=age, cc=cc)

canales = Counter(); canal_cid = {}; chicas = []
total_raw = total_pass = 0

for puerta in PUERTAS:
    print(f"\n{'='*100}\nPUERTA: {puerta}\n{'='*100}")
    print(f"{'POS':>3} {'DUR':>7} {'VIEWS':>12} CC  {'EDAD':<13} CANAL")
    print("-"*100)
    try:
        res = scrapetube.get_search(puerta, limit=PER_PUERTA) if PX is None else \
              scrapetube.get_search(puerta, limit=PER_PUERTA, proxies=PX)
        for pos, v in enumerate(itertools.islice(res, PER_PUERTA)):
            r = parse(v); total_raw += 1
            ok = MIN_SEC <= r["sec"] <= MAX_SEC and r["v"] >= MIN_VIEWS
            tag = " " if ok else "x"   # x = descartado por filtro
            small = ok and r["v"] <= SMALL_MAX_VIEWS
            mark = "  <<< CHICA" if small else ""
            print(f"{tag}{pos:>2} {r['length']:>7} {r['views']:>12} "
                  f"{'Y' if r['cc'] else '-'}  {r['age']:<13} {r['channel'][:28]}{mark}")
            if ok:
                total_pass += 1
                canales[r["channel"]] += 1; canal_cid[r["channel"]] = r["cid"]
                if small: chicas.append((puerta, r))
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\n\n{'#'*60}")
print(f"RESUMEN: {total_pass}/{total_raw} pasaron el filtro de formato")
print(f"{'#'*60}")

print(f"\n--- JOYAS CHICAS (<{SMALL_MAX_VIEWS:,} views, formato OK) — ¿LAS PESCAMOS? ---")
if chicas:
    for puerta, r in sorted(chicas, key=lambda x: -x[1]["v"]):
        print(f"  {r['v']:>9,} v  {r['length']:>7}  {r['channel'][:25]:<27} {r['title'][:45]}")
else:
    print("  (ninguna — abajo del top-N solo hay basura o gigantes)")

print(f"\n--- VIGIAS (canales que pasan filtro, por apariciones) ---")
for ch, n in canales.most_common(15):
    print(f"  {n:>2}x  {ch[:32]:<34} {canal_cid.get(ch,'')}")