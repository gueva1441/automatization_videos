"""
mixer_server.py — Tool de mezcla interactiva MULTI-CAP (chat 39 v1 → chat 40 bloque 4).
AISLADO del pipeline.

Backend local (stdlib http.server, CERO deps nuevas) que sirve `mixer.html` y deja a
Omar calibrar de OÍDO el par (music_volume, music_volume_floor) de CADA cap de un video,
y GUARDARLO en el json del track (audio_library/<track_id>.json). El número viaja con
el track → se calibra una vez, vale para todos los videos que usen ese track.

Reusa en modo LECTURA:
  - audio_profiles.AUDIO_PROFILES["MISTERIO_ABISAL"]["mixing"]  → /defaults (base ref)
  - el filter_complex de fase2b._mix_music_into_video (replicado en _build_mix_filter,
    SIN video ni padding inicial — ver §6 DEUDA en el handoff) → /render_confirm

NO importa fase2b (arrastra depthflow/gemini/pyphen). Replica el lookup de ffmpeg, el
filtro de audio, y la resolución cap→track→json (misma lógica que fase2b para no
divergir). audio_profiles SÍ se importa (data pura).

Cap → voz / track / json se resuelven POR CAP vía music_map (output/audio/<TOPIC_ID>/
music_map.json → tracks_by_chapter[chXX]). Sin localStorage.

USO:
    python mixer_server.py
    python mixer_server.py --topic <TOPIC_ID>
    → abre http://127.0.0.1:8000  en el navegador
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import audio_profiles  # data pura, import liviano (verificado chat 39)

# Forzar UTF-8 en stdout/stderr (Windows usa cp1252 por defecto) — igual que fase2b.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────
#  CONFIG (editable arriba; TOPIC_ID también por --topic)
# ─────────────────────────────────────────────────────────────────

HOST = "127.0.0.1"
PORT = 8000
PROFILE_NAME = "MISTERIO_ABISAL"
TOPIC_ID = "8286b193-ff82-4357-b32d-21ca30909c4d"

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
HTML_PATH = BASE_DIR / "mixer.html"

# Se setean en función de TOPIC_ID (re-evaluados en main si llega --topic).
MUSIC_MAP_PATH = BASE_DIR / "output" / "audio" / TOPIC_ID / "music_map.json"
RENDER_DIR = BASE_DIR / "output" / "audio" / TOPIC_ID / "_mixer_renders_chat40"
MUSIC_MAP: dict[str, dict] = {}


def _set_topic(topic_id: str) -> None:
    """Re-apunta los paths derivados del topic (llamado en main)."""
    global TOPIC_ID, MUSIC_MAP_PATH, RENDER_DIR
    TOPIC_ID = topic_id
    MUSIC_MAP_PATH = BASE_DIR / "output" / "audio" / TOPIC_ID / "music_map.json"
    RENDER_DIR = BASE_DIR / "output" / "audio" / TOPIC_ID / "_mixer_renders_chat40"


def _load_music_map() -> dict[str, dict]:
    """Carga tracks_by_chapter del music_map del topic (cap → track_info)."""
    if not MUSIC_MAP_PATH.exists():
        raise FileNotFoundError(f"music_map no existe: {MUSIC_MAP_PATH}")
    raw = json.loads(MUSIC_MAP_PATH.read_text(encoding="utf-8"))
    return raw.get("tracks_by_chapter", {}) or {}


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
#  Resolución cap → voz / track / json (MISMA lógica que fase2b)
# ─────────────────────────────────────────────────────────────────

def _voice_path(cap: str) -> Path:
    return BASE_DIR / "output" / "audio" / TOPIC_ID / f"{cap}.mp3"


def _track_mp3_and_json(cap: str) -> tuple[Path, Path]:
    """Resuelve mp3 + json del track del cap vía music_map (igual que fase2b)."""
    ti = MUSIC_MAP.get(cap)
    if not ti or ti.get("match_source") == "skipped":
        raise ValueError(f"{cap}: sin track en music_map")
    mp3_rel = ti.get("mp3_path")
    if not mp3_rel:
        raise ValueError(f"{cap}: track sin mp3_path en music_map")
    mp3_abs = BASE_DIR / mp3_rel
    if not mp3_abs.exists():
        raise FileNotFoundError(f"{cap}: track no existe en disco: {mp3_abs}")
    return mp3_abs, mp3_abs.with_suffix(".json")


def _caps_list() -> list[dict]:
    """[{cap, track_id}] ordenado, para el dropdown."""
    out = []
    for cap in sorted(MUSIC_MAP.keys()):
        ti = MUSIC_MAP[cap] or {}
        out.append({"cap": cap, "track_id": ti.get("track_id", "—"),
                    "skipped": ti.get("match_source") == "skipped"})
    return out


def _topic_title() -> str | None:
    """Título del topic si se puede leer TRIVIAL (sin deps nuevas): del sync_map.
    El id es el must-have; el título es opcional (None si no está)."""
    sm = BASE_DIR / "output" / "audio" / TOPIC_ID / "sync_map.json"
    if not sm.exists():
        return None
    try:
        data = json.loads(sm.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    # Solo el título REAL del topic. NO usar profile_description (es del perfil de voz,
    # no del topic → mostrarlo como "título" confunde). Si no está → None (solo id).
    return data.get("topic_title") or None


def _topic_info() -> dict:
    return {"topic_id": TOPIC_ID, "title": _topic_title()}


# ─────────────────────────────────────────────────────────────────
#  Lógica de mezcla / medición
# ─────────────────────────────────────────────────────────────────

def _mixing_params() -> dict:
    """Params del perfil (lectura). Base 0.26/0.16 + sidechain (threshold/ratio/...)."""
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


def _read_saved_volumes(json_path: Path) -> tuple[float | None, float | None]:
    """Lee music_volume / music_volume_floor del json del track (None si no están)."""
    try:
        meta = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, None
    mv = meta.get("music_volume")
    mvf = meta.get("music_volume_floor")
    return (float(mv) if mv is not None else None,
            float(mvf) if mvf is not None else None)


def _suggested_start(cap: str) -> dict:
    """Punto de partida MEDIDO (física) para un cap + el valor GUARDADO si existe."""
    prof = _mixing_params()
    voice = _voice_path(cap)
    mp3, json_path = _track_mp3_and_json(cap)
    voz_band = _measure_band_db(voice)
    mus_band = _measure_band_db(mp3)
    # cuántos dB mover la música para quedar HEADROOM_DB bajo la voz en la banda
    target_db = voz_band - HEADROOM_DB - mus_band
    gain = 10 ** (target_db / 20)
    mv = _clamp(gain, *MV_CLAMP)
    ratio_floor = prof["music_volume_floor"] / prof["music_volume"]
    mvf = _clamp(gain * ratio_floor, *MVF_CLAMP)
    saved_mv, saved_mvf = _read_saved_volumes(json_path)
    return {
        "cap": cap,
        "track_id": (MUSIC_MAP.get(cap) or {}).get("track_id", "—"),
        "music_volume_suggested": round(mv, 3),
        "music_volume_floor_suggested": round(mvf, 3),
        "music_volume_saved": round(saved_mv, 3) if saved_mv is not None else None,
        "music_volume_floor_saved": round(saved_mvf, 3) if saved_mvf is not None else None,
        "base_music_volume": prof["music_volume"],
        "base_music_volume_floor": prof["music_volume_floor"],
        "voz_band_db": round(voz_band, 1),
        "mus_band_db": round(mus_band, 1),
        "headroom_db": HEADROOM_DB,
        "note": (
            "Sugerido = MEDIDO sobre los archivos (banda 1–4 kHz), no veredicto. "
            "Saved = lo que ya está en el json del track (si fue calibrado). El "
            "oído de Omar y el render real mandan."
        ),
    }


def _build_mix_filter(mv: float, mvf: float, p: dict) -> str:
    """
    Espejo SIMPLIFICADO del filter_complex de fase2b._mix_music_into_video, PERO:
      - input 0 = voz del cap (chXX.mp3) en vez de [0:a] del MP4 con narración.
      - SIN [0:v]/tpad ni adelay/padding inicial: acá es la voz suelta, no el video
        con hook (INITIAL_SILENCE_SEC solo aplica al MP4 final). El ducking de las 3
        ramas (narr + ducked + floor, normalize=0) y los params del sidechain son
        idénticos. ⚠ DEUDA (handoff §6): este filtro es un espejo manual del pipeline;
        si se tocan params de mixing en fase2b, acá queda stale. Documentado.
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


_render_cache: dict[tuple[str, float, float], Path] = {}


def _render_confirm(cap: str, mv: float, mvf: float) -> Path:
    """Mix REAL de ffmpeg (ducking fiel) voz(cap)+track(cap), salida MP3. Cacheado."""
    assert FFMPEG is not None
    key = (cap, round(mv, 4), round(mvf, 4))
    cached = _render_cache.get(key)
    if cached and cached.exists():
        return cached

    voice = _voice_path(cap)
    mp3, _ = _track_mp3_and_json(cap)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    out = RENDER_DIR / f"mix_{cap}_{key[1]:.4f}_{key[2]:.4f}.mp3"
    if out.exists():
        _render_cache[key] = out
        return out

    dur = _get_duration(voice)
    filt = _build_mix_filter(mv, mvf, _mixing_params())
    # input 0 = voz; input 1 = música loopeada (-stream_loop -1 va ANTES de su -i).
    # -t acota la salida al largo de la voz (la música loopea infinita → la corta -t).
    cmd = [
        FFMPEG, "-y",
        "-i", str(voice),
        "-stream_loop", "-1", "-i", str(mp3),
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


def _write_volume_to_json(json_path: Path, mv: float, mvf: float) -> dict:
    """
    Update QUIRÚRGICO: lee el json, muta SOLO music_volume + music_volume_floor,
    reescribe preservando TODO el resto. Devuelve el meta resultante.
    (Factorizado para poder probarlo sobre un json DUMMY en el smoke — GATE 4-CC.)
    """
    meta = json.loads(json_path.read_text(encoding="utf-8"))
    meta["music_volume"] = round(float(mv), 3)
    meta["music_volume_floor"] = round(float(mvf), 3)
    json_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def _save_track_volume(cap: str, mv: float, mvf: float) -> dict:
    """EL CORAZÓN: escribe el par en el json del track del cap."""
    _, json_path = _track_mp3_and_json(cap)
    meta = _write_volume_to_json(json_path, mv, mvf)
    return {
        "saved": True,
        "cap": cap,
        "track_id": meta.get("track_id"),
        "json_path": str(json_path.relative_to(BASE_DIR)),
        "music_volume": meta["music_volume"],
        "music_volume_floor": meta["music_volume_floor"],
    }


# ─────────────────────────────────────────────────────────────────
#  Re-armar video (fase2b) — bloque 7D. Corre SOLO fase2b ($0, sin gate).
# ─────────────────────────────────────────────────────────────────

_RERUN: dict = {"running": False, "returncode": None, "log": []}
_RERUN_LOCK = threading.Lock()
_RERUN_LOG_MAX = 400  # líneas


def _rerun_command() -> list[str]:
    """Comando del re-armado. FACTORIZADO para que el smoke inyecte un stub rápido
    (GATE 7-CC: el test NO corre la fase2b real). sys.executable = python del venv
    desde donde se lanzó el server."""
    return [sys.executable, "fase2b.py", TOPIC_ID]


def _rerun_worker() -> None:
    """Thread daemon: lanza el comando, streamea stdout+stderr al buffer _RERUN."""
    try:
        # Windows: text=True sin encoding decodifica con cp1252 (charmap) → los
        # emojis utf-8 de fase2b (✓ ✅ ⚠ —) tumban el lector (rc=-1). Forzar utf-8 al
        # decodificar + errors="replace" (un byte raro nunca mata el lector) + env
        # PYTHONIOENCODING para que el hijo TAMBIÉN emita utf-8 (belt-and-suspenders).
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        proc = subprocess.Popen(
            _rerun_command(), cwd=str(BASE_DIR),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
            encoding="utf-8", errors="replace", env=env,
        )
        for line in proc.stdout:
            with _RERUN_LOCK:
                _RERUN["log"].append(line.rstrip("\n"))
                if len(_RERUN["log"]) > _RERUN_LOG_MAX:
                    _RERUN["log"] = _RERUN["log"][-_RERUN_LOG_MAX:]
        proc.wait()
        rc = proc.returncode
    except Exception as e:  # noqa: BLE001
        with _RERUN_LOCK:
            _RERUN["log"].append(f"[mixer] error lanzando fase2b: {type(e).__name__}: {e}")
        rc = -1
    with _RERUN_LOCK:
        _RERUN["returncode"] = rc
        _RERUN["running"] = False


def _start_rerun() -> dict:
    """Arranca el re-armado si no hay otro en curso. {'started':True} o {'conflict':True}."""
    with _RERUN_LOCK:
        if _RERUN["running"]:
            return {"conflict": True}
        _RERUN["running"] = True
        _RERUN["returncode"] = None
        _RERUN["log"] = []
    threading.Thread(target=_rerun_worker, daemon=True).start()
    return {"started": True}


def _rerun_status(tail: int = 40) -> dict:
    with _RERUN_LOCK:
        return {
            "running": _RERUN["running"],
            "returncode": _RERUN["returncode"],
            "log_tail": list(_RERUN["log"][-tail:]),
        }


# ─────────────────────────────────────────────────────────────────
#  HTTP handler
# ─────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # silenciar el log ruidoso por request
        sys.stderr.write("  " + (fmt % args) + "\n")

    def _qs(self) -> dict:
        return parse_qs(urlparse(self.path).query)

    def _cap_param(self) -> str:
        cap = self._qs().get("cap", [None])[0]
        if not cap:
            raise ValueError("falta el query param ?cap=chXX")
        return cap

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
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
            route = urlparse(self.path).path
            if route == "/" or route.startswith("/index"):
                self._send_file(HTML_PATH, "text/html; charset=utf-8")
            elif route == "/caps":
                self._send_json(_caps_list())
            elif route == "/audio/voice":
                self._send_file(_voice_path(self._cap_param()), "audio/mpeg")
            elif route == "/audio/music":
                mp3, _ = _track_mp3_and_json(self._cap_param())
                self._send_file(mp3, "audio/mpeg")
            elif route == "/defaults":
                self._send_json(_mixing_params())
            elif route == "/suggested_start":
                self._send_json(_suggested_start(self._cap_param()))
            elif route == "/topic":
                self._send_json(_topic_info())
            elif route == "/rerun_status":
                self._send_json(_rerun_status())
            else:
                self._send_json({"error": "ruta no encontrada"}, status=404)
        except Exception as e:  # noqa: BLE001
            self._send_json({"error": f"{type(e).__name__}: {e}"}, status=500)

    def do_POST(self):
        try:
            route = urlparse(self.path).path

            # /rerun no lleva body (usa el TOPIC_ID del server).
            if route == "/rerun":
                res = _start_rerun()
                if res.get("conflict"):
                    self._send_json({"error": "ya hay una corrida en curso"}, status=409)
                    print("  ▶ rerun: rechazado (ya hay una corrida en curso)")
                else:
                    print(f"  ▶ rerun: lanzando fase2b para {TOPIC_ID[:8]}…")
                    self._send_json({"started": True})
                return

            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            cap = body.get("cap")
            mv = float(body["music_volume"])
            mvf = float(body["music_volume_floor"])
            if not cap:
                raise ValueError("falta 'cap' en el body")

            if route == "/render_confirm":
                print(f"  🎚  render_confirm [{cap}]: vol={mv}, floor={mvf} ...")
                out = _render_confirm(cap, mv, mvf)
                self._send_file(out, "audio/mpeg")
                print(f"     ✓ {out.name} ({out.stat().st_size/1024:.0f} KB)")
            elif route == "/save":
                print(f"  💾 save [{cap}]: vol={mv}, floor={mvf} ...")
                res = _save_track_volume(cap, mv, mvf)
                self._send_json(res)
                print(f"     ✓ escrito en {res['json_path']} "
                      f"(track={res['track_id']})")
            else:
                self._send_json({"error": "ruta no encontrada"}, status=404)
        except Exception as e:  # noqa: BLE001
            self._send_json({"error": f"{type(e).__name__}: {e}"}, status=500)


def _preflight() -> list[str]:
    problems = []
    if FFMPEG is None:
        problems.append("ffmpeg no encontrado")
    if FFPROBE is None:
        problems.append("ffprobe no encontrado")
    if not HTML_PATH.exists():
        problems.append(f"mixer.html no existe: {HTML_PATH}")
    if not MUSIC_MAP_PATH.exists():
        problems.append(f"music_map no existe: {MUSIC_MAP_PATH}")
        return problems
    for cap in sorted(MUSIC_MAP.keys()):
        v = _voice_path(cap)
        if not v.exists():
            problems.append(f"[{cap}] voz no existe: {v}")
        try:
            mp3, jsn = _track_mp3_and_json(cap)
            if not jsn.exists():
                problems.append(f"[{cap}] json del track no existe: {jsn}")
        except (ValueError, FileNotFoundError) as e:
            problems.append(f"[{cap}] {e}")
    return problems


def _die_no_assets(problems: list[str] | None = None, extra: str | None = None) -> None:
    """Muere con un mensaje accionable cuando el topic no tiene assets de audio."""
    print(f"❌ El topic {TOPIC_ID} no tiene assets de audio "
          f"(falta music_map.json / chXX.mp3).")
    print(f"   ¿Corriste fase1_5 + fase2a para este topic? El mixer necesita la voz "
          f"+ el music_map.")
    print(f"   Esperaba: output/audio/{TOPIC_ID}/music_map.json + chXX.mp3")
    if problems:
        print("   Detalle:")
        for p in problems:
            print(f"     - {p}")
    elif extra:
        print(f"   Detalle: {extra}")
    sys.exit(1)


def main():
    global MUSIC_MAP
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default=TOPIC_ID, help="topic_id (default: el cableado)")
    args = ap.parse_args()
    _set_topic(args.topic)

    try:
        MUSIC_MAP = _load_music_map()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        _die_no_assets(extra=str(e))

    problems = _preflight()
    if problems:
        # Si lo que falta son assets de audio (music_map / voces), dar el mensaje
        # accionable; si es otra cosa (ffmpeg, html), listar crudo.
        assets_missing = any(("music_map" in p or "voz no existe" in p) for p in problems)
        if assets_missing:
            _die_no_assets(problems=problems)
        print("❌ Preflight falló:")
        for p in problems:
            print(f"   - {p}")
        sys.exit(1)

    prof = _mixing_params()
    title = _topic_title()
    print("─" * 64)
    print(f"  Mixer MULTI-CAP — {('« ' + title + ' » · ') if title else ''}{TOPIC_ID}")
    print(f"  perfil {PROFILE_NAME}")
    print(f"  base perfil (fallback): music_volume={prof['music_volume']}, "
          f"floor={prof['music_volume_floor']}")
    print(f"  caps ({len(MUSIC_MAP)}):")
    for c in _caps_list():
        mp3, jsn = _track_mp3_and_json(c["cap"])
        smv, smvf = _read_saved_volumes(jsn)
        saved = f"saved {smv}/{smvf}" if smv is not None else "sin calibrar (base)"
        print(f"     {c['cap']} — {c['track_id']:<24} {saved}")
    print("─" * 64)
    url = f"http://{HOST}:{PORT}"
    print(f"  ▶ Abrí en el navegador:  {url}    (Ctrl+C para frenar)")
    print("─" * 64)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  frenado.")
        server.shutdown()


if __name__ == "__main__":
    main()
