"""
_lab_wiki_smoke_chat47.py — LAB AISLADO read-only (chat 47). NO toca el pipeline,
NO escribe en prod, $0. Smoke test de la PUERTA 3 (señales de lectura, Wikipedia).

Objetivo: decidir CON DATO, no con corazonada, si Wikipedia sirve como boca de
embudo para el nicho dark-history/misterio — y si sirve, QUÉ versión construir
(most-read del día vs pageviews sostenidos por categoría).

Wikimedia Pageviews API (REST/AQS): gratis, oficial, SIN proxy, SIN API key.
Solo requiere User-Agent descriptivo. La data tiene ~1-2 días de lag.

────────────────────────────────────────────────────────────────────────────
HIPÓTESIS FALSABLE (clavada ANTES de correr — el lab TIENE que poder fallar):

  H1 (descubrimiento):  el most-read EN del día contiene entidades dark-history
                        atómicas del nicho, no solo evento-actual.
       → MUERE si: el subconjunto marcado por el léxico del nicho es ~vacío o
         puro genérico (p.ej. "disaster" matcheando una película de estreno).

  H2 (los conocidos):   Centralia / búnkers de Albania / Corpsewood tienen
                        tráfico de lectura sostenido real en Wikipedia.
       → MUERE si: tráfico ~nulo o inexistente (la entidad no vive en Wikipedia).

  H3 (la que DECIDE qué construir):  ¿los conocidos son EVERGREEN estable o
                        PICO puntual? ¿aparecieron alguna vez en el most-read?
       → Si tienen tráfico fuerte SOSTENIDO pero NUNCA trendean en el día →
         el primitivo correcto NO es "most-read de hoy", es "pageviews
         sostenidos por categoría". El smoke test dice qué Puerta 3 construir.

ESTE LAB NO TOCA el lado ES (scanner) ni el gap EN/ES. Eso es la etapa siguiente,
SOLO si esto sobrevive. Una cosa a la vez.
────────────────────────────────────────────────────────────────────────────

USO:
    python -X utf8 _lab_wiki_smoke_chat47.py

Output: _lab_out/wiki_smoke_chat47.json  (+ tabla legible a stdout)
"""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

import requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Config ──────────────────────────────────────────────────────────────────
API = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
PROJECT = "en.wikipedia"
UA = ("automatization_videos-lab/0.1 "
      "(https://github.com/gueva1441/automatization_videos; research) "
      "python-requests")
HEADERS = {"User-Agent": UA}
OUT_JSON = Path("_lab_out/wiki_smoke_chat47.json")

WINDOW_DAYS_FEED = 14        # Sonda 1: días de most-read a acumular
WINDOW_DAYS_ARTICLE = 180    # Sonda 2: días de per-article hacia atrás
DATA_LAG_DAYS = 2            # la API no tiene "hoy"; arrancamos hace 2 días
TOP_RAW_SHOW = 50            # cuántos del feed crudo mostrar en stdout
SLEEP = 0.4                  # cortesía con la API

# Léxico FLOJO del nicho (a propósito laxo: queremos ver si emerge ALGO).
# Match = cualquiera de estas subcadenas en el título normalizado (lower, _→espacio).
NICHE_LEXICON = [
    "disaster", "catastrophe", "tragedy", "abandoned", "ghost town", "ruins",
    "ruin", "deserted", "nuclear", "radiation", "radioactive", "chernobyl",
    "fukushima", "meltdown", "cult", "massacre", "murder", "killer", "serial",
    "mystery", "mysterious", "unsolved", "disappearance", "disappeared",
    "missing", "vanished", "haunted", "haunting", "shipwreck", "wreck", "sinking",
    "sank", "sunk", "explosion", "exploded", "blast", "mine ", "mining", "asylum",
    "sanatorium", "prison", "penitentiary", "plague", "epidemic", "pandemic",
    "outbreak", "bunker", "cold war", "conspiracy", "occult", "ritual", "satanic",
    "cursed", "expedition", "lost", "buried", "collapse", "collapsed", "famine",
    "fire", "wildfire", "earthquake", "tsunami", "eruption", "volcano", "flood",
    "crash", "hijack", "kidnapping", "hostage", "execution", "torture", "asbestos",
    "leper", "leprosy", "quarantine", "island", "fortress", "catacomb",
]

# Conocidos para Sonda 2. Cada uno con TÍTULOS CANDIDATOS (probamos en orden,
# usamos el primero que devuelva data; reportamos cuál resolvió y cuáles 404).
KNOWN_ENTITIES = {
    "Centralia (PA mine fire)": [
        "Centralia,_Pennsylvania",
        "Centralia_mine_fire",
    ],
    "Albanian bunkers": [
        "Bunkers_in_Albania",
        "Bunkerisation_of_Albania",
        "Albanian_bunkers",
    ],
    "Corpsewood Manor": [
        "Corpsewood_Manor_murders",
        "Corpsewood_Manor",
        "Corpsewood",
    ],
}


def _get(url: str) -> dict | None:
    """GET con UA. None si falla (logueado). No revienta el lab por un 404."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            return r.json()
        print(f"    [HTTP {r.status_code}] {url.split('/metrics/')[-1]}")
        return None
    except Exception as e:
        print(f"    [ERR] {e} :: {url.split('/metrics/')[-1]}")
        return None


def _norm(title: str) -> str:
    return title.replace("_", " ").strip().lower()


def _is_junk(article: str) -> bool:
    """Filtra ruido estructural del top de Wikipedia."""
    if article in ("Main_Page", "-", "Special:Search", "Wikipedia:Featured_pictures"):
        return True
    for pre in ("Special:", "Wikipedia:", "Portal:", "Help:", "Category:",
                "Template:", "User:", "File:", "Talk:"):
        if article.startswith(pre):
            return True
    return False


def _niche_hits(title_norm: str) -> list[str]:
    return [kw.strip() for kw in NICHE_LEXICON if kw in title_norm]


# ── Sonda 1: most-read feed (¿descubre?) ──────────────────────────────────────
def sonda1_feed() -> dict:
    print("\n" + "=" * 78)
    print("SONDA 1 — most-read EN del día (¿el feed descubre el nicho?)")
    print("=" * 78)

    end = date.today() - timedelta(days=DATA_LAG_DAYS)
    days = [end - timedelta(days=i) for i in range(WINDOW_DAYS_FEED)]

    agg_views: dict[str, int] = defaultdict(int)
    agg_days: dict[str, int] = defaultdict(int)
    days_ok = 0
    for d in days:
        url = f"{API}/top/{PROJECT}/all-access/{d.year}/{d.month:02d}/{d.day:02d}"
        data = _get(url)
        time.sleep(SLEEP)
        if not data:
            continue
        try:
            articles = data["items"][0]["articles"]
        except (KeyError, IndexError):
            continue
        days_ok += 1
        for a in articles:
            art = a.get("article", "")
            if _is_junk(art):
                continue
            agg_views[art] += int(a.get("views", 0))
            agg_days[art] += 1

    print(f"\nDías de feed OK: {days_ok}/{WINDOW_DAYS_FEED} · "
          f"artículos únicos (sin junk): {len(agg_views)}")

    ranked = sorted(agg_views.items(), key=lambda kv: kv[1], reverse=True)

    # Feed crudo (top N) — para ver el sesgo a evento-actual con tus propios ojos
    print(f"\n--- FEED CRUDO (top {TOP_RAW_SHOW} por views acumuladas) ---")
    for art, v in ranked[:TOP_RAW_SHOW]:
        flag = " <NICHO?>" if _niche_hits(_norm(art)) else ""
        print(f"  {v:>10,}  ({agg_days[art]:>2}d)  {art}{flag}")

    # Subconjunto marcado por el léxico del nicho — LA pregunta de H1
    marked = [(art, v, _niche_hits(_norm(art))) for art, v in ranked
              if _niche_hits(_norm(art))]
    print(f"\n--- MARCADOS POR LÉXICO DEL NICHO ({len(marked)} de {len(agg_views)}) ---")
    if not marked:
        print("  (vacío — el feed del día no trae nada del nicho)")
    for art, v, hits in marked[:60]:
        print(f"  {v:>10,}  {art}   ← {','.join(hits)}")

    feed_titles_norm = {_norm(a) for a in agg_views}
    return {
        "days_requested": WINDOW_DAYS_FEED,
        "days_ok": days_ok,
        "unique_articles": len(agg_views),
        "top_raw": [{"article": a, "views": v, "days_in_top": agg_days[a]}
                    for a, v in ranked[:TOP_RAW_SHOW]],
        "niche_marked": [{"article": a, "views": v, "hits": h}
                         for a, v, h in marked],
        "_feed_titles_norm": sorted(feed_titles_norm),  # para cross-check sonda 2
    }


# ── Sonda 2: per-article (¿los conocidos viven? evergreen vs pico) ────────────
def sonda2_known(feed_titles_norm: set[str]) -> dict:
    print("\n" + "=" * 78)
    print("SONDA 2 — per-article de conocidos (¿viven? ¿evergreen o pico?)")
    print("=" * 78)

    end = date.today() - timedelta(days=DATA_LAG_DAYS)
    start = end - timedelta(days=WINDOW_DAYS_ARTICLE)
    s, e = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")

    out = {}
    for label, candidates in KNOWN_ENTITIES.items():
        print(f"\n  · {label}")
        resolved = None
        series = None
        tried = []
        for title in candidates:
            url = (f"{API}/per-article/{PROJECT}/all-access/user/"
                   f"{quote(title, safe='')}/daily/{s}/{e}")
            data = _get(url)
            time.sleep(SLEEP)
            if data and data.get("items"):
                resolved = title
                series = [int(it.get("views", 0)) for it in data["items"]]
                break
            tried.append(title)

        if not series:
            print(f"    NO RESOLVIÓ ningún candidato: {candidates}")
            out[label] = {"resolved_title": None, "tried": candidates,
                          "error": "no candidate returned data"}
            continue

        total = sum(series)
        n = len(series)
        mean = total / n if n else 0
        mx = max(series)
        srt = sorted(series)
        median = srt[n // 2] if n else 0
        p90 = srt[int(n * 0.9)] if n else 0
        spike_ratio = (mx / mean) if mean else 0

        # ¿apareció en el feed de la sonda 1? (cross-check H3)
        in_feed = _norm(resolved) in feed_titles_norm

        print(f"    resolvió: {resolved}  ({n} días)")
        print(f"    total={total:,}  media/día={mean:,.0f}  mediana/día={median:,}  "
              f"p90={p90:,}  max/día={mx:,}")
        print(f"    spike_ratio (max/media)={spike_ratio:.1f}  "
              f"→ {'PICO' if spike_ratio >= 8 else 'EVERGREEN-ish'}")
        print(f"    ¿apareció en el most-read de Sonda 1? "
              f"{'SÍ' if in_feed else 'NO'}")

        out[label] = {
            "resolved_title": resolved,
            "days": n,
            "total_views": total,
            "mean_daily": round(mean, 1),
            "median_daily": median,
            "p90_daily": p90,
            "max_daily": mx,
            "spike_ratio": round(spike_ratio, 2),
            "shape_hint": "PICO" if spike_ratio >= 8 else "EVERGREEN-ish",
            "appeared_in_feed_sonda1": in_feed,
        }
    return out


def main():
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    print("LAB SMOKE PUERTA 3 — Wikipedia (chat 47). read-only, $0, sin proxy.")
    print("Hipótesis falsable en el docstring del archivo. Leer ANTES de interpretar.")

    s1 = sonda1_feed()
    feed_titles = set(s1.pop("_feed_titles_norm"))
    s2 = sonda2_known(feed_titles)

    # Lectura NEUTRA — solo enuncia qué dice el dato, sin teñir con fe.
    print("\n" + "=" * 78)
    print("LECTURA (neutra — contrastá contra la hipótesis del docstring)")
    print("=" * 78)
    n_marked = len(s1["niche_marked"])
    print(f"H1 (¿feed descubre?): {n_marked} marcados del nicho en {s1['days_ok']} días "
          f"de feed. Mirá CUÁLES arriba: ¿entidades atómicas reales o evento-actual?")
    any_resolved = [v for v in s2.values() if v.get("resolved_title")]
    print(f"H2 (¿conocidos viven?): {len(any_resolved)}/{len(s2)} resolvieron con "
          f"tráfico medible. (ver media/día arriba)")
    in_feed_any = any(v.get("appeared_in_feed_sonda1") for v in s2.values())
    print(f"H3 (evergreen vs pico): ningún conocido en el feed = "
          f"{'CONFIRMA' if not in_feed_any else 'NO confirma'} la tesis "
          f"'most-read del día NO es la boca de embudo correcta'.")
    print("    → si los conocidos son fuertes+sostenidos pero NO trendean, el "
          "primitivo a construir es PAGEVIEWS SOSTENIDOS POR CATEGORÍA, no el feed.")

    report = {"sonda1_feed": s1, "sonda2_known": s2}
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\nGuardado: {OUT_JSON}")


if __name__ == "__main__":
    main()
