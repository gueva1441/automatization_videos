"""
test_module_38e_voice_ab.py — Lab A/B de voz: Bill vs Adam (solo escuchar).

Genera la MISMA frase con dos voces y los MISMOS settings del perfil activo
(MISTERIO_ABISAL), para que la única variable sea la voz. NO toca producción,
NO pisa audios del Tuskegee, NO regenera alignments, NO corre fase2b.

Output (carpeta gitignoreada): _lab_voice_ab_chat38/voice_bill.mp3 + voice_adam.mp3

USO:
    python test_module_38e_voice_ab.py

COSTO: 2 llamadas TTS de una frase corta = centavos.
"""
import sys
from pathlib import Path

import requests

from config import api
from audio_config import AUDIO_STYLE, ACTIVE_AUDIO_PROFILE

# ── Frase de prueba (swappable: cambiá TEXT y volvé a correr) ──
TEXT = (
    "A cuatrocientos hombres empobrecidos y a menudo analfabetos se les mintió. "
    "Bajo el diagnóstico falso de mala sangre, se les negó la penicilina, una "
    "cura establecida desde hacía años."
)

# ── Voces ──
# Bill: del perfil activo (mismo camino que producción). Sanity esperado: pqHfZKP75CvOlQylNhV4.
BILL_VOICE_ID = AUDIO_STYLE.get("voice_id") or api.elevenlabs_voice_id
# Adam (pre-made): hardcodeado, lo dio Omar.
ADAM_VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# ── Settings IDÉNTICOS para ambas voces (los del perfil activo, sin override de intent) ──
SETTINGS = dict(AUDIO_STYLE["voice_settings"])

# ── Modelo (mismo que producción para español) ──
MODEL_ID = getattr(api, "elevenlabs_model", None) or "eleven_multilingual_v2"

OUTPUT_DIR = Path("_lab_voice_ab_chat38")

VOICES = [
    ("bill", BILL_VOICE_ID),
    ("adam", ADAM_VOICE_ID),
]


def _generate(name: str, voice_id: str) -> bool:
    out_path = OUTPUT_DIR / f"voice_{name}.mp3"
    print(f"\n--- {name} ---")
    print(f"  voice_id : {voice_id}")
    print(f"  settings : {SETTINGS}")
    print(f"  model    : {MODEL_ID}")
    print(f"  POST text-to-speech/{voice_id} ...")
    try:
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": api.elevenlabs_api_key,
                "Content-Type": "application/json",
            },
            json={"text": TEXT, "model_id": MODEL_ID, "voice_settings": SETTINGS},
            timeout=120,
        )
    except Exception as e:
        print(f"  [FAIL] request falló: {type(e).__name__}: {e}")
        return False

    if resp.status_code != 200:
        print(f"  [FAIL] HTTP {resp.status_code}: {resp.text[:400]}")
        return False

    out_path.write_bytes(resp.content)
    kb = len(resp.content) / 1024
    print(f"  [OK] {out_path}  ({kb:.0f} KB)")
    return kb > 1  # sanity: no vacío


def main() -> int:
    if not getattr(api, "elevenlabs_api_key", None):
        print("[FAIL] no hay elevenlabs_api_key en config.")
        return 1

    OUTPUT_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print(f"  A/B de voz — perfil activo: {ACTIVE_AUDIO_PROFILE}")
    print(f"  Settings (IDÉNTICOS para ambas voces): {SETTINGS}")
    print(f"  Modelo: {MODEL_ID}")
    print(f"  Bill voice_id leído del perfil: {BILL_VOICE_ID}")
    if BILL_VOICE_ID != "pqHfZKP75CvOlQylNhV4":
        print(f"  ⚠ OJO: el voice_id de Bill NO es pqHfZKP75CvOlQylNhV4 "
              f"(es {BILL_VOICE_ID}). Usando el del perfil igual.")
    print(f"  Adam voice_id (hardcodeado): {ADAM_VOICE_ID}")
    print("=" * 60)

    ok = 0
    for name, vid in VOICES:
        if _generate(name, vid):
            ok += 1

    print(f"\n{'PASS' if ok == len(VOICES) else 'PARCIAL'} - {ok}/{len(VOICES)} mp3 generados")
    print(f"Escuchá {OUTPUT_DIR}/voice_bill.mp3 y voice_adam.mp3 y decidí de oído.")
    return 0 if ok == len(VOICES) else 1


if __name__ == "__main__":
    sys.exit(main())
