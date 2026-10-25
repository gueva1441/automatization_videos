"""F22d — métricas del reporte (sin API): escaleta de Kyshtym sin columna (F22d) contra la de F22 (con columna), y su
guion Opus 5.5 v5.2 contra el de F22 (Sol v5.2, escaleta con columna). Escribe `tabla_f22d.md`.
Uso: python -I lab/hyperframes/f22d/f22d_tabla.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
F22 = LAB.parent / "f22"
sys.path[:0] = [str(ROOT), str(F22), str(LAB.parent / "f22c")]
STEPS = ROOT / "data" / "scripts" / "_steps" / "f18-kyshtym-mayak"


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import f22_compara as fc2
    from f22c_tabla import esc_view
    from script_engine import guion_v4 as g4
    pool, ficha = _j(STEPS / "00_pool_v3.json"), _j(STEPS / "ficha_caso.json")
    filas = [("F22d (sin columna, guion Opus)", _j(LAB / "escaleta_kyshtym_f22d.json"), _j(LAB / "guion_kyshtym_f22d.json")),
             ("F22d (sin columna, guion Fable)", _j(LAB / "escaleta_kyshtym_f22d.json"),
              _j(LAB / "guion_kyshtym_f22d_fable.json")),
             ("F22 (con columna, guion Sol; ref.)", _j(F22 / "escaleta_kyshtym_f22.json"), _j(F22 / "guion_kyshtym_f22.json"))]
    filas = [f for f in filas if f[2] and f[2].get("parrafos")]
    L = ["| escaleta | beats | beats por cap | ids totales | a_pantalla | apoyos/beat | palabras de imagen (total · por beat) "
         "| intentos (bloqueantes) | humano | antagonista |", "|---|---|---|---|---|---|---|---|---|---|"]
    T = ["| escaleta | promesa_gancho | cierre_humano |", "|---|---|---|"]
    G = ["| guion | modelo | palabras | min | bloqueantes | citas | personas con nombre | cierre |",
         "|---|---|---|---|---|---|---|---|"]
    P = ["| cap | " + " | ".join(n for n, *_ in filas) + " |", "|---|" + "---|" * len(filas)]
    vistas = []
    for nom, esc, g in filas:
        v = esc_view(esc)
        a = v["antagonista"] or {}
        L.append(f"| {nom} | {v['beats']} | {v['beats_por_cap']} | {v['ids_totales']} | {v['a_pantalla']} | "
                 f"{v['apoyos_promedio']} | {v['palabras_imagen']} · {v['palabras_imagen_promedio']} | {v['intentos']} | "
                 f"{v['humano']} | {a.get('tipo')} {a.get('nombre') or ''} |")
        T.append(f"| {nom} | «{v['promesa_gancho']}» | «{v['cierre_humano']}» |")
        gv = fc2.guion_view("kyshtym", g, esc, ficha, pool)
        bl = g4.bloqueantes({"id": "f18-kyshtym-mayak", "evidence_pool": pool}, esc, g["parrafos"], ficha=ficha,
                            version=g.get("version") or g.get("prompt_version") or "f22-1")
        m = g.get("metricas") or {}
        G.append(f"| {nom} | {g.get('modelo')} | {gv['palabras']} | {g.get('minutos')} | {len(bl)}"
                 + (f" ({'; '.join(b['motivo'] for b in bl)})" if bl else "")
                 + f" | {m.get('citas')} | {len(gv['personas_total'])} | {m.get('cierre')} |")
        vistas.append(gv)
    for n in range(1, 8):
        P.append(f"| {n} | " + " | ".join(
            f"{v['por_cap'][n]['palabras']} pal · {v['por_cap'][n]['citas']} citas · {v['por_cap'][n]['bloqueantes']} bl · "
            f"{', '.join(v['por_cap'][n]['personas']) or '—'}" for v in vistas) + " |")
    c = _j(LAB / "costos_f22d.json") or {}
    md = "\n".join(["#### Escaleta", ""] + L + ["", "#### Promesa del gancho y cierre humano (textuales)", ""] + T
                   + ["", "#### Guion", ""] + G + ["", "#### Por cap (palabras · citas · bloqueantes · personas con nombre)",
                                                   ""] + P
                   + ["", "Costo F22d: " + " · ".join(f"{x['paso']} US$ {x['usd']}" for x in c.get("etapas") or [])
                      + f" · total US$ {c.get('usd_total')} de 3.00 (1.50 en la primera corrida)."]) + "\n"
    (LAB / "tabla_f22d.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
