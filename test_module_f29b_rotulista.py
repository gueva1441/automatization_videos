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


# ═══════════════ anclaje ═══════════════

# ═══════════════ candado ═══════════════

# ═══════════════ no dicho y spoiler ═══════════════

# ═══════════════ topes ═══════════════

# ═══════════════ a_pantalla: reintento y nunca inventar ═══════════════


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


# ═══════════════ F29b, antes de B: candado de persona y tope en paralelo ═══════════════

