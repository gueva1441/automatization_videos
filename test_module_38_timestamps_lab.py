"""
test_module_38_timestamps_lab.py — LABORATORIO standalone (chat 37)

Compara el timing de subtitulos entre:
  A) WHISPER (lo que usa produccion hoy, via _force_align_to_script)
  B) ELEVENLABS /with-timestamps (char-level, timing real del TTS)

Sobre la MISMA oracion del cap 1 del Tuskegee (0:12-0:25 aprox), que es donde
Omar escucha el "Bill acelerado" = sintoma de la interpolacion uniforme del
forced alignment.

CERO RIESGO: NO importa ni toca audio_manager.py, NO toca produccion, NO toca
audio_library/, NO toca el video. Todo va a _lab_timestamps_chat37/.

QUE HACE:
  1. Manda la oracion a ElevenLabs /with-timestamps con Bill + settings del cap1
     -> guarda lab_eleven.mp3 + lab_eleven_alignment.json (char-level)
  2. Corre Whisper sobre ESE MISMO mp3 -> lab_whisper_words.json (palabra)
  3. Construye 2 archivos .ass:
       - lab_subs_whisper.ass   (timing Whisper, por PALABRA, como hoy)
       - lab_subs_silabas.ass   (timing ElevenLabs, por SILABA, lo nuevo)
  4. Quema cada .ass sobre fondo negro -> 2 videitos cortos:
       - lab_video_whisper.mp4
       - lab_video_silabas.mp4
  Omar mira los dos lado a lado y JUZGA con su oido/ojo (gate humano).

USO:
    python test_module_38_timestamps_lab.py

REQUISITOS: requests, faster-whisper (ya instalado), ffmpeg (ya en winget).
COSTO: ~1 llamada TTS de <300 chars (centavos). Cero music, cero Flux/Veo.
"""
from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import requests

# ─── Config tomada de produccion (NO se importa audio_manager) ───
# Bill, profile MISTERIO_ABISAL, settings del intent "hook" (cap 1)
VOICE_ID = "pqHfZKP75CvOlQylNhV4"  # Bill
MODEL_ID = "eleven_multilingual_v2"  # mismo modelo que soporta timestamps
VOICE_SETTINGS = {
    "stability": 0.50,          # hook override (chat 24)
    "similarity_boost": 0.8,    # profile MISTERIO_ABISAL
    "style": 0.40,              # hook override
    "use_speaker_boost": True,
}

# La oracion exacta del cap 1 donde Omar escucha el problema (0:12-0:25).
# Tomada del texto real, sin nombres propios problematicos para comparar limpio.
SENTENCE = (
    "se les mintio. Promesas de \"tratamientos especiales\" ocultaban un oscuro "
    "secreto medico: una cruel observacion. Bajo el diagnostico falso de "
    "\"mala sangre\", se les nego la penicilina."
)

OUT_DIR = Path("_lab_timestamps_chat37")
VIDEO_W, VIDEO_H = 1080, 1920  # vertical 9:16, igual que produccion

# ─── API key: la leemos de config sin importar audio_manager ───
def _get_api_key() -> str:
    try:
        from config import api
        return api.elevenlabs_api_key
    except Exception as e:
        print(f"  [ERR] No pude leer la api key de config: {e}")
        sys.exit(1)


def _find_ffmpeg(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    winget_base = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if winget_base.exists():
        for pkg_dir in winget_base.glob("Gyan.FFmpeg_*"):
            matches = list(pkg_dir.glob(f"ffmpeg-*/bin/{name}.exe"))
            if matches:
                return str(matches[0])
    print(f"  [ERR] No encontre {name}")
    sys.exit(1)


FFMPEG = _find_ffmpeg("ffmpeg")


# ═══════════════════════════════════════════════════════════════
#  PASO 1 — ElevenLabs with-timestamps
# ═══════════════════════════════════════════════════════════════

def step1_eleven_with_timestamps(api_key: str) -> dict:
    print("\n  [1] Llamando ElevenLabs /with-timestamps (Bill)...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"
    resp = requests.post(
        url,
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={
            "text": SENTENCE,
            "model_id": MODEL_ID,
            "voice_settings": VOICE_SETTINGS,
        },
        timeout=120,
    )
    if resp.status_code != 200:
        print(f"  [ERR] HTTP {resp.status_code}: {resp.text[:500]}")
        sys.exit(1)

    data = resp.json()
    # Guardar mp3
    mp3_bytes = base64.b64decode(data["audio_base64"])
    mp3_path = OUT_DIR / "lab_eleven.mp3"
    mp3_path.write_bytes(mp3_bytes)
    # Guardar alignment crudo
    (OUT_DIR / "lab_eleven_alignment.json").write_text(
        json.dumps(data.get("alignment"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  [1] OK -> lab_eleven.mp3 + lab_eleven_alignment.json")
    n_chars = len(data["alignment"]["characters"])
    print(f"      alignment: {n_chars} caracteres con timing real del TTS")
    return data["alignment"]


# ═══════════════════════════════════════════════════════════════
#  PASO 2 — Whisper sobre el MISMO mp3 (como produccion)
# ═══════════════════════════════════════════════════════════════

def step2_whisper(mp3_path: Path) -> list[dict]:
    print("\n  [2] Transcribiendo con Whisper (mismo mp3)...")
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(mp3_path), language="es", word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words:
            t = w.word.strip()
            if t:
                words.append({"word": t, "start": float(w.start), "end": float(w.end)})
    (OUT_DIR / "lab_whisper_words.json").write_text(
        json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  [2] OK -> lab_whisper_words.json ({len(words)} palabras)")
    return words


# ═══════════════════════════════════════════════════════════════
#  PASO 3 — Char alignment -> SILABAS (agrupado real)
# ═══════════════════════════════════════════════════════════════

# Silabeador simple del espanol: agrupa caracteres por nucleos vocalicos.
# No es perfecto (no maneja todos los diptongos/hiatos), pero el timing es
# REAL (viene del TTS), que es lo que queremos demostrar.
VOWELS = set("aeiouaeiouuAEIOUAEIOUU")

def _chars_to_syllable_chunks(alignment: dict) -> list[dict]:
    """Agrupa los caracteres del alignment en silabas aproximadas con su
    timing real (start de la 1a letra, end de la ultima)."""
    chars = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]

    syllables = []
    cur_text = ""
    cur_start = None
    seen_vowel = False

    def flush():
        nonlocal cur_text, cur_start, seen_vowel
        if cur_text.strip():
            syllables.append({
                "text": cur_text,
                "start": cur_start,
                "end": ends[i - 1],
            })
        cur_text = ""
        cur_start = None
        seen_vowel = False

    for i, ch in enumerate(chars):
        if cur_start is None:
            cur_start = starts[i]
        # corte de silaba: espacio o puntuacion siempre rompe
        if ch == " " or ch in ".,;:!?\"'()":
            cur_text += ch
            flush()
            continue
        is_vowel = ch in VOWELS
        # si ya vimos vocal y aparece consonante seguida de otra vocal -> nueva silaba
        if seen_vowel and not is_vowel:
            # mirar siguiente: si lo que viene es vocal, cortamos antes de esta consonante
            nxt = chars[i + 1] if i + 1 < len(chars) else ""
            if nxt and nxt in VOWELS:
                flush()
                cur_start = starts[i]
        cur_text += ch
        if is_vowel:
            seen_vowel = True
    # ultimo
    if cur_text.strip():
        syllables.append({"text": cur_text, "start": cur_start, "end": ends[-1]})
    return syllables


# ═══════════════════════════════════════════════════════════════
#  PASO 4 — Construir .ass y quemar
# ═══════════════════════════════════════════════════════════════

def _fmt_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"


ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {VIDEO_W}
PlayResY: {VIDEO_H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Arial,100,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,4,2,40,40,640,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_ass_whisper(words: list[dict], path: Path):
    """Karaoke por PALABRA con timing Whisper, chunks de 3 (como produccion)."""
    events = []
    # chunk de a 3
    chunks = [words[i:i + 3] for i in range(0, len(words), 3)]
    for chunk in chunks:
        for idx, w in enumerate(chunk):
            start = w["start"]
            end = w["end"]
            parts = []
            for j, ww in enumerate(chunk):
                txt = ww["word"].upper().replace("{", "").replace("}", "")
                if j == idx:
                    parts.append(r"{\c&H0000FFFF&\fscx115\fscy115}" + txt)
                else:
                    parts.append(r"{\c&H00FFFFFF&\fscx100\fscy100}" + txt)
            text = " ".join(parts)
            events.append(
                f"Dialogue: 0,{_fmt_time(start)},{_fmt_time(end)},Viral,,0,0,0,,{text}"
            )
    path.write_text(ASS_HEADER + "\n".join(events) + "\n", encoding="utf-8")


def build_ass_silabas(syllables: list[dict], path: Path):
    """Karaoke por SILABA con timing real ElevenLabs. Muestra la palabra
    completa y resalta la silaba activa."""
    events = []
    for idx, syl in enumerate(syllables):
        start = syl["start"]
        end = syl["end"]
        if end <= start:
            end = start + 0.05
        # ventana: silaba actual + las 5 de alrededor para dar contexto
        lo = max(0, idx - 2)
        hi = min(len(syllables), idx + 4)
        parts = []
        for j in range(lo, hi):
            txt = syllables[j]["text"].upper().replace("{", "").replace("}", "")
            if j == idx:
                parts.append(r"{\c&H0000FFFF&\fscx120\fscy120}" + txt)
            else:
                parts.append(r"{\c&H00FFFFFF&\fscx100\fscy100}" + txt)
        text = "".join(parts)
        events.append(
            f"Dialogue: 0,{_fmt_time(start)},{_fmt_time(end)},Viral,,0,0,0,,{text}"
        )
    path.write_text(ASS_HEADER + "\n".join(events) + "\n", encoding="utf-8")


def burn(ass_path: Path, mp3_path: Path, out_path: Path):
    """Quema el .ass sobre fondo negro + el audio de Bill."""
    # ruta ass para ffmpeg en windows necesita escape de :
    ass_str = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    vf = f"subtitles='{ass_str}'"
    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"color=c=black:s={VIDEO_W}x{VIDEO_H}:d=30",
        "-i", str(mp3_path),
        "-vf", vf,
        "-shortest",
        "-c:v", "libx264", "-c:a", "aac",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [ERR] ffmpeg fallo en {out_path.name}:")
        print(r.stderr[-800:])
        return False
    return True


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    OUT_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print("  LAB chat 37 — Whisper vs ElevenLabs char-level timestamps")
    print("=" * 60)
    print(f"  Oracion cobaya (cap 1, 0:12-0:25):")
    print(f"    {SENTENCE[:70]}...")

    api_key = _get_api_key()

    # 1. ElevenLabs with-timestamps
    alignment = step1_eleven_with_timestamps(api_key)
    mp3_path = OUT_DIR / "lab_eleven.mp3"

    # 2. Whisper sobre el mismo mp3
    whisper_words = step2_whisper(mp3_path)

    # 3. Silabas desde char alignment
    print("\n  [3] Agrupando caracteres en silabas (timing real)...")
    syllables = _chars_to_syllable_chunks(alignment)
    (OUT_DIR / "lab_silabas.json").write_text(
        json.dumps(syllables, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  [3] OK -> lab_silabas.json ({len(syllables)} silabas)")

    # 4. Construir .ass y quemar
    print("\n  [4] Construyendo subtitulos y quemando videos...")
    ass_w = OUT_DIR / "lab_subs_whisper.ass"
    ass_s = OUT_DIR / "lab_subs_silabas.ass"
    build_ass_whisper(whisper_words, ass_w)
    build_ass_silabas(syllables, ass_s)

    ok_w = burn(ass_w, mp3_path, OUT_DIR / "lab_video_whisper.mp4")
    ok_s = burn(ass_s, mp3_path, OUT_DIR / "lab_video_silabas.mp4")

    print("\n" + "=" * 60)
    print("  RESULTADO")
    print("=" * 60)
    print(f"  Carpeta: {OUT_DIR.resolve()}")
    print(f"  lab_video_whisper.mp4  (timing actual, por palabra)  {'OK' if ok_w else 'FALLO'}")
    print(f"  lab_video_silabas.mp4  (timing nuevo, por silaba)    {'OK' if ok_s else 'FALLO'}")
    print()
    print("  >>> MIRA LOS DOS VIDEOS LADO A LADO <<<")
    print("  El gate es TUYO: cual va mas pegado a la voz de Bill?")
    print("  Fijate sobre todo en 'se les mintio' y 'se les nego la' —")
    print("  ahi es donde el de Whisper va mecanico/acelerado.")


if __name__ == "__main__":
    main()
