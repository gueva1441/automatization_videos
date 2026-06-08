"""
_lab_es_saturation_relaxed_chat49.py — LAB T2 (NO cablear hasta validar): copia RELAJADA de
score_spanish_saturation + suite de regresión. NO toca la función de prod.

Por qué lab: score_spanish_saturation es el árbitro de saturación de TODO el sistema (spy + Mode
B). Relajar idioma + anchor puede arreglar Chernobyl (hoy da 0 competidores ES siendo
obviamente saturado) pero el riesgo simétrico es catastrófico: contar competidores-fantasma →
TODO da SATURADO falso → no sale ningún seed, en silencio. Por eso: regresión contra controles
que HOY clasifican bien ANTES de cablear.

Relajaciones (handoff chat 49):
  - IDIOMA: en una query YT ya geolocalizada ES, asumir válido salvo que el título sea de un
    mercado claramente extranjero (ruso/árabe/CJK/…). Relaja `detect_language(title)=="es"`,
    que hoy descarta español real (por eso Chernobyl da 0).
  - ANCHOR: cuenta como competidor si (a) alguna palabra del anchor >4 letras está en el título
    (substring, case-insensitive) O (b) YT lo posicionó orgánico en el top-5 de esa query.
    Relaja el `title_contains_anchor` word-boundary estricto.

Criterio de éxito (lo decide la TABLA, no la intuición): la versión relajada ARREGLA Chernobyl
(pasa a SATURADO) SIN cambiar el label de los controles. Si voltea un control → demasiado
agresivo, iterar. NADA se cablea sin esa tabla limpia.

La LÓGICA de los dos predicados relajados está cubierta offline por test_t2_relaxed.py.
Esta corrida necesita scrapetube vivo (proxies) → la corre Omar.

Correr (máquina de Omar):  python -X utf8 _lab_es_saturation_relaxed_chat49.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langdetect import detect

from script_engine.youtube_scanner import (
    score_spanish_saturation,          # PROD (no se toca) — referencia "antes"
    extract_anchors, scrapetube, _proxies_dict,
    _parse_views_scrapetube, _es_pub_text, _parse_date_scrapetube_months_ago,
    _es_age_decay, _es_saturation_label, ES_SCRAPE_PASSES, YT_LIMIT_ARCHAEOLOGY,
)

OUT_FILE = Path("_lab_out/es_saturation_relaxed_chat49.json")

# Mercados claramente NO-español: si el título cae acá, NO cuenta. El resto (es / en mal
# detectado / ambiguo) SÍ cuenta — en una query ES-geo casi todo es español real.
_FOREIGN_LANGS = {"ru", "ar", "zh-cn", "zh-tw", "ja", "ko", "hi", "th",
                  "he", "fa", "el", "uk", "bg", "sr", "mk", "vi"}

TOP_ORGANIC = 5   # los primeros N resultados de la query ES cuentan aunque no matcheen anchor


def _lang_ok_relaxed(title: str) -> bool:
    try:
        return detect(title) not in _FOREIGN_LANGS
    except Exception:
        return True   # indetectable en query ES-geo → asumir válido


def _anchor_ok_relaxed(title: str, anchors, rank: int) -> bool:
    if rank < TOP_ORGANIC:          # YT lo posicionó orgánico arriba → relevante de facto
        return True
    if not anchors:
        return True
    tl = title.lower()
    return any(len(a) > 4 and a.lower() in tl for a in anchors)


def score_spanish_saturation_relaxed(keyword: str, anchors=None,
                                     limit: int = YT_LIMIT_ARCHAEOLOGY) -> dict:
    """Copia de prod con los DOS predicados relajados. MISMA matemática de saturación
    (decay + competidor más pesado) — solo cambia QUÉ videos cuentan como competidor."""
    report = {"source": "scrapetube", "keyword": keyword, "saturation": 0.0, "label": "VACIO",
              "heaviest": None, "ontopic_count": 0, "anchors_used": anchors or [], "error": None}
    seen: dict = {}
    for _ in range(ES_SCRAPE_PASSES):
        try:
            for v in scrapetube.get_search(keyword, limit=limit, proxies=_proxies_dict()):
                vid_id = v.get("videoId")
                if vid_id and vid_id not in seen:
                    seen[vid_id] = v
        except Exception as e:
            if not seen:
                report["error"] = str(e); report["saturation"] = -1.0; report["label"] = "ERROR"
                return report
    vids = list(seen.values())

    best, count = None, 0
    for rank, v in enumerate(vids):
        try:
            title = v["title"]["runs"][0]["text"]
        except (KeyError, IndexError):
            continue
        if not _lang_ok_relaxed(title):
            continue
        if not _anchor_ok_relaxed(title, anchors, rank):
            continue
        months = _parse_date_scrapetube_months_ago(_es_pub_text(v))
        views = _parse_views_scrapetube(v)
        decay = _es_age_decay(months)
        eff = views * decay
        count += 1
        if best is None or eff > best["eff"]:
            best = {"title": title[:80], "views": views, "months": months, "decay": decay, "eff": eff}

    report["ontopic_count"] = count
    if best:
        report["saturation"] = best["eff"]
        report["heaviest"] = best
        report["label"] = _es_saturation_label(best["eff"])
    return report


# Controles sacados de los 26 seeds de hoy (clasifican BIEN) + Chernobyl (el roto, da 0).
# (keyword, label_esperado_hoy)
CONTROLS = [
    ("Pennhurst Asylum horrores", "VACIO"),
    ("Villa Epecuén",             "HUECO"),
    ("Fukushima Daiichi",         "VACIO"),
    ("Craco, Italy",              "VACIO"),
    ("North Brother Island",      "HUECO"),
]
BROKEN = ("Chernobyl", "SATURADO")   # hoy da VACIO (bug); relajado DEBE dar SATURADO


def main() -> None:
    rows = []
    print("LAB T2 — score_spanish_saturation: PROD vs RELAJADO (regresión)\n")
    print(f"  {'keyword':<28} {'esperado':<9} {'OLD label':<10} {'NEW label':<10} {'OK?'}")
    print("  " + "─" * 70)
    ok_controls = True
    chernobyl_fixed = False
    for keyword, expected in CONTROLS + [BROKEN]:
        anchors = extract_anchors(keyword)
        old = score_spanish_saturation(keyword, anchors=anchors)
        new = score_spanish_saturation_relaxed(keyword, anchors=anchors)
        is_broken = (keyword == BROKEN[0])
        if is_broken:
            ok = (old["label"] != "SATURADO") and (new["label"] == "SATURADO")
            chernobyl_fixed = new["label"] == "SATURADO"
        else:
            ok = old["label"] == new["label"]   # control NO debe cambiar
            ok_controls = ok_controls and ok
        mark = "✓" if ok else "✗ ←REVISAR"
        print(f"  {keyword:<28} {expected:<9} {old['label']:<10} {new['label']:<10} {mark}")
        rows.append({"keyword": keyword, "expected": expected,
                     "old": {"label": old["label"], "saturation": old["saturation"],
                             "ontopic_count": old["ontopic_count"]},
                     "new": {"label": new["label"], "saturation": new["saturation"],
                             "ontopic_count": new["ontopic_count"]},
                     "is_broken_case": is_broken, "ok": ok})

    print("\n  CRITERIO: Chernobyl OLD≠SATURADO y NEW=SATURADO, y los controles NO cambian.")
    veredicto = "✅ CABLEABLE" if (chernobyl_fixed and ok_controls) else \
                "❌ NO CABLEAR (relajación voltea un control o no arregla Chernobyl)"
    print(f"  Chernobyl arreglado: {chernobyl_fixed} · controles intactos: {ok_controls} → {veredicto}")
    OUT_FILE.parent.mkdir(exist_ok=True)
    OUT_FILE.write_text(json.dumps({"rows": rows, "chernobyl_fixed": chernobyl_fixed,
                                    "controls_intact": ok_controls}, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"\n  Guardado: {OUT_FILE}  (NADA cableado a prod)")


if __name__ == "__main__":
    main()
