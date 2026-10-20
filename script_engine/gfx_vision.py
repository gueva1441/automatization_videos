"""
gfx_vision.py — Zoom foto-primero (F4b §3): visión MIRA la foto antes de que el director elija el zoom.

    photo_details(img)  1 llamada Flash visión por imagen → hasta 3 detalles {label, box [x,y,w,h] 0–1, conf, tipo},
                        tipo ∈ rostro | manos | persona | objeto | texto | textura. Cache por hash de la imagen
                        (output/<video>/assets/photo_details.json): re-render no re-gasta.
    pick_zoom()         1 zoom de evidencia por cap:
                          1. NOMBRADO: la voz dice el detalle (o un sinónimo) dentro del tramo → zoom ahí, latido en la
                             palabra (la caja ya viene de visión);
                          2. DE EDITOR: si nada se nombra, un detalle rostro|manos|persona con conf ≥ 0.8 → zoom en la
                             foto que tiene la frase de mayor intensidad (§1);
                          3. textura (agua, aceite, humo, nubes) SOLO si se nombra literal y la foto no tiene detalle
                             humano. Prioridad fija: rostro/manos > persona > objeto > texto > textura.
    human_box()         caja del detalle humano de una escena → el router la marca de riesgo alto y el acercar apunta ahí.
El zoom_judge viejo (gfx_director.apply_zoom_vision) queda como respaldo si este pase falla.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Callable

TIPOS = ("rostro", "manos", "persona", "objeto", "texto", "textura")
PRIORITY = {"rostro": 0, "manos": 0, "persona": 1, "objeto": 2, "texto": 3, "textura": 4}
HUMAN = {"rostro", "manos", "persona"}
EDITOR_CONF = 0.8
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
# palabras de la voz que nombran un detalle aunque el label de visión diga otra cosa
SYNONYMS = {"rostro": {"rostro", "cara", "rostros", "caras", "ojos", "mirada"},
            "manos": {"mano", "manos", "dedos", "puño", "puños"},
            "persona": {"niño", "niños", "niña", "hombre", "hombres", "mujer", "mujeres", "preso", "presos", "prisionero",
                        "prisioneros", "recluso", "reclusos", "cuerpo", "cuerpos", "cadáver", "cadáveres"}}


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
        data[h] = {"imagen": Path(img).name, "detalles": [], "error": f"{type(e).__name__}: {str(e)[:120]}"}
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        return None
    det = validate(raw)
    data[h] = {"imagen": Path(img).name, "detalles": det}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return det


_ART = {"del", "las", "los", "una", "unos", "unas", "con", "sin", "por", "para"}


def _named_word(detail: dict[str, Any], words: list[dict], t0: float, t1: float, time_offset: float) -> dict | None:
    """Palabra de la voz dentro de [t0, t1) que nombra el detalle (label o sinónimo del tipo)."""
    # el sustantivo principal del detalle (la 1ra palabra de contenido): «insecto en agua» se nombra con «insecto»,
    # no con «agua» (F4b: con cualquier palabra del label se acercaba un insecto porque la voz decía «agua»)
    toks = [_plain(_tok(w))[:5] for w in detail["label"].split() if len(_tok(w)) >= 3 and _tok(w) not in _ART]
    # textura: cualquier palabra del label (el material: «mancha de ACEITE»); el resto: solo el sustantivo principal
    label = set(toks) if detail["tipo"] == "textura" else set(toks[:1])
    syn = {_plain(s)[:5] for s in SYNONYMS.get(detail["tipo"], set())}
    for w in words:
        t = float(w["start"]) + time_offset
        if not t0 <= t < t1:
            continue
        k = _plain(_tok(w["word"]))[:5]
        if len(_tok(w["word"])) >= 4 and (k in label or k in syn):
            return w
    return None


def pick_zoom(details: dict[int, list[dict[str, Any]]], scenes: list[Any], words: list[dict], *,
              intensity: dict[str, Any] | None, sentences: list[dict[str, Any]], peak_t: float | None,
              time_offset: float = 0.0, zoom_dur: float = 2.85, clear: float = 5.0,
              verify: Callable[[Any, dict[str, Any]], bool] | None = None, max_tries: int = 3) -> dict[str, Any] | None:
    """El zoom del cap (o None). Nunca a ±clear s del pico; la escena tiene que alcanzar para el zoom.
    Orden: nombrado (no textura) → de editor (humano, foto de la frase más intensa) → textura nombrada. Con `verify`,
    cada candidato se confirma recortando la caja (visión: «¿se ve X?»); hasta max_tries candidatos."""
    def ok_scene(sc: Any) -> bool:
        z0 = sc.end - zoom_dur
        return sc.end - sc.start >= zoom_dur + 0.2 and (peak_t is None or abs(z0 - peak_t) > clear)

    def zoom(sc: Any, d: dict[str, Any], word: dict | None, how: str) -> dict[str, Any]:
        start = round(sc.end - zoom_dur, 3)
        z = {"scene_idx": sc.idx, "box": d["box"], "start": start, "anchor": d["label"], "detail": d["label"],
             "tipo": d["tipo"], "conf": d["conf"], "como": how, "word": _tok(word["word"]) if word else d["label"]}
        if word is not None:
            t = float(word["start"]) + time_offset
            z.update(latido=True, latido_t=round(max(start + 0.7, min(t, sc.end - 0.6)), 3))
        return z

    named = []
    for sc in scenes:
        if not ok_scene(sc):
            continue
        dets = details.get(sc.idx) or []
        has_human = any(d["tipo"] in HUMAN for d in dets)
        for d in dets:
            if d["tipo"] == "textura" and has_human:
                continue                                       # textura solo sin detalle humano en la foto
            w = _named_word(d, words, sc.start, sc.end, time_offset)
            if w is not None:
                named.append((PRIORITY[d["tipo"]], -d["conf"], sc.idx, sc, d, w))
    inten = (intensity or {}).get("intensidad") or []

    def scene_intensity(sc: Any) -> float:
        vals = [inten[i] for i, s in enumerate(sentences) if i < len(inten) and s["t0"] < sc.end and s["t1"] > sc.start]
        return max(vals) if vals else 0.0
    order: list[tuple[Any, dict[str, Any], dict | None, str]] = []
    order += [(x[3], x[4], x[5], "nombrado") for x in sorted((x for x in named if x[4]["tipo"] != "textura"), key=lambda x: x[:3])]
    eds = [(sc, d) for sc in scenes if ok_scene(sc) for d in details.get(sc.idx) or []
           if d["tipo"] in HUMAN and d["conf"] >= EDITOR_CONF]
    order += [(sc, d, None, "de editor") for sc, d in sorted(eds, key=lambda x: (-scene_intensity(x[0]), PRIORITY[x[1]["tipo"]],
                                                                                    -x[1]["conf"], x[0].idx))]
    order += [(x[3], x[4], x[5], "nombrado") for x in sorted((x for x in named if x[4]["tipo"] == "textura"), key=lambda x: x[:3])]
    for k, (sc, d, w, how) in enumerate(order):
        if verify is not None and k >= max_tries:
            break
        if verify is None or verify(sc, d):
            return zoom(sc, d, w, how)
    return None


VERIFY_SYSTEM = ("Mirás un RECORTE de una imagen. Respondé se_ve=true SOLO si lo que dice la etiqueta está en el CENTRO del "
                 "recorte y ocupa la mayor parte. Si está cortado en un borde, si se ve sobre todo otra cosa (barrotes, "
                 "pared, agua) o si es dudoso, se_ve=false. Respondés SOLO JSON.")
VERIFY_SCHEMA = {"type": "OBJECT", "properties": {"se_ve": {"type": "BOOLEAN"}}, "required": ["se_ve"]}


def verify_crop(img: Path, d: dict[str, Any], cache: Path, call: Callable[..., dict] | None = None) -> bool:
    """¿El recorte de la caja muestra el detalle? 1 llamada de visión por (imagen, caja); cacheada. Error → False."""
    key = f"v2|{image_hash(img)}|{d['box']}|{d['label']}"
    try:
        data = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    except (OSError, ValueError):
        data = {}
    if key in data:
        return bool(data[key])
    try:
        from PIL import Image
        import io
        im = Image.open(img).convert("RGB")
        W, H = im.size
        x, y, w, h = d["box"]
        pad = 0.05
        crop = im.crop((int(max(0, x - w * pad) * W), int(max(0, y - h * pad) * H),
                        int(min(1, x + w * (1 + pad)) * W), int(min(1, y + h * (1 + pad)) * H)))
        buf = io.BytesIO()
        crop.save(buf, "JPEG", quality=90)
        if call is None:
            from google.genai import types as genai_types
            from config import api, gemini_client
            from cost_tracker import cost_tracker
            resp = gemini_client.models.generate_content(
                model=api.gemini_model,
                contents=[genai_types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg"),
                          f"Etiqueta: «{d['label']}». ¿Se ve?"],
                config=genai_types.GenerateContentConfig(system_instruction=VERIFY_SYSTEM, temperature=0.0,
                                                         response_mime_type="application/json",
                                                         response_schema=VERIFY_SCHEMA))
            cost_tracker.track_gemini_vision(description="gfx_zoom_verify", calls=1)
            ok = bool(json.loads(resp.text).get("se_ve"))
        else:
            ok = bool(call(buf.getvalue(), d))
    except Exception:  # noqa: BLE001 — sin confirmación no hay zoom (conservador)
        return False
    data[key] = ok
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return ok


def human_box(dets: list[dict[str, Any]] | None) -> list[float] | None:
    return next((d["box"] for d in dets or [] if d["tipo"] in ("rostro", "manos")), None)
