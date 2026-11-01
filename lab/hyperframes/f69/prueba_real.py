"""F69, prueba real (una sola): ch01 de Wittenoom con el pedido del handoff, por `_fotoclip_core` sin deps inyectadas.
Foto, final y clip quedan en producción; aquí, la evidencia. Corre una vez: si `prueba_real.json` existe, no vuelve a gastar."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import qa_studio_server as qa  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402

TOPIC = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
PEDIDO = "solo Daniel, sin niños, sin borde de diapositiva"
SALIDA = AQUI / "prueba_real.json"


def md5(p: Path) -> str | None:
    return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None


def main() -> int:
    if SALIDA.exists():
        sys.exit("la prueba ya corrió: no se gasta de nuevo")
    st = qa.QAState(TOPIC)
    veo = st.assets_dir / "ch01_veo"
    foto, final, clip = veo / "ch01_img_01.png", veo / "ch01_img_01_final.png", veo / "ch01_clip_01.mp4"
    manifest = st.assets_dir / "assets_manifest.json"
    e0 = st.resolve_fix_entry(foto.name)
    c0 = st.resolve_clip_entry("ch01")
    m0 = json.loads(manifest.read_text(encoding="utf-8"))
    shutil.copy2(foto, AQUI / "antes_foto.png")
    shutil.copy2(final, AQUI / "antes_final.png")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(clip), "-vf", "select=eq(n\\,0)", "-vsync", "0",
                    "-frames:v", "1", str(AQUI / "antes_primer_cuadro.png")], check=True)
    antes = {p.name: md5(p) for p in (foto, final, clip)}

    cost_tracker.start_video(video_id="lab_f69")
    ok, texto = qa._fotoclip_core(st, TOPIC, "ch01", PEDIDO)

    e1 = st.resolve_fix_entry(foto.name)
    c1 = st.resolve_clip_entry("ch01")
    m1 = json.loads(manifest.read_text(encoding="utf-8"))
    shutil.copy2(foto, AQUI / "despues_foto.png")
    shutil.copy2(final, AQUI / "despues_final.png")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(clip), "-vf", "select=eq(n\\,0)", "-vsync", "0",
                    "-frames:v", "1", str(AQUI / "despues_primer_cuadro.png")], check=True)
    fila = next(c for c in m1["chapters"] if c.get("id") == "ch01")["clips"][0]
    costos = [{"servicio": x.service, "descripcion": x.description, "usd": x.total_cost} for x in cost_tracker.current_video.entries]
    SALIDA.write_text(json.dumps({
        "pedido": PEDIDO, "ok": ok, "texto": texto,
        "casilleros_antes": e0["casilleros"], "casilleros_despues": e1["casilleros"],
        "prompt_antes": e0["prompt"], "prompt_despues": e1["prompt"],
        "video_prompt_igual": c0["video_prompt"] == c1["video_prompt"], "video_prompt": c1["video_prompt"],
        "md5_antes": antes, "md5_despues": {p.name: md5(p) for p in (foto, final, clip)},
        "fila_manifest": {k: v for k, v in fila.items() if k not in ("image_prompt", "video_prompt")},
        "manifest_sello_igual": m0.get("papel_md5") == m1.get("papel_md5"),
        "costos": costos, "usd_total": sum(x["usd"] for x in costos),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(ok, texto)
    print("usd", sum(x["usd"] for x in costos))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
