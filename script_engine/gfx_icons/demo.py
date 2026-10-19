"""
demo.py — demo de 6 s de las animaciones del ícono (pre-merge): press_wipe (gota), ink_bleed (calavera y cruz),
stamp (candado) + hold vivo + salida "tinta que se seca", sobre un frame de ch02. Mismas funciones que el templater.
Uso: python script_engine/gfx_icons/demo.py <fondo.jpg> <salida.mp4>
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from gfx_config import gsap_js  # noqa: E402
from script_engine.gfx_icons import anim_js, icon_svg, scoped_svg  # noqa: E402

W, H, DUR = 2560, 1440, 6.0
ITEMS = (("gota", "press_wipe", "agua"), ("calavera", "ink_bleed", "cadáveres"),
         ("cruz", "ink_bleed", "tumba"), ("candado", "stamp", "encerrados"))


def build(bg: Path, project: Path) -> None:
    from script_engine.gfx_project import _tpl
    (project / "public").mkdir(parents=True, exist_ok=True)
    (project / "vendor").mkdir(parents=True, exist_ok=True)
    shutil.copy2(bg, project / "public" / "bg.jpg")
    shutil.copy2(gsap_js(), project / "vendor" / "gsap.min.js")
    overlays = [f'      <img class="clip" src="public/bg.jpg" data-start="0" data-duration="{DUR}" alt="" '
                f'style="position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover" />']
    init: list[str] = []
    js: list[str] = []
    for i, (key, anim, word) in enumerate(ITEMS):
        svg = icon_svg(key)
        uid = f"d{i}"
        t0 = 0.3 + 0.35 * i
        overlays.append(f'      <div class="clip" data-start="0" data-duration="{DUR}" style="position:absolute;left:{220 + 560 * i}px;'
                        f'top:430px;width:300px;text-align:center">{scoped_svg(svg, uid, 300)}'
                        f'<div style="font:400 44px/1.2 Arial,sans-serif;color:#f4f1ea;margin-top:16px">{anim}<br/>«{word}»</div></div>')
        a_init, a_js = anim_js(uid, anim, t0, DUR - 0.2, has_accent='class="ic-accent"' in svg)
        init += a_init
        js += a_js
    html = _tpl("index.html.tmpl").substitute(width=W, height=H, duration=f"{DUR:.3f}",
                                              css="      html, body { margin: 0; background: #000; }", scene_hosts="",
                                              overlays="\n".join(overlays), init_js="\n".join(init), timeline_js="\n".join(js))
    (project / "index.html").write_text(html, encoding="utf-8")
    (project / "hyperframes.json").write_text(json.dumps({"media": {"autoProxy": True}}), encoding="utf-8")


if __name__ == "__main__":
    from script_engine.gfx_layer import _lint, _render
    bg, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    proj = out.parent / (out.stem + "_proj")
    build(bg, proj)
    lint = _lint(proj)
    print(f"lint: {lint.get('errorCount')} errores, {lint.get('warningCount')} warnings")
    _render(proj, out, "looks")
    print("→", out)
