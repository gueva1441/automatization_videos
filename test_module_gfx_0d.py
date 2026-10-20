"""test_module_gfx_0d.py — F2 §0d: sfx, chapter_question y source_tag.
Correr: python -m pytest test_module_gfx_0d.py -q
"""
import json
import sys

import pytest

import gfx_config as gc
import script_engine.gfx_director as gd
from script_engine.gfx_literal_lock import lock
from script_engine.gfx_project import GfxScene, write_project

WORDS = [{"word": w, "start": i * 0.5, "end": i * 0.5 + 0.4} for i, w in enumerate(
    "Ese día el huracán Katrina llegó a Nueva Orleans y el agua subió sin parar".split())]
NEXT = {"next.bullets[0]": "Generadores de respaldo fallan el 29 de agosto de 2005.",
        "next.bullets[1]": "Prisión sin luz ni ventilación.", "narration_ch03": "La prisión quedó a oscuras."}


def test_libreria_sfx_existe_y_perfil_la_referencia():
    wavs = {p.name for p in gc.SFX_DIR.glob("*.wav")}
    assert 8 <= len(wavs) <= 15                       # F4c R5: + 5 SFX propios de las categorías de reserva
    prof = gc.load_profile("misterio")
    assert {v["file"] for v in prof["sfx"].values()} <= wavs
    assert all(v["gain_db"] <= -18 for v in prof["sfx"].values())          # bajo la voz


def test_sfx_se_corre_al_hueco_y_nunca_sobre_palabra_acentuada():
    out = {"title_card": None, "callouts": [{"start": 2.1, "text": "Katrina"}], "archive_clippings": [],
           "count_up": None, "evidence_zoom": None, "chapter_question": None}
    sf = lambda b: (gc.SFX_DIR / "tic.wav", -18.0)                           # noqa: E731
    ev = gd.sfx_events(out, WORDS, 0.0, sf)
    # 2.1 cae sobre "Katrina" (2.0–2.4); el hueco 2.4–2.5 está a 0.3 s > 120 ms → acentuada → sin SFX
    assert ev == []
    out["callouts"][0]["start"] = 2.45                                      # dentro del hueco 2.4–2.5
    ev = gd.sfx_events(out, WORDS, 0.0, sf)
    assert len(ev) == 1 and ev[0]["shift_ms"] == 0
    out["callouts"][0]["start"] = 0.55                                      # sobre "día" (corta), hueco a 50 ms
    ev = gd.sfx_events(out, WORDS, 0.0, sf)
    assert len(ev) == 1 and abs(ev[0]["shift_ms"]) <= gc.gfx_rules.sfx_shift_max_ms


def test_chapter_question_candado_por_palabras_de_contenido():
    assert gd.question_ok("¿Por qué fallan los generadores de respaldo?", NEXT)
    assert not gd.question_ok("¿Quién apagó la prisión entera?", NEXT)      # "apagó", "entera" no están
    plan = {"chapter_number": 2, "title_card": None, "callouts": [], "count_up": None, "archive_clippings": [],
            "evidence_zoom": None, "chapter_question": {"text": "¿Quién apagó la prisión entera?"}}
    ok, rej = lock(plan, {}, chapter_number=2, question_sources=NEXT)
    assert ok["chapter_question"] is None and rej[0]["block"] == "chapter_question"


def test_chapter_question_validador_y_cierre(monkeypatch):
    real = gd.max_per_cap                       # F2b §1.3: OFF en el perfil; el código sigue vivo
    monkeypatch.setattr(gd, "max_per_cap", lambda b: 1 if b == "chapter_question" else real(b))
    raw = {"chapter_question": {"use": True, "text": "Por qué fallan los generadores de respaldo"}}
    plan = gd.validate_plan(raw, n_facts=1, n_words=len(WORDS), scenes=[GfxScene(0, 0, 40)], facts=["x"])
    assert plan["chapter_question"]["text"] == "¿Por qué fallan los generadores de respaldo?"
    long = {"chapter_question": {"use": True, "text": "uno dos tres cuatro cinco seis siete ocho nueve diez"}}
    assert "chapter_question" not in gd.validate_plan(long, n_facts=1, n_words=1, scenes=[GfxScene(0, 0, 40)], facts=["x"])
    ctx = {"chapter_number": 2, "facts": ["x"], "skeleton": {}, "eligible": {}}
    res = gd.resolve_plan(plan, ctx=ctx, words=WORDS, scenes=[GfxScene(0, 0.0, 40.0)])
    q = res["chapter_question"]
    assert q["start"] == pytest.approx(40.0 - gc.gfx_rules.question_dur - 0.15) and q["keyword"] == "generadores"


def test_source_tag_solo_si_el_fact_nombra_la_fuente():
    facts = ["Más de 500 prisioneros no figuraban en la lista, según Human Rights Watch.", "El agua subió."]
    srcs = ["Human Rights Watch, 2005, 'New Orleans: Prisoners Abandoned'", "Tanber, George J., 2005, 'Arrested'"]
    tags = gd.fact_sources(facts, srcs)
    assert tags == {0: "Human Rights Watch, 2005"}
    plan = {"chapter_number": 2, "title_card": None, "count_up": None, "archive_clippings": [], "evidence_zoom": None,
            "callouts": [{"text": "500 prisioneros", "source": "Human Rights Watch, 2005"},
                         {"text": "500 prisioneros", "source": "Inventado, 1999"}]}
    sources = {"verified_facts[0]": facts[0], "sources[0]": srcs[0]}
    ok, _ = lock(plan, sources, chapter_number=2)
    assert ok["callouts"][0]["source"] == "Human Rights Watch, 2005" and ok["callouts"][1]["source"] == ""


def test_plantillas_question_y_source(tmp_path):
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    plan = {"chapter_number": 2, "title_card": None, "count_up": None, "archive_clippings": [], "evidence_zoom": None,
            "punch_in": [], "callouts": [{"text": "500 prisioneros", "start": 1.0, "kind": "figure", "duration": 2.5,
                                          "side": "left", "source": "Human Rights Watch, 2005"}],
            "chapter_question": {"text": "¿Por qué fallan los generadores?", "start": 7.5, "duration": 2.3,
                                 "keyword": "generadores"}}
    write_project(plan, [GfxScene(0, 0.0, 10.0, "R3", "")], tmp_path, duration=10.0, width=2560, height=1440, fps=30)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'class="co-src">Human Rights Watch, 2005<' in html
    assert '<span class="kw">generadores</span>' in html and 'id="cq-dim"' in html


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
