"""
test_module_f15.py — F15 (prompt del guionista v5 + ficha v2): el sistema y la tarea del v5 byte-idénticos al archivo
del analista (se leen del .md); el bloque de la ficha v2 literal en su prompt; esquema y chequeo de historia y escenas
(sentidos que no están en sus ids → descartados); la escaleta sin ficha byte-idéntica y con ficha v2 con historia y
escenas primero; el bloqueante (d) mira las `personas_descartadas` de la ficha. Sin red.
"""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path

from researcher_steps import ficha_caso as fc
from script_engine import guion_v4 as g4
from script_engine import m01a_escaleta as ma
from test_module_f11 import POOL as POOL11
from test_module_f11 import TOPIC as TOPIC11
from test_module_f11 import _esc_ok, _parrafos
from test_module_f14 import ESC_MD5, POOL

F15 = Path(__file__).resolve().parent / "lab" / "hyperframes" / "f15"


def _md(name: str) -> str:
    # git (autocrlf) puede dejar el .md con CRLF en un checkout nuevo: el contenido es el mismo, se compara en LF
    return (F15 / name).read_text(encoding="utf-8").replace("\r\n", "\n")


# ═══════════════════════════════════════════════════════════════
#  Guionista v5 (§1.1): literal del archivo
# ═══════════════════════════════════════════════════════════════

def test_sistema_v5_byte_identico_al_archivo():
    md = _md("PROMPT_GUIONISTA_v5.md")
    i0 = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")         # el bloque, no el «<rol>» de la intro
    bloque = md[i0:md.index("</errores>", i0) + len("</errores>")]
    assert bloque.startswith("<rol>\nSos el guionista") and "Base: técnicas" not in g4.system("f15-1")
    assert g4.system("f15-1") == bloque and g4.SYSTEM_V5 == bloque      # F15b: el v5 se pide explícito
    for tag in ("<rol>", "<voz>", "<estructura>", "<oficio>", "<ejemplos>", "<errores>"):
        assert tag in g4.system("f15-1")
    assert g4.PROMPT_VERSION_V5 == "f15-1" and g4.system("f11c-1") == g4.system_f11c() != g4.system("f15-1")


def test_usuario_v5_caso_escaleta_y_tarea_literal():
    md = _md("PROMPT_GUIONISTA_v5.md")
    u0 = md.index("\n## USUARIO")                                             # la tarea del bloque USUARIO
    tarea = md[md.index("<tarea>", u0):md.index("</tarea>", u0) + len("</tarea>")]
    esc = _esc_ok()
    p = g4.prompt(TOPIC11, esc, version="f15-1")
    assert p.endswith(tarea) and g4.TAREA_V5 == tarea
    assert p.index("<caso>") < p.index("</caso>") < p.index("<escaleta>") < p.index("</escaleta>") < p.index("<tarea>")
    assert "palabras" not in p.split("<tarea>")[0] and "≈" not in p          # sin cifras de largo
    assert "CAP 1 (gancho)" in p and "intensidad" in p and "por qué:" in p
    assert g4.prompt_version(version="f15-1") == "f15-1" and g4.prompt(TOPIC11, esc, "objetivo", version="f15-1") == p


def test_marca_version_de_quien():
    esc = _esc_ok()
    ficha = {"versiones": [{"tema": "quién cerró", "versiones": [
        {"dice": "x", "doc_id": "F01", "offset": 0, "ids": [esc["beats"][0]["dato_central"]]}]}]}
    i = esc["beats"][0]["dato_central"]
    vm = g4.version_marks(ficha, POOL11)
    assert vm[i].startswith("VERSIÓN DE: ")
    assert f"[{i}]" in g4.prompt(TOPIC11, esc, ficha=ficha) and "VERSIÓN DE: " in g4.prompt(TOPIC11, esc, ficha=ficha)
    assert "VERSIÓN DE" not in g4.prompt(TOPIC11, esc)


def test_write_por_defecto_v5():
    esc = _esc_ok()
    seen = {}

    def call(prompt, **kw):
        seen.update(p=prompt, s=kw.get("system_instruction"))
        return {"parrafos": [{"beat": p["beat"], "texto": p["texto"]} for p in _parrafos(esc)]}
    g = g4.write(TOPIC11, esc, call=call, version="f15-1")
    assert seen["s"] == g4.SYSTEM_V5 and seen["p"] == g4.prompt(TOPIC11, esc, version="f15-1")
    assert g["prompt_version"] == "f15-1"


# ═══════════════════════════════════════════════════════════════
#  Ficha v2 (§1.2)
# ═══════════════════════════════════════════════════════════════

def test_ficha_v2_bloque_literal_y_esquema():
    md = _md("PROMPT_FICHA_v2.md")
    a0 = "## Lo que se agrega al <tarea> del sistema\n\n"
    bloque = md[md.index(a0) + len(a0):md.index("\n\n---\n\n## Lo que cambia en la escaleta")]
    s = fc.system()
    assert bloque in s and s.index(bloque) < s.index("- hechos: entre 60 y 80")
    assert fc.PROMPT_VERSION == "f15-1"
    pr = fc.SCHEMA["properties"]
    assert {"humanos_candidatos", "giros", "pico", "pregunta_final"} <= set(pr["historia"]["properties"])
    assert {"donde", "quien", "que_pasa", "sentidos", "ids"} <= set(pr["escenas"]["items"]["properties"])
    assert {"nivel", "sirve_para"} <= set(pr["hechos"]["items"]["properties"])


def _f(**over):
    f = {s: [] for s in fc.SECCIONES}
    f["historia"] = {"humanos_candidatos": [], "giros": [], "pico": None, "pregunta_final": None}
    f.update(over)
    return f


def test_escena_con_sentidos_respaldados_y_sin_respaldo():
    ok = {"donde": "pasillo", "quien": "la gente", "que_pasa": "llegan a las puertas",
          "sentidos": "los guardias cerraron las puertas", "ids": ["D40"]}
    sin = {**ok, "sentidos": "olor a pan recién horneado"}
    sin_sentidos = {**ok, "sentidos": ""}
    out, sacados = fc.check(_f(escenas=[ok, sin, sin_sentidos]), POOL)
    assert out["escenas"] == [ok] and len(sacados) == 2
    assert "ningún sentido de la escena («olor a pan recién horneado») está en sus ids" in sacados[0]["motivo"]   # F15b
    assert "la escena no trae sentidos" in sacados[1]["motivo"]


def test_historia_con_el_mismo_control():
    h = {"humanos_candidatos": [{"nombre": "Digna Cáceres", "rol": "sobreviviente", "arco": "entra, ve el portón cerrado",
                                 "ids": ["Q34"], "citas_verificadas": 1},
                                {"nombre": "Nadie", "rol": "x", "arco": "y", "ids": ["Q999"], "citas_verificadas": 0}],
         "giros": [{"orden": 1, "que_cambia": "Oficialmente hubo 327 muertos.", "ids": ["D11"]},
                   {"orden": 2, "que_cambia": "Murieron 999 personas.", "ids": ["D11"]}],
         "pico": {"que": "Empieza el fuego a las 11:25.", "por_que": "todo lo prepara", "ids": ["T21"]},
         "pregunta_final": {"pregunta": "¿Quién cerró?", "ids": ["D404"]}}
    out, sacados = fc.check(_f(historia=h), POOL)
    oh = out["historia"]
    assert [x["nombre"] for x in oh["humanos_candidatos"]] == ["Digna Cáceres"]
    assert [x["orden"] for x in oh["giros"]] == [1] and oh["pico"] == h["pico"] and oh["pregunta_final"] is None
    assert {x["seccion"] for x in sacados} == {"historia.humanos_candidatos", "historia.giros", "historia.pregunta_final"}
    assert fc.counts(out)["humanos_candidatos"] == 1 and fc.counts(out)["pico"] == 1


def test_markdown_historia_y_escenas_arriba():
    f = _f(escenas=[{"donde": "pasillo", "quien": "gente", "que_pasa": "corren", "sentidos": "humo", "ids": ["D40"]}],
           historia={"humanos_candidatos": [{"nombre": "Digna", "rol": "r", "arco": "a", "ids": ["Q34"],
                                              "citas_verificadas": 1}], "giros": [], "pico": None, "pregunta_final": None})
    md = fc.markdown(f, {"titulo": "x", "usd": 0})
    assert md.index("## Historia") < md.index("## Escenas") < md.index("## Contradicciones")


# ═══════════════════════════════════════════════════════════════
#  Escaleta (§1.3)
# ═══════════════════════════════════════════════════════════════

def test_escaleta_sin_ficha_sigue_byte_identica():
    assert hashlib.md5(ma.build_prompt(TOPIC11, POOL11).encode()).hexdigest() == ESC_MD5["sin_fb"]
    assert "escena_idx" not in str(ma.SCHEMA) and "escena_idx" in str(ma.SCHEMA_FICHA)


FICHA_V2 = {"prompt_version": "f15-1",
            "historia": {"humanos_candidatos": [{"nombre": "Liz Torres", "rol": "sobreviviente", "arco": "a",
                                                 "ids": ["P1"], "citas_verificadas": 1}],
                         "giros": [{"orden": 1, "que_cambia": "cierran el portón", "ids": ["D4"]}],
                         "pico": {"que": "el humo", "por_que": "p", "ids": ["D5"]},
                         "pregunta_final": {"pregunta": "¿Quién?", "ids": ["D6"]}},
            "escenas": [{"donde": "patio", "quien": "gente", "que_pasa": "corren", "sentidos": "humo negro", "ids": ["D4"]}],
            "hechos": [{"texto": "El portón 4 estaba cerrado.", "nivel": 1, "sirve_para": "giro", "ids": ["D4"]}],
            "personas": [{"nombre": "Liz Torres", "rol": "sobreviviente", "variantes": [], "ids": ["P1"]}]}


def test_escaleta_con_ficha_v2_historia_y_escenas_primero():
    p = ma.build_prompt(TOPIC11, POOL11, None, FICHA_V2)
    assert p.index("HISTORIA:") < p.index("ESCENAS") < p.index("PERSONAS:") < p.index("HECHOS:")
    assert "HUMANOS CANDIDATOS" in p and "E1. patio" in p and "(nivel 1 · giro)" in p and "escena_idx" in p


def test_ficha_notes_humano_fuera_de_candidatos_y_escena_idx():
    esc = {"humano": {"id": "P2", "nombre": "Nelson Astigarraga"}, "justificacion_humano": "tiene más citas",
           "beats": [{"n": 1, "escena_idx": 1}, {"n": 2, "escena_idx": 7}]}
    ma.ficha_notes(esc, FICHA_V2)
    assert "escena_idx" in esc["beats"][0] and "escena_idx" not in esc["beats"][1]
    assert any("no está entre los humanos_candidatos" in a and "tiene más citas" in a for a in esc["_avisos"])
    esc2 = {"humano": {"id": "P1", "nombre": "Liz Torres"}, "beats": []}
    ma.ficha_notes(esc2, FICHA_V2)
    assert "_avisos" not in esc2


# ═══════════════════════════════════════════════════════════════
#  Bloqueante (d) sobre la ficha (§1.4)
# ═══════════════════════════════════════════════════════════════

def test_bloqueante_d_mira_personas_descartadas_de_la_ficha():
    esc = _esc_ok()
    topic = copy.deepcopy(TOPIC11)
    topic["evidence_pool"]["_descartados"] = list(topic["evidence_pool"].get("_descartados") or []) + [
        {"kind": "personajes", "texto": "Burl Cain", "motivo": "sin acción"}]
    ps = _parrafos(esc)
    ps[0] = {**ps[0], "texto": ps[0]["texto"] + " Burl Cain llegó con los oficiales."}
    sin = [x for x in g4.bloqueantes(topic, esc, ps) if x["codigo"] == "d"]
    ficha = {"personas_descartadas": [{"nombre": "Burl Cain", "rol": "director", "motivo": "m", "ids": ["D1"]}]}
    con = [x for x in g4.bloqueantes(topic, esc, ps, ficha=ficha) if x["codigo"] == "d"]
    assert sin and "Burl Cain" in sin[0]["motivo"] and con == []
    assert any(d.get("texto") == "Burl Cain" for d in topic["evidence_pool"]["_descartados"])   # el pool no se toca
