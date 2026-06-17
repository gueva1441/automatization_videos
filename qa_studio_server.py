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
import shutil
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
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
                "veo_position": str(item.get("veo_position", "start")).lower() or "start",
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

    def _is_veo(self, cid: str) -> bool:
        """cap VEO = tiene clip en disco, o el script lo marca render_engine=veo."""
        if self.resolve_clip(cid) is not None:
            return True
        return self._script.get(cid, {}).get("render_engine") == "veo"

    def _veo_position(self, cid: str) -> str:
        """'start' (clip primero — Option A) | 'end' (clip último — modelo timeline).
        Default 'start' (compat con caps veo legacy sin el campo)."""
        return self._script.get(cid, {}).get("veo_position", "start") or "start"

    def _is_single(self, cid: str) -> bool:
        """v1.7: Option A retirada — TODOS los caps usan la estructura timeline (los veo
        con el clip como segmento, primero si veo_position=='start', último si 'end').
        Se mantiene el método (lo usa caps()/print) devolviendo siempre False."""
        return False

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
            # count = nº de FOTOS (el clip nunca cuenta). veo (start o end) → supps; flux → imgs.
            if self._is_veo(cid):
                count = len(self._supp_imgs(cid))
            else:
                count = len(self._flux_imgs(cid))
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
        if self._is_veo(cid):
            if self._veo_position(cid) == "end":
                return self._cap_veo_timeline(cid, role)  # v1.1: clip al final → timeline
            return self._cap_veo(cid, role)               # Option A: clip primero + galería
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
            "is_clip": False,
            "img_name": p.name,
            "anchor": anchors[i] if i < len(anchors) else None,
            "start": round(float(start), 3),
            "end": round(float(end), 3),
            "dur": round(float(dur), 3),
            "url": f"/img?cap={cid}&name={p.name}",
        }

    def _cap_veo(self, cid: str, role: str) -> dict:
        """v1.7 — cap veo con veo_position=='start': MISMA estructura timeline que los
        flux y que el cap 7, pero con el CLIP como PRIMER segmento (va primero, ocupa
        [0, primer supp]); las supps se reparten después. Antes era "Option A" (galería),
        pero ya tenemos el sync por ítem → unificamos la vista.

        Sincronizamos por los SUPPS solos (el base_anchor del clip suele venir con números
        normalizados —ej. "1948"→"mil novecientos cuarenta y ocho"— que no matchean el
        texto crudo). Fallback sin sync → clip como tile inicial + supps uniformes."""
        clip = self.resolve_clip(cid)
        supps = self._supp_imgs(cid)
        sa = self._script.get(cid, {}).get("supp_anchors", [])
        base_anchor = self._script.get(cid, {}).get("base_anchor", "")
        words = self._load_words(cid)
        total = float(words[-1]["end"]) if words else 0.0
        n = len(supps)
        has_clip = clip is not None
        clip_url = f"/clip?cap={cid}" if has_clip else None

        starts = None
        if n and words and len(sa[:n]) == n:
            starts = compute_anchor_starts(list(sa[:n]), words)

        segments: list[dict] = []
        sync_approx = False
        # camino sincronizado: clip [0, primer supp] + supps tiled.
        matched = starts is not None and starts[0] > 0
        if matched:
            segments.append({
                "is_clip": True, "img_name": None, "anchor": base_anchor or None,
                "start": 0.0, "end": round(starts[0], 3), "dur": round(starts[0], 3),
                "clip_url": clip_url,
            })
            for k, p in enumerate(supps):
                s_start = starts[k]
                s_end = starts[k + 1] if (k + 1) < n else total
                segments.append(self._seg(cid, p, sa, k, s_start, s_end, s_end - s_start))
            if any(s["dur"] <= 0 for s in segments):
                segments, matched = [], False

        if not matched:
            sync_approx = True
            if has_clip:   # clip como tile inicial SIN sync
                segments.append({
                    "is_clip": True, "img_name": None, "anchor": base_anchor or None,
                    "start": None, "end": None, "dur": None, "clip_url": clip_url,
                })
            seg = (total / n) if n else 0.0
            for k, p in enumerate(supps):
                segments.append(self._seg(cid, p, sa, k, k * seg, (k + 1) * seg, seg))

        return {
            "cap": cid,
            "single": False,            # v1.7: ya no es Option A → timeline
            "role": role,
            "count": n,
            "total": round(total, 3),
            "sync_approx": sync_approx,
            "audio_url": f"/audio?cap={cid}",
            "segments": segments,
            "has_clip": has_clip,
        }

    def _cap_veo_timeline(self, cid: str, role: str) -> dict:
        """v1.1 — cap veo con veo_position=='end': el clip va ÚLTIMO, así los supps
        arrancan en offset=0 y se distribuyen IDÉNTICO a un cap flux (MISMO matcher,
        compute_anchor_starts). El clip es el segmento final.

        ⚠ Precisión a propósito: el `start` del clip sale de dónde arranca SU narración
        (base_anchor), no del frame exacto donde fase2b concatena el clip visual. Para el
        QA es lo correcto (querés ver que supps+clip ilustran su narración); el borde
        exacto del clip queda aproximado."""
        sc = self._script.get(cid, {})
        supp_anchors = sc.get("supp_anchors", [])
        base_anchor = sc.get("base_anchor", "")
        clip = self.resolve_clip(cid)
        imgs = self._supp_imgs(cid)
        words = self._load_words(cid)
        total = float(words[-1]["end"]) if words else 0.0
        n = len(imgs)
        has_base = bool(base_anchor)

        all_anchors = list(supp_anchors[:n]) + ([base_anchor] if has_base else [])
        # ¿la cuenta cuadra para el matcher? supps + (1 clip si hay base_anchor).
        expect = n + (1 if has_base else 0)
        starts = None
        if all_anchors and words and len(all_anchors) == expect and expect > 0:
            starts = compute_anchor_starts(all_anchors, words)

        segments: list[dict] = []
        sync_approx = False
        if starts is not None:
            # supps: cada uno hasta el arranque del siguiente anchor (supp o clip).
            for i, p in enumerate(imgs):
                start = starts[i]
                end = starts[i + 1] if i + 1 < len(starts) else total
                dur = end - start
                segments.append(self._seg(cid, p, supp_anchors, i, start, end, dur))
            if has_base:
                cstart = starts[n]
                segments.append({
                    "is_clip": True,
                    "img_name": None,
                    "anchor": base_anchor,
                    "start": round(cstart, 3),
                    "end": round(total, 3),
                    "dur": round(total - cstart, 3),
                    "clip_url": f"/clip?cap={cid}" if clip else None,
                })
            if any(s["dur"] <= 0 for s in segments):
                segments, starts = [], None

        if starts is None:
            # fallback: supps con reparto uniforme + clip como tile final SIN sync.
            sync_approx = True
            seg = (total / n) if n else 0.0
            for i, p in enumerate(imgs):
                start = i * seg
                end = (i + 1) * seg
                segments.append(self._seg(cid, p, supp_anchors, i, start, end, seg))
            if has_base:
                segments.append({
                    "is_clip": True,
                    "img_name": None,
                    "anchor": base_anchor,
                    "start": None,
                    "end": None,
                    "dur": None,
                    "clip_url": f"/clip?cap={cid}" if clip else None,
                })

        return {
            "cap": cid,
            "single": False,
            "role": role,
            "count": n,
            "total": round(total, 3),
            "sync_approx": sync_approx,
            "audio_url": f"/audio?cap={cid}",
            "segments": segments,
            "has_clip": has_base and clip is not None,
        }

    def resolve_fix_entry(self, img_name: str) -> dict | None:
        """Re-lee data/scripts/{topic}.json FRESCO y ubica la entrada del prompt para
        `img_name` (Zona 1 fix). El kind (img|supp) sale del PROPIO img_name → evita la
        ambigüedad _img_ vs _supp_. Normaliza igual que asset_manager._iter_image_items
        (dict nuevo o str legacy). None si no resuelve.

        Devuelve {cap, img_name, kind, idx, prompt, art_profile, subject_ref, narration_anchor}.
        idx es 1-indexed (el de _img_NN / _supp_NN)."""
        m = re.match(r"^(ch\d{2})_(img|supp)_(\d+)\.png$", img_name)
        if not m:
            return None
        cid, kind, idx = m.group(1), m.group(2), int(m.group(3))
        if not self.script_path.exists():
            return None
        try:
            raw = json.loads(self.script_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        chap = next(
            (c for c in raw.get("chapters", [])
             if c.get("chapter_number") == int(cid[2:])),
            None,
        )
        if not chap:
            return None
        key = "supplemental_image_prompts" if kind == "supp" else "image_prompts"
        items = chap.get(key) or []
        if not isinstance(items, list) or not (1 <= idx <= len(items)):
            return None
        rawi = items[idx - 1]
        if isinstance(rawi, dict):
            prompt = str(rawi.get("prompt", "") or "").strip()
            art_profile = rawi.get("art_profile") or chap.get("art_profile") or ""
            subject_ref = rawi.get("subject_ref") if "subject_ref" in rawi else chap.get("subject_ref")
            anchor = (rawi.get("narration_anchor") or "").strip()
        else:
            prompt = str(rawi or "").strip()
            art_profile = chap.get("art_profile") or ""
            subject_ref = chap.get("subject_ref")
            anchor = ""
        if not prompt:
            return None
        return {
            "cap": cid, "img_name": img_name, "kind": kind, "idx": idx,
            "prompt": prompt, "art_profile": art_profile,
            "subject_ref": subject_ref or None, "narration_anchor": anchor,
        }

    def resolve_clip_entry(self, cap: str) -> dict | None:
        """Re-lee el script FRESCO y saca, para un cap VEO, el video_prompt (movimiento/
        cámara) + image_prompt (contexto del primer frame) + base_anchor + el path del
        primer frame y del clip de salida. None si no es un cap veo / no resuelve.

        Schema: el script usa singular `video_prompt`/`image_prompt` en caps veo; toleramos
        también listas `video_prompts[]`/`image_prompts[]` (schema runtime) por las dudas."""
        if not _CAP_RE.match(cap) or not self._is_veo(cap):
            return None
        if not self.script_path.exists():
            return None
        try:
            raw = json.loads(self.script_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        chap = next(
            (c for c in raw.get("chapters", [])
             if c.get("chapter_number") == int(cap[2:])),
            None,
        )
        if not chap:
            return None

        def _first(singular, plural):
            v = chap.get(singular)
            if not v:
                lst = chap.get(plural)
                v = lst[0] if isinstance(lst, list) and lst else ""
            return str(v or "").strip()

        video_prompt = _first("video_prompt", "video_prompts")
        if not video_prompt:
            return None
        image_prompt = _first("image_prompt", "image_prompts")
        base_anchor = (chap.get("narration_anchor") or "").strip()

        veo_dir = self.assets_dir / f"{cap}_veo"
        frames = sorted(veo_dir.glob(f"{cap}_img_*.png")) if veo_dir.exists() else []
        first_frame = frames[0] if frames else (veo_dir / f"{cap}_img_01.png")
        out_clip = self.resolve_clip(cap) or (veo_dir / f"{cap}_clip_01.mp4")
        return {
            "cap": cap,
            "video_prompt": video_prompt,
            "image_prompt": image_prompt,
            "base_anchor": base_anchor,
            "first_frame": str(first_frame),
            "out_clip": str(out_clip),
            "clip_name": Path(out_clip).name,
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
#  ZONA 1 — FIX DE FOTO (/fix_image) · regenera 1 imagen sola
#  (clona el molde threaded de _ASM; reusa asset_manager + gemini, read-only)
# ═════════════════════════════════════════════════════════════════

# Instrucción DEDICADA del rewrite (NO la de m03, que es traductor). Embebe las
# reglas de MODEL_PROMPTING_RULES §1 (Flux) y §1.8 (content-safety). El gate es Omar
# mirando la IMAGEN; este LLM solo aplica el cambio que pide, en inglés, cuidando las
# reglas. NUNCA se le muestra el prompt a Omar para aprobar.
_FIX_REWRITE_INSTRUCTION = """\
Sos un editor de prompts de imagen para Flux 2 Pro (generación documental en 9:16).
Te paso un PROMPT ACTUAL en inglés, su narration_anchor (lo que la imagen DEBE
ilustrar), y un CAMBIO que pide el usuario en español. Tu tarea: devolver el prompt
reescrito EN INGLÉS aplicando ESE cambio y manteniendo TODO lo demás (sujeto, setting,
estilo, consistencia del personaje). NO inventes una escena nueva: editás la existente.

El narration_anchor es la VERDAD de lo que la toma debe mostrar — no te alejes de él.

REGLAS DE FLUX (inviolables — el prompt resultante DEBE cumplirlas):
1. Subject-first: el sujeto principal va al INICIO, nunca después de un prefijo técnico
   largo. El estilo/cámara/iluminación van integrados o al final, no al principio.
2. SIN negativos: Flux 2 NO soporta prompts negativos. No escribas "no people", "no
   text", "no blur". Para excluir → describí en positivo: "an empty scene", "clean
   surfaces", "sharp focus throughout".
3. Descriptores físicos (etnia, edad, rasgos, ropa con período) INTEGRADOS al bloque del
   sujeto al inicio, no esparcidos al final (lo que llega tarde, llega diluido).
4. Prosa natural descriptiva, NO keyword-soup ni CSV de props al final.
5. Longitud objetivo 30–80 palabras (medium). Si el cambio no lo exige, no lo infles.
6. Para fotorealismo, cámara/lente/película específicas > genéricos.

CONTENT-SAFETY (§1.8 — Flux devuelve 422 y rechaza; evitalo SIEMPRE):
- Muerte → calma previa. NUNCA cuerpos/figuras inmóviles ni aftermath de muerte (aunque
  sea "quieto" dispara el filtro). Mostrá la escena VIVA y tranquila anterior (la narración
  hace el horror, la imagen muestra la calma): aldea al atardecer, ganado pastando, luz de
  lámpara. Aplica a personas, animales y víctimas masivas.
- Aparato de ejecución (horca, mecanismo de matar): NUNCA el mecanismo entero, ni aunque no
  haya gente. Reemplazo = el espacio cargado y vacío (luz dramática + escala opresiva + UN
  objeto que implica lo que pasó: una soga sola, un banco volcado).
- Si el cambio del usuario empuja hacia muerte/aparato explícito, aplicá el pivote y cumplí
  el espíritu del pedido sin disparar el filtro.

Devolvé SOLO el JSON {"new_prompt": "<prompt reescrito en inglés>"}. Sin markdown.
"""

_FIX: dict = {"running": False, "done": False, "ok": None, "reason": None, "img_name": None}
_FIX_LOCK = threading.Lock()


def _build_fix_user_prompt(entry: dict, feedback: str) -> str:
    return (
        f"PROMPT ACTUAL (inglés, para Flux):\n{entry['prompt']}\n\n"
        f"narration_anchor (lo que la imagen DEBE ilustrar): "
        f"{entry.get('narration_anchor') or '(sin anchor)'}\n\n"
        f"CAMBIO QUE PIDE EL USUARIO (español): {feedback}\n\n"
        "Reescribí el prompt en inglés aplicando ese cambio, manteniendo todo lo demás "
        "y respetando las reglas. Devolvé solo {\"new_prompt\": ...}."
    )


def _invalidate_baked(state, topic_id: str, cap: str) -> None:
    """Borra el clip visual horneado del cap en _fase2b_work para que ENSAMBLAR (fase2b)
    RE-RENDERICE ese cap desde el asset nuevo (PNG del fix de foto o clip del fix de clip).
    El fix pisa el mismo filename (conteo intacto → NO toca el bug de manifest-honesto), pero
    en modo reuse-baked fase2b reusaría el MP4 viejo y el fix no llegaría al video. Borramos un
    artefacto DERIVADO: no toca fase2b ni data sagrada. Cubre ambos engines (flux + hybrid)."""
    work = state.base / "output" / topic_id / "_fase2b_work"
    for stale in (f"{cap}_flux_visual.mp4", f"{cap}_hybrid_visual.mp4"):
        try:
            (work / stale).unlink(missing_ok=True)
        except OSError:
            pass


def _fix_core(
    state: "QAState",
    topic_id: str,
    cap: str,
    img_name: str,
    feedback: str,
    *,
    rewrite_fn=None,        # (system_instruction, user_prompt) -> {"new_prompt": str}
    seed_fn=None,           # (video_id, subject_ref) -> int | None
    generate_fn=None,       # (prompt, art_profile, out_path, use_ultra, seed) -> dict
    is_hook_fn=None,        # (cap) -> bool
    content_rejected_exc=None,
    now_ts: str | None = None,
) -> tuple[bool, str | None]:
    """Lógica del fix, TESTEABLE con deps inyectadas (sin red ni Flux real).
    Devuelve (ok, reason). En producción las deps se resuelven lazy desde
    asset_manager + gemini_helpers (import pesado → solo al pedir un fix, no al boot)."""
    # ── deps reales (lazy; los tests pasan TODAS para no importar pesado) ──
    if rewrite_fn is None:
        from gemini_helpers import call_flash_json, types  # noqa: PLC0415
        _schema = types.Schema(
            type=types.Type.OBJECT, required=["new_prompt"],
            properties={"new_prompt": types.Schema(type=types.Type.STRING)},
        )
        rewrite_fn = lambda si, up: call_flash_json(  # noqa: E731
            prompt=up, system_instruction=si, response_schema=_schema)
    if seed_fn is None or generate_fn is None or is_hook_fn is None or content_rejected_exc is None:
        import asset_manager as am  # noqa: PLC0415
        seed_fn = seed_fn or am._seed_for_subject
        generate_fn = generate_fn or am._generate_flux_image_at
        is_hook_fn = is_hook_fn or am._is_hook_chapter
        content_rejected_exc = content_rejected_exc or am.ContentRejectedError

    # 1. Resolver la entrada en el script (fresco).
    entry = state.resolve_fix_entry(img_name)
    if not entry:
        return False, "no se pudo resolver la entrada del prompt en el script"

    # 2. Rewrite del prompt (obedece reglas Flux).
    try:
        res = rewrite_fn(_FIX_REWRITE_INSTRUCTION, _build_fix_user_prompt(entry, feedback))
        new_prompt = str((res or {}).get("new_prompt", "")).strip()
        if not new_prompt:
            return False, "el rewrite devolvió un prompt vacío"
    except Exception as e:  # noqa: BLE001
        return False, f"rewrite falló: {type(e).__name__}: {str(e)[:140]}"

    # 3. Resolver el path real (el que el visor ya renderiza) + backup ANTES de pisar.
    out_path = state.resolve_image(cap, img_name)
    if out_path is None:
        out_path = state.assets_dir / f"{cap}_flux" / img_name
    try:
        if out_path.exists():
            bdir = state.assets_dir / "_qa_backups"
            bdir.mkdir(parents=True, exist_ok=True)
            ts = now_ts or datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(out_path, bdir / f"{img_name}.{ts}.bak.png")
    except OSError as e:
        return False, f"backup falló: {e}"

    # 4. seed por sujeto (consistencia de personaje) + 5. generar (pisa el mismo nombre).
    seed = seed_fn(topic_id, entry.get("subject_ref"))
    try:
        # ⚠ use_ultra: flux_config tiene ultra_model == standard_model (flux-2-pro) →
        #   use_ultra es cosmético hoy (mismo modelo). Respetamos _is_hook_chapter igual.
        generate_fn(new_prompt, entry.get("art_profile", ""), out_path,
                    use_ultra=is_hook_fn(cap), seed=seed)
    except content_rejected_exc as e:
        return False, f"filtro: {str(e)[:160]}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:160]}"

    # Invalidar el baked → ENSAMBLAR re-renderiza el cap desde el PNG nuevo.
    _invalidate_baked(state, topic_id, cap)

    return True, None


def _fix_worker(cap: str, img_name: str, feedback: str) -> None:
    """Thread daemon: corre _fix_core y cierra el status."""
    try:
        ok, reason = _fix_core(STATE, TOPIC_ID, cap, img_name, feedback)
    except Exception as e:  # noqa: BLE001
        ok, reason = False, f"{type(e).__name__}: {e}"
    with _FIX_LOCK:
        _FIX.update(running=False, done=True, ok=ok, reason=reason)
    tag = "✓ ok" if ok else f"✗ {reason}"
    print(f"  ✎ fix {img_name}: {tag}")


def _start_fix(cap: str, img_name: str, feedback: str) -> dict:
    with _FIX_LOCK:
        if _FIX["running"]:
            return {"conflict": True}
        _FIX.update(running=True, done=False, ok=None, reason=None, img_name=img_name)
    threading.Thread(target=_fix_worker, args=(cap, img_name, feedback), daemon=True).start()
    return {"started": True}


def _fix_status() -> dict:
    with _FIX_LOCK:
        return {
            "running": _FIX["running"],
            "done": _FIX["done"],
            "ok": _FIX["ok"],
            "reason": _FIX["reason"],
            "img_name": _FIX["img_name"],
        }


# ═════════════════════════════════════════════════════════════════
#  ZONA 1.5 — FIX DE CLIP (/fix_clip) · regenera el video de un cap veo
#  Reescribe el video_prompt (MOVIMIENTO/cámara), mantiene el MISMO primer frame.
#  Reusa el estado _FIX + _FIX_LOCK (un solo regen a la vez: foto O clip).
# ═════════════════════════════════════════════════════════════════

# Instrucción DEDICADA del rewrite del clip (NO la de foto). Embebe MODEL_PROMPTING_RULES
# §2 (Veo) y §2.3 (content-safety). Edita SOLO el movimiento/cámara; el primer frame (la
# imagen Flux) no se toca acá.
_FIX_CLIP_REWRITE_INSTRUCTION = """\
Sos un editor de prompts de VIDEO para Veo 3.1 (image-to-video, clip de 8s en 9:16).
Te paso el VIDEO_PROMPT ACTUAL en inglés (describe el MOVIMIENTO y la cámara sobre un
primer frame fijo), el IMAGE_PROMPT del primer frame (CONTEXTO, NO lo repitas), el
narration_anchor (lo que el clip ilustra) y un CAMBIO que pide el usuario en español
sobre el MOVIMIENTO / la cámara. Devolvé el video_prompt reescrito EN INGLÉS aplicando
ESE cambio y manteniendo el resto. El primer frame NO cambia: editás cómo se mueve la
cámara y qué cambia en el tiempo, no qué se ve en el cuadro.

REGLAS DE VEO (inviolables — el prompt resultante DEBE cumplirlas):
1. Cinematografía AL INICIO: empezá con shot type + camera movement (Veo genera movimiento
   y el movimiento empieza por la cámara).
2. Vocabulario cinematográfico específico: dolly shot, tracking shot, crane shot, aerial
   view, slow pan, POV shot; wide shot, close-up, low angle; shallow depth of field, etc.
3. Describí MOVIMIENTO + temporalidad, NO repitas la descripción visual del primer frame
   (eso ya está en el image_prompt → redundancia = ruido).
4. SIN audio: en este pipeline NO usamos audio de Veo. NO incluyas diálogo entre comillas,
   NI 'SFX:', NI 'Ambient noise:'. Solo cámara y movimiento.
5. SIN negativos: describí en positivo ("a desolate landscape with no buildings", no "no
   buildings").
6. Longitud objetivo 100–200 palabras. Clip de 8s fijos — NO menciones duración en el prompt.

CONTENT-SAFETY (§2.3 — Veo es MUY estricto, devuelve 422 y rechaza):
- Muerte → calma previa. Evitá "motionless", "abandoned", "eerie", "deep night", "no human
  figures" y cualquier referencia a muerte/destrucción humana. La narración hace el horror;
  el clip muestra la calma viva anterior (aldea al atardecer, luz de lámpara, brisa suave).

Devolvé SOLO el JSON {"new_video_prompt": "<video_prompt reescrito en inglés>"}. Sin markdown.
"""


def _build_clipfix_user_prompt(entry: dict, feedback: str) -> str:
    return (
        f"VIDEO_PROMPT ACTUAL (inglés — movimiento/cámara):\n{entry['video_prompt']}\n\n"
        f"IMAGE_PROMPT del primer frame (CONTEXTO, no lo repitas):\n"
        f"{entry.get('image_prompt') or '(n/d)'}\n\n"
        f"narration_anchor (lo que el clip ilustra): "
        f"{entry.get('base_anchor') or '(sin anchor)'}\n\n"
        f"CAMBIO QUE PIDE EL USUARIO sobre el MOVIMIENTO/cámara (español): {feedback}\n\n"
        "Reescribí el video_prompt en inglés aplicando ese cambio, manteniendo el resto y "
        "respetando las reglas. Devolvé solo {\"new_video_prompt\": ...}."
    )


def _clipfix_core(
    state: "QAState",
    topic_id: str,
    cap: str,
    feedback: str,
    *,
    rewrite_fn=None,          # (system_instruction, user_prompt) -> {"new_video_prompt": str}
    generate_veo_fn=None,     # (image_path: Path, prompt: str, out_path: Path) -> Path
    content_rejected_exc=None,
    now_ts: str | None = None,
) -> tuple[bool, str | None]:
    """Misma forma testeable que _fix_core (deps inyectadas, imports lazy). Regenera el
    clip Veo de un cap veo reescribiendo el video_prompt; mantiene el primer frame."""
    if rewrite_fn is None:
        from gemini_helpers import call_flash_json, types  # noqa: PLC0415
        _schema = types.Schema(
            type=types.Type.OBJECT, required=["new_video_prompt"],
            properties={"new_video_prompt": types.Schema(type=types.Type.STRING)},
        )
        rewrite_fn = lambda si, up: call_flash_json(  # noqa: E731
            prompt=up, system_instruction=si, response_schema=_schema)
    if generate_veo_fn is None or content_rejected_exc is None:
        import asset_manager as am  # noqa: PLC0415
        generate_veo_fn = generate_veo_fn or am._generate_veo_clip
        content_rejected_exc = content_rejected_exc or am.ContentRejectedError

    # 1. Resolver la entrada (video_prompt + primer frame + out clip).
    entry = state.resolve_clip_entry(cap)
    if not entry:
        return False, "no se pudo resolver el clip del cap en el script"
    first_frame = Path(entry["first_frame"])
    out_clip = Path(entry["out_clip"])
    if not first_frame.exists():
        return False, f"falta el primer frame del clip: {first_frame.name}"

    # 2. Rewrite del video_prompt (reglas Veo).
    try:
        res = rewrite_fn(_FIX_CLIP_REWRITE_INSTRUCTION, _build_clipfix_user_prompt(entry, feedback))
        new_vp = str((res or {}).get("new_video_prompt", "")).strip()
        if not new_vp:
            return False, "el rewrite devolvió un video_prompt vacío"
    except Exception as e:  # noqa: BLE001
        return False, f"rewrite falló: {type(e).__name__}: {str(e)[:140]}"

    # 3. Backup del clip viejo ANTES de pisar.
    try:
        if out_clip.exists():
            bdir = state.assets_dir / "_qa_backups"
            bdir.mkdir(parents=True, exist_ok=True)
            ts = now_ts or datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(out_clip, bdir / f"{entry['clip_name']}.{ts}.bak.mp4")
    except OSError as e:
        return False, f"backup falló: {e}"

    # 4. Re-generar el clip Veo i2v desde el MISMO primer frame (pisa el mismo nombre).
    try:
        generate_veo_fn(first_frame, new_vp, out_clip)
    except content_rejected_exc as e:
        return False, f"filtro: {str(e)[:160]}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:160]}"

    # Invalidar el baked → ENSAMBLAR re-concatena el cap desde el clip nuevo.
    _invalidate_baked(state, topic_id, cap)

    return True, None


def _clipfix_worker(cap: str, feedback: str) -> None:
    try:
        ok, reason = _clipfix_core(STATE, TOPIC_ID, cap, feedback)
    except Exception as e:  # noqa: BLE001
        ok, reason = False, f"{type(e).__name__}: {e}"
    with _FIX_LOCK:
        _FIX.update(running=False, done=True, ok=ok, reason=reason)
    print(f"  ✎ clip-fix {cap}: {'✓ ok' if ok else '✗ ' + str(reason)}")


def _start_clipfix(cap: str, feedback: str) -> dict:
    marker = f"{cap}_clip_01.mp4"   # el front machea /fix_status.img_name contra esto
    with _FIX_LOCK:
        if _FIX["running"]:
            return {"conflict": True}
        _FIX.update(running=True, done=False, ok=None, reason=None, img_name=marker)
    threading.Thread(target=_clipfix_worker, args=(cap, feedback), daemon=True).start()
    return {"started": True, "marker": marker}


# ═════════════════════════════════════════════════════════════════
#  ZONA 2 — FIX DE NARRACIÓN/PRONUNCIACIÓN (/fix_narration) · Sabor 1, per-cap
#  Omar describe criollo una mala pronunciación → LLM emite la entrada de
#  normalización → patch del narration_normalized DE ESTE CAP + append al dict
#  global → re-TTS del cap (process_script reusa los demás) → spans se recalculan
#  solos (anchors INTACTOS). Reusa _FIX/_FIX_LOCK (un regen a la vez).
# ═════════════════════════════════════════════════════════════════

_VALID_DICT_CATEGORIES = ("spelled", "pronounceable", "abbreviation", "unit")
_WORD_CHARS = "A-Za-z0-9ÁÉÍÓÚÑáéíóúñ"

# §3 (Gemini): UNA destilación (solo identifica la entrada, NO reescribe el texto →
# evita drift), response_schema (R4), sin ejemplos ✗ MAL con texto copiable (R3/AP3).
_NARRFIX_INSTRUCTION = """\
Sos un auditor de pronunciación TTS (ElevenLabs, español neutro). El usuario escuchó el
audio de UN capítulo y reporta —con sus palabras— UN término que el TTS pronuncia mal
(típicamente una sigla que deletrea raro, una palabra extranjera, o una abreviatura).

Tu ÚNICA tarea: identificar ESE token tal cual aparece en el texto normalizado que te paso,
y decir cómo debería pronunciarse en español para que el TTS lo lea bien. NO reescribas el
texto, NO cambies QUÉ dice la narración: solo emitís la entrada de normalización.

- token: el término EXACTO como aparece en el texto (copialo literal, misma capitalización).
- pronunciation: la forma hablada en español que arregla la lectura.
    · Sigla deletreada → los nombres de las letras en español separados por espacio
      (categoría "spelled").
    · Palabra que el TTS debería leer tal cual o casi → aproximación fonética
      (categoría "pronounceable").
    · Abreviatura → su forma expandida hablada (categoría "abbreviation").
    · Unidad/símbolo → su forma hablada (categoría "unit").
- category: una de exactamente {spelled, pronounceable, abbreviation, unit}.
- found: true sólo si identificás con confianza UN token del texto que matchea el reporte;
    si el reporte es ambiguo o el término no está en el texto, found=false (y no inventes).
- note: una línea legible explicando la decisión.

Si dudás entre categorías para una sigla que se deletrea, usá "spelled".
Devolvé SOLO el JSON del schema. Sin markdown, sin texto fuera del JSON.
"""


def _build_narrfix_user_prompt(normalized_text: str, feedback: str) -> str:
    return (
        f"NARRACIÓN NORMALIZADA DEL CAP (es lo que lee el TTS):\n{normalized_text}\n\n"
        f"REPORTE DEL USUARIO (mala pronunciación, español criollo): {feedback}\n\n"
        "Identificá el ÚNICO token mal pronunciado y devolvé "
        "{token, pronunciation, category, found, note}."
    )


def _boundary_replace(text: str, token: str, replacement: str) -> tuple[str, int]:
    """Reemplazo con LÍMITE DE PALABRA (espejo de tts_normalizer._replace_acronyms).
    NO usa str.replace pelado: 'DEA' NO pega dentro de 'DEAL'. Devuelve (texto, n_reemplazos)."""
    pat = r"(?<![" + _WORD_CHARS + r"])" + re.escape(token) + r"(?![" + _WORD_CHARS + r"])"
    new, n = re.subn(pat, replacement, text)
    if n:
        new = re.sub(r"[ \t]{2,}", " ", new)  # el suggested puede traer espacios extra
    return new, n


def _custom_dict_path(state: "QAState") -> Path:
    # Igual convención que el resto de QAState (base/data == DATA_DIR en producción).
    return state.base / "data" / "normalizer_custom_dict.json"


def _append_custom_dict(state: "QAState", token: str, pronunciation: str, category: str) -> None:
    """Append IDEMPOTENTE al normalizer_custom_dict.json (token único → reemplaza la entry).
    Global: solo afecta VIDEOS FUTUROS (este video ya se arregla vía el normalized patcheado)."""
    p = _custom_dict_path(state)
    data = {"entries": []}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {"entries": []}
    entries = data.setdefault("entries", [])
    entries[:] = [e for e in entries if e.get("token") != token]  # dedup → idempotente
    entries.append({"token": token, "pronunciation": pronunciation, "category": category})
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _narrfix_core(
    state: "QAState",
    topic_id: str,
    cap: str,
    feedback: str,
    *,
    rewrite_fn=None,          # (system_instruction, user_prompt) -> {token,pronunciation,category,found,note}
    process_fn=None,          # (script_dict) -> re-TTS + rebuild sync_map (default audio_manager.process_script)
    content_rejected_exc=None,
    now_ts: str | None = None,
) -> tuple[bool, str | None]:
    """Sabor 1 (pronunciación), per-cap. TESTEABLE con deps inyectadas (sin red, sin TTS).

    El lever obligatorio es el narration_normalized (lo que _resolve_text_for_tts lee primero
    en un LONG con gate corrido) → patchearlo arregla ESTE video. El custom_dict se agrega
    aparte para herencia global. Anchors / narración ORIGINAL INTACTOS → spans se recalculan."""
    if rewrite_fn is None:
        from gemini_helpers import call_flash_json, types  # noqa: PLC0415
        _schema = types.Schema(
            type=types.Type.OBJECT, required=["token", "pronunciation", "category", "found"],
            properties={
                "token": types.Schema(type=types.Type.STRING),
                "pronunciation": types.Schema(type=types.Type.STRING),
                "category": types.Schema(type=types.Type.STRING, enum=list(_VALID_DICT_CATEGORIES)),
                "found": types.Schema(type=types.Type.BOOLEAN),
                "note": types.Schema(type=types.Type.STRING),
            },
        )
        rewrite_fn = lambda si, up: call_flash_json(  # noqa: E731
            prompt=up, system_instruction=si, response_schema=_schema)
    if process_fn is None or content_rejected_exc is None:
        import audio_manager as am  # noqa: PLC0415
        import asset_manager as am2  # noqa: PLC0415
        process_fn = process_fn or am.process_script
        content_rejected_exc = content_rejected_exc or am2.ContentRejectedError

    cap_n = int(cap[2:])
    norm_path = (state.base / "data" / "scripts" / "_steps" / topic_id
                 / "01b_narration_normalized.json")
    if not norm_path.exists():
        return False, "no hay narration_normalized para este topic (¿corrió el gate?)"
    try:
        norm_data = json.loads(norm_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return False, f"narration_normalized ilegible: {e}"
    cap_entry = next(
        (c for c in norm_data.get("chapters", []) if c.get("chapter_number") == cap_n), None)
    if cap_entry is None:
        return False, "el cap no está en el narration_normalized"
    norm_text = cap_entry.get("narration_normalized") or ""

    # 1. LLM: identifica la entrada (NO reescribe el texto).
    try:
        res = rewrite_fn(_NARRFIX_INSTRUCTION, _build_narrfix_user_prompt(norm_text, feedback)) or {}
    except Exception as e:  # noqa: BLE001
        return False, f"LLM falló: {type(e).__name__}: {str(e)[:140]}"
    if not res.get("found"):
        return False, "no encontré un término claro — reformulá el feedback"
    token = str(res.get("token", "")).strip()
    pron = str(res.get("pronunciation", "")).strip()
    cat = str(res.get("category", "")).strip()
    if not token or not pron:
        return False, "el LLM no devolvió token/pronunciación"
    if cat not in _VALID_DICT_CATEGORIES:
        cat = "spelled"

    # 2. Patch del normalized (determinístico, límite de palabra). Si el token no está → abortar.
    new_text, count = _boundary_replace(norm_text, token, pron)
    if count == 0:
        return False, f"'{token}' no aparece en este cap"
    cap_entry["narration_normalized"] = new_text

    ts = now_ts or datetime.now().strftime("%Y%m%d_%H%M%S")
    bdir = state.assets_dir / "_qa_backups"
    bdir.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(norm_path, bdir / f"01b_narration_normalized.{ts}.bak.json")
    except OSError:
        pass
    norm_path.write_text(json.dumps(norm_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3. Append al custom_dict (global, idempotente).
    try:
        _append_custom_dict(state, token, pron, cat)
    except OSError:
        pass

    # 4. Backup del audio viejo del cap (mp3 + timestamps + alignment + meta).
    for fn in (f"{cap}.mp3", f"{cap}_timestamps.json", f"{cap}_alignment.json", f"{cap}.meta.json"):
        src = state.audio_dir / fn
        if src.exists():
            try:
                shutil.copy2(src, bdir / f"{fn}.{ts}.bak")
            except OSError:
                pass

    # 5. Re-TTS vía process_script (DECISIÓN: opción (b) del handoff). Reconstruyo el script
    #    desde el sync_map existente (cada entry trae text ORIGINAL + narrative_intent) y dejo
    #    que process_script(skip_if_exists=True) regenere SOLO este cap (text_hash difiere por el
    #    normalized patcheado) y reuse los demás (hash match + alignment) → recomputa offsets y
    #    reescribe sync_map sin merge a mano. Un solo productor.
    sm_path = state.audio_dir / "sync_map.json"
    if not sm_path.exists():
        return False, "no hay sync_map.json (¿corrió fase2a?)"
    try:
        sm = json.loads(sm_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return False, f"sync_map ilegible: {e}"
    script = {
        "video_id": topic_id,
        "chapters": [
            {"id": e.get("id"), "text": e.get("text", ""),
             "narrative_intent": e.get("narrative_intent", "")}
            for e in sm.get("chapters", []) if e.get("id")
        ],
    }
    try:
        process_fn(script)
    except content_rejected_exc as e:
        return False, f"filtro: {str(e)[:160]}"
    except Exception as e:  # noqa: BLE001
        low = str(e).lower()
        if any(k in low for k in ("content", "policy", "moderation", "safety", "blocked", "prohibited")):
            return False, f"filtro: {str(e)[:160]}"
        return False, f"{type(e).__name__}: {str(e)[:160]}"

    # 6. Invalidar el baked → ENSAMBLAR re-renderiza el cap con el audio nuevo.
    _invalidate_baked(state, topic_id, cap)
    return True, None


def _narrfix_worker(cap: str, feedback: str) -> None:
    try:
        ok, reason = _narrfix_core(STATE, TOPIC_ID, cap, feedback)
    except Exception as e:  # noqa: BLE001
        ok, reason = False, f"{type(e).__name__}: {e}"
    with _FIX_LOCK:
        _FIX.update(running=False, done=True, ok=ok, reason=reason)
    print(f"  ✎ narr-fix {cap}: {'✓ ok' if ok else '✗ ' + str(reason)}")


def _start_narrfix(cap: str, feedback: str) -> dict:
    marker = f"{cap}_audio"   # el front machea /fix_status.img_name contra esto
    with _FIX_LOCK:
        if _FIX["running"]:
            return {"conflict": True}
        _FIX.update(running=True, done=False, ok=None, reason=None, img_name=marker)
    threading.Thread(target=_narrfix_worker, args=(cap, feedback), daemon=True).start()
    return {"started": True, "marker": marker}


# ═════════════════════════════════════════════════════════════════
#  FORM ASISTIDO — driver del subprocess run_pipeline + gates al browser
#  (contrato chat 61). Lanza `run_pipeline.py --research` con QA_FORM=1; lee stdout
#  linea a linea; al ver el marcador @@QAFORM@@ lo expone como dialogo; la respuesta
#  del HTML (window.qaFormAnswer) se traduce a una linea de stdin. La terminal NO
#  cambia: el marcador solo se emite con QA_FORM seteada.
# ═════════════════════════════════════════════════════════════════

HTML_FORM_PATH = BASE_DIR / "qa_form.html"
_FORM_MARKER = "@@QAFORM@@ "
_FORM_PHASES = ["RESEARCH", "GUION", "ASSETS", "VIDEO", "PACKAGING"]
_FORM_CONSOLE_MAX = 600
# HTML por menú. __choice__ = diálogo genérico de botones (accept='key': video_type, …).
# El host elige cuál según marker.accept. HANDOFF 65a: seed_pick y reuse_seeds van ambos a
# __gallery__ (galería única) → qa_seed_pick.html jubilado (ya no se sirve).
_FORM_MENU_HTML = {
    "__choice__": BASE_DIR / "qa_choice.html",
    "__multi__": BASE_DIR / "qa_multi.html",   # accept='keys': submenú de nichos (checkboxes)
    "__gallery__": BASE_DIR / "qa_gallery.html",  # reuse_seeds + seed_pick: galería única de seeds
    "__judge__": BASE_DIR / "qa_judge.html",   # judge_action: lista de issues + V/A/R/S
}

_FORM: dict = {"running": False, "returncode": None, "console": [], "marker": None, "phase": None, "run_tid": None}
_FORM_LOCK = threading.Lock()
_FORM_PROC: dict = {"p": None}


def _form_command() -> list[str]:
    """Comando del run asistido. FACTORIZADO para que el smoke inyecte un stub.
    El form arranca long directo (sin S/L) y con --batch: tras el pick de seed corre
    GUION->ASSETS->VIDEO solo (gates del medio auto-decididos en fase1_5). El pick de
    seed SIGUE interactivo (--batch solo gobierna del guion en adelante). Los flags los
    agrega SOLO este lanzamiento; correr run_pipeline/fase1 a mano por terminal sigue
    interactivo igual que hoy."""
    return [sys.executable, "run_pipeline.py", "--research", "--video-type", "long", "--batch"]


def _form_reader(proc) -> None:
    """Thread daemon: lee stdout. Marcador → _FORM['marker']; header de fase → progreso;
    el resto → consola. (PYTHONUNBUFFERED=1 en el env mantiene a run_pipeline Y a fase1
    sin buffer → el marcador llega al toque.)"""
    global TOPIC_ID, STATE
    try:
        for line in proc.stdout:
            line = line.rstrip("\n")
            if line.startswith(_FORM_MARKER):
                try:
                    marker = json.loads(line[len(_FORM_MARKER):])
                except json.JSONDecodeError:
                    marker = None
                if marker:
                    with _FORM_LOCK:
                        _FORM["marker"] = marker
                    # Gate del visor: apuntar el visor al topic de la corrida en vivo. NO basta
                    # con TOPIC_ID (eso alimenta /assemble y los fixes): el visor LEE de STATE,
                    # así que hay que RECONSTRUIRLO o se ve el topic viejo. Mismo patrón que serve().
                    if marker.get("menu") == "visor_gate":
                        try:
                            TOPIC_ID = marker["payload"]["topic_id"]
                            STATE = QAState(TOPIC_ID, BASE_DIR)
                        except Exception as e:  # noqa: BLE001 — no tumbar el reader si falla
                            with _FORM_LOCK:
                                _FORM["console"].append(
                                    f"[qa_form] no pude reapuntar STATE: {type(e).__name__}: {e}")
                continue  # el marcador NO va a la consola
            if "  ▶ " in line:
                for ph in _FORM_PHASES:
                    if ph in line:
                        with _FORM_LOCK:
                            _FORM["phase"] = ph
                        break
                # tid del header "▶ <fase> — <tid>" (lo emite _phase_header). Para el % real
                # de ASSETS. RESEARCH no trae tid; GUION sí → run_tid llega antes de ASSETS.
                if " — " in line:
                    cand = line.rsplit(" — ", 1)[-1].strip()
                    if cand and "/" not in cand and 0 < len(cand) <= 64:
                        with _FORM_LOCK:
                            _FORM["run_tid"] = cand
            with _FORM_LOCK:
                _FORM["console"].append(line)
                if len(_FORM["console"]) > _FORM_CONSOLE_MAX:
                    _FORM["console"] = _FORM["console"][-_FORM_CONSOLE_MAX:]
        proc.wait()
        rc = proc.returncode
    except Exception as e:  # noqa: BLE001
        with _FORM_LOCK:
            _FORM["console"].append(f"[qa_form] error leyendo subprocess: {type(e).__name__}: {e}")
        rc = -1
    with _FORM_LOCK:
        _FORM["returncode"] = rc
        _FORM["running"] = False
        _FORM["marker"] = None


def _start_form() -> dict:
    with _FORM_LOCK:
        if _FORM["running"]:
            return {"conflict": True}
        _FORM.update(running=True, returncode=None, console=[], marker=None, phase=None, run_tid=None)
    # QA_FORM=1 → fase1 emite el marcador. PYTHONUNBUFFERED → run_pipeline Y fase1 sin
    # buffer (el marcador llega al toque). PYTHONIOENCODING=utf-8 → el hijo emite utf-8 en
    # Windows (sin esto, los ▶/emojis de fase1 tumban el child con cp1252; igual que el
    # assemble worker). El reader decodifica utf-8 con errors="replace".
    env = {**os.environ, "QA_FORM": "1", "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"}
    try:
        proc = subprocess.Popen(
            _form_command(), cwd=str(BASE_DIR),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, encoding="utf-8", errors="replace", env=env,
        )
    except Exception as e:  # noqa: BLE001
        with _FORM_LOCK:
            _FORM.update(running=False, returncode=-1)
            _FORM["console"].append(f"[qa_form] no pude lanzar run_pipeline: {e}")
        return {"error": str(e)}
    _FORM_PROC["p"] = proc
    threading.Thread(target=_form_reader, args=(proc,), daemon=True).start()
    return {"started": True}


def _sanitize_form_line(line: str) -> str | None:
    """Una sola línea para el stdin del subprocess (lo que su input() ya parsea). Saca el
    salto final; rechaza saltos embebidos (anti-inyección de varias líneas) y líneas
    absurdamente largas. Permite cualquier respuesta de menú: 7 · 1,4 · Q · S · L · …"""
    line = (line or "").rstrip("\r\n")
    if "\n" in line or "\r" in line or len(line) > 500:
        return None
    return line


def _form_answer(line: str) -> dict:
    """Escribe `line`+\\n al stdin del subprocess (lo que el input() del gate ya parsea).
    Acepta cualquier respuesta de UNA línea (números/Q del seed_pick, S/L del tipo de
    video, etc.) — la valida el propio prompt del subprocess, no nosotros."""
    line = _sanitize_form_line(line)
    if line is None:
        return {"error": "respuesta inválida (una sola línea)"}
    proc = _FORM_PROC.get("p")
    if proc is None or proc.poll() is not None:
        return {"error": "no hay corrida activa"}
    try:
        proc.stdin.write(line + "\n")
        proc.stdin.flush()
    except (BrokenPipeError, OSError) as e:
        return {"error": f"no pude escribir al subprocess: {e}"}
    with _FORM_LOCK:
        _FORM["marker"] = None  # el diálogo ya fue respondido → el form vuelve a consola
    return {"ok": True}


def _form_shutdown() -> dict:
    """Mata la corrida hija (si la hay) y apaga el server. El os._exit va en un timer
    corto para que la respuesta HTTP alcance a llegar al browser antes de morir."""
    killed = False
    proc = _FORM_PROC.get("p")
    if proc is not None and proc.poll() is None:
        try:
            proc.terminate()
            killed = True
        except Exception:  # noqa: BLE001
            pass
    threading.Timer(0.4, lambda: os._exit(0)).start()
    return {"bye": True, "killed_run": killed}


def _assets_progress(tid: str | None) -> dict | None:
    """{done,total} de imágenes para el % real del segmento ASSETS. Read-only:
    total = anchors+supp_anchors del script; done = .png en disco (caps()). Mismo patrón
    de disco que el visor; NO toca el motor. Nunca tira excepción hacia /form_state."""
    if not tid:
        return None
    try:
        st = QAState(tid, BASE_DIR)
        total = sum(len(v.get("anchors", [])) + len(v.get("supp_anchors", []))
                    for v in st._script.values())
        if total <= 0:
            return None
        done = sum(c["count"] for c in st.caps())
        return {"done": min(done, total), "total": total}
    except Exception:  # noqa: BLE001
        return None


def _form_state(tail: int = 200) -> dict:
    with _FORM_LOCK:
        phase = _FORM["phase"]
        run_tid = _FORM["run_tid"]
        base = {
            "running": _FORM["running"],
            "returncode": _FORM["returncode"],
            "phase": phase,
            "phases": _FORM_PHASES,
            "marker": _FORM["marker"],
            "console_tail": list(_FORM["console"][-tail:]),
        }
    # disco fuera del lock; solo cuando importa (ASSETS)
    base["assets"] = _assets_progress(run_tid) if phase == "ASSETS" else None
    return base


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

    def _write(self, data: bytes) -> None:
        """Escribe al socket tolerando que el browser corte la conexión (seek/pause de
        media abortan el request a media camino → BrokenPipe normal, no es error)."""
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def _send_file(self, path: Path | None, content_type: str):
        if path is None or not path.exists():
            self._send_json({"error": "no encontrado"}, status=404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Accept-Ranges", "none")
        self.end_headers()
        self._write(data)

    def _send_media(self, path: Path | None, content_type: str):
        """Sirve audio/video con soporte de HTTP Range (206) → el <audio>/<video> puede
        SEEKEAR (currentTime = start del span). Sin esto el browser arranca de 0 y
        reproduce todo el cap. (handoff: range requests cuando el seek se traba.)"""
        if path is None or not path.exists():
            self._send_json({"error": "no encontrado"}, status=404)
            return
        size = path.stat().st_size
        rng = self.headers.get("Range")
        if not rng:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            with open(path, "rb") as f:
                self._write(f.read())
            return
        # Parseo de "bytes=START-END" (incluye sufijo "bytes=-N" y abierto "bytes=N-").
        start, end = 0, size - 1
        try:
            unit, _, spec = rng.partition("=")
            if unit.strip() != "bytes":
                raise ValueError("unidad no soportada")
            s_str, _, e_str = spec.strip().partition("-")
            if s_str == "":  # sufijo: últimos N bytes
                start = max(0, size - int(e_str))
            else:
                start = int(s_str)
                end = int(e_str) if e_str else size - 1
            end = min(end, size - 1)
            if start > end or start >= size:
                raise ValueError("rango fuera de límites")
        except (ValueError, OverflowError):
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return
        length = end - start + 1
        with open(path, "rb") as f:
            f.seek(start)
            chunk = f.read(length)
        self.send_response(206)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(len(chunk)))
        self.end_headers()
        self._write(chunk)

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
                self._send_media(STATE.resolve_audio(self._cap_str()), "audio/mpeg")
            elif route == "/clip":
                self._send_media(STATE.resolve_clip(self._cap_str()), "video/mp4")
            elif route == "/topic":
                self._send_json(STATE.topic_info())
            elif route == "/assemble_status":
                self._send_json(_assemble_status())
            elif route == "/fix_status":
                self._send_json(_fix_status())
            elif route == "/form":
                self._send_file(HTML_FORM_PATH, "text/html; charset=utf-8")
            elif route == "/form_menu":
                menu = self._qs().get("menu", [""])[0]
                self._send_file(_FORM_MENU_HTML.get(menu), "text/html; charset=utf-8")
            elif route == "/form_state":
                self._send_json(_form_state())
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
            elif route == "/fix_image":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                cap = str(body.get("cap", ""))
                img_name = str(body.get("img_name", ""))
                feedback = str(body.get("feedback", "")).strip()
                # anti path-traversal (reusa las regex del archivo) + sanity.
                if not _CAP_RE.match(cap) or not _IMG_NAME_RE.match(img_name):
                    self._send_json({"error": "cap/img_name inválido"}, status=400)
                    return
                if not img_name.startswith(cap + "_"):
                    self._send_json({"error": "img_name no corresponde al cap"}, status=400)
                    return
                if not feedback:
                    self._send_json({"error": "falta 'feedback'"}, status=400)
                    return
                # El tile del clip NO se fixea en v1 (Zona 1.5).
                if "_img_" not in img_name and "_supp_" not in img_name:
                    self._send_json({"error": "solo fotos (_img_/_supp_)"}, status=400)
                    return
                res = _start_fix(cap, img_name, feedback)
                if res.get("conflict"):
                    self._send_json({"error": "ya hay un fix en curso"}, status=409)
                    print("  ✎ fix: rechazado (ya hay uno en curso)")
                else:
                    print(f"  ✎ fix: {img_name} ← {feedback[:50]!r}")
                    self._send_json({"started": True})
            elif route == "/fix_clip":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                cap = str(body.get("cap", ""))
                feedback = str(body.get("feedback", "")).strip()
                if not _CAP_RE.match(cap):
                    self._send_json({"error": "cap inválido"}, status=400)
                    return
                if not feedback:
                    self._send_json({"error": "falta 'feedback'"}, status=400)
                    return
                if STATE is None or STATE.resolve_clip_entry(cap) is None:
                    self._send_json({"error": "el cap no tiene clip Veo regenerable"}, status=400)
                    return
                res = _start_clipfix(cap, feedback)
                if res.get("conflict"):
                    self._send_json({"error": "ya hay un regen en curso"}, status=409)
                    print("  ✎ clip-fix: rechazado (ya hay uno en curso)")
                else:
                    print(f"  ✎ clip-fix: {cap} ← {feedback[:50]!r}")
                    self._send_json({"started": True, "marker": res.get("marker")})
            elif route == "/fix_narration":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                cap = str(body.get("cap", ""))
                feedback = str(body.get("feedback", "")).strip()
                if not _CAP_RE.match(cap):
                    self._send_json({"error": "cap inválido"}, status=400)
                    return
                if not feedback:
                    self._send_json({"error": "falta 'feedback'"}, status=400)
                    return
                res = _start_narrfix(cap, feedback)
                if res.get("conflict"):
                    self._send_json({"error": "ya hay un regen en curso"}, status=409)
                    print("  ✎ narr-fix: rechazado (ya hay uno en curso)")
                else:
                    print(f"  ✎ narr-fix: {cap} ← {feedback[:50]!r}")
                    self._send_json({"started": True, "marker": res.get("marker")})
            elif route == "/form_launch":
                res = _start_form()
                if res.get("conflict"):
                    self._send_json({"error": "ya hay una corrida en curso"}, status=409)
                elif res.get("error"):
                    self._send_json(res, status=500)
                else:
                    print("  ▶ form: lanzando run_pipeline --research (QA_FORM=1)…")
                    self._send_json({"started": True})
            elif route == "/form_answer":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                res = _form_answer(str(body.get("line", "")))
                if res.get("error"):
                    self._send_json(res, status=400)
                else:
                    print(f"  ▶ form: stdin ← {str(body.get('line',''))[:40]!r}")
                    self._send_json(res)
            elif route == "/form_shutdown":
                print("  ▶ form: cerrando server (pedido desde el form)…")
                self._send_json(_form_shutdown())
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


def serve(topic_id: str, open_form: bool = True) -> None:
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
        if STATE._is_veo(c["cap"]):
            pos = STATE._veo_position(c["cap"])
            kind = f"VEO {pos} (timeline ×{c['count']}+clip)"
        else:
            kind = f"FLUX ×{c['count']}"
        print(f"     {c['cap']} — {c['role']:<14} {kind}")
    base_url = f"http://{HOST}:{PORT}"
    open_url = f"{base_url}/form" if open_form else base_url
    print("─" * 64)
    print(f"  ▶ Abrí en el navegador:  {open_url}    (Ctrl+C para frenar)")
    print("─" * 64)
    try:
        webbrowser.open(open_url)
    except Exception:  # noqa: BLE001
        pass
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  frenado.")
        server.shutdown()


def main():
    ap = argparse.ArgumentParser(description="QA Studio v1 — form + visor read-only + ENSAMBLAR.")
    ap.add_argument(
        "--topic",
        default=None,
        help="topic_id explícito → abre el VISOR de ese topic. Sin --topic → abre el FORM.",
    )
    args = ap.parse_args()
    tid = args.topic or TOPIC_ID
    serve(tid, open_form=(args.topic is None))


if __name__ == "__main__":
    main()
