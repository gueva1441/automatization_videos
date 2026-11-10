"""F79: compara dos copias del guion de pantalla de Wittenoom (lab/hyperframes/f79/<a>/ contra <b>/).

Uso: python lab/hyperframes/f79/comparar.py <a> <b> [--corrimiento ch01=0,ch02=-3.0,...] [--sin-tc ch01]

Imprime en markdown: duración, por cap (offset, seg_dur, voz en el mp4, inicio de voz medido), eventos emparejados por
(tipo, etiqueta, texto) en orden con su `t`, `queda` y la clase de diferencia (tiempo / reserva / crítico / otra), el
golpe del title card, la música por cap, los chequeos en ✗ y los veredictos del crítico (de los logs gfx_chXX.log, la
última corrida de cada uno). Solo lee archivos del lab; no escribe nada.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CUADRO = 1 / 30


def cargar(d: str) -> dict:
    return json.loads((AQUI / d / "GUION_PANTALLA.json").read_text(encoding="utf-8"))


def log_ultimo(d: str, cap: str, con: str = "") -> list[str]:
    """La última corrida del log del cap (el log se va sumando); con `con`, la última que tiene una línea con eso
    (un render con el plan congelado no pregunta al crítico)."""
    f = AQUI / d / "_fase2b_work" / f"gfx_{cap}.log"
    if not f.exists():
        return []
    lineas = f.read_text(encoding="utf-8", errors="replace").splitlines()
    cortes = [i for i, l in enumerate(lineas) if re.match(r"^\[\d{4}-\d\d-\d\d .*\] " + cap + " base=", l)] or [0]
    bloques = [lineas[a:b] for a, b in zip(cortes, cortes[1:] + [len(lineas)])]
    for b in reversed(bloques):
        if not con or any(con in l for l in b):
            return b
    return []


def critico(d: str, cap: str) -> list[tuple[str, str, str, bool]]:
    out = []
    for l in log_ultimo(d, cap, "crítico (¿estorba?)"):
        m = re.search(r"crítico \(¿estorba\?\):\s+([\d.]+)s (\S+)\s+«(.*)» → (NO ESTORBA|ESTORBA)", l)
        if m:
            out.append((m.group(2), m.group(3), m.group(4), "(caché)" in l, float(m.group(1))))
    return out


def sfx(d: str, cap: str) -> tuple[list, list[str]]:
    f = AQUI / d / "_fase2b_work" / f"gfx_sfx_{cap}.json"
    ev = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    desc = [l.strip() for l in log_ultimo(d, cap) if "sfx descartado" in l]
    return [(e["block"], e["t"], e.get("shift_ms")) for e in ev], desc


def clave(e: dict) -> tuple:
    return (e["tipo"], e.get("etiqueta") or "", e.get("texto") or "")


def emparejar(ea: list[dict], eb: list[dict]) -> list[tuple[dict | None, dict | None]]:
    usados, pares = set(), []
    for a in ea:
        j = next((j for j, b in enumerate(eb) if j not in usados and clave(b) == clave(a)), None)
        if j is None and a["tipo"] == "costura":
            j = next((j for j, b in enumerate(eb) if j not in usados and b["tipo"] == "costura"), None)
        if j is not None:
            usados.add(j)
        pares.append((a, eb[j] if j is not None else None))
    pares += [(None, b) for j, b in enumerate(eb) if j not in usados]
    return pares


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--corrimiento", default="")
    a_, b_ = ap.parse_args().a, ap.parse_args().b
    corr = {k: float(v) for k, v in (x.split("=") for x in ap.parse_args().corrimiento.split(",") if x)}
    A, B = cargar(a_), cargar(b_)
    print(f"# {a_} → {b_}\n")
    print(f"- duracion_s: {A['duracion_s']} → {B['duracion_s']} (Δ {B['duracion_s'] - A['duracion_s']:+.3f})")
    print(f"- intro_s: {A.get('intro_s')} → {B.get('intro_s')}")
    print(f"- costos: {A.get('costos')} → {B.get('costos')}\n")
    print("| cap | offset | seg_dur (Δ) | voz en el mp4 | inicio de voz medido | ok |")
    print("|---|---|---|---|---|---|")
    cb = {c["cap"]: c for c in B["caps"]}
    for c in A["caps"]:
        d = cb.get(c["cap"]) or {}
        va = (c.get("inicio_voz") or {})
        vb = (d.get("inicio_voz") or {})
        print(f"| {c['cap']} | {c['offset']} → {d.get('offset')} | {c['seg_dur']} → {d.get('seg_dur')} "
              f"({(d.get('seg_dur') or 0) - c['seg_dur']:+.3f}) | {va.get('esperado')} → {vb.get('esperado')} | "
              f"{va.get('medido')} → {vb.get('medido')} | {va.get('ok')} → {vb.get('ok')} |")
    print()
    for c in A["caps"]:
        cap = c["cap"]
        d = cb.get(cap) or {"eventos": []}
        print(f"## {cap} — {c.get('titulo')} → {d.get('titulo')}\n")
        s = corr.get(cap, 0.0)
        print("| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |")
        print("|---|---|---|---|---|---|")
        for ea, eb in emparejar(c["eventos"], d["eventos"]):
            if ea and eb:
                dt = eb["t"] - ea["t"]
                esperado = 0.0 if ea["t"] == 0.0 else s
                if ea["queda"] != eb["queda"] or (ea.get("filtro") != eb.get("filtro") and "crítico" in str(eb.get("filtro")) + str(ea.get("filtro"))):
                    clase = "crítico" if "crítico" in str(eb.get("filtro")) + str(ea.get("filtro")) else "otra"
                elif abs(dt - esperado) <= CUADRO + 1e-6:
                    clase = "tiempo" if dt else "igual"
                elif "title card" in str(eb.get("movido") or "") + str(eb.get("filtro") or ""):
                    clase = "reserva del title card"
                else:
                    clase = "otra"
                if ea["tipo"] == "costura" and ea.get("texto") != eb.get("texto"):
                    clase += " (texto de costura nuevo)"
                if clase == "igual":
                    continue
                print(f"| {ea['tipo']} | {(ea.get('texto') or '')[:60]} | {ea['t']} → {eb['t']} ({dt:+.3f}) | "
                      f"{ea['t_mp4']} → {eb['t_mp4']} | {ea['queda']} → {eb['queda']} | {clase} |")
            elif ea:
                print(f"| {ea['tipo']} | {(ea.get('texto') or '')[:60]} | {ea['t']} → — | {ea['t_mp4']} → — | "
                      f"{ea['queda']} → — | otra (no está) |")
            else:
                print(f"| {eb['tipo']} | {(eb.get('texto') or '')[:60]} | — → {eb['t']} | — → {eb['t_mp4']} | "
                      f"— → {eb['queda']} | otra (nuevo) |")
        n_igual = sum(1 for ea, eb in emparejar(c["eventos"], d["eventos"]) if ea and eb and ea["t"] == eb["t"]
                      and ea["queda"] == eb["queda"])
        print(f"\n{len(c['eventos'])} → {len(d['eventos'])} eventos; {n_igual} con el mismo `t` y `queda`.\n")
        for e in d["eventos"]:
            if e["tipo"] == "costura":
                print(f"- costura después: {e['texto']}")
                print(f"- tramos después: {e.get('tramos')}\n")
        sa, sb = sfx(a_, cap), sfx(b_, cap)
        print(f"- golpe del title card: {sa[0]} {sa[1]} → {sb[0]} {sb[1]}")
        def _por_bloque(lst):                       # (tipo, texto) → veredictos en orden (un bloque se pregunta por lado)
            g: dict = {}
            for k, t, v, _, tt in lst:
                g.setdefault((k, t), []).append((v, tt))
            return g
        ka, kb = _por_bloque(critico(a_, cap)), critico(b_, cap)
        gb = _por_bloque(kb)
        cambios = [(k, t, [x[0] for x in ka.get((k, t), [])], [x[0] for x in vs], [x[1] for x in vs])
                   for (k, t), vs in gb.items() if [x[0] for x in ka.get((k, t), [])] != [x[0] for x in vs]]
        print(f"- crítico: {len(kb)} preguntas, {sum(1 for x in kb if not x[3])} llamadas (sin caché); "
              f"veredictos que cambiaron: {cambios or 'ninguno'}\n")
    print("## Música por cap\n")
    mb = {r["cap"]: r for r in (B.get("mezcla") or {}).get("musica") or []}
    for r in (A.get("mezcla") or {}).get("musica") or []:
        q = mb.get(r["cap"]) or {}
        print(f"- {r['cap']}: {json.dumps({k: v for k, v in r.items() if k != 'cap'}, ensure_ascii=False)} → "
              f"{json.dumps({k: v for k, v in q.items() if k != 'cap'}, ensure_ascii=False)}")
    print("\n## Chequeos\n")
    nb = {ch["nombre"]: ch for ch in B["chequeos"]}
    for ch in A["chequeos"]:
        q = nb.get(ch["nombre"]) or {}
        print(f"- {'✓' if ch['ok'] else '✗'} → {'✓' if q.get('ok') else '✗'} {ch['nombre']}")
        if not ch["ok"] or not q.get("ok"):
            for l in q.get("lineas") or []:
                if l.startswith("✗"):
                    print(f"    - {l}")
    for n in nb:
        if n not in {ch["nombre"] for ch in A["chequeos"]}:
            print(f"- (nuevo) {'✓' if nb[n]['ok'] else '✗'} {n}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
