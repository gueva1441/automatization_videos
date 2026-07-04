# lab/diag_237_pausa_ab.py — LAB (HANDOFF_136a). Probe A/B de PAUSAS dramáticas.
#
# Produce 3 mp3 para que el OÍDO de Omar decida la ruta del P1 (retención):
#   A) break tag nativo  <break time="1.5s" />  (1 call TTS)
#   B) narración LIMPIA + splice de 1.5s de silencio post-TTS con ffmpeg (1 TTS + 1 FA)
#   C) narración LIMPIA sin pausa (línea base; es la MISMA generación que B → gratis)
#
# Punto de pausa (A y B): después de "mirar." — 1.5s.
# Reusa helpers de producción (audio_profiles, config.api, _forced_align_elevenlabs,
# normalize_for_tts) — NO toca ningún módulo de producción. El TTS se hace inline
# (mismo payload que audio_manager._generate_chapter_audio) para no acoplar el
# cost_tracker de producción a un lab. Cero reintentos de variantes: si algo falla,
# se reporta tal cual (el veredicto es de Omar).
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# El script vive en lab/; el repo root (donde están config.py, audio_manager.py…)
# debe estar en sys.path para importar los helpers de producción.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import requests

from config import api
from audio_profiles import AUDIO_PROFILES
from audio_manager import _forced_align_elevenlabs
from tts_normalizer import normalize_for_tts
from fase2b import FFMPEG, FFPROBE

OUT = Path(__file__).resolve().parent / "outputs"

PROFILE = "MISTERIO_ABISAL"
PAUSE_S = 1.5
PAUSE_AFTER_WORD = "mirar"   # última ocurrencia

TEXT = (
    "En la superficie, la torre de agua seguía intacta. Los ingenieros revisaron los "
    "planos una vez, dos veces, tres veces. Todo parecía en orden. Pero había un "
    "detalle que nadie quiso mirar. El acero de los pernos no era el que figuraba "
    "en los documentos."
)


def _tts(text: str, voice_id: str, voice_settings: dict, out_path: Path) -> None:
    """TTS ElevenLabs → mp3. Mismo payload que audio_manager._generate_chapter_audio
    (model_id = api.elevenlabs_model), sin cost_tracker (es lab)."""
    payload = {
        "text": text,
        "model_id": api.elevenlabs_model,
        "voice_settings": voice_settings,
    }
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": api.elevenlabs_api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.content)


def _probe_duration(path: Path) -> float:
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    r.check_returncode()
    return float(json.loads(r.stdout)["format"]["duration"])


def _probe_audio_stream(path: Path) -> tuple[int, int, str]:
    """(sample_rate, channels, channel_layout) del primer stream de audio.
    NO asume 44100/mono — sondea el mp3 real."""
    r = subprocess.run(
        [FFPROBE, "-v", "quiet", "-print_format", "json",
         "-select_streams", "a:0",
         "-show_entries", "stream=sample_rate,channels,channel_layout", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    r.check_returncode()
    st = json.loads(r.stdout)["streams"][0]
    sr = int(st["sample_rate"])
    ch = int(st["channels"])
    layout = st.get("channel_layout") or ("mono" if ch == 1 else "stereo" if ch == 2 else f"{ch}c")
    return sr, ch, layout


def _norm_word(w: str) -> str:
    return "".join(c for c in w.lower() if c.isalnum())


def _find_word_end(fa: dict, target: str) -> float | None:
    """`end` de la ÚLTIMA ocurrencia de `target` en fa['words']."""
    tgt = _norm_word(target)
    hit = None
    for w in fa.get("words", []):
        if _norm_word(w.get("text", "")) == tgt:
            hit = float(w["end"])
    return hit


def _splice_silence(src_mp3: Path, cut_s: float, sr: int, layout: str, out_path: Path) -> None:
    """Corta src_mp3 en cut_s e inserta PAUSE_S de silencio. filter_complex +
    libmp3lame (re-encode) — el camino seguro (concat demuxer de mp3+wav se lleva mal).
    Silencio con el MISMO sample_rate/channel_layout que el fuente."""
    fc = (
        f"[0:a]atrim=end={cut_s:.3f},asetpts=PTS-STARTPTS[a1];"
        f"anullsrc=channel_layout={layout}:sample_rate={sr},"
        f"atrim=duration={PAUSE_S},asetpts=PTS-STARTPTS[sil];"
        f"[0:a]atrim=start={cut_s:.3f},asetpts=PTS-STARTPTS[a2];"
        f"[a1][sil][a2]concat=n=3:v=0:a=1[out]"
    )
    cmd = [
        FFMPEG, "-y", "-i", str(src_mp3),
        "-filter_complex", fc, "-map", "[out]",
        "-c:a", "libmp3lame", "-q:a", "2", str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg splice falló:\n{r.stderr[-500:]}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    prof = AUDIO_PROFILES[PROFILE]
    voice_id = prof["voice_id"]
    voice_settings = prof["voice_settings"]

    a_path = OUT / "pausa_A_breaktag.mp3"
    b_path = OUT / "pausa_B_splice.mp3"
    c_path = OUT / "pausa_C_sinpausa.mp3"
    fa_path = OUT / "diag_237_fa_limpio.json"
    result_path = OUT / "diag_237_result.txt"

    print("=" * 90)
    print(f"DIAG #237 — probe A/B pausas — perfil {PROFILE} · voz {voice_id} · modelo {api.elevenlabs_model}")
    print(f"  pausa {PAUSE_S}s después de '{PAUSE_AFTER_WORD}.'  ·  settings {voice_settings}")
    print("=" * 90)

    # Texto normalizado como lo haría producción (fuente de verdad para FA en B/C).
    norm_text = normalize_for_tts(TEXT, language="es")
    if norm_text != TEXT:
        print("  ⓘ normalize_for_tts modificó el texto (se usa el normalizado para TTS+FA)")

    # ── Versión A: break tag nativo (sobre el texto crudo, el tag debe sobrevivir intacto) ──
    if PAUSE_AFTER_WORD + "." not in TEXT:
        raise RuntimeError(f"no encuentro '{PAUSE_AFTER_WORD}.' en el texto para insertar el tag")
    tag_text = TEXT.replace(
        f"{PAUSE_AFTER_WORD}.", f'{PAUSE_AFTER_WORD}. <break time="{PAUSE_S}s" />', 1
    )
    print(f"\n[A] TTS con break tag → {a_path.name}")
    _tts(tag_text, voice_id, voice_settings, a_path)
    print(f"    ✓ {a_path.name}")

    # ── Versión C (= base de B): texto LIMPIO normalizado ──
    print(f"\n[C] TTS limpio (base) → {c_path.name}")
    _tts(norm_text, voice_id, voice_settings, c_path)
    print(f"    ✓ {c_path.name}")

    # ── Forced Alignment sobre el audio limpio ──
    print(f"\n[FA] forced-alignment sobre {c_path.name} (texto normalizado)")
    fa = _forced_align_elevenlabs(c_path, norm_text, language="es")
    fa_path.write_text(json.dumps(fa, indent=2, ensure_ascii=False), encoding="utf-8")
    cut_s = _find_word_end(fa, PAUSE_AFTER_WORD)
    if cut_s is None:
        raise RuntimeError(f"FA no contiene la palabra '{PAUSE_AFTER_WORD}' — no puedo cortar")
    print(f"    ✓ end('{PAUSE_AFTER_WORD}') = {cut_s:.3f}s  ·  FA → {fa_path.name}")

    # ── Versión B: splice de silencio en cut_s ──
    sr, ch, layout = _probe_audio_stream(c_path)
    print(f"\n[B] splice {PAUSE_S}s en {cut_s:.3f}s (sr={sr} ch={ch} layout={layout}) → {b_path.name}")
    _splice_silence(c_path, cut_s, sr, layout, b_path)
    print(f"    ✓ {b_path.name}")

    # ── Verificación: dur(B) ≈ dur(C) + PAUSE_S (±0.1s) ──
    dur_a = _probe_duration(a_path)
    dur_b = _probe_duration(b_path)
    dur_c = _probe_duration(c_path)
    expected_b = dur_c + PAUSE_S
    delta = dur_b - expected_b
    ok = abs(delta) <= 0.1

    lines = [
        f"pausa_A_breaktag.mp3   dur={dur_a:.3f}s   (break tag nativo)",
        f"pausa_B_splice.mp3     dur={dur_b:.3f}s   (splice ffmpeg — ruta candidata)",
        f"pausa_C_sinpausa.mp3   dur={dur_c:.3f}s   (línea base sin pausa)",
        f"cut_timestamp (end de '{PAUSE_AFTER_WORD}') = {cut_s:.3f}s",
        f"audio limpio: sample_rate={sr} Hz, channels={ch}, layout={layout}",
    ]
    check = (f"CHECK dur(B) ≈ dur(C)+{PAUSE_S}: {dur_b:.3f} vs {expected_b:.3f} "
             f"(Δ={delta:+.3f}s) → {'OK' if ok else '¡¡¡ FALLA !!!'}")
    lines.append(check)
    if not ok:
        lines.append(f"⚠⚠⚠ GRITO: el splice NO agregó exactamente {PAUSE_S}s de silencio. "
                     f"Revisar cut/anullsrc antes de confiar en B.")

    result_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n{'='*90}")
    for ln in lines:
        print("  " + ln)
    print(f"\n  escrito: {a_path}\n           {b_path}\n           {c_path}"
          f"\n           {fa_path}\n           {result_path}")


if __name__ == "__main__":
    main()
