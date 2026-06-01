"""
test_module_36_hook_v3.py — TEST hook v3 (chat 36).

Solo el hook, con energia de apertura (85 BPM, glockenspiel agudo presente,
inminencia). Genera 2 tomas distintas en una corrida para elegir.

Salida: _music_palette_test_chat36/hook_palette_test_v3_a.mp3 y _v3_b.mp3

USO:
    python test_module_36_hook_v3.py

COSTO: ~$0.80 (2 tomas x 30s).
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
    MUSIC_MODEL_ID,
    MUSIC_OUTPUT_FORMAT,
    MUSIC_REQUEST_TIMEOUT_SEC,
    NEGATIVE_GLOBAL_STYLES,
)

TEST_LENGTH_MS = 30_000
OUTPUT_DIR = Path("_music_palette_test_chat36")

# Formula ganadora del setup (cello + glockenspiel agudo) con energia de apertura.
HOOK_PROMPT = (
    "Dark cinematic underscore in D minor. A low sustained cello drone with "
    "bright glockenspiel notes ringing clearly high above in a tense, insistent "
    "pulse, creating a sense of imminence and pulling the listener in from the "
    "very first second. Present and gripping, not slow or contemplative. "
    "Designed for seamless background looping under documentary narration. "
    "85 BPM, dark and urgent, consistent intensity throughout."
)

# 2 tomas del mismo prompt (ElevenLabs genera distinto cada vez).
TAKES = ["a", "b"]


def build_test_prompt(base: str) -> str:
    negatives = ", ".join(NEGATIVE_GLOBAL_STYLES)
    return f"{base.rstrip('.')}. STRICTLY AVOID: {negatives}."


def generate_one(take: str, base_prompt: str) -> bool:
    prompt = build_test_prompt(base_prompt)
    print(f"\n--- hook toma {take} ---")
    print(f"  POST {MUSIC_API_URL}  ({TEST_LENGTH_MS / 1000:.0f}s)...")

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
                "music_length_ms": TEST_LENGTH_MS,
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

    out_path = OUTPUT_DIR / f"hook_palette_test_v3_{take}.mp3"
    out_path.write_bytes(mp3_bytes)
    print(f"  [OK] {out_path}  ({len(mp3_bytes) / 1024:.0f}KB, {time.time() - t0:.0f}s)")
    return True


def main() -> int:
    if not getattr(api, "elevenlabs_api_key", None):
        print("[FAIL] no hay elevenlabs_api_key en config.")
        return 1

    OUTPUT_DIR.mkdir(exist_ok=True)
    n = len(TAKES)
    est = n * (TEST_LENGTH_MS / 60000) * 0.80
    print("=" * 60)
    print(f"  TEST hook v3 - {n} tomas x {TEST_LENGTH_MS / 1000:.0f}s")
    print(f"  Costo estimado: ~${est:.2f}")
    print(f"  Output: {OUTPUT_DIR.absolute()}")
    print(f"  NO toca music_config.py / audio_library / m07")
    print("=" * 60)

    ok = 0
    for i, take in enumerate(TAKES):
        if generate_one(take, HOOK_PROMPT):
            ok += 1
        if i < n - 1:
            time.sleep(2)

    print(f"\n{'PASS' if ok == n else 'PARCIAL'} - {ok}/{n} tomas generadas")
    print(f"Escucha hook_palette_test_v3_a.mp3 y _v3_b.mp3 y elegi la mejor.")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
