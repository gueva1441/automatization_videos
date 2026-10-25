"""
test_module_f27.py — F27 §A: (1) gemini_helpers: una respuesta sin texto es un fallo de parseo (se re-llama; si sigue
vacía, el ValueError de siempre con «respuesta vacía» y el motivo); m03 atrapa ese ValueError por imagen y la imagen
sigue por el backstop; (2) reparación (e): se quita el nombre y la oración se queda; (3) el editor m01c fuera del
camino v4 (solo con editor=True); (4) PALABRAS_POR_SEG 2.4. Sin red.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import gemini_helpers as gh
from script_engine import guion_v4 as g4
from script_engine import m03_visual as mv


# ── (1) gemini_helpers ──

def test_respuesta_vacia_tres_veces_es_el_valueerror_de_siempre(monkeypatch):
    monkeypatch.setattr(gh, "_dump_invalid_json", lambda *a, **k: "")
    vistos = []
    with pytest.raises(ValueError, match="respuesta vacía"):
        gh._parse_with_retry(lambda: vistos.append(1) or None)
    assert len(vistos) == gh.PARSE_MAX_ATTEMPTS


def test_respuesta_vacia_y_despues_json_valido():
    xs = iter([None, "  ", '{"a": 1}'])
    assert gh._parse_with_retry(lambda: next(xs)) == {"a": 1}


def test_el_motivo_va_al_log_y_al_error(monkeypatch, capsys):
    vistos = {}
    monkeypatch.setattr(gh, "_dump_invalid_json", lambda r, t, e, motivo=None: vistos.setdefault("m", motivo) and "")
    resp = SimpleNamespace(text=None, candidates=[SimpleNamespace(finish_reason=SimpleNamespace(name="SAFETY"))],
                           prompt_feedback=SimpleNamespace(block_reason=None))
    with pytest.raises(ValueError) as ei:
        gh._parse_with_retry(lambda: gh._texto(resp, "m03:fluidificador"))
    assert "finish_reason=SAFETY" in str(ei.value) and vistos["m"] == "finish_reason=SAFETY"
    assert "respuesta vacía (finish_reason=SAFETY) en m03:fluidificador" in capsys.readouterr().out
    ok = SimpleNamespace(text='{"x": 2}', candidates=[], prompt_feedback=None)
    assert gh._parse_with_retry(lambda: gh._texto(ok)) == {"x": 2}


# ── (1) m03: el ValueError del helper no tumba el cap ──

PERFIL = SimpleNamespace(formula=["subject", "action", "setting", "text_in_image", "lighting", "mood"],
                         aspect_ratio_text="16:9 aspect ratio")
SLOTS = {"subject": "An empty child's bed in a dark room", "action": "the bed frame trembles",
         "setting": "a stone house in an Alpine valley, 1963", "lighting": "moonlight through a window",
         "mood": "dread", "text_in_image": {"present": False}}


def test_m03_flash_vacio_en_todos_los_intentos_backstop_con_los_slots(monkeypatch, capsys):
    def nada(*a, **k):
        raise ValueError("Gemini devolvió JSON inválido en char 0 (line 1 col 1): respuesta vacía (finish_reason=SAFETY).")
    monkeypatch.setattr(mv, "call_flash_json", nada)
    prose = mv._fluidify_item(SLOTS, [], PERFIL, "cap 1 img #1")
    assert prose == ("An empty child's bed in a dark room. the bed frame trembles. a stone house in an Alpine valley, "
                     "1963. moonlight through a window. dread.")
    out = capsys.readouterr().out
    assert out.count("el fluidificador no devolvió texto") == 3 and "SIN RESPUESTA en 3 intentos" in out


def test_m03_flash_vacio_una_vez_y_despues_prosa(monkeypatch):
    xs = iter([ValueError("respuesta vacía"), {"prose": "A child's bed stands empty in a dark stone room."}])

    def call(*a, **k):
        x = next(xs)
        if isinstance(x, Exception):
            raise x
        return x
    monkeypatch.setattr(mv, "call_flash_json", call)
    assert mv._fluidify_item(SLOTS, [], PERFIL, "cap 1 img #1") == "A child's bed stands empty in a dark stone room."


def test_m03_otros_errores_siguen_igual(monkeypatch):
    monkeypatch.setattr(mv, "call_flash_json", lambda *a, **k: {"prose": ""})
    with pytest.raises(mv.VisualValidationError):
        mv._fluidify_item(SLOTS, [], PERFIL, "cap 1 img #1")


# ── (2) reparación (e) ──

PARRAFO = {"cap": 4, "beat": 10, "texto": "Verano de 1958. Kuleshov recuerda instalaciones inundadas, tablones para "
                                          "caminar a oscuras y productos químicos que no limpiaban nada. Nadie lo anotó."}
PROB_E = {"codigo": "e", "frase": "Kuleshov recuerda instalaciones inundadas, tablones para caminar a oscuras y "
                                  "productos químicos que no limpiaban nada.",
          "motivo": "Q20 está SIN VERIFICAR y va con el nombre de Mikhail Kuleshov"}


def test_reparacion_e_quita_el_nombre_y_deja_la_oracion():
    pedidos = []

    def call(prompt, **kw):
        pedidos.append(prompt)
        return {"texto": PARRAFO["texto"].replace("Kuleshov recuerda", "Uno de los trabajadores recuerda")}
    nuevo, why = g4.edit_sentences(PARRAFO, [PROB_E], call=call)
    assert why == "" and "Kuleshov" not in nuevo and "Uno de los trabajadores recuerda instalaciones inundadas" in nuevo
    assert g4.PEDIDO_E in pedidos[0] and "No saques la oración." in pedidos[0]
    assert "Sacá esas frases o corregilas" not in pedidos[0]


def test_otros_motivos_el_pedido_queda_como_estaba():
    pedidos = []
    g4.edit_sentences(PARRAFO, [{**PROB_E, "codigo": "a", "motivo": "cifra 1958 no está en los datos"}],
                      call=lambda p, **k: pedidos.append(p) or {"texto": PARRAFO["texto"]})
    assert ("hay frases con un problema. Sacá esas frases o corregilas para que el\nproblema desaparezca, con las "
            "palabras que ya tienen. No toques nada más del párrafo; no agregues datos, cifras,\nnombres, adjetivos ni "
            "citas.") in pedidos[0]
    assert g4.PEDIDO_E not in pedidos[0]


# ── (3) el editor m01c fuera de reparar ──

def test_reparar_con_bloqueantes_ya_no_llama_al_editor():
    import test_module_f11c as t
    esc = t._esc_ok()
    ps = t._parrafos(esc)
    ps[0]["texto"] += " Murieron 412 personas."
    calls: list = []
    log: list[str] = []
    r = g4.reparar(t.TOPIC, esc, ps, call=t._fake(calls), log=log)
    assert calls == ["guion_v4 editar frase"] and r["pasos"]["editor"] == []
    assert any("fuera del camino desde F27" in x for x in log)


def test_fase1_5_editor_solo_con_la_bandera(monkeypatch):
    import fase1_5 as f15
    vistos = []
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: {"id": tid, "evidence_pool": {"datos": []}})
    monkeypatch.setattr(f15, "_topic_v3", lambda tid: {"id": tid})
    out = {"particion": {"skeleton": {}, "narration": {}}}
    monkeypatch.setattr(f15, "run_guion_v4", lambda tid, **kw: vistos.append(kw) or out)
    f15.process_topic("t", from_step="m01b", stop_after_step="m01b", v3=True, guion="v4")
    f15.process_topic("t", from_step="m01b", stop_after_step="m01b", v3=True, guion="v4", editor=True)
    assert vistos == [{}, {"editor": True}]


# ── (4) métrica ──

def test_palabras_por_segundo_medidas_en_vajont():
    assert g4.PALABRAS_POR_SEG == 2.4
    assert g4.largo_txt(2355).startswith("largo: 2355 palabras ≈ 16.4 min")
