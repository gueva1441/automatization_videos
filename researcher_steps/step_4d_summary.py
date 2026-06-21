"""
researcher_steps/step_4d_summary.py — Sub-paso 4d del módulo 00.

Tarea ÚNICA: escribir un research_summary masivo (1500-3000 chars) que
sirva de materia prima al guionista (~1,800 palabras de guion).

Recibe verified_facts + canonical + meta CERRADOS. NO redunda los facts
ya capturados — aporta CONTEXTO NARRATIVO (cronología, atmósfera, tensión).

INPUT:  seed + angle_blocks + verified_facts + canonical + meta (todo cerrado)
OUTPUT: {"research_summary": str}
"""

from gemini_helpers import call_flash_json


def _format_facts(verified_facts: list) -> str:
    """Convierte verified_facts a texto enumerado."""
    if not verified_facts:
        return "(sin facts)"
    lines = []
    for i, f in enumerate(verified_facts, 1):
        if isinstance(f, dict):
            lines.append(f"  {i}. {f.get('fact', '')}")
        else:
            lines.append(f"  {i}. {f}")
    return "\n".join(lines)


def _format_blocks_full(angle_blocks: dict) -> str:
    """Bloques completos para que el summary tenga material."""
    parts = []
    for key in ("tecnico", "humano", "misterio"):
        block = angle_blocks.get(key, "")
        if block:
            parts.append(f"=== BLOQUE {key.upper()} ===\n{block}")
    return "\n\n".join(parts) if parts else "(sin bloques)"


def _build_prompt(
    seed: dict,
    angle_blocks: dict,
    verified_facts: list,
    canonical: str,
    meta: dict,
) -> str:
    """Construye el prompt del sub-paso 4d."""
    facts_block = _format_facts(verified_facts)
    blocks_block = _format_blocks_full(angle_blocks)

    meta_summary = (
        f"  Title:    {meta.get('video_title', '')}\n"
        f"  Hook:     {meta.get('hook', '')}\n"
        f"  Mystery:  {meta.get('mystery', '')}\n"
        f"  Reveal:   {meta.get('reveal', '')}\n"
        f"  Angle:    {meta.get('angle', '')}"
    )

    return f"""Eres un editor de documentales largos (estilo History Channel /
Netflix). Tu tarea: escribir el research_summary masivo que será materia
prima del guionista para producir 1,800 palabras de guión.

TEMA: "{seed.get('seed_title', '?')}"

═══════════════════════════════════════════════════
DATOS DUROS YA CAPTURADOS (NO los repitas literal)
═══════════════════════════════════════════════════
{facts_block}

═══════════════════════════════════════════════════
CANONICAL (cerrado)
═══════════════════════════════════════════════════
{canonical or "(sin canonical)"}

═══════════════════════════════════════════════════
META NARRATIVA (cerrada)
═══════════════════════════════════════════════════
{meta_summary}

═══════════════════════════════════════════════════
BLOQUES DE INVESTIGACIÓN ORIGINALES (material crudo)
═══════════════════════════════════════════════════
{blocks_block}

═══════════════════════════════════════════════════
TU TAREA: research_summary de 1500-3000 caracteres
═══════════════════════════════════════════════════

ESTRUCTURA OBLIGATORIA (3 párrafos, separados con ||):

[TÉCNICA] Párrafo con datos duros del bloque técnico: cronología,
fechas exactas, números, instituciones. Aportá CONTEXTO que el guionista
necesita para narrar (no solo datos sueltos).

||

[HUMANA] Párrafo con nombres reales y testimonios del bloque humano:
quiénes vivieron esto, qué les pasó, qué dijeron. Atmósfera, tensión.

||

[MISTERIO] Párrafo con teorías y cabos sueltos del bloque misterio:
qué queda sin explicar, qué documentos siguen clasificados, qué
investigadores siguen el caso hoy.

REGLAS:
1. NO repitas literal los facts ya capturados arriba (el guionista los
   tiene aparte). Aportá CONTEXTO NARRATIVO, no datos sueltos.
2. Sin adjetivos vacíos. Sin redundancias entre párrafos.
3. Mínimo 1500 caracteres. Máximo 3000.
4. En español neutro.

FORMATO DE SALIDA — JSON puro, sin markdown:

{{
  "research_summary": "[TÉCNICA] ... || [HUMANA] ... || [MISTERIO] ..."
}}

RESPONDE SOLO CON EL JSON."""


def extract_research_summary(
    seed: dict,
    angle_blocks: dict,
    verified_facts: list,
    canonical: str,
    meta: dict,
) -> dict:
    """
    Sub-paso 4d: genera research_summary masivo.

    Args:
        seed: el seed original.
        angle_blocks: los 3 bloques angulares.
        verified_facts: facts cerrados del 4a.
        canonical: canonical cerrado del 4b.
        meta: meta narrativa cerrada del 4c.

    Returns:
        {"research_summary": str (1500-3000 chars)}
    """
    prompt = _build_prompt(seed, angle_blocks, verified_facts, canonical, meta)
    data = call_flash_json(prompt)

    summary = str(data.get("research_summary", "") or "").strip()

    # Si Gemini fue muy corto, marcamos pero no rompemos (puede pasar)
    if len(summary) < 500:
        # Devolvemos lo que tengamos — el orquestador loguea el tamaño
        pass

    return {"research_summary": summary}
