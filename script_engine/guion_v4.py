"""
script_engine/guion_v4.py — F11 (HANDOFF_F11 §1): guion v4. Menos reglas, oficio, reparar por edición.

    prompt(topic, esc)                 encabezado + escaleta por cap (palabras del CAP; cada dato con su marca COMO DATO:
                                       VERIFICADA / SIN VERIFICAR (sin nombre) / PANTALLA (no va en la voz) / CIFRA
                                       OFICIAL) + 8 líneas de oficio. Sin `instrucciones_guionista`, sin `ids_usados`.
    write(topic, esc)                  UNA llamada a Pro: sin best-of, sin bucle de feedback. Los ids de cada párrafo se
                                       calculan después (`m05.used_items(texto, pool, hard=False)`) para el contrato.
    bloqueantes(topic, esc, parrafos)  los ÚNICOS que frenan (a–e, §1.2); todos salen de funciones existentes:
        a  cifra o cita no respaldada      m05.invented_numbers (con verified_facts) + m05.false_quotes
        b  rol de persona incorrecto       guion_v3_reglas.role_problems (solo distingue preso / guardia)
        c  estructura                      beat faltante, cap vacío, cap fuera de ±25 % de su objetivo, video > max_words
        d  contaminación                   m05.contamination
        e  cita SIN VERIFICAR con nombre   el bloque de m01b_guionista.review (salvo el humano: §1.1)
    reparar(topic, esc, parrafos)      UNA ronda: (c) → m01d.regenerate_cap_v3 de ese cap (1 intento); (a)(b)(d)(e) →
                                       edición de la oración (patrón de m01d.cut_phrases + guardia léxica de m01c);
                                       fechas repetidas (determinista); una pasada del editor m01c con sus blandas,
                                       aceptando por párrafo si no suben los bloqueantes y pasa la guardia léxica.
                                       Si quedan bloqueantes, se reportan: no hay segunda ronda.
    metricas(topic, esc, parrafos)     todo lo de review + review_v3 + cap_review, tal cual (nunca rechaza).
m01b_guionista, m01c_editor, m05_narrative y guion_v3_reglas NO se modifican: se usan.
F11b: el prompt dice el largo (≈ N palabras por cap y el total); la regeneración de un cap corto mide solo cifras,
nombres y citas nuevas (REGEN_GUARD); `call_for(modelo)` enchufa Gemini Pro o un GPT en toda la cadena; los ids de
cada párrafo son `used_items ∩ beat_ids` (dato central, apoyos y lo asignado a su cap).
F11c: el prompt sigue la estructura de los fabricantes: `system()` = rol, voz, oficio y ejemplos de voz (XML);
`prompt()` = el usuario, con los datos primero (<caso>, <escaleta>) y la <tarea> al final. `--modelo gemini-4-argon`
es el modelo propio del guionista (no toca `gemini_model_research`). La pasada del editor m01c se saltea cuando el
crudo tiene 0 bloqueantes.
"""
from __future__ import annotations

import datetime as _dt
import re
from collections import Counter
from typing import Any, Callable

from script_engine import evidence as ev
from script_engine import m01b_guionista as mg

PROMPT_VERSION = "f11c-1"
CAP_TOL = 0.25                       # (c) cap fuera de ±25 % de su objetivo
REGEN_GUARD = ("cifras", "nombres", "citas")   # F11b §1.2: la regeneración de un cap corto permite prosa y adjetivos
MODELOS = ("gemini-pro", "gpt-6.1-sol", "gpt-6-astra", "gemini-4-argon")   # F11b §1.3 / F11c §1.2: `--modelo`
GEMINI_PROPIOS = ("gemini-4-argon",)  # F11c §1.2: modelo propio del guionista (gemini_model_research no cambia)
ESFUERZO = {"gpt-6.1-sol": "high"}   # F11b §2: Sol en esfuerzo high; Astra, el de la API por defecto
DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")

OFICIO = [
    "Gancho: la imagen del beat 1; después, la promesa.",
    "Seguimos a un humano con nombre.",
    "Frases cortas antes del golpe.",
    "Cita literal, 25 palabras o menos, con quién la dijo (la marcada SIN VERIFICAR va sin el nombre).",
    "Hechos, citas y alguna pregunta; no juicios.",
    "La fecha completa, una vez; después, \"ese día\", \"esa noche\".",
    "Lo marcado PANTALLA no lo dice la voz.",
    "La última frase es una cita o una pregunta.",
]

# F11c §1.1: párrafos de lab/hyperframes/f7/NARRACION_orleans_v3r3.md (F7c-3, nota 8.5), copiados literal. Solo la voz.
EJEMPLOS_VOZ = [
    "El 30 de agosto, el agua sucia de la inundación irrumpió en las celdas. Olía a una mezcla de aguas residuales y "
    "combustible diésel. En varios pabellones, los presos quedaron atrapados en sus celdas cerradas. Vieron cómo el "
    "nivel subía sin poder hacer nada. Pronto, el agua les llegaría hasta el pecho.",
    "El oficial Renard Reed también fue testigo. «Parecía que estaban abatiendo a la gente», dijo Reed. Vio a alguien "
    "caer al agua. No sabía si la munición era real o de goma. Fue suficiente. Lo vio.",
]


def system() -> str:
    """F11c §1.1: el mensaje de sistema / desarrollador (rol → voz → oficio → ejemplos), igual para todos los modelos."""
    oficio = "\n".join(f"{k}. {x}" for k, x in enumerate(OFICIO, start=1))
    ejemplos = "\n\n".join(EJEMPLOS_VOZ)
    return f"""<rol>Sos el guionista de Misterios Sepultados, un canal de documentales de historia oscura en YouTube, en español neutro.
Escribís la narración en off que escucha el espectador. Tu meta: que no se vaya. Contás una historia real con un humano con nombre, escenas concretas y suspenso; no explicás ni analizás. No inventás: toda cifra, fecha, hora, nombre y cita sale de los datos que te dan.</rol>
<voz>Narrativa y cinematográfica. Presente o pasado cercano. Frases cortas cuando algo golpea. Lo que se ve, se oye, se huele. El narrador no habla de sus fuentes ("los datos", "el testimonio señala", "la frase indica") ni del video.</voz>
<oficio>
{oficio}
</oficio>
<ejemplos_de_voz>
(Solo la voz; los hechos son de otro caso y no se usan.)

{ejemplos}
</ejemplos_de_voz>"""

SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {"parrafos": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
        "beat": {"type": "INTEGER"}, "texto": {"type": "STRING"}}, "required": ["beat", "texto"]}}},
    "required": ["parrafos"],
}


# ═══════════════════════════════════════════════════════════════
#  Prompt
# ═══════════════════════════════════════════════════════════════

def _surname(name: str) -> str:
    return ev.norm(name).split()[-1] if name else ""


def _is_human(author: str, esc: dict) -> bool:
    hum = (esc.get("humano") or {}).get("nombre") or ""
    return bool(hum and author) and _surname(author) == _surname(hum)


def screen_ids(esc: dict) -> set[str]:
    return {i for c in esc.get("caps") or [] for i in c.get("pantalla_ids") or []} | \
        {x["id"] for x in esc.get("a_pantalla") or []}


def official_ids(pool: dict) -> set[str]:
    from script_engine.m01a_escaleta import count_variants
    return {g["canon"] for g in count_variants(pool)}


def mark(i: str, its: dict, esc: dict, pool: dict) -> str:
    """La marca de un dato, como dato (no como orden)."""
    it = its.get(i) or {}
    out = []
    if i in screen_ids(esc):
        out.append("PANTALLA (no va en la voz)")
    if it.get("_kind") == "citas":
        v = it.get("verificacion") or {}
        if v.get("estado") == "verificada":
            out.append("VERIFICADA")
        elif v:
            # §1.1: si el autor es el humano de la escaleta, no se marca «sin nombre» (se reporta en §4)
            out.append("SIN VERIFICAR" if _is_human(it.get("autor") or "", esc) else "SIN VERIFICAR (sin nombre)")
    if i in official_ids(pool):
        out.append("CIFRA OFICIAL")
    return " · ".join(out)


def data_line(i: str, its: dict, esc: dict, pool: dict) -> str:
    it = its.get(i)
    if not it:
        return f"[{i}] (no existe)"
    m = mark(i, its, esc, pool)
    m = f" · {m}" if m else ""
    if it["_kind"] == "citas":
        return f"[{i}] CITA «{it.get('fragmento') or ev.text_of(it)}» — {it.get('autor')}{m}"
    fecha = f" ({it['fecha']})" if it.get("fecha") else ""
    return f"[{i}] {ev.text_of(it)}{fecha}{m}"


def escaleta_section(esc: dict, pool: dict) -> str:
    its = ev.items(pool)
    caps = {c["chapter_number"]: c for c in esc.get("caps") or []}
    out = []
    for n in range(1, 8):
        c = caps.get(n, {})
        bs = [b for b in esc["beats"] if b["cap"] == n]
        out.append(f"CAP {n} · ≈ {c.get('palabras_objetivo') or 0} palabras")
        in_beats = {i for b in bs for i in [b["dato_central"]] + list(b.get("datos_apoyo") or [])}
        for i in c.get("pantalla_ids") or []:
            if i not in in_beats:
                out.append(f"  en pantalla: {data_line(i, its, esc, pool)}")
        for b in bs:
            out.append(f"  BEAT {b['n']} · {b.get('funcion')} · {b.get('emocion')}")
            out.append(f"    imagen: {b.get('imagen_sensorial')}")
            out.append(f"    dato central: {data_line(b['dato_central'], its, esc, pool)}")
            for i in b.get("datos_apoyo") or []:
                out.append(f"    apoyo: {data_line(i, its, esc, pool)}")
            out.append(f"    el espectador se pregunta: {b.get('pregunta_abierta')}")
            if b.get("cierre"):
                out.append(f"    cierre: {b['cierre']}")
            cl = c.get("cliffhanger")
            if b is bs[-1] and n <= 6 and cl in its:          # el cliffhanger es un dato del último beat, no una regla
                out.append(f"    lo que abre el cap {n + 1}: {data_line(cl, its, esc, pool)}")
    return "\n".join(out)


def prompt(topic: dict, esc: dict) -> str:
    """F11c §1.1: el mensaje del usuario: los datos primero (<caso>, <escaleta>) y la tarea al final (<tarea>). El rol,
    la voz, el oficio y los ejemplos van en `system()`."""
    pool = topic["evidence_pool"]
    hum = esc.get("humano") or {}
    pico = esc.get("pico") or {}
    total = sum(c.get("palabras_objetivo") or 0 for c in esc.get("caps") or [])
    return f"""<caso>
TEMA: {topic.get("video_title")}
HUMANO: {hum.get("nombre")} ({hum.get("rol")})
PROMESA DEL GANCHO: {esc.get("promesa_gancho")}
PICO: beat {pico.get("beat")}
CIERRE HUMANO: {esc.get("cierre_humano")}
</caso>

<escaleta>
{escaleta_section(esc, pool)}
</escaleta>

<tarea>Con lo de arriba, escribí la narración completa en párrafos, cada uno con su beat. Cada cap, cerca de sus palabras (es su largo, no un máximo); el video completo ≈ {total:,} palabras. Devolvé el JSON del esquema.</tarea>"""


# ═══════════════════════════════════════════════════════════════
#  Escritura (una llamada) e ids calculados
# ═══════════════════════════════════════════════════════════════

def beat_ids(esc: dict, beat: int) -> set[str]:
    """F11b §1.4: los ids que un párrafo puede reclamar: dato central y apoyos de su beat + lo asignado a su cap
    (`evidence_ids`)."""
    b = next((x for x in esc.get("beats") or [] if x["n"] == beat), None)
    if not b:
        return set()
    cap = next((c for c in esc.get("caps") or [] if c["chapter_number"] == b["cap"]), {})
    return {b["dato_central"], *(b.get("datos_apoyo") or []), *(cap.get("evidence_ids") or [])}


def with_ids(parrafos: list[dict], pool: dict, esc: dict | None = None) -> list[dict]:
    """Cada párrafo con `ids_usados` calculados (lo que leen m03/gfx), nunca declarados por el modelo.
    F11b §1.4: con `esc`, `used_items(texto) ∩ beat_ids(beat)` (sin `esc`, todo lo que matchea en el pool, como F11)."""
    from script_engine.m05_narrative import used_items
    out = []
    for p in parrafos:
        ids = used_items(p["texto"], pool, hard=False)
        if esc is not None:
            own = beat_ids(esc, p["beat"])
            ids = [i for i in ids if i in own]
        out.append({**p, "ids_usados": ids})
    return out


def call_for(modelo: str | None) -> Callable[..., dict]:
    """F11b §1.3: el `call` de toda la cadena v4 de una corrida (guionista, regeneración, edición de oración, editor).
    `gemini-pro` (o None) → gemini_helpers.call_pro_json; `gemini-4-argon` (F11c) → gemini_helpers.make_call con ese
    modelo (sin temperature ni thinking); los GPT → gpt_helpers.make_call con su esfuerzo. Un modelo
    que no está en MODELOS es un error (no se reemplaza por otro)."""
    if modelo in (None, "gemini-pro"):
        from gemini_helpers import call_pro_json
        return call_pro_json
    if modelo not in MODELOS:
        raise ValueError(f"modelo desconocido: {modelo} (válidos: {', '.join(MODELOS)})")
    if modelo in GEMINI_PROPIOS:
        import gemini_helpers
        return gemini_helpers.make_call(modelo)
    import gpt_helpers
    return gpt_helpers.make_call(modelo, ESFUERZO.get(modelo))


def write(topic: dict, esc: dict, *, call: Callable[..., dict] | None = None,
          log: list[str] | None = None) -> dict[str, Any]:
    log = log if log is not None else []
    if call is None:
        from gemini_helpers import call_pro_json as call
    raw = call(prompt(topic, esc), system_instruction=system(), response_schema=SCHEMA,
               description="guion_v4 guionista")
    ps = with_ids(mg.normalize(raw, esc), topic["evidence_pool"], esc)
    log.append(f"  [guionista v4] {len(ps)} párrafos · {sum(mg.wc(p['texto']) for p in ps)} palabras")
    return {"parrafos": ps, "prompt_version": PROMPT_VERSION}


# ═══════════════════════════════════════════════════════════════
#  Bloqueantes (§1.2)
# ═══════════════════════════════════════════════════════════════

def _sentence_with(text: str, needle: str) -> str:
    """La oración del párrafo que contiene `needle` (normalizado); el párrafo si no se encuentra."""
    nn = ev.norm(needle)
    for s in mg.sentences(text):
        if nn and nn in ev.norm(s):
            return s
    return text


def _b(code: str, p: dict | None, frase: str, motivo: str, cap: int | None = None, beat: int | None = None) -> dict:
    return {"codigo": code, "cap": p["cap"] if p else cap, "beat": p["beat"] if p else beat, "frase": frase,
            "motivo": motivo}


def unverified_named(esc: dict, pool: dict, parrafos: list[dict]) -> list[dict]:
    """(e) El bloque de m01b_guionista.review «citas sin verificar: sin el nombre de quien la dijo», por párrafo,
    salvo cuando el autor es el humano de la escaleta (§1.1: no se le pide decirlo sin nombre)."""
    from researcher_steps.verify_quotes import _named
    out = []
    for q in pool.get("citas") or []:
        v = q.get("verificacion") or {}
        if not v or v.get("estado") == "verificada":
            continue
        if not _named(q.get("autor") or "") or _is_human(q.get("autor") or "", esc):
            continue
        sur = mg._surname(q.get("autor") or "")
        if v.get("estado") == "verificada_parcial" and mg._verified_antagonist(esc, pool, sur):
            continue
        for p in parrafos:
            nf = ev.norm(p["texto"])
            k = nf.find(ev.norm(q["texto"])[:40])
            if k < 0 and q.get("fragmento"):
                k = nf.find(ev.norm(q["fragmento"])[:40])
            if k < 0:
                continue
            if sur and len(sur) > 3 and re.search(rf"\b{re.escape(sur)}\b", nf[max(0, k - 200):k + len(q["texto"]) + 200]):
                out.append(_b("e", p, _sentence_with(p["texto"], sur),
                              f"{q['id']} está SIN VERIFICAR y va con el nombre de {q.get('autor')}"))
    return out


def bloqueantes(topic: dict, esc: dict, parrafos: list[dict]) -> list[dict]:
    """[{codigo, cap, beat, frase, motivo}] — lo único que frena. Lista vacía = pasa."""
    from script_engine.guion_v3_reglas import role_problems
    from script_engine.m05_narrative import contamination, false_quotes, invented_numbers
    from script_engine.video_length import get as _len
    pool = topic["evidence_pool"]
    facts = topic.get("verified_facts") or []
    out: list[dict] = []
    for p in parrafos:
        t = p["texto"]
        for x in invented_numbers(t, pool, facts):
            out.append(_b("a", p, _sentence_with(t, x), f"cifra que no está en el research: {x}"))
        for x in false_quotes(t, pool):
            out.append(_b("a", p, _sentence_with(t, x[:40]), f"entre comillas, pero no es una cita del pool: «{x}…»"))
        for x in role_problems(t, pool):
            name = x.split("»")[0].split()[-1] if "»" in x else ""
            out.append(_b("b", p, _sentence_with(t, name), f"rol: {x}"))
        for x in contamination(t, pool, facts):
            out.append(_b("d", p, t, f"fuera del caso (descartado en el pool): {x[:80]}"))
    out += unverified_named(esc, pool, parrafos)
    # (c) estructura
    written = {p["beat"] for p in parrafos}
    for b in esc["beats"]:
        if b["n"] not in written:
            out.append(_b("c", None, "", f"falta el beat {b['n']} ({b.get('funcion')})", cap=b["cap"], beat=b["n"]))
    for c in esc.get("caps") or []:
        n = c["chapter_number"]
        ps = [p for p in parrafos if p["cap"] == n]
        tgt = c.get("palabras_objetivo") or 0
        w = sum(mg.wc(p["texto"]) for p in ps)
        if not ps:
            out.append(_b("c", None, "", f"cap {n} vacío", cap=n))
        elif tgt and w < (1 - CAP_TOL) * tgt:
            out.append(_b("c", None, "", f"cap {n} corto: {w} palabras (objetivo {tgt}, mínimo "
                                         f"{round((1 - CAP_TOL) * tgt)})", cap=n))
        elif tgt and w > (1 + CAP_TOL) * tgt:
            out.append(_b("c", None, "", f"cap {n} largo: {w} palabras (objetivo {tgt}, máximo "
                                         f"{round((1 + CAP_TOL) * tgt)})", cap=n))
    tw = sum(mg.wc(p["texto"]) for p in parrafos)
    if tw > _len("max_words"):
        out.append(_b("c", None, "", f"el video tiene {tw} palabras: el tope es {_len('max_words')}"))
    return out


# ═══════════════════════════════════════════════════════════════
#  Reparación: UNA ronda (§1.3)
# ═══════════════════════════════════════════════════════════════

EDIT_SCHEMA = {"type": "OBJECT", "properties": {"texto": {"type": "STRING"}}, "required": ["texto"]}


def _cap_ids(esc: dict, cap: int) -> list[str]:
    ids = [i for b in esc["beats"] if b["cap"] == cap for i in [b["dato_central"]] + list(b.get("datos_apoyo") or [])]
    return [i for i in dict.fromkeys(ids) if i not in screen_ids(esc)]


def _structural_caps(bl: list[dict]) -> dict[int, list[str]]:
    """Caps a regenerar: beat faltante, cap vacío o corto (el largo y el tope del video se reportan, no se regeneran)."""
    out: dict[int, list[str]] = {}
    for x in bl:
        if x["codigo"] == "c" and x["cap"] and (x["motivo"].startswith("falta el beat") or "vacío" in x["motivo"]
                                                or " corto:" in x["motivo"]):
            out.setdefault(int(x["cap"]), []).append(x["motivo"])
    return out


def edit_sentences(p: dict, problems: list[dict], *, call: Callable[..., dict]) -> tuple[str, str]:
    """Edición sobre las oraciones con bloqueante (patrón de m01d.cut_phrases): sacar o corregir esas frases, nada
    más. Devuelve (texto nuevo o el mismo, motivo si no se aceptó)."""
    from script_engine.m01c_editor import lexical_guard
    lines = "\n".join(f"- «{x['frase']}» → {x['motivo']}" for x in problems)
    raw = call(f"""En este párrafo de un documental hay frases con un problema. Sacá esas frases o corregilas para que el
problema desaparezca, con las palabras que ya tienen. No toques nada más del párrafo; no agregues datos, cifras,
nombres, adjetivos ni citas.

FRASES CON PROBLEMA:
{lines}

PÁRRAFO:
{p['texto']}""", response_schema=EDIT_SCHEMA, description="guion_v4 editar frase") or {}
    new = ev.fix_glued_caps(str(raw.get("texto") or "").strip())
    if not new or new == p["texto"]:
        return p["texto"], "sin cambio"
    lg = lexical_guard(p["texto"], new)
    if lg:
        return p["texto"], "guardia léxica: " + "; ".join(lg)
    targets = {ev.norm(x["frase"]) for x in problems}
    kept = [s for s in mg.sentences(p["texto"]) if ev.norm(s) not in targets]
    if any(ev.norm(s) not in ev.norm(new) for s in kept):
        return p["texto"], "tocó otras frases del párrafo"
    return new, ""


def event_date(esc: dict, pool: dict) -> str | None:
    """La fecha del evento central: la del ítem del pico si tiene día; si no, la fecha más repetida de la cronología."""
    its = ev.items(pool)
    pk = its.get(str((esc.get("pico") or {}).get("id") or ""))
    if pk and ev.item_date(pk):
        return ev.item_date(pk)
    ds = Counter(str(c.get("fecha")) for c in pool.get("cronologia") or []
                 if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(c.get("fecha") or "")))
    return ds.most_common(1)[0][0] if ds else None


def replace_repeated_dates(parrafos: list[dict], iso: str | None) -> tuple[list[dict], list[str]]:
    """`guion_v3_reglas.replace_repeated_dates` generalizado: el día y el año salen de `iso` (la fecha del evento
    central) y la paráfrasis es «ese <día de la semana>» calculado con datetime (no un «domingo» fijo). La primera
    aparición se queda; las siguientes («el 1 de agosto», «del domingo 1 de agosto de 2004») pasan a «ese domingo» /
    «de ese domingo». Determinista; devuelve (párrafos, cambios)."""
    if not iso or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", iso):
        return [dict(p) for p in parrafos], []
    d = _dt.date.fromisoformat(iso)
    day, year, wd = ev.spoken_date(iso), str(d.year), DIAS[d.weekday()]
    pat = re.compile(rf"\b(?:(?P<art>[Ee]l|[Dd]el)\s+)?(?:{wd}\s+)?{re.escape(day)}(?:\s+de\s+{year})?\b")
    seen, out, changes = False, [], []

    def _rep(m: re.Match) -> str:
        nonlocal seen
        if not seen:
            seen = True
            return m.group(0)
        art = m.group("art") or ""
        new = f"de ese {wd}" if art.lower() == "del" else f"ese {wd}"
        if art[:1].isupper():
            new = new[0].upper() + new[1:]
        changes.append(f"«{m.group(0)}» → «{new}»")
        return new
    for p in parrafos:
        out.append({**p, "texto": pat.sub(_rep, p["texto"])})
    return out, changes


def editor_pass(topic: dict, esc: dict, parrafos: list[dict], *, call: Callable[..., dict],
                log: list[str]) -> tuple[list[dict], list[dict]]:
    """Una pasada del editor m01c (su prompt, sus blandas: eco y cierre) aceptando cada párrafo si pasa la guardia
    léxica y NO sube la cantidad de bloqueantes (el conteo de duras v3 ya no decide)."""
    from script_engine import m01c_editor as mc
    from script_engine.guion_v3_reglas import closing_soft, echo_soft
    pool = topic["evidence_pool"]
    raw = call(mc.build_prompt(esc, parrafos, echo_soft(parrafos), closing_soft(parrafos)),
               system_instruction=mc.SYSTEM, response_schema=mc.SCHEMA, description="guion_v4 editor") or {}
    edited = raw.get("parrafos") or []
    motivo = {int(c.get("parrafo", -1)): c.get("motivo") for c in raw.get("cambios") or [] if isinstance(c, dict)}
    if len(edited) != len(parrafos):
        log.append(f"  [editor v4] devolvió {len(edited)} párrafos (se esperaban {len(parrafos)}): sin cambios")
        return [dict(p) for p in parrafos], [{"estado": "rechazado", "motivo_rechazo": "cantidad de párrafos"}]
    out = [dict(p) for p in parrafos]
    cur = len(bloqueantes(topic, esc, out))
    estado = []
    for k, (orig, e) in enumerate(zip(parrafos, edited)):
        new_t = ev.fix_glued_caps(str(e.get("texto") or "").strip())
        if not new_t or new_t == orig["texto"]:
            continue
        rec = {"parrafo": k, "beat": orig["beat"], "antes": orig["texto"], "despues": new_t,
               "motivo": motivo.get(k) or ""}
        lg = mc.lexical_guard(orig["texto"], new_t)
        if lg:
            estado.append({**rec, "estado": "rechazado", "motivo_rechazo": "; ".join(lg)})
            continue
        trial = [dict(p) for p in out]
        trial[k] = with_ids([{**orig, "texto": new_t}], pool, esc)[0]
        n = len(bloqueantes(topic, esc, trial))
        if n > cur:
            estado.append({**rec, "estado": "rechazado", "motivo_rechazo": f"bloqueantes {cur} → {n}"})
            continue
        out, cur = trial, n
        estado.append({**rec, "estado": "aceptado"})
    ok = sum(1 for s in estado if s["estado"] == "aceptado")
    log.append(f"  [editor v4] {len(estado)} párrafo(s) editado(s): {ok} aceptado(s), {len(estado) - ok} rechazado(s)")
    return out, estado


def reparar(topic: dict, esc: dict, parrafos: list[dict], *, call: Callable[..., dict] | None = None,
            log: list[str] | None = None) -> dict[str, Any]:
    """UNA ronda de reparación. Nunca vuelve a llamar al guionista completo. Devuelve los párrafos finales, los
    bloqueantes antes/después y lo que hizo cada paso."""
    from script_engine import m01d_particion as md
    log = log if log is not None else []
    if call is None:
        from gemini_helpers import call_pro_json as call
    pool = topic["evidence_pool"]
    ps = with_ids(parrafos, pool, esc)
    bl0 = bloqueantes(topic, esc, ps)
    pasos: dict[str, Any] = {"regenerados": [], "ediciones": [], "fechas": [], "editor": []}
    # (c) → regenerate_cap_v3 SOLO de ese cap, 1 intento, notas = el texto del bloqueante
    caps_tgt = {c["chapter_number"]: c.get("palabras_objetivo") or 0 for c in esc.get("caps") or []}
    for cap, notas in sorted(_structural_caps(bl0).items()):
        before = [p for p in ps if p["cap"] == cap]
        ps = md.regenerate_cap_v3(topic, esc, ps, cap, pool, notas=notas, permitidos=_cap_ids(esc, cap),
                                  min_words=round((1 - CAP_TOL) * caps_tgt.get(cap, 0)), attempts=1, call=call, log=log,
                                  guard=REGEN_GUARD)
        ps = with_ids(ps, pool, esc)
        after = [p for p in ps if p["cap"] == cap]
        pasos["regenerados"].append({"cap": cap, "notas": notas, "cambio": before != after,
                                     "palabras": [sum(mg.wc(p["texto"]) for p in before),
                                                  sum(mg.wc(p["texto"]) for p in after)]})
    # (a)(b)(d)(e) → edición sobre la oración
    bl1 = [x for x in bloqueantes(topic, esc, ps) if x["codigo"] in ("a", "b", "d", "e")]
    for k, p in enumerate(ps):
        mine = [x for x in bl1 if x["beat"] == p["beat"] and ev.norm(x["frase"]) in ev.norm(p["texto"])]
        if not mine:
            continue
        new, why = edit_sentences(p, mine, call=call)
        n_before = len([x for x in bloqueantes(topic, esc, ps) if x["codigo"] != "c"])
        trial = [dict(q) for q in ps]
        trial[k] = with_ids([{**p, "texto": new}], pool, esc)[0]
        n_after = len([x for x in bloqueantes(topic, esc, trial) if x["codigo"] != "c"])
        ok = not why and n_after < n_before
        if not why and not ok:
            why = f"no bajó los bloqueantes ({n_before} → {n_after})"
        pasos["ediciones"].append({"beat": p["beat"], "problemas": mine, "antes": p["texto"],
                                   "despues": new if ok else p["texto"], "aceptada": ok, "motivo_rechazo": why})
        log.append(f"  [editar v4] beat {p['beat']}: {'aceptada' if ok else 'rechazada (' + why + ')'}")
        if ok:
            ps = trial
    # fechas repetidas (determinista)
    ps, pasos["fechas"] = replace_repeated_dates(ps, event_date(esc, pool))
    ps = with_ids(ps, pool, esc)
    # una pasada del editor m01c; F11c §1.3: solo si el crudo trae bloqueantes (con 0 se saltea)
    if bl0:
        ps, pasos["editor"] = editor_pass(topic, esc, ps, call=call, log=log)
    else:
        log.append("  [editor v4] crudo con 0 bloqueantes: sin pasada del editor m01c")
    bl2 = bloqueantes(topic, esc, ps)
    log.append(f"  [reparación v4] bloqueantes {len(bl0)} → {len(bl2)} (una ronda; no hay segunda)")
    return {"parrafos": ps, "bloqueantes_antes": bl0, "bloqueantes_despues": bl2, "pasos": pasos,
            "parada": bool(bl2)}


# ═══════════════════════════════════════════════════════════════
#  Métricas (§1.4): nunca rechazan
# ═══════════════════════════════════════════════════════════════

def closing_kind(parrafos: list[dict]) -> str:
    from script_engine.guion_v3_reglas import closing_soft, sentences_of
    if not parrafos:
        return "—"
    last = (sentences_of(parrafos[-1]["texto"]) or [""])[-1]
    if closing_soft(parrafos):
        return "resumen"
    return "pregunta" if last.rstrip().endswith("?") else "cita"


def metricas(topic: dict, esc: dict, parrafos: list[dict], *, declared: bool = False) -> dict[str, Any]:
    """Todo lo de m01b_guionista.review (cap_review + review_v3 + gancho, ritmo, humano…) tal cual, más conteos para
    la tabla. `declared`: los párrafos traen los ids que declaró el modelo (v3); si no, se calculan (v4)."""
    from script_engine.guion_v3_reglas import echo_soft, quotes_in
    pool = topic["evidence_pool"]
    ps = [dict(p) for p in parrafos] if declared else with_ids(parrafos, pool, esc)
    rv = mg.review(topic, esc, ps)
    caps = mg.caps_text(esc, ps)
    hum = esc.get("humano") or {}
    sur = _surname(hum.get("nombre") or "")
    human_caps = [c["chapter_number"] for c in caps if sur and re.search(rf"\b{re.escape(sur)}\b", ev.norm(c["narration"]))]
    tgt = {c["chapter_number"]: c.get("palabras_objetivo") or 0 for c in esc.get("caps") or []}
    return {"duras_v3": rv["hard"], "blandas_v3": rv["soft"], "puntaje": rv["score"],
            "palabras": sum(mg.wc(p["texto"]) for p in ps),
            "palabras_por_cap": {c["chapter_number"]: [mg.wc(c["narration"]), tgt.get(c["chapter_number"], 0)]
                                 for c in caps},
            "citas": sum(len(quotes_in(p["texto"])) for p in ps),
            "humano_caps": human_caps, "cierre": closing_kind(ps), "ecos": echo_soft(ps),
            "por_cap": rv["por_cap"], "ids_por_parrafo": ids_per_paragraph(ps, pool, esc, declared=declared)}


def ids_per_paragraph(parrafos: list[dict], pool: dict, esc: dict, *, declared: bool = False) -> dict[str, float]:
    """F11b §1.4: promedio de ids por párrafo antes (todo lo que matchea en el pool; en v3, lo declarado) y después
    (∩ los ids del beat)."""
    from script_engine.m05_narrative import used_items
    if not parrafos:
        return {"antes": 0.0, "despues": 0.0}
    before = [p.get("ids_usados") or [] if declared else used_items(p["texto"], pool, hard=False) for p in parrafos]
    after = [[i for i in used_items(p["texto"], pool, hard=False) if i in beat_ids(esc, p["beat"])] for p in parrafos]
    n = len(parrafos)
    return {"antes": round(sum(map(len, before)) / n, 2), "despues": round(sum(map(len, after)) / n, 2)}
