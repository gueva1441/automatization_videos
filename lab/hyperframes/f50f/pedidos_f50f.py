# -*- coding: utf-8 -*-
"""F50f C — verificación de los pedidos en seco con el canon de B (los arma `f50d/pedidos_f50d.py --salida
lab/hyperframes/f50f`): 0 líneas cambiadas fuera del bloque del canon y de las líneas de grupo (la medida de F50d B)
en los 7 caps, y en los caps 5, 6 y 7 el bloque ERA trae tramos de 1967 en adelante (no solo 1958-1966).
Escribe PEDIDOS_F50f.md con la tabla y el bloque ERA de los caps 5–7. Sale 1 si algo no da (PARADA).
Uso: python lab/hyperframes/f50f/pedidos_f50f.py   (después de pedidos_f50d.py --salida lab/hyperframes/f50f)
"""
import json
import re
import sys
from pathlib import Path

F50F = Path(__file__).resolve().parent


def main() -> int:
    from script_engine import m03_visual as m3
    d = json.loads((F50F / "PEDIDOS.json").read_text(encoding="utf-8"))
    fallas, L = [], ["# PEDIDOS_F50f — los 7 pedidos con el canon de Opus (F50f C, en seco)", "",
                     "Armados con `python lab/hyperframes/f50d/pedidos_f50d.py --salida lab/hyperframes/f50f` (código "
                     "de producción, llamada a Opus cortada); detalle por zona en `PEDIDOS_F50d.md` de esta carpeta. "
                     "Verificación de F50f: 0 líneas fuera del bloque del canon entero y de las líneas de grupo; caps "
                     "5–7 con tramos de 1967+.", "",
                     "| cap | años de las fotos | periods que entran | fuera del canon y de los grupos | grupos |",
                     "|---|---|---|---:|---:|"]
    for f in d["filas"]:
        L.append(f"| {f['cap']} | {' '.join(f['anios'])} | {' · '.join(f['periods']) or '—'} | "
                 f"{f['fuera_del_canon_y_grupos']} | {f['grupos']} |")
        if f["fuera_del_canon_y_grupos"]:
            fallas.append(f"ch{f['cap']:02d}: {f['fuera_del_canon_y_grupos']} líneas fuera del canon y de los grupos")
        if f["cap"] in (5, 6, 7):
            tardios = [y for y in f["periods"] if (t := m3._tramo(y)) and t[1] >= 1967]
            if not tardios:
                fallas.append(f"ch{f['cap']:02d}: sin tramos de 1967+ ({f['periods']})")
    L += ["", f"**Resultado: {'PASA' if not fallas else 'NO PASA — PARADA'}**", ""] + [f"- {x}" for x in fallas]
    for n in (5, 6, 7):
        txt = (F50F / "pedidos" / f"pedido_ch{n:02d}.txt").read_text(encoding="utf-8")
        i = txt.index("ERA (capa genérica de la época):")
        j = txt.index("LUGAR PUNTUAL", i)
        L += ["", f"## Bloque ERA del cap {n}", "", "```", txt[i:j].rstrip(), "```"]
    (F50F / "PEDIDOS_F50f.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps({"filas": [{k: f[k] for k in ("cap", "periods", "fuera_del_canon_y_grupos", "grupos")}
                                for f in d["filas"]], "fallas": fallas}, ensure_ascii=False))
    return 0 if not fallas else 1


if __name__ == "__main__":
    sys.path.insert(0, str(F50F.parents[2]))
    sys.exit(main())
