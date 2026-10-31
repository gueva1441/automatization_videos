# -*- coding: utf-8 -*-
"""
lab/hyperframes/f64/etapa2_relato.py — F64 Etapa 2, salida en texto: el año del relato VIEJO («el último año que dijo
la voz», F37 §A.1b, reimplementado acá tal cual porque el código ya no lo tiene) contra el NUEVO (m01e_pantalla.momentos:
máximo del cap sin los beats flash-forward, heredado del cap anterior) sobre Wittenoom, con la función real
(voz_utils.anios_dichos). Escribe lab/hyperframes/f64/ETAPA2_relato.md:
  1. la tabla del handoff (D23 [18], D23 [12], T57 [2], D94 [8], D83 [7]) con corta/pasa por la regla `fecha_relato`
     (anio > relato, sin testimonio, sin `dice_anio` en la oración ancla ± 1);
  2. una fila por cada oración donde el relato nuevo ≠ el viejo;
  3. qué lee `anios_dichos` en ch06 [7] («dos mil»).
Solo lee data/ (cargar/entrada de producción); no escribe nada fuera de f64/. Sin llamadas al modelo.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from script_engine import m01e_pantalla as m  # noqa: E402
from script_engine.clima import vocabulario_clima  # noqa: E402
from script_engine.voz_utils import anio_de, anios_dichos, dice_anio  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps"
AQUI = Path(__file__).resolve().parent
# la tabla del handoff: (ficha, cap, idx)
FILAS = [("D23", "ch05", 18), ("D23", "ch05", 12), ("T57", "ch06", 2), ("D94", "ch05", 8), ("D83", "ch02", 7)]


def momentos_viejo(ent: dict) -> dict[tuple[str, int], int | None]:
    """F37 §A.1b tal cual estaba en m01e_pantalla hasta F64 Etapa 1: el último año dicho, arrastrado entre caps."""
    out: dict[tuple[str, int], int | None] = {}
    ultimo = None
    for c in ent["caps"]:
        for s in c["oraciones"]:
            ys = anios_dichos(s["texto"], ent.get("anios"))
            if ys:
                ultimo = ys[-1]
            out[(c["cap"], s["idx"])] = ultimo
    return out


def veredicto(ent: dict, pool_items: dict, pid: str, cap: str, idx: int, relato: int | None) -> str:
    """La regla `fecha_relato` sobre una ficha: corta si anio > relato, no es testimonio y ni la oración ni sus vecinas
    sitúan el año (dice_anio). F64 Etapa 3: donde hoy cortaría pasa a ser una marca para el verificador."""
    it = pool_items[pid]
    anio = anio_de(it.get("fecha"))
    c = next(c for c in ent["caps"] if c["cap"] == cap)
    vecinas = " ".join(s["texto"] for s in c["oraciones"][max(0, idx - 1):idx + 2])
    if anio and relato and anio > relato and not it.get("testimonio") and not dice_anio(anio, vecinas, ent.get("anios")):
        return "corta"
    return "pasa"


def main() -> None:
    from script_engine import evidence as ev
    carga = m.cargar(TID, STEPS)
    ent = m.entrada(carga, vocabulario_clima())
    its = ev.items(carga["pool"])
    viejo, nuevo, det = momentos_viejo(ent), m.momentos(ent), m.momentos_detalle(ent)
    L = ["# F64 Etapa 2 — el año del relato: viejo (último año dicho) vs nuevo (máximo del cap) sobre Wittenoom", "",
         f"Topic `{TID}` · rango de años del material {ent['anios']} · beats flash-forward: "
         f"{[b['n'] for b in ent['beats'] if b.get('flash_forward')]} · calculado con `voz_utils.anios_dichos` y "
         f"`m01e_pantalla.momentos` (el viejo, reimplementado en este script tal cual F37 §A.1b).", "",
         "## 1. La tabla del handoff, con la función real", "",
         "| ficha | año | ancla | relato hoy (viejo) | relato nuevo |", "|---|---|---|---|---|"]
    for pid, cap, idx in FILAS:
        anio = anio_de(its[pid].get("fecha"))
        rv, rn = viejo[(cap, idx)], nuevo[(cap, idx)]
        vv, vn = veredicto(ent, its, pid, cap, idx, rv), veredicto(ent, its, pid, cap, idx, rn)
        vn_txt = "marca (la decide el verificador, Etapa 3)" if vn == "corta" else vn
        L.append(f"| {pid} | {anio} | {cap} [{idx}] | {rv} → {vv} | {rn} → {vn_txt} |")
    L += ["", "## 2. Oraciones de Wittenoom donde el relato nuevo ≠ el viejo", "",
          "| cap | idx | beat | viejo | nuevo | de dónde sale el nuevo | oración |", "|---|---|---|---|---|---|---|"]
    n_dif = 0
    for c in ent["caps"]:
        for s in c["oraciones"]:
            k = (c["cap"], s["idx"])
            if viejo[k] != nuevo[k]:
                n_dif += 1
                d = det[k]
                de = ("— (ningún año dicho fuera del flash-forward)" if d["anio"] is None else
                      f"{'heredado de ' if d['heredado'] else 'dicho en '}{d['cap']} [{d['idx']}]")
                L.append(f"| {c['cap']} | {s['idx']} | {s['beat']} | {viejo[k]} | {nuevo[k]} | {de} | "
                         f"{s['texto'][:110].replace('|', '/')} |")
    L += ["", f"Total: {n_dif} oraciones distintas de {sum(len(c['oraciones']) for c in ent['caps'])}.", "",
          "## 3. «dos mil» en ch06 [7]", ""]
    c6 = next(c for c in ent["caps"] if c["cap"] == "ch06")
    s7 = c6["oraciones"][7]
    L += [f"- oración: «{s7['texto']}»", f"- `anios_dichos` lee: {anios_dichos(s7['texto'], ent['anios'])}",
          f"- relato viejo en ch06 [7]–[9]: {[viejo[('ch06', i)] for i in (7, 8, 9)]} · nuevo: "
          f"{[nuevo[('ch06', i)] for i in (7, 8, 9)]}", ""]
    (AQUI / "ETAPA2_relato.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
