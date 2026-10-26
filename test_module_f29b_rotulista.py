"""
test_module_f29b_rotulista.py — F29b §A: el rotulista (script_engine/gfx_rotulista), sin red. Fixtures de Vajont ch03 y ch06
(oraciones, beats, ítems, palabras con tiempos y una respuesta cruda de Sonnet 5.5) en lab/hyperframes/f29b/fixtures/:
candado, no dicho y spoiler, `a_pantalla` con reintento, pico único (gana la escaleta) y el orden del final del plan (el
crítico después del respaldo). F29c cambió el prompt, el anclaje (palabra), los topes (1 por beat), la duración (lectura)
y la unidad del «no dicho» (oraciones vecinas): esos tests están en test_module_f29c_rotulista.py; acá quedan los de F29b
con el esquema nuevo.
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
        sents.append({"idx": k, "t0": ws[0]["start"], "t1": ws[-1]["end"], "texto": txt, "beat": 1})
    beats = beats or [{"n": 1, "funcion": "escalada", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "",
                       "datos_apoyo": []}]
    its = [{"a_pantalla": False, "por_que": "", "beats": [beats[0]["n"]], "kind": "datos", "fuente": "Fuente X, 2013",
            "autor": "", **x, "tipo": x["id"][0]} for x in items]
    return {"cap": 3, "titulo": "t", "oraciones": sents, "beats": beats, "items": its, "ya_mostrado": [],
            "pico": None, "voz_video": []}, words


def _b(si: int, tipo: str, texto: str, pid: str, et: str | None = None, aporta: str = "algo concreto",
       wi: int = 0) -> dict:
    """Un bloque con el esquema de F29c (§A.5): word_idx, rank, etiqueta."""
    return {"sentence_idx": si, "word_idx": wi, "beat": 1, "rank": 1, "tipo": tipo, "texto": texto, "etiqueta": et,
            "pool_id": pid, "aporta": aporta}


# ═══════════════ F29b con el esquema de F29c (el prompt literal y las reglas nuevas: test_module_f29c_rotulista) ═══════════════
def test_candado_cita_alterada_falla_y_literal_pasa():
    q = "Antes me parecía osado. Ahora lo considero una completa locura, y lo firmo."
    ent, words = _ent([(0, "Dal Piaz escribió una carta."), (10, "La obra siguió.")],
                      [{"id": "Q37", "texto": q, "kind": "citas", "autor": "Giorgio Dal Piaz"}])
    ok = gro.validar({"bloques": [_b(0, "cita", "«Ahora lo considero una completa locura»", "Q37")]}, ent, words)
    assert [b["pool_id"] for b in ok["bloques"]] == ["Q37"]
    mal = gro.validar({"bloques": [_b(0, "cita", "Ahora lo considero una locura total", "Q37")]}, ent, words)
    assert not mal["bloques"] and mal["rechazos"][0]["regla"] == "candado"


def test_candado_cifra_que_no_esta_en_la_fuente_falla():
    ent, words = _ent([(0, "La presa crece en la garganta."), (10, "Nadie mira.")],
                      [{"id": "D01", "texto": "La presa mide 261,6 metros de altura."}])
    v = gro.validar({"bloques": [_b(0, "cifra", "266 m", "D01", "Altura de la presa")]}, ent, words)
    assert not v["bloques"] and v["rechazos"][0]["regla"] == "candado"


def test_cifra_266_con_etiqueta_pasa_y_sin_etiqueta_falla():
    ent, words = _ent([(0, "La presa crece en la garganta."), (10, "Nadie mira.")],
                      [{"id": "D02", "texto": "La presa del Vajont tiene 266 metros de altura."}])
    ok = gro.validar({"bloques": [_b(0, "cifra", "266 m", "D02", "Altura de la presa")]}, ent, words)
    assert [(b["etiqueta"], b["pantalla"]) for b in ok["bloques"]] == [("Altura de la presa", "266 m")]
    sin = gro.validar({"bloques": [_b(0, "cifra", "266 m", "D02", None)]}, ent, words)
    assert not sin["bloques"] and sin["rechazos"][0]["motivo"] == "cifra sin etiqueta"


def test_nombre_propio_que_no_esta_en_la_fuente_falla():
    ent, words = _ent([(0, "Alguien firmó el acta."), (10, "Nadie mira.")],
                      [{"id": "T10", "texto": "El Consejo Superior de Obras Públicas aprobó el proyecto en 1943."}])
    ok = gro.validar({"bloques": [_b(0, "hecho", "Lo aprobó el Consejo Superior de Obras Públicas", "T10",
                                     "Acta del proyecto")]}, ent, words)
    assert ok["bloques"]
    mal = gro.validar({"bloques": [_b(0, "hecho", "Lo aprobó el ministro Rossi", "T10", "Acta del proyecto")]},
                      ent, words)
    assert not mal["bloques"] and "Rossi" in mal["rechazos"][0]["motivo"]


def test_no_dicho_1910_dicho_en_letras_en_la_oracion_siguiente_falla():
    ent, words = _ent([(0, "El recuento oficial llega días después."),
                       (12, "Fueron mil novecientas diez personas.")],
                      [{"id": "D128", "texto": "En el desastre murieron 1.910 personas."}])
    v = gro.validar({"bloques": [_b(0, "cifra", "1.910 personas", "D128", "Muertos")]}, ent, words)
    assert not v["bloques"] and v["rechazos"][0]["regla"] == "no_dicho"


def test_persona_el_nombre_lo_puede_decir_la_voz():
    ent, words = _ent([(0, "Giorgio Dal Piaz mira la ladera."), (10, "Nadie más la mira.")],
                      [{"id": "T27", "texto": "El geólogo Giorgio Dal Piaz revisó la ladera."}])
    v = gro.validar({"bloques": [_b(0, "persona", "Giorgio Dal Piaz", "T27", "geólogo")]}, ent, words)
    assert [b["pool_id"] for b in v["bloques"]] == ["T27"]


def test_a_pantalla_sin_la_cifra_en_liras_reintenta_y_despues_se_anota(tmp_path):
    ent, words = _ent([(0, "La justicia cierra el caso civil de la empresa."), (10, "La empresa paga.")],
                      [{"id": "D245", "texto": "En 1997 Montedison fue condenada a pagar 55.645 millones de liras.",
                        "a_pantalla": True, "por_que": "Condena a Montedison de 1997: cifra de liras en fallo, ilegible en voz."}])
    sin_cifra = {"bloques": [_b(0, "hecho", "La empresa fue condenada a pagar", "D245", "Fallo de la justicia")]}
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


def test_colocar_mapea_tipos_a_bloques_y_saca_lo_ya_mostrado():
    class Sc:
        def __init__(self, i, a, b):
            self.idx, self.start, self.end, self.quiet_side = i, a, b, "left"
    ent, words = _ent([(0, "La presa crece en la garganta."), (30, "La junta decide."), (60, "Nadie mira.")],
                      [{"id": "D02", "texto": "La presa del Vajont tiene 266 metros de altura."},
                       {"id": "T10", "texto": "El Consejo Superior de Obras Públicas aprobó el proyecto en 1943."},
                       {"id": "D03", "texto": "La obra de Erto costó mucho."}],
                      beats=[{"n": k, "funcion": "escalada", "t0": t, "t1": t + 29.0, "cierre": "", "dato_central": "",
                              "datos_apoyo": []} for k, t in ((1, 0.0), (2, 30.0), (3, 60.0))])
    for k, it in enumerate(ent["items"]):
        it["beats"] = [k + 1]
    for s in ent["oraciones"]:
        s["beat"] = s["idx"] + 1
    resp = {"bloques": [_b(0, "cifra", "266 m", "D02", "Altura de la presa"),
                        _b(1, "documento", "Lo aprobó el Consejo Superior de Obras Públicas", "T10", "Acta del proyecto"),
                        _b(2, "documento", "La obra de Erto costó mucho", "D03", "Informe de obra")]}
    res = {"final": resp, "modelo": "m"}
    plan = {"callouts": [{"text": "viejo"}], "archive_clippings": [{"headline": "viejo"}], "water_level": {"start": 1}}
    filas = gro.colocar(plan, res, ent, scenes=[Sc(0, 0, 100)], pool=None, used_before={"D03"}, lupa_box=None,
                        zoom_dur=2.85, log=[], words=words)
    assert [(c["kicker"], c["text"], c["ficha"]) for c in plan["callouts"]] == [("Altura de la presa", "266 m", True)]
    assert [a["headline"] for a in plan["archive_clippings"]] == ["Lo aprobó el Consejo Superior de Obras Públicas"]
    assert plan["water_level"] is None
    assert any(f["pool_id"] == "D03" and f["accion"] == "fuera" for f in filas)


def test_persona_nombre_y_cargo_tienen_que_estar_en_la_fuente():
    ent, words = _ent([(0, "Alguien mira la ladera."), (10, "Nadie más la mira.")],
                      [{"id": "T27", "texto": "El geólogo Giorgio Dal Piaz revisó la ladera."}])
    ok = gro.validar({"bloques": [_b(0, "persona", "Giorgio Dal Piaz", "T27", "geólogo")]}, ent, words)
    assert [b["pool_id"] for b in ok["bloques"]] == ["T27"]
    for txt, et, falta in (("Mario Bianchi", "geólogo", "Mario"), ("Pedro", "geólogo", "Pedro"),
                           ("Giorgio Dal Piaz", "ingeniero", "ingeniero")):
        v = gro.validar({"bloques": [_b(0, "persona", txt, "T27", et)]}, ent, words)
        assert not v["bloques"] and v["rechazos"][0]["regla"] == "candado" and falta in v["rechazos"][0]["motivo"]


# ═══════════════ anclaje ═══════════════

# ═══════════════ candado ═══════════════

# ═══════════════ no dicho y spoiler ═══════════════

# ═══════════════ topes ═══════════════

# ═══════════════ a_pantalla: reintento y nunca inventar ═══════════════

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


def test_rotulista_modelo_por_cli():
    """--rotulista-modelo cambia gfx_rules.rotulista_modelo (GfxRules es frozen: va por object.__setattr__)."""
    import ast
    src = (ROOT / "fase2b.py").read_text(encoding="utf-8")
    assert '"--rotulista-modelo"' in src and 'object.__setattr__(_gr, "rotulista_modelo"' in src
    ast.parse(src)


# ═══════════════ F29b, antes de B: candado de persona y tope en paralelo ═══════════════

def test_tope_cuenta_las_llamadas_en_vuelo(tmp_path, monkeypatch):
    import threading
    import time as _t
    import claude_helpers as hx
    entrar = threading.Barrier(3, timeout=5)
    soltar = threading.Event()

    def fake_post(body):
        soltar.wait(5)
        return {"content": [{"type": "text", "text": "{}"}], "usage": {"input_tokens": 10, "output_tokens": 10},
                "stop_reason": "end_turn", "model": "claude-sonnet-5-5"}
    monkeypatch.setattr(hx, "_post", fake_post)
    body = {"messages": [{"role": "user", "content": "x" * 100}]}
    peor = len(__import__("json").dumps(body)) / 2.5 / 1e6 * 2.0 + gro.OUT_TOKENS_PEOR / 1e6 * 10.0
    res = []

    def una(k):
        post = gro._post_con_registro(tmp_path, f"ch0{k}", "claude-sonnet-5-5", 2.5 * peor, [])
        entrar.wait()
        try:
            post(body)
            res.append("ok")
        except gro.TopeRotulista:
            res.append("tope")
    hs = [threading.Thread(target=una, args=(k,)) for k in range(3)]
    for h in hs:
        h.start()
    _t.sleep(0.5)
    soltar.set()
    for h in hs:
        h.join(5)
    assert sorted(res) == ["ok", "ok", "tope"]           # el ledger arranca en 0 para las 3: la 3.ª no entra
    assert gro._EN_VUELO.get(str(tmp_path.resolve())) == 0.0
