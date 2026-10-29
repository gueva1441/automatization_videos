"""F54 adenda 2026-10-29 18:30 (2) — panel ciego de retención: 3 modelos (Gemini Flash, Sonnet 5.5, Opus 5.5) leen los
dos guiones (viejo y nuevo) sin marcar, en orden al azar por cap, con la pregunta literal de la adenda, una por cap.
Salida: oración de abandono y nota (1–10) por cap y modelo, y la tabla de coincidencias (lo que los 3 marcan igual).
Informa, no frena. Costo ≈ US$ 0,50 (se mide con cost_tracker, id «f54-panel»).
Uso: python lab/hyperframes/f54/panel_ciego.py [--viejo DIR] [--nuevo DIR] [--salida MD] [--seco]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

PREGUNTA = ("Estás escuchando este capítulo. ¿En qué oración dejarías de escuchar y por qué? Al final, una nota de 1 a 10 "
            "de cuánto te quedarías hasta el siguiente capítulo.")
SCHEMA = {"type": "OBJECT", "properties": {"oracion_abandono": {"type": "STRING"}, "por_que": {"type": "STRING"},
                                           "nota": {"type": "INTEGER"}},
          "required": ["oracion_abandono", "por_que", "nota"]}
MODELOS = ("gemini-flash", "claude-sonnet-5-5", "claude-opus-5-5")
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
SEMILLA = 54        # el orden al azar es reproducible (número de la tanda; no es una constante del pipeline)


def _call_for(modelo: str):
    if modelo == "gemini-flash":
        from gemini_helpers import call_flash_json
        return lambda prompt, **k: call_flash_json(prompt, response_schema=SCHEMA, description=k.get("description"))
    from claude_helpers import make_call
    c = make_call(modelo, "medium")
    return lambda prompt, **k: c(prompt, response_schema=SCHEMA, description=k.get("description"))


def caps_de(d: Path) -> dict[int, str]:
    nar = json.loads((d / "01b_narration.json").read_text(encoding="utf-8"))
    return {c["chapter_number"]: c["narration"] for c in nar["chapters"]}


def prompt_cap(texto: str) -> str:
    return f"{PREGUNTA}\n\n<capitulo>\n{texto}\n</capitulo>"


def correr(viejo: dict[int, str], nuevo: dict[int, str], *, seco: bool) -> dict:
    rnd = random.Random(SEMILLA)
    res = {"orden": {}, "respuestas": []}
    calls = {m: (None if seco else _call_for(m)) for m in MODELOS}
    for cap in range(1, 8):
        par = [("viejo", viejo[cap]), ("nuevo", nuevo[cap])]
        rnd.shuffle(par)
        res["orden"][cap] = [p[0] for p in par]            # qué guion fue «primero» en este cap (ciego para el modelo)
        for cual, texto in par:
            for m in MODELOS:
                if seco:
                    r = {"oracion_abandono": "(seco)", "por_que": "", "nota": 0}
                else:
                    r = calls[m](prompt_cap(texto), description=f"f54 panel ciego cap {cap} {m}") or {}
                res["respuestas"].append({"cap": cap, "guion": cual, "modelo": m,
                                          "oracion_abandono": str(r.get("oracion_abandono") or "").strip(),
                                          "por_que": str(r.get("por_que") or "").strip(),
                                          "nota": int(r.get("nota") or 0)})
    return res


def _norm(s: str) -> str:
    from script_engine import evidence as ev
    return ev.norm(s)[:60]


def tablas(res: dict) -> str:
    L = ["## Notas (1–10) por cap y modelo", "", "| cap | " + " | ".join(f"{m} v" + " | " + f"{m} n" for m in MODELOS)
         + " | media v | media n |", "|---|" + "---|" * (2 * len(MODELOS) + 2)]
    by = {(r["cap"], r["guion"], r["modelo"]): r for r in res["respuestas"]}
    tot = {"viejo": [], "nuevo": []}
    for cap in range(1, 8):
        fila, medias = [], {}
        for g in ("viejo", "nuevo"):
            ns = [by[(cap, g, m)]["nota"] for m in MODELOS]
            medias[g] = round(sum(ns) / len(ns), 1)
            tot[g].append(medias[g])
        for m in MODELOS:
            fila += [str(by[(cap, "viejo", m)]["nota"]), str(by[(cap, "nuevo", m)]["nota"])]
        L.append(f"| {cap} | " + " | ".join(fila) + f" | {medias['viejo']} | {medias['nuevo']} |")
    L.append(f"| **video** | " + " | ".join([""] * (2 * len(MODELOS))) + f" | **{round(sum(tot['viejo']) / 7, 1)}** | "
             f"**{round(sum(tot['nuevo']) / 7, 1)}** |")
    L += ["", "## Oración de abandono por cap y modelo", ""]
    for g in ("viejo", "nuevo"):
        L += [f"### {g}", "", "| cap | modelo | oración de abandono | por qué |", "|---|---|---|---|"]
        for cap in range(1, 8):
            for m in MODELOS:
                r = by[(cap, g, m)]
                L.append(f"| {cap} | {m} | {r['oracion_abandono'][:140]} | {r['por_que'][:160]} |")
        L.append("")
    L += ["## Coincidencias (los 3 modelos marcan la misma oración de abandono)", "",
          "| cap | viejo | nuevo |", "|---|---|---|"]
    for cap in range(1, 8):
        celda = {}
        for g in ("viejo", "nuevo"):
            ors = [_norm(by[(cap, g, m)]["oracion_abandono"]) for m in MODELOS]
            celda[g] = f"sí: «{by[(cap, g, MODELOS[0])]['oracion_abandono'][:100]}»" if len(set(ors)) == 1 and ors[0] \
                else ("2 de 3" if len(set(ors)) == 2 else "no")
        L.append(f"| {cap} | {celda['viejo']} | {celda['nuevo']} |")
    L += ["", "Orden en que cada modelo leyó los dos guiones por cap (ciego; semilla fija): "
          + ", ".join(f"cap {c}: {' → '.join(o)}" for c, o in res["orden"].items())]
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--viejo", default=str(ROOT / "lab/hyperframes/f54/antes"))
    ap.add_argument("--nuevo", default=str(ROOT / "data/scripts/_steps" / TID))
    ap.add_argument("--salida", default=str(ROOT / "lab/hyperframes/f54/PANEL_CIEGO.md"))
    ap.add_argument("--seco", action="store_true")
    a = ap.parse_args()
    viejo, nuevo = caps_de(Path(a.viejo)), caps_de(Path(a.nuevo))
    costo = 0.0
    if a.seco:
        res = correr(viejo, nuevo, seco=True)
    else:
        from cost_tracker import cost_tracker
        cost_tracker.start_video("f54-panel")
        try:
            res = correr(viejo, nuevo, seco=False)
        finally:
            r = cost_tracker.end_video()
            costo = round(getattr(r, "total_cost", 0.0) or 0.0, 4)
    res["costo_usd"] = costo
    md = ["# F54 — panel ciego de retención (adenda 18:30, 2)", "",
          f"Pregunta literal por cap: «{PREGUNTA}» · modelos: {', '.join(MODELOS)} · los dos guiones sin marcar, orden al "
          f"azar por cap · costo US$ {costo} · informa, no frena.", "", tablas(res), "", "## Crudo", "", "```json",
          json.dumps(res, ensure_ascii=False, indent=1), "```"]
    Path(a.salida).write_text("\n".join(md), encoding="utf-8", newline="\n")
    (Path(a.salida).with_suffix(".json")).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(md[:4]))
    print(f"respuestas: {len(res['respuestas'])} · costo {costo}")


if __name__ == "__main__":
    main()
