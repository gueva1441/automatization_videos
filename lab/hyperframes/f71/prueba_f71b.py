"""F71b Etapa B, prueba real (una sola): `_fix_core` de la mujer con la foto de Daniel (el handoff la llama «ch01 supp 1»; el archivo es ch01_supp_02), sin deps inyectadas. La foto queda en producción, con backup.
Si `prueba_f71b.json` existe, no vuelve a gastar."""
import json
import os
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import qa_studio_server as qa  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402

T = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
FOTO = "ch01_supp_02.png"
PEDIDO = "la foto que sostiene la mujer es de Daniel Écija joven, su cara"
SALIDA = AQUI / "prueba_f71b.json"


def main() -> int:
    if SALIDA.exists():
        sys.exit("la prueba ya corrió: no se gasta de nuevo")
    st = qa.QAState(T)
    png = st.resolve_image("ch01", FOTO)
    graded = png.with_name(f"{png.stem}_graded.png")
    e0 = st.resolve_fix_entry(FOTO)
    shutil.copy2(png, AQUI / "ch01_supp_02_antes.png")
    shutil.copy2(graded, AQUI / "ch01_supp_02_antes_graded.png")
    cost_tracker.start_video(video_id="lab_f71b")
    ok, texto = qa._fix_core(st, T, "ch01", FOTO, PEDIDO)
    e1 = st.resolve_fix_entry(FOTO)
    shutil.copy2(png, AQUI / "ch01_supp_02_despues.png")
    shutil.copy2(graded, AQUI / "ch01_supp_02_despues_graded.png")
    llamada = json.loads(png.with_name(f"{png.stem}.llamada.json").read_text(encoding="utf-8"))["llamadas"]
    costos = [{"servicio": x.service, "descripcion": x.description, "usd": x.total_cost} for x in cost_tracker.current_video.entries]
    SALIDA.write_text(json.dumps({
        "pedido": PEDIDO, "ok": ok, "texto": texto,
        "casilleros_antes": e0["casilleros"], "casilleros_despues": e1["casilleros"],
        "prompt_antes": e0["prompt"], "prompt_despues": e1["prompt"],
        "persona_antes": e0["persona"], "persona_despues": e1["persona"],
        "llamada": {k: {c: v.get(c) for c in ("endpoint", "texto", "referencias_md5", "estado", "segundos", "request_id")} for k, v in llamada.items()},
        "costos": costos, "usd_total": sum(c["usd"] for c in costos),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(ok, texto)
    print("usd", sum(c["usd"] for c in costos))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
