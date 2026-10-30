# -*- coding: utf-8 -*-
"""F57 Parte B — un clip real en lab por el camino de producción de la Parte A: la foto inicial del cap 1 de Wittenoom
(`lab/hyperframes/f52/fotos/cap01.png`, JPEG 2560×1440; `image_prompt` de `fotos_f52.json` → cap01.prompt), la voz del
clip (`m03_visual.voz_del_clip` sobre la copia de A0, cap 1, start, ventana con 2,4 palabras/s de `guion_v4.PALABRAS_POR_SEG`
porque la narración F56 no tiene voz), el movimiento REGENERADO con `m03_visual._seedream_video_prompt` (prueba A2; el del
03_visual.json vivo se escribió con el ancla vieja: se informan los dos) → `asset_manager.foto_final_del_clip` (instrucción
de Opus → Seedream /edit → SSIM) → `asset_manager._generate_clip` con las 2 fotos (Opus escribe el prompt del motor con
PEDIDO_CON_FINAL; G 1080p 8 s; si G rechaza, K con las mismas 2 fotos). Gasto por `cost_tracker.start_video/end_video`
(como f53b/clip_real.py). No toca `_steps` ni `output/<topic>`. Salida: SALIDA_B.md, clip_b.json, clip/ (fotos, mp4, lado a
lado, hoja de contactos 0/2/4/6/8 s). Uso: python lab/hyperframes/f57/clip_b.py"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

F57 = Path(__file__).resolve().parent
CLIP = F57 / "clip"
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
FOTO_F52 = ROOT / "lab" / "hyperframes" / "f52" / "fotos" / "cap01.png"
PROMPTS_F52 = ROOT / "lab" / "hyperframes" / "f52" / "fotos" / "fotos_f52.json"
ANTES = F57 / "antes" / "01b_narration.json"
VISUAL_VIVO = ROOT / "data" / "scripts" / "_steps" / TID / "03_visual.json"
TIEMPOS = (0, 2, 4, 6, 8)


def ff(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)],
                          capture_output=True, text=True)


def hoja_de_contactos(mp4: Path, salida: Path) -> None:
    """Cuadros a 0, 2, 4, 6 s y el último (≈ 8 s), uno al lado del otro."""
    tmp = CLIP / "_cuadros"
    tmp.mkdir(exist_ok=True)
    for i, t in enumerate(TIEMPOS):
        if t >= TIEMPOS[-1]:
            ff("-sseof", "-0.1", "-i", mp4, "-frames:v", "1", "-vf", "scale=640:-2", tmp / f"k_{i:03d}.png")
        else:
            ff("-ss", t, "-i", mp4, "-frames:v", "1", "-vf", "scale=640:-2", tmp / f"k_{i:03d}.png")
    ff("-framerate", "1", "-i", tmp / "k_%03d.png", "-vf", f"tile={len(TIEMPOS)}x1", "-frames:v", "1", salida)
    shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    import asset_manager as am
    from cost_tracker import cost_tracker
    from script_engine import m03_visual as m3
    from script_engine.guion_v4 import PALABRAS_POR_SEG

    CLIP.mkdir(exist_ok=True)
    foto = CLIP / "cap01_img_01.png"
    shutil.copyfile(FOTO_F52, foto)
    image_prompt = json.loads(PROMPTS_F52.read_text(encoding="utf-8"))["cap01"]["prompt"]
    narr = next(c for c in json.loads(ANTES.read_text(encoding="utf-8"))["chapters"] if c["chapter_number"] == 1)["narration"]
    # la ventana como la calcula _process_one_cap (m03 l.2181-2186), con la duración = palabras / 2,4 (solo acá)
    dur = len(narr.split()) / PALABRAS_POR_SEG
    ventana = max(1, min(int(m3.VEO_CLIP_DURATION_SEC * (len(narr) / dur)), len(narr) - 1))
    voz_clip = m3.voz_del_clip(narr, "start", ventana)
    cap_vivo = next(c for c in json.loads(VISUAL_VIVO.read_text(encoding="utf-8"))["chapters"] if c["chapter_number"] == 1)
    mov_viejo, ancla_vieja = cap_vivo["video_prompt"], cap_vivo.get("narration_anchor")

    res: dict = {"foto_inicial": str(FOTO_F52.relative_to(ROOT)), "image_prompt": image_prompt, "narracion_cap1_chars": len(narr),
                 "palabras_cap1": len(narr.split()), "ventana_chars": ventana, "voz_clip": voz_clip,
                 "palabras_voz_clip": len(voz_clip.split()), "ancla_vieja": ancla_vieja, "movimiento_viejo": mov_viejo,
                 "movimiento_nuevo": None, "foto_final": None, "clip": None, "error": None, "pasos": []}
    log: list = []
    t0 = time.time()
    cost_tracker.start_video("f57_clip_b")
    try:
        mov = m3._seedream_video_prompt(image_prompt, voz_clip, "f57 cap 1 (clip_b) video_prompt")
        res["movimiento_nuevo"] = mov
        res["pasos"].append("movimiento (Opus) ok")
        final = am.foto_final_del_clip(foto, image_prompt, voz_clip, mov, CLIP / "cap01_img_01_final.png")
        res["foto_final"] = {**final, "path": str(final["path"].relative_to(ROOT)) if final["path"] else None}
        res["pasos"].append(f"foto final: {'ok' if final['path'] else 'sin final'} · ssim {final['ssim']} · {final['motivo']}")
        salida = CLIP / "cap01_clip_01.mp4"
        am._generate_clip(foto, mov, salida, image_prompt=image_prompt, ancla=voz_clip, foto_final=final["path"], log=log)
        res["clip"] = str(salida.relative_to(ROOT))
        res["pasos"].append("clip ok")
    except Exception as e:                                    # noqa: BLE001 — se reporta tal cual
        res["error"] = f"{type(e).__name__}: {e}"[:900]
    finally:
        rep = cost_tracker.end_video()
    res["log_clip"] = log
    res["segundos_reloj"] = round(time.time() - t0, 1)
    res["cost_tracker"] = [{"servicio": x.service, "descripcion": x.description, "usd": round(x.total_cost, 5)}
                           for x in (rep.entries if rep else [])]
    res["usd_total"] = round(rep.total_cost, 4) if rep else None
    # imágenes para el reporte
    fin = CLIP / "cap01_img_01_final.png"
    if fin.exists():
        ff("-i", foto, "-i", fin, "-filter_complex", "[0:v]scale=960:-2[a];[1:v]scale=960:-2[b];[a][b]hstack=inputs=2",
           CLIP / "lado_a_lado.jpg")
    if res["clip"]:
        hoja_de_contactos(CLIP / "cap01_clip_01.mp4", CLIP / "hoja_contactos.jpg")
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height:format=duration",
                              "-of", "json", str(CLIP / "cap01_clip_01.mp4")], capture_output=True, text=True)
        res["ffprobe"] = json.loads(out.stdout or "{}")
    (F57 / "clip_b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    # Salida B en texto
    fila = next((x for x in log if x.get("motor")), None)
    rech = [r for x in log for r in x.get("rechazos", [])]
    L = ["# F57 — Salida B (texto)", "",
         f"Foto inicial: `{res['foto_inicial']}` (JPEG 2560×1440, F52). Narración: copia A0 (`lab/hyperframes/f57/antes/01b_narration.json`), cap 1, "
         f"{res['narracion_cap1_chars']} caracteres, {res['palabras_cap1']} palabras; ventana {ventana} caracteres (2,4 palabras/s, solo acá).", "",
         f"**voz_clip** ({res['palabras_voz_clip']} palabras): «{voz_clip}»", "",
         f"Ancla vieja (03_visual.json vivo): «{ancla_vieja}»", "",
         "## 1. Movimiento viejo y nuevo", "", f"**Viejo (03_visual.json, con el ancla):**", "", f"    {mov_viejo}", "",
         f"**Nuevo (`_seedream_video_prompt` con voz_clip):**", "", f"    {res['movimiento_nuevo']}", "",
         "## 2. Instrucción de edit (foto final)", "",
         f"    {(res['foto_final'] or {}).get('instruccion')}", "",
         f"Resultado: {'foto final ' + str((res['foto_final'] or {}).get('path')) if (res['foto_final'] or {}).get('path') else 'SIN foto final'} · "
         f"**SSIM inicial/final: {(res['foto_final'] or {}).get('ssim')}** (se informa; sin umbral) · motivo: {(res['foto_final'] or {}).get('motivo')}", "",
         "## 3. Prompt del motor y motor que lo hizo", "",
         f"Motor: **{fila['motor'] if fila else None}** · rechazos: {rech or 'ninguno'}", "",
         f"    {fila['prompt'] if fila else '(sin clip)'}", "",
         f"Clip: {res['clip']} · {json.dumps({k: fila.get(k) for k in ('segundos', 'ancho', 'alto', 'audio', 'usd', 'foto_final')}, ensure_ascii=False) if fila else res['error']}", "",
         "## 4. Gasto", "", "| servicio | descripción | US$ |", "|---|---|---|"]
    L += [f"| {x['servicio']} | {x['descripcion']} | {x['usd']} |" for x in res["cost_tracker"]]
    L += ["", f"**Total US$ {res['usd_total']}** · {res['segundos_reloj']} s de reloj.", "",
          "## 5. Archivos", "", "- `clip/cap01_img_01.png` (inicial, copia de F52) · `clip/cap01_img_01_final.png` (final)",
          "- `clip/lado_a_lado.jpg` (las 2 fotos lado a lado) · `clip/hoja_contactos.jpg` (cuadros 0, 2, 4, 6, 8 s)",
          "- `clip/cap01_clip_01.mp4` · `clip_b.json` (todo, con el log del clip y ffprobe)", "",
          f"Error: {res['error']}" if res["error"] else "Sin errores."]
    (F57 / "SALIDA_B.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))
    return 1 if res["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
