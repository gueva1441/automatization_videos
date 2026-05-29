"""
test_elevenlabs_music_hook.py

Test aislado de ElevenLabs Music API para validar calidad antes de
integrar al pipeline (PR 2 chat 23+).

Genera UN track de música tipo HOOK para un documental sobre Pripyat.
Output: hook_pripyat_test.mp3 en el directorio actual.

USO:
    python test_elevenlabs_music_hook.py

REQUISITOS:
- Plan ElevenLabs Creator+ (Music API es paid)
- API key configurada en config.py (la misma del TTS)
- requests instalado (ya viene con el proyecto)
"""

import sys
import time
from pathlib import Path

import requests

# Reusar config del proyecto (misma API key del TTS)
try:
    from config import api
    API_KEY = api.elevenlabs_api_key
except ImportError:
    # Fallback: si corrés esto fuera del proyecto, pegá la key acá
    API_KEY = "TU_API_KEY_AQUI"

# ─── Prompt de prueba — HOOK para documentary Pripyat ───
MUSIC_PROMPT = (
    "Cinematic dark documentary underscore at full intensity from "
    "the very first second. Strong low ominous drone in D minor at "
    "maximum sustained level immediately, distinct piano notes with "
    "long reverb appearing every 3-4 seconds, deep sub-bass rumble "
    "present throughout, bowed cello sustains layered underneath. "
    "NO slow build, NO fade-in, NO quiet introduction. The atmosphere "
    "must hit at full power from second 1 and stay sustained. "
    "Tense and contemplative. No vocals, no melody hooks, no rhythm, "
    "no percussion, no drums."
)

# Duración del track — 60 segundos para test rápido
DURATION_MS = 60_000  # 60 segundos

# Output settings
OUTPUT_FILE = Path("hook_pripyat_test.mp3")
OUTPUT_FORMAT = "mp3_44100_128"  # MP3 44.1kHz 128kbps

# Endpoint
URL = "https://api.elevenlabs.io/v1/music/compose"


def main():
    print("═" * 60)
    print("  ElevenLabs Music API — Test HOOK Pripyat")
    print("═" * 60)
    print()
    print(f"  Prompt ({len(MUSIC_PROMPT)} chars):")
    print(f"  {MUSIC_PROMPT[:100]}...")
    print()
    print(f"  Duración: {DURATION_MS / 1000:.0f}s")
    print(f"  Formato:  {OUTPUT_FORMAT}")
    print(f"  Output:   {OUTPUT_FILE.absolute()}")
    print()

    if not API_KEY or API_KEY == "TU_API_KEY_AQUI":
        print("  ❌ ERROR: API key no configurada.")
        print("     Pegá tu key en la constante API_KEY o configurá config.py")
        sys.exit(1)

    print("  Generando música... (puede tardar 30-90s)")
    t0 = time.time()

    try:
        response = requests.post(
            URL,
            headers={
                "xi-api-key": API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "prompt": MUSIC_PROMPT,
                "music_length_ms": DURATION_MS,
                "output_format": OUTPUT_FORMAT,
            },
            timeout=300,  # 5 min timeout (Music puede tardar)
        )
    except requests.exceptions.Timeout:
        print("  ❌ Timeout — el servidor tardó más de 5 minutos.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error de red: {e}")
        sys.exit(1)

    elapsed = time.time() - t0
    print(f"  Respuesta recibida en {elapsed:.1f}s")
    print()

    if response.status_code != 200:
        print(f"  ❌ ERROR HTTP {response.status_code}")
        print(f"     Body: {response.text[:500]}")

        # Errores comunes
        if response.status_code == 401:
            print("     → API key inválida o no autorizada para Music")
        elif response.status_code == 403:
            print("     → Plan no incluye Music API (necesitás Creator+)")
        elif response.status_code == 422:
            print("     → Prompt rechazado por contenido (bad_prompt error)")
        sys.exit(1)

    # Guardar el MP3
    OUTPUT_FILE.write_bytes(response.content)
    size_kb = len(response.content) / 1024

    print(f"  ✅ Listo. {size_kb:.1f} KB guardados en:")
    print(f"     {OUTPUT_FILE.absolute()}")
    print()
    print("  Reproducí el archivo y evaluá:")
    print("    1. ¿Suena cinematográfico documentary?")
    print("    2. ¿Hay vocales/melodía/percussion no deseadas?")
    print("    3. ¿La atmósfera matchea Pripyat / dark history?")
    print("    4. ¿Apoya o distrae de un narrador encima?")
    print()
    print("═" * 60)


if __name__ == "__main__":
    main()
