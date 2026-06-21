"""
researcher_steps/step_4c_meta.py — Sub-paso 4c del módulo 00.

Tarea ÚNICA: generar la meta narrativa del video.

Recibe verified_facts + canonical CERRADOS. Cualquier fecha/cifra que
aparezca en hook/mystery/reveal/angle DEBE existir literal en los facts
— imposible inventar datos.

INPUT:  seed + angle_blocks + verified_facts + canonical (todo cerrado)
OUTPUT: {
  "video_title": str,
  "search_keyword": str,
  "hook": str,
  "mystery": str,
  "reveal": str,
  "angle": str,
  "virality_score": int 1-10
}
"""

from gemini_helpers import call_flash_json


def _format_facts(verified_facts: list) -> str:
    """Convierte verified_facts a texto enumerado."""
    if not verified_facts:
        return "(sin facts)"
    lines = []
    for i, f in enumerate(verified_facts, 1):
        if isinstance(f, dict):
            fact_text = f.get("fact", "")
            block = f.get("source_block", "")
            lines.append(f"  {i}. [{block}] {fact_text}")
        else:
            lines.append(f"  {i}. {f}")
    return "\n".join(lines)


def _format_blocks_short(angle_blocks: dict) -> str:
    """Versión corta de los bloques (truncados a 800 chars c/u)."""
    parts = []
    for key in ("tecnico", "humano", "misterio"):
        block = angle_blocks.get(key, "")
        if block:
            parts.append(f"[{key.upper()}] {block[:800]}")
    return "\n\n".join(parts) if parts else "(sin bloques)"


def _build_prompt(
    seed: dict,
    angle_blocks: dict,
    verified_facts: list,
    canonical: str,
) -> str:
    """Construye el prompt del sub-paso 4c."""
    facts_block = _format_facts(verified_facts)
    blocks_block = _format_blocks_short(angle_blocks)
    canonical_text = canonical or "(sin canonical)"

    return f"""Eres un editor de contenido viral en español neutro. Tu tarea:
generar la meta narrativa del video.

TEMA: "{seed.get('seed_title', '?')}"
NICHO: {seed.get('root_niche', 'general')}

═══════════════════════════════════════════════════
DATOS DUROS (cerrados, NO inventes nuevos)
═══════════════════════════════════════════════════
{facts_block}

═══════════════════════════════════════════════════
CANONICAL VISUAL (cerrado)
═══════════════════════════════════════════════════
{canonical_text}

═══════════════════════════════════════════════════
BLOQUES DE INVESTIGACIÓN (contexto)
═══════════════════════════════════════════════════
{blocks_block}

═══════════════════════════════════════════════════
TU TAREA: generar 7 campos meta del video
═══════════════════════════════════════════════════

REGLAS INNEGOCIABLES:

1. **Cualquier fecha, cifra o nombre propio** que aparezca en
   hook/mystery/reveal/angle DEBE existir literal en los verified_facts
   listados arriba. PROHIBIDO inventar datos nuevos.

2. **search_keyword**: ENTIDAD PURA, máximo 2-3 palabras.
   Sin años, sin artículos, sin verbos, sin adjetivos.
   ✓ Válidos: "MV Joyita", "USS Thresher", "Wittenoom", "K-129"
   ✗ Inválidos: "Misterio del MV Joyita", "Wittenoom 1966",
                "El desastre de Chernobyl"

3. **video_title**: ≤62 chars en español, sin signos. Buscable. Apuntá a 6-10 palabras.

4. **hook**: ≤12 palabras. Scroll-stopper anclado en una cifra/fecha
   real de los facts.

5. **mystery**: 1 oración con el enigma central.

6. **reveal**: 1 oración con la teoría/respuesta principal.

7. **angle**: 2 oraciones con datos duros (cifras + nombres reales).

8. **virality_score**: int 1-10. Score 8-10 si tiene ≥3 facts impactantes
   (cifras grandes, conspiración, encubrimiento, número alto de víctimas).
   Score 5-7 si tiene 1-2 facts impactantes. Score 1-4 si la historia es
   interesante pero sin elementos de pico viral.

FORMATO DE SALIDA — JSON puro, sin markdown:

{{
  "video_title": "...",
  "search_keyword": "...",
  "hook": "...",
  "mystery": "...",
  "reveal": "...",
  "angle": "...",
  "virality_score": 7
}}

RESPONDE SOLO CON EL JSON."""


def extract_meta(
    seed: dict,
    angle_blocks: dict,
    verified_facts: list,
    canonical: str,
) -> dict:
    """
    Sub-paso 4c: genera la meta narrativa.

    Args:
        seed: el seed original.
        angle_blocks: los 3 bloques angulares.
        verified_facts: facts cerrados del 4a.
        canonical: canonical cerrado del 4b (puede ser None/"").

    Returns:
        dict con title, search_keyword, hook, mystery, reveal, angle, virality.
    """
    prompt = _build_prompt(seed, angle_blocks, verified_facts, canonical)
    data = call_flash_json(prompt)

    # ─── Validación defensiva ───
    out = {
        "video_title": str(data.get("video_title", "") or "").strip(),
        "search_keyword": str(data.get("search_keyword", "") or "").strip(),
        "hook": str(data.get("hook", "") or "").strip(),
        "mystery": str(data.get("mystery", "") or "").strip(),
        "reveal": str(data.get("reveal", "") or "").strip(),
        "angle": str(data.get("angle", "") or "").strip(),
        "virality_score": data.get("virality_score", 5),
    }

    # Validar virality_score: int 1-10
    try:
        vs = int(out["virality_score"])
        if vs < 1 or vs > 10:
            vs = 5
    except (ValueError, TypeError):
        vs = 5
    out["virality_score"] = vs

    return out
