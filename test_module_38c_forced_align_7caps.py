"""
test_module_38c_forced_align_7caps.py — LAB validacion 7 caps (chat 37)

Valida el Forced Alignment de ElevenLabs sobre LOS 7 CAPITULOS reales del
Tuskegee. Usa los chXX.mp3 que YA existen (NO regenera audio, NO toca voz).

OBJETIVO: confirmar que el alignment se porta bien en TODA la narracion, no
solo el cap 1, antes de disenar el handoff de produccion.

CERO RIESGO: NO toca audio_manager.py, NO regenera audio, NO toca produccion.
Todo va a _lab_forcealign_7caps_chat37/.

POR CADA CAP:
  1. Manda chXX.mp3 real + su texto (del guion final) al Forced Alignment
  2. Valida el JSON:
       - trajo characters + words?
       - loss (confianza): mas bajo = mejor
       - timestamps monotonos crecientes (sin saltos raros)?
       - primera/ultima palabra dentro de la duracion del audio?
  3. Agrupa caracteres en silabas (timing real) y quema el video completo
       -> lab_cap0X_silabas.mp4  (audio real + subs alineados)

AL FINAL: tabla resumen con PASS/WARN por cap.

USO:
    python test_module_38c_forced_align_7caps.py
    python test_module_38c_forced_align_7caps.py --no-video   # solo validar JSON, sin quemar

COSTO: 7 llamadas Forced Alignment sobre los 7 audios (centavos c/u).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import requests

VIDEO_ID = "8286b193-ff82-4357-b32d-21ca30909c4d"
SCRIPT_PATH = Path("data") / "scripts" / f"{VIDEO_ID}.json"
AUDIO_DIR = Path("output") / "audio" / VIDEO_ID
OUT_DIR = Path("_lab_forcealign_7caps_chat37")
VIDEO_W, VIDEO_H = 1080, 1920


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


def _get_ffprobe_duration(mp3: Path) -> float:
    ffprobe = _find_ffmpeg("ffprobe")
    r = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(mp3)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return 0.0


FFMPEG = _find_ffmpeg("ffmpeg")
VOWELS = set("aeiouáéíóúüAEIOUÁÉÍÓÚÜ")


# ═══════════════════════════════════════════════════════════════
#  Forced Alignment
# ═══════════════════════════════════════════════════════════════

def forced_align(api_key: str, mp3: Path, text: str) -> dict | None:
    url = "https://api.elevenlabs.io/v1/forced-alignment"
    with open(mp3, "rb") as f:
        files = {"file": (mp3.name, f, "audio/mpeg")}
        data = {"text": text}
        resp = requests.post(
            url, headers={"xi-api-key": api_key},
            files=files, data=data, timeout=180,
        )
    if resp.status_code != 200:
        print(f"      [ERR] HTTP {resp.status_code}: {resp.text[:300]}")
        return None
    return resp.json()


# ═══════════════════════════════════════════════════════════════
#  Validacion del JSON
# ═══════════════════════════════════════════════════════════════

def validate_alignment(result: dict, audio_dur: float) -> dict:
    """Devuelve dict con checks y un veredicto PASS/WARN/FAIL."""
    chars = result.get("characters", [])
    words = result.get("words", [])
    loss = result.get("loss")

    checks = {}
    checks["has_characters"] = len(chars) > 0
    checks["has_words"] = len(words) > 0
    checks["loss"] = loss

    # Monotonia: cada start >= start anterior
    monotonic = True
    prev = -1.0
    for w in words:
        s = w.get("start", 0.0)
        if s < prev - 0.01:  # tolerancia minima
            monotonic = False
            break
        prev = s
    checks["monotonic"] = monotonic

    # Cobertura: ultima palabra termina dentro de la duracion (con margen)
    last_end = words[-1].get("end", 0.0) if words else 0.0
    checks["last_end"] = round(last_end, 2)
    checks["audio_dur"] = round(audio_dur, 2)
    checks["coverage_ok"] = (last_end <= audio_dur + 0.5) and (last_end >= audio_dur - 3.0)

    # Veredicto
    if not (checks["has_characters"] and checks["has_words"] and monotonic):
        verdict = "FAIL"
    elif not checks["coverage_ok"]:
        verdict = "WARN"
    else:
        verdict = "PASS"
    checks["verdict"] = verdict
    return checks


# ═══════════════════════════════════════════════════════════════
#  Silabas + render
# ═══════════════════════════════════════════════════════════════

def chars_to_syllables(chars: list[dict]) -> list[dict]:
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
        if ch == " " or ch in ".,;:!?\"'()¿?¡":
            cur_text += ch
            if cur_text.strip():
                syllables.append({"text": cur_text, "start": cur_start, "end": en})
            cur_text = ""; cur_start = None; seen_vowel = False
            continue
        is_vowel = ch in VOWELS
        if seen_vowel and not is_vowel:
            nxt = chars[i + 1].get("text", "") if i + 1 < len(chars) else ""
            if nxt and nxt in VOWELS:
                if cur_text.strip():
                    syllables.append({"text": cur_text, "start": cur_start,
                                      "end": chars[i - 1].get("end", st)})
                cur_text = ""; cur_start = st; seen_vowel = False
        cur_text += ch
        if is_vowel:
            seen_vowel = True
    if cur_text.strip():
        syllables.append({"text": cur_text,
                          "start": cur_start if cur_start is not None else 0.0,
                          "end": chars[-1].get("end", 0.0) if chars else 0.0})
    return syllables


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


def build_ass(syllables: list[dict], path: Path):
    events = []
    for idx, syl in enumerate(syllables):
        start = syl["start"]; end = syl["end"]
        if end <= start:
            end = start + 0.05
        lo = max(0, idx - 3); hi = min(len(syllables), idx + 5)
        parts = []
        for j in range(lo, hi):
            txt = syllables[j]["text"].upper().replace("{", "").replace("}", "")
            if j == idx:
                parts.append(r"{\c&H0000FFFF&\fscx118\fscy118"
                             r"\t(0,70,\fscx132\fscy132)\t(70,160,\fscx118\fscy118)}" + txt)
            else:
                parts.append(r"{\c&H00FFFFFF&\fscx100\fscy100}" + txt)
        events.append(f"Dialogue: 0,{_fmt(start)},{_fmt(end)},Viral,,0,0,0,,{''.join(parts)}")
    path.write_text(ASS_HEADER + "\n".join(events) + "\n", encoding="utf-8")


def burn(ass_path: Path, mp3: Path, out: Path) -> bool:
    ass_str = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    cmd = [FFMPEG, "-y",
           "-f", "lavfi", "-i", f"color=c=black:s={VIDEO_W}x{VIDEO_H}:d=120",
           "-i", str(mp3), "-vf", f"subtitles='{ass_str}'",
           "-shortest", "-c:v", "libx264", "-c:a", "aac", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"      [ERR] ffmpeg: {r.stderr[-400:]}")
        return False
    return True


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-video", action="store_true", help="solo validar JSON, no quemar videos")
    args = ap.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    print("=" * 64)
    print("  LAB 7 CAPS — Forced Alignment sobre audio REAL del Tuskegee")
    print("=" * 64)

    api_key = _get_api_key()
    script = json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))
    chapters = script["chapters"]

    results_summary = []

    for i, ch in enumerate(chapters):
        cap_n = i + 1
        cap_id = f"ch{cap_n:02d}"
        mp3 = AUDIO_DIR / f"{cap_id}.mp3"
        text = (ch.get("text") or ch.get("narration", "")).strip()

        print(f"\n  ── Cap {cap_n} ({cap_id}) ──")
        if not mp3.exists():
            print(f"      [SKIP] no existe {mp3}")
            results_summary.append((cap_n, "NO_MP3", None, None))
            continue
        if not text:
            print(f"      [SKIP] cap sin texto")
            results_summary.append((cap_n, "NO_TEXT", None, None))
            continue

        audio_dur = _get_ffprobe_duration(mp3)
        print(f"      audio: {audio_dur:.1f}s · alineando...")

        result = forced_align(api_key, mp3, text)
        if result is None:
            results_summary.append((cap_n, "API_FAIL", None, None))
            continue

        (OUT_DIR / f"{cap_id}_alignment.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        checks = validate_alignment(result, audio_dur)
        print(f"      chars={len(result.get('characters',[]))} "
              f"words={len(result.get('words',[]))} "
              f"loss={checks['loss']} "
              f"monotonic={checks['monotonic']} "
              f"cover={checks['last_end']}/{checks['audio_dur']}s "
              f"-> {checks['verdict']}")

        results_summary.append((cap_n, checks["verdict"], checks["loss"], len(result.get("words", []))))

        if not args.no_video:
            syllables = chars_to_syllables(result.get("characters", []))
            ass_path = OUT_DIR / f"{cap_id}_subs.ass"
            build_ass(syllables, ass_path)
            ok = burn(ass_path, mp3, OUT_DIR / f"lab_{cap_id}_silabas.mp4")
            print(f"      video: {'OK' if ok else 'FALLO'}  ({len(syllables)} silabas)")

    # ─── Tabla resumen ───
    print("\n" + "=" * 64)
    print("  RESUMEN")
    print("=" * 64)
    print(f"  {'cap':<5}{'verdict':<10}{'loss':<12}{'words':<8}")
    print(f"  {'-'*4:<5}{'-'*8:<10}{'-'*10:<12}{'-'*6:<8}")
    n_pass = 0
    for cap_n, verdict, loss, nwords in results_summary:
        loss_str = f"{loss:.4f}" if isinstance(loss, (int, float)) else str(loss)
        print(f"  {cap_n:<5}{verdict:<10}{loss_str:<12}{nwords if nwords else '-':<8}")
        if verdict == "PASS":
            n_pass += 1
    print(f"\n  PASS: {n_pass}/{len(results_summary)}")
    print(f"  Carpeta: {OUT_DIR.resolve()}")
    if not args.no_video:
        print(f"\n  >>> Mira los lab_chXX_silabas.mp4 — son los 7 caps con audio real")
        print(f"      + subs alineados por Forced Alignment. El gate es tuyo.")
    print(f"\n  Nota: 'loss' mas bajo = alignment mas confiado. WARN en coverage")
    print(f"  suele ser silencios al final del audio, no necesariamente un problema.")


if __name__ == "__main__":
    main()
