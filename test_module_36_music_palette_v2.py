"""
test_module_36_music_palette_v2.py — TEST paleta musica v2 (chat 36).

Re-genera hook/setup/shock con color ALTO audible (leccion del outro v1).
El outro NO se incluye (ya aprobado en v1).

Salida con sufijo _v2: NO pisa los mp3 v1.

USO:
    python test_module_36_music_palette_v2.py

COSTO: ~$0.80/min. 3 tracks x 30s = ~$1.20.
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

TEST_LENGTH_MS = 30_000          # 30s. 60000 = como produccion.
OUTPUT_DIR = Path("_music_palette_test_chat36")
SUFFIX = "_v2"

# Bed fijo: cello drone grave. + 1 color ALTO que se mueve (arriba de la voz).
NEW_PROMPTS: dict[str, str] = {
    "hook": (
        "Dark cinematic underscore in D minor. A low sustained cello drone "
        "underneath shimmering high violin harmonics that slowly waver and "
        "swell with quiet tension, drawing the listener inward. The high "
        "harmonics stay clearly present and audible. Designed for seamless "
        "background looping under documentary narration. 70 BPM, brooding yet "
        "present, consistent dark intensity throughout."
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
}


def build_test_prompt(base: str) -> str:
    """Replica build_music_prompt() de music_config: positivo + STRICTLY AVOID."""
    negatives = ", ".join(NEGATIVE_GLOBAL_STYLES)
    return f"{base.rstrip('.')}. STRICTLY AVOID: {negatives}."


def generate_one(intent: str, base_prompt: str) -> bool:
    prompt = build_test_prompt(base_prompt)
    print(f"\n--- {intent} ---")
    print(f"  prompt ({len(prompt)} chars): {base_prompt[:80]}...")
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

    out_path = OUTPUT_DIR / f"{intent}_palette_test{SUFFIX}.mp3"
    out_path.write_bytes(mp3_bytes)
    print(f"  [OK] {out_path}  ({len(mp3_bytes) / 1024:.0f}KB, {time.time() - t0:.0f}s)")
    return True


def main() -> int:
    if not getattr(api, "elevenlabs_api_key", None):
        print("[FAIL] no hay elevenlabs_api_key en config.")
        return 1

    OUTPUT_DIR.mkdir(exist_ok=True)
    n = len(NEW_PROMPTS)
    est = n * (TEST_LENGTH_MS / 60000) * 0.80
    print("=" * 60)
    print(f"  TEST paleta musica v2 - {n} tracks x {TEST_LENGTH_MS / 1000:.0f}s")
    print(f"  Costo estimado: ~${est:.2f}")
    print(f"  Output: {OUTPUT_DIR.absolute()} (sufijo {SUFFIX})")
    print(f"  NO toca music_config.py / audio_library / m07")
    print("=" * 60)

    ok = 0
    for i, (intent, base) in enumerate(NEW_PROMPTS.items()):
        if generate_one(intent, base):
            ok += 1
        if i < n - 1:
            time.sleep(2)

    print(f"\n{'PASS' if ok == n else 'PARCIAL'} - {ok}/{n} tracks generados")
    print(f"Escucha los *_v2.mp3 en {OUTPUT_DIR}/ y compara contra los v1.")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
