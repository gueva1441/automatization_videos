"""
_lab_wiki_apisurf_chat47.py — LAB AISLADO read-only (chat 47). RELEVAMIENTO, no experimento.
NO toca el pipeline, NO escribe en prod, $0, SIN proxy (Wikipedia es API pública).

Objetivo: relevar la FORMA de dos superficies de la API de Wikimedia para diseñar la
Puerta 3 más adelante. NO saca conclusiones — solo trae el material crudo (shapes reales,
keys, sumas EN vs ES, paginado) a stdout + _lab_out/wiki_apisurf_chat47.json.

SUPERFICIES:
  A) Pageviews API   (https://wikimedia.org/api/rest_v1/metrics/pageviews)
     - /top/en.wikipedia/all-access/{Y}/{M}/{D}
     - /per-article ... user vs all-agents (cuánto inflan los bots)
     - per-article desglosado desktop / mobile-web / mobile-app
  B) MediaWiki Action API (https://en.wikipedia.org/w/api.php)
     - categorymembers (page y subcat) + paginado (continue)
     - search
     - langlinks EN→ES, y luego pageviews es.wikipedia (gap EN/ES medio armado)

Pageviews API tiene ~1-2 días de lag y requiere User-Agent descriptivo (sin API key).

USO:
    python -X utf8 _lab_wiki_apisurf_chat47.py

Output: _lab_out/wiki_apisurf_chat47.json  (+ stdout legible)
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

import requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Config ──────────────────────────────────────────────────────────────────
PV_API = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
EN_ACTION = "https://en.wikipedia.org/w/api.php"
UA = ("automatization_videos-lab/0.1 "
      "(https://github.com/gueva1441/automatization_videos; research) "
      "python-requests")
HEADERS = {"User-Agent": UA}
OUT_JSON = Path("_lab_out/wiki_apisurf_chat47.json")

DATA_LAG_DAYS = 2
WINDOW_30 = 30
SLEEP = 0.4


def _get(url: str, params: dict | None = None) -> dict | None:
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=20)
        if r.status_code == 200:
            return r.json()
        tail = url.split("/metrics/")[-1] if "/metrics/" in url else url
        print(f"    [HTTP {r.status_code}] {tail} {params or ''}")
        return None
    except Exception as e:
        print(f"    [ERR] {e} :: {url}")
        return None


def _pv_per_article(project: str, title: str, agent: str, access: str,
                    start: str, end: str) -> list[int] | None:
    url = (f"{PV_API}/per-article/{project}/{access}/{agent}/"
           f"{quote(title, safe='')}/daily/{start}/{end}")
    data = _get(url)
    time.sleep(SLEEP)
    if data and data.get("items"):
        return data["items"]
    return None


def _sum(items: list[dict] | None) -> int:
    return sum(int(it.get("views", 0)) for it in (items or []))


# ══════════════════════════════════════════════════════════════════════════════
#  A) PAGEVIEWS API
# ══════════════════════════════════════════════════════════════════════════════
def surf_pageviews() -> dict:
    print("\n" + "=" * 78)
    print("A) PAGEVIEWS API")
    print("=" * 78)
    out: dict = {}

    end = date.today() - timedelta(days=DATA_LAG_DAYS)
    start30 = end - timedelta(days=WINDOW_30)
    s30, e30 = start30.strftime("%Y%m%d"), end.strftime("%Y%m%d")

    # ── A1. /top ──
    print(f"\n[A1] /top/en.wikipedia/all-access/{end.year}/{end.month:02d}/{end.day:02d}")
    top_url = f"{PV_API}/top/en.wikipedia/all-access/{end.year}/{end.month:02d}/{end.day:02d}"
    top = _get(top_url)
    time.sleep(SLEEP)
    a1: dict = {"date": end.isoformat(), "url": top_url}
    if top:
        items0 = top["items"][0]
        a1["items0_keys"] = sorted(items0.keys())
        a1["items0_meta"] = {k: v for k, v in items0.items() if k != "articles"}
        a1["n_articles"] = len(items0.get("articles", []))
        sample = items0["articles"][0] if items0.get("articles") else {}
        a1["sample_article"] = sample
        a1["sample_article_keys"] = sorted(sample.keys())
        print(f"    items[0] keys: {a1['items0_keys']}")
        print(f"    items[0] meta: {a1['items0_meta']}")
        print(f"    n articles: {a1['n_articles']}")
        print(f"    sample article (rank 1): {sample}")
    else:
        a1["error"] = "no data"
    out["A1_top"] = a1

    # ── A2. per-article: user vs all-agents ──
    title = "Centralia,_Pennsylvania"
    print(f"\n[A2] per-article '{title}' últimos 30d ({s30}→{e30}) — user vs all-agents")
    user_items = _pv_per_article("en.wikipedia", title, "user", "all-access", s30, e30)
    allag_items = _pv_per_article("en.wikipedia", title, "all-agents", "all-access", s30, e30)
    sum_user = _sum(user_items)
    sum_allag = _sum(allag_items)
    inflate = (sum_allag / sum_user) if sum_user else 0
    a2: dict = {
        "title": title,
        "window": f"{s30}-{e30}",
        "sum_user": sum_user,
        "sum_all_agents": sum_allag,
        "bot_inflation_ratio_all_over_user": round(inflate, 3),
        "item_keys": sorted(user_items[0].keys()) if user_items else None,
        "sample_item_user": user_items[0] if user_items else None,
    }
    print(f"    sum user       = {sum_user:,}")
    print(f"    sum all-agents = {sum_allag:,}")
    print(f"    inflación (all-agents / user) = {inflate:.3f}x")
    print(f"    item keys: {a2['item_keys']}")
    print(f"    sample item (user): {a2['sample_item_user']}")
    out["A2_user_vs_allagents"] = a2

    # ── A3. desglose por access (desktop / mobile-web / mobile-app), sumas 30d ──
    print(f"\n[A3] per-article '{title}' 30d desglosado por access (agent=user) — sumas")
    a3: dict = {"title": title, "window": f"{s30}-{e30}", "agent": "user", "by_access": {}}
    for access in ("desktop", "mobile-web", "mobile-app"):
        items = _pv_per_article("en.wikipedia", title, "user", access, s30, e30)
        ssum = _sum(items)
        a3["by_access"][access] = ssum
        print(f"    {access:<12} = {ssum:,}")
    out["A3_by_access"] = a3

    out["_centralia_en_user_sum_30d"] = sum_user  # para el gap EN/ES en B5
    out["_window_30d"] = {"start": s30, "end": e30}
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  B) MEDIAWIKI ACTION API
# ══════════════════════════════════════════════════════════════════════════════
def surf_action(pv_ctx: dict) -> dict:
    print("\n" + "=" * 78)
    print("B) MEDIAWIKI ACTION API")
    print("=" * 78)
    out: dict = {}

    # ── B1. categorymembers cmtype=page ──
    print("\n[B1] categorymembers 'Category:Abandoned_places' cmlimit=20 cmtype=page")
    p = {
        "action": "query", "format": "json", "list": "categorymembers",
        "cmtitle": "Category:Abandoned_places", "cmlimit": 20, "cmtype": "page",
    }
    data = _get(EN_ACTION, p)
    time.sleep(SLEEP)
    b1: dict = {"params": p}
    if data:
        members = data.get("query", {}).get("categorymembers", [])
        b1["titles"] = [m.get("title") for m in members]
        b1["item_keys"] = sorted(members[0].keys()) if members else None
        b1["sample_item"] = members[0] if members else None
        b1["continue"] = data.get("continue")
        print(f"    {len(b1['titles'])} títulos:")
        for t in b1["titles"]:
            print(f"      - {t}")
        print(f"    item keys: {b1['item_keys']}")
        print(f"    continue: {b1['continue']}")
    else:
        b1["error"] = "no data"
    out["B1_categorymembers_page"] = b1

    # ── B2. categorymembers cmtype=subcat ──
    print("\n[B2] categorymembers 'Category:Abandoned_places' cmlimit=20 cmtype=subcat")
    p = {
        "action": "query", "format": "json", "list": "categorymembers",
        "cmtitle": "Category:Abandoned_places", "cmlimit": 20, "cmtype": "subcat",
    }
    data = _get(EN_ACTION, p)
    time.sleep(SLEEP)
    b2: dict = {"params": p}
    if data:
        members = data.get("query", {}).get("categorymembers", [])
        b2["titles"] = [m.get("title") for m in members]
        b2["item_keys"] = sorted(members[0].keys()) if members else None
        b2["continue"] = data.get("continue")
        print(f"    {len(b2['titles'])} subcategorías:")
        for t in b2["titles"]:
            print(f"      - {t}")
        print(f"    continue: {b2['continue']}")
    else:
        b2["error"] = "no data"
    out["B2_categorymembers_subcat"] = b2

    # ── B3. search ──
    print("\n[B3] search srsearch='abandoned soviet bunker' srlimit=8")
    p = {
        "action": "query", "format": "json", "list": "search",
        "srsearch": "abandoned soviet bunker", "srlimit": 8,
    }
    data = _get(EN_ACTION, p)
    time.sleep(SLEEP)
    b3: dict = {"params": p}
    if data:
        hits = data.get("query", {}).get("search", [])
        b3["titles"] = [h.get("title") for h in hits]
        b3["hit_keys"] = sorted(hits[0].keys()) if hits else None
        b3["sample_hit"] = hits[0] if hits else None
        b3["totalhits"] = data.get("query", {}).get("searchinfo", {}).get("totalhits")
        print(f"    {len(b3['titles'])} hits (totalhits={b3['totalhits']}):")
        for t in b3["titles"]:
            print(f"      - {t}")
        print(f"    hit keys: {b3['hit_keys']}")
    else:
        b3["error"] = "no data"
    out["B3_search"] = b3

    # ── B4. langlinks EN→ES ──
    en_title = "Centralia, Pennsylvania"
    print(f"\n[B4] langlinks '{en_title}' lllang=es")
    p = {
        "action": "query", "format": "json", "prop": "langlinks",
        "titles": en_title, "lllang": "es",
    }
    data = _get(EN_ACTION, p)
    time.sleep(SLEEP)
    b4: dict = {"params": p}
    es_title = None
    if data:
        pages = data.get("query", {}).get("pages", {})
        b4["raw_pages"] = pages
        for _, pg in pages.items():
            lls = pg.get("langlinks", [])
            if lls:
                es_title = lls[0].get("*")
        b4["es_title"] = es_title
        print(f"    ES title: {es_title}")
    else:
        b4["error"] = "no data"
    out["B4_langlinks"] = b4

    # ── B5. pageviews es.wikipedia del título ES → gap EN/ES ──
    print(f"\n[B5] pageviews es.wikipedia per-article 30d (user) del título ES → gap EN/ES")
    b5: dict = {}
    win = pv_ctx.get("_window_30d", {})
    s30, e30 = win.get("start"), win.get("end")
    en_sum = pv_ctx.get("_centralia_en_user_sum_30d", 0)
    if es_title and s30 and e30:
        es_title_us = es_title.replace(" ", "_")
        es_items = _pv_per_article("es.wikipedia", es_title_us, "user", "all-access", s30, e30)
        es_sum = _sum(es_items)
        b5 = {
            "es_title": es_title,
            "window": f"{s30}-{e30}",
            "sum_es_user": es_sum,
            "sum_en_user": en_sum,
            "en_over_es_ratio": round((en_sum / es_sum), 2) if es_sum else None,
        }
        print(f"    ES '{es_title}' sum user 30d = {es_sum:,}")
        print(f"    EN 'Centralia,_Pennsylvania' sum user 30d = {en_sum:,}")
        print(f"    ratio EN/ES = {b5['en_over_es_ratio']}")
    else:
        b5 = {"error": "no es_title o ventana — no se pudo medir gap"}
        print(f"    (no se pudo medir: es_title={es_title})")
    out["B5_gap_en_es"] = b5

    return out


def main():
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    print("LAB API SURF — Wikimedia (chat 47). read-only, $0, sin proxy. RELEVAMIENTO.")
    print("Solo material crudo (shapes/keys/sumas). NO interpretar.")

    a = surf_pageviews()
    b = surf_action(a)

    # limpiar claves internas del dump
    a.pop("_centralia_en_user_sum_30d", None)
    a.pop("_window_30d", None)

    report = {"A_pageviews": a, "B_action_api": b}
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\nGuardado: {OUT_JSON}")


if __name__ == "__main__":
    main()
