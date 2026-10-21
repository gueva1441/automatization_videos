"""F6a: re-research de Orleans SOLO de la sección [TESTIMONIOS] (1 Pro + Google Search, ≈ US$ 0.50) y su pool v3.

Topic nuevo `ba6c3cac-f6v3` (data/scripts/_steps/ba6c3cac-f6v3/): copia los pasos de investigación de
`ba6c3cac-f5v2` (no se toca: es el video producido) y le suma el bloque de testimonios con
`evidence_pool.add_block` (ids viejos intactos; lo nuevo sigue la numeración). Deja:
    00c_testimonios.json     el bloque crudo + seed + costo (si existe, no se vuelve a investigar)
    00d_testimonios_raw.json respuesta cruda de Flash (caché)
    01_facts_sources.json    verified_facts y sources de v2 + el pool con testimonios, testigo y presente_en
    F6a_testimonios.md       resumen legible (lab/hyperframes/f6/)
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f6/f6a_testimonios_orleans.py
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

V2, V3 = "ba6c3cac-f5v2", "ba6c3cac-f6v3"
STEPS = ROOT / "data" / "scripts" / "_steps"
SRC, DST = STEPS / V2, STEPS / V3
COPY = ("00_pool_etiquetado.json", "00b_pool_raw.json", "01_facts_sources.json", "02_canonical.json")
SEED_TITLE = "Prisión Parroquial de Orleans (OPP) durante el huracán Katrina, 2005"
REPORT = Path(__file__).resolve().parent / "F6a_testimonios.md"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _dump(p: Path, d) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    from researcher_steps.evidence_pool import add_block
    DST.mkdir(parents=True, exist_ok=True)
    for f in COPY:
        if not (DST / f).exists():
            shutil.copy2(SRC / f, DST / f)
    tfile = DST / "00c_testimonios.json"
    log: list[str] = []
    if not tfile.exists():
        import topic_researcher as tr
        from cost_tracker import cost_tracker
        cost_tracker.start_video(V3)
        t0 = time.time()
        block = tr.research_testimonios({"seed_title": SEED_TITLE})
        rep = cost_tracker.end_video()
        _dump(tfile, {"seed_title": SEED_TITLE, "block": block, "segundos": round(time.time() - t0, 1),
                      "costo_usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4),
                      "generado_en": time.strftime("%Y-%m-%d %H:%M:%S")})
    t = _load(tfile)
    block = t["block"]
    if not block.strip():
        raise SystemExit("el research de testimonios volvió vacío")
    ab = _load(DST / "00_pool_etiquetado.json")
    ab["angle_blocks"]["testimonios"] = block
    _dump(DST / "00_pool_etiquetado.json", ab)
    fs = _load(SRC / "01_facts_sources.json")                 # siempre desde el pool de v2 (re-correr es idempotente)
    pool = fs["evidence_pool"]
    add_block(pool, "testimonios", block, raw_cache=DST / "00d_testimonios_raw.json", log=log,
              other_blocks=[v for k, v in ab["angle_blocks"].items() if k != "testimonios"])
    fs["evidence_pool"] = pool
    fs["_f6a"] = {"testimonios_de": str(tfile.relative_to(ROOT)), "log": log}
    _dump(DST / "01_facts_sources.json", fs)

    sin_nombre = "SIN TESTIMONIOS CON NOMBRE" in block.upper()
    lines = ["# F6a — Testimonios de Orleans (re-research de la sección [TESTIMONIOS])", "",
             f"- Query: 1 Pro + Google Search, {t['segundos']} s, US$ {t['costo_usd']}. Bloque: "
             f"`data/scripts/_steps/{V3}/00c_testimonios.json` ({len(block)} caracteres)."
             + (" El research declara **SIN TESTIMONIOS CON NOMBRE**." if sin_nombre else ""), "",
             "## Citas que son testimonio (alguien que estuvo ahí)", ""]
    for q in pool["citas"]:
        if q.get("testimonio"):
            lines.append(f"- **{q['id']}** «{q['texto']}» — {q['autor']}"
                         f"{' (' + q['rol'] + ')' if q.get('rol') else ''} · fuente: {q.get('fuente') or '—'}")
    lines += ["", "## Citas que no son testimonio", ""]
    lines += [f"- {q['id']} «{q['texto'][:90]}» — {q['autor']}" for q in pool["citas"] if not q.get("testimonio")]
    lines += ["", "## Personajes", "", "| id | nombre | rol | testigo | presente_en | antagonista |", "|---|---|---|---|---|---|"]
    for p in pool["personajes"]:
        lines.append(f"| {p['id']} | {p['nombre']} | {p.get('rol') or ''} | {'sí' if p.get('testigo') else 'no'} | "
                     f"{', '.join(p.get('presente_en') or []) or '—'} | {'sí' if p.get('antagonista') else ''} |")
    lines += ["", "## Log", ""] + [f"- {x.strip()}" for x in log]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
