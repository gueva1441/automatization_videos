"""F78c Etapa B — lab de 5 fotos de Colza, TODO en lab/hyperframes/f78c/b/ (nada de producción se reemplaza).
1. md5 de output/<tid>/assets (todo), 03_visual.json y data/scripts/<tid>.json ANTES.
2. Casilleros de nuevo con Opus por la función de producción de una foto (`m03_visual._f8_refill`, nota vacía, mismo ancla y
   beat), con el bloque PERSONAS DOCUMENTADAS de la Etapa A (rasgos vigentes). `_f8_refill` arma con `armar_item` y no escribe
   nada; por las dudas `_persist` y `save_db` quedan bloqueados.
3. Referencia = la que da hoy la regla única (`_madres_para_item` con el guion vivo).
   V1 = prompt nuevo + Nano Banana 2 Lite /edit (las 5); V2 = prompt nuevo + Nano Banana 2 /edit completo (las 3 de Arcadio).
   Mismo payload que producción (`_generar_nb2`: frase de madres + prompt, aspect_ratio y safety_tolerance del perfil) pero SIN
   respaldo Seedream: un rechazo se anota. V0 = la foto actual de producción (sin costo).
4. md5 DESPUÉS y comparación; costo por servicio en b/costo.json.
Uso (venv): PYTHONIOENCODING=utf-8 <venv>/python lab/hyperframes/f78c/b/lab_f78c.py"""
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
import requests  # noqa: E402

import asset_manager as am  # noqa: E402
import fase1_5  # noqa: E402
from config import OUTPUT_DIR, DATA_DIR, pipeline  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402
from engine_profiles import select_profile  # noqa: E402
from script_engine import m03_visual as m3, m03_imagenes_v3 as v3img, m03_expediente as mexp  # noqa: E402

TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
AQUI = Path(__file__).parent
ASSETS = OUTPUT_DIR / TID / "assets"
FOTOS = ["ch01_img_01", "ch01_supp_05", "ch06_img_14", "ch04_img_12", "ch07_supp_07"]
ARCADIO = {"ch01_img_01", "ch01_supp_05", "ch06_img_14"}
# Motor completo (Nano Banana 2 /edit): id y precio leídos de fal.ai/models/fal-ai/nano-banana-2/edit/llms.txt el 2026-11-04
# (US$ 0,08 por imagen a 1K, la resolución por defecto, que es la que da Lite). Solo lab: no entra a producción.
NB2_FULL_EDIT = "fal-ai/nano-banana-2/edit"
NB2_FULL_USD = 0.08


def log(*a):
    print(time.strftime("[%H:%M:%S]"), *a, flush=True)


def md5s() -> dict:
    out = {str(p.relative_to(OUTPUT_DIR)): hashlib.md5(p.read_bytes()).hexdigest() for p in sorted(ASSETS.rglob("*")) if p.is_file()}
    for p in (m3.STEPS_DIR / TID / "03_visual.json", DATA_DIR / "scripts" / f"{TID}.json"):
        out[str(p)] = hashlib.md5(p.read_bytes()).hexdigest()
    return out


def bloquear(*a, **k):
    raise RuntimeError("F78c lab: escribir producción está bloqueado")


def contexto():
    """Topic y caps como los arma fase1_5 → m03 (assign_visual_prompts l.2082 y l.2111-2117), solo lectura."""
    topic = fase1_5._load_topic_by_id(TID)
    skel = fase1_5._load_skeleton(TID)
    narr = fase1_5._load_narration(TID)
    topic = {**topic, **m3._geo_era(TID, narr)}
    beats = v3img.load_beats(topic, m3.STEPS_DIR)
    topic = {**topic, "_f8": {"beats": beats, "year": v3img.topic_year(topic, beats), "lang": v3img.place_language(topic),
                              "fuentes": mexp.fuentes(TID, m3.STEPS_DIR),
                              "anio_prev": {n: mexp.anio_previo(narr["chapters"], n) for n in range(1, 8)}}}
    sk = {c["chapter_number"]: c for c in skel["chapters"]}
    nr = {c["chapter_number"]: (c.get("narration") or "").strip() for c in narr["chapters"]}
    vis = json.loads((m3.STEPS_DIR / TID / "03_visual.json").read_text(encoding="utf-8"))
    return topic, sk, nr, {c["chapter_number"]: c for c in vis["chapters"]}


def item_de(vc: dict, foto: str) -> tuple[int, dict, Path]:
    cap, kind, idx = int(foto[2:4]), foto.split("_")[1], int(foto.split("_")[2])
    ch = vc[cap]
    if foto == f"ch{cap:02d}_img_01" and isinstance(ch.get("image_f8"), dict):     # foto de arranque del clip
        return cap, {**ch["image_f8"], "prompt": ch.get("image_prompt", ""), "narration_anchor": ch["narration_anchor"]}, \
            ASSETS / f"ch{cap:02d}_veo" / f"{foto}.png"
    lista = ch["image_prompts"] if kind == "img" else ch["supplemental_image_prompts"]
    return cap, lista[idx - 1], ASSETS / f"ch{cap:02d}_flux" / f"{foto}.png"


def generar(endpoint: str, motor: str, prompt: str, refs: list[str], out: Path) -> dict:
    perfil = select_profile(am.MOTOR_PRINCIPAL)
    texto = f"{am.FRASE_EDIT_UNA if len(refs) == 1 else am.FRASE_EDIT_VARIAS} {prompt}" if refs else prompt
    payload = {"prompt": texto, "aspect_ratio": perfil.render.aspect_ratio, "safety_tolerance": perfil.render.safety_tolerance,
               "num_images": 1, "image_urls": [am._path_to_data_uri(p) for p in refs]}
    t0 = time.time()
    try:
        data = am._llamada_cola(motor, endpoint, payload, out)
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        return {"estado": "rechazo" if am._motivo_rechazo(body) else "error", "motivo": (am._motivo_rechazo(body) or body)[:400],
                "segundos": round(time.time() - t0, 1)}
    if not data.get("images"):
        return {"estado": "sin imagen", "motivo": json.dumps(data, ensure_ascii=False)[:400], "segundos": round(time.time() - t0, 1)}
    tam = am._bajar_foto(data, out)
    return {"estado": "ok", "path": str(out), "nativo": list(tam), "segundos": round(time.time() - t0, 1)}


def main() -> int:
    antes = md5s()
    (AQUI / "md5_antes.json").write_text(json.dumps(antes, indent=1), encoding="utf-8")
    m3._persist = bloquear
    fase1_5.save_db = bloquear
    cost_tracker.start_video("lab_f78c")       # solo en memoria: no se llama end_video (no escribe cost_history.json)
    topic, sk, nr, vc = contexto()
    script = json.loads((DATA_DIR / "scripts" / f"{TID}.json").read_text(encoding="utf-8"))

    def refill(foto):
        cap, item, v0 = item_de(vc, foto)
        new = m3._f8_refill(topic, sk[cap], nr[cap], item, cap, "")
        return foto, cap, item, new, v0

    with ThreadPoolExecutor(max_workers=len(FOTOS)) as ex:
        res = list(ex.map(refill, FOTOS))
    filas = {}
    for foto, cap, item, new, v0 in res:
        madres = am._madres_para_item(am._norm_persona(new.get("persona")), am._norm_foto_madre_refs(new.get("foto_madre_ref")),
                                      new.get("anio"), script["foto_madre_registry"], script["foto_madre_personas"],
                                      new.get("prompt") or "")
        filas[foto] = {"cap": cap, "v0": str(v0), "prompt_viejo": item.get("prompt"), "prompt_nuevo": new["prompt"],
                       "casilleros_viejos": json.loads(item["raw_llm_prompt"]) if item.get("raw_llm_prompt") else None,
                       "casilleros_nuevos": json.loads(new["raw_llm_prompt"]), "persona_vieja": item.get("persona"),
                       "persona_nueva": new.get("persona"), "anio": new.get("anio"),
                       "referencias": [{"ref": r, "path": p} for r, p in madres]}
        log(foto, "→ refs", [Path(p).name for _, p in madres])
    (AQUI / "prompts.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")

    lite = select_profile(am.MOTOR_PRINCIPAL).render.edit_model_id
    trabajos = [(f, "V1", lite, "nb2_lite") for f in FOTOS] + [(f, "V2", NB2_FULL_EDIT, "nb2_completo") for f in FOTOS if f in ARCADIO]

    def gen(t):
        foto, v, endpoint, motor = t
        refs = [r["path"] for r in filas[foto]["referencias"]]
        return foto, v, {"endpoint": endpoint, **generar(endpoint, motor, filas[foto]["prompt_nuevo"], refs, AQUI / v / f"{foto}.png")}

    with ThreadPoolExecutor(max_workers=min(len(trabajos), am.FLUX_MAX_WORKERS)) as ex:
        for foto, v, r in ex.map(gen, trabajos):
            filas[foto][v] = r
            log(foto, v, r["estado"], r.get("motivo", "")[:120])
    (AQUI / "resultados.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")

    opus = [e.__dict__ for e in cost_tracker.current_video.entries]
    n1 = sum(1 for f in filas.values() if (f.get("V1") or {}).get("estado") == "ok")
    n2 = sum(1 for f in filas.values() if (f.get("V2") or {}).get("estado") == "ok")
    costo = {"Anthropic Opus 5.5 (casilleros, 5 fotos)": round(sum(e["total_cost"] for e in opus), 4),
             f"Nano Banana 2 Lite /edit ({n1} fotos, {pipeline.costs['nb2_lite_per_image']} estimado de config)":
                 round(n1 * pipeline.costs["nb2_lite_per_image"], 4),
             f"Nano Banana 2 /edit completo ({n2} fotos, {NB2_FULL_USD} lista de fal a 1K)": round(n2 * NB2_FULL_USD, 4)}
    costo["total"] = round(sum(costo.values()), 4)
    (AQUI / "costo.json").write_text(json.dumps({"servicios": costo, "llamadas_opus": opus}, ensure_ascii=False, indent=1,
                                                default=str), encoding="utf-8")
    despues = md5s()
    (AQUI / "md5_despues.json").write_text(json.dumps(despues, indent=1), encoding="utf-8")
    dif = sorted(k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k))
    log(f"md5 producción: {len(antes)} archivos antes, {len(despues)} después, {len(dif)} distintos {dif[:5]}")
    log("costo", costo)
    return 0 if not dif else 3


if __name__ == "__main__":
    sys.exit(main())
