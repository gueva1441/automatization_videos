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

INPUT:  seed + angle_blocks + verified_facts + canonical (todo cerrado)
OUTPUT: {
  "era_visual_canon": {
    "primary_decade": str,
    "spans": str,
    "clothing": str,
    "technology": str,
    "vehicles_machinery": str,
    "interiors": str,
    "forbidden_anachronisms": str
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
    """Concatena los 3 bloques angulares (truncados) para contexto."""
    parts = []
    for key in ("tecnico", "humano", "misterio"):
        block = angle_blocks.get(key, "")
        if block:
            parts.append(f"[{key.upper()}]\n{block[:1500]}")
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

BLOQUES DE INVESTIGACIÓN ORIGINALES (contexto para deducir época):
{blocks_block}

═══════════════════════════════════════════════════
TU TAREA
═══════════════════════════════════════════════════

Emití un objeto JSON con TRES bloques: era_visual_canon, documented_people,
anachronism_blocklist. Strings en INGLÉS (los consumirán Flux y Veo).

═══ BLOQUE 1: era_visual_canon ═══

Describe cómo se ve el mundo del tema en su época. 7 sub-campos:

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

REGLAS de era_visual_canon:
1. Solo elementos GENÉRICOS y AMPLIAMENTE DOCUMENTADOS de la época. NO
   detalles específicos no verificables (ej: "the captain wore a Rolex").
2. Si dudás entre 2 versiones de un detalle, usá el más genérico.
3. primary_decade y spans deben ser COHERENTES con las fechas en
   verified_facts. NO inventes décadas.

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
    "forbidden_anachronisms": "..."
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

RESPONDE SOLO CON EL JSON."""


# ═══════════════════════════════════════════════════════════════
#  VALIDACIÓN DEFENSIVA
# ═══════════════════════════════════════════════════════════════

_ERA_REQUIRED_KEYS = (
    "primary_decade",
    "spans",
    "clothing",
    "technology",
    "vehicles_machinery",
    "interiors",
    "forbidden_anachronisms",
)

_PERSON_REQUIRED_KEYS = ("name", "role", "era", "appearance_canon")


def _empty_canon() -> dict:
    """Estructura vacía pero con shape correcto (para que m03/m05 no rompan)."""
    return {
        "era_visual_canon": {k: "" for k in _ERA_REQUIRED_KEYS},
        "documented_people": [],
        "anachronism_blocklist": [],
    }


def _clean_era_canon(raw: dict) -> dict:
    """Asegura las 7 keys de era_visual_canon. Faltantes → string vacío."""
    if not isinstance(raw, dict):
        return {k: "" for k in _ERA_REQUIRED_KEYS}
    cleaned = {}
    for k in _ERA_REQUIRED_KEYS:
        v = raw.get(k, "")
        cleaned[k] = str(v).strip() if v is not None else ""
    return cleaned


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

    try:
        data = call_flash_json(prompt)
    except Exception:
        # Tolerancia defensiva (consistente con 4b). No rompemos el m00 entero
        # por un fallo del 4e — m03 va a degradar a inferir, pero el pipeline
        # sigue. El test_module_00 detectará el vacío.
        return _empty_canon()

    if not isinstance(data, dict):
        return _empty_canon()

    # ─── BLOQUE 1: era_visual_canon ───
    era_canon = _clean_era_canon(data.get("era_visual_canon", {}))

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
