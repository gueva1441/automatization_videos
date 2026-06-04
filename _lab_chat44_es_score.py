"""LAB chat 44 v2 — score hueco ES (cobertura ponderada). Aislado, no toca prod.
v2: queries ES + grafía ES + extracción robusta de fecha + dump del publishedTimeText crudo."""
import scrapetube, itertools, json
from script_engine.youtube_scanner import (
    detect_language, _parse_views_scrapetube, _parse_date_scrapetube_months_ago,
    title_contains_anchor, _proxies_dict,
)
from niche_discoverer import extract_anchors

LIMIT = 25

# FIX #1+#2: queries en ESPAÑOL, con grafía ES de nombres propios (como saldría de Gemini)
TESTS = [
    ("Apolo 13",          "tragedia del Apolo 13",                       "SATURADO"),
    ("Kursk",             "desastre del submarino Kursk",                "HUECO/DISPUTADO (tesis)"),
    ("Alexander Kielland","hundimiento plataforma Alexander Kielland",   "VACÍO"),
    # agregá más temas ES conocidos para afinar los cortes
]

# FIX #3: extracción robusta — probar simpleText, si vacío caer a runs[].text
def pub_text(v) -> str:
    p = v.get("publishedTimeText", {}) or {}
    if p.get("simpleText"):
        return p["simpleText"]
    runs = p.get("runs") or []
    return "".join(r.get("text", "") for r in runs)

def age_decay(months: int) -> float:
    if months <= 12: return 1.0
    if months <= 36: return 0.6
    if months <= 60: return 0.3
    return 0.1

def label_for(sat: float) -> str:
    if sat <= 0:        return "VACÍO"
    if sat < 30_000:    return "HUECO"
    if sat < 150_000:   return "DISPUTADO"
    return "SATURADO"

for human, query, expected in TESTS:
    anchors = extract_anchors(query)
    try:
        vids = list(itertools.islice(scrapetube.get_search(query, limit=LIMIT, proxies=_proxies_dict()), LIMIT))
    except Exception as e:
        print(f"\n### {human}  → ERROR scrape: {e}")
        continue

    ontopic = []
    for v in vids:
        try:
            title = v["title"]["runs"][0]["text"]
        except (KeyError, IndexError):
            continue
        if detect_language(title) != "es":
            continue
        if not title_contains_anchor(title, anchors):
            continue
        raw_pub = v.get("publishedTimeText", {})          # ← dump crudo para diagnosticar el 999
        txt = pub_text(v)
        months = _parse_date_scrapetube_months_ago(txt)
        views = _parse_views_scrapetube(v)
        decay = age_decay(months)
        ontopic.append({"title": title, "views": views, "months": months, "decay": decay,
                        "eff": views * decay, "raw_pub": raw_pub, "txt": txt})

    ontopic.sort(key=lambda o: o["eff"], reverse=True)
    sat = ontopic[0]["eff"] if ontopic else 0
    lab = label_for(sat)

    print(f"\n{'='*74}")
    print(f"### {human}   query='{query}'   ancla={anchors}")
    print(f"    on-topic ES: {len(ontopic)}  ·  saturación={sat:,.0f}  →  {lab}   (esperado: {expected})")
    for o in ontopic[:6]:
        print(f"    {o['views']:>10,}v  {o['months']:>3}m  ×{o['decay']}  → {o['eff']:>11,.0f}ef  "
              f"| pub_raw={json.dumps(o['raw_pub'], ensure_ascii=False)[:60]} txt='{o['txt']}' "
              f"| {o['title'][:42]}")
    if not ontopic:
        print(f"    (0 on-topic — revisá si la ancla descartó todo o el idioma)")
