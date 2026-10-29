# -*- coding: utf-8 -*-
"""F53a — un reintento de foto2_G: la 1.ª llamada dio HTTP 504 `downstream_service_unavailable` (falla del servicio, no
respuesta de moderación). Mismo prompt (el de `resultado.json`), misma foto y mismos campos, por `moderacion.py` /
`f52/prueba_video.correr`. Guarda de tope antes. Agrega el resultado a `resultado.json` como `foto2_G_reintento` y rehace
`contactos.png` con los clips que haya.
Uso: python lab/hyperframes/f53a/reintento_g2.py
"""
import json
import sys
from pathlib import Path

F53A = Path(__file__).resolve().parent
sys.path.insert(0, str(F53A))
import moderacion as mo          # noqa: E402

PEOR_G = mo.DUR * 0.15           # handoff F53a: G a ×5 del precio leído


def main() -> int:
    res_p = F53A / "resultado.json"
    d = json.loads(res_p.read_text(encoding="utf-8"))
    if "foto2_G_reintento" in d["clips"]:
        print("ya se reintentó")
        return 1
    previo = d["clips"]["foto2_G"]
    assert "504" in (previo.get("error") or ""), "foto2_G no fue un 504: no se reintenta"
    gastado, tope = mo.pr.gastado_desde_tope()
    print(f"gastado {gastado} · peor caso del reintento {PEOR_G:.2f} · tope {tope}")
    if gastado + PEOR_G >= tope:
        print("PARADA: el reintento pasaría el tope")
        return 1
    clips_dir = F53A / "clips"
    mo.pr.CLIPS, mo.pr.payload, mo.pr.F52 = clips_dir, mo.payload_f53a, F53A
    _, _, uri = mo.foto(F53A / "fotos" / d["elegidas"][1]["archivo"])
    r = mo.pr.correr(2, "G", d["prompts"]["foto2_G"]["prompt"], uri)
    src = clips_dir / "cap02_G.mp4"
    if src.exists():
        dst = clips_dir / "foto2_G.mp4"
        src.replace(dst)
        r["archivo"] = str(dst.relative_to(F53A))
    r["clip"] = "foto2_G_reintento"
    if r.get("usd"):
        from cost_tracker import cost_tracker
        from error_handler import PipelineStage
        cost_tracker.start_video("f53a_lab_clips_reintento")
        cost_tracker._add_entry(stage=PipelineStage.VIDEO.value, service=f"fal {r['endpoint']}",
                                description="f53a:clip:foto2_G_reintento", units=r["ffprobe"]["duracion_s"],
                                unit_label="s", cost_per_unit=0.0, total_cost=r["usd"])
        cost_tracker.end_video()
    d["clips"]["foto2_G_reintento"] = r
    res_p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    hechos = sorted(clips_dir.glob("foto*.mp4"))
    if hechos:
        mo.contactos(hechos, F53A / "contactos.png")
    print("foto2_G_reintento", r.get("error") or f"{r['ffprobe']} · espera {r.get('espera_s')} s · US$ {r.get('usd')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
