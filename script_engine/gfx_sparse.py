"""
gfx_sparse.py — Render DISPERSO de la capa gráfica (F2 §3.1, flag --gfx-sparse).

En vez de renderizar el cap entero en HyperFrames (captura de Chrome cuadro a cuadro), se
renderizan solo las VENTANAS con eventos (title card, callouts, count_up, recorte, zoom,
punch_in hasta el corte, transiciones, chapter_question) y el resto sale del base_g30.

Diseño (sin empalmes visibles):
  1. event_windows(): ventanas de eventos ± margen, fusionadas si están cerca.
  2. UN solo proyecto HyperFrames con las ventanas una detrás de otra (un arranque de Chrome):
     base_sparse.mp4 = concat de los tramos del base; plan y escenas corridos al timeline
     concatenado; en cada unión de ventanas, corte seco (no hay transición entre ventanas).
  3. Las ventanas se renderizan SIN grade CSS. El grade (viñeta + grano) se aplica con FFmpeg
     sobre el cap ya cosido, igual en ventanas y en tramos de base → el look es uniforme y
     los empalmes no saltan.
  4. stitch(): un solo ffmpeg: trim de tramos del base + trims del render HF, concat,
     grade FFmpeg, encode.

Nunca lanza hacia fase2b: gfx_layer envuelve todo en el fallback de siempre.
"""
from __future__ import annotations

import copy
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from gfx_config import gfx_rules
from script_engine.gfx_project import GfxScene, archive_list, transitions_of


def _frame(t: float, fps: int) -> float:
    return round(round(t * fps) / fps, 6)


def event_windows(plan: dict[str, Any], scenes: list[GfxScene], fps: int, dur: float, *,
                  margin: float = 0.5, merge_gap: float = 2.0) -> list[tuple[float, float]]:
    """Intervalos [a, b) del cap que necesitan HyperFrames, alineados a frame."""
    iv: list[tuple[float, float]] = []
    if plan.get("title_card"):
        iv.append((0.0, gfx_rules.title_dur + 0.2))
    for c in plan.get("callouts", []):
        iv.append((c["start"], c["start"] + c.get("duration", gfx_rules.callout_dur)))
    cu = plan.get("count_up")
    if cu:
        iv.append((cu["start"], cu["start"] + gfx_rules.count_dur + gfx_rules.count_hold_sec))
    for ar in archive_list(plan):
        iv.append((ar["start"], ar["start"] + ar["duration"]))
    cq = plan.get("chapter_question")
    if cq:
        iv.append((cq["start"], cq["start"] + cq["duration"]))
    for e in plan.get("emphasis", []) or []:                  # F2b §2: capa de mood + sello
        iv.append((e["start"], e["start"] + e["duration"]))
    if plan.get("icon_array"):                                # F2b §3
        iv.append((plan["icon_array"]["start"], plan["icon_array"]["start"] + plan["icon_array"]["duration"]))
    for k in ("water_level", "time_ticker", "black_hold"):    # F4: bloques del pico (F3) también en disperso
        b = plan.get(k)
        if b:
            iv.append((b["start"], b["start"] + b["duration"]))

    def _scene_end(t: float) -> float:
        return next((s.end for s in scenes if s.start <= t < s.end), dur)

    ez = plan.get("evidence_zoom")
    if ez and 0 <= ez["scene_idx"] < len(scenes):
        sc = scenes[ez["scene_idx"]]
        iv.append((ez.get("start", sc.end - gfx_rules.zoom_dur), sc.end))
    for s in scenes:                                           # F2 §4: movimiento seguro = escena entera en HF
        if s.safe:
            iv.append((s.start, s.end))
    for t in plan.get("punch_in", []):                        # el punch se sostiene hasta el corte
        iv.append((t, _scene_end(t)))
    for idx, tr in transitions_of(plan, scenes).items():
        st = scenes[idx].start
        d = max(tr["frames"] / fps, 0.35)                       # cut_punch dura .35 s
        iv.append((st - 1.5 / fps, st + d))                     # incluye el freeze del saliente
    iv = sorted((max(0.0, a - margin), min(dur, b + margin)) for a, b in iv if b > a)
    merged: list[list[float]] = []
    for a, b in iv:
        if merged and a - merged[-1][1] <= merge_gap:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return [(_frame(a, fps), _frame(b, fps)) for a, b in merged if b - a >= 2 / fps]


def compose_sparse(plan: dict[str, Any], scenes: list[GfxScene], windows: list[tuple[float, float]], fps: int
                   ) -> tuple[dict[str, Any], list[GfxScene], dict[int, dict[str, Any]], list[tuple[float, float, float]]]:
    """Plan + escenas + transiciones en el timeline CONCATENADO de ventanas.

    Devuelve (plan_s, scenes_s, transitions_s, offsets) con offsets = [(a, b, off)] → el instante t del
    cap dentro de la ventana [a, b) vive en off + (t − a) del render disperso.
    """
    offsets: list[tuple[float, float, float]] = []
    off = 0.0
    for a, b in windows:
        offsets.append((a, b, off))
        off = _frame(off + (b - a), fps)

    def m(t: float) -> float | None:
        for a, b, o in offsets:
            if a - 1e-6 <= t < b + 1e-6:
                return round(o + (t - a), 4)
        return None

    full_tr = transitions_of(plan, scenes)
    scenes_s: list[GfxScene] = []
    tr_s: dict[int, dict[str, Any]] = {}
    idx_map: dict[int, int] = {}
    for wi, (a, b, o) in enumerate(offsets):
        for s in scenes:
            lo, hi = max(s.start, a), min(s.end, b)
            if hi - lo < 1 / fps:
                continue
            k = len(scenes_s)
            scenes_s.append(GfxScene(k, round(o + lo - a, 4), round(o + hi - a, 4), s.rank, s.text_in_image, s.quiet_side,
                                     s.safe if (lo == s.start and hi == s.end) else None))
            idx_map.setdefault(s.idx, k)
            if k == 0:
                continue
            if lo == s.start and s.idx in full_tr:              # el corte real cae dentro de la ventana
                tr_s[k] = full_tr[s.idx]
            else:                                               # unión de ventanas o tramo interno: corte seco
                tr_s[k] = {"kind": "cut", "frames": 0, "rank": s.rank, "window_join": lo != s.start}

    p = copy.deepcopy(plan)
    p.pop("transitions", None)                                  # en disperso las manda tr_s (timeline concatenado)
    for k in ("water_level", "time_ticker", "black_hold"):     # F4: bloques del pico corridos al timeline disperso
        if p.get(k):
            p[k]["start"] = m(p[k]["start"])
            if p[k]["start"] is None:
                p[k] = None
    for c in p.get("callouts", []):
        c["start"] = m(c["start"])
    p["callouts"] = [c for c in p.get("callouts", []) if c["start"] is not None]
    if p.get("count_up"):
        p["count_up"]["start"] = m(p["count_up"]["start"])
    for ar in p.get("archive_clippings", []) or []:
        ar["start"] = m(ar["start"])
    if p.get("chapter_question"):
        p["chapter_question"]["start"] = m(p["chapter_question"]["start"])
    for e in p.get("emphasis", []) or []:
        e["start"] = m(e["start"])
    p["emphasis"] = [e for e in p.get("emphasis", []) or [] if e["start"] is not None]
    if p.get("icon_array"):
        p["icon_array"]["start"] = m(p["icon_array"]["start"])
        if p["icon_array"]["start"] is None:
            p["icon_array"] = None
    if p.get("evidence_zoom"):
        ez = p["evidence_zoom"]
        sc = scenes[ez["scene_idx"]]
        z0 = m(ez.get("start", sc.end - gfx_rules.zoom_dur))
        # la escena del zoom en el timeline disperso = la última porción de esa escena (la que contiene z0)
        k = next((s.idx for s in scenes_s if z0 is not None and s.start <= z0 < s.end), None)
        p["evidence_zoom"] = {**ez, "scene_idx": k, "start": z0} if k is not None else None
        if p["evidence_zoom"] and ez.get("latido_t") is not None:   # F4: el latido también se corre
            p["evidence_zoom"]["latido_t"] = m(ez["latido_t"])
    p["punch_in"] = [x for x in (m(t) for t in p.get("punch_in", [])) if x is not None]
    return p, scenes_s, tr_s, offsets


def cut_base(base: Path, windows: list[tuple[float, float]], out: Path, fps: int) -> None:
    """base_sparse.mp4 = concat exacto a frame de los tramos [a, b) del base (re-encode -g 30)."""
    parts = "".join(f"[0:v]trim=start={a:.6f}:end={b:.6f},setpts=PTS-STARTPTS[v{i}];" for i, (a, b) in enumerate(windows))
    graph = parts + "".join(f"[v{i}]" for i in range(len(windows))) + f"concat=n={len(windows)}:v=1:a=0[o]"
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(base), "-filter_complex", graph, "-map", "[o]",
                        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "14", "-r", str(fps), "-g", "30",
                        "-keyint_min", "30", "-pix_fmt", "yuv420p", "-an", str(out)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise RuntimeError(f"cut_base falló: {r.stderr[-300:]}")


def vignette_png(width: int, height: int, out: Path) -> Path:
    """La MISMA viñeta del CSS (radial-gradient ellipse 85% 85% at 50% 42%, 62 % → 100 %, negro .6)
    × opacidad del perfil, como PNG RGBA para un overlay de FFmpeg."""
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    # CSS: "ellipse 85% 85%" = radios 85 % del ancho y 85 % del alto; centro 50 % / 42 %
    r = np.sqrt(((x - 0.5 * width) / (0.85 * width)) ** 2 + ((y - 0.42 * height) / (0.85 * height)) ** 2)
    a = np.clip((r - 0.62) / 0.38, 0.0, 1.0) * 0.6 * gfx_rules.vignette_opacity
    rgba = np.zeros((height, width, 4), np.uint8)
    rgba[..., 3] = np.round(a * 255).astype(np.uint8)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{width}x{height}",
                    "-i", "-", str(out)], input=rgba.tobytes(), check=True, timeout=120)
    return out


GRAIN_SIGMA: float = 0.14     # calibrado: misma energía 2–4 px que el grano CSS (2.86× vs sin grano)
GRAIN_PAD: int = 360           # el CSS mueve el grano ±180 px
XFADE_FRAMES: int = 4          # nocturno §3: fundido de 4 cuadros en cada unión base ↔ ventana


def grain_png(width: int, height: int, out: Path, seed: int = 1441) -> Path:
    """Textura de grano gris (media 0.5) más grande que el cuadro, para recortarla saltando 12 veces/s."""
    rng = np.random.default_rng(seed)
    tex = np.clip(rng.normal(0.5, GRAIN_SIGMA, (height + GRAIN_PAD, width + GRAIN_PAD)), 0, 1)
    g = np.round(tex * 255).astype(np.uint8)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
                    "-s", f"{width + GRAIN_PAD}x{height + GRAIN_PAD}", "-i", "-", str(out)],
                   input=g.tobytes(), check=True, timeout=120)
    return out


def stitch(base: Path, hf: Path, windows: list[tuple[float, float]], offsets: list[tuple[float, float, float]],
           dur: float, out: Path, *, width: int, height: int, fps: int, vignette: Path | None,
           grain: Path | None, grain_opacity: float, crf: int = 16, bug: dict[str, Any] | None = None) -> None:
    """Cap final = tramos del base fuera de ventanas + tramos del render HF, y grade FFmpeg uniforme encima."""
    # Tramos en orden del cap. Nocturno §3: en cada unión base↔HF, fundido de XF cuadros; para eso los
    # tramos de BASE se extienden XF cuadros dentro de la ventana vecina (el HF queda exacto).
    xf = XFADE_FRAMES / fps
    pieces: list[tuple[str, float, float, float]] = []          # (fuente, start, end, inicio en el cap)
    t = 0.0
    for (a, b, o) in offsets:
        if a - t >= 1 / fps:
            pieces.append(("base", max(0.0, t - (xf if pieces else 0.0)), a + xf, max(0.0, t - (xf if pieces else 0.0))))
        pieces.append(("hf", o, o + (b - a), a))
        t = b
    if dur - t >= 1 / fps:
        pieces.append(("base", t - xf, dur, t - xf))
    graph = []
    for i, (src, s, e, _) in enumerate(pieces):
        inp = "0:v" if src == "base" else "1:v"
        graph.append(f"[{inp}]trim=start={s:.6f}:end={e:.6f},setpts=PTS-STARTPTS,fps={fps},format=yuv420p,settb=AVTB[p{i}]")
    last = "p0"
    for i in range(1, len(pieces)):
        src, s, e, at = pieces[i]
        # offset = instante del cap donde arranca el fundido (= inicio de la ventana, o b − XF al volver al base)
        off = at if src == "hf" else at
        graph.append(f"[{last}][p{i}]xfade=transition=fade:duration={xf:.6f}:offset={off:.6f}[x{i}]")
        last = f"x{i}"
    if vignette is not None:
        graph.append(f"[2:v]format=rgba[vg];[{last}][vg]overlay=0:0:format=auto[g1]")
        last = "g1"
    if grain is not None and grain_opacity > 0:
        # grano = la textura en blend overlay a la opacidad del perfil, saltando de posición
        # grain_jumps_per_sec veces por segundo (igual que el CSS), uniforme en todo el cap
        gi = 3 if vignette is not None else 2
        j = gfx_rules.grain_jumps_per_sec
        # blend solo en luma (textura gris): mismo resultado visual que el overlay RGB y ~3× más rápido
        graph.append(f"[{gi}:v]crop={width}:{height}:x='mod(floor(t*{j})*137,{GRAIN_PAD})':"
                     f"y='mod(floor(t*{j})*89,{GRAIN_PAD})',format=yuv420p[gt];"
                     f"[{last}]format=yuv420p[gb];[gb][gt]blend=c0_mode=overlay:c0_opacity={grain_opacity:.3f}:"
                     f"shortest=1[g2]")   # c1/c2 por default (normal, 1) = croma intacto
        last = "g2"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(base), "-i", str(hf)]
    if vignette is not None:
        cmd += ["-loop", "1", "-framerate", str(fps), "-i", str(vignette)]
    if grain is not None and grain_opacity > 0:
        cmd += ["-loop", "1", "-framerate", str(fps), "-i", str(grain)]
    if bug:                                                     # F4b §0.3: marca del canal (+ cierre en el último cap)
        from script_engine import gfx_bug
        n_in = 2 + (vignette is not None) + (grain is not None and grain_opacity > 0)

        def _inp(p: Path | None) -> int | None:
            nonlocal n_in
            if p is None:
                return None
            cmd.extend(["-loop", "1", "-framerate", str(fps), "-i", str(p)])
            n_in += 1
            return n_in - 1
        cfg = bug["cfg"]
        if bug.get("corner", True):
            ib, ifl = _inp(bug["corner_pngs"][0]), _inp(bug["corner_pngs"][1])
            g, last = gfx_bug.overlay_graph(cfg, bug["plan"], bug.get("visible_until", dur), width=width, height=height,
                                            in_body=ib, in_flame=ifl, last=last, intro=bug.get("intro", False))
            graph.extend(g)
        if bug.get("outro_t0") is not None:
            ob, ofl = _inp(bug["outro_pngs"][0]), _inp(bug["outro_pngs"][1])
            g, last = gfx_bug.outro_graph(cfg, bug["outro_t0"], width=width, height=height, in_body=ob, in_flame=ofl,
                                          last=last)
            graph.extend(g)
    graph.append(f"[{last}]format=yuv420p[o]")
    cmd += ["-filter_complex", ";".join(graph), "-map", "[o]", "-t", f"{dur:.6f}", "-c:v", "libx264",
            "-preset", "ultrafast", "-crf", str(crf), "-r", str(fps), "-pix_fmt", "yuv420p", "-an", str(out)]   # intermedio: fase2b re-encodea
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise RuntimeError(f"stitch falló: {r.stderr[-400:]}")
