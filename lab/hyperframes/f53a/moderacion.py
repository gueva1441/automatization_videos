# -*- coding: utf-8 -*-
"""F53a etapa 2 — prueba de moderación de Gemini Omni Flash 1.1 (G) y Seedance 2.5 (S) con las 2 fotos más oscuras ya
generadas del canal (`f53a/fotos/elegidas.json`, armado en la etapa 1). Reusa por import, sin copiar:
- `f52/prompts_video.py`: `PEDIDO` (el de F52b, con la línea FIRST FRAME) y `llamar` (Opus 5.5 effort high, foto como
  bloque `image` + pedido), con la ficha `f52/guias/{G,S}.md`; «APPROVED MOTION» = el `video_prompt` vivo del topic si
  existe, si no «(none)»;
- `f52/prueba_video.py`: `correr` (cola de fal, espera, descarga, ffprobe, costo), `ffprobe`, `costo`. Para F53a se
  cambian en ese módulo `CLIPS` (→ `f53a/clips/`) y `payload` (→ 4 s, G 360p, S 480p y `generate_audio` false), que
  ahí están fijos para F52 (8 s, 1080p), y su `F52` (→ `f53a/`), base de la ruta relativa del clip.
La foto va como data URI con el tipo leído de los bytes. Guarda de tope antes de llamar: gastado desde `TOPE_TANDA.desde`
+ peor caso (handoff: G 2 × 4 s × 0,15; S 2 × 0,8; Opus 0,15) < tope; si no, PARADA. Costo en `cost_tracker`
(`f53a_lab_prompts`, `f53a_lab_clips`). No toca producción.

Salida: `clips/fotoN_<G|S>.mp4`, `resultado.json`, `contactos.png` (cuadros a 0/1/2/3/4 s, filas = clip).
Uso: python lab/hyperframes/f53a/moderacion.py
"""
import base64
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
F53A = Path(__file__).resolve().parent
F52 = ROOT / "lab" / "hyperframes" / "f52"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(F52))
import prompts_video as pv          # noqa: E402  F52b: PEDIDO + llamar
import prueba_video as pr           # noqa: E402  F52 etapa 3: correr, ffprobe, costo

MODELOS = {"G": "Gemini Omni Flash 1.1", "S": "Seedance 2.5"}
DUR = 4                                                         # mínimo común de los schemas (G 3–10, S 4–30)
RES = {"G": "360p", "S": "480p"}                                # la más baja de cada schema
PEOR_CASO = 2 * DUR * 0.15 + 2 * 0.8 + 0.15                     # handoff F53a §Constantes
FUENTE = "C\\:/Windows/Fonts/arial.ttf"
TIEMPOS = (0, 1, 2, 3, 4)


def payload_f53a(k: str, prompt: str, foto: str) -> dict:
    if k == "S":
        return {"prompt": prompt, "image_url": foto, "duration": str(DUR), "resolution": RES["S"],
                "generate_audio": False}
    return {"prompt": prompt, "image_url": foto, "duration": DUR, "resolution": RES["G"]}          # G: sin audio


def foto(path: Path) -> tuple[str, str, str]:
    """(tipo leído de los bytes, base64, data URI)."""
    b = path.read_bytes()
    tipo = "image/jpeg" if b[:3] == b"\xff\xd8\xff" else "image/png" if b[:8] == b"\x89PNG\r\n\x1a\n" else None
    if tipo is None:
        raise SystemExit(f"{path.name} no es ni JPEG ni PNG")
    b64 = base64.b64encode(b).decode("ascii")
    return tipo, b64, f"data:{tipo};base64,{b64}"


def contactos(clips: list[Path], dst: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp, idx = Path(tmp), 0
        for c in clips:
            for t in TIEMPOS:
                idx += 1
                ts = min(t, DUR - 1 / 24)
                subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{ts:.3f}", "-i", str(c),
                                "-frames:v", "1", "-vf",
                                f"scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2,"
                                f"drawtext=fontfile='{FUENTE}':text='{c.stem} · {t} s':x=10:y=10:fontsize=22:"
                                f"fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=6",
                                str(tmp / f"k_{idx:03d}.png")], check=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "1", "-i",
                        str(tmp / "k_%03d.png"), "-vf", f"tile={len(TIEMPOS)}x{len(clips)}", "-frames:v", "1",
                        str(dst)], check=True)


def main() -> int:
    clips_dir = F53A / "clips"
    if any(clips_dir.glob("*.mp4")):
        print("ya hay clips en f53a/clips/: no se vuelve a llamar")
        return 1
    elegidas = json.loads((F53A / "fotos" / "elegidas.json").read_text(encoding="utf-8"))
    assert len(elegidas) == 2

    gastado, tope = pr.gastado_desde_tope()
    print(f"gastado {gastado} · peor caso {PEOR_CASO:.2f} · tope {tope}")
    if gastado + PEOR_CASO >= tope:
        print("PARADA: el peor caso pasa el tope")
        return 1

    # 1) los 4 prompts con el camino de F52b
    fichas = {k: (F52 / "guias" / f"{k}.md").read_text(encoding="utf-8").strip() for k in MODELOS}
    fotos = {i: foto(F53A / "fotos" / e["archivo"]) for i, e in enumerate(elegidas, start=1)}
    pedidos = {(i, k): pv.PEDIDO.format(ficha=fichas[k], prompt_foto=e["prompt"], ancla=e.get("ancla") or "(none)",
                                        video_prompt_vivo=e.get("video_prompt") or "(none)")
               for i, e in enumerate(elegidas, start=1) for k in MODELOS}
    from cost_tracker import cost_tracker
    cost_tracker.start_video("f53a_lab_prompts")
    prompts, err_p = {}, {}
    try:
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs = {(i, k): ex.submit(pv.llamar, p, fotos[i][:2], f"f53a:prompt:{k}:foto{i}")
                    for (i, k), p in pedidos.items()}
            for (i, k), f in futs.items():
                try:
                    prompts[(i, k)] = f.result()
                except Exception as e:                                  # noqa: BLE001 — se reporta tal cual
                    err_p[(i, k)] = f"{type(e).__name__}: {e}"[:600]
    finally:
        rp = cost_tracker.end_video()
    if err_p:
        print("PARADA: Opus no escribió", err_p)
        (F53A / "resultado.json").write_text(json.dumps({"errores_prompt": {f"foto{i}_{k}": v for (i, k), v in
                                                                            err_p.items()}}, ensure_ascii=False,
                                                        indent=1), encoding="utf-8")
        return 1

    # 2) los 4 clips en paralelo, con correr/ffprobe/costo de F52 (CLIPS y payload de F53a)
    clips_dir.mkdir(exist_ok=True)
    pr.CLIPS, pr.payload, pr.F52 = clips_dir, payload_f53a, F53A    # F52 de pr: base de r["archivo"]
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {(i, k): ex.submit(pr.correr, i, k, prompts[(i, k)][0], fotos[i][2]) for (i, k) in pedidos}
        res = {(i, k): f.result() for (i, k), f in futs.items()}
    for (i, k), r in res.items():                                      # nombre propio: fotoN_<letra>.mp4
        src = clips_dir / f"cap{i:02d}_{k}.mp4"
        if src.exists():
            dst = clips_dir / f"foto{i}_{k}.mp4"
            src.replace(dst)
            r["archivo"] = str(dst.relative_to(F53A))
        r["clip"] = f"foto{i}_{k}"

    cost_tracker.start_video("f53a_lab_clips")
    from error_handler import PipelineStage
    for (i, k), r in res.items():
        if r.get("usd"):
            cost_tracker._add_entry(stage=PipelineStage.VIDEO.value, service=f"fal {r['endpoint']}",
                                    description=f"f53a:clip:foto{i}_{k}", units=r["ffprobe"]["duracion_s"],
                                    unit_label="s", cost_per_unit=0.0, total_cost=r["usd"])
    rc = cost_tracker.end_video()

    hechos = [clips_dir / f"foto{i}_{k}.mp4" for (i, k) in sorted(res) if (clips_dir / f"foto{i}_{k}.mp4").exists()]
    if hechos:
        contactos(hechos, F53A / "contactos.png")
    out = {"elegidas": elegidas, "tipo_foto": {f"foto{i}": fotos[i][0] for i in fotos},
           "gastado_antes": gastado, "peor_caso": round(PEOR_CASO, 2),
           "usd_prompts": round(rp.total_cost, 4) if rp else None, "usd_clips": round(rc.total_cost, 4) if rc else 0,
           "prompts": {f"foto{i}_{k}": {"prompt": t, **m} for (i, k), (t, m) in prompts.items()},
           "clips": {f"foto{i}_{k}": r for (i, k), r in sorted(res.items())}}
    (F53A / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for (i, k), r in sorted(res.items()):
        print(f"foto{i}_{k}", r.get("error") or f"{r['ffprobe']} · espera {r.get('espera_s')} s · US$ {r.get('usd')}")
    print(f"US$ prompts {out['usd_prompts']} · clips {out['usd_clips']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
