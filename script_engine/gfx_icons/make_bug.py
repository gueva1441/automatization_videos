"""
make_bug.py — Marca del canal (`channel_bug`, F4b §0): encapuchado con farol, mismo pipeline que los 12 íconos.

  gen    → Flux.2 Pro (fal), 1024², 3 semillas fijas → lab/hyperframes/f4b/bug_raw/bug_<k>.png (cacheado)
  trace  → potrace (trace.trace_png) de la silueta + la LLAMA aparte en <g id="flame"> (color cálido #e8a84a)
           → gfx_profiles/bug/candidates/bug_<k>.svg
  strip  → lab/hyperframes/f4b/tira_marca_canal.jpg: cada candidato a tamaño de esquina (4 % de alto) sobre un
           frame oscuro de ch02 y grande (como en el cierre del video)

La llama: el prompt la pide como "el único detalle iluminado". Se busca primero por COLOR (píxeles cálidos y
saturados); si el t2i la dibujó en blanco, por BRILLO dentro de la mitad del farol (la mancha clara más compacta
cerca del extremo del brazo). La llama se resta de la silueta para que no quede duplicada.
"""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from config import api  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402

RAW_DIR: Path = ROOT / "lab" / "hyperframes" / "f4b" / "bug_raw"
CAND_DIR: Path = ROOT / "gfx_profiles" / "bug" / "candidates"
ENGINE: str = "fal-ai/flux-2-pro"
SEEDS: tuple[int, ...] = (1441, 1442, 1443)
PROMPT: str = ("1890 woodcut engraving, hooded figure holding a lantern, three-quarter view, white ink on pure black, "
               "thick irregular engraved strokes, the lantern flame as the only lit detail, no text, centered, isolated")
FLAME_HEX: str = "#e8a84a"


def generate_one(k: int, seed: int) -> Path:
    out = RAW_DIR / f"bug_{k}.png"
    if out.exists():
        return out
    payload = {"prompt": PROMPT, "num_images": 1, "enable_safety_checker": True, "output_format": "png",
               "image_size": {"width": 1024, "height": 1024}, "seed": seed}
    headers = {"Authorization": f"Key {api.fal_api_key}", "Content-Type": "application/json"}
    last: Exception | None = None
    for attempt in range(3):
        try:
            r = requests.post(f"{api.fal_sync_base_url}/{ENGINE}", headers=headers, json=payload, timeout=180)
            r.raise_for_status()
            data = requests.get(r.json()["images"][0]["url"], timeout=60)
            data.raise_for_status()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data.content)
            cost_tracker.track_flux_pro(description=f"channel_bug_{k}", images=1)
            return out
        except Exception as e:  # noqa: BLE001
            last = e
            import time
            time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"bug_{k}: {last}")


def _label(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """Componentes conexas (4-vecinos) sin scipy: barrido con union-find por filas."""
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    parent = [0]

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    nxt = 1
    for y in range(h):
        row = mask[y]
        for x in np.flatnonzero(row):
            up = lab[y - 1, x] if y else 0
            left = lab[y, x - 1] if x else 0
            if up and left:
                a, b = find(up), find(left)
                lab[y, x] = min(a, b)
                if a != b:
                    parent[max(a, b)] = min(a, b)
            elif up or left:
                lab[y, x] = up or left
            else:
                parent.append(nxt)
                lab[y, x] = nxt
                nxt += 1
    roots = np.array([find(i) for i in range(nxt)], np.int32)
    lab = roots[lab]
    uniq = np.unique(lab[lab > 0])
    remap = np.zeros(nxt, np.int32)
    remap[uniq] = np.arange(1, len(uniq) + 1)
    return remap[lab], len(uniq)


def _dilate(m: np.ndarray, it: int) -> np.ndarray:
    out = m.copy()
    for _ in range(it):
        o = out.copy()
        o[1:] |= out[:-1]; o[:-1] |= out[1:]; o[:, 1:] |= out[:, :-1]; o[:, :-1] |= out[:, 1:]
        out = o
    return out


def flame_box(png: Path) -> list[float] | None:
    """Caja [x, y, w, h] (0–1) de la llama del farol según Gemini visión (judge_zoom_box). Cacheada en bug_raw/."""
    import json
    cache = png.with_suffix(".flame.json")
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8")).get("box")
    from script_engine.gfx_director import judge_zoom_box
    jpg = png.with_suffix(".jpg")
    Image.open(png).convert("RGB").save(jpg, quality=92)
    r = judge_zoom_box(jpg, "la llama encendida dentro del farol (solo el fuego, no el farol entero)")
    cache.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    return r.get("box")


def flame_mask(png: Path) -> tuple[np.ndarray, str]:
    """Máscara (768²) de la llama + cómo se encontró. Primero por COLOR (píxeles cálidos); si el t2i la dibujó en
    blanco, los píxeles claros DENTRO de la caja de la llama que da visión (F4b: el brillo solo elegía la capucha)."""
    im = Image.open(png).convert("RGB").resize((768, 768), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    warm = (r > 150) & (r - b > 60) & (g > 80)
    if warm.sum() >= 40:
        lab, n = _label(warm)
        sizes = np.bincount(lab.ravel())[1:]
        k = int(np.argmax(sizes)) + 1
        return _dilate(lab == k, 2), "color"
    box = flame_box(png)
    if not box:
        return np.zeros((768, 768), bool), "ninguna"
    x, y, w, h = box
    pad = 0.15
    x0, y0 = int(max(0, (x - w * pad)) * 768), int(max(0, (y - h * pad)) * 768)
    x1, y1 = int(min(1, x + w * (1 + pad)) * 768), int(min(1, y + h * (1 + pad)) * 768)
    m = np.zeros((768, 768), bool)
    m[y0:y1, x0:x1] = a[y0:y1, x0:x1].mean(axis=2) > 170
    return _dilate(m, 1), "visión"


def trace_bug(png: Path) -> dict:
    """Silueta (trace_png sobre la imagen SIN llama) + llama trazada aparte en <g id="flame">."""
    from script_engine.gfx_icons import trace as tr
    import tempfile
    fm, how = flame_mask(png)
    im = Image.open(png).convert("L").resize((768, 768), Image.LANCZOS)
    a = np.asarray(im).copy()
    a[fm] = 0                                                   # la silueta no lleva la llama
    with tempfile.TemporaryDirectory() as td:
        body_png = Path(td) / "body.png"
        Image.fromarray(a).save(body_png)
        body = tr.trace_png(body_png)
        flame_svg = ""
        if fm.any():
            fl = np.where(fm, 255, 0).astype(np.uint8)
            # misma caja que la silueta: se traza la llama sobre la imagen completa y se re-encuadra igual
            both = np.maximum(a, fl)
            both_png = Path(td) / "both.png"
            Image.fromarray(both).save(both_png)
            whole = tr.trace_png(both_png)
            flame_svg = _flame_paths(fl, body_png, both_png)
    import re
    body["svg"] = re.sub(r'<path class="ic-accent"[^>]*/>\s*', "", body["svg"])   # la marca no lleva rojo: solo la llama
    svg = body["svg"].replace("</svg>", f'<g id="flame" fill="{FLAME_HEX}">{flame_svg}</g>\n</svg>') if flame_svg else body["svg"]
    return {"svg": svg, "flame": how, "n_paths": body["n_paths"]}


def _flame_paths(fl: np.ndarray, body_png: Path, both_png: Path) -> str:
    """Contornos de la llama en el MISMO sistema de coordenadas que la silueta (encuadre de trace_png)."""
    import potrace
    from script_engine.gfx_icons import trace as tr
    # encuadre de la silueta: se repite el cálculo de trace_png sobre body_png
    im = Image.open(body_png).convert("L")
    ink = np.array(im) > tr.THRESHOLD
    bnd = int(tr.TRACE_PX * tr.BORDER_FRAC)
    ink[:bnd, :], ink[-bnd:, :], ink[:, :bnd], ink[:, -bnd:] = False, False, False, False
    curves = [(c, bool(c._path.sign), abs(c._path.area), tr._pts(c)) for c in
              potrace.Bitmap(~ink).trace(turdsize=tr.TURDSIZE, alphamax=1.0, opticurve=True, opttolerance=0.2)]
    outers = [x for x in curves if x[1]]
    main = max(outers, key=lambda x: x[2])
    big = [tr._bbox(x[3]) for x in outers if x[2] >= tr.BIG_FRAC * main[2]]
    m = tr.KEEP_MARGIN * tr.TRACE_PX
    box = (min(b[0] for b in big) - m, min(b[1] for b in big) - m, max(b[2] for b in big) + m, max(b[3] for b in big) + m)
    keep = [x for x in curves if (lambda bb: bb[0] >= box[0] and bb[1] >= box[1] and bb[2] <= box[2] and bb[3] <= box[3])(tr._bbox(x[3]))]
    allp = [p for x in keep for p in x[3]]
    bx0, by0, bx1, by1 = tr._bbox(allp)
    side = max(bx1 - bx0, by1 - by0)
    s = tr.VIEW / side
    ox, oy = (tr.VIEW - (bx1 - bx0) * s) / 2, (tr.VIEW - (by1 - by0) * s) / 2
    f = lambda x, y: ((x - bx0) * s + ox, (y - by0) * s + oy)  # noqa: E731
    fc = potrace.Bitmap(~(fl > 0)).trace(turdsize=4, alphamax=1.0, opticurve=True, opttolerance=0.2)
    paths = [c for c in fc if abs(c._path.area) < 0.5 * fl.size]          # sin el contorno del cuadro entero
    return "".join(f'<path fill-rule="evenodd" d="{tr._d(c, f)}"/>' for c in paths)


def cmd_gen() -> None:
    with ThreadPoolExecutor(max_workers=3) as ex:
        for p in ex.map(lambda j: generate_one(*j), list(enumerate(SEEDS, start=1))):
            print("ok", p.name, flush=True)


def cmd_trace() -> None:
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    for k in range(1, len(SEEDS) + 1):
        r = trace_bug(RAW_DIR / f"bug_{k}.png")
        (CAND_DIR / f"bug_{k}.svg").write_text(r["svg"], encoding="utf-8")
        print(f"bug_{k}: {r['n_paths']} paths · llama por {r['flame']}", flush=True)


if __name__ == "__main__":
    {"gen": cmd_gen, "trace": cmd_trace}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()


def render_svg(svg: str, px: int, out: Path) -> Image.Image:
    """SVG → RGBA px×px (chrome headless de HyperFrames sobre negro; alfa = luminancia)."""
    from script_engine.gfx_icons.shot import screenshot
    svg = svg.replace('class="gfx-icon"', f'class="gfx-icon" width="{px}" height="{px}"')
    svg = svg.replace('<g class="ic-strokes"', '<g class="ic-strokes" style="display:none"')
    page = out.with_suffix(".html")
    page.write_text(f'<!doctype html><html><body style="margin:0;background:#000">{svg}</body></html>', encoding="utf-8")
    screenshot(page, out, px, px)
    rgb = Image.open(out).convert("RGB").crop((0, 0, px, px))
    a = np.asarray(rgb).astype(np.float32)
    alpha = np.clip(a.max(axis=2) * 1.6, 0, 255).astype(np.uint8)
    rgba = rgb.copy()
    rgba.putalpha(Image.fromarray(alpha))
    return rgba


def cmd_strip() -> None:
    """tira_marca_canal.jpg. Por candidato (columna): frame oscuro de ch02 con la marca en la esquina superior izquierda
    a 4 % de alto y opacidad 0.55 · la misma esquina ampliada ×4 (para ver el detalle) · la marca grande (25 % de alto)
    al centro sobre negro, como en el cierre."""
    import subprocess
    from PIL import ImageDraw
    out_dir = ROOT / "lab" / "hyperframes" / "f4b"
    work = out_dir / "_tira_bug"
    work.mkdir(parents=True, exist_ok=True)
    base = ROOT / "output" / "ba6c3cac-a091-41c0-8dad-afd2f4364747" / "_fase2b_work" / "ch02_flux_visual.mp4"
    bg_p = work / "bg.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "96.0", "-i", str(base), "-frames:v", "1", str(bg_p)], check=True)
    bg = Image.open(bg_p).convert("RGB").resize((2560, 1440))
    W, H = 2560, 1440
    corner, big = int(H * 0.04), int(H * 0.25)
    cw = 960
    sheet = Image.new("RGB", (3 * cw + 4 * 20, 540 + 20 + 360 + 20 + 540 + 80), (17, 17, 17))
    d = ImageDraw.Draw(sheet)
    for k in range(1, len(SEEDS) + 1):
        svg = (CAND_DIR / f"bug_{k}.svg").read_text(encoding="utf-8")
        ic = render_svg(svg, 512, work / f"bug_{k}.png")
        fr = bg.copy()
        small = ic.resize((corner, corner), Image.LANCZOS)
        sa = np.asarray(small).copy()
        sa[..., 3] = (sa[..., 3] * 0.55).astype(np.uint8)
        x0, y0 = int(W * 0.03), int(H * 0.035)
        fr.paste(Image.fromarray(sa), (x0, y0), Image.fromarray(sa))
        x = 20 + (k - 1) * (cw + 20)
        sheet.paste(fr.resize((cw, 540)), (x, 20))
        zoom = fr.crop((0, 0, 240, 135)).resize((cw, 540 * 360 // 540 * 1), Image.LANCZOS).resize((cw, 360))
        sheet.paste(zoom, (x, 20 + 540 + 20))
        bk = Image.new("RGB", (cw, 540), (0, 0, 0))
        bb = ic.resize((big * 540 // H, big * 540 // H), Image.LANCZOS)
        bk.paste(bb, ((cw - bb.width) // 2, (540 - bb.height) // 2), bb)
        sheet.paste(bk, (x, 20 + 540 + 20 + 360 + 20))
        d.text((x + cw // 2 - 10, sheet.height - 60), str(k), fill=(230, 230, 230))
    dst = out_dir / "tira_marca_canal.jpg"
    sheet.save(dst, quality=90)
    print("ok", dst)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "strip":
    cmd_strip()
