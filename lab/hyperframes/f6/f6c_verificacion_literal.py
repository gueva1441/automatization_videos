"""F6c (validación del analista sobre f6b-3, punto A): verificación LITERAL de los testimonios de Orleans v3 contra
los documentos fuente bajados, más los cambios editoriales que pidió el analista. Sin API (los documentos ya están en
data/scripts/_steps/ba6c3cac-f6v3/fuentes/; se bajan solos si faltan; el PDF se pasa a texto con pdftotext).

Documentos:
    bbc_rebelion  «Los presos de Katrina», Olenka Frenkiel (BBC), 15/08/2006 — copia en rebelion.org
    aclu_2006     ACLU National Prison Project, «Abandoned and Abused», 09/08/2006 (PDF completo)
    thelens_2025  The Lens, «Reforms resulted from the thousands left to drown in OPP», 29/08/2025
Cambios editoriales (el analista):
    contaminación  Lenore Burnley / Chad Joseph salen de una nota de la ACLU de 2026 sobre Trinidad: fuera del pool
    Q05            «Era como un campo de concentración…»: en la ACLU 2006 lo dice un preso anónimo sobre la cárcel de
                   Hunt, no Vincent Norman ni la OPP → atribución errónea: fuera del pool
    Q04            el texto literal de la BBC: «Simplemente abandonaron la cárcel» (antes, la traducción de Gemini)
    dato nuevo     Norman debía estar ~1 semana y estuvo 103 días (BBC), literal
Deja el pool en 01_facts_sources.json (antes: produccion previa en lab/hyperframes/f6/01_facts_sources_pre_f6c.json)
y lab/hyperframes/f6/F6c_verificacion.md.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f6/f6c_verificacion_literal.py
"""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
STEPS = ROOT / "data" / "scripts" / "_steps" / "ba6c3cac-f6v3"
SRC = STEPS / "fuentes"
LAB = Path(__file__).resolve().parent
EVENT_YEAR = 2005
PLACE_RE = r"Orleans Parish|\bOPP\b|Katrina"
DOCS = [
    {"id": "bbc_rebelion", "url": "https://rebelion.org/los-presos-de-katrina/", "fecha": "2006-08-15",
     "titulo": "«Los presos de Katrina», Olenka Frenkiel (BBC) — copia en rebelion.org", "file": "rebelion_presos_katrina"},
    {"id": "aclu_2006", "url": "https://www.aclu.org/sites/default/files/pdfs/prison/oppreport20060809.pdf",
     "fecha": "2006-08-09", "titulo": "ACLU National Prison Project, «Abandoned and Abused» (2006)",
     "file": "aclu_abandoned_and_abused"},
    {"id": "thelens_2025",
     "url": "https://thelensnola.org/2025/08/29/reforms-resulted-from-the-thousands-left-to-drown-in-opp/",
     "fecha": "2025-08-29", "titulo": "The Lens, «Reforms resulted from the thousands left to drown in OPP» (2025)",
     "file": "thelens_2025_opp"},
]
CONTAMINADOS = ("Burnley", "Chad Joseph")
NORMAN_103 = ("Norman no debería haber estado allí más de una semana. En vez, pasó 103 días en la cárcel sin agua ni "
              "comida y en condiciones insalubres, mientras el agua subía.")
Q04_BBC = "Simplemente abandonaron la cárcel"
FUENTE_BBC = "BBC (Olenka Frenkiel), «Los presos de Katrina», 2006 — copia en rebelion.org"


def _text(doc: dict) -> str:
    SRC.mkdir(parents=True, exist_ok=True)
    txt = SRC / f"{doc['file']}.txt"
    if doc["id"] == "aclu_2006":
        txt = SRC / "aclu_raw.txt"
    if not txt.exists():
        raw_ext = ".pdf" if doc["url"].endswith(".pdf") else ".html"
        raw = SRC / f"{doc['file']}{raw_ext}"
        if not raw.exists():
            req = urllib.request.Request(doc["url"], headers={"User-Agent": "Mozilla/5.0"})
            raw.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        if raw_ext == ".pdf":
            subprocess.run(["pdftotext", str(raw), str(txt)], check=True)
        else:
            s = raw.read_bytes().decode("utf-8", errors="replace")
            s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
            txt.write_text(re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))), encoding="utf-8")
    return txt.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    from researcher_steps.verify_quotes import find_literal, verify_literal
    f = STEPS / "01_facts_sources.json"
    pre = LAB / "01_facts_sources_pre_f6c.json"
    if not pre.exists():
        shutil.copy2(f, pre)
    fs = json.loads(pre.read_text(encoding="utf-8"))           # siempre desde el pool previo: idempotente
    pool = fs["evidence_pool"]
    log: list[str] = []
    docs = [{**d, "texto": _text(d)} for d in DOCS]
    gone = pool.setdefault("_descartados", [])

    # contaminación (el analista): nota ACLU 2026 sobre Trinidad
    for k in ("citas", "personajes", "datos", "cronologia"):
        keep = []
        for it in pool.get(k) or []:
            blob = json.dumps(it, ensure_ascii=False)
            if any(c in blob for c in CONTAMINADOS):
                gone.append({"kind": k, "id": it["id"], "texto": it.get("texto") or it.get("nombre") or it.get("evento"),
                             "motivo": "contaminación: Lenore Burnley / Chad Joseph salen de una nota de la ACLU de 2026 "
                                       "sobre Trinidad, no de Orleans 2005 (validación del analista)"})
                log.append(f"  [pool] {it['id']} fuera por contaminación (Burnley / Chad Joseph, ACLU 2026, Trinidad)")
            else:
                keep.append(it)
        pool[k] = keep
    # Q05: atribución errónea
    q05 = next((q for q in pool["citas"] if q["id"] == "Q05"), None)
    aclu = next(d for d in docs if d["id"] == "aclu_2006")
    if q05 and find_literal("It was like a concentration camp", aclu["texto"]) is not None:
        pool["citas"] = [q for q in pool["citas"] if q["id"] != "Q05"]
        gone.append({"kind": "citas", "id": "Q05", "texto": q05["texto"],
                     "motivo": "atribución errónea: en la ACLU 2006 «It was like a concentration camp» lo dice un preso "
                               "anónimo sobre la cárcel de Hunt, no Vincent Norman ni la OPP"})
        log.append("  [pool] Q05 fuera: atribución errónea (ACLU 2006: preso anónimo, cárcel de Hunt)")
    # Q04: el literal de la BBC
    bbc = next(d for d in docs if d["id"] == "bbc_rebelion")
    q04 = next((q for q in pool["citas"] if q["id"] == "Q04"), None)
    if q04 and find_literal(Q04_BBC, bbc["texto"]) is not None:
        q04["texto_anterior"] = q04["texto"]
        q04.update({"texto": Q04_BBC, "fuente": FUENTE_BBC, "fecha": "2006"})
        log.append(f"  [pool] Q04 → literal de la BBC «{Q04_BBC}» (antes «{q04['texto_anterior']}»)")
    # dato nuevo: 103 días (literal BBC)
    if find_literal(NORMAN_103, bbc["texto"]) is not None and not any("103 días" in d["texto"] for d in pool["datos"]):
        nid = f"D{max(int(d['id'][1:]) for d in pool['datos']) + 1:02d}"
        pool["datos"].append({"id": nid, "texto": NORMAN_103, "tipo": "cifra", "valor": "103 días", "fecha": None,
                              "bloque": "testimonios", "fuente": FUENTE_BBC})
        log.append(f"  [pool] {nid} nuevo: Norman, 103 días (literal BBC)")
    else:
        nid = next((d["id"] for d in pool["datos"] if "103 días" in d["texto"]), None)

    n = verify_literal(pool, docs, event_year=EVENT_YEAR, place_re=PLACE_RE, log=log)
    n2 = verify_literal(pool, docs, event_year=EVENT_YEAR, place_re=PLACE_RE, ids=[nid], log=log) if nid else {}
    fs["evidence_pool"] = pool
    fs["_f6c"] = {"verificacion_literal": {"conteo": n, "dato_103": n2, "documentos": [
        {k: d[k] for k in ("id", "url", "fecha", "titulo")} for d in DOCS]}, "log": log}
    f.write_text(json.dumps(fs, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# F6c — Verificación LITERAL de testimonios (Orleans v3)", "",
             "Regla del analista: se baja el documento fuente y se busca la cita literal (no el dominio). El documento "
             f"vale si es de ≤ {EVENT_YEAR + 20} y nombra el lugar o el evento. Verificada = literal + el autor a ≤ 400 "
             "caracteres; literal sin el autor = se usa sin nombre.", "", "## Documentos", ""]
    lines += [f"- **{d['id']}** — {d['titulo']} · {d['url']}" for d in DOCS]
    lines += ["", f"## Resultado: {n}", "", "| id | autor | estado | documento | motivo |", "|---|---|---|---|---|"]
    for q in pool["citas"] + [d for d in pool["datos"] if d["id"] == nid]:
        v = q.get("verificacion")
        if v:
            lines.append(f"| {q['id']} | {q.get('autor') or '(dato)'} | **{v['estado']}** | {v.get('documento') or '—'} | "
                         f"{v['motivo']} |")
    lines += ["", "## Fuera del pool", ""] + [f"- {g.get('id')} ({g['kind']}): {g['motivo']}" for g in gone
                                                if "contaminación" in g["motivo"] or "atribución" in g["motivo"]]
    lines += ["", "## Testimonios literales que hay en las fuentes y NO se sumaron (el pedido era solo los 103 días)", "",
              "- BBC 2006: Andrew Joseph dice haber visto un cuerpo flotando con una rata sentada en el pecho.",
              "- BBC 2006: «Nos abandonaron a nuestra suerte» — Cardell Williams, dos meses preso sin acusación.",
              "- BBC 2006: la ayudante Rhonda Ducre, sola en un ala, con una linterna casi sin pilas: «Agitaban las barras, "
              "prendían fuego las cosas, gritaban y trataban de salir de sus celdas. Era peligroso».",
              "- ACLU 2006: «fearing we were left for dead» (preso anónimo); testimonios con número de recluso.",
              "", "## Log", ""] + [f"- {x.strip()}" for x in log]
    (LAB / "F6c_verificacion.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
