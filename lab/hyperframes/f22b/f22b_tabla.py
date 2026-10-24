"""F22b — tablas del reporte con lo que quedó en disco (sin API): las cinco narraciones de F22b más la de F22 (Sol v5.2,
misma escaleta) y la de F16 (Sol v5.1, escaleta F16) como referencia. Escribe `tabla_f22b.md` y `resumen_f22b.json`.
Uso: python -I lab/hyperframes/f22b/f22b_tabla.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
F22 = LAB.parent / "f22"
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(F22))
sys.path.insert(2, str(LAB))
STEPS = ROOT / "data" / "scripts" / "_steps" / "f8s1-ycua-bolanos"


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import f22_compara as fc2
    from f22b_corridas import CORRIDAS, VERSION_NOMBRE
    pool, ficha = _j(STEPS / "00_pool_v3.json"), _j(STEPS / "ficha_caso.json")
    esc22 = _j(F22 / "escaleta_ycua_f22.json")
    filas = [(t, f"{m} · {VERSION_NOMBRE[v]}", _j(LAB / f"guion_ycua_f22b_{t}.json"), esc22) for t, (m, v) in CORRIDAS.items()]
    filas.append(("F22 (ref.)", "gpt-6.1-sol · v5.2", _j(F22 / "guion_ycua_f22.json"), esc22))
    filas.append(("F16 (ref.)", "gpt-6.1-sol · v5.1 · escaleta F16", _j(LAB.parent / "f16" / "guion_ycua_f16.json"),
                  _j(STEPS / "01a_escaleta_f16.json")))
    costos = {x["corrida"]: x for x in (_j(LAB / "costos_f22b.json") or {}).get("etapas") or []}
    L = ["| corrida | modelo · guion | palabras | min | bloqueantes | citas | personas con nombre | cierre | US$ |",
         "|---|---|---|---|---|---|---|---|---|"]
    por_cap = ["| cap | " + " | ".join(t for t, *_ in filas) + " |", "|---|" + "---|" * len(filas)]
    res = {}
    vistas = {}
    for tag, nom, g, esc in filas:
        if not g or not g.get("parrafos"):
            L.append(f"| {tag} | {nom} | — | — | — | — | — | — | {(costos.get(tag) or {}).get('usd', '—')} |"
                     + (f" error: {g.get('error')}" if g and g.get("error") else ""))
            continue
        # F16 se re-mide con su versión (v5.1); las demás, con la suya
        version = (g.get("version") or g.get("prompt_version") or "f22-1")
        v = fc2.guion_view("ycua", g, esc, ficha, pool)
        from script_engine import guion_v4 as g4
        bl = g4.bloqueantes({"id": "f8s1-ycua-bolanos", "evidence_pool": pool}, esc, g["parrafos"], ficha=ficha,
                            version=version if version in g4.VERSIONES_V5 else "f22-1")
        m = g.get("metricas") or {}
        vistas[tag] = v
        usd = (costos.get(tag) or {}).get("usd")
        L.append(f"| {tag} | {nom} | {v['palabras']} | {g.get('minutos')} | {len(bl)} | {m.get('citas')} | "
                 f"{len(v['personas_total'])} | {m.get('cierre')} | {usd if usd is not None else '—'} |")
        res[tag] = {"modelo": nom, "palabras": v["palabras"], "minutos": g.get("minutos"), "bloqueantes": len(bl),
                    "bloqueantes_lista": [b["motivo"] for b in bl], "citas": m.get("citas"),
                    "personas": v["personas_total"], "cierre": m.get("cierre"), "usd": usd,
                    "por_cap": {n: {k: c[k] for k in ("palabras", "personas", "citas", "bloqueantes")}
                                for n, c in v["por_cap"].items()}}
    for n in range(1, 8):
        celdas = []
        for tag, *_ in filas:
            c = (vistas.get(tag) or {}).get("por_cap", {}).get(n)
            celdas.append(f"{c['palabras']} · {len(c['personas'])}p · {c['citas']}c · {c['bloqueantes']}b" if c else "—")
        por_cap.append(f"| {n} | " + " | ".join(celdas) + " |")
    personas = ["| corrida | personas con nombre por cap |", "|---|---|"]
    for tag, v in vistas.items():
        personas.append(f"| {tag} | " + " · ".join(f"{n}: {', '.join(c['personas']) or '—'}"
                                                   for n, c in sorted(v["por_cap"].items())) + " |")
    total = (_j(LAB / "costos_f22b.json") or {}).get("usd_total")
    md = "\n".join(["### Resumen", ""] + L + ["", "### Por cap (palabras · personas con nombre · citas · bloqueantes)", ""]
                   + por_cap + ["", "### Personas con nombre por cap", ""] + personas
                   + ["", f"Tanda F22b: US$ {total} de 4.00 (incluye la llamada de prueba de la llave)."]) + "\n"
    (LAB / "tabla_f22b.md").write_text(md, encoding="utf-8")
    (LAB / "resumen_f22b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
