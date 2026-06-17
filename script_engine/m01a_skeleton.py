"""
script_engine/m01a_skeleton.py — Módulo 01a: estructurador.

TAREA ÚNICA: a partir del topic completo (output del módulo 00), generar
el SKELETON de 7 capítulos. SIN narración, SIN profiles.

INPUT:  topic (dict, el que está en topics_db.json post módulo 00)
OUTPUT: {
  "topic_id": "uuid",
  "chapters": [
    {
      "chapter_number": 1..7,
      "title": "...",
      "role": "hook" | "development" | "reveal_outro",
      "render_engine": "veo" | "flux",
      "duration_seconds": int,
      "bullets": ["...", ...]   # 4-7 frases nominales
    },
    ...
  ]
}

ESTRUCTURA INTERNA (1 archivo, 5 funciones privadas + 1 pública):
  _build_prompt(topic)            → str
  _validate_distribution_plan(...)→ raise si falla
  _validate_skeleton(data)        → raise si falla
  _enforce_structure(chapters)    → list normalizada
  _persist(topic_id, full)        → escribe _steps/{topic_id}/01a_skeleton.json
  generate_skeleton(topic)        → dict        # PÚBLICA

LLAMADAS GEMINI: 1 (Flash con JSON mode).

NOTA SOBRE _distribution_plan:
  Flash genera primero un plan que asigna cada fact [F##] a un cap
  intermedio (2-6). Esto fuerza planning-before-generation y elimina
  redundancia entre caps de desarrollo. El plan se PERSISTE en el JSON
  intermedio (auditoría) pero NO se devuelve en el output público.
"""

import json
from pathlib import Path

from config import DATA_DIR
from gemini_helpers import call_flash_json


# ═══════════════════════════════════════════════════════════════
#  PATHS Y CONSTANTES
# ═══════════════════════════════════════════════════════════════

STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"

# Estructura fija del skeleton — NO se le pide a Flash que la decida.
CHAPTER_SCHEMA = [
    {"chapter_number": 1, "role": "hook",         "render_engine": "veo",  "duration_seconds": 45},
    {"chapter_number": 2, "role": "development",  "render_engine": "flux", "duration_seconds": 75},
    {"chapter_number": 3, "role": "development",  "render_engine": "flux", "duration_seconds": 75},
    {"chapter_number": 4, "role": "development",  "render_engine": "flux", "duration_seconds": 75},
    {"chapter_number": 5, "role": "development",  "render_engine": "flux", "duration_seconds": 75},
    {"chapter_number": 6, "role": "development",  "render_engine": "flux", "duration_seconds": 75},
    {"chapter_number": 7, "role": "reveal_outro", "render_engine": "veo",  "duration_seconds": 45},
]

MIN_BULLETS_PER_CHAPTER = 4
MAX_BULLETS_PER_CHAPTER = 7

MAX_RETRY_ATTEMPTS = 3
# 1 intento original + 2 retries con feedback enriquecido. La falla típica
# (_distribution_plan no cubre todos los facts, bullets fuera de rango)
# suele corregirse en intento 2; el 3ro queda como red de seguridad.

# Caps intermedios sobre los que aplica la regla de distribución única.
DEVELOPMENT_CAPS = (2, 3, 4, 5, 6)


# ═══════════════════════════════════════════════════════════════
#  NARRATIVE INTENT — catálogo cerrado y defaults por cap (PR 2.A chat 24)
# ═══════════════════════════════════════════════════════════════

VALID_NARRATIVE_INTENTS: frozenset[str] = frozenset({
    "hook", "setup", "rising_tension", "shock",
    "consequences", "resolution", "outro",
})

DEFAULT_INTENT_BY_CAP: dict[int, str] = {
    1: "hook",
    2: "setup",
    3: "rising_tension",
    4: "shock",
    5: "consequences",
    6: "resolution",
    7: "outro",
}


# ═══════════════════════════════════════════════════════════════
#  CONSTRUCCIÓN DEL PROMPT
# ═══════════════════════════════════════════════════════════════

def _format_facts(verified_facts: list) -> str:
    """Enumera verified_facts numerados para que el prompt los referencie."""
    if not verified_facts:
        return "(sin facts)"

    lines = []
    for i, f in enumerate(verified_facts, start=1):
        if isinstance(f, dict):
            text = (f.get("fact") or "").strip()
            block = (f.get("source_block") or "").strip()
            tag = f" [{block}]" if block else ""
            lines.append(f"  [F{i:02d}] {text}{tag}")
        elif isinstance(f, str):
            # Tolerancia retro-compat: facts en formato viejo (list[str])
            lines.append(f"  [F{i:02d}] {f.strip()}")
    return "\n".join(lines)


def _fact_ids(verified_facts: list) -> list[str]:
    """Devuelve la lista de IDs [F01, F02, ...] correspondiente a los facts."""
    return [f"F{i:02d}" for i in range(1, len(verified_facts) + 1)]


def _build_prompt(topic: dict) -> str:
    """Construye el prompt Flash del módulo 01a."""
    video_title = topic.get("video_title") or "(sin título)"
    topic_title = topic.get("topic_title") or video_title
    angle = topic.get("angle") or "(sin ángulo)"
    hook = topic.get("hook") or "(sin hook)"
    mystery = topic.get("mystery") or "(sin misterio)"
    reveal = topic.get("reveal") or "(sin revelación)"
    canonical = topic.get("canonical_subject_description") or "(sin canonical)"
    summary = topic.get("research_summary") or "(sin summary)"
    facts = topic.get("verified_facts") or []
    facts_block = _format_facts(facts)
    fact_ids = _fact_ids(facts)
    n_facts = len(facts)

    return f"""Eres un guionista narrativo. Tienes investigación CERRADA sobre un tema y debes
generar el ESQUELETO de un video documental de 7 capítulos.

═══════════════════════════════════════════════════
TEMA
═══════════════════════════════════════════════════
Título del video : {video_title}
Topic            : {topic_title}
Ángulo dominante : {angle}

Hook        : {hook}
Misterio    : {mystery}
Revelación  : {reveal}

═══════════════════════════════════════════════════
DESCRIPCIÓN CANÓNICA DEL SUJETO
═══════════════════════════════════════════════════
{canonical}

═══════════════════════════════════════════════════
DATOS DUROS (verified_facts) — ÚNICA fuente válida de cifras/fechas/nombres
═══════════════════════════════════════════════════
{facts_block}

Total de facts disponibles: {n_facts}  →  IDs: {", ".join(fact_ids) if fact_ids else "(ninguno)"}

═══════════════════════════════════════════════════
RESEARCH SUMMARY (contexto narrativo, NO datos nuevos)
═══════════════════════════════════════════════════
{summary}

═══════════════════════════════════════════════════
TU TAREA: emitir el skeleton de 7 capítulos en DOS PASOS dentro del mismo JSON.
═══════════════════════════════════════════════════

ESTRUCTURA FIJA (NO la cambies):
- Cap 1 : HOOK             (45s, render veo) — abre con el gancho.
- Cap 2 : DESARROLLO       (75s, render flux) — escenario / contexto inicial.
- Cap 3 : DESARROLLO       (75s, render flux) — entra el problema/conflicto.
- Cap 4 : DESARROLLO       (75s, render flux) — el conflicto escala.
- Cap 5 : DESARROLLO       (75s, render flux) — punto de inflexión.
- Cap 6 : DESARROLLO       (75s, render flux) — antesala de la revelación.
- Cap 7 : REVELACIÓN+OUTRO (45s, render veo) — cierra con la revelación.

═══════════════════════════════════════════════════
PASO 1 OBLIGATORIO — `_distribution_plan`
═══════════════════════════════════════════════════

ANTES de escribir cualquier bullet, generá el plan de distribución que
asigna CADA fact [F##] a EXACTAMENTE UN cap intermedio (cap_2..cap_6).

REGLAS INVIOLABLES del plan:
1. Cada fact [F##] aparece UNA SOLA VEZ en todo el plan.
2. Todos los {n_facts} facts disponibles deben quedar asignados.
3. Cada cap_2..cap_6 puede recibir entre 0 y N facts (la cantidad la
   decidís según pertinencia temática).
4. Agrupá los facts por afinidad temática:
   - facts sobre el mismo objeto/persona/momento → mismo cap.
   - facts cronológicamente cercanos → mismo cap o caps contiguos.
5. La SECUENCIA de caps debe seguir progresión narrativa creciente
   (escenario → conflicto → escalada → inflexión → antesala revelación).

EJEMPLO de plan correcto (un fact en un solo cap):
{{
  "_distribution_plan": {{
    "cap_2": ["F01", "F04"],
    "cap_3": ["F07"],
    "cap_4": ["F02", "F08"],
    "cap_5": ["F03"],
    "cap_6": ["F05", "F06", "F09"]
  }}
}}

PROHIBIDO:
✗ Repetir un fact en dos caps:
   "cap_3": ["F05"], "cap_4": ["F05"]   ← INVÁLIDO
✗ Dejar un fact afuera del plan:
   facts disponibles F01..F09, plan solo cubre F01..F08   ← INVÁLIDO

═══════════════════════════════════════════════════
PASO 1.5 OBLIGATORIO — narrative_intent por cap
═══════════════════════════════════════════════════

Para cada uno de los 7 caps emití el campo "narrative_intent" eligiendo
EXACTAMENTE UNO de estos 7 valores (catálogo cerrado, NO inventes otros):

  hook            — tensión + promesa. Apertura impactante.
  setup           — contexto eficiente. Pacing calmo.
  rising_tension  — el conflicto escala. Pacing apretado.
  shock           — pattern interrupt al 50%. Frases muy cortas.
  consequences    — peso emocional, reflexión sobre lo perdido.
  resolution      — bajada de intensidad, pacing pausado.
  outro           — cierre con pregunta sin respuesta.

ASIGNACIÓN POR DEFAULT (úsala salvo justificación fuerte del topic):
  cap 1 → "hook"
  cap 2 → "setup"
  cap 3 → "rising_tension"
  cap 4 → "shock"
  cap 5 → "consequences"
  cap 6 → "resolution"
  cap 7 → "outro"

Solo desviá del default si el topic claramente lo amerita (ej: un topic
sin "shock" real puede mantener "rising_tension" en cap 4). Si dudás,
quedate con el default.

═══════════════════════════════════════════════════
PASO 2 — bullets de cada cap
═══════════════════════════════════════════════════

Después del plan, escribí los bullets de los 7 caps respetando la
distribución que acabás de fijar.

REGLAS DE BULLETS POR CAP:
1. Entre {MIN_BULLETS_PER_CHAPTER} y {MAX_BULLETS_PER_CHAPTER} bullets por cap.
2. FRASES NOMINALES, NO oraciones completas.
   ✓ BIEN : "Junio 2007: borrado oficial del mapa"
   ✓ BIEN : "Casas de chapa corrugada en el outback aislado"
   ✗ MAL  : "En junio de 2007, el gobierno borró Wittenoom del mapa."
   ✗ MAL  : "Las casas eran de chapa corrugada."
3. IDIOMA: español neutro. NO uses anglicismos sin traducir.
   ✗ MAL : "Sección de popa telescoped sobre sí misma"
   ✓ BIEN : "Sección de popa colapsada sobre sí misma"
4. Cada bullet con cifra, fecha, nombre propio o detalle visual concreto
   cuando sea posible.
5. **REGLA NUMÉRICA INVIOLABLE**: cualquier cifra, fecha, nombre propio
   o cantidad que aparezca en un bullet DEBE existir LITERALMENTE en
   algún fact [F##] de la lista. NO inventes números, fechas ni nombres.

DISTRIBUCIÓN DE BULLETS POR ROL:
- **Cap 1 (hook)**: bullets que abren con impacto. Toma facts del hook,
  el día/lugar dramático, una cifra fuerte. PUEDE reusar facts que
  estén asignados a algún cap intermedio en el plan — el hook abre y
  los caps intermedios profundizan.
- **Cap 2-6 (desarrollo)**: bullets cubren ÚNICAMENTE los facts que les
  asignaste en el plan, más descripciones visuales del canonical o
  detalles del summary que aporten contexto SIN cifras/nombres nuevos.
  Si un cap tiene 0 facts asignados, sus bullets son 100% visuales/de
  contexto, sin números.
- **Cap 7 (reveal_outro)**: bullets que componen la revelación + cierre
  emocional. PUEDE reusar facts ya cubiertos por caps intermedios —
  eso es lo esperado, el outro retoma para cerrar.

REGLA ANTI-REDUNDANCIA (caps 2-6 entre sí):
Como cada fact está en UN solo cap del plan, los bullets numéricos de
los caps 2-6 NO se repetirán entre sí. Si te das cuenta de que estás
escribiendo el mismo dato en dos caps de desarrollo, eso significa que
violaste el plan — corregí el plan o el bullet.

REGLAS DE `title` (por capítulo):
- 2-6 palabras, en español, evocador y específico AL TEMA DEL CAP.
- El title debe describir QUÉ pasa en ese cap, no ser genérico.
- Ej. del cap 2 si trata defectos del submarino: "Un submarino con defectos" ✓
- Ej. del cap 3 si trata del último contacto: "El último mensaje" ✓
- ✗ MAL : "Capítulo 2", "El problema", "Más detalles"

═══════════════════════════════════════════════════
FORMATO DE SALIDA — JSON puro, sin markdown, sin texto adicional
═══════════════════════════════════════════════════

{{
  "_distribution_plan": {{
    "cap_2": ["F##", "F##"],
    "cap_3": ["F##"],
    "cap_4": ["F##", "F##"],
    "cap_5": ["F##"],
    "cap_6": ["F##", "F##"]
  }},
  "chapters": [
    {{
      "chapter_number": 1,
      "title": "...",
      "narrative_intent": "hook",
      "bullets": ["...", "...", "...", "..."]
    }},
    {{
      "chapter_number": 2,
      "title": "...",
      "narrative_intent": "setup",
      "bullets": ["...", "...", "...", "..."]
    }},
    {{
      "chapter_number": 3,
      "title": "...",
      "narrative_intent": "rising_tension",
      "bullets": ["...", "...", "...", "..."]
    }},
    {{
      "chapter_number": 4,
      "title": "...",
      "narrative_intent": "shock",
      "bullets": ["...", "...", "...", "..."]
    }},
    {{
      "chapter_number": 5,
      "title": "...",
      "narrative_intent": "consequences",
      "bullets": ["...", "...", "...", "..."]
    }},
    {{
      "chapter_number": 6,
      "title": "...",
      "narrative_intent": "resolution",
      "bullets": ["...", "...", "...", "..."]
    }},
    {{
      "chapter_number": 7,
      "title": "...",
      "narrative_intent": "outro",
      "bullets": ["...", "...", "...", "..."]
    }}
  ]
}}

NO incluyas role, render_engine ni duration_seconds en tu respuesta — esos
campos los completa el código localmente.

RESPONDE SOLO CON EL JSON."""


# ═══════════════════════════════════════════════════════════════
#  VALIDACIONES DETERMINÍSTICAS
# ═══════════════════════════════════════════════════════════════

class SkeletonValidationError(ValueError):
    """Skeleton emitido por Flash no cumple el contrato del módulo 01a."""


def _validate_distribution_plan(plan: dict, expected_fact_ids: list[str]) -> None:
    """
    Valida el _distribution_plan emitido por Flash.

    Reglas:
      - Llaves: cap_2..cap_6 (no más, no menos).
      - Cada fact_id de expected_fact_ids aparece EXACTAMENTE UNA vez
        sumando todas las llaves.
      - Ningún fact_id desconocido.
    """
    if not isinstance(plan, dict):
        raise SkeletonValidationError("_distribution_plan no es dict")

    expected_keys = {f"cap_{i}" for i in DEVELOPMENT_CAPS}
    actual_keys = set(plan.keys())
    if actual_keys != expected_keys:
        missing = expected_keys - actual_keys
        extra = actual_keys - expected_keys
        raise SkeletonValidationError(
            f"_distribution_plan llaves inválidas. "
            f"Faltan: {sorted(missing) or '∅'}. Sobran: {sorted(extra) or '∅'}."
        )

    seen: dict[str, str] = {}  # fact_id -> cap_key donde apareció
    expected_set = set(expected_fact_ids)
    unknown: list[str] = []

    for cap_key in sorted(expected_keys):
        items = plan.get(cap_key) or []
        if not isinstance(items, list):
            raise SkeletonValidationError(
                f"_distribution_plan[{cap_key}] no es lista"
            )
        for fid in items:
            fid_norm = str(fid).strip().upper()
            if fid_norm not in expected_set:
                unknown.append(fid_norm)
                continue
            if fid_norm in seen:
                raise SkeletonValidationError(
                    f"Fact {fid_norm} aparece en {seen[fid_norm]} y también en {cap_key} "
                    f"(cada fact debe estar en exactamente 1 cap intermedio)"
                )
            seen[fid_norm] = cap_key

    if unknown:
        raise SkeletonValidationError(
            f"_distribution_plan referencia facts inexistentes: {sorted(set(unknown))}"
        )

    missing_facts = expected_set - set(seen.keys())
    if missing_facts:
        raise SkeletonValidationError(
            f"_distribution_plan no cubre todos los facts. Faltan: {sorted(missing_facts)}"
        )


def _validate_skeleton(data: dict) -> None:
    """Valida estructura del skeleton. Raise SkeletonValidationError si falla."""
    if not isinstance(data, dict):
        raise SkeletonValidationError(f"data no es dict: {type(data).__name__}")

    chapters = data.get("chapters")
    if not isinstance(chapters, list):
        raise SkeletonValidationError("falta lista 'chapters'")
    if len(chapters) != 7:
        raise SkeletonValidationError(f"se esperaban 7 caps, llegaron {len(chapters)}")

    for i, ch in enumerate(chapters, start=1):
        if not isinstance(ch, dict):
            raise SkeletonValidationError(f"cap {i} no es dict")

        cn = ch.get("chapter_number")
        if cn != i:
            raise SkeletonValidationError(
                f"cap pos {i}: chapter_number={cn} (esperado {i})"
            )

        title = (ch.get("title") or "").strip()
        if not title:
            raise SkeletonValidationError(f"cap {i}: title vacío")
        if len(title) > 80:
            raise SkeletonValidationError(f"cap {i}: title demasiado largo ({len(title)} chars)")

        bullets = ch.get("bullets")
        if not isinstance(bullets, list):
            raise SkeletonValidationError(f"cap {i}: bullets no es lista")

        clean_bullets = [str(b).strip() for b in bullets if str(b).strip()]
        n = len(clean_bullets)
        if n < MIN_BULLETS_PER_CHAPTER or n > MAX_BULLETS_PER_CHAPTER:
            raise SkeletonValidationError(
                f"cap {i}: {n} bullets (esperado {MIN_BULLETS_PER_CHAPTER}-{MAX_BULLETS_PER_CHAPTER})"
            )

        expected = CHAPTER_SCHEMA[i - 1]
        for field in ("role", "render_engine", "duration_seconds"):
            if field in ch and ch[field] != expected[field]:
                raise SkeletonValidationError(
                    f"cap {i}: {field}={ch[field]!r} (esperado {expected[field]!r})"
                )

        # PR 2.A chat 24: validación dura del narrative_intent.
        intent = ch.get("narrative_intent")
        if intent is None:
            raise SkeletonValidationError(
                f"cap {i}: falta campo 'narrative_intent'"
            )
        if intent not in VALID_NARRATIVE_INTENTS:
            raise SkeletonValidationError(
                f"cap {i}: narrative_intent={intent!r} no está en el catálogo "
                f"válido {sorted(VALID_NARRATIVE_INTENTS)}"
            )


def _enforce_structure(chapters: list) -> list:
    """Inyecta role / render_engine / duration_seconds, normaliza bullets,
    y aplica fallback al default de narrative_intent si el LLM no lo emitió."""
    out = []
    for i, ch in enumerate(chapters, start=1):
        expected = CHAPTER_SCHEMA[i - 1]
        bullets = [str(b).strip() for b in (ch.get("bullets") or []) if str(b).strip()]

        # Fallback: si LLM no emitió narrative_intent o emitió uno fuera del
        # catálogo, caer al default por cap. La validación dura en
        # _validate_skeleton agarra el caso de "está pero es inválido"; este
        # fallback solo cubre "está vacío o ausente".
        intent = ch.get("narrative_intent")
        if not isinstance(intent, str) or not intent.strip():
            intent = DEFAULT_INTENT_BY_CAP.get(i, "setup")

        out.append({
            "chapter_number": i,
            "title": (ch.get("title") or "").strip(),
            "role": expected["role"],
            "render_engine": expected["render_engine"],
            "duration_seconds": expected["duration_seconds"],
            "narrative_intent": intent,
            "bullets": bullets,
        })
    return out


# ═══════════════════════════════════════════════════════════════
#  RESPONSE SCHEMA (HANDOFF 66b · R4) — derivado de _validate_skeleton /
#  _validate_distribution_plan. Fuerza a Gemini a decodificar JSON válido
#  (mata la clase "comillas dobles sin escapar" en la fuente).
# ═══════════════════════════════════════════════════════════════

def _skeleton_schema() -> dict:
    dev_caps = {f"cap_{i}": {"type": "ARRAY", "items": {"type": "STRING"}}
                for i in DEVELOPMENT_CAPS}
    return {
        "type": "OBJECT",
        "properties": {
            "_distribution_plan": {
                "type": "OBJECT",
                "properties": dev_caps,
                "required": [f"cap_{i}" for i in DEVELOPMENT_CAPS],
            },
            "chapters": {
                "type": "ARRAY", "minItems": 7, "maxItems": 7,
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "chapter_number": {"type": "INTEGER"},
                        "title": {"type": "STRING"},
                        "narrative_intent": {"type": "STRING"},
                        "bullets": {
                            "type": "ARRAY", "items": {"type": "STRING"},
                            "minItems": MIN_BULLETS_PER_CHAPTER,
                            "maxItems": MAX_BULLETS_PER_CHAPTER,
                        },
                    },
                    "required": ["chapter_number", "title", "narrative_intent", "bullets"],
                },
            },
        },
        "required": ["_distribution_plan", "chapters"],
    }


# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA
# ═══════════════════════════════════════════════════════════════

def _persist(topic_id: str, full_data: dict) -> Path:
    """
    Escribe data/scripts/_steps/{topic_id}/01a_skeleton.json.

    El JSON intermedio incluye `_distribution_plan` para auditoría.
    El output retornado por generate_skeleton lo descarta.
    """
    step_dir = STEPS_DIR / topic_id
    step_dir.mkdir(parents=True, exist_ok=True)
    out_file = step_dir / "01a_skeleton.json"
    out_file.write_text(
        json.dumps(full_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_file


# ═══════════════════════════════════════════════════════════════
#  LLAMADA FLASH CON RETRY POR FEEDBACK
# ═══════════════════════════════════════════════════════════════

def _call_with_validation_retry(
    prompt: str,
    expected_fact_ids: list[str],
    max_attempts: int = MAX_RETRY_ATTEMPTS,
) -> tuple[dict, list]:
    """Llama Flash, valida, reintenta enriqueciendo el prompt si falla.

    Encapsula:
      - call_flash_json(prompt)
      - _validate_distribution_plan(plan, expected_fact_ids)
      - len(chapters_raw) == 7
      - _enforce_structure(chapters_raw)
      - _validate_skeleton(skeleton público resultante)

    Returns:
        (plan, chapters): plan crudo emitido por Flash (para persistir en
        el JSON intermedio) y la lista de chapters ya normalizados con
        role/render_engine/duration_seconds inyectados.

    Raises:
        SkeletonValidationError tras agotar max_attempts.
    """
    attempt_prompt = prompt
    last_error: SkeletonValidationError | None = None

    for attempt in range(1, max_attempts + 1):
        raw = call_flash_json(attempt_prompt, response_schema=_skeleton_schema())  # HANDOFF 66b (R4)
        try:
            plan = raw.get("_distribution_plan") or {}
            _validate_distribution_plan(plan, expected_fact_ids)

            chapters_raw = raw.get("chapters") or []
            if len(chapters_raw) != 7:
                raise SkeletonValidationError(
                    f"Flash devolvió {len(chapters_raw)} caps (esperado 7)"
                )
            chapters = _enforce_structure(chapters_raw)

            _validate_skeleton({"chapters": chapters})

            return plan, chapters
        except SkeletonValidationError as e:
            last_error = e
            if attempt == max_attempts:
                raise
            print(
                f"  [01a] validación falló intento {attempt}/{max_attempts}: "
                f"{str(e)[:120]}..."
            )
            feedback = f"""

═══════════════════════════════════════════════════
RETRY {attempt + 1}/{max_attempts} — TU INTENTO PREVIO FALLÓ
═══════════════════════════════════════════════════
PROBLEMA DETECTADO:
{str(e)}

CORREGÍLO. Reescribí el JSON COMPLETO respetando TODAS las reglas
inviolables (especialmente: cubrir TODOS los facts en el plan, sin
duplicar, y mantener {MIN_BULLETS_PER_CHAPTER}-{MAX_BULLETS_PER_CHAPTER}
bullets por cap). Generá la respuesta nueva desde cero, no parches
sobre la anterior.
"""
            attempt_prompt = prompt + feedback

    # Inalcanzable en teoría
    if last_error:
        raise last_error
    raise SkeletonValidationError("retry exhausted sin error capturado")


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA
# ═══════════════════════════════════════════════════════════════

def generate_skeleton(topic: dict) -> dict:
    """
    Genera el skeleton de 7 capítulos a partir de un topic completo (módulo 00).

    Args:
        topic: dict con id/title/hook/mystery/reveal/angle/canonical/
               research_summary/verified_facts (formato post módulo 00).

    Returns:
        {
          "topic_id": str,
          "chapters": [ {chapter_number, title, role, render_engine,
                         duration_seconds, bullets[]}, ... ]   # 7 items
        }
        (NO incluye _distribution_plan; ese se persiste solo en disco.)

    Raises:
        SkeletonValidationError si Flash devuelve algo que no cumple el
        contrato (cantidad de caps, bullets fuera de rango, plan inválido)
        después de los retries permitidos.
    """
    topic_id = topic.get("id") or topic.get("topic_id")
    if not topic_id:
        raise ValueError("topic sin 'id' ni 'topic_id'")

    facts = topic.get("verified_facts") or []
    expected_fact_ids = _fact_ids(facts)

    prompt = _build_prompt(topic)
    plan, chapters = _call_with_validation_retry(prompt, expected_fact_ids)

    # Output público (sin plan)
    skeleton = {
        "topic_id": topic_id,
        "chapters": chapters,
    }

    # JSON intermedio (con plan, para auditoría)
    full_data = {
        "topic_id": topic_id,
        "_distribution_plan": plan,
        "chapters": chapters,
    }
    _persist(topic_id, full_data)

    return skeleton
