"""
test_module_f13.py — F13 (largo abierto): con `largo="objetivo"` el prompt es byte-idéntico a `f11c-1` (md5 tomados del
guion_v4.py de b204868); con `largo="abierto"` no hay cifras de largo en el prompt y el bloqueante (c) de largo no se
evalúa (beat faltante, cap vacío y el tope siguen). Sin red.
"""
from __future__ import annotations

import hashlib
import re

import pytest

from script_engine import guion_v4 as g4
from test_module_f11 import TOPIC, _esc, _esc_ok, _parrafos

# md5 del prompt de f11c-1 (b204868) sobre los fixtures de test_module_f11
F11C_MD5 = {"_esc_ok": "d3a0533e828fc8eb28be73d836b53245", "_esc": "4d7816f174d84d6bb61e9ca30c3fe926"}
F11C_SYSTEM_MD5 = "8edea05efeac91afdb88f9a7bb2f0b73"


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def test_objetivo_byte_identico_a_f11c():
    for f in (_esc_ok, _esc):
        assert _md5(g4.prompt(TOPIC, f())) == _md5(g4.prompt(TOPIC, f(), "objetivo")) == F11C_MD5[f.__name__]
    assert _md5(g4.system()) == F11C_SYSTEM_MD5
    assert g4.prompt_version("objetivo") == g4.PROMPT_VERSION == "f11c-1"


def test_abierto_sin_cifras_de_largo():
    esc = _esc_ok()
    a, o = g4.prompt(TOPIC, esc, "abierto"), g4.prompt(TOPIC, esc, "objetivo")
    assert "palabras" not in a and "≈" not in a and re.search(r"^CAP \d+$", a, re.M)
    assert "Cada cap dura lo que su historia necesita: ni relleno ni resumen." in a
    assert a.rstrip().endswith("</tarea>") and g4.prompt_version("abierto") == "f13-1"
    # fuera del largo, el prompt es el mismo
    strip = lambda s: re.sub(r"(CAP \d+)( · ≈ \d+ palabras)?", r"\1", s.split("<tarea>")[0])
    assert strip(a) == strip(o)
    with pytest.raises(ValueError):
        g4.prompt(TOPIC, esc, "corto")


def test_write_abierto_manda_el_prompt_abierto():
    esc = _esc_ok()
    seen = {}

    def call(prompt, **kw):
        seen["p"] = prompt
        return {"parrafos": [{"beat": p["beat"], "texto": p["texto"]} for p in _parrafos(esc)]}
    g = g4.write(TOPIC, esc, call=call, largo="abierto")
    assert seen["p"] == g4.prompt(TOPIC, esc, "abierto") and g["prompt_version"] == "f13-1"


def test_bloqueante_de_largo_apagado_solo_con_abierto():
    esc = _esc_ok()
    ps = [p for p in _parrafos(esc) if p["cap"] != 3]
    ps = [{**p, "texto": p["texto"] + " Y otra cosa más." * 40} if p["cap"] == 2 else p for p in ps]
    obj = [x["motivo"] for x in g4.bloqueantes(TOPIC, esc, ps)]
    abi = [x["motivo"] for x in g4.bloqueantes(TOPIC, esc, ps, largo="abierto")]
    assert any("cap 2 largo" in m for m in obj) and not any(" largo:" in m or " corto:" in m for m in abi)
    assert "cap 3 vacío" in obj and "cap 3 vacío" in abi                    # cap vacío sigue
    assert any(m.startswith("falta el beat") for m in abi)                   # beat faltante sigue
    assert g4.bloqueantes(TOPIC, esc, _parrafos(esc), largo="abierto") == []
