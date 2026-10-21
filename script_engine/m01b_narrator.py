"""
script_engine/m01b_narrator.py — Módulo 01b: narrador.

TAREA ÚNICA: a partir del topic completo + skeleton (output del 01a),
generar la narración cap-por-cap + 3 humanizer_phrases.

INPUT:
  - topic    (dict, post módulo 00)
  - skeleton (dict, post módulo 01a)

OUTPUT:
  {
    "topic_id": "uuid",
    "chapters": [
      {"chapter_number": 1, "narration": "string (300-800 chars)"},
      {"chapter_number": 2, "narration": "string (800-1800 chars)"},
      ... cap 3-6 (800-1800)
      {"chapter_number": 7, "narration": "string (400-1100 chars, objetivo ~750)"}
    ],
    "humanizer_phrases": ["...", "...", "..."]
  }

LLAMADAS GEMINI: 8 (Flash con JSON mode):
  1 hook + 5 developments + 1 outro + 1 humanizer.

CADA cap recibe los anteriores ya cerrados como string fijo. Imposible
repetir frases. Cada cap arranca con cliffhanger del anterior y cierra
con cliffhanger hacia el siguiente (excepto cap 7, que cierra el arco).

PERSISTENCIA: data/scripts/_steps/{topic_id}/01b_narration.json

F5 §1.3 (si el topic trae evidence_pool y el skeleton su _evidence_plan; si no, todo igual):
  - lista blanca numérica = verified_facts ∪ evidence_pool (regla 6);
  - cada cap recibe SUS datos asignados (ids del skeleton), las personas que entran, el cliffhanger y los datos
    ya gastados en 2 caps; reglas nuevas en el prompt y en la validación (script_engine.m05_narrative.cap_problems):
    ≥ 3 datos asignados literales, ningún dato en > 2 caps, personas por nombre y cargo, cronología en orden con
    fechas, citas entre comillas con autor, relleno prohibido, cierre que anticipa el cliffhanger;
  - falla de esas reglas → reintento con feedback dirigido (kind="evidence"); si tras los intentos sigue, la
    narración se ACEPTA y las violaciones quedan en `_f5_violations` (no se mata un topic ya investigado).
"""

import json
import re
from pathlib import Path

from config import DATA_DIR
from gemini_helpers import call_flash_json, call_pro_json
from script_engine import evidence as ev


# ═══════════════════════════════════════════════════════════════
#  PATHS Y CONSTANTES
# ═══════════════════════════════════════════════════════════════

STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"

# Largos por rol (chars)
LEN_HOOK = (300, 800)
LEN_DEVELOPMENT = (800, 2000)
LEN_OUTRO = (400, 1100)

# Chat 51: margen del techo INSTRUIDO al outro en el reintento del lado largo (deja aire para
# que el modelo no apunte al techo exacto y se pase por poco). NO cambia la banda del validador.
OUTRO_RETRY_MARGIN = 120

# Hook: primera oración debe ser corta y de impacto
HOOK_FIRST_SENTENCE_MAX_WORDS = 12

# Humanizer
HUMANIZER_COUNT = 3
HUMANIZER_MAX_CHARS = 40

# Frases prohibidas — clichés de YouTube que matan retención
FORBIDDEN_OPENINGS = (
    "hoy les voy a contar",
    "hoy te voy a contar",
    "en este video",
    "bienvenidos",
    "bienvenido a",
    "hola a todos",
    "qué tal",
)
FORBIDDEN_CLOSINGS = (
    "si te gustó",
    "suscríbete",
    "suscribite",
    "dejá tu comentario",
    "deja tu comentario",
    "compartí con",
    "comparte con",
    "hasta el próximo",
    "hasta la próxima",
    "no olvides darle like",
    "dale like",
)
GENERIC_CONNECTORS = (
    "a continuación",
    "por otra parte",
    "por otro lado",
    "sigamos con",
    "veamos ahora",
    "como vimos antes",
)


# ═══════════════════════════════════════════════════════════════
#  TONE INSTRUCTIONS POR INTENT (PR 2.A chat 24)
#  Se inyectan en cada prompt builder según el narrative_intent del cap.
# ═══════════════════════════════════════════════════════════════

TONE_INSTRUCTIONS_BY_INTENT: dict[str, str] = {
    "hook":           "Frases cortas y tensas. Promesa explícita. NO contexto largo. Densidad alta.",
    "setup":          "Pacing calmo. Contexto eficiente sin rambling. Densidad baja.",
    "rising_tension": "Frases medias. 'Pero', 'lo que no sabían', 'sin embargo'. Foreshadowing. Densidad media.",
    "shock":          "Frases muy cortas. Signos de exclamación posibles. Pacing acelerado. Densidad media.",
    "consequences":   "Frases más largas. Peso emocional. Reflexión sobre lo perdido. Densidad media.",
    "resolution":     "Pacing pausado. Frases reflexivas. Bajada de intensidad. Densidad media-alta.",
    "outro":          "Cierre con pregunta sin respuesta. Frase final corta y suspensiva. Densidad alta en el cierre.",
}


def _tone_block(narrative_intent: str | None) -> str:
    """Construye el bloque TONO NARRATIVO para inyectar en cada prompt.

    Si narrative_intent es None o desconocido, devuelve string vacío
    (el prompt funciona sin tono específico — fallback seguro).
    """
    if not narrative_intent:
        return ""
    instr = TONE_INSTRUCTIONS_BY_INTENT.get(narrative_intent)
    if not instr:
        return ""
    return f"""
═══════════════════════════════════════════════════
TONO NARRATIVO DE ESTE CAP — narrative_intent={narrative_intent!r}
═══════════════════════════════════════════════════
{instr}
"""


# ═══════════════════════════════════════════════════════════════
#  HELPERS DE FORMATO
# ═══════════════════════════════════════════════════════════════

def _format_facts(verified_facts: list) -> str:
    if not verified_facts:
        return "(sin facts)"
    lines = []
    for i, f in enumerate(verified_facts, start=1):
        if isinstance(f, dict):
            lines.append(f"  [F{i:02d}] {f.get('fact', '').strip()}")
        elif isinstance(f, str):
            lines.append(f"  [F{i:02d}] {f.strip()}")
    return "\n".join(lines)


def _format_skeleton(skeleton: dict) -> str:
    out = []
    for ch in skeleton.get("chapters", []):
        cn = ch.get("chapter_number")
        title = ch.get("title", "")
        role = ch.get("role", "")
        bullets = ch.get("bullets", []) or []
        bullets_txt = "\n".join(f"      • {b}" for b in bullets)
        out.append(f"  Cap {cn} [{role}] — {title}\n{bullets_txt}")
    return "\n\n".join(out)


def _format_previous_narrations(narrations: list[dict]) -> str:
    if not narrations:
        return "(ninguna todavía — sos el primer cap)"
    out = []
    for n in narrations:
        cn = n.get("chapter_number")
        text = n.get("narration", "")
        out.append(f"  ── Cap {cn} ──\n{text}")
    return "\n\n".join(out)


def _format_topic_block(topic: dict) -> str:
    return f"""Título     : {topic.get('video_title', '')}
Ángulo     : {topic.get('angle', '')}
Hook       : {topic.get('hook', '')}
Misterio   : {topic.get('mystery', '')}
Revelación : {topic.get('reveal', '')}

Canonical  : {topic.get('canonical_subject_description', '')}

Research summary:
{topic.get('research_summary', '')}"""


# ═══════════════════════════════════════════════════════════════
#  REGLAS COMPARTIDAS DE PROSA (se inyectan en todos los prompts)
# ═══════════════════════════════════════════════════════════════

PROSE_RULES = """REGLAS DE PROSA (todas inviolables):
1. IDIOMA: español neutro. Sin anglicismos sin traducir.
   ✗ MAL: "telescoped sobre sí misma"  ✓ BIEN: "colapsada sobre sí misma"
2. RITMO: alternar oraciones cortas (impacto) y largas (explicación).
   Frases cortas seguidas → tensión. Frase larga → respiro.
3. ADJETIVOS: usar sensoriales (frío, metálico, denso, azul, vasto).
   PROHIBIDO: muy, bastante, interesante, increíble, asombroso.
4. NO uses conectores genéricos: "a continuación", "por otra parte",
   "sigamos con", "veamos ahora", "como vimos antes".
5. PROHIBIDO ABSOLUTO en cualquier cap (apertura o cierre):
   "Hoy les voy a contar...", "En este video...", "Bienvenidos...",
   "Suscribite", "Dejá tu comentario", "Hasta el próximo video".
6. REGLA NUMÉRICA INVIOLABLE: cualquier cifra, fecha, nombre propio o
   cantidad debe estar literal en los verified_facts arriba. NO inventes.
7. PROHIBIDO incluir referencias internas tipo [F##] o [F\\d+] en la narración
   final. Esos son IDs de facts del contexto del prompt, SOLO para tu
   razonamiento interno. La narración final va directo a TTS y los tags se
   leen literal como "F cero ocho" — destruyendo el audio."""


PROSE_RULE_6_POOL = """6. REGLA NUMÉRICA INVIOLABLE: cualquier cifra, fecha, nombre propio o
   cantidad debe estar literal en los verified_facts o en el EVIDENCE POOL de arriba. NO inventes."""

F5_RULES = """REGLAS DEL EVIDENCE POOL (inviolables, se validan):
A. Usá entre 3 y 6 de los datos asignados a este cap (los que más golpean): cada uno aparece LITERAL (la cifra,
   la fecha o el nombre tal cual). No hace falta usarlos todos: el LARGO OBLIGATORIO manda. Densidad: al menos
   2 datos DISTINTOS cada 100 palabras (≈ 5 en un cap de 250 palabras); un párrafo sin dato es relleno.
B. No repitas datos que ya salieron en 2 caps (lista de abajo). Un dato del video vive en 2 caps como máximo.
C. Nombrá a cada persona por nombre y apellido y con su cargo la primera vez (p. ej. "el sheriff Marlin Gusman").
D. Si el cap cuenta 2 o más eventos fechados, narralos EN ORDEN y decí las fechas.
E. Citas: entre comillas, copiadas literal, con el autor DENTRO de la oración ("dijo el sheriff Gusman").
   Nunca como firma con guion al final ("— Sheriff Gusman"): la narración va a TTS.
F. Prohibido el relleno: "imaginen", "una eternidad de", "cámara de tortura", "coloso de", "manto oscuro",
   "infierno personal", "eco fantasmal", "sombra inalcanzable", "tragedia íntima", "manto de", "el monstruo",
   "infierno flotante", "velo de misterio", "ecos de", "alfombra de la negación", "sentencia de abandono",
   "trampa brutal", y más de 2 oraciones seguidas que califican sin un dato. Cambiá adjetivos por hechos.
G. El cierre anticipa el dato CONCRETO del próximo cap (lo nombra o lo deja incompleto). Nada de retórica
   genérica como "¿cuánto podrían resistir?".
H. Cada dato se dice UNA sola vez en el cap: la cifra o la fecha suena una vez; después, paráfrasis SIN la cifra
   ("ese lunes", "esa noche", "el agua", "los desaparecidos"). Nada de "29 de agosto" tres veces.
I. Ni acta ni novela: entre 2 y 4 adjetivos calificativos cada 100 palabras, atados a hechos (cómo era el agua,
   la celda, el calor). Una lista seca de hechos también falla.
J. Nombrá a una persona solo si HACE algo en la historia (decide, declara, demanda, testifica, rescata). Nada de
   "casos como el de…" para llenar: si una persona no actúa, no la nombres.
K. En "datos_usados" del JSON listá los ids ([D..], [T..], [Q..]) del EVIDENCE POOL que tu narración cuenta
   LITERALES (también los de caps anteriores que repitas). Nunca F## (los verified_facts no van ahí). Un id
   declarado que no suena literal es un error; un dato que usaste y no declaraste NO cuenta para el cap.

L. Fechas: todo evento que cuentes va con SU fecha. Nunca fundas dos fechas en una oración ni pegues un evento de
   otro día a la fecha que venías diciendo (la decisión de Gusman es del 28 de agosto; el impacto, del 29).
M. Literal es solo lo que se verifica: cifras, nombres, fechas y citas. Todo lo demás, contalo con tus palabras: no
   copies frases del pool ni repitas fórmulas de caps anteriores.
N. Cifra canónica: un mismo conteo se dice con UNA cifra en todo el video (la oficial). La otra solo en el cap que
   cuenta la contradicción.
O. Los DATOS RESERVADOS PARA PANTALLA no se dicen: la pantalla los muestra mientras la voz cuenta otra cosa.

PRIORIDAD DE LAS REGLAS (F5c):
- DURAS (si fallan, el texto se rechaza): no inventar (toda cifra está en el research), cada dato asignado una
  vez y literal (A, B, H, K), nada fuera del caso ni personas que no hacen nada (J), sin relleno prohibido (F),
  cierre con el dato del cliffhanger (G), cada evento con su fecha y sin fundir fechas (L), la cifra canónica (N)
  y no decir lo reservado para pantalla (O).
- BLANDAS (se avisan, nunca rechazan): la ventana de 2 a 4 adjetivos cada 100 palabras (I) y no repetir
  fórmulas de caps anteriores (frases de 3 palabras ya dichas: menos del 5 %).
Si no podés cumplir todo, sacrificá la ventana de adjetivos, nunca los datos ni los nombres."""


def _prose_rules(topic: dict) -> str:
    """PROSE_RULES; con evidence_pool, la regla 6 admite el pool (F5 §1.3)."""
    if not topic.get("evidence_pool"):
        return PROSE_RULES
    i = PROSE_RULES.index("6. REGLA NUMÉRICA")
    j = PROSE_RULES.index("7. PROHIBIDO")
    return PROSE_RULES[:i] + PROSE_RULE_6_POOL + "\n" + PROSE_RULES[j:]


def _evidence_block(topic: dict, skeleton: dict, cap: int, previous: list[dict]) -> str:
    """F5 §1.3: lo que este cap tiene que contar del pool. "" si no hay pool (prompt idéntico al de antes)."""
    pool = topic.get("evidence_pool")
    ch = next((c for c in skeleton.get("chapters") or [] if c.get("chapter_number") == cap), {})
    if not pool or "evidence_ids" not in ch:
        return ""
    from script_engine import m05_narrative as mn
    its = ev.items(pool)
    from collections import Counter
    pairs = [mn.text_and_ids(n) for n in previous]
    spent = Counter(i for t, d in pairs for i in set(mn.repeat_items(t, pool, declared=d)))
    gone = [i for i, n in spent.items() if n >= mn.MAX_DATO_CAPS]
    people = [p for p in skeleton.get("personajes") or [] if p.get("entra_en_cap") == cap]
    cid = ch.get("cliffhanger")
    lines = ["", "═══════════════════════════════════════════════════",
             f"DATOS DEL EVIDENCE POOL ASIGNADOS A ESTE CAP (usalos literales)",
             "═══════════════════════════════════════════════════",
             ev.format_pool(pool, ch["evidence_ids"])]
    if people:
        lines += ["", "PERSONAS QUE ENTRAN EN ESTE CAP (nombre + cargo la primera vez):",
                  *[f"  • {p['nombre']} — {p.get('rol') or ''}{' (antagonista)' if p.get('antagonista') else ''}"
                    for p in people]]
        roles = [str(p.get("rol") or "").lower() for p in people]
        twins = sorted({r for r in roles if r and roles.count(r) > 1})
        if twins:                                     # F5d+: «dos turistas de Ohio, A y B», no «A, turista, y B, turista»
            lines += ["  (Personas con el mismo rol se presentan JUNTAS, con el rol en plural una sola vez: «dos "
                      "turistas de Ohio, Robie Waganfeald y Paul Kunkel Jr.»; nunca «A, turista, y B, turista».)"]
    if cid and cid in its:
        lines += ["", f"CLIFFHANGER (el cierre anticipa ESTE dato, que se revela en el cap {cap + 1}):",
                  f"  [{cid}] {ev.text_of(its[cid])}"]
    if gone:
        lines += ["", "DATOS YA GASTADOS EN 2 CAPS (NO los repitas):",
                  *[f"  • {' / '.join(ev.anchors(its[i]))}" for i in gone if i in its]]
    for g in pool.get("cifras_canonicas") or []:      # F5d: una sola cifra por conteo en todo el video
        o = its.get(g["oficial"])
        var = ", ".join(f"{v['valor']} ({v['estatus']})" for v in g["variantes"])
        if g["oficial"] in (ch.get("contradiccion_cifras") or []):
            lines += ["", f"CIFRA CANÓNICA EN CONTRADICCIÓN (este es el cap que la cuenta): la oficial es {g['valor']} "
                          f"(«{ev.text_of(o)[:80]}»); las otras cifras del research son {var}. Contá la diferencia: "
                          "la oficial primero, la otra como lo que es (estimación, cifra de los medios)."]
        else:
            lines += ["", f"CIFRA CANÓNICA: si hablás de este conteo, usá SOLO {g['valor']} (la oficial). "
                          f"Prohibido decir {var}: se cuenta en otro cap."]
    scr = [i for i in ch.get("pantalla_ids") or [] if i in its]
    if scr:
        lines += ["", "DATOS RESERVADOS PARA PANTALLA (NO los digas: salen escritos en pantalla en este cap):",
                  ev.format_pool(pool, scr)]
    lines += ["", F5_RULES]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  PROMPT — CAP 1 (HOOK)
# ═══════════════════════════════════════════════════════════════

def _prompt_hook(topic: dict, skeleton: dict) -> str:
    facts = _format_facts(topic.get("verified_facts") or [])
    skel = _format_skeleton(skeleton)
    topic_block = _format_topic_block(topic)
    cap1 = next((c for c in skeleton["chapters"] if c["chapter_number"] == 1), {})
    cap1_bullets = "\n".join(f"  • {b}" for b in cap1.get("bullets", []))
    cap1_intent = cap1.get("narrative_intent", "hook")
    tone_block = _tone_block(cap1_intent)
    lo, hi = LEN_HOOK

    return f"""Eres un narrador documental viral. Vas a redactar el HOOK (cap 1) de un
video corto en español sobre el siguiente tema.

═══════════════════════════════════════════════════
TEMA
═══════════════════════════════════════════════════
{topic_block}

═══════════════════════════════════════════════════
DATOS DUROS (única fuente válida de cifras/fechas/nombres)
═══════════════════════════════════════════════════
{facts}

═══════════════════════════════════════════════════
SKELETON COMPLETO (para que veas hacia dónde va el video)
═══════════════════════════════════════════════════
{skel}

═══════════════════════════════════════════════════
TU TAREA: redactar la narración del CAP 1 (HOOK).
═══════════════════════════════════════════════════

Función del HOOK: enganchar al espectador en los primeros 3 segundos.
Si el hook falla, el video falla. Esto es lo más importante del guion.

LARGO OBLIGATORIO: entre {lo} y {hi} caracteres.

BULLETS DEL CAP 1 (qué cubrir):
{cap1_bullets}
{_evidence_block(topic, skeleton, 1, [])}

REGLA DE APERTURA (CRÍTICA):
- Primera oración: MÁXIMO {HOOK_FIRST_SENTENCE_MAX_WORDS} palabras.
- Frase de IMPACTO directo. NO explicación. NO contexto.
- ✓ BIEN: "99 marinos. Sin un solo SOS."
- ✓ BIEN: "Junio de 2007. Un pueblo desapareció de los mapas."
- ✗ MAL : "En 1968, el USS Scorpion partió hacia el Mediterráneo..."
  (esto es contexto, no impacto)

REGLA DE CIERRE (CRÍTICA):
- Última oración deja flotando una incógnita / contradicción / promesa.
- El espectador debe NECESITAR ver el cap 2.
- ✓ BIEN: "Pero lo que ocurrió antes es peor."
- ✓ BIEN: "Y la advertencia llegó veinte años antes."
- ✗ MAL : "Y así comenzó esta tragedia." (cierre conformista)

{tone_block}
{_prose_rules(topic)}

FORMATO DE SALIDA — JSON puro, sin markdown:
{{
  "narration": "..."
}}

RESPONDE SOLO CON EL JSON."""


# ═══════════════════════════════════════════════════════════════
#  PROMPT — CAPS 2-6 (DEVELOPMENT)
# ═══════════════════════════════════════════════════════════════

def _prompt_development(topic: dict, skeleton: dict, previous: list[dict],
                        current_cap: int) -> str:
    facts = _format_facts(topic.get("verified_facts") or [])
    skel = _format_skeleton(skeleton)
    topic_block = _format_topic_block(topic)
    prev = _format_previous_narrations(previous)
    cap = next((c for c in skeleton["chapters"] if c["chapter_number"] == current_cap), {})
    cap_title = cap.get("title", "")
    cap_bullets = "\n".join(f"  • {b}" for b in cap.get("bullets", []))
    cap_intent = cap.get("narrative_intent", "")
    tone_block = _tone_block(cap_intent)
    lo, hi = LEN_DEVELOPMENT

    return f"""Eres un narrador documental viral. Vas a redactar el CAP {current_cap}
de un video corto en español.

═══════════════════════════════════════════════════
TEMA
═══════════════════════════════════════════════════
{topic_block}

═══════════════════════════════════════════════════
DATOS DUROS (única fuente válida de cifras/fechas/nombres)
═══════════════════════════════════════════════════
{facts}

═══════════════════════════════════════════════════
SKELETON COMPLETO
═══════════════════════════════════════════════════
{skel}

═══════════════════════════════════════════════════
NARRACIONES YA ESCRITAS (NO REPETIR FRASES NI DATOS YA DADOS)
═══════════════════════════════════════════════════
{prev}

═══════════════════════════════════════════════════
TU TAREA: redactar la narración del CAP {current_cap} — "{cap_title}"
═══════════════════════════════════════════════════

LARGO OBLIGATORIO: entre {lo} y {hi} caracteres.

BULLETS DE ESTE CAP (qué facts cubrir EXCLUSIVAMENTE en este cap):
{cap_bullets}
{_evidence_block(topic, skeleton, current_cap, previous)}

REGLA DE APERTURA (CRÍTICA):
- Primera oración CONECTA con el cliffhanger del cap anterior.
- NO repitas las palabras finales del cap anterior; continuá la idea
  con vocabulario nuevo.
- Si el cap anterior cerró abriendo una pregunta, este cap empieza
  acercándose a la respuesta (sin darla todavía).
- ✗ MAL: "A continuación...", "Por otra parte...", "Sigamos con..."

REGLA DE CONTENIDO:
- Cubrí ÚNICAMENTE los facts asignados a este cap (los del bullet list).
- NO uses datos de OTROS caps — están reservados para que esos caps
  los cuenten.
- Podés agregar contexto del summary o del canonical para describir
  ambiente, sin agregar cifras/nombres nuevos.

REGLA DE CIERRE (CRÍTICA):
- Cierra con cliffhanger hacia el cap {current_cap + 1}.
- Una pregunta retórica, una contradicción flotante, una promesa.
- ✗ MAL: "Esto continuó", "Y todo siguió igual", "El tiempo pasaba".

{tone_block}
{_prose_rules(topic)}

FORMATO DE SALIDA — JSON puro, sin markdown:
{{
  "narration": "..."
}}

RESPONDE SOLO CON EL JSON."""


# ═══════════════════════════════════════════════════════════════
#  PROMPT — CAP 7 (REVEAL + OUTRO)
# ═══════════════════════════════════════════════════════════════

def _prompt_outro(topic: dict, skeleton: dict, previous: list[dict]) -> str:
    facts = _format_facts(topic.get("verified_facts") or [])
    skel = _format_skeleton(skeleton)
    topic_block = _format_topic_block(topic)
    prev = _format_previous_narrations(previous)
    cap7 = next((c for c in skeleton["chapters"] if c["chapter_number"] == 7), {})
    cap7_bullets = "\n".join(f"  • {b}" for b in cap7.get("bullets", []))
    cap7_intent = cap7.get("narrative_intent", "outro")
    tone_block = _tone_block(cap7_intent)
    lo, hi = LEN_OUTRO

    return f"""Eres un narrador documental viral. Vas a redactar el CAP 7 (REVELACIÓN +
OUTRO) — el cierre del video.

═══════════════════════════════════════════════════
TEMA
═══════════════════════════════════════════════════
{topic_block}

═══════════════════════════════════════════════════
DATOS DUROS
═══════════════════════════════════════════════════
{facts}

═══════════════════════════════════════════════════
SKELETON COMPLETO
═══════════════════════════════════════════════════
{skel}

═══════════════════════════════════════════════════
NARRACIONES YA ESCRITAS
═══════════════════════════════════════════════════
{prev}

═══════════════════════════════════════════════════
TU TAREA: redactar la narración del CAP 7 (REVEAL + OUTRO).
═══════════════════════════════════════════════════

LARGO OBLIGATORIO: entre {lo} y {hi} caracteres.

BULLETS DEL CAP 7:
{cap7_bullets}
{_evidence_block(topic, skeleton, 7, previous)}

Función del OUTRO: cerrar el arco emocional. NO cliffhanger — el video
termina acá.

REGLA DE APERTURA:
- Primera oración conecta con el cliffhanger del cap 6.
- Acto seguido, REVELÁ la respuesta que el video venía preparando.
- Usa el campo "Revelación" del tema como núcleo del cap.

REGLA DE CIERRE (CRÍTICA):
- Última oración debe ser MEMORABLE. Puede ser:
  · Moraleja contundente sobre el tema.
  · Pregunta filosófica abierta.
  · Eco del hook (cierre circular, retomar la primera frase del cap 1).
- ✗ PROHIBIDO ABSOLUTO:
  · "Si te gustó, suscribite."
  · "Dejá tu comentario abajo."
  · "Compartí con tus amigos."
  · "Hasta el próximo video."
  · CUALQUIER llamada de YouTube.
- El video debe terminar con tono dramático/reflexivo, no con CTA.

{tone_block}
{_prose_rules(topic)}

FORMATO DE SALIDA — JSON puro, sin markdown:
{{
  "narration": "..."
}}

RESPONDE SOLO CON EL JSON."""


# ═══════════════════════════════════════════════════════════════
#  PROMPT — HUMANIZER PHRASES
# ═══════════════════════════════════════════════════════════════

def _prompt_humanizer(topic: dict, all_narrations: list[dict]) -> str:
    full_narration = "\n\n".join(
        f"Cap {n['chapter_number']}: {n['narration']}" for n in all_narrations
    )
    topic_title = topic.get("video_title", "")
    angle = topic.get("angle", "")

    return f"""Tenés un video documental ya redactado sobre:
"{topic_title}"

Ángulo: {angle}

Narración completa del video (los 7 caps):
{full_narration}

═══════════════════════════════════════════════════
TU TAREA: generar EXACTAMENTE {HUMANIZER_COUNT} frases humanizadoras
cortas, que se intercalarán en momentos clave del video como cortinas
narrativas.
═══════════════════════════════════════════════════

CRITERIOS — UNA frase de CADA tipo, en este orden:

1. SHOCK — incredulidad / impacto.
   Ejemplos genéricos:
     "Y eso fue solo el principio."
     "Y nadie pudo evitarlo."
     "Lo peor estaba por venir."

2. EMPATÍA — invita al espectador a ponerse en el lugar.
   Ejemplos genéricos:
     "Imaginá ser una de esas familias."
     "Pensá en ese instante."
     "Imaginá oírlo crujir."

3. NO OLVIDAR — cierre moral / llamado a la memoria.
   Ejemplos genéricos:
     "Que nunca vuelva a pasar."
     "Para que nadie lo olvide."
     "Su memoria sigue viva."

REGLAS INVIOLABLES:
- Cada frase: máximo {HUMANIZER_MAX_CHARS} caracteres (incluyendo espacios y puntuación).
- Español neutro.
- Sin nombres propios, sin cifras, sin fechas (deben servir para
  cualquier momento del video).
- Sin clichés de YouTube ("y ahora viene lo bueno", "no vas a creer",
  "atención a esto").
- Tono: serio, dramático, documental.
- Las frases deben sonar coherentes con el tono del video que leíste.

FORMATO DE SALIDA — JSON puro, sin markdown:
{{
  "humanizer_phrases": ["frase shock", "frase empatía", "frase no olvidar"]
}}

RESPONDE SOLO CON EL JSON."""


# ═══════════════════════════════════════════════════════════════
#  VALIDACIONES DETERMINÍSTICAS
# ═══════════════════════════════════════════════════════════════

class NarrationValidationError(ValueError):
    """Narración emitida por Flash no cumple el contrato del módulo 01b.

    `kind` tipa la falla para que el retry decida sin string-matchear el mensaje:
      "empty" | "length" | "first_sentence" | "phrase" | "other".
    `detail` lleva el dato accionable (p.ej. la frase prohibida emitida) para
    armar la dirección targeteada del reintento.
    """

    def __init__(self, msg: str, *, kind: str = "other", detail: str | None = None):
        super().__init__(msg)
        self.kind = kind
        self.detail = detail


# ═══════════════════════════════════════════════════════════════
#  RESPONSE SCHEMAS (Gemini) — HANDOFF 66b (R4)
#  Schemas PLAIN DICT, tipos UPPERCASE (estilo m03_visual._flux_anchor_schema).
#  DERIVADOS de los validadores y del contrato de salida de cada prompt.
# ═══════════════════════════════════════════════════════════════

def _narration_schema(with_ids: bool = False) -> dict:
    """Schema de la salida per-cap. El prompt pide {"narration": "..."} (el
    chapter_number lo agrega el código, NO el modelo). _validate_narration
    exige narration como string no vacío → único campo required.
    F5b N2: con evidence_pool, además "datos_usados" (ids del pool que el narrador DECLARA haber usado)."""
    if with_ids:
        return {
            "type": "OBJECT",
            "properties": {
                "narration": {"type": "STRING"},
                "datos_usados": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["narration", "datos_usados"],
        }
    return {
        "type": "OBJECT",
        "properties": {
            "narration": {"type": "STRING"},
        },
        "required": ["narration"],
    }


def _humanizer_schema() -> dict:
    """Schema de la salida del humanizer. El prompt pide
    {"humanizer_phrases": [3 strings]} y _validate_humanizer exige
    exactamente HUMANIZER_COUNT frases → array de strings con min/maxItems."""
    return {
        "type": "OBJECT",
        "properties": {
            "humanizer_phrases": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "minItems": HUMANIZER_COUNT,
                "maxItems": HUMANIZER_COUNT,
            },
        },
        "required": ["humanizer_phrases"],
    }


_SENTENCE_END = re.compile(r"[.!?]+")


def _first_sentence(text: str) -> str:
    """Devuelve la primera oración del texto.

    Chat 32: ignora marcadores de pausa "..." al inicio. Si el hook abre con
    una pausa, la validación de ≤N palabras debe medir la PRIMERA FRASE REAL,
    no el "...".
    """
    text = text.strip()
    text = re.sub(r"^[.…\s]+", "", text).strip()  # saltar "..." / "…" iniciales
    m = _SENTENCE_END.search(text)
    if not m:
        return text
    return text[: m.end()].strip()


def _word_count(text: str) -> int:
    return len([w for w in text.split() if w.strip()])


def _contains_any(text: str, needles: tuple[str, ...]) -> str | None:
    """Devuelve el primer needle encontrado o None."""
    tl = text.lower()
    for n in needles:
        if n in tl:
            return n
    return None


POOL_MIN_LEN_FACTOR = 1.15             # F5d: el narrador Pro escribe cerca del piso → mínimo de caracteres +15 %


def _len_range(role: str, min_factor: float = 1.0) -> tuple[int, int]:
    lo, hi = LEN_HOOK if role == "hook" else (LEN_OUTRO if role == "reveal_outro" else LEN_DEVELOPMENT)
    return min(int(round(lo * min_factor)), hi), hi


def _validate_narration(text: str, role: str, cap_number: int, f5: dict | None = None,
                        min_factor: float = 1.0) -> None:
    """Valida largo, primera oración (si hook), y frases prohibidas. Con `f5` ({pool, skeleton, previous}), además
    las reglas del evidence_pool (F5 §1.3) → kind="evidence" con la lista de problemas en `detail`."""
    if not isinstance(text, str) or not text.strip():
        raise NarrationValidationError(f"cap {cap_number}: narration vacía", kind="empty")

    n = len(text)

    # Largo según rol (F5d: con el narrador Pro, el mínimo sube POOL_MIN_LEN_FACTOR)
    lo, hi = _len_range(role, min_factor)

    if n < lo or n > hi:
        raise NarrationValidationError(
            f"cap {cap_number} ({role}): largo {n} fuera de rango [{lo}, {hi}]",
            kind="length",
        )

    # Hook: primera oración corta
    if role == "hook":
        first = _first_sentence(text)
        wc = _word_count(first)
        if wc > HOOK_FIRST_SENTENCE_MAX_WORDS:
            raise NarrationValidationError(
                f"cap 1 (hook): primera oración tiene {wc} palabras "
                f"(máx {HOOK_FIRST_SENTENCE_MAX_WORDS}): \"{first}\"",
                kind="first_sentence",
            )

    # Frases prohibidas en apertura
    head = text[:200].lower()
    bad = _contains_any(head, FORBIDDEN_OPENINGS)
    if bad:
        raise NarrationValidationError(
            f"cap {cap_number}: apertura prohibida — contiene \"{bad}\"",
            kind="phrase", detail=bad,
        )

    # Frases prohibidas en cierre (especialmente outro)
    tail = text[-200:].lower()
    bad = _contains_any(tail, FORBIDDEN_CLOSINGS)
    if bad:
        raise NarrationValidationError(
            f"cap {cap_number}: cierre prohibido — contiene \"{bad}\"",
            kind="phrase", detail=bad,
        )

    # Conectores genéricos en cualquier parte (suaves, sólo log/warn-style:
    # acá los hacemos bloqueantes para forzar reescritura)
    bad = _contains_any(text.lower(), GENERIC_CONNECTORS)
    if bad:
        raise NarrationValidationError(
            f"cap {cap_number}: conector genérico prohibido — contiene \"{bad}\"",
            kind="phrase", detail=bad,
        )

    if f5 and f5.get("pool"):                         # F5 §1.3: reglas del evidence_pool
        from script_engine.m05_narrative import cap_problems
        probs = cap_problems(text, cap=cap_number, pool=f5["pool"], skeleton=f5["skeleton"],
                             previous=f5.get("previous") or [], declared=f5.get("declared"))
        if probs:
            raise NarrationValidationError(
                f"cap {cap_number}: reglas del evidence_pool — " + " | ".join(probs),
                kind="evidence", detail="\n".join(f"- {x}" for x in probs),
            )


def _validate_humanizer(phrases: list) -> list[str]:
    """Normaliza y valida las 3 humanizer_phrases."""
    if not isinstance(phrases, list):
        raise NarrationValidationError("humanizer_phrases no es lista")
    clean = [str(p).strip() for p in phrases if str(p).strip()]
    if len(clean) != HUMANIZER_COUNT:
        raise NarrationValidationError(
            f"humanizer_phrases: se esperaban {HUMANIZER_COUNT}, llegaron {len(clean)}"
        )
    for i, p in enumerate(clean, start=1):
        if len(p) > HUMANIZER_MAX_CHARS:
            raise NarrationValidationError(
                f"humanizer #{i}: {len(p)} chars (máx {HUMANIZER_MAX_CHARS}): \"{p}\""
            )
        # Sin números
        if re.search(r"\d", p):
            raise NarrationValidationError(
                f"humanizer #{i}: contiene número: \"{p}\""
            )
    return clean


# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA
# ═══════════════════════════════════════════════════════════════

def _persist(topic_id: str, data: dict) -> Path:
    step_dir = STEPS_DIR / topic_id
    step_dir.mkdir(parents=True, exist_ok=True)
    out_file = step_dir / "01b_narration.json"
    out_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_file


# ═══════════════════════════════════════════════════════════════
#  RETRY CON FEEDBACK DE LARGO
# ═══════════════════════════════════════════════════════════════

# Split por límite de oración (lookbehind sobre el punto final + espacio). Maneja . ! ? …
_SENT_SPLIT = re.compile(r'(?<=[.!?…])\s+')


def _trim_to_sentence_boundary(text: str, max_chars: int) -> str:
    """Devuelve el prefijo más largo de `text` que (a) termina en oración completa
    y (b) mide ≤ max_chars. "" si ni la primera oración entra (→ el caller hace raise).

    Red de seguridad del outro (chat 51): un cierre un toque largo se recorta en el
    límite de la última oración que entra, sin partir palabras ni romper el arco.
    """
    out = ""
    for s in _SENT_SPLIT.split(text.strip()):
        cand = f"{out} {s}".strip() if out else s.strip()
        if len(cand) > max_chars:
            break
        out = cand
    return out


# F5c: con evidence_pool, el narrador es Gemini Pro y cada cap se elige entre 3 candidatos por puntaje
# (m05_narrative.cap_review). Sin pool, todo sigue por _call_with_length_retry con Flash, como antes.
POOL_NARRATOR = "pro"
POOL_BEST_OF = 3


def _call_narrator(prompt: str, model: str, cap_number: int) -> dict:
    schema = _narration_schema(with_ids=True)
    if model == "pro":
        return call_pro_json(prompt, response_schema=schema, description=f"01b narrador cap {cap_number} (pro)")
    return call_flash_json(prompt, response_schema=schema)


def _base_direction(e: "NarrationValidationError", narr: str, role: str, min_factor: float = 1.0) -> str:
    """Feedback de las reglas de siempre (largo, primera oración, frases prohibidas)."""
    lo, hi = _len_range(role, min_factor)
    if e.kind == "length":
        return (f"Tu intento tuvo {len(narr)} caracteres; el LARGO OBLIGATORIO es entre {lo} y {hi}. "
                f"{'Acortá' if len(narr) > hi else 'Alargá con datos del pool'} sin perder los datos.")
    if e.kind == "first_sentence":
        return f"La primera oración tiene que tener como máximo {HOOK_FIRST_SENTENCE_MAX_WORDS} palabras."
    if e.kind == "phrase":
        return f"Sacá «{e.detail}» y reescribí ese pasaje encadenando por contenido."
    return str(e)


def _best_of_n(prompt: str, role: str, cap_number: int, f5: dict, *, n: int = POOL_BEST_OF,
               model: str = POOL_NARRATOR, violations: dict | None = None, declared: dict | None = None,
               audit: dict | None = None) -> str:
    """F5c: genera hasta n candidatos del cap (el 2.º y el 3.º con el feedback del anterior: primero las reglas
    duras; las blandas, una sola vez), los puntúa con cap_review y se queda con el MEJOR, no con el último.
    Orden: pasa largo/frases y no tiene problemas duros → mayor puntaje → menos avisos blandos. Si ningún candidato
    pasa largo/frases, se comporta como antes (recorte del outro o error)."""
    from script_engine.m05_narrative import cap_review
    min_factor = POOL_MIN_LEN_FACTOR if model == "pro" else 1.0
    lo_, hi_ = _len_range(role, min_factor)
    prompt = (prompt + f"\n\nLARGO MÍNIMO REAL PARA ESTE NARRADOR: {lo_} caracteres (máximo {hi_}). El largo se llena "
              "con hechos y escenas del pool contadas con tus palabras, no con adjetivos.")
    cands: list[dict] = []
    attempt_prompt, soft_retry = prompt, False
    last_err: NarrationValidationError | None = None
    for k in range(1, n + 1):
        raw = _call_narrator(attempt_prompt, model, cap_number)
        narr = ev.fix_glued_caps((raw.get("narration") or "").strip())
        ids_raw = [str(x).strip() for x in raw.get("datos_usados") or [] if str(x).strip()]
        ids = ev.resolve_declared(ids_raw, f5["pool"], f5.get("facts"), narr)
        c = {"k": k, "narration": narr, "ids": ids, "base_ok": True, "review": None}
        try:
            _validate_narration(narr, role=role, cap_number=cap_number, min_factor=min_factor)
        except NarrationValidationError as e:
            c["base_ok"], c["base_error"], last_err = False, str(e), e
        if c["base_ok"]:
            c["review"] = cap_review(narr, cap=cap_number, pool=f5["pool"], skeleton=f5["skeleton"],
                                     previous=f5.get("previous") or [], declared=ids, facts=f5.get("facts"))
        cands.append(c)
        rv = c["review"]
        if c["base_ok"] and not rv["hard"] and (not rv["soft"] or soft_retry):
            break                                          # limpio, o blandas ya reintentadas una vez
        if k == n:
            break
        if not c["base_ok"]:
            direction = _base_direction(last_err, narr, role, min_factor)
        elif rv["hard"]:
            direction = ("REGLAS DURAS que tu intento no cumple (corregilas sin perder datos ni nombres):\n"
                         + "\n".join(f"- {x}" for x in rv["hard"]))
        else:
            soft_retry = True
            direction = ("AVISOS (reglas blandas; si no podés cumplir todo, sacrificá la ventana de adjetivos, nunca "
                         "los datos ni los nombres):\n" + "\n".join(f"- {x}" for x in rv["soft"]))
        attempt_prompt = (prompt + "\n\n═══════════════════════════════════════════════════\n"
                          f"REINTENTO {k + 1}/{n}\n═══════════════════════════════════════════════════\n"
                          + direction + "\n\nReescribí la narración completa y devolvé el JSON.")
        print(f"  [01b] cap {cap_number}: candidato {k}/{n} "
              + ("inválido (largo/frases)" if not c["base_ok"] else
                 f"puntaje {rv['score']} · {len(rv['hard'])} duras · {len(rv['soft'])} blandas"))
    ok = [c for c in cands if c["base_ok"]]
    if audit is not None:
        audit[cap_number] = [{"candidato": c["k"], "valido": c["base_ok"],
                              **({"puntaje": c["review"]["score"], "partes": c["review"]["parts"],
                                  "duras": len(c["review"]["hard"]), "blandas": len(c["review"]["soft"])}
                                 if c["review"] else {"error": c.get("base_error")})} for c in cands]
    if not ok:
        lo, hi = LEN_OUTRO
        narr = cands[-1]["narration"]
        if role == "reveal_outro" and len(narr) > hi:
            trimmed = _trim_to_sentence_boundary(narr, hi)
            if trimmed and lo <= len(trimmed) <= hi:
                if declared is not None:
                    declared[cap_number] = cands[-1]["ids"]
                return trimmed
        raise last_err
    best = max(ok, key=lambda c: (not c["review"]["hard"], c["review"]["score"], -len(c["review"]["soft"]), -c["k"]))
    if audit is not None:
        audit[cap_number] = {"elegido": best["k"], "candidatos": audit[cap_number]}
    if declared is not None:
        declared[cap_number] = best["ids"]
    probs = [f"- [dura] {x}" for x in best["review"]["hard"]] + [f"- [blanda] {x}" for x in best["review"]["soft"]]
    if violations is not None and probs:
        violations[cap_number] = probs
    print(f"  [01b] cap {cap_number}: elegido el candidato {best['k']}/{len(cands)} (puntaje {best['review']['score']}, "
          f"{len(best['review']['hard'])} duras, {len(best['review']['soft'])} blandas)")
    return best["narration"]


def _call_with_length_retry(prompt: str, role: str, cap_number: int,
                             max_attempts: int = 2, f5: dict | None = None,
                             violations: dict | None = None, declared: dict | None = None) -> str:
    """
    Llama Flash, valida largo y reglas, reintenta con feedback targeteado si la
    falla es reintentar-able (largo, primera-oración del hook, o FRASE prohibida
    —apertura/cierre/conector—). `kind="empty"`/`"other"` rompen sin retry.

    Funcionamiento:
      Intento 1: prompt original.
      Intento 2: prompt + sección RETRY con la dirección según el tipo de falla
                 (ajustar largo, acortar la 1ª oración, o sacar la frase prohibida
                 y reescribir ese pasaje).
    """
    if role == "hook":
        lo, hi = LEN_HOOK
    elif role == "reveal_outro":
        lo, hi = LEN_OUTRO
    else:
        lo, hi = LEN_DEVELOPMENT

    target = (lo + hi) // 2

    attempt_prompt = prompt
    last_error: NarrationValidationError | None = None
    best_pool_only: tuple[str, str] | None = None    # F5: intento que solo fallaba reglas del pool (largo y frases OK)

    ids: list[str] = []
    for attempt in range(1, max_attempts + 1):
        # HANDOFF 66b (R4): response_schema fuerza el shape {"narration": str}
        raw = call_flash_json(attempt_prompt, response_schema=_narration_schema(with_ids=bool(f5)))
        narr = (raw.get("narration") or "").strip()
        if f5:
            # F5b N5: mayúsculas pegadas del pool («…Schwarz, Arrestado por…»); N2: ids que declara el narrador
            narr = ev.fix_glued_caps(narr)
            ids_raw = [str(x).strip() for x in raw.get("datos_usados") or [] if str(x).strip()]
            ids = ev.resolve_declared(ids_raw, f5["pool"], f5.get("facts"), narr)   # «F05», «[D07]», texto → ids
            f5 = {**f5, "declared": ids}
        try:
            _validate_narration(narr, role=role, cap_number=cap_number, f5=f5)
            if declared is not None:
                declared[cap_number] = ids
            return narr
        except NarrationValidationError as e:
            # Retry si la falla es largo, primera-oración del hook, o frase prohibida.
            # (gate tipado: ya no se string-matchea el mensaje). "empty"/"other" → no retry.
            retryable = e.kind in ("length", "first_sentence", "phrase", "evidence")
            if e.kind == "evidence":
                best_pool_only = (narr, e.detail or "", ids)
            if e.kind != "evidence" and attempt == max_attempts and best_pool_only is not None:
                # F5: el último intento rompió el largo/frases, pero uno anterior solo fallaba reglas del pool → ese
                narr, det, ids = best_pool_only
                if violations is not None:
                    violations[cap_number] = det.splitlines()
                if declared is not None:
                    declared[cap_number] = ids
                print(f"  [01b] cap {cap_number}: último intento inválido ({e.kind}); acepta el anterior con "
                      f"{len(det.splitlines())} problema(s) del pool")
                return narr
            if e.kind == "evidence" and attempt == max_attempts:
                # F5: las reglas del pool no matan el topic — se acepta y se anota (el juez lo reporta)
                if violations is not None:
                    violations[cap_number] = (e.detail or "").splitlines()
                if declared is not None:
                    declared[cap_number] = ids
                print(f"  [01b] cap {cap_number}: acepta con {len((e.detail or '').splitlines())} problema(s) del pool")
                return narr
            if not retryable or attempt == max_attempts:
                # FIX DE RAÍZ (chat 51) — ÚLTIMO RECURSO, SOLO outro + SOLO lado largo:
                # un outro un toque sobre el techo NO debe matar un topic ya investigado
                # (3 angle Pro + Flash gastados). Recortar en límite de oración a ≤ hi y
                # re-aceptar. Si ni la primera oración entra (oración gigante > hi) o el
                # recorte cae < lo, el raise queda (falla legítima). hook/development NUNCA
                # se recortan (cortarían el gancho o el arco).
                if role == "reveal_outro" and len(narr) > hi:
                    trimmed = _trim_to_sentence_boundary(narr, hi)
                    if trimmed and lo <= len(trimmed) <= hi:
                        print(f"  [01b] cap {cap_number}: recortado por oración "
                              f"{len(narr)}→{len(trimmed)} chars (≤{hi}) — outro salvado")
                        return trimmed
                raise
            last_error = e

            actual_len = len(narr)
            if e.kind == "evidence":
                direction = (
                    "REGLAS DEL EVIDENCE POOL: tu intento previo tiene estos problemas:\n"
                    f"{e.detail}\nCorregilos manteniendo el largo dentro de rango. Usá los datos LITERALES "
                    "(cifra, fecha, nombre tal cual) y cambiá adjetivos por hechos."
                )
                reason = "reglas del evidence_pool"
            elif e.kind == "phrase":
                # Frase prohibida (apertura/cierre/conector): pedir que saque ESA frase y
                # reescriba el pasaje encadenando por contenido. El largo ya está en rango.
                direction = (
                    f'FRASE PROHIBIDA: tu intento previo usó "{e.detail}". Reescribí ESE '
                    "pasaje SIN esa frase, encadenando por el contenido (causa→efecto, "
                    "tensión→revelación). Mantené el largo dentro de rango y NO toques "
                    "los datos duros."
                )
                reason = f'frase prohibida "{e.detail}"'
            elif actual_len > hi:
                # 1.2: para el outro, instruir un techo con margen (deja aire → no se pasa
                # por poco). hook/development: instrucción intacta (techo = hi). La banda del
                # validador NO cambia en ningún caso.
                instructed_max = hi - OUTRO_RETRY_MARGIN if role == "reveal_outro" else hi
                direction = (
                    f"DEMASIADO LARGO: tu intento previo tuvo {actual_len} chars. "
                    f"Reescribilo con MÁXIMO {instructed_max} chars (objetivo ~{target}). "
                    "Quitá frases descriptivas secundarias, agrupá ideas afines, "
                    "eliminá adjetivos redundantes. NO quites datos duros."
                )
                reason = f"{actual_len} chars fuera de [{lo}, {hi}]"
            elif actual_len < lo:
                direction = (
                    f"DEMASIADO CORTO: tu intento previo tuvo {actual_len} chars. "
                    f"Reescribilo con MÍNIMO {lo} chars (objetivo ~{target}). "
                    "Profundizá con descripciones sensoriales del canonical o "
                    "detalles narrativos del summary (sin agregar cifras nuevas)."
                )
                reason = f"{actual_len} chars fuera de [{lo}, {hi}]"
            else:
                # Falla específica: primera oración del hook con muchas palabras
                direction = (
                    "PRIMERA ORACIÓN DEMASIADO LARGA: el hook abre con una frase "
                    f"de máximo {HOOK_FIRST_SENTENCE_MAX_WORDS} palabras. "
                    "Empezá con una frase de impacto cortísima."
                )
                reason = "primera oración del hook demasiado larga"

            feedback = f"""

═══════════════════════════════════════════════════
RETRY {attempt + 1}/{max_attempts} — INSTRUCCIÓN ADICIONAL DE REESCRITURA
═══════════════════════════════════════════════════
{direction}

Reescribí la narración respetando TODAS las reglas anteriores.
Devolvé el JSON con la nueva versión completa.
"""
            attempt_prompt = prompt + feedback
            print(f"  [01b] cap {cap_number}: {reason}, "
                  f"reintentando ({attempt + 1}/{max_attempts})...")

    # En teoría inalcanzable
    if last_error:
        raise last_error
    raise NarrationValidationError(f"cap {cap_number}: retry exhausted sin error capturado")


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA
# ═══════════════════════════════════════════════════════════════

def generate_narration(topic: dict, skeleton: dict) -> dict:
    """
    Genera narración cap-por-cap + 3 humanizer_phrases.

    Args:
        topic    : dict post módulo 00.
        skeleton : dict post módulo 01a (con 7 chapters).

    Returns:
        {
          "topic_id": str,
          "chapters": [{"chapter_number": int, "narration": str}, ... 7 items],
          "humanizer_phrases": [str, str, str]
        }

    Raises:
        NarrationValidationError si Flash devuelve algo fuera de contrato.
    """
    topic_id = topic.get("id") or topic.get("topic_id") or skeleton.get("topic_id")
    if not topic_id:
        raise ValueError("topic/skeleton sin id")

    chapters_skel = skeleton.get("chapters") or []
    if len(chapters_skel) != 7:
        raise ValueError(f"skeleton debe tener 7 caps, tiene {len(chapters_skel)}")

    narrations: list[dict] = []
    pool = topic.get("evidence_pool") if any("evidence_ids" in c for c in chapters_skel) else None
    violations: dict[int, list[str]] = {}
    tries = 3 if pool else 2

    def _f5() -> dict | None:
        return {"pool": pool, "skeleton": skeleton, "previous": list(narrations),
                "facts": topic.get("verified_facts") or []} if pool else None

    declared: dict[int, list[str]] = {}
    audit: dict[int, object] = {}

    def _narrate(prompt: str, role: str, cap_n: int, attempts: int) -> str:
        # F5c: con pool, Gemini Pro y el mejor de POOL_BEST_OF candidatos; sin pool, Flash con reintentos (igual que antes)
        if pool:
            return _best_of_n(prompt, role, cap_n, _f5(), violations=violations, declared=declared, audit=audit)
        return _call_with_length_retry(prompt, role=role, cap_number=cap_n, max_attempts=attempts, f5=None,
                                       violations=violations, declared=declared)

    def _cap(n: int, text: str) -> dict:
        # F5b N2: con pool, cada cap lleva los ids que el narrador declaró haber usado (las métricas cuentan por id)
        return {"chapter_number": n, "narration": text, **({"datos_usados": declared.get(n, [])} if pool else {})}

    # ─── CAP 1: HOOK ───
    print(f"  [01b] generando cap 1 (hook)...")
    prompt1 = _prompt_hook(topic, skeleton)
    narr1 = _narrate(prompt1, "hook", 1, tries)
    narrations.append(_cap(1, narr1))

    # ─── CAPS 2-6: DEVELOPMENT ───
    for cap_n in (2, 3, 4, 5, 6):
        print(f"  [01b] generando cap {cap_n} (development)...")
        prompt = _prompt_development(topic, skeleton, narrations, cap_n)
        narr = _narrate(prompt, "development", cap_n, tries)
        narrations.append(_cap(cap_n, narr))

    # ─── CAP 7: OUTRO ───
    print(f"  [01b] generando cap 7 (reveal+outro)...")
    prompt7 = _prompt_outro(topic, skeleton, narrations)
    # 1.3 (chat 51): un intento más SOLO para el outro (que converja antes de tocar el
    # recorte). hook/development quedan en max_attempts=2 (default).
    narr7 = _narrate(prompt7, "reveal_outro", 7, 3)
    narrations.append(_cap(7, narr7))

    # ─── HUMANIZER PHRASES ───
    print(f"  [01b] generando humanizer phrases...")
    # HANDOFF 66b (R4): response_schema fuerza {"humanizer_phrases": [3 strings]}
    raw_h = call_flash_json(_prompt_humanizer(topic, narrations), response_schema=_humanizer_schema())
    humanizer = _validate_humanizer(raw_h.get("humanizer_phrases") or [])

    out = {
        "topic_id": topic_id,
        "chapters": narrations,
        "humanizer_phrases": humanizer,
        **({"_f5_violations": {str(k): v for k, v in violations.items()},
            "_f5c_candidatos": {str(k): v for k, v in audit.items()},
            "_narrador": {"modelo": POOL_NARRATOR, "mejor_de": POOL_BEST_OF}} if pool else {}),
    }
    _persist(topic_id, out)
    return out


def regenerate_caps(topic: dict, skeleton: dict, narration: dict, caps: list[int],
                    extra: dict[int, str] | None = None) -> dict:
    """Retoque (F5d+): rehace SOLO los caps pedidos con el mejor de POOL_BEST_OF, con una instrucción extra por cap; el
    resto de la narración queda byte-idéntica. Cada cap ve como «anteriores» los caps ya definitivos (incluidos los
    retocados antes que él). Persiste 01b_narration.json con `_retoque` anotado."""
    pool = topic.get("evidence_pool")
    if not pool:
        raise ValueError("regenerate_caps es para guiones con evidence_pool")
    chapters = [dict(c) for c in sorted(narration["chapters"], key=lambda c: c["chapter_number"])]
    violations = {int(k): v for k, v in (narration.get("_f5_violations") or {}).items()}
    audit: dict = {int(k): v for k, v in (narration.get("_f5c_candidatos") or {}).items()}
    declared: dict[int, list[str]] = {}
    roles = {1: "hook", 7: "reveal_outro"}
    for n in sorted(caps):
        prev = [c for c in chapters if c["chapter_number"] < n]
        if n == 1:
            prompt = _prompt_hook(topic, skeleton)
        elif n == 7:
            prompt = _prompt_outro(topic, skeleton, prev)
        else:
            prompt = _prompt_development(topic, skeleton, prev, n)
        if extra and extra.get(n):
            prompt += ("\n\n═══════════════════════════════════════════════════\nRETOQUE PEDIDO PARA ESTE CAP\n"
                       "═══════════════════════════════════════════════════\n" + extra[n])
        f5 = {"pool": pool, "skeleton": skeleton, "previous": prev, "facts": topic.get("verified_facts") or []}
        violations.pop(n, None)
        text = _best_of_n(prompt, roles.get(n, "development"), n, f5, violations=violations, declared=declared,
                          audit=audit)
        k = next(i for i, c in enumerate(chapters) if c["chapter_number"] == n)
        chapters[k] = {"chapter_number": n, "narration": text, "datos_usados": declared.get(n, [])}
    out = {**narration, "chapters": chapters,
           "_f5_violations": {str(k): v for k, v in violations.items()},
           "_f5c_candidatos": {str(k): v for k, v in audit.items()},
           "_retoque": {"caps": sorted(caps), "instrucciones": {str(k): v for k, v in (extra or {}).items()}}}
    _persist(narration["topic_id"], out)
    return out
