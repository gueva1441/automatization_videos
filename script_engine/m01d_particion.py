"""
script_engine/m01d_particion.py — F10 §2: de los párrafos v3 (escaleta → guionista → editor) al CONTRATO de 7 caps que
lee todo lo de río abajo (m02_5, audio, m07, m03, assemble, fase2a/2b, gfx).

Escribe en data/scripts/_steps/<topic>/ los mismos archivos que dejaban m01a_skeleton + m01b_narrator:
    01a_skeleton.json   chapters[7]: chapter_number, title, role, render_engine, duration_seconds, narrative_intent,
                        bullets, evidence_ids, cliffhanger, pantalla_ids (+ personajes, _pool_plan, `_v3`)
    01b_narration.json  chapters[7]: chapter_number, narration, datos_usados (+ ids_usados, narration_tts)
                        y humanizer_phrases ([]: v3 no usa frases de humanizador)
    01b_narracion_v3.json  parrafos + caps (lo que lee m03 v3 para el ancla por beat)
Solo AGREGA campos (`ids_usados`, `narration_tts`); los de siempre quedan con el mismo nombre y tipo.

Partición: cada párrafo va al cap de su beat (la escaleta ya repartió beat → cap). Largo por cap contra
`m01b_narrator._len_range(role)` ±15 %: si un cap se pasa, su último párrafo pasa al cap siguiente solo si no es del
beat del pico, el cap no se queda sin párrafos y el cap que lo recibe no se pasa; si no, el editor lo acorta (una
llamada, misma regla de no agregar nada). Un cap corto queda como aviso (no se inventa texto).
`title`: una llamada Flash corta (7 títulos de ≤ 5 palabras desde la escaleta, sin cifras ni nombres nuevos); si
falla, la imagen sensorial del primer beat del cap, recortada.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Callable

from script_engine import m01b_guionista as mg
from script_engine.m01a_skeleton import CHAPTER_SCHEMA, DEFAULT_INTENT_BY_CAP, STEPS_DIR

LEN_TOL = 0.15
TITLE_MAX_WORDS = 5


def len_range(role: str) -> tuple[int, int]:
    """Rango de caracteres del cap: el de m01b_narrator ±15 % (F10 §2)."""
    from script_engine.m01b_narrator import _len_range
    lo, hi = _len_range(role)
    return int(lo * (1 - LEN_TOL)), int(hi * (1 + LEN_TOL))


def _caps_of(parrafos: list[dict]) -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {n: [] for n in range(1, 8)}
    for p in parrafos:
        out[int(p["cap"])].append(p)
    return out


def _cap_len(ps: list[dict]) -> int:
    return len("\n\n".join(p["texto"] for p in ps))


def rebalance(esc: dict, parrafos: list[dict], *, shorten: Callable[[str, int], str] | None = None
              ) -> tuple[list[dict], list[str]]:
    """Párrafos con `cap` ajustado a los rangos de largo. Devuelve (párrafos, notas)."""
    ps = [dict(p) for p in parrafos]
    roles = {c["chapter_number"]: c["role"] for c in CHAPTER_SCHEMA}
    pico = int((esc.get("pico") or {}).get("beat") or 0)
    notes: list[str] = []
    for n in range(1, 8):
        caps = _caps_of(ps)
        lo, hi = len_range(roles[n])
        if _cap_len(caps[n]) <= hi:
            continue
        last = caps[n][-1] if caps[n] else None
        if (last and n < 7 and last["beat"] != pico and len(caps[n]) > 1
                and _cap_len(caps[n + 1]) + len(last["texto"]) + 2 <= len_range(roles[n + 1])[1]):
            last["cap"] = n + 1
            notes.append(f"cap {n}: {_cap_len(caps[n])} caracteres > {hi} → el último párrafo (beat {last['beat']}) "
                         f"pasa al cap {n + 1}")
            continue
        if shorten is not None and last is not None:
            over = _cap_len(caps[n]) - hi
            target = max(200, len(last["texto"]) - over - 40)
            new = shorten(last["texto"], target)
            if new and len(new) < len(last["texto"]):
                notes.append(f"cap {n}: {_cap_len(caps[n])} caracteres > {hi} → el editor acortó el último párrafo "
                             f"({len(last['texto'])} → {len(new)})")
                last["texto"] = new
                continue
        notes.append(f"cap {n}: {_cap_len(caps[n])} caracteres > {hi} y no se pudo mover ni acortar (aviso)")
    caps = _caps_of(ps)
    for n in range(1, 8):
        lo, hi = len_range(roles[n])
        if _cap_len(caps[n]) < lo:
            notes.append(f"cap {n}: {_cap_len(caps[n])} caracteres < {lo} (corto; aviso, no se inventa texto)")
    # orden estable: por cap y, dentro del cap, por beat y por el orden original
    order = {id(p): k for k, p in enumerate(ps)}
    ps.sort(key=lambda p: (int(p["cap"]), order[id(p)]))
    return ps, notes


def editor_shorten(call: Callable[..., dict] | None = None) -> Callable[[str, int], str]:
    """El editor acorta UN párrafo a ≈ `target` caracteres sin agregar nada (guardia léxica de m01c)."""
    from script_engine.m01c_editor import lexical_guard

    def _do(text: str, target: int) -> str:
        nonlocal call
        if call is None:
            from gemini_helpers import call_pro_json as call
        raw = call(f"""Acortá este párrafo de un documental a unos {target} caracteres (hoy tiene {len(text)}).
SOLO cortar: frases que repiten, relleno, calificativos. NUNCA agregar datos, cifras, fechas, nombres, adjetivos ni
citas; cada cifra, fecha, nombre y cita que quede, literal. La última frase se queda.

PÁRRAFO:
{text}""", response_schema={"type": "OBJECT", "properties": {"texto": {"type": "STRING"}}, "required": ["texto"]},
                   description="m01d_particion: acortar")
        new = str((raw or {}).get("texto") or "").strip()
        return new if new and not lexical_guard(text, new) else text
    return _do


TITLES_SCHEMA = {"type": "OBJECT", "properties": {"titulos": {"type": "ARRAY", "items": {"type": "STRING"}}},
                 "required": ["titulos"]}


def _title_fallback(beats: list[dict]) -> str:
    img = re.sub(r"[.,;:]+$", "", str((beats[0] if beats else {}).get("imagen_sensorial") or "").strip())
    words = img.split()
    return (" ".join(words[:TITLE_MAX_WORDS]) or "Capítulo").capitalize()


def titles(esc: dict, *, call: Callable[..., dict] | None = None) -> tuple[list[str], str]:
    """7 títulos de cap (≤ 5 palabras, sin cifras, sin nombres que no estén en la escaleta). Se ven en el title card."""
    by_cap = {n: [b for b in esc["beats"] if b["cap"] == n] for n in range(1, 8)}
    fb = [_title_fallback(by_cap[n]) for n in range(1, 8)]
    lines = "\n".join(f"CAP {n}: " + " / ".join(f"{b.get('funcion')}: {b.get('imagen_sensorial')}" for b in by_cap[n])
                      for n in range(1, 8))
    try:
        if call is None:
            from gemini_helpers import call_flash_json as call
        raw = call(f"""Títulos de capítulo para un documental en español (se leen en pantalla al abrir cada cap).
Uno por cap, en orden, de 2 a {TITLE_MAX_WORDS} palabras, concretos (un objeto, un lugar, un momento), sin cifras, sin
fechas, sin nombres propios de personas y sin signos de pregunta. Basate en lo que se ve en cada cap:
{lines}""", response_schema=TITLES_SCHEMA, description="m01d_particion: títulos") or {}
        ts = [str(t).strip().strip('".«»') for t in raw.get("titulos") or []]
    except Exception:  # noqa: BLE001 — sin títulos del LLM: los de respaldo
        return fb, "respaldo"
    if len(ts) != 7:
        return fb, "respaldo"
    out, src = [], "flash"
    for t, f in zip(ts, fb):
        ok = t and len(t.split()) <= TITLE_MAX_WORDS and not re.search(r"\d|\?", t)
        out.append(t if ok else f)
        src = src if ok else "mixto"
    return out, src


def build_contract(topic: dict, esc: dict, parrafos: list[dict], pool: dict, *, title_list: list[str] | None = None,
                   slowly_dev: bool = False) -> tuple[dict, dict, dict]:
    """(skeleton, narration, narracion_v3) con el contrato de 7 caps. `parrafos` ya repartidos (rebalance)."""
    from script_engine.m01a_escaleta import caps_view
    from script_engine.m01c_editor import narration_tts
    cv = {c["chapter_number"]: c for c in caps_view(esc)["chapters"]}
    esc_caps = {c["chapter_number"]: c for c in esc.get("caps") or []}
    title_list = title_list or [_title_fallback([b for b in esc["beats"] if b["cap"] == n]) for n in range(1, 8)]
    its = {**{d["id"]: d for d in pool.get("datos") or []}, **{c["id"]: c for c in pool.get("cronologia") or []},
           **{q["id"]: q for q in pool.get("citas") or []}}

    def _txt(i: str) -> str:
        it = its.get(i) or {}
        return str(it.get("texto") or it.get("evento") or "").strip()
    chapters = []
    for c in CHAPTER_SCHEMA:
        n = c["chapter_number"]
        ec, vc = esc_caps.get(n) or {}, cv.get(n) or {}
        bs = [b for b in esc["beats"] if b["cap"] == n]
        chapters.append({
            "chapter_number": n, "title": title_list[n - 1], "role": c["role"],
            "render_engine": ec.get("render_engine") or c.get("render_engine"),
            "duration_seconds": ec.get("duration_seconds") or c.get("duration_seconds"),
            "narrative_intent": ec.get("narrative_intent") or DEFAULT_INTENT_BY_CAP[n],
            "bullets": [f"{b.get('imagen_sensorial')} · {_txt(b['dato_central']) or b['dato_central']}" for b in bs],
            "evidence_ids": ec.get("evidence_ids") or vc.get("evidence_ids") or [],
            "cliffhanger": ec.get("cliffhanger") if ec.get("cliffhanger") is not None else vc.get("cliffhanger", ""),
            "pantalla_ids": ec.get("pantalla_ids") or [],
        })
    pers = {p.get("id"): p for p in pool.get("personajes") or []}
    hum = esc.get("humano") or {}
    ant = str((esc.get("antagonista") or {}).get("id") or "")
    personajes = []
    for pid in [str(hum.get("id") or ""), ant]:
        p = pers.get(pid)
        if p:
            first = next((b["cap"] for b in esc["beats"]
                          if p["nombre"].split()[-1].lower() in json.dumps(b, ensure_ascii=False).lower()), 1)
            personajes.append({"id": pid, "nombre": p["nombre"], "rol": p.get("rol") or "",
                               "antagonista": pid == ant, "entra_en_cap": first})
    skeleton = {"topic_id": topic.get("id") or topic.get("topic_id"), "chapters": chapters, "personajes": personajes,
                "_pool_plan": esc.get("_pool_plan") or {},
                "_v3": {"escaleta": "01a_escaleta.json", "prompt_version": esc.get("prompt_version"),
                        "humano": hum, "antagonista": esc.get("antagonista"), "pico": esc.get("pico")}}
    caps = narration_tts(esc, parrafos, mg.caps_text(esc, parrafos), slowly_dev=slowly_dev)
    narr_chapters = []
    for c in caps:
        narr_chapters.append({"chapter_number": c["chapter_number"], "narration": c["narration"],
                              "datos_usados": c["datos_usados"], "ids_usados": c["datos_usados"],
                              "narration_tts": c["narration_tts"]})
    narration = {"topic_id": skeleton["topic_id"], "chapters": narr_chapters, "humanizer_phrases": [],
                 "_v3": {"tts_tags": {c["chapter_number"]: c["tts_tags"] for c in caps}}}
    narracion_v3 = {"topic_id": skeleton["topic_id"], "parrafos": parrafos, "caps": caps}
    return skeleton, narration, narracion_v3


def particionar(topic: dict, esc: dict, parrafos: list[dict], pool: dict, *, persist: bool = True,
                call_titles: Callable[..., dict] | None = None, shorten: Callable[[str, int], str] | None = None,
                log: list[str] | None = None) -> dict[str, Any]:
    """Rebalance + títulos + contrato; persiste los 3 archivos. Devuelve {skeleton, narration, narracion_v3, notas}."""
    log = log if log is not None else []
    ps, notes = rebalance(esc, copy.deepcopy(parrafos), shorten=shorten)
    tl, src = titles(esc, call=call_titles)
    sk, na, n3 = build_contract(topic, esc, ps, pool, title_list=tl)
    sk["_v3"]["particion"] = {"notas": notes, "titulos": src}
    for x in notes:
        log.append(f"  [01d] {x}")
    if persist:
        d = STEPS_DIR / sk["topic_id"]
        d.mkdir(parents=True, exist_ok=True)
        for name, obj in (("01a_skeleton.json", sk), ("01b_narration.json", na), ("01b_narracion_v3.json", n3)):
            (d / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    empty = [c["chapter_number"] for c in na["chapters"] if not c["narration"].strip()]
    if empty:                                       # F10: un cap sin texto rompe el audio y todo lo de abajo
        raise ParticionError(f"caps sin narración: {empty} (el guionista no escribió sus beats); los archivos quedan "
                             f"escritos para leerlos, pero la cadena no sigue")
    return {"skeleton": sk, "narration": na, "narracion_v3": n3, "notas": notes}


class ParticionError(ValueError):
    """La partición dejó un cap sin narración: la cadena no puede seguir a audio."""


def regenerate_cap(topic: dict, esc: dict, parrafos: list[dict], cap: int, *,
                   call: Callable[..., dict] | None = None, log: list[str] | None = None) -> list[dict]:
    """F10 §2 «regenerate_caps v3»: rehace UN cap con el editor (escaleta + texto vecino), no con el guionista entero.
    Devuelve los párrafos con los del cap editados (los demás, intactos)."""
    from script_engine import m01c_editor as mc
    idx = [k for k, p in enumerate(parrafos) if p["cap"] == cap]
    ctx = [k for k, p in enumerate(parrafos) if p["cap"] in (cap - 1, cap, cap + 1)]
    sub = [parrafos[k] for k in ctx]
    res = mc.edit(topic, esc, sub, call=call, log=log)
    out = [dict(p) for p in parrafos]
    for k_sub, k in enumerate(ctx):
        if k in idx:
            out[k] = res["parrafos"][k_sub]
    return out
