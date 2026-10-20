"""F3 (pedido de Omar 2026-10-20): pregunta de cierre automática + bloque de ícono + pausa de cierre."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from script_engine import gfx_question as gq

NEXT3 = ["La respuesta a esa pregunta no tardó en llegar, y fue brutal.",
         "La prisión, una fortaleza de concreto, empezó a ceder desde adentro.",
         "El mismo 29 de agosto de 2005, el día del impacto del huracán, los generadores de respaldo sucumbieron."]
SAID = "Algunas partes quedaron bajo 15 pies de agua. Aproximadamente 6,500 personas estaban en la prisión."


# ── validador (contrato literal de Omar)

@pytest.mark.parametrize("q,ok", [
    ("¿Qué pasó con los generadores de la prisión?", True),
    ("¿Cómo cedió la fortaleza de concreto?", True),
    ("¿Por qué sucumbieron los generadores?", True),
    ("¿El huracán destruyó la prisión?", False),                        # sí/no
    ("¿La prisión resistió?", False),
    ("¿Los generadores fallaron?", False),
    ("¿Las celdas aguantaron?", False),
    ("¿Resistió la prisión al huracán?", False),                         # no empieza con interrogativo abierto
    ("¿Qué pasó con las 6,500 personas dentro de la prisión?", False),   # repite cifra ya dicha
    ("¿Qué sintieron todos ellos mientras miraban afuera sin poder hacer nada en absoluto?", False),   # > 12 palabras
    ("¿Quién tuvo la culpa de todo esto?", False),                       # ningún sustantivo del cap siguiente
])
def test_validate(q, ok):
    assert (gq.validate(q, NEXT3, SAID) is None) is ok, gq.validate(q, NEXT3, SAID)


def test_clean_pone_signos():
    assert gq.clean("Qué pasó con la prisión") == "¿Qué pasó con la prisión?"
    assert gq.clean("¿Qué pasó?.") == "¿Qué pasó?"


def test_dos_reintentos_y_despues_sin_pregunta():
    calls = []

    def fake(prompt, **kw):
        calls.append(prompt)
        return {"pregunta": "¿El huracán destruyó la prisión?"}
    r = gq.generate("Una frase. Otra frase. La última frase.", " ".join(NEXT3), SAID, call=fake)
    assert r["text"] is None and len(calls) == 3                     # 1 + 2 reintentos
    assert "rechazada" in calls[1] and "sí/no" in calls[2]           # el rechazo se le cuenta al modelo
    assert all(x["rechazo"] for x in r["intentos"])


def test_segundo_intento_valido():
    answers = iter(["¿La prisión resistió?", "¿Qué hizo ceder a la fortaleza de concreto?"])
    r = gq.generate("A. B. C.", " ".join(NEXT3), SAID, call=lambda p, **k: {"pregunta": next(answers)})
    assert r["text"] == "¿Qué hizo ceder a la fortaleza de concreto?" and len(r["intentos"]) == 2


def test_cache_regenerar_editar_y_ultimo_cap(tmp_path):
    chapters = [{"chapter_number": 2, "narration": "Una. Dos. Tres."}, {"chapter_number": 3, "narration": " ".join(NEXT3)}]
    n = {"c": 0}

    def fake(p, **k):
        n["c"] += 1
        return {"pregunta": "¿Qué hizo ceder a la prisión?" if n["c"] == 1 else "¿Cómo sucumbieron los generadores?"}
    a = gq.question_for(tmp_path, "ch02", 2, chapters, call=fake)
    b = gq.question_for(tmp_path, "ch02", 2, chapters, call=fake)                 # cache
    assert a["text"] == b["text"] and n["c"] == 1 and a["generated"] is True
    c = gq.question_for(tmp_path, "ch02", 2, chapters, call=fake, regenerate=True)
    assert c["text"] == "¿Cómo sucumbieron los generadores?"
    e = gq.save_edited(tmp_path, "ch02", "quién fue el culpable")
    assert e["text"] == "¿quién fue el culpable?" and e["manual"] is True and e["generated"] is True
    last = gq.question_for(tmp_path, "ch03", 3, chapters, call=fake)
    assert last["text"] is None and n["c"] == 2                                   # último cap: sin llamada


def test_candado_deja_pasar_la_pregunta_generada():
    from script_engine.gfx_literal_lock import lock
    q = {"text": "¿Qué hizo ceder a la prisión?", "start": 97.6, "duration": 3.0, "generated": True, "pause": 3.0}
    ok, rej = lock({"chapter_question": dict(q)}, {"narration_ch02": "otra cosa"}, chapter_number=2, question_sources={})
    assert ok["chapter_question"]["text"] == q["text"] and not rej
    ok, rej = lock({"chapter_question": dict(q, generated=False)}, {"narration_ch02": "otra cosa"}, chapter_number=2,
                   question_sources={})
    assert ok["chapter_question"] is None and rej                                # sin la marca sigue el candado viejo


# ── bloque de ícono y viñetas

def test_bloque_de_icono_siempre_con_la_palabra_al_lado():
    from script_engine.gfx_project import icon_callout_html
    e = {"word": "agua", "icon": "gota", "icon_anim": "stamp", "duration": 2.5, "side": "right", "stamp": False,
         "source": "Human Rights Watch, 2005"}
    html, init, js = icon_callout_html(0, e, 38.5, 97.6, zone="mid")
    assert ">agua<" in html                                           # la palabra aunque stamp=False: nunca suelto
    assert "flex-direction:row-reverse" in html and "top:38%;right:6%" in html
    assert 'width="360"' in html                                       # ícono L (perfil misterio)
    assert "ic0-grain" in html and "feComposite" in html and "drop-shadow" in html
    assert "Human Rights Watch, 2005" in html and "ib-src" in html     # fuente debajo
    html2, _, _ = icon_callout_html(1, dict(e, side="left", source=""), 10, 97.6, zone="top")
    assert "top:14%;left:6%" in html2 and "ib-src" not in html2


def test_icono_dentro_del_dato_y_del_recorte(tmp_path):
    from script_engine.gfx_project import GfxScene, card_icon_html, write_project
    assert card_icon_html("x", None, 100) == "" and card_icon_html("x", "no_existe", 100) == ""
    assert "#1b1a17" in card_icon_html("x", "candado", 100, dark=True)
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    plan = {"chapter_number": 2, "callouts": [{"text": "15 pies", "start": 5.0, "kind": "figure", "duration": 2.5, "side": "right",
                                               "icon": "gota"}],
            "archive_clippings": [{"kicker": "2005", "headline": "Titular", "body": "", "start": 2.0, "duration": 4.0,
                                   "side": "left", "era_decade": 2000, "icon": "candado"}]}
    write_project(plan, [GfxScene(0, 0.0, 10.0)], tmp_path, duration=10.0, width=2560, height=1440, fps=30)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'class="co-ico"' in html and 'class="ar-ico"' in html and ".ar-ico ~ .ar-head" in html


def test_pregunta_entra_en_persiana(tmp_path):
    from script_engine.gfx_project import GfxScene, write_project
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    q = {"text": "¿Qué hizo ceder a la prisión?", "start": 10.0, "duration": 3.0, "keyword": "prisión", "generated": True, "pause": 3.0}
    write_project({"chapter_number": 2, "chapter_question": q}, [GfxScene(0, 0.0, 13.0)], tmp_path, duration=13.0,
                  width=2560, height=1440, fps=30)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'class="cq-line"' in html and 'gsap.set("#cq-text .cq-line", { yPercent: 110 })' in html
    assert 'data-start="10.000" data-duration="3.000"' in html and "opacity: 0.7" in html   # fondo 70 %


# ── pausa de cierre en el pipeline

def test_closing_question_alarga_y_deja_la_pausa(tmp_path, monkeypatch):
    from script_engine import gfx_layer
    monkeypatch.setattr(gq, "question_for", lambda *a, **k: {"text": "¿Qué hizo ceder a la prisión?", "intentos": [{}]})
    resolved: dict = {"chapter_question": None}
    log: list[str] = []
    pause = gfx_layer.closing_question(resolved, {"chapter_number": 2, "chapters": []}, tmp_path, "ch02", 97.633, log)
    q = resolved["chapter_question"]
    assert pause == 4.0 and q["start"] == 97.633 and q["duration"] == 3.0 and q["generated"] and q["pause"] == 3.0
    assert resolved["black_hold"] == {"start": 100.633, "duration": 1.0}          # corte a negro 1 s después de la pregunta
    assert json.loads((tmp_path / "gfx_pause_ch02.json").read_text(encoding="utf-8"))["pause"] == 4.0
    monkeypatch.setattr(gq, "question_for", lambda *a, **k: {"text": None, "motivo": "último capítulo", "intentos": []})
    assert gfx_layer.closing_question(resolved, {"chapter_number": 7, "chapters": []}, tmp_path, "ch02", 97.6, log) == 0.0
    assert resolved["chapter_question"] is None and not (tmp_path / "gfx_pause_ch02.json").exists()


def test_fase2b_musica_suma_la_pausa_solo_con_gfx(tmp_path):
    import fase2b

    class P:
        def __init__(self, cid):
            self.chapter_id = cid
    (tmp_path / "gfx_pause_ch02.json").write_text('{"pause": 3.0}', encoding="utf-8")
    assert fase2b._gfx_pauses([P("ch01"), P("ch02")], tmp_path) == {"ch02": 3.0}
    import inspect
    src = inspect.getsource(fase2b._assemble_one_video)
    assert "_gfx_pauses(plans, work_dir) if gfx else None" in src             # sin --gfx: None → sin cambios
    assert "plan.audio_duration + (extra_sec or {}).get(ch_id, 0.0)" in inspect.getsource(fase2b._build_continuous_music_track)


def test_extend_base_alarga_con_el_ultimo_cuadro(tmp_path):
    import subprocess
    from script_engine.gfx_layer import _ffprobe_duration, extend_base
    base = tmp_path / "base.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=red:s=320x180:d=2:r=30", "-pix_fmt", "yuv420p",
                    str(base)], check=True, timeout=120)
    extend_base(base, 3.0, 30)
    assert abs(_ffprobe_duration(base) - 5.0) < 0.1
    assert not list(tmp_path.glob("*.pausa.mp4"))


def test_icon_sources_toma_la_fuente_del_dato():
    from script_engine.gfx_layer import icon_sources
    ctx = {"facts": ["Más de 500 prisioneros no figuraban, según Human Rights Watch.", "El agua subió."],
           "fact_source": {0: "Human Rights Watch, 2005"}}
    res = {"emphasis": [{"word": "prisioneros", "icon_callout": True}, {"word": "agua", "icon_callout": True},
                        {"word": "prisioneros", "icon_callout": False}]}
    assert icon_sources(res, ctx) == 1
    assert res["emphasis"][0]["source"] == "Human Rights Watch, 2005"
    assert "source" not in res["emphasis"][1] and "source" not in res["emphasis"][2]
