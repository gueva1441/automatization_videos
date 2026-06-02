# test_module_39_shock_lab.py — lab aislado chat 39. NO toca produccion.
import sys, time
from email.parser import BytesParser
from email.policy import default
from pathlib import Path

# Consola Windows cp1252 no encodea ≈ — forzamos UTF-8 en stdout (no toca lógica).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import requests

from config import api
from music_config import (
    MUSIC_API_URL, MUSIC_LENGTH_MS, MUSIC_MODEL_ID,
    MUSIC_OUTPUT_FORMAT, MUSIC_REQUEST_TIMEOUT_SEC, NEGATIVE_GLOBAL_STYLES,
)

TRACK_LENGTH_MS = MUSIC_LENGTH_MS          # 60000 (produccion)
OUTPUT_DIR = Path("_music_shock_lab_chat39")
TAKES = ["a", "b"]

LAB_PROMPTS = {
    "shockA": (
        "Dramatic cinematic underscore in F sharp minor. A heavy low cello "
        "drone holding the foundation, with dissonant tension lifted high "
        "into glassy, screeching violin harmonics ringing far above the "
        "voice, shimmering and unsettling. The low end is dark and weighted, "
        "the midrange left open and uncluttered. Designed for seamless "
        "background looping under documentary narration. 80 BPM, dark and "
        "ominous, consistent intensity throughout."
    ),
    "shockB": (
        "Dramatic cinematic underscore in F sharp minor. A heavy low cello "
        "and double bass drone with a slow swelling sub-bass surge and deep "
        "ominous pressure underneath, with sparse high metallic shimmer "
        "hanging far above. The midrange stays spacious and clear. Dark, "
        "dread-laden intensity. Designed for seamless background looping "
        "under documentary narration. 80 BPM, dark and consistent throughout."
    ),
}

def build_test_prompt(base: str) -> str:
    negatives = ", ".join(NEGATIVE_GLOBAL_STYLES)
    return f"{base.rstrip('.')}. STRICTLY AVOID: {negatives}."

def generate_one(name: str, base: str, take: str) -> bool:
    prompt = build_test_prompt(base)
    print(f"\n--- {name}_{take} ---")
    print(f"  prompt ({len(prompt)} chars): {base[:80]}...")
    print(f"  POST {MUSIC_API_URL}  ({TRACK_LENGTH_MS/1000:.0f}s)...")
    t0 = time.time()
    try:
        resp = requests.post(
            MUSIC_API_URL,
            headers={"xi-api-key": api.elevenlabs_api_key, "Accept": "multipart/mixed"},
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
        print(f"  [FAIL] request: {type(e).__name__}: {e}")
        return False
    if resp.status_code != 200:
        print(f"  [FAIL] HTTP {resp.status_code}: {resp.text[:300]}")
        return False
    raw = f"Content-Type: {resp.headers.get('Content-Type','')}\r\n\r\n".encode() + resp.content
    msg = BytesParser(policy=default).parsebytes(raw)
    mp3 = None
    for part in msg.iter_parts():
        ct = part.get_content_type().lower()
        payload = part.get_payload(decode=True)
        if payload and ("audio" in ct or "mpeg" in ct or "octet" in ct):
            mp3 = payload
    if not mp3:
        print("  [FAIL] no audio en multipart")
        return False
    out = OUTPUT_DIR / f"{name}_{take}.mp3"
    out.write_bytes(mp3)
    print(f"  [OK] {out}  ({len(mp3)/1024:.0f}KB, {time.time()-t0:.0f}s)")
    return True

def main() -> int:
    if not getattr(api, "elevenlabs_api_key", None):
        print("[FAIL] no hay elevenlabs_api_key en config."); return 1
    OUTPUT_DIR.mkdir(exist_ok=True)
    n_calls = len(LAB_PROMPTS) * len(TAKES)
    cost = n_calls * (TRACK_LENGTH_MS/1000/60) * 0.80
    print(f"\n[lab] {n_calls} generaciones de {TRACK_LENGTH_MS/1000:.0f}s "
          f"≈ ${cost:.2f} (ElevenLabs Music ~$0.80/min)")
    ok = 0
    for name, base in LAB_PROMPTS.items():
        for take in TAKES:
            if generate_one(name, base, take):
                ok += 1
            time.sleep(2)
    print(f"\n[lab] {ok}/{n_calls} generados en {OUTPUT_DIR}/")
    return 0 if ok == n_calls else 2

if __name__ == "__main__":
    sys.exit(main())
