"""F78d Etapa B — Colza: textos. Corre `fase1_5.py --topic <tid> --only aspecto` (paso nuevo + assemble) con el venv y arma:
- md5 de la narración y el papel aprobados (y del resto de la foto madre) ANTES y DESPUÉS → b/md5_antes.json, b/md5_despues.json;
  si cambian, sale con 3 (PARADA).
- copia de 03_visual.json y data/scripts/<tid>.json de antes en b/antes/ (para la tabla y la Etapa C);
- tabla por foto → persona → subject viejo → subject nuevo → marca (b/tabla_subject.md), el movimiento de los clips viejo/nuevo
  (b/movimiento.md) y el costo del paso (01_v3_costos.json, paso «aspecto»).
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f78d/b/etapa_b.py   (el subproceso usa el venv)"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
from config import DATA_DIR, OUTPUT_DIR  # noqa: E402
from script_engine import m03_visual as m3  # noqa: E402

TID = "c4934b7d-3f54-448f-ba5f-539dc744f0d8"
VENV = Path(r"C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv\Scripts\python.exe")
AQUI = Path(__file__).parent
SD = m3.STEPS_DIR / TID
SCRIPT = DATA_DIR / "scripts" / f"{TID}.json"
APROBADOS = ["01a_skeleton.json", "01b_narracion_v3.json", "01b_narration.json", "01b_narration_normalized.json",
             "01e_pantalla.json", "01e_pantalla.md"]


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def md5s() -> dict:
    out = {f"_steps/{n}": md5(SD / n) for n in APROBADOS}
    sc = json.loads(SCRIPT.read_text(encoding="utf-8"))
    out["script.papel_md5"] = sc.get("papel_md5")
    for p in sorted((OUTPUT_DIR / TID / "foto_madre").rglob("*")):     # la foto madre no debe rehacerse
        if p.is_file():
            out[str(p.relative_to(OUTPUT_DIR))] = md5(p)
    return out


def subj(it: dict) -> str:
    try:
        return (json.loads(it.get("raw_llm_prompt") or "{}") or {}).get("subject") or ""
    except ValueError:
        return ""


def main() -> int:
    antes = md5s()
    (AQUI / "md5_antes.json").write_text(json.dumps(antes, indent=1), encoding="utf-8")
    (AQUI / "antes").mkdir(exist_ok=True)
    shutil.copy2(SD / "03_visual.json", AQUI / "antes" / "03_visual.json")
    shutil.copy2(SCRIPT, AQUI / "antes" / f"{TID}.json")
    with open(AQUI / "fase1_5.log", "w", encoding="utf-8") as log:
        r = subprocess.run([str(VENV), "fase1_5.py", "--topic", TID, "--only", "aspecto"], cwd=R, stdout=log,
                           stderr=subprocess.STDOUT, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    print("fase1_5 salió con", r.returncode)
    despues = md5s()
    (AQUI / "md5_despues.json").write_text(json.dumps(despues, indent=1), encoding="utf-8")
    dif = sorted(k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k))
    print("md5 aprobados/madre:", "IGUALES" if not dif else f"DISTINTOS {dif}")

    va = json.loads((AQUI / "antes" / "03_visual.json").read_text(encoding="utf-8"))
    vn = json.loads((SD / "03_visual.json").read_text(encoding="utf-8"))
    viejo = {f["foto"]: f["item"] for f in m3._fotos_con_persona(va)}
    nuevo = {f["foto"]: f["item"] for f in m3._fotos_con_persona(vn)}
    filas = ["| foto | persona | subject viejo | subject nuevo | marca |", "|---|---|---|---|---|"]
    cambiadas = []
    for foto, it in viejo.items():
        n = nuevo.get(foto, {})
        marca = n.get("_rasgos_refill") or n.get("aspecto_fuente") or "sin tocar"
        if n.get("prompt") != it.get("prompt"):
            cambiadas.append(foto)
        filas.append(f"| {foto} | {', '.join(m3._personas_de(it))} | {subj(it)} | "
                     f"{subj(n) if n.get('prompt') != it.get('prompt') else '(igual)'} | {marca} |")
    (AQUI / "tabla_subject.md").write_text("\n".join(filas) + "\n", encoding="utf-8")
    mov = []
    for ca, cn in zip(va["chapters"], vn["chapters"]):
        if "video_prompt" in ca:
            mov.append(f"### cap {ca['chapter_number']} — {'CAMBIÓ' if ca['video_prompt'] != cn['video_prompt'] else 'igual'}\n\n"
                       f"VIEJO\n\n{ca['video_prompt']}\n\nNUEVO\n\n{cn['video_prompt']}\n")
    (AQUI / "movimiento.md").write_text("\n".join(mov), encoding="utf-8")
    (AQUI / "cambiadas.json").write_text(json.dumps(cambiadas, indent=1), encoding="utf-8")
    costos = json.loads((SD / "01_v3_costos.json").read_text(encoding="utf-8"))
    asp = [c for c in costos.get("_corridas") or [] if c.get("paso") == "aspecto"]
    (AQUI / "costo.json").write_text(json.dumps(asp[-1:], indent=1), encoding="utf-8")
    print("costo aspecto:", asp[-1:] or "sin corrida")
    print(f"prompts cambiados: {len(cambiadas)}")
    return 3 if dif else r.returncode


if __name__ == "__main__":
    sys.exit(main())
