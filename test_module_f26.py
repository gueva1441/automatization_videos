"""
test_module_f26.py — F26 §A.1: escaleta f25-1 → f26-1, tres agregados literales (la prueba de la promesa al final de
<oficio> §2, «Un id que va a `a_pantalla` no va en ningún beat.» al final de §10 y el nombre del antagonista como está
en la ficha al final de su párrafo de <que_es_una_escaleta>), literal contra su archivo. Sin red.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from script_engine import m01a_escaleta as me

ROOT = Path(__file__).resolve().parent
F26 = ROOT / "lab" / "hyperframes" / "f26"


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _sistema(p: Path) -> str:
    md = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    i = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    return md[i:md.index("\n\n---\n", i)]


PROMESA = (" Probala así: si la oración se puede leer como un resumen de lo que viene («nadie lo sabrá durante años», "
           "«terminará en un juicio»), no es una promesa; es un adelanto. Volvé a escribirla con lo que se ve o lo que "
           "no cierra.")
PANTALLA = " Un id que va a `a_pantalla` no va en ningún beat."
ANTAGONISTA = " Su nombre va exactamente como está escrito en la ficha, sin siglas ni paréntesis agregados."


def test_escaleta_f26_1_literal_contra_el_archivo():
    # F54: la escaleta de hoy es la f54-1 (test_module_f54); la f26-1 queda con su versión
    assert me.SYSTEM_V2_F26_1 == _sistema(F26 / "PROMPT_ESCALETA_f26_1.md") and me.PROMPT_VERSION_V2_F26_1 == "f26-1"
    assert _md5(me.SYSTEM_V2_F26_1) == "2e67791cedbfa7492f8b6de1268b7b30"


def test_f25_1_queda_con_su_version():
    assert me.PROMPT_VERSION_V2_F25_1 == "f25-1"
    assert _md5(me.SYSTEM_V2_F25_1) == "9325ad3890ebfe241953d86759e20296"


def test_solo_los_tres_agregados():
    a, b = me.SYSTEM_V2_F25_1.split("\n"), me.SYSTEM_V2_F26_1.split("\n")
    assert len(a) == len(b)
    dif = [(x, y) for x, y in zip(a, b) if x != y]
    assert len(dif) == 3
    esperado = {("no nombra juicios, comisiones ni consecuencias.", PROMESA),
                ("Las cifras que sí dice la voz, una vez cada una.", PANTALLA),
                ("lo decís («ninguno») y por qué.", ANTAGONISTA)}
    vistos = set()
    for viejo, nuevo in dif:
        for fin, add in esperado:
            if viejo.endswith(fin) and nuevo == viejo + add:
                vistos.add((fin, add))
    assert vistos == esperado
    assert me.SYSTEM_V2_F26_1.replace(PROMESA, "").replace(PANTALLA, "").replace(ANTAGONISTA, "") == me.SYSTEM_V2_F25_1

