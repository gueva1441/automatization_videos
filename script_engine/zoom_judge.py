"""
zoom_judge.py — Juez semántico de visión del gate de zoom v3 (Camino B, chat 55).

La geometría (depth_probe.center_minus_border) separa "sujeto cercano centrado vs
entorno que recede", pero NO distingue un sujeto digno de zoom de una cara
close-up o un muro con relieve fantasma (validado lab 1.5). Eso es semántico, no
geométrico → un clasificador de visión sobre el PNG real lo cierra.

Clasificador CIEGO de 5 categorías (Gemini Flash vision, temp 0, response_schema
enum). Validado lab 1.6: 12/12 estable entre corridas; atrapa la cara y la
fachada plana que la geometría dejaba pasar. Solo `sujeto_con_fondo` se promueve
a zoom_in. La taxonomía completa se persiste (los `corredor_tunel` quedan para el
backlog de push-in a punto de fuga).

Determinismo entre corridas POR CONSTRUCCIÓN: los veredictos se cachean en
zoom_verdicts.json; las re-animaciones releen, no re-llaman.
"""
from __future__ import annotations

import json
from pathlib import Path

from google.genai import types as genai_types

from config import gemini_client, api
from cost_tracker import cost_tracker
from error_handler import error_handler, PipelineStage

# Categorías EXACTAS del lab 1.6 (no cambiar sin re-validar).
CATEGORIES = ["sujeto_con_fondo", "cara_closeup", "superficie_plana", "corredor_tunel", "otro"]
ZOOM_CATEGORY = "sujeto_con_fondo"   # única que se promueve a zoom_in

# Test CIEGO: el prompt NO menciona filename, expectativa, ni zoom/cámara.
_SYSTEM = """Sos un clasificador visual. Mirás UNA imagen y la asignás a EXACTAMENTE UNA categoría
según su COMPOSICIÓN DE PROFUNDIDAD. No evalúes estilo, época ni calidad.

Categorías:
- sujeto_con_fondo: una persona u objeto claro es el foco en primer plano, y hay espacio o fondo
  que se aleja DETRÁS de ese foco (hay distancia real detrás del sujeto).
- cara_closeup: un rostro humano ocupa la mayor parte del cuadro (retrato cercano), sin fondo
  profundo relevante.
- superficie_plana: un muro, textura, superficie u objeto plano llena el cuadro; NO hay un foco
  con espacio que se aleje detrás.
- corredor_tunel: un pasillo, túnel o espacio que se aleja hacia un punto de fuga central, SIN una
  persona u objeto en primer plano.
- otro: ninguna de las anteriores domina con claridad.

Desempates: si dudás entre sujeto_con_fondo y cara_closeup, mirá cuánto ocupa el rostro: si es
casi todo el cuadro, es cara_closeup. Si dudás entre sujeto_con_fondo y superficie_plana,
preguntate si hay un foco con vacío o distancia detrás; sin eso, es superficie_plana."""

_USER = "Clasificá la imagen adjunta según la taxonomía del sistema. Devolvé solo el JSON."

_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "categoria": {"type": "STRING", "enum": CATEGORIES},
        "confianza": {"type": "STRING", "enum": ["alta", "media", "baja"]},
        "razon": {"type": "STRING"},
    },
    "required": ["categoria", "confianza", "razon"],
}


def classify_image(image_path: Path) -> dict:
    """Una llamada Flash vision (temp 0, ciega). Devuelve {categoria, confianza, razon}.

    Fail-safe: si Flash falla o devuelve algo inválido → categoría 'otro' (NO promueve
    a zoom; el gate es conservador ante incertidumbre).
    """
    try:
        contents = [
            genai_types.Part.from_bytes(data=image_path.read_bytes(), mime_type="image/png"),
            _USER,
        ]
        resp = gemini_client.models.generate_content(
            model=api.gemini_model,
            contents=contents,
            config=genai_types.GenerateContentConfig(
                system_instruction=_SYSTEM, temperature=0.0,
                response_mime_type="application/json", response_schema=_SCHEMA,
            ),
        )
        cost_tracker.track_gemini_vision(description=f"zoom_judge:{image_path.stem}", calls=1)
        data = json.loads(resp.text)
        cat = str(data.get("categoria", "otro"))
        if cat not in CATEGORIES:
            cat = "otro"
        return {
            "categoria": cat,
            "confianza": str(data.get("confianza", "baja")),
            "razon": str(data.get("razon", ""))[:160],
        }
    except Exception as e:
        error_handler.log_warning(
            PipelineStage.ASSEMBLY,
            f"[zoom_judge] falló sobre {image_path.name} — categoría 'otro' (no promueve): {e}"[:200],
        )
        return {"categoria": "otro", "confianza": "baja", "razon": "judge_unavailable"}


def judge_candidates(candidates: dict[str, Path], cache_path: Path) -> dict[str, dict]:
    """Clasifica las candidatas (nombre→path) que pasaron el pre-filtro geométrico.

    Persiste/lee `zoom_verdicts.json`: las re-animaciones releen, no re-llaman
    (determinismo por construcción). Solo llama a Flash sobre las candidatas que
    aún no estén cacheadas.
    """
    verdicts: dict[str, dict] = {}
    if cache_path.exists():
        try:
            verdicts = json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            verdicts = {}

    dirty = False
    for name, path in candidates.items():
        if name in verdicts and verdicts[name].get("categoria") in CATEGORIES:
            continue
        verdicts[name] = classify_image(path)
        dirty = True

    if dirty:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(verdicts, indent=2, ensure_ascii=False), encoding="utf-8")

    return {n: verdicts[n] for n in candidates if n in verdicts}


def promotes_to_zoom(verdict: dict) -> bool:
    """Solo `sujeto_con_fondo` se promueve a zoom_in."""
    return verdict.get("categoria") == ZOOM_CATEGORY
