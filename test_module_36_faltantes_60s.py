"""
test_module_36_faltantes_60s.py — Los 3 intents faltantes a 60s (chat 36).

rising_tension / consequences / resolution. Misma formula que los 4 aprobados:
cello grave de bed + 1 color ALTO que se mueve. 2 tomas por intent.

Salida: _music_palette_test_chat36/<intent>_60s_<a|b>.mp3

USO:
    python test_module_36_faltantes_60s.py

COSTO: 6 tracks x 60s x ~$0.80/min = ~$4.80.
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

TRACK_LENGTH_MS = MUSIC_LENGTH_MS   # 60000 (largo de produccion)
OUTPUT_DIR = Path("_music_palette_test_chat36")
TAKES = ["a", "b"]                  # 2 tomas por intent. ["a"] para 1 sola.

PROMPTS: dict[str, str] = {
    "rising_tension": (
        "Building cinematic underscore in G sharp minor. A low sustained cello "
        "drone beneath high tremolo strings in viola and violin that slowly "
        "rise and intensify, clearly audible up high, mounting unease that "
        "pushes forward and refuses to settle. Designed for seamless background "
        "looping under documentary narration. 78 BPM, dark and steadily "
        "tightening, consistent intensity throughout."
    ),
    "consequences": (
        "Heavy cinematic underscore in D minor. A deep low cello drone with "
        "slow, spaced glockenspiel notes ringing high above, sparse and "
        "weighted, carrying a sense of crushing gravity and loss. Clearly "
        "audible high notes against the dark bed. Designed for seamless "
        "background looping under documentary narration. 60 BPM, brooding and "
        "heavy, consistent dark depth throughout."
    ),
    "resolution": (
        "Lingering cinematic underscore in D minor. A low sustained cello drone "
        "under high sustained string harmonics that hang unresolved, shimmering "
        "and clearly audible above, an open question that never fully releases. "
        "Designed for seamless background looping under documentary narration. "
        "62 BPM, brooding and suspended, consistent quiet tension throughout."
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
    print(f"  Faltantes a {TRACK_LENGTH_MS / 1000:.0f}s - {total} tracks "
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
    print(f"Escucha los *_60s_*.mp3 nuevos y elegi 1 por intent.")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
