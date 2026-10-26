"""F29b §A — las dos crudas de ejemplo del rotulista (ch03 y ch06 de Vajont) y los fixtures de los tests, SIN render.

Arma la entrada de cada cap con el mismo código que apply_gfx (gfx_rotulista.preparar_cap: oraciones de la voz,
beats de la escaleta, ítems, ya mostrado, pico) sobre el topic de v3 (`f8s3-vajont-f29`), llama al rotulista (Sonnet
5.5, effort medium) en paralelo y guarda en `lab/hyperframes/f29b/a/`:
    rotulista_chNN.raw.json   pedido, respuesta cruda de la API, validación A.4 de cada intento
    rotulista_costos.json     tokens y US$ por llamada (tope de la tanda: US$ 2 entre A y B)
y en `lab/hyperframes/f29b/fixtures/`: entrada + palabras con tiempos + respuesta (la primera) de cada cap, más la
intensidad cacheada de ch06 (para el test del pico único).
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f29b/a/f29b_crudas.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
FIX = LAB.parent / "fixtures"
VID = "f8s3-vajont-f29"
CAPS = ("ch03", "ch06")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import fase2b
    from config import OUTPUT_DIR
    from script_engine import gfx_rotulista as gro
    audio_dir = OUTPUT_DIR / "audio" / VID
    sync = json.loads((audio_dir / "sync_map.json").read_text(encoding="utf-8"))
    man = json.loads((OUTPUT_DIR / VID / "assets" / "assets_manifest.json").read_text(encoding="utf-8"))
    plans = [p for p in fase2b._build_plans(sync, man, VID, audio_dir, fase2b._load_script_lookup(VID))
             if p.chapter_id in CAPS]
    LAB.mkdir(parents=True, exist_ok=True)
    FIX.mkdir(parents=True, exist_ok=True)
    res = gro.prefetch(plans, VID, LAB, {p.chapter_id: 0.0 for p in plans}, tope=2.0)
    print(json.dumps(res, ensure_ascii=False), flush=True)
    for p in plans:
        cap = p.chapter_id
        got = gro.preparar_cap(p, VID, LAB, 0.0)
        ent, words, _ = got
        raw = json.loads((LAB / f"rotulista_{cap}.raw.json").read_text(encoding="utf-8"))
        (FIX / f"rotulista_{cap}_entrada.json").write_text(json.dumps(
            {"entrada": ent, "words": [{k: w.get(k) for k in ("word", "start", "end")} for w in words]},
            ensure_ascii=False, indent=1), encoding="utf-8")
        (FIX / f"rotulista_{cap}_respuesta.json").write_text(json.dumps(
            {"modelo": raw["modelo"], "respuesta": raw["intentos"][0]["respuesta"],
             "cruda": (raw["intentos"][0]["crudas"] or [{}])[0].get("respuesta")}, ensure_ascii=False, indent=1),
            encoding="utf-8")
    src = OUTPUT_DIR / VID / "_fase2b_work" / "gfx_intensity_ch06.json"
    if src.exists():
        shutil.copy2(src, FIX / "gfx_intensity_ch06.json")
    c = json.loads((LAB / "rotulista_costos.json").read_text(encoding="utf-8"))
    print(f"Claude US$ {c['usd']} · {len(c['llamadas'])} llamada(s)", flush=True)


if __name__ == "__main__":
    main()
