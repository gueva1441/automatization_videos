"""
researcher_steps/step_4e_visual_canon.py — Sub-paso 4e del módulo 00.

Tarea ÚNICA: emitir el "canon visual" del tema en una sola llamada Flash.
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

Recibe verified_facts + canonical CERRADOS y angle_blocks como contexto
de época. NO inventa fechas/personas/lugares — los hereda de los facts.

ESLABÓN 2 (B-eslabon2): _format_blocks ahora surfacea el 4º ángulo "visual"
(eslabón 1, ya en prod) que antes caía en angle_blocks pero NUNCA entraba al
prompt. era_visual_canon se extiende con una 2ª CAPA de campos SOURCED del
sujeto puntual (materials_textures, color_palette, scale_dimensions,
distinctive_features, demographics, visual_reference_availability,
condition_evolution) que salen de ese bloque visual. color_palette se fuerza a
flat-string vía response_schema nullable. C5: era/ropa que se colaba en
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
     "appearance_canon": str},
    ...
  ],
  "anachronism_blocklist": [str, ...]
}

NUMERACIÓN EN DISCO: el orquestador persiste este sub-paso como
`05_visual_canon.json` para mantener consistencia con la numeración
entera del resto (00→04). El "4e" es interno al razonamiento del
módulo 00 (es el quinto sub-paso del paso 4 del orquestador), no una
nomenclatura de filesystem.
"""

import re

from google.genai import types as genai_types

from gemini_helpers import call_flash_json


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

Emití un objeto JSON con TRES bloques: era_visual_canon, documented_people,
anachronism_blocklist. Strings en INGLÉS (los consumirán Flux y Veo).

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
- appearance_canon: 1-2 frases EN describiendo aspecto físico genérico
  (edad aparente + nacionalidad/etnia + rol + atuendo de época). PROHIBIDO
  mencionar el nombre real. PROHIBIDO mencionar rasgos específicos como
  "tall", "blue eyes", "scar" — solo descriptores ampliamente verificables.

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
   ✓ BIEN: "a mid-30s American naval officer with focused demeanor"

✗ MAL appearance_canon: "Francis Slattery, a 36-year-old American naval
                          officer with focused gaze"
                          (incluye nombre propio, prohibido por regla)
✗ MAL appearance_canon: "a mid-30s American naval officer in 1960s
                          service uniform, focused authoritative demeanor"
                          (incluye era textual "1960s service uniform" — la era
                          va separada en era_visual_canon.clothing, NO acá)
✓ BIEN appearance_canon: "a mid-30s American naval officer with focused
                           authoritative demeanor"
                           (solo rol + edad + nacionalidad + actitud, sin era;
                           la era se infiere del era_visual_canon del topic)

═══ BLOQUE 3: anachronism_blocklist ═══

Array plano de strings con elementos visuales prohibidos para este tema.
Mínimo 6, máximo 12 items. Incluí AL MENOS:
- "smartphones"
- "LED screens" o "modern flat panels"
- "contemporary clothing" (post-2000s)
- al menos 1 item específico al tema (ej: "modern submarine designs"
  para un tema naval de los 60s, "modern industrial safety equipment"
  para un tema minero de mediados de siglo).

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
      "appearance_canon": "a mid-30s American naval officer with focused authoritative demeanor"
    }}
  ],
  "anachronism_blocklist": [
    "smartphones",
    "LED screens",
    "contemporary clothing",
    "modern flat panels",
    "modern cars post-1980",
    "branded modern logos"
  ]
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


# ═══════════════════════════════════════════════════════════════
#  RESPONSE SCHEMA (decisión B chat 93) — fuerza el TIPO, NO la presencia
# ═══════════════════════════════════════════════════════════════
#
# Root-cause de color_palette dict {ext,int}: el modelo lo emitía como objeto.
# El schema fuerza color_palette (y todos los sourced) a STRING. PERO: pasar un
# response_schema vuelve los campos OBLIGATORIOS (gemini_helpers L127-129) → en
# topics POBRES forzaría a inventar. Por eso TODO va nullable=True y NADA en
# `required`: el modelo puede devolver null/"" sin presión de alucinar. Solo se
# constriñe el TIPO. El flatten defensivo de _clean_era_canon es el cinturón.
_STR = genai_types.Schema(type=genai_types.Type.STRING, nullable=True)

_VISUAL_CANON_SCHEMA = genai_types.Schema(
    type=genai_types.Type.OBJECT,
    nullable=True,
    properties={
        "era_visual_canon": genai_types.Schema(
            type=genai_types.Type.OBJECT,
            nullable=True,
            properties={
                "primary_decade": _STR,
                "spans": _STR,
                "clothing": _STR,
                "technology": _STR,
                "vehicles_machinery": _STR,
                "interiors": _STR,
                "forbidden_anachronisms": _STR,
                "materials_textures": _STR,
                "color_palette": _STR,       # ← el objetivo: STRING, nunca objeto
                "scale_dimensions": _STR,
                "distinctive_features": _STR,
                "demographics": _STR,
                "visual_reference_availability": _STR,
                "condition_evolution": genai_types.Schema(
                    type=genai_types.Type.OBJECT,
                    nullable=True,
                    properties={"at_event": _STR, "later": _STR},
                ),
            },
        ),
        "documented_people": genai_types.Schema(
            type=genai_types.Type.ARRAY,
            nullable=True,
            items=genai_types.Schema(
                type=genai_types.Type.OBJECT,
                properties={
                    "name": _STR,
                    "role": _STR,
                    "age_at_event": genai_types.Schema(
                        type=genai_types.Type.INTEGER, nullable=True
                    ),
                    "era": _STR,
                    "appearance_canon": _STR,
                },
            ),
        ),
        "anachronism_blocklist": genai_types.Schema(
            type=genai_types.Type.ARRAY,
            nullable=True,
            items=genai_types.Schema(type=genai_types.Type.STRING),
        ),
    },
)


def _empty_canon() -> dict:
    """Estructura vacía pero con shape correcto (para que m03/m05 no rompan)."""
    era = {k: "" for k in _ERA_REQUIRED_KEYS}
    era["condition_evolution"] = {"at_event": "", "later": ""}  # objeto, aparte
    return {
        "era_visual_canon": era,
        "documented_people": [],
        "anachronism_blocklist": [],
    }


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

    return {
        "name": name,
        "role": role,
        "age_at_event": age,
        "era": era,
        "appearance_canon": appearance,
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
) -> dict:
    """
    Sub-paso 4e: emite el canon visual del tema.

    Args:
        seed: el seed original (necesita seed_title).
        angle_blocks: los 3 bloques angulares (contexto de época).
        verified_facts: facts ya cerrados del 4a.
        canonical: canonical_subject_description del 4b (puede ser None).

    Returns:
        dict con era_visual_canon, documented_people, anachronism_blocklist.
        Si verified_facts está vacío o Flash falla, retorna estructura
        vacía pero con shape correcto (no rompe el pipeline).
    """
    # Sin facts no podemos derivar época con seguridad. Devolver vacío.
    if not verified_facts:
        return _empty_canon()

    prompt = _build_prompt(seed, angle_blocks, verified_facts, canonical)

    data = None
    try:
        # response_schema (decisión B): fuerza color_palette y sourced a STRING
        # (nullable, no required → no presiona alucinar en topics pobres).
        data = call_flash_json(prompt, response_schema=_VISUAL_CANON_SCHEMA)
    except Exception:
        # El response_schema es la ÚNICA pieza no validada en lab (el probe del
        # chat 93 corrió prompt-only). Si la API lo rechaza, degradá al camino
        # prompt-only que SÍ se validó + flatten defensivo — NO a vacío (sería
        # regresión para TODOS los topics). El prompt ya pide color_palette flat.
        try:
            data = call_flash_json(prompt)
        except Exception:
            # Ahora sí, fallo real del 4e. Tolerancia defensiva (espejo de 4b):
            # no rompemos el m00 — m03 degrada a inferir, el pipeline sigue.
            return _empty_canon()

    if not isinstance(data, dict):
        return _empty_canon()

    # ─── BLOQUE 1: era_visual_canon ───
    raw_era = data.get("era_visual_canon", {})
    era_canon = _clean_era_canon(raw_era)
    # condition_evolution es OBJETO → clean aparte (no entra en _clean_era_canon).
    era_canon["condition_evolution"] = _clean_condition_evolution(
        raw_era.get("condition_evolution") if isinstance(raw_era, dict) else None
    )

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

    return {
        "era_visual_canon": era_canon,
        "documented_people": cleaned_people,
        "anachronism_blocklist": blocklist,
    }
