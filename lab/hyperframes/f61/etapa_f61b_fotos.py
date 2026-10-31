# -*- coding: utf-8 -*-
"""F61b — 10 fotos de los planos medios con persona (HANDOFF_F61b_fotos_medio.md): prompts TAL CUAL de
f61/03_visual_f61.json, una foto por llamada con las funciones de producción de F60 (asset_manager._madres_para_item con
persona_aporta_madre adentro; Seedream /edit con las madres o t2i sin madre), madres de la prueba F60 B+C (no se generan
nuevas), las 10 a la vez (tope FLUX_MAX_WORKERS), cost_tracker con id de lab «lab_f61b». Salidas en f61/b/. Producción
intacta: mismo control de mtimes que f60/etapa_bc_prueba.py. Ningún módulo de producción se toca.
USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f61/etapa_f61b_fotos.py
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F61 = Path(__file__).resolve().parent
B = F61 / "b"
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
VIDEO_ID_COSTO = "lab_f61b"
MADRES_DIR = ROOT / "lab/hyperframes/f60/bc/output" / TID / "foto_madre"
CANON_A3 = ROOT / "lab/hyperframes/f60/a3/05_visual_canon_a3.json"
VISUAL = F61 / "03_visual_f61.json"
PROD = [ROOT / "data/topics_db.json", ROOT / "data/scripts" / f"{TID}.json", ROOT / "data/scripts/_steps" / TID, ROOT / "output" / TID]
# tabla del handoff: (ítem, plano, persona, año)
TABLA = [
    (1, (0, "supplemental_image_prompts", 0), "medium", ["Daniel Écija", "María Bernal"], "1962"),
    (2, (0, "supplemental_image_prompts", 1), "medium", ["Daniel Écija"], "1962"),
    (3, (1, "image_prompts", 1), "medium", ["Daniel Écija", "María Bernal"], "1962"),
    (4, (1, "image_prompts", 5), "medium", ["Milagros Barroso", "Ramón de Juan"], "1962"),
    (5, (1, "image_prompts", 7), "medium", ["Víctor Calvo"], "1962"),
    (6, (2, "image_prompts", 5), "close", ["Eric Saint"], "1948"),
    (7, (3, "image_prompts", 9), "medium", ["Daniel Écija"], "1962"),
    (8, (3, "image_prompts", 12), "medium", ["María Bernal", "Daniel Écija"], "1963"),
    (9, (4, "image_prompts", 12), "medium", ["Daniel Écija"], "1991"),
    (10, (4, "image_prompts", 7), "close", ["Daniel Écija hijo"], "1985"),
]
LOG: list[str] = []


def log(s):
    print(s, flush=True)
    LOG.append(s)


def mtimes(paths):
    out = {}
    for p in paths:
        if p.is_dir():
            fs = [f for f in p.rglob("*") if f.is_file()]
            out[str(p)] = (len(fs), max((f.stat().st_mtime for f in fs), default=0.0))
        else:
            out[str(p)] = (1, p.stat().st_mtime) if p.exists() else (0, 0.0)
    return out


def main() -> int:
    B.mkdir(exist_ok=True)
    antes = mtimes(PROD)
    import asset_manager as am
    import foto_madre as fm
    from config import api
    from cost_tracker import cost_tracker
    assert api.image_engine == "seedream"
    v = json.loads(VISUAL.read_text(encoding="utf-8"))
    canon = json.loads(CANON_A3.read_text(encoding="utf-8"))
    personas_canon = {p["name"]: {"era": p.get("era") or "", "condition_by_period": p.get("condition_by_period") or []}
                      for p in canon["documented_people"]}
    registry = {p.stem: str(p) for p in MADRES_DIR.glob("*.png")}
    registry = {name: registry[fm._slug(name)] for name in personas_canon if fm._slug(name) in registry}   # {nombre canon: madre}
    log(f"madres F60 B+C: {sorted(registry)}")
    # ── verificación de la tabla (PARÁ si no coincide) ──
    fotos = []
    for n, (k, key, i), sc, per, an in TABLA:
        try:
            it = v["chapters"][k][key][i]
        except (IndexError, KeyError) as e:
            log(f"PARÁ: #{n} chapters[{k}].{key}[{i}] no existe ({e})")
            return 2
        if it.get("shot_scale") != sc or it.get("persona") != per or str(it.get("anio")) != an:
            log(f"PARÁ: #{n} no coincide: plano {it.get('shot_scale')} persona {it.get('persona')} año {it.get('anio')} vs tabla {sc} {per} {an}")
            return 2
        madres = am._madres_para_item(it["persona"], am._norm_foto_madre_refs(it.get("foto_madre_ref")), it.get("anio"), registry, personas_canon)
        fotos.append({"n": n, "ref": f"chapters[{k}].{key}[{i}]", "file": f"f61b_{n:02d}.png", "plano": sc, "persona": per, "anio": an,
                      "ancla": it.get("narration_anchor"), "prompt": it["prompt"], "madres": [r for r, _ in madres],
                      "madres_paths": [p for _, p in madres], "cap": k + 1, "use_ultra": am._is_hook_chapter(f"ch{k + 1:02d}"),
                      "seed": am._seed_for_subject(TID, it.get("subject_ref"))})
    for f in fotos:
        log(f"#{f['n']} {f['ref']} {f['plano']} {f['persona']} {f['anio']} → madres {f['madres']}")
    cost_tracker.start_video(video_id=VIDEO_ID_COSTO)

    def una(f):
        t0 = time.time()
        uris = [am._path_to_data_uri(p) for p in f["madres_paths"]] or None
        meta = am._generate_flux_image_at(f["prompt"], "", B / f["file"], f["use_ultra"], f["seed"], uris)
        return meta, round(time.time() - t0, 1)
    t_pared = time.time()
    with ThreadPoolExecutor(max_workers=min(len(fotos), am.FLUX_MAX_WORKERS)) as ex:
        futs = {ex.submit(una, f): f for f in fotos}
        for fut in as_completed(futs):
            f = futs[fut]
            try:
                meta, seg = fut.result()
                f["segundos"] = seg
                f["endpoint"] = (meta.get("flux_meta") or {}).get("endpoint")
                log(f"  ✓ {f['file']} · {seg} s · {f['endpoint']}")
            except Exception as e:  # noqa: BLE001 — sin reintento, texto literal
                f["error"] = f"{type(e).__name__}: {str(e)[:400]}"
                log(f"  ✗ {f['file']}: {f['error']}")
    pared = round(time.time() - t_pared, 1)
    rep = cost_tracker.end_video()
    total = round(rep.total_cost, 4) if rep else None
    por_foto = round(total / len(fotos), 4) if total else None
    for f in fotos:
        f["usd"] = por_foto
    log(f"pared {pared} s · costo cost_tracker US$ {total} ({len(rep.entries) if rep else 0} entradas)")

    # ── hoja: por foto, madre(s) + foto + pie ──
    from PIL import Image, ImageDraw
    W, H = 480, 270
    hoja = Image.new("RGB", (3 * (W + 10) + 10, len(fotos) * (H + 50) + 10), (18, 18, 18))
    d = ImageDraw.Draw(hoja)
    for r, f in enumerate(fotos):
        y = 10 + r * (H + 50)
        for c, p in enumerate(f["madres_paths"][:2]):
            hoja.paste(Image.open(p).convert("RGB").resize((W, H)), (10 + c * (W + 10), y))
            d.text((12 + c * (W + 10), y + 2), f"MADRE {f['madres'][c]}", fill=(255, 255, 0))
        if not f["madres_paths"]:
            d.text((12, y + H // 2), "(sin madre: t2i)", fill=(140, 140, 140))
        fp = B / f["file"]
        if fp.exists():
            hoja.paste(Image.open(fp).convert("RGB").resize((W, H)), (10 + 2 * (W + 10), y))
        ancla = " ".join((f["ancla"] or "").split()[:12])
        d.text((12, y + H + 6), f"#{f['n']} · plano pedido: {f['plano']} · {', '.join(f['persona'])} · {f['anio']} · «{ancla}»", fill=(255, 255, 255))
        d.text((12, y + H + 24), f"{f['file']} · madres {f['madres'] or 'ninguna (t2i)'} · {f.get('segundos')} s · {f.get('endpoint')}", fill=(180, 180, 180))
    hoja.save(B / "hoja_f61b.jpg", quality=85)
    despues = mtimes(PROD)
    intacta = antes == despues
    log(f"PRODUCCIÓN INTACTA: {intacta}")
    res = {"hora": datetime.now().isoformat(timespec="seconds"), "video_id_costo": VIDEO_ID_COSTO, "registry": registry, "fotos": fotos,
           "segundos_pared": pared, "usd_total": total, "entradas": [{"service": e.service, "units": e.units, "cost": round(e.total_cost, 4)} for e in (rep.entries if rep else [])],
           "produccion_intacta": intacta, "mtimes_antes": antes, "mtimes_despues": despues, "log": LOG}
    (B / "etapa_f61b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (B / "etapa_f61b.log").write_text("\n".join(LOG), encoding="utf-8")
    return 0 if intacta and not any(f.get("error") for f in fotos) else 1


if __name__ == "__main__":
    sys.exit(main())
