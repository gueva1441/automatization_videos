"""
approve.py — Copia los candidatos que eligió Omar a gfx_profiles/icons/<clave>.svg (F2b §3, PARADA 2).

Acento rojo solo donde significa algo (pedido de Omar):
  calavera → ojos: dos óvalos rojos DETRÁS de la tinta (el rojo se ve por los huecos de las cuencas)
  candado  → cerradura: el hueco que ya marcó trace.py
  cruz     → un clavo rojo en el cruce de los maderos (la cruz entera en rojo se leería como "Cruz Roja")
  resto    → sin rojo (se quita el acento automático)
Uso: python script_engine/gfx_icons/approve.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from script_engine.gfx_icons.make_icons import CAND_DIR, ICONS, ICONS_DIR, MANIFEST  # noqa: E402
from script_engine.gfx_icons.trace import ACCENT  # noqa: E402

# Elección de Omar en la PARADA 2 (número de la tira → candidato)
CHOICE: dict[str, str] = {"calavera": "b", "gota": "a", "llama": "a", "biohazard": "a", "reloj": "b", "candado": "a",
                          "ojo_tachado": "a", "balanza": "b", "cruz": "b", "persona": "b", "edificio_ruina": "b",
                          "pregunta": "a",
                          # F5d+ G4: elegidos por CC (sin PARADA de Omar): espiral «a» (sin marco), rayo tachado «b»
                          "espiral": "a", "rayo_tachado": "b"}
# calavera_2: centros de las cuencas medidos sobre el viewBox 200×200 (≤ 15 min a mano, regla del handoff)
SKULL_EYES: tuple[tuple[float, float, float, float], ...] = ((70.0, 85.0, 15.0, 10.5), (127.0, 85.0, 15.0, 10.5))
# cruz_2: clavo en el cruce de los maderos (viewBox 200×200)
CROSS_NAIL: tuple[float, float, float] = (101.0, 62.0, 6.0)


def approved_svg(key: str, svg: str) -> str:
    """SVG del candidato → SVG aprobado con el acento según la regla de Omar."""
    svg = re.sub(r'\s*<path class="ic-accent"[^>]*/>', "", svg) if key != "candado" else svg
    fill = re.search(r'<path class="ic-fill"[^>]*d="([^"]+)"/>', svg)
    if key == "calavera":
        eyes = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"/>' for x, y, rx, ry in SKULL_EYES)
        svg = svg.replace('<path class="ic-fill"', f'<g class="ic-accent" fill="{ACCENT}">{eyes}</g>\n<path class="ic-fill"', 1)
    elif key == "cruz" and fill:
        x, y, r = CROSS_NAIL
        # encima de todo (también de los contornos del engrave)
        svg = svg.replace("</svg>", f'<circle class="ic-accent" fill="{ACCENT}" cx="{x}" cy="{y}" r="{r}"/>\n</svg>', 1)
    return svg


def cmd_approve() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for n, (key, _obj) in enumerate(ICONS, start=1):
        k = "abc".index(CHOICE[key]) + 1
        src = CAND_DIR / f"{key}_{k}.svg"
        (ICONS_DIR / f"{key}.svg").write_text(approved_svg(key, src.read_text(encoding="utf-8")), encoding="utf-8")
        manifest["icons"][key]["approved"] = {"candidate": f"{n}{CHOICE[key]}", "file": f"{key}.svg",
                                              "accent": key in ("calavera", "candado", "cruz")}
        print(f"{n:2d}{CHOICE[key]} → {key}.svg")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    cmd_approve()
