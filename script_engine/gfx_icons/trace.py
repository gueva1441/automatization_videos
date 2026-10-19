"""
trace.py — PNG del t2i → SVG de paths reales (F2b §3). Determinista, sin red.

1. Gris, reducción a TRACE_PX, umbral fijo → tinta blanca = primer plano.
2. Se borra una banda de BORDER_FRAC en los bordes (marcos y rayones de la "etiqueta").
3. potrace (potracer) con turdsize → curvas Bézier. Se queda el sujeto: curvas cuya caja entra en la caja
   que une las piezas exteriores grandes (≥ BIG_FRAC de la principal, + margen). Caen manchas y rayones sueltos.
4. SVG:
   - <path class="ic-fill">   todas las curvas, fill-rule evenodd, blanco hueso (lo que se ve)
   - <path class="ic-accent"> un hueco chico del sujeto (0.3–6 % del área) relleno en el rojo del acento
                              (un solo detalle); si no hay ninguno de ese tamaño, no hay acento
   - <g class="ic-strokes">   contornos de las STROKE_TOP curvas más largas, para la animación `engrave`
   Todas las coordenadas en un viewBox cuadrado normalizado a VIEW (el ícono centrado, sin márgenes extra).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import potrace
from PIL import Image

TRACE_PX: int = 768
THRESHOLD: int = 140
BORDER_FRAC: float = 0.06
TURDSIZE: int = 20
KEEP_MARGIN: float = 0.04
BIG_FRAC: float = 0.03            # piezas ≥ 3 % del área de la principal definen la caja del sujeto
STROKE_TOP: int = 40
ACCENT_MIN: float = 0.003
ACCENT_MAX: float = 0.06
VIEW: int = 200
BONE: str = "#e8e0cc"
ACCENT: str = "#c8102e"


def _pts(curve: Any) -> list[tuple[float, float]]:
    out = [(curve.start_point.x, curve.start_point.y)]
    for s in curve.segments:
        if s.is_corner:
            out += [(s.c.x, s.c.y), (s.end_point.x, s.end_point.y)]
        else:
            out += [(s.c1.x, s.c1.y), (s.c2.x, s.c2.y), (s.end_point.x, s.end_point.y)]
    return out


def _bbox(pts: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _d(curve: Any, f: Any) -> str:
    """Curva potrace → comando SVG con la transformación f(x, y)."""
    x, y = f(curve.start_point.x, curve.start_point.y)
    parts = [f"M{x:.1f} {y:.1f}"]
    for s in curve.segments:
        if s.is_corner:
            (ax, ay), (bx, by) = f(s.c.x, s.c.y), f(s.end_point.x, s.end_point.y)
            parts.append(f"L{ax:.1f} {ay:.1f}L{bx:.1f} {by:.1f}")
        else:
            (ax, ay), (bx, by), (cx, cy) = f(s.c1.x, s.c1.y), f(s.c2.x, s.c2.y), f(s.end_point.x, s.end_point.y)
            parts.append(f"C{ax:.1f} {ay:.1f} {bx:.1f} {by:.1f} {cx:.1f} {cy:.1f}")
    return "".join(parts) + "Z"


def _length(pts: list[tuple[float, float]]) -> float:
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def trace_png(png: Path) -> dict[str, Any]:
    """PNG → {svg, n_paths, accent, bbox}. Nunca agrega texto."""
    im = Image.open(png).convert("L").resize((TRACE_PX, TRACE_PX), Image.LANCZOS)
    ink = np.array(im) > THRESHOLD
    b = int(TRACE_PX * BORDER_FRAC)
    ink[:b, :], ink[-b:, :], ink[:, :b], ink[:, -b:] = False, False, False, False
    plist = potrace.Bitmap(~ink).trace(turdsize=TURDSIZE, alphamax=1.0, opticurve=True, opttolerance=0.2)
    curves = [(c, bool(c._path.sign), abs(c._path.area), _pts(c)) for c in plist]   # sign True = contorno exterior
    outers = [x for x in curves if x[1]]
    if not outers:
        raise ValueError(f"{png.name}: sin tinta")
    main = max(outers, key=lambda x: x[2])
    big = [_bbox(x[3]) for x in outers if x[2] >= BIG_FRAC * main[2]]
    x0, y0 = min(bb[0] for bb in big), min(bb[1] for bb in big)
    x1, y1 = max(bb[2] for bb in big), max(bb[3] for bb in big)
    m = KEEP_MARGIN * TRACE_PX
    box = (x0 - m, y0 - m, x1 + m, y1 + m)
    keep = [x for x in curves if (lambda bb: bb[0] >= box[0] and bb[1] >= box[1] and bb[2] <= box[2] and bb[3] <= box[3])(_bbox(x[3]))]
    # encuadre: caja de todo lo que quedó → cuadrado centrado en VIEW
    allp = [p for x in keep for p in x[3]]
    bx0, by0, bx1, by1 = _bbox(allp)
    side = max(bx1 - bx0, by1 - by0)
    s = VIEW / side
    ox, oy = (VIEW - (bx1 - bx0) * s) / 2, (VIEW - (by1 - by0) * s) / 2
    f = lambda x, y: ((x - bx0) * s + ox, (y - by0) * s + oy)  # noqa: E731
    fill_d = "".join(_d(x[0], f) for x in keep)
    holes = [x for x in keep if not x[1] and x is not main]
    # acento: el hueco más grande DENTRO de la curva principal (un solo detalle rojo)
    mb = _bbox(main[3])
    inside = [h for h in holes if (lambda bb: bb[0] >= mb[0] and bb[1] >= mb[1] and bb[2] <= mb[2] and bb[3] <= mb[3])(_bbox(h[3]))]
    # "un solo detalle": hueco chico (ACCENT_MIN–ACCENT_MAX del área principal); el más grande de esos
    small = [h for h in inside if ACCENT_MIN * main[2] <= h[2] <= ACCENT_MAX * main[2]]
    accent = max(small, key=lambda h: h[2]) if small else None
    strokes = sorted(keep, key=lambda x: -_length(x[3]))[:STROKE_TOP]
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}" class="gfx-icon">',
           f'<path class="ic-fill" fill="{BONE}" fill-rule="evenodd" d="{fill_d}"/>']
    if accent is not None:
        svg.append(f'<path class="ic-accent" fill="{ACCENT}" d="{_d(accent[0], f)}"/>')
    svg.append(f'<g class="ic-strokes" fill="none" stroke="{BONE}" stroke-width="1.1" stroke-linejoin="round">')
    svg += [f'<path pathLength="1" d="{_d(x[0], f)}"/>' for x in strokes]
    svg += ["</g>", "</svg>"]
    return {"svg": "\n".join(svg), "n_paths": len(keep), "accent": accent is not None,
            "dropped": len(curves) - len(keep)}


def cmd_trace() -> None:
    from script_engine.gfx_icons.make_icons import CAND_DIR, ENGINE, ICONS, MANIFEST, RAW_DIR, SEEDS, SIZE, prompt_for
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"engine": ENGINE, "size": SIZE, "seeds": list(SEEDS),
                                "trace": {"px": TRACE_PX, "threshold": THRESHOLD, "border_frac": BORDER_FRAC,
                                          "turdsize": TURDSIZE, "keep_margin": KEEP_MARGIN},
                                "icons": {}}
    for n, (key, obj) in enumerate(ICONS, start=1):
        entry = {"num": n, "object": obj, "prompt": prompt_for(obj), "candidates": {}}
        for k, seed in enumerate(SEEDS, start=1):
            png = RAW_DIR / f"{key}_{k}.png"
            if not png.exists():
                print(f"falta {png.name}")
                continue
            r = trace_png(png)
            out = CAND_DIR / f"{key}_{k}.svg"
            out.write_text(r["svg"], encoding="utf-8")
            entry["candidates"][f"{n}{'abc'[k - 1]}"] = {"file": out.name, "seed": seed, "paths": r["n_paths"],
                                                         "accent": r["accent"], "dropped": r["dropped"],
                                                         "kb": round(out.stat().st_size / 1024, 1)}
            print(f"{n:2d}{'abc'[k - 1]} {key}_{k}: {r['n_paths']} paths (−{r['dropped']}), acento={r['accent']}, "
                  f"{out.stat().st_size / 1024:.0f} KB", flush=True)
        manifest["icons"][key] = entry
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
