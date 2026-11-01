"""F68b Etapa 1: mueve los 2 clips viejos al archivo y rehace ch01 y ch07 en paralelo con `_generate_clip` (G → K), desde las
fotos de F68. No genera fotos: si falta una, frena. Si un clip ya se rehizo (el viejo está en el archivo y el nuevo en assets), no lo paga de nuevo.
Salida: clips_llamadas.json (motor, rechazos, prompt, segundos, costo) y el manifest actualizado solo en las filas de los clips."""
import hashlib
import json
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import asset_manager as am  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402

TOPIC = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
CAPS = {"ch01": 1, "ch07": 7}
AQUI = Path(__file__).resolve().parent
TOPIC_DIR = am.OUTPUT_DIR / TOPIC
ASSETS = TOPIC_DIR / "assets"
ARCHIVO = TOPIC_DIR / "_archivo_seedream5lite" / "clips"
MANIFEST = ASSETS / "assets_manifest.json"


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def fila(man: dict, cap: str) -> dict:
    return next(c for c in man["chapters"] if c.get("id") == cap)["clips"][0]


def rehacer(cap: str, man: dict, guion: dict) -> dict:
    veo = ASSETS / f"{cap}_veo"
    clip, foto, final = veo / f"{cap}_clip_01.mp4", veo / f"{cap}_img_01.png", veo / f"{cap}_img_01_final.png"
    viejo = ARCHIVO / clip.name
    log: list = []
    if viejo.exists() and clip.exists():
        return {"cap": cap, "ok": True, "reusado": True, "log": []}
    if clip.exists():
        shutil.move(str(clip), str(viejo))
    f = fila(man, cap)
    ch = next(c for c in guion["chapters"] if c.get("chapter_number") == CAPS[cap])
    if ch["video_prompt"] != f["video_prompt"]:
        raise ValueError(f"{cap}: el video_prompt del manifest no es el del guion")
    try:
        am._generate_clip(foto, f["video_prompt"], clip, image_prompt=f["image_prompt"], ancla=ch["voz_clip"].strip(),
                          foto_final=final, log=log)
        return {"cap": cap, "ok": True, "log": log}
    except Exception as e:  # noqa: BLE001 — el otro clip sigue; no hay foto de respaldo (regla 1)
        return {"cap": cap, "ok": False, "error": f"{type(e).__name__}: {e}"[:900], "log": log}


def main() -> int:
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    guion = json.loads((Path("data/scripts") / f"{TOPIC}.json").read_text(encoding="utf-8"))
    fotos = [ASSETS / f"{c}_veo" / f"{c}_img_01{s}.png" for c in CAPS for s in ("", "_final")]
    if faltan := [p.name for p in fotos if not p.exists()]:
        raise SystemExit(f"faltan fotos, no se generan: {faltan}")
    antes = {p.name: md5(p) for p in fotos}
    ARCHIVO.mkdir(parents=True, exist_ok=True)
    cost_tracker.start_video(video_id=TOPIC)

    with ThreadPoolExecutor(max_workers=len(CAPS)) as ex:
        res = list(ex.map(lambda c: rehacer(c, man, guion), CAPS))

    despues = {p.name: md5(p) for p in fotos}
    # F68b regla 5: solo las filas de los clips rehechos; el resto del manifest, el sello y la fecha no cambian
    for r in res:
        if not r["ok"] or r.get("reusado"):
            continue
        cap, ultimo = r["cap"], r["log"][-1]
        f = fila(man, cap)
        f.pop("foto_de_arranque_cambio", None)
        f.update({"status": "ok", "foto_arranque_md5": despues[f"{cap}_img_01.png"],
                  "foto_final_md5": despues[f"{cap}_img_01_final.png"], "clip_motor": ultimo["motor"],
                  "clip_rechazos": ultimo["rechazos"], "clip_segundos": ultimo["segundos"], "clip_usd": ultimo["usd"]})
    tmp = MANIFEST.with_name(MANIFEST.name + ".tmp")
    tmp.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(MANIFEST)

    entradas = [{"servicio": e.service, "descripcion": e.description, "usd": e.total_cost, "unidades": e.units,
                 "tokens_in": e.tokens_in, "tokens_out": e.tokens_out} for e in cost_tracker.current_video.entries]
    (AQUI / "clips_llamadas.json").write_text(json.dumps(
        {"resultados": res, "costos": entradas, "usd_total": sum(e["usd"] for e in entradas),
         "fotos_antes": antes, "fotos_despues": despues, "fotos_iguales": antes == despues},
        ensure_ascii=False, indent=1), encoding="utf-8")
    for r in res:
        print(r["cap"], "OK" if r["ok"] else f"FALLO {r['error']}", [(x.get("motor"), len(x.get("rechazos", []))) for x in r["log"]])
    print("fotos iguales:", antes == despues, "| usd:", round(sum(e["usd"] for e in entradas), 4))
    return 0 if all(r["ok"] for r in res) and antes == despues else 1


if __name__ == "__main__":
    raise SystemExit(main())
