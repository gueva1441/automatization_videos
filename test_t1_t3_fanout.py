"""
test_t1_t3_fanout.py — valida T1 (skip por fallo de infra) y T3 (EN-barato → cap → ES-caro)
en `niche_discoverer._try_subtema_fanout`, SIN red ni Gemini (todo mockeado).

T1: transcript None (fallo infra) o classify ERROR → _FANOUT_SKIP (no se crea seed).
    transcript "" (sin subs legítimo) o ATOMICO → None (cae al flujo de hoy).
T3: el ES (caro) se mide SOLO a los ≤K ganadores del cap EN, no a los N sujetos.
    Reporta el delta de mediciones ES (lo que decide el cableado).

Correr:  python -X utf8 test_t1_t3_fanout.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import script_engine.transcript_fetch as tf
import script_engine.subtopic_classifier as sc
import script_engine.subtopic_extractor as se
import script_engine.subtopic_measurer as sm
import niche_discoverer as nd
from niche_discoverer import _try_subtema_fanout, _FANOUT_SKIP, SUBTEMA_FANOUT_CAP_K


# ── Contadores de mediciones (para el delta de ahorro T3) ──
COUNT = {"en": 0, "es": 0}


def _reset():
    COUNT["en"] = 0
    COUNT["es"] = 0


def _install(transcript, tipo, subjects, en_fn, es_fn):
    """Parchea las dependencias que _try_subtema_fanout importa localmente."""
    tf.fetch_transcript = lambda vid, *a, **k: transcript
    sc.classify = lambda title, tr: {"tipo": tipo, "razon": "mock"}
    se.extract_segment_subjects = lambda title, tr: list(subjects)
    se.verify_names = lambda names, *a, **k: {}
    # los dos medidores partidos (T3)
    def _en(name):
        COUNT["en"] += 1
        return en_fn(name)
    def _es(name):
        COUNT["es"] += 1
        return es_fn(name)
    sm._measure_en_laxo = _en
    sm._measure_es = _es


REP = {"video_id": "VID123", "original_title": "Mock Container Title"}


def _en_pass(views):
    return lambda name: {"pasa_laxo": True, "top_rel_views": views(name) if callable(views) else views,
                         "top_rel_title": f"{name} EN", "top_rel_video_id": f"en_{name}"}


def _es_vacio(name):
    return {"label": "VACIO", "saturation": 0.0, "heaviest": None,
            "ontopic_count": 0, "anchors_used": [name.lower()], "source": "mock"}


def run():
    failures = []

    def check(cond, msg):
        mark = "✓" if cond else "✗"
        print(f"  [{mark}] {msg}")
        if not cond:
            failures.append(msg)

    print("T1 — distinción fallo-de-infra vs sin-subtítulos\n")

    # 1. transcript None (fallo infra) → SKIP
    _reset(); _install(None, "CONTENEDOR", [], _en_pass(1), _es_vacio)
    r = _try_subtema_fanout(REP, "abandonados", {}, 1)
    check(r is _FANOUT_SKIP, "transcript None (infra) → _FANOUT_SKIP (no se crea seed)")

    # 2. transcript "" (sin subs legítimo) → None (flujo de hoy)
    _reset(); _install("", "CONTENEDOR", [], _en_pass(1), _es_vacio)
    r = _try_subtema_fanout(REP, "abandonados", {}, 1)
    check(r is None, 'transcript "" (sin subs) → None (cae al flujo de hoy, 1 seed)')

    # 3. classify ERROR → SKIP (no fabricar atómico)
    _reset(); _install("transcript real", "ERROR", [], _en_pass(1), _es_vacio)
    r = _try_subtema_fanout(REP, "abandonados", {}, 1)
    check(r is _FANOUT_SKIP, "classify ERROR → _FANOUT_SKIP (no fabrica seed atómico)")

    # 4. ATOMICO legítimo → None (flujo de hoy)
    _reset(); _install("transcript real", "ATOMICO", [], _en_pass(1), _es_vacio)
    r = _try_subtema_fanout(REP, "abandonados", {}, 1)
    check(r is None, "ATOMICO legítimo → None (flujo de hoy)")

    print("\nT3 — EN barato → cap → ES caro (el ES NO se paga para lo que el cap tira)\n")

    # 5. 20 sujetos, todos pasan EN con views distintas, ES todos VACIO.
    N = 20
    subjects = [f"S{i:02d}" for i in range(N)]
    # views = inverso al índice → S00 el más alto; el cap debe quedarse con los 8 más altos
    views_map = {s: (N - i) * 100_000 for i, s in enumerate(subjects)}
    _reset()
    _install("transcript real", "CONTENEDOR", subjects,
             _en_pass(lambda n: views_map[n]), _es_vacio)
    out = _try_subtema_fanout(REP, "abandonados", {}, 1)

    check(isinstance(out, list), "CONTENEDOR → devuelve list de seeds")
    check(COUNT["en"] == N, f"EN medido para TODOS los sujetos: {COUNT['en']} == {N}")
    check(COUNT["es"] == SUBTEMA_FANOUT_CAP_K,
          f"ES medido SOLO a los ≤K del cap: {COUNT['es']} == {SUBTEMA_FANOUT_CAP_K}")
    check(len(out) == SUBTEMA_FANOUT_CAP_K, f"emite K seeds: {len(out)} == {SUBTEMA_FANOUT_CAP_K}")
    fo = out[0]["evidence"]["fanout"]
    check(fo["subjects_extracted"] == N and fo["en_passing"] == N,
          f"fanout record: subjects_extracted={fo['subjects_extracted']}, en_passing={fo['en_passing']}")
    check(fo["dropped_by_cap"] == N - SUBTEMA_FANOUT_CAP_K,
          f"dropped_by_cap cuenta los tirados ANTES de ES: {fo['dropped_by_cap']} == {N - SUBTEMA_FANOUT_CAP_K}")
    # el cap se quedó con los 8 de MAYOR demanda EN (S00..S07)
    emitted_titles = {s["seed_title"] for s in out}
    expected_top = {f"S{i:02d}" for i in range(SUBTEMA_FANOUT_CAP_K)}
    check(emitted_titles == expected_top, f"cap conservó los top-{SUBTEMA_FANOUT_CAP_K} por demanda EN")
    es_old = N
    print(f"      → AHORRO T3: ES medido {COUNT['es']} (nuevo) vs {es_old} (flujo viejo ES-primero) "
          f"= {es_old - COUNT['es']} mediciones ES evitadas ({N} sujetos)")

    # 6. ES-gate DENTRO del cap: 2 de los top-8 salen SATURADO → caen igual.
    def _es_gate_two(name):
        if name in ("S00", "S03"):
            return {"label": "SATURADO", "saturation": 9_000_000, "heaviest": None,
                    "ontopic_count": 9, "anchors_used": [name.lower()], "source": "mock"}
        return _es_vacio(name)
    _reset()
    _install("transcript real", "CONTENEDOR", subjects,
             _en_pass(lambda n: views_map[n]), _es_gate_two)
    out = _try_subtema_fanout(REP, "abandonados", {}, 1)
    check(COUNT["es"] == SUBTEMA_FANOUT_CAP_K,
          f"ES igual se mide para los 8 del cap: {COUNT['es']} == {SUBTEMA_FANOUT_CAP_K}")
    check(len(out) == SUBTEMA_FANOUT_CAP_K - 2,
          f"2 ganadores EN saturados en ES caen: emite {len(out)} == {SUBTEMA_FANOUT_CAP_K - 2}")
    if out:
        check(out[0]["evidence"]["fanout"]["es_gated_in_cap"] == 2,
              "fanout.es_gated_in_cap == 2")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
