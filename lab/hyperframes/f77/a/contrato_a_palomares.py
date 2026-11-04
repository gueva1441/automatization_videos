"""F77 Contrato A — corrida real: «Palomares 1966» por la cadena nueva del gate ES.
Mismo camino que el modo C (F74): semilla manual con remeasure={es_query: título, entity: título,
already_es: True} → fase1.measure_pick_es (lo que llama _verify_pick_es_saturation, sin preguntas),
n=3 como el gate. Gasto: API de YouTube (cuota, US$ 0) + Gemini (aliases + juez, 3×).
No escribe nada fuera de su salida (la guarda quien lo corre con tee). La llave no se imprime.

Correr (desde la raíz):  PYTHONIOENCODING=utf-8 python lab/hyperframes/f77/a/contrato_a_palomares.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

import fase1  # noqa: E402
import niche_discoverer as nd  # noqa: E402

TITULO = "Palomares 1966"
SHORTS = {"IUpaoH-lvkI", "Yvo7kps24Fo"}


def _dur(s):
    return "?" if s is None else f"{s // 60}:{s % 60:02d}"


def main():
    seed = nd._build_seed(TITULO, "manual", None, {},
                          remeasure={"es_query": TITULO, "entity": TITULO, "already_es": True})
    m = fase1.measure_pick_es(seed, n=3)
    print(f"\n=== Contrato A · «{TITULO}» · status={m['status']} ===")
    for k, x in enumerate(m["measurements"], 1):
        print(f"  corrida {k}: {x}")
    w = m["worst"] or {}
    print(f"\nfuente={w.get('source')} · query buscada='{w.get('search_query_es')}' · "
          f"crudos ES > 180 s={w.get('n_cands_es')} · Shorts fuera={w.get('n_short_es')} · "
          f"api_error={w.get('api_error')}")
    cands = sorted(w.get("candidates") or [], key=lambda c: (c["views"] or 0) * c["peso"], reverse=True)
    print("\n| # | id | título | dur | views | meses | peso | eff | relevante |")
    print("|---|---|---|---|---|---|---|---|---|")
    for i, c in enumerate(cands, 1):
        eff = (c["views"] or 0) * c["peso"]
        print(f"| {i} | {c['video_id']} | {(c['title'] or '')[:70]} | {_dur(c['duration_s'])} | "
              f"{c['views']:,} | {c['months']} | {c['peso']} | {eff:,.0f} | "
              f"{'sí' if c['relevante'] else 'no'} |")
    hv = m["heaviest"] or {}
    print(f"\nLABEL (peor de {len([x for x in m['measurements'] if 'error' not in x])}): {m['label']} "
          f"(sat={m['saturation'] or 0:,.0f})")
    print(f"competidor más pesado: {hv.get('video_id')} «{hv.get('title')}» {hv.get('views') or 0:,} v · "
          f"{hv.get('months')} meses · peso {hv.get('decay')} · {_dur(hv.get('duration_s'))}")
    print(f"unidades de cuota gastadas (3 medidas): {m['quota_units']}")
    ids = {c["video_id"] for c in w.get("candidates") or []}
    print(f"Shorts {sorted(SHORTS)} en la tabla: {sorted(SHORTS & ids) or 'ninguno'}")


if __name__ == "__main__":
    main()
