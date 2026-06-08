"""
_lab_wiki_gap_chat47.py — LAB AISLADO read-only (chat 47). Puerta 3 (Wikipedia).
NO toca el pipeline, NO escribe en prod salvo este lab y su output, $0, SIN proxy.

────────────────────────────────────────────────────────────────────────────
HIPÓTESIS FALSABLE (clavada ANTES de correr — NO interpretar acá):

  Caminando UNA categoría-raíz dark-history en profundidad y midiendo el gap EN/ES
  de cada entidad por pageviews, ¿el ranking por gap hace EMERGER arriba entidades
  atómicas reales del nicho (alta lectura EN + baja o nula ES) y HUNDE el ruido
  (puentes, estadios, ficción, baja lectura general)?

    MUERE si: arriba del ranking hay puro ruido, o el gap no discrimina (todo
    parecido), o las entidades buenas no suben.
────────────────────────────────────────────────────────────────────────────

PIEZA 1 — caminar el árbol (descubrimiento):
  Raíz: Category:Abandoned buildings and structures (en.wikipedia).
  MediaWiki Action API: list=categorymembers (cmtype=page junta, cmtype=subcat baja).
  GUARDS: prof máx 3 · set de visitadas (hay ciclos) · solo ns=0 · dedup páginas ·
          cap 200 categorías y 400 entidades únicas.

PIEZA 2 — gap EN/ES (ventana 90d, agent=user, all-access):
  EN: REST per-article en.wikipedia, suma 90d.
  langlinks EN→ES: BATCH (50 titles/call, prop=langlinks&lllang=es).
  ES: si hay título ES, REST per-article es.wikipedia, suma 90d; si no, es_sum=0.
  gap_ratio = en_sum / max(es_sum, 1).
  Labels: sin ES → VACIO · ES con pocas lecturas → HUECO · ES con muchas → SATURADO.
  Piso de demanda EN antes de rankear (los que no pasan van a sección "ruido").
  es_dudoso: si la página ES es de desambiguación (pageprops disambiguation).

CORTES ELEGIDOS (declarados, no escondidos):
  EN_FLOOR_90D   = 3000   (piso de demanda EN para entrar al ranking)
  ES_HUECO_MAX   = 1000   (es_sum_90d < 1000 → HUECO ; >= 1000 → SATURADO)
  WINDOW_DAYS    = 90

USO:
    python -X utf8 _lab_wiki_gap_chat47.py

Output: _lab_out/wiki_gap_chat47.json  (+ stdout: stats walk + tabla rankeada + ruido)
"""
from __future__ import annotations

import json
import sys
import time
from collections import deque
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
ES_ACTION = "https://es.wikipedia.org/w/api.php"
UA = ("automatization_videos-lab/0.1 "
      "(https://github.com/gueva1441/automatization_videos; research) "
      "python-requests")
HEADERS = {"User-Agent": UA}
OUT_JSON = Path("_lab_out/wiki_gap_chat47.json")

ROOT_CAT = "Category:Abandoned buildings and structures"

# Guards del walk
MAX_DEPTH = 3
CAP_CATEGORIES = 200
CAP_ENTITIES = 400

# Ventana y cortes (declarados)
WINDOW_DAYS = 90
DATA_LAG_DAYS = 2
EN_FLOOR_90D = 3000
ES_HUECO_MAX = 1000

# Cortesía
SLEEP_PV = 0.12      # per-article (no batcheable)
SLEEP_ACTION = 0.25  # action api (batcheado)


def _get(url: str, params: dict | None = None) -> dict | None:
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=25)
        if r.status_code == 200:
            return r.json()
        tail = url.split("/metrics/")[-1] if "/metrics/" in url else url
        print(f"    [HTTP {r.status_code}] {tail}")
        return None
    except Exception as e:
        print(f"    [ERR] {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  PIEZA 1 — WALK
# ══════════════════════════════════════════════════════════════════════════════
def _categorymembers(cmtitle: str, cmtype: str) -> list[dict]:
    """Trae TODOS los miembros (paginado) de una categoría, de un tipo dado."""
    out: list[dict] = []
    cmcontinue = None
    while True:
        p = {
            "action": "query", "format": "json", "list": "categorymembers",
            "cmtitle": cmtitle, "cmtype": cmtype, "cmlimit": 500,
        }
        if cmcontinue:
            p["cmcontinue"] = cmcontinue
        data = _get(EN_ACTION, p)
        time.sleep(SLEEP_ACTION)
        if not data:
            break
        out.extend(data.get("query", {}).get("categorymembers", []))
        cont = data.get("continue", {})
        cmcontinue = cont.get("cmcontinue")
        if not cmcontinue:
            break
    return out


def walk_tree() -> dict:
    print("\n" + "=" * 78)
    print(f"PIEZA 1 — WALK · raíz: {ROOT_CAT}")
    print(f"  guards: depth<={MAX_DEPTH} · cap {CAP_CATEGORIES} cats · cap {CAP_ENTITIES} entidades · ns=0")
    print("=" * 78)

    visited_cats: set[str] = set()
    entities: dict[str, dict] = {}   # title -> {subcat_origen, depth}
    raw_page_count = 0
    cats_visited = 0

    # BFS con (categoria, profundidad)
    q: deque[tuple[str, int]] = deque()
    q.append((ROOT_CAT, 0))
    visited_cats.add(ROOT_CAT)

    while q:
        if cats_visited >= CAP_CATEGORIES or len(entities) >= CAP_ENTITIES:
            print(f"  [CAP] corte: cats_visited={cats_visited} entidades={len(entities)}")
            break
        cat, depth = q.popleft()
        cats_visited += 1

        # páginas (ns=0) de esta categoría
        pages = _categorymembers(cat, "page")
        added_here = 0
        for m in pages:
            if m.get("ns") != 0:
                continue
            raw_page_count += 1
            title = m.get("title")
            if title and title not in entities:
                if len(entities) >= CAP_ENTITIES:
                    break
                entities[title] = {"subcat_origen": cat, "depth": depth}
                added_here += 1
        print(f"  [d{depth}] {cat[:60]:<60} +{added_here} pág (únicas acum: {len(entities)})")

        # bajar a subcats si no llegamos al fondo
        if depth < MAX_DEPTH and len(entities) < CAP_ENTITIES:
            subcats = _categorymembers(cat, "subcat")
            for sc in subcats:
                sct = sc.get("title")
                if sct and sct not in visited_cats:
                    visited_cats.add(sct)
                    q.append((sct, depth + 1))

    stats = {
        "root": ROOT_CAT,
        "cats_visited": cats_visited,
        "raw_pages_seen": raw_page_count,
        "unique_entities": len(entities),
        "hit_cap_categories": cats_visited >= CAP_CATEGORIES,
        "hit_cap_entities": len(entities) >= CAP_ENTITIES,
    }
    print(f"\n  WALK STATS: cats={cats_visited} · páginas crudas={raw_page_count} · "
          f"únicas tras dedup={len(entities)}")
    return {"stats": stats, "entities": entities}


# ══════════════════════════════════════════════════════════════════════════════
#  PIEZA 2 — GAP EN/ES
# ══════════════════════════════════════════════════════════════════════════════
def _pv_sum(project: str, title: str, start: str, end: str) -> int | None:
    """Suma de pageviews (agent=user, all-access) o None si no hay artículo."""
    url = (f"{PV_API}/per-article/{project}/all-access/user/"
           f"{quote(title.replace(' ', '_'), safe='')}/daily/{start}/{end}")
    data = _get(url)
    time.sleep(SLEEP_PV)
    if data and data.get("items"):
        return sum(int(it.get("views", 0)) for it in data["items"])
    return None


def _chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def batch_langlinks_es(titles: list[str]) -> dict[str, str]:
    """EN title -> ES title (si existe). Batch de 50 con prop=langlinks&lllang=es."""
    result: dict[str, str] = {}
    for chunk in _chunks(titles, 50):
        p = {
            "action": "query", "format": "json", "prop": "langlinks",
            "lllang": "es", "lllimit": 500, "titles": "|".join(chunk),
        }
        data = _get(EN_ACTION, p)
        time.sleep(SLEEP_ACTION)
        if not data:
            continue
        q = data.get("query", {})
        # mapa de normalización (título pedido -> normalizado por la API)
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        # construir mapa normalizado -> es
        norm_to_es: dict[str, str] = {}
        for _, pg in q.get("pages", {}).items():
            lls = pg.get("langlinks", [])
            if lls:
                norm_to_es[pg.get("title")] = lls[0].get("*")
        for t in chunk:
            key = norm.get(t, t)
            if key in norm_to_es:
                result[t] = norm_to_es[key]
    return result


def batch_es_disambig(es_titles: list[str]) -> set[str]:
    """Set de títulos ES que son páginas de desambiguación (pageprops disambiguation)."""
    dudosos: set[str] = set()
    uniq = sorted(set(es_titles))
    for chunk in _chunks(uniq, 50):
        p = {
            "action": "query", "format": "json", "prop": "pageprops",
            "ppprop": "disambiguation", "titles": "|".join(chunk),
        }
        data = _get(ES_ACTION, p)
        time.sleep(SLEEP_ACTION)
        if not data:
            continue
        q = data.get("query", {})
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        disambig_norm = set()
        for _, pg in q.get("pages", {}).items():
            if "disambiguation" in (pg.get("pageprops") or {}):
                disambig_norm.add(pg.get("title"))
        for t in chunk:
            if norm.get(t, t) in disambig_norm:
                dudosos.add(t)
    return dudosos


def measure_gap(entities: dict[str, dict]) -> list[dict]:
    print("\n" + "=" * 78)
    print(f"PIEZA 2 — GAP EN/ES · ventana {WINDOW_DAYS}d · user · all-access")
    print("=" * 78)

    end = date.today() - timedelta(days=DATA_LAG_DAYS)
    start = end - timedelta(days=WINDOW_DAYS)
    s, e = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")

    titles = list(entities.keys())
    n = len(titles)
    est_calls = n + (n // 50 + 1) + n + (n // 50 + 1)  # EN pv + langlinks + ES pv + disambig
    est_sec = int(n * SLEEP_PV * 2 + (n / 50) * SLEEP_ACTION * 2 + n * 0.05)
    print(f"  entidades: {n} · llamadas estimadas ~{est_calls} · "
          f"runtime estimado ~{est_sec}s ({est_sec//60}m{est_sec%60}s)")
    print(f"  ventana: {s} → {e}\n")

    # ── langlinks batch EN→ES ──
    print("  [langlinks] batch EN→ES (50/call)...")
    en_to_es = batch_langlinks_es(titles)
    print(f"    {len(en_to_es)}/{n} entidades tienen artículo ES")

    # ── disambig ES batch ──
    print("  [pageprops] batch ES disambig...")
    es_dudosos = batch_es_disambig(list(en_to_es.values()))
    print(f"    {len(es_dudosos)} títulos ES marcados como desambiguación (es_dudoso)")

    # ── pageviews por entidad ──
    print("  [pageviews] EN + ES por entidad (con sleep de cortesía)...")
    rows: list[dict] = []
    for i, title in enumerate(titles, 1):
        en_sum = _pv_sum("en.wikipedia", title, s, e) or 0
        es_title = en_to_es.get(title)
        has_es = es_title is not None
        es_sum = 0
        if has_es:
            es_sum = _pv_sum("es.wikipedia", es_title, s, e) or 0
        gap_ratio = en_sum / max(es_sum, 1)

        if not has_es:
            label = "VACIO"
        elif es_sum < ES_HUECO_MAX:
            label = "HUECO"
        else:
            label = "SATURADO"

        rows.append({
            "title": title,
            "subcat_origen": entities[title]["subcat_origen"],
            "depth": entities[title]["depth"],
            "en_sum_90d": en_sum,
            "has_es_article": has_es,
            "es_title": es_title,
            "es_sum_90d": es_sum,
            "gap_ratio": round(gap_ratio, 2),
            "label": label,
            "es_dudoso": (es_title in es_dudosos) if es_title else False,
            "passes_en_floor": en_sum >= EN_FLOOR_90D,
        })
        if i % 50 == 0:
            print(f"    ...{i}/{n}")

    return rows


# ══════════════════════════════════════════════════════════════════════════════
#  REPORTE
# ══════════════════════════════════════════════════════════════════════════════
def _baskets(rows: list[dict]) -> dict:
    """Tres canastas (intuición del scanner YouTube), ordenadas por en_sum_90d desc.
      ORO      = VACIO  + passes_en_floor  (no existe en ES + demanda EN fuerte)
      JOYA     = HUECO  + passes_en_floor  (existe ES pero poca lectura)
      DESCARTE = SATURADO, o cualquiera que NO pase el piso EN
    El gap_ratio queda en el JSON como dato pero NO ordena.
    """
    oro = [r for r in rows if r["label"] == "VACIO" and r["passes_en_floor"]]
    joya = [r for r in rows if r["label"] == "HUECO" and r["passes_en_floor"]]
    descarte = [r for r in rows
                if not (r["passes_en_floor"] and r["label"] in ("VACIO", "HUECO"))]
    oro.sort(key=lambda r: r["en_sum_90d"], reverse=True)
    joya.sort(key=lambda r: r["en_sum_90d"], reverse=True)
    descarte.sort(key=lambda r: r["en_sum_90d"], reverse=True)
    return {"oro": oro, "joya": joya, "descarte": descarte}


def _slim(r: dict) -> dict:
    return {
        "title": r["title"],
        "subcat_origen": r["subcat_origen"],
        "en_sum_90d": r["en_sum_90d"],
        "es_sum_90d": r["es_sum_90d"],
        "label": r["label"],
    }


def _print_basket(name: str, desc: str, items: list[dict]) -> None:
    print("\n" + "=" * 78)
    print(f"CANASTA {name} — {desc}")
    print(f"  {len(items)} entidades (orden: en_sum_90d desc)")
    print("=" * 78)
    print(f"  {'EN_90d':>9}  {'ES_90d':>8}  {'LABEL':<9} TÍTULO  ← subcat")
    print(f"  {'-'*9}  {'-'*8}  {'-'*9} {'-'*40}")
    for r in items:
        print(f"  {r['en_sum_90d']:>9,}  {r['es_sum_90d']:>8,}  {r['label']:<9} "
              f"{r['title'][:42]}  ← {r['subcat_origen'][9:40]}")


def report(rows: list[dict], walk_stats: dict) -> dict:
    label_counts = {l: sum(1 for r in rows if r["label"] == l)
                    for l in ("VACIO", "HUECO", "SATURADO")}
    n_pass = sum(1 for r in rows if r["passes_en_floor"])
    baskets = _baskets(rows)

    # ── stdout resumido ──
    print("\n" + "=" * 78)
    print("RESUMEN (lo único que se pega al chat — JSON completo queda en disco)")
    print("=" * 78)
    print(f"  walk: cats={walk_stats['cats_visited']} · páginas_crudas={walk_stats['raw_pages_seen']} "
          f"· únicas={walk_stats['unique_entities']} · "
          f"cap_cortó={'entidades' if walk_stats['hit_cap_entities'] else ('cats' if walk_stats['hit_cap_categories'] else 'ninguno')}")
    print(f"  labels: VACIO={label_counts['VACIO']} · HUECO={label_counts['HUECO']} "
          f"· SATURADO={label_counts['SATURADO']}  ·  pasan piso EN (>= {EN_FLOOR_90D}): {n_pass}")

    _print_basket("ORO", f"VACIO + demanda EN >= {EN_FLOOR_90D} (sin artículo ES)", baskets["oro"])
    _print_basket("JOYA", f"HUECO + demanda EN >= {EN_FLOOR_90D} (ES existe, poca lectura)", baskets["joya"])

    # muestra de 12 del descarte/ruido (auditar el filtro)
    print("\n" + "=" * 78)
    print(f"DESCARTE / RUIDO — muestra de 12 (de {len(baskets['descarte'])}) por en_sum desc")
    print("=" * 78)
    print(f"  {'EN_90d':>9}  {'ES_90d':>8}  {'LABEL':<9} {'PISO':<5} TÍTULO  ← subcat")
    print(f"  {'-'*9}  {'-'*8}  {'-'*9} {'-'*5} {'-'*40}")
    for r in baskets["descarte"][:12]:
        piso = "ok" if r["passes_en_floor"] else "NO"
        print(f"  {r['en_sum_90d']:>9,}  {r['es_sum_90d']:>8,}  {r['label']:<9} {piso:<5} "
              f"{r['title'][:42]}  ← {r['subcat_origen'][9:40]}")

    # ── objeto resumen para disco ──
    resumen = {
        "config": {
            "root_cat": ROOT_CAT, "max_depth": MAX_DEPTH,
            "cap_categories": CAP_CATEGORIES, "cap_entities": CAP_ENTITIES,
            "window_days": WINDOW_DAYS, "en_floor_90d": EN_FLOOR_90D,
            "es_hueco_max": ES_HUECO_MAX,
        },
        "walk_stats": walk_stats,
        "label_counts": label_counts,
        "pass_en_floor": n_pass,
        "oro": [_slim(r) for r in baskets["oro"]],
        "joya": [_slim(r) for r in baskets["joya"]],
        "descarte_sample_12": [_slim(r) for r in baskets["descarte"][:12]],
        "descarte_total": len(baskets["descarte"]),
    }
    return resumen


def main():
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    print("LAB GAP PUERTA 3 — Wikipedia (chat 47). read-only, $0, sin proxy.")
    print("Hipótesis falsable en el docstring. NO interpretar — solo material crudo.")

    walk = walk_tree()
    entities = walk["entities"]
    if not entities:
        print("\n  ⚠ Walk no trajo entidades. Abortando (revisar raíz).")
        return

    rows = measure_gap(entities)
    resumen = report(rows, walk["stats"])

    # JSON COMPLETO (400 entidades) en disco para trazabilidad
    out = {
        "config": resumen["config"],
        "walk_stats": walk["stats"],
        "entities": rows,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # JSON RESUMEN (lo que se pega al chat)
    resumen_path = OUT_JSON.parent / "wiki_gap_chat47_resumen.json"
    resumen_path.write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nGuardado completo (400): {OUT_JSON}")
    print(f"Guardado resumen:        {resumen_path}")


if __name__ == "__main__":
    main()
