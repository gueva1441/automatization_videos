# -*- coding: utf-8 -*-
"""F53a-K — prueba de moderación de Kling 4.0 (`kling/v4/image-to-video`) con las 2 fotos oscuras de F53a
(`f53a/fotos/foto1.png`, `foto2.png`, de `elegidas.json`). Igual que F53a, solo con K. Reusa `f53a/moderacion.py` por
import (que a su vez reusa `f52/prompts_video` y `f52/prueba_video`): `foto` (tipo leído de los bytes), `contactos`, el
`PEDIDO` y `llamar` de F52b (Opus 5.5 effort high, mira la foto) con la ficha `f52/guias/K.md`, y `correr`/`ffprobe`/
`costo` de F52. Para K: `start_image_url`, 4 s, 720p (la más baja del schema); K no tiene campo de audio (la pista se
descarta). Guarda de tope antes de llamar: gastado desde `TOPE_TANDA.desde` (F53b + F53a-K) + peor caso de K (2 × 4 s ×
0,235 US$/s, el precio por segundo de K a 1080p según la estimación de F52, + Opus 0,08) < tope; si no, PARADA.

Salida en `f53a/K/`: `clips/fotoN_K.mp4`, `resultado.json`, `contactos.png` (0/1/2/3/4 s).
Uso: python lab/hyperframes/f53a/K/moderacion_k.py
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KDIR = Path(__file__).resolve().parent
F53A = KDIR.parent
sys.path.insert(0, str(F53A))
import moderacion as mo          # noqa: E402  F53a (y por él, f52/prompts_video y f52/prueba_video)

DUR, RES = mo.DUR, "720p"
PEOR_CASO = 2 * DUR * 0.235 + 0.08          # handoff F52: K ≈ 1,88 por clip de 8 s a 1080p; Opus ≈ 0,04 por prompt


def payload_k(k: str, prompt: str, foto: str) -> dict:
    assert k == "K"
    return {"prompt": prompt, "start_image_url": foto, "duration": DUR, "resolution": RES}


def main() -> int:
    clips_dir = KDIR / "clips"
    if any(clips_dir.glob("*.mp4")):
        print("ya hay clips en f53a/K/clips/: no se vuelve a llamar")
        return 1
    elegidas = json.loads((F53A / "fotos" / "elegidas.json").read_text(encoding="utf-8"))
    gastado, tope = mo.pr.gastado_desde_tope()
    print(f"gastado {gastado} · peor caso K {PEOR_CASO:.2f} · tope {tope}")
    if gastado + PEOR_CASO >= tope:
        print("PARADA: el peor caso pasa el tope")
        return 1

    ficha = (mo.F52 / "guias" / "K.md").read_text(encoding="utf-8").strip()
    fotos = {i: mo.foto(F53A / "fotos" / e["archivo"]) for i, e in enumerate(elegidas, start=1)}
    pedidos = {i: mo.pv.PEDIDO.format(ficha=ficha, prompt_foto=e["prompt"], ancla=e.get("ancla") or "(none)",
                                      video_prompt_vivo=e.get("video_prompt") or "(none)")
               for i, e in enumerate(elegidas, start=1)}
    from cost_tracker import cost_tracker
    cost_tracker.start_video("f53ak_lab_prompts")
    prompts, err = {}, {}
    try:
        with ThreadPoolExecutor(max_workers=2) as ex:
            futs = {i: ex.submit(mo.pv.llamar, p, fotos[i][:2], f"f53ak:prompt:K:foto{i}") for i, p in pedidos.items()}
            for i, f in futs.items():
                try:
                    prompts[i] = f.result()
                except Exception as e:                                  # noqa: BLE001 — se reporta tal cual
                    err[i] = f"{type(e).__name__}: {e}"[:600]
    finally:
        rp = cost_tracker.end_video()
    if err:
        print("PARADA: Opus no escribió", err)
        return 1

    clips_dir.mkdir(exist_ok=True)
    mo.pr.CLIPS, mo.pr.payload, mo.pr.F52 = clips_dir, payload_k, KDIR
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {i: ex.submit(mo.pr.correr, i, "K", prompts[i][0], fotos[i][2]) for i in pedidos}
        res = {i: f.result() for i, f in futs.items()}
    for i, r in res.items():
        src = clips_dir / f"cap{i:02d}_K.mp4"
        if src.exists():
            dst = clips_dir / f"foto{i}_K.mp4"
            src.replace(dst)
            r["archivo"] = str(dst.relative_to(KDIR))
        r["clip"] = f"foto{i}_K"

    cost_tracker.start_video("f53ak_lab_clips")
    from error_handler import PipelineStage
    for i, r in res.items():
        if r.get("usd"):
            cost_tracker._add_entry(stage=PipelineStage.VIDEO.value, service=f"fal {r['endpoint']}",
                                    description=f"f53ak:clip:foto{i}_K", units=r["ffprobe"]["duracion_s"],
                                    unit_label="s", cost_per_unit=0.0, total_cost=r["usd"])
    rc = cost_tracker.end_video()
    hechos = [clips_dir / f"foto{i}_K.mp4" for i in sorted(res) if (clips_dir / f"foto{i}_K.mp4").exists()]
    if hechos:
        mo.contactos(hechos, KDIR / "contactos.png")
    out = {"tipo_foto": {f"foto{i}": fotos[i][0] for i in fotos}, "gastado_antes": gastado,
           "peor_caso": round(PEOR_CASO, 2), "usd_prompts": round(rp.total_cost, 4) if rp else None,
           "usd_clips": round(rc.total_cost, 4) if rc else 0,
           "prompts": {f"foto{i}_K": {"prompt": t, **m} for i, (t, m) in prompts.items()},
           "clips": {f"foto{i}_K": r for i, r in sorted(res.items())}}
    (KDIR / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for i, r in sorted(res.items()):
        print(f"foto{i}_K", r.get("error") or f"{r['ffprobe']} · espera {r.get('espera_s')} s · US$ {r.get('usd')}")
    print(f"US$ prompts {out['usd_prompts']} · clips {out['usd_clips']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
