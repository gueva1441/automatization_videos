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
    from script_engine.clima import peak_word                        # F36 §A: vive en clima
    assert peak_word(peak, w, MOODS)["word"] == "cadáveres"


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
