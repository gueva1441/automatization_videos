"""
test_module_f15b.py — F15b (v5.1: la escena merece un párrafo): el sistema v5.1 byte-idéntico al archivo del analista
(el v5 sigue reproducible); la escaleta sin ficha intacta y con ficha v2 pidiendo gancho y pico desde las escenas (aviso
«gancho sin escena de la ficha», no rechaza); los dos aflojes del chequeo de la ficha (las 12 cifras de Ycuá: en letras
y en millones; una escena con un solo sentido respaldado). Sin red.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from researcher_steps import ficha_caso as fc
from script_engine import guion_v4 as g4
from script_engine import m01a_escaleta as ma
from test_module_f11 import POOL as POOL11
from test_module_f11 import TOPIC as TOPIC11
from test_module_f11 import _esc_ok
from test_module_f14 import ESC_MD5
from test_module_f15 import FICHA_V2

F15 = Path(__file__).resolve().parent / "lab" / "hyperframes" / "f15"


def _md(name: str) -> str:
    return (F15 / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def _sistema(md: str) -> str:
    i0 = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    return md[i0:md.index("</errores>", i0) + len("</errores>")]


# ═══════════════════════════════════════════════════════════════
#  Prompt v5.1 (§1.1)
# ═══════════════════════════════════════════════════════════════

def test_sistema_v5_1_byte_identico_al_archivo():
    bloque = _sistema(_md("PROMPT_GUIONISTA_v5_1.md"))
    assert g4.system() == bloque == g4.SYSTEM_V5_1 and g4.PROMPT_VERSION == "f15b-1"
    for nuevo in ("Una escena merece un párrafo entero", "no es más corto el que dice menos, sino el que no repite",
                  "- Telegrama:", "- Gancho abstracto:"):
        assert nuevo in g4.system() and nuevo not in g4.system("f15-1")
    assert g4.system("f15-1") == _sistema(_md("PROMPT_GUIONISTA_v5.md"))         # el v5, reproducible


def test_usuario_igual_al_v5_y_version_f15b():
    esc = _esc_ok()
    assert g4.prompt(TOPIC11, esc) == g4.prompt(TOPIC11, esc, version="f15-1")     # la <tarea> no cambia en v5.1
    seen = {}

    def call(prompt, **kw):
        seen["s"] = kw.get("system_instruction")
        return {"parrafos": [{"beat": b["n"], "texto": "x"} for b in esc["beats"]]}
    g = g4.write(TOPIC11, esc, call=call)
    assert seen["s"] == g4.SYSTEM_V5_1 and g["prompt_version"] == "f15b-1"


# ═══════════════════════════════════════════════════════════════
#  Escaleta (§1.2)
# ═══════════════════════════════════════════════════════════════

def test_escaleta_sin_ficha_intacta_y_con_ficha_pide_gancho_y_pico_desde_escenas():
    assert hashlib.md5(ma.build_prompt(TOPIC11, POOL11).encode()).hexdigest() == ESC_MD5["sin_fb"]
    p = ma.build_prompt(TOPIC11, POOL11, None, FICHA_V2)
    assert ("El beat 1 (gancho) y el beat del pico toman su `imagen_sensorial` de una escena de la ficha cuando hay una "
            "para ese momento; los demás beats, cuando sirva.") in p


def test_aviso_gancho_sin_escena():
    sin = {"humano": {"id": "P1", "nombre": "Liz Torres"}, "beats": [{"n": 1}, {"n": 2, "escena_idx": 1}]}
    ma.ficha_notes(sin, FICHA_V2)
    assert "gancho sin escena de la ficha" in sin.get("_avisos", [])
    con = {"humano": {"id": "P1", "nombre": "Liz Torres"}, "beats": [{"n": 1, "escena_idx": 1}]}
    ma.ficha_notes(con, FICHA_V2)
    assert "_avisos" not in con


# ═══════════════════════════════════════════════════════════════
#  Aflojes del chequeo de la ficha (§1.3)
# ═══════════════════════════════════════════════════════════════

# los pasajes del pool de Ycuá de las 12 cifras que F15 sacó (texto literal de sus ids)
DOCE = [
    ("6", "personas", "Tras la tragedia, se reportaron seis personas desaparecidas."),
    ("2", "hijas", "Yessica Vanessa y Yessica Natalia, las dos únicas hijas de Ángela."),
    ("5", "personas", "La familia López perdió cinco integrantes en el incendio."),
    ("4", "personas", "La familia de Angélica Roa perdió cuatro integrantes en el incendio."),
    ("15", "días", "Nelson Astigarraga estuvo internado quince días por las secuelas."),
    ("10", "días", "La sobreviviente Angélica Roa permaneció diez días hospitalizada."),
    ("3", "puertas", "El informe sobre las puertas concluyó que solo tres de ellas estaban cerradas."),
    ("4", "puertas", "Las cuatro puertas de blíndex del supermercado eran pivotantes."),
    ("4.500.000.000", "guaraníes", "La Sala Civil condenó a pagar un total de G. 4.500 millones a un matrimonio."),
    ("5.000.000.000", "guaraníes", "El juez Enrique Mongelós condenó a pagar G. 5.000 millones."),
    ("600.000.000", "guaraníes", "La primera sentencia condenó a Ycuá Bolaños y a Mapfre a pagar G. 600 millones."),
    ("más de 400.000.000", "guaraníes", "Fueron condenados a pagar más de G. 400 millones en otra demanda."),
]


def test_las_12_cifras_de_ycua_quedan_respaldadas():
    pool = {"datos": [{"id": f"D{k}", "texto": t, "doc_id": "F01", "offset": k} for k, (_, _, t) in enumerate(DOCE)]}
    cifras = [{"que": "x", "valor": v, "unidad": u, "fuente": "F01", "ids": [f"D{k}"], "otras_versiones": []}
              for k, (v, u, _) in enumerate(DOCE)]
    out, sacados = fc.check({"cifras": cifras}, pool)
    assert sacados == [] and len(out["cifras"]) == 12
    malas = [{**c, "valor": "7"} for c in cifras[:2]] + [{**cifras[8], "valor": "4.600.000.000"}]
    assert len(fc.check({"cifras": malas}, pool)[1]) == 3                            # lo que no está, sigue afuera


def test_normalizacion_de_cifras():
    assert fc.unsupported("4.500 personas", "eran 4500") == fc.unsupported("4,500", "4 500") == []
    assert fc.unsupported("US$ 398", "debía 398 dólares") == fc.unsupported("600 °C", "600 grados") == []
    assert fc.unsupported("G. 4.500 millones", "4.500.000.000 de guaraníes") == []
    assert fc.unsupported("35 presos", "treinta y cinco presos") == []
    assert fc.unsupported("Murieron 400", "hubo 327 muertos") == ["cifra 400"]
    assert fc.unsupported("1 sobreviviente", "una vez, un día, tres veces") == ["cifra 1"]      # artículos ≠ «1»
    assert fc.unsupported("1 sobreviviente", "quedó uno solo") == []


def test_escena_con_un_solo_sentido_respaldado():
    pool = {"datos": [{"id": "D40", "texto": "Los guardias cerraron las puertas.", "doc_id": "F09", "offset": 1}]}
    esc = {"donde": "pasillo", "quien": "gente", "que_pasa": "llegan a las puertas",
           "sentidos": "olor a pan recién horneado; los guardias cerraron las puertas", "ids": ["D40"]}
    nada = {**esc, "sentidos": "olor a pan recién horneado; música de cumbia"}
    out, sacados = fc.check({"escenas": [esc, nada]}, pool)
    assert out["escenas"] == [esc] and len(sacados) == 1 and "ningún sentido" in sacados[0]["motivo"]
