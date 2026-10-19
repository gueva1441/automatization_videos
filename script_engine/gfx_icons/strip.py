"""
strip.py — tira_iconos_12.jpg para que Omar elija (F2b §3, PARADA 2).

Una composición HyperFrames de 1.2 s (las MISMAS funciones del templater: scoped_svg + anim_js) con los
36 candidatos sobre un frame de ch02. Por ícono, una celda:
  fila 1: los 3 candidatos terminados (engrave arrancó en t = 0)
  fila 2: los mismos 3 con `engrave` a mitad (arrancó en t = 0.6 → en el cuadro de t = 1.0 van 0.4 de 0.8 s)
Se renderiza con el CLI de HyperFrames (lint incluido) y se saca el cuadro de t = 1.0 s.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from gfx_config import gfx_rules
from script_engine.gfx_icons import ENGRAVE_SEC, anim_js, scoped_svg
from script_engine.gfx_icons.make_icons import CAND_DIR, ICONS, MANIFEST, ROOT

W, H, FPS = 2560, 1440, 30
DUR, SHOT_T = 1.2, 1.0
MID_START = SHOT_T - ENGRAVE_SEC / 2           # a mitad del engrave en el cuadro de la tira
CELL_W, CELL_H = 640, 480
ICON = 150
NOTES = {"reloj": "ojo: trae números (texto)"}


def build(bg: Path, project: Path) -> Path:
    from script_engine.gfx_project import _tpl
    from gfx_config import gsap_js
    (project / "public").mkdir(parents=True, exist_ok=True)
    (project / "vendor").mkdir(parents=True, exist_ok=True)
    shutil.copy2(bg, project / "public" / "bg.jpg")
    shutil.copy2(gsap_js(), project / "vendor" / "gsap.min.js")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    overlays = [f'      <img class="clip" src="public/bg.jpg" data-start="0" data-duration="{DUR}" alt="" '
                f'style="position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover" />']
    init: list[str] = []
    js: list[str] = []
    for n, (key, _obj) in enumerate(ICONS, start=1):
        cx, cy = ((n - 1) % 4) * CELL_W, ((n - 1) // 4) * CELL_H
        cands = manifest["icons"][key]["candidates"]
        note = f' <span style="color:{gfx_rules.accent_hex}">· {NOTES[key]}</span>' if key in NOTES else ""
        cell = [f'<div style="position:absolute;left:{cx + 8}px;top:{cy + 8}px;width:{CELL_W - 16}px;height:{CELL_H - 16}px;'
                f'background:rgba(0,0,0,.42);border:1px solid rgba(232,224,204,.25)">'
                f'<div style="font:400 30px/1 Arial,sans-serif;color:#f4f1ea;padding:10px 14px">{n} · {key}{note}</div>']
        for row, t0 in ((0, 0.0), (1, MID_START)):
            for j, (lab, c) in enumerate(sorted(cands.items())):
                uid = f"t{n}{lab[-1]}{row}"
                svg = (CAND_DIR / c["file"]).read_text(encoding="utf-8")
                x, y = 30 + j * (ICON + 52), 56 + row * (ICON + 52)
                cell.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{ICON}px">{scoped_svg(svg, uid, ICON)}'
                            f'<div style="font:700 22px/1 Arial,sans-serif;color:#f4f1ea;text-align:center;margin-top:4px">'
                            f'{lab}{" · a mitad" if row else ""}</div></div>')
                a_init, a_js = anim_js(uid, "engrave", t0, DUR + 10)    # sin salida dentro de la tira
                init += a_init
                js += a_js
        cell.append("</div>")
        overlays.append(f'      <div class="clip" data-start="0" data-duration="{DUR}" style="position:absolute;inset:0">'
                        + "".join(cell) + "</div>")
    html = _tpl("index.html.tmpl").substitute(width=W, height=H, duration=f"{DUR:.3f}",
                                              css="      html, body { margin: 0; background: #000; }",
                                              scene_hosts="", overlays="\n".join(overlays),
                                              init_js="\n".join(init), timeline_js="\n".join(js))
    (project / "index.html").write_text(html, encoding="utf-8")
    (project / "hyperframes.json").write_text(json.dumps({"media": {"autoProxy": True}}), encoding="utf-8")
    return project / "index.html"


def cmd_strip(bg: Path) -> None:
    from script_engine.gfx_layer import _lint, _render
    out_dir = ROOT / "lab" / "hyperframes" / "f2b"
    project = out_dir / "tira_iconos_proj"
    build(bg, project)
    lint = _lint(project)
    print(f"lint: {lint.get('errorCount')} errores, {lint.get('warningCount')} warnings", flush=True)
    mp4 = project / "renders" / "tira.mp4"
    mp4.parent.mkdir(parents=True, exist_ok=True)
    _render(project, mp4, "looks")
    jpg = out_dir / "tira_iconos_12.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{SHOT_T:.3f}", "-i", str(mp4), "-frames:v", "1", "-q:v", "3",
                    str(jpg)], check=True, timeout=120)
    print(f"→ {jpg} ({jpg.stat().st_size // 1024} KB)")
