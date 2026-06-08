"""
_lab_atomicity_chat48.py — LAB AISLADO read-only (chat 48). Clasificador de ATOMICIDAD.
NO toca prod (topics_db/selected_seeds/módulos). Solo escribe en _lab_out/. Chat-only.

────────────────────────────────────────────────────────────────────────────
HIPÓTESIS FALSABLE:
  La salida del gap (Puerta 3) trae suciedad en ORO/JOYA: conceptos (Crofting, Modern
  ruins, Rooftopping), actividades, listas, ficción. Un LLM clasifica TIPO (atómico-
  producible vs concepto/lista/ficción) y limpia la materia prima antes del scanner.

  MUERE si: el clasificador no separa los CONTROLES conocidos (un solo FAIL = no sirve).

Doble propósito:
  1. Validar el clasificador contra el answer-key del árbol de lugares (sección gate).
  2. Primer test real de 2 raíces nuevas (Man-made disasters, Unsolved murders): ¿generaliza?

REUSO de _lab_wiki_gap_chat47.py (importable, su walk NO se dispara solo):
  - _categorymembers(cmtitle, cmtype)  — miembros paginados de una categoría
  - measure_gap(entities)              — pageviews EN/ES + label + passes_en_floor
  - EN_FLOOR_90D, ES_HUECO_MAX         — mismos cortes (no se tocan)
El walk se RE-ESCRIBE acá parametrizado por raíz (no se modifica el chat47).

CLASIFICADOR (Gemini Flash, temperature=0.0, response_schema):
  - corre SOLO sobre ORO+JOYA (label∈{VACIO,HUECO} y passes_en_floor)
  - input por entidad: SOLO title + subcat_origen + root_origen (NUNCA pageviews)
  - output: type + reason; keep se DERIVA en Python (keep = type∈{ATOMIC_PLACE,ATOMIC_EVENT})

Correr:  python -X utf8 _lab_atomicity_chat48.py
Output:  _lab_out/atomicity_chat48_full.json  +  _lab_out/atomicity_chat48_resumen.json
"""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Reuso del chat 47 (NO se modifica ese archivo) ──
from _lab_wiki_gap_chat47 import (
    _categorymembers, measure_gap, EN_FLOOR_90D, ES_HUECO_MAX, WINDOW_DAYS,
)
# ── Cliente Gemini directo (call_flash_json no soporta response_schema; no lo tocamos) ──
from gemini_helpers import _client, _cfg, types, _with_retry

OUT_DIR = Path("_lab_out")
OUT_FULL = OUT_DIR / "atomicity_chat48_full.json"
OUT_RESUMEN = OUT_DIR / "atomicity_chat48_resumen.json"

# ── Raíces (3, exactas) + caps POR RAÍZ (decididas) ──
ROOTS = [
    "Category:Abandoned buildings and structures",
    "Category:Man-made disasters",
    "Category:Unsolved murders",
]
MAX_DEPTH = 3
CAP_CATEGORIES = 150
CAP_ENTITIES = 700

CLASSIFY_BATCH = 25
SLEEP_ACTION = 0.25

KEEP_TYPES = {"ATOMIC_PLACE", "ATOMIC_EVENT"}

# ── Controles del gate (answer-key). NO van al few-shot. ──
GATE_DIRTY = [  # esperado keep=False
    "Crofting", "Modern ruins", "Rooftopping", "Mole people", "Passive rewilding",
    "Nerdy Prudes Must Die", "List of former and unopened London Underground stations",
]
GATE_GEMS = [  # esperado keep=True
    "Trans-Allegheny Lunatic Asylum", "Charity Hospital (New Orleans)",
    "Packard Automotive Plant", "Sathorn Unique Tower", "Newsham Park Hospital",
]


# ══════════════════════════════════════════════════════════════════════════════
#  WALK parametrizado por raíz (reusa _categorymembers del chat 47)
# ══════════════════════════════════════════════════════════════════════════════
def walk_root(root: str, max_depth: int, cap_cats: int, cap_entities: int) -> dict:
    """BFS de UNA raíz. Devuelve {title: {subcat_origen, depth}} + stats.
    Guards: depth<=max_depth · set de visitadas (hay ciclos) · solo ns=0 · dedup · caps."""
    print(f"\n  WALK raíz: {root}")
    visited: set[str] = {root}
    entities: dict[str, dict] = {}
    raw_pages = 0
    cats_visited = 0
    q: deque[tuple[str, int]] = deque([(root, 0)])

    while q:
        if cats_visited >= cap_cats or len(entities) >= cap_entities:
            print(f"    [CAP] corte: cats={cats_visited} entidades={len(entities)}")
            break
        cat, depth = q.popleft()
        cats_visited += 1

        for m in _categorymembers(cat, "page"):
            if m.get("ns") != 0:
                continue
            raw_pages += 1
            t = m.get("title")
            if t and t not in entities:
                if len(entities) >= cap_entities:
                    break
                entities[t] = {"subcat_origen": cat, "depth": depth}

        if depth < max_depth and len(entities) < cap_entities:
            for sc in _categorymembers(cat, "subcat"):
                sct = sc.get("title")
                if sct and sct not in visited:
                    visited.add(sct)
                    q.append((sct, depth + 1))

    stats = {
        "root": root, "cats_visited": cats_visited, "raw_pages_seen": raw_pages,
        "unique_entities": len(entities),
        "hit_cap_categories": cats_visited >= cap_cats,
        "hit_cap_entities": len(entities) >= cap_entities,
    }
    print(f"    stats: cats={cats_visited} · crudas={raw_pages} · únicas={len(entities)}")
    return {"stats": stats, "entities": entities}


# ══════════════════════════════════════════════════════════════════════════════
#  CLASIFICADOR (Gemini Flash, schema, temp 0.0)
# ══════════════════════════════════════════════════════════════════════════════
SYSTEM_INSTRUCTION = (
    "Sos un clasificador de TIPO de entidades de Wikipedia para un pipeline de video. "
    "Tu ÚNICA tarea es decidir QUÉ TIPO de cosa es cada entrada, mirando solo su título y "
    "la categoría de la que cuelga. NO juzgás si es popular, viral ni si sería un buen video: "
    "la demanda se mide en OTRO lado y no es tu problema. "
    "Clasificá en uno de estos tipos:\n"
    "- ATOMIC_PLACE: un lugar físico concreto y nombrado (un hospital puntual, una fábrica, "
    "una torre específica, un edificio identificable).\n"
    "- ATOMIC_EVENT: un incidente concreto acotado en tiempo y lugar (un desastre puntual, "
    "un homicidio sin resolver específico, una desaparición o caso único).\n"
    "- CONCEPT: una práctica, fenómeno o categoría general; no una instancia concreta "
    "(ejemplo abstracto: una práctica de uso de la tierra; una actividad de exploración urbana).\n"
    "- LIST: un artículo índice que agrega muchos ítems (ejemplo abstracto: 'lista de ...').\n"
    "- FICTION: una obra de ficción o entretenimiento (ejemplo abstracto: una película, "
    "un musical, una novela, un videojuego).\n"
    "- OTHER: real pero no encaja en lo anterior o es ambiguo. Usalo poco.\n"
    "Devolvé para cada ítem su id, el type, y un reason de máximo 15 palabras."
)

_ITEM_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=["id", "type", "reason"],
    properties={
        "id": types.Schema(type=types.Type.INTEGER),
        "type": types.Schema(
            type=types.Type.STRING,
            enum=["ATOMIC_PLACE", "ATOMIC_EVENT", "CONCEPT", "LIST", "FICTION", "OTHER"],
        ),
        "reason": types.Schema(type=types.Type.STRING),
    },
)
_RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=["items"],
    properties={"items": types.Schema(type=types.Type.ARRAY, items=_ITEM_SCHEMA)},
)


def _classify_batch(batch: list[dict]) -> dict[int, dict]:
    """batch = [{id,title,subcat_origen,root_origen}]. Devuelve {id: {type,reason}}."""
    lines = [
        f'{it["id"]}. title="{it["title"]}" | subcat="{it["subcat_origen"]}" '
        f'| root="{it["root_origen"]}"'
        for it in batch
    ]
    prompt = ("Clasificá el TIPO de cada entidad (solo título + categoría de origen):\n\n"
              + "\n".join(lines))

    def _do():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=_RESPONSE_SCHEMA,
                temperature=0.0,
            ),
        )
        return json.loads(resp.text)

    data = _with_retry(_do)
    out: dict[int, dict] = {}
    for it in (data.get("items") or []):
        try:
            out[int(it["id"])] = {"type": it.get("type", "OTHER"),
                                  "reason": (it.get("reason") or "").strip()}
        except (KeyError, ValueError, TypeError):
            continue
    return out


def classify(candidates: list[dict]) -> list[dict]:
    """candidates = rows ORO/JOYA. Agrega type/reason/keep a cada uno (copia)."""
    print(f"\n  Clasificando {len(candidates)} candidatos (batch {CLASSIFY_BATCH})...")
    # asignar ids estables
    for i, c in enumerate(candidates):
        c["_cid"] = i
    results: dict[int, dict] = {}
    for start in range(0, len(candidates), CLASSIFY_BATCH):
        chunk = candidates[start:start + CLASSIFY_BATCH]
        batch = [{"id": c["_cid"], "title": c["title"],
                  "subcat_origen": c["subcat_origen"], "root_origen": c["root_origen"]}
                 for c in chunk]
        results.update(_classify_batch(batch))
        print(f"    ...{min(start + CLASSIFY_BATCH, len(candidates))}/{len(candidates)}")
        time.sleep(SLEEP_ACTION)

    out = []
    for c in candidates:
        r = results.get(c["_cid"], {"type": "OTHER", "reason": "no clasificado"})
        ctype = r["type"]
        rec = dict(c)
        rec["type"] = ctype
        rec["reason"] = r["reason"]
        rec["keep"] = ctype in KEEP_TYPES
        rec.pop("_cid", None)
        out.append(rec)
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  GATE
# ══════════════════════════════════════════════════════════════════════════════
def _basket_of(row: dict) -> str:
    if row["label"] == "VACIO" and row["passes_en_floor"]:
        return "ORO"
    if row["label"] == "HUECO" and row["passes_en_floor"]:
        return "JOYA"
    return "DESCARTE"


def eval_gate(by_title: dict[str, dict], all_titles: set[str]) -> dict:
    """Para cada control: ¿llegó a ORO/JOYA? type/keep. PASS/FAIL/NOT_REACHED."""
    def _one(name: str, expect_keep: bool) -> dict:
        row = by_title.get(name)
        reached = row is not None and "keep" in row  # clasificado = llegó a ORO/JOYA
        if not reached:
            # ¿se caminó siquiera?
            walked = name in all_titles
            return {"control": name, "verdict": "NOT_REACHED",
                    "reason_not_reached": ("filtrado por demanda/saturación (descarte)"
                                           if walked else "no se caminó / no apareció en el árbol"),
                    "basket": (_basket_of(by_title[name]) if name in by_title else None),
                    "type": None, "keep": None, "expected_keep": expect_keep}
        verdict = "PASS" if row["keep"] == expect_keep else "FAIL"
        return {"control": name, "verdict": verdict, "basket": _basket_of(row),
                "type": row["type"], "keep": row["keep"], "expected_keep": expect_keep,
                "en_90d": row["en_sum_90d"], "es_90d": row["es_sum_90d"],
                "label": row["label"], "clf_reason": row["reason"]}

    dirty = [_one(n, False) for n in GATE_DIRTY]
    gems = [_one(n, True) for n in GATE_GEMS]

    dirty_reached = [d for d in dirty if d["verdict"] != "NOT_REACHED"]
    gems_reached = [g for g in gems if g["verdict"] != "NOT_REACHED"]
    dirty_pass = sum(1 for d in dirty_reached if d["verdict"] == "PASS")
    gems_pass = sum(1 for g in gems_reached if g["verdict"] == "PASS")

    return {
        "dirty_pass_over_reached": f"{dirty_pass}/{len(dirty_reached)}",
        "gems_pass_over_reached": f"{gems_pass}/{len(gems_reached)}",
        "any_fail": any(d["verdict"] == "FAIL" for d in dirty)
                    or any(g["verdict"] == "FAIL" for g in gems),
        "dirty_detail": dirty,
        "gems_detail": gems,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def _slim(r: dict) -> dict:
    return {"title": r["title"], "root": r["root_origen"], "type": r.get("type"),
            "en_90d": r["en_sum_90d"], "es_90d": r["es_sum_90d"],
            "label": r["label"], "reason": r.get("reason")}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("LAB ATOMICIDAD — chat 48. read-only, $0 (Wikipedia) + ~$0.001 (Flash). sin proxy.")
    print(f"cuts: EN_FLOOR_90D={EN_FLOOR_90D} · ES_HUECO_MAX={ES_HUECO_MAX} · ventana={WINDOW_DAYS}d")
    print(f"caps/raíz: depth={MAX_DEPTH} · cats={CAP_CATEGORIES} · entidades={CAP_ENTITIES}")

    # ── 1. Walk de las 3 raíces + pool con dedup cross-root ──
    print("\n" + "=" * 78)
    print("PASO 1 — WALK 3 raíces + pool dedup cross-root (primera raíz gana)")
    print("=" * 78)
    walk_stats = {}
    pool: dict[str, dict] = {}          # title -> {subcat_origen, depth, root_origen}
    for root in ROOTS:
        w = walk_root(root, MAX_DEPTH, CAP_CATEGORIES, CAP_ENTITIES)
        walk_stats[root] = w["stats"]
        for t, meta in w["entities"].items():
            if t not in pool:           # dedup cross-root: primera raíz se lo queda
                pool[t] = {**meta, "root_origen": root}
    all_titles = set(pool.keys())
    print(f"\n  POOL total (dedup cross-root): {len(pool)} entidades únicas")

    # ── 2. Gap EN/ES UNA sola vez sobre el pool, reinyectando root_origen ──
    print("\n" + "=" * 78)
    print("PASO 2 — GAP EN/ES sobre el pool (1 batch langlinks/pageviews)")
    print("=" * 78)
    rows = measure_gap({t: {"subcat_origen": m["subcat_origen"], "depth": m["depth"]}
                        for t, m in pool.items()})
    for r in rows:
        r["root_origen"] = pool[r["title"]]["root_origen"]

    # ── 3. Canastas: ORO+JOYA → clasificador ──
    oro = [r for r in rows if r["label"] == "VACIO" and r["passes_en_floor"]]
    joya = [r for r in rows if r["label"] == "HUECO" and r["passes_en_floor"]]
    candidates = oro + joya
    print(f"\n  baskets: ORO={len(oro)} · JOYA={len(joya)} · a_clasificar={len(candidates)} "
          f"(de {len(rows)} rows)")

    # ── 4. Clasificar ──
    print("\n" + "=" * 78)
    print("PASO 3 — CLASIFICADOR (Flash, temp 0.0, schema)")
    print("=" * 78)
    classified = classify(candidates) if candidates else []
    by_title = {c["title"]: c for c in classified}

    # ── 5. Gate ──
    gate = eval_gate(by_title, all_titles)

    # ── 6. per_root (keep/drop por árbol) ──
    per_root = defaultdict(lambda: {"keep": 0, "drop": 0, "total_classified": 0})
    for c in classified:
        per_root[c["root_origen"]]["total_classified"] += 1
        per_root[c["root_origen"]]["keep" if c["keep"] else "drop"] += 1

    # ── 7. drop_by_type ──
    drop_by_type = defaultdict(list)
    for c in classified:
        if not c["keep"]:
            drop_by_type[c["type"]].append(_slim(c))

    keep_rows = sorted([c for c in classified if c["keep"]],
                       key=lambda r: r["en_sum_90d"], reverse=True)

    # ── stdout: SOLO el resumen ──
    print("\n" + "=" * 78)
    print("RESUMEN (lo único que se pega al chat)")
    print("=" * 78)
    print("\n[walk_stats por raíz]")
    for root, st in walk_stats.items():
        cap = "entidades" if st["hit_cap_entities"] else ("cats" if st["hit_cap_categories"] else "ninguno")
        print(f"  {root[:50]:<50} cats={st['cats_visited']:>3} únicas={st['unique_entities']:>3} cap={cap}")
    print(f"  POOL dedup cross-root: {len(pool)}  ·  rows con gap: {len(rows)}")

    print(f"\n[baskets]  ORO={len(oro)} · JOYA={len(joya)} · clasificadas={len(classified)} "
          f"· keep={len(keep_rows)} · drop={len(classified)-len(keep_rows)}")

    print("\n[per_root keep/drop]")
    for root, d in per_root.items():
        print(f"  {root[:50]:<50} keep={d['keep']:>3} drop={d['drop']:>3} (clasif={d['total_classified']})")

    print(f"\n[gate]  sucios PASS/llegaron={gate['dirty_pass_over_reached']}  ·  "
          f"joyas PASS/llegaron={gate['gems_pass_over_reached']}  ·  any_FAIL={gate['any_fail']}")
    print("  -- sucios (esperado keep=False) --")
    for d in gate["dirty_detail"]:
        extra = f"type={d['type']} keep={d['keep']}" if d["verdict"] != "NOT_REACHED" else d.get("reason_not_reached", "")
        print(f"    [{d['verdict']:<11}] {d['control'][:45]:<45} {extra}")
    print("  -- joyas (esperado keep=True) --")
    for g in gate["gems_detail"]:
        extra = f"type={g['type']} keep={g['keep']}" if g["verdict"] != "NOT_REACHED" else g.get("reason_not_reached", "")
        print(f"    [{g['verdict']:<11}] {g['control'][:45]:<45} {extra}")

    print(f"\n[keep_list_top40] (ordenado por en_90d)")
    print(f"  {'EN_90d':>8} {'ES_90d':>7} {'TYPE':<13} {'LABEL':<8} TÍTULO ← root")
    for r in keep_rows[:40]:
        rt = r["root_origen"].replace("Category:", "")[:22]
        print(f"  {r['en_sum_90d']:>8,} {r['es_sum_90d']:>7,} {r['type']:<13} {r['label']:<8} "
              f"{r['title'][:38]} ← {rt}")

    print(f"\n[drop_by_type] (conteos)")
    for tp, items in sorted(drop_by_type.items(), key=lambda kv: -len(kv[1])):
        print(f"  {tp:<10} {len(items)}")

    # ── Persistir ──
    full = {
        "cuts": {"EN_FLOOR_90D": EN_FLOOR_90D, "ES_HUECO_MAX": ES_HUECO_MAX,
                 "window_days": WINDOW_DAYS, "max_depth": MAX_DEPTH,
                 "cap_categories": CAP_CATEGORIES, "cap_entities": CAP_ENTITIES, "roots": ROOTS},
        "walk_stats": walk_stats,
        "pool_size": len(pool),
        "rows": rows,
        "classified": classified,
    }
    resumen = {
        "cuts": full["cuts"],
        "walk_stats": walk_stats,
        "pool_size": len(pool),
        "baskets": {"oro": len(oro), "joya": len(joya),
                    "clasificadas": len(classified),
                    "keep": len(keep_rows), "drop": len(classified) - len(keep_rows)},
        "per_root": {k: dict(v) for k, v in per_root.items()},
        "gate": gate,
        "keep_list_top40": [_slim(r) for r in keep_rows[:40]],
        "drop_by_type": {k: v for k, v in drop_by_type.items()},
    }
    OUT_FULL.write_text(json.dumps(full, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_RESUMEN.write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado full:    {OUT_FULL}")
    print(f"Guardado resumen: {OUT_RESUMEN}")


if __name__ == "__main__":
    main()
