"""
qa_studio_server.py — QA STUDIO v1 · VISOR (read-only) + ENSAMBLAR (handoff chat 58).

Gate fase2.5: revisar foto + anchor + audio POR CAPÍTULO antes de gastar el ensamble.
v1 = SOLO lectura + botón ENSAMBLAR. Los fixes (foto/audio) son fases siguientes.

Espejo de mixer_server.py: stdlib ThreadingHTTPServer + BaseHTTPRequestHandler, CERO
deps nuevas. Lógica en QAState (testeable sin socket), Handler fino.

NO importa fase2b (arrastra DepthFlow/Gemini/pyphen) — el ENSAMBLAR lo lanza por
subprocess. SÍ importa anchor_timing.compute_anchor_starts (data pura, COMPARTIDO con
fase2b → el preview del visor usa el MISMO matcher que el render → sync idéntico).

FUENTES (verificadas en máquina, handoff §VERIFICÁ):
  - anchors : data/scripts/{topic_id}.json  (MISMO archivo que fase2b._load_script_lookup;
              flux → chapters[].image_prompts[].narration_anchor;
              veo  → chapters[].supplemental_image_prompts[].narration_anchor)
  - words   : output/audio/{topic_id}/chXX_timestamps.json  (lista pura [{word,start,end}])
  - audio   : output/audio/{topic_id}/chXX.mp3              (glob: .mp3/.wav/.m4a/.ogg)
  - PNG flux: output/{topic_id}/assets/chNN_flux/chNN_img_MM.png
  - PNG supp: output/{topic_id}/assets/chNN_flux/chNN_supp_MM.png   (caps veo: 1,7)
  - VEO clip: output/{topic_id}/assets/chNN_veo/chNN_clip_01.mp4

REGLA (handoff): LEER SIEMPRE DE DISCO, NUNCA del manifest. caps()/imágenes salen de
glob sobre disco; los anchors salen del script (que ES la fuente de fase2b, no el
manifest de render). De paso caza el bug manifest-vs-disco.

⚠ DECISIÓN /assemble (v1): el gasto que este gate protege es fase2b (el ensamble caro).
   `python fase3.py {tid}` SIN --headless cae en package() → abre el form interactivo de
   m09 (y _menu() usa input()), que colgaría/abriría un browser desde el thread daemon.
   Por eso ENSAMBLAR corre fase2b y, al exit 0, avisa "listo para packaging". El wiring
   de fase3 queda DEFERIDO (coherente con los DEFERIDOS del handoff). Si mañana se quiere
   cablear fase3, va headless con sus flags de compose — no el form.

USO:
    python qa_studio_server.py
    python qa_studio_server.py --topic <TOPIC_ID>
    → abre http://127.0.0.1:8000  en el navegador
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from anchor_timing import compute_anchor_starts  # data pura, COMPARTIDO con fase2b

# Forzar UTF-8 en stdout/stderr (Windows usa cp1252) — igual que mixer_server / fase2b.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────

HOST = "127.0.0.1"
PORT = 8000
TOPIC_ID = "985a942f-ae78-4193-8486-2cc4c5a999a4"  # default cableado (editable / --topic)

BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "qa_studio.html"

AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".ogg")
# name de imagen permitido (defensa #1 contra path traversal; la #2 es relative_to).
_IMG_NAME_RE = re.compile(r"^ch\d{2}_(img|supp)_\d+\.png$")
_CAP_RE = re.compile(r"^ch\d{2}$")


# ═════════════════════════════════════════════════════════════════
#  QAState — LÓGICA (testeable sin socket)
# ═════════════════════════════════════════════════════════════════

class QAState:
    """Toda la lógica del visor. Lee SIEMPRE de disco. Sin red, sin globals →
    construible con un base_dir custom en los tests."""

    def __init__(self, topic_id: str, base_dir: Path | None = None) -> None:
        self.topic_id = topic_id
        self.base = (base_dir or BASE_DIR).resolve()
        self.audio_dir = self.base / "output" / "audio" / topic_id
        self.assets_dir = self.base / "output" / topic_id / "assets"
        self.script_path = self.base / "data" / "scripts" / f"{topic_id}.json"
        self._script = self._load_script()      # cid → {render_engine, anchors, supp_anchors, ...}
        self._roles = self._load_skeleton_roles()  # cid → role (puede estar vacío)

    # ─── carga de fuentes ───

    def _load_script(self) -> dict[str, dict]:
        """Mirror de fase2b._load_script_lookup (LONG), + supp_anchors + render_engine.
        MISMO archivo que fase2b → sync preview==render."""
        if not self.script_path.exists():
            return {}
        try:
            raw = json.loads(self.script_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        if raw.get("video_type") != "long":
            return {}  # v1: solo LONG (el QA por-cap es del formato documental largo)

        lookup: dict[str, dict] = {}
        for item in raw.get("chapters", []):
            n = item.get("chapter_number")
            if n is None:
                continue
            cid = f"ch{int(n):02d}"
            anchors: list[str] = []
            rip = item.get("image_prompts")
            if isinstance(rip, list):
                for ip in rip:
                    if isinstance(ip, dict):
                        a = (ip.get("narration_anchor") or "").strip()
                        if a:
                            anchors.append(a)
            supp: list[str] = []
            sip = item.get("supplemental_image_prompts")
            if isinstance(sip, list):
                for ip in sip:
                    if isinstance(ip, dict):
                        supp.append((ip.get("narration_anchor") or "").strip())
                    elif isinstance(ip, str):
                        supp.append(ip.strip())
            lookup[cid] = {
                "render_engine": str(item.get("render_engine", "")).lower(),
                "anchors": anchors,
                "supp_anchors": supp,
                "base_anchor": (item.get("narration_anchor") or "").strip(),
                "narration": str(item.get("narration", "")).strip(),
            }
        return lookup

    def _load_skeleton_roles(self) -> dict[str, str]:
        """cid → role del 01a_skeleton (si está). Opcional: si no, derivamos en _role()."""
        p = self.base / "data" / "scripts" / "_steps" / self.topic_id / "01a_skeleton.json"
        if not p.exists():
            return {}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        out: dict[str, str] = {}
        for c in data.get("chapters", []):
            if isinstance(c, dict) and c.get("chapter_number") is not None:
                cid = f"ch{int(c['chapter_number']):02d}"
                role = c.get("role") or c.get("label") or ""
                if role:
                    out[cid] = str(role)
        return out

    def _load_words(self, cid: str) -> list[dict]:
        """words [{word,start,end}] de chXX_timestamps.json (lista pura o {'words':[]})."""
        p = self.audio_dir / f"{cid}_timestamps.json"
        if not p.exists():
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if isinstance(data, dict):
            data = data.get("words", [])
        return data if isinstance(data, list) else []

    # ─── resolución de paths (glob, disco) ───

    @staticmethod
    def _cap_id(n: int) -> str:
        return f"ch{int(n):02d}"

    @staticmethod
    def _img_idx(p: Path) -> int:
        m = re.search(r"_(\d+)\.png$", p.name)
        return int(m.group(1)) if m else 0

    def _flux_imgs(self, cid: str) -> list[Path]:
        d = self.assets_dir / f"{cid}_flux"
        if not d.exists():
            return []
        return sorted(d.glob(f"{cid}_img_*.png"), key=self._img_idx)

    def _supp_imgs(self, cid: str) -> list[Path]:
        d = self.assets_dir / f"{cid}_flux"
        if not d.exists():
            return []
        return sorted(d.glob(f"{cid}_supp_*.png"), key=self._img_idx)

    def resolve_clip(self, cid: str) -> Path | None:
        d = self.assets_dir / f"{cid}_veo"
        if not d.exists():
            return None
        clips = sorted(d.glob(f"{cid}_clip_*.mp4"))
        return clips[0] if clips else None

    def resolve_audio(self, cid: str) -> Path | None:
        for ext in AUDIO_EXTS:
            p = self.audio_dir / f"{cid}{ext}"
            if p.exists():
                return p
        # fallback glob (por si la extensión real difiere)
        for p in sorted(self.audio_dir.glob(f"{cid}.*")):
            if p.suffix.lower() in AUDIO_EXTS:
                return p
        return None

    def resolve_image(self, cid: str, name: str) -> Path | None:
        """Path del PNG validando que quede DENTRO de assets/ (anti path-traversal).
        Doble defensa: regex de nombre + relative_to(assets_dir). None si no resuelve."""
        if not _CAP_RE.match(cid) or not _IMG_NAME_RE.match(name):
            return None
        if not name.startswith(cid + "_"):
            return None
        assets_root = self.assets_dir.resolve()
        # supps e imgs flux viven en {cid}_flux; la base veo en {cid}_veo. Probamos ambos.
        for sub in (f"{cid}_flux", f"{cid}_veo"):
            cand = self.assets_dir / sub / name
            try:
                cand.resolve().relative_to(assets_root)
            except ValueError:
                continue
            if cand.exists():
                return cand
        return None

    # ─── derivaciones ───

    def _is_single(self, cid: str) -> bool:
        """single = cap VEO (1,7). Disco manda: si hay clip veo → single. Fallback al
        render_engine del script."""
        if self.resolve_clip(cid) is not None:
            return True
        return self._script.get(cid, {}).get("render_engine") == "veo"

    def _role(self, n: int, n_max: int) -> str:
        cid = self._cap_id(n)
        if cid in self._roles:
            return self._roles[cid]
        if n == 1:
            return "gancho"
        if n == n_max:
            return "cierre"
        return "desarrollo"

    def _cap_nums(self) -> list[int]:
        """Caps existentes en DISCO: unión de audio chXX.* y carpetas assets/chNN_*."""
        nums: set[int] = set()
        if self.audio_dir.exists():
            for p in self.audio_dir.glob("ch*.*"):
                m = re.match(r"ch(\d{2})\.", p.name)
                if m and p.suffix.lower() in AUDIO_EXTS:
                    nums.add(int(m.group(1)))
        if self.assets_dir.exists():
            for d in self.assets_dir.glob("ch*_*"):
                m = re.match(r"ch(\d{2})_", d.name)
                if m and d.is_dir():
                    nums.add(int(m.group(1)))
        return sorted(nums)

    # ─── API pública ───

    def caps(self) -> list[dict]:
        nums = self._cap_nums()
        n_max = nums[-1] if nums else 0
        out = []
        for n in nums:
            cid = self._cap_id(n)
            single = self._is_single(cid)
            count = len(self._supp_imgs(cid)) if single else len(self._flux_imgs(cid))
            out.append({
                "num": n,
                "cap": cid,
                "role": self._role(n, n_max),
                "count": count,
                "single": single,
            })
        return out

    def cap(self, n: int) -> dict:
        cid = self._cap_id(n)
        nums = self._cap_nums()
        n_max = nums[-1] if nums else n
        role = self._role(n, n_max)
        if self._is_single(cid):
            return self._cap_veo(cid, role)
        return self._cap_flux(cid, role)

    def _cap_flux(self, cid: str, role: str) -> dict:
        imgs = self._flux_imgs(cid)
        anchors = self._script.get(cid, {}).get("anchors", [])
        words = self._load_words(cid)
        total = float(words[-1]["end"]) if words else 0.0
        n = len(imgs)

        # Timing por anchor (MISMO matcher que fase2b) sólo si la cuenta cuadra.
        starts = None
        if anchors and words and len(anchors) == n and n > 0:
            starts = compute_anchor_starts(anchors, words)

        segments: list[dict] = []
        sync_approx = False
        if starts is not None and n > 0:
            for i, p in enumerate(imgs):
                start = starts[i]
                end = starts[i + 1] if i + 1 < n else total
                dur = end - start
                segments.append(self._seg(cid, p, anchors, i, start, end, dur))
            # guard: si algún span quedó <=0 (borde raro), caemos a reparto uniforme.
            if any(s["dur"] <= 0 for s in segments):
                segments, starts = [], None

        if starts is None:
            sync_approx = True
            seg = (total / n) if n else 0.0
            for i, p in enumerate(imgs):
                start = i * seg
                end = (i + 1) * seg
                segments.append(self._seg(cid, p, anchors, i, start, end, seg))

        return {
            "cap": cid,
            "single": False,
            "role": role,
            "count": n,
            "total": round(total, 3),
            "sync_approx": sync_approx,
            "audio_url": f"/audio?cap={cid}",
            "segments": segments,
        }

    @staticmethod
    def _seg(cid, p, anchors, i, start, end, dur) -> dict:
        return {
            "img_name": p.name,
            "anchor": anchors[i] if i < len(anchors) else None,
            "start": round(float(start), 3),
            "end": round(float(end), 3),
            "dur": round(float(dur), 3),
            "url": f"/img?cap={cid}&name={p.name}",
        }

    def _cap_veo(self, cid: str, role: str) -> dict:
        """OPCIÓN A (Omar): clip Veo + galería de supps, SIN sync fino del offset."""
        clip = self.resolve_clip(cid)
        supps = self._supp_imgs(cid)
        sa = self._script.get(cid, {}).get("supp_anchors", [])
        words = self._load_words(cid)
        total = float(words[-1]["end"]) if words else 0.0
        gallery = [
            {
                "img_name": p.name,
                "anchor": (sa[i] if i < len(sa) and sa[i] else None),
                "url": f"/img?cap={cid}&name={p.name}",
            }
            for i, p in enumerate(supps)
        ]
        return {
            "cap": cid,
            "single": True,
            "role": role,
            "count": len(supps),
            "total": round(total, 3),
            "sync_approx": False,
            "audio_url": f"/audio?cap={cid}",
            "clip_url": f"/clip?cap={cid}" if clip else None,
            "base_anchor": self._script.get(cid, {}).get("base_anchor", ""),
            "gallery": gallery,
        }

    def topic_info(self) -> dict:
        """topic_id (must-have) + título si se puede leer trivial del sync_map (opcional)."""
        title = None
        sm = self.audio_dir / "sync_map.json"
        if sm.exists():
            try:
                title = json.loads(sm.read_text(encoding="utf-8")).get("topic_title") or None
            except (json.JSONDecodeError, OSError):
                title = None
        return {"topic_id": self.topic_id, "title": title}


# ═════════════════════════════════════════════════════════════════
#  ENSAMBLAR — subprocess fase2b (patrón _rerun de mixer_server)
# ═════════════════════════════════════════════════════════════════

_ASM: dict = {"running": False, "returncode": None, "log": []}
_ASM_LOCK = threading.Lock()
_ASM_LOG_MAX = 600  # líneas


def _assemble_command() -> list[str]:
    """Comando del ensamble. FACTORIZADO para que el smoke inyecte un stub.
    sys.executable = python del venv desde donde se lanzó el server.
    v1: SOLO fase2b (el gasto que el gate protege). fase3 (packaging) queda deferido —
    ver nota en el docstring del módulo."""
    return [sys.executable, "fase2b.py", TOPIC_ID]


def _assemble_worker() -> None:
    """Thread daemon: lanza fase2b, streamea stdout+stderr al buffer _ASM."""
    try:
        # Windows: forzar utf-8 al decodificar (los emojis de fase2b tumban cp1252) +
        # PYTHONIOENCODING para que el hijo emita utf-8 (belt-and-suspenders, igual mixer).
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        proc = subprocess.Popen(
            _assemble_command(), cwd=str(BASE_DIR),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,  # nunca colgar esperando input()
            text=True, bufsize=1,
            encoding="utf-8", errors="replace", env=env,
        )
        for line in proc.stdout:
            with _ASM_LOCK:
                _ASM["log"].append(line.rstrip("\n"))
                if len(_ASM["log"]) > _ASM_LOG_MAX:
                    _ASM["log"] = _ASM["log"][-_ASM_LOG_MAX:]
        proc.wait()
        rc = proc.returncode
    except Exception as e:  # noqa: BLE001
        with _ASM_LOCK:
            _ASM["log"].append(f"[qa_studio] error lanzando fase2b: {type(e).__name__}: {e}")
        rc = -1
    with _ASM_LOCK:
        if rc == 0:
            _ASM["log"].append("✅ ensamble OK — listo para packaging (fase3).")
        else:
            _ASM["log"].append(f"❌ ensamble terminó con código {rc}.")
        _ASM["returncode"] = rc
        _ASM["running"] = False


def _start_assemble() -> dict:
    with _ASM_LOCK:
        if _ASM["running"]:
            return {"conflict": True}
        _ASM["running"] = True
        _ASM["returncode"] = None
        _ASM["log"] = []
    threading.Thread(target=_assemble_worker, daemon=True).start()
    return {"started": True}


def _assemble_status(tail: int = 60) -> dict:
    with _ASM_LOCK:
        return {
            "running": _ASM["running"],
            "returncode": _ASM["returncode"],
            "log_tail": list(_ASM["log"][-tail:]),
        }


# ═════════════════════════════════════════════════════════════════
#  HTTP handler (capa fina)
# ═════════════════════════════════════════════════════════════════

STATE: QAState | None = None  # seteado en main()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # silenciar el log ruidoso por request
        sys.stderr.write("  " + (fmt % args) + "\n")

    # ─── helpers ───

    def _qs(self) -> dict:
        return parse_qs(urlparse(self.path).query)

    def _cap_n(self) -> int:
        cap = self._qs().get("cap", [None])[0]
        if not cap or not _CAP_RE.match(cap):
            raise ValueError("falta/!inválido query param ?cap=chNN")
        return int(cap[2:])

    def _cap_str(self) -> str:
        cap = self._qs().get("cap", [None])[0]
        if not cap or not _CAP_RE.match(cap):
            raise ValueError("falta/!inválido query param ?cap=chNN")
        return cap

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path | None, content_type: str):
        if path is None or not path.exists():
            self._send_json({"error": "no encontrado"}, status=404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        # v1: archivo entero (como m09). Range requests → diferido (DEFERIDOS handoff).
        self.send_header("Accept-Ranges", "none")
        self.end_headers()
        self.wfile.write(data)

    # ─── routing ───

    def do_GET(self):
        assert STATE is not None
        try:
            route = urlparse(self.path).path
            if route == "/" or route.startswith("/index"):
                self._send_file(HTML_PATH, "text/html; charset=utf-8")
            elif route == "/caps":
                self._send_json(STATE.caps())
            elif route == "/cap":
                self._send_json(STATE.cap(self._cap_n()))
            elif route == "/img":
                name = self._qs().get("name", [""])[0]
                self._send_file(STATE.resolve_image(self._cap_str(), name), "image/png")
            elif route == "/audio":
                self._send_file(STATE.resolve_audio(self._cap_str()), "audio/mpeg")
            elif route == "/clip":
                self._send_file(STATE.resolve_clip(self._cap_str()), "video/mp4")
            elif route == "/topic":
                self._send_json(STATE.topic_info())
            elif route == "/assemble_status":
                self._send_json(_assemble_status())
            else:
                self._send_json({"error": "ruta no encontrada"}, status=404)
        except Exception as e:  # noqa: BLE001
            self._send_json({"error": f"{type(e).__name__}: {e}"}, status=500)

    def do_POST(self):
        try:
            route = urlparse(self.path).path
            if route == "/assemble":
                res = _start_assemble()
                if res.get("conflict"):
                    self._send_json({"error": "ya hay un ensamble en curso"}, status=409)
                    print("  ▶ assemble: rechazado (ya hay uno en curso)")
                else:
                    print(f"  ▶ assemble: lanzando fase2b para {TOPIC_ID[:8]}…")
                    self._send_json({"started": True})
            else:
                self._send_json({"error": "ruta no encontrada"}, status=404)
        except Exception as e:  # noqa: BLE001
            self._send_json({"error": f"{type(e).__name__}: {e}"}, status=500)


# ═════════════════════════════════════════════════════════════════
#  ARRANQUE
# ═════════════════════════════════════════════════════════════════

def _free_port(host: str, start: int) -> int:
    """Primer puerto libre desde `start` (igual idea que mixer/m09)."""
    import socket
    for port in range(start, start + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((host, port)) != 0:
                return port
    return start


def _preflight(state: QAState) -> list[str]:
    problems = []
    if not HTML_PATH.exists():
        problems.append(f"qa_studio.html no existe: {HTML_PATH}")
    if not state.audio_dir.exists() and not state.assets_dir.exists():
        problems.append(
            f"el topic {state.topic_id} no tiene assets ni audio "
            f"(esperaba {state.audio_dir} / {state.assets_dir})"
        )
    return problems


def serve(topic_id: str) -> None:
    global STATE, TOPIC_ID, PORT
    TOPIC_ID = topic_id
    STATE = QAState(topic_id, BASE_DIR)

    problems = _preflight(STATE)
    if problems:
        print("❌ Preflight falló:")
        for p in problems:
            print(f"   - {p}")
        print("   ¿Corriste fase1_5 + fase2a (audio) + el render de imágenes para este topic?")
        sys.exit(1)

    caps = STATE.caps()
    info = STATE.topic_info()
    PORT = _free_port(HOST, PORT)
    print("─" * 64)
    title = info.get("title")
    print(f"  QA STUDIO v1 — {('« ' + title + ' » · ') if title else ''}{topic_id}")
    print(f"  caps ({len(caps)}):")
    for c in caps:
        kind = "VEO (single)" if c["single"] else f"FLUX ×{c['count']}"
        print(f"     {c['cap']} — {c['role']:<14} {kind}")
    url = f"http://{HOST}:{PORT}"
    print("─" * 64)
    print(f"  ▶ Abrí en el navegador:  {url}    (Ctrl+C para frenar)")
    print("─" * 64)
    try:
        webbrowser.open(url)
    except Exception:  # noqa: BLE001
        pass
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  frenado.")
        server.shutdown()


def main():
    ap = argparse.ArgumentParser(description="QA Studio v1 — visor read-only + ENSAMBLAR.")
    ap.add_argument("--topic", default=TOPIC_ID, help="topic_id (default: el cableado)")
    args = ap.parse_args()
    serve(args.topic)


if __name__ == "__main__":
    main()
