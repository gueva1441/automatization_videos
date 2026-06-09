"""
test_chat51_observabilidad.py — valida la observabilidad del label ES/EN (CHAT 51), SIN red.
Cubre §3 del handoff. 100% observabilidad: NO cambia ningún label ni descarte.

POR QUÉ: dos seeds entraron off-angle (Lemieux→hockey, Sri Lanka→street food) porque el fallback
over-narrow re-buscó el nombre pelado. El fallback es necesario; el problema es que NO se veía.
Este fix captura + persiste + imprime + marca en el menú los diagnósticos (query_fallback,
n_cands crudos, query ES real) para que cada hueco sea auditable.

Cubre:
  - _measure_es devuelve n_cands_es (crudo) además de ontopic_count (post-juez); cands=[] → 0.
  - seed: es_gap trae es_query/n_cands_es/query_fallback; en_viral trae n_cands/n_relevantes.
  - fallback: subtema cuya query ES da 0 y re-busca pelado → es_gap.query_fallback==True y el
    menú muestra '⚠ fallback'.
  - limpio (sin fallback) → sin marcador.
  - VACÍO auditable: n_cands_es=8 ontopic_count=0 se distingue de n_cands_es=0.

Correr:  python -X utf8 test_chat51_observabilidad.py
"""
from __future__ import annotations

import builtins
import io
import sys
from contextlib import redirect_stdout

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import script_engine.subtopic_measurer as sm
import script_engine.transcript_fetch as tf
import script_engine.subtopic_classifier as sc
import script_engine.subtopic_extractor as se
import niche_discoverer as nd
from niche_discoverer import _try_subtema_fanout
import fase1


REP = {"video_id": "VIDx", "original_title": "Container Title"}


def run():
    failures = []

    def check(cond, msg):
        print(f"  [{'✓' if cond else '✗'}] {msg}")
        if not cond:
            failures.append(msg)

    # ── 1.1: _measure_es devuelve n_cands_es (crudo) ──
    print("1.1 — _measure_es expone n_cands_es (crudo, pre-juez)\n")
    sm.translate_to_es = lambda q: {"es_query": f"ES::{q}", "es_aliases": []}
    orig_list, orig_filter = sm.list_spanish_candidates, sm.filter_relevant

    # 8 crudos, el juez deja 0 → VACÍO pero n_cands_es=8 (buscó bien, juez descartó)
    sm.list_spanish_candidates = lambda q, limit=50: [
        {"title": f"ruido {i}", "views": 100, "months": 2} for i in range(8)]
    sm.filter_relevant = lambda entity, cands, aliases=None: []
    try:
        es_vacio_real = sm._measure_es("Algo", "Algo")
    finally:
        sm.list_spanish_candidates, sm.filter_relevant = orig_list, orig_filter
    check(es_vacio_real.get("n_cands_es") == 8 and es_vacio_real.get("ontopic_count") == 0,
          f"n_cands_es=8 (crudo) vs ontopic_count=0 (juez descartó): "
          f"{es_vacio_real.get('n_cands_es')}/{es_vacio_real.get('ontopic_count')}")
    check(es_vacio_real.get("label") != "ERROR", "no rompe (VACÍO auditable, búsqueda SÍ trajo data)")

    # cands=[] → n_cands_es=0 (búsqueda vino vacía)
    sm.list_spanish_candidates = lambda q, limit=50: []
    sm.filter_relevant = lambda entity, cands, aliases=None: cands
    try:
        es_vacio_search = sm._measure_es("Nada", "Nada")
    finally:
        sm.list_spanish_candidates, sm.filter_relevant = orig_list, orig_filter
    check(es_vacio_search.get("n_cands_es") == 0,
          f"cands=[] → n_cands_es=0 (search vacío): {es_vacio_search.get('n_cands_es')}")

    # ── helpers para construir seeds vía el fan-out (mocks) ──
    def _install(subjects, en_fn, es_fn):
        tf.fetch_transcript = lambda vid, *a, **k: "transcript real"
        sc.classify = lambda title, tr: {"tipo": "CONTENEDOR", "razon": "mock"}
        se.extract_segment_subjects = lambda title, tr: [
            {"nombre_en": s, "search_query_en": f"{s} angle", "angle_en": f"{s} angle"} for s in subjects]
        se.verify_names = lambda names, *a, **k: {}
        sm._measure_en_laxo = en_fn
        sm._measure_es = es_fn
        nd._channel_baseline = lambda cid, n, exclude: None

    def _en(fb=False, n_cands=10, n_rel=3):
        def _fn(sq, entity=None):
            return {"pasa_laxo": True, "top_rel_views": 500_000, "top_rel_title": f"{entity} viral",
                    "top_rel_video_id": "vv", "top_rel_channel_id": None, "top_rel_age_months": 5,
                    "query_used": sq, "query_fallback": fb, "n_cands": n_cands, "n_relevantes": n_rel}
        return _fn

    def _es(fb=False, n_cands_es=4, ontopic=1, label="HUECO"):
        def _fn(sq, entity=None):
            return {"label": label, "saturation": 0.0, "heaviest": None, "ontopic_count": ontopic,
                    "anchors_used": [sq], "source": "mock", "es_query": f"ES::{sq}",
                    "n_cands_es": n_cands_es, "query_fallback": fb}
        return _fn

    # ── 1.2: el seed persiste los diagnósticos ──
    print("\n1.2 — el seed persiste diagnósticos (en_viral + es_gap)\n")
    _install(["Sujeto"], _en(n_cands=12, n_rel=4), _es(n_cands_es=6, ontopic=2))
    out = _try_subtema_fanout(REP, "abandonados", {}, 1)
    ev = out[0]["evidence"]
    en_v, es_g = ev["en_viral"], ev["es_gap"]
    check(en_v.get("n_cands") == 12 and en_v.get("n_relevantes") == 4,
          f"en_viral persiste n_cands/n_relevantes: {en_v.get('n_cands')}/{en_v.get('n_relevantes')}")
    check(es_g.get("es_query") == "ES::Sujeto angle", f"es_gap.es_query persistido: {es_g.get('es_query')!r}")
    check(es_g.get("n_cands_es") == 6, f"es_gap.n_cands_es persistido: {es_g.get('n_cands_es')}")
    check("query_fallback" in es_g, "es_gap.query_fallback persistido")

    # ── 1.3: línea de auditoría impresa en la corrida ──
    print("\n1.3 — línea [audit] por subtema\n")
    _install(["Lemieux"], _en(fb=True), _es(fb=False))
    buf = io.StringIO()
    with redirect_stdout(buf):
        _try_subtema_fanout(REP, "abandonados", {}, 1)
    audit = buf.getvalue()
    check("[audit] Lemieux" in audit, "imprime línea [audit] con el nombre")
    check("fb=S" in audit, "la línea audit refleja el fallback (fb=S)")

    # ── 1.4: el menú marca ⚠ fallback ──
    print("\n1.4 — el menú marca ⚠ fallback (EN o ES)\n")

    def _seed(title, en_fb, es_fb):
        return {"seed_id": title, "seed_title": title,
                "judge": {"verdict": "dudoso", "cohort": "2/3", "risk": "ninguno", "reason": "x"},
                "evidence": {
                    "en_viral": {"original_title": f"{title} EN", "views": 500_000,
                                 "outlier_ratio": 5.0, "en_age_months": 4, "query_fallback": en_fb},
                    "es_gap": {"label": "VACIO", "ontopic_count": 0, "query_fallback": es_fb}}}

    seeds = [_seed("Lemieux landslide", True, False),   # EN fallback
             _seed("Otro pelado", False, True),         # ES fallback
             _seed("Limpio", False, False)]             # sin fallback
    orig_input = builtins.input
    try:
        builtins.input = lambda *a, **k: "Q"
        buf2 = io.StringIO()
        with redirect_stdout(buf2):
            fase1._select_seed_interactive(seeds)
        menu = buf2.getvalue()
    finally:
        builtins.input = orig_input

    check(menu.count("⚠ fallback") == 2, f"2 seeds con fallback marcados (EN y ES): {menu.count('⚠ fallback')}")
    check("demanda medida con nombre pelado" in menu, "muestra la línea explicativa del fallback")
    # el seed limpio NO debe tener marcador en su fila
    limpio_line = next((ln for ln in menu.splitlines() if "Limpio" in ln), "")
    check("⚠" not in limpio_line, f"el seed limpio NO lleva marcador: {limpio_line.strip()!r}")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
