"""
test_module_f29a.py — F29 §A: el gfx obedece a la escaleta (script_engine/gfx_realizador). Con la escaleta, la narración
por beat, el pool y los timestamps de Vajont (sin red): ventanas por beat; los `a_pantalla` en su beat (D128 en el
respiro del cap 6, después del pico; D245 en el beat 13; Q50 en el beat 8); ningún bloque fuera de su ventana; ≤ 5 por
cap; pico con bloque grande en los 7 caps; sellos ≤ 1; la pregunta = `cierre` del último beat; crítico parejo.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from script_engine import gfx_realizador as gr

ROOT = Path(__file__).resolve().parent
STEPS = ROOT / "data" / "scripts" / "_steps"
AUD = ROOT / "output" / "audio" / "f8s3-vajont"
HAY = (STEPS / "f8s3-vajont" / "01a_escaleta.json").exists() and (AUD / "ch06_timestamps.json").exists()
pytestmark = pytest.mark.skipif(not HAY, reason="sin los datos de Vajont en disco")


def _datos():
    carga = gr.cargar("f8s3-vajont", STEPS)
    pool = json.loads((STEPS / "f8s3-vajont" / "00_pool_v3.json").read_text(encoding="utf-8"))
    return carga, pool


def _real(cap, carga, pool, tmp_path):
    w = json.loads((AUD / f"ch{cap:02d}_timestamps.json").read_text(encoding="utf-8"))
    return gr.preparar(cap, carga, pool, w, 0.0, tmp_path, f"ch{cap:02d}"), w


def test_ventanas_por_beat(tmp_path):
    carga, pool = _datos()
    for cap in range(1, 8):
        real, w = _real(cap, carga, pool, tmp_path)
        bs = real["beats"]
        assert bs and all(b["t0"] < b["t1"] for b in bs)
        assert all(a["t1"] <= b["t0"] + 0.01 for a, b in zip(bs, bs[1:]))            # en orden, sin pisarse
        assert bs[-1]["t1"] <= float(w[-1]["end"]) + 0.01
        assert (tmp_path / f"gfx_beats_ch{cap:02d}.json").exists()
    real6, _ = _real(6, carga, pool, tmp_path)
    assert [(b["n"], b["funcion"]) for b in real6["beats"]] == [(10, "pico"), (11, "respiro")]


def test_a_pantalla_en_su_beat(tmp_path):
    carga, pool = _datos()
    r6, _ = _real(6, carga, pool, tmp_path)
    c = {x["id"]: x for x in r6["candidatos"]}
    pico = next(b for b in r6["beats"] if b["funcion"] == "pico")
    assert c["D128"]["beat"] == 11 and c["D128"]["obligatorio"] and c["D128"]["t0"] >= pico["t1"]
    r7, _ = _real(7, carga, pool, tmp_path)
    assert {x["id"]: x for x in r7["candidatos"]}["D245"]["beat"] == 13
    r5, _ = _real(5, carga, pool, tmp_path)
    assert {x["id"]: x for x in r5["candidatos"]}["Q50"]["beat"] == 8
    # nada de otro cap entra como candidato
    ids6 = {i for b in carga["escaleta"]["beats"] if int(b["cap"]) == 6 for i in [b["dato_central"], *b["datos_apoyo"]]}
    assert {x["id"] for x in r6["candidatos"]} <= ids6 | {"D128", "D192"}


def _plan_lleno(real):
    """Un plan con de todo: bloques dentro y fuera de ventana, candidatos y no candidatos, sellos de más."""
    b0 = real["beats"][0]
    cands = real["candidatos"]
    ok = next(c for c in cands if c["obligatorio"] or not c["ya_dicho"])
    return {
        "archive_clippings": [
            {"headline": "uno dos tres cuatro cinco seis", "start": ok["t0"] + 1, "duration": 6.0, "pool_id": ok["id"]},
            {"headline": "fuera de su ventana", "start": ok["t1"] + 30, "duration": 6.0, "pool_id": ok["id"]},
        ] + [{"headline": f"extra {k}", "start": c["t0"] + 2 + k, "duration": 6.0, "pool_id": c["id"]}
             for k, c in enumerate(x for x in cands if (x["obligatorio"] or not x["ya_dicho"]) and x is not ok)],
        "callouts": [{"text": "de VERIFIED_FACTS", "start": b0["t0"] + 3, "duration": 2.5, "kind": "figure"}],
        "count_up": {"start": b0["t0"] + 5, "duration": 3.7, "value_text": "1910"},
        "emphasis": [{"word": "muertos", "start": b0["t0"] + 8, "icon": "calavera"},
                     {"word": "agua", "start": b0["t0"] + 9, "icon": "gota"},
                     {"word": "ola", "start": b0["t0"] + 10, "peak_word": True, "icon": "gota"}],
        "punch_in": [b0["t0"] + 1.5, b0["t0"] + 40],
        "pico": {"t": b0["t0"] + 10, "word": "ola", "block": None},
    }


def test_finalizar_ventana_topes_sellos_y_duraciones(tmp_path):
    carga, pool = _datos()
    for cap in range(1, 8):
        real, _ = _real(cap, carga, pool, tmp_path)
        plan = _plan_lleno(real)
        gr.finalizar(plan, real, [])
        cand = {c["id"]: c for c in real["candidatos"]}
        for b in plan["archive_clippings"] + plan["callouts"]:
            c = cand[b["pool_id"]]                                   # solo candidatos
            assert c["t0"] - 0.3 <= b["start"] <= c["t1"]            # dentro de su ventana
            assert b["duration"] == gr.duracion_texto(b.get("headline") or b.get("text"))
        n = len(plan["archive_clippings"]) + len(plan["callouts"]) + len(plan["emphasis"])
        assert n <= gr.TOPE_CAP
        assert plan["count_up"] is None
        assert len(plan["emphasis"]) <= 1 and all(e.get("peak_word") for e in plan["emphasis"])
        assert all("icon" not in e for e in plan["emphasis"])     # gota fuera: ícono figurativo
        assert all(not b.get("text") == "de VERIFIED_FACTS" for b in plan["callouts"])
    assert gr.duracion_texto("una dos tres") == 2.5 and gr.duracion_texto(" ".join(["x"] * 30)) == 8.0
    assert gr.duracion_texto(" ".join(["x"] * 9)) == 4.0


def test_pico_con_bloque_grande_en_los_7_caps(tmp_path):
    carga, pool = _datos()
    for cap in range(1, 8):
        real, _ = _real(cap, carga, pool, tmp_path)
        top = max(real["beats"], key=lambda b: b["intensidad"])
        plan = {"pico": {"t": top["t0"] + 2, "word": "x", "block": None}, "callouts": [], "archive_clippings": []}
        blk = gr.garantizar_pico(plan, real, pool, [])
        assert blk in gr.GRANDES and plan["pico"]["block"] in gr.GRANDES, cap
        rot = [c for c in plan["callouts"] if c.get("pico")]
        assert rot and rot[0]["beat"] == top["n"] and rot[0]["text"]
    # con un nivel de agua en el pico, no agrega nada
    plan = {"pico": {"t": 50.0, "word": "x", "block": "water_level"}, "water_level": {"start": 49.0, "duration": 4.5}}
    assert gr.garantizar_pico(plan, real, pool, []) == "water_level" and not plan.get("callouts")


def test_pregunta_es_el_cierre_del_ultimo_beat(tmp_path, monkeypatch):
    from script_engine import gfx_layer as gl
    carga, pool = _datos()
    real, _ = _real(4, carga, pool, tmp_path)
    resolved: dict = {}
    ctx = {"realizador": real, "chapter_number": 4, "chapters": []}
    monkeypatch.setattr("script_engine.gfx_question.question_for", lambda *a, **k: pytest.fail("no se genera"))
    pause = gl.closing_question(resolved, ctx, tmp_path, "ch04", 100.0, [])
    cierre = next(b for b in carga["escaleta"]["beats"] if int(b["n"]) == 7)["cierre"]
    assert resolved["chapter_question"]["text"] == cierre.strip() and pause > 0
    assert json.loads((tmp_path / "gfx_pause_ch04.json").read_text(encoding="utf-8"))["text"] == cierre.strip()


def test_critico_parejo(tmp_path):
    from script_engine import gfx_critic as gc
    plan = {"archive_clippings": [{"headline": "recorte reservado", "start": 1.0, "duration": 5.0, "reserved": True},
                                  {"headline": "reservado que estorba", "start": 9.0, "duration": 5.0, "reserved": True}],
            "quote_card": {"text": "una cita que estorba", "author": "X", "start": 20.0, "duration": 4.0}}
    ver = {"recorte reservado": "repite", "reservado que estorba": "estorba", "una cita que estorba": "estorba"}

    for n in ("a", "b", "c"):
        (tmp_path / f"{n}.jpg").write_bytes(b"x")

    def call(img, prompt, *drawn):
        txt = next(k for k in ver if k in prompt)
        return {"veredicto": ver[txt], "motivo": "test"}
    rows = gc.criticize(plan, base=tmp_path / "no.mp4", words=[], time_offset=0.0, work_dir=tmp_path, cap="ch01",
                        log=[], call=call, fewshot=[], snaps={1.0 + 1.0: tmp_path / "a.jpg", 9.0 + 1.0: tmp_path / "b.jpg",
                                                             20.0 + 1.0: tmp_path / "c.jpg"})
    assert [a["headline"] for a in plan["archive_clippings"]] == ["reservado que estorba"]   # «repite» corta igual
    assert plan["quote_card"] is None                                                        # la cita perdió la reserva
    assert {r["texto"]: r["pasa"] for r in rows} == {"recorte reservado": False, "reservado que estorba": True,
                                                      "una cita que estorba": False}


def test_pico_sin_pico_de_gfx_peak_sale_de_la_escaleta(tmp_path):
    carga, pool = _datos()
    for cap in (2, 4):                                  # en F27, gfx_peak no encontró pico en estos dos caps
        real, _ = _real(cap, carga, pool, tmp_path)
        plan = {"pico": None, "callouts": [], "archive_clippings": []}
        assert gr.garantizar_pico(plan, real, pool, []) in gr.GRANDES
        top = max(real["beats"], key=lambda b: (b["intensidad"], b["n"]))
        assert plan["pico"]["fuente"].startswith(f"escaleta (beat {top['n']}") and plan["callouts"][0]["pico"]


def test_pico_no_repite_un_item_ya_puesto(tmp_path):
    carga, pool = _datos()
    real, _ = _real(6, carga, pool, tmp_path)
    pico = next(b for b in real["beats"] if b["funcion"] == "pico")
    t = pico["t1"] - 4
    # un recorte que arranca 3 s después de la frase del pico es el bloque del pico: no se agrega nada
    plan = {"pico": {"t": t, "word": "x", "block": None}, "callouts": [],
            "archive_clippings": [{"headline": "h", "start": t + 3, "duration": 5.0, "pool_id": "T58"}]}
    assert gr.garantizar_pico(plan, real, pool, []) == "archive_clippings" and plan["callouts"] == []
    # el mismo ítem puesto lejos del pico: el rótulo del pico usa OTRO candidato del beat
    plan = {"pico": {"t": t, "word": "x", "block": None}, "callouts": [],
            "archive_clippings": [{"headline": "h", "start": pico["t0"] + 5, "duration": 5.0, "pool_id": "T58"}]}
    gr.garantizar_pico(plan, real, pool, [])
    assert plan["callouts"] and plan["callouts"][0]["pool_id"] != "T58"
