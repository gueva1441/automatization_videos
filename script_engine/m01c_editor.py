"""
script_engine/m01c_editor.py — Módulo 01c v3 (F6c, HANDOFF_F6 §2.4): el editor APRIETA la narración del guionista.

Una llamada a Gemini Pro con la narración completa (párrafo por párrafo, con su beat) y la escaleta. Solo puede
cortar, reordenar frases dentro del beat, acortar, quitar repeticiones y relleno y reforzar el ritmo (partir una frase
larga, dejar una corta antes del golpe). NO puede agregar datos, cifras, nombres, adjetivos ni citas. Devuelve el
texto editado (mismos párrafos, mismo orden) + `cambios[]` (antes/después/motivo) para auditoría.

Después del editor corren TODOS los validadores duros otra vez. Por párrafo (`edit`):
    1. guardia léxica   el párrafo editado no trae cifras (dígitos o en letras), nombres propios, adjetivos ni citas
                        entre comillas que el original no tenía
    2. validadores      se aplica sobre el texto aceptado hasta ahí; si el cap queda con MÁS problemas duros
                        (m01b_guionista.review: los de m05 por cap + gancho, ritmo, humano, citas sin verificar,
                        un conteo una cifra), el párrafo se rechaza
Un párrafo rechazado vuelve al original del guionista; nunca se rechaza el video.
"""
from __future__ import annotations

import re
from typing import Any, Callable

from script_engine import evidence as ev

PROMPT_VERSION = "f8-1"            # f8-1: cierre del video en cita o pregunta (blanda, F8 §2)

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


def lexical_guard(before: str, after: str) -> list[str]:
    """Lo que el párrafo editado AGREGA respecto del original (cifras, nombres, adjetivos, citas). Vacío = pasa."""
    out = []
    n = _numbers(after) - _numbers(before)
    if n:
        out.append(f"cifras nuevas {sorted(n)}")
    nm = _names(after) - _names(before) - {ev.norm(w) for w in re.findall(r"[\wáéíóúñ]+", before)}
    if nm:
        out.append(f"nombres nuevos {sorted(nm)}")
    a = _adjs(after) - _adjs(before) - {ev.norm(w) for w in re.findall(r"[\wáéíóúñ]+", before)}
    if a:
        out.append(f"adjetivos nuevos {sorted(a)}")
    q = {ev.norm(x) for x in _QUOTE.findall(after)} - {ev.norm(x) for x in _QUOTE.findall(before)}
    if q and not all(any(x in ev.norm(before) for x in [y]) for y in q):
        out.append(f"citas nuevas {sorted(q)[:2]}")
    return out


# ═══════════════════════════════════════════════════════════════
#  Edición con validación
# ═══════════════════════════════════════════════════════════════

def _cap_hard(review: dict, cap: int) -> int:
    pc = review["por_cap"].get(cap) or {}
    glob = [h for h in review["hard"] if not h.startswith("cap ")]
    return len(pc.get("duras") or []) + len(glob)


def edit(topic: dict, esc: dict, parrafos: list[dict], *, call: Callable[..., dict] | None = None,
         log: list[str] | None = None) -> dict[str, Any]:
    """{"parrafos": aceptados, "cambios": [...con estado], "revision_antes", "revision_despues"}."""
    from script_engine import m01b_guionista as mg
    log = log if log is not None else []
    if call is None:
        from gemini_helpers import call_pro_json as call
    from script_engine.guion_v3_reglas import closing_soft, echo_soft
    raw = call(build_prompt(esc, parrafos, echo_soft(parrafos), closing_soft(parrafos)), system_instruction=SYSTEM,
               response_schema=SCHEMA,
               description="m01c_editor")
    edited = raw.get("parrafos") or []
    cambios_llm = raw.get("cambios") or []
    before_rv = mg.review(topic, esc, parrafos)
    out = [dict(p) for p in parrafos]
    estado = []
    if len(edited) != len(parrafos):
        log.append(f"  [editor] devolvió {len(edited)} párrafos (se esperaban {len(parrafos)}): se conserva el original")
        return {"parrafos": out, "cambios": [{**c, "estado": "rechazado", "motivo_rechazo": "cantidad de párrafos"}
                                            for c in cambios_llm],
                "revision_antes": before_rv, "revision_despues": before_rv, "aceptados": 0}
    cur_rv = before_rv
    for k, (orig, e) in enumerate(zip(parrafos, edited)):
        new_t = ev.fix_glued_caps(str(e.get("texto") or "").strip())
        if not new_t or new_t == orig["texto"]:
            continue
        rec = {"parrafo": k, "beat": orig["beat"], "antes": orig["texto"], "despues": new_t}
        lg = lexical_guard(orig["texto"], new_t)
        if lg:
            estado.append({**rec, "estado": "rechazado", "motivo_rechazo": "; ".join(lg)})
            continue
        trial = [dict(p) for p in out]
        ids = [str(x).strip().strip("[]").upper() for x in e.get("ids_usados") or [] if str(x).strip()]
        trial[k] = {**orig, "texto": new_t, "ids_usados": ids or orig["ids_usados"]}
        rv = mg.review(topic, esc, trial)
        if _cap_hard(rv, orig["cap"]) > _cap_hard(cur_rv, orig["cap"]) or len(rv["hard"]) > len(cur_rv["hard"]):
            new_h = [h for h in rv["hard"] if h not in cur_rv["hard"]]
            estado.append({**rec, "estado": "rechazado", "motivo_rechazo": "validadores: " + "; ".join(new_h[:3])})
            continue
        out, cur_rv = trial, rv
        estado.append({**rec, "estado": "aceptado"})
    motivo = {int(c.get("parrafo", -1)): c.get("motivo") for c in cambios_llm if isinstance(c, dict)}
    for s in estado:
        s["motivo"] = motivo.get(s["parrafo"]) or ""
    n_ok = sum(1 for s in estado if s["estado"] == "aceptado")
    log.append(f"  [editor] {len(estado)} párrafo(s) editado(s): {n_ok} aceptado(s), {len(estado) - n_ok} rechazado(s) · "
               f"duras {len(before_rv['hard'])} → {len(cur_rv['hard'])}")
    return {"parrafos": out, "cambios": estado, "cambios_llm": cambios_llm, "revision_antes": before_rv,
            "revision_despues": cur_rv, "aceptados": n_ok, "prompt_version": PROMPT_VERSION}
