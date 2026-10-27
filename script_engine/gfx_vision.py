"""
gfx_vision.py — Zoom foto-primero (F4b §3): visión MIRA la foto antes de que el director elija el zoom.

    photo_details(img)  1 llamada Flash visión por imagen → hasta 3 detalles {label, box [x,y,w,h] 0–1, conf, tipo},
                        tipo ∈ rostro | manos | persona | objeto | texto | textura. Cache por hash de la imagen
                        (output/<video>/assets/photo_details.json): re-render no re-gasta.
    human_box()         caja del detalle humano de una escena → el router la marca de riesgo alto y el acercar apunta ahí.
F36 §D: la lupa se borró (pick_zoom y la verificación de su caja, verify_crop); queda la visión de la foto para el
movimiento seguro (rostro/manos → acercar al detalle).
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
import unicodedata
from pathlib import Path
from typing import Any, Callable

_CACHE_LOCK = threading.Lock()      # F32 §A: el -g30 y los planes pueden correr en hilos; la caché es compartida


def _guardar(cache: Path, key: str, value: Any) -> None:
    """Suma una entrada a la caché (relee bajo el candado: otro hilo pudo escribir otra entrada mientras tanto)."""
    with _CACHE_LOCK:
        try:
            data = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
        except (OSError, ValueError):
            data = {}
        data[key] = value
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

TIPOS = ("rostro", "manos", "persona", "objeto", "texto", "textura")
PRIORITY = {"rostro": 0, "manos": 0, "persona": 1, "objeto": 2, "texto": 3, "textura": 4}
HUMAN = {"rostro", "manos", "persona"}
MIN_CONF = 0.6
SYSTEM = """Sos editor de un documental. Mirás UNA imagen y listás hasta 3 detalles que un editor ACERCARÍA con un zoom
(lo que cuenta la historia: un rostro, unas manos, una herida, un objeto clave, un texto legible). Para cada uno:
label = 1–3 palabras en español (sustantivo concreto: «herida en la mano», «rostro del niño», «candado»), box normalizada
[x, y, w, h] (0–1, origen arriba a la izquierda, lado entre 0.06 y 0.3), conf 0–1 y tipo (rostro | manos | persona |
objeto | texto | textura). Agua, aceite, humo, nubes, paredes o cielo son «textura». Si no hay nada que acercar, lista vacía."""
SCHEMA: dict[str, Any] = {"type": "OBJECT", "properties": {"detalles": {"type": "ARRAY", "items": {
    "type": "OBJECT", "properties": {"label": {"type": "STRING"}, "box": {"type": "ARRAY", "items": {"type": "NUMBER"}},
                                     "conf": {"type": "NUMBER"}, "tipo": {"type": "STRING", "enum": list(TIPOS)}},
    "required": ["label", "box", "conf", "tipo"]}}}, "required": ["detalles"]}


def _plain(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s).lower()) if unicodedata.category(c) != "Mn")


def _tok(w: str) -> str:
    return re.sub(r"^[¿¡\"'«“(]+|[.,;:!?…\"'»”)]+$", "", str(w)).lower()


def clamp_box(b: Any) -> list[float] | None:
    try:
        x, y, w, h = (float(v) for v in list(b)[:4])
    except (TypeError, ValueError):
        return None
    w, h = max(0.06, min(0.3, w)), max(0.06, min(0.3, h))
    x, y = max(0.0, min(1.0 - w, x)), max(0.0, min(1.0 - h, y))
    return [round(x, 3), round(y, 3), round(w, 3), round(h, 3)]


def image_hash(path: Path) -> str:
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()[:16]


def validate(raw: Any) -> list[dict[str, Any]]:
    out = []
    for d in (raw or {}).get("detalles") or []:
        if not isinstance(d, dict) or d.get("tipo") not in TIPOS:
            continue
        box = clamp_box(d.get("box") or [])
        try:
            conf = max(0.0, min(1.0, float(d.get("conf") or 0.0)))
        except (TypeError, ValueError):
            continue
        label = str(d.get("label", "")).strip()[:40]
        if box and label and conf >= MIN_CONF:
            out.append({"label": label, "box": box, "conf": round(conf, 2), "tipo": d["tipo"]})
    return sorted(out, key=lambda d: (PRIORITY[d["tipo"]], -d["conf"]))[:3]


def _vision_call(img: Path) -> dict[str, Any]:
    from google.genai import types as genai_types
    from config import api, gemini_client
    from cost_tracker import cost_tracker
    mime = "image/png" if img.suffix.lower() == ".png" else "image/jpeg"
    resp = gemini_client.models.generate_content(
        model=api.gemini_model,
        contents=[genai_types.Part.from_bytes(data=img.read_bytes(), mime_type=mime), "Devolvé solo el JSON."],
        config=genai_types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.0,
                                                 response_mime_type="application/json", response_schema=SCHEMA))
    cost_tracker.track_gemini_vision(description=f"gfx_photo_details:{img.stem}", calls=1)
    return json.loads(resp.text)


def photo_details(img: Path, cache: Path, call: Callable[[Path], dict] | None = None) -> list[dict[str, Any]] | None:
    """Detalles validados de la imagen (cacheados por hash). None si visión falló (→ respaldo zoom_judge)."""
    h = image_hash(img)
    try:
        data = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    except (OSError, ValueError):
        data = {}
    if h in data:
        return data[h]["detalles"]
    try:
        raw = (call or _vision_call)(img)
    except Exception as e:  # noqa: BLE001 — se anota y no se reintenta en cada render: la escena queda sin detalles
        _guardar(cache, h, {"imagen": Path(img).name, "detalles": [], "error": f"{type(e).__name__}: {str(e)[:120]}"})
        return None
    det = validate(raw)
    _guardar(cache, h, {"imagen": Path(img).name, "detalles": det})
    return det


def human_box(dets: list[dict[str, Any]] | None) -> list[float] | None:
    return next((d["box"] for d in dets or [] if d["tipo"] in ("rostro", "manos")), None)
