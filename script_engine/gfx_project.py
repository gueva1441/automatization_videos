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
    safe: dict | None = None   # F2 §4: {"image": png, "movement": push|pan, "risk"} → movimiento seguro HF

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


def callout_anim(kind: str) -> str:
    """Animación firma por tipo de dato (F2 §2)."""
    if kind == "year":
        return gfx_rules.anim_year
    if kind == "figure":
        return gfx_rules.anim_figure
    return gfx_rules.anim_name_place


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


def _source_html(source: str) -> str:
    """source_tag (F2 §0d): 1 línea bajo el callout/contador; vacío si el fact no tiene fuente resoluble."""
    return f'        <div class="co-src">{_esc(source)}</div>\n' if source else ""


# ═══════════════════════════════════════════════════════════════
#  F2b §2: capas de mood (CSS, 1–3 s, intensidad baja; nunca toca píxeles del video)
# ═══════════════════════════════════════════════════════════════

_ABS = "position:absolute;pointer-events:none;"


def mood_layer(i: int, layer: str, t0: float, d: float, width: int, height: int) -> tuple[str, list[str], list[str]]:
    """(html, init, timeline) de la capa de mood `layer` (veneno | agua | muerte | oscuridad) en [t0, t0 + d)."""
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
        # cáusticas de luz sutiles (screen) + sombra oscura que sube desde abajo hasta 1/3
        kids.append(f'<div id="{rid}-cau" style="{_ABS}left:-10%;top:-10%;width:120%;height:120%;mix-blend-mode:screen;'
                    'background:repeating-radial-gradient(circle at 30% 40%,rgba(170,215,255,0) 0 18px,'
                    'rgba(170,215,255,.10) 22px,rgba(170,215,255,0) 30px),repeating-radial-gradient(circle at 70% 65%,'
                    'rgba(170,215,255,0) 0 26px,rgba(170,215,255,.08) 30px,rgba(170,215,255,0) 38px)"></div>')
        fade(f"#{rid}-cau", 0.6, t0, 0.5)
        js.append(f'      tl.to("#{rid}-cau", {{ x: 40, y: 20, rotation: 3, duration: {d:.3f}, ease: "none" }}, {t0:.3f});')
        kids.append(f'<div id="{rid}-rise" style="{_ABS}left:0;right:0;bottom:0;height:34%;'
                    'background:linear-gradient(to top,rgba(2,10,20,.78),rgba(2,10,20,0))"></div>')
        init.append(f'      gsap.set("#{rid}-rise", {{ yPercent: 100 }});')
        js.append(f'      tl.to("#{rid}-rise", {{ yPercent: 0, duration: 1.2, ease: "power2.out" }}, {t0:.3f})'
                  f'.to("#{rid}-rise", {{ opacity: 0, duration: .5, ease: "sine.in" }}, {out_at:.3f});')
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


def load_grade_preset() -> dict[str, Any]:
    """Preset de grade versionado (D4)."""
    return json.loads((GFX_TEMPLATES_DIR / "gfx_grade.json").read_text(encoding="utf-8"))


# ═══════════════════════════════════════════════════════════════
#  count_up: formateo que reproduce EXACTO el literal del fact
# ═══════════════════════════════════════════════════════════════

_NUM_RE = re.compile(r"^(?P<num>\d{1,3}(?:[,.]\d{3})+|\d+(?:[.,]\d+)?)(?P<suffix>%?)$")


def parse_count_literal(value_text: str) -> dict[str, Any] | None:
    """'6,500' → {value: 6500, thousands: ',', decimals: 0, dec_sep: '.', suffix: ''}. None si no es cifra."""
    m = _NUM_RE.match(value_text.strip())
    if not m:
        return None
    num, suffix = m.group("num"), m.group("suffix")
    if re.fullmatch(r"\d{1,3}(?:[,.]\d{3})+", num):
        sep = "," if "," in num else "."
        return {"value": int(num.replace(sep, "")), "thousands": sep, "decimals": 0,
                "dec_sep": "." if sep == "," else ",", "suffix": suffix}
    if "." in num or "," in num:
        dec_sep = "." if "." in num else ","
        ip, dp = num.split(dec_sep)
        return {"value": float(f"{ip}.{dp}"), "thousands": "", "decimals": len(dp),
                "dec_sep": dec_sep, "suffix": suffix}
    return {"value": int(num), "thousands": "", "decimals": 0, "dec_sep": ".", "suffix": suffix}


def format_count(value: float, spec: dict[str, Any]) -> str:
    """Formatea igual que el literal (separador de miles, decimales, sufijo)."""
    if spec["decimals"]:
        s = f"{value:.{spec['decimals']}f}".replace(".", spec["dec_sep"])
    else:
        s = f"{int(round(value)):,}".replace(",", spec["thousands"]) if spec["thousands"] else str(int(round(value)))
    return s + spec["suffix"]


# ═══════════════════════════════════════════════════════════════
#  Escenas
# ═══════════════════════════════════════════════════════════════

def scene_at(scenes: list[GfxScene], t: float) -> GfxScene:
    """Escena que contiene el instante t (la última si t cae al final)."""
    for s in scenes:
        if s.start <= t < s.end:
            return s
    return scenes[-1]


def _extract_freeze(base: Path, t: float, out: Path) -> bool:
    """Último frame del plano saliente. Llamar con t = corte − 1.5 frames: `-ss` descarta los frames con
    pts < t, así que pedir "corte − 1 frame" redondeado a 4 decimales caía DESPUÉS del último frame
    saliente y devolvía el ENTRANTE (bug F2 §0b.4: disolvencias R3 = corte duro)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, t):.4f}", "-i", str(base),
                        "-frames:v", "1", "-q:v", "2", str(out)],
                       capture_output=True, timeout=120)
    return r.returncode == 0 and out.exists()


def plan_transitions(scenes: list[GfxScene], zoom_scene_idx: int | None = None) -> dict[int, dict[str, Any]]:
    """shot_transition de ENTRADA por escena (determinista desde emotional_rank del plano entrante).

    R1 → flash, salvo que ya se hayan usado gfx_rules.flash_max_per_cap flashes o el anterior
    esté a < flash_min_gap_sec: entonces corte duro + punch (cut_punch). R2/R3 → disolvencia.
    """
    out: dict[int, dict[str, Any]] = {}
    flashes: list[float] = []
    for s in scenes[1:]:
        frames = gfx_rules.transition_frames.get(s.rank, gfx_rules.transition_frames["R3"])
        if zoom_scene_idx is not None and s.idx == zoom_scene_idx + 1:
            # F2 §0b.5: el zoom termina EN el corte; una disolvencia partiría del freeze sin zoom
            # (la foto inicial) → corte seco
            out[s.idx] = {"kind": "cut", "frames": 0, "rank": s.rank}
        elif s.rank == "R1":
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
        else:
            init.append(f'        gsap.set("#sf{tag}", {{ scale: 1, transformOrigin: "50% 50%" }});')
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
    has_zoom = bool(plan.get("evidence_zoom")) and plan["evidence_zoom"].get("scene_idx") == s.idx
    for e in plan.get("emphasis", []) or []:
        if e.get("layer") == "muerte" and s.start <= e["start"] < s.end and not (has_punch or has_zoom):
            js.append(f'        tl.to("#vw{tag}", {{ scale: 1.015, duration: {e["duration"]:.3f}, ease: "none" }}, {e["start"] - s.start:.3f});')
            break

    # ── evidence_zoom sobre el FRAME DE VIDEO, salida en corte
    ez = plan.get("evidence_zoom")
    if ez and ez["scene_idx"] == s.idx:
        bx, by, bw, bh = ez["box"]
        x, y, w, h = bx * width, by * height, bw * width, bh * height
        cx, cy, S = x + w / 2, y + h / 2, gfx_rules.zoom_scale
        tx = min(max(width / 2, width - (width - cx) * S), cx * S) - cx
        ty = min(max(height * .42, height - (height - cy) * S), cy * S) - cy
        mg = gfx_rules.zoom_label_margin_px                         # "DETALLE" a ≥ mg px de los bordes
        lx = min(max(mg, cx + tx - w * S / 2), width - mg - 380.0)
        ly = min(max(mg, cy + ty - h * S / 2 - 64), height - mg - 50.0)
        # F2 §0b.5: el zoom TERMINA en el corte (acerca, sostiene ≥ 1 s y la escena corta). Nunca vuelve.
        z0 = (ez["start"] - s.start) if "start" in ez else max(0.0, s.duration - gfx_rules.zoom_dur)
        rest = s.duration - z0
        inner.append(_tpl("evidence_zoom.html.tmpl").substitute(n=tag, x=f"{x:.0f}", y=f"{y:.0f}", w=f"{w:.0f}", h=f"{h:.0f}"))
        outer.append(f'    <div id="zl{tag}" class="zlabel clip" data-start="{z0:.3f}" data-duration="{rest:.3f}" '
                     f'style="left:{lx:.0f}px;top:{ly:.0f}px">DETALLE</div>')
        if gfx_rules.anim_detail_label == "stamp":   # F2 §2: "DETALLE" entra como sello
            init.append(f'        gsap.set("#vw{tag}", {{ transformOrigin: "{cx:.1f}px {cy:.1f}px" }});'
                        f' gsap.set("#zl{tag}", {{ opacity: 0, scale: {gfx_rules.stamp_from_scale}, rotation: {gfx_rules.stamp_rotation} }});')
        else:
            init.append(f'        gsap.set("#vw{tag}", {{ transformOrigin: "{cx:.1f}px {cy:.1f}px" }}); gsap.set("#zl{tag}", {{ opacity: 0 }});')
        r0, ap = gfx_rules.zoom_rect_sec, gfx_rules.zoom_approach_sec
        js.append(f'        tl.to("#zr{tag}", {{ opacity: 1, duration: .3 }}, {z0 + .25:.3f})'
                  f'.to("#vw{tag}", {{ scale: {S}, x: {tx:.1f}, y: {ty:.1f}, duration: {ap}, ease: "power3.inOut" }}, {z0 + r0:.3f})'
                  + (f'.to("#zl{tag}", {{ opacity: 1, scale: 1, rotation: 0, duration: {gfx_rules.stamp_sec}, ease: "power4.in" }}, {z0 + r0 + ap - .1:.3f});'
                     if gfx_rules.anim_detail_label == "stamp" else
                     f'.to("#zl{tag}", {{ opacity: 1, duration: .25 }}, {z0 + r0 + ap - .1:.3f});'))

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
    for c in plan.get("callouts", []):
        if c.get("source"):
            add(c["start"], c.get("duration", gfx_rules.callout_dur), "source_tag", c["source"])
    for c in plan.get("callouts", []):
        add(c["start"], c.get("duration", gfx_rules.callout_dur), "data_callout", c["text"])
    cu = plan.get("count_up")
    if cu:
        add(cu["start"], cu.get("duration", gfx_rules.count_dur + gfx_rules.count_hold_sec), "count_up", f"{cu['value_text']} {cu.get('unit', '')}".strip())
    for ar in archive_list(plan):
        add(ar["start"], ar["duration"], "archive_clipping", ar["headline"])
    ez = plan.get("evidence_zoom")
    if ez and 0 <= ez["scene_idx"] < len(scenes):
        sc = scenes[ez["scene_idx"]]
        z0 = ez.get("start", sc.end - gfx_rules.zoom_dur)
        add(z0, sc.end - z0, "evidence_zoom", f"box {ez['box']}")
    for t in plan.get("punch_in", []):
        add(t, gfx_rules.punch_in_sec + gfx_rules.punch_out_sec, "punch_in")
    for e in plan.get("emphasis", []) or []:                    # F2b §2
        add(e["start"], e["duration"], f"keyword_emphasis:{e['category']}", e["word"])
    for idx, tr in plan_transitions(scenes, (plan.get("evidence_zoom") or {}).get("scene_idx")).items():
        sc = scenes[idx]
        label = (f"{tr['frames']} f" if tr["frames"] else
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

def render_css(width: int, height: int) -> str:
    """CSS común con los tokens de gfx_config (acento único, escalas de title y recorte, tipografía)."""
    r, ts, ars = gfx_rules, gfx_rules.title_scale, gfx_rules.archive_scale
    kick_top = 380
    title_top = round(kick_top + 64 * ts + 24)
    return Template((GFX_TEMPLATES_DIR / "gfx_common.css").read_text(encoding="utf-8")).substitute(
        width=width, height=height, accent=r.accent_hex, archive_body_px=r.archive_body_px,
        archive_body_lines=r.archive_body_lines,
        tc_scale=ts, tc_kicker_px=round(64 * ts), tc_kicker_top=kick_top, tc_title_px=round(190 * ts),
        tc_title_top=title_top, tc_line_top=round(title_top + 190 * ts * 1.05 + 20), tc_line_w=round(900 * ts),
        callout_font=r.callout_font, callout_font_weight=r.callout_font_weight, callout_font_px=r.callout_font_px,
        callout_anton_px=r.callout_anton_px, callout_shadow=r.callout_shadow,
        title_font=r.title_font, figure_font=r.figure_font, clipping_font=r.clipping_font,
        source_px=round(r.callout_anton_px * r.source_tag_scale), question_px=r.question_font_px,
        stamp_px=round(r.callout_font_px * 0.62),   # el sello va en una sola línea (fechas largas)
        ar_scale=ars, ar_w=min(round(1100 * ars), round(width * r.archive_max_w_frac)), ar_pad_v=round(50 * ars), ar_pad_h=round(60 * ars),
        ar_pad_b=round(60 * ars), ar_kicker_px=round(34 * ars), ar_head_px=round(84 * ars))


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
        transitions = plan_transitions(scenes, (plan.get("evidence_zoom") or {}).get("scene_idx"))
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
            overlays.append(f'      <div id="em{i}" class="clip" data-start="{st:.3f}" data-duration="{sd:.3f}" '
                            f'style="position:absolute;top:44%;{side};z-index:6">'
                            f'<span class="em-text" style="display:inline-block;font:400 {gfx_rules.emphasis_stamp_px}px/1 '
                            f'&quot;{gfx_rules.figure_font}&quot;,sans-serif;text-transform:uppercase;color:{gfx_rules.accent_hex};'
                            f'border:7px solid {gfx_rules.accent_hex};padding:8px 26px 4px;background:rgba(10,10,10,.35);'
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
            duration=f"{dur:.3f}", kicker=_esc(tc["kicker"]), title=_esc(tc["title"])))
        init.append(f'      gsap.set("#tc-dim", {{ opacity: {gfx_rules.title_dim} }}); gsap.set("#tc-title span", {{ yPercent: 110 }});'
                    ' gsap.set("#tc-line", { scaleX: 0 }); gsap.set("#tc-kicker", { opacity: 0 });')
        js.append('      tl.to("#tc-kicker", { opacity: 1, duration: .3 }, .05)'
                  '.to("#tc-title span", { yPercent: 0, duration: .55, ease: "power4.out" }, .1)'
                  '.to("#tc-line", { scaleX: 1, duration: .7, ease: "power3.inOut" }, .25)'
                  f'.to(["#tc", "#tc-dim"], {{ opacity: 0, duration: {fo}, ease: "power2.in" }}, {dur - fo:.3f});')

    # ── data_callout (tercio superior, lado según el sujeto; figure → Anton, resto → Playfair SC)
    for i, c in enumerate(plan.get("callouts", [])):
        dur = c.get("duration", gfx_rules.callout_dur)
        st = min(c["start"], max(0.0, duration - dur))
        face = "anton" if c.get("kind") == "figure" else "serif"
        anim = callout_anim(c.get("kind", ""))
        text_html = chars_html(c["text"]) if anim == "cascade" else _esc(c["text"])
        face_cls = f"{face} stamp" if anim == "stamp" else face
        overlays.append(_tpl("data_callout.html.tmpl").substitute(
            i=i, start=f"{st:.3f}", duration=f"{dur:.3f}", text=text_html,
            side=c.get("side", "left"), face=face_cls, mask_cls="co-mask stamped" if anim == "stamp" else "co-mask",
            source_html=_source_html(c.get("source", ""))))
        a_init, a_js = _anim_in_js(f"#co{i} .co-text", anim, st)
        init += a_init + [f'      gsap.set("#co{i} .co-rule", {{ scaleX: 0 }});']
        js += a_js
        js.append(f'      tl.to("#co{i} .co-rule", {{ scaleX: 1, duration: .5, ease: "power3.inOut" }}, {st + .08:.3f})'
                  f'.to("#co{i}", {{ opacity: 0, duration: .35, ease: "power1.in" }}, {st + dur - .35:.3f});')

    # ── count_up (cifra literal del fact, Anton)
    cu = plan.get("count_up")
    if cu:
        spec = parse_count_literal(cu["value_text"])
        if spec is not None and format_count(spec["value"], spec) == cu["value_text"]:
            dur = gfx_rules.count_dur + gfx_rules.count_hold_sec
            st = min(cu["start"], max(0.0, duration - dur))
            overlays.append(_tpl("count_up.html.tmpl").substitute(
                start=f"{st:.3f}", duration=f"{dur:.3f}", zero_text=_esc(format_count(0, spec)), unit=_esc(cu.get("unit", "")),
                source_html=_source_html(cu.get("source", ""))))
            js.append(f'      var cuSpec = {json.dumps(spec)}; var cuObj = {{ v: 0 }};'
                      ' function cuFmt(v) { var s = cuSpec.decimals ? v.toFixed(cuSpec.decimals).replace(".", cuSpec.dec_sep)'
                      ' : String(Math.round(v)).replace(/\\B(?=(\\d{3})+(?!\\d))/g, cuSpec.thousands); return s + cuSpec.suffix; }'
                      f' tl.to(cuObj, {{ v: cuSpec.value, duration: {gfx_rules.count_dur}, ease: "power2.out",'
                      ' onUpdate: function () { document.getElementById("cu-num").textContent = cuFmt(cuObj.v); } },'
                      f' {st:.3f}); tl.to("#cu", {{ opacity: 0, duration: .3 }}, {st + dur - .3:.3f});')
            if gfx_rules.anim_figure == "number_pop":            # F2 §2: golpe 1.08 → 1.0 al llegar al valor
                t_hit = st + gfx_rules.count_dur
                js.append(f'      tl.fromTo("#cu-num", {{ scale: {gfx_rules.pop_from_scale} }}, {{ scale: 1, duration: {gfx_rules.pop_sec},'
                          f' ease: "power2.out", immediateRender: false }}, {t_hit:.3f});')
                init.append('      gsap.set("#cu-num", { display: "inline-block", transformOrigin: "50% 60%" });')

    # ── archive_clipping (F2: hasta 2, 6 s, lado opuesto al sujeto, cuerpo ≥ 52 px, tipografía por década)
    for i, ar in enumerate(archive_list(plan)):
        a0 = ar["start"]
        a1 = min(a0 + ar["duration"], duration)
        decade = int(ar.get("era_decade") or 2000)
        font, paper = (("Georgia, serif", "#e6dcc3") if decade < 1950
                       else ("'Courier New', monospace", "#e9e4d6") if decade < 1990
                       else ("'Times New Roman', Times, serif", "#ece6d8"))
        overlays.append(_tpl("archive_clipping.html.tmpl").substitute(
            i=i, start=f"{a0:.3f}", duration=f"{a1 - a0:.3f}", paper=paper, font=font, side=ar.get("side", "right"),
            kicker=_esc(ar.get("kicker", "")),
            headline=chars_html(ar["headline"]) if gfx_rules.anim_archive_head == "cascade" else _esc(ar["headline"]),
            body_block=(f'          <div class="ar-body">{_esc(ar["body"])}</div>\n' if ar.get("body") else "")))
        init.append(f'      gsap.set("#ar{i}-paper", {{ opacity: 0, y: -40, rotation: -6 }});')
        if gfx_rules.anim_archive_head == "cascade":
            h_init, h_js = _anim_in_js(f"#ar{i} .ar-head", "cascade", a0 + .35)
            init += h_init
            js += h_js
        js.append(f'      tl.to("#ar{i}-paper", {{ opacity: 1, y: 0, rotation: -2.5, duration: .6, ease: "power3.out" }}, {a0:.3f})'
                  f'.to("#ar{i}-paper", {{ opacity: 0, y: 20, duration: .4, ease: "power1.in" }}, {a1 - .4:.3f});')

    # ── chapter_question (F2 §0d): cierre del cap, fondo 50 %, palabra clave en el acento
    cq = plan.get("chapter_question")
    if cq:
        q0, qd = cq["start"], cq["duration"]
        kw = cq.get("keyword", "")
        txt = _esc(cq["text"])
        if kw:
            txt = re.sub(rf"\b({re.escape(_esc(kw))})\b", r'<span class="kw">\1</span>', txt, count=1)
        overlays.append(_tpl("chapter_question.html.tmpl").substitute(start=f"{q0:.3f}", duration=f"{qd:.3f}", text_html=txt))
        init.append('      gsap.set("#cq-dim", { opacity: 0 }); gsap.set("#cq-text", { opacity: 0, y: 24 });')
        js.append(f'      tl.to("#cq-dim", {{ opacity: {gfx_rules.question_dim}, duration: .35 }}, {q0:.3f})'
                  f'.to("#cq-text", {{ opacity: 1, y: 0, duration: .5, ease: "power3.out" }}, {q0 + .15:.3f})'
                  f'.to(["#cq-text", "#cq-dim"], {{ opacity: 0, duration: .3, ease: "power1.in" }}, {q0 + qd - .3:.3f});')

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
