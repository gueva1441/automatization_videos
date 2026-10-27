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
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from gfx_config import gfx_rules
from script_engine.gfx_project import GfxScene, archive_list, transitions_of


def _frame(t: float, fps: int) -> float:
    return round(round(t * fps) / fps, 6)


def transition_span(c: float, tr: dict[str, Any], fps: int) -> tuple[float, float]:
    """Lo que ocupa una transición alrededor de su corte c (incluye el último cuadro del saliente). F30b: el zoom_punch
    ocupa la mitad antes del corte (el saliente se acerca) y la mitad después (el entrante se aleja)."""
    if tr["kind"] == "zoom_punch":
        h = (tr["frames"] // 2) / fps
        return c - h - 1.5 / fps, c + h
    return c - 1.5 / fps, c + max(tr["frames"] / fps, 0.35)          # cut_punch dura .35 s


def event_windows(plan: dict[str, Any], scenes: list[GfxScene], fps: int, dur: float, *,
                  margin: float = 0.5, merge_gap: float = 2.0, safe_windows: bool = False,
                  transition_windows: bool = False) -> list[tuple[float, float]]:
    """Intervalos [a, b) del cap que necesitan HyperFrames, alineados a frame.

    F30 §B: las transiciones ya no abren ventana (las hace `stitch` con ffmpeg), salvo la que toca una ventana de
    bloque (o queda sin aire para su fundido): esa entra a la ventana y la sigue dibujando HyperFrames, como siempre.
    `transition_windows=True` vuelve al camino de antes (una ventana por transición)."""
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
    for k in ("water_level", "time_ticker", "black_hold", "quote_card"):   # F4: bloques del pico; F5f: cita
        b = plan.get(k)
        if b:
            iv.append((b["start"], b["start"] + b["duration"]))

    def _scene_end(t: float) -> float:
        return next((s.end for s in scenes if s.start <= t < s.end), dur)

    ez = plan.get("evidence_zoom")
    if ez and 0 <= ez["scene_idx"] < len(scenes):
        sc = scenes[ez["scene_idx"]]
        iv.append((ez.get("start", sc.end - gfx_rules.zoom_dur), sc.end))
    # F30 §A: la escena safe ya está cocida en el base (gfx_safe_bake) → no abre ventana. Solo sin bake
    # (gfx_rules.safe_bake apagado) vuelve el camino de F2 §4: la escena entera en HF
    for s in scenes if safe_windows else ():
        if s.safe:
            iv.append((s.start, s.end))
    for t in plan.get("punch_in", []):                        # el punch se sostiene hasta el corte
        iv.append((t, _scene_end(t)))
    trs = sorted((scenes[idx].start, idx, tr) for idx, tr in transitions_of(plan, scenes).items())
    dentro = {idx for _, idx, _ in trs} if transition_windows else set()

    def _windows() -> list[tuple[float, float]]:
        ivs = iv + [transition_span(c, tr, fps) for c, idx, tr in trs if idx in dentro]
        ivs = sorted((max(0.0, a - margin), min(dur, b + margin)) for a, b in ivs if b > a)

        def _merge(gap: float) -> list[list[float]]:
            out: list[list[float]] = []
            for a, b in ivs:
                if out and a - out[-1][1] <= gap:
                    out[-1][1] = max(out[-1][1], b)
                else:
                    out.append([a, b])
            return out
        merged = _merge(merge_gap)
        # F10 B1: si la fusión deja (casi) todo el cap en UNA ventana, el cap entero pasa por HyperFrames y el clip de
        # base se congela (ch05 de Orleans, 100 %). Se vuelve a cortar fusionando solo lo que se pisa: los tramos sin
        # eventos salen del base, con su movimiento.
        if dur > 0 and sum(b - a for a, b in merged) >= FULL_COVER_FRAC * dur and len(merged) <= 1 and merge_gap > 0:
            merged = _merge(0.0)
        return [(_frame(a, fps), _frame(b, fps)) for a, b in merged if b - a >= 2 / fps]
    # F30 §B: una transición que toca una ventana (con su margen) o que no tiene aire para su fundido (otro corte, el
    # final del cap) entra a la ventana; se repite hasta que no cambia nada (una ventana que crece toca otras)
    while True:
        win = _windows()
        fuera = [(c, idx, tr) for c, idx, tr in trs if idx not in dentro]
        nuevos = set()
        for k, (c, idx, tr) in enumerate(fuera):
            lo, hi = transition_span(c, tr, fps)
            lo, hi = lo - margin, hi + margin
            sig = fuera[k + 1][0] if k + 1 < len(fuera) else dur
            ant = fuera[k - 1][0] if k > 0 else 0.0
            sin_aire = sig - c < max(tr["frames"] / fps, 0.35) + 2 / fps or c - ant < 2 / fps
            if sin_aire or any(lo < b and hi > a for a, b in win):
                nuevos.add(idx)
        if not nuevos:
            return win
        dentro |= nuevos


def stitch_transitions(plan: dict[str, Any], scenes: list[GfxScene], windows: list[tuple[float, float]]
                       ) -> list[tuple[float, dict[str, Any]]]:
    """F30 §B.3: las transiciones que aplica `stitch` = las de corte fuera de toda ventana [a, b) (las de adentro las
    dibuja HyperFrames: nunca dos veces). Los cortes `cut` también van (concat seco)."""
    out = []
    for idx, tr in sorted(transitions_of(plan, scenes).items()):
        c = scenes[idx].start
        if not any(a - 1e-6 <= c < b + 1e-6 for a, b in windows):
            out.append((round(c, 6), {**tr, "scene_idx": idx}))
    return out


FULL_COVER_FRAC = 0.95


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
    for k in ("water_level", "time_ticker", "black_hold", "quote_card"):   # F4 / F5f: corridos al timeline disperso
        if p.get(k):
            p[k]["start"] = m(p[k]["start"])
            if p[k]["start"] is None:
                p[k] = None
    if p.get("time_ticker"):                                   # F5f: los cambios de fecha también se corren
        p["time_ticker"]["changes"] = [{**c, "t": m(c["t"])} for c in p["time_ticker"].get("changes") or []
                                       if m(c["t"]) is not None]
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


def stitch_segments(windows_offsets: list[tuple[float, float, float]], dur: float, fps: int,
                    transitions: list[tuple[float, dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """El cap cuadro a cuadro, en segmentos que no se pisan (todo en cuadros enteros, [k0, k1)):
        base       el base tal cual                       hf        el render HF tal cual (cuadros [h0, h1))
        xf_in      unión base → HF: fundido de XF cuadros (nocturno §3; el mismo xfade de antes, en su tramo)
        xf_out     unión HF → base
        dissolve   el último cuadro del saliente congelado se funde sobre el entrante (el freeze del templater)
        dip_out    el último cuadro del saliente congelado baja a negro en d/2 · dip_in: el entrante sube desde negro
        flash      el entrante con el blanco por cuadro · punch: el entrante de r1_cut_punch_scale a 1 en .35 s
        zp_out     (F30b, zoom_punch) el saliente se acerca 1 → 1.4 en la mitad antes del corte · zp_in: el entrante
                   se aleja 1.4 → 1 en la mitad después
    F30 §B: antes los tramos se unían con una cadena de xfade (uno por unión: con 15 ventanas el stitch de ch06 pasó de
    50 a 135 s); ahora cada fundido es un segmento corto y todo va a UN concat."""
    D = round(dur * fps)
    wins = [(round(a * fps), round(b * fps), round(o * fps)) for a, b, o in windows_offsets]
    cuts = sorted((round(c * fps), tr) for c, tr in transitions or [])
    segs: list[dict[str, Any]] = []

    def base_tramo(k0: int, k1: int) -> None:
        k = k0
        for c, tr in cuts:
            if not (k0 < c < k1):
                continue
            if tr["kind"] == "zoom_punch":                       # F30b §A: mitad antes del corte, mitad después
                h = tr["frames"] // 2
                a = max(k, c - h)
                if a > k:
                    segs.append({"kind": "base", "k0": k, "k1": a})
                if c > a:
                    segs.append({"kind": "zp_out", "k0": a, "k1": c})
                e = min(c + h, k1)
                segs.append({"kind": "zp_in", "k0": c, "k1": e})
                k = e
                continue
            if c > k:
                segs.append({"kind": "base", "k0": k, "k1": c})
            n = {"dissolve": tr["frames"], "dip": tr["frames"], "flash": tr["frames"],
                 "cut_punch": math.ceil(0.35 * fps)}.get(tr["kind"], 0)
            n = min(n, k1 - c)
            if tr["kind"] == "dip":
                h = n // 2
                segs.append({"kind": "dip_out", "k0": c, "k1": c + h, "freeze": c - 1})
                segs.append({"kind": "dip_in", "k0": c + h, "k1": c + n})
            elif n:
                segs.append({"kind": {"cut_punch": "punch"}.get(tr["kind"], tr["kind"]), "k0": c, "k1": c + n,
                             "freeze": c - 1, "frames": tr["frames"]})
            k = c + n
        if k1 > k:
            segs.append({"kind": "base", "k0": k, "k1": k1})

    k = 0
    for a, b, o in wins:
        if a > k:
            base_tramo(k, a)
        x_in = XFADE_FRAMES if a > 0 else 0
        x_out = XFADE_FRAMES if b < D else 0
        if x_in:
            segs.append({"kind": "xf_in", "k0": a, "k1": a + x_in, "h0": o})
        if b - x_out > a + x_in:
            segs.append({"kind": "hf", "k0": a + x_in, "k1": b - x_out, "h0": o + x_in})
        if x_out:
            segs.append({"kind": "xf_out", "k0": b - x_out, "k1": b, "h0": o + (b - a) - x_out})
        k = b
    if D > k:
        base_tramo(k, D)
    return segs


def _flash_alphas(frames: int, fps: int) -> list[float]:
    """Opacidad del blanco por cuadro, igual que el templater: 0 → flash_peak en d/3 (lineal) y → 0 en 2d/3
    (power1.in)."""
    d, pk = frames / fps, gfx_rules.flash_peak
    out = []
    for k in range(frames):
        t = k / fps
        out.append(pk * t / (d / 3) if t < d / 3 else pk * (1 - ((t - d / 3) / (2 * d / 3)) ** 2))
    return out


def stitch_graph(segs: list[dict[str, Any]], fps: int, width: int, height: int) -> tuple[list[str], str]:
    """(filtros, etiqueta final): un trim por cuadros por segmento, los fundidos dentro de su segmento y UN concat."""
    pre = "setpts=PTS-STARTPTS,fps={fps},format=yuv420p,settb=AVTB".format(fps=fps)

    def b(k0: int, k1: int, lab: str, extra: str = "") -> str:
        return f"[0:v]trim=start_frame={k0}:end_frame={k1},{pre}{extra}[{lab}]"

    def h(k0: int, k1: int, lab: str) -> str:
        return f"[1:v]trim=start_frame={k0}:end_frame={k1},{pre}[{lab}]"

    def congelado(k: int, n: int, lab: str, extra: str = "") -> str:
        return f"[0:v]trim=start_frame={k}:end_frame={k + 1},{pre},tpad=stop_mode=clone:stop={n - 1}{extra}[{lab}]"
    g: list[str] = []
    labs: list[str] = []
    for i, s in enumerate(segs):
        n, lab = s["k1"] - s["k0"], f"s{i}"
        kd = s["kind"]
        if kd == "base":
            g.append(b(s["k0"], s["k1"], lab))
        elif kd == "hf":
            g.append(h(s["h0"], s["h0"] + n, lab))
        elif kd in ("xf_in", "xf_out"):
            first, second = (b(s["k0"], s["k1"], f"{lab}a"), h(s["h0"], s["h0"] + n, f"{lab}b")) if kd == "xf_in" else \
                (h(s["h0"], s["h0"] + n, f"{lab}a"), b(s["k0"], s["k1"], f"{lab}b"))
            g += [first, second, f"[{lab}a][{lab}b]xfade=transition=fade:duration={n / fps:.6f}:offset=0[{lab}]"]
        elif kd == "dissolve":
            g += [congelado(s["freeze"], n, f"{lab}a"), b(s["k0"], s["k1"], f"{lab}b"),
                  f"[{lab}a][{lab}b]xfade=transition=fade:duration={n / fps:.6f}:offset=0[{lab}]"]
        elif kd == "dip_out":
            g.append(congelado(s["freeze"], n, lab, f",fade=t=out:st=0:d={n / fps:.6f}"))
        elif kd == "dip_in":
            g.append(b(s["k0"], s["k1"], lab, f",fade=t=in:st=0:d={n / fps:.6f}"))
        elif kd == "flash":
            boxes = "".join(f",drawbox=x=0:y=0:w=iw:h=ih:color=white@{a:.4f}:t=fill:enable='eq(n\\,{k})'"
                            for k, a in enumerate(_flash_alphas(n, fps)) if a > 0)
            g.append(b(s["k0"], s["k1"], lab, boxes))
        elif kd == "punch":
            S = gfx_rules.r1_cut_punch_scale
            z = f"{S}-{S - 1:.6f}*(1-pow(1-min(in/{0.35 * fps:.6f}\\,1)\\,2))"
            g.append(b(s["k0"], s["k1"], lab, f",zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:"
                                             f"s={width}x{height}:fps={fps},setsar=1,setpts=PTS-STARTPTS,settb=AVTB"))
        elif kd in ("zp_out", "zp_in"):                        # F30b §A: zoom_punch (transition_config)
            from script_engine.gfx_style import ZOOM_PUNCH_SCALE as S
            x = f"min((in+1)/{n}\\,1)"
            z = (f"1+{S - 1:.6f}*pow({x}\\,2)" if kd == "zp_out" else
                 f"{S}-{S - 1:.6f}*(1-pow(1-min(in/{n}\\,1)\\,2))")
            g.append(b(s["k0"], s["k1"], lab, f",zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:"
                                             f"s={width}x{height}:fps={fps},setsar=1,setpts=PTS-STARTPTS,settb=AVTB"))
        labs.append(f"[{lab}]")
    g.append("".join(labs) + f"concat=n={len(labs)}:v=1:a=0[cat]")
    return g, "cat"


def stitch(base: Path, hf: Path, windows: list[tuple[float, float]], offsets: list[tuple[float, float, float]],
           dur: float, out: Path, *, width: int, height: int, fps: int, vignette: Path | None,
           grain: Path | None, grain_opacity: float, crf: int = 16,
           transitions: list[tuple[float, dict[str, Any]]] | None = None, encoder: list[str] | None = None) -> None:
    """Cap final = tramos del base fuera de ventanas + tramos del render HF, y grade FFmpeg uniforme encima. F30 §B:
    `transitions` = las transiciones de corte que caen fuera de las ventanas (stitch_transitions): el base se corta en
    sus cortes y cada unión lleva la suya. F30 §C.2: `encoder` (p. ej. NVENC) en vez de libx264 ultrafast."""
    graph, last = stitch_graph(stitch_segments(offsets, dur, fps, transitions), fps, width, height)
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
    graph.append(f"[{last}]format=yuv420p[o]")
    enc = encoder or ["-c:v", "libx264", "-preset", "ultrafast", "-crf", str(crf)]   # intermedio: fase2b re-encodea
    cmd += ["-filter_complex", ";".join(graph), "-map", "[o]", "-t", f"{dur:.6f}", *enc, "-r", str(fps),
            "-pix_fmt", "yuv420p", "-an", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0 and encoder:                           # F30 §C.2: sin NVENC (otra máquina) → libx264
        i = cmd.index(enc[0])
        cmd[i:i + len(enc)] = ["-c:v", "libx264", "-preset", "ultrafast", "-crf", str(crf)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise RuntimeError(f"stitch falló: {r.stderr[-400:]}")
