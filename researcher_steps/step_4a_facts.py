"""
researcher_steps/step_4a_facts.py — Sub-paso 4a del módulo 00.

Tarea ÚNICA: extraer datos duros (verified_facts) y fuentes (sources)
de los 3 bloques angulares, etiquetando cada fact con su bloque de origen.

Esto rompe el bug 1943↔1937: cada cifra/fecha queda marcada con su
source_block (tecnico|humano|misterio), imposible mezclarlas.

INPUT:  angle_blocks = {bloque_tecnico, bloque_humano, bloque_misterio}
OUTPUT: {
  "verified_facts": [{"fact": "...", "source_block": "tecnico"}, ...],
  "sources": ["autor/publicación/año", ...]
}
"""

from gemini_helpers import call_flash_json


def _build_prompt(angle_blocks: dict[str, str]) -> str:
    """Construye el prompt del sub-paso 4a."""
    return f"""Eres un investigador documental. Tienes 3 bloques de investigación
angular sobre el mismo tema, cada uno enfocado en un ángulo distinto.

═══════════════════════════════════════════════════
[BLOQUE TÉCNICO] — datos duros, fechas, cifras
═══════════════════════════════════════════════════
{angle_blocks.get("tecnico", "(vacío)")}

═══════════════════════════════════════════════════
[BLOQUE HUMANO] — personas, testigos, víctimas
═══════════════════════════════════════════════════
{angle_blocks.get("humano", "(vacío)")}

═══════════════════════════════════════════════════
[BLOQUE MISTERIO] — teorías, cabos sueltos
═══════════════════════════════════════════════════
{angle_blocks.get("misterio", "(vacío)")}

═══════════════════════════════════════════════════
TU TAREA: Extraer datos duros y fuentes de los 3 bloques.
═══════════════════════════════════════════════════

REGLAS DE verified_facts:
1. Extraé entre 6 y 12 datos duros.
2. Cada dato debe ser VERIFICABLE: cifra exacta, fecha, nombre propio, lugar.
3. AL MENOS 3 datos deben ser VISUALES (cómo se ve un objeto/lugar/sujeto).
   Ej VÁLIDO visual: "blue-grey crocidolite asbestos tailings piles"
   Ej VÁLIDO visual: "isolated outback corrugated iron and timber houses"
   Ej INVÁLIDO (no visual): "el desastre fue grande"
4. Cada dato DEBE traer source_block indicando su origen:
   "tecnico" | "humano" | "misterio"
5. Si un dato aparece en 2 bloques, eligí el bloque DOMINANTE
   (donde tiene más contexto/peso) — no lo dupliques.

REGLAS DE sources:
1. Entre 6 y 10 fuentes textuales con formato: autor/publicación/año.
   Ej: "Hills B, 1989, Blue Murder. South Melbourne: Sun Books"
2. NO inventes URLs.
3. Solo las fuentes que aparecen explícitamente en los bloques.

FORMATO DE SALIDA — JSON puro, sin markdown, sin texto adicional:

{{
  "verified_facts": [
    {{"fact": "<dato concreto>", "source_block": "tecnico"}},
    {{"fact": "<dato concreto>", "source_block": "humano"}},
    {{"fact": "<dato concreto visual>", "source_block": "misterio"}}
  ],
  "sources": [
    "<autor/publicación/año>",
    "<autor/publicación/año>"
  ]
}}

RESPONDE SOLO CON EL JSON."""


def extract_facts_and_sources(angle_blocks: dict[str, str]) -> dict:
    """
    Sub-paso 4a: extrae verified_facts (etiquetados) + sources.

    Args:
        angle_blocks: dict con bloque_tecnico, bloque_humano, bloque_misterio.

    Returns:
        {
          "verified_facts": [{"fact": str, "source_block": str}, ...],
          "sources": [str, ...]
        }
    """
    if not angle_blocks:
        return {"verified_facts": [], "sources": []}

    prompt = _build_prompt(angle_blocks)
    data = call_flash_json(prompt)

    # ─── Validación defensiva ───
    facts = data.get("verified_facts", [])
    if not isinstance(facts, list):
        facts = []

    # Cada fact debe ser dict con fact + source_block
    valid_facts = []
    valid_blocks = {"tecnico", "humano", "misterio"}
    for f in facts:
        if isinstance(f, dict):
            fact_text = (f.get("fact") or "").strip()
            block = (f.get("source_block") or "").strip().lower()
            if fact_text and block in valid_blocks:
                valid_facts.append({"fact": fact_text, "source_block": block})
        elif isinstance(f, str) and f.strip():
            # Tolerancia: si Gemini devolvió string, etiquetar como "tecnico"
            valid_facts.append({"fact": f.strip(), "source_block": "tecnico"})

    sources = data.get("sources", [])
    if not isinstance(sources, list):
        sources = []
    sources = [str(s).strip() for s in sources if str(s).strip()]

    return {
        "verified_facts": valid_facts,
        "sources": sources,
    }
