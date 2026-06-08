"""
_lab_spy_stage3_precision_chat49.py — LAB (chat 49 addendum 2). Test de PRECISION del piso LAXO.
read-only sobre prod. Gasta poco scrape (vara LAXO = NO usa outlier → solo el search por subtema,
sin get_channel). NO toca prod. Output a _lab_out/.

CONTRATO DEL MEDIDOR DE SUBTEMAS (asentado, addendum 2):
  - vara = LAXO: standalone EN con vistas medianas propias (top_views >= LAXO_FLOOR_VIEWS).
  - la fórmula outlier (compute_outlier_filter) NO se usa para subtemas (mide anomalía-de-canal,
    señal equivocada para un subtema-entidad; mató Marine Sulphur Queen con 585k reales).
  - compuerta ES-primero: score_spanish_saturation → si SATURADO, CORTA (no paga EN). Solo los
    con hueco ES (VACIO/HUECO) pagan la medición EN-LAXO.

TEST (Decisión 6): el piso 50k, ¿corta abstractos/oscuros Y mantiene los buenos? Muestra:
  - ABSTRACTOS (extractor v2 los tira por concreción; acá medimos demanda igual para ver si
    el PISO los cortaría o no): the lithium problem, dark matter, the flyby anomaly, space roar.
  - OSCUROS (entidades particulares de baja/nula demanda real, de #18 'fall asleep to'):
    Echol Loop Anomaly, Azores Plateau Monolith.
  - BUENOS (control should-keep): Mary Celeste, USS Cyclops, Wilhelm Gustloff, Doña Paz.

Correr:  python -X utf8 _lab_spy_stage3_precision_chat49.py
Output:  _lab_out/spy_stage3_precision.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from script_engine.youtube_scanner import (
    search_viral_english, extract_anchors, score_spanish_saturation,
)

LAB_OUT = Path("_lab_out")
OUT = LAB_OUT / "spy_stage3_precision.json"

LAXO_FLOOR_VIEWS = 50_000
EN_SEARCH_LIMIT = 15

# muestra etiquetada por lo que el piso DEBERÍA hacer
SAMPLE = [
    # (nombre, clase_esperada, parent)
    ("the lithium problem",    "ABSTRACTO", "#9 10 Obscure Unexplained Mysteries of the Universe"),
    ("dark matter",            "ABSTRACTO", "#6 Cosmic Anomalies That Baffle Scientists"),
    ("the flyby anomaly",      "ABSTRACTO", "#6 Cosmic Anomalies That Baffle Scientists"),
    ("space roar",             "ABSTRACTO", "#6 Cosmic Anomalies That Baffle Scientists"),
    ("Echol Loop Anomaly",     "OSCURO",    "#18 100+ Unexplained Ocean Mysteries to Fall Asleep To"),
    ("Azores Plateau Monolith","OSCURO",    "#18 100+ Unexplained Ocean Mysteries to Fall Asleep To"),
    ("Mary Celeste",           "BUENO",     "#15 4+ HOURS of Unexplained Deep Sea Mysteries"),
    ("USS Cyclops",            "BUENO",     "#15 4+ HOURS of Unexplained Deep Sea Mysteries"),
    ("Wilhelm Gustloff",       "BUENO",     "#17 18 Terrifying Ocean Mysteries That Swallowed Entire Ships"),
    ("Doña Paz",               "BUENO",     "#17 18 Terrifying Ocean Mysteries That Swallowed Entire Ships"),
]

SCRAPE = {"es_sat": 0, "en_search": 0}


def es_gate(name: str) -> dict:
    try:
        SCRAPE["es_sat"] += 1
        sat = score_spanish_saturation(name, anchors=extract_anchors(name))
        return {"label": sat.get("label"), "saturation": sat.get("saturation")}
    except Exception as e:
        return {"label": "ERR", "saturation": None, "error": str(e)[:80]}


def en_laxo(name: str) -> dict:
    """LAXO: top_views del mejor standalone EN. SIN outlier filter (Decisión 5)."""
    try:
        SCRAPE["en_search"] += 1
        cands = search_viral_english(name, limit=EN_SEARCH_LIMIT)
    except Exception as e:
        return {"error": str(e)[:100], "top_views": 0, "pasa_laxo": False}
    top = max(cands, key=lambda c: int(c.get("views") or 0), default=None)
    tv = int(top.get("views") or 0) if top else 0
    return {"n_cands": len(cands), "top_title": (top or {}).get("title"),
            "top_views": tv, "pasa_laxo": tv >= LAXO_FLOOR_VIEWS}


def main():
    LAB_OUT.mkdir(parents=True, exist_ok=True)
    print("LAB STAGE 3 PRECISION — piso LAXO. read-only. ES-primero, EN-LAXO sin outlier.")
    print(f"LAXO_FLOOR_VIEWS={LAXO_FLOOR_VIEWS:,}\n")

    rows = []
    for i, (name, clase, parent) in enumerate(SAMPLE, 1):
        print(f"[{i}/{len(SAMPLE)}] {name}  ({clase})")
        es = es_gate(name)
        gated = es["label"] == "SATURADO"
        if gated:
            print(f"    ES={es['label']} sat={es['saturation']} → CORTA (no paga EN)")
            en = {"gated_by_es": True}
            verdict = "CORTADO_ES"
        else:
            en = en_laxo(name)
            err = en.get("error")
            if err:
                print(f"    ES={es['label']} · EN ERROR: {err}")
                verdict = "EN_ERROR"
            else:
                print(f"    ES={es['label']} · EN top_views={en['top_views']:,} "
                      f"→ LAXO {'PASA' if en['pasa_laxo'] else 'CORTA'}  ('{(en.get('top_title') or '')[:40]}')")
                verdict = "PASA_LAXO" if en["pasa_laxo"] else "CORTA_LAXO"
        rows.append({"nombre": name, "clase_esperada": clase, "parent_origen": parent,
                     "es": es, "en": en, "verdict": verdict})
        time.sleep(0.4)

    # ── evaluación de precision por ambos lados ──
    print("\n" + "=" * 86)
    print("PRECISION DEL PISO LAXO (¿corta malos Y mantiene buenos?)")
    print("=" * 86)
    print(f"  {'NOMBRE':<26} {'CLASE':<10} {'top_views':>10} {'verdict':<12} origen")
    for r in rows:
        tv = r["en"].get("top_views", 0) if not r["en"].get("gated_by_es") else "-"
        tvs = f"{tv:,}" if isinstance(tv, int) else tv
        print(f"  {r['nombre']:<26} {r['clase_esperada']:<10} {tvs:>10} {r['verdict']:<12} {r['parent_origen'][:34]}")

    # ¿qué pasó por clase?
    def _passed(r):  # "pasó el medidor" = no cortado por ES ni por LAXO
        return r["verdict"] == "PASA_LAXO"
    buenos = [r for r in rows if r["clase_esperada"] == "BUENO"]
    malos = [r for r in rows if r["clase_esperada"] in ("ABSTRACTO", "OSCURO")]
    buenos_keep = sum(1 for r in buenos if _passed(r))
    malos_pass = [r for r in malos if _passed(r)]
    print(f"\n  BUENOS mantenidos: {buenos_keep}/{len(buenos)}")
    print(f"  MALOS que el piso DEJÓ pasar (precision fail si >0): {len(malos_pass)}/{len(malos)}")
    for r in malos_pass:
        print(f"     ⚠ {r['nombre']} ({r['clase_esperada']}) top_views={r['en'].get('top_views'):,} "
              f"→ el piso {LAXO_FLOOR_VIEWS:,} NO lo corta")
    print(f"\n  COSTO scrape: ES_sat={SCRAPE['es_sat']} · EN_search={SCRAPE['en_search']} "
          f"(LAXO no usa outlier → 0 get_channel)")

    OUT.write_text(json.dumps({"config": {"LAXO_FLOOR_VIEWS": LAXO_FLOOR_VIEWS,
                                          "EN_SEARCH_LIMIT": EN_SEARCH_LIMIT},
                               "scrape": SCRAPE, "rows": rows}, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print(f"\nGuardado: {OUT}")


if __name__ == "__main__":
    main()
