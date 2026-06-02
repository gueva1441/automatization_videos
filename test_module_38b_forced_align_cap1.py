"""
test_module_38b_forced_align_cap1.py — LAB Video B (chat 37)

OBJETIVO: generar el cap 1 COMPLETO con subtitulos por SILABA usando el
timing REAL del audio que ya existe (ch01.mp3 del Tuskegee), via el
Forced Alignment API de ElevenLabs.

Esto NO regenera el audio. Usa EXACTAMENTE el mismo mp3 que esta en el video
que Omar ya tiene. Lo unico que cambia vs el video real es de donde sale el
timing del subtitulo:
   Video A (real, ya existe) -> timing Whisper (interpola -> "acelerado")
   Video B (este lab)        -> timing Forced Alignment (mide el audio real)

CERO RIESGO: NO toca audio_manager.py, NO toca produccion, NO regenera audio,
NO toca el video real. Todo va a _lab_forcealign_chat37/.

QUE HACE:
  1. Toma el ch01.mp3 REAL del Tuskegee (NO lo regenera)
  2. Lo manda al Forced Alignment API + el texto del cap 1
     -> recibe timing por CARACTER y por PALABRA del audio real
  3. Agrupa caracteres en silabas (timing real)
  4. Construye el .ass por silaba y lo quema sobre fondo negro + el audio real
     -> lab_video_B_silabas.mp4  (cap 1 completo)
  Omar compara este Video B contra su video real (Video A).

USO:
    python test_module_38b_forced_align_cap1.py

COSTO: 1 llamada Forced Alignment sobre ~30s de audio (centavos).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import requests

# ─── Identidad del topic + paths del audio REAL ───
VIDEO_ID = "8286b193-ff82-4357-b32d-21ca30909c4d"
CH01_MP3 = Path("output") / "audio" / VIDEO_ID / "ch01.mp3"

# Texto exacto del cap 1 (del guion final, con acentos correctos).
# Forced Alignment exige STRING PLANO (no JSON).
CAP1_TEXT = (
    "Por 40 años, 600 aparceros sufrieron sífilis no tratada. Hombres como "
    "Charlie Pollard y Herman Shaw. A 399 de ellos, empobrecidos y a menudo "
    "analfabetos, se les mintió. Promesas de \"tratamientos especiales\" "
    "ocultaban un oscuro secreto médico: una cruel observación. Bajo el "
    "diagnóstico falso de \"mala sangre\", se les negó la penicilina, una cura "
    "establecida desde 1943. ¿Quién decidió mantenerlos en las sombras por "
    "décadas?"
)

OUT_DIR = Path("_lab_forcealign_chat37")
VIDEO_W, VIDEO_H = 1080, 1920  # vertical 9:16


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
#  PASO 1 — Forced Alignment sobre el mp3 REAL
# ═══════════════════════════════════════════════════════════════

def step1_forced_alignment(api_key: str) -> dict:
    print(f"\n  [1] Forced Alignment sobre el audio REAL: {CH01_MP3}")
    if not CH01_MP3.exists():
        print(f"  [ERR] No existe {CH01_MP3}")
        print(f"        Confirma el path con: dir output\\audio\\{VIDEO_ID}\\")
        sys.exit(1)

    url = "https://api.elevenlabs.io/v1/forced-alignment"
    with open(CH01_MP3, "rb") as f:
        files = {"file": (CH01_MP3.name, f, "audio/mpeg")}
        data = {"text": CAP1_TEXT}
        resp = requests.post(
            url,
            headers={"xi-api-key": api_key},
            files=files,
            data=data,
            timeout=180,
        )

    if resp.status_code != 200:
        print(f"  [ERR] HTTP {resp.status_code}: {resp.text[:600]}")
        sys.exit(1)

    result = resp.json()
    (OUT_DIR / "lab_B_alignment_raw.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    chars = result.get("characters", [])
    words = result.get("words", [])
    print(f"  [1] OK -> {len(chars)} caracteres, {len(words)} palabras (timing real)")
    return result


# ═══════════════════════════════════════════════════════════════
#  PASO 2 — Caracteres -> silabas (timing real)
# ═══════════════════════════════════════════════════════════════

VOWELS = set("aeiouáéíóúüAEIOUÁÉÍÓÚÜ")


def _chars_to_syllables(chars: list[dict]) -> list[dict]:
    """chars: [{text, start, end}, ...]. Agrupa en silabas aproximadas
    con timing real (start de 1a letra, end de la ultima)."""
    syllables = []
    cur_text = ""
    cur_start = None
    seen_vowel = False

    for i, c in enumerate(chars):
        ch = c.get("text", "")
        st = c.get("start", 0.0)
        en = c.get("end", 0.0)

        if cur_start is None:
            cur_start = st

        if ch == " " or ch in ".,;:!?\"'()¿¡":
            cur_text += ch
            if cur_text.strip():
                syllables.append({"text": cur_text, "start": cur_start, "end": en})
            cur_text = ""
            cur_start = None
            seen_vowel = False
            continue

        is_vowel = ch in VOWELS
        if seen_vowel and not is_vowel:
            nxt = chars[i + 1].get("text", "") if i + 1 < len(chars) else ""
            if nxt and nxt in VOWELS:
                # cortar antes de esta consonante
                if cur_text.strip():
                    syllables.append({
                        "text": cur_text,
                        "start": cur_start,
                        "end": chars[i - 1].get("end", st),
                    })
                cur_text = ""
                cur_start = st
                seen_vowel = False
        cur_text += ch
        if is_vowel:
            seen_vowel = True

    if cur_text.strip():
        syllables.append({
            "text": cur_text,
            "start": cur_start if cur_start is not None else 0.0,
            "end": chars[-1].get("end", 0.0) if chars else 0.0,
        })
    return syllables


# ═══════════════════════════════════════════════════════════════
#  PASO 3 — .ass por silaba + quemar sobre el audio REAL
# ═══════════════════════════════════════════════════════════════

def _fmt(t: float) -> str:
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
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


def build_ass_silabas(syllables: list[dict], path: Path):
    """Muestra una ventana de silabas alrededor de la activa, resaltando
    la silaba que suena con pop + amarillo."""
    events = []
    for idx, syl in enumerate(syllables):
        start = syl["start"]
        end = syl["end"]
        if end <= start:
            end = start + 0.05
        lo = max(0, idx - 3)
        hi = min(len(syllables), idx + 5)
        parts = []
        for j in range(lo, hi):
            txt = syllables[j]["text"].upper().replace("{", "").replace("}", "")
            if j == idx:
                parts.append(
                    r"{\c&H0000FFFF&\fscx118\fscy118"
                    r"\t(0,70,\fscx132\fscy132)\t(70,160,\fscx118\fscy118)}" + txt
                )
            else:
                parts.append(r"{\c&H00FFFFFF&\fscx100\fscy100}" + txt)
        text = "".join(parts)
        events.append(
            f"Dialogue: 0,{_fmt(start)},{_fmt(end)},Viral,,0,0,0,,{text}"
        )
    path.write_text(ASS_HEADER + "\n".join(events) + "\n", encoding="utf-8")


def burn(ass_path: Path, mp3_path: Path, out_path: Path) -> bool:
    ass_str = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    vf = f"subtitles='{ass_str}'"
    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"color=c=black:s={VIDEO_W}x{VIDEO_H}:d=60",
        "-i", str(mp3_path),
        "-vf", vf,
        "-shortest",
        "-c:v", "libx264", "-c:a", "aac",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [ERR] ffmpeg fallo:")
        print(r.stderr[-800:])
        return False
    return True


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    OUT_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print("  LAB Video B — Forced Alignment sobre audio REAL (cap 1)")
    print("=" * 60)

    api_key = _get_api_key()
    result = step1_forced_alignment(api_key)

    chars = result.get("characters", [])
    if not chars:
        print("  [ERR] El alignment no trajo 'characters'. Revisa lab_B_alignment_raw.json")
        sys.exit(1)

    print("\n  [2] Agrupando caracteres en silabas (timing real)...")
    syllables = _chars_to_syllables(chars)
    (OUT_DIR / "lab_B_silabas.json").write_text(
        json.dumps(syllables, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  [2] OK -> {len(syllables)} silabas")

    print("\n  [3] Construyendo subtitulos por silaba + quemando...")
    ass_path = OUT_DIR / "lab_B_subs_silabas.ass"
    build_ass_silabas(syllables, ass_path)
    ok = burn(ass_path, CH01_MP3, OUT_DIR / "lab_video_B_silabas.mp4")

    print("\n" + "=" * 60)
    print("  RESULTADO")
    print("=" * 60)
    print(f"  Carpeta: {OUT_DIR.resolve()}")
    print(f"  lab_video_B_silabas.mp4  (cap 1 completo, audio REAL, subs silaba)  {'OK' if ok else 'FALLO'}")
    print()
    print("  >>> COMPARA contra tu video real (Video A) <<<")
    print("  Mismo audio de Bill en los dos. La unica diferencia es el subtitulo.")
    print("  Pregunta clave: en 'se les mintio' y 'se les nego la' —")
    print("  el Video B va PEGADO a la voz, o sigue acelerado?")
    print("  Si va pegado -> el problema era el subtitulo (Whisper), confirmado.")


if __name__ == "__main__":
    main()
