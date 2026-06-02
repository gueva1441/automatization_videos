"""
mixer_server.py — Tool de mezcla interactiva ch04 (chat 39). AISLADO del pipeline.

Backend local (stdlib http.server, CERO deps nuevas) que sirve `mixer.html` y deja
a Omar encontrar de OÍDO el par (music_volume, music_volume_floor) que deja oír a
Bill claro en ch04. El tool IMPRIME números; NO toca audio_profiles.py.

Reusa en modo LECTURA:
  - audio_profiles.AUDIO_PROFILES["MISTERIO_ABISAL"]["mixing"]  → /defaults
  - el filter_complex de fase2b._mix_music_into_video (replicado abajo, SIN video
    ni padding inicial — ver comentario en _build_mix_filter) → /render_confirm

NO importa fase2b (arrastra depthflow/gemini/pyphen). Replica solo el lookup de
ffmpeg y el filtro de audio. audio_profiles SÍ se importa (es data pura).

Alcance v1: SOLO ch04, fix GLOBAL. Sin localStorage. Sin multi-cap. Cableado a ch04.

USO:
    python mixer_server.py
    → abre http://127.0.0.1:8000  en el navegador
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import audio_profiles  # data pura, import liviano (verificado chat 39)

# Forzar UTF-8 en stdout/stderr (Windows usa cp1252 por defecto) — igual que fase2b.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────
#  CONFIG (editable arriba — cableado a ch04, v1)
# ─────────────────────────────────────────────────────────────────

HOST = "127.0.0.1"
PORT = 8000
PROFILE_NAME = "MISTERIO_ABISAL"
TOPIC_ID = "8286b193-ff82-4357-b32d-21ca30909c4d"
CHAPTER = "ch04"

# Headroom del punto de partida MEDIDO: cuántos dB por debajo de la voz queremos la
# música en la banda crítica 1–4 kHz. Editable. NO es un veredicto — es física + el
# oído de Omar manda (ver /suggested_start).
HEADROOM_DB = 10.0

# Banda crítica donde la música "masca" sobre la voz.
BAND_LO_HZ = 1000
BAND_HI_HZ = 4000

# Clamps sanos para el punto de partida sugerido.
MV_CLAMP = (0.05, 0.40)
MVF_CLAMP = (0.03, 0.30)

BASE_DIR = Path(__file__).resolve().parent
VOICE_PATH = BASE_DIR / "output" / "audio" / TOPIC_ID / f"{CHAPTER}.mp3"
MUSIC_PATH = BASE_DIR / "audio_library" / "shock_curated.mp3"
HTML_PATH = BASE_DIR / "mixer.html"
# Renders cacheados bajo output/ (gitignored).
RENDER_DIR = BASE_DIR / "output" / "audio" / TOPIC_ID / "_mixer_renders_chat39"


# ─────────────────────────────────────────────────────────────────
#  FFmpeg / FFprobe lookup (replicado de fase2b — mismo winget fallback)
# ─────────────────────────────────────────────────────────────────

def _find_ffmpeg_binary(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    winget_base = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if winget_base.exists():
        for pkg_dir in winget_base.glob("Gyan.FFmpeg_*"):
            matches = list(pkg_dir.glob(f"ffmpeg-*/bin/{name}.exe"))
            if matches:
                return str(matches[0])
    return None


FFMPEG = _find_ffmpeg_binary("ffmpeg")
FFPROBE = _find_ffmpeg_binary("ffprobe")


def _run(cmd: list[str], timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _get_duration(path: Path) -> float:
    assert FFPROBE is not None
    r = _run([FFPROBE, "-v", "quiet", "-print_format", "json",
              "-show_format", str(path)], timeout=15)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe falló sobre {path.name}: {r.stderr[-200:]}")
    return float(json.loads(r.stdout)["format"]["duration"])


# ─────────────────────────────────────────────────────────────────
#  Lógica
# ─────────────────────────────────────────────────────────────────

def _mixing_params() -> dict:
    """Params actuales del perfil (lectura, no edita)."""
    return dict(audio_profiles.AUDIO_PROFILES[PROFILE_NAME]["mixing"])


_MEAN_RE = re.compile(r"mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB")


def _measure_band_db(path: Path) -> float:
    """mean_volume (dB) del archivo filtrado a la banda 1–4 kHz, vía volumedetect."""
    assert FFMPEG is not None
    r = _run([
        FFMPEG, "-hide_banner", "-i", str(path),
        "-af", f"highpass=f={BAND_LO_HZ},lowpass=f={BAND_HI_HZ},volumedetect",
        "-f", "null", "-",
    ], timeout=120)
    m = _MEAN_RE.search(r.stderr)
    if not m:
        raise RuntimeError(f"no se pudo medir mean_volume de {path.name}: {r.stderr[-200:]}")
    return float(m.group(1))


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _suggested_start() -> dict:
    """Punto de partida MEDIDO (física, no LLM). Ver handoff §3.5 / §8."""
    prof = _mixing_params()
    voz_band = _measure_band_db(VOICE_PATH)
    mus_band = _measure_band_db(MUSIC_PATH)
    # cuántos dB mover la música para quedar HEADROOM_DB bajo la voz en la banda
    target_db = voz_band - HEADROOM_DB - mus_band
    gain = 10 ** (target_db / 20)
    mv = _clamp(gain, *MV_CLAMP)
    # floor sugerido = misma proporción floor/volume que el perfil hoy
    ratio_floor = prof["music_volume_floor"] / prof["music_volume"]
    mvf = _clamp(gain * ratio_floor, *MVF_CLAMP)
    return {
        "music_volume_suggested": round(mv, 3),
        "music_volume_floor_suggested": round(mvf, 3),
        "voz_band_db": round(voz_band, 1),
        "mus_band_db": round(mus_band, 1),
        "headroom_db": HEADROOM_DB,
        "note": (
            "Punto de partida MEDIDO sobre los archivos reales (banda 1–4 kHz), "
            "no un veredicto. Pone la música ~{:.0f} dB bajo la voz en la banda donde "
            "masca. Movelo a gusto — el oído de Omar y el render real mandan."
        ).format(HEADROOM_DB),
    }


def _build_mix_filter(mv: float, mvf: float, p: dict) -> str:
    """
    Replica el filter_complex de audio de fase2b._mix_music_into_video, PERO:
      - input 0 = ch04.mp3 (voz aislada) en vez de [0:a] del MP4 con narración.
      - SIN [0:v]/tpad ni adelay/padding inicial: acá es ch04 suelto, no el video
        con hook (el padding INITIAL_SILENCE_SEC solo aplica al MP4 final). El
        ducking de las 3 ramas (narr + ducked + floor, normalize=0) es idéntico.
    """
    return (
        f"[0:a]aresample=44100,asplit=2[narr_main][narr_sc];"
        f"[1:a]aresample=44100,asplit=2[music_a][music_b];"
        f"[music_a]volume={mv}[music_lvl];"
        f"[music_lvl][narr_sc]sidechaincompress="
        f"threshold={p['duck_threshold']}:"
        f"ratio={p['duck_ratio']}:"
        f"attack={p['duck_attack_ms']}:"
        f"release={p['duck_release_ms']}"
        f"[music_ducked];"
        f"[music_b]volume={mvf}[music_floor];"
        f"[narr_main][music_ducked][music_floor]amix=inputs=3:duration=longest:"
        f"dropout_transition=0:normalize=0[mixed]"
    )


_render_cache: dict[tuple[float, float], Path] = {}


def _render_confirm(mv: float, mvf: float) -> Path:
    """Mix REAL de ffmpeg (ducking fiel) sobre ch04, salida MP3. Cacheado."""
    assert FFMPEG is not None
    key = (round(mv, 4), round(mvf, 4))
    cached = _render_cache.get(key)
    if cached and cached.exists():
        return cached

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    out = RENDER_DIR / f"mix_{key[0]:.4f}_{key[1]:.4f}.mp3"
    if out.exists():
        _render_cache[key] = out
        return out

    dur = _get_duration(VOICE_PATH)
    p = _mixing_params()
    filt = _build_mix_filter(mv, mvf, p)

    # input 0 = voz; input 1 = música loopeada (-stream_loop -1 va ANTES de su -i),
    # igual que _build_music_piece_for_chapter. -t acota la salida al largo de ch04
    # (amix duration=longest, pero la música loopea infinita → la corta el -t).
    cmd = [
        FFMPEG, "-y",
        "-i", str(VOICE_PATH),
        "-stream_loop", "-1", "-i", str(MUSIC_PATH),
        "-filter_complex", filt,
        "-map", "[mixed]",
        "-t", f"{dur:.3f}",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(out),
    ]
    r = _run(cmd, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"FFmpeg mix falló: {r.stderr[-500:]}")
    _render_cache[key] = out
    return out


# ─────────────────────────────────────────────────────────────────
#  HTTP handler
# ─────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # silenciar el log ruidoso por request
        sys.stderr.write("  " + (fmt % args) + "\n")

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str):
        if not path.exists():
            self._send_json({"error": f"no existe: {path}"}, status=404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Accept-Ranges", "none")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            if self.path == "/" or self.path.startswith("/index"):
                self._send_file(HTML_PATH, "text/html; charset=utf-8")
            elif self.path == "/audio/voice":
                self._send_file(VOICE_PATH, "audio/mpeg")
            elif self.path == "/audio/music":
                self._send_file(MUSIC_PATH, "audio/mpeg")
            elif self.path == "/defaults":
                self._send_json(_mixing_params())
            elif self.path == "/suggested_start":
                self._send_json(_suggested_start())
            else:
                self._send_json({"error": "ruta no encontrada"}, status=404)
        except Exception as e:  # noqa: BLE001
            self._send_json({"error": f"{type(e).__name__}: {e}"}, status=500)

    def do_POST(self):
        try:
            if self.path != "/render_confirm":
                self._send_json({"error": "ruta no encontrada"}, status=404)
                return
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            mv = float(body["music_volume"])
            mvf = float(body["music_volume_floor"])
            print(f"  🎚  render_confirm: music_volume={mv}, floor={mvf} ...")
            out = _render_confirm(mv, mvf)
            self._send_file(out, "audio/mpeg")
            print(f"     ✓ {out.name} ({out.stat().st_size/1024:.0f} KB)")
        except Exception as e:  # noqa: BLE001
            self._send_json({"error": f"{type(e).__name__}: {e}"}, status=500)


def _preflight():
    problems = []
    if FFMPEG is None:
        problems.append("ffmpeg no encontrado")
    if FFPROBE is None:
        problems.append("ffprobe no encontrado")
    if not VOICE_PATH.exists():
        problems.append(f"voz no existe: {VOICE_PATH}")
    if not MUSIC_PATH.exists():
        problems.append(f"música no existe: {MUSIC_PATH}")
    if not HTML_PATH.exists():
        problems.append(f"mixer.html no existe: {HTML_PATH}")
    return problems


def main():
    problems = _preflight()
    if problems:
        print("❌ Preflight falló:")
        for p in problems:
            print(f"   - {p}")
        sys.exit(1)

    prof = _mixing_params()
    print("─" * 60)
    print(f"  Mixer ch04 — Tuskegee  (perfil {PROFILE_NAME})")
    print(f"  voz:    {VOICE_PATH}")
    print(f"  música: {MUSIC_PATH}")
    print(f"  defaults perfil: music_volume={prof['music_volume']}, "
          f"music_volume_floor={prof['music_volume_floor']}")
    print("─" * 60)
    url = f"http://{HOST}:{PORT}"
    print(f"  ▶ Abrí en el navegador:  {url}")
    print(f"    (Ctrl+C para frenar)")
    print("─" * 60)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  frenado.")
        server.shutdown()


if __name__ == "__main__":
    main()
