"""
script_engine/m01b_guionista.py — Módulo 01b v3 (F6c, HANDOFF_F6 §2.3): los validadores y utilidades de la narración
completa que usa el guion v4. F41 (DECISIONES 2026-10-27 20:59, una sola cadena): el guionista v3 (`write`, best_of_2
en una llamada a Gemini Pro, con su prompt `build_prompt`) se borró con la cadena vieja de fase1_5; escribe el guion
`guion_v4`.

    review(topic, esc, parrafos) → validadores duros y blandos de la narración completa (los de m05 por cap + v3)
    caps_text(esc, parrafos)     → [{"chapter_number", "narration", "datos_usados"}] (parte por el cap de cada beat)
    normalize, sentences, wc, _surname, _verified_antagonist   utilidades de guion_v4

Reglas que mide `review` (las del guion v3):
    gancho   frase 1 = la imagen del beat 1 (sin año, cifra ni institución); frase 2 = la promesa; el contexto, desde
             la frase 3; sin cifras en las 2 primeras
    ritmo    ≥ 1 frase de ≤ 6 palabras por beat; ninguna frase > 30 palabras; antes del pico, dos frases cortas seguidas
    humano   nombre y apellido + rol la primera vez; por nombre en ≥ 3 caps
    citas    literal, entre comillas, con el autor dentro de la oración; una cita SIN VERIFICAR va sin el nombre
    cifras   las `instrucciones_guionista` de la escaleta (517 una vez; nunca «más de 500»); nada de lo reservado o de
             `a_pantalla` en la voz
Validación (`review`): por cap, `m01b_narrator._validate_narration` (largo, primera oración, frases prohibidas) y
`m05_narrative.cap_review` (no inventar, datos asignados y declarados, una vez, contaminación, relleno, comillas,
canónica, reservados, fechas, cliffhanger; blandas: adjetivos, 3-gramas, densidad…); y las v3 de arriba.
m01b_narrator y m05 NO se modifican: se usan.
"""
from __future__ import annotations

import json
import re
from typing import Any

from script_engine import evidence as ev

MIN_WORDS_FACTOR = 0.85
SHORT_WORDS = 6
LONG_WORDS = 30
WORDS_TOL = 0.15
MIN_HUMAN_CAPS = 3
def institution_re(ficha: dict | None = None) -> re.Pattern:
    """F21: las instituciones del caso, no las de Orleans: las «personas» de la ficha que no son personas (organizaciones)
    más las palabras de organización de `nombres`; sin ficha, solo esas palabras. Es métrica."""
    from script_engine import nombres
    xs = [str(p.get("nombre") or "") for p in (ficha or {}).get("personas") or []
          if p.get("nombre") and not nombres.es_persona(p["nombre"])]
    alts = sorted({re.escape(x) for x in xs if len(x) >= 3} | set(nombres._ORG), key=len, reverse=True)
    return re.compile(r"(?<![^\W\d_])(?:" + "|".join(alts) + r")(?![^\W\d_])", re.I)


INSTITUTION = institution_re()                                          # F21: sin ficha, solo `nombres._ORG`


# ═══════════════════════════════════════════════════════════════
#  Prompt
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
#  Partición y revisión
# ═══════════════════════════════════════════════════════════════

def _beat_cap(esc: dict) -> dict[int, int]:
    return {b["n"]: b["cap"] for b in esc["beats"]}


def normalize(raw: dict, esc: dict, pool: dict | None = None) -> list[dict]:
    bc = _beat_cap(esc)
    out = []
    for p in (raw or {}).get("parrafos") or []:
        try:
            b = int(p.get("beat"))
        except (TypeError, ValueError):
            continue
        t = ev.fix_glued_caps(str(p.get("texto") or "").strip(), pool)
        if not t or b not in bc:
            continue
        out.append({"beat": b, "cap": bc[b], "texto": t,
                    "ids_usados": [str(x).strip().strip("[]").upper() for x in p.get("ids_usados") or [] if str(x).strip()]})
    return out


def caps_text(esc: dict, parrafos: list[dict]) -> list[dict]:
    out = []
    for n in range(1, 8):
        ps = [p for p in parrafos if p["cap"] == n]
        out.append({"chapter_number": n, "narration": "\n\n".join(p["texto"] for p in ps),
                    "datos_usados": list(dict.fromkeys(i for p in ps for i in p["ids_usados"]))})
    return out


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?…])[»”\"]?\s+", text.strip()) if s.strip()]


def wc(s: str) -> int:
    return len(re.findall(r"[\wáéíóúñü]+", s, re.I))


def _surname(name: str) -> str:
    from script_engine import nombres
    return nombres.apellido(name)                                       # F21: alias


def _verified_antagonist(esc: dict, pool: dict, sur: str) -> bool:
    """¿`sur` es el apellido del antagonista de la escaleta y algún dato o evento VERIFICADO del pool lo nombra?"""
    aid = (esc.get("antagonista") or {}).get("id")
    ant = next((p for p in pool.get("personajes") or [] if p.get("id") == aid), None)
    if not ant or not sur or ev.norm(_surname(ant["nombre"])) != ev.norm(sur):
        return False
    return any((it.get("verificacion") or {}).get("estado") == "verificada"
               and re.search(rf"\b{re.escape(ev.norm(sur))}\b", ev.norm(ev.text_of(it)))
               for k in ("datos", "cronologia") for it in pool.get(k) or [])


def review(topic: dict, esc: dict, parrafos: list[dict], ficha: dict | None = None) -> dict[str, Any]:
    """{"hard": [...], "soft": [...], "score": int, "por_cap": {n: {...}}} de la narración completa."""
    from script_engine.m01a_escaleta import count_variants, has_figure
    from script_engine.m01b_narrator import NarrationValidationError, _validate_narration
    from script_engine.m05_narrative import cap_review
    pool = topic["evidence_pool"]
    its = ev.items(pool)
    facts = topic.get("verified_facts") or []
    sk = {"chapters": esc.get("caps") or [], "personajes": []}
    hard: list[str] = []
    soft: list[str] = []
    score = 0
    por_cap: dict[int, Any] = {}
    caps = caps_text(esc, parrafos)
    # cobertura y orden
    beats_written = [p["beat"] for p in parrafos]
    missing = [b["n"] for b in esc["beats"] if b["n"] not in beats_written]
    if missing:
        hard.append(f"faltan los beats {missing}")
    if beats_written != sorted(beats_written):
        hard.append("los párrafos no siguen el orden de los beats")
    for k, c in enumerate(caps):
        n = c["chapter_number"]
        role = next((x["role"] for x in esc.get("caps") or [] if x["chapter_number"] == n), "development")
        ch_hard, ch_soft = [], []
        if not c["narration"]:
            hard.append(f"cap {n} vacío")
            continue
        try:
            _validate_narration(c["narration"], role=role, cap_number=n)
        except NarrationValidationError as e:
            if e.kind != "length":                   # el largo se mide en palabras (abajo): el mensaje lo entiende
                ch_hard.append(str(e))
        tgt = next((x.get("palabras_objetivo") for x in esc.get("caps") or [] if x["chapter_number"] == n), 0) or 0
        w = wc(c["narration"])
        if tgt and w < MIN_WORDS_FACTOR * tgt:
            ch_hard.append(f"{w} palabras: el mínimo del cap es {round(MIN_WORDS_FACTOR * tgt)} (objetivo {tgt}); "
                           "contá más hechos del beat con escenas, no adjetivos")
        elif tgt and w > (2 - MIN_WORDS_FACTOR) * tgt:
            ch_hard.append(f"{w} palabras: el máximo del cap es {round((2 - MIN_WORDS_FACTOR) * tgt)} (objetivo {tgt})")
        decl = ev.resolve_declared(c["datos_usados"], pool, facts, c["narration"])
        rv = cap_review(c["narration"], cap=n, pool=pool, skeleton=sk, previous=caps[:k], declared=decl, facts=facts)
        ch_hard += rv["hard"]
        ch_soft += rv["soft"]
        score += rv["score"]
        por_cap[n] = {"palabras": wc(c["narration"]), "duras": ch_hard, "blandas": ch_soft, "puntaje": rv["score"],
                      "objetivo": next((x.get("palabras_objetivo") for x in esc.get("caps") or []
                                        if x["chapter_number"] == n), None)}
        hard += [f"cap {n}: {x}" for x in ch_hard]
        soft += [f"cap {n}: {x}" for x in ch_soft]
    full = "\n\n".join(c["narration"] for c in caps)
    # gancho
    ss = sentences(caps[0]["narration"]) if caps and caps[0]["narration"] else []
    if ss:
        if has_figure(ss[0]):
            hard.append(f"gancho: la primera frase no lleva año, cifra ni institución: «{ss[0]}»")
        elif institution_re(ficha).search(ss[0]):           # F21: la institución es métrica
            soft.append(f"gancho: la primera frase no lleva institución: «{ss[0]}»")
        if len(ss) > 1 and has_figure(ss[1]):
            hard.append(f"gancho: la segunda frase (la promesa) no lleva cifras: «{ss[1]}»")
    # ritmo
    for b in esc["beats"]:
        bt = " ".join(p["texto"] for p in parrafos if p["beat"] == b["n"])
        if not bt:
            continue
        sl = [wc(s) for s in sentences(bt)]
        if not any(x <= SHORT_WORDS for x in sl):
            hard.append(f"beat {b['n']}: ninguna frase de {SHORT_WORDS} palabras o menos")
        long_ = [x for x in sl if x > LONG_WORDS]
        if long_:
            hard.append(f"beat {b['n']}: {len(long_)} frase(s) de más de {LONG_WORDS} palabras ({max(long_)})")
        tgt = b.get("palabras_objetivo") or 0
        w = wc(bt)
        if tgt and abs(w - tgt) > WORDS_TOL * tgt:
            soft.append(f"beat {b['n']}: {w} palabras (objetivo {tgt} ±15 %)")
    pk = (esc.get("pico") or {}).get("beat")
    if pk:
        before = [p["texto"] for p in parrafos if p["beat"] == pk - 1][-1:] + \
                 [p["texto"] for p in parrafos if p["beat"] == pk][:1]
        sl = [wc(s) for t in before for s in sentences(t)]
        if not any(a <= SHORT_WORDS and b2 <= SHORT_WORDS for a, b2 in zip(sl, sl[1:])):
            hard.append(f"antes del pico (beat {pk}): faltan dos frases cortas seguidas")
    # humano
    hum = esc.get("humano") or {}
    if hum.get("nombre") and not hum.get("colectivo"):
        sur = _surname(hum["nombre"])
        hc = [c["chapter_number"] for c in caps if re.search(rf"\b{re.escape(sur)}\b", ev.norm(c["narration"]))]
        if len(hc) < MIN_HUMAN_CAPS:
            hard.append(f"{hum['nombre']} aparece por nombre en los caps {hc}: tienen que ser ≥ {MIN_HUMAN_CAPS}")
    # citas sin verificar: sin el nombre de quien la dijo
    nf = ev.norm(full)
    for q in pool.get("citas") or []:
        v = q.get("verificacion") or {}
        if not v or v.get("estado") == "verificada":
            continue
        k = nf.find(ev.norm(q["texto"])[:40])
        if k < 0 and q.get("fragmento"):               # F7c-2: la voz cita el fragmento
            k = nf.find(ev.norm(q["fragmento"])[:40])
        if k < 0:
            continue
        from researcher_steps.verify_quotes import _named
        if not _named(q.get("autor") or ""):            # un anónimo («una presa de Conchetta») no tiene nombre que ocultar
            continue
        sur = _surname(q.get("autor") or "")
        if v.get("estado") == "verificada_parcial" and _verified_antagonist(esc, pool, sur):
            continue                                    # F7c-3 §9.1.3: el antagonista va con nombre
        if sur and len(sur) > 3 and re.search(rf"\b{re.escape(sur)}\b", nf[max(0, k - 200):k + len(q["texto"]) + 200]):
            hard.append(f"{q['id']} está SIN VERIFICAR y va con el nombre de {q.get('autor')}: decila sin el nombre")
    # F7c-2: reglas duras nuevas (citas por párrafo, gancho, juicios, nombre completo, repetición) y tope del video
    from script_engine.guion_v3_reglas import review_v3
    from script_engine.video_length import get as _len
    v3_hard, v3_soft = review_v3(caps, parrafos, pool, esc)
    hard += v3_hard
    soft += v3_soft
    tw = wc(full)
    if tw > _len("max_words"):
        hard.append(f"el video tiene {tw} palabras: el tope es {_len('max_words')}")
    # un conteo, una cifra (en todo el video)
    for g in count_variants(pool):
        n_canon = len(re.findall(rf"(?<![\d,.]){re.escape(g['num'])}(?![\d,.])", full))
        if n_canon > 1:
            hard.append(f"la cifra {g['num']} suena {n_canon} veces en el video: una sola")
        others = [x for x in g["otras"] if re.search(rf"(?<![\d,.]){re.escape(x)}(?![\d,.])", full)]
        if others:
            hard.append(f"otra cifra del conteo {g['num']} en la voz: {others}")
    return {"hard": hard, "soft": soft, "score": score, "por_cap": por_cap}


# ═══════════════════════════════════════════════════════════════
#  Escritura (best_of_2)
# ═══════════════════════════════════════════════════════════════

