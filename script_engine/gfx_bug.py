"""
gfx_bug.py — Marca del canal (`channel_bug`, F4b §0.3): el encapuchado con farol en la esquina superior izquierda.

Sale SOLO del perfil (`channel_bug` en gfx_profiles/<canal>.json; sin esa clave o enabled=false → no hay marca).
Se compone en el COSIDO FFmpeg del render disperso (gfx_sparse.stitch), no en HyperFrames: así está en todo el cap
(también en los tramos que no pasan por HyperFrames) sin re-renderizar nada.

    pngs()          silueta (hueso) + llama (cálida) rasterizadas desde el SVG elegido, por alto en px (cache)
    hide_windows()  intervalos del cap donde la marca NO se ve: título, pregunta + negro, nivel de agua y todo bloque
                    que cae en el lado izquierdo de arriba (la esquina de la marca); entra/sale con fade de 0.3 s
    overlay_graph() filtros FFmpeg: opacidad 0.55 × visibilidad(t); entrada del video (solo ch01): la silueta aparece
                    en 0.8 s y la llama se enciende 0.5 s después; parpadeo leve de la llama (0.4 s) cada 90 s del cap
    outro_graph()   cierre del video (último cap): 2.5 s el encapuchado al centro (25 % de alto), la llama parpadea y
                    se apaga → negro 1 s. Sin texto.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from gfx_config import ACTIVE_PROFILE, GFX_PROFILES_DIR, gfx_rules

FADE = 0.3


def config(profile: dict[str, Any] | None = None) -> dict[str, Any] | None:
    cb = (profile if profile is not None else ACTIVE_PROFILE).get("channel_bug") or {}
    if not cb.get("enabled") or not cb.get("svg"):
        return None
    svg = GFX_PROFILES_DIR / cb["svg"]
    if not svg.exists():
        return None
    return {"svg": svg, "height_frac": float(cb.get("height_frac", 0.04)), "opacity": float(cb.get("opacity", 0.55)),
            "margin_x_frac": float(cb.get("margin_x_frac", 0.03)), "margin_y_frac": float(cb.get("margin_y_frac", 0.035)),
            "flicker_every_sec": float(cb.get("flicker_every_sec", 90.0)), "intro_sec": float(cb.get("intro_sec", 0.8)),
            "flame_delay_sec": float(cb.get("flame_delay_sec", 0.5)), "outro_sec": float(cb.get("outro_sec", 2.5)),
            "outro_black_sec": float(cb.get("outro_black_sec", 1.0)),
            "outro_height_frac": float(cb.get("outro_height_frac", 0.25))}


def pngs(cfg: dict[str, Any], px: int, out_dir: Path, *, corner: bool = False) -> tuple[Path, Path | None]:
    """(silueta.png, llama.png | None) RGBA de px×px. Cacheados por SVG + tamaño + versión.
    corner=True (pedido de Omar 2026-10-20): trazos de la silueta engrosados `corner_dilate_px` (a 6 % de alto el
    grabado fino se perdía) y halo suave alrededor de la llama. El cierre va tal cual (corner=False)."""
    import hashlib
    from PIL import Image, ImageFilter
    from script_engine.gfx_icons.make_bug import render_svg
    svg = cfg["svg"].read_text(encoding="utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    dil = int(cfg.get("corner_dilate_px", 2)) if corner else 0
    halo = bool(cfg.get("flame_halo", True)) and corner
    stem = f"{cfg['svg'].stem}_{hashlib.sha1(svg.encode()).hexdigest()[:8]}_{px}_{'esq' if corner else 'cie'}"
    body_p, flame_p = out_dir / f"{stem}_body.png", out_dir / f"{stem}_flame.png"
    has_flame = '<g id="flame"' in svg
    if not body_p.exists():
        body_svg = re.sub(r'<g id="flame".*?</g>', "", svg, flags=re.S)
        im = render_svg(body_svg, px, out_dir / f"{stem}_body_raw.png")
        if dil:
            a = im.getchannel("A").filter(ImageFilter.MaxFilter(2 * dil + 1))
            im = Image.new("RGBA", im.size, (232, 224, 204, 0))
            im.putalpha(a)
        im.save(body_p)
    if has_flame and not flame_p.exists():
        flame_only = re.sub(r'<path class="ic-fill"[^>]*/>', "", svg)
        flame_only = re.sub(r'<g class="ic-strokes".*?</g>', "", flame_only, flags=re.S)
        fl = render_svg(flame_only, px, out_dir / f"{stem}_flame_raw.png")
        if halo:
            r = max(2.0, px * float(cfg.get("flame_halo_frac", 0.07)))
            glow_a = fl.getchannel("A").filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(r))
            glow = Image.new("RGBA", fl.size, (232, 168, 74, 0))
            glow.putalpha(glow_a.point(lambda v: int(min(255, v * 1.6 * 0.55))))
            fl = Image.alpha_composite(glow, fl)
        fl.save(flame_p)
    return body_p, (flame_p if has_flame else None)


def hide_windows(plan: dict[str, Any], clip_dur: float) -> list[tuple[float, float]]:
    """Intervalos (cap) donde la marca se esconde."""
    iv: list[tuple[float, float]] = []
    if plan.get("title_card"):
        iv.append((0.0, gfx_rules.title_dur + 0.2))
    for k in ("chapter_question", "black_hold", "water_level", "outro_bug"):
        b = plan.get(k)
        if b:
            iv.append((b["start"], b["start"] + b["duration"]))
    for c in plan.get("callouts") or []:                       # bloques arriba a la izquierda = la esquina de la marca
        if c.get("side", "left") == "left":
            iv.append((c["start"], c["start"] + float(c.get("duration", gfx_rules.callout_dur))))
    for a in plan.get("archive_clippings") or []:
        if a.get("side", "left") == "left":
            iv.append((a["start"], a["start"] + a["duration"]))
    cu = plan.get("count_up")
    if cu:
        iv.append((cu["start"], cu["start"] + gfx_rules.count_dur + gfx_rules.count_hold_sec))
    tk = plan.get("time_ticker")
    if tk and tk.get("side", "left") == "left":
        iv.append((tk["start"], tk["start"] + tk["duration"]))
    for e in plan.get("emphasis") or []:
        if e.get("icon_callout") and e.get("side") == "left" and e.get("zone_v", "top") == "top":
            iv.append((e["start"], e["start"] + e["duration"]))
    iv = sorted((max(0.0, a), min(clip_dur, b)) for a, b in iv if b > a)
    merged: list[list[float]] = []
    for a, b in iv:
        if merged and a <= merged[-1][1] + 2 * FADE:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return [(round(a, 3), round(b, 3)) for a, b in merged]


def visibility_expr(windows: list[tuple[float, float]]) -> str:
    """Expresión FFmpeg de visibilidad 0–1 en T (1 fuera de las ventanas, rampas de FADE s)."""
    terms = [f"max(clip(({a:.3f}-T)/{FADE},0,1),clip((T-{b:.3f})/{FADE},0,1))" for a, b in windows]
    return "*".join(terms) if terms else "1"


def overlay_graph(cfg: dict[str, Any], plan: dict[str, Any], clip_dur: float, *, width: int, height: int,
                  in_body: int, in_flame: int | None, last: str, intro: bool) -> tuple[list[str], str]:
    """Filtros que superponen la marca sobre `last`. Devuelve (filtros, etiqueta de salida)."""
    vis = visibility_expr(hide_windows(plan, clip_dur))
    op = cfg["opacity"]
    i0, fd = cfg["intro_sec"], cfg["flame_delay_sec"]
    body_a = f"{op}*({vis})" + (f"*clip(T/{i0},0,1)" if intro else "")
    every = cfg["flicker_every_sec"]
    # parpadeo: 0.4 s cada `every` s del cap (primero a la mitad del período) → la llama baja a 35 % y vuelve
    flick = f"(1-0.65*between(mod(T+{every / 2:.1f},{every:.1f}),0,0.4)*sin(PI*mod(T+{every / 2:.1f},{every:.1f})/0.4))"
    flame_a = f"{op}*({vis})*{flick}" + (f"*clip((T-{i0 + fd})/0.25,0,1)" if intro else "")
    x, y = int(width * cfg["margin_x_frac"]), int(height * cfg["margin_y_frac"])
    g = [f"[{in_body}:v]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*{body_a}'[bgb]",
         f"[{last}][bgb]overlay={x}:{y}:format=auto[bg1]"]
    out = "bg1"
    if in_flame is not None:
        g += [f"[{in_flame}:v]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*{flame_a}'[bgf]",
              f"[{out}][bgf]overlay={x}:{y}:format=auto[bg2]"]
        out = "bg2"
    return g, out


def outro_graph(cfg: dict[str, Any], t0: float, *, width: int, height: int, in_body: int, in_flame: int | None,
                last: str) -> tuple[list[str], str]:
    """Cierre del video desde t0: negro + encapuchado al centro 2.5 s (la llama parpadea y se apaga) → negro 1 s."""
    d, k = cfg["outro_sec"], int(height * cfg["outro_height_frac"])
    t1, t2 = t0 + d, t0 + d + cfg["outro_black_sec"]
    x, y = (width - k) // 2, (height - k) // 2
    body_a = f"between(T,{t0:.3f},{t1:.3f})*clip((T-{t0:.3f})/0.6,0,1)*clip(({t1:.3f}-T)/0.5,0,1)"
    # la llama: parpadeo irregular y se apaga del todo 0.6 s antes de que se vaya la silueta
    flame_a = (f"between(T,{t0:.3f},{t1:.3f})*clip((T-{t0 + 0.4:.3f})/0.3,0,1)*clip(({t1 - 0.6:.3f}-T)/0.25,0,1)"
               f"*(0.75+0.25*sin(23*T)*sin(7*T))")
    g = [f"color=c=black:s={width}x{height}:r=30[blk]",
         f"[{last}][blk]overlay=0:0:enable='between(t,{t0:.3f},{t2:.3f})'[ob0]",
         f"[{in_body}:v]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*{body_a}'[obb]",
         f"[ob0][obb]overlay={x}:{y}:format=auto[ob1]"]
    out = "ob1"
    if in_flame is not None:
        g += [f"[{in_flame}:v]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*{flame_a}'[obf]",
              f"[{out}][obf]overlay={x}:{y}:format=auto[ob2]"]
        out = "ob2"
    return g, out


def burn_on_clip(clip: Path, plan: dict[str, Any], out: Path, *, cap: str, last_cap: bool, width: int, height: int,
                 fps: int, png_dir: Path, cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Cose la marca sobre una capa gfx YA renderizada (chNN_gfx.mp4), sin HyperFrames (pedido de Omar 2026-10-20:
    «cosé la marca en el final sin re-render»). En el último cap agrega el cierre (alarga el clip outro + negro).
    Devuelve {"pause": s agregados, "hide": ventanas}. Mismos filtros que el cosido del render disperso."""
    import subprocess
    cfg = cfg or config()
    if cfg is None:
        raise ValueError("channel_bug apagado en el perfil")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(clip)],
                               capture_output=True, text=True).stdout)
    pause = cfg["outro_sec"] + cfg["outro_black_sec"] if last_cap else 0.0
    plan = dict(plan)
    if last_cap:
        plan["outro_bug"] = {"start": round(dur, 3), "duration": round(pause, 3)}
    cb, cf = pngs(cfg, int(height * cfg["height_frac"]), png_dir, corner=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(clip)]
    inputs = [cb, cf]
    if last_cap:
        inputs += list(pngs(cfg, int(height * cfg["outro_height_frac"]), png_dir))
    for p in inputs:
        if p is not None:
            cmd += ["-loop", "1", "-framerate", str(fps), "-i", str(p)]
    idx, n = [], 1
    for p in inputs:
        idx.append(n if p is not None else None)
        n += p is not None
    graph = [f"[0:v]tpad=stop_mode=clone:stop_duration={pause:.3f},format=yuv420p[v0]" if pause else "[0:v]format=yuv420p[v0]"]
    g, last = overlay_graph(cfg, plan, dur + pause, width=width, height=height, in_body=idx[0], in_flame=idx[1],
                            last="v0", intro=cap == "ch01")
    graph += g
    if last_cap:
        g, last = outro_graph(cfg, dur, width=width, height=height, in_body=idx[2], in_flame=idx[3], last=last)
        graph += g
    graph.append(f"[{last}]format=yuv420p[o]")
    cmd += ["-filter_complex", ";".join(graph), "-map", "[o]", "-t", f"{dur + pause:.6f}", "-c:v", "libx264",
            "-preset", "ultrafast", "-crf", "16", "-r", str(fps), "-pix_fmt", "yuv420p", "-an", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if r.returncode != 0:
        raise RuntimeError(f"burn_on_clip {cap}: {r.stderr[-400:]}")
    return {"pause": pause, "hide": hide_windows(plan, dur + pause), "dur": dur}
