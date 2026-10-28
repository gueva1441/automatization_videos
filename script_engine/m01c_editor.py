"""
script_engine/m01c_editor.py — Módulo 01c v3 (F6c, HANDOFF_F6 §2.4): el editor que APRIETA la narración.

Solo puede cortar, reordenar frases dentro del beat, acortar, quitar repeticiones y relleno y reforzar el ritmo (partir
una frase larga, dejar una corta antes del golpe). NO puede agregar datos, cifras, nombres, adjetivos ni citas.
Queda lo que usa la cadena única: el prompt (`SYSTEM`, `SCHEMA`, `build_prompt`) de la pasada `--editor` de guion_v4
(F27), la guardia léxica (`lexical_guard`, `GUARD_ALL`: el texto editado no trae cifras, nombres propios, adjetivos
ni citas que el original no tenía) que usan guion_v4 y m01d_particion, y `narration_tts`.
F41 (DECISIONES 2026-10-27 20:59, una sola cadena): `edit` (el editor del guion v3 con re-revisión por párrafo) se
borró con la cadena vieja de fase1_5.
"""
from __future__ import annotations

import re
from typing import Any

from script_engine import evidence as ev


SYSTEM = ("Sos el editor de guion de un canal de documentales de misterio. Recibís una narración ya escrita y la "
          "apretás: cortás, acortás, sacás repeticiones y relleno, reordenás frases dentro del mismo párrafo y "
          "reforzás el ritmo. Nunca agregás información: ni datos, ni cifras, ni nombres, ni adjetivos, ni citas. "
          "Respondés SOLO JSON.")

SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "parrafos": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "beat": {"type": "INTEGER"}, "texto": {"type": "STRING"},
            "ids_usados": {"type": "ARRAY", "items": {"type": "STRING"}}},
            "required": ["beat", "texto", "ids_usados"]}},
        "cambios": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "parrafo": {"type": "INTEGER"}, "antes": {"type": "STRING"}, "despues": {"type": "STRING"},
            "motivo": {"type": "STRING"}}, "required": ["parrafo", "antes", "despues", "motivo"]}},
    },
    "required": ["parrafos", "cambios"],
}


def build_prompt(esc: dict, parrafos: list[dict], notas: list[str] | None = None,
                 cierre: list[str] | None = None) -> str:
    beats = {b["n"]: b for b in esc["beats"]}
    lines = []
    for k, p in enumerate(parrafos):
        b = beats.get(p["beat"], {})
        lines.append(f"[párrafo {k}] beat {p['beat']} · cap {p['cap']} · {b.get('funcion')} · intensidad "
                     f"{b.get('intensidad')} · ≈ {b.get('palabras_objetivo')} palabras el beat · ids {p['ids_usados']}\n"
                     f"{p['texto']}")
    pico = (esc.get("pico") or {}).get("beat")
    return f"""NARRACIÓN DEL GUIONISTA ({len(parrafos)} párrafos; el pico es el beat {pico}):

{chr(10).join(lines)}

EDITÁ (solo esto):
- cortar y acortar: frases que repiten lo ya dicho, relleno, calificativos que no suman;
- reordenar frases DENTRO del mismo párrafo;
- ritmo: partir una frase de más de 30 palabras; dejar una frase corta (≤ 6 palabras) antes del golpe; dos frases
  cortas seguidas antes del pico.
NUNCA:
- agregar datos, cifras, fechas, nombres propios, adjetivos ni citas que el párrafo no tenía;
- sacar la cifra, la fecha, el nombre o la cita de un id de `ids` (cada dato del párrafo se queda, literal);
- mover texto de un párrafo a otro, cambiar el beat, unir o partir párrafos (devolvé EXACTAMENTE {len(parrafos)}
  párrafos, en el mismo orden);
- tocar la primera frase del video ni la última frase de cada cap (anticipa el cap siguiente) salvo para acortarlas.
`ids_usados`: los ids que siguen sonando literales en el párrafo editado. `cambios`: uno por edición, con el número
de párrafo, el antes, el después y el motivo (corta, ritmo, repetición, relleno, orden). Un párrafo que no tocás va
igual y sin cambio.""" + (("\n\nCITA FUERTE, SILENCIO DESPUÉS (cortá estas frases-eco):\n" + "\n".join(f"- {x}" for x in notas))
                          if notas else "") + (("\n\nÚLTIMA FRASE DEL VIDEO: una cita o una pregunta, nunca un resumen "
                                                "(acá sí podés tocar la última frase, sin agregar nada):\n"
                                                + "\n".join(f"- {x}" for x in cierre)) if cierre else "")


# ═══════════════════════════════════════════════════════════════
#  Guardia léxica
# ═══════════════════════════════════════════════════════════════

_NUM = re.compile(r"\d[\d.,]*\d|\d")
_QUOTE = re.compile(r"[\"“«]([^\"”»]{3,})[\"”»]")


def _numbers(t: str) -> set[str]:
    from script_engine.m01a_escaleta import NUM_WORDS
    return {re.sub(r"[,.]", "", x) for x in _NUM.findall(t)} | set(NUM_WORDS.findall(ev.norm(t)))


def _names(t: str) -> set[str]:
    out = set()
    for s in re.split(r"(?<=[.!?…:])\s+|[\"“«]", t):
        ws = re.findall(r"[\wáéíóúñÁÉÍÓÚÑ]+", s)
        out |= {ev.norm(w) for w in ws[1:] if w[:1].isupper()}
    return out


def _adjs(t: str) -> set[str]:
    from script_engine.m05_narrative import adjectives
    return {ev.norm(a) for a in adjectives(t)}


GUARD_ALL = ("cifras", "nombres", "adjetivos", "citas")


def lexical_guard(before: str, after: str, checks: tuple[str, ...] = GUARD_ALL) -> list[str]:
    """Lo que el párrafo editado AGREGA respecto del original (cifras, nombres, adjetivos, citas). Vacío = pasa.
    F11b: `checks` elige qué se mide (la regeneración del v4 no mide adjetivos); por defecto, todo, como siempre."""
    out = []
    n = _numbers(after) - _numbers(before)
    if n and "cifras" in checks:
        out.append(f"cifras nuevas {sorted(n)}")
    nm = _names(after) - _names(before) - {ev.norm(w) for w in re.findall(r"[\wáéíóúñ]+", before)}
    if nm and "nombres" in checks:
        out.append(f"nombres nuevos {sorted(nm)}")
    a = _adjs(after) - _adjs(before) - {ev.norm(w) for w in re.findall(r"[\wáéíóúñ]+", before)}
    if a and "adjetivos" in checks:
        out.append(f"adjetivos nuevos {sorted(a)}")
    q = {ev.norm(x) for x in _QUOTE.findall(after)} - {ev.norm(x) for x in _QUOTE.findall(before)}
    if q and not all(any(x in ev.norm(before) for x in [y]) for y in q) and "citas" in checks:
        out.append(f"citas nuevas {sorted(q)[:2]}")
    return out


# ═══════════════════════════════════════════════════════════════
#  Edición con validación
# ═══════════════════════════════════════════════════════════════

def narration_tts(esc: dict, parrafos: list[dict], caps: list[dict], *, slowly_dev: bool = False) -> list[dict]:
    """F9 §3.3: `narration_tts` (etiquetas de v4: pausas, susurro en la frase de golpe, [slowly]) por cap, sobre los
    párrafos ya editados. `narration` no cambia. In place sobre `caps` (m01b_guionista.caps_text); devuelve `caps`."""
    from script_engine.tts_tags import caps_tts
    return caps_tts(esc, parrafos, caps, slowly_dev=slowly_dev)


