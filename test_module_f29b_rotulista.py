"""
test_module_f29b_rotulista.py — F29b §A: el rotulista (script_engine/gfx_rotulista), sin red. Fixtures de Vajont ch03 y ch06
(oraciones, beats, ítems, palabras con tiempos y una respuesta cruda de Sonnet 5.5) en lab/hyperframes/f29b/fixtures/:
prompt literal del handoff, anclaje, candado, no dicho y spoiler, topes, `a_pantalla` con reintento, pico único (gana la
escaleta) y el orden del final del plan (el crítico después del respaldo).
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from script_engine import gfx_rotulista as gro

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "lab" / "hyperframes" / "f29b" / "fixtures"
HANDOFF = ROOT / "lab" / "hyperframes" / "f29b" / "HANDOFF_F29b_rotulista.md"


def _fix(cap: str) -> tuple[dict, list[dict], dict]:
    f = json.loads((FIX / f"rotulista_{cap}_entrada.json").read_text(encoding="utf-8"))
    r = json.loads((FIX / f"rotulista_{cap}_respuesta.json").read_text(encoding="utf-8"))
    return f["entrada"], f["words"], r


def _w(texto: str, t0: float, paso: float = 0.4) -> list[dict]:
    """Palabras con tiempos (una cada `paso` s) desde t0."""
    return [{"word": w, "start": round(t0 + k * paso, 3), "end": round(t0 + k * paso + paso * 0.8, 3)}
            for k, w in enumerate(texto.split())]


def _ent(oraciones: list[tuple[float, str]], items: list[dict], beats: list[dict] | None = None) -> tuple[dict, list]:
    """Entrada mínima: oraciones [(t0, texto)] con sus palabras; un beat que cubre todo (o `beats`)."""
    words, sents = [], []
    for k, (t0, txt) in enumerate(oraciones):
        ws = _w(txt, t0)
        words += ws
        sents.append({"idx": k, "t0": ws[0]["start"], "t1": ws[-1]["end"], "texto": txt})
    beats = beats or [{"n": 1, "funcion": "escalada", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "",
                       "datos_apoyo": []}]
    its = [{"a_pantalla": False, "por_que": "", "beats": [beats[0]["n"]], "kind": "datos", "fuente": "Fuente X, 2013",
            "autor": "", **x, "tipo": x["id"][0]} for x in items]
    return {"cap": 3, "titulo": "t", "oraciones": sents, "beats": beats, "items": its, "ya_mostrado": [],
            "pico": None}, words


def _b(si: int, tipo: str, texto: str, pid: str, et: str | None = None, aporta: str = "algo concreto") -> dict:
    return {"sentence_idx": si, "tipo": tipo, "texto": texto, "etiqueta_o_kicker": et, "pool_id": pid, "aporta": aporta}


# ═══════════════ prompt literal ═══════════════

def test_prompt_literal_del_handoff():
    md = HANDOFF.read_text(encoding="utf-8")
    sys_ = re.search(r"\*\*SYSTEM:\*\*\s*```\n(.*?)\n```", md, re.S).group(1)
    usr = re.search(r"\*\*USER:\*\*\s*```\n(.*?)\n```", md, re.S).group(1)
    assert gro.ROTULISTA_SYSTEM == sys_
    assert gro.ROTULISTA_USER == usr
    ent, _, _ = _fix("ch06")
    u = gro.prompt_user(ent)
    assert "{" not in u.split("Devolvé:")[0]                      # todos los huecos llenos
    assert u.split("Devolvé:")[1] == usr.split("Devolvé:")[1]     # el formato de salida, intacto


# ═══════════════ anclaje ═══════════════

def test_anclaje_fin_de_oracion_y_ventana_del_beat():
    ent, words, r = _fix("ch06")
    v = gro.validar(r["respuesta"], ent, words)
    sents = {s["idx"]: s for s in ent["oraciones"]}
    assert v["bloques"]
    for b in v["bloques"]:
        assert b["t0"] == round(sents[b["sentence_idx"]]["t1"] + 0.3, 3)
        x = next(i for i in ent["items"] if i["id"] == b["pool_id"])
        assert any(bt["t0"] - 0.3 <= b["t0"] <= bt["t1"] + 0.35 for bt in ent["beats"] if bt["n"] in x["beats"])
    # la respuesta cruda pone D192 en la oración 19 (beat 10) y D192 es del beat 11 → fuera por la ventana
    assert any(x["pool_id"] == "D192" and x["regla"] == "A.4.1" for x in v["rechazos"])


def test_dur_por_texto():
    assert gro.duracion("Altura de la presa: 266 m") == pytest.approx(3.0)
    assert gro.duracion("uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince") == 6.0
    assert gro.duracion("x") == 2.5


# ═══════════════ candado ═══════════════

def test_candado_cita_alterada_falla_y_literal_pasa():
    q = "Antes me parecía osado. Ahora lo considero una completa locura, y lo firmo."
    ent, words = _ent([(0, "Dal Piaz escribió una carta."), (10, "La obra siguió.")],
                      [{"id": "Q37", "texto": q, "kind": "citas", "autor": "Giorgio Dal Piaz"}])
    ok = gro.validar({"bloques": [_b(0, "cita", "«Ahora lo considero una completa locura»", "Q37")]}, ent, words)
    assert [b["pool_id"] for b in ok["bloques"]] == ["Q37"]
    mal = gro.validar({"bloques": [_b(0, "cita", "Ahora lo considero una locura total", "Q37")]}, ent, words)
    assert not mal["bloques"] and mal["rechazos"][0]["regla"] == "A.4.3"


def test_candado_cifra_que_no_esta_en_la_fuente_falla():
    ent, words = _ent([(0, "La presa crece en la garganta."), (10, "Nadie mira.")],
                      [{"id": "D01", "texto": "La presa mide 261,6 metros de altura."}])
    v = gro.validar({"bloques": [_b(0, "cifra", "266 m", "D01", "Altura de la presa")]}, ent, words)
    assert not v["bloques"] and v["rechazos"][0]["regla"] == "A.4.3"


def test_cifra_266_con_etiqueta_pasa_y_sin_etiqueta_falla():
    ent, words = _ent([(0, "La presa crece en la garganta."), (10, "Nadie mira.")],
                      [{"id": "D02", "texto": "La presa del Vajont tiene 266 metros de altura."}])
    ok = gro.validar({"bloques": [_b(0, "cifra", "266 m", "D02", "Altura de la presa")]}, ent, words)
    assert [b["pantalla"] for b in ok["bloques"]] == ["Altura de la presa: 266 m"]
    sin = gro.validar({"bloques": [_b(0, "cifra", "266 m", "D02", None)]}, ent, words)
    assert not sin["bloques"] and sin["rechazos"][0]["motivo"] == "cifra sin etiqueta"


def test_nombre_propio_que_no_esta_en_la_fuente_falla():
    ent, words = _ent([(0, "Alguien firmó el acta."), (10, "Nadie mira.")],
                      [{"id": "T10", "texto": "El Consejo Superior de Obras Públicas aprobó el proyecto en 1943."}])
    ok = gro.validar({"bloques": [_b(0, "recorte", "Lo aprobó el Consejo Superior de Obras Públicas", "T10",
                                     "Fuente X, 2013")]}, ent, words)
    assert ok["bloques"]
    mal = gro.validar({"bloques": [_b(0, "recorte", "Lo aprobó el ministro Rossi", "T10", "Fuente X, 2013")]},
                      ent, words)
    assert not mal["bloques"] and "Rossi" in mal["rechazos"][0]["motivo"]


# ═══════════════ no dicho y spoiler ═══════════════

def test_no_dicho_1910_dicho_en_letras_a_20_s_falla():
    ent, words = _ent([(0, "El recuento oficial llega días después."),
                       (12, "Fueron mil novecientas diez personas.")],
                      [{"id": "D128", "texto": "En el desastre murieron 1.910 personas."}])
    v = gro.validar({"bloques": [_b(0, "cifra", "Murieron 1.910 personas", "D128", "Muertos")]}, ent, words)
    assert not v["bloques"] and v["rechazos"][0]["regla"] == "A.4.4"


def test_spoiler_longarone_75_s_despues_falla():
    ent, words = _ent([(0, "La ola sube por encima de la presa."), (40, "El agua baja por la garganta."),
                       (75, "Después llega a Longarone.")],
                      [{"id": "T58", "texto": "Una ola enorme pasó por encima de la presa y devastó Longarone."}])
    v = gro.validar({"bloques": [_b(0, "recorte", "La ola devastó Longarone", "T58", "Fuente X, 2013")]}, ent, words)
    assert not v["bloques"] and "spoiler" in v["rechazos"][0]["motivo"]


def test_persona_el_nombre_lo_puede_decir_la_voz():
    ent, words = _ent([(0, "Giorgio Dal Piaz mira la ladera."), (10, "Nadie más la mira.")],
                      [{"id": "T27", "texto": "El geólogo Giorgio Dal Piaz revisó la ladera."}])
    v = gro.validar({"bloques": [_b(0, "persona", "Giorgio Dal Piaz, geólogo", "T27")]}, ent, words)
    assert [b["pool_id"] for b in v["bloques"]] == ["T27"]


# ═══════════════ topes ═══════════════

def test_topes_5_por_cap_1_por_oracion_1_en_gancho():
    ors = [(k * 10.0, f"Oración número {k} de prueba sin cifras.") for k in range(8)]
    its = [{"id": f"D{k:02d}", "texto": f"El dato {k} dice que la obra de Erto fue enorme."} for k in range(8)]
    ent, words = _ent(ors, its)
    seis = {"bloques": [_b(k, "recorte", "La obra de Erto fue enorme", f"D{k:02d}", "Fuente X, 2013") for k in range(6)]}
    assert len(gro.validar(seis, ent, words)["bloques"]) == 5
    misma = {"bloques": [_b(0, "recorte", "La obra de Erto fue enorme", "D00", "Fuente X, 2013"),
                         _b(0, "recorte", "La obra de Erto fue enorme", "D01", "Fuente X, 2013")]}
    v = gro.validar(misma, ent, words)
    assert len(v["bloques"]) == 1 and v["rechazos"][0]["regla"] == "A.4.5"
    gancho = [{"n": 1, "funcion": "gancho", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ent_g, words_g = _ent(ors, its, beats=gancho)
    dos = {"bloques": [_b(k, "recorte", "La obra de Erto fue enorme", f"D{k:02d}", "Fuente X, 2013") for k in range(2)]}
    assert len(gro.validar(dos, ent_g, words_g)["bloques"]) == 1


# ═══════════════ a_pantalla: reintento y nunca inventar ═══════════════

def test_a_pantalla_sin_la_cifra_en_liras_reintenta_y_despues_se_anota(tmp_path):
    ent, words = _ent([(0, "La justicia cierra el caso civil."), (10, "La empresa paga.")],
                      [{"id": "D245", "texto": "En 1997 Montedison fue condenada a pagar 55.645 millones de liras.",
                        "a_pantalla": True, "por_que": "Condena a Montedison de 1997: cifra de liras en fallo, ilegible en voz."}])
    sin_cifra = {"bloques": [_b(0, "recorte", "La empresa fue condenada a pagar", "D245", "Fuente X, 2013")]}
    pedidos = []

    def call(prompt, system_instruction=None, description=None):
        pedidos.append(prompt)
        return copy.deepcopy(sin_cifra)
    r = gro.llamar(ent, words, 0.0, tmp_path, "ch07", call=call)
    assert len(pedidos) == 2                                       # un reintento, no más
    assert "D245" in pedidos[1] and "la cifra que pide el por_que" in pedidos[1]
    v = r["validacion"]
    assert v["incompletos"] == {"D245": "la cifra que pide el por_que"}            # anotado
    assert "liras" not in v["bloques"][0]["pantalla"] and not gro.numeros(v["bloques"][0]["pantalla"])  # no inventado


def test_respuesta_que_no_parsea_dos_veces_deja_el_cap_sin_bloques(tmp_path):
    ent, words = _ent([(0, "Nada.")], [{"id": "D01", "texto": "x"}])

    def call(prompt, system_instruction=None, description=None):
        raise ValueError("JSON inválido")
    r = gro.llamar(ent, words, 0.0, tmp_path, "ch01", call=call)
    assert r["validacion"] is None and len(r["intentos"]) == 2


def test_cruda_de_ch03_valida_y_el_reintento_queda_en_la_cruda():
    ent, words, r = _fix("ch03")
    v = gro.validar(r["respuesta"], ent, words)
    assert r["cruda"]["model"].startswith("claude-sonnet-5-5")
    assert all(not gro.munon(b["pantalla"]) for b in v["bloques"])
    assert all(b["tipo"] != "cifra" or b["etiqueta_o_kicker"] for b in v["bloques"])


# ═══════════════ pico único ═══════════════

def test_pico_unico_gana_la_escaleta():
    from script_engine.gfx_intensity import peak_sentence
    from script_engine.gfx_peak import sentences
    from script_engine.music_intensity import beat_pico_de_cap
    ent, words, _ = _fix("ch06")
    raw = json.loads((FIX / "gfx_intensity_ch06.json").read_text(encoding="utf-8"))["raw"]
    si_peak = peak_sentence({"intensidad": raw["intensidad"], "cargas": raw.get("cargas") or []})
    t_peak = sentences(words)[si_peak]["t0"]
    plan: dict = {}
    pk = gro.pico_plan(plan, ent, words=words, scenes=[], moods={}, intensity=None, time_offset=0.0, freq=None, log=[])
    assert pk["fuente"] == "escaleta.pico" and pk["beat"] == 10
    assert plan["pico"]["t"] == ent["pico"]["t"] != t_peak
    assert plan["pico"]["sentence_idx"] == ent["pico"]["sentence_idx"] != si_peak
    # la misma función que lee music_intensity
    assert beat_pico_de_cap([{"n": 10, "intensidad": 3}, {"n": 11, "intensidad": 5}], 10) == 10
    assert beat_pico_de_cap([{"n": 4, "intensidad": 3}, {"n": 5, "intensidad": 3}], 10) == 4


# ═══════════════ orden del final: el crítico después del respaldo ═══════════════

def test_orden_el_critico_juzga_lo_que_entra_por_respaldo(monkeypatch):
    from script_engine import gfx_realizador as gr
    vistos: list[list] = []

    def fake_pico(plan, real, pool, log, side="right"):
        plan.setdefault("callouts", []).append({"text": "respaldo", "start": 1.0, "pool_id": "X"})

    monkeypatch.setattr(gr, "garantizar_pico", fake_pico)
    monkeypatch.setattr(gr, "finalizar", lambda plan, real, log: [])
    plan: dict = {"callouts": [], "rotulista": {}}
    gr.cerrar(plan, {"beats": []}, None, [], criticar=lambda: vistos.append(list(plan["callouts"])), rotulista=True,
              garantizar=True)
    assert vistos == [[{"text": "respaldo", "start": 1.0, "pool_id": "X"}]]
    vistos.clear()
    plan = {"callouts": []}                                           # sin rotulista: el orden de F29 (v3)
    gr.cerrar(plan, {"beats": []}, None, [], criticar=lambda: vistos.append(list(plan["callouts"])), rotulista=False,
              garantizar=True)
    assert vistos == [[]] and plan["callouts"]


# ═══════════════ colocar ═══════════════

def test_colocar_mapea_tipos_a_bloques_y_saca_lo_ya_mostrado():
    class Sc:
        def __init__(self, i, a, b):
            self.idx, self.start, self.end, self.quiet_side = i, a, b, "left"
    ent, words = _ent([(0, "La presa crece en la garganta."), (30, "La junta decide."), (60, "Nadie mira.")],
                      [{"id": "D02", "texto": "La presa del Vajont tiene 266 metros de altura."},
                       {"id": "T10", "texto": "El Consejo Superior de Obras Públicas aprobó el proyecto en 1943."},
                       {"id": "D03", "texto": "La obra de Erto costó mucho."}])
    resp = {"bloques": [_b(0, "cifra", "266 m", "D02", "Altura de la presa"),
                        _b(1, "recorte", "Lo aprobó el Consejo Superior de Obras Públicas", "T10", "Fuente X, 2013"),
                        _b(2, "recorte", "La obra de Erto costó mucho", "D03", "Fuente X, 2013")]}
    res = {"validacion": gro.validar(resp, ent, words), "modelo": "m"}
    plan = {"callouts": [{"text": "viejo"}], "archive_clippings": [{"headline": "viejo"}], "water_level": {"start": 1}}
    filas = gro.colocar(plan, res, ent, scenes=[Sc(0, 0, 100)], pool=None, used_before={"D03"}, lupa_box=None,
                        zoom_dur=2.85, log=[])
    assert [c["text"] for c in plan["callouts"]] == ["Altura de la presa: 266 m"]
    assert plan["callouts"][0]["face"] == "anton" and plan["callouts"][0]["anim"] != "stamp"
    assert [a["headline"] for a in plan["archive_clippings"]] == ["Lo aprobó el Consejo Superior de Obras Públicas"]
    assert plan["water_level"] is None
    assert any(f["pool_id"] == "D03" and f["accion"] == "fuera" for f in filas)


def test_candado_literal_deja_pasar_los_bloques_del_rotulista():
    from script_engine.gfx_literal_lock import lock
    plan = {"callouts": [{"text": "Altura de la presa: 266 m", "rotulista": True}, {"text": "inventado"}],
            "archive_clippings": [{"kicker": "K", "headline": "redactado", "rotulista": True}]}
    ok, rej = lock(plan, {"x": "nada que ver"}, chapter_number=3)
    assert [c["text"] for c in ok["callouts"]] == ["Altura de la presa: 266 m"]
    assert len(ok["archive_clippings"]) == 1 and rej == [{"block": "data_callout", "field": "text", "text": "inventado"}]


def test_numeros_por_valor():
    assert gro.numero_en("1.910", "fueron mil novecientas diez")
    assert gro.numero_en("39", "son las diez y treinta y nueve")
    assert not gro.numero_en("1", "una fisura en la ladera")              # «una» es artículo
    assert gro.numeros("3 millones de metros") == ["3"]
