"""Producción completa de Orleans v2 (OK del analista, F5d+) en su topic propio `ba6c3cac-f5v2`.

Etapas (cada una idempotente; el log va a lab/hyperframes/f5/produccion/produccion.log):
    preparar  topic en data/topics_db.json (copia del v1 con id/video_id = v2, el evidence_pool del guion F5d+ y status
              «validated»; respaldo previo en lab/hyperframes/f5/produccion/topics_db_pre.json) y la carpeta de
              simulaciones output/<V2>/ movida a output/_bak_ba6c3cac-f5v2_simulaciones/ (no puede contaminar el
              render: el caché del director no depende de la narración)
    guion     fase1_5.process_topic(from_step="audio"): TTS de la narración F5d+ normalizada, música (m07), prompts de
              imagen (m03, con timestamps reales), foto madre (paso0) y data/scripts/<V2>.json
    imagenes  fase2a --topic V2: Seedream (97) + Veo (ch01/ch07)
    render    fase2b V2 --keep-segments --gfx --gfx-sparse --gfx-quality looks (UN render). Antes: Firefox cerrado y
              RAM libre > 14 GB, si no, no arranca
    render_gfx (F5e) re-render SOLO de la capa gfx: guion, imágenes y clips visuales quedan. Antes respalda el final y
              las capas chNN_gfx.mp4 en _fase2b_work/_bak_f5e_pre/ (con --reuse-visuals fase2b reusaría la capa vieja)
              y corre fase2b --reuse-visuals --keep-segments --gfx --gfx-sparse --gfx-quality looks
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/produccion_orleans_v2.py --etapa preparar|guion|imagenes|render|render_gfx
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

V1 = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
V2 = "ba6c3cac-f5v2"
LAB = Path(__file__).resolve().parent
PROD = LAB / "produccion"
DB = ROOT / "data" / "topics_db.json"
STEPS = ROOT / "data" / "scripts" / "_steps"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def preparar(log: list[str]) -> None:
    PROD.mkdir(exist_ok=True)
    if not (PROD / "topics_db_pre.json").exists():
        shutil.copy2(DB, PROD / "topics_db_pre.json")
    db = _load(DB)
    ts = db["topics"]
    if not any(t.get("id") == V2 for t in ts):
        t = json.loads(json.dumps(next(t for t in ts if t.get("id") == V1)))
        for k in ("video_path", "assets_rendered_at", "video_generated_at"):
            t.pop(k, None)
        t.update({"id": V2, "video_id": V2, "status": "validated",
                  "evidence_pool": _load(STEPS / V2 / "01_facts_sources.json")["evidence_pool"],
                  "f5_nota": "Orleans v2 (guion F5d+): research de v1, guion con evidence_pool; foto madre de v1"})
        ts.append(t)
        DB.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
        log.append(f"preparar: topic {V2} agregado a topics_db.json")
    sims = ROOT / "output" / V2
    bak = ROOT / "output" / "_bak_ba6c3cac-f5v2_simulaciones"
    if sims.exists() and not bak.exists():
        shutil.move(str(sims), str(bak))
        log.append(f"preparar: {sims} → {bak}")


def guion(log: list[str]) -> None:
    import fase1_5
    t0 = time.time()
    r = fase1_5.process_topic(V2, from_step="audio", gate_interactive=False, music_gate_interactive=False)
    log.append(f"guion: {r.get('status')} pasos {r.get('steps_completed')} en {time.time() - t0:.0f}s "
               + (f"· error {r.get('error')}" if r.get("error") else ""))
    if r.get("status") != "PASS":
        raise SystemExit(1)


def _ram_free_gb() -> float:
    """RAM física disponible (Windows, GlobalMemoryStatusEx; sin psutil)."""
    import ctypes

    class _MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = _MS()
    ms.dwLength = ctypes.sizeof(_MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    return ms.ullAvailPhys / 1e9


def _firefox_open() -> bool:
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq firefox.exe"], capture_output=True, text=True).stdout
    return "firefox.exe" in out.lower()


def _run(cmd: list[str], log: list[str], name: str) -> None:
    t0 = time.time()
    with (PROD / f"{name}.out").open("w", encoding="utf-8") as fh:
        r = subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, text=True,
                           env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    log.append(f"{name}: rc={r.returncode} en {(time.time() - t0) / 60:.1f} min ({' '.join(cmd[1:])})")
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def _backup_gfx(log: list[str], tag: str = "f5e") -> None:
    """Respaldo (una vez) del final y de las capas gfx; el render nuevo las rehace desde los clips visuales."""
    out = ROOT / "output" / V2
    work = out / "_fase2b_work"
    bak = work / f"_bak_{tag}_pre"
    if bak.exists():
        log.append(f"render_gfx: respaldo ya existe ({bak})")
        return
    bak.mkdir(parents=True)
    for f in sorted(work.glob("ch0?_gfx.mp4")):
        shutil.move(str(f), str(bak / f.name))
    for f in sorted(work.glob("gfx_plan_ch0?.resolved.json")) + sorted(work.glob("hoja_contactos_ch0?.jpg")) + \
            sorted(work.glob("gfx_cues_ch0?.md")):
        shutil.copy2(f, bak / f.name)
    for name in (f"{V2}_final_gfx.mp4", f"{V2}_final_gfx_no_music.mp4"):
        if (out / name).exists():
            shutil.move(str(out / name), str(out / name.replace("_final_gfx", "_final_gfx_f5d")))
    log.append(f"render_gfx: capas y planes a {bak}; final anterior → *_final_gfx_f5d.mp4")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--etapa", choices=["preparar", "guion", "imagenes", "render", "render_gfx"], required=True)
    a = ap.parse_args()
    PROD.mkdir(exist_ok=True)
    log = [f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] producción Orleans v2 · etapa {a.etapa}"]
    try:
        if a.etapa == "preparar":
            preparar(log)
        elif a.etapa == "guion":
            guion(log)
        elif a.etapa == "imagenes":
            _run([sys.executable, "fase2a.py", "--topic", V2], log, "fase2a")
        else:
            if a.etapa == "render_gfx":
                _backup_gfx(log)
            ram, ff = _ram_free_gb(), _firefox_open()
            log.append(f"render: RAM libre {ram:.1f} GB · Firefox {'ABIERTO' if ff else 'cerrado'}")
            if ff or ram <= 14:
                log.append("render: NO arranca (regla de Omar: Firefox cerrado y RAM > 14 GB)")
                raise SystemExit(3)
            extra = ["--reuse-visuals"] if a.etapa == "render_gfx" else []
            _run([sys.executable, "fase2b.py", V2, *extra, "--keep-segments", "--gfx", "--gfx-sparse", "--gfx-quality",
                  "looks"], log, "fase2b_gfx" if extra else "fase2b")
    finally:
        with (PROD / "produccion.log").open("a", encoding="utf-8") as fh:
            fh.write("\n".join(log) + "\n")
        print("\n".join(log))


if __name__ == "__main__":
    main()
