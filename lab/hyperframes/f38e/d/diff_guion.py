"""
lab/hyperframes/f38e/d/diff_guion.py — F38e D (copia del de B.5): qué cambió entre el guion de B.5 (d/antes/ = b/despues/) y
el de después del --plan-only sin la fecha-hora del segundo 0 (d/despues/), evento por evento (JSON) y línea por línea (MD). Solo lectura.

    python lab/hyperframes/f38e/d/diff_guion.py
"""
from __future__ import annotations

import difflib
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
IGNORAR_TOP = {"generado", "tiempos_s", "costos"}
IGNORAR_EV = {"t_mp4"}          # se compara aparte vía offset/seg_dur


def clave(e: dict) -> tuple:
    return (e.get("cap"), e.get("tipo"), e.get("pool_id") or (e.get("texto") or "")[:40], e.get("beat"))


def main() -> None:
    a = json.loads((AQUI / "antes" / "GUION_PANTALLA.json").read_text(encoding="utf-8"))
    d = json.loads((AQUI / "despues" / "GUION_PANTALLA.json").read_text(encoding="utf-8"))
    print("## Top")
    for k in sorted(set(a) | set(d)):
        if k in IGNORAR_TOP or k in ("caps", "chequeos"):
            continue
        if a.get(k) != d.get(k):
            print(f"- {k}: {a.get(k)!r} → {d.get(k)!r}")
    print(f"- costos: {a.get('costos')} → {d.get('costos')}")
    print("\n## Caps (escalares)")
    for ca, cd in zip(a["caps"], d["caps"]):
        for k in sorted(set(ca) | set(cd)):
            if k in ("eventos", "resumen"):
                continue
            if ca.get(k) != cd.get(k):
                print(f"- {ca['cap']} {k}: {ca.get(k)!r} → {cd.get(k)!r}")
    print("\n## Eventos")
    for ca, cd in zip(a["caps"], d["caps"]):
        ea = {clave(e): e for e in ca["eventos"]}
        ed = {clave(e): e for e in cd["eventos"]}
        for k in ea.keys() - ed.keys():
            e = ea[k]
            print(f"- {ca['cap']} QUITADO: {e['tipo']} «{(e.get('texto') or '')[:60]}» @ {e.get('t')} (queda={e.get('queda')})")
        for k in ed.keys() - ea.keys():
            e = ed[k]
            print(f"- {cd['cap']} NUEVO: {e['tipo']} «{(e.get('texto') or '')[:60]}» @ {e.get('t')} (queda={e.get('queda')}) "
                  f"movido={e.get('movido')!r} filtro={e.get('filtro')!r}")
        for k in sorted(ea.keys() & ed.keys(), key=lambda x: ea[x].get("t") or 0):
            x, y = ea[k], ed[k]
            dif = {f: (x.get(f), y.get(f)) for f in sorted(set(x) | set(y)) if f not in IGNORAR_EV and x.get(f) != y.get(f)}
            if dif:
                print(f"- {ca['cap']} {x['tipo']} «{(x.get('texto') or '')[:50]}» @ {x.get('t')}:")
                for f, (v1, v2) in dif.items():
                    print(f"    · {f}: {str(v1)[:220]!r} → {str(v2)[:220]!r}")
    print("\n## Chequeos")
    cha = {c.get("nombre") or c.get("titulo") or str(i): c for i, c in enumerate(a["chequeos"])}
    chd = {c.get("nombre") or c.get("titulo") or str(i): c for i, c in enumerate(d["chequeos"])}
    for n in cha.keys() | chd.keys():
        x, y = cha.get(n), chd.get(n)
        if x != y:
            print(f"- {n}:")
            print(f"    antes:   {json.dumps(x, ensure_ascii=False)[:600]}")
            print(f"    después: {json.dumps(y, ensure_ascii=False)[:600]}")
    print("\n## MD línea a línea")
    la = (AQUI / "antes" / "GUION_PANTALLA.md").read_text(encoding="utf-8").splitlines()
    ld = (AQUI / "despues" / "GUION_PANTALLA.md").read_text(encoding="utf-8").splitlines()
    n = 0
    for line in difflib.unified_diff(la, ld, "antes", "despues", n=0, lineterm=""):
        if line.startswith(("---", "+++", "@@")):
            continue
        n += 1
        print(line[:300])
    print(f"\n({n} líneas distintas en el .md; {len(la)} → {len(ld)} líneas)")


if __name__ == "__main__":
    main()
