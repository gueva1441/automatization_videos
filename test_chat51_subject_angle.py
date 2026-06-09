"""
test_chat51_subject_angle.py — valida el fix de raíz: subject con ÁNGULO (no nombre pelado) en el
fan-out, SIN red ni Gemini. Cubre §2 del handoff.

POR QUÉ: el contenedor Belt & Road parió seeds basura ('Mongolia', 'Cambodia' pelados). El nombre
pelado envenenaba 3 etapas: search trae genérico (turismo), relevancia substring deja pasar todo,
research groundea "Cambodia general". Fix: el extractor emite 3 campos —nombre_en (relevancia/dedup),
search_query_en (con qué se busca), angle_en (seed_title → research)— cada uno a su destino.

Cubre:
  - extract_segment_subjects devuelve dicts con los 3 campos; search_query_en NO es el país pelado.
  - _measure_en_laxo(search_query, entity): BUSCA con search_query, RELEVANCIA con entity.
  - over-narrow fallback: <EN_MIN_CANDS con search_query → re-busca con entity → query_fallback=True.
  - _measure_es(search_query, entity): traduce/busca con search_query, juzga relevancia contra entity;
    0 cands → re-busca con entity (query_fallback=True).
  - _try_subtema_fanout: seed_title con ángulo (no pelado), nombre_en = entidad, en_viral.query =
    search_query_en.

Correr:  python -X utf8 test_chat51_subject_angle.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import script_engine.subtopic_extractor as se
import script_engine.subtopic_measurer as sm
import script_engine.transcript_fetch as tf
import script_engine.subtopic_classifier as sc
import niche_discoverer as nd
from niche_discoverer import _try_subtema_fanout


REP = {"video_id": "VIDbr", "original_title": "Belt and Road's Abandoned Megaprojects"}


def run():
    failures = []

    def check(cond, msg):
        print(f"  [{'✓' if cond else '✗'}] {msg}")
        if not cond:
            failures.append(msg)

    # ── 1.1: extract_segment_subjects devuelve dicts con 3 campos (modelo mockeado) ──
    print("1.1 — extract_segment_subjects → dicts {nombre_en, search_query_en, angle_en}\n")

    class _Resp:
        def __init__(self, text): self.text = text

    import json as _json
    fake = {"subtemas": [
        {"nombre_en": "Cambodia", "search_query_en": "Cambodia debt-trap ruins",
         "angle_en": "abandoned Belt and Road projects"},
        {"nombre_en": "Mongolia", "search_query_en": "Mongolia abandoned mining town",
         "angle_en": "ghost mining boomtown"},
        # modelo omite search/angle → deben caer a nombre_en (defensivo)
        {"nombre_en": "Zambia"},
    ]}
    orig_client = se._client
    class _Models:
        def generate_content(self, *a, **k):
            return _Resp(_json.dumps(fake))
    class _FakeClient:
        models = _Models()
    se._client = _FakeClient()
    try:
        subs = se.extract_segment_subjects("title", "transcript largo")
    finally:
        se._client = orig_client

    check(len(subs) == 3 and all(isinstance(x, dict) for x in subs), f"devuelve 3 dicts: {len(subs)}")
    check(all({"nombre_en", "search_query_en", "angle_en"} <= set(x) for x in subs),
          "cada dict trae los 3 campos")
    camb = subs[0]
    check(camb["search_query_en"] != camb["nombre_en"] and "Cambodia" in camb["search_query_en"],
          f"search_query_en angulado, NO el país pelado: {camb['search_query_en']!r}")
    zam = subs[2]
    check(zam["search_query_en"] == "Zambia" and zam["angle_en"] == "Zambia",
          "fallback: si el modelo omite search/angle → caen a nombre_en")

    # ── 1.3: _measure_en_laxo BUSCA con search_query, RELEVANCIA con entity ──
    print("\n1.3 — _measure_en_laxo: busca con search_query, relevancia vs entity\n")
    SEARCHED = {"q": None}
    # 6 candidatos (≥ EN_MIN_CANDS=5) → sin fallback. Solo el que menciona la entidad es relevante.
    def _search_ok(q, limit=15):
        SEARCHED["q"] = q
        return [
            {"title": "Cambodia debt-trap abandoned city", "views": 700_000,
             "video_id": "v1", "channel_id": "UC1", "en_age_months": 5},
            {"title": "random vlog one", "views": 50, "video_id": "v2"},
            {"title": "random vlog two", "views": 40, "video_id": "v3"},
            {"title": "random vlog three", "views": 30, "video_id": "v4"},
            {"title": "random vlog four", "views": 20, "video_id": "v5"},
            {"title": "random vlog five", "views": 10, "video_id": "v6"},
        ]
    orig_search = sm.search_viral_english
    sm.search_viral_english = _search_ok
    try:
        en = sm._measure_en_laxo("Cambodia debt-trap ruins", "Cambodia")
    finally:
        sm.search_viral_english = orig_search
    check(SEARCHED["q"] == "Cambodia debt-trap ruins",
          f"el string buscado es el search_query (no la entidad): {SEARCHED['q']!r}")
    check(en["query_fallback"] is False, "≥EN_MIN_CANDS → sin fallback")
    check(en["top_rel_views"] == 700_000 and en["n_relevantes"] == 1,
          "relevancia vs entity: solo el video que menciona Cambodia cuenta")

    # ── over-narrow fallback: <EN_MIN_CANDS con search_query → re-busca con entity ──
    print("\nover-narrow — <EN_MIN_CANDS con la query angulada → re-busca con la entidad pelada\n")
    seq = {"calls": []}
    def _search_narrow(q, limit=15):
        seq["calls"].append(q)
        if q == "Cambodia debt-trap collapsed concrete pylons":   # angulada: 2 resultados (< 5)
            return [{"title": "Cambodia ruins", "views": 90_000, "video_id": "a1",
                     "channel_id": "UC9", "en_age_months": 3},
                    {"title": "Cambodia b", "views": 100, "video_id": "a2"}]
        # entidad pelada: muchos resultados
        return [{"title": f"Cambodia thing {i}", "views": 200_000 - i, "video_id": f"b{i}",
                 "channel_id": "UCb", "en_age_months": 4} for i in range(8)]
    sm.search_viral_english = _search_narrow
    try:
        en2 = sm._measure_en_laxo("Cambodia debt-trap collapsed concrete pylons", "Cambodia")
    finally:
        sm.search_viral_english = orig_search
    check(seq["calls"] == ["Cambodia debt-trap collapsed concrete pylons", "Cambodia"],
          f"primero la angulada, luego fallback a la entidad: {seq['calls']}")
    check(en2["query_fallback"] is True, "query_fallback=True tras el rescate")
    check(en2["query_used"] == "Cambodia" and en2["n_cands"] == 8, "usó los candidatos de la entidad")

    # ── 1.3 ES: 0 cands con la query angulada → re-busca con entity, juzga vs entity ──
    print("\nES over-narrow — 0 cands con query angulada → re-busca con la entidad\n")
    es_seq = {"list": []}
    sm.translate_to_es = lambda q: {"es_query": f"ES::{q}", "es_aliases": []}
    def _list_es(q, limit=50):
        es_seq["list"].append(q)
        if q == "ES::Mongolia abandoned mining town":
            return []                                  # angulada ES → 0
        return [{"title": "Mongolia documental", "views": 10_000, "months": 6}]
    orig_list = sm.list_spanish_candidates
    orig_filter = sm.filter_relevant
    JUDGED = {"entity": None}
    def _filter(entity, cands, aliases=None):
        JUDGED["entity"] = entity
        return cands
    sm.list_spanish_candidates = _list_es
    sm.filter_relevant = _filter
    try:
        es = sm._measure_es("Mongolia abandoned mining town", "Mongolia")
    finally:
        sm.list_spanish_candidates = orig_list
        sm.filter_relevant = orig_filter
    check(es_seq["list"] == ["ES::Mongolia abandoned mining town", "ES::Mongolia"],
          f"ES: angulada (0) → fallback a la entidad: {es_seq['list']}")
    check(es.get("query_fallback") is True, "ES query_fallback=True")
    check(JUDGED["entity"] == "Mongolia", "el juez ES juzga relevancia contra la ENTIDAD")
    check(es["label"] != "ERROR", f"ES no rompe: label={es['label']}")

    # ── 1.2: _try_subtema_fanout → seed_title con ángulo, nombre_en, en_viral.query angulada ──
    print("\n1.2 — fanout: seed_title con ángulo, nombre_en = entidad, en_viral.query = search_query\n")
    tf.fetch_transcript = lambda vid, *a, **k: "transcript real"
    sc.classify = lambda title, tr: {"tipo": "CONTENEDOR", "razon": "mock"}
    se.extract_segment_subjects = lambda title, tr: [
        {"nombre_en": "Cambodia", "search_query_en": "Cambodia debt-trap ruins",
         "angle_en": "abandoned Belt and Road megaprojects"}]
    se.verify_names = lambda names, *a, **k: {}
    sm._measure_en_laxo = lambda sq, entity=None: {
        "pasa_laxo": True, "top_rel_views": 700_000, "top_rel_title": "Cambodia ghost city",
        "top_rel_video_id": "vX", "top_rel_channel_id": None, "top_rel_age_months": 5,
        "query_used": sq, "query_fallback": False}
    sm._measure_es = lambda sq, entity=None: {"label": "VACIO", "saturation": 0.0,
        "heaviest": None, "ontopic_count": 0, "anchors_used": [sq], "source": "mock"}
    nd._channel_baseline = lambda cid, n, exclude: None
    out = _try_subtema_fanout(REP, "abandonados", {}, 1)

    check(isinstance(out, list) and len(out) == 1, f"emite 1 seed: {len(out) if out else 0}")
    seed = out[0]
    check(seed["seed_title"] == "Cambodia: abandoned Belt and Road megaprojects",
          f"seed_title CON ángulo (no 'Cambodia' pelado): {seed['seed_title']!r}")
    check(seed.get("nombre_en") == "Cambodia", f"nombre_en = entidad canónica: {seed.get('nombre_en')!r}")
    check(seed["evidence"]["en_viral"]["query"] == "Cambodia debt-trap ruins",
          f"en_viral.query = search_query_en (trazabilidad): {seed['evidence']['en_viral']['query']!r}")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
