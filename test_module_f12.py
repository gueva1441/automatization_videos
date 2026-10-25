"""
test_module_f12.py — F12 (ficha del caso): el esquema y la estructura del prompt, el chequeo determinista (id
inexistente, cifra no respaldada, cita corregida de más, contradicción con doc/offset ajenos) y el modelo por defecto
del guion v4 (gpt-6.1-sol high). Sin red.
"""
from __future__ import annotations

import json

from researcher_steps import ficha_caso as fc
from script_engine import guion_v4 as g4

POOL = {
    "datos": [
        {"id": "D20", "texto": "Emiliano Paiva, hijo del dueño, fue condenado a 10 años de prisión.", "valor": "10",
         "doc_id": "F05", "offset": 2282, "cita_literal": "su hijo, Emiliano Paiva, a 10 años de prisión",
         "evidencia": [{"doc_id": "F05", "offset": 2282, "cita_literal": "su hijo, Emiliano Paiva, a 10 años de prisión"},
                       {"doc_id": "F10", "offset": 3282, "cita_literal": "a su hijo Víctor Paiva, a 10 años"}]},
        {"id": "D101", "texto": "La temperatura alcanzó los 600 °C.", "valor": "600", "doc_id": "F06", "offset": 10,
         "cita_literal": "alcanzó los 600 grados"},
        {"id": "D192", "texto": "Oficialmente hubo 327 muertos.", "valor": "327", "doc_id": "F10", "offset": 3213,
         "cita_literal": "En el incendio hubo oficialmente 327 muertos, más los desaparecidos."},
    ],
    "cronologia": [{"id": "T21", "fecha": "2004-08-01", "hora": "11:25", "evento": "Se inicia el fuego.",
                    "doc_id": "F09", "offset": 5, "cita_literal": "a las 11.25 empezó el fuego"}],
    "citas": [{"id": "Q34", "texto": "la gente corría porque el portó estaba cerrado", "autor": "Digna Felicia Cáceres",
               "rol": "Sobreviviente", "verificacion": {"estado": "verificada"}, "doc_id": "F09", "offset": 7,
               "cita_literal": "la gente corría porque el portó estaba cerrado"}],
    "personajes": [{"id": "P07", "nombre": "Emiliano Paiva", "rol": "Hijo del propietario", "doc_id": "F05",
                    "offset": 1484, "cita_literal": "de su hijo, Emiliano Paiva"},
                   {"id": "P28", "nombre": "Víctor Daniel Paiva", "rol": "Hijo de Juan Pío Paiva", "doc_id": "F15",
                    "offset": 524, "cita_literal": "su hijo Víctor Daniel Paiva"}],
    "lugares": [],
}


def _ficha(**over):
    f = {s: [] for s in fc.SECCIONES}
    f.update(over)
    return f


# ═══════════════════════════════════════════════════════════════
#  Esquema y prompt
# ═══════════════════════════════════════════════════════════════

def test_esquema_tiene_las_siete_secciones():
    assert set(fc.SCHEMA["required"]) == set(fc.SECCIONES) | {"historia"}   # F15: + historia
    assert "unidad" in fc.SCHEMA["properties"]["cifras"]["items"]["required"]
    v = fc.SCHEMA["properties"]["contradicciones"]["items"]["properties"]["versiones"]["items"]["required"]
    assert {"doc_id", "offset", "ids"} <= set(v)
    import gpt_helpers
    assert json.dumps(gpt_helpers.json_schema(fc.SCHEMA))                # convertible a JSON Schema (GPT)


def test_prompt_estructura_f11c_y_pool_completo():
    s, u = fc.system(), fc.prompt(POOL, "Ycuá")
    assert s.index("<rol>") < s.index("<tarea>") and "contradicciones" in s
    assert u.startswith("<caso>") and u.rstrip().endswith("</tarea>") and u.index("</pool>") < u.index("<tarea>")
    assert all(f"[{i}]" in u for i in ("D20", "D101", "D192", "T21", "Q34", "P07", "P28"))
    assert "F10@3282" in u and "F05@2282" in u                          # cada evidencia con doc y offset


def test_evidencia_repetida_va_como_referencia():
    pool = json.loads(json.dumps(POOL))
    pool["datos"][2]["evidencia"] = [{"doc_id": "F10", "offset": 3282, "cita_literal": "a su hijo Víctor Paiva, a 10 años"}]
    u = fc.prompt(pool, "Ycuá")
    assert u.count("«a su hijo Víctor Paiva, a 10 años»") == 1 and "F10@3282: (= arriba)" in u


# ═══════════════════════════════════════════════════════════════
#  Chequeo determinista
# ═══════════════════════════════════════════════════════════════

def test_respaldado_queda():
    f = _ficha(hechos=[{"texto": "Oficialmente hubo 327 muertos.", "ids": ["D192"]}],
               cronologia=[{"fecha": "2004-08-01", "hora": "11:25", "evento": "Se inicia el fuego.", "ids": ["T21"]}],
               cifras=[{"que": "temperatura", "valor": "600", "unidad": "°C", "fuente": "F06", "ids": ["D101"],
                        "otras_versiones": []}])
    out, sacados = fc.check(f, POOL)
    assert sacados == [] and len(out["hechos"]) == len(out["cronologia"]) == len(out["cifras"]) == 1


def test_id_inexistente_va_a_descartados():
    out, sacados = fc.check(_ficha(hechos=[{"texto": "Hubo 327 muertos.", "ids": ["D999"]}]), POOL)
    assert out["hechos"] == [] and "id inexistente D999" in sacados[0]["motivo"]
    assert out["descartados"][0]["motivo"].startswith("no respaldado")


def test_cifra_no_respaldada_va_a_descartados():
    out, sacados = fc.check(_ficha(hechos=[{"texto": "Murieron 400 personas.", "ids": ["D192"]}],
                                   cronologia=[{"fecha": "2004-08-01", "hora": "11:20", "evento": "Fuego",
                                                "ids": ["T21"]}]), POOL)
    assert out["hechos"] == out["cronologia"] == []
    by = {x["seccion"]: x["motivo"] for x in sacados}
    assert "cifra 400" in by["hechos"] and "hora 11:20" in by["cronologia"]


def test_cita_corregida_dentro_y_fuera_del_limite():
    ok = {"autor": "Digna Felicia Cáceres", "rol": "Sobreviviente", "verificacion": "verificada",
          "texto": "la gente corría porque el portón estaba cerrado",
          "original": "la gente corría porque el portó estaba cerrado", "ids": ["Q34"]}
    de_mas = {**ok, "texto": "la gente huía porque el portón estaba trabado"}
    out, sacados = fc.check(_ficha(citas=[ok, de_mas]), POOL)
    assert out["citas"] == [ok] and len(sacados) == 1
    assert "cita corregida a" in sacados[0]["motivo"]
    assert fc.levenshtein("portó", "portón") == 1


def test_contradiccion_con_doc_offset_de_sus_ids():
    buena = {"tema": "nombre del hijo de Paiva", "versiones": [
        {"dice": "Emiliano Paiva", "doc_id": "F05", "offset": 1484, "ids": ["P07"]},
        {"dice": "Víctor Daniel Paiva", "doc_id": "F15", "offset": 524, "ids": ["P28"]}]}
    mala = {"tema": "x", "versiones": [{"dice": "Víctor Paiva", "doc_id": "F99", "offset": 1, "ids": ["P28"]}]}
    out, sacados = fc.check(_ficha(contradicciones=[buena, mala]), POOL)
    assert out["contradicciones"] == [buena] and "F99@1 no es evidencia de P28" in sacados[0]["motivo"]


def test_numeros_con_separadores():
    assert fc.unsupported("4.000 personas", "eran 4000 personas") == []
    assert fc.unsupported("el 1 de agosto de 2004", "domingo 1 de agosto del 2004") == []
    assert fc.unsupported("G. 5.000 millones", "G. 4.500 millones") == ["cifra 5.000"]
    assert fc.unsupported("La crónica de F15 y el dato D101 dicen 327", "hubo 327 muertos") == []   # ids ≠ cifras


def test_markdown_contradicciones_arriba_y_conteos():
    f = _ficha(contradicciones=[{"tema": "nombre del hijo", "versiones": [
        {"dice": "Emiliano Paiva", "doc_id": "F05", "offset": 1484, "ids": ["P07"]}]}],
        hechos=[{"texto": "Hubo 327 muertos.", "ids": ["D192"]}])
    md = fc.markdown(f, {"titulo": "Ycuá", "usd": 0.1})
    assert md.index("## Contradicciones") < md.index("## Personas") < md.index("## Cifras") < md.index(
        "## Cronología") < md.index("## Hechos") < md.index("## Citas") < md.index("## Descartados")
    assert "**contradicciones** 1" in md and "<sub>D192</sub>" in md


# ═══════════════════════════════════════════════════════════════
#  Modelo por defecto del guion v4
# ═══════════════════════════════════════════════════════════════

def test_v4_por_defecto_es_sol_high():
    c = g4.call_for(None)
    assert g4.DEFAULT_MODELO == "gpt-6.1-sol" and (c.model, c.reasoning_effort) == ("gpt-6.1-sol", "high")


def test_v4_write_sin_call_usa_sol(monkeypatch):
    # F22d (decisión del analista): sin `call`, el guion v4 usa su modelo por defecto (F22e: Fable 5.1 high);
    # `call_for(None)` (escaleta, columna) sigue siendo Sol high
    import claude_helpers
    from test_module_f11 import TOPIC, _esc_ok, _parrafos
    esc = _esc_ok()
    seen = {}

    def fake_make_call(model, effort=None, post=None):
        seen["m"] = (model, effort)
        return lambda prompt, **kw: {"parrafos": [{"beat": p["beat"], "texto": p["texto"]} for p in _parrafos(esc)]}
    monkeypatch.setattr(claude_helpers, "make_call", fake_make_call)
    g4.write(TOPIC, esc)
    assert seen["m"] == ("claude-fable-5-1", "high")
    assert g4.call_for(None).model == "gpt-6.1-sol"
