"""
gfx_layer.py — Orquestador de la capa gráfica HyperFrames por capítulo (fase2b --gfx).

DOC_MAESTRO_HyperFrames §2 (D2): se inserta en fase2b._build_chapter_segment DESPUÉS de
resolver base_clip y ANTES de quemar subs + pegar audio. Pasos:
  1. re-encode base_clip -g 30 → work_dir/gfx_chXX/public/base.mp4      (D11)
  2. grade: capas CSS de identidad en la composición (desvío de D4: la pasada media-treatment
     sobre el footage costó 6.29× tiempo real en F1 paso 1; el preset nativo queda versionado)
  3. gfx_plan = gfx_director (cache work_dir/gfx_plan_chXX.json)
  4. gfx_literal_lock(plan) → bloques rechazados se QUITAN, nunca se reescriben (D7)
  5. templater (gfx_project) → proyecto HyperFrames en work_dir/gfx_chXX/
  6. hyperframes lint (0 errores) → render draft|looks → work_dir/chXX_gfx.mp4 (sin audio)
  7. CUALQUIER excepción → return base_clip (+ error_handler.log_warning)

Todo queda en work_dir/gfx_chXX.log (tiempos y resultado por paso).
"""
from __future__ import annotations

import json
import math
import subprocess
import time
from pathlib import Path
from typing import Any

from error_handler import error_handler, PipelineStage
from gfx_config import (
    browser_env,
    clamp_quality,
    gfx_render,
    gfx_rules,
    hyperframes_cli,
    resolve_node,
)
from anchor_timing import compute_anchor_starts
from subs_remap import remap_words_to_original

from script_engine.gfx_project import GfxScene, write_project

_DOCTOR_DONE: bool = False                      # `hyperframes doctor` 1 vez por corrida


class GfxError(RuntimeError):
    """Falla de la capa gráfica (siempre termina en fallback a base_clip)."""


# ═══════════════════════════════════════════════════════════════
#  Subprocess helpers (shell=False, UTF-8 forzado)
# ═══════════════════════════════════════════════════════════════

def _run(cmd: list[str], *, timeout: int, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, cwd=str(cwd) if cwd else None, env=browser_env(), shell=False)


def _hf(args: list[str], *, timeout: int, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Invoca el CLI pineado: node <runtime>/hyperframes.mjs <args>."""
    node = resolve_node()
    cli = hyperframes_cli()
    if node is None:
        raise GfxError("node no encontrado (PATH ni gfx_render.node_dir)")
    if not cli.exists():
        raise GfxError(f"CLI hyperframes no instalado en {cli} (npm install en script_engine/gfx_runtime)")
    return _run([node, str(cli), *args], timeout=timeout, cwd=cwd)


def _ffprobe_duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, timeout=60)
    return float(r.stdout.strip())


# ═══════════════════════════════════════════════════════════════
#  Pasos
# ═══════════════════════════════════════════════════════════════

def _doctor_once(log: list[str]) -> None:
    """`hyperframes doctor` una vez por corrida (informativo, no bloquea)."""
    global _DOCTOR_DONE
    if _DOCTOR_DONE:
        return
    _DOCTOR_DONE = True
    try:
        r = _hf(["doctor"], timeout=120)
        lines = [ln.strip() for ln in r.stdout.splitlines() if "Chrome" in ln or "FFmpeg" in ln or "Version" in ln]
        log.append("doctor: " + " | ".join(lines[:4]))
    except Exception as e:  # noqa: BLE001 — doctor es informativo
        log.append(f"doctor falló: {e}")


def _reencode(base_clip: Path, out: Path, fps: int) -> None:
    """Paso 1 (D11): keyframe cada 30 frames para que el seek del render no congele."""
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(base_clip), "-an", "-c:v", "libx264",
           "-preset", gfx_render.reencode_preset, "-crf", str(gfx_render.reencode_crf),
           "-r", str(fps), "-g", str(gfx_render.reencode_gop), "-keyint_min", str(gfx_render.reencode_gop),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out.exists():
        raise GfxError(f"re-encode falló: {r.stderr[-300:]}")


def _lint(project: Path) -> dict[str, Any]:
    r = _hf(["lint", str(project), "--json"], timeout=180)
    data = json.loads(r.stdout)
    if int(data.get("errorCount", 1)) > 0:
        codes = sorted({f.get("code", "?") for f in data.get("findings", []) if f.get("severity") == "error"})
        raise GfxError(f"lint con {data['errorCount']} error(es): {codes}")
    return data


def _render(project: Path, out: Path, quality: str) -> None:
    timeout = gfx_render.timeout_sec
    cmd = ["render", str(project), "-o", str(out), "--quality", quality, "--workers", str(gfx_render.workers),
           "--player-ready-timeout", str(gfx_render.player_ready_timeout_ms),
           "--protocol-timeout", str(gfx_render.protocol_timeout_ms), "--quiet"]
    try:
        r = _hf(cmd, timeout=timeout, cwd=project)
    except subprocess.TimeoutExpired as e:
        raise GfxError(f"render excedió timeout {timeout}s") from e
    if r.returncode != 0 or not out.exists():
        raise GfxError(f"render rc={r.returncode}: {(r.stderr or r.stdout)[-400:]}")


# ═══════════════════════════════════════════════════════════════
#  Escenas del cap (cortes intra-cap)
# ═══════════════════════════════════════════════════════════════

def build_scenes(chplan: Any, script_chapter: dict[str, Any], raw_words: list[dict],
                 clip_duration: float, time_offset: float = 0.0) -> list[GfxScene]:
    """Cortes intra-cap desde compute_anchor_starts (importado). Un solo plano si algo no cuadra.

    El adelanto de ~45 ms del corte real vs anchor NO se corrige en F1 (anotado en DOC_MAESTRO §6).
    """
    single = [GfxScene(0, 0.0, clip_duration, "R3", "")]
    try:
        if chplan.engine == "flux":
            prompts = script_chapter.get("image_prompts") or []
            anchors = chplan.narration_anchors or [p.get("narration_anchor", "") for p in prompts]
            starts = compute_anchor_starts(anchors, raw_words)
            if not starts or len(starts) != len(prompts):
                return single
            starts = [0.0] + [s + time_offset for s in starts[1:]]
            meta = [(p.get("emotional_rank") or "R3", _text_in_image(p)) for p in prompts]
        elif chplan.engine == "veo" and chplan.supplemental_paths and chplan.supplemental_anchors:
            veo_dur = _ffprobe_duration(chplan.asset_paths[0])
            supp = compute_anchor_starts(chplan.supplemental_anchors, raw_words)
            if not supp:
                return single
            supp = [s + time_offset for s in supp]
            if chplan.veo_position == "start":
                starts = [0.0, veo_dur] + supp[1:]
            else:
                starts = [0.0] + supp[1:] + [clip_duration - veo_dur]
            # Veo: 1 plano R3 (sin emotional_rank en supplementals); supps R3
            meta = [("R3", "")] * len(starts)
        else:
            return single
    except Exception:  # noqa: BLE001 — cortes no derivables → plano único
        return single
    scenes: list[GfxScene] = []
    for i, st in enumerate(starts):
        en = starts[i + 1] if i + 1 < len(starts) else clip_duration
        if en - st <= 0.3 or st >= clip_duration:
            return single
        scenes.append(GfxScene(i, round(st, 3), round(min(en, clip_duration), 3), meta[i][0], meta[i][1]))
    return scenes


def _gray_frames(path: Path, t0: float, dur: float, w: int = 160, h: int = 90, with_times: bool = False):
    """Frames en gris (numpy uint8 [n, h, w]) del tramo [t0, t0+dur); con with_times, también los
    tiempos ABSOLUTOS reales de cada frame (pts de showinfo: tras -ss el primer frame no siempre cae
    donde supone la grilla 1/fps)."""
    import re
    import numpy as np
    vf = ("showinfo," if with_times else "") + f"scale={w}:{h},format=gray"
    r = subprocess.run(["ffmpeg", "-v", "info" if with_times else "error", "-ss", f"{max(0.0, t0):.3f}", "-i", str(path),
                        "-t", f"{dur:.3f}", "-vf", vf, "-f", "rawvideo", "-"], capture_output=True, timeout=120)
    frames = np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w)
    if not with_times:
        return frames
    pts = [max(0.0, t0) + float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr.decode(errors="replace"))]
    return frames, pts


def snap_cuts(scenes: list[GfxScene], base: Path, fps: int) -> list[GfxScene]:
    """F2 §0b.4: ancla cada corte intra-cap al cambio REAL de imagen en el base_clip.

    compute_anchor_starts da el tiempo de la PALABRA; el corte de video cae ~45 ms antes (1–2 frames).
    Con el anchor, el "freeze" de la disolvencia salía de la imagen ENTRANTE (disolvencia nula = corte
    duro). Se busca la máxima diferencia entre frames consecutivos en ±cut_snap_window_sec del anchor y
    se usa el pts REAL del primer frame del plano entrante.
    """
    import numpy as np
    win = gfx_rules.cut_snap_window_sec
    for i in range(1, len(scenes)):
        anchor_t = scenes[i].start
        t0 = max(scenes[i - 1].start, anchor_t - win)
        fr, pts = _gray_frames(base, t0, 2 * win, 160, 90, with_times=True)
        n = min(len(fr), len(pts))
        if n < 3:
            continue
        diffs = np.abs(np.diff(fr[:n].astype(np.int16), axis=0)).mean(axis=(1, 2))
        k = int(diffs.argmax())
        if diffs[k] < 6.0:                     # sin cambio claro (p.ej. corte entre planos parecidos)
            continue
        real = round(round(pts[k + 1] * fps) / fps, 3)   # primer frame del plano entrante, en la grilla
        if scenes[i - 1].start + 0.3 < real < scenes[i].end - 0.3:
            scenes[i - 1].end = real
            scenes[i].start = real
    return scenes


def assign_quiet_sides(scenes: list[GfxScene], base: Path) -> list[GfxScene]:
    """F2 §0b.6–7: lado con menos detalle (menor varianza de luminancia, tercios izquierdo vs derecho,
    franja superior 70 %). No hay bbox del sujeto en depth_probe/zoom_judge → fallback del handoff.
    F3: además, en ese lado, la banda más OSCURA entre arriba (0–33 %) y medio (33–66 %) = dark_v (ahí va el
    bloque de ícono: lejos del sujeto y sobre fondo oscuro; la franja de abajo es de los subtítulos)."""
    for s in scenes:
        fr = _gray_frames(base, (s.start + s.end) / 2, 0.05)
        if len(fr) == 0:
            continue
        f = fr[0].astype(float)[: int(fr.shape[1] * 0.7)]          # franja superior 70 %
        w = f.shape[1]
        left, right = f[:, : int(w * 0.4)].var(), f[:, int(w * 0.6):].var()
        s.quiet_side = "left" if left < right else "right"
        g = fr[0].astype(float)
        h3 = g.shape[0] // 3
        cols = slice(0, int(w * 0.4)) if s.quiet_side == "left" else slice(int(w * 0.6), w)
        s.dark_v = "top" if g[:h3, cols].mean() <= g[h3: 2 * h3, cols].mean() else "mid"
    return scenes


def icon_sources(resolved: dict[str, Any], ctx: dict[str, Any]) -> int:
    """F3: el bloque de ícono lleva la fuente debajo si la palabra está en un dato con fuente resoluble
    (ctx["fact_source"]: prefijo literal de sources[], el mismo que usa source_tag). Devuelve cuántos tomaron fuente."""
    import re as _re
    n = 0
    for e in resolved.get("emphasis") or []:
        if not e.get("icon_callout") or e.get("source"):
            continue
        w = str(e.get("word", "")).lower()
        for i, f in enumerate(ctx.get("facts") or []):
            src = (ctx.get("fact_source") or {}).get(i)
            if src and w and _re.search(rf"\b{_re.escape(w)}\b", f.lower()):
                e["source"] = src
                n += 1
                break
    return n


def extend_base(base: Path, pause: float, fps: int) -> None:
    """F3: alarga el base_clip (-g 30) `pause` segundos congelando el último cuadro (pausa de la pregunta de cierre).
    Escribe a un archivo nuevo y reemplaza (nunca trunca el original: el lab lo usa por hardlink)."""
    tmp = base.with_name(base.stem + ".pausa.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(base), "-an", "-vf", f"tpad=stop_mode=clone:stop_duration={pause:.3f}",
           "-c:v", "libx264", "-preset", gfx_render.reencode_preset, "-crf", str(gfx_render.reencode_crf),
           "-r", str(fps), "-g", str(gfx_render.reencode_gop), "-keyint_min", str(gfx_render.reencode_gop),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(tmp)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not tmp.exists():
        raise GfxError(f"no se pudo alargar el base para la pausa: {r.stderr[-300:]}")
    import os
    os.replace(tmp, base)


def closing_question(resolved: dict[str, Any], ctx: dict[str, Any], work_dir: Path, cap: str, clip_dur: float,
                     log: list[str]) -> float:
    """F3: pregunta de cierre generada (gfx_question, Flash + validador) al FINAL del cap, durante una pausa de
    question_pause_sec con la voz en silencio. Devuelve la pausa a agregar al base (0 si no hay pregunta)."""
    if not gfx_rules.question_auto or gfx_rules.question_pause_sec <= 0:
        return 0.0
    from script_engine.gfx_director import question_keyword
    from script_engine.gfx_question import question_for
    q = question_for(work_dir, cap, ctx["chapter_number"], ctx.get("chapters") or [])
    pause_file = work_dir / f"gfx_pause_{cap}.json"
    if not q.get("text"):
        log.append(f"  pregunta de cierre: no ({q.get('motivo', 'sin texto')}; intentos: "
                   f"{[(x.get('pregunta'), x.get('rechazo')) for x in q.get('intentos', [])]})")
        resolved["chapter_question"] = None
        pause_file.unlink(missing_ok=True)
        return 0.0
    pause = float(gfx_rules.question_pause_sec)
    resolved["chapter_question"] = {"text": q["text"], "start": round(clip_dur, 3), "duration": round(pause, 3),
                                    "keyword": question_keyword(q["text"]), "generated": True, "pause": pause,
                                    **({"manual": True} if q.get("manual") else {})}
    bh = float(gfx_rules.black_hold_sec)
    resolved["black_hold"] = {"start": round(clip_dur + pause, 3), "duration": round(bh, 3)} if bh > 0 else None
    pause_file.write_text(json.dumps({"pause": pause + bh, "text": q["text"]}, ensure_ascii=False), encoding="utf-8")
    log.append(f"  pregunta de cierre: {q['text']!r} (+{pause:.1f} s de pausa{f' + {bh:.1f} s de negro' if bh else ''}, "
               f"{len(q.get('intentos', []))} intento(s))")
    return pause + bh


def _render_sparse(resolved: dict[str, Any], scenes: list[GfxScene], project: Path, out: Path, *, cap: str,
                   clip_dur: float, width: int, height: int, fps: int, quality: str, log: list[str]) -> float:
    """F2 §3.1: HyperFrames solo en las ventanas con eventos (un proyecto con las ventanas concatenadas),
    sin grade CSS; después se cose con el base_g30 y se aplica el grade FFmpeg (viñeta + grano) parejo."""
    from script_engine import gfx_sparse as sp

    def _step(name: str, t_start: float) -> None:
        log.append(f"  {name}: {time.time() - t_start:.1f}s")

    ts = time.time()
    base = project / "public" / "base.mp4"
    windows = sp.event_windows(resolved, scenes, fps, clip_dur)
    cov = sum(b - a for a, b in windows)
    log.append(f"  sparse: {len(windows)} ventanas, {cov:.1f}s de {clip_dur:.1f}s ({100 * cov / clip_dur:.0f} %)")
    plan_s, scenes_s, tr_s, offsets = sp.compose_sparse(resolved, scenes, windows, fps)
    sproj = project.parent / f"{project.name}_sparse"
    (sproj / "public").mkdir(parents=True, exist_ok=True)
    sp.cut_base(base, windows, sproj / "public" / "base.mp4", fps)
    sdur = offsets[-1][2] + (offsets[-1][1] - offsets[-1][0])
    write_project(plan_s, scenes_s, sproj, duration=sdur, width=width, height=height, fps=fps,
                  transitions=tr_s, grade=False)
    _step("5 templater (sparse)", ts)
    ts = time.time()
    lint = _lint(sproj)
    log.append(f"  lint: {lint.get('errorCount')} errores, {lint.get('warningCount')} warnings")
    hf = sproj / "renders" / f"{cap}_sparse.mp4"
    hf.parent.mkdir(parents=True, exist_ok=True)
    _render(sproj, hf, quality)
    render_sec = time.time() - ts
    _step(f"6 lint + render {quality} (sparse)", ts)
    ts = time.time()
    vig = sp.vignette_png(width, height, project / "public" / "vignette.png") if gfx_rules.vignette_opacity > 0 else None
    gr = sp.grain_png(width, height, project / "public" / "grain.png") if gfx_rules.grain_opacity > 0 else None
    tmp = project / "renders" / f"{cap}_gfx_stitch.mp4"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    sp.stitch(base, hf, windows, offsets, clip_dur, tmp, width=width, height=height, fps=fps,
              vignette=vig, grain=gr, grain_opacity=gfx_rules.grain_opacity)
    tmp.replace(out)
    _step("7 stitch + grade FFmpeg", ts)
    return render_sec


def _zoom_frame(base: Path, scene: GfxScene, out: Path) -> Path | None:
    """Frame donde arrancaría el zoom (final de la escena − zoom_dur) para el juez de visión."""
    t = max(scene.start + 0.1, scene.end - gfx_rules.zoom_dur)
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(base), "-frames:v", "1",
                        "-vf", "scale=1280:-2", "-q:v", "3", str(out)], capture_output=True, timeout=120)
    return out if r.returncode == 0 and out.exists() else None


def _text_in_image(prompt: dict[str, Any]) -> str:
    tii = prompt.get("text_in_image")
    if isinstance(tii, dict):
        return str(tii.get("text", "")) if tii.get("present") else ""
    if isinstance(tii, str):
        return tii
    return ""


def remapped_words(chplan: Any) -> tuple[list[dict], list[dict]]:
    """(raw normalizados, remapeados a texto original legible) — misma ruta que los subs de fase2b."""
    raw = json.loads(Path(chplan.timestamps_path).read_text(encoding="utf-8")) if chplan.timestamps_path else []
    words = remap_words_to_original((chplan.narration or "").strip(), raw) if chplan.narration else []
    return raw, (words or [w for w in raw if str(w.get("word", "")).strip()])


# ═══════════════════════════════════════════════════════════════
#  Palanca F1b: director de todos los caps en paralelo (antes del loop de render)
# ═══════════════════════════════════════════════════════════════

def prefetch_plans(plans: list[Any], video_id: str, work_dir: Path, *, max_workers: int = 7) -> dict[str, float]:
    """Llama al gfx_director de todos los caps en paralelo (threads) y deja el cache
    work_dir/gfx_plan_chXX.json. apply_gfx después lo encuentra y no espera a Gemini.

    Las escenas se estiman con la duración del audio (el cache guarda la respuesta CRUDA y apply_gfx
    la re-valida con las escenas reales). Nunca lanza: un cap que falla queda para apply_gfx.
    Devuelve {cap: segundos} (0.0 si ya estaba en cache).
    """
    from concurrent.futures import ThreadPoolExecutor
    from script_engine.gfx_director import DIRECTOR_VERSION, load_chapter_context, select_gfx_plan

    def _cached(cap: str) -> bool:
        """Cache vigente = existe Y es de la versión actual del director (si no, se re-llama acá en paralelo)."""
        f = work_dir / f"gfx_plan_{cap}.json"
        try:
            return f.exists() and json.loads(f.read_text(encoding="utf-8")).get("director") == DIRECTOR_VERSION
        except (OSError, ValueError, AttributeError):
            return False

    def _one(chplan: Any) -> tuple[str, float]:
        cap = chplan.chapter_id
        if _cached(cap):
            return cap, 0.0
        t = time.time()
        try:
            raw_words, words = remapped_words(chplan)
            ctx = load_chapter_context(video_id, chplan)
            scenes = build_scenes(chplan, ctx["script_chapter"], raw_words, float(chplan.audio_duration))
            select_gfx_plan(chplan, ctx=ctx, words=words, scenes=scenes, work_dir=work_dir)
        except Exception as e:  # noqa: BLE001
            error_handler.log_warning(PipelineStage.ASSEMBLY, f"[gfx] prefetch {cap} falló ({e}); lo hará apply_gfx")
        return cap, time.time() - t

    work_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        return dict(ex.map(_one, plans))


# ═══════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════

def apply_gfx(base_clip: Path, plan: Any, video_id: str, work_dir: Path, *,
              width: int, height: int, fps: int, quality: str | None = None,
              reuse: bool = False, time_offset: float = 0.0,
              gfx_plan_override: dict[str, Any] | None = None, debug: bool = False,
              sparse: bool = False, safe_scenes: dict[int, dict[str, Any]] | None = None) -> Path:
    """Aplica la capa gráfica al base_clip de un cap. Devuelve chXX_gfx.mp4 o base_clip (fallback).

    Args:
        base_clip: flux_visual / hybrid_visual / veo (sin audio).
        plan: ChapterPlan de fase2b.
        quality: draft | looks (default gfx_render.quality).
        reuse: si existe chXX_gfx.mp4 y reuse → no re-renderiza (respeta --reuse-visuals).
        time_offset: pre-pad del hook (ch01) — las palabras se corren igual que los subs.
        gfx_plan_override: plan RESUELTO fijo (paso 1 del handoff, sin LLM). None → director + lock.
        debug: overlay de depuración quemado (timecode, bloque activo, escena, rank). Solo con --gfx-debug.
    """
    cap = plan.chapter_id
    out = work_dir / f"{cap}_gfx.mp4"
    log_path = work_dir / f"gfx_{cap}.log"
    log: list[str] = [f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {cap} base={Path(base_clip).name}"]
    t0 = time.time()

    def _step(name: str, t_start: float) -> None:
        log.append(f"  {name}: {time.time() - t_start:.1f}s")

    if reuse and out.exists():
        log.append("  reuse: chXX_gfx.mp4 existente, sin re-render")
        with log_path.open("a", encoding="utf-8") as fh:   # append: no pisar el log del render original
            fh.write("\n".join(log) + "\n")
        return out

    project = work_dir / f"gfx_{cap}"
    try:
        q = clamp_quality(quality or gfx_render.quality)
        _doctor_once(log)

        ts = time.time()
        project.mkdir(parents=True, exist_ok=True)
        _reencode(Path(base_clip), project / "public" / "base.mp4", fps)
        clip_dur = _ffprobe_duration(project / "public" / "base.mp4")
        _step("1 reencode -g30", ts)

        # paso 2: grade CSS dentro de la composición (desvío D4 medido: pasada media-treatment = 6.29× tiempo real)
        log.append(f"  2 grade: CSS intensidad {gfx_rules.css_grade_intensity}")

        ts = time.time()
        raw_words, words = remapped_words(plan)
        from script_engine.gfx_director import load_chapter_context, resolve_plan, select_gfx_plan
        ctx = load_chapter_context(video_id, plan)
        scenes = build_scenes(plan, ctx["script_chapter"], raw_words, clip_dur, time_offset)
        scenes = assign_quiet_sides(snap_cuts(scenes, project / "public" / "base.mp4", fps), project / "public" / "base.mp4")
        log.append(f"  escenas: {len(scenes)} ({', '.join(f'{s.start:.2f}{s.rank}' for s in scenes)})")
        # F2 §4: router anti-deformación → imágenes de riesgo alto (o caídas a Ken Burns) con movimiento seguro
        for si, sv in (safe_scenes or {}).items():
            if 0 <= si < len(scenes) and len(scenes) > 1:
                scenes[si].safe = sv
                log.append(f"  safe_router: escena {si} {Path(sv['image']).name} → {sv['movement']} ({sv.get('risk', '?')})")
        intensity = None
        if gfx_plan_override is None and gfx_rules.intensity_director:   # F4b §1: director de intensidad (Flash)
            from gfx_config import ACTIVE_PROFILE, active_moods, active_profile_name, profile_path
            from script_engine import gfx_intensity as gi
            from script_engine.gfx_peak import sentences as _sents
            from script_engine.gfx_question import sentences as _q_sents
            chs = {int(c.get("chapter_number", 0)): str(c.get("narration", "")) for c in ctx.get("chapters") or []}
            n = ctx["chapter_number"]
            moods_all = ACTIVE_PROFILE.get("moods") or {}
            intensity = gi.intensity_for([s["text"] for s in _sents(words, time_offset)], cap=cap, work_dir=work_dir,
                                         moods_all=moods_all, prev2=_q_sents(chs.get(n - 1, ""))[-2:],
                                         next2=_q_sents(chs.get(n + 1, ""))[:2], log=log)
            ctx["moods"] = gi.augmented_moods(active_moods(), intensity)
            ctx["intensity"] = intensity
            if intensity:
                log.append(f"  intensidad: pico frase {gi.peak_sentence(intensity)} · cargas "
                           f"{[(c['word'], c['categoria'], c['peso']) for c in intensity['cargas']]}")
                gi.record_proposals(intensity, moods_all, video_id=video_id, profile_path=profile_path(active_profile_name()),
                                    log=log)
        if gfx_plan_override is not None:
            resolved = gfx_plan_override
            rejected: list[dict] = []
            log.append("  plan: override fijo (sin LLM)")
        else:
            from script_engine.gfx_literal_lock import lock
            raw_plan = select_gfx_plan(plan, ctx=ctx, words=words, scenes=scenes, work_dir=work_dir, log=log,
                                       time_offset=time_offset)
            # F2 §1: el box del zoom lo decide visión sobre el frame real (cache por escena)
            from script_engine.gfx_director import apply_zoom_vision
            raw_plan = apply_zoom_vision(raw_plan, frame_for_scene=lambda si: _zoom_frame(
                project / "public" / "base.mp4", scenes[si], work_dir / f"gfx_zoomframe_{cap}_s{si:02d}.jpg"),
                cache=work_dir / f"gfx_zoom_box_{cap}.json", log=log)
            # pre-merge: dedupe de cifras a nivel video (contadores ya animados en caps anteriores)
            from script_engine.gfx_director import counted_figures_before
            ctx["video_counted"] = counted_figures_before(work_dir, ctx["chapter_number"])
            if ctx["video_counted"]:
                log.append(f"  cifras ya animadas en caps anteriores: {sorted(ctx['video_counted'])}")
            resolved = resolve_plan(raw_plan, ctx=ctx, words=words, scenes=scenes, time_offset=time_offset, log=log)
            resolved, rejected = lock(resolved, ctx["sources"], chapter_number=ctx["chapter_number"],
                                      question_sources=ctx.get("next_sources"))
            if gfx_rules.fragment_director:                          # F4b §2: el fragmento literal más impactante
                from gfx_config import active_moods as _am
                from script_engine.gfx_fragments import choose_fragments
                resolved["fragmentos"] = choose_fragments(resolved, ctx=ctx, words=words, scenes=scenes,
                                                          time_offset=time_offset, moods=ctx.get("moods") or _am(),
                                                          work_dir=work_dir, cap=cap, log=log)
                resolved, rej_f = lock(resolved, ctx["sources"], chapter_number=ctx["chapter_number"],
                                       question_sources=ctx.get("next_sources"))
                rejected += rej_f
        if gfx_plan_override is None and gfx_rules.peak_blocks:      # F3: pico del cap + zoom con latido + reloj
            from gfx_config import active_moods
            from script_engine.gfx_peak import box_from_cache, plan_peak, water_used_before
            cache_box = box_from_cache(work_dir / f"gfx_zoom_box_{cap}.json")

            def _box(si: int, word: str) -> list[float] | None:
                b = cache_box(si, word)
                if b is None:                                 # sin caja → visión sobre el frame del final de la escena
                    from script_engine.gfx_director import apply_zoom_vision
                    tmp = apply_zoom_vision({"evidence_zoom": {"scene_idx": si, "anchor": word}}, frame_for_scene=lambda i: _zoom_frame(
                        project / "public" / "base.mp4", scenes[i], work_dir / f"gfx_zoomframe_{cap}_s{i:02d}.jpg"),
                        cache=work_dir / f"gfx_zoom_box_{cap}.json", log=log)
                    b = (tmp.get("evidence_zoom") or {}).get("box")
                return b
            plan_peak(resolved, ctx=ctx, words=words, scenes=scenes, moods=ctx.get("moods") or active_moods(), clip_dur=clip_dur,
                      box_for=_box, water_used=water_used_before(work_dir, ctx["chapter_number"]), time_offset=time_offset,
                      log=log, intensity=intensity)
            from script_engine.gfx_literal_lock import lock as _lock2                 # lo nuevo también pasa el candado
            resolved, rej2 = _lock2(resolved, ctx["sources"], chapter_number=ctx["chapter_number"],
                                    question_sources=ctx.get("next_sources"))
            rejected += rej2
        if gfx_plan_override is None and gfx_rules.identity_rules:   # F4 §2: formas de la identidad del canal
            from script_engine.gfx_style import (identity_transitions, identity_violations, plan_movements,
                                                 prompt_for_asset, select_punches)
            prompts = ctx["script_chapter"].get("image_prompts") or []
            movs = plan_movements(scenes, plan, prompts, log)
            resolved["punch_in"] = select_punches(resolved, words, time_offset=time_offset, moods=ctx.get("moods"), log=log)
            pbs = ([prompt_for_asset(a, prompts, i) for i, a in enumerate(plan.asset_paths)]
                   if getattr(plan, "engine", "") == "flux" else [])
            tr = identity_transitions(scenes, pbs, (resolved.get("evidence_zoom") or {}).get("scene_idx"))
            resolved["transitions"] = {str(k): v for k, v in tr.items()}
            viol = identity_violations(resolved, tr)
            resolved["identity"] = {"movimientos": movs, "violaciones": viol}
            log.append(f"  identidad: transiciones {[tr[k]['kind'] for k in sorted(tr)]} · violaciones {viol}")
        n_src = icon_sources(resolved, ctx)                  # F3: fuente debajo del bloque de ícono (si hay)
        if n_src:
            log.append(f"  íconos con fuente: {n_src}")
        # F3: pregunta de cierre generada + pausa real (alarga el base; fase2b rellena el audio con silencio)
        if gfx_plan_override is None:
            pause = closing_question(resolved, ctx, work_dir, cap, clip_dur, log)
        else:
            pause = float((resolved.get("chapter_question") or {}).get("pause") or 0.0)
        if pause > 0:
            extend_base(project / "public" / "base.mp4", pause, fps)
            clip_dur = _ffprobe_duration(project / "public" / "base.mp4")
            scenes[-1].end = round(clip_dur, 3)
        log.append(f"  plan: {json.dumps(resolved, ensure_ascii=False)}")
        log.append(f"  lock rechazados: {len(rejected)} {json.dumps(rejected, ensure_ascii=False)}")
        (work_dir / f"gfx_plan_{cap}.resolved.json").write_text(
            json.dumps({"plan": resolved, "rejected": rejected}, ensure_ascii=False, indent=1), encoding="utf-8")
        # F2 §0d: SFX por bloque visible → fase2b los mezcla en el pase de audio (si --sfx)
        from gfx_config import sfx_for
        from script_engine.gfx_director import sfx_events
        sfx = sfx_events(resolved, words, time_offset, sfx_for, log)
        (work_dir / f"gfx_sfx_{cap}.json").write_text(json.dumps(sfx, ensure_ascii=False, indent=1), encoding="utf-8")
        log.append(f"  sfx: {len(sfx)} eventos ({', '.join(e['block'] for e in sfx)})")
        _step("3-4 plan + lock", ts)

        if sparse and not debug:
            # F2 §3.1: render disperso (solo ventanas con eventos) + grade FFmpeg uniforme
            render_sec = _render_sparse(resolved, scenes, project, out, cap=cap, clip_dur=clip_dur,
                                        width=width, height=height, fps=fps, quality=q, log=log)
            from script_engine.gfx_project import cue_events
            from script_engine.gfx_review import write_cues
            write_cues(cap, cue_events(resolved, scenes, fps), log, resolved.get("gap_warnings", []), render_sec, work_dir)
            log.append(f"  OK total {time.time() - t0:.1f}s → {out.name} (disperso)")
            error_handler.log_success(PipelineStage.ASSEMBLY, f"[gfx] {cap} OK en {time.time() - t0:.0f}s (disperso)")
            return out

        ts = time.time()
        write_project(resolved, scenes, project, duration=clip_dur, width=width, height=height, fps=fps,
                      debug=debug)
        _step("5 templater", ts)

        ts = time.time()
        lint = _lint(project)
        log.append(f"  lint: {lint.get('errorCount')} errores, {lint.get('warningCount')} warnings")
        tmp = project / "renders" / f"{cap}_gfx.mp4"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        _render(project, tmp, q)
        tmp.replace(out)
        render_sec = time.time() - ts
        _step(f"6 lint + render {q}", ts)

        # F1b: hoja de cues (misma fuente de eventos que el overlay --gfx-debug)
        from script_engine.gfx_project import cue_events
        from script_engine.gfx_review import write_cues
        write_cues(cap, cue_events(resolved, scenes, fps), log, resolved.get("gap_warnings", []), render_sec, work_dir)

        log.append(f"  OK total {time.time() - t0:.1f}s → {out.name}")
        error_handler.log_success(PipelineStage.ASSEMBLY, f"[gfx] {cap} OK en {time.time() - t0:.0f}s")
        return out
    except Exception as e:  # noqa: BLE001 — D2: cualquier error → fallback al base_clip
        log.append(f"  FALLBACK {type(e).__name__}: {e} ({time.time() - t0:.1f}s)")
        error_handler.log_warning(PipelineStage.ASSEMBLY, f"[gfx] {cap} fallback a base_clip: {type(e).__name__}: {e}")
        return Path(base_clip)
    finally:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(log) + "\n")
