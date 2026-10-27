"""
gfx_project.py — Templater determinista de la capa gráfica HyperFrames (sin LLM).

Recibe un plan RESUELTO (textos ya literales, tiempos en segundos del base_clip) +
las escenas del cap (cortes intra-cap) y escribe un proyecto HyperFrames completo en
work_dir/gfx_chXX/:

    index.html                    madre: secuencia escenas + overlays (title, callouts, recorte, contador)
    compositions/scene_NN.html    una escena por imagen: tramo del video + grade + transición de entrada
                                  + punch-in / zoom de evidencia de esa escena
    public/base.mp4               base_clip re-encodeado -g 30 (lo deja gfx_layer)
    public/cuts/freeze_NN.jpg     último frame del plano saliente (disolvencias R2/R3)
    public/fonts/Anton-Regular.ttf
    vendor/gsap.min.js            GSAP local (nunca CDN)

Plan resuelto (dict):
    {"chapter_number": 2, "title_card": {"kicker", "title"} | None,
     "callouts": [{"text", "start", "kind"}], "count_up": {"value_text", "unit", "start"} | None,
     "archive_clipping": {"kicker", "headline", "body", "scene_idx", "era_decade"} | None,
     "evidence_zoom": {"scene_idx", "box": [x, y, w, h] normalizado} | None,
     "punch_in": [t, ...]}
"""
from __future__ import annotations

import html
import json
import random
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any

from gfx_config import GFX_FONTS_DIR, GFX_TEMPLATES_DIR, GRADE_VARIANTS, gfx_rules, gsap_js


@dataclass
class GfxScene:
    """Un plano del cap dentro del base_clip."""
    idx: int                 # 0-based
    start: float             # segundos en el base_clip
    end: float
    rank: str = "R3"         # emotional_rank del plano (decide la transición de ENTRADA)
    text_in_image: str = ""  # texto que ya muestra la imagen (regla de omisión de callouts)
    quiet_side: str = "right"  # lado con menos detalle (gráficos van ahí; el sujeto queda del otro lado)
    safe: dict | None = None   # F2 §4: {"image": png, "movement": push|pan|pull|static, "risk"} → movimiento seguro HF
    dark_v: str = "top"        # F3: banda más oscura del lado tranquilo (top | mid): ahí va el bloque de ícono

    @property
    def duration(self) -> float:
        return self.end - self.start


def _tpl(name: str) -> Template:
    return Template((GFX_TEMPLATES_DIR / name).read_text(encoding="utf-8"))


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def chars_html(text: str) -> str:
    """Texto → palabras (.w, sin corte interno) de letras (.ch) para la animación cascade."""
    words = []
    for w in text.split(" "):
        words.append('<span class="w">' + "".join(f'<span class="ch">{_esc(c)}</span>' for c in w) + "</span>")
    return " ".join(words)


def _anim_in_js(sel: str, anim: str, t: float) -> tuple[list[str], list[str]]:
    """(init, timeline) de entrada de un texto. Sin letter-spacing animado (lint)."""
    r = gfx_rules
    if anim == "cascade":
        return ([f'      gsap.set("{sel} .ch", {{ opacity: 0, y: {r.cascade_rise_px} }});'],
                [f'      tl.to("{sel} .ch", {{ opacity: 1, y: 0, duration: .45, ease: "power3.out", stagger: {r.cascade_stagger} }}, {t:.3f});'])
    if anim == "stamp":
        return ([f'      gsap.set("{sel}", {{ opacity: 0, scale: {r.stamp_from_scale}, rotation: {r.stamp_rotation}, transformOrigin: "30% 50%" }});'],
                [f'      tl.to("{sel}", {{ opacity: 1, scale: 1, duration: {r.stamp_sec}, ease: "power4.in" }}, {t:.3f});'])
    if anim == "number_pop":
        return ([f'      gsap.set("{sel}", {{ opacity: 0, scale: {r.pop_from_scale}, transformOrigin: "50% 60%" }});'],
                [f'      tl.to("{sel}", {{ opacity: 1, duration: .12, ease: "none" }}, {t:.3f})'
                 f'.to("{sel}", {{ scale: 1, duration: {r.pop_sec}, ease: "power2.out" }}, {t:.3f});'])
    return ([f'      gsap.set("{sel}", {{ yPercent: 105 }});'],                         # slide (F1)
            [f'      tl.to("{sel}", {{ yPercent: 0, duration: .38, ease: "power3.out" }}, {t:.3f});'])


# ═══════════════════════════════════════════════════════════════
#  F2b §2: capas de mood (CSS, 1–3 s, intensidad baja; nunca toca píxeles del video)
# ═══════════════════════════════════════════════════════════════

_ABS = "position:absolute;pointer-events:none;"


def mood_layer(i: int, layer: str, t0: float, d: float, width: int, height: int) -> tuple[str, list[str], list[str]]:
    """(html, init, timeline) de la capa de mood `layer` (veneno | agua | muerte | oscuridad | minima) en [t0, t0 + d)."""
    rid = f"md{i}"
    kids: list[str] = []
    init: list[str] = []
    js: list[str] = []
    out_at = t0 + d - 0.5

    def fade(sel: str, peak: float, t_in: float, d_in: float, t_out: float = out_at, d_out: float = 0.5) -> None:
        init.append(f'      gsap.set("{sel}", {{ opacity: 0 }});')
        js.append(f'      tl.to("{sel}", {{ opacity: {peak}, duration: {d_in:.3f}, ease: "sine.out" }}, {t_in:.3f})'
                  f'.to("{sel}", {{ opacity: 0, duration: {d_out:.3f}, ease: "sine.in" }}, {t_out:.3f});')

    if layer == "veneno":
        # viraje verde-amarillo 1 s (multiply: pesa en sombras y medios) + partículas oscuras + viñeta −10 %
        kids.append(f'<div id="{rid}-tint" style="{_ABS}inset:0;background:#c9d36a;mix-blend-mode:multiply"></div>')
        fade(f"#{rid}-tint", 0.38, t0, 0.25, t0 + 1.0, 0.5)
        rnd = random.Random(1441 + i)
        for k in range(14):
            r = rnd.randint(4, 9)
            x, y = rnd.uniform(0.05, 0.95) * width, rnd.uniform(0.15, 0.9) * height
            kids.append(f'<div id="{rid}-p{k}" class="{rid}-pt" style="{_ABS}left:{x:.0f}px;top:{y:.0f}px;width:{2 * r}px;'
                        f'height:{2 * r}px;border-radius:50%;background:rgba(18,22,8,.6);filter:blur(1px)"></div>')
            js.append(f'      tl.to("#{rid}-p{k}", {{ x: {rnd.uniform(-25, 25):.0f}, y: {rnd.uniform(-60, -20):.0f}, '
                      f'duration: {d:.3f}, ease: "none" }}, {t0:.3f});')
        fade(f".{rid}-pt", 1.0, t0, 0.4)
        kids.append(f'<div id="{rid}-vig" style="{_ABS}inset:0;background:radial-gradient(ellipse 80% 80% at 50% 45%,'
                    f'rgba(0,0,0,0) 55%,rgba(0,0,0,.9) 100%)"></div>')
        fade(f"#{rid}-vig", 0.35, t0, 0.6)
    elif layer == "agua":
        # sombra oscura que sube desde abajo hasta 1/3 en 1 s, se mantiene y baja al salir + bordes un poco más
        # oscuros. Sin cáusticas: el repeating-radial-gradient se veía como un mosquitero sobre la foto (Omar, F3).
        kids.append(f'<div id="{rid}-vig" style="{_ABS}inset:0;background:radial-gradient(ellipse 85% 85% at 50% 45%,'
                    f'rgba(0,0,0,0) 60%,rgba(2,8,16,.85) 100%)"></div>')
        fade(f"#{rid}-vig", 0.35, t0, 0.8)
        kids.append(f'<div id="{rid}-rise" style="{_ABS}left:0;right:0;bottom:0;height:34%;'
                    'background:linear-gradient(to top,rgba(2,10,20,.78),rgba(2,10,20,0))"></div>')
        init.append(f'      gsap.set("#{rid}-rise", {{ yPercent: 100 }});')
        js.append(f'      tl.to("#{rid}-rise", {{ yPercent: 0, duration: 1.0, ease: "power2.out" }}, {t0:.3f})'
                  f'.to("#{rid}-rise", {{ yPercent: 100, duration: .5, ease: "power2.in" }}, {out_at:.3f});')
    elif layer == "muerte":
        # desaturación 80 % en 1.5 s (gris en blend saturation) + letterbox 2 s + viñeta cerrada (push-in: en la escena)
        kids.append(f'<div id="{rid}-ds" style="{_ABS}inset:0;background:#808080;mix-blend-mode:saturation"></div>')
        fade(f"#{rid}-ds", 0.8, t0, 1.5)
        bar = round(height * 0.10)
        for k, pos in enumerate(("top:0", "bottom:0")):
            kids.append(f'<div id="{rid}-lb{k}" style="{_ABS}left:0;right:0;{pos};height:{bar}px;background:#000;'
                        f'transform-origin:50% {"0%" if k == 0 else "100%"}"></div>')
            init.append(f'      gsap.set("#{rid}-lb{k}", {{ scaleY: 0 }});')
            js.append(f'      tl.to("#{rid}-lb{k}", {{ scaleY: 1, duration: .35, ease: "power2.out" }}, {t0:.3f})'
                      f'.to("#{rid}-lb{k}", {{ scaleY: 0, duration: .35, ease: "power2.in" }}, {t0 + 2.0 - .35:.3f});')
        kids.append(f'<div id="{rid}-vig" style="{_ABS}inset:0;background:radial-gradient(ellipse 75% 75% at 50% 45%,'
                    f'rgba(0,0,0,0) 45%,rgba(0,0,0,.9) 100%)"></div>')
        fade(f"#{rid}-vig", 0.5, t0, 0.8)
    elif layer == "minima":
        # F4c R5: capa mínima de las categorías de reserva hasta que el lab les dé forma: desaturación leve + viñeta
        kids.append(f'<div id="{rid}-ds" style="{_ABS}inset:0;background:#808080;mix-blend-mode:saturation"></div>')
        fade(f"#{rid}-ds", 0.3, t0, 0.8)
        kids.append(f'<div id="{rid}-vig" style="{_ABS}inset:0;background:radial-gradient(ellipse 80% 80% at 50% 45%,'
                    f'rgba(0,0,0,0) 50%,rgba(0,0,0,.9) 100%)"></div>')
        fade(f"#{rid}-vig", 0.45, t0, 0.6)
    elif layer == "oscuridad":
        # oscuridad desde los bordes + haz de linterna que deriva ±2.5° (+ 2 parpadeos si mood_dark_flicker)
        kids.append(f'<div id="{rid}-edge" style="{_ABS}inset:0;background:radial-gradient(ellipse 62% 58% at 50% 45%,'
                    f'rgba(0,0,0,0) 35%,rgba(0,0,0,.92) 100%)"></div>')
        fade(f"#{rid}-edge", 0.85, t0, 0.8)
        kids.append(f'<div id="{rid}-beam" style="{_ABS}left:-50%;top:-50%;width:200%;height:200%;transform-origin:50% 75%;'
                    'background:radial-gradient(ellipse 18% 26% at 50% 46%,rgba(0,0,0,0) 0,rgba(0,0,0,0) 45%,rgba(0,0,0,.5) 100%)"></div>')
        fade(f"#{rid}-beam", 1.0, t0, 0.6)
        init.append(f'      gsap.set("#{rid}-beam", {{ rotation: -2.5 }});')
        js.append(f'      tl.to("#{rid}-beam", {{ rotation: 2.5, duration: {d:.3f}, ease: "sine.inOut" }}, {t0:.3f});')
        if gfx_rules.mood_dark_flicker:                     # parpadeo de luz 2 veces (token del perfil)
            kids.append(f'<div id="{rid}-fl" style="{_ABS}inset:0;background:#000"></div>')
            init.append(f'      gsap.set("#{rid}-fl", {{ opacity: 0 }});')
        for tf, pk in ((t0 + 0.9, 0.5), (t0 + 1.25, 0.45)) if gfx_rules.mood_dark_flicker else ():
            js.append(f'      tl.set("#{rid}-fl", {{ opacity: {pk} }}, {tf:.3f}).set("#{rid}-fl", {{ opacity: 0 }}, {tf + 0.07:.3f});')
    html_ = (f'      <div id="{rid}" class="clip" data-start="{t0:.3f}" data-duration="{d:.3f}" '
             f'style="{_ABS}inset:0;overflow:hidden;z-index:2">' + "".join(kids) + "</div>")
    return html_, init, js


# ═══════════════════════════════════════════════════════════════
#  F3/F5f: cita, ficha y reloj de esquina
# ═══════════════════════════════════════════════════════════════


def quote_card_html(qc: dict[str, Any], width: int, height: int, duration: float) -> tuple[str, list[str], list[str]]:
    """F5f: cita LITERAL entre comillas tipográficas + «— autor» en el acento, centrada sobre la foto oscurecida
    (gfx_rules.quote_dim). Entra con fundido y sube 30 px; sale con fundido."""
    q0 = min(float(qc["start"]), max(0.0, duration - float(qc["duration"])))
    qd = float(qc["duration"])
    px = round(height * 0.05)
    html_ = (f'      <div id="qc-dim" class="clip" data-start="{q0:.3f}" data-duration="{qd:.3f}" '
             f'style="position:absolute;inset:0;z-index:28;background:#000"></div>\n'
             f'      <div id="qc" class="clip" data-start="{q0:.3f}" data-duration="{qd:.3f}" '
             f'style="position:absolute;inset:0;z-index:29;display:flex;align-items:center;justify-content:center">'
             f'<div id="qc-box" style="max-width:{round(width * 0.66)}px;text-align:center">'
             f'<div id="qc-text" style="font:700 {px}px/1.28 &quot;{gfx_rules.clipping_font}&quot;,serif;color:#f4f1ea;'
             f'font-variant-ligatures:none;font-feature-settings:&quot;liga&quot; 0">&ldquo;{_esc(qc["text"])}&rdquo;</div>'
             f'<div id="qc-rule" style="width:{round(px * 2.4)}px;height:5px;margin:{round(px * .55)}px auto '
             f'{round(px * .4)}px;background:{gfx_rules.accent_hex}"></div>'
             f'<div id="qc-author" style="font:400 {round(px * .62)}px/1 &quot;{gfx_rules.figure_font}&quot;,sans-serif;'
             f'letter-spacing:.06em;text-transform:uppercase;color:{gfx_rules.accent_hex}">&mdash; {_esc(qc["author"])}</div>'
             f'</div></div>')
    init = ['      gsap.set("#qc-dim", { opacity: 0 }); gsap.set("#qc-box", { opacity: 0, y: 30 }); '
            'gsap.set("#qc-rule", { scaleX: 0 });']
    js = [f'      tl.to("#qc-dim", {{ opacity: {gfx_rules.quote_dim}, duration: .35 }}, {q0:.3f})'
          f'.to("#qc-box", {{ opacity: 1, y: 0, duration: .5, ease: "power3.out" }}, {q0 + .15:.3f})'
          f'.to("#qc-rule", {{ scaleX: 1, duration: .5, ease: "power3.inOut" }}, {q0 + .35:.3f})'
          f'.to(["#qc-box", "#qc-dim"], {{ opacity: 0, duration: .35, ease: "power1.in" }}, {q0 + qd - .35:.3f});']
    return html_, init, js


def forma(eje: str) -> str | None:
    """F31: la variante de forma que pide `--forma-variante` para un eje (V = entrada/salida de ficha y recorte, S =
    sello, R = reloj), o None = como hoy. Sin el flag nada cambia (ningún default se toca)."""
    for x in str(gfx_rules.forma_variante or "").split(","):
        x = x.strip().upper()
        if x[:1] == eje:
            return x
    return None


def _forma_v_js(sel: str, st: float, dur: float, v: str) -> tuple[list[str], list[str]]:
    """F31 V2/V3: el bloque entra y sale entero. V2 = fundido simple, con la duración del fundido del title card
    (title_fade_out) en los dos sentidos; V3 = el mismo fundido + desplazamiento vertical del alto de la raya del title
    card (#tc-line), con las curvas del title card (power4.out al entrar, power2.in al salir)."""
    fo = gfx_rules.title_fade_out
    dy = tc_metrics()["line_h"] if v == "V3" else 0
    e_in, e_out = ("power4.out", "power2.in") if dy else ("none", "none")
    return ([f'      gsap.set("{sel}", {{ opacity: 0, y: {dy} }});'],
            [f'      tl.to("{sel}", {{ opacity: 1, y: 0, duration: {fo}, ease: "{e_in}" }}, {st:.3f})'
             f'.to("{sel}", {{ opacity: 0, y: {-dy}, duration: {fo}, ease: "{e_out}" }}, {st + dur - fo:.3f});'])


def ficha_html(fid: str, c: dict[str, Any], st: float, dur: float, width: int) -> tuple[str, list[str], list[str]]:
    """F29c §A.5: la ficha del rotulista con el componente del title card: kicker = etiqueta, título = dato. Misma
    posición, raya, wipe de entrada y fundido de salida (gfx_rules.title_fade_out); sin #tc-dim (no oscurece la imagen).
    F32 §B.8: un escalón más chica que el title card: el dato al tamaño de la pregunta de cierre (question_font_px) y la
    etiqueta (tc_kicker_px) sobre la placa de `.co-text.stamp` (clase `.tc-box.ficha` del CSS); la raya va debajo de la
    última línea del dato (misma cuenta que la del CSS, con el tamaño del dato)."""
    m = tc_metrics()
    lines = max(1, ficha_medida(c.get("kicker", ""), c["text"], width)["title"])
    line_style = f' style="top:{round(m["title_top"] + gfx_rules.question_font_px * 1.05 * lines + 20)}px"'
    html_ = _tpl("title_card.html.tmpl").substitute(
        dim_html="", tid=fid, start=f"{st:.3f}", duration=f"{dur:.3f}", line_style=line_style, box_class=" ficha",
        kicker=_esc(str(c.get("kicker", "")).upper()), title=_esc(c["text"]))
    fo = gfx_rules.title_fade_out
    v = forma("V")
    if v in ("V2", "V3"):                                       # F31: la ficha entra y sale entera
        f_init, f_js = _forma_v_js(f"#{fid}", st, dur, v)
        return html_, f_init, f_js
    init = [f'      gsap.set("#{fid}-title span", {{ yPercent: 110 }}); gsap.set("#{fid}-line", {{ scaleX: 0 }});'
            f' gsap.set("#{fid}-kicker", {{ opacity: 0 }});']
    js = [f'      tl.to("#{fid}-kicker", {{ opacity: 1, duration: .3 }}, {st + .05:.3f})'
          f'.to("#{fid}-title span", {{ yPercent: 0, duration: .55, ease: "power4.out" }}, {st + .1:.3f})'
          f'.to("#{fid}-line", {{ scaleX: 1, duration: .7, ease: "power3.inOut" }}, {st + .25:.3f})'
          f'.to("#{fid}", {{ opacity: 0, duration: {fo}, ease: "power2.in" }}, {st + dur - fo:.3f});']
    return html_, init, js


def time_ticker_html(tk: dict[str, Any], duration: float) -> tuple[str, list[str], list[str]]:
    """Reloj de esquina (arriba a la izquierda, Anton S): "29 AGO · 23:40". Avanza entre las dos horas de los datos
    si las hay; si no, la fecha quieta."""
    st, d = tk["start"], min(tk["duration"], max(0.5, duration - tk["start"]))
    tk_px = tc_metrics()["kicker_px"] if forma("R") == "R2" else 64     # F31 R2: al tamaño del kicker del title card
    head = f'{tk["day"]} {tk["month"]}'
    html_ = (f'      <div id="tk" class="clip" data-start="{st:.3f}" data-duration="{d:.3f}" '
             f'style="position:absolute;{"right" if tk.get("side") == "right" else "left"}:150px;top:64px;z-index:23;color:#f2efe6;font:400 {tk_px}px/1 &quot;{gfx_rules.figure_font}&quot;,'
             f'sans-serif;letter-spacing:.08em;text-shadow:{gfx_rules.callout_shadow};font-variant-numeric:tabular-nums">'
             f'<span style="display:inline-block;overflow:hidden;vertical-align:bottom"><span id="tk-d" style="display:inline-block">'
             f'{_esc(head)}</span></span> <span style="color:{gfx_rules.accent_hex}">·</span> <span id="tk-t">{_esc(tk.get("tail", ""))}</span></div>')
    init = ['      gsap.set("#tk", { opacity: 0 });']
    js = [f'      tl.to("#tk", {{ opacity: 1, duration: .4 }}, {st:.3f}).to("#tk", {{ opacity: 0, duration: .4 }}, {st + d - .4:.3f});']
    # F5f: cambio de fecha = la fecha vieja sube y sale, la nueva entra desde abajo con un destello en el acento
    for ch in tk.get("changes") or []:
        t = float(ch["t"])
        if not st + .4 < t < st + d - .6:
            continue
        lab = json.dumps(str(ch["day"]) + " " + str(ch["month"]), ensure_ascii=False)
        tail = json.dumps(str(ch.get("tail", "")), ensure_ascii=False)
        js.append(f'      tl.to("#tk-d", {{ yPercent: -110, duration: .22, ease: "power2.in" }}, {t:.3f})'
                  f'.set("#tk-d", {{ textContent: {lab}, '
                  f'yPercent: 110, color: "{gfx_rules.accent_hex}" }}, {t + .22:.3f})'
                  f'.set("#tk-t", {{ textContent: {tail} }}, {t + .22:.3f})'
                  f'.to("#tk-d", {{ yPercent: 0, duration: .32, ease: "power3.out" }}, {t + .22:.3f})'
                  f'.to("#tk-d", {{ color: "#f2efe6", duration: .6 }}, {t + .9:.3f});')
    if tk.get("advance") and len(tk.get("times") or []) >= 2:
        (h0, m0), (h1, m1) = [map(int, x.split(":")) for x in tk["times"][:2]]
        a, b = h0 * 60 + m0, h1 * 60 + m1
        js.append(f'      var tkObj = {{ m: {a} }}; tl.to(tkObj, {{ m: {b}, duration: {d - .8:.3f}, ease: "none", onUpdate: function () {{'
                  ' var m = Math.round(tkObj.m) % 1440, h = Math.floor(m / 60), mm = m % 60;'
                  ' document.getElementById("tk-t").textContent = (h < 10 ? "0" : "") + h + ":" + (mm < 10 ? "0" : "") + mm; } },'
                  f' {st + .4:.3f});')
    return html_, init, js


def load_grade_preset() -> dict[str, Any]:
    """Preset de grade versionado (D4)."""
    return json.loads((GFX_TEMPLATES_DIR / "gfx_grade.json").read_text(encoding="utf-8"))


# ═══════════════════════════════════════════════════════════════
#  Escenas
# ═══════════════════════════════════════════════════════════════

def scene_at(scenes: list[GfxScene], t: float) -> GfxScene:
    """Escena que contiene el instante t (la última si t cae al final)."""
    for s in scenes:
        if s.start <= t < s.end:
            return s
    return scenes[-1]


_FREEZE_MEMO: set[tuple[str, int, int, str, str]] = set()   # F3: freezes ya extraídos EN ESTE proceso


def _extract_freeze(base: Path, t: float, out: Path) -> bool:
    """Último frame del plano saliente. Llamar con t = corte − 1.5 frames: `-ss` descarta los frames con
    pts < t, así que pedir "corte − 1 frame" redondeado a 4 decimales caía DESPUÉS del último frame
    saliente y devolvía el ENTRANTE (bug F2 §0b.4: disolvencias R3 = corte duro).

    F3 (lab): memo en proceso — si este mismo proceso ya extrajo ese frame (mismo base, mtime, tamaño, t y
    salida) y el archivo sigue ahí, no se vuelve a llamar a ffmpeg. fase2b llama una vez por cap → sin cambio."""
    out.parent.mkdir(parents=True, exist_ok=True)
    st = Path(base).stat()
    key = (str(Path(base).resolve()), st.st_mtime_ns, st.st_size, f"{max(0.0, t):.4f}", str(out.resolve()))
    if key in _FREEZE_MEMO and out.exists():
        return True
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, t):.4f}", "-i", str(base),
                        "-frames:v", "1", "-q:v", "2", str(out)],
                       capture_output=True, timeout=120)
    ok = r.returncode == 0 and out.exists()
    if ok:
        _FREEZE_MEMO.add(key)
    return ok


def transitions_of(plan: dict[str, Any], scenes: list[GfxScene]) -> dict[int, dict[str, Any]]:
    """Transiciones del cap: las que fijó la identidad (F4 §2.3, plan["transitions"]) o las de plan_transitions."""
    tr = plan.get("transitions")
    if tr:
        return {int(k): v for k, v in tr.items() if 0 < int(k) < len(scenes)}
    return plan_transitions(scenes)


def plan_transitions(scenes: list[GfxScene]) -> dict[int, dict[str, Any]]:
    """shot_transition de ENTRADA por escena (determinista desde emotional_rank del plano entrante).

    R1 → flash, salvo que ya se hayan usado gfx_rules.flash_max_per_cap flashes o el anterior
    esté a < flash_min_gap_sec: entonces corte duro + punch (cut_punch). R2/R3 → disolvencia.
    """
    out: dict[int, dict[str, Any]] = {}
    flashes: list[float] = []
    for s in scenes[1:]:
        frames = gfx_rules.transition_frames.get(s.rank, gfx_rules.transition_frames["R3"])
        if s.rank == "R1":
            if len(flashes) < gfx_rules.flash_max_per_cap and all(
                    s.start - f >= gfx_rules.flash_min_gap_sec for f in flashes):
                flashes.append(s.start)
                out[s.idx] = {"kind": "flash", "frames": frames, "rank": "R1"}
            else:
                out[s.idx] = {"kind": "cut_punch", "frames": 0, "rank": "R1"}
        elif s.rank == "R3" and gfx_rules.r3_style == "dip":
            out[s.idx] = {"kind": "dip", "frames": gfx_rules.dip_frames, "rank": "R3"}
        else:
            out[s.idx] = {"kind": "dissolve", "frames": frames, "rank": s.rank}
    return out


def _freeze_img(prev: GfxScene | None, s: GfxScene, tag: str, project: Path, base: Path,
                width: int, fps: int) -> tuple[str, str] | None:
    """(src, style) del freeze del plano SALIENTE. Si el saliente tuvo movimiento seguro (F2 §4), el freeze
    es SU imagen fija en el estado final de la animación (no el clip DepthFlow que quedó tapado)."""
    if prev is not None and prev.safe and Path(prev.safe["image"]).exists():
        src = Path(prev.safe["image"])
        dst = project / "public" / "cuts" / f"freeze_{tag}{src.suffix}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if prev.safe.get("movement") == "pan":
            style = f"transform: translateX({gfx_rules.safe_pan_frac * width / 2:.1f}px) scale(1.04)"
        elif prev.safe.get("movement") in ("pull", "static"):     # F3: terminan en escala 1
            style = ""
        else:
            style = f"transform: scale({gfx_rules.safe_push_scale})"
        return f"public/cuts/{dst.name}", style
    freeze = project / "public" / "cuts" / f"freeze_{tag}.jpg"
    if _extract_freeze(base, s.start - 1.5 / fps, freeze):
        return f"public/cuts/{freeze.name}", ""
    return None


def _scene_html(s: GfxScene, n: int, plan: dict[str, Any], project: Path,
                base: Path, width: int, height: int, fps: int,
                transitions: dict[int, dict[str, Any]] | None = None, prev: GfxScene | None = None) -> str:
    """Una sub-composición por imagen."""
    inner, outer, init, js = [], [], [], []
    tag = f"{n:02d}"

    # ── shot_transition de ENTRADA (plan por cap: plan_transitions)
    tr = (transitions or {}).get(s.idx)
    if s.idx > 0 and tr:
        frames = tr["frames"]
        d = frames / fps
        if tr["kind"] == "cut_punch":
            js.append(f'        tl.fromTo("#vw{tag}", {{ scale: {gfx_rules.r1_cut_punch_scale} }}, {{ scale: 1, duration: .35, ease: "power2.out", immediateRender: false }}, 0);')
        elif tr["kind"] == "zoom_punch":
            # F30b §A: el entrante se aleja 1.4 → 1 en la mitad después del corte (HyperFrames no escala <video>: va
            # el primer cuadro fijo encima, como el freeze de la disolvencia)
            from script_engine.gfx_style import ZOOM_PUNCH_SCALE
            h = (frames // 2) / fps
            fi = project / "public" / "cuts" / f"zpin_{tag}.jpg"
            if _extract_freeze(base, s.start + 0.5 / fps, fi):
                outer.append(f'    <img id="zpi{tag}" class="media clip" src="public/cuts/{fi.name}" data-start="0" '
                             f'data-duration="{h:.3f}" alt="" />')
                init.append(f'        gsap.set("#zpi{tag}", {{ scale: {ZOOM_PUNCH_SCALE} }});')
                js.append(f'        tl.to("#zpi{tag}", {{ scale: 1, duration: {h:.3f}, ease: "power2.out" }}, 0);')
        elif tr["kind"] == "flash":
            outer.append(f'    <div id="fl{tag}" class="flash clip" data-start="0" data-duration="{d:.3f}"></div>')
            init.append(f'        gsap.set("#fl{tag}", {{ opacity: 0 }});')
            js.append(f'        tl.to("#fl{tag}", {{ opacity: {gfx_rules.flash_peak}, duration: {d / 3:.3f}, ease: "none" }}, 0)'
                      f'.to("#fl{tag}", {{ opacity: 0, duration: {2 * d / 3:.3f}, ease: "power1.in" }}, {d / 3:.3f});')
        elif tr["kind"] == "dip":
            # dip-to-black: el saliente (freeze) baja a negro y el entrante sube desde negro
            fz = _freeze_img(prev, s, tag, project, base, width, fps)
            if fz:
                outer.append(f'    <img id="fz{tag}" class="media clip" src="{fz[0]}" data-start="0" '
                             f'data-duration="{d / 2:.3f}" alt="" style="{fz[1]}" />')
            outer.append(f'    <div id="dp{tag}" class="clip" data-start="0" data-duration="{d:.3f}" '
                         f'style="position:absolute;inset:0;background:#000"></div>')
            init.append(f'        gsap.set("#dp{tag}", {{ opacity: 0 }});')
            js.append(f'        tl.to("#dp{tag}", {{ opacity: 1, duration: {d / 2:.3f}, ease: "none" }}, 0)'
                      f'.to("#dp{tag}", {{ opacity: 0, duration: {d / 2:.3f}, ease: "none" }}, {d / 2:.3f});')
        else:
            # disolvencia: el freeze es el ÚLTIMO frame del plano saliente (corte anclado al cambio real
            # de imagen en gfx_layer.snap_cuts; F2 §0b.4: antes se tomaba 45 ms tarde = imagen entrante)
            fz = _freeze_img(prev, s, tag, project, base, width, fps)
            if fz:
                outer.append(f'    <img id="fz{tag}" class="media clip" src="{fz[0]}" data-start="0" '
                             f'data-duration="{d:.3f}" alt="" style="{fz[1]}" />')
                init.append(f'        gsap.set("#fz{tag}", {{ opacity: 1 }});')
                js.append(f'        tl.to("#fz{tag}", {{ opacity: 0, duration: {d:.3f}, ease: "sine.inOut" }}, 0);')

    # ── F30b §A: zoom_punch de SALIDA (la escena siguiente entra con zoom_punch): el último cuadro se acerca 1 → 1.4
    nxt = (transitions or {}).get(s.idx + 1)
    if nxt and nxt["kind"] == "zoom_punch":
        from script_engine.gfx_style import ZOOM_PUNCH_SCALE
        h = (nxt["frames"] // 2) / fps
        fo = project / "public" / "cuts" / f"zpout_{tag}.jpg"
        if _extract_freeze(base, s.end - 1.5 / fps, fo):
            outer.append(f'    <img id="zpo{tag}" class="media clip" src="public/cuts/{fo.name}" '
                         f'data-start="{max(0.0, s.duration - h):.3f}" data-duration="{h:.3f}" alt="" />')
            js.append(f'        tl.fromTo("#zpo{tag}", {{ scale: 1 }}, {{ scale: {ZOOM_PUNCH_SCALE}, duration: {h:.3f}, '
                      f'ease: "power2.in", immediateRender: false }}, {max(0.0, s.duration - h):.3f});')

    # ── F2 §4: movimiento seguro (riesgo de deformación alto): la imagen FIJA tapa el clip DepthFlow
    # y se anima con un push-in o un paneo leve (nunca se deforma: solo escala/traslada)
    if s.safe and Path(s.safe["image"]).exists():
        dst = project / "public" / "safe" / f"safe_{tag}{Path(s.safe['image']).suffix}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s.safe["image"], dst)
        inner.append(f'      <img id="sf{tag}" class="media clip" src="public/safe/{dst.name}" data-start="0" '
                     f'data-duration="{s.duration:.3f}" alt="" />')
        if s.safe.get("movement") == "pan":
            dx = gfx_rules.safe_pan_frac * width
            init.append(f'        gsap.set("#sf{tag}", {{ scale: 1.04, x: {-dx / 2:.1f} }});')
            js.append(f'        tl.to("#sf{tag}", {{ x: {dx / 2:.1f}, duration: {s.duration:.3f}, ease: "none" }}, 0);')
        elif s.safe.get("movement") == "pull":     # F3 lab: alejamiento (inverso del push-in)
            init.append(f'        gsap.set("#sf{tag}", {{ scale: {gfx_rules.safe_push_scale}, transformOrigin: "50% 50%" }});')
            js.append(f'        tl.to("#sf{tag}", {{ scale: 1, duration: {s.duration:.3f}, ease: "sine.inOut" }}, 0);')
        elif s.safe.get("movement") == "static":   # F3 lab: foto quieta (sin tween)
            init.append(f'        gsap.set("#sf{tag}", {{ scale: 1, transformOrigin: "50% 50%" }});')
        else:
            # F4b §3: foto con rostro/manos → el acercar apunta al detalle (origen = centro de la caja de visión)
            org = s.safe.get("origin")
            origin = f"{org[0] * 100:.1f}% {org[1] * 100:.1f}%" if org else "50% 50%"
            init.append(f'        gsap.set("#sf{tag}", {{ scale: 1, transformOrigin: "{origin}" }});')
            js.append(f'        tl.to("#sf{tag}", {{ scale: {gfx_rules.safe_push_scale}, duration: {s.duration:.3f}, ease: "sine.inOut" }}, 0);')

    # ── punch_in en la CAPA DE VIDEO (los subs se queman después, no escalan)
    for t in plan.get("punch_in", []):
        if s.start <= t < s.end:
            lt = t - s.start
            js.append(f'        tl.to("#vw{tag}", {{ scale: {gfx_rules.punch_scale}, duration: {gfx_rules.punch_in_sec}, ease: "power2.out" }}, {lt:.3f});')
            if not gfx_rules.punch_hold:   # F2 §0b.3: por default se sostiene hasta el corte
                js.append(f'        tl.to("#vw{tag}", {{ scale: 1, duration: {gfx_rules.punch_out_sec}, ease: "power2.inOut" }}, {lt + gfx_rules.punch_in_sec:.3f});')

    # ── F2b §2: mood "muerte" → push-in lentísimo de la capa de video (solo si la escena no tiene punch/zoom)
    has_punch = any(s.start <= t < s.end for t in plan.get("punch_in", []))
    for e in plan.get("emphasis", []) or []:
        if e.get("layer") == "muerte" and s.start <= e["start"] < s.end and not has_punch:
            js.append(f'        tl.to("#vw{tag}", {{ scale: 1.015, duration: {e["duration"]:.3f}, ease: "none" }}, {e["start"] - s.start:.3f});')
            break

    return _tpl("scene.html.tmpl").substitute(
        n=tag, duration=f"{s.duration:.3f}", width=width, height=height,
        media_start=f"{s.start:.3f}",
        inner_html="\n".join(inner), outer_html="\n".join(outer),
        init_js="\n".join(init), timeline_js="\n".join(js),
    )


# ═══════════════════════════════════════════════════════════════
#  Cues: eventos del cap (hoja de cues, overlay --gfx-debug, página de revisión)
# ═══════════════════════════════════════════════════════════════

def archive_list(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Recortes del plan resuelto (F2: lista `archive_clippings`; compat F1 `archive_clipping`)."""
    if plan.get("archive_clippings"):
        return list(plan["archive_clippings"])
    one = plan.get("archive_clipping")
    return [one] if one and "start" in one else []


def cue_events(plan: dict[str, Any], scenes: list[GfxScene], fps: int) -> list[dict[str, Any]]:
    """Eventos visibles del cap ordenados por tiempo: {t, dur, block, text, scene, rank}.

    Usa las MISMAS reglas que el templater (duraciones de gfx_rules, plan_transitions), así la
    hoja de cues y el overlay coinciden con lo renderizado.
    """
    ev: list[dict[str, Any]] = []

    def add(t: float, dur: float, block: str, text: str = "", rank: str = "") -> None:
        ev.append({"t": round(t, 3), "dur": round(dur, 3), "block": block, "text": text,
                   "scene": scene_at(scenes, t).idx + 1, "rank": rank})

    if plan.get("title_card"):
        add(0.0, gfx_rules.title_dur, "title_card", f"{plan['title_card']['kicker']} · {plan['title_card']['title']}")
    if plan.get("chapter_question"):
        add(plan["chapter_question"]["start"], plan["chapter_question"]["duration"], "chapter_question",
            plan["chapter_question"]["text"])
    for c in plan.get("callouts", []):                          # F29c §A.5: todo texto es ficha (F36 §D)
        add(c["start"], c.get("duration", gfx_rules.callout_dur), "ficha", f"{c.get('kicker', '')} · {c['text']}")
    for ar in archive_list(plan):
        add(ar["start"], ar["duration"], "archive_clipping", ar["headline"])
    for t in plan.get("punch_in", []):
        add(t, gfx_rules.punch_in_sec + gfx_rules.punch_out_sec, "punch_in")
    for e in plan.get("emphasis", []) or []:                    # F2b §2
        add(e["start"], e["duration"], f"keyword_emphasis:{e['category']}", e["word"])
    if plan.get("quote_card"):                                  # F5f: cita literal + autor
        qc = plan["quote_card"]
        add(qc["start"], qc["duration"], "quote_card", f"«{qc['text']}» — {qc['author']}")
    if plan.get("time_ticker"):
        tk = plan["time_ticker"]
        add(tk["start"], tk["duration"], "time_ticker", f"{tk['day']} {tk['month']} · {tk.get('tail', '')}".strip())
        for ch in tk.get("changes") or []:                      # F5f: el reloj cambia de fecha
            add(ch["t"], 0.54, "time_ticker_change", f"→ {ch['day']} {ch['month']} · {ch.get('tail', '')}".strip())
    if plan.get("black_hold"):
        add(plan["black_hold"]["start"], plan["black_hold"]["duration"], "black_hold", "corte a negro")
    for idx, tr in transitions_of(plan, scenes).items():
        sc = scenes[idx]
        label = (f"{tr['frames']} f" if tr["frames"] else
                 f"corte ({tr['why']})" if tr.get("why") and tr["kind"] == "cut" else    # F4: motivo de la identidad
                 "corte seco (post-zoom)" if tr["kind"] == "cut" else "corte + punch")
        add(sc.start, tr["frames"] / fps, f"shot_transition:{tr['kind']}", label,
            tr["rank"])
    return sorted(ev, key=lambda e: (e["t"], e["block"]))


def _debug_overlay(events: list[dict[str, Any]], duration: float, fps: int) -> tuple[str, list[str], list[str]]:
    """Overlay --gfx-debug: timecode mm:ss.ff + bloque activo + escena + rank. SOLO con debug=True."""
    html_ = ('      <div id="dbg" class="clip" data-start="0" data-duration="' + f"{duration:.3f}" + '" '
             'style="position:absolute;left:24px;top:24px;z-index:999;padding:10px 16px;background:rgba(0,0,0,.6);'
             'color:#fff;font:400 28px/1.35 \'Courier New\',monospace;white-space:pre">'
             '<span id="dbg-tc">00:00.00</span>  <span id="dbg-sc"></span>\n<span id="dbg-ev"></span></div>')
    init = ['      var dbgObj = { t: 0 };']
    js = [f'      tl.to(dbgObj, {{ t: {duration:.3f}, duration: {duration:.3f}, ease: "none", onUpdate: function () {{'
          ' var t = dbgObj.t, m = Math.floor(t / 60), s = Math.floor(t % 60), f = Math.floor((t % 1) * ' + str(fps) + ');'
          ' document.getElementById("dbg-tc").textContent = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s + "." + (f < 10 ? "0" : "") + f; } }, 0);']
    marks: dict[float, list[str]] = {}
    for e in events:
        label = e["block"] + (f" {e['rank']}" if e["rank"] else "") + (f" · {e['text'][:38]}" if e["text"] else "")
        marks.setdefault(e["t"], []).append(label)
        marks.setdefault(round(e["t"] + max(e["dur"], 1 / fps), 3), [])
    # escena actual en cada corte; texto del evento activo hasta que termina
    active: list[tuple[float, float, str]] = [(e["t"], e["t"] + max(e["dur"], 1 / fps), marks[e["t"]][0]) for e in events]
    for t in sorted(marks):
        now = [lab for a, b, lab in active if a <= t < b]
        js.append(f'      tl.set("#dbg-ev", {{ textContent: {json.dumps(" | ".join(dict.fromkeys(now)) or "—", ensure_ascii=False)} }}, {t:.3f});')
    return html_, init, js


# ═══════════════════════════════════════════════════════════════
#  Proyecto completo
# ═══════════════════════════════════════════════════════════════

TC_LEFT, TC_RIGHT, TC_KICKER_TRACK = 180, 180, 0.12   # los del CSS del title card (left/right, letter-spacing .12em)


def tc_metrics() -> dict[str, Any]:
    """Medidas del title card (las de siempre, F2 §0b.2), en un solo lugar: el CSS y la ficha (F29c §A.5) las leen."""
    ts = gfx_rules.title_scale
    kick_top = 380
    title_top = round(kick_top + 64 * ts + 24)
    return {"scale": ts, "kicker_px": round(64 * ts), "kicker_top": kick_top, "title_px": round(190 * ts),
            "title_top": title_top, "line_top": round(title_top + 190 * ts * 1.05 + 20), "line_w": round(900 * ts),
            "line_h": 6}


def _wrap_lines(text: str, px: int, avail: float, track_em: float = 0.0) -> int:
    """Líneas que ocupa `text` en Anton a `px`, cortando por palabra en `avail` px (medido con la fuente real)."""
    from PIL import ImageFont
    f = ImageFont.truetype(str(GFX_FONTS_DIR / "Anton-Regular.ttf"), px)

    def w(s: str) -> float:
        return f.getlength(s) + track_em * px * len(s)
    lines, cur = 1, ""
    for word in text.split():
        nxt = f"{cur} {word}" if cur else word
        if cur and w(nxt) > avail:
            lines, cur = lines + 1, word
        else:
            cur = nxt
    return lines if text.strip() else 0


FICHA_PLACA_PAD_H = 26          # F32 §B.8: el aire lateral de la placa de `.co-text.stamp` (padding 6px 26px)


def ficha_medida(kicker: str, title: str, width: int = 2560) -> dict[str, int]:
    """F29c §A.5: líneas del kicker y del dato en la ficha: el kicker en una línea, el dato en mayúsculas al ancho del
    title card (left/right 180 px). F32 §B.8: el dato al tamaño de la pregunta de cierre y el kicker con su placa."""
    m = tc_metrics()
    avail = width - TC_LEFT - TC_RIGHT
    return {"kicker": _wrap_lines(kicker.upper(), m["kicker_px"], avail - 2 * FICHA_PLACA_PAD_H, TC_KICKER_TRACK),
            "title": _wrap_lines(title.upper(), gfx_rules.question_font_px, avail)}


def render_css(width: int, height: int) -> str:
    """CSS común con los tokens de gfx_config (acento único, escalas de title y recorte, tipografía)."""
    r, ars = gfx_rules, gfx_rules.archive_scale
    tc = tc_metrics()
    return Template((GFX_TEMPLATES_DIR / "gfx_common.css").read_text(encoding="utf-8")).substitute(
        width=width, height=height, accent=r.accent_hex, archive_body_px=r.archive_body_px,
        archive_body_lines=r.archive_body_lines,
        tc_scale=tc["scale"], tc_kicker_px=tc["kicker_px"], tc_kicker_top=tc["kicker_top"], tc_title_px=tc["title_px"],
        tc_title_top=tc["title_top"], tc_line_top=tc["line_top"], tc_line_w=tc["line_w"],
        callout_font=r.callout_font, callout_font_weight=r.callout_font_weight, callout_font_px=r.callout_font_px,
        callout_anton_px=r.callout_anton_px, callout_shadow=r.callout_shadow,
        title_font=r.title_font, figure_font=r.figure_font, clipping_font=r.clipping_font,
        question_px=r.question_font_px,
        stamp_px=round(r.callout_font_px * 0.62),   # el sello va en una sola línea (fechas largas)
        ar_scale=ars, ar_w=min(round(1100 * ars), round(width * r.archive_max_w_frac)), ar_pad_v=round(50 * ars), ar_pad_h=round(60 * ars),
        ar_pad_b=round(60 * ars), ar_kicker_px=round(34 * ars), ar_head_px=round(84 * ars),
        ar_ico_pad=round(ars * 150) + 16)                          # F3: aire para el ícono del recorte


HEAD_CHAR_W = 0.58                   # ancho medio de una letra de Playfair Display SC 900, en cuerpos
HEAD_STEPS = (1.0, 0.85, 0.72)       # G2: cuerpo del titular; si no entra, baja un cuerpo (nunca se corta)


def archive_head_px(headline: str, width: int, height: int) -> tuple[int, int]:
    """(cuerpo en px, escalón) del titular del recorte para que la tarjeta entre en el cuadro sin cortar texto.
    Estima líneas por ancho de la tarjeta y alto total (kicker + regla + titular + márgenes) contra el alto útil
    (de top 120 px a 120 px del borde de abajo). Escalón 0 = el cuerpo normal."""
    from gfx_config import gfx_rules as r
    ars = r.archive_scale
    ar_w = min(round(1100 * ars), round(width * r.archive_max_w_frac))
    inner = ar_w - 2 * round(60 * ars)
    fixed = round(50 * ars) + round(34 * ars) + 42 + round(60 * ars)
    avail = height - 120 - 120 - fixed
    base = round(84 * ars)
    words = headline.split()
    # F5e G2: hasta 8 palabras va el cuerpo normal si entra; de 9 a 12, un cuerpo menor desde el arranque
    start = 1 if len(words) > 8 else 0
    for k, f in enumerate(HEAD_STEPS):
        if k < start:
            continue
        px = round(base * f)
        per_line = max(1, int(inner / (px * HEAD_CHAR_W)))
        lines, cur = 1, 0
        for w in words:                                   # las palabras no se parten (.w sin corte interno)
            n = len(w) + (1 if cur else 0)
            if cur and cur + n > per_line:
                lines, cur = lines + 1, len(w)
            else:
                cur += n
        if lines * px * 1.04 <= avail:
            return px, k
    return round(base * HEAD_STEPS[-1]), len(HEAD_STEPS) - 1


def write_project(plan: dict[str, Any], scenes: list[GfxScene], project: Path, *,
                  duration: float, width: int, height: int, fps: int,
                  grade_variant: str | None = None, debug: bool = False,
                  transitions: dict[int, dict[str, Any]] | None = None, grade: bool = True) -> Path:
    """Escribe el proyecto HyperFrames del cap. Requiere project/public/base.mp4 ya presente.

    Returns: path a index.html.
    """
    base = project / "public" / "base.mp4"
    if not base.exists():
        raise FileNotFoundError(f"falta {base}")
    (project / "compositions").mkdir(parents=True, exist_ok=True)
    (project / "public" / "fonts").mkdir(parents=True, exist_ok=True)
    (project / "vendor").mkdir(parents=True, exist_ok=True)
    for f in ("Anton-Regular.ttf", "PlayfairDisplaySC-Bold.ttf", "PlayfairDisplaySC-Black.ttf"):
        shutil.copy2(GFX_FONTS_DIR / f, project / "public" / "fonts" / f)
    shutil.copy2(gsap_js(), project / "vendor" / "gsap.min.js")

    # ── escenas
    if transitions is None:
        transitions = transitions_of(plan, scenes)
    hosts: list[str] = []
    for s in scenes:
        n = s.idx + 1
        (project / "compositions" / f"scene_{n:02d}.html").write_text(
            _scene_html(s, n, plan, project, base, width, height, fps, transitions,
                        prev=next((x for x in scenes if x.idx == s.idx - 1), None)), encoding="utf-8")
        hosts.append(f'      <div id="s{n:02d}" class="scene clip" data-composition-id="scene-{n:02d}" '
                     f'data-composition-src="compositions/scene_{n:02d}.html" data-start="{s.start:.3f}" '
                     f'data-duration="{s.duration:.3f}" data-width="{width}" data-height="{height}"></div>')

    overlays, init, js = [], [], []

    # ── grade CSS: solo capas con opacidad > 0 (default "off" = grano + viñeta; sin backdrop-filter)
    variant = GRADE_VARIANTS[grade_variant or gfx_rules.grade_default]
    gi = variant["intensity"]
    layers = {k: v * gi for k, v in variant["opacity"].items() if v * gi > 0} if grade else {}
    if layers:
        divs = "".join(f'\n        <div id="{k}"></div>' for k in layers)
        overlays.append(f'      <div id="grade" class="clip" data-start="0" data-duration="{duration:.3f}">{divs}\n      </div>')
        init.append("      " + " ".join(f'gsap.set("#{k}", {{ opacity: {v:.3f} }});' for k, v in layers.items()))
        if "gr-grain" in layers:
            rnd = random.Random(1441)   # grano determinista: salta de posición N veces/s
            pts = ",".join(f"[{rnd.randint(-180, 180)},{rnd.randint(-180, 180)}]"
                           for _ in range(int(duration * gfx_rules.grain_jumps_per_sec)))
            js.append(f'      [{pts}].forEach(function (p, k) {{ tl.set("#gr-grain", {{ x: p[0], y: p[1] }}, k / {gfx_rules.grain_jumps_per_sec}); }});')

    # ── F2b §2: capas de mood (debajo de los textos) + sello rojo con la palabra
    for i, e in enumerate(plan.get("emphasis", []) or []):
        st = min(e["start"], max(0.0, duration - e["duration"]))
        m_html, m_init, m_js = mood_layer(i, e["layer"], st, e["duration"], width, height)
        overlays.append(m_html)
        init += m_init
        js += m_js
        if e.get("stamp") and e.get("word"):
            sd = gfx_rules.emphasis_stamp_sec
            side = "right:8%" if e.get("side", "right") == "right" else "left:8%"
            # F31: S1/S2/S3 = el sello de hoy ×1/×2/×3 (cuerpo, borde y aire); con P lleva la placa rgba(10,10,10,.35)
            # que ya usa (sin P, sin placa). Sin el flag, como hoy.
            fs = forma("S")
            k = {"S2": 2, "S3": 3}.get((fs or "S1")[:2], 1)
            placa = "background:rgba(10,10,10,.35);" if fs is None or fs.endswith("P") else ""
            overlays.append(f'      <div id="em{i}" class="clip" data-start="{st:.3f}" data-duration="{sd:.3f}" '
                            f'style="position:absolute;top:44%;{side};z-index:6">'
                            f'<span class="em-text" style="display:inline-block;font:400 {gfx_rules.emphasis_stamp_px * k}px/1 '
                            f'&quot;{gfx_rules.figure_font}&quot;,sans-serif;text-transform:uppercase;color:{gfx_rules.accent_hex};'
                            f'border:{7 * k}px solid {gfx_rules.accent_hex};padding:{8 * k}px {26 * k}px {4 * k}px;{placa}'
                            f'white-space:nowrap">{_esc(e["word"])}</span></div>')
            a_init, a_js = _anim_in_js(f"#em{i} .em-text", "stamp", st + 0.05)
            init += a_init
            js += a_js
            js.append(f'      tl.to("#em{i}", {{ opacity: 0, duration: .3, ease: "power1.in" }}, {st + sd - .3:.3f});')

    # ── title_card (F2: 3.0 s, 30 % más chica, fade de salida 0.4 s, video vivo oscurecido 40 %)
    tc = plan.get("title_card")
    if tc:
        dur, fo = gfx_rules.title_dur, gfx_rules.title_fade_out
        overlays.append(_tpl("title_card.html.tmpl").substitute(
            dim_html=f'      <div id="tc-dim" class="clip" data-start="0" data-duration="{dur:.3f}"></div>\n',
            tid="tc", start="0", line_style="", box_class="",
            duration=f"{dur:.3f}", kicker=_esc(tc["kicker"]), title=_esc(tc["title"])))
        init.append(f'      gsap.set("#tc-dim", {{ opacity: {gfx_rules.title_dim} }}); gsap.set("#tc-title span", {{ yPercent: 110 }});'
                    ' gsap.set("#tc-line", { scaleX: 0 }); gsap.set("#tc-kicker", { opacity: 0 });')
        js.append('      tl.to("#tc-kicker", { opacity: 1, duration: .3 }, .05)'
                  '.to("#tc-title span", { yPercent: 0, duration: .55, ease: "power4.out" }, .1)'
                  '.to("#tc-line", { scaleX: 1, duration: .7, ease: "power3.inOut" }, .25)'
                  f'.to(["#tc", "#tc-dim"], {{ opacity: 0, duration: {fo}, ease: "power2.in" }}, {dur - fo:.3f});')

    # ── las fichas (F29c §A.5: la ficha = el title card sin #tc-dim, con su id; F36 §D: el único bloque de texto)
    for i, c in enumerate(plan.get("callouts", [])):
        dur = c.get("duration", gfx_rules.callout_dur)
        st = min(c["start"], max(0.0, duration - dur))
        f_html, f_init, f_js = ficha_html(f"fc{i}", c, st, dur, width)
        overlays.append(f_html)
        init += f_init
        js += f_js

    # ── archive_clipping (F2: hasta 2, 6 s, lado opuesto al sujeto, cuerpo ≥ 52 px, tipografía por década)
    forma_v = forma("V") if forma("V") in ("V2", "V3") else None     # F31
    for i, ar in enumerate(archive_list(plan)):
        a0 = ar["start"]
        a1 = min(a0 + ar["duration"], duration)
        decade = int(ar.get("era_decade") or 2000)
        font, paper = (("Georgia, serif", "#e6dcc3") if decade < 1950
                       else ("'Courier New', monospace", "#e9e4d6") if decade < 1990
                       else ("'Times New Roman', Times, serif", "#ece6d8"))
        head_px, head_step = archive_head_px(ar["headline"], width, height)
        overlays.append(_tpl("archive_clipping.html.tmpl").substitute(
            head_style=(f' style="font-size:{head_px}px"' if head_step else ""),
            i=i, start=f"{a0:.3f}", duration=f"{a1 - a0:.3f}", paper=paper, font=font, side=ar.get("side", "right"),
            kicker=_esc(ar.get("kicker", "")),
            icon_html="",                                                  # F36 §D: sin ícono por tema
            headline=chars_html(ar["headline"]) if gfx_rules.anim_archive_head == "cascade" and not forma_v
            else _esc(ar["headline"]),
            body_block=(f'          <div class="ar-body">{_esc(ar["body"])}</div>\n' if ar.get("body") else "")))
        if forma_v:                                            # F31 V2/V3: el recorte (ya inclinado) entra y sale entero
            v_init, v_js = _forma_v_js(f"#ar{i}-paper", a0, a1 - a0, forma_v)
            init += [f'      gsap.set("#ar{i}-paper", {{ rotation: -2.5 }});'] + v_init
            js += v_js
            continue
        init.append(f'      gsap.set("#ar{i}-paper", {{ opacity: 0, y: -40, rotation: -6 }});')
        if gfx_rules.anim_archive_head == "cascade":
            h_init, h_js = _anim_in_js(f"#ar{i} .ar-head", "cascade", a0 + .35)
            init += h_init
            js += h_js
        js.append(f'      tl.to("#ar{i}-paper", {{ opacity: 1, y: 0, rotation: -2.5, duration: .6, ease: "power3.out" }}, {a0:.3f})'
                  f'.to("#ar{i}-paper", {{ opacity: 0, y: 20, duration: .4, ease: "power1.in" }}, {a1 - .4:.3f});')

    # ── F5f: cita (texto literal + autor) sobre la foto oscurecida
    qc = plan.get("quote_card")
    if qc:
        q_html, q_init, q_js = quote_card_html(qc, width, height, duration)
        overlays.append(q_html)
        init += q_init
        js += q_js

    # ── F3: reloj de esquina
    if plan.get("time_ticker"):
        t_html, t_init, t_js = time_ticker_html(plan["time_ticker"], duration)
        overlays.append(t_html)
        init += t_init
        js += t_js
    bh = plan.get("black_hold")
    if bh:                                                     # F3: corte a negro (sin fundido) al final
        overlays.append(f'      <div id="bh" class="clip" data-start="{bh["start"]:.3f}" data-duration="{bh["duration"]:.3f}" '
                        f'style="position:absolute;inset:0;z-index:60;background:#000"></div>')

    # ── chapter_question (F2 §0d): cierre del cap, fondo 50 %, palabra clave en el acento
    cq = plan.get("chapter_question")
    if cq:
        q0, qd = cq["start"], cq["duration"]
        kw = cq.get("keyword", "")
        txt = _esc(cq["text"])
        if kw:
            txt = re.sub(rf"\b({re.escape(_esc(kw))})\b", r'<span class="kw">\1</span>', txt, count=1)
        overlays.append(_tpl("chapter_question.html.tmpl").substitute(start=f"{q0:.3f}", duration=f"{qd:.3f}", text_html=txt))
        # F3: entrada en persiana (el texto sale de detrás del borde de su máscara) sobre el fondo oscurecido
        init.append('      gsap.set("#cq-dim", { opacity: 0 }); gsap.set("#cq-text .cq-line", { yPercent: 110 });')
        js.append(f'      tl.to("#cq-dim", {{ opacity: {gfx_rules.question_dim}, duration: .35 }}, {q0:.3f})'
                  f'.to("#cq-text .cq-line", {{ yPercent: 0, duration: .6, ease: "power4.out" }}, {q0 + .2:.3f})'
                  + ("" if bh and abs(bh["start"] - (q0 + qd)) < .05 else          # con corte a negro: corte seco, sin fundido
                     f'.to(["#cq-text", "#cq-dim"], {{ opacity: 0, duration: .3, ease: "power1.in" }}, {q0 + qd - .3:.3f})') + ";")

    # ── --gfx-debug: overlay quemado (NUNCA sin el flag)
    if debug:
        dbg_html, dbg_init, dbg_js = _debug_overlay(cue_events(plan, scenes, fps), duration, fps)
        overlays.append(dbg_html)
        init += dbg_init
        js += dbg_js
        for s in scenes:
            js.append(f'      tl.set("#dbg-sc", {{ textContent: "scene_{s.idx + 1:02d}" }}, {s.start:.3f});')

    css = render_css(width, height)
    index = _tpl("index.html.tmpl").substitute(
        width=width, height=height, duration=f"{duration:.3f}", css=css,
        scene_hosts="\n".join(hosts), overlays="\n".join(overlays),
        init_js="\n".join(init), timeline_js="\n".join(js))
    out = project / "index.html"
    out.write_text(index, encoding="utf-8")
    (project / "hyperframes.json").write_text(json.dumps({"media": {"autoProxy": True}}), encoding="utf-8")
    return out
