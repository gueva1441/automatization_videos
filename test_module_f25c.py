"""
test_module_f25c.py — F25c: escaleta v2 con Fable 5.1 por defecto (Sol con `modelo=` / `--modelo-escaleta`), prompt
de la escaleta f25-1 (la promesa en una sola oración) y guion v5.4 (la promesa del gancho como viene en la escaleta),
cada uno con un solo cambio y literal contra su archivo; largo: max_words 2200 y el tope pasa de bloqueante (c) a
métrica. Sin red.
"""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path

from script_engine import guion_v4 as g4
from script_engine import m01a_escaleta as me
from script_engine import video_length as vl

ROOT = Path(__file__).resolve().parent
F25C = ROOT / "lab" / "hyperframes" / "f25c"


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _sistema(name: str) -> str:
    md = (F25C / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    i = md.index("\n## SISTEMA\n\n") + len("\n## SISTEMA\n\n")
    return md[i:md.index("\n\n---\n", i)]


def _dif(a: str, b: str) -> list[tuple[str, str]]:
    x, y = a.split("\n"), b.split("\n")
    assert len(x) == len(y)
    return [(p, q) for p, q in zip(x, y) if p != q]


def test_escaleta_f25_1_literal_y_un_solo_cambio():
    assert me.SYSTEM_V2 == _sistema("PROMPT_ESCALETA_f25_1.md") and me.PROMPT_VERSION_V2 == "f25-1"
    assert _md5(me.SYSTEM_V2) == "9325ad3890ebfe241953d86759e20296"
    assert _md5(me.SYSTEM_V2_F24_1) == "006a195f0ce4be014df34d71644aedb1"
    (viejo, nuevo), = _dif(me.SYSTEM_V2_F24_1, me.SYSTEM_V2)
    va = ("La promesa es una frase que dice qué va a entender el espectador si se queda. Es una imagen o una pregunta, "
          "nunca un resumen de lo que va a pasar ni una lista de lo que viene.")
    nu = ("La promesa es una sola oración que deja una imagen sin cerrar o una pregunta que el espectador no puede "
          "responder todavía. No cuenta lo que va a pasar, no enumera lo que viene, no nombra juicios, comisiones ni "
          "consecuencias.")
    assert viejo.replace(va, nu) == nuevo and va in viejo


def test_guion_v5_4_literal_y_un_solo_cambio():
    assert g4.system() == g4.SYSTEM_V5_4 == _sistema("PROMPT_GUIONISTA_v5_4.md") and g4.PROMPT_VERSION == "f25-1"
    assert _md5(g4.system()) == "2f66c1e07e4d6c31178091371821c0c9"
    assert _md5(g4.system("f23-1")) == "8ca9aa494e3a0b9b4a99f60e6006c5f8"
    (viejo, nuevo), = _dif(g4.system("f23-1"), g4.system())
    assert viejo.replace("Segunda: la promesa.", "Segunda: la promesa, como viene en la escaleta, sin agregarle lo "
                                                 "que va a pasar después.") == nuevo
    assert "f25-1" in g4.VERSIONES_V5 and "f23-1" in g4.VERSIONES_V5


def test_escaleta_con_fable_por_defecto_y_sol_con_modelo(monkeypatch):
    import claude_helpers
    import gpt_helpers
    vistos = []
    monkeypatch.setattr(claude_helpers, "make_call", lambda m, e=None, post=None: vistos.append((m, e)) or "C")
    monkeypatch.setattr(gpt_helpers, "make_call", lambda m, e=None, post=None: vistos.append((m, e)) or "G")
    assert me.DEFAULT_MODELO_ESCALETA == "claude-fable-5-1"
    assert me.call_escaleta() == "C" and me.call_escaleta("gpt-6.1-sol") == "G"
    assert vistos == [("claude-fable-5-1", "medium"), ("gpt-6.1-sol", "high")]


def test_generate_escaleta_v2_sin_call_usa_call_escaleta(monkeypatch, tmp_path):
    import test_module_f16 as t16
    vistos = []

    def fake(modelo=None):
        vistos.append(modelo)
        return lambda prompt, **kw: copy.deepcopy(t16.good())
    monkeypatch.setattr(me, "call_escaleta", fake)
    monkeypatch.setattr(me, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(me, "pool_gate_profile", lambda *a, **k: None)
    me.generate_escaleta(t16.TOPIC, persist=False, ficha=t16.FICHA)
    me.generate_escaleta(t16.TOPIC, persist=False, ficha=t16.FICHA, modelo="gpt-6.1-sol")
    assert vistos == [None, "gpt-6.1-sol"]


def test_largo_2200_y_el_tope_es_metrica():
    assert vl.DEFAULTS["max_words"] == 2200
    assert g4.largo_txt(2047) == "largo: 2047 palabras ≈ 16.6 min"
    assert g4.largo_txt(2300).endswith("(más que el tope de 2200)") or vl.get("max_words") != 2200
    src = Path(g4.__file__).read_text(encoding="utf-8")
    assert "el tope es {_len('max_words')}" not in src.split("def bloqueantes", 1)[1].split("\ndef ", 1)[0]
