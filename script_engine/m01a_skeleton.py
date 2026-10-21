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

F5 §1.2 (si el topic trae evidence_pool; si no, todo igual que antes):
  - `_evidence_plan` {cap_1..cap_7: [ids del pool]}: reparte DATOS (no facts) por cap siguiendo la cronología;
    cada cap ≥ MIN_NEW_EVIDENCE ids nuevos (datos / cronología / citas no usados antes) + ≤ 1 repetido (puente).
  - `personajes` del video [{id, entra_en_cap}]: el antagonista del pool es obligatorio.
  - por cap `cliffhanger`: el id del dato concreto que el cap siguiente revela (es la pregunta de cierre).
  Validación determinista (_validate_evidence_plan) + los mismos reintentos con feedback.

NOTA SOBRE _distribution_plan:
  Flash genera primero un plan que asigna cada fact [F##] a un cap
  intermedio (2-6). Esto fuerza planning-before-generation y elimina
  redundancia entre caps de desarrollo. El plan se PERSISTE en el JSON
  intermedio (auditoría) pero NO se devuelve en el output público.
"""

import json
import re
from pathlib import Path

from config import DATA_DIR
from gemini_helpers import call_flash_json
from script_engine import evidence as ev


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

# F5 §1.2: datos del evidence_pool por cap
MIN_NEW_EVIDENCE = 3          # ids nuevos por cap (datos / cronología / citas no usados en caps anteriores)
MAX_BRIDGE_EVIDENCE = 1       # ids repetidos de caps anteriores (puente)
EVIDENCE_KINDS = ("datos", "cronologia", "citas")


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
    pool = topic.get("evidence_pool")
    pool_section = _pool_prompt_section(pool) if pool else ""
    numeric_rule = ("algún fact [F##] o del EVIDENCE POOL (ids D/T/Q/L/P)" if pool else "algún fact [F##] de la lista")

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
{pool_section}
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
   {numeric_rule}. NO inventes números, fechas ni nombres.

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


def _pool_prompt_section(pool: dict) -> str:
    """F5 §1.2: el evidence_pool numerado + el paso 1b (_evidence_plan, personajes, cliffhanger)."""
    n_ev = sum(len(pool.get(k) or []) for k in EVIDENCE_KINDS)
    min_new = _min_new(pool)
    antag = ", ".join(f"[{p['id']}] {p['nombre']}" for p in ev.antagonists(pool)) or "(ninguno)"
    return f"""
═══════════════════════════════════════════════════
EVIDENCE POOL — TODO lo que el research documentó ({n_ev} datos/eventos/citas). Úsalo: es el material del guion.
═══════════════════════════════════════════════════
{ev.format_pool(pool)}

═══════════════════════════════════════════════════
PASO 1b OBLIGATORIO — `_evidence_plan`, `personajes` y `cliffhanger`
═══════════════════════════════════════════════════
`_evidence_plan`: para CADA cap (cap_1..cap_7) la lista de ids del pool (D##, T##, Q##) que ese cap cuenta.
REGLAS:
1. Cada cap recibe AL MENOS {min_new} ids NUEVOS (no usados en caps anteriores) + a lo sumo {MAX_BRIDGE_EVIDENCE}
   repetido como puente. No más de 7 por cap: la narración tiene largo fijo y usa 3–6.
2. Seguí la CRONOLOGÍA (ids T##) en los caps 2–6: un cap no cuenta un evento anterior al del cap previo.
   El cap 1 (hook) puede abrir con el momento más fuerte; el cap 7 cierra con lo último que se supo.
3. Las CONTRADICCIONES oficiales y las CITAS van al cap donde más golpean.
4. Si dos datos se contradicen (p. ej. dos cifras para lo mismo), asignalos juntos al mismo cap: la narración
   cuenta la contradicción, nunca elige una en silencio.
`personajes`: [{{"id": "P##", "entra_en_cap": N}}] — las personas del pool que el video nombra y el cap donde
   entran. OBLIGATORIO el antagonista: {antag}.
`cliffhanger` (en cada cap 1–6): el id del dato CONCRETO que el cap SIGUIENTE revela (tiene que estar en el
   _evidence_plan del cap siguiente y no en el de este). Es la pregunta de cierre del cap. Cap 7: "".
"""


def _min_new(pool: dict) -> int:
    n = sum(len(pool.get(k) or []) for k in EVIDENCE_KINDS)
    return MIN_NEW_EVIDENCE if n >= 7 * MIN_NEW_EVIDENCE else max(1, n // 7)


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


def _validate_evidence_plan(raw: dict, pool: dict, repairs: list[str] | None = None
                            ) -> tuple[dict[int, list[str]], list[dict], dict[int, str]]:
    """F5 §1.2: (_evidence_plan por cap, personajes, cliffhanger por cap) o SkeletonValidationError.
    Lo que Flash suele errar se REPARA de forma determinista y queda en `repairs` (auditable en el skeleton):
      cronología   un evento anterior al primero del cap previo se muda a ese cap
      repetidos    los que pasan de MAX_BRIDGE_EVIDENCE se quitan
      faltantes    un cap con menos de N ids nuevos se completa con ids sin usar (eventos en su rango de fechas,
                   después datos; el cap 7 prefiere lo más reciente)
      antagonista  si falta, entra en el primer cap cuyos datos lo nombran
      cliffhanger  inválido → el primer id nuevo del cap siguiente
    Error (y reintento) solo si un id no existe o el pool no alcanza para completar."""
    repairs = repairs if repairs is not None else []
    its = ev.items(pool)
    valid_ev = {i for i, it in its.items() if it["_kind"] in EVIDENCE_KINDS}
    plan_raw = raw.get("_evidence_plan") or {}
    plan: dict[int, list[str]] = {}
    for n in range(1, 8):
        ids = [str(x).strip().upper() for x in plan_raw.get(f"cap_{n}") or []]
        # F## (facts), P## y L## no son datos: se ignoran (Flash los mezcla); un D/T/Q inexistente sí es error
        ids = [i for i in ids if i[:1] in "DTQ"]
        bad = [i for i in ids if i not in valid_ev]
        if bad:
            raise SkeletonValidationError(f"_evidence_plan cap_{n}: ids inexistentes o que no son datos/eventos/citas {bad}")
        plan[n] = list(dict.fromkeys(ids))
    min_new = _min_new(pool)

    def _date(i: str) -> str | None:
        return its[i].get("fecha") if its[i]["_kind"] in ("cronologia", "datos") else None

    def _first_t(n: int) -> str | None:
        ds = sorted(its[i]["fecha"] for i in plan[n] if its[i]["_kind"] == "cronologia" and its[i].get("fecha"))
        return ds[0] if ds else None

    # 1) cronología en orden en los caps de desarrollo: un evento anterior al primero del cap previo se muda ahí
    for _ in range(10):
        moved = False
        prev = None
        for n in DEVELOPMENT_CAPS:
            f = _first_t(n)
            if f is None:
                continue
            if prev is not None:
                floor = _first_t(prev)
                back = [i for i in plan[n] if its[i]["_kind"] == "cronologia" and (its[i].get("fecha") or "") < floor]
                if back:
                    plan[n] = [i for i in plan[n] if i not in back]
                    plan[prev] += [i for i in back if i not in plan[prev]]
                    repairs.append(f"cronología: {back} de cap_{n} → cap_{prev} (anteriores a {floor})")
                    moved = True
            if _first_t(n) is not None:                # un cap que se quedó sin eventos no fija el piso
                prev = n
        if not moved:
            break
    # 2) repetidos de más y 3) caps con ids nuevos de menos (se completan con ids sin usar)
    seen: set[str] = set()
    used_any = {i for n in plan for i in plan[n]}
    for n in range(1, 8):
        rep_ = [i for i in plan[n] if i in seen]
        if len(rep_) > MAX_BRIDGE_EVIDENCE:
            drop = rep_[MAX_BRIDGE_EVIDENCE:]
            plan[n] = [i for i in plan[n] if i not in drop]
            repairs.append(f"cap_{n}: repetidos de más quitados {drop}")
        new = [i for i in plan[n] if i not in seen]
        if len(new) < min_new:
            lo = _first_t(n) or next((_first_t(k) for k in range(n - 1, 0, -1) if _first_t(k)), "")
            hi = next((_first_t(k) for k in range(n + 1, 8) if _first_t(k)), "9999")
            free = [i for i in valid_ev if i not in used_any]

            def _rank(i: str) -> tuple:
                d = _date(i) or ""
                in_range = bool(d) and lo <= d <= hi
                return (not in_range, its[i]["_kind"] != "cronologia",
                        (-int(d[:4]) if n == 7 and d[:4].isdigit() else 0), i)
            fill = sorted(free, key=_rank)[:min_new - len(new)]
            if len(new) + len(fill) < min_new:
                raise SkeletonValidationError(f"_evidence_plan cap_{n}: {len(new)} ids nuevos (mínimo {min_new})")
            plan[n] += fill
            used_any |= set(fill)
            repairs.append(f"cap_{n}: {len(new)} ids nuevos → completado con {fill}")
        seen |= set(plan[n])
    pers = []
    pids = {p["id"] for p in pool.get("personajes") or []}
    for p in raw.get("personajes") or []:
        pid, cap = str(p.get("id", "")).strip().upper(), p.get("entra_en_cap")
        if pid not in pids or not isinstance(cap, int) or not 1 <= cap <= 7:
            raise SkeletonValidationError(f"personajes: entrada inválida {p}")
        pers.append({"id": pid, "nombre": its[pid]["nombre"], "rol": its[pid].get("rol"),
                     "antagonista": bool(its[pid].get("antagonista")), "entra_en_cap": cap})
    # 4) antagonista ausente → entra en el primer cap cuyos datos lo nombran (o el 2)
    for a_ in ev.antagonists(pool):
        if a_["id"] in {p["id"] for p in pers}:
            continue
        sur = ev._surname(a_["nombre"])
        cap = next((n for n in range(1, 8) if any(ev.literal_in(sur, ev.text_of(its[i])) for i in plan[n])), 2)
        pers.append({"id": a_["id"], "nombre": a_["nombre"], "rol": a_.get("rol"), "antagonista": True,
                     "entra_en_cap": cap})
        repairs.append(f"personajes: antagonista {a_['id']} {a_['nombre']} agregado (entra en cap {cap})")
    cliff: dict[int, str] = {}
    for ch in raw.get("chapters") or []:
        n = ch.get("chapter_number")
        c = str(ch.get("cliffhanger") or "").strip().upper()
        if isinstance(n, int) and 1 <= n <= 6:
            cliff[n] = c
    for n in range(1, 7):
        c = cliff.get(n, "")
        if c not in plan.get(n + 1, []) or c in plan[n]:
            new_next = [i for i in plan[n + 1] if i not in plan[n]]
            cliff[n] = new_next[0]
            repairs.append(f"cap {n}: cliffhanger {c or '(vacío)'} inválido → {cliff[n]} (primer id nuevo del cap {n + 1})")
    return plan, pers, cliff


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

def _skeleton_schema(with_pool: bool = False) -> dict:
    dev_caps = {f"cap_{i}": {"type": "ARRAY", "items": {"type": "STRING"}}
                for i in DEVELOPMENT_CAPS}
    if with_pool:                                    # F5 §1.2
        sch = _skeleton_schema(False)
        all_caps = {f"cap_{i}": {"type": "ARRAY", "items": {"type": "STRING"}} for i in range(1, 8)}
        sch["properties"]["_evidence_plan"] = {"type": "OBJECT", "properties": all_caps,
                                               "required": list(all_caps)}
        sch["properties"]["personajes"] = {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "id": {"type": "STRING"}, "entra_en_cap": {"type": "INTEGER"}}, "required": ["id", "entra_en_cap"]}}
        item = sch["properties"]["chapters"]["items"]
        item["properties"]["cliffhanger"] = {"type": "STRING"}
        item["required"] = item["required"] + ["cliffhanger"]
        sch["required"] = sch["required"] + ["_evidence_plan", "personajes"]
        return sch
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
    pool: dict | None = None,
    extra: dict | None = None,
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
        raw = call_flash_json(attempt_prompt, response_schema=_skeleton_schema(bool(pool)))  # HANDOFF 66b (R4)
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

            if pool:                                  # F5 §1.2: datos por cap, personajes y cliffhangers
                repairs: list[str] = []
                ev_plan, pers, cliff = _validate_evidence_plan(raw, pool, repairs)
                for r in repairs:
                    print(f"  [01a] evidence_plan reparado: {r}")
                for ch in chapters:
                    ch["evidence_ids"] = ev_plan[ch["chapter_number"]]
                    ch["cliffhanger"] = cliff.get(ch["chapter_number"])
                if extra is not None:
                    extra.update({"_evidence_plan": {f"cap_{n}": ids for n, ids in ev_plan.items()},
                                  "personajes": pers, "_evidence_repairs": repairs})

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
bullets por cap{"; y el _evidence_plan: ids nuevos por cap, cronología en orden, antagonista en personajes, cliffhanger = id del cap siguiente" if pool else ""}).
Generá la respuesta nueva desde cero, no parches sobre la anterior.
"""
            attempt_prompt = prompt + feedback

    # Inalcanzable en teoría
    if last_error:
        raise last_error
    raise SkeletonValidationError("retry exhausted sin error capturado")


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA
# ═══════════════════════════════════════════════════════════════

SCREEN_PER_CAP = 2                     # F5d: ids del pool reservados para pantalla, por cap (1–2)
SCREEN_MUST = (6, 7)                   # caps que tienen que tener al menos uno


def canonize_figures(sk: dict, pool: dict) -> list[str]:
    """F5d (in place): una sola cifra por conteo en todo el video. Las variantes de una cifra canónica (pool
    `cifras_canonicas`: «6,500 aprox.», «8,000 de medios», el rango) salen de los caps; la oficial entra en el
    primero que tenía una variante. El cap que trae la variante de MEDIOS es el de la contradicción: conserva la
    variante, suma la oficial y queda marcado (`contradiccion_cifras`) — ahí el narrador cuenta las dos."""
    notes: list[str] = []
    chs = sorted(sk.get("chapters") or [], key=lambda c: c["chapter_number"])
    for g in pool.get("cifras_canonicas") or []:
        var = {v["id"]: v for v in g["variantes"]}
        contra = next((c for c in chs if any(var.get(i, {}).get("estatus") == "medios"
                                             for i in c.get("evidence_ids") or [])), None)
        placed = any(g["oficial"] in (c.get("evidence_ids") or []) for c in chs if c is not contra)
        for c in chs:
            ids = c.get("evidence_ids") or []
            if c is contra:
                if g["oficial"] not in ids:
                    ids.append(g["oficial"])
                c.setdefault("contradiccion_cifras", []).append(g["oficial"])
                notes.append(f"cap {c['chapter_number']}: contradicción {g['valor']} (oficial) vs "
                             f"{[var[i]['valor'] for i in ids if i in var]}")
                continue
            gone = [i for i in ids if i in var]
            if not gone:
                continue
            k = ids.index(gone[0])
            ids = [i for i in ids if i not in var]
            if not placed and g["oficial"] not in ids:
                ids.insert(k, g["oficial"])
                placed = True
            c["evidence_ids"] = ids
            notes.append(f"cap {c['chapter_number']}: cifra canónica {g['valor']} en vez de "
                         f"{[var[i]['valor'] for i in gone]}")
    return notes


def assign_screen_ids(sk: dict, pool: dict) -> list[str]:
    """F5d (in place): por cap, 1–2 ids del pool RESERVADOS PARA PANTALLA (`pantalla_ids`): datos que el narrador no
    dice y el director muestra con prioridad. Son datos duros que nadie narra, con fuente, cifra precisa, fecha
    completa o una cita corta, que tienen un recorte posible (cláusula completa + kicker) y no cuentan el mismo
    hecho que algo narrado. Van al cap con el que más se relacionan (palabras en común; +2 si la fecha cae en el
    rango del cap). Los caps 6 y 7 reciben al menos uno."""
    from script_engine.gfx_pool import _kicker, pool_clause_options
    its = ev.items(pool)
    chs = sorted(sk.get("chapters") or [], key=lambda c: c["chapter_number"])
    narrated = {i for c in chs for i in c.get("evidence_ids") or []}
    narrated |= {v["id"] for g in pool.get("cifras_canonicas") or [] for v in g["variantes"]}

    def _worthy(it: dict) -> bool:
        txt = ev.text_of(it)
        if it["_kind"] == "citas":
            return len(txt.split()) <= 12
        return bool(it.get("fuente") or (it.get("tipo") in ("cifra", "magnitud") and re.search(r"\d", txt))
                    or ev.item_date(it))
    cands = []
    for i, it in its.items():
        if i in narrated or it["_kind"] not in ("datos", "cronologia", "citas") or not ev.is_hard(it) or not _worthy(it):
            continue
        if any(ev.same_fact(it, its[j]) for j in narrated if j in its):
            continue
        # el mismo día y el mismo asunto que algo narrado (≥ 2 palabras en común): ya lo cuenta la voz en algún cap
        d = ev.item_date(it)
        if d and any(ev.item_date(its[j]) == d and len(ev._content(ev.text_of(it)) & ev._content(ev.text_of(its[j]))) >= 2
                     for j in narrated if j in its):
            continue
        txt = ev.text_of(it)
        if not any(_kicker(it, o) for o in pool_clause_options(txt)) and it["_kind"] != "citas":
            continue
        cands.append(i)

    def _score(i: str, c: dict) -> int:
        """Relación dato ↔ cap; −1 = no puede ir (su fecha es posterior a todo lo que narra el cap: S2 lo
        bloquearía en pantalla)."""
        own = [its[j] for j in c.get("evidence_ids") or [] if j in its]
        words = set().union(*(ev._content(ev.text_of(x)) for x in own)) if own else set()
        sc = len(ev._content(ev.text_of(its[i])) & words)
        # el rango del cap sale de sus eventos y fechas (no de la fecha suelta de una cifra)
        dates = sorted(d for d in (ev.item_date(x) for x in own
                                   if x["_kind"] == "cronologia" or x.get("tipo") == "fecha") if d)
        d = ev.item_date(its[i])
        if d and dates and d > dates[-1]:
            return -1
        if d and dates and dates[0] <= d:
            sc += 2
        return sc
    for c in chs:
        c["pantalla_ids"] = []
    # cada dato al cap con el que más se relaciona (empate: el cap más temprano, donde ocurre); primero los datos
    # más relacionados
    best = {i: max(chs, key=lambda c: (_score(i, c), -c["chapter_number"])) for i in cands}
    for i in sorted(cands, key=lambda i: (-_score(i, best[i]), i)):
        c = best[i]
        if _score(i, c) >= 2 and len(c["pantalla_ids"]) < SCREEN_PER_CAP:
            c["pantalla_ids"].append(i)
    for c in chs:                                      # los caps 6 y 7 tienen al menos uno
        if c["chapter_number"] in SCREEN_MUST and not c["pantalla_ids"]:
            used = {j for x in chs for j in x["pantalla_ids"]}
            # los caps del final: primero lo más reciente (es lo que cuentan), después lo más relacionado
            late = lambda i: (ev.item_date(its[i]) or "", _score(i, c), i)  # noqa: E731
            free = sorted((i for i in cands if i not in used and _score(i, c) >= 0), key=late, reverse=True)
            if free:
                c["pantalla_ids"].append(free[0])
                continue
            # sin libres: se le pasa uno de un cap que tiene 2 (el que mejor encaja acá)
            donors = [(i, x) for x in chs if len(x["pantalla_ids"]) > 1 for i in x["pantalla_ids"] if _score(i, c) >= 0]
            if donors:
                i, x = max(donors, key=lambda t: late(t[0]))
                x["pantalla_ids"].remove(i)
                c["pantalla_ids"].append(i)
    return [f"cap {c['chapter_number']}: pantalla {c['pantalla_ids']}" for c in chs if c["pantalla_ids"]]


def finalize_pool_plan(sk: dict, pool: dict | None) -> None:
    """F5d: cifras canónicas y datos reservados para pantalla sobre el skeleton (in place, anotado en `_pool_plan`)."""
    if not pool:
        return
    sk["_pool_plan"] = {"cifras_canonicas": canonize_figures(sk, pool), "pantalla": assign_screen_ids(sk, pool)}


def frozen_skeleton(topic: dict) -> dict:
    """F5c (token `skeleton_frozen`): usa un skeleton ya generado en vez de llamar a Flash.

    topic["skeleton_frozen"] = {"skeleton": <01a_skeleton.json>, "pool": <01_facts_sources.json del pool al que se
    refieren sus ids>}. Los ids del pool viejo se traducen al pool ACTUAL por texto (sin mayúsculas ni tildes); lo
    que ya no está (filtro de relevancia, F5b N1) se quita, igual que los personajes que el pool actual no tiene
    (F5b N5: un nombre entra solo si hace algo). Todo queda anotado en `_frozen`. Sin `pool` viejo, los ids se usan
    como están. Se persiste como 01a_skeleton.json del topic.
    """
    from script_engine import evidence as ev
    cfg = topic["skeleton_frozen"]
    sk = json.loads(Path(cfg["skeleton"]).read_text(encoding="utf-8"))
    cur = topic.get("evidence_pool") or {}
    cur_its = ev.items(cur)
    remap: dict[str, str | None] = {}
    if cfg.get("pool"):
        old = json.loads(Path(cfg["pool"]).read_text(encoding="utf-8"))
        old = old.get("evidence_pool", old)
        by_text = {(it["_kind"], ev.norm(ev.text_of(it))): i for i, it in cur_its.items()}
        for i, it in ev.items(old).items():
            remap[i] = by_text.get((it["_kind"], ev.norm(ev.text_of(it))))
    def _m(i: str | None) -> str | None:
        return (remap.get(i) if remap else i) if i else None
    notes: list[str] = []
    for ch in sk.get("chapters") or []:
        if "evidence_ids" in ch:
            new = [_m(i) for i in ch["evidence_ids"]]
            gone = [i for i, n in zip(ch["evidence_ids"], new) if n is None or n not in cur_its]
            if gone:
                notes.append(f"cap {ch['chapter_number']}: fuera del pool actual {gone}")
            ch["evidence_ids"] = [n for n in new if n and n in cur_its]
        if ch.get("cliffhanger"):
            c = _m(ch["cliffhanger"])
            if c is None or c not in cur_its:
                notes.append(f"cap {ch['chapter_number']}: cliffhanger {ch['cliffhanger']} fuera del pool actual")
                c = None
            ch["cliffhanger"] = c
    names = {ev.norm(p["nombre"]) for p in cur.get("personajes") or []}
    pers = []
    for p in sk.get("personajes") or []:
        if ev.norm(p["nombre"]) in names:
            pers.append(p)
        else:
            notes.append(f"personaje fuera (el pool actual no lo tiene: no hace nada en la historia): {p['nombre']}")
    sk["personajes"] = pers
    sk["topic_id"] = topic.get("id") or topic.get("topic_id")
    sk["_frozen"] = {"skeleton": str(cfg["skeleton"]), "pool": str(cfg.get("pool") or ""),
                     "ids_traducidos": {k: v for k, v in remap.items() if v and v != k}, "notas": notes}
    finalize_pool_plan(sk, cur)                      # F5d: cifras canónicas + datos reservados para pantalla
    _persist(sk["topic_id"], sk)
    return {"topic_id": sk["topic_id"], "chapters": sk["chapters"], "personajes": pers}


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

    if topic.get("skeleton_frozen"):                 # F5c: skeleton fijo, no se regenera
        return frozen_skeleton(topic)

    facts = topic.get("verified_facts") or []
    expected_fact_ids = _fact_ids(facts)

    prompt = _build_prompt(topic)
    pool = topic.get("evidence_pool") or None
    extra: dict = {}
    plan, chapters = _call_with_validation_retry(prompt, expected_fact_ids, pool=pool, extra=extra)

    # Output público (sin plan)
    skeleton = {
        "topic_id": topic_id,
        "chapters": chapters,
        **({"personajes": extra["personajes"]} if pool else {}),
    }

    # JSON intermedio (con plan, para auditoría)
    full_data = {
        "topic_id": topic_id,
        "_distribution_plan": plan,
        **({"_evidence_plan": extra["_evidence_plan"], "personajes": extra["personajes"],
            "_evidence_repairs": extra["_evidence_repairs"]} if pool else {}),
        "chapters": chapters,
    }
    finalize_pool_plan(full_data, pool)              # F5d: cifras canónicas + datos reservados para pantalla
    _persist(topic_id, full_data)

    return skeleton
