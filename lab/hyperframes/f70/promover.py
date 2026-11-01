"""F70b: pasa 3 fotos del lab F70 a producción (HANDOFF_F70b_promover.md). Sin llamadas a fal, Opus ni Gemini. Corre una sola vez:
si las fotos de producción ya son las del lab o existe `promover_resultado.json`, no hace nada."""
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import qa_studio_server as qa  # noqa: E402
from run_pipeline import etapa_de  # noqa: E402

TOPIC = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
FOTOS = ("ch03_img_08", "ch03_img_15", "ch06_img_07")
CAPS = ("ch03", "ch06")
SALIDA = AQUI / "promover_resultado.json"
TAM_FOTO, TAM_NATIVO = (2560, 1440), (1376, 768)


def md5(p: Path) -> str | None:
    return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None


def tam(p: Path) -> tuple[int, int]:
    with Image.open(p) as im:
        return im.size


def nombre_entrada(it: dict) -> str | None:
    rel = it.get("path_original")
    return str(rel).replace("\\", "/").rsplit("/", 1)[-1].removesuffix(".png") if rel else None


def entradas(man: dict) -> dict[str, dict]:
    return {nombre_entrada(it): it for c in man["chapters"] for it in c.get("images") or [] if nombre_entrada(it) in FOTOS}


def sin_las_tres(man: dict) -> dict:
    """El manifest sin las 3 entradas, para comparar el resto."""
    copia = json.loads(json.dumps(man))
    for c in copia["chapters"]:
        if "images" in c:
            c["images"] = [it for it in c["images"] if nombre_entrada(it) not in FOTOS]
    return copia


def parar(motivo: str) -> None:
    sys.exit(f"PARADA: {motivo}")


def main() -> None:
    if SALIDA.exists():
        parar("ya corrió")
    st = qa.QAState(TOPIC)
    mpath = st.assets_dir / "assets_manifest.json"
    guion, visual = st.script_path, qa._visual_path(st, TOPIC)
    man0 = json.loads(mpath.read_text(encoding="utf-8"))
    actuales = entradas(man0)
    if set(actuales) != set(FOTOS):
        parar(f"el manifest no tiene las 3 entradas: {sorted(actuales)}")
    for f in FOTOS:
        for suf in (".png", "_native.png", ".llamada.json"):
            if not (AQUI / f"{f}{suf}").exists():
                parar(f"falta en el lab: {f}{suf}")
        if md5(AQUI / f"{f}.png") == md5(st.assets_dir / f"{f[:4]}_flux" / f"{f}.png"):
            parar(f"{f} ya es la del lab")

    etapa0, sello0 = etapa_de(TOPIC), man0.get("papel_md5")
    md5_guion0, md5_visual0 = md5(guion), md5(visual)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    qa._backup(st, mpath, ts)
    filas = {}
    for f in FOTOS:
        d = st.assets_dir / f"{f[:4]}_flux"
        png, graded, nativo, llamada = d / f"{f}.png", d / f"{f}_graded.png", d / f"{f}_native.png", d / f"{f}.llamada.json"
        antes = {p.name: md5(p) for p in (png, nativo, graded)}
        for p in (png, graded, nativo, llamada):
            qa._backup(st, p, ts)
        graded_viejo = st.assets_dir / "_qa_backups" / f"{graded.name}.{ts}.bak.png"
        for suf, dst in ((".png", png), ("_native.png", nativo), (".llamada.json", llamada)):
            shutil.copy2(AQUI / f"{f}{suf}", dst)
        if qa._grade_como_produccion(png) is None:
            parar(f"{f}: _grade_como_produccion devolvió None (grade apagado); la foto cruda y su backup quedan, el manifest no se tocó")
        filas[f] = {"antes": antes, "despues": {p.name: md5(p) for p in (png, nativo, graded)},
                    "lab": {"png": md5(AQUI / f"{f}.png"), "native": md5(AQUI / f"{f}_native.png")},
                    "tam_png": tam(png), "tam_native": tam(nativo), "tam_graded": tam(graded), "graded_viejo": str(graded_viejo)}
        for k in ("tam_png", "tam_graded"):
            if tuple(filas[f][k]) != TAM_FOTO:
                parar(f"{f}: {k} {filas[f][k]}")
        if tuple(filas[f]["tam_native"]) != TAM_NATIVO:
            parar(f"{f}: nativo {filas[f]['tam_native']}")

    man = json.loads(mpath.read_text(encoding="utf-8"))
    diffs = {}
    for f, it in entradas(man).items():
        r = json.loads((AQUI / f"{f}.llamada.json").read_text(encoding="utf-8"))["llamadas"]["nb2_lite"]
        previo = json.loads(json.dumps(it))
        it["prompt"] = r["texto"]
        for k in ("motor", "usd", "segundos", "respaldo_motivo"):
            if k in r:
                it[k] = r[k]
        for k in ("endpoint", "motor", "usd", "segundos", "respaldo_motivo"):
            if k in r:
                it.setdefault("flux_meta", {})[k] = r[k]
        diffs[f] = {k: {"antes": previo.get(k), "despues": it.get(k)} for k in it if previo.get(k) != it.get(k)}
    qa._write_json(mpath, man)
    for cap in CAPS:
        qa._invalidate_baked(st, TOPIC, cap)

    man1 = json.loads(mpath.read_text(encoding="utf-8"))
    work = st.base / "output" / TOPIC / "_fase2b_work"
    resultado = {
        "ts": ts, "fotos": filas, "manifest_diff": diffs, "resto_del_manifest_identico": sin_las_tres(man0) == sin_las_tres(man1),
        "papel_md5": {"antes": sello0, "despues": man1.get("papel_md5")},
        "etapa_de": {"antes": list(etapa0), "despues": list(etapa_de(TOPIC))},
        "guion_md5": {"antes": md5_guion0, "despues": md5(guion)}, "visual_md5": {"antes": md5_visual0, "despues": md5(visual)},
        "horneados_que_quedan": sorted(p.name for c in CAPS for p in work.glob(f"{c}_*visual.mp4")),
    }
    SALIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")

    ancho, alto, cab = 960, 540, 40
    hoja = Image.new("RGB", (ancho * 2, (alto + cab) * len(FOTOS)), (20, 20, 20))
    dib = ImageDraw.Draw(hoja)
    for y, f in enumerate(FOTOS):
        d = st.assets_dir / f"{f[:4]}_flux"
        for x, (rotulo, ruta) in enumerate((("VIEJA", Path(filas[f]["graded_viejo"])), ("NUEVA", d / f"{f}_graded.png"))):
            dib.text((x * ancho + 10, y * (alto + cab) + 10), f"{f}_graded · {rotulo}", fill=(255, 255, 255))
            im = Image.open(ruta).convert("RGB")
            im.thumbnail((ancho, alto), Image.LANCZOS)
            hoja.paste(im, (x * ancho, y * (alto + cab) + cab))
    hoja.save(AQUI / "promovidas_hoja.jpg", quality=92)
    print(json.dumps(resultado, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
