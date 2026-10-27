"""
test_module_f38e_b.py — F38e B (HANDOFF_F38e_lo_que_rompe_cualquier_video §B; contrato REVISION_GUION_F38d §3 B1–B4).
    B1  `instantes` prueba todo inicio de escena dentro de la oración ancla, antes o después de la palabra ancla, en
        orden de tiempo, antes de pasar a la oración siguiente; una ficha que no entra en su ancla entra en el corte
        anterior de su propia oración (el patrón D47 de Vajont ch02, sintético).
    B2  el reloj mueve su fin con el intento: falla en su instante por solape y entra en el inicio de la escena
        siguiente con la duración completa; con hasta_el_corte antes (como gfx_layer), la duración plena se conserva y
        el nuevo corte lo recorta.
    B3  todo movido declara qué falló en cada intento anterior: un bloque movido al intento 3 tiene 2 fallas; las fallas
        de los filtros (`intentos_fallidos`) se suman en orden de escalera; el reloj movido también las declara.
    B4  pregunta de cierre desde la voz: (i) voz-pregunta, (ii) voz-alineada (empate: la más tardía; en orden; sin
        repetir), (iii) escaleta; y la tabla del analista sobre los 7 caps de Vajont (entradas congeladas de lab/).
Lee de lab/ o es sintético; nunca de data/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace as Sc

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import gfx_realizador as gr, pantalla_colocar as pc  # noqa: E402
from script_engine.gfx_pool import TICKER_MIN  # noqa: E402
from script_engine.voz_utils import oraciones  # noqa: E402

FASE1 = Path(__file__).resolve().parent / "lab" / "hyperframes" / "f38" / "b2" / "fase1" / "f8s3-vajont"


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


# ═══════════════════════ B1: todo inicio de escena dentro de la oración ancla ═══════════════════════

def test_b1_los_cortes_antes_y_despues_del_ancla_son_intentos_2_antes_de_la_oracion_siguiente():
    words = _voz([(79.5, 86.3, "En la década del cincuenta el geólogo Leopold Müller detectó en el Toc un gran desmoronamiento."),
                  (86.52, 95.0, "Y hubo otro hombre que caminó esa ladera con un martillo en la mano.")])
    ent = _ent(words, [(3, 70.0, 120.0)])
    scenes = [Sc(idx=1, start=70.0, end=79.6), Sc(idx=2, start=79.6, end=84.0), Sc(idx=3, start=84.0, end=90.0),
              Sc(idx=4, start=90.0, end=110.0)]
    its = pc.instantes(ent["oraciones"], 0, scenes, ancla=82.0)
    comos = [c for _, _, c in its]
    assert comos[:2] == ["1 · palabra ancla", "1 · inicio de la oración"]
    # los dos cortes que caen dentro de la oración, el de antes del ancla (79.6) y el de después (84.0), en orden de tiempo
    assert comos[2:4] == ["2 · inicio de la escena 2", "2 · inicio de la escena 3"]
    assert [t for t, _, _ in its][2:4] == [79.6, 84.0]
    assert comos[4].startswith("3 · oración siguiente [1]") and all(c.startswith("3 ·") for c in comos[4:])
    assert all(k == 0 for _, k, c in its if c.startswith(("1 ·", "2 ·")))


def test_b1_un_corte_fuera_de_la_oracion_no_es_intento_2():
    words = _voz([(10.0, 15.0, "Una oración corta con su ancla."), (15.3, 20.0, "Otra oración del mismo beat.")])
    ent = _ent(words, [(1, 0.0, 30.0)])
    scenes = [Sc(idx=0, start=0.0, end=9.9), Sc(idx=1, start=9.9, end=15.2), Sc(idx=2, start=15.2, end=30.0)]
    its = pc.instantes(ent["oraciones"], 0, scenes, ancla=12.0)
    assert not any(c.startswith("2 ·") for _, _, c in its)          # 9.9 y 15.2 caen fuera de [10.0, 15.0]
    assert any(c == "3 · oración siguiente [1]" for _, _, c in its)


def test_b1_la_ficha_que_no_entra_en_su_ancla_entra_en_el_corte_anterior_de_su_oracion():
    """El patrón D47 (Vajont ch02): la oración arranca 0.1 s antes de un corte y el ancla deja menos lectura que la
    ficha pide antes del corte siguiente; la escena que arranca dentro de la oración, antes del ancla, la recibe."""
    from script_engine.pantalla_filtros import validar_papel
    words = _voz([(79.5, 86.3, "En la década del cincuenta el geólogo Leopold Müller detectó en el Toc un gran desmoronamiento."),
                  (86.52, 95.0, "Y hubo otro hombre que caminó esa ladera con un martillo en la mano.")])
    ent = _ent(words, [(3, 70.0, 120.0)])
    ent["items"] = [{"id": "D47", "a_pantalla": False, "por_que": "", "beats": [3], "tipo": "D", "kind": "datos",
                     "texto": "Müller estimó un deslizamiento de 200 millones de metros cúbicos", "fuente": "x",
                     "autor": "", "gancho": False}]
    scenes = [Sc(idx=8, start=70.0, end=79.6, quiet_side="right"), Sc(idx=9, start=79.6, end=86.6, quiet_side="right"),
              Sc(idx=10, start=86.6, end=110.0, quiet_side="right")]
    b = {"pool_id": "D47", "sentence_idx": 0, "word_idx": 12, "tipo": "cifra", "etiqueta": "LO QUE MÜLLER ESTIMÓ",
         "texto": "200 millones de metros cúbicos de ladera en movimiento"}      # 20 + 55 = 75 car. → 5.0 s
    v = validar_papel([b], ent, words, 0.0, escenas=scenes)
    assert v["bloques"], v["rechazos"]
    d = v["bloques"][0]
    assert d["sentence_idx"] == 0 and d["t0"] == 79.6 and d["intentos"][0]["como"] == "2 · inicio de la escena 9"
    assert d["t1"] <= 86.6 and d["movido_corte"] and d["intentos_fallidos"]


# ═══════════════════════ B2: el reloj mueve su fin con el intento ═══════════════════════

def test_b2_el_reloj_que_choca_en_su_instante_entra_en_la_escena_siguiente_con_la_duracion_completa():
    words = _voz([(80.0, 87.0, "Antes de esa mañana nadie había escrito nada."),
                  (87.5, 96.0, "El nueve de octubre a la mañana, el director técnico se sentó a escribir una carta."),
                  (96.5, 105.0, "La carta llegó tarde.")])
    ent = _ent(words, [(8, 70.0, 120.0)])
    scenes = [Sc(idx=9, start=81.9, end=92.0, quiet_side="right"), Sc(idx=10, start=92.0, end=109.6, quiet_side="right")]
    plan = {"title_card": None,
            "archive_clippings": [{"headline": "recorte", "start": 85.0, "duration": 3.5, "rotulista": True,
                                   "pool_id": "D1", "tipo_rotulista": "documento",
                                   "intentos": [{"t0": 85.0, "t1": 88.5, "si": 0, "como": "1 · palabra ancla"}]}],
            "time_ticker": {"day": "9", "month": "OCT", "start": 87.52, "duration": 12.0, "changes": []}}
    filas = pc.repartir(plan, scenes, ent, [])
    tk = plan["time_ticker"]
    assert tk["start"] == 92.0 and tk["duration"] == 12.0 and tk["duracion_plena"] == 12.0   # fin = 104.0, no 99.52
    mov = next(f for f in filas if f.get("bloque") == "time_ticker" and f["accion"] == "movido")
    assert mov["intentos"] and "se solapa con recorte" in mov["intentos"][0] and "dura 12.00 s" in mov["motivo"]
    assert mov["motivo"].startswith("87.52 → 92.00 s (2 · inicio de la escena 10)")


def test_b2_con_hasta_el_corte_antes_el_reloj_corto_en_su_escena_se_mueve_entero_y_el_nuevo_corte_lo_recorta():
    """9 OCT de Vajont ch05, sintético: hasta_el_corte lo deja en 1.88 s (la escena 9 corta en 89.43); con el fin fijo
    todo intento «quedaría menos de 2 s»; ahora entra en la escena 10 con sus 12 s, y una escena más corta lo recorta."""
    words = _voz([(87.52, 96.0, "El nueve de octubre a la mañana, el director técnico se sentó a escribir una carta."),
                  (96.5, 105.0, "La carta llegó tarde.")])      # la oración arranca en la ancla: un solo intento 1
    ent = _ent(words, [(8, 70.0, 120.0)])
    log: list[str] = []
    for fin10, dur_esperada in ((109.6, 12.0), (95.0, round(95.0 - 89.43 - 1 / 30, 3))):
        scenes = [Sc(idx=9, start=81.9, end=89.43, quiet_side="right"), Sc(idx=10, start=89.43, end=fin10, quiet_side="right"),
                  Sc(idx=11, start=fin10, end=120.0, quiet_side="right")]
        plan = {"title_card": None, "time_ticker": {"day": "9", "month": "OCT", "start": 87.52, "duration": 12.0, "changes": []}}
        pc.hasta_el_corte(plan, scenes, 30.0, log)
        assert plan["time_ticker"]["duration"] < TICKER_MIN and plan["time_ticker"]["duracion_plena"] == 12.0
        filas = pc.repartir(plan, scenes, ent, log)
        tk = plan["time_ticker"]
        assert tk is not None and tk["start"] == 89.43 and tk["duration"] == dur_esperada
        mov = next(f for f in filas if f.get("bloque") == "time_ticker" and f["accion"] == "movido")
        assert mov["intentos"] == [f"1 · palabra ancla (87.52 s): quedaría menos de {TICKER_MIN} s (corta en 89.40 s)"]
        assert not plan["rotulista"]["corte"]                      # el recorte del instante viejo (87.52) ya no aplica
        pc.hasta_el_corte(plan, scenes, 30.0, log)                 # y después no hay nada más que acortar
        assert plan["time_ticker"]["duration"] == dur_esperada


# ═══════════════════════ B3: todo movido declara qué falló antes ═══════════════════════

def _juez_que_tira_en(ts: set[float]):
    def juez(kind, obj):
        t = round(float(obj["start"]), 2)
        mal = t in ts
        return {"t": t, "pasa": not mal, "veredicto": "estorba" if mal else "no estorba",
                "motivo": "tapa el texto de la carta" if mal else "no tapa nada"}
    return juez


def test_b3_un_bloque_movido_al_intento_3_declara_sus_2_fallas():
    words = _voz([(113.24, 121.0, "Biadene volvió al papel y agregó una posdata con las mediciones de esta mañana."),
                  (121.5, 128.0, "De veinte a treinta centímetros de avance."),
                  (128.16, 140.0, "Y algo más: pequeñas piedras caían en el borde del deslizamiento.")])
    ent = _ent(words, [(9, 100.0, 170.0)])
    scenes = [Sc(idx=12, start=113.27, end=128.2, quiet_side="right"), Sc(idx=13, start=128.2, end=143.0, quiet_side="right")]
    plan = {"title_card": None, "archive_clippings": [],
            "callouts": [{"text": "«Que Dios nos ayude» — Alberico Biadene", "kicker": "POSDATA", "ficha": True,
                          "start": 115.46, "duration": 4.333, "side": "left", "pool_id": "Q51", "rotulista": True,
                          "tipo_rotulista": "cita", "sentence_idx": 0,
                          "intentos": [{"t0": 115.46, "t1": 119.793, "si": 0, "como": "1 · palabra ancla"},
                                       {"t0": 121.86, "t1": 126.193, "si": 1, "como": "3 · oración siguiente [1]"},
                                       {"t0": 128.2, "t1": 132.533, "si": 2, "como": "3 · oración siguiente [2], inicio de la escena 13"}]}]}
    filas = pc.repartir(plan, scenes, ent, [], juez=_juez_que_tira_en({115.46, 121.86}))
    c = plan["callouts"][0]
    assert c["start"] == 128.2 and c["sentence_idx"] == 2
    mov = next(f for f in filas if f.get("pool_id") == "Q51" and f["accion"] == "movido")
    assert len(mov["intentos"]) == 2 and all("estorba — tapa el texto de la carta" in x for x in mov["intentos"])
    assert mov["intentos"][0].startswith("1 · palabra ancla (115.46 s)") and mov["intentos"][1].startswith("3 · oración siguiente [1] (121.86 s)")
    # lo que lee el guion de pantalla (gfx_guion: `movido_escena`) trae las fallas, no solo el destino
    assert c["movido_escena"].startswith("115.46 → 128.20 s (3 · oración siguiente [2], inicio de la escena 13) · antes: 1 · palabra ancla (115.46 s): estorba")
    assert c["intentos_fallidos"] == mov["intentos"] and mov["motivo"] == c["movido_escena"]


def test_b3_las_fallas_de_los_filtros_se_declaran_tambien_en_orden_de_escalera():
    words = _voz([(10.0, 16.0, "Una oración con una ancla adentro."), (16.5, 24.0, "Otra oración del mismo beat.")])
    ent = _ent(words, [(1, 0.0, 30.0)])
    scenes = [Sc(idx=0, start=0.0, end=14.0, quiet_side="right"), Sc(idx=1, start=14.0, end=30.0, quiet_side="right")]
    plan = {"title_card": None,
            "archive_clippings": [{"headline": "recorte", "start": 11.0, "duration": 2.5, "rotulista": True, "pool_id": "D1",
                                   "tipo_rotulista": "documento",       # 11.0–13.5: choca con 12.0, no toca a 14.0
                                   "intentos": [{"t0": 11.0, "t1": 13.5, "si": 0, "como": "1 · palabra ancla"}]}],
            "callouts": [{"text": "ficha", "kicker": "K", "ficha": True, "start": 12.0, "duration": 2.0, "side": "left",
                          "pool_id": "T1", "rotulista": True, "tipo_rotulista": "hecho", "sentence_idx": 0,
                          "intentos_fallidos": ["1 · inicio de la oración (10.00 s): sin tiempo de lectura: 60 caracteres piden 4.0 s y hay 4.0 s hasta el corte de escena (14.0 s)"],
                          "intentos": [{"t0": 12.0, "t1": 14.0, "si": 0, "como": "1 · palabra ancla"},
                                       {"t0": 14.0, "t1": 16.0, "si": 0, "como": "2 · inicio de la escena 1"}]}]}
    filas = pc.repartir(plan, scenes, ent, [])
    mov = next(f for f in filas if f.get("pool_id") == "T1" and f["accion"] == "movido")
    assert plan["callouts"][0]["start"] == 14.0
    assert [x.split(" (")[0] for x in mov["intentos"]] == ["1 · inicio de la oración", "1 · palabra ancla"]   # 10.0 antes que 12.0
    assert "sin tiempo de lectura" in mov["intentos"][0] and "se solapa con recorte" in mov["intentos"][1]
    assert pc.en_orden(["b (20.00 s): x", "a (3.50 s): y", "sin instante", "a (3.50 s): y"]) == ["a (3.50 s): y", "b (20.00 s): x", "sin instante"]


def test_b3_el_bloque_que_no_entra_en_nada_declara_tambien_lo_que_fallo_en_los_filtros():
    words = _voz([(10.0, 16.0, "Una oración con una ancla adentro."), (16.5, 24.0, "Otra oración del mismo beat.")])
    ent = _ent(words, [(1, 0.0, 30.0)])
    scenes = [Sc(idx=0, start=0.0, end=30.0, quiet_side="right")]
    plan = {"title_card": None,
            "archive_clippings": [{"headline": "recorte", "start": 11.0, "duration": 4.0, "rotulista": True, "pool_id": "D1",
                                   "tipo_rotulista": "documento",
                                   "intentos": [{"t0": 11.0, "t1": 15.0, "si": 0, "como": "1 · palabra ancla"}]}],
            "callouts": [{"text": "ficha", "kicker": "K", "ficha": True, "start": 12.0, "duration": 2.0, "side": "left",
                          "pool_id": "T1", "rotulista": True, "tipo_rotulista": "hecho", "sentence_idx": 0,
                          "intentos_fallidos": ["1 · inicio de la oración (10.00 s): sin tiempo de lectura: pide más"],
                          "intentos": [{"t0": 12.0, "t1": 14.0, "si": 0, "como": "1 · palabra ancla"}]}]}
    filas = pc.repartir(plan, scenes, ent, [])
    fuera = next(f for f in filas if f.get("pool_id") == "T1" and f["accion"] == "fuera")
    assert plan["callouts"] == [] and len(fuera["intentos"]) == 2 and fuera["intentos"][0].startswith("1 · inicio de la oración (10.00 s)")


# ═══════════════════════ B4: la pregunta de cierre desde la voz ═══════════════════════

def test_b4_i_la_ultima_oracion_de_la_voz_si_es_pregunta_es_el_texto():
    real = {"beats": [{"n": 12, "cierre": "El juez no aceptó la palabra imprevisible.",
                       "texto": "El juez pidió otra pericia y después nombres."},
                      {"n": 13, "cierre": "La sentencia dice inundación agravada por la previsión del evento. No dice quién decidió que Micaela siguiera durmiendo.",
                       "texto": "La sentencia habla de inundación agravada. Alguien decidió que Longarone no debía saber. ¿Quién decidió que Micaela siguiera durmiendo?"}]}
    assert gr.pregunta_cierre_fuente(real) == ("¿Quién decidió que Micaela siguiera durmiendo?", "voz-pregunta")
    assert gr.pregunta_cierre(real) == "¿Quién decidió que Micaela siguiera durmiendo?"
    real2 = {"beats": [{"n": 1, "cierre": "Algo.", "texto": "Y él preguntó: «¿quién lo decidió?»"}]}
    assert gr.pregunta_cierre_fuente(real2)[1] == "voz-pregunta"          # la comilla de cierre no tapa el «?»


def test_b4_ii_las_oraciones_de_la_voz_que_alinean_con_el_cierre_en_orden_sin_repetir_y_empate_a_la_mas_tardia():
    real = {"beats": [{"n": 1, "cierre": "", "texto": "El dique no cedió nunca en este beat anterior."},
                      {"n": 2, "cierre": "El dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él.",
                       "texto": "Longarone dormía. Pero el dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él. "
                                "Y para entender eso hay que volver atrás."}]}
    txt, fuente = gr.pregunta_cierre_fuente(real)
    assert fuente == "voz-alineada"
    assert txt == "Pero el dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él."
    # dos oraciones del cierre que alinean con la misma de la voz → una vez; empate → la más tardía
    real3 = {"beats": [{"n": 2, "cierre": "La montaña caminó primero. La montaña caminó otra vez.",
                        "texto": "Una montaña caminó primero en el embalse. Pasaron meses. Otra montaña caminó primero."}]}
    assert gr.pregunta_cierre_fuente(real3) == ("Otra montaña caminó primero.", "voz-alineada")
    # el orden es el de la voz, no el del cierre
    real4 = {"beats": [{"n": 2, "cierre": "La gente ya sabía qué pedirle. Tres días después llegó el presidente del Consejo.",
                        "texto": "Tres días después llegó el presidente del Consejo. La gente ya sabía qué pedirle."}]}
    assert gr.pregunta_cierre_fuente(real4)[0] == "Tres días después llegó el presidente del Consejo. La gente ya sabía qué pedirle."


def test_b4_iii_sin_oracion_alineada_queda_el_cierre_de_la_escaleta_y_sin_nada_none():
    real = {"beats": [{"n": 2, "cierre": "Algo totalmente distinto aquí.", "texto": "Hablamos de otras cosas ahora."}]}
    assert gr.pregunta_cierre_fuente(real) == ("Algo totalmente distinto aquí.", "escaleta")
    assert gr.pregunta_cierre_fuente({"beats": [{"n": 2, "cierre": "Pregunta de la escaleta.", "texto": ""}]}) == ("Pregunta de la escaleta.", "escaleta")
    assert gr.pregunta_cierre_fuente({"beats": []}) == (None, None)
    assert gr.pregunta_cierre_fuente({"beats": [{"n": 2, "cierre": "", "texto": "Voz sin pregunta."}]}) == (None, None)
    assert gr.pregunta_cierre({"beats": [{"n": 11, "cierre": "Como hasta F38d."}]}) == "Como hasta F38d."


def test_b4_vajont_los_7_caps_dan_lo_que_simulo_el_analista():
    esc = json.loads((FASE1 / "01a_escaleta.json").read_text(encoding="utf-8"))
    pars = json.loads((FASE1 / "01b_narracion_v3.json").read_text(encoding="utf-8"))["parrafos"]

    def real(cap: int) -> dict:
        bs = []
        for b in esc["beats"]:
            if int(b["cap"]) != cap:
                continue
            bs.append({"n": int(b["n"]), "cierre": str(b.get("cierre") or "").strip(),
                       "texto": " ".join(p["texto"] for p in pars if int(p["cap"]) == cap and int(p["beat"]) == int(b["n"]))})
        return {"beats": bs}
    assert gr.pregunta_cierre_fuente(real(1)) == (
        "Pero el dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él.", "voz-alineada")
    assert gr.pregunta_cierre_fuente(real(7)) == ("¿Quién decidió que Micaela siguiera durmiendo?", "voz-pregunta")
    from script_engine.voz_utils import oraciones_de_texto
    for cap, n in ((2, 1), (3, 1), (5, 1), (4, 2), (6, 2)):     # ch02, ch03, ch05 = su última oración; ch04, ch06 = sus dos últimas
        r = real(cap)
        voz = oraciones_de_texto(r["beats"][-1]["texto"])
        assert gr.pregunta_cierre_fuente(r) == (" ".join(voz[-n:]), "voz-alineada"), cap
