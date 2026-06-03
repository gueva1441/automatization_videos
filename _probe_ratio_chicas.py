# _probe_ratio_barrido.py — sourcing top-20 + barrido de ABS_FLOOR sobre los mismos datos
# Reusa el motor REAL del scanner. Correr:  python -X utf8 _probe_ratio_barrido.py
import scrapetube, itertools, re, time
from script_engine.youtube_scanner import (
    _channel_baseline, compute_ratio,
    PISO_DEMANDA, PISO_MEDIANA, OUTLIER_MIN, BASELINE_N,
)

PUERTAS = [
    "declassified medical experiments",
    "soviet cold war cover ups",
    "abandoned facility disaster",
    "unexplained historical tragedy",
]
PER_PUERTA = 20
MIN_SEC, MAX_SEC = 5*60, 50*60
MIN_VIEWS, SMALL_MAX = 1_000, 200_000   # "chica" = formato OK + tracción + no gigante
PISOS = [80_000, 50_000, 30_000, 20_000]

def length_to_sec(s):
    p = [int(x) for x in (s or "").split(":") if x.isdigit()]
    return p[0]*3600+p[1]*60+p[2] if len(p)==3 else (p[0]*60+p[1] if len(p)==2 else (p[0] if p else 0))

def views_to_int(s):
    m = re.search(r"[\d,]+", s or ""); return int(m.group().replace(",","")) if m else 0

def parse(v):
    try: title = v["title"]["runs"][0]["text"]
    except Exception: title = "<sin titulo>"
    try: cid = v["ownerText"]["runs"][0]["navigationEndpoint"]["browseEndpoint"]["browseId"]
    except Exception: cid = None
    try: ch = v["ownerText"]["runs"][0]["text"]
    except Exception: ch = "?"
    return dict(title=title, channel=ch, cid=cid,
                sec=length_to_sec(v.get("lengthText",{}).get("simpleText","")),
                v=views_to_int(v.get("viewCountText",{}).get("simpleText","")))

# 1) recolectar candidatos CHICOS de formato OK
chicas = []
for puerta in PUERTAS:
    res = scrapetube.get_search(puerta, limit=PER_PUERTA)
    for v in itertools.islice(res, PER_PUERTA):
        r = parse(v)
        if MIN_SEC <= r["sec"] <= MAX_SEC and MIN_VIEWS <= r["v"] <= SMALL_MAX and r["cid"]:
            chicas.append(r)

print(f"Candidatos chicos a testear: {len(chicas)}")
print(f"Outlier fijo: ratio>={OUTLIER_MIN} + mediana>={PISO_MEDIANA:,}. Barriendo ABS_FLOOR.\n")

# 2) scrapear mediana UNA sola vez por canal (reusa para todos los pisos)
cache = {}
enriquecidos = []
for r in sorted(chicas, key=lambda x: -x["v"]):
    if r["cid"] not in cache:
        cache[r["cid"]] = _channel_baseline(r["cid"], BASELINE_N, exclude=r["v"])
        time.sleep(2.0)   # anti-ban
    med = cache[r["cid"]]
    r["median"] = med
    r["ratio"] = compute_ratio(r["v"], med) if med else 0.0
    enriquecidos.append(r)

# 3) BARRIDO de ABS_FLOOR sobre los mismos datos (sin re-scrapear)
def pasa(r, abs_floor):
    if r["v"] >= PISO_DEMANDA:                      # volumen
        return True
    return (r["median"] is not None and r["median"] >= PISO_MEDIANA   # outlier
            and r["ratio"] >= OUTLIER_MIN and r["v"] >= abs_floor)

print(f"{'VIEWS':>9} {'MEDIANA':>9} {'RATIO':>7}  " + "  ".join(f"{p//1000:>2}K" for p in PISOS) + "   CANAL / titulo")
print("-"*112)
for r in enriquecidos:
    med_s = f"{r['median']:,.0f}" if r["median"] else "—"
    marks = "  ".join(" ✅" if pasa(r, p) else " —" for p in PISOS)
    print(f"{r['v']:>9,} {med_s:>9} {r['ratio']:>7.1f}  {marks}  {r['channel'][:16]:<18} {r['title'][:34]}")

print(f"\n{'='*60}\nJOYAS POR PISO (de {len(enriquecidos)} candidatos chicos):")
for p in PISOS:
    n = sum(1 for r in enriquecidos if pasa(r, p))
    print(f"  ABS_FLOOR {p:>6,} → {n} joyas")
print("="*60)
print("OJO: ratio alto + mediana baja (canal chico/muerto) = falso positivo;")
print("mirá la columna MEDIANA al juzgar las que entran con pisos bajos.")