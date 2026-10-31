"""
researcher_steps/step_4e_visual_canon.py — Sub-paso 4e del módulo 00.

Tarea ÚNICA: emitir el "canon visual" del tema en una sola llamada a Claude Opus 5.5 (F50f, DECISIONES 2026-10-28
23:34: antes era Flash con esquema; la API de Claude no acepta ese esquema —46 opcionales > 24—, así que la llamada va
sin esquema y la salida JSON se parsea del texto). Si la llamada falla o la respuesta no trae `era_visual_canon.periods`
y `people_groups`: CanonError (no hay canon vacío de respaldo).
Datos estables del topic que m03 (extractor visual) y m05 (juez) consumen
sin re-inferir.

Bloques que produce:
  - era_visual_canon: cómo se ve el mundo del tema (clothing, technology,
    vehicles, interiors, forbidden_anachronisms) + primary_decade + spans.
  - documented_people: personas reales mencionadas por nombre en
    verified_facts, con appearance_canon SIN nombre (para que Flux no
    intente likeness).
  - anachronism_blocklist: array plano de elementos visuales prohibidos
    específicos del tema.
  - documented_props: objetos físicos centrales (eslabón 2), tomados del bloque
    [OBJETOS] del ángulo visual, con nombre/forma/anclado/foto_madre. Filtro
    fino: solo entra el objeto que ES el evento (no evidencia ni auxiliar).

Recibe verified_facts + canonical CERRADOS y angle_blocks como contexto
de época. NO inventa fechas/personas/lugares — los hereda de los facts.

ESLABÓN 2 (B-eslabon2): _format_blocks ahora surfacea el 4º ángulo "visual"
(eslabón 1, ya en prod) que antes caía en angle_blocks pero NUNCA entraba al
prompt. era_visual_canon se extiende con una 2ª CAPA de campos SOURCED del
sujeto puntual (materials_textures, color_palette, scale_dimensions,
distinctive_features, demographics, visual_reference_availability,
condition_evolution) que salen de ese bloque visual. color_palette se fuerza a
flat-string (hasta F50f vía response_schema; hoy por el pedido + `_flatten_to_str`). C5: era/ropa que se colaba en
documented_people.appearance_canon se remueve con un check determinista
post-LLM. Las 7 keys de época viejas NO se tocan (m05 las lee).

INPUT:  seed + angle_blocks (incluye "visual") + verified_facts + canonical
OUTPUT: {
  "era_visual_canon": {
    # capa ÉPOCA (genérica) — las 7 viejas
    "primary_decade": str,
    "spans": str,
    "clothing": str,
    "technology": str,
    "vehicles_machinery": str,
    "interiors": str,
    "forbidden_anachronisms": str,
    # capa SUJETO PUNTUAL (sourced) — eslabón 2
    "materials_textures": str,
    "color_palette": str,            # flat-string (nunca objeto)
    "scale_dimensions": str,
    "distinctive_features": str,     # ancla de síntesis
    "demographics": str,
    "visual_reference_availability": str,
    "condition_evolution": {"at_event": str, "later": str}
  },
  "documented_people": [
    {"name": str, "role": str, "age_at_event": int|None, "era": str,
     "appearance_canon": str, "condition_by_period": [{"years": str, "condition": str}]},
    ...
  ],
  "anachronism_blocklist": [str, ...],
  "documented_props": [
    {"nombre": str, "forma": str, "anclado": "si"|"no", "foto_madre": ""},
    ...
  ]
}

NUMERACIÓN EN DISCO: el orquestador persiste este sub-paso como
`05_visual_canon.json` para mantener consistencia con la numeración
entera del resto (00→04). El "4e" es interno al razonamiento del
módulo 00 (es el quinto sub-paso del paso 4 del orquestador), no una
nomenclatura de filesystem.
"""

import re

import claude_helpers

# F50f: el modelo del canon y su esfuerzo (DECISIONES 2026-10-28 23:34; effort = guion_v4.ESFUERZO de Opus)
MODELO_CANON = "claude-opus-5-5"
ESFUERZO_CANON = "high"


class CanonError(RuntimeError):
    """F50f: el canon no salió (la llamada falló, o la respuesta no es JSON o le faltan `periods`/`people_groups`)."""


# ═══════════════════════════════════════════════════════════════
#  HELPERS DE FORMATEO (espejo del patrón de 4b)
# ═══════════════════════════════════════════════════════════════

def _format_facts(verified_facts: list) -> str:
    """Convierte verified_facts a texto enumerado para el prompt."""
    if not verified_facts:
        return "(no hay facts disponibles)"
    lines = []
    for i, f in enumerate(verified_facts, 1):
        if isinstance(f, dict):
            fact_text = f.get("fact", "")
        else:
            fact_text = str(f)
        lines.append(f"  {i}. {fact_text}")
    return "\n".join(lines)


def _format_blocks(angle_blocks: dict) -> str:
    """Concatena los bloques angulares para contexto del prompt.

    ESLABÓN 2 — EL CAÑO: los 3 bloques viejos (tecnico/humano/misterio) son
    CONTEXTO DE ÉPOCA (capa genérica). El 4º bloque "visual" (eslabón 1) es la
    FUENTE SOURCED de los campos del sujeto puntual; sin surfacearlo acá el LLM
    no tiene de dónde sacar los campos sourced y los inventa. Se trunca más
    largo (6000) que los de época (1500) porque es la fuente de la capa lugar.
    """
    parts = []
    for key in ("tecnico", "humano", "misterio"):
        block = angle_blocks.get(key, "")
        if block:
            parts.append(f"[{key.upper()} -- contexto de época]\n{block[:1500]}")
    visual = angle_blocks.get("visual", "")
    if visual:
        parts.append(f"[VISUAL -- FUENTE de los campos sourced]\n{visual[:6000]}")
    return "\n\n".join(parts) if parts else "(sin bloques)"


# ═══════════════════════════════════════════════════════════════
#  PROMPT
# ═══════════════════════════════════════════════════════════════

def _build_prompt(
    seed: dict,
    angle_blocks: dict,
    verified_facts: list,
    canonical: str | None,
) -> str:
    """Construye el prompt del sub-paso 4e."""
    facts_block = _format_facts(verified_facts)
    blocks_block = _format_blocks(angle_blocks)
    canonical_block = canonical or "(sin canonical_subject_description)"

    return f"""Eres un director de fotografía de documentales históricos. Tu tarea:
emitir el "canon visual" de un tema histórico — la verdad estable de cómo
se ve ese mundo, su gente y su época. Este canon será consumido por
módulos posteriores que generarán prompts visuales y auditarán coherencia.

TEMA: "{seed.get('seed_title', '?')}"

CANONICAL DEL SUJETO (ya cerrado en 4b):
{canonical_block}

DATOS DUROS YA EXTRAÍDOS (verified_facts, NO inventes nuevos):
{facts_block}

BLOQUES DE INVESTIGACIÓN (3 viejos = contexto de época; VISUAL = fuente sourced):
{blocks_block}

═══════════════════════════════════════════════════
TU TAREA
═══════════════════════════════════════════════════

Emití un objeto JSON con CINCO bloques: era_visual_canon, documented_people,
anachronism_blocklist, documented_props, central_subject. Strings en INGLÉS (los consumirán Flux y Veo).

═══ BLOQUE 1: era_visual_canon ═══

DOS CAPAS, no las mezcles. La capa ÉPOCA es genérica de la década; la capa
SUJETO PUNTUAL es específica y documentada (sale de [VISUAL]).

Sub-campos de ÉPOCA (genéricos de la década, derivados de los facts/contexto):
- primary_decade: década dominante del evento principal, formato "1960s",
  "1940s", "early 20th century". Derivá de las fechas en verified_facts.
- spans: rango temporal del tema, formato "1937-2007" o "1968" si es puntual.
  Derivá de las fechas extremas en verified_facts.
- clothing: string EN, ropa de época para personas en este tema. Mencioná
  roles relevantes (oficial naval, minero, civil) con su atuendo de la era.
- technology: string EN, tecnología de la época + lo que NO existía aún.
  Ej: "analog gauges, vacuum tubes, rotary dials. NO LEDs, NO digital displays."
- vehicles_machinery: string EN, vehículos y maquinaria de época.
- interiors: string EN, interiores característicos (oficinas, salas, casas).
- periods: una entrada por cada tramo del material en que cambian la ropa, la tecnología, los vehículos o los interiores; years "AAAA-AAAA" y esos 4 campos para ese tramo (EN). Si el tema es de una sola época, una sola entrada.
- forbidden_anachronisms: string EN, lista de elementos contemporáneos a
  evitar específicos del tema.

Sub-campos SOURCED del SUJETO PUNTUAL (de [VISUAL], específicos de ESTE
lugar/objeto). CARRIL ESTRICTO: cada campo escribe SOLO lo que le toca y NO
invade a otro. La MISMA observación NO se reparte palabra por palabra en varios
campos. TODOS string EN, salvo condition_evolution (objeto):
- materials_textures: SOLO material y textura (ladrillo, hormigón, acero
  corrugado, pintura descascarada). El COLOR va en color_palette, NO acá. NO
  dimensión.
- color_palette: SOLO color, como STRING PLANO. Exterior e interior en UNA
  sola frase (ej: "exterior red brick and rust-brown; interior pale green
  walls"). NO objeto anidado. NO material. NO dimensión.
- scale_dimensions: SOLO dimensión y escala (altura, pisos, huella, longitud,
  diámetro). NO material. NO color.
- distinctive_features: la SÍNTESIS de 1-2 frases de lo MÁS identificable de
  ESTE sujeto puntual -- lo que lo distingue de cualquier otro de su tipo. Es
  el ANCLA que el consumidor (m03) usa para fijar el sujeto. Re-dice A
  PROPÓSITO lo más fuerte de los campos de arriba; NO es un catálogo ni repite
  todo lo granular.
- demographics: composición demográfica documentada (GRUPO/ROL,
  etnia/nacionalidad), + vestimenta específica del lugar/función. NUNCA como
  rasgo de un individuo nombrable.
- visual_reference_availability: qué referencias visuales reales sobreviven y
  de qué TIPO es la fuente. Distinguí explícito FUENTE VISUAL (photo/plan/
  footage/archive) de FUENTE TEXTO (descripción académica). Si un dato viene
  de texto y no de imagen, decilo (ej: "ethnicity from written record, not
  photographic").
- condition_evolution: OBJETO con dos estados temporales SEPARADOS. Este es el
  ÚNICO campo anidado; todos los demás son STRINGS PLANOS:
    "at_event": cómo se veía DURANTE el momento que el video narra
                (intacto/operando).
    "later":    deterioro / abandono / demolición posterior.
  NUNCA mezcles ambos en una sola frase.

REGLAS de era_visual_canon:
1. CAPA LUGAR/OBJETO (materials, color_palette, scale, distinctive, condition):
   tan ESPECÍFICA como la fuente lo documente. Si [VISUAL] documenta el detalle,
   USALO con su especificidad ("13-story red brick building", NO "a tall
   building"). Genérico SOLO como fallback honesto cuando no hay fuente, marcado
   como tal en visual_reference_availability.
2. CAPA ÉPOCA-GENÉRICA (clothing, technology, vehicles, interiors) y CUALQUIER
   persona: mantené genérico y ampliamente documentado. NO inventes un detalle
   específico no verificable (ej: "the captain wore a Rolex"). Si dudás entre 2
   versiones, el más genérico. El detalle de un individuo nombrable vive en
   documented_people, NO acá.
3. Por CADA afirmación de la capa lugar/objeto, el campo
   visual_reference_availability debe permitir rastrear si viene de FUENTE REAL
   (photo/plan/footage/archive) o de INFERENCIA/TEXTO.
4. primary_decade y spans COHERENTES con verified_facts. NO inventes décadas.
5. CARRILES: si una observación es de color va SOLO en color_palette; si es de
   material va SOLO en materials_textures; si es de dimensión va SOLO en
   scale_dimensions. distinctive_features es la ÚNICA que re-dice a propósito
   (sintetiza el ancla, no cataloga). Repartir un mismo dato en 3 campos = ERROR.
6. TIPOS: todos los sub-campos son STRING PLANO salvo condition_evolution
   (objeto {{at_event, later}}). color_palette NUNCA es objeto.
7. CAMPOS SOURCED sin fuente: si [VISUAL] no documenta un campo de la capa
   lugar/objeto, dejá el campo como "" (string vacío) o marcá "INFERENCE". NO
   inventes para rellenar — un campo honestamente vacío es mejor que uno falso.

═══ BLOQUE 2: documented_people ═══

Array de personas concretas mencionadas POR NOMBRE PROPIO en verified_facts.

Cada entrada:
- name: nombre real exacto como aparece en facts.
- role: rol/profesión en el evento.
- age_at_event: número entero. Si los facts no lo dicen, dejá null.
- era: año o década del evento que los involucra.
- appearance_canon: 1 frase EN con solo el aspecto físico fijo de la persona
  (edad aparente en los años de era + nacionalidad/etnia + contextura si el
  material la documenta). Nada que cambie según dónde esté, qué haga o qué
  le pase (ropa, oficio, heridas, enfermedad, ánimo, acción): el oficio va
  en role, la ropa en era_visual_canon y el estado físico documentado en
  condition_by_period. PROHIBIDO mencionar el nombre real. PROHIBIDO
  mencionar rasgos específicos como "tall", "blue eyes", "scar" — solo
  descriptores ampliamente verificables.
- condition_by_period: una entrada por cada tramo de años en que el material
  documenta un estado físico de esa persona (heridas, enfermedad, desgaste);
  years "AAAA-AAAA" y condition (EN, una frase). Si el material no documenta
  ningún estado, lista vacía.

REGLAS CRÍTICAS de documented_people:
1. Si age_at_event tiene valor → appearance_canon DEBE usar el descriptor
   correspondiente, sin contradicción:
   - 20-23 → "early-20s"
   - 24-26 → "mid-20s"
   - 27-29 → "late-20s"
   - 30-33 → "early-30s"
   - 34-36 → "mid-30s"
   - 37-39 → "late-30s"
   - 40-43 → "early-40s"
   - 44-46 → "mid-40s"
   - 47-49 → "late-40s"
   - 50-53 → "early-50s"
   - 54-56 → "mid-50s"
   - 57-59 → "late-50s"
   - 60+   → "elderly" o "in his/her 60s"
2. Si age_at_event = null → usar descriptor general ("middle-aged",
   "elderly", "young adult") según contexto.
3. Solo personas con NOMBRE PROPIO en facts. NO inferir personas no
   mencionadas.
4. Si NO hay personas nombradas en facts, devolvé array vacío [].
5. **NO incluir era textual en appearance_canon.** Frases como "1960s
   uniform", "1940s attire", "Victorian-era clothing" están PROHIBIDAS
   en appearance_canon. La era visual completa va en el campo
   era_visual_canon.clothing (separado). appearance_canon describe
   SOLO la persona específica para que el consumidor m03 pueda
   combinar persona + era sin redundancia ni contradicción.

   ✗ MAL: "a mid-30s American naval officer in 1960s service uniform"
   ✓ BIEN: "a mid-30s American man of medium build"

✗ MAL appearance_canon: "Francis Slattery, a 36-year-old American naval
                          officer with focused gaze"
                          (incluye nombre propio, prohibido por regla)
✗ MAL appearance_canon: "a mid-30s American naval officer in 1960s
                          service uniform, focused authoritative demeanor"
                          (incluye era textual "1960s service uniform" — la era
                          va separada en era_visual_canon.clothing, NO acá)
✓ BIEN appearance_canon: "a mid-30s American man of medium build"
                           (solo edad + nacionalidad + contextura, sin era;
                           el oficio va en role, la ropa en era_visual_canon)

═══ BLOQUE 3: anachronism_blocklist ═══

Array plano de strings con elementos visuales prohibidos para este tema.
Mínimo 6, máximo 12 items. Incluí AL MENOS:
- "smartphones"
- "LED screens" o "modern flat panels"
- "contemporary clothing" (post-2000s)
- al menos 1 item específico al tema (ej: "modern submarine designs"
  para un tema naval de los 60s, "modern industrial safety equipment"
  para un tema minero de mediados de siglo).

═══ BLOQUE 4: documented_props ═══

Array de objetos físicos centrales, tomados de la sección
[OBJETOS / EQUIPO RECURRENTE] del ángulo visual — NO de verified_facts.

Cada entrada:
- nombre: el objeto puntual tal como aparece en [OBJETOS].
- forma: 1-2 frases EN con la forma física, TOMADA de los datos que [OBJETOS]
         ya trae (silueta/proporción/rasgos/material/escala). NO re-inventes:
         si [OBJETOS] marcó HUECO en un dato, no lo rellenes — dejalo afuera.
- anclado: "si" o "no" (regla abajo).
- foto_madre: siempre "" (vacío — no lo llenás vos).

QUÉ INCLUIR — el default es NO incluir:
  Incluí un objeto SOLO si el evento en sí ES ese objeto — si el tema
  literalmente trata sobre él. Test: ¿el evento sucede igual sin este objeto?
   · si el evento pasa igual, y el objeto solo aportó PRUEBAS de lo que pasó
     (cómo lo sabemos) o cumplió una función de APOYO → NO entra.
   · entra únicamente si, sacándolo, el evento no existiría.

anclado — "si" o "no", según su RECURRENCIA (no su forma):
  · "si": el objeto es un FOCO CENTRAL y RECURRENTE del tema — vuelve como sujeto de
     las imágenes a lo largo de la pieza — SIN IMPORTAR si su forma es una silueta
     continua o está armada de partes. Si el tema vuelve una y otra vez a este objeto,
     tiene que verse IGUAL cada vez → anclalo.
  · "no" (default): el objeto aparece una sola vez, o solo como fondo/contexto, o es
     mera evidencia de lo que pasó. Ante la duda → "no".

Ejemplos conceptuales (de OTRO tema, no copiar):
✗ MAL incluir: un objeto que registró o probó lo que pasó → es evidencia, no el evento.
✗ MAL incluir: un objeto que sirvió de apoyo a otra tarea → función auxiliar.
✓ BIEN incluir: un objeto sobre cuyo uso o falla gira el evento entero.

Ejemplos conceptuales de anclado (recurrencia, NO forma; de OTRO tema, no copiar):
✓ anclado="si": un objeto al que el tema vuelve como protagonista visual capítulo tras capítulo.
✗ anclado="no": un objeto que aparece en una sola escena, o solo de fondo.

Si ningún objeto de [OBJETOS] pasa el test → array vacío [].

═══ BLOQUE 5: central_subject ═══

Clasificá el SUJETO CENTRAL del tema —eso de lo que el video habla una y otra
vez— en UNA de cuatro categorías. El criterio NO es gramatical (cosa/persona/
lugar) sino UNO SOLO: ¿tiene una SILUETA propia y reconocible que debe verse
IGUAL en imagen tras imagen?

- "object": el sujeto es un objeto físico con silueta única y anclable que se
  repite a lo largo del tema (un submarino, un barco, un dirigible, un
  transbordador, un avión, un faro, una máquina singular). Su forma ya la
  escribiste en distinctive_features; acá SOLO marcás que ES de este tipo.
- "person": el sujeto es UNA persona real nombrable (su aspecto ya vive en
  documented_people).
- "place": el sujeto es un lugar o entorno SIN una silueta-objeto única (una
  ciudad, un pueblo, un bosque, una región). No hay una forma que repetir.
- "other": no hay un sujeto físico dominante, o dudás (un fenómeno, una
  epidemia, un evento difuso).

REGLA DEL DEFAULT: "object" es la categoría FUERTE (dispara la foto madre). En
la duda entre "object" y cualquier otra, elegí la otra. Un objeto mal marcado
como "object" cuesta más que uno marcado conservador. Si no estás seguro de que
hay UNA silueta única y anclable, poné "other".

foto_madre: siempre "" (vacío — no lo llenás vos, se completa después).

═══════════════════════════════════════════════════
FORMATO DE SALIDA — JSON puro, sin markdown:
═══════════════════════════════════════════════════

{{
  "era_visual_canon": {{
    "primary_decade": "1960s",
    "spans": "1968",
    "clothing": "...",
    "technology": "...",
    "vehicles_machinery": "...",
    "interiors": "...",
    "forbidden_anachronisms": "...",
    "materials_textures": "...",
    "color_palette": "exterior weathered steel and white panels; interior pale grey and green",
    "scale_dimensions": "...",
    "distinctive_features": "...",
    "demographics": "...",
    "visual_reference_availability": "...",
    "condition_evolution": {{
      "at_event": "...",
      "later": "..."
    }}
  }},
  "documented_people": [
    {{
      "name": "Francis Slattery",
      "role": "USS Scorpion submarine commander",
      "age_at_event": 36,
      "era": "1968",
      "appearance_canon": "a mid-30s American man of medium build",
      "condition_by_period": []
    }}
  ],
  "anachronism_blocklist": [
    "smartphones",
    "LED screens",
    "contemporary clothing",
    "modern flat panels",
    "modern cars post-1980",
    "branded modern logos"
  ],
  "documented_props": [
    {{
      "nombre": "the object the case is literally about",
      "forma": "1-2 sentences EN: physical form taken from [OBJETOS] (silhouette/proportion/features/material/scale)",
      "anclado": "no",
      "foto_madre": ""
    }}
  ],
  "central_subject": {{
    "kind": "object",
    "foto_madre": ""
  }}
}}

LANGUAGE: Output EVERY field value in English, regardless of the language of
the instructions above. This applies to materials_textures, color_palette,
distinctive_features and ALL sourced fields. Do NOT mix Spanish into any value.

RESPONDE SOLO CON EL JSON."""


# ═══════════════════════════════════════════════════════════════
#  VALIDACIÓN DEFENSIVA
# ═══════════════════════════════════════════════════════════════

_ERA_REQUIRED_KEYS = (
    # capa ÉPOCA (las 7 viejas — m05 las lee, NO renombrar/borrar)
    "primary_decade",
    "spans",
    "clothing",
    "technology",
    "vehicles_machinery",
    "interiors",
    "forbidden_anachronisms",
    # capa SUJETO PUNTUAL — campos SOURCED planos (eslabón 2). condition_evolution
    # NO va acá: es OBJETO y _clean_era_canon lo aplastaría con str() (se limpia aparte).
    "materials_textures",
    "color_palette",
    "scale_dimensions",
    "distinctive_features",
    "demographics",
    "visual_reference_availability",
)

_PERSON_REQUIRED_KEYS = ("name", "role", "era", "appearance_canon")


def _flatten_to_str(v) -> str:
    """Aplana un valor a string plano. Si viene dict (ej: color_palette llegó
    como {exterior, interior} pese al schema), une sus valores en una frase en
    vez de str(dict) ("{'exterior': ...}"). Cinturón del response_schema."""
    if v is None:
        return ""
    if isinstance(v, dict):
        parts = [f"{k}: {sv}" for k, sv in v.items() if str(sv).strip()]
        return "; ".join(parts).strip()
    if isinstance(v, (list, tuple)):
        return ", ".join(str(x).strip() for x in v if str(x).strip())
    return str(v).strip()


def _clean_era_canon(raw: dict) -> dict:
    """Asegura las keys planas de era_visual_canon (época + sourced). Faltantes
    → string vacío. condition_evolution se trata aparte (es objeto)."""
    if not isinstance(raw, dict):
        return {k: "" for k in _ERA_REQUIRED_KEYS}
    cleaned = {}
    for k in _ERA_REQUIRED_KEYS:
        # _flatten_to_str absorbe el caso color_palette-como-dict sin romper.
        cleaned[k] = _flatten_to_str(raw.get(k, ""))
    return cleaned


def _clean_condition_evolution(raw) -> dict:
    """condition_evolution = OBJETO {at_event, later}. Mini-clean propio porque
    _clean_era_canon (str/flatten) lo aplastaría. Tolera string suelto del LLM
    (lo mete en at_event) y faltantes (→ "")."""
    if isinstance(raw, dict):
        return {
            "at_event": _flatten_to_str(raw.get("at_event", "")),
            "later": _flatten_to_str(raw.get("later", "")),
        }
    if isinstance(raw, str) and raw.strip():
        return {"at_event": raw.strip(), "later": ""}
    return {"at_event": "", "later": ""}


_SUBJECT_KINDS = {"object", "person", "place", "other"}


def _clean_central_subject(raw) -> dict:
    """central_subject = {kind, foto_madre}. kind normalizado a uno de 4 valores,
    default conservador "other". foto_madre SIEMPRE "" (el 4e nunca la llena)."""
    kind = ""
    if isinstance(raw, dict):
        kind = str(raw.get("kind", "")).strip().lower()
    if kind not in _SUBJECT_KINDS:
        kind = "other"          # default conservador: no ancla
    return {"kind": kind, "foto_madre": ""}


# ── FIX C5 (Patrón #91): tokens de ERA que NO deben vivir en appearance_canon ──
# Décadas de 4 dígitos ("1960s", "mid-1940s") — NUNCA matchea bandas de edad
# ("mid-30s", "early-20s") porque esas son de 2 dígitos.
_C5_DECADE = r"(?:early[-\s]|mid[-\s]|late[-\s])?(?:1[6-9]\d0s|20[0-2]0s)"
_C5_NAMED_ERA = (
    r"(?:[A-Z][a-z]+-era|Victorian|Edwardian|Georgian|Elizabethan|antebellum|"
    r"post-war|wartime|interwar)"
)
_C5_CLOTHING = (
    r"(?:service\s+|military\s+|naval\s+|period\s+|formal\s+|civilian\s+)?"
    r"(?:uniforms?|attire|clothing|garb|outfit|costume|robes?|dress|workwear|wear)"
)
# Pass 1: era ligada a ropa (era+ropa  o  ropa+era). ADYACENCIA estricta: la ropa
# debe pegar a la era (su propio prefijo cubre "service/military/...") — sin filler
# arbitrario en el medio, que se comería el sujeto ("Victorian gentleman in attire").
_C5_PHRASE_RE = re.compile(
    rf"\b(?:in\s+|wearing\s+|dressed\s+in\s+)?(?:a\s+|the\s+)?"
    rf"(?:{_C5_DECADE}|{_C5_NAMED_ERA})(?:[-\s]era)?[-\s]+{_C5_CLOTHING}\b"
    rf"|\b{_C5_CLOTHING}\s+(?:of\s+|from\s+|in\s+)?(?:the\s+)?"
    rf"(?:{_C5_DECADE}|{_C5_NAMED_ERA})\b",
    re.IGNORECASE,
)
# Pass 2: tokens de era sueltos que sobrevivan.
_C5_TOKEN_RE = re.compile(
    rf"\b(?:in\s+|the\s+|of\s+)?(?:{_C5_DECADE}|{_C5_NAMED_ERA})(?:[-\s]era)?\b",
    re.IGNORECASE,
)


def _strip_era_from_appearance(appearance: str) -> tuple[str, bool]:
    """Remueve era/ropa-de-época incrustada en appearance_canon (va en
    era_visual_canon.clothing, no acá). Conservador: borra el fragmento de era,
    NO rompe el resto. Devuelve (texto_limpio, hubo_hit)."""
    base = appearance.strip(" ,;.-")
    s = _C5_PHRASE_RE.sub(" ", appearance)
    s = _C5_TOKEN_RE.sub(" ", s)
    # limpiar conectores colgados ("... wearing ." / "... in ,") y puntuación doble
    s = re.sub(r"\b(?:in|wearing|dressed\s+in)\s*(?=[,.;]|$)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\s+([,.;])", r"\1", s)
    s = re.sub(r"([,;])\s*(?=[,.;])", r"\1", s)
    s = s.strip(" ,;.-")
    return s, (s != base)


def _clean_person(raw: dict) -> dict | None:
    """Valida y limpia una entrada de documented_people. None si inválida."""
    if not isinstance(raw, dict):
        return None
    name = str(raw.get("name", "")).strip()
    role = str(raw.get("role", "")).strip()
    era = str(raw.get("era", "")).strip()
    appearance = str(raw.get("appearance_canon", "")).strip()

    # name + role + appearance son obligatorios
    if not (name and role and appearance):
        return None

    # age_at_event puede ser int o None
    raw_age = raw.get("age_at_event")
    age: int | None = None
    if isinstance(raw_age, int):
        age = raw_age
    elif isinstance(raw_age, str) and raw_age.strip().isdigit():
        age = int(raw_age.strip())

    # Sanity: el appearance_canon NO debe contener el name
    # (regla inviolable del 4e)
    if name.lower() in appearance.lower():
        # Strip defensivo: no rompemos pero marcamos. m03 igual no debe
        # confiar ciegamente; el test_module_00 lo va a auditar.
        # Estrategia: si hay nombre incrustado, lo removemos.
        # Es defensivo, pero conservador (mejor que romper el pipeline).
        for token in name.split():
            appearance = appearance.replace(token, "").replace("  ", " ").strip()
        appearance = appearance.lstrip(",. ")

    # FIX C5 (Patrón #91): la regla anti-era del prompt YA existe y el LLM la
    # viola igual → check DETERMINISTA post-LLM, mismo mecanismo que el strip
    # de nombre de arriba. La era/ropa-de-época pertenece a
    # era_visual_canon.clothing, no a appearance_canon.
    appearance, era_hit = _strip_era_from_appearance(appearance)
    if era_hit:
        print(f"       [4e/C5] era/ropa removida de appearance de '{name}'")

    # F60 A3: el estado físico documentado va aparte, por tramo de años (m03 lo ve como dato; el armado no lo pega).
    # Determinista: solo dicts con years y condition no vacíos; el nombre se quita de `condition` por tokens, como en
    # appearance; el strip C5 de era NO se aplica. Ausente o no-lista → [].
    condition_by_period = []
    raw_cbp = raw.get("condition_by_period")
    for entry in (raw_cbp if isinstance(raw_cbp, list) else []):
        if not isinstance(entry, dict):
            continue
        years = str(entry.get("years", "") or "").strip()
        condition = str(entry.get("condition", "") or "").strip()
        if not (years and condition):
            continue
        if name.lower() in condition.lower():
            for token in name.split():
                condition = condition.replace(token, "").replace("  ", " ").strip()
            condition = condition.lstrip(",. ")
        condition_by_period.append({"years": years, "condition": condition})

    return {
        "name": name,
        "role": role,
        "age_at_event": age,
        "era": era,
        "appearance_canon": appearance,
        "condition_by_period": condition_by_period,
    }


def _clean_prop(raw: dict) -> dict | None:
    """Valida y limpia una entrada de documented_props. None si inválida.

    Espejo EXACTO de _clean_person: determinista, NO juzga (el juicio
    central/evidencia-auxiliar vive en el prompt/BLOQUE 4, no acá). nombre+forma
    son obligatorios; anclado se normaliza a "si"/"no" con default conservador
    "no"; foto_madre se fuerza a "" (el 4e NUNCA la llena — la completa m03)."""
    if not isinstance(raw, dict):
        return None
    nombre = str(raw.get("nombre", "")).strip()
    forma = str(raw.get("forma", "")).strip()
    anclado = str(raw.get("anclado", "")).strip().lower()

    # nombre + forma obligatorios (espejo de name+role+appearance)
    if not (nombre and forma):
        return None

    # anclado: normalizar a "si"/"no". default conservador "no" (= va por TEXTO).
    anclado = "si" if anclado in {"si", "sí", "yes", "true", "y"} else "no"

    return {
        "nombre": nombre,
        "forma": forma,
        "anclado": anclado,
        "foto_madre": "",  # el 4e NUNCA la llena (check determinista)
    }


def _clean_blocklist(raw: list) -> list[str]:
    """Lista plana de strings no vacíos, deduplicada conservando orden."""
    if not isinstance(raw, list):
        return []
    seen: set[str] = set()
    out: list[str] = []
    for item in raw:
        s = str(item).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA
# ═══════════════════════════════════════════════════════════════

def extract_visual_canon(
    seed: dict,
    angle_blocks: dict,
    verified_facts: list,
    canonical: str | None,
    extra: str = "",
) -> dict:
    """
    Sub-paso 4e: emite el canon visual del tema (F50f: UNA llamada a `MODELO_CANON`, sin esquema).

    Args:
        seed: el seed original (necesita seed_title).
        angle_blocks: los bloques angulares (contexto de época; desde la ficha van vacíos).
        verified_facts: los hechos (desde F50 A, la ficha vía `adaptador_facts`).
        canonical: canonical_subject_description del 4b (puede ser None).
        extra: el bloque de people_groups (F50 A), al final del pedido.

    Returns:
        dict con era_visual_canon (con `periods`), documented_people, anachronism_blocklist, documented_props,
        central_subject y people_groups.

    Raises:
        CanonError: sin hechos, si la llamada falla, o si la respuesta no trae `era_visual_canon.periods` ni
        `people_groups` (F50f: sin canon vacío de respaldo).
    """
    if not verified_facts:
        raise CanonError("sin hechos no hay canon visual")

    prompt = _build_prompt(seed, angle_blocks, verified_facts, canonical)
    if extra:                                                  # F50 A: el bloque de people_groups, al final
        prompt = prompt.rstrip() + "\n\n" + extra
    try:
        data = claude_helpers.call_json(prompt, model=MODELO_CANON, effort=ESFUERZO_CANON,
                                        description="canon visual")
    except claude_helpers.ClaudeError as e:
        raise CanonError(f"{MODELO_CANON}: {e}") from e
    if not isinstance(data, dict):
        raise CanonError(f"{MODELO_CANON}: la respuesta no es un objeto JSON")
    raw_era = data.get("era_visual_canon")
    if not (isinstance(raw_era, dict) and isinstance(raw_era.get("periods"), list) and raw_era["periods"]):
        raise CanonError(f"{MODELO_CANON}: la respuesta no trae era_visual_canon.periods")
    if not [g for g in data.get("people_groups") or [] if isinstance(g, dict) and g.get("id")]:
        raise CanonError(f"{MODELO_CANON}: la respuesta no trae people_groups")

    # ─── BLOQUE 1: era_visual_canon ───
    raw_era = data.get("era_visual_canon", {})
    era_canon = _clean_era_canon(raw_era)
    # condition_evolution es OBJETO → clean aparte (no entra en _clean_era_canon).
    era_canon["condition_evolution"] = _clean_condition_evolution(
        raw_era.get("condition_evolution") if isinstance(raw_era, dict) else None
    )
    # F50d A: la época por tramo (lista de objetos; _clean_era_canon solo deja los campos planos)
    if isinstance(raw_era, dict) and isinstance(raw_era.get("periods"), list):
        era_canon["periods"] = [{k: _flatten_to_str(p.get(k, "")) for k in PERIODO_CAMPOS}
                                for p in raw_era["periods"] if isinstance(p, dict)]

    # ─── BLOQUE 2: documented_people ───
    raw_people = data.get("documented_people", [])
    if not isinstance(raw_people, list):
        raw_people = []
    cleaned_people: list[dict] = []
    for raw_p in raw_people:
        cp = _clean_person(raw_p)
        if cp is not None:
            cleaned_people.append(cp)

    # ─── BLOQUE 3: anachronism_blocklist ───
    blocklist = _clean_blocklist(data.get("anachronism_blocklist", []))

    # ─── BLOQUE 4: documented_props (eslabón 2) ───
    raw_props = data.get("documented_props", [])
    if not isinstance(raw_props, list):  # puede venir None
        raw_props = []
    cleaned_props = [cp for rp in raw_props if (cp := _clean_prop(rp)) is not None]

    out = {
        "era_visual_canon": era_canon,
        "documented_people": cleaned_people,
        "anachronism_blocklist": blocklist,
        "documented_props": cleaned_props,
        "central_subject": _clean_central_subject(data.get("central_subject")),
    }
    # F50 A: grupos con id (= lab f46b.canon_c)
    out["people_groups"] = [g for g in data.get("people_groups") or [] if isinstance(g, dict) and g.get("id")]
    return out


# ═══════════════════════════════════════════════════════════════
#  F50 A — CANON DESDE LA FICHA (antes de m03; reemplaza al 4e del research)
# ═══════════════════════════════════════════════════════════════

# los textos del lab (F46b texto 1; F48 TEXTO_S5); F50d A: where_when con todos los años y clothing_by_period;
# F51b: appearance = solo los rasgos fijos, y el estado documentado va a condition_by_period (nadie lo pega en la foto)
TEXTO_1_PEOPLE_GROUPS = """═══ BLOQUE EXTRA: people_groups ═══
Lista de los grupos de personas que el material documenta en este caso (hechos, cronología, escenas y citas de arriba). Por grupo, un objeto:
- id: corto, snake_case, en inglés (p. ej. "spanish_migrant_families")
- who: quiénes son y su origen documentado (EN, una frase)
- where_when: dónde y en qué años aparecen, todos los años en que el material los muestra, también décadas después (EN, una frase)
- appearance: solo los rasgos físicos fijos de la persona según su origen documentado: tono de piel, color y tipo de pelo, color de ojos, rasgos de la cara y contextura (EN, una frase). Nada que cambie según dónde estén, qué hagan o qué les pase: eso va en condition_by_period
- condition_by_period: una entrada por cada tramo de años en que el material documenta un estado físico de ese grupo (polvo, suciedad, bronceado, heridas, enfermedad, desgaste); years "AAAA-AAAA" y condition (EN, una frase). Si el material no documenta ningún estado, lista vacía
- clothing_by_period: una entrada por cada tramo de años en que el material muestra a ese grupo; years "AAAA-AAAA" y clothing: ropa, peinado y accesorios de ESE grupo en ESE tramo, ese clima y esa clase social (EN, una frase)
Sin nombres propios de personas. Solo grupos que el material documenta; si el material no dice el origen de un grupo, no lo inventes: dejá appearance vacío."""
TEXTO_S5 = ("Personajes del material (rol · lugar · años; sin nombres). Que ningún grupo que aparezca acá quede fuera de "
            "people_groups:")

# F50d A: la época por tramo de años («AAAA-AAAA», como `spans`): los campos de cada period
PERIODO_CAMPOS = ("years", "clothing", "technology", "vehicles_machinery", "interiors")


def adaptador_facts(ficha: dict) -> list[dict]:
    """La ficha como «verified_facts» del canon (dato, no regla): hechos, cronología «fecha: evento» y escenas
    «donde — quien — que_pasa — sentidos»."""
    out = [{"fact": h.get("texto") or ""} for h in ficha.get("hechos") or []]
    out += [{"fact": f"{c.get('fecha') or ''}: {c.get('evento') or ''}"} for c in ficha.get("cronologia") or []]
    out += [{"fact": " — ".join(str(e.get(k) or "") for k in ("donde", "quien", "que_pasa", "sentidos"))}
            for e in ficha.get("escenas") or []]
    return [f for f in out if f["fact"].strip(" :—")]


def bloque_people_groups(topic: dict) -> str:
    """Texto 1 + TEXTO_S5 + los personajes del pool (rol · lugar · años), al final del pedido."""
    pers = (topic.get("evidence_pool") or {}).get("personajes") or []
    lineas = [f"- {(p.get('rol') or '').strip().rstrip('.')} · {p.get('lugar') or '-'} · "
              f"{', '.join(p.get('fechas_presente') or []) or '-'}" for p in pers]
    return TEXTO_1_PEOPLE_GROUPS + "\n" + TEXTO_S5 + "\n" + "\n".join(lineas)


def _args_canon(topic: dict, ficha: dict) -> dict:
    return {"seed": {"seed_title": topic.get("video_title")}, "angle_blocks": {},
            "verified_facts": adaptador_facts(ficha), "canonical": topic.get("canonical_subject_description"),
            "extra": bloque_people_groups(topic)}


def pedido_canon(topic: dict, ficha: dict) -> str:
    """El texto exacto que `canon_desde_ficha` le manda al modelo (el mismo armado que `extract_visual_canon`)."""
    a = _args_canon(topic, ficha)
    return _build_prompt(a["seed"], a["angle_blocks"], a["verified_facts"], a["canonical"]).rstrip() + "\n\n" + a["extra"]


def marca_canon(topic: dict, ficha: dict, ficha_bytes: bytes) -> str:
    """F50f: md5(ficha + texto del pedido del canon + modelo + esfuerzo). Cambiar el pedido o el modelo rehace el
    canon en cualquier tema."""
    import hashlib
    return hashlib.md5(ficha_bytes + pedido_canon(topic, ficha).encode("utf-8")
                       + f"{MODELO_CANON}|{ESFUERZO_CANON}".encode("utf-8")).hexdigest()


def canon_desde_ficha(topic: dict, ficha: dict) -> dict:
    """El canon visual en UNA llamada a `MODELO_CANON`, con la ficha como hechos (sin bloques de ángulo) y
    `people_groups`. Todas las claves salen de esta respuesta; si no sale, CanonError."""
    return extract_visual_canon(**_args_canon(topic, ficha))
