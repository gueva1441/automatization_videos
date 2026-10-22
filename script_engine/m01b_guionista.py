"""
script_engine/m01b_guionista.py — Módulo 01b v3 (F6c, HANDOFF_F6 §2.3): el guionista escribe la narración COMPLETA de
corrido, sabiendo a dónde va (escaleta), en UNA llamada a Gemini Pro. best_of_2 sobre el texto entero.

    write(topic, esc)       → {"parrafos": [{"beat", "cap", "texto", "ids_usados"}], "revision": {...}, "_intentos": [...]}
    review(topic, esc, parrafos) → validadores duros y blandos de la narración completa (los de m05 por cap + v3)
    caps_text(esc, parrafos)     → [{"chapter_number", "narration", "datos_usados"}] (parte por el cap de cada beat)

Reglas: las de prosa del narrador v2 (`m01b_narrator._prose_rules`, conectores y aperturas prohibidas, relleno
prohibido de m05) + las de v3:
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
from typing import Any, Callable

from script_engine import evidence as ev

PROMPT_VERSION = "f7c3-1"            # f7c3-1: + rol, párrafo con dato, antagonista con nombre, sin fotos ni tráiler, ancla
PARA_WORDS = (55, 80)
EXTRA_PER_CAP = 3
MIN_WORDS_FACTOR = 0.85
BEST_OF = 2
SHORT_WORDS = 6
LONG_WORDS = 30
WORDS_TOL = 0.15
MIN_HUMAN_CAPS = 3
INSTITUTION = re.compile(r"\b(prisi[oó]n|c[aá]rcel de|parish|opp|departamento|aclu|human rights|sheriff|"
                         r"cuerpo de ingenieros|jurado|tribunal|gobierno|fema|alcald[ií]a)\b", re.I)

SYSTEM = ("Sos el guionista de un canal de documentales de misterio en YouTube. Escribís para que el espectador se quede "
          "al segundo siguiente: imágenes concretas, frases cortas antes del golpe, un humano con nombre. Tenés la "
          "escaleta entera: sabés a dónde vas y podés plantar en un beat lo que pagás en otro. No inventás nada: cada "
          "cifra, fecha, nombre y cita sale literal de la investigación. Respondés SOLO JSON.")

SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {"parrafos": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
        "beat": {"type": "INTEGER"}, "texto": {"type": "STRING"},
        "ids_usados": {"type": "ARRAY", "items": {"type": "STRING"}}},
        "required": ["beat", "texto", "ids_usados"]}}},
    "required": ["parrafos"],
}


# ═══════════════════════════════════════════════════════════════
#  Prompt
# ═══════════════════════════════════════════════════════════════

def _item_line(i: str, its: dict) -> str:
    it = its.get(i)
    if not it:
        return f"[{i}] (no existe)"
    txt = ev.text_of(it)
    if it["_kind"] == "citas":
        v = it.get("verificacion") or {}
        mark = "" if not v else (" · VERIFICADA: con nombre" if v.get("estado") == "verificada"
                                 else " · SIN VERIFICAR: sin el nombre de quien la dijo")
        frag = it.get("fragmento")
        if frag and frag != txt:                    # F7c-2: literal SOLO el fragmento; el resto, parafraseado
            return (f'[{i}] CITA «{frag}» — {it.get("autor")}{mark} · entre comillas va SOLO este fragmento, palabra '
                    f'por palabra, con quién lo dijo; el resto de lo que contó, con tus palabras: «{txt}»')
        return f'[{i}] CITA «{txt}» — {it.get("autor")}{mark} · se copia ENTERA, palabra por palabra, o no se usa'
    extra = f" ({it['fecha']})" if it.get("fecha") else ""
    lit = " / ".join(f"«{a}»" for a in ev.anchors(it))
    return f"[{i}] {txt}{extra}" + (f" · tiene que sonar literal: {lit}" if lit else "")


def extra_material(esc: dict, pool: dict) -> dict[int, list[str]]:
    """Por cap, hasta EXTRA_PER_CAP datos del pool que la escaleta no usa y que se relacionan con sus beats (≥ 2
    palabras de contenido en común con sus datos o su imagen): material opcional para llenar el largo con hechos. Nunca
    lo reservado para pantalla, lo de `a_pantalla`, otras cifras de un conteo ni citas sin verificar."""
    from script_engine.m01a_escaleta import count_variants
    its = ev.items(pool)
    used = {i for b in esc["beats"] for i in [b["dato_central"]] + b["datos_apoyo"]}
    banned = used | {i for c in esc.get("caps") or [] for i in c.get("pantalla_ids") or []}
    banned |= {x["id"] for x in esc.get("a_pantalla") or []}
    banned |= {v for g in count_variants(pool) for v in g["variantes"]}
    out: dict[int, list[str]] = {}
    taken: set[str] = set()
    for n in range(1, 8):
        bs = [b for b in esc["beats"] if b["cap"] == n]
        ctx = set().union(*[ev._content(" ".join([b["imagen_sensorial"]] + [ev.text_of(its[i]) for i in
                                                   [b["dato_central"]] + b["datos_apoyo"] if i in its])) for b in bs]) \
            if bs else set()
        cands = []
        for i, it in its.items():
            if i in banned or i in taken or it["_kind"] not in ("datos", "cronologia", "citas"):
                continue
            v = it.get("verificacion") or {}
            if it["_kind"] == "citas" and v and v.get("estado") != "verificada":
                continue
            sc = len(ev._content(ev.text_of(it)) & ctx)
            if sc >= 2:
                cands.append((sc, i))
        out[n] = [i for _, i in sorted(cands, key=lambda x: (-x[0], x[1]))[:EXTRA_PER_CAP]]
        taken |= set(out[n])
    return out


def beats_section(esc: dict, pool: dict) -> str:
    its = ev.items(pool)
    caps = {c["chapter_number"]: c for c in esc.get("caps") or []}
    from script_engine.m05_narrative import entity_terms
    extra = extra_material(esc, pool)
    out = []
    for n in range(1, 8):
        c = caps.get(n, {})
        scr = c.get("pantalla_ids") or []
        tgt = c.get("palabras_objetivo") or 0
        out.append(f"── CAP {n} ({c.get('role')}, {tgt} palabras: MÍNIMO {round(MIN_WORDS_FACTOR * tgt)})"
                   + (f" · NO DECIR (va en pantalla): {', '.join(scr)}" if scr else ""))
        bs = [b for b in esc["beats"] if b["cap"] == n]
        for i in extra.get(n) or []:
            out.append(f"  material extra (opcional; si lo usás, literal y en ids_usados): {_item_line(i, its)}")
        for b in bs:
            flags = [x for x, on in (("FLASH-FORWARD", b.get("flash_forward")), ("contador en pantalla", b.get("contador")),
                                     ("humano en escena", b.get("humano_en_escena"))) if on]
            k = max(1, round((b["palabras_objetivo"] or 0) / 65))
            out.append(f"  BEAT {b['n']} · {b['funcion']} · {b['emocion']} · intensidad {b['intensidad']} · "
                       f"≈ {b['palabras_objetivo']} palabras = {k} párrafo(s) de {PARA_WORDS[0]}–{PARA_WORDS[1]} palabras"
                       + (f" · {', '.join(flags)}" if flags else ""))
            out.append(f"    imagen: {b['imagen_sensorial']}")
            out.append(f"    dato central: {_item_line(b['dato_central'], its)}")
            for i in b.get("datos_apoyo") or []:
                out.append(f"    apoyo: {_item_line(i, its)}")
            out.append(f"    queda abierta: {b['pregunta_abierta']}")
            if b.get("cierre"):
                out.append(f"    cierre: {b['cierre']}")
            cl = c.get("cliffhanger")
            if b is bs[-1] and n <= 6 and cl in its:
                terms = entity_terms(its[cl])[:5]
                out.append(f"    CIERRE DEL CAP (obligatorio): la última frase del cap nombra el dato del cap {n + 1} "
                           f"— al menos uno de: {', '.join('«' + t + '»' for t in terms)}")
    return "\n".join(out)


def build_prompt(topic: dict, esc: dict, feedback: list[str] | None = None) -> str:
    from script_engine.m01b_narrator import FORBIDDEN_CLOSINGS, FORBIDDEN_OPENINGS, GENERIC_CONNECTORS, _prose_rules
    from script_engine.m05_narrative import FORBIDDEN_FILLER
    pool = topic["evidence_pool"]
    hum = esc.get("humano") or {}
    pico = (esc.get("pico") or {}).get("beat")
    ins = "\n".join(f"- {x}" for x in esc.get("instrucciones_guionista") or []) or "- (ninguna)"
    fb = ""
    if feedback:
        fb = ("\n═══ TU VERSIÓN ANTERIOR NO PASÓ. CORREGÍ ESTO (sin perder datos ni nombres) ═══\n"
              + "\n".join(f"- {x}" for x in feedback) + "\n")
    return f"""TEMA: {topic.get("video_title")}
HUMANO QUE SEGUIMOS: {hum.get("nombre")} ({hum.get("rol")})
PROMESA DEL GANCHO: {esc.get("promesa_gancho")}
PICO: beat {pico} · CIERRE HUMANO: {esc.get("cierre_humano")}

═══ ESCALETA (la historia ya está decidida: escribila) ═══
{beats_section(esc, pool)}

═══ INSTRUCCIONES DE LA ESCALETA (deterministas, se validan) ═══
{ins}

═══ CÓMO ESCRIBIR ═══
1. La narración COMPLETA, de corrido, en párrafos. Cada párrafo lleva su `beat`; cada beat, EXACTAMENTE los párrafos
   que dice la escaleta, cada uno de {PARA_WORDS[0]}–{PARA_WORDS[1]} palabras (contalas).
   LARGO: cada beat suma sus palabras objetivo (±15 %); cada cap, al menos su MÍNIMO. El video entero son ≈
   {sum(b["palabras_objetivo"] for b in esc["beats"])} palabras: un texto corto se rechaza. El largo se llena con
   hechos del beat contados con escenas y tus palabras, no con adjetivos.
2. GANCHO: la frase 1 es la imagen del beat 1 (sin año, sin cifra, sin nombre de institución, ≤ 12 palabras); la
   frase 2 es la promesa. Nada de contexto («En 2005, el huracán Katrina…») hasta la frase 3. Sin cifras en las dos
   primeras frases.
3. RITMO: en cada beat, al menos una frase de {SHORT_WORDS} palabras o menos. Ninguna frase de más de {LONG_WORDS}
   palabras. Justo antes del pico (beat {pico}), dos frases cortas seguidas.
4. HUMANO: {hum.get("nombre")} con nombre y apellido y su rol la primera vez; después, por su nombre, en al menos
   {MIN_HUMAN_CAPS} caps (los beats «humano en escena»).
5. DATOS: toda cifra, fecha, nombre y cita sale LITERAL de los datos del beat («tiene que sonar literal»: eso, tal
   cual, o el dato no cuenta). Cada dato se dice UNA vez; después se parafrasea sin la cifra. Cada evento con su fecha;
   nunca fundas dos fechas. No inventes NADA. Un dato que no podés decir literal, no lo pongas en ids_usados.
6. CITAS: entre comillas va SOLO el fragmento de la cita (≤ 25 palabras), copiado literal, con el autor DENTRO de la
   oración («dijo Vincent Norman»), nunca como firma; lo demás que contó, con tus palabras. UNA cita literal por
   párrafo como máximo. Una cita SIN VERIFICAR va sin el nombre de quien la dijo («un preso de diecinueve años
   contó: «…»»).
7. Lo que dice «NO DECIR (va en pantalla)» no lo dice la voz.
8. El último párrafo de cada cap 1–6 anticipa el dato CONCRETO del cap siguiente (lo nombra o lo deja incompleto).
   La última frase del video es la del cierre del último beat (con tus palabras, sin repetir una cita textual).
9. Adjetivos: entre 2 y 4 cada 100 palabras, atados a hechos (cómo era el agua, la celda, el calor).
10. Prohibido el relleno: {", ".join(FORBIDDEN_FILLER)}. Prohibidos los conectores genéricos
    ({", ".join(GENERIC_CONNECTORS[:8])}…), las aperturas ({", ".join(FORBIDDEN_OPENINGS[:4])}…) y los cierres
    ({", ".join(FORBIDDEN_CLOSINGS[:4])}…).
11. `ids_usados` de cada párrafo: los ids del pool cuya cifra, fecha, nombre o cita suena LITERAL en ese párrafo.
12. GANCHO (cap 1) = flash-forward sensorial del peor momento (el beat 1): lo que se ve, se oye, se huele adentro.
    Nunca describe una foto ni da la fecha de una foto; no adelanta citas que suenan en caps siguientes.
13. SOLO HECHOS, CITAS Y PREGUNTAS: ninguna interpretación ni juicio tuyo que no esté en los datos («caos
    deliberado», «no eran considerados humanos», «el colapso de la humanidad»). Si querés que el espectador juzgue,
    dale el hecho o preguntá.
14. {hum.get("nombre")}: nombre completo UNA vez por cap como mucho; después, solo el apellido.
15. No repitas entre caps una frase de 3 o más palabras ya dicha: cada cap lo cuenta con palabras nuevas.
16. ROL: a quien habla se lo presenta con SU rol del pool (preso, guardia, oficial…), nunca con otro. Si no sabés el
    rol, sin rol.
17. Todo párrafo lleva al menos un dato del pool (su id en `ids_usados`); un párrafo sin dato solo puede ser una
    transición de 2 frases como mucho. Nada de párrafos de atmósfera.
18. ANTAGONISTA CON NOMBRE: si el beat trae un hecho verificado que lo nombra (su decisión, su reunión), decí su
    nombre, aunque su cita esté sin verificar. Nunca «según alguien», «una voz oficial».
19. Ninguna foto ni imagen en ningún cap («las imágenes dieron la vuelta al mundo», «una fotógrafa tomó la foto»):
    contá la escena.
20. Sin voz de tráiler: el narrador no habla del video («esta es la historia de…», «lo que sigue», «los testigos que
    se negaron a olvidar»).
21. GANCHO: una frase corta con la ciudad y el año («Nueva Orleans, agosto de 2005.») antes de la segunda cita; es la
    única fecha del cap 1.
22. Después de una cita fuerte, silencio: no la cierres con una frase-eco («Era la única opción.»).

{_prose_rules(topic)}
{fb}
Devolvé {{"parrafos": [{{"beat": 1, "texto": "…", "ids_usados": ["Q13"]}}, …]}}."""


# ═══════════════════════════════════════════════════════════════
#  Partición y revisión
# ═══════════════════════════════════════════════════════════════

def _beat_cap(esc: dict) -> dict[int, int]:
    return {b["n"]: b["cap"] for b in esc["beats"]}


def normalize(raw: dict, esc: dict) -> list[dict]:
    bc = _beat_cap(esc)
    out = []
    for p in (raw or {}).get("parrafos") or []:
        try:
            b = int(p.get("beat"))
        except (TypeError, ValueError):
            continue
        t = ev.fix_glued_caps(str(p.get("texto") or "").strip())
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
    return ev.norm(name).split()[-1] if name else ""


def _verified_antagonist(esc: dict, pool: dict, sur: str) -> bool:
    """¿`sur` es el apellido del antagonista de la escaleta y algún dato o evento VERIFICADO del pool lo nombra?"""
    aid = (esc.get("antagonista") or {}).get("id")
    ant = next((p for p in pool.get("personajes") or [] if p.get("id") == aid), None)
    if not ant or not sur or ev.norm(_surname(ant["nombre"])) != ev.norm(sur):
        return False
    return any((it.get("verificacion") or {}).get("estado") == "verificada"
               and re.search(rf"\b{re.escape(ev.norm(sur))}\b", ev.norm(ev.text_of(it)))
               for k in ("datos", "cronologia") for it in pool.get(k) or [])


def review(topic: dict, esc: dict, parrafos: list[dict]) -> dict[str, Any]:
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
        if has_figure(ss[0]) or INSTITUTION.search(ss[0]):
            hard.append(f"gancho: la primera frase no lleva año, cifra ni institución: «{ss[0]}»")
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

def write(topic: dict, esc: dict, *, call: Callable[..., dict] | None = None, n: int = BEST_OF,
          log: list[str] | None = None) -> dict[str, Any]:
    log = log if log is not None else []
    if call is None:
        from gemini_helpers import call_pro_json as call
    cands, feedback = [], None
    for k in range(1, n + 1):
        raw = call(build_prompt(topic, esc, feedback), system_instruction=SYSTEM, response_schema=SCHEMA,
                   description=f"m01b_guionista intento {k}")
        ps = normalize(raw, esc)
        rv = review(topic, esc, ps)
        cands.append({"k": k, "parrafos": ps, "revision": rv})
        log.append(f"  [guionista] intento {k}: {len(rv['hard'])} duras · {len(rv['soft'])} blandas · puntaje {rv['score']}")
        if not rv["hard"]:
            break
        feedback = rv["hard"][:25]
    best = min(cands, key=lambda c: (len(c["revision"]["hard"]), -c["revision"]["score"], len(c["revision"]["soft"])))
    return {"parrafos": best["parrafos"], "revision": best["revision"], "elegido": best["k"],
            "prompt_version": PROMPT_VERSION,
            "_intentos": [{"intento": c["k"], "duras": c["revision"]["hard"], "blandas": len(c["revision"]["soft"]),
                           "puntaje": c["revision"]["score"]} for c in cands]}
