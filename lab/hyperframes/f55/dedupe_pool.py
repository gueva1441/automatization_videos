"""F55 B.2/B.3: aplica `research_v3._dedupe_citas` al pool de Wittenoom sin volver a investigar (sin API, sin tocar
fase1_5) y lista qué apunta a ids descartados en la escaleta, los `ids_usados` y el papel de F54 (solo listar).
Escribe el pool en data/topics_db.json (respaldo topics_db.pre_f55_dedupe.json) y en _steps/<id>/01_facts_sources.json
(los dos tenían el mismo pool). Uso: python lab/hyperframes/f55/dedupe_pool.py [--seco]  → SALIDA_B.md"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5  # noqa: E402
from researcher_steps import research_v3 as r3  # noqa: E402
from script_engine import evidence as ev  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps" / TID
ANTES = ROOT / "lab" / "hyperframes" / "f55" / "antes"


def _ids_en(obj, acc: list[tuple[str, str]], ruta: str = "") -> None:
    if isinstance(obj, str):
        if obj.startswith("Q") and obj[1:].isdigit():
            acc.append((ruta, obj))
    elif isinstance(obj, list):
        for k, v in enumerate(obj):
            _ids_en(v, acc, f"{ruta}[{k}]")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("texto", "narration", "oracion", "respaldo", "pregunta", "motivo", "cierre"):
                continue
            _ids_en(v, acc, f"{ruta}.{k}" if ruta else k)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true")
    a = ap.parse_args()
    db = json.loads(fase1_5.TOPICS_DB.read_text(encoding="utf-8"))
    topics = db.get("topics", []) if isinstance(db, dict) else db
    t = next(x for x in topics if x.get("id") == TID)
    pool = t["evidence_pool"]
    # D.0: el pool vive en TRES copias; el dedupe es idempotente (0 pares si ya se aplicó). Para las tablas se parte del
    # pool de antes (f55/antes/01_facts_sources.json, 58 citas), que es el mismo que tenían las tres.
    antes_p = json.loads((ANTES / "01_facts_sources.json").read_text(encoding="utf-8"))
    antes_p = antes_p.get("evidence_pool", antes_p)
    its_antes = ev.items(antes_p)
    n_antes = len(antes_p["citas"])
    log: list[str] = []
    fuera = r3._dedupe_citas(antes_p, log)
    r3._dedupe_citas(pool, log)                     # topics_db (ya deduplicado en B.2: 0 pares)
    fs = STEPS / "01_facts_sources.json"
    d2 = json.loads(fs.read_text(encoding="utf-8"))
    r3._dedupe_citas(d2["evidence_pool"], log)
    p3 = STEPS / "00_pool_v3.json"
    pool3 = json.loads(p3.read_text(encoding="utf-8"))
    r3._dedupe_citas(pool3.get("evidence_pool", pool3), log)
    copias = {"topics_db.json": pool, "01_facts_sources.json": d2["evidence_pool"], "00_pool_v3.json": pool3.get("evidence_pool", pool3)}
    L = ["# F55 — Salida B (texto): dedupe de citas del pool de Wittenoom", "",
         f"Regla: mismo autor (igualdad exacta tras `norm`) + |Ca∩Cb| / min(|Ca|,|Cb|) ≥ {r3.UMBRAL_DEDUPE_CITAS} "
         f"(DECISIONES 2026-10-29 19:30). Citas: {n_antes} → {len(pool['citas'])}. {'SECO: no se escribió nada.' if a.seco else 'Escrito en topics_db.json y 01_facts_sources.json.'}", "",
         "## 1. Los pares: cuál quedó y por qué", "",
         "| sale | queda | similitud | autor | n_fuentes (sale → queda) | por qué queda | texto que sale | texto que queda |",
         "|---|---|---|---|---|---|---|---|"]
    for d in fuera:
        s, q = its_antes[d["id"]], its_antes[d["duplicado_de"]]
        ns, nq = int(s.get("n_fuentes") or 0), int(q.get("n_fuentes") or 0)
        porque = "más fuentes" if nq > ns else ("más larga (empate en fuentes)" if len(q.get("texto") or "") > len(s.get("texto") or "") else "primera en el pool (empate total)")
        qn = next(x for x in pool["citas"] if x["id"] == d["duplicado_de"])
        L.append(f"| {d['id']} | {d['duplicado_de']} | {d['similitud']} | {d['autor']} | {ns} → {qn.get('n_fuentes')} (docs {qn.get('docs')}) | {porque} | {str(s.get('texto'))[:90]} | {str(q.get('texto'))[:90]} |")
    L += ["", "Pares que NO se deduplican (control del handoff §4):", ""]
    for x, y in (("Q30", "Q36"), ("Q18", "Q36"), ("Q19", "Q32")):
        qa, qb = its_antes.get(x), its_antes.get(y)
        if qa and qb:
            sim = r3._similitud_citas(qa, qb)
            L.append(f"- {x}/{y}: similitud {('%.2f' % sim) if sim is not None else 'no se compara (autores distintos o sin autor)'}"
                     f" · autores «{qa.get('autor')}» / «{qb.get('autor')}»")
    # referencias a ids descartados
    mapa = {d["id"]: d["duplicado_de"] for d in fuera}
    L += ["", "## 2. Qué apunta hoy a ids descartados (solo listar; la Parte D regenera todo desde la escaleta)", "",
          "| archivo | dónde | id | debería ser |", "|---|---|---|---|"]
    archivos = {"01a_escaleta.json": ANTES / "01a_escaleta.json", "01a_skeleton.json": ANTES / "01a_skeleton.json",
                "01b_guionista_v4.json": ANTES / "01b_guionista_v4.json", "01b_narration.json": ANTES / "01b_narration.json",
                "01e_pantalla.json": ANTES / "01e_pantalla.json"}
    n_refs = 0
    for nombre, f in archivos.items():
        acc: list[tuple[str, str]] = []
        _ids_en(json.loads(f.read_text(encoding="utf-8")), acc)
        for ruta, i in acc:
            if i in mapa:
                n_refs += 1
                L.append(f"| {nombre} | {ruta} | {i} | {mapa[i]} |")
    if not n_refs:
        L.append("| — | — | — | — |")
    L += ["", f"Total de referencias a ids descartados: {n_refs}.", "", "## 3. Las tres copias del pool (D.0)", "",
          "| copia | citas | ids de citas | descartados (citas) |", "|---|---|---|---|"]
    firmas = set()
    for nombre, pc in copias.items():
        ids = [q["id"] for q in pc["citas"]]
        desc = sorted(d["id"] for d in pc.get("_descartados") or [] if d.get("kind") == "citas")
        firmas.add((tuple(ids), tuple(desc)))
        L.append(f"| {nombre} | {len(ids)} | {', '.join(ids)} | {', '.join(desc)} |")
    L += ["", f"Las tres copias {'tienen los MISMOS ids de citas y los mismos descartados' if len(firmas) == 1 else 'DIFIEREN'}.",
          "", "Log:", ""] + [f"    {x.strip()}" for x in log]
    if not a.seco:
        bak = fase1_5.TOPICS_DB.with_name("topics_db.pre_f55_dedupe.json")
        if not bak.exists():
            shutil.copy2(fase1_5.TOPICS_DB, bak)
        fase1_5.TOPICS_DB.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
        fs.write_text(json.dumps(d2, ensure_ascii=False, indent=2), encoding="utf-8")
        p3.write_text(json.dumps(pool3, ensure_ascii=False, indent=1), encoding="utf-8")
        L += ["", f"Escrito: `{fase1_5.TOPICS_DB}` (respaldo `{bak.name}`), `{fs}` y `{p3}` (su copia de antes: `{ANTES / '00_pool_v3.json'}`)."]
    (ROOT / "lab/hyperframes/f55/SALIDA_B.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
