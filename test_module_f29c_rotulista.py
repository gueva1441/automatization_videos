"""
test_module_f29c_rotulista.py — F29c §A.7: el rotulista por beat, sin red. Fixtures de Vajont ch06 (F29b) y las 4 crudas
de ch01 que no parseaban (lab/hyperframes/f29c/fixtures/): prompt literal del handoff F29c, 1 texto por beat y 0 en el
pico, arranque en la palabra, fin en la oración / la siguiente / el corte de escena, «sin tiempo de lectura», no dicho
por oraciones vecinas, spoiler por oración posterior, coherencia de cifras (720 vs 700/715), la ficha (= title card sin
#tc-dim), la ficha no convive con reloj ni title card, el primer JSON válido y D245 pasa el crítico.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from script_engine import gfx_rotulista as gro

ROOT = Path(__file__).resolve().parent
FIX_B = ROOT / "lab" / "hyperframes" / "f29b" / "fixtures"
FIX_C = ROOT / "lab" / "hyperframes" / "f29c" / "fixtures"
HANDOFF = ROOT / "lab" / "hyperframes" / "f29c" / "HANDOFF_F29c_rotulista_por_beat.md"


class Sc:
    def __init__(self, i: int, a: float, b: float):
        self.idx, self.start, self.end, self.quiet_side = i, a, b, "right"


def _ch06() -> tuple[dict, list[dict]]:
    f = json.loads((FIX_B / "rotulista_ch06_entrada.json").read_text(encoding="utf-8"))
    return f["entrada"], f["words"]


def _w(texto: str, t0: float, paso: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(t0 + k * paso, 3), "end": round(t0 + k * paso + paso * 0.8, 3)}
            for k, w in enumerate(texto.split())]


def _ent(oraciones: list[tuple[float, str]], items: list[dict], beats: list[dict] | None = None,
         pico: dict | None = None, voz_video: list[str] | None = None) -> tuple[dict, list]:
    words = []
    for t0, txt in oraciones:
        words += _w(txt, t0)
    beats = beats or [{"n": 1, "funcion": "escalada", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "",
                       "datos_apoyo": []}]
    its = [{"a_pantalla": False, "por_que": "", "beats": [beats[0]["n"]], "kind": "datos", "fuente": "Fuente X, 2013",
            "autor": "", **x, "tipo": x["id"][0]} for x in items]
    ent = {"cap": 3, "titulo": "t", "oraciones": gro.oraciones(words), "beats": beats, "items": its,
           "ya_mostrado": [], "pico": pico, "voz_video": voz_video or []}
    for s in ent["oraciones"]:
        s["beat"] = gro.beat_de_oracion(s, beats)
    return ent, words


def _b(si: int, tipo: str, texto: str, pid: str, et: str | None = None, wi: int = 0, rank: int = 1,
       aporta: str = "algo concreto") -> dict:
    return {"sentence_idx": si, "word_idx": wi, "beat": 0, "rank": rank, "tipo": tipo, "etiqueta": et, "texto": texto,
            "pool_id": pid, "aporta": aporta}


# ═══════════════ prompt literal (A.5) ═══════════════

def test_prompt_literal_del_handoff_f29c():
    md = HANDOFF.read_text(encoding="utf-8")
    sys_ = re.search(r"\*\*SYSTEM:\*\*\s*```\n(.*?)\n```", md, re.S).group(1)
    usr = re.search(r"\*\*USER:\*\*\s*```\n(.*?)\n```", md, re.S).group(1)
    # F32 §B.7: el de F29c queda como ROTULISTA_SYSTEM_F29C; el de hoy suma una línea (test_module_f32)
    assert gro.ROTULISTA_SYSTEM_F29C == sys_ and gro.ROTULISTA_USER == usr
    assert gro.prompt_md5() == "c9231e24afbc785d5870b33088ce076e"
    ent, words = _ch06()
    ent = {**ent, "oraciones": gro.oraciones(words)}
    for s in ent["oraciones"]:
        s["beat"] = gro.beat_de_oracion(s, ent["beats"])
    u = gro.prompt_user(ent)
    assert "{" not in u.split("Devolvé:")[0]                        # todos los huecos llenos
    assert u.split("Devolvé:")[1] == usr.split("Devolvé:")[1]       # el formato de salida, intacto
    assert "el pico es el beat 10:" in u and "[21] 110.2–112.4 · beat 11 · 0:Donde 1:había" in u


# ═══════════════ A.1: 1 por beat, 0 en el pico ═══════════════

def test_ch06_d128_y_d192_en_respiro_uno_por_beat_y_el_del_pico_sale():
    ent, words = _ch06()
    resp = {"bloques": [
        _b(21, "cifra", "1.910 personas", "D128", "Muertos en el desastre"),
        _b(24, "cifra", "20 técnicos", "D192", "Muertos en el estribo", rank=1),
        _b(13, "hecho", "La segunda ola golpeó tras superar la presa", "D124", "Crónica del desastre")]}
    v = gro.validar(resp, ent, words)
    fuera = {r["pool_id"]: r for r in v["rechazos"]}
    assert fuera["D124"]["regla"] == "cantidad" and "beat pico" in fuera["D124"]["motivo"]
    # F32 §B.5: D128 y D192 (los dos `a_pantalla`) quedan en respiro; las escenas distintas las pone escena_final
    assert [b["pool_id"] for b in v["bloques"]] == ["D128", "D192"] and {b["beat"] for b in v["bloques"]} == {11}
    assert "D192" not in fuera and not v["faltan"]


def test_a_pantalla_del_beat_pico_queda_en_el_pico_f32():
    """F32 §B.5 (§0): un `a_pantalla` puede ir en el beat pico, así que ya no se mueve al beat siguiente; D192 es del
    beat 11, y anclado en el 10 sale por anclaje como cualquier dato fuera de su beat (el caso del pico, en f32)."""
    ent, words = _ch06()
    v = gro.validar({"bloques": [_b(19, "cifra", "20 técnicos", "D192", "Muertos en el estribo", wi=3)]}, ent, words)
    assert not v["bloques"] and v["rechazos"][0]["regla"] == "anclaje" and "beat 10" in v["rechazos"][0]["motivo"]


def test_gancho_a_lo_sumo_uno():
    gancho = [{"n": 1, "funcion": "gancho", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ors = [(k * 10.0, f"Oración número {k} de prueba sin cifras.") for k in range(3)]
    its = [{"id": f"D{k:02d}", "texto": f"El dato {k} dice que la obra de Erto fue enorme."} for k in range(3)]
    ent, words = _ent(ors, its, beats=gancho)
    v = gro.validar({"bloques": [_b(k, "hecho", "La obra de Erto fue enorme", f"D{k:02d}", "Fuente X, 2013", rank=k + 1)
                                 for k in range(3)]}, ent, words)
    assert [b["pool_id"] for b in v["bloques"]] == ["D00"]


# ═══════════════ A.2: arranque y fin ═══════════════

def test_arranque_en_la_palabra_word_idx():
    ent, words = _ent([(0, "La comisión aprobó el proyecto ese mismo invierno."), (10, "Nadie protestó.")],
                      [{"id": "T10", "texto": "El acta fue aprobada con 13 de 34 presentes."}])
    v = gro.validar({"bloques": [_b(0, "hecho", "Aprobada con 13 de 34 presentes", "T10", "Fuente X, 2013", wi=2)]},
                    ent, words)
    b = v["bloques"][0]
    assert b["t0"] == words[2]["start"] and b["palabra"] == "aprobó"


def test_fin_en_la_oracion_en_la_siguiente_y_en_el_corte_de_escena():
    larga = "La comisión aprobó el proyecto de la presa en una reunión del invierno de aquel año."
    ent, words = _ent([(0, larga), (10, "Nadie protestó en la sala."), (20, "Y la obra siguió.")],
                      [{"id": "T10", "texto": "El acta fue aprobada con 13 de 34 presentes."}])
    b13 = _b(0, "hecho", "Aprobada con 13 de 34 presentes", "T10", "Fuente X, 2013", wi=2)
    v = gro.validar({"bloques": [b13]}, ent, words)
    assert v["bloques"][0]["t1"] == gro.oraciones(words)[0]["t1"]                     # alcanza: fin de la oración
    b_tarde = {**b13, "word_idx": 15}                                                 # «año.»: no alcanza
    v = gro.validar({"bloques": [b_tarde]}, ent, words)
    assert v["bloques"][0]["t1"] == gro.oraciones(words)[1]["t1"]                     # → fin de la siguiente
    v = gro.validar({"bloques": [b13]}, ent, words, escenas=[Sc(0, 0.0, 4.5), Sc(1, 4.5, 40.0)])
    assert v["bloques"][0]["t1"] == 4.5                                               # muere en el corte


def test_sin_tiempo_de_lectura_no_va_y_no_se_acorta():
    ent, words = _ent([(0, "La comisión aprobó el proyecto."), (10, "Nadie protestó.")],
                      [{"id": "T10", "texto": "El acta fue aprobada con 13 de 34 presentes."}])
    b = _b(0, "hecho", "Aprobada con 13 de 34 presentes", "T10", "Acta del consejo", wi=2)
    # F32 §B.3: tampoco cabe en la escena siguiente (0.5 s) → sin tiempo de lectura
    v = gro.validar({"bloques": [b]}, ent, words, escenas=[Sc(0, 0.0, 1.5), Sc(1, 1.5, 2.0), Sc(2, 2.0, 40.0)])
    assert not v["bloques"] and v["rechazos"][0]["regla"] == "lectura"
    assert "sin tiempo de lectura" in v["rechazos"][0]["motivo"] and "corte de escena" in v["rechazos"][0]["motivo"]


# ═══════════════ A.3: no dicho por vecinas, spoiler por posterior ═══════════════

def test_no_dicho_oracion_vecina_y_lejana():
    its = [{"id": "D128", "texto": "En el desastre murieron 1.910 personas."}]
    ors = [(0, "Fueron mil novecientas diez personas."), (10, "El recuento oficial llega días después."),
           (20, "La lista se cierra.")]
    ent, words = _ent(ors, its)
    b = _b(1, "cifra", "1.910 personas", "D128", "Muertos en el desastre")
    v = gro.validar({"bloques": [b]}, ent, words)
    assert not v["bloques"] and v["rechazos"][0]["regla"] == "no_dicho"              # la oración anterior lo dice
    ors2 = [(0, "Fueron mil novecientas diez personas."), (5, "Otra cosa pasa."), (10, "El recuento llega."),
            (20, "La lista se cierra.")]
    ent2, words2 = _ent(ors2, its)
    v2 = gro.validar({"bloques": [{**b, "sentence_idx": 2}]}, ent2, words2)
    assert [x["pool_id"] for x in v2["bloques"]] == ["D128"]                         # dos oraciones antes: no cuenta


def test_spoiler_oracion_posterior_del_cap():
    ent, words = _ent([(0, "La ola sube por encima de la presa."), (10, "El agua baja por la garganta."),
                       (20, "Nada se oye."), (75, "Después llega a Longarone.")],
                      [{"id": "T58", "texto": "Una ola enorme pasó por encima de la presa y devastó Longarone."}])
    v = gro.validar({"bloques": [_b(0, "hecho", "La ola devastó Longarone", "T58", "Fuente X, 2013")]}, ent, words)
    assert not v["bloques"] and v["rechazos"][0]["regla"] == "spoiler"


# ═══════════════ A.4: coherencia de cifras ═══════════════

def test_coherencia_720_contra_700_y_715_de_la_voz_del_video():
    voz = ["La recomendación que salió de ahí fue no pasar de los setecientos metros sobre el nivel del mar.",
           "La cota autorizada fue de setecientos quince.",
           "En junio de mil novecientos sesenta y tres el agua llegó a los setecientos metros.",
           "Ese marzo, una masa de roca entró al agua y levantó una ola de veinte metros."]
    assert any("720 m vs 700 m" in c for c in gro.contradicciones("Nivel del embalse 720 m", voz))
    assert any("720 m vs 715" in c for c in gro.contradicciones("Nivel del embalse 720 m", voz))
    assert not any("vs 20 m" in c for c in gro.contradicciones("Nivel del embalse 720 m", voz))   # otra magnitud
    assert gro.contradicciones("Nivel del embalse 700 m", voz[:1]) == []
    assert gro.contradicciones("Altura de la presa: 261 m", voz[:2]) == []          # otra magnitud nombrada
    assert gro.contradicciones("15 metros por encima de la cota de seguridad", voz) == []   # una diferencia
    assert gro.contradicciones("Pagar a Longarone 55.645.758.500 liras",
                               ["ENEL ofreció diez mil millones de liras de la época como indemnización."]) == []
    ent, words = _ent([(0, "El agua seguía subiendo en el embalse."), (10, "Nadie miraba.")],
                      [{"id": "T50", "texto": "El embalse llegó a 720 metros, cinco por encima de la cota autorizada."}],
                      voz_video=voz)
    v = gro.validar({"bloques": [_b(0, "cifra", "720 m", "T50", "Nivel del embalse")]}, ent, words)
    assert not v["bloques"] and v["rechazos"][0]["regla"] == "coherencia"
    assert "contradice la voz" in v["rechazos"][0]["motivo"]


# ═══════════════ A.5: la ficha ═══════════════

def test_ficha_es_el_title_card_con_kicker_y_titulo_y_sin_tc_dim(tmp_path):
    from script_engine.gfx_project import ficha_html, ficha_medida, write_project
    html_, init, js = ficha_html("fc0", {"text": "Giorgio Dal Piaz", "kicker": "geólogo"}, 12.0, 3.0, 2560)
    assert 'id="fc0-kicker" class="tc-kicker">GEÓLOGO<' in html_ and "Giorgio Dal Piaz" in html_
    assert "tc-dim" not in html_ and 'class="clip tc-box ficha" data-start="12.000" data-duration="3.000"' in html_
    assert "#fc0-title span" in init[0] and '"#fc0", { opacity: 0, duration: 0.4' in js[0]
    assert ficha_medida("ANCHO DE LA FISURA", "Más de 1 metro") == {"kicker": 1, "title": 1}
    assert ficha_medida("x", "Aprobada con solo 13 de 34 representantes presentes en la sala")["title"] == 2
    # el title card sigue con su #tc-dim
    from script_engine.gfx_project import GfxScene
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "base.mp4").write_bytes(b"")
    plan = {"title_card": {"kicker": "CAPÍTULO 3", "title": "La fisura"},
            "callouts": [{"text": "Más de 1 metro", "kicker": "Ancho de la fisura", "ficha": True, "start": 8.0,
                          "duration": 3.0, "side": "left"}]}
    sc = [GfxScene(idx=0, start=0.0, end=20.0, rank="R2")]
    write_project(plan, sc, tmp_path, duration=20.0, width=2560, height=1440, fps=30, grade=False)
    idx = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert idx.count('id="tc-dim"') == 1 and 'id="fc0"' in idx and "ANCHO DE LA FISURA" in idx


def test_ficha_no_convive_con_reloj_ni_con_title_card():
    ent, words = _ent([(0, "Arranca el capítulo con su título."), (5, "La comisión aprobó el proyecto ese invierno."),
                       (12, "Después la obra siguió por meses en la garganta."), (20, "Nadie protestó.")],
                      [{"id": "T10", "texto": "x"}])
    scenes = [Sc(0, 0.0, 9.0), Sc(1, 9.0, 18.0), Sc(2, 18.0, 30.0)]
    plan = {"title_card": {"kicker": "CAPÍTULO 3", "title": "t"},
            "callouts": [{"text": "Aprobada con 13", "kicker": "Acta", "ficha": True, "start": 5.5, "duration": 2.0,
                          "t1": 7.5, "pool_id": "T10", "tipo_rotulista": "hecho", "rotulista": True}]}
    filas = gro.escena_final(plan, scenes, ent, [])
    c = plan["callouts"][0]
    assert c["start"] == 9.0 and c["start"] + c["duration"] <= 18.0                 # espera a la escena siguiente
    assert any(f["accion"] == "movido" and "title card" in f["motivo"] for f in filas)
    plan2 = {"time_ticker": {"day": "9", "month": "OCT", "start": 9.5, "duration": 12.0, "changes": []},
             "callouts": [{"text": "Aprobada con 13", "kicker": "Acta", "ficha": True, "start": 12.0, "duration": 2.0,
                           "pool_id": "T10", "tipo_rotulista": "hecho", "rotulista": True}]}
    filas2 = gro.escena_final(plan2, scenes, ent, [])
    assert plan2["callouts"] == [] and plan2["time_ticker"]                           # el reloj cubre el resto del beat
    assert any(f["regla"] == "zona" and f["accion"] == "fuera" and "reloj" in f["motivo"] for f in filas2)


def test_reloj_no_va_encima_de_un_recorte_y_arranca_en_la_escena_siguiente_del_beat():
    ent, words = _ent([(0, "Uno dos tres."), (10, "Cuatro cinco seis.")], [{"id": "D1", "texto": "x"}])
    scenes = [Sc(0, 0.0, 9.0), Sc(1, 9.0, 18.0), Sc(2, 18.0, 30.0)]
    plan = {"archive_clippings": [{"headline": "h", "start": 2.0, "duration": 3.0, "rotulista": True, "pool_id": "D1"}],
            "time_ticker": {"day": "9", "month": "OCT", "start": 3.0, "duration": 12.0, "changes": []}}
    gro.escena_final(plan, scenes, ent, [])
    assert plan["time_ticker"]["start"] == 9.0 and plan["time_ticker"]["duration"] == 6.0


# ═══════════════ A.6.1: el primer JSON válido ═══════════════

def test_las_4_crudas_de_ch01_parsean_con_el_primer_json(tmp_path, monkeypatch):
    crudas = json.loads((FIX_C / "rotulista_ch01_crudas_fallidas.json").read_text(encoding="utf-8"))["crudas"]
    assert len(crudas) == 4
    for c in crudas:
        try:
            json.loads(c["texto"])
            raise AssertionError("debía fallar con json.loads")
        except json.JSONDecodeError:
            pass
        assert isinstance(gro.primer_json(c["texto"])["bloques"], list)
    import claude_helpers as hx
    monkeypatch.setattr(hx, "_post", lambda body: {"content": [{"type": "text", "text": crudas[1]["texto"]}],
                                                   "usage": {"input_tokens": 10, "output_tokens": 10},
                                                   "stop_reason": "end_turn", "model": "claude-sonnet-5-5"})
    llamadas = []
    post = gro._post_con_registro(tmp_path, "ch01", "claude-sonnet-5-5", 2.0, llamadas)
    out = hx.call_json("x", model="claude-sonnet-5-5", post=post, description="test")
    assert "bloques" in out and len(llamadas) == 1                                  # una sola llamada, sin reintento
    assert gro.primer_json("sin json") is None


# ═══════════════ A.6.2: D245 pasa el crítico ═══════════════

def test_d245_a_pantalla_no_lo_corta_la_pregunta_1(tmp_path):
    from script_engine.gfx_critic import criticize_rotulista, pasa_rot
    plan = {"callouts": [
        {"text": "55.645.758.500 liras", "kicker": "Condena a Montedison, 1997", "ficha": True, "start": 10.0,
         "duration": 4.0, "rotulista": True, "pool_id": "D245", "a_pantalla": True, "aporta": "la cifra en liras",
         "por_que": "Condena a Montedison de 1997: cifra de liras en fallo, ilegible en voz.", "sentence_idx": 0},
        {"text": "Otra cosa", "kicker": "K", "ficha": True, "start": 20.0, "duration": 3.0, "rotulista": True,
         "pool_id": "D9", "a_pantalla": False, "aporta": "algo", "sentence_idx": 1}]}
    words = _w("La justicia cierra el caso. La empresa paga.", 9.0)
    vistos = []

    def call(img, prompt, *rest):
        vistos.append(prompt)
        return {"habla_de_eso": False, "motivo_1": "habla de ENEL", "dice_algo_nuevo": True, "motivo_2": "la cifra",
                "estorba": False, "motivo_3": "no tapa"}
    img = tmp_path / "f.jpg"
    from PIL import Image
    Image.new("RGB", (8, 8)).save(img)
    rows = criticize_rotulista(plan, base=tmp_path / "no.mp4", words=words, time_offset=0.0, work_dir=tmp_path,
                               cap="ch07", log=[], call=call, snaps={11.0: img, 21.0: img})
    assert [c["pool_id"] for c in plan["callouts"]] == ["D245"]                      # el otro sale por (1)
    assert [r["pasa"] for r in rows] == [True, False]
    assert "SE PIDIÓ PARA PANTALLA" in vistos[0] and "SE PIDIÓ" not in vistos[1]
    assert not pasa_rot({"habla_de_eso": True, "dice_algo_nuevo": True, "estorba": True}, True)    # estorba: sale
    assert not pasa_rot({"habla_de_eso": True, "dice_algo_nuevo": False, "estorba": False}, True)  # (2): sale
