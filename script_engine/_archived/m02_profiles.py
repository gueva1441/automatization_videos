"""
script_engine/m02_profiles.py — Módulo 02: asignador de profiles.

TAREA ÚNICA: a partir de topic + skeleton (output del 01a) + narración
(output del 01b), elegir UN `art_profile` por cap (de las 13 etiquetas
definidas en `art_profiles.py`).

INPUT:
  topic     — dict (topics_db.json post módulo 00)
  skeleton  — dict {topic_id, chapters[7]} (output del 01a, sin
              _distribution_plan)
  narration — dict {topic_id, chapters[7] con narration, humanizer_phrases}
              (output del 01b)

OUTPUT:
  {
    "topic_id": "uuid",
    "chapters": [
      {
        "chapter_number": 1..7,
        "art_profile": "INTERIOR" | "INDUSTRIAL" | ... ,
        "rationale": "≤200 chars, español, por qué encaja"
      },
      ...
    ]
  }

ESTRUCTURA INTERNA (1 archivo, 5 funciones privadas + 1 pública):
  _format_profiles_guide()                → str (catálogo legible)
  _format_facts(verified_facts)           → str
  _format_chapters(skeleton, narration)   → str
  _build_prompt(topic, skeleton, narr)    → str
  _validate_profiles(data)                → raise si falla
  _persist(topic_id, data)                → escribe _steps/{id}/02_profiles.json
  assign_profiles(topic, skeleton, narr)  → dict       # PÚBLICA

LLAMADAS GEMINI: 1 (Flash con JSON mode).

NOTA:
  No hay retry con feedback. Si el Flash devuelve algo inválido
  (profile fuera del catálogo, faltan caps, etc.) rompe con
  ProfileValidationError. Es responsabilidad del caller decidir reintentar.
"""

import json
from pathlib import Path

from config import DATA_DIR
from gemini_helpers import call_flash_json
from art_profiles import VALID_PROFILES


# ═══════════════════════════════════════════════════════════════
#  PATHS Y CONSTANTES
# ═══════════════════════════════════════════════════════════════

STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"

EXPECTED_CHAPTER_COUNT = 7
MAX_RATIONALE_CHARS = 200

# Guía pedagógica por profile (cuándo usar cada uno).
# OJO: NO confundir con el texto largo de ART_PROFILES (ese es para
# inyectar a Flux). Esta guía es solo para que Flash entienda criterios.
PROFILE_GUIDE: dict[str, str] = {
    "POLAR": (
        "Ártico/Antártico, hielo, glaciares, expediciones polares. "
        "Paleta cyan-blanca con sombras cobalto."
    ),
    "DESERT": (
        "Desierto, dunas, outback, mesetas áridas, pueblos del desierto. "
        "Paleta ocre/sienna quemada con sombras violetas. Calor visible."
    ),
    "JUNGLE": (
        "Selva tropical densa, vegetación cerrada, copas espesas, vapor "
        "y esporas. Paleta esmeralda con luz ámbar filtrada por canopy."
    ),
    "WILDERNESS": (
        "Naturaleza salvaje no tropical: bosques templados, valles, "
        "montañas, lagos, ríos, parques nacionales fríos. "
        "Paleta verde apagado y azul pizarra, niebla matinal."
    ),
    "AERIAL": (
        "Toma desde altura considerable: nubes vistas desde arriba, "
        "panorámica de tierra desde avión, vuelo en cabina alta. "
        "Perspectiva atmosférica con capas de bruma."
    ),
    "SPACE": (
        "Espacio exterior, cosmos, planetas, vacío negro absoluto, "
        "estética NASA-archival. Sin atmósfera, sombras duras."
    ),
    "SUBMARINE": (
        "FONDO marino, abismos oceánicos, pecios sumergidos en negro "
        "absoluto, criaturas bioluminiscentes, expediciones submarinas. "
        "NO usar para barcos en superficie (eso es MARITIME_EXTERIOR)."
    ),
    "MARITIME_EXTERIOR": (
        "Barcos en superficie, puertos, mar abierto vista desde cubierta, "
        "naufragios sobre el agua, puentes de mando. "
        "Paleta steel-blue con ámbar de lámparas. Aire libre marino."
    ),
    "INTERIOR": (
        "Interiores cálidos de cualquier época moderna (siglo XX o XXI): "
        "oficinas, salones, bibliotecas, comedores, casas. Madera, latón, "
        "lámparas. Paleta ámbar/oro viejo con sombras profundas."
    ),
    "URBAN": (
        "Calles de ciudad nocturnas, neón, asfalto mojado, faroles ámbar, "
        "callejones, fachadas urbanas. NO usar para pueblos rurales o "
        "casas aisladas (eso es DESERT/WILDERNESS según contexto)."
    ),
    "INDUSTRIAL": (
        "Fábricas, plantas procesadoras, refinerías, instalaciones "
        "industriales del siglo XX/XXI. Paleta cold slate-blue/ash-grey "
        "OBLIGATORIA. EVITAR sepia/golden/amber (eso entra en HISTORICAL "
        "o INTERIOR). Maquinaria pesada, vapor, polvo industrial."
    ),
    "UNDERGROUND": (
        "Subterráneo: minas excavadas, cuevas, túneles, galerías, "
        "catacumbas. Luz puntual de antorchas o linternas. Paleta "
        "mineral-green/slate-cyan con voids negros. NO confundir con "
        "INDUSTRIAL (planta procesadora) — UNDERGROUND es la galería."
    ),
    "HISTORICAL": (
        "EXCLUSIVO para épocas PRE-INDUSTRIALES (Antigüedad, Edad Media, "
        "época colonial, hasta inicios siglo XIX). Iluminación por velas, "
        "antorchas, fuegos de hogar. Paleta candle-lit gold + parchment. "
        "PROHIBIDO para temas del siglo XX/XXI — usar INTERIOR/INDUSTRIAL."
    ),
}


# ═══════════════════════════════════════════════════════════════
#  CONSTRUCCIÓN DEL PROMPT
# ═══════════════════════════════════════════════════════════════

def _format_profiles_guide() -> str:
    """Devuelve el catálogo de 13 profiles en bloque legible."""
    lines = []
    for name in sorted(PROFILE_GUIDE.keys()):
        lines.append(f"  • {name}")
        lines.append(f"      {PROFILE_GUIDE[name]}")
    return "\n".join(lines)


def _format_facts(verified_facts: list) -> str:
    """Enumera verified_facts numerados (mismo formato que 01a/01b)."""
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
            lines.append(f"  [F{i:02d}] {f.strip()}")
    return "\n".join(lines)


def _format_chapters(skeleton: dict, narration: dict) -> str:
    """
    Concatena por cap: número, role, render_engine, title, bullets, narración.
    Es el bloque más importante del prompt — Flash decide profile a partir de
    lo que dice acá.
    """
    skel_chs = {ch["chapter_number"]: ch for ch in skeleton.get("chapters", [])}
    narr_chs = {ch["chapter_number"]: ch for ch in narration.get("chapters", [])}

    blocks = []
    for n in range(1, EXPECTED_CHAPTER_COUNT + 1):
        sch = skel_chs.get(n) or {}
        nch = narr_chs.get(n) or {}

        title = (sch.get("title") or "(sin título)").strip()
        role = sch.get("role") or "?"
        engine = sch.get("render_engine") or "?"
        bullets = sch.get("bullets") or []
        narr = (nch.get("narration") or "").strip()

        bullet_lines = "\n".join(f"      - {b}" for b in bullets) or "      (sin bullets)"

        blocks.append(
            f"── CAP {n} ─────────────────────────────────\n"
            f"  role          : {role}\n"
            f"  render_engine : {engine}\n"
            f"  title         : {title}\n"
            f"  bullets       :\n{bullet_lines}\n"
            f"  narración     :\n      {narr}"
        )

    return "\n\n".join(blocks)


def _build_prompt(topic: dict, skeleton: dict, narration: dict) -> str:
    """Construye el prompt Flash del módulo 02."""
    video_title = topic.get("video_title") or "(sin título)"
    angle = topic.get("angle") or "(sin ángulo)"
    canonical = topic.get("canonical_subject_description") or "(sin canonical)"
    summary = topic.get("research_summary") or "(sin summary)"
    facts = topic.get("verified_facts") or []
    facts_block = _format_facts(facts)

    profiles_guide = _format_profiles_guide()
    chapters_block = _format_chapters(skeleton, narration)
    valid_list = ", ".join(sorted(VALID_PROFILES))

    return f"""Eres un director de fotografía. Tu tarea es elegir UN `art_profile`
visual por capítulo de un video documental de 7 capítulos. Cada profile
representa una paleta + óptica cinematográfica concreta.

═══════════════════════════════════════════════════
TEMA
═══════════════════════════════════════════════════
Título  : {video_title}
Ángulo  : {angle}

DESCRIPCIÓN CANÓNICA DEL SUJETO RECURRENTE:
{canonical}

DATOS DUROS (verified_facts):
{facts_block}

CONTEXTO NARRATIVO (research_summary):
{summary}

═══════════════════════════════════════════════════
CATÁLOGO DE 13 PROFILES DISPONIBLES
═══════════════════════════════════════════════════
{profiles_guide}

═══════════════════════════════════════════════════
CAPÍTULOS A ETIQUETAR (skeleton + narración)
═══════════════════════════════════════════════════
{chapters_block}

═══════════════════════════════════════════════════
TU TAREA
═══════════════════════════════════════════════════

Para CADA UNO de los 7 capítulos, elegí EXACTAMENTE 1 `art_profile`
de esta lista (en MAYÚSCULAS, exacto):
  {valid_list}

Y un `rationale` (≤{MAX_RATIONALE_CHARS} chars, español neutro) que
justifique la elección citando elementos visuales concretos de los
bullets/narración/canonical, NO solo del title.

═══════════════════════════════════════════════════
REGLAS INVIOLABLES
═══════════════════════════════════════════════════

1. **Mirá lo que SE VE en la escena**, no lo que dice el title.
   Bullets y narración te dicen qué objetos/lugares aparecen
   visualmente. El title puede ser metafórico ("Pueblo Fantasma")
   pero la escena puede ser DESERT (outback) o INTERIOR (casa
   abandonada con muebles), depende del cap.

2. **HISTORICAL es PRE-INDUSTRIAL únicamente.** Si el topic ocurre
   en siglo XX o XXI (ej: 1968, 1978, 2007), HISTORICAL queda
   PROHIBIDO. Para épocas modernas usá INTERIOR (interiores cálidos)
   o INDUSTRIAL (instalaciones frías).

3. **INDUSTRIAL exige paleta fría.** No la uses para escenas con
   ambiente cálido o ámbar. Si el cap describe maquinaria moderna
   con luz cálida, eso es INTERIOR, no INDUSTRIAL.

4. **SUBMARINE ≠ MARITIME_EXTERIOR.** SUBMARINE es FONDO marino
   (pecios sumergidos, abismo). MARITIME_EXTERIOR es superficie
   (barco zarpando, mar abierto, puerto).

5. **UNDERGROUND ≠ INDUSTRIAL.** Una galería de mina excavada
   es UNDERGROUND (cueva, túnel). Una planta procesadora arriba
   en superficie es INDUSTRIAL (fábrica). Pueden coexistir en el
   mismo topic (caps diferentes).

6. **Caps distintos del mismo topic suelen tener profiles distintos.**
   Es NORMAL y deseable. Un mismo video puede tener caps INTERIOR +
   DESERT + UNDERGROUND + INDUSTRIAL si la narración los justifica.

7. **`art_profile` DEBE estar literal en la lista** (mayúsculas
   exactas). Cualquier valor fuera del catálogo rompe el pipeline.

═══════════════════════════════════════════════════
EJEMPLOS de rationale BIEN vs MAL
═══════════════════════════════════════════════════

✓ BIEN (cita elementos visuales concretos):
  "Cap describe galerías excavadas con polvo de asbesto suspendido
  y linternas — escena subterránea cerrada."

✓ BIEN:
  "Bullets mencionan panel de control del submarino en operación
  con tripulación trabajando — interior técnico iluminado."

✗ MAL (justifica por title, no por escena):
  "Es un cap de hook, así que va INTERIOR."

✗ MAL (justifica con frase genérica):
  "Encaja con el tono del video."

═══════════════════════════════════════════════════
FORMATO DE OUTPUT (JSON estricto, nada más)
═══════════════════════════════════════════════════

{{
  "chapters": [
    {{
      "chapter_number": 1,
      "art_profile": "INTERIOR",
      "rationale": "Cap abre en oficina del médico de los 60s con archivos de pacientes — espacio interior cálido íntimo."
    }},
    {{
      "chapter_number": 2,
      "art_profile": "DESERT",
      "rationale": "..."
    }}
    // ... cap 3-7
  ]
}}

NO agregues texto fuera del JSON. NO uses bloque markdown ```.
"""


# ═══════════════════════════════════════════════════════════════
#  VALIDACIONES
# ═══════════════════════════════════════════════════════════════

class ProfileValidationError(ValueError):
    """Output del Flash no cumple el contrato del módulo 02."""


def _validate_profiles(data: dict) -> None:
    """Valida estructura del output. Raise ProfileValidationError si falla."""
    if not isinstance(data, dict):
        raise ProfileValidationError(f"data no es dict: {type(data).__name__}")

    chapters = data.get("chapters")
    if not isinstance(chapters, list):
        raise ProfileValidationError("falta lista 'chapters'")
    if len(chapters) != EXPECTED_CHAPTER_COUNT:
        raise ProfileValidationError(
            f"se esperaban {EXPECTED_CHAPTER_COUNT} caps, llegaron {len(chapters)}"
        )

    seen_numbers: set[int] = set()
    for i, ch in enumerate(chapters, start=1):
        if not isinstance(ch, dict):
            raise ProfileValidationError(f"cap pos {i} no es dict")

        cn = ch.get("chapter_number")
        if cn != i:
            raise ProfileValidationError(
                f"cap pos {i}: chapter_number={cn} (esperado {i})"
            )
        if cn in seen_numbers:
            raise ProfileValidationError(f"chapter_number {cn} duplicado")
        seen_numbers.add(cn)

        profile = ch.get("art_profile")
        if not isinstance(profile, str):
            raise ProfileValidationError(
                f"cap {i}: art_profile no es string ({type(profile).__name__})"
            )
        profile_norm = profile.strip().upper()
        if profile_norm not in VALID_PROFILES:
            raise ProfileValidationError(
                f"cap {i}: art_profile='{profile}' no está en el catálogo. "
                f"Válidos: {sorted(VALID_PROFILES)}"
            )

        rationale = ch.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ProfileValidationError(f"cap {i}: rationale vacío o no string")
        if len(rationale) > MAX_RATIONALE_CHARS:
            raise ProfileValidationError(
                f"cap {i}: rationale demasiado largo ({len(rationale)} chars, "
                f"máx {MAX_RATIONALE_CHARS})"
            )


def _normalize_chapters(chapters: list) -> list:
    """Normaliza profiles a uppercase y rationale stripped."""
    out = []
    for ch in chapters:
        out.append({
            "chapter_number": ch["chapter_number"],
            "art_profile": ch["art_profile"].strip().upper(),
            "rationale": ch["rationale"].strip(),
        })
    return out


# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA
# ═══════════════════════════════════════════════════════════════

def _persist(topic_id: str, data: dict) -> Path:
    """Escribe data/scripts/_steps/{topic_id}/02_profiles.json."""
    step_dir = STEPS_DIR / topic_id
    step_dir.mkdir(parents=True, exist_ok=True)
    out_file = step_dir / "02_profiles.json"
    out_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_file


# ═══════════════════════════════════════════════════════════════
#  FUNCIÓN PÚBLICA
# ═══════════════════════════════════════════════════════════════

def assign_profiles(topic: dict, skeleton: dict, narration: dict) -> dict:
    """
    Asigna un `art_profile` por cap usando topic + skeleton + narración.

    Args:
        topic     : dict (formato post módulo 00).
        skeleton  : dict {topic_id, chapters[7]} (output del 01a, sin
                    _distribution_plan).
        narration : dict {topic_id, chapters[7] con narration,
                    humanizer_phrases} (output del 01b).

    Returns:
        {
          "topic_id": str,
          "chapters": [
            {chapter_number, art_profile, rationale}, ...   # 7 items
          ]
        }

    Raises:
        ProfileValidationError si Flash devuelve algo fuera de contrato.
        ValueError si el topic no tiene id.
    """
    topic_id = topic.get("id") or topic.get("topic_id")
    if not topic_id:
        raise ValueError("topic sin 'id' ni 'topic_id'")

    # Validación cruzada de inputs (no rompe duro, solo avisa si discrepan)
    skel_chapters = skeleton.get("chapters") or []
    narr_chapters = narration.get("chapters") or []
    if len(skel_chapters) != EXPECTED_CHAPTER_COUNT:
        raise ValueError(
            f"skeleton tiene {len(skel_chapters)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
        )
    if len(narr_chapters) != EXPECTED_CHAPTER_COUNT:
        raise ValueError(
            f"narration tiene {len(narr_chapters)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
        )

    prompt = _build_prompt(topic, skeleton, narration)
    raw = call_flash_json(prompt)

    chapters_raw = raw.get("chapters") or []
    if len(chapters_raw) != EXPECTED_CHAPTER_COUNT:
        raise ProfileValidationError(
            f"Flash devolvió {len(chapters_raw)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
        )

    # Validar antes de normalizar (preserva mensaje de error claro)
    _validate_profiles({"chapters": chapters_raw})
    chapters_norm = _normalize_chapters(chapters_raw)

    output = {
        "topic_id": topic_id,
        "chapters": chapters_norm,
    }

    _persist(topic_id, output)
    return output
