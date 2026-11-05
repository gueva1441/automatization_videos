"""F78d Etapa C — Colza: fotos y clips (la Etapa C de F78a), camino de producción (`asset_manager.process_script`, motor Lite).
Qué se regenera (regla declarada en el reporte):
  - toda foto /edit (con al menos una madre por `_madres_para_item`, la regla única, contra el guion vivo) cuyo prompt cambió en la
    Etapa B (guion de antes en lab/hyperframes/f78d/b/antes/) O alguna de cuyas madres/variantes es más nueva que la foto
    (rehecha en F78a/F78b después de la foto);
  - los clips del gancho (ch01) y de ch07 (F78a_REPORT l.127): clip, foto de arranque y foto final.
Lo viejo se MUEVE a <carpeta del cap>/_previas_f78d/ (png, _native, _graded, .llamada.json; en clips también el mp4 y la final).
Preflight: antes de mover, todo lo que process_script miraría existe; después de mover, falta exactamente la lista (si no, PARA).
Costo: cost_tracker del tid → c/costo.json. Uso (venv): PYTHONIOENCODING=utf-8 <venv>/python lab/hyperframes/f78d/c/etapa_c.py [--lista]"""
import json
import shutil
import sys
import time
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
from config import OUTPUT_DIR, DATA_DIR  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402
import asset_manager as am  # noqa: E402
import fase2a  # noqa: E402

TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
AQUI = Path(__file__).parent
ANTES_SCRIPT = AQUI.parent / "b" / "antes" / f"{TID}.json"
ASSETS = OUTPUT_DIR / TID / "assets"
PREVIAS = "_previas_f78d"
CLIPS = ["ch01", "ch07"]


def log(*a):
    print(time.strftime("[%H:%M:%S]"), *a, flush=True)


def norm_de(p: Path) -> dict:
    return fase2a._normalize_long({**json.loads(p.read_text(encoding="utf-8")), "video_id": TID})


def fotos(norm: dict) -> dict[str, dict]:
    """{stem: {path, prompt, madres}} de cada foto (flux, supps y la foto de arranque de cada clip) con sus madres hoy."""
    sc = json.loads((DATA_DIR / "scripts" / f"{TID}.json").read_text(encoding="utf-8"))
    reg, per = sc.get("foto_madre_registry") or {}, sc.get("foto_madre_personas") or {}
    out = {}
    for it in am._items_para_secuencia(norm["chapters"], TID):
        m = am._madres_para_item(it["persona"], it["refs"], it["anio"], reg, per, it["prompt"])
        out[it["path"].stem] = {"path": it["path"], "prompt": it["prompt"], "madres": m}
    for ch in norm["chapters"]:
        if (ch.get("render_engine") or "").lower() == "veo":
            f8 = ch.get("image_f8") if isinstance(ch.get("image_f8"), dict) else {}
            prompt = (ch.get("image_prompts") or [""])[0]
            m = am._madres_para_item(am._norm_persona(f8.get("persona")), am._norm_foto_madre_refs(f8.get("foto_madre_ref")),
                                     f8.get("anio"), reg, per, prompt)
            p = ASSETS / f"{ch['id']}_veo" / am._image_filename(ch["id"], 1)
            out[p.stem] = {"path": p, "prompt": prompt, "madres": m, "clip": ch["id"]}
    return out


def esperados(norm: dict) -> list[Path]:
    """Lo que process_script miraría (si falta, lo generaría): fotos, supps, foto de arranque y clip de cada cap con clip."""
    out = [it["path"] for it in am._items_para_secuencia(norm["chapters"], TID)]
    for ch in norm["chapters"]:
        if (ch.get("render_engine") or "").lower() == "veo":
            veo = ASSETS / f"{ch['id']}_veo"
            for i, _ in enumerate(ch.get("image_prompts") or [], 1):
                out += [veo / am._clip_filename(ch["id"], i), veo / am._image_filename(ch["id"], i)]
    return out


def lista() -> tuple[dict, list[dict]]:
    norm, viejo = norm_de(DATA_DIR / "scripts" / f"{TID}.json"), fotos(norm_de(ANTES_SCRIPT))
    hoy = fotos(norm)
    filas = []
    for stem, f in hoy.items():
        if not f["madres"] and not f.get("clip"):
            continue                                                      # t2i: no es /edit
        png = f["path"]
        cambio_prompt = f["prompt"] != (viejo.get(stem) or {}).get("prompt")
        madre_nueva = [Path(p).name for _, p in f["madres"] if png.exists() and Path(p).stat().st_mtime > png.stat().st_mtime]
        motivo = (["prompt nuevo (B)"] if cambio_prompt else []) + ([f"madre más nueva: {', '.join(madre_nueva)}"]
                                                                    if madre_nueva else [])
        if f.get("clip") in CLIPS:
            motivo.append("clip del gancho/ch07 (F78a l.127)")
        if motivo:
            filas.append({"foto": stem, "path": str(png), "clip": f.get("clip"), "motivo": motivo,
                          "madres": [{"ref": r, "path": p} for r, p in f["madres"]], "prompt": f["prompt"],
                          "prompt_viejo": (viejo.get(stem) or {}).get("prompt")})
    return norm, filas


def hermanos(png: Path, clip: str | None) -> list[Path]:
    s = png.stem
    out = [png, png.with_name(f"{s}_native.png"), png.with_name(f"{s}_graded.png"), png.with_name(f"{s}.llamada.json")]
    if clip:
        out += [png.with_name(f"{s}_final.png"), png.with_name(f"{s}_final_native.png"),
                png.with_name(f"{s}_final.llamada.json"), png.with_name(am._clip_filename(clip, 1))]
    return [p for p in out if p.exists()]


def mover(p: Path) -> Path:
    prev = p.parent / PREVIAS
    prev.mkdir(exist_ok=True)
    dest, k = prev / p.name, 1
    while dest.exists():
        dest, k = prev / f"{p.stem}_{k}{p.suffix}", k + 1
    p.rename(dest)
    return dest


def main(solo_lista: bool) -> int:
    norm, filas = lista()
    (AQUI / "lista.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"a regenerar: {len(filas)} fotos ({sum(1 for f in filas if f['clip'])} con clip)")
    for f in filas:
        log(" ", f["foto"], "·", "; ".join(f["motivo"]))
    faltan = [p for p in esperados(norm) if not p.exists()]
    if faltan:
        log("PARA: antes de mover ya falta", [p.name for p in faltan])
        return 2
    if solo_lista:
        return 0
    movidos = {}
    for f in filas:
        movidos[f["foto"]] = [str(mover(p)) for p in hermanos(Path(f["path"]), f["clip"])]
    (AQUI / "movidos.json").write_text(json.dumps(movidos, ensure_ascii=False, indent=1), encoding="utf-8")
    faltan = sorted(p.stem for p in esperados(norm) if not p.exists())
    quiero = sorted({f["foto"] for f in filas} | {am._clip_filename(f["clip"], 1)[:-4] for f in filas if f["clip"]})
    log("faltan ahora:", len(faltan))
    if faltan != quiero:
        log("PARA: lo que falta no es la lista", sorted(set(faltan) ^ set(quiero)))
        return 2
    cost_tracker.start_video(TID)
    t0 = time.time()
    try:
        am.process_script(norm, None)
    finally:
        rep = cost_tracker.end_video()
        entradas = [e.__dict__ if hasattr(e, "__dict__") else e for e in getattr(rep, "entries", [])]
        por = {}
        for e in entradas:
            k = f"{e.get('service', '?')} · {e.get('operation', e.get('model', '?'))}"
            por[k] = round(por.get(k, 0) + (e.get("total_cost") or 0), 4)
        (AQUI / "costo.json").write_text(json.dumps({"total_usd": round(rep.total_cost, 4), "por_servicio": por,
                                                     "entradas": entradas}, ensure_ascii=False, indent=1, default=str),
                                         encoding="utf-8")
        log(f"US$ {rep.total_cost:.4f} · {time.time() - t0:.0f} s · {por}")
    sigue = sorted(p.stem for p in esperados(norm) if not p.exists())
    log("faltan después:", sigue)
    return 0 if not sigue else 4


if __name__ == "__main__":
    sys.exit(main("--lista" in sys.argv))
