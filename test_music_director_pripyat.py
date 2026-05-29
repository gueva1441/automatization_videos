"""
test_music_director_pripyat.py

Test profesional del flujo completo de música:

  Narración del cap 1 (Pripyat hook)
        │
        ▼
  Gemini Flash actúa como MUSIC DIRECTOR
        │  (lee narración + narrative_intent + reglas de la doc ElevenLabs)
        ▼
  composition_plan estructurado (JSON con secciones temporales)
        │
        ▼
  ElevenLabs Music API (compose endpoint)
        │
        ▼
  hook_pripyat_v2.mp3

Diferencias vs el test anterior:
- NO usa text prompt simple (que produjo el bug "arranca muy bajo")
- USA composition_plan con secciones temporales precisas
- El LLM razona como productor musical: dónde poner el punch inicial,
  dónde construir tensión, dónde resolver
- Sigue el contrato exacto de la doc oficial ElevenLabs
- Sigue el patrón de gemini_helpers.call_flash_json del proyecto

USO:
    python test_music_director_pripyat.py

REQUISITOS:
- config.py con api.elevenlabs_api_key + cliente Gemini configurado
- Plan ElevenLabs Creator+ (Music API es paid)
- Créditos disponibles (~1,650 por test)
"""

import json
import os
import sys
import time
from pathlib import Path

import requests

# Reusar config del proyecto
try:
    from config import api, gemini_client
    from google.genai import types
    ELEVENLABS_API_KEY = api.elevenlabs_api_key
except ImportError:
    print("❌ No se pudo importar config.py o gemini_client.")
    print("   Asegurate de correr este script desde la raíz del proyecto.")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════
#  INPUT — Narración real del cap 1 (Pripyat hook)
#  Estilo: documentary suspense, validado chat 22.
#  Si tenés la narración real de m01b, reemplazala acá.
# ═══════════════════════════════════════════════════════════════

CAP1_HOOK_NARRATION = (
    "26 de abril de 1986. Una hora y veintitrés minutos de la madrugada. "
    "En la planta nuclear de Chernóbil, alguien presiona el botón AZ-5. "
    "Cuarenta segundos después, una explosión de vapor levanta la losa "
    "de dos mil toneladas del reactor número cuatro. La ciudad de Pripyat, "
    "a tres kilómetros de distancia, sigue durmiendo. Cincuenta mil "
    "personas. Niños, ancianos, familias enteras. Nadie sabe que respiran "
    "una de las nubes más radiactivas de la historia. La evacuación no "
    "llegará hasta treinta y seis horas después. Y lo que ocurrió en "
    "esas horas es peor de lo que el mundo supo durante años."
)

CAP1_DURATION_MS = 60_000  # 60 segundos del cap 1
NARRATIVE_INTENT = "hook"
TOPIC_CONTEXT = (
    "Documentary about the 1986 Chernobyl nuclear disaster and the "
    "abandoned city of Pripyat. Soviet-era setting, dark history, "
    "human tragedy, environmental disaster. Cold and tense atmosphere."
)


# ═══════════════════════════════════════════════════════════════
#  SYSTEM INSTRUCTION para Gemini como MUSIC DIRECTOR
#  Sigue el patrón de gemini_helpers.call_flash_json del proyecto.
#  Inyecta el contrato exacto de composition_plan de ElevenLabs.
# ═══════════════════════════════════════════════════════════════

SYSTEM_INSTRUCTION_MUSIC_DIRECTOR = """You are a senior film music director composing the underscore for a dark history documentary in Spanish about Chernobyl/Pripyat.

Your job: read the chapter narration and emit a JSON composition_plan that ElevenLabs Music will use to generate the underscore. You think like a real composer — you identify dramatic peaks in the narration and design music sections that match those peaks in time.

═══════════════════════════════════════════════════════════════
ELEVENLABS COMPOSITION PLAN CONTRACT (official spec)
═══════════════════════════════════════════════════════════════

Structure:
{
  "positive_global_styles": [string, ...]   // genre, instruments, tempo, key
  "negative_global_styles": [string, ...]   // global prohibitions
  "sections": [
    {
      "section_name": string,                // 1-100 chars, descriptive
      "duration_ms": int,                    // 3000 to 120000 per section
      "positive_local_styles": [string, ...], // max 50, English only
      "negative_local_styles": [string, ...], // max 50, English only
      "lines": []                            // ALWAYS empty for instrumental
    }
  ]
}

HARD CONSTRAINTS:
- Total duration of all sections MUST equal the target duration provided.
- Each section: minimum 3000ms, maximum 120000ms.
- Maximum 30 sections per song.
- All style strings MUST be in English (the model parses English only).
- ALL sections must have lines: [] (instrumental only — no vocals ever).
- NO copyrighted artist names, song titles, or specific copyrighted material.

═══════════════════════════════════════════════════════════════
DOCUMENTARY UNDERSCORE STYLE GUIDE
═══════════════════════════════════════════════════════════════

REQUIRED in positive_global_styles (always include):
- "cinematic documentary underscore"
- "instrumental"
- A specific key like "D minor", "C minor", "A minor" (minor keys for dark)
- A slow tempo like "60 BPM" or "70 BPM"
- Sound palette: pick from "low ominous drone", "sub-bass rumble", "sparse piano", "bowed cello sustains", "ambient string pads", "distant timpani"

REQUIRED in negative_global_styles (always include all):
- "vocals"
- "lyrics"
- "singing"
- "choir"
- "drums"
- "percussion beat"
- "melody hooks"
- "pop structure"
- "EDM"
- "synthwave"
- "electric guitar"
- "happy"
- "uplifting"

SECTION DESIGN BY narrative_intent:

"hook" (cap 1):
  Start with a 3-5s section called "opening_punch":
    - positive: "full intensity drone immediate", "sub-bass hit", "low strings entering at peak volume"
    - negative: "fade-in", "soft start", "build-up", "quiet introduction"
  THIS IS CRITICAL. Hook cannot fade in — must hit at full atmosphere from second 1.
  Then build sections for the rest of the duration that follow the dramatic peaks
  identified in the narration.

"setup" (cap 2):
  Slower, more contemplative. Can fade in subtly. Pacing is calm.
  Sparse piano, ambient pads.

"rising_tension" (cap 3):
  Each subsequent section must escalate intensity. Use "building intensity",
  "tension increasing", "tremolo strings".

"shock" (cap 4 — pattern interrupt at 50% of video):
  One sudden short section (3-5s) called "impact":
    - positive: "sudden timpani hit", "dissonant brass cluster", "dramatic strike"
    - negative: "smooth transition", "build-up"
  Then sustained intensity.

"consequences" (cap 5):
  Melancholic but heavy. Solo piano with reverb, mournful strings.

"resolution" (cap 6):
  Lower intensity. Reflection. Ambient pad with slow piano.

"outro" (cap 7):
  Gentle fade. Single sustained chord. Leave the listener with a question
  hanging. Final section can use "fading out" in positive styles.

═══════════════════════════════════════════════════════════════
HOW TO MAP NARRATION TO SECTIONS
═══════════════════════════════════════════════════════════════

1. Read the full narration.
2. Estimate where the main dramatic peaks land in time, assuming Spanish
   TTS at ~13 chars/second pace.
3. Design sections so that EACH dramatic peak gets its own section with
   matched intensity styles.
4. The first second of audio MUST already be at full atmospheric power
   (this is critical for YouTube hook retention).
5. Section names should describe the dramatic moment, not just be generic
   ("opening_punch", "approaching_shock", "aftermath_reveal", etc.).

═══════════════════════════════════════════════════════════════
OUTPUT FORMAT — STRICT JSON ONLY
═══════════════════════════════════════════════════════════════

Return ONLY a valid JSON object matching the contract above.
No markdown, no comments, no explanations outside the JSON.
The "sections" array's duration_ms values MUST sum to exactly the target_duration_ms.
"""


def build_user_prompt(narration: str, intent: str, duration_ms: int, topic_context: str) -> str:
    """Construye el user prompt para Gemini con la narración real."""
    return f"""TARGET TOTAL DURATION: {duration_ms} ms ({duration_ms / 1000:.0f} seconds)

NARRATIVE INTENT: {intent}

TOPIC CONTEXT:
{topic_context}

CHAPTER NARRATION (Spanish, this is what the audience will HEAR while the music plays):
\"\"\"
{narration}
\"\"\"

Read the narration carefully. Identify the dramatic peaks in time. Design a composition_plan with sections that match those peaks. The total of duration_ms across all sections MUST equal {duration_ms}.

Respond with ONLY the JSON composition_plan. No prose."""


# ═══════════════════════════════════════════════════════════════
#  PASO 1 — Generar composition_plan con Gemini Flash
# ═══════════════════════════════════════════════════════════════

def generate_composition_plan(
    narration: str,
    intent: str,
    duration_ms: int,
    topic_context: str,
) -> dict:
    """Llama Gemini Flash con el system_instruction de music director."""
    user_prompt = build_user_prompt(narration, intent, duration_ms, topic_context)

    print("  [Gemini] Llamando a Flash como music director...")
    t0 = time.time()

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            system_instruction=SYSTEM_INSTRUCTION_MUSIC_DIRECTOR,
        ),
    )

    elapsed = time.time() - t0
    print(f"  [Gemini] Respuesta en {elapsed:.1f}s")

    # Parsear el JSON
    raw_text = response.text.strip()
    try:
        plan = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON inválido de Gemini: {e}")
        print(f"     Raw response (primeros 500 chars):\n{raw_text[:500]}")
        sys.exit(1)

    # Validación dura del schema
    _validate_composition_plan(plan, duration_ms)
    return plan


def _validate_composition_plan(plan: dict, target_duration_ms: int) -> None:
    """Valida que el plan respete el contrato ElevenLabs."""
    required_top = {"positive_global_styles", "negative_global_styles", "sections"}
    missing = required_top - set(plan.keys())
    if missing:
        raise ValueError(f"composition_plan falta keys: {missing}")

    sections = plan["sections"]
    if not isinstance(sections, list) or len(sections) == 0:
        raise ValueError("composition_plan.sections vacío o no es lista")
    if len(sections) > 30:
        raise ValueError(f"Demasiadas secciones ({len(sections)} > 30)")

    total_ms = 0
    for i, sec in enumerate(sections):
        required_sec = {"section_name", "duration_ms", "positive_local_styles",
                        "negative_local_styles", "lines"}
        missing_sec = required_sec - set(sec.keys())
        if missing_sec:
            raise ValueError(f"Sección {i} falta keys: {missing_sec}")

        dur = sec["duration_ms"]
        if not isinstance(dur, int) or dur < 3000 or dur > 120_000:
            raise ValueError(
                f"Sección {i} duration_ms={dur} fuera de rango [3000, 120000]"
            )
        total_ms += dur

    if total_ms != target_duration_ms:
        # Permitir desvío de ±200ms (Gemini puede redondear)
        if abs(total_ms - target_duration_ms) > 200:
            raise ValueError(
                f"Total duración secciones {total_ms}ms ≠ target {target_duration_ms}ms "
                f"(desvío {abs(total_ms - target_duration_ms)}ms)"
            )


# ═══════════════════════════════════════════════════════════════
#  PASO 2 — Generar música con ElevenLabs API
# ═══════════════════════════════════════════════════════════════

def generate_music_from_plan(plan: dict, output_path: Path) -> Path:
    """Llama ElevenLabs Music API con composition_plan."""
    print("  [ElevenLabs] Generando música... (puede tardar 30-90s)")
    t0 = time.time()

    response = requests.post(
        "https://api.elevenlabs.io/v1/music/compose",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "composition_plan": plan,
            "output_format": "mp3_44100_128",
        },
        timeout=300,
    )

    elapsed = time.time() - t0
    print(f"  [ElevenLabs] Respuesta en {elapsed:.1f}s")

    if response.status_code != 200:
        print(f"  ❌ HTTP {response.status_code}")
        print(f"     Body: {response.text[:500]}")
        if response.status_code == 401:
            print("     → API key inválida o sin acceso a Music")
        elif response.status_code == 403:
            print("     → Plan no incluye Music API (necesitás Creator+)")
        elif response.status_code == 422:
            print("     → composition_plan rechazado (bad_composition_plan)")
            print("     → Revisar suggested alternative en el body")
        sys.exit(1)

    output_path.write_bytes(response.content)
    return output_path


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("═" * 70)
    print("  Music Director Test — Pripyat Cap 1 Hook")
    print("═" * 70)
    print()
    print(f"  Narración ({len(CAP1_HOOK_NARRATION)} chars):")
    print(f"    \"{CAP1_HOOK_NARRATION[:100]}...\"")
    print()
    print(f"  Intent:      {NARRATIVE_INTENT}")
    print(f"  Duración:    {CAP1_DURATION_MS / 1000:.0f}s")
    print()

    # ─── Paso 1 — composition_plan via Gemini ───
    print("┌" + "─" * 68 + "┐")
    print("│  PASO 1: Gemini Flash como Music Director                          │")
    print("└" + "─" * 68 + "┘")
    plan = generate_composition_plan(
        narration=CAP1_HOOK_NARRATION,
        intent=NARRATIVE_INTENT,
        duration_ms=CAP1_DURATION_MS,
        topic_context=TOPIC_CONTEXT,
    )

    # Guardar el plan para inspección
    plan_path = Path("hook_pripyat_v2_plan.json")
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✅ composition_plan generado y guardado en {plan_path}")
    print()
    print(f"  Resumen del plan ({len(plan['sections'])} secciones):")
    for i, sec in enumerate(plan["sections"], 1):
        print(f"    {i}. {sec['section_name']:30s} {sec['duration_ms']:>6}ms")
    print()

    # ─── Paso 2 — Música via ElevenLabs ───
    print("┌" + "─" * 68 + "┐")
    print("│  PASO 2: ElevenLabs Music con composition_plan                     │")
    print("└" + "─" * 68 + "┘")
    output_mp3 = Path("hook_pripyat_v2.mp3")
    generate_music_from_plan(plan, output_mp3)
    size_kb = output_mp3.stat().st_size / 1024
    print(f"  ✅ MP3 generado: {output_mp3.absolute()} ({size_kb:.1f} KB)")
    print()

    # ─── Evaluación ───
    print("═" * 70)
    print("  EVALUACIÓN")
    print("═" * 70)
    print(f"  1. Reproducí: {output_mp3.absolute()}")
    print(f"  2. Revisá el plan generado: {plan_path.absolute()}")
    print()
    print("  Preguntas a responder:")
    print("    A. ¿Arranca CON intensidad desde segundo 1? (NO debe haber fade-in)")
    print("    B. ¿Las secciones se sienten distintas o todo es uniforme?")
    print("    C. ¿Hay vocales/melodía/percussion no deseadas?")
    print("    D. ¿La atmósfera matchea Pripyat / dark history?")
    print("    E. ¿Apoya o pelea con la voz del narrador imaginada encima?")
    print()
    print("═" * 70)


if __name__ == "__main__":
    main()
