"""
make_icons.py — Set propio de 12 íconos de la capa gráfica (F2b §3).

Estilo: grabado / etiqueta de veneno 1890 / forense. Blanco hueso, un solo detalle en el rojo del acento.
Nunca estilo ícono de interfaz. Sin texto dentro del ícono.

Pasos (cada uno cachea su salida; re-correr no re-gasta):
  gen    → t2i con el motor del pipeline (Flux.2 Pro, fal) : prompt base FIJO + objeto, 3 semillas fijas por ícono
           → lab/hyperframes/f2b/icons_raw/<key>_<k>.png
  trace  → umbral a blanco/negro + potrace (potracer, port puro de potrace) → SVG con paths reales
           → gfx_profiles/icons/candidates/<key>_<k>.svg   (+ manifest.json con prompt, seed y motor)
  strip  → tira_iconos_12.jpg: 3 candidatos por ícono sobre un fondo de ch02 + fila con `engrave` a mitad

Uso:
  python script_engine/gfx_icons/make_icons.py gen
  python script_engine/gfx_icons/make_icons.py trace
  python script_engine/gfx_icons/make_icons.py strip <frame_fondo.jpg>
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from config import api  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402

RAW_DIR: Path = ROOT / "lab" / "hyperframes" / "f2b" / "icons_raw"
ICONS_DIR: Path = ROOT / "gfx_profiles" / "icons"
CAND_DIR: Path = ICONS_DIR / "candidates"
MANIFEST: Path = ICONS_DIR / "manifest.json"

ENGINE: str = "fal-ai/flux-2-pro"            # motor t2i del pipeline (api.fal_image_model)
SIZE: dict[str, int] = {"width": 1024, "height": 1024}
SEEDS: tuple[int, ...] = (1441, 1442, 1443)  # mismas 3 semillas para todo el set
PROMPT_BASE: str = ("1890 poison label woodcut, single {obj}, white ink on pure black background, thick irregular "
                    "engraved strokes, no text, no letters, centered, isolated")

# clave → objeto (en inglés, como los prompts de imagen del pipeline). Orden = número en la tira.
ICONS: tuple[tuple[str, str], ...] = (
    ("calavera", "human skull"),
    ("gota", "drop of liquid"),
    ("llama", "flame"),
    ("biohazard", "biohazard symbol"),
    ("reloj", "pocket watch"),
    ("candado", "padlock"),
    ("ojo_tachado", "eye crossed out by one diagonal slash"),
    ("balanza", "balance scale of justice"),
    ("cruz", "grave cross"),
    ("persona", "standing human figure"),
    ("edificio_ruina", "ruined building"),
    ("pregunta", "question mark symbol"),
)


def prompt_for(obj: str) -> str:
    return PROMPT_BASE.format(obj=obj)


def _headers() -> dict[str, str]:
    return {"Authorization": f"Key {api.fal_api_key}", "Content-Type": "application/json"}


def generate_one(key: str, obj: str, k: int, seed: int) -> Path:
    """1 imagen Flux.2 Pro (fal SYNC). Cacheada: si existe el PNG no se vuelve a pedir."""
    out = RAW_DIR / f"{key}_{k}.png"
    if out.exists():
        return out
    payload = {"prompt": prompt_for(obj), "num_images": 1, "enable_safety_checker": True, "output_format": "png",
               "image_size": SIZE, "seed": seed}
    last: Exception | None = None
    for attempt in range(3):                       # reintentos con backoff (errores de red / 5xx)
        try:
            r = requests.post(f"{api.fal_sync_base_url}/{ENGINE}", headers=_headers(), json=payload, timeout=180)
            r.raise_for_status()
            img = r.json()["images"][0]
            data = requests.get(img["url"], timeout=60)
            data.raise_for_status()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data.content)
            cost_tracker.track_flux_pro(description=f"gfx_icon:{key}_{k}", images=1)
            return out
        except Exception as e:  # noqa: BLE001
            last = e
            import time
            time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"{key}_{k}: {last}")


def cmd_gen() -> None:
    jobs = [(key, obj, k, seed) for key, obj in ICONS for k, seed in enumerate(SEEDS, start=1)]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for p in ex.map(lambda j: generate_one(*j), jobs):
            print("ok", p.name, flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "gen":
        cmd_gen()
    elif cmd == "trace":
        from script_engine.gfx_icons.trace import cmd_trace
        cmd_trace()
    elif cmd == "strip":
        from script_engine.gfx_icons.strip import cmd_strip
        cmd_strip(Path(sys.argv[2]))
    else:
        print(__doc__)
