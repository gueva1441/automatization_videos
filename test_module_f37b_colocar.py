"""
test_module_f37b_colocar.py — F37 §B (HANDOFF_F37_papel_y_colocar): Fase 2 mueve en vez de cortar. Los tiempos de los
casos son los de Vajont medidos por el simulador (lab/hyperframes/f37/b/simulacion_previa.md), en un cap de juguete con
las mismas oraciones, cortes y beats.
    §B.1  un sello que cruza el corte se mueve: AVISO ch04 al inicio de la escena siguiente (intento 2), SILENCIO ch05
          a la oración siguiente del beat (intento 3); COLAPSO ch06 no tiene salida → sin colocar con cada intento;
    §B.1  el crítico re-juzga en la otra posición (el sello va a izquierda o derecha) y no tira a la primera; la ficha
          tiene una sola posición: sin paso 4;
    §B.1  una ficha que no entra en su oración (corte, lectura) se corre a la oración siguiente del beat (Q50 corta);
    §B.2  ninguna ficha dura más de callout_dur_max ni menos de callout_dur_min; la que pide más lectura no entra;
    §B.3  la lectura de una cita cuenta el autor una vez.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace as Sc

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gfx_config import gfx_rules  # noqa: E402
from script_engine import clima, pantalla_colocar as pc  # noqa: E402
from script_engine.voz_utils import oraciones  # noqa: E402


def _voz(frases: list[tuple[float, float, str]]) -> list[dict]:
    """Palabras con tiempos: cada frase (t0, t1, texto) reparte su tiempo entre sus palabras."""
    words = []
    for a, b, txt in frases:
        ws = txt.split()
        d = (b - a) / len(ws)
        words += [{"word": w, "start": round(a + i * d, 3), "end": round(a + (i + 1) * d - 0.02, 3)} for i, w in enumerate(ws)]
    return words


def _ent(words: list[dict], beats: list[tuple[int, float, float]]) -> dict:
    sents = oraciones(words)
    bs = [{"n": n, "funcion": "escalada", "t0": a, "t1": b, "cierre": "", "dato_central": "", "datos_apoyo": []}
          for n, a, b in beats]
    for s in sents:
        s["beat"] = next((b["n"] for b in bs if b["t0"] - 0.3 <= s["t0"] <= b["t1"]), bs[-1]["n"])
    return {"oraciones": sents, "beats": bs, "items": [], "voz_video": [s["texto"] for s in sents], "voz_antes": ""}


def _sellos(words, ent, scenes, sellos, juez=None, vocab=("AVISO", "SILENCIO", "COLAPSO", "RABIA"), monkeypatch=None):
    monkeypatch.setattr(clima, "vocabulario_clima", lambda: list(vocab))
    plan: dict = {"title_card": None}
    filas = clima.sellos_del_papel(plan, scenes, ent, words, 0.0, {}, [], sellos, juez=juez, usadas_video=set())
    return plan, filas


# ═══════════════════════ §B.1 sellos que cruzan el corte ═══════════════════════

def test_b1_aviso_ch04_se_mueve_al_inicio_de_la_escena_siguiente(monkeypatch):
    # oración [14] 87.98–92.6 (sin palabra de peso); la escena 7 corta en 88.03; la 8 arranca dentro de la oración
    words = _voz([(80.0, 87.9, "La cota autorizada fue de setecientos quince."),
                  (87.98, 92.6, "En noviembre la ladera ya se desplazaba más de un centímetro por día.")])
    ent = _ent(words, [(7, 80.0, 100.0)])
    scenes = [Sc(idx=7, start=60.0, end=88.03, quiet_side="right"), Sc(idx=8, start=88.03, end=120.0, quiet_side="right")]
    plan, filas = _sellos(words, ent, scenes, [{"palabra": "AVISO", "sentence_idx": 1}], monkeypatch=monkeypatch)
    e = plan["emphasis"][0]
    assert e["word"] == "AVISO" and e["start"] == 88.03 and e["intento"].startswith("2 · inicio de la escena 8")
    assert any(f["accion"] == "movido" and "cruza el corte" in f["motivo"] for f in filas)


def test_b1_silencio_ch05_se_mueve_a_la_oracion_siguiente_del_beat(monkeypatch):
    # oración [10] 71.66–72.9; la escena 7 corta en 74.13 (inicio + 2.5 s = 74.16 la cruza); la escena 8 arranca
    # después de la oración; la [11] (74.14) es del mismo beat
    words = _voz([(71.66, 72.9, "De la ola no hablaba nadie."),
                  (74.14, 79.0, "La respuesta que llegó desde un ministerio fue tranquila.")])
    ent = _ent(words, [(8, 60.0, 90.0)])
    scenes = [Sc(idx=7, start=50.0, end=74.13, quiet_side="left"), Sc(idx=8, start=74.13, end=95.0, quiet_side="left")]
    plan, filas = _sellos(words, ent, scenes, [{"palabra": "SILENCIO", "sentence_idx": 0}], monkeypatch=monkeypatch)
    e = plan["emphasis"][0]
    assert e["start"] == 74.14 and e["intento"].startswith("3 · oración siguiente [1]") and e["sentence_idx"] == 1


def test_b1_colapso_ch06_sin_salida_queda_sin_colocar_con_los_intentos(monkeypatch):
    # «Longarone ya no.» 111.16–112.16; corte de la escena 11 en 113.17; la 12 arranca después de la oración; la
    # oración siguiente es de otro beat
    words = _voz([(111.16, 112.16, "Longarone ya no."), (113.16, 118.0, "En la plaza quedó el barro hasta las rodillas.")])
    ent = _ent(words, [(10, 100.0, 112.5), (11, 113.0, 130.0)])
    scenes = [Sc(idx=11, start=100.0, end=113.17, quiet_side="right"), Sc(idx=12, start=113.17, end=130.0, quiet_side="right")]
    plan, filas = _sellos(words, ent, scenes, [{"palabra": "COLAPSO", "sentence_idx": 0}], monkeypatch=monkeypatch)
    assert plan["emphasis"] == []
    f = next(f for f in filas if f["texto"] == "COLAPSO")
    assert f["accion"] == "fuera" and f["regla"] == "colocar" and "no entra en ningún intento" in f["motivo"]
    assert f["intentos"] and all("cruza el corte" in x for x in f["intentos"])


# ═══════════════════════ §B.1 el crítico, en cada intento y en la otra posición ═══════════════════════

def test_b1_el_critico_rejuzga_en_el_otro_lado_y_no_tira_a_la_primera(monkeypatch):
    words = _voz([(10.0, 16.0, "Abajo en el pueblo la gente seguía su vida.")])
    ent = _ent(words, [(1, 0.0, 30.0)])
    scenes = [Sc(idx=1, start=0.0, end=30.0, quiet_side="right")]
    vistos: list[tuple[float, str]] = []

    def juez(em):
        vistos.append((em["start"], em["side"]))
        return {"pasa": em["side"] == "left", "motivo": "tapa rostros a la derecha", "mira": "foto sola",
                "veredicto": "estorba" if em["side"] == "right" else "no estorba"}
    plan, filas = _sellos(words, ent, scenes, [{"palabra": "RABIA", "sentence_idx": 0}], juez=juez,
                          monkeypatch=monkeypatch)
    e = plan["emphasis"][0]
    assert e["side"] == "left" and e["start"] == 10.0 and vistos == [(10.0, "right"), (10.0, "left")]
    assert "lado left" in e["intento"]
    assert pc.lados({"side": "left"}, "ficha") == ["left"]                    # la ficha: una sola posición (sin paso 4)


def test_b1_ficha_que_estorba_prueba_el_intento_siguiente_y_queda():
    plan = {"title_card": None,
            "callouts": [{"text": "13 de 34 presentes", "kicker": "SESIÓN", "ficha": True, "start": 24.6, "duration": 4.0,
                          "side": "left", "pool_id": "D117", "rotulista": True, "tipo_rotulista": "hecho",
                          "intentos": [{"t0": 24.6, "t1": 28.6, "si": 2, "como": "2 · inicio de la escena 2"},
                                       {"t0": 31.96, "t1": 35.96, "si": 3, "como": "3 · oración siguiente [3]"}]}]}
    words = _voz([(19.2, 31.0, "En mil novecientos cuarenta y tres se aprobó el proyecto."), (31.96, 36.0, "La empresa era SADE.")])
    ent = _ent(words, [(2, 0.0, 60.0)])
    scenes = [Sc(idx=2, start=24.6, end=31.5, quiet_side="right"), Sc(idx=3, start=31.5, end=60.0, quiet_side="right")]
    juez = lambda kind, b: {"pasa": b["start"] > 30, "motivo": "tapa el documento", "veredicto": "estorba", "t": b["start"]}
    filas = pc.repartir(plan, scenes, ent, [], juez=juez)
    c = plan["callouts"][0]
    assert c["start"] == 31.96 and c["sentence_idx"] == 3 and c["critico"]["estorba"] is False
    assert any(f["accion"] == "movido" and "estorba" in f["motivo"] for f in filas)


# ═══════════════════════ §B.1 la ficha que no cabe se corre a la oración siguiente ═══════════════════════

def test_b1_q50_corta_se_mueve_a_la_oracion_siguiente_si_no_cabe():
    from script_engine.pantalla_filtros import validar_papel
    words = _voz([(18.24, 27.0, "Desde el dos de octubre los avisos se multiplicaron en la ladera."),
                  (27.48, 33.0, "Las autoridades cerraron algunos caminos con barreras en Erto y Casso.")])
    ent = _ent(words, [(8, 10.0, 40.0)])
    ent["items"] = [{"id": "Q50", "a_pantalla": False, "por_que": "", "beats": [8], "tipo": "Q", "kind": "citas",
                     "texto": "en continua aprensión y en continua alarma", "fuente": "x",
                     "autor": "Administración de Erto y Casso", "gancho": False}]
    scenes = [Sc(idx=6, start=10.0, end=19.5, quiet_side="right"), Sc(idx=7, start=19.5, end=27.1, quiet_side="right"),
              Sc(idx=8, start=27.1, end=40.0, quiet_side="right")]      # la escena 8 arranca después de la oración
    b = {"pool_id": "Q50", "sentence_idx": 0, "word_idx": 4, "tipo": "cita", "etiqueta": "CARTA DE ERTO",
         "texto": "en continua aprensión y en continua alarma"}
    v = validar_papel([b], ent, words, 0.0, escenas=scenes)
    assert v["bloques"], v["rechazos"]
    q = v["bloques"][0]
    # F38e B1 (test editado): la palabra ancla (21.4) y el inicio de la oración (18.24) no dejan la lectura (6.0 s) antes
    # del corte de 27.1; hasta F38d la escalera saltaba a la oración siguiente (27.48). Ahora prueba también el inicio de
    # la escena 7 (19.5), que cae dentro de la oración ANTES del ancla: 19.5 + 6.0 = 25.5 < 27.1 → la cita se queda en
    # su oración, movida al corte; la oración siguiente queda como intento posterior.
    assert q["sentence_idx"] == 0 and q["t0"] == 19.5 and q["movido_corte"]
    assert q["intentos_fallidos"] and q["intentos"][0]["como"] == "2 · inicio de la escena 7"
    assert any(i["como"].startswith("3 · oración siguiente") and i["t0"] == 27.48 for i in q["intentos"][1:])


# ═══════════════════════ §B.2 duración de la ficha y §B.3 lectura de la cita ═══════════════════════

def test_b2_ninguna_ficha_dura_mas_de_callout_dur_max_ni_menos_de_callout_dur_min():
    mn, mx = float(gfx_rules.callout_dur_min), float(gfx_rules.callout_dur_max)
    for chars in (10, 39, 41, 60, 90):                 # T16 (39) y D131 (41) duraban 12.7 y 11.2 s
        t1, sin = pc.tiempos(100.0, chars, [Sc(idx=0, start=0.0, end=500.0)])
        assert sin is None and mn - 1e-9 <= t1 - 100.0 <= mx + 1e-9
    t1, sin = pc.tiempos(100.0, 39, [Sc(idx=0, start=0.0, end=500.0)])
    assert round(t1 - 100.0, 2) == 2.6                                      # T16: su lectura, no 12.7 s
    t1, sin = pc.tiempos(100.0, 127, [Sc(idx=0, start=0.0, end=500.0)])     # Q50 con 127: pide 8.5 s
    assert sin and "callout_dur_max" in sin
    t1, sin = pc.tiempos(100.0, 60, [Sc(idx=0, start=0.0, end=102.0)])      # nunca más allá del corte
    assert t1 == 102.0 and sin


def test_b3_la_lectura_de_la_cita_cuenta_el_autor_una_vez():
    et, txt, autor = "RESPUESTA DE LEONE", "Y justicia tendréis", "Giovanni Leone"
    n = pc.caracteres("cita", et, txt, autor)
    assert n == len(et) + len(f"«{txt}» — {autor}")                           # lo que se dibuja, una vez
    # el reparto ya no vuelve a contar: usa los intentos que trae el bloque (medidos con `caracteres`)
    plan = {"title_card": None, "callouts": [{"text": f"«{txt}» — {autor}", "kicker": et, "author": autor, "ficha": True,
                                              "start": 5.0, "duration": round(n / pc.LECTURA_CPS, 3), "side": "left",
                                              "pool_id": "Q14", "rotulista": True, "tipo_rotulista": "cita",
                                              "intentos": [{"t0": 5.0, "t1": round(5.0 + n / pc.LECTURA_CPS, 3), "si": 0,
                                                            "como": "1 · palabra ancla"}]}]}
    words = _voz([(4.0, 12.0, "El presidente respondió algo esa noche en la plaza.")])
    pc.repartir(plan, [Sc(idx=0, start=0.0, end=30.0, quiet_side="right")], _ent(words, [(1, 0.0, 30.0)]), [])
    assert plan["callouts"][0]["duration"] == round(n / pc.LECTURA_CPS, 3)


def test_b1_d47_la_oracion_siguiente_arranca_en_la_escena_que_empieza_dentro_de_ella():
    """F37 C (Vajont ch02 D47): la ancla deja 1.9 s antes del corte de 86.6; la oración siguiente arranca 0.1 s antes de
    ese corte: el intento 3 prueba también el inicio de la escena que arranca dentro de ella (como F32 §B.3)."""
    words = _voz([(79.5, 86.3, "En la década del cincuenta el geólogo Leopold Müller detectó en el Toc un gran desmoronamiento."),
                  (86.52, 95.0, "Y hubo otro hombre que caminó esa ladera con un martillo en la mano.")])
    ent = _ent(words, [(3, 70.0, 120.0)])
    scenes = [Sc(idx=8, start=70.0, end=79.6), Sc(idx=9, start=79.6, end=86.6), Sc(idx=10, start=86.6, end=110.0)]
    its = pc.instantes(ent["oraciones"], 0, scenes, ancla=84.7)
    assert [c for _, _, c in its][-1] == "3 · oración siguiente [1], inicio de la escena 10"
    t1, sin = pc.tiempos(86.6, 71, scenes)
    assert sin is None and round(t1 - 86.6, 2) == round(71 / pc.LECTURA_CPS, 2)


def test_c_el_reparto_ve_el_reloj_recortado_al_corte():
    """F37 C (Vajont ch07 T85): el reloj de 9 s cruzaba el corte de su escena; sin recortarlo antes del reparto, la ficha
    del pico chocaba con un tramo de reloj que ya no se ve."""
    words = _voz([(80.0, 90.0, "Pasaron más de cuatro años hasta que se depositó la resolución de remisión a juicio."),
                  (91.0, 96.0, "El juez no aceptó la palabra imprevisible.")])
    ent = _ent(words, [(12, 70.0, 110.0)])
    scenes = [Sc(idx=3, start=70.0, end=88.0, quiet_side="right"), Sc(idx=4, start=88.0, end=110.0, quiet_side="right")]
    plan = {"title_card": None, "time_ticker": {"day": "20", "month": "FEB", "start": 82.0, "duration": 9.0, "changes": []},
            "callouts": [{"text": "contra 11 personas", "kicker": "REMISIÓN A JUICIO", "ficha": True, "start": 88.5,
                          "duration": 2.5, "side": "left", "pool_id": "T85", "rotulista": True, "tipo_rotulista": "hecho",
                          "intentos": [{"t0": 88.5, "t1": 91.0, "si": 0, "como": "1 · palabra ancla"}]}]}
    sin = json.loads(json.dumps(plan))
    pc.repartir(sin, scenes, ent, [])
    # F38e B2 (test editado): el reparto recorta el reloj en su corte por sí mismo (el fin se mueve con el intento y se
    # corta en la escena): aun sin hasta_el_corte antes, el tramo del reloj termina en 88.0 y la ficha de 88.5 no choca
    # (hasta F38d chocaba con un tramo de reloj que ya no se veía).
    assert sin["callouts"] and sin["callouts"][0]["start"] == 88.5
    assert round(sin["time_ticker"]["start"] + sin["time_ticker"]["duration"], 3) == 88.0
    pc.hasta_el_corte(plan, scenes, 30.0, [])
    pc.repartir(plan, scenes, ent, [])
    assert plan["callouts"][0]["start"] == 88.5 and plan["rotulista"]["corte"]
    assert plan["time_ticker"]["duracion_plena"] == 9.0 and plan["time_ticker"]["start"] == 82.0   # no se movió
