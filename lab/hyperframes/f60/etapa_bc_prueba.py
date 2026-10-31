# -*- coding: utf-8 -*-
"""F60 Etapas B+C — prueba en la copia lab/hyperframes/f60/base (HANDOFF_F60_BC_madre_secuencia_prod.md §Prueba).

NUNCA topics_db ni _steps ni output reales: los módulos de producción se importan y se les PARCHEAN las rutas
(foto_madre.OUTPUT_DIR/STEPS_DIR, asset_manager.OUTPUT_DIR, m06.STEPS_DIR/SCRIPTS_DIR/_load_topic); `config` no se toca,
`save_db` no se llama; se verifica con mtimes al final. PROHIBIDO process_script (pide clips): el runner llama directo a
la madre (generate_fotos_madre_personas), al pre-paso (_pre_paso_secuencia) y al camino de una foto (_generate_flux_image_at
con la regla única _madres_para_item), ítem por ítem, SOLO para las fotos con `persona` (caps flux + supps y foto inicial
de caps con clip). Cero clips.

Entradas: canon a3/05_visual_canon_a3.json inyectado al topic (CANON_KEYS, como en A3) y a3/03_visual_a3.json como
03_visual de la copia. Salidas en lab/hyperframes/f60/bc/ (output/ propio = fresco: todas las fotos con persona se generan).
Reanudable: el pre-paso reanuda por request_id (pedidos.json) y el camino de una foto salta lo que ya existe.

USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f60/etapa_bc_prueba.py
"""
from __future__ import annotations

import copy
import json
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F60 = Path(__file__).resolve().parent
BASE = F60 / "base"
A3 = F60 / "a3"
BC = F60 / "bc"
DRY = "--dry" in sys.argv          # corrida en seco: fal mockeado, salida a bc/dry_output, sin hojas
OUT = BC / ("dry_output" if DRY else "output")
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
VIDEO_ID_COSTO = "f60_bc_lab"
STEPS_COPIA = BASE / "data/scripts/_steps" / TID
SCRIPTS_COPIA = BASE / "data/scripts"
PROD = [ROOT / "data/topics_db.json", ROOT / "data/scripts" / f"{TID}.json", ROOT / "data/scripts/_steps" / TID,
        ROOT / "output" / TID]

LOG: list[str] = []
_LOCK = Lock()


def log(s: str) -> None:
    with _LOCK:
        print(s, flush=True)
        LOG.append(s)


def mtimes(paths: list[Path]) -> dict[str, tuple[int, float]]:
    """{ruta: (archivos, mtime máxima)} para comparar antes/después."""
    out = {}
    for p in paths:
        if p.is_dir():
            fs = [f for f in p.rglob("*") if f.is_file()]
            out[str(p)] = (len(fs), max((f.stat().st_mtime for f in fs), default=0.0))
        elif p.exists():
            out[str(p)] = (1, p.stat().st_mtime)
        else:
            out[str(p)] = (0, 0.0)
    return out


def main() -> int:
    BC.mkdir(exist_ok=True)
    antes = mtimes(PROD)

    import asset_manager as am
    import foto_madre as fm
    import fase2a
    from script_engine import m06_assembler as m6
    from fase1_5 import _load_topic_by_id, CANON_KEYS
    from config import api
    from cost_tracker import cost_tracker

    assert api.image_engine == "seedream", f"motor activo {api.image_engine!r}: la prueba es de Seedream"
    if DRY:
        PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
        shutil.rmtree(OUT, ignore_errors=True)

        def _fm(prompt, dest):
            dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(PNG)
            return {"endpoint": "DRY", "path": str(dest), "seed": 0, "nsfw": None, "request_id": "dry"}

        def _sec(video_id, prompts, refs, madre_paths, out_paths):
            am._guardar_pedido(video_id, am._clave_lote(prompts, refs), {"request_id": "dry", "n": len(prompts), "refs": refs,
                               "fotos": [p.name for p in out_paths], "devueltas": len(prompts), "segundos": 0})
            for p in out_paths:
                p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(PNG)
            return list(out_paths)

        def _una(prompt, art, path, use_ultra, seed=None, foto_madre_data_uris=None):
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(PNG)
            return {"flux_meta": {"endpoint": f"DRY edit×{len(foto_madre_data_uris or [])}"}}
        fm._generate_madre_seedream = _fm
        am._llamar_secuencia = _sec
        am._generate_flux_image_at = _una
        am._path_to_data_uri = lambda p: "data:dry"
    res: dict = {"tid": TID, "hora": datetime.now().isoformat(timespec="seconds"), "fotos_por_llamada": am.FOTOS_POR_LLAMADA,
                 "submit_timeout_s": am.FAL_SUBMIT_TIMEOUT_S, "poll_timeout_s": am.CLIP_POLL_TIMEOUT,
                 "flux_max_workers": am.FLUX_MAX_WORKERS, "ropa_madre": fm.ROPA_MADRE}

    # ── entradas: 03_visual de A3 a la copia (respaldo del que había) ──
    v03 = STEPS_COPIA / "03_visual.json"
    if v03.exists() and not (BC / "03_visual_copia_antes.json").exists():
        shutil.copy2(v03, BC / "03_visual_copia_antes.json")
    shutil.copy2(A3 / "03_visual_a3.json", v03)
    guion_copia = SCRIPTS_COPIA / f"{TID}.json"
    if guion_copia.exists() and not (BC / "guion_copia_antes.json").exists():
        shutil.copy2(guion_copia, BC / "guion_copia_antes.json")
    canon_a3 = json.loads((A3 / "05_visual_canon_a3.json").read_text(encoding="utf-8"))
    topic = copy.deepcopy(_load_topic_by_id(TID))
    topic.update({k: copy.deepcopy(canon_a3[k]) for k in CANON_KEYS})
    log(f"topic {TID} con el canon A3 inyectado ({list(CANON_KEYS)}); central_subject kind={topic.get('central_subject', {}).get('kind')!r}")

    # ── rutas parcheadas (nunca config) ──
    fm.OUTPUT_DIR = OUT
    fm.STEPS_DIR = STEPS_COPIA.parent
    am.OUTPUT_DIR = OUT
    m6.STEPS_DIR = STEPS_COPIA.parent
    m6.SCRIPTS_DIR = SCRIPTS_COPIA
    m6._load_topic = lambda tid: topic
    cost_tracker.start_video(video_id=VIDEO_ID_COSTO)

    # ── 1. madres por persona (Seedream t2i por la cola) ──
    t0 = time.time()
    est = fm.generate_fotos_madre_personas(topic, TID)
    res["madres"] = est
    res["segundos_madres"] = round(time.time() - t0, 1)
    log(f"\nMADRES ({res['segundos_madres']} s de pared):")
    for name, e in est.items():
        log(f"  {name}: {e['fotos']} fotos {e.get('fotos_ids')} → {e.get('estado')}" + (f" · {Path(e['dest']).name}" if e.get("dest") else ""))
    for name, e in est.items():
        if e.get("prompt"):
            log(f"\nPROMPT MADRE {name}:\n{e['prompt']}")

    # ── 2. m06 → guion de la copia → adaptador de fase2a ──
    guion_path = m6.assemble_final_script(TID)
    script = json.loads(guion_path.read_text(encoding="utf-8"))
    registry = script["foto_madre_registry"]
    personas = script["foto_madre_personas"]
    res["registry"] = registry
    res["foto_madre_personas"] = personas
    log(f"\nm06 → {guion_path.relative_to(ROOT)} · registry {list(registry)} · image_f8 en caps {[c['chapter_number'] for c in script['chapters'] if 'image_f8' in c]}")
    norm = fase2a._normalize_long(script)
    assert norm["foto_madre_personas"] == personas and all(c.get("image_f8") is not None for c in norm["chapters"] if c["render_engine"] == "veo")

    # ── 3. pre-paso de secuencia (una vez, antes de los caps) ──
    t0 = time.time()
    secuencia = am._pre_paso_secuencia(norm["chapters"], TID, registry, personas)
    res["segundos_pre_paso"] = round(time.time() - t0, 1)
    pedidos = am._leer_pedidos(TID)
    res["pedidos"] = pedidos
    log(f"\nPRE-PASO: {len(secuencia)} fotos por secuencia en {res['segundos_pre_paso']} s de pared · {len(pedidos)} lote(s) pedidos")
    for clave, ped in pedidos.items():
        log(f"  lote {clave[:8]} {ped.get('refs')}: {ped.get('n')} pedidas / {ped.get('devueltas')} devueltas · {ped.get('segundos')} s · {ped.get('fotos')}")

    # ── 4. camino de una foto, ítem por ítem, SOLO fotos con persona que no salieron por secuencia ──
    trabajos = []
    filas: list[dict] = []
    for ch in norm["chapters"]:
        cid = ch["id"]
        use_ultra = am._is_hook_chapter(cid)
        if ch["render_engine"] == "flux":
            d = am._chapter_dir(TID, cid, "flux")
            for it in am._iter_image_items(ch):
                if not it["persona"]:
                    continue
                clave = (cid, "img", it["idx"])
                path = d / am._image_filename(cid, it["idx"])
                madres = am._madres_para_item(it["persona"], it["foto_madre_refs"], it["anio"], registry, personas)
                filas.append({"clave": list(clave), "file": path.name, "persona": it["persona"], "anio": it["anio"],
                              "madres": [r for r, _ in madres], "path": path, "prompt": it["prompt"], "use_ultra": use_ultra,
                              "seed": am._seed_for_subject(TID, it["subject_ref"])})
        else:
            f8 = ch.get("image_f8") or {}
            per = am._norm_persona(f8.get("persona"))
            if per:
                path = am._chapter_dir(TID, cid, "veo") / am._image_filename(cid, 1)
                madres = am._madres_para_item(per, am._norm_foto_madre_refs(f8.get("foto_madre_ref")), f8.get("anio"), registry, personas)
                filas.append({"clave": [cid, "f8", 1], "file": path.name, "persona": per, "anio": f8.get("anio"),
                              "madres": [r for r, _ in madres], "path": path, "prompt": ch["image_prompts"][0], "use_ultra": use_ultra,
                              "seed": None})
            d = am._chapter_dir(TID, cid, "flux")
            for idx, s in enumerate(ch.get("supplemental_image_prompts") or [], start=1):
                per = am._norm_persona(s.get("persona"))
                if not per:
                    continue
                path = d / f"{cid}_supp_{idx:02d}.png"
                madres = am._madres_para_item(per, am._norm_foto_madre_refs(s.get("foto_madre_ref")), s.get("anio"), registry, personas)
                filas.append({"clave": [cid, "supp", idx], "file": path.name, "persona": per, "anio": s.get("anio"),
                              "madres": [r for r, _ in madres], "path": path, "prompt": str(s.get("prompt") or ""), "use_ultra": use_ultra,
                              "seed": None})
    for f in filas:
        sec = secuencia.get(tuple(f["clave"]))
        if sec:
            f["camino"] = "secuencia"
            f["lote"] = sec["lote"]
            f["segundos"] = sec.get("segundos_lote")
        elif f["path"].exists():
            f["camino"] = "ya existía (reanudado)"
        elif f["madres"]:
            f["camino"] = "una foto (/edit)"
            trabajos.append(f)
        else:
            f["camino"] = "una foto sin madre" + (" por era" if any(not am.persona_aporta_madre(personas.get(p), f["anio"]) for p in f["persona"]) else " (sin madre en registry)")
            trabajos.append(f)
    log(f"\nCAMINO DE UNA FOTO: {len(trabajos)} fotos a pedir (de {len(filas)} con persona)")

    def una(f):
        t0 = time.time()
        uris = [am._path_to_data_uri(registry[r]) for r in f["madres"]] or None
        meta = am._generate_flux_image_at(f["prompt"], "", f["path"], f["use_ultra"], f["seed"], uris)
        return meta, round(time.time() - t0, 1)

    t_pared = time.time()
    with ThreadPoolExecutor(max_workers=min(max(len(trabajos), 1), am.FLUX_MAX_WORKERS)) as ex:
        futs = {ex.submit(una, f): f for f in trabajos}
        for fut in as_completed(futs):
            f = futs[fut]
            try:
                meta, seg = fut.result()
                f["segundos"] = seg
                f["endpoint"] = (meta.get("flux_meta") or {}).get("endpoint")
                f["nsfw"] = (meta.get("flux_meta") or {}).get("nsfw_flag")
                log(f"  ✓ {f['file']} {f['camino']} madres={f['madres']} · {seg} s · {f['endpoint']}")
            except Exception as e:  # noqa: BLE001 — sin reintento, texto literal
                f["error"] = f"{type(e).__name__}: {str(e)[:400]}"
                log(f"  ✗ {f['file']} {f['camino']}: {f['error']}")
    res["segundos_pared_una_foto"] = round(time.time() - t_pared, 1)

    # ── 5. costo ──
    rep = cost_tracker.end_video()
    res["costo"] = {"total_usd": round(rep.total_cost, 4) if rep else None,
                    "entradas": [{"service": e.service, "units": e.units, "cost": round(e.total_cost, 4), "desc": e.description[:80]}
                                 for e in (rep.entries if rep else [])]}
    log(f"\nCOSTO cost_tracker: US$ {res['costo']['total_usd']} ({len(res['costo']['entradas'])} entradas)")

    # ── 6. tabla foto → camino → lote → tiempo ──
    for f in filas:
        f["path"] = str(f["path"].relative_to(ROOT))
        f["existe"] = (ROOT / f["path"]).exists()
    res["fotos"] = filas
    log("\nTABLA foto → camino → lote → s")
    for f in filas:
        log(f"  {f['file']:<20} {str(f['persona']):<42} {str(f['anio']):<6} {f['camino']:<30} {f.get('lote') or '-':<22} {f.get('segundos') or '-'}  {'OK' if f['existe'] else 'FALTA'}")

    # ── 7. hojas de contacto por persona (madre + sus fotos) ──
    from PIL import Image, ImageDraw
    W, H = 512, 288
    hojas = {}
    for name in ([] if DRY else registry):
        mias = [f for f in filas if name in f["persona"]]
        if not mias:
            continue
        cols = 4
        filas_n = (len(mias) + cols) // cols
        hoja = Image.new("RGB", (cols * (W + 10) + 10, (filas_n + 0) * (H + 30) + 10), (18, 18, 18))
        d = ImageDraw.Draw(hoja)
        celdas = [("MADRE " + name, ROOT / Path(registry[name]).relative_to(ROOT) if str(registry[name]).startswith(str(ROOT)) else Path(registry[name]))] + \
                 [(f"{f['file']} · {f['camino'][:14]} · {f['anio']}", ROOT / f["path"]) for f in mias]
        for i, (etiq, p) in enumerate(celdas):
            x, y = 10 + (i % cols) * (W + 10), 10 + (i // cols) * (H + 30)
            if p.exists():
                hoja.paste(Image.open(p).convert("RGB").resize((W, H)), (x, y + 20))
            else:
                d.text((x + 5, y + H // 2), "(sin foto)", fill=(140, 140, 140))
            d.text((x, y + 4), etiq, fill=(255, 255, 0))
        hp = BC / f"hoja_{fm._slug(name)}.jpg"
        hoja.save(hp, quality=85)
        hojas[name] = str(hp.relative_to(ROOT))
    res["hojas"] = hojas
    log(f"\nHOJAS: {list(hojas.values())}")

    # ── 8. mtimes: nada fuera de la copia cambió ──
    despues = mtimes(PROD)
    res["mtimes_antes"] = antes
    res["mtimes_despues"] = despues
    res["produccion_intacta"] = antes == despues
    log(f"\nPRODUCCIÓN INTACTA (mtimes iguales): {res['produccion_intacta']}")
    for k in antes:
        if antes[k] != despues[k]:
            log(f"  CAMBIÓ: {k} {antes[k]} → {despues[k]}")

    res["log"] = LOG
    (BC / "etapa_bc.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (BC / "etapa_bc.log").write_text("\n".join(LOG), encoding="utf-8")
    return 0 if res["produccion_intacta"] and not any(f.get("error") for f in filas) else 1


if __name__ == "__main__":
    sys.exit(main())
