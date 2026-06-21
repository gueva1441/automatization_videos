"""
researcher_steps/step_4b_canonical.py — Sub-paso 4b del módulo 00.

Tarea ÚNICA: generar la descripción canónica del sujeto principal
recurrente del video (en inglés, 20-35 palabras).

Recibe verified_facts CERRADO. La canonical hereda geo+era literales
de los facts — imposible inventar datos nuevos.

INPUT:  seed + angle_blocks + verified_facts (ya cerrado)
OUTPUT: {"canonical_subject_description": "..." | None}
"""

from gemini_helpers import call_flash_json


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


def _build_prompt(seed: dict, angle_blocks: dict, verified_facts: list) -> str:
    """Construye el prompt del sub-paso 4b."""
    facts_block = _format_facts(verified_facts)
    blocks_block = _format_blocks(angle_blocks)

    return f"""Eres un director de fotografía documental. Tu tarea: escribir UNA
descripción visual canónica del sujeto principal recurrente del tema.

TEMA: "{seed.get('seed_title', '?')}"

DATOS DUROS YA EXTRAÍDOS (NO inventes nuevos):
{facts_block}

BLOQUES DE INVESTIGACIÓN ORIGINALES (contexto):
{blocks_block}

═══════════════════════════════════════════════════
TU TAREA
═══════════════════════════════════════════════════

Escribí 1-2 oraciones EN INGLÉS (~20-35 palabras) describiendo el sujeto
principal recurrente que aparecerá en las imágenes del video.

REGLAS:
1. EN INGLÉS, no español.
2. ELEGÍ UN TIPO de sujeto según el tema:
   - OBJETO FÍSICO ÚNICO: barco, sonda, criatura, objeto histórico
     Ej: "A 1950s steel-hulled cargo ship, 110 feet long, weathered hull,
          peeling white paint, raised pilothouse, single funnel."
   - PERSONA/GRUPO: explorador, equipo, víctima recurrente
     Ej: "A 1960s European immigrant miner in his 40s, weathered face,
          dust-coated workwear, helmet with carbide lamp."
   - LUGAR: mina, ciudad, sitio histórico
     Ej: "A 1950s isolated outback Australian town, corrugated iron and
          timber houses scattered across deep red ochre Pilbara soil."
3. Cualquier referencia GEOGRÁFICA (lugar, región) DEBE existir literal
   en los verified_facts. NO inventes lugares.
4. Cualquier referencia TEMPORAL (año, década) DEBE existir literal
   en los verified_facts. NO inventes fechas.
5. Si el tema NO tiene un sujeto físico recurrente claro, devolvé null.

FORMATO DE SALIDA — JSON puro, sin markdown:

{{
  "canonical_subject_description": "A <descripción en inglés>"
}}

O si no hay sujeto claro:

{{
  "canonical_subject_description": null
}}

RESPONDE SOLO CON EL JSON."""


def extract_canonical(
    seed: dict,
    angle_blocks: dict,
    verified_facts: list,
) -> dict:
    """
    Sub-paso 4b: genera canonical_subject_description.

    Args:
        seed: el seed original.
        angle_blocks: los 3 bloques angulares.
        verified_facts: facts ya cerrados del sub-paso 4a.

    Returns:
        {"canonical_subject_description": str | None}
    """
    if not verified_facts:
        return {"canonical_subject_description": None}

    prompt = _build_prompt(seed, angle_blocks, verified_facts)
    data = call_flash_json(prompt)

    canonical = data.get("canonical_subject_description")
    if canonical is None:
        return {"canonical_subject_description": None}
    if not isinstance(canonical, str):
        canonical = str(canonical)
    canonical = canonical.strip()
    if not canonical or canonical.lower() in ("null", "none", ""):
        return {"canonical_subject_description": None}

    # Truncar si Gemini se pasó de palabras
    if len(canonical) > 500:
        canonical = canonical[:497] + "..."

    return {"canonical_subject_description": canonical}
