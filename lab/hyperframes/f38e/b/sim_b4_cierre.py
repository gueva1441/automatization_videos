"""
lab/hyperframes/f38e/b/sim_b4_cierre.py — F38e B4: simulación de la pregunta de cierre desde la voz sobre los 7 caps de
Vajont, con la regla ya programada en script_engine.gfx_realizador.pregunta_cierre_fuente (no hay una copia de la regla
acá: lo que se simula es lo que corre). Entradas congeladas de Fase 1 (lab/hyperframes/f38/b2/fase1/f8s3-vajont/):
01a_escaleta.json + 01b_narracion_v3.json. No escribe en data/ ni output/. Salida: tabla cap → antes (cierre de la
escaleta) → ahora (texto, fuente, caracteres, lectura a 15 cps).

    python lab/hyperframes/f38e/b/sim_b4_cierre.py [--md salida.md]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

from script_engine.gfx_realizador import pregunta_cierre_fuente  # noqa: E402
from script_engine.pantalla_colocar import LECTURA_CPS  # noqa: E402   (15 cps; el handoff lo cita como pantalla_entrada)

FASE1 = RAIZ / "lab" / "hyperframes" / "f38" / "b2" / "fase1" / "f8s3-vajont"


def real_de(cap: int, esc: dict, parrafos: list[dict]) -> dict:
    """El `real` que arma gfx_realizador.ventanas, sin tiempos: beats del cap con su `cierre` y su `texto` (los párrafos
    de la narración por beat, unidos como en ventanas())."""
    beats = []
    for b in esc["beats"]:
        if int(b.get("cap") or 0) != cap:
            continue
        n = int(b["n"])
        beats.append({"n": n, "cierre": str(b.get("cierre") or "").strip(),
                      "texto": " ".join(p["texto"] for p in parrafos
                                        if int(p.get("cap") or 0) == cap and int(p.get("beat") or 0) == n)})
    return {"cap": cap, "beats": beats}


def main() -> None:
    esc = json.loads((FASE1 / "01a_escaleta.json").read_text(encoding="utf-8"))
    nar = json.loads((FASE1 / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    pars = nar.get("parrafos") or []
    caps = sorted({int(b["cap"]) for b in esc["beats"]})
    filas = ["| cap | antes (cierre de la escaleta) | ahora (texto) | fuente | car. | lectura s |", "|---|---|---|---|---|---|"]
    for cap in caps:
        real = real_de(cap, esc, pars)
        antes = real["beats"][-1]["cierre"]
        txt, fuente = pregunta_cierre_fuente(real)
        n = len(txt or "")
        filas.append(f"| ch{cap:02d} | {antes} | {txt} | {fuente} | {n} | {n / LECTURA_CPS:.1f} |")
    out = "\n".join(filas)
    print(out)
    if "--md" in sys.argv:
        p = Path(sys.argv[sys.argv.index("--md") + 1])
        p.write_text(out + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
