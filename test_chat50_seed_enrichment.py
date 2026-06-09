"""
test_chat50_seed_enrichment.py — valida el enriquecimiento del seed fan-out con
outlier_ratio + channel_median + en_age_months (CHAT 50), SIN red ni Gemini.

POR QUÉ: el juez de oro (m_judge_seeds._build_judge_prompt) arma su Criterio #1
(DEMANDA REAL vs RATIO INFLADO) sobre outlier_ratio + channel_median. El camino
fan-out NO los emitía → al juez le llegaba `ratio outlier: Nonex / mediana: None`.
Este test prueba que el productor (fan-out) ahora los emite, con nombres idénticos
al camino directo, y que el fetch caro (mediana del canal) queda DESPUÉS del cap.

Cubre §4 del handoff:
  - 2.1: _measure_en_laxo propaga top_rel_channel_id + top_rel_age_months (gratis).
  - 2.3: el seed fan-out trae en_viral.outlier_ratio == views/mediana, channel_median, en_age_months.
  - el fetch de mediana corre == len(survivors) (≤K), NUNCA len(todos los sujetos).
  - edge: channel_id None → median=None, ratio=0.0, sin crash.
  - edge: dos subtemas mismo channel_id → un solo fetch (cache).
  - consistencia de nombres: un seed fan-out por _build_judge_prompt ya no interpola None.

Correr:  python -X utf8 test_chat50_seed_enrichment.py
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
from niche_discoverer import _try_subtema_fanout, SUBTEMA_FANOUT_CAP_K
from script_engine.m_judge_seeds import _build_judge_prompt


REP = {"video_id": "VID123", "original_title": "Mock Container Title"}

# Contador de fetches a la mediana del canal (el único caro de este fix)
BASELINE_CALLS: list[str] = []


def _install_fanout(subjects, en_fn, baseline_value):
    """Parchea las deps locales del fan-out + el _channel_baseline (módulo nd)."""
    tf.fetch_transcript = lambda vid, *a, **k: "transcript real"
    sc.classify = lambda title, tr: {"tipo": "CONTENEDOR", "razon": "mock"}
    se.extract_segment_subjects = lambda title, tr: list(subjects)
    se.verify_names = lambda names, *a, **k: {}
    sm._measure_en_laxo = en_fn
    sm._measure_es = lambda name: {"label": "VACIO", "saturation": 0.0, "heaviest": None,
                                   "ontopic_count": 0, "anchors_used": [name.lower()], "source": "mock"}
    BASELINE_CALLS.clear()

    def _counting_baseline(channel_id, n, exclude):
        BASELINE_CALLS.append(channel_id)
        # baseline_value puede ser un dict por cid, un callable, o un escalar
        if callable(baseline_value):
            return baseline_value(channel_id)
        if isinstance(baseline_value, dict):
            return baseline_value.get(channel_id)
        return baseline_value

    nd._channel_baseline = _counting_baseline


def _en(views, cid, age):
    """Fabrica un _measure_en_laxo mockeado (un sujeto que pasa LAXO)."""
    def _fn(name):
        return {
            "pasa_laxo": True,
            "top_rel_views": views(name) if callable(views) else views,
            "top_rel_title": f"{name} EN",
            "top_rel_video_id": f"en_{name}",
            "top_rel_channel_id": cid(name) if callable(cid) else cid,
            "top_rel_age_months": age(name) if callable(age) else age,
        }
    return _fn


def run():
    failures = []

    def check(cond, msg):
        print(f"  [{'✓' if cond else '✗'}] {msg}")
        if not cond:
            failures.append(msg)

    # ── 2.1: _measure_en_laxo propaga channel_id + age (REAL, con search mockeada) ──
    print("2.1 — _measure_en_laxo propaga top_rel_channel_id + top_rel_age_months\n")
    sm.search_viral_english = lambda name, limit=15: [
        {"title": "Wittenoom asbestos ghost town", "views": 800_000,
         "video_id": "vReal", "channel_id": "UC_real_chan", "en_age_months": 7},
        {"title": "unrelated cooking video", "views": 5_000_000,
         "video_id": "vNope", "channel_id": "UC_other", "en_age_months": 1},
    ]
    en = sm._measure_en_laxo("Wittenoom")
    check(en.get("top_rel_channel_id") == "UC_real_chan",
          f"top_rel_channel_id propagado: {en.get('top_rel_channel_id')!r}")
    check(en.get("top_rel_age_months") == 7,
          f"top_rel_age_months propagado: {en.get('top_rel_age_months')!r}")
    check(en.get("top_rel_views") == 800_000,
          "el candidato RELEVANTE (no el cooking de más vistas) es el top")

    # ── 2.3: el seed fan-out trae los 3 campos, ratio == views/mediana ──
    print("\n2.3 — seed fan-out: outlier_ratio == views/mediana, channel_median, en_age_months\n")
    VIEWS, MEDIAN, AGE = 600_000, 50_000, 9
    _install_fanout(["Subtema Uno"],
                    _en(VIEWS, "UC_aaa", AGE), MEDIAN)
    out = _try_subtema_fanout(REP, "abandonados", {}, 1)
    check(isinstance(out, list) and len(out) == 1, f"emite 1 seed: {len(out) if out else 0}")
    ev = out[0]["evidence"]["en_viral"]
    check(ev.get("channel_median") == MEDIAN, f"channel_median == {MEDIAN}: {ev.get('channel_median')}")
    check(abs(ev.get("outlier_ratio") - VIEWS / MEDIAN) < 1e-9,
          f"outlier_ratio == {VIEWS}/{MEDIAN} == {VIEWS/MEDIAN}: {ev.get('outlier_ratio')}")
    check(ev.get("en_age_months") == AGE, f"en_age_months == {AGE}: {ev.get('en_age_months')}")

    # ── fetch DESPUÉS del cap: baseline llamado == survivors (≤K), no == todos los sujetos ──
    print("\nfetch caro DESPUÉS del cap — baseline corre solo sobre survivors (≤K)\n")
    N = 20
    subjects = [f"S{i:02d}" for i in range(N)]
    views_map = {s: (N - i) * 100_000 for i, s in enumerate(subjects)}
    _install_fanout(subjects,
                    _en(lambda n: views_map[n], lambda n: f"UC_{n}", 5),
                    50_000)
    out = _try_subtema_fanout(REP, "abandonados", {}, 1)
    check(len(BASELINE_CALLS) == SUBTEMA_FANOUT_CAP_K,
          f"_channel_baseline llamado == K survivors ({SUBTEMA_FANOUT_CAP_K}), "
          f"NO == {N} sujetos: {len(BASELINE_CALLS)}")
    check(len(out) == SUBTEMA_FANOUT_CAP_K, f"emite K seeds: {len(out)}")

    # ── edge: channel_id None → median=None, ratio=0.0, sin crash, seed igual se construye ──
    print("\nedge — channel_id None → median=None, ratio=0.0, sin crash\n")
    _install_fanout(["Sin Canal"],
                    _en(400_000, None, 3), 50_000)
    out = _try_subtema_fanout(REP, "abandonados", {}, 1)
    ev = out[0]["evidence"]["en_viral"]
    check(ev.get("channel_median") is None, f"channel_median is None: {ev.get('channel_median')}")
    check(ev.get("outlier_ratio") == 0.0, f"outlier_ratio == 0.0: {ev.get('outlier_ratio')}")
    check(len(BASELINE_CALLS) == 0, f"sin channel_id → 0 fetches: {len(BASELINE_CALLS)}")

    # ── edge: dos subtemas mismo channel_id → un solo fetch (cache) ──
    print("\nedge — dos subtemas mismo channel_id → un solo fetch (cache)\n")
    _install_fanout(["Hermano A", "Hermano B"],
                    _en(300_000, "UC_shared", 4), 50_000)
    out = _try_subtema_fanout(REP, "abandonados", {}, 1)
    check(len(out) == 2, f"emite 2 seeds: {len(out)}")
    check(len(BASELINE_CALLS) == 1,
          f"canal compartido → 1 solo fetch (cache): {len(BASELINE_CALLS)}")
    check(BASELINE_CALLS == ["UC_shared"], f"el fetch fue del canal compartido: {BASELINE_CALLS}")

    # ── consistencia de nombres: el juez ya NO interpola None en ratio/mediana ──
    print("\nconsistencia — _build_judge_prompt no interpola None en ratio/mediana\n")
    _install_fanout(["Tema Juez"],
                    _en(600_000, "UC_judge", 9), 50_000)
    out = _try_subtema_fanout(REP, "abandonados", {}, 1)
    prompt = _build_judge_prompt(out[0])
    check("ratio outlier: Nonex" not in prompt, "el juez NO recibe 'ratio outlier: Nonex'")
    check("mediana del canal: None" not in prompt, "el juez NO recibe 'mediana del canal: None'")
    check("ratio outlier: 12.0x" in prompt, "el juez recibe el ratio real (600k/50k = 12.0x)")
    check("mediana del canal: 50000" in prompt, "el juez recibe la mediana real (50000)")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
