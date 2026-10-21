"""F5f (después de ver el video F5e): sustantivo con ícono sobre adjetivo, palabras del tema a peso 1, reservados con
prioridad y motivo de choque, bloque cita, eco de cifras, aire entre recortes, nivel de agua desde un reservado y
titulares sin comillas abiertas. Sin red."""
from __future__ import annotations

from script_engine import gfx_intensity as gi
from script_engine import gfx_peak as gk
from script_engine import gfx_pool as gp
from script_engine.gfx_project import GfxScene

MOODS = {"muerte": {"layer": "muerte", "triggers": {"cadáveres": 3, "escalofriantes": 3, "reclusos": 3},
                    "icon_words": {"cadáveres": "calavera"}}}


def _words(text: str, step: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + step * 0.9, 3)}
            for k, w in enumerate(text.split())]


def test_sustantivo_con_icono_gana_al_adjetivo_de_su_categoria():
    hits = [{"i": 2, "word": "escalofriantes", "category": "muerte", "weight": 3},
            {"i": 9, "word": "cadáveres", "category": "muerte", "weight": 2}]
    assert [h["word"] for h in gk.prefer_icon_nouns(hits, MOODS)] == ["cadáveres"]
    other = [{"i": 2, "word": "escalofriantes", "category": "muerte", "weight": 3},
             {"i": 9, "word": "celda", "category": "oscuridad", "weight": 2}]
    assert len(gk.prefer_icon_nouns(other, {**MOODS, "oscuridad": {"icon_words": {"celda": "candado"}}})) == 2
    w = _words("Los testimonios más escalofriantes hablaban de cadáveres flotando.")
    peak = {**gk.sentences(w)[0], "t": 0.0}
    assert gk.peak_word(peak, w, MOODS)["word"] == "cadáveres"


def test_palabras_del_tema_peso_1():
    assert gi.is_theme_word("Reclusos") and gi.is_theme_word("cárcel") and not gi.is_theme_word("cadáveres")
    assert gi.stamp_lexicon(MOODS)["muerte"]["triggers"]["reclusos"] == 1
    raw = {"intensidad": [0.5], "pico_sentence_idx": 0, "cargas": [
        {"word": "prisioneros", "sentence_idx": 0, "categoria": "muerte", "peso": 3, "concreta": True,
         "clase": "sustantivo", "neutra": False},
        {"word": "cadáveres", "sentence_idx": 0, "categoria": "muerte", "peso": 3, "concreta": True,
         "clase": "sustantivo", "neutra": False}]}
    res, why = gi.validate(raw, ["Los prisioneros vieron cadáveres"], MOODS)
    assert [c["word"] for c in res["cargas"]] == ["cadáveres"] and any("tema" in x for x in why)


def test_reservado_desplaza_sellos_y_cede_ante_la_pregunta():
    sc, sc2 = GfxScene(0, 4.0, 10.0), GfxScene(0, 0.0, 20.0)    # en sc no hay ventana libre: desplaza
    sello = {"start": 5.0, "duration": 2.5, "word": "abandono"}
    plan = {"emphasis": [sello], "chapter_question": {"start": 14.0, "duration": 3.0, "text": "¿Y?"}}
    busy = gp._busy_blocks(plan)
    slot, victims = gp.reserved_slot(4.0, sc, 30.0, busy, [], 6.0, 4.0)
    assert slot == (4.0, 10.0) and [v["label"] for v in victims] == ["sello «abandono»"]
    assert gp.displace(plan, victims, busy) == ["sello «abandono»"] and plan["emphasis"] == []
    assert gp.reserved_slot(1.0, sc2, 30.0, busy, [], 6.0, 4.0) == ((1.0, 7.0), [])            # libre: no desplaza
    back, _ = gp.reserved_slot(12.0, sc2, 30.0, gp._busy_blocks(plan), [], 6.0, 4.0)
    assert back == (8.0, 14.0)                                  # no pisa la pregunta: se corre para atrás
    q_all = {"chapter_question": {"start": 0.0, "duration": 30.0, "text": "¿Y?"}}
    assert gp.reserved_slot(12.0, sc2, 30.0, gp._busy_blocks(q_all), [], 6.0, 4.0)[0] is None
    rec = {"start": 4.0, "duration": 6.0, "reserved": True, "pool_id": "T16", "headline": "x"}
    p2 = {"archive_clippings": [rec], "count_up": {"start": 6.0, "value_text": "517"}, "emphasis": [dict(sello)]}
    out = gp.enforce_reserved(p2, [])
    assert p2["count_up"] is None and p2["emphasis"] == [] and "T16 desplaza" in out[0]
    p3 = {"archive_clippings": [dict(rec)], "water_level": {"start": 7.0, "duration": 4.5, "value_text": "4.6"}}
    assert gp.enforce_reserved(p3, []) and p3["archive_clippings"] == []                     # cede ante el agua
    assert gk.clear_around({"archive_clippings": [rec]}, 5.0, "emphasis") == []              # el pico no lo saca


def test_eco_de_cifra_y_comillas_abiertas():
    w = _words("La prisión albergaba a 6,375 reclusos esa noche y nadie los contaba.")
    assert gp.figure_echo("albergaba a 6,375 reclusos", w, 8.0, 0.0, 10.0) == "6,375"
    assert gp.figure_echo("albergaba a 6,375 reclusos", w, 30.0, 0.0, 10.0) is None
    assert gp.figure_echo("el informe de 2006", w, 1.0, 0.0, 10.0) is None                   # un año no es cifra
    src = 'La ACLU publica el informe "Abandoned & Abused: Orleans Parish Prisoners in the Wake of Hurricane Katrina".'
    assert gp.close_quotes('La ACLU publica el informe "Abandoned & Abused', src, 12) == "La ACLU publica el informe"
    assert gp.close_quotes('Publica "Abandoned', 'Publica "Abandoned" hoy.', 12) == 'Publica "Abandoned"'
    assert all(gp._open_quote(o) is None for o in gp.pool_clause_options(src, 12))


def test_bloque_cita_literal_con_autor():
    q = {"id": "Q02", "texto": "Están en la cárcel, hombre. Mienten... No confíen en drogadictos", "autor": "Sheriff Gusman"}
    pool = {"citas": [q], "datos": [], "cronologia": [], "lugares": [], "personajes": []}
    w = _words("Gusman fue tajante. Están en la cárcel, hombre. Mienten... No confíen en drogadictos, declaró.")
    plan = {"emphasis": [{"start": 2.0, "duration": 2.5, "word": "tajante"}]}
    row = gp.plan_pool_quote(plan, ctx={"pool": pool}, words=w, scenes=[GfxScene(0, 0.0, 30.0)], time_offset=0.0,
                             busy=gp._busy_blocks(plan), cands=["Q02"], used=set(), log=[])
    qc = plan["quote_card"]
    assert row["ahora"] == q["texto"] and qc["author"] == "Sheriff Gusman" and qc["start"] == 1.2
    assert 4.0 <= qc["duration"] <= 5.0 and plan["emphasis"] == []                           # desplaza el sello
    from script_engine.gfx_literal_lock import lock
    ok, rej = lock(plan, {"pool.Q02": q["texto"], "pool.Q02.autor": q["autor"]}, chapter_number=5)
    assert ok["quote_card"] and not rej
    bad, rej2 = lock(plan, {"pool.Q02": "otra cosa"}, chapter_number=5)
    assert bad["quote_card"] is None and rej2[0]["block"] == "quote_card"


def test_nivel_de_agua_desde_un_reservado_de_altura():
    it = {"id": "D15", "texto": "Algunas partes quedaron bajo 15 pies (4.6 metros) de agua.", "tipo": "lugar"}
    pool = {"datos": [it], "citas": [], "cronologia": [], "lugares": [], "personajes": []}
    skel = {"chapters": [{"chapter_number": 3, "pantalla_ids": ["D15"], "evidence_ids": []}]}
    w = _words("El agua subía. Las celdas del primer piso quedaron bajo el agua.")
    wl = gk.reserved_water_level({"pool": pool, "skeleton_all": skel, "chapter_number": 3}, w)
    assert wl["value_text"] == "4.6" and wl["unit"] == "metros" and wl["pool_id"] == "D15"
    assert gk.reserved_water_level({"pool": pool, "skeleton_all": {"chapters": []}, "chapter_number": 3}, w) is None


def test_reloj_cambia_de_fecha_con_animacion():
    from script_engine.gfx_project import time_ticker_html
    from script_engine.gfx_literal_lock import lock
    crono = [{"id": "T05", "fecha": "2005-08-28", "hora": None, "evento": "El sheriff anuncia que no evacuará la prisión."},
             {"id": "T08", "fecha": "2005-08-29", "hora": None, "evento": "La energía eléctrica se pierde en la prisión."}]
    pool = {"cronologia": crono, "datos": [], "citas": [], "lugares": [], "personajes": []}
    skel = {"chapters": [{"chapter_number": 2, "evidence_ids": ["T05", "T08"]}]}
    w = _words("El 28 de agosto el sheriff anuncia que no evacuará la prisión. Pasan horas y horas sin noticias. "
               "El 29 de agosto la energía eléctrica se pierde en la prisión.")
    tk = gp.pool_ticker({"pool": pool, "skeleton_all": skel, "chapter_number": 2}, w, 60.0)
    assert (tk["day"], tk["month"]) == ("28", "AGO") and [(c["day"], c["pool_id"]) for c in tk["changes"]] == [("29", "T08")]
    assert tk["duration"] == round(tk["changes"][0]["t"] + gp.TICKER_HOLD - tk["start"], 3)
    html_, _, js = time_ticker_html(tk, 60.0)
    assert 'id="tk-d"' in html_ and any('"29 AGO"' in x for x in js)
    ok, _ = lock({"time_ticker": tk}, {"pool.T05": crono[0]["evento"]}, chapter_number=2)   # sin la fuente de T08
    assert ok["time_ticker"]["changes"] == []
