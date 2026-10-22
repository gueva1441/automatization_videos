"""F7a: R1 descubrimiento + R2 descarga de fuentes de Orleans (topic ba6c3cac-f7r3). 2 Pro + Google Search.

Deja data/scripts/_steps/ba6c3cac-f7r3/fuentes.json (R1, con caché cruda en _r1_cache.json), fuentes/<slug>.* +
fuentes/manifest.json (R2) y lab/hyperframes/f7/F7a_fuentes.md (tabla url/tipo/año/bytes/ok).
Los documentos que F6c ya bajó (ACLU PDF, BBC/rebelion, The Lens) se copian desde ba6c3cac-f6v3/fuentes si su URL
aparece en el grounding: no se vuelven a pedir.
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f7/f7a_fuentes_orleans.py [--solo-r2]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
TOPIC = "ba6c3cac-f7r3"
STEPS = ROOT / "data" / "scripts" / "_steps" / TOPIC
OLD_SRC = ROOT / "data" / "scripts" / "_steps" / "ba6c3cac-f6v3" / "fuentes"
LAB = Path(__file__).resolve().parent
SEED = {"seed_title": "Prisión Parroquial de Orleans (OPP) durante el huracán Katrina, 2005",
        "lugar_idioma": "inglés (Nueva Orleans, Luisiana, EE. UU.)"}
PLACE_RE = r"Orleans Parish|\bOPP\b|Katrina|Templeman|Jefferson Parish Prison"
# documentos que el analista sabe que existen (handoff F7 §4): R1 busca su página; si no está en el grounding, no entra
PISTAS = [
    "ACLU National Prison Project, «Abandoned & Abused: Orleans Parish Prisoners in the Wake of Hurricane Katrina» (2006, PDF completo)",
    "Human Rights Watch, «New Orleans: Prisoners Abandoned to Floodwaters» (2005)",
    "U.S. Department of Justice, Civil Rights Division, Orleans Parish Prison findings letter (2009/2010)",
    "BBC, Olenka Frenkiel, sobre los presos de Katrina (2006)",
    "The Times-Picayune / NOLA.com, notas de la semana del 29 de agosto de 2005 sobre la cárcel",
    "The Lens, «Reforms resulted from the thousands left to drown in OPP» (2025)",
    "Toledo Blade, George J. Tanber, «Arrested on misdemeanors, left to die in flooded jail» (2005)",
    "Fallo judicial Waganfeald v. Gusman (Robie Waganfeald y Paul Kunkel, 5th Circuit)",
]
LOCAL = {
    "aclu.org/sites/default/files/pdfs/prison/oppreport20060809.pdf": OLD_SRC / "aclu_abandoned_and_abused.pdf",
    "rebelion.org/los-presos-de-katrina": OLD_SRC / "rebelion_presos_katrina.html",
    "thelensnola.org/2025/08/29/reforms-resulted-from-the-thousands-left-to-drown-in-opp":
        OLD_SRC / "thelens_2025_opp.html",
}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    from cost_tracker import cost_tracker
    from researcher_steps import research_v3 as r3
    log: list[str] = []
    STEPS.mkdir(parents=True, exist_ok=True)
    fpath = STEPS / "fuentes.json"
    t0 = time.time()
    if "--solo-r2" in sys.argv and fpath.exists():
        r1 = json.loads(fpath.read_text(encoding="utf-8"))
    else:
        cost_tracker.start_video(TOPIC)
        try:
            r1 = r3.discover_sources(SEED, pistas=PISTAS, cache=STEPS / "_r1_cache.json", log=log)
        finally:
            rep = cost_tracker.end_video()
        r1["_costo"] = {"usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1)}
        fpath.write_text(json.dumps(r1, ensure_ascii=False, indent=1), encoding="utf-8")
    man = r3.download_sources(r1["fuentes"], STEPS / "fuentes", place_re=PLACE_RE, local=LOCAL, log=log)
    cost_tracker.start_video(TOPIC)
    try:
        r3.refine_fichas(man, STEPS / "fuentes", SEED, log=log)
    finally:
        rep = cost_tracker.end_video()
    r1["_costo"]["fichas_usd"] = round(getattr(rep, "total_cost", 0.0) or 0.0, 4)
    (STEPS / "fuentes" / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    fpath.write_text(json.dumps(r1, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(log))
    write_report(r1, man)


def write_report(r1: dict, man: dict) -> None:
    docs = {d["id"]: d for d in man["documentos"]}
    ok = [d for d in man["documentos"] if d.get("ok")]
    L = ["# F7a — Fuentes de Orleans (R1 descubrimiento + R2 descarga)", "",
         f"Topic `ba6c3cac-f7r3` · R1 `{r1.get('prompt_version')}` · costo R1 US$ {r1.get('_costo', {}).get('usd')} "
         f"({r1.get('_costo', {}).get('segundos')} s) · {len(r1['fuentes'])} fuentes aceptadas del grounding, "
         f"{len(r1.get('_descartadas') or [])} descartadas · **{len(ok)} documentos bajados**.", "",
         "Ficha: `exacta` / `similar x` = la del modelo para esa URL del grounding; `ficha_flash` = URL del grounding que "
         "el modelo no listó, fichada por Flash. Ninguna URL sale del modelo.", "",
         "| id | tipo | año | prio | ficha | título | url | bytes | caracteres txt | idioma | ok | nota |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for f in r1["fuentes"]:
        d = docs.get(f["id"], {})
        nota = d.get("motivo") or ""
        if d.get("ok"):
            nota = "; ".join(x for x in [f"vía {d['via']}" if d.get("via") != "original" else "",
                                         "copia local de F6c" if any(i.get("copia_local") for i in d["intentos"]) else "",
                                         d.get("recorte") or "", "" if d.get("nombra_evento") else "NO nombra el evento en 5 k"]
                             if x)
        elif d.get("intentos"):
            nota = " → ".join(f"{i['via']}: {i.get('status') or i.get('error')}" for i in d["intentos"])
        g = d if d.get("ficha_busqueda") else f                 # ficha leída del documento, si se bajó
        L.append(f"| {f['id']} | {g['tipo']} | {g.get('anio') or ''} | {f['prioridad']} | {f.get('match')} | "
                 f"{g['titulo'][:70]} | {f['url']} | {d.get('bytes', '')} | {d.get('caracteres', '')} | "
                 f"{d.get('idioma', '')} | {'✔' if d.get('ok') else '✖'} | {nota} |")
    if r1.get("_descartadas"):
        L += ["", "## Fuentes del modelo fuera (URL que no está en el grounding)", ""]
        L += [f"- {f.get('titulo', '')[:80]} — `{f.get('url')}`" for f in r1["_descartadas"]]
    (LAB / "F7a_fuentes.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
