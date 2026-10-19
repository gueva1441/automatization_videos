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

    @property
    def duration(self) -> float:
        return self.end - self.start


def _tpl(name: str) -> Template:
    return Template((GFX_TEMPLATES_DIR / name).read_text(encoding="utf-8"))


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


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
    """Último frame del plano saliente (t = corte - 1 frame)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, t):.4f}", "-i", str(base),
                        "-frames:v", "1", "-q:v", "2", str(out)],
                       capture_output=True, timeout=120)
    return r.returncode == 0 and out.exists()


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
        else:
            out[s.idx] = {"kind": "dissolve", "frames": frames, "rank": s.rank}
    return out


def _scene_html(s: GfxScene, n: int, plan: dict[str, Any], project: Path,
                base: Path, width: int, height: int, fps: int,
                transitions: dict[int, dict[str, Any]] | None = None) -> str:
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
        else:
            freeze = project / "public" / "cuts" / f"freeze_{tag}.jpg"
            if _extract_freeze(base, s.start - 1 / fps, freeze):
                outer.append(f'    <img id="fz{tag}" class="media clip" src="public/cuts/{freeze.name}" data-start="0" '
                             f'data-duration="{d:.3f}" alt="" />')
                init.append(f'        gsap.set("#fz{tag}", {{ opacity: 1 }});')
                js.append(f'        tl.to("#fz{tag}", {{ opacity: 0, duration: {d:.3f}, ease: "sine.inOut" }}, 0);')

    # ── punch_in en la CAPA DE VIDEO (los subs se queman después, no escalan)
    for t in plan.get("punch_in", []):
        if s.start <= t < s.end:
            lt = t - s.start
            js.append(f'        tl.to("#vw{tag}", {{ scale: {gfx_rules.punch_scale}, duration: {gfx_rules.punch_in_sec}, ease: "power2.out" }}, {lt:.3f})'
                      f'.to("#vw{tag}", {{ scale: 1, duration: {gfx_rules.punch_out_sec}, ease: "power2.inOut" }}, {lt + gfx_rules.punch_in_sec:.3f});')

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
        z0 = (ez["start"] - s.start) if "start" in ez else min(0.5, max(0.0, s.duration - gfx_rules.zoom_dur))
        inner.append(_tpl("evidence_zoom.html.tmpl").substitute(n=tag, x=f"{x:.0f}", y=f"{y:.0f}", w=f"{w:.0f}", h=f"{h:.0f}"))
        outer.append(f'    <div id="zl{tag}" class="zlabel clip" data-start="{z0:.3f}" data-duration="{gfx_rules.zoom_dur:.3f}" '
                     f'style="left:{lx:.0f}px;top:{ly:.0f}px">DETALLE</div>')
        init.append(f'        gsap.set("#vw{tag}", {{ transformOrigin: "{cx:.1f}px {cy:.1f}px" }}); gsap.set("#zl{tag}", {{ opacity: 0 }});')
        end = z0 + gfx_rules.zoom_dur - 1 / fps
        js.append(f'        tl.to("#zr{tag}", {{ opacity: 1, duration: .3 }}, {z0 + .25:.3f})'
                  f'.to("#vw{tag}", {{ scale: {S}, x: {tx:.1f}, y: {ty:.1f}, duration: 1.2, ease: "power3.inOut" }}, {z0 + .65:.3f})'
                  f'.to("#zl{tag}", {{ opacity: 1, duration: .25 }}, {z0 + 1.75:.3f})'
                  f'.set("#vw{tag}", {{ scale: 1, x: 0, y: 0 }}, {end:.3f})'
                  f'.set(["#zr{tag}", "#zl{tag}"], {{ opacity: 0 }}, {end:.3f});')

    return _tpl("scene.html.tmpl").substitute(
        n=tag, duration=f"{s.duration:.3f}", width=width, height=height,
        media_start=f"{s.start:.3f}",
        inner_html="\n".join(inner), outer_html="\n".join(outer),
        init_js="\n".join(init), timeline_js="\n".join(js),
    )


# ═══════════════════════════════════════════════════════════════
#  Cues: eventos del cap (hoja de cues, overlay --gfx-debug, página de revisión)
# ═══════════════════════════════════════════════════════════════

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
    for c in plan.get("callouts", []):
        add(c["start"], c.get("duration", gfx_rules.callout_dur), "data_callout", c["text"])
    cu = plan.get("count_up")
    if cu:
        add(cu["start"], cu.get("duration", gfx_rules.count_dur + gfx_rules.count_hold_sec), "count_up", f"{cu['value_text']} {cu.get('unit', '')}".strip())
    ar = plan.get("archive_clipping")
    if ar and 0 <= ar["scene_idx"] < len(scenes):
        sc = scenes[ar["scene_idx"]]
        add(sc.start + 0.5, sc.duration - 1.0, "archive_clipping", ar["headline"])
    ez = plan.get("evidence_zoom")
    if ez and 0 <= ez["scene_idx"] < len(scenes):
        sc = scenes[ez["scene_idx"]]
        add(ez.get("start", sc.start + 0.5), gfx_rules.zoom_dur, "evidence_zoom", f"box {ez['box']}")
    for t in plan.get("punch_in", []):
        add(t, gfx_rules.punch_in_sec + gfx_rules.punch_out_sec, "punch_in")
    for idx, tr in plan_transitions(scenes).items():
        sc = scenes[idx]
        add(sc.start, tr["frames"] / fps, f"shot_transition:{tr['kind']}", f"{tr['frames']} f" if tr["frames"] else "corte + punch",
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

def write_project(plan: dict[str, Any], scenes: list[GfxScene], project: Path, *,
                  duration: float, width: int, height: int, fps: int,
                  grade_variant: str | None = None, debug: bool = False) -> Path:
    """Escribe el proyecto HyperFrames del cap. Requiere project/public/base.mp4 ya presente.

    Returns: path a index.html.
    """
    base = project / "public" / "base.mp4"
    if not base.exists():
        raise FileNotFoundError(f"falta {base}")
    (project / "compositions").mkdir(parents=True, exist_ok=True)
    (project / "public" / "fonts").mkdir(parents=True, exist_ok=True)
    (project / "vendor").mkdir(parents=True, exist_ok=True)
    shutil.copy2(GFX_FONTS_DIR / "Anton-Regular.ttf", project / "public" / "fonts" / "Anton-Regular.ttf")
    shutil.copy2(gsap_js(), project / "vendor" / "gsap.min.js")

    # ── escenas
    transitions = plan_transitions(scenes)
    hosts: list[str] = []
    for s in scenes:
        n = s.idx + 1
        (project / "compositions" / f"scene_{n:02d}.html").write_text(
            _scene_html(s, n, plan, project, base, width, height, fps, transitions), encoding="utf-8")
        hosts.append(f'      <div id="s{n:02d}" class="scene clip" data-composition-id="scene-{n:02d}" '
                     f'data-composition-src="compositions/scene_{n:02d}.html" data-start="{s.start:.3f}" '
                     f'data-duration="{s.duration:.3f}" data-width="{width}" data-height="{height}"></div>')

    overlays, init, js = [], [], []

    # ── grade CSS (todos los caps): capas sobre las escenas, bajo los gráficos
    variant = GRADE_VARIANTS[grade_variant or gfx_rules.css_grade_variant]
    gi = variant["intensity"]
    if gi > 0:
        overlays.append(_tpl("grade_css.html.tmpl").substitute(duration=f"{duration:.3f}"))
        init.append("      " + " ".join(f'gsap.set("#{k}", {{ opacity: {v * gi:.3f} }});'
                                         for k, v in variant["opacity"].items()))
        rnd = random.Random(1441)   # grano determinista: salta de posición N veces/s
        pts = ",".join(f"[{rnd.randint(-180, 180)},{rnd.randint(-180, 180)}]"
                       for _ in range(int(duration * gfx_rules.grain_jumps_per_sec)))
        js.append(f'      [{pts}].forEach(function (p, k) {{ tl.set("#gr-grain", {{ x: p[0], y: p[1] }}, k / {gfx_rules.grain_jumps_per_sec}); }});')

    # ── title_card (1.9 s, video vivo oscurecido 40 %)
    tc = plan.get("title_card")
    if tc:
        dur = gfx_rules.title_dur
        overlays.append(_tpl("title_card.html.tmpl").substitute(
            duration=f"{dur:.3f}", kicker=_esc(tc["kicker"]), title=_esc(tc["title"])))
        init.append(f'      gsap.set("#tc-dim", {{ opacity: {gfx_rules.title_dim} }}); gsap.set("#tc-title span", {{ yPercent: 110 }});'
                    ' gsap.set("#tc-line", { scaleX: 0 }); gsap.set("#tc-kicker", { opacity: 0 });')
        js.append('      tl.to("#tc-kicker", { opacity: 1, duration: .3 }, .05)'
                  '.to("#tc-title span", { yPercent: 0, duration: .55, ease: "power4.out" }, .1)'
                  '.to("#tc-line", { scaleX: 1, duration: .7, ease: "power3.inOut" }, .25)'
                  f'.to(["#tc", "#tc-dim"], {{ opacity: 0, duration: .4, ease: "power2.in" }}, {dur - .4:.3f});')

    # ── data_callout (tercio superior, máscara de entrada + fade)
    for i, c in enumerate(plan.get("callouts", [])):
        dur = c.get("duration", gfx_rules.callout_dur)
        st = min(c["start"], max(0.0, duration - dur))
        overlays.append(_tpl("data_callout.html.tmpl").substitute(i=i, start=f"{st:.3f}", duration=f"{dur:.3f}", text=_esc(c["text"])))
        init.append(f'      gsap.set("#co{i} .co-text", {{ yPercent: 105 }}); gsap.set("#co{i} .co-rule", {{ scaleX: 0 }});')
        js.append(f'      tl.to("#co{i} .co-text", {{ yPercent: 0, duration: .38, ease: "power3.out" }}, {st:.3f})'
                  f'.to("#co{i} .co-rule", {{ scaleX: 1, duration: .5, ease: "power3.inOut" }}, {st + .08:.3f})'
                  f'.to("#co{i}", {{ opacity: 0, duration: .35, ease: "power1.in" }}, {st + dur - .35:.3f});')

    # ── count_up (cifra literal del fact)
    cu = plan.get("count_up")
    if cu:
        spec = parse_count_literal(cu["value_text"])
        if spec is not None and format_count(spec["value"], spec) == cu["value_text"]:
            dur = gfx_rules.count_dur + gfx_rules.count_hold_sec
            st = min(cu["start"], max(0.0, duration - dur))
            overlays.append(_tpl("count_up.html.tmpl").substitute(
                start=f"{st:.3f}", duration=f"{dur:.3f}", zero_text=_esc(format_count(0, spec)), unit=_esc(cu.get("unit", ""))))
            js.append(f'      var cuSpec = {json.dumps(spec)}; var cuObj = {{ v: 0 }};'
                      ' function cuFmt(v) { var s = cuSpec.decimals ? v.toFixed(cuSpec.decimals).replace(".", cuSpec.dec_sep)'
                      ' : String(Math.round(v)).replace(/\\B(?=(\\d{3})+(?!\\d))/g, cuSpec.thousands); return s + cuSpec.suffix; }'
                      f' tl.to(cuObj, {{ v: cuSpec.value, duration: {gfx_rules.count_dur}, ease: "power2.out",'
                      ' onUpdate: function () { document.getElementById("cu-num").textContent = cuFmt(cuObj.v); } },'
                      f' {st:.3f}); tl.to("#cu", {{ opacity: 0, duration: .3 }}, {st + dur - .3:.3f});')

    # ── archive_clipping (sobre su escena, cuerpo ≥ 52 px, tipografía por década)
    ar = plan.get("archive_clipping")
    if ar and 0 <= ar["scene_idx"] < len(scenes):
        s = scenes[ar["scene_idx"]]
        a0, a1 = s.start + 0.5, s.end - 0.5
        decade = int(ar.get("era_decade") or 2000)
        font, paper = (("Georgia, serif", "#e6dcc3") if decade < 1950
                       else ("'Courier New', monospace", "#e9e4d6") if decade < 1990
                       else ("'Times New Roman', Times, serif", "#ece6d8"))
        overlays.append(_tpl("archive_clipping.html.tmpl").substitute(
            start=f"{a0:.3f}", duration=f"{a1 - a0:.3f}", paper=paper, font=font,
            kicker=_esc(ar.get("kicker", "")), headline=_esc(ar["headline"]), body=_esc(ar["body"])))
        init.append('      gsap.set("#ar-paper", { opacity: 0, y: -40, rotation: -6 });')
        js.append(f'      tl.to("#ar-paper", {{ opacity: 1, y: 0, rotation: -2.5, duration: .6, ease: "power3.out" }}, {a0:.3f})'
                  f'.to("#ar-paper", {{ opacity: 0, y: 20, duration: .4, ease: "power1.in" }}, {a1 - .4:.3f});')

    # ── --gfx-debug: overlay quemado (NUNCA sin el flag)
    if debug:
        dbg_html, dbg_init, dbg_js = _debug_overlay(cue_events(plan, scenes, fps), duration, fps)
        overlays.append(dbg_html)
        init += dbg_init
        js += dbg_js
        for s in scenes:
            js.append(f'      tl.set("#dbg-sc", {{ textContent: "scene_{s.idx + 1:02d}" }}, {s.start:.3f});')

    css = Template((GFX_TEMPLATES_DIR / "gfx_common.css").read_text(encoding="utf-8")).substitute(
        width=width, height=height, archive_body_px=gfx_rules.archive_body_px)
    index = _tpl("index.html.tmpl").substitute(
        width=width, height=height, duration=f"{duration:.3f}", css=css,
        scene_hosts="\n".join(hosts), overlays="\n".join(overlays),
        init_js="\n".join(init), timeline_js="\n".join(js))
    out = project / "index.html"
    out.write_text(index, encoding="utf-8")
    (project / "hyperframes.json").write_text(json.dumps({"media": {"autoProxy": True}}), encoding="utf-8")
    return out
