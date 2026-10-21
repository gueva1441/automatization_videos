"""
gfx_icons — íconos de la capa gráfica (F2b §3).

Set propio (12 SVG de grabado, generados con make_icons.py + trace.py) con respaldo Lucide restilizado.
El director NUNCA inventa un SVG: solo elige claves de ICON_WHITELIST. Si la clave no tiene archivo
aprobado (gfx_profiles/icons/<clave>.svg) ni respaldo declarado, no hay ícono (texto solo).

Animaciones (GSAP, seek-safe, sin shaders):
  ink_bleed   tinta que se expande desde el centro con borde irregular (0.7 s)   → moods veneno / muerte
  press_wipe  revelado de arriba abajo con borde rugoso, como una prensa (0.8 s)  → agua / evidencia
  engrave     contornos trazo a trazo: SOLO para íconos de trazos reales (Lucide). Los SVG de potrace son
              RELLENOS (las líneas del grabado son manchas): ahí engrave dibujaba el contorno de las manchas,
              no los trazos → sobre potrace se usa press_wipe (pre-merge, pedido de Omar)
  stamp       sello (el mismo del data_callout)
  hold vivo   entre la entrada y la salida: respiración de opacidad 0.85–1, deriva ±3 px y un único pulso del
              rojo; nunca quieto más de 1 s
  salida      "tinta que se seca": se agrietan puntos de la tinta y se apaga (0.45 s)
"""
from __future__ import annotations

import random
import re
import zlib
from pathlib import Path

from gfx_config import GFX_PROFILES_DIR

ICONS_DIR: Path = GFX_PROFILES_DIR / "icons"
LUCIDE_DIR: Path = ICONS_DIR / "lucide"

# Lista blanca: las 12 claves del set (orden = número en la tira) → nombre del respaldo Lucide (MIT)
ICON_WHITELIST: dict[str, str] = {
    "calavera": "skull", "gota": "droplet", "llama": "flame", "biohazard": "biohazard", "reloj": "clock",
    "candado": "lock", "ojo_tachado": "eye-off", "balanza": "scale", "cruz": "cross", "persona": "person-standing",
    "edificio_ruina": "building", "pregunta": "circle-help",
}
VALID_ICON_ANIMS: frozenset[str] = frozenset({"ink_bleed", "press_wipe", "engrave", "stamp"})
ENGRAVE_SEC: float = 0.8
PRESS_SEC: float = 0.8
BREATH_SEC: float = 0.9          # medio ciclo de respiración (< 1 s: nunca quieto más de 1 s)
DRIFT_SEC: float = 1.4
DRIFT_PX: float = 3.0
INK_SEC: float = 0.7
DRY_SEC: float = 0.45
BONE: str = "#e8e0cc"


def icon_svg(key: str | None, *, fallback: bool = False) -> str | None:
    """SVG aprobado de la clave (gfx_profiles/icons/<clave>.svg). Con fallback=True y sin SVG propio → Lucide
    restilizado. Clave fuera de la lista blanca o sin archivo → None (sin ícono; nunca uno equivocado)."""
    if key and key.startswith("gi:"):                 # F4b §4: game-icons.net (CC BY 3.0) restilizado
        from script_engine.gfx_icons.auto_icons import game_icon_svg
        return game_icon_svg(key)
    if not key or key not in ICON_WHITELIST:
        return None
    own = ICONS_DIR / f"{key}.svg"
    if own.exists():
        return own.read_text(encoding="utf-8")
    luc = LUCIDE_DIR / f"{ICON_WHITELIST[key]}.svg"
    if fallback and luc.exists():
        return lucide_restyled(luc.read_text(encoding="utf-8"))
    return None


def lucide_restyled(svg: str) -> str:
    """Lucide (trazo de interfaz) → SVG normalizado del set: solo contornos (`ic-strokes`), color hueso y trazo
    grueso; el filtro de tinta de scoped_svg le rompe el borde. Sin texto (Lucide no trae)."""
    view = re.search(r'viewBox="([^"]+)"', svg)
    inner = re.sub(r"(?s)^.*?<svg[^>]*>|</svg>\s*$", "", re.sub(r"(?s)<!--.*?-->", "", svg)).strip()
    inner = re.sub(r"<(path|circle|line|polyline|polygon|rect|ellipse)\b", r'<\1 pathLength="1"', inner)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view.group(1) if view else "0 0 24 24"}" class="lucide-ink">'
            f'<g class="ic-strokes" fill="none" stroke="{BONE}" stroke-width="2.4" stroke-linecap="round" '
            f'stroke-linejoin="round">{inner}</g></svg>')


def scoped_svg(svg: str, uid: str, size_px: int) -> str:
    """SVG con ids únicos (uid), máscara de secado y filtro de tinta. Tamaño fijo en px."""
    vb = re.search(r'viewBox="([^"]+)"', svg)
    view = vb.group(1) if vb else "0 0 200 200"
    w = float(view.split()[2])                                # 200 (set propio) o 24 (Lucide)
    k = w / 200.0
    rnd = random.Random(zlib.crc32(uid.encode()))          # determinista entre procesos
    dots = "".join(f'<circle cx="{rnd.uniform(.025, .975) * w:.2f}" cy="{rnd.uniform(.025, .975) * w:.2f}" r="0"/>'
                   for _ in range(70))
    defs = (f'<defs><mask id="{uid}-dry" maskUnits="userSpaceOnUse" x="{-.1 * w:.1f}" y="{-.1 * w:.1f}" '
            f'width="{1.2 * w:.1f}" height="{1.2 * w:.1f}"><rect x="{-.1 * w:.1f}" y="{-.1 * w:.1f}" width="{1.2 * w:.1f}" '
            f'height="{1.2 * w:.1f}" fill="#fff"/><g class="dry" fill="#000" data-k="{k:.3f}">{dots}</g></mask>'
            f'<filter id="{uid}-ink" x="-20%" y="-20%" width="140%" height="140%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{0.06 / k:.3f}" numOctaves="2" seed="7"/>'
            f'<feDisplacementMap id="{uid}-dm" in="SourceGraphic" scale="0"/></filter>'
            # press_wipe: polígono blanco con el borde de abajo rugoso; arranca ABIERTO (y = 1.2 w) y la
            # animación lo sube a −0.06 w para después bajarlo
            f'<mask id="{uid}-pw" maskUnits="userSpaceOnUse" x="{-.1 * w:.1f}" y="{-1.4 * w:.1f}" width="{1.2 * w:.1f}" '
            f'height="{2.8 * w:.1f}"><g class="pw" transform="translate(0 {1.2 * w:.2f})"><path fill="#fff" d="{_rough_edge(w, rnd)}"/></g></mask>'
            f'</defs>')
    body = re.sub(r"(?s)^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    return (f'<svg id="{uid}" class="gfx-icon" xmlns="http://www.w3.org/2000/svg" viewBox="{view}" '
            f'width="{size_px}" height="{size_px}" style="overflow:visible">{defs}'
            f'<g class="ic-body" mask="url(#{uid}-dry)" filter="url(#{uid}-ink)"><g class="ic-pw" mask="url(#{uid}-pw)">'
            f'{body}</g></g></svg>')


def _rough_edge(w: float, rnd: random.Random) -> str:
    """Polígono que cubre de −1.3 w a 0, con el borde inferior rugoso (±4 % del ancho, cada 5 %)."""
    xs = [(-.1 + .05 * i) * w for i in range(25)]
    bottom = "".join(f"L{x:.2f} {rnd.uniform(-.04, .04) * w:.2f}" for x in reversed(xs))
    return f"M{-.1 * w:.2f} {-1.3 * w:.2f}L{1.1 * w:.2f} {-1.3 * w:.2f}{bottom}Z"


def anim_js(uid: str, anim: str, t0: float, end: float, *, k: float = 1.0, strokes_only: bool = False,
            has_accent: bool = False, hold: bool = True) -> tuple[list[str], list[str]]:
    """(init, timeline): entrada `anim` en t0, hold vivo y salida "tinta que se seca" que termina en `end`.
    k = ancho del viewBox / 200 (Lucide 0.12); strokes_only = ícono de solo contornos (Lucide): no se apagan.
    engrave sobre un SVG de rellenos (potrace) se convierte en press_wipe."""
    s = f"#{uid}"
    init: list[str] = []
    js: list[str] = []
    if anim == "engrave" and not strokes_only:
        anim = "press_wipe"
    w = 200.0 * k
    enter = {"press_wipe": PRESS_SEC, "engrave": ENGRAVE_SEC, "ink_bleed": INK_SEC}.get(anim, .18)
    if anim == "press_wipe":
        init.append(f'      gsap.set("{s} .pw", {{ y: {-.06 * w:.2f} }}); gsap.set("{s} .ic-strokes", {{ opacity: 0 }});')
        js.append(f'      tl.to("{s} .pw", {{ y: {1.2 * w:.2f}, duration: {PRESS_SEC}, ease: "power1.inOut" }}, {t0:.3f});')
    elif anim == "engrave":
        init.append(f'      gsap.set("{s} .ic-strokes path", {{ strokeDasharray: 1, strokeDashoffset: 1 }});'
                    f' gsap.set(["{s} .ic-fill", "{s} .ic-accent"], {{ clipPath: "inset(0% 100% 0% 0%)" }});')
        js.append(f'      tl.to("{s} .ic-strokes path", {{ strokeDashoffset: 0, duration: .32, ease: "power1.inOut",'
                  f' stagger: {{ amount: .13 }} }}, {t0:.3f})'
                  f'.to(["{s} .ic-fill", "{s} .ic-accent"], {{ clipPath: "inset(0% 0% 0% 0%)", duration: .35, ease: "power2.out" }}, {t0 + .42:.3f})'
                  + ("" if strokes_only else f'.to("{s} .ic-strokes", {{ opacity: 0, duration: .2 }}, {t0 + ENGRAVE_SEC - .2:.3f})') + ";")
    elif anim == "ink_bleed":
        init.append(f'      gsap.set("{s} .ic-body", {{ clipPath: "circle(0% at 50% 55%)" }});'
                    f' gsap.set("{s}-dm", {{ attr: {{ scale: {26 * k:.2f} }} }});'
                    + ("" if strokes_only else f' gsap.set("{s} .ic-strokes", {{ opacity: 0 }});'))
        js.append(f'      tl.to("{s} .ic-body", {{ clipPath: "circle(75% at 50% 55%)", duration: {INK_SEC}, ease: "power2.out" }}, {t0:.3f})'
                  f'.to("{s}-dm", {{ attr: {{ scale: 0 }}, duration: {INK_SEC}, ease: "power2.out" }}, {t0:.3f});')
    else:                                                     # stamp: el ícono entero entra como sello
        init.append(f'      gsap.set("{s}", {{ opacity: 0, scale: 1.4, rotation: -3, transformOrigin: "50% 50%" }});'
                    + ("" if strokes_only else f' gsap.set("{s} .ic-strokes", {{ opacity: 0 }});'))
        js.append(f'      tl.to("{s}", {{ opacity: 1, scale: 1, rotation: 0, duration: .18, ease: "power4.in" }}, {t0:.3f});')
    # salida única: la tinta se seca (puntos que se abren en la máscara) y se apaga
    d0 = max(t0 + .9, end - DRY_SEC)
    te = t0 + enter
    if hold and d0 - te > .2:
        # hold vivo: respiración 1 → 0.85 → 1 (medio ciclo BREATH_SEC), deriva ±DRIFT_PX y un único pulso del rojo
        span = d0 - te
        n_b = max(0, int(span / BREATH_SEC) - 1)
        n_d = max(0, int((span - DRIFT_SEC / 2) / DRIFT_SEC) - 1)
        js.append(f'      tl.to("{s} .ic-body", {{ opacity: .85, duration: {BREATH_SEC}, ease: "sine.inOut", yoyo: true,'
                  f' repeat: {n_b} }}, {te:.3f})'
                  f'.to("{s}", {{ x: {DRIFT_PX}, y: {-DRIFT_PX * .6:.1f}, duration: {DRIFT_SEC / 2:.2f}, ease: "sine.inOut" }}, {te:.3f})'
                  f'.to("{s}", {{ x: {-DRIFT_PX}, y: {DRIFT_PX * .6:.1f}, duration: {DRIFT_SEC:.2f}, ease: "sine.inOut",'
                  f' yoyo: true, repeat: {n_d} }}, {te + DRIFT_SEC / 2:.3f});')
        if has_accent:
            js.append(f'      tl.to("{s} .ic-accent", {{ opacity: .45, duration: .25, ease: "sine.inOut", yoyo: true, repeat: 1 }},'
                      f' {te + .15:.3f});')
    js.append(f'      tl.to("{s} .dry circle", {{ attr: {{ r: function (j) {{ return {k:.3f} * (2 + (j * 7919 % 6)); }} }}, duration: {DRY_SEC},'
              f' ease: "power1.in", stagger: {{ amount: .15 }} }}, {d0:.3f})'
              f'.to("{s}", {{ opacity: 0, duration: {DRY_SEC}, ease: "power1.in" }}, {d0 + .05:.3f});')
    return init, js
