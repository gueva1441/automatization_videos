"""F41 §A.3: qué haría HOY `python fase1_5.py --topic <id> --batch` con la cadena única, para cada topic de
data/topics_db.json. SOLO LECTURA: lee topics_db, `_steps/<id>/` (ficha, escaleta, papel), seeds_archive y
`fase1_5.estado_papel`; la compuerta del pool se evalúa en memoria (`pool_gate.evaluate`, sin escribir POOL_GATE.md).
No llama a ninguna API, no escribe nada.

    PYTHONIOENCODING=utf-8 python lab/hyperframes/f41/a/tabla_topics.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import fase1_5 as f15  # noqa: E402
from researcher_steps import pool_gate as pg  # noqa: E402
from researcher_steps.ficha_caso import load as load_ficha  # noqa: E402
from script_engine import m01a_escaleta as me  # noqa: E402


def que_haria(t: dict) -> tuple[str, str]:
    """(qué haría `--topic <id> --batch` desde m01a, notas)."""
    tid = t["id"]
    ok, motivo_papel = f15.estado_papel(tid)
    corto = motivo_papel if ok else ("no hay papel" if motivo_papel.startswith("no hay papel") else motivo_papel)
    notas = [f"papel hoy: {'APROBADO' if ok else 'no'} ({corto})"]
    if (f15.DATA_DIR / "scripts" / f"{tid}.json").exists():
        notas.append(f"data/scripts/{tid}.json existe")
    if not f15.pool_v3(t):
        return f"PARADA antes de gastar: {f15.motivo_sin_pool(tid, t).split(': ', 1)[1].split(';')[0]}", " · ".join(notas)
    pasos = []
    if t.get("escaleta_frozen") or me._frozen_is_escaleta(t):
        pasos.append("escaleta congelada (sin compuerta ni ficha)")
    else:
        gate = pg.evaluate(t["evidence_pool"])
        if gate["color"] == pg.RED:
            return f"PARADA en m01a: compuerta del pool ROJA ({'; '.join(gate.get('motivos') or [])})", " · ".join(notas)
        pasos.append(f"compuerta {gate['color']}")
        ficha = load_ficha(tid, f15.STEPS_DIR)
        if ficha and "historia" in ficha:
            pasos.append(f"ficha v2 existente ({ficha.get('prompt_version')}, no se paga)")
        elif f15._titulo_de_semilla(t):
            pasos.append("ficha NUEVA (se paga)")
        else:
            return ("PARADA en m01a: sin ficha v2 y sin seed_title (no se inventa)", " · ".join(notas))
    pasos += ["escaleta (se paga)", "guion v4 → partición → papel (se paga)",
              "PARADA del papel (el papel nuevo queda sin aprobar)"]
    if ok:
        notas.append("OJO: desde m01a se rehace y se paga el papel aprobado; retomar sin pagar = "
                     "`--from normalizer_gate --batch`")
    return "cadena única desde m01a: " + " → ".join(pasos), " · ".join(notas)


def main() -> None:
    db = json.loads((f15.TOPICS_DB).read_text(encoding="utf-8"))
    topics = db.get("topics", []) if isinstance(db, dict) else db
    print("| topic | video_type | guion_version | pool v3 | qué haría `fase1_5 --topic <id> --batch` | notas |")
    print("|---|---|---|---|---|---|")
    for t in topics:
        accion, notas = que_haria(t)
        print(f"| {t['id']} | {t.get('video_type')} | {t.get('guion_version')} | {'sí' if f15.pool_v3(t) else 'no'} "
              f"| {accion} | {notas} |")


if __name__ == "__main__":
    main()
