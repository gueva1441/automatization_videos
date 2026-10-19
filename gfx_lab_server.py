"""
gfx_lab_server.py — Laboratorio interactivo de identidad (F3, HANDOFF_F3_laboratorio_identidad.md).

Mini-servidor local (http.server, sin dependencias nuevas) que sirve el lab en http://localhost:8765:

    /                         lab/identidad/index.html (Historia · Escena · Catálogo)
    /lab/<archivo>            estáticos del lab (lab.js, lab.css, catalogo.json, …)
    /player.js, /runtime.js   <hyperframes-player> y runtime del paquete hyperframes PINEADO (los mismos que
                              usa `hyperframes play`; nunca una copia)
    /composition/<ruta>       proyecto HyperFrames del preview (index.html + compositions/) con el runtime
                              inyectado al inicio del <head>, igual que `hyperframes play`; video con Range
    /media/audio              narración del cap (mp3)
    /media/photo/<i>          foto i del cap (PNG Flux); /media/thumb/<i> = miniatura JPG cacheada
    GET  /api/story           palabras (Whisper remapeado = subs), duración, escenas y tira de fotos
    GET  /api/plan            estado del lab {plan, tokens, anotado, sugerencias}; ?origin=director → plan del director
    POST /api/plan            guarda el estado del lab (lab/identidad/plan_<cap>_lab.json)
    GET  /api/context         léxico de moods dicho en la narración, facts elegibles, moods activos
    GET  /api/profile         perfil gfx activo (valores actuales de los tokens)
    POST /preview             {plan, tokens} → candado literal → gfx_project.write_project (plantillas REALES)
                              con los tokens pisando gfx_rules SOLO durante ese write_project → src del player
    GET  /summary             IDENTIDAD_<perfil>.md del estado guardado (text/markdown)
    POST /summary             estado de la página → IDENTIDAD_<perfil>.md en vivo (§4), sin escribir nada
    POST /save_identity       estado → perfil validado + plan dorado + IDENTIDAD_<perfil>.md (gfx_identity)

El preview NO es un render: el player carga la composición y GSAP la anima; el audio va por `audio-src`.

Uso:
    python gfx_lab_server.py [--video ba6c3cac-…] [--cap ch02] [--port 8765]
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import shutil
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

BASE_DIR = Path(__file__).resolve().parent
LAB_DIR = BASE_DIR / "lab" / "identidad"
DEFAULT_VIDEO = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
_HF_DIST = BASE_DIR / "script_engine" / "gfx_runtime" / "node_modules" / "hyperframes" / "dist"
PLAYER_JS = _HF_DIST / "hyperframes-player.global.js"
RUNTIME_JS = _HF_DIST / "hyperframe-runtime.js"
RUNTIME_TAG = '<script src="/runtime.js"></script>'


def inject_runtime(html: str) -> str:
    """Mismo efecto que injectRuntime de `hyperframes play`: el runtime va primero dentro del <head>
    (si no hay <head>, al principio del documento)."""
    m = re.search(r"<head[^>]*>", html, flags=re.IGNORECASE)
    if m:
        return html[:m.end()] + RUNTIME_TAG + html[m.end():]
    return RUNTIME_TAG + html


def parse_range(header: str | None, size: int) -> tuple[int, int] | None:
    """'bytes=a-b' → (a, b) inclusivo y acotado; None si no hay Range válido."""
    if not header:
        return None
    m = re.fullmatch(r"\s*bytes=(\d*)-(\d*)\s*", header)
    if not m or (not m.group(1) and not m.group(2)):
        return None
    if m.group(1):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else size - 1
    else:                                           # sufijo: últimos N bytes
        a, b = max(0, size - int(m.group(2))), size - 1
    if a >= size:
        return None
    return a, min(b, size - 1)


def safe_join(root: Path, rel: str) -> Path | None:
    """root/rel solo si queda DENTRO de root (sin ../)."""
    p = (root / rel).resolve()
    try:
        p.relative_to(root.resolve())
    except ValueError:
        return None
    return p


# ═══════════════════════════════════════════════════════════════
#  Sesión del lab: un cap de un video (datos cargados una vez al arrancar)
# ═══════════════════════════════════════════════════════════════

class LabSession:
    """Datos del cap (ChapterPlan de fase2b, escenas, palabras) + proyecto de preview."""

    def __init__(self, video_id: str, cap: str) -> None:
        import fase2b
        from script_engine.gfx_layer import remapped_words

        self.video_id, self.cap = video_id, cap
        self.out_dir = fase2b.OUTPUT_DIR / video_id
        self.work_dir = self.out_dir / "_fase2b_work"
        audio_dir = fase2b.OUTPUT_DIR / "audio" / video_id
        sync_map = json.loads((audio_dir / "sync_map.json").read_text(encoding="utf-8"))
        manifest = json.loads((self.out_dir / "assets" / "assets_manifest.json").read_text(encoding="utf-8"))
        plans = fase2b._build_plans(sync_map, manifest, video_id, audio_dir, fase2b._load_script_lookup(video_id))
        self.chplan = next(p for p in plans if p.chapter_id == cap)
        self.width, self.height, self.fps = fase2b.pipeline.video_width, fase2b.pipeline.video_height, fase2b.pipeline.fps
        # proyecto del preview: carpeta propia (NUNCA el gfx_chXX del render)
        self.project = self.work_dir / f"gfx_lab_{cap}"
        self.state_path = LAB_DIR / f"plan_{cap}_lab.json"
        self._lock = threading.Lock()
        self.version = 0
        self.raw_words, self.words = remapped_words(self.chplan)
        self.time_offset = 0.0              # el pre-pad del hook solo aplica a ch01 (no soportado en el lab)
        self._prepare_base()
        self.scenes = self._scenes(fase2b)

    # ── base.mp4 (-g 30) del preview: hardlink al del último render si existe; si no, re-encode
    def _prepare_base(self) -> None:
        from script_engine.gfx_layer import _ffprobe_duration, _reencode
        dst = self.project / "public" / "base.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            src = self.work_dir / f"gfx_{self.cap}" / "public" / "base.mp4"
            visual = self.work_dir / f"{self.cap}_{self.chplan.engine}_visual.mp4"
            if src.exists():
                try:
                    os.link(src, dst)
                except OSError:
                    shutil.copy2(src, dst)
            elif visual.exists():
                _reencode(visual, dst, self.fps)
            else:
                raise FileNotFoundError(f"sin base del cap: ni {src} ni {visual}")
        self.duration = _ffprobe_duration(dst)

    # ── escenas como en apply_gfx: anchors → cortes reales → lado tranquilo → router seguro (cache)
    def _scenes(self, fase2b: Any) -> list[Any]:
        from script_engine.gfx_director import load_chapter_context
        from script_engine.gfx_layer import assign_quiet_sides, build_scenes, snap_cuts
        from script_engine.gfx_project import GfxScene
        cache = self.project / "lab_scenes.json"
        base = self.project / "public" / "base.mp4"
        if cache.exists() and cache.stat().st_mtime >= base.stat().st_mtime:
            return [GfxScene(**d) for d in json.loads(cache.read_text(encoding="utf-8"))]
        ctx = load_chapter_context(self.video_id, self.chplan)
        scenes = build_scenes(self.chplan, ctx["script_chapter"], self.raw_words, self.duration, self.time_offset)
        scenes = assign_quiet_sides(snap_cuts(scenes, base, self.fps), base)
        routed, _ = fase2b._route_safe([self.chplan], self.video_id, {})
        base_clip = self.work_dir / f"{self.cap}_{self.chplan.engine}_visual.mp4"
        safe = fase2b._safe_scenes_for(self.chplan, base_clip, routed.get(self.cap, {})) or {}
        for si, sv in safe.items():
            if 0 <= si < len(scenes) and len(scenes) > 1:
                scenes[si].safe = sv
        cache.write_text(json.dumps([s.__dict__ for s in scenes], ensure_ascii=False, indent=1), encoding="utf-8")
        return scenes

    # ── planes
    def director_plan(self) -> dict[str, Any]:
        f = self.work_dir / f"gfx_plan_{self.cap}.resolved.json"
        return json.loads(f.read_text(encoding="utf-8"))["plan"]

    def lab_state(self) -> dict[str, Any]:
        """Estado del lab: {plan, tokens, …}. Sin archivo → plan del director y sin tokens cambiados."""
        if self.state_path.exists():
            st = json.loads(self.state_path.read_text(encoding="utf-8"))
            st.setdefault("tokens", {})
            return st
        return {"plan": self.director_plan(), "tokens": {}}

    def lab_plan(self) -> dict[str, Any]:
        return self.lab_state()["plan"]

    def save_lab_state(self, state: dict[str, Any]) -> None:
        """Guarda el estado completo que manda la página (plan, tokens y lo que §C agregue)."""
        if "plan" not in state:
            raise ValueError("estado sin plan")
        bad = sorted(set(state.get("tokens") or {}) - _rule_fields())
        if bad:
            raise ValueError(f"tokens desconocidos: {bad}")
        out = {"video_id": self.video_id, "cap": self.cap, **state, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")}
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── contexto del cap: fuentes del candado, facts elegibles, léxico de moods en la narración
    def context(self) -> dict[str, Any]:
        if getattr(self, "_ctx_cache", None) is None:
            from gfx_config import active_moods
            from script_engine.gfx_director import load_chapter_context
            ctx = load_chapter_context(self.video_id, self.chplan)
            moods = active_moods()
            lex: list[dict[str, Any]] = []
            for w in self.story()["words"]:
                key = re.sub(r"[^\wáéíóúüñ]", "", w["word"].lower())
                for cat, m in moods.items():
                    if key in (m.get("triggers") or {}):
                        lex.append({"i": w["i"], "word": w["word"], "start": w["start"], "category": cat,
                                    "layer": m.get("layer"), "weight": m["triggers"][key],
                                    "icon": (m.get("icon_words") or {}).get(key), "icon_anim": m.get("icon_anim")})
            elig: dict[int, bool] = ctx.get("eligible") or {}          # {fact_idx: foráneo}
            facts = [{"idx": i, "text": f, "eligible": i in elig, "foreign": bool(elig.get(i)),
                      "source": ctx["fact_source"].get(i, "")} for i, f in enumerate(ctx["facts"])]
            self._ctx = ctx
            self._ctx_cache = {"chapter_number": ctx["chapter_number"], "facts": facts, "lexicon_hits": lex,
                               "moods": {k: {"layer": v.get("layer"), "icon_anim": v.get("icon_anim")}
                                         for k, v in moods.items()},
                               "next_chapter": bool(ctx.get("next_sources"))}
        return self._ctx_cache

    def locked(self, plan: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Candado literal (§6) sobre el plan del lab. La pregunta de cierre escrita por Omar (manual: true)
        es la ÚNICA excepción: no pasa por question_ok y queda marcada como manual."""
        from script_engine.gfx_literal_lock import lock
        self.context()
        manual_q = plan.get("chapter_question") if (plan.get("chapter_question") or {}).get("manual") else None
        p = dict(plan)
        if manual_q:
            p["chapter_question"] = None
        ok, rejected = lock(p, self._ctx["sources"], chapter_number=self._ctx["chapter_number"],
                            question_sources=self._ctx.get("next_sources"))
        if manual_q:
            ok["chapter_question"] = manual_q
        return ok, rejected

    # ── historia
    def story(self) -> dict[str, Any]:
        photos = []
        scene_img = self.chplan.asset_paths if self.chplan.engine == "flux" else []
        for s in self.scenes:
            photos.append({"idx": s.idx, "start": s.start, "end": s.end, "rank": s.rank,
                           "quiet_side": s.quiet_side, "safe": bool(s.safe),
                           "url": f"/media/photo/{s.idx}" if s.idx < len(scene_img) else None,
                           "thumb": f"/media/thumb/{s.idx}" if s.idx < len(scene_img) else None})
        words = [{"i": i, "word": str(w.get("word", "")).strip(), "start": round(float(w["start"]), 3),
                  "end": round(float(w["end"]), 3)}
                 for i, w in enumerate(self.words) if str(w.get("word", "")).strip()]
        return {"video_id": self.video_id, "cap": self.cap, "duration": round(self.duration, 3),
                "audio_duration": self.chplan.audio_duration, "width": self.width, "height": self.height,
                "fps": self.fps, "audio_url": "/media/audio", "words": words, "photos": photos}

    def photo_path(self, idx: int, thumb: bool = False) -> Path | None:
        """Foto idx del cap; thumb=True → JPG de 480 px de ancho cacheado en el proyecto del lab."""
        if not (self.chplan.engine == "flux" and 0 <= idx < len(self.chplan.asset_paths)):
            return None
        src = Path(self.chplan.asset_paths[idx])
        if not thumb:
            return src
        dst = self.project / "lab_thumbs" / f"{src.stem}.jpg"
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            from PIL import Image
            dst.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(src) as im:
                im = im.convert("RGB")
                im.thumbnail((480, 480))
                im.save(dst, "JPEG", quality=82)
        return dst

    # ── §C: resumen en vivo y Guardar identidad
    def _catalog(self) -> dict[str, Any]:
        return json.loads((LAB_DIR / "catalogo.json").read_text(encoding="utf-8"))

    def _sugerencias(self) -> list[dict[str, Any]]:
        f = LAB_DIR / f"sugerencias_{self.cap}.json"
        return json.loads(f.read_text(encoding="utf-8"))["sugerencias"] if f.exists() else []

    def cues_for(self, plan: dict[str, Any], tokens: dict[str, Any]) -> tuple[dict[str, Any], list, list]:
        """(plan con candado, rechazados, cues) sin escribir el proyecto."""
        from script_engine import gfx_project
        ok, rejected = self.locked(plan)
        with rules_override(tokens or {}):
            cues = gfx_project.cue_events(ok, self.scenes, self.fps)
        return ok, rejected, cues

    def summary(self, state: dict[str, Any]) -> str:
        from dataclasses import asdict
        import gfx_config
        from script_engine.gfx_identity import summary_md
        _, _, cues = self.cues_for(state["plan"], state.get("tokens") or {})
        return summary_md(state, self._catalog(), cues, self.story()["words"], asdict(gfx_config.gfx_rules),
                          profile=gfx_config.active_profile_name(), cap=self.cap, video_id=self.video_id,
                          sugerencias=self._sugerencias())

    def save_identity(self, state: dict[str, Any]) -> dict[str, str]:
        import gfx_config
        from script_engine.gfx_identity import save_identity
        with self._lock:
            self.save_lab_state(state)
            ok, rejected, _ = self.cues_for(state["plan"], state.get("tokens") or {})
            return save_identity(state, profile=gfx_config.active_profile_name(), cap=self.cap,
                                 video_id=self.video_id, locked_plan=ok, rejected=rejected,
                                 summary=self.summary(state), md_dir=LAB_DIR)

    # ── preview: plantillas REALES vía gfx_project.write_project
    def preview(self, plan: dict[str, Any], tokens: dict[str, Any] | None = None) -> dict[str, Any]:
        """plan (+ tokens del perfil que el lab está probando) → candado literal → write_project.
        Los tokens pisan gfx_rules SOLO durante este write_project (se restauran siempre)."""
        from script_engine import gfx_project
        with self._lock:
            t = time.time()
            ok, rejected = self.locked(plan)
            with rules_override(tokens or {}):
                gfx_project.write_project(ok, self.scenes, self.project, duration=self.duration, width=self.width,
                                          height=self.height, fps=self.fps)
                cues = gfx_project.cue_events(ok, self.scenes, self.fps)
            self.version += 1
            return {"src": f"/composition/index.html?v={self.version}", "ms": round(1000 * (time.time() - t)),
                    "cues": cues, "rejected": rejected}


def _rule_fields() -> frozenset[str]:
    from gfx_config import _RULE_FIELDS
    return _RULE_FIELDS


class rules_override:
    """Context manager: gfx_project.gfx_rules / GRADE_VARIANTS con los tokens del lab encima del perfil activo."""

    def __init__(self, tokens: dict[str, Any]) -> None:
        bad = sorted(set(tokens) - _rule_fields())
        if bad:
            raise ValueError(f"tokens desconocidos: {bad}")
        self.tokens = tokens

    def __enter__(self) -> None:
        from dataclasses import replace
        import gfx_config
        from script_engine import gfx_project
        self._saved = (gfx_project.gfx_rules, gfx_project.GRADE_VARIANTS)
        if self.tokens:
            rules = replace(gfx_config.gfx_rules, **self.tokens)
            gfx_project.gfx_rules = rules
            gfx_project.GRADE_VARIANTS = gfx_config.grade_variants(rules)

    def __exit__(self, *exc: Any) -> None:
        from script_engine import gfx_project
        gfx_project.gfx_rules, gfx_project.GRADE_VARIANTS = self._saved


# ═══════════════════════════════════════════════════════════════
#  HTTP
# ═══════════════════════════════════════════════════════════════

class LabHandler(BaseHTTPRequestHandler):
    session: LabSession                         # se asigna en main()
    server_version = "gfx-lab/1"

    def log_message(self, fmt: str, *args: Any) -> None:     # silencio salvo errores
        if args and str(args[1] if len(args) > 1 else "").startswith(("4", "5")):
            sys.stderr.write("[lab] " + fmt % args + "\n")

    # ── respuestas
    def _send(self, body: bytes, ctype: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, obj: Any, status: int = 200) -> None:
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def _error(self, status: int, msg: str) -> None:
        self._json({"error": msg}, status)

    def _file(self, path: Path, ctype: str | None = None) -> None:
        if not path.exists() or not path.is_file():
            return self._error(404, f"no existe {path.name}")
        ctype = ctype or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if ctype.startswith("text/html"):
            ctype = "text/html; charset=utf-8"
        size = path.stat().st_size
        rng = parse_range(self.headers.get("Range"), size)
        if rng is None:
            self.send_response(200)
            a, b = 0, size - 1
        else:
            a, b = rng
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Range", f"bytes {a}-{b}/{size}")
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(b - a + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if self.command == "HEAD":
            return
        with path.open("rb") as fh:
            fh.seek(a)
            left = b - a + 1
            try:
                while left > 0:
                    chunk = fh.read(min(1 << 20, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                pass                              # el player cancela rangos al hacer seek

    def _body(self) -> Any:
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    # ── rutas
    def do_HEAD(self) -> None:
        self.do_GET()

    def do_GET(self) -> None:
        u = urlparse(self.path)
        path = unquote(u.path)
        s = self.session
        try:
            if path in ("/", "/index.html"):
                return self._file(LAB_DIR / "index.html")
            if path.startswith("/lab/"):
                p = safe_join(LAB_DIR, path[len("/lab/"):])
                return self._file(p) if p else self._error(403, "fuera del lab")
            if path == "/player.js":
                return self._file(PLAYER_JS, "application/javascript")
            if path == "/runtime.js":
                return self._file(RUNTIME_JS, "application/javascript")
            if path.startswith("/composition/"):
                p = safe_join(s.project, path[len("/composition/"):])
                if p is None:
                    return self._error(403, "fuera del proyecto")
                if p.suffix == ".html" and p.exists():
                    return self._send(inject_runtime(p.read_text(encoding="utf-8")).encode("utf-8"),
                                      "text/html; charset=utf-8")
                return self._file(p)
            if path == "/media/audio":
                return self._file(Path(s.chplan.audio_path), "audio/mpeg")
            m = re.fullmatch(r"/media/(photo|thumb)/(\d+)", path)
            if m:
                p = s.photo_path(int(m.group(2)), thumb=m.group(1) == "thumb")
                return self._file(p) if p else self._error(404, "sin foto")
            if path == "/api/story":
                return self._json(s.story())
            if path == "/api/plan":
                q = parse_qs(u.query)
                if q.get("origin") == ["director"]:
                    return self._json({"plan": s.director_plan(), "tokens": {}, "origin": "director"})
                return self._json({**s.lab_state(), "origin": "lab" if s.state_path.exists() else "director"})
            if path == "/api/context":
                return self._json(s.context())
            if path == "/summary":
                return self._send(s.summary(s.lab_state()).encode("utf-8"), "text/markdown; charset=utf-8")
            if path == "/api/profile":
                from dataclasses import asdict
                import gfx_config
                return self._json({"name": gfx_config.active_profile_name(), "rules": asdict(gfx_config.gfx_rules)})
            return self._error(404, f"ruta desconocida {path}")
        except Exception as e:  # noqa: BLE001 — el lab nunca se cae por un pedido
            return self._error(500, f"{type(e).__name__}: {e}")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        s = self.session
        try:
            if path == "/preview":
                body = self._body()
                st = s.lab_state()
                plan = body.get("plan") or st["plan"]
                tokens = body["tokens"] if "tokens" in body else st["tokens"]
                return self._json(s.preview(plan, tokens))
            if path == "/api/plan":
                s.save_lab_state(self._body())
                return self._json({"ok": True})
            if path == "/summary":
                return self._json({"md": s.summary(self._body())})
            if path == "/save_identity":
                return self._json({"ok": True, "archivos": s.save_identity(self._body())})
            return self._error(404, f"ruta desconocida {path}")
        except Exception as e:  # noqa: BLE001
            return self._error(500, f"{type(e).__name__}: {e}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Laboratorio de identidad gfx (F3)")
    ap.add_argument("--video", default=DEFAULT_VIDEO)
    ap.add_argument("--cap", default="ch02")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    if args.cap == "ch01":
        print("⚠  ch01 lleva pre-pad del hook: el lab no lo soporta todavía (usar ch02/ch05)")
    t = time.time()
    session = LabSession(args.video, args.cap)
    st = session.lab_state()
    first = session.preview(st["plan"], st["tokens"])
    LabHandler.session = session
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), LabHandler)
    print(f"🧪 lab {args.cap} listo en {time.time() - t:.1f}s (preview inicial {first['ms']} ms, "
          f"{len(session.scenes)} escenas) → http://localhost:{args.port}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
