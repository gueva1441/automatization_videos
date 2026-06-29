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
"""

import json
import re
from pathlib import Path

from config import DATA_DIR
from gemini_helpers import call_flash_json


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
{PROSE_RULES}

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
{PROSE_RULES}

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
{PROSE_RULES}

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

def _narration_schema() -> dict:
    """Schema de la salida per-cap. El prompt pide {"narration": "..."} (el
    chapter_number lo agrega el código, NO el modelo). _validate_narration
    exige narration como string no vacío → único campo required."""
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


def _validate_narration(text: str, role: str, cap_number: int) -> None:
    """Valida largo, primera oración (si hook), y frases prohibidas."""
    if not isinstance(text, str) or not text.strip():
        raise NarrationValidationError(f"cap {cap_number}: narration vacía", kind="empty")

    n = len(text)

    # Largo según rol
    if role == "hook":
        lo, hi = LEN_HOOK
    elif role == "reveal_outro":
        lo, hi = LEN_OUTRO
    else:
        lo, hi = LEN_DEVELOPMENT

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


def _call_with_length_retry(prompt: str, role: str, cap_number: int,
                             max_attempts: int = 2) -> str:
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

    for attempt in range(1, max_attempts + 1):
        # HANDOFF 66b (R4): response_schema fuerza el shape {"narration": str}
        raw = call_flash_json(attempt_prompt, response_schema=_narration_schema())
        narr = (raw.get("narration") or "").strip()
        try:
            _validate_narration(narr, role=role, cap_number=cap_number)
            return narr
        except NarrationValidationError as e:
            # Retry si la falla es largo, primera-oración del hook, o frase prohibida.
            # (gate tipado: ya no se string-matchea el mensaje). "empty"/"other" → no retry.
            retryable = e.kind in ("length", "first_sentence", "phrase")
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
            if e.kind == "phrase":
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

    # ─── CAP 1: HOOK ───
    print(f"  [01b] generando cap 1 (hook)...")
    prompt1 = _prompt_hook(topic, skeleton)
    narr1 = _call_with_length_retry(prompt1, role="hook", cap_number=1)
    narrations.append({"chapter_number": 1, "narration": narr1})

    # ─── CAPS 2-6: DEVELOPMENT ───
    for cap_n in (2, 3, 4, 5, 6):
        print(f"  [01b] generando cap {cap_n} (development)...")
        prompt = _prompt_development(topic, skeleton, narrations, cap_n)
        narr = _call_with_length_retry(prompt, role="development", cap_number=cap_n)
        narrations.append({"chapter_number": cap_n, "narration": narr})

    # ─── CAP 7: OUTRO ───
    print(f"  [01b] generando cap 7 (reveal+outro)...")
    prompt7 = _prompt_outro(topic, skeleton, narrations)
    # 1.3 (chat 51): un intento más SOLO para el outro (que converja antes de tocar el
    # recorte). hook/development quedan en max_attempts=2 (default).
    narr7 = _call_with_length_retry(prompt7, role="reveal_outro", cap_number=7, max_attempts=3)
    narrations.append({"chapter_number": 7, "narration": narr7})

    # ─── HUMANIZER PHRASES ───
    print(f"  [01b] generando humanizer phrases...")
    # HANDOFF 66b (R4): response_schema fuerza {"humanizer_phrases": [3 strings]}
    raw_h = call_flash_json(_prompt_humanizer(topic, narrations), response_schema=_humanizer_schema())
    humanizer = _validate_humanizer(raw_h.get("humanizer_phrases") or [])

    out = {
        "topic_id": topic_id,
        "chapters": narrations,
        "humanizer_phrases": humanizer,
    }
    _persist(topic_id, out)
    return out
