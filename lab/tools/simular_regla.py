"""
lab/tools/simular_regla.py — F33 §C.3: correr una regla EN SECO contra un guion de pantalla antes de programarla.

Entrada: un `GUION_PANTALLA.json` (fase2b --plan-only) y la regla como predicado de Python sobre cada evento `e` (un dict
con las claves del guion: cap, beat, funcion, tipo, etiqueta, texto, dur, lectura_min, escena, escena_t0, escena_t1,
voz_prev, voz_ancla, voz_next, aporta, fuente, filtro, queda, t, t_mp4, pool_id…). El predicado devuelve algo verdadero
(o un texto con el motivo) si la regla CORTARÍA ese evento. Salida (markdown): por cap, propuestos → cortados por esta
regla → quedan, y 3 ejemplos de lo que corta. No toca nada del pipeline ni del guion.

    python lab/tools/simular_regla.py output/f8s3-vajont-f30/GUION_PANTALLA.json \
        --nombre "el sello no repite la voz" --tipos sello \
        --regla "e['texto'].lower() in e['voz_ancla'].lower()"

`--sobre quedan` (default): la regla se aplica a lo que hoy queda en pantalla (¿qué más cortaría?). `--sobre todos`: a
todo lo propuesto, también lo que ya cortó otro filtro (¿cuánto se solapa?). `--archivo regla.py`: en vez de `--regla`,
un archivo con `def regla(e) -> bool | str`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any, Callable

NO_BLOQUES = ("costura", "transición", "silencio de voz", "title card")


def cargar_regla(expr: str | None, archivo: str | None) -> Callable[[dict], Any]:
    if archivo:
        ns: dict[str, Any] = {}
        exec(Path(archivo).read_text(encoding="utf-8"), {"re": re}, ns)
        return ns["regla"]
    return eval(f"lambda e: ({expr})", {"re": re})


def simular(guion: dict, regla: Callable[[dict], Any], *, tipos: set[str] | None = None, sobre: str = "quedan"
            ) -> dict[str, Any]:
    """{por_cap: {cap: [propuestos, cortados, quedan]}, cortados: [eventos con su motivo], errores: [...]}."""
    por: "OrderedDict[str, list[int]]" = OrderedDict()
    cortados, errores = [], []
    for c in guion["caps"]:
        fila = por.setdefault(c["cap"], [0, 0, 0])
        for e in c["eventos"]:
            if e["tipo"] in NO_BLOQUES or (tipos and e["tipo"] not in tipos):
                continue
            if sobre == "quedan" and not e["queda"]:
                continue
            fila[0] += 1
            try:
                r = regla(e)
            except Exception as x:  # noqa: BLE001 — un evento que la regla no sabe leer se anota y no se corta
                errores.append(f"{c['cap']} {e['tipo']} «{e.get('texto')}»: {type(x).__name__}: {x}")
                r = None
            if r:
                fila[1] += 1
                cortados.append({**e, "motivo_simulado": r if isinstance(r, str) else "la regla lo corta"})
            else:
                fila[2] += 1
    return {"por_cap": por, "cortados": cortados, "errores": errores}


def mmss(t: float) -> str:
    return f"{int(t // 60):02d}:{t % 60:04.1f}"


def tabla(nombre: str, res: dict[str, Any], sobre: str, ejemplos: int = 3) -> str:
    tot = [sum(v[i] for v in res["por_cap"].values()) for i in range(3)]
    L = [f"### Regla simulada: {nombre}", "",
         f"Sobre {'lo que hoy queda en pantalla' if sobre == 'quedan' else 'todo lo propuesto'}: "
         f"**{tot[0]} propuestos → {tot[1]} cortados por esta regla → {tot[2]} quedan**.", "",
         "| cap | propuestos | cortados por esta regla | quedan |", "|---|---|---|---|"]
    L += [f"| {cap} | {p} | {k} | {q} |" for cap, (p, k, q) in res["por_cap"].items()]
    L += [f"| **total** | **{tot[0]}** | **{tot[1]}** | **{tot[2]}** |", "", f"Ejemplos de lo que corta ({min(ejemplos, len(res['cortados']))} de {len(res['cortados'])}):"]
    for e in res["cortados"][:ejemplos]:
        L.append(f"- {mmss(e['t_mp4'])} · {e['cap']} · beat {e['beat']} · {e['tipo']} «{e.get('texto')}» · voz: "
                 f"«{e.get('voz_ancla')}» → {e['motivo_simulado']}")
    if res["errores"]:
        L += ["", f"La regla no pudo leer {len(res['errores'])} evento(s): " + "; ".join(res["errores"][:3])]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="Simula una regla en seco contra un GUION_PANTALLA.json")
    ap.add_argument("guion")
    ap.add_argument("--nombre", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--regla", help="expresión de Python sobre el evento `e` (verdadera = la regla lo corta)")
    g.add_argument("--archivo", help="archivo .py con def regla(e)")
    ap.add_argument("--tipos", default="", help="tipos de evento a mirar, separados por coma (default: todos los bloques)")
    ap.add_argument("--sobre", choices=("quedan", "todos"), default="quedan")
    ap.add_argument("--ejemplos", type=int, default=3)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    guion = json.loads(Path(a.guion).read_text(encoding="utf-8"))
    res = simular(guion, cargar_regla(a.regla, a.archivo), tipos={t.strip() for t in a.tipos.split(",") if t.strip()} or None,
                  sobre=a.sobre)
    print(tabla(a.nombre, res, a.sobre, a.ejemplos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
