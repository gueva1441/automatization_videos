# -*- coding: utf-8 -*-
"""
lab/hyperframes/f65/revalida.py — F65a Etapa A, salida en texto (solo lectura, CERO llamadas al modelo): re-valida con el
`validar` nuevo (a_pantalla ya no es motivo) dos papeles, con un juez de CACHÉ que devuelve los veredictos guardados por
`pedido_md5`; si un pedido no está guardado, PARÁ (no se llama al verificador).
  1. el papel actual de Wittenoom: `data/scripts/_steps/<tid>/01e_pantalla.raw.json` → `final`, caché = `raw["verificador"]`;
  2. `lab/hyperframes/f63/a/O2_1.raw.json` → `respuesta`, caché = `lab/hyperframes/f64/sim/O2_1.json` (`verificador`).
Para cada uno: motivos y claves ANTES (regla de F38c §A.1 reconstruida acá: cada `a_pantalla_vacios` sumaba un motivo y
la clave ("a_pantalla", cap, beat)) y DESPUÉS (lo que devuelve `validar` hoy), y `a_pantalla_vacios` (igual en ambos).
Escribe lab/hyperframes/f65/REVALIDA.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from script_engine import m01e_pantalla as m  # noqa: E402
from script_engine import pantalla_verificador as pv  # noqa: E402
from script_engine.clima import vocabulario_clima  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps"
AQUI = Path(__file__).resolve().parent


def juez_cache(guardados: list[dict], nombre: str):
    por_md5 = {g["pedido_md5"]: g for g in guardados}

    def juez(marcas, caps):
        h = pv.pedido_md5(pv.pedido(marcas, caps))
        g = por_md5.get(h)
        if g is None:
            raise SystemExit(f"PARÁ: {nombre}: el pedido_md5 {h} de {len(marcas)} marcas no está en la caché "
                             f"({sorted(por_md5)}); no se llama al verificador")
        vs = g["veredictos"] if "veredictos" in g and isinstance(g["veredictos"], dict) and "fichas" in g["veredictos"] else None
        if vs is not None:                                     # raw de producción: {fichas, descartes, …}
            return {"veredictos_fichas": vs["fichas"], "veredictos_descartes": vs["descartes"], "usd": 0.0, "pedido_md5": h,
                    "cache": True}
        return {"veredictos_fichas": g["veredictos_fichas"], "veredictos_descartes": g["veredictos_descartes"], "usd": 0.0,
                "pedido_md5": h, "cache": True}                 # sim/*.json: lo que devolvió verificar
    return juez


def antes(val: dict) -> tuple[list[str], list[tuple]]:
    """La regla vieja (F38c §A.1, hasta 5225edf): un motivo y una clave por `a_pantalla_vacios`, después de los picos."""
    motivos, claves = list(val["motivos"]), [tuple(c) for c in val["claves"]]
    for a in val["a_pantalla_vacios"]:
        motivos.append(f"el beat {a['beat']} de {a['cap']} quedó sin ninguno de los datos que la escaleta dejó para la "
                       f"pantalla porque la voz no los dice: " + ", ".join(f"{x['id']} («{x['por_que']}»)" for x in a["ids"]))
        claves.append(("a_pantalla", a["cap"], a["beat"]))
    return motivos, claves


def tabla(nombre: str, val: dict) -> list[str]:
    ma, ca = antes(val)
    md_, cd = list(val["motivos"]), [tuple(c) for c in val["claves"]]
    L = [f"### {nombre}", "", "| | antes (F38c §A.1) | después (F65a) |", "|---|---|---|",
         f"| motivos | {len(ma)} | {len(md_)} |", f"| claves | {len(ca)} | {len(cd)} |",
         f"| motivos `a_pantalla` | {len(ma) - len(md_)} | 0 |",
         f"| `a_pantalla_vacios` | {[(a['cap'], a['beat'], [x['id'] for x in a['ids']]) for a in val['a_pantalla_vacios']]} | igual |",
         f"| fichas que quedan | {sum(1 for b in val['beats'] if b['ficha'])}/13 | igual |",
         f"| cortadas por el verificador (caché) | {[d['pool_id'] for d in val['descartados'] if d.get('quien') == 'verificador']} | igual |", "",
         "Claves antes: " + ("; ".join("(" + ", ".join(str(x) for x in c) + ")" for c in ca) or "ninguna"), "",
         "Claves después: " + ("; ".join("(" + ", ".join(str(x) for x in c) + ")" for c in cd) or "ninguna"), "",
         "Motivos después (los que siguen):"] + ([f"- {x}" for x in md_] or ["- (ninguno)"]) + [""]
    return L


def main() -> None:
    carga = m.cargar(TID, STEPS)
    ent = m.entrada(carga, vocabulario_clima())
    ent["_pool"] = carga["pool"]
    raw = json.loads((STEPS / TID / "01e_pantalla.raw.json").read_text(encoding="utf-8"))
    assert raw.get("prompt_version") == m.PROMPT_VERSION and raw.get("final"), "el raw de producción no es el de m01e-7"
    v1 = m.validar(raw["final"], ent, juez=juez_cache(raw["verificador"], "Wittenoom raw"))
    o2 = json.loads((ROOT / "lab/hyperframes/f63/a/O2_1.raw.json").read_text(encoding="utf-8"))["respuesta"]
    sim = json.loads((ROOT / "lab/hyperframes/f64/sim/O2_1.json").read_text(encoding="utf-8"))["verificador"]
    v2 = m.validar(o2, ent, juez=juez_cache([sim], "O2_1 sim"))
    L = ["# F65a Etapa A — REVALIDA: `a_pantalla` ya no es motivo de vuelta (solo lectura, 0 llamadas)", "",
         f"Entrada de producción de hoy (`entrada_md5` {m.entrada_md5(ent)}), `validar` de `{m.PROMPT_VERSION}`; juez = caché por "
         "`pedido_md5` (raw de producción / `lab/hyperframes/f64/sim/O2_1.json`). «Antes» = la regla de F38c §A.1 reconstruida "
         "sobre el mismo `a_pantalla_vacios` (un motivo y una clave por beat sin su a_pantalla).", ""]
    L += tabla("1. Papel actual de Wittenoom (`01e_pantalla.raw.json` → `final`, m01e-7, 13 fichas)", v1)
    L += tabla("2. O2_1 de F63 (`respuesta` del intento 1 de Opus medium con entrada completa)", v2)
    (AQUI / "REVALIDA.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
