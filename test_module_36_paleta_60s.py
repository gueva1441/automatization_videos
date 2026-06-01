"""
test_module_36_paleta_60s.py — Regenera los 4 ganadores a 60s (chat 36).

Prompts EXACTOS de los takes aprobados (hook v3, setup v2, shock v2, outro v1).
2 tomas por intent (ElevenLabs genera distinto cada vez) para elegir.

Salida: _music_palette_test_chat36/<intent>_60s_<a|b>.mp3 (no pisa los 30s).

USO:
    python test_module_36_paleta_60s.py

COSTO: 8 tracks x 60s x ~$0.80/min = ~$6.40.
"""
import sys
import time
from email.parser import BytesParser
from email.policy import default
from pathlib import Path

import requests

from config import api
from music_config import (
    MUSIC_API_URL,
    MUSIC_LENGTH_MS,
    MUSIC_MODEL_ID,
    MUSIC_OUTPUT_FORMAT,
    MUSIC_REQUEST_TIMEOUT_SEC,
    NEGATIVE_GLOBAL_STYLES,
)

# Largo de PRODUCCION (60s). Sale de music_config para que sea fiel.
TRACK_LENGTH_MS = MUSIC_LENGTH_MS   # 60000
OUTPUT_DIR = Path("_music_palette_test_chat36")
TAKES = ["a", "b"]                  # 2 tomas por intent. Poner ["a"] para 1 sola.

# Prompts EXACTOS de los takes aprobados.
PROMPTS: dict[str, str] = {
    "hook": (
        "Dark cinematic underscore in D minor. A low sustained cello drone with "
        "bright glockenspiel notes ringing clearly high above in a tense, "
        "insistent pulse, creating a sense of imminence and pulling the listener "
        "in from the very first second. Present and gripping, not slow or "
        "contemplative. Designed for seamless background looping under "
        "documentary narration. 85 BPM, dark and urgent, consistent intensity "
        "throughout."
    ),
    "setup": (
        "Slow cinematic underscore in D minor. A patient low cello drone with "
        "sparse, distant glockenspiel notes ringing high above at long "
        "intervals, clearly audible against the dark bed. Dark mystery "
        "atmosphere with quiet ominous tension and a sense of space. Designed "
        "for seamless background looping under documentary narration. 65 BPM, "
        "brooding and spacious, consistent dark depth throughout."
    ),
    "shock": (
        "Dramatic cinematic underscore in F sharp minor. A heavy low cello "
        "drone beneath a high dissonant string cluster in violins and violas, "
        "screeching and unsettling in the upper register, cutting clearly "
        "through. Dark ominous intensity. Designed for seamless background "
        "looping under documentary narration. 80 BPM, dark and consistent "
        "throughout."
    ),
    "outro": (
        "Fading cinematic underscore in D minor. Sustained low cello receding "
        "into the distance, with a slow descending harp glissando shimmering "
        "high above. Dark mystery atmosphere with lingering unease that refuses "
        "to resolve. Designed for seamless background looping under documentary "
        "narration. 60 BPM, brooding and haunting, consistent dark throughout."
    ),
}


def build_test_prompt(base: str) -> str:
    negatives = ", ".join(NEGATIVE_GLOBAL_STYLES)
    return f"{base.rstrip('.')}. STRICTLY AVOID: {negatives}."


def generate_one(intent: str, take: str, base_prompt: str) -> bool:
    prompt = build_test_prompt(base_prompt)
    print(f"\n--- {intent} toma {take} ({TRACK_LENGTH_MS / 1000:.0f}s) ---")
    print(f"  POST {MUSIC_API_URL} ...")

    t0 = time.time()
    try:
        resp = requests.post(
            MUSIC_API_URL,
            headers={
                "xi-api-key": api.elevenlabs_api_key,
                "Accept": "multipart/mixed",
            },
            json={
                "prompt": prompt,
                "music_length_ms": TRACK_LENGTH_MS,
                "model_id": MUSIC_MODEL_ID,
                "output_format": MUSIC_OUTPUT_FORMAT,
                "force_instrumental": True,
            },
            timeout=MUSIC_REQUEST_TIMEOUT_SEC,
        )
    except Exception as e:
        print(f"  [FAIL] request fallo: {type(e).__name__}: {e}")
        return False

    if resp.status_code != 200:
        print(f"  [FAIL] HTTP {resp.status_code}: {resp.text[:300]}")
        return False

    content_type = resp.headers.get("Content-Type", "")
    raw = f"Content-Type: {content_type}\r\n\r\n".encode() + resp.content
    msg = BytesParser(policy=default).parsebytes(raw)

    mp3_bytes = None
    for part in msg.iter_parts():
        ct = part.get_content_type().lower()
        payload = part.get_payload(decode=True)
        if payload and ("audio" in ct or "mpeg" in ct or "octet" in ct):
            mp3_bytes = payload

    if not mp3_bytes:
        print("  [FAIL] no se encontro audio en el multipart")
        return False

    out_path = OUTPUT_DIR / f"{intent}_60s_{take}.mp3"
    out_path.write_bytes(mp3_bytes)
    print(f"  [OK] {out_path}  ({len(mp3_bytes) / 1024:.0f}KB, {time.time() - t0:.0f}s)")
    return True


def main() -> int:
    if not getattr(api, "elevenlabs_api_key", None):
        print("[FAIL] no hay elevenlabs_api_key en config.")
        return 1

    OUTPUT_DIR.mkdir(exist_ok=True)
    total = len(PROMPTS) * len(TAKES)
    est = total * (TRACK_LENGTH_MS / 60000) * 0.80
    print("=" * 60)
    print(f"  Regen paleta a {TRACK_LENGTH_MS / 1000:.0f}s - {total} tracks "
          f"({len(PROMPTS)} intents x {len(TAKES)} tomas)")
    print(f"  Costo estimado: ~${est:.2f}")
    print(f"  Output: {OUTPUT_DIR.absolute()}")
    print(f"  NO toca music_config.py / audio_library / m07")
    print("=" * 60)

    ok = 0
    items = [(intent, take) for intent in PROMPTS for take in TAKES]
    for i, (intent, take) in enumerate(items):
        if generate_one(intent, take, PROMPTS[intent]):
            ok += 1
        if i < len(items) - 1:
            time.sleep(2)

    print(f"\n{'PASS' if ok == total else 'PARCIAL'} - {ok}/{total} tracks generados")
    print(f"Escucha los *_60s_*.mp3 en {OUTPUT_DIR}/ y elegi 1 por intent.")
    print(f"Foco: que el setup_60s se parezca al setup_v2 que te gusto.")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
