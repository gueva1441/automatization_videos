"""F78a Etapa B (solo Colza): camino de producción, SIN Opus de m03 y SIN `fase1_5 --from m03`.
1. mover las 7 madres actuales a foto_madre/_previas_f78a/;
2. foto_madre.generate_fotos_madre_personas(topic de topics_db, tid) + save_db → rasgos.json, 7 madres, 8 variantes;
3. m06_assembler.assemble_final_script(tid);
4. regenerar SOLO las 6 fotos de control con asset_manager.process_script (su prompt actual), después de mover a
   <cap>/_previas_f78a/ su .png, _native.png, _graded.png y .llamada.json. Antes de pedir nada se verifica que en assets no
   falte ninguna otra foto ni clip (si faltara, process_script la generaría: PARA).
Nada se borra. Copias del «antes» (script, manifest, topic) en lab/hyperframes/f78a/b/antes/. Costo: cost_tracker del tid.
Uso (venv): PYTHONIOENCODING=utf-8 <venv>/python lab/hyperframes/f78a/b/etapa_b.py [--preflight]"""
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
import foto_madre as fm  # noqa: E402
import fase2a  # noqa: E402
from script_engine import m06_assembler as m6  # noqa: E402
from script_engine.topics_db import load_db, save_db  # noqa: E402

TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
CONTROL = ["ch01_supp_05", "ch06_img_14", "ch03_img_11", "ch03_img_14", "ch05_img_12", "ch07_supp_07"]
AQUI = Path(__file__).parent
ANTES = AQUI / "antes"
ASSETS = OUTPUT_DIR / TID / "assets"
MADRES = OUTPUT_DIR / TID / "foto_madre"


def log(*a):
    print(time.strftime("[%H:%M:%S]"), *a, flush=True)


def esperados(norm: dict) -> list[Path]:
    """Todas las fotos y clips que process_script miraría (si falta uno, lo generaría)."""
    out = [it["path"] for it in am._items_para_secuencia(norm["chapters"], TID)]
    for ch in norm["chapters"]:
        if (ch.get("render_engine") or "").lower() == "veo":
            veo = ASSETS / f"{ch['id']}_veo"
            for i, _ in enumerate(ch.get("image_prompts") or [], 1):
                out += [veo / am._clip_filename(ch["id"], i), veo / am._image_filename(ch["id"], i)]
    return out


def foto_de(stem: str) -> Path:
    return ASSETS / f"{stem[:4]}_flux" / f"{stem}.png"


def main(preflight: bool) -> int:
    script_path = DATA_DIR / "scripts" / f"{TID}.json"
    norm = fase2a._normalize_long({**json.loads(script_path.read_text(encoding="utf-8")), "video_id": TID})
    faltan = [p for p in esperados(norm) if not p.exists()]
    log(f"preflight: {len(esperados(norm))} fotos/clips esperados, faltan {len(faltan)}: {[p.name for p in faltan]}")
    if faltan:
        log("PARA: falta algo fuera de las 6 de control; process_script lo generaría")
        return 2
    for s in CONTROL:
        assert foto_de(s).exists(), s
    if preflight:
        return 0

    ANTES.mkdir(parents=True, exist_ok=True)
    shutil.copy2(script_path, ANTES / script_path.name)
    shutil.copy2(ASSETS / "assets_manifest.json", ANTES / "assets_manifest.json")
    db = load_db()
    topic = next(t for t in db["topics"] if t.get("id") == TID)
    (ANTES / "documented_people.json").write_text(json.dumps(topic["documented_people"], ensure_ascii=False, indent=1),
                                                  encoding="utf-8")
    cost_tracker.start_video(TID)
    t0 = time.time()

    # 1. las 7 madres actuales → foto_madre/_previas_f78a/ (con su .prompt.txt)
    for p in topic["documented_people"]:
        if p.get("foto_madre") and Path(p["foto_madre"]).exists():
            log("madre vieja →", fm._a_previas(Path(p["foto_madre"])))

    # 2. rasgos + 7 madres + variantes
    est = fm.generate_fotos_madre_personas(topic, TID)
    save_db(db)
    (AQUI / "estados_foto_madre.json").write_text(json.dumps(est, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    log(f"madres y variantes: {time.time() - t0:.0f} s")

    # 3. el contrato
    log("m06 →", m6.assemble_final_script(TID))

    # 4. las 6 fotos de control
    for s in CONTROL:
        f = foto_de(s)
        prev = f.parent / "_previas_f78a"
        prev.mkdir(exist_ok=True)
        for x in (f, f.with_name(f"{s}_native.png"), f.with_name(f"{s}_graded.png"), f.with_name(f"{s}.llamada.json")):
            if x.exists():
                x.rename(prev / x.name)
    norm = fase2a._normalize_long({**json.loads(script_path.read_text(encoding="utf-8")), "video_id": TID})
    faltan = sorted(p.stem for p in esperados(norm) if not p.exists())
    log("a regenerar:", faltan)
    assert faltan == sorted(CONTROL), faltan
    t1 = time.time()
    am.process_script(norm, None)
    log(f"6 fotos: {time.time() - t1:.0f} s")
    rep = cost_tracker.end_video()
    entradas = [e.__dict__ if hasattr(e, "__dict__") else e for e in getattr(rep, "entries", [])]
    (AQUI / "costo_etapa_b.json").write_text(json.dumps({"total_usd": rep.total_cost, "entradas": entradas},
                                                        ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    log(f"US$ {rep.total_cost:.4f} · total {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main("--preflight" in sys.argv))
