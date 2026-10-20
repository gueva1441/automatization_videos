"""F3 (pedido de Omar 2026-10-20): pico del capítulo, nivel de agua, reloj de esquina, zoom con latido, corte a negro."""
from __future__ import annotations

import json
from dataclasses import replace

from script_engine import gfx_peak as gp
from script_engine.gfx_project import GfxScene

MOODS = {"agua": {"triggers": {"sumergidos": 3, "agua": 1, "ahogaba": 3}},
         "oscuridad_encierro": {"triggers": {"oscuro": 1, "encierro": 2}}}


def W(text: str, t0: float = 0.0, step: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(t0 + k * step, 3), "end": round(t0 + k * step + 0.3, 3)} for k, w in enumerate(text.split())]


WORDS = W("Aquel 29 de agosto de 2005 todo cambió. Un manto oscuro cubrió la ciudad. "
          "Calles enteras quedaron sumergidas, sumergidos bajo 4.6 metros de agua putrefacta. "
          "El mundo exterior se ahogaba. Un nuevo tipo de encierro.")
CTX = {"facts": ["Algunas partes quedaron bajo 15 pies (4.6 metros) de agua.", "El huracán tocó tierra el 29 de agosto de 2005."],
       "eligible": {0: False, 1: False}, "fact_source": {}}


def test_pico_es_la_frase_con_mas_peso_3():
    pk = gp.find_peak(WORDS, MOODS)
    assert pk["word"] == "sumergidos" and "4.6" in pk["text"]
    assert gp.find_peak(W("Nada de carga acá."), MOODS) is None


def test_nivel_de_agua_con_cifra_literal_y_dicha():
    pk = gp.find_peak(WORDS, MOODS)
    wl = gp.water_level(pk, CTX, WORDS)
    assert (wl["value_text"], wl["unit"], wl["fact_idx"]) == ("4.6", "metros", 0)
    assert abs(wl["height"] - 0.605) < 0.01                                 # 4.6 m ≈ 60 % de la pantalla
    assert wl["duration"] == 4.5 and wl["rise"] == 2.5
    assert gp.water_level(pk, {"facts": ["Sin cifras."], "eligible": {}}, WORDS) is None
    sin_cifra = W("Las calles quedaron sumergidos en el agua.")
    assert gp.water_level(gp.find_peak(sin_cifra, MOODS), CTX, sin_cifra) is None     # la voz no dice la cifra


def test_reloj_con_la_fecha_literal_y_antes_del_pico(monkeypatch):
    monkeypatch.setattr(gp, "gfx_rules", replace(gp.gfx_rules, ticker_min_times=0))   # motor F3: con la fecha alcanza
    pk = gp.find_peak(WORDS, MOODS)
    tk = gp.time_ticker(CTX, WORDS, 30.0, pk)
    assert (tk["day"], tk["month"], tk["tail"], tk["advance"]) == ("29", "AGO", "2005", False)
    assert tk["source_text"] == "29 de agosto de 2005"
    assert tk["start"] + tk["duration"] <= pk["t"] - gp.PEAK_CLEAR_SEC + 2.0 + 1e-6
    ctx2 = dict(CTX, facts=CTX["facts"] + ["A las 23:40 se cortó la luz y a las 01:15 volvió."])
    assert gp.time_ticker(ctx2, WORDS, 30.0, None)["advance"] is True


def test_clear_around_deja_solo_el_bloque_del_pico():
    plan = {"callouts": [{"text": "15 pies", "start": 9.0}, {"text": "lejos", "start": 30.0}],
            "emphasis": [{"word": "sumergidos", "start": 8.4}, {"word": "oscuro", "start": 2.0}],
            "punch_in": [8.0, 25.0], "archive_clippings": [], "water_level": {"start": 8.4}, "count_up": {"start": 10.0}}
    gone = gp.clear_around(plan, 8.4, "water_level")
    assert [c["text"] for c in plan["callouts"]] == ["lejos"] and [e["word"] for e in plan["emphasis"]] == ["oscuro"]
    assert plan["punch_in"] == [25.0] and plan["count_up"] is None and plan["water_level"]
    assert "callouts:15 pies" in gone and "count_up" in gone


def test_plan_peak_ch02_tipo_y_un_agua_por_video(tmp_path, monkeypatch):
    monkeypatch.setattr(gp, "gfx_rules", replace(gp.gfx_rules, ticker_min_times=0))
    words = W(" ".join(w["word"] for w in WORDS), step=0.6)
    ts = next(w["start"] for w in words if w["word"] == "sumergidos")
    ta = next(w["start"] for w in words if w["word"] == "ahogaba.")
    assert ta - ts > gp.PEAK_CLEAR_SEC
    end = round(words[-1]["end"] + 1, 3)
    scenes = [GfxScene(0, 0.0, ts - 1), GfxScene(1, ts - 1, ta - 1), GfxScene(2, ta - 1, end)]
    boxes = {2: [0.4, 0.45, 0.2, 0.2]}
    plan = {"callouts": [{"text": "15 pies", "start": ts + 2}], "emphasis": [{"word": "sumergidos", "start": ts}],
            "punch_in": [], "archive_clippings": []}
    log: list[str] = []
    gp.plan_peak(plan, ctx=CTX, words=words, scenes=scenes, moods=MOODS, clip_dur=end, box_for=lambda si, w: boxes.get(si), log=log)
    assert plan["pico"]["block"] == "water_level" and plan["water_level"]["value_text"] == "4.6"
    assert plan["callouts"] == [] and plan["emphasis"] == []                     # ±5 s libres
    ez = plan["evidence_zoom"]
    assert ez["word"] == "ahogaba" and ez["latido"] and ez["scene_idx"] == 2 and ez["start"] == round(end - 2.85, 3)
    assert plan["time_ticker"]["tail"] == "2005"
    again = dict(plan)
    assert gp.plan_peak(again, ctx=CTX, words=words, scenes=scenes, moods=MOODS, clip_dur=end,
                        box_for=lambda si, w: None) is again and again["pico"] == plan["pico"]          # idempotente
    # máx 1 nivel de agua por video: si un cap anterior ya lo usó → el pico usa otro bloque (o ninguno)
    (tmp_path / "gfx_plan_ch01.resolved.json").write_text(json.dumps({"plan": {"water_level": {"start": 1}}}), encoding="utf-8")
    assert gp.water_used_before(tmp_path, 2) and not gp.water_used_before(tmp_path, 1)
    p2 = {"callouts": [], "emphasis": [], "punch_in": [], "archive_clippings": []}
    gp.plan_peak(p2, ctx=CTX, words=words, scenes=scenes, moods=MOODS, clip_dur=end, box_for=lambda si, w: None, water_used=True)
    assert not p2.get("water_level")


def test_plantillas_nivel_reloj_latido_y_negro(tmp_path):
    from script_engine.gfx_project import water_level_html, time_ticker_html, write_project
    wl = {"value_text": "4.6", "unit": "metros", "height": 0.605, "start": 33.7, "duration": 4.5, "rise": 2.5}
    h, init, js = water_level_html(wl, 2560, 1440, 97.6)
    assert "height:871px" in h and "#f2efe6" in h and "text-transform:none" in h
    assert 'height: 871, duration: 2.500' in " ".join(js) and '"4.6"' in " ".join(js) and '" m"' in " ".join(js).replace("+ \" m\"", '" m"')
    th, _, tjs = time_ticker_html({"day": "29", "month": "AGO", "tail": "2005", "start": 6.6, "duration": 22.0, "advance": False}, 97.6)
    assert "29 AGO" in th and "2005" in th and "tkObj" not in " ".join(tjs)
    th2, _, tjs2 = time_ticker_html({"day": "29", "month": "AGO", "tail": "23:40", "times": ["23:40", "01:15"], "start": 1,
                                     "duration": 10, "advance": True}, 97.6)
    assert "tkObj" in " ".join(tjs2)
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    q = {"text": "¿Qué pasó?", "start": 10.0, "duration": 3.0, "keyword": "", "generated": True, "pause": 3.0}
    plan = {"chapter_number": 2, "chapter_question": q, "black_hold": {"start": 13.0, "duration": 1.0},
            "evidence_zoom": {"scene_idx": 0, "box": [0.4, 0.45, 0.2, 0.2], "start": 5.0, "latido": True, "latido_t": 6.0}}
    write_project(plan, [GfxScene(0, 0.0, 14.0)], tmp_path, duration=14.0, width=2560, height=1440, fps=30)
    idx = (tmp_path / "index.html").read_text(encoding="utf-8")
    sc = (tmp_path / "compositions" / "scene_01.html").read_text(encoding="utf-8")
    assert 'id="bh" class="clip" data-start="13.000" data-duration="1.000"' in idx
    assert '["#cq-text", "#cq-dim"], { opacity: 0' not in idx                   # corte seco a negro, sin fundido
    assert 'id="lt01"' in sc and "6.000" in sc and "6.280" in sc               # latido lub-dub


def test_candado_nivel_de_agua_y_reloj():
    from script_engine.gfx_literal_lock import lock
    src = {"verified_facts[0]": "Algunas partes quedaron bajo 15 pies (4.6 metros) de agua.",
           "verified_facts[1]": "El huracán tocó tierra el 29 de agosto de 2005."}
    plan = {"water_level": {"value_text": "4.6", "unit": "metros"},
            "time_ticker": {"source_text": "29 de agosto de 2005", "times": []}}
    ok, rej = lock(plan, src, chapter_number=2)
    assert ok["water_level"] and ok["time_ticker"] and not rej
    bad = {"water_level": {"value_text": "5", "unit": "metros"}, "time_ticker": {"source_text": "30 de agosto", "times": []}}
    ok, rej = lock(bad, src, chapter_number=2)
    assert ok["water_level"] is None and ok["time_ticker"] is None and len(rej) == 2


def test_latido_en_los_sfx():
    from gfx_config import sfx_for
    from script_engine.gfx_director import sfx_events
    out = {"evidence_zoom": {"start": 5.0, "latido_t": 6.0, "scene_idx": 0}}
    ev = sfx_events(out, [], 0.0, sfx_for, [])
    lat = [e for e in ev if e["block"] == "latido"]
    assert lat and lat[0]["t"] == 6.0 and lat[0]["file"].endswith("latido.wav")


def test_reloj_elige_la_esquina_libre():
    tk = {"start": 6.0, "duration": 20.0}
    gp.ticker_corner(tk, {"archive_clippings": [{"start": 9.9, "duration": 4.0, "side": "left"}]})
    assert tk["side"] == "right" and tk["start"] == 6.0
    tk = {"start": 6.0, "duration": 20.0}
    gp.ticker_corner(tk, {"callouts": [{"start": 8.0, "duration": 2.5, "side": "right"}]})
    assert tk["side"] == "left"
    tk = {"start": 6.0, "duration": 20.0}
    gp.ticker_corner(tk, {"callouts": [{"start": 8.0, "duration": 2.5, "side": "right"}],
                          "archive_clippings": [{"start": 9.0, "duration": 4.0, "side": "left"}]})
    assert tk["start"] == 13.3 and tk["duration"] == 12.7                    # las dos ocupadas → arranca después


def test_zoom_tapa_el_video_con_un_cuadro_congelado(tmp_path, monkeypatch):
    """Lab (zoom_freeze_frame): el zoom va sobre un cuadro congelado (img). En producción F4 §3 lo apaga."""
    from script_engine import gfx_project
    monkeypatch.setattr(gfx_project, "gfx_rules", replace(gfx_project.gfx_rules, zoom_freeze_frame=True))
    from script_engine.gfx_project import write_project
    monkeypatch.setattr(gfx_project, "_extract_freeze", lambda base, t, out: (out.parent.mkdir(parents=True, exist_ok=True),
                                                                              out.write_bytes(b"jpg"), True)[-1])
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    plan = {"chapter_number": 2, "evidence_zoom": {"scene_idx": 0, "box": [0.4, 0.45, 0.2, 0.2], "start": 5.0}}
    write_project(plan, [GfxScene(0, 0.0, 8.0)], tmp_path, duration=8.0, width=2560, height=1440, fps=30)
    sc = (tmp_path / "compositions" / "scene_01.html").read_text(encoding="utf-8")
    assert 'id="zf01" class="media clip" src="public/cuts/zoomfz_01.jpg" data-start="5.000" data-duration="3.000"' in sc
    assert sc.index('id="zf01"') < sc.index('id="zr01"')                       # dentro del contenedor que escala


def test_f4_reloj_solo_con_dos_horas_verificadas():
    pk = gp.find_peak(WORDS, MOODS)
    assert gp.gfx_rules.ticker_min_times == 2                                # perfil misterio (identidad F4)
    assert gp.time_ticker(CTX, WORDS, 30.0, pk) is None                      # solo fecha → no sale
    ctx2 = dict(CTX, facts=CTX["facts"] + ["A las 23:40 se cortó la luz y a las 01:15 volvió."])
    assert gp.time_ticker(ctx2, WORDS, 30.0, None)["advance"] is True


def test_f4_zoom_y_golpes_escalan_el_contenedor_del_video(tmp_path, monkeypatch):
    """F4 §3: sin cuadro congelado; zoom, golpe de zoom y corte+golpe animan #vw (el frame del <video> va adentro)."""
    from script_engine import gfx_project
    from script_engine.gfx_project import write_project
    assert gfx_project.gfx_rules.zoom_freeze_frame is False
    monkeypatch.setattr(gfx_project, "_extract_freeze", lambda base, t, out: True)
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"x")
    plan = {"chapter_number": 2, "evidence_zoom": {"scene_idx": 1, "box": [0.4, 0.45, 0.2, 0.2], "start": 13.0},
            "punch_in": [3.0], "transitions": {"1": {"kind": "cut_punch", "frames": 0, "rank": "R1"}}}
    write_project(plan, [GfxScene(0, 0.0, 8.0), GfxScene(1, 8.0, 16.0)], tmp_path, duration=16.0, width=2560, height=1440, fps=30)
    s1 = (tmp_path / "compositions" / "scene_01.html").read_text(encoding="utf-8")
    s2 = (tmp_path / "compositions" / "scene_02.html").read_text(encoding="utf-8")
    assert "zoomfz" not in s2 and '.to("#vw02", { scale: 2.2' in s2
    assert 'tl.to("#vw01", { scale: 1.015' in s1 and 'tl.fromTo("#vw02", { scale:' in s2
