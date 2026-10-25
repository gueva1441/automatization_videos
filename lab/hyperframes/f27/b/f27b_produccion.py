"""F27 §B — Vajont desde m03 hasta el mp4, con el runner de F26 (`lab/hyperframes/f26/b/f26b_produccion.py`: topic,
partición, voz y música ya hechos en F26 y reusados, sin volver a pagar) y los arreglos de F27 §A.

Etapas (log en lab/hyperframes/f27/b/produccion.log, costos en costos_f27b.json, tope Gemini US$ 4 propio de F27):
    guion      plan de imágenes como en F26 (92 a 10.75 s por imagen, por la duración real) → m03 (hasta 3 intentos, cada
               uno con su freno y su traceback) → paso0 (foto madre) → assemble (`data/scripts/f8s3-vajont.json`).
    imagenes   fase2a en este proceso (`fase2a.main`, `--topic f8s3-vajont`) con un contador sobre
               `asset_manager._generate_image_raw`: a la imagen 101 (re-hechuras del guardia de visión incluidas) corta.
    render     Firefox cerrado y RAM libre > 14 GB; fase2b con gfx (identidad `misterio`). Si falla → render_sin_gfx.
    render_sin_gfx  fase2b sin gfx.
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f27/b/f27b_produccion.py --etapa <etapa>
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LAB = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / "lab" / "hyperframes" / "f26" / "b")]
import f26b_produccion as f26b  # noqa: E402

# el runner de F26 con los archivos y el tope de F27
f26b.LAB = LAB
f26b.COSTOS = LAB / "costos_f27b.json"
f26b.TOPE_GEMINI = 4.00
TID = f26b.TID
M03_INTENTOS = 3
TOPE_IMAGENES = 100
Parada = f26b.Parada


def guion(log: list[str]) -> None:
    import json
    import fase1_5 as f15
    from script_engine import m03_visual as mv
    from script_engine.m06_assembler import assemble_final_script
    sm = json.loads((ROOT / "output" / "audio" / TID / "sync_map.json").read_text(encoding="utf-8"))
    if not (ROOT / "output" / "audio" / TID / "music_map.json").exists():
        raise Parada("falta la voz/música de F26 (output/audio/f8s3-vajont): F27 no la vuelve a pagar")
    spi, plan = f26b._plan_imagenes(sm)
    mv.SECONDS_PER_IMAGE_TARGET = spi
    f26b._w(LAB / "plan_imagenes.json", plan)
    log.append(f"guion: voz y música de F26 reusadas; plan de imágenes {plan['total']} ({plan['por_cap']}) a {spi} s")
    topic = f15._load_topic_by_id(TID)
    skeleton, narration = f15._load_skeleton(TID), f15._load_narration(TID)
    for k in range(1, M03_INTENTOS + 1):
        f26b._freno_gemini(1.50, f"m03 intento {k}")
        t0 = time.time()
        try:
            f15.assign_visual_prompts(topic, skeleton, narration, sync_map=sm)
        except Exception as e:  # noqa: BLE001
            (LAB / f"m03_traceback_{k}.txt").write_text(traceback.format_exc(), encoding="utf-8")
            f26b._anotar_costos(f"m03_intento{k}", {"error": f"{type(e).__name__}: {e}", "s": round(time.time() - t0)})
            log.append(f"guion: m03 intento {k} FALLÓ: {type(e).__name__}: {str(e)[:300]}")
            if k == M03_INTENTOS:
                raise Parada(f"m03: {M03_INTENTOS} intentos fallidos")
            continue
        f26b._anotar_costos(f"m03_intento{k}", {"plan_imagenes": plan, "s": round(time.time() - t0)})
        log.append(f"guion: m03 intento {k} OK en {time.time() - t0:.0f} s")
        break
    db = f15.load_db()
    for t in db.get("topics", []):
        if t.get("id") == TID:
            f15.generate_foto_madre_for_topic(t, TID)
            f15.save_db(db)
            break
    final = assemble_final_script(TID)
    log.append(f"guion: paso0 + assemble → {final}")
    f26b._anotar_costos("paso0_assemble")


def imagenes(log: list[str]) -> int:
    import asset_manager as am
    import fase2a
    cuenta = {"n": 0, "cortadas": 0}
    lock = threading.Lock()
    crudo = am._generate_image_raw

    def contada(*a, **k):
        with lock:
            if cuenta["n"] >= TOPE_IMAGENES:
                cuenta["cortadas"] += 1
                raise RuntimeError(f"F27: tope de {TOPE_IMAGENES} imágenes (re-hechuras incluidas)")
            cuenta["n"] += 1
        return crudo(*a, **k)
    am._generate_image_raw = contada
    sys.argv = ["fase2a.py", "--topic", TID]
    t0 = time.time()
    try:
        rc = fase2a.main()
    finally:
        f26b._anotar_costos("imagenes", {"imagenes_pedidas": cuenta["n"], "cortadas_por_tope": cuenta["cortadas"],
                                         "s": round(time.time() - t0)})
    log.append(f"imagenes: fase2a rc={rc} · {cuenta['n']} imágenes pedidas al motor (tope {TOPE_IMAGENES}; "
               f"{cuenta['cortadas']} cortadas por el tope) · {(time.time() - t0) / 60:.1f} min")
    return int(rc or 0)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--etapa", choices=["guion", "imagenes", "render", "render_sin_gfx"], required=True)
    a = ap.parse_args()
    log = [f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] F27 §B Vajont · etapa {a.etapa}"]
    rc = 0
    try:
        if a.etapa == "guion":
            guion(log)
        elif a.etapa == "imagenes":
            rc = imagenes(log)
        else:
            ram, ff = f26b._ram_free_gb(), f26b._firefox_open()
            log.append(f"render: RAM libre {ram:.1f} GB · Firefox {'ABIERTO' if ff else 'cerrado'}")
            if ff or ram <= 14:
                log.append("render: NO arranca (regla de Omar: Firefox cerrado y RAM > 14 GB)")
                rc = 3
            elif a.etapa == "render":
                rc = f26b._run([sys.executable, "fase2b.py", TID, "--keep-segments", "--gfx", "--gfx-sparse",
                                "--gfx-quality", "looks"], log, "fase2b")
            else:
                rc = f26b._run([sys.executable, "fase2b.py", TID, "--keep-segments"], log, "fase2b_sin_gfx")
    except Parada as e:
        log.append(f"PARADA: {e}")
        rc = 2
    finally:
        with (LAB / "produccion.log").open("a", encoding="utf-8") as fh:
            fh.write("\n".join(log) + "\n")
        print("\n".join(log), flush=True)
    sys.exit(rc)


if __name__ == "__main__":
    main()
