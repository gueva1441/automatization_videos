"""
dump_topic_evidence.py — Extractor de evidencia completa por tema (READ-ONLY, $0).

Vuelca TODA la evidencia persistida de cada topic en data/topics_db.json a dos
archivos planos en data/:
  - topic_evidence_dump.md   → legible para humano + pegable a Gemini
  - topic_evidence_dump.json → la misma data estructurada

NO modifica topics_db.json. NO llama APIs. Solo lee y escribe los dos dumps.

Uso:
    python tools/dump_topic_evidence.py
"""

import json
from pathlib import Path

# Raíz del proyecto = carpeta padre de tools/
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
TOPICS_DB_FILE = DATA_DIR / "topics_db.json"
OUT_MD = DATA_DIR / "topic_evidence_dump.md"
OUT_JSON = DATA_DIR / "topic_evidence_dump.json"

# Prioridad de veredicto para ordenar (menor = primero).
# Cubre variantes de nombre que pueden aparecer en market_verdict.
VERDICT_PRIORITY = {
    "oro": 0,
    "arbitraje": 1,
    "caliente": 1,
    "hot": 1,
    "frio": 2,
    "frío": 2,
    "cold": 2,
    "desconocido": 3,
    "unknown": 3,
}


def _load_db() -> dict:
    """Carga topics_db.json en modo lectura, tolerante a esquema."""
    db = json.loads(TOPICS_DB_FILE.read_text(encoding="utf-8"))
    if isinstance(db, list):
        return {"topics": db}
    if isinstance(db, dict):
        db.setdefault("topics", [])
        return db
    return {"topics": []}


def _verdict_of(topic: dict) -> str:
    """Devuelve el veredicto crudo del topic (market_verdict, con fallbacks)."""
    return (
        topic.get("market_verdict")
        or topic.get("verdict")
        or topic.get("competition_level")
        or "desconocido"
    )


def _verdict_rank(topic: dict) -> int:
    v = str(_verdict_of(topic)).strip().lower()
    return VERDICT_PRIORITY.get(v, 99)


def _en_views(topic: dict):
    """Vistas EN del viral (o None si no existe el dato)."""
    ev = topic.get("evidence_from_discovery") or {}
    en = ev.get("en_viral") or {}
    return en.get("views")


def _en_ratio(topic: dict):
    """outlier_ratio del viral EN (o None)."""
    ev = topic.get("evidence_from_discovery") or {}
    en = ev.get("en_viral") or {}
    return en.get("outlier_ratio")


def _sort_key(item):
    """Ordena por veredicto; dentro de cada grupo por ratio o views EN desc.
    Si no hay dato numérico, queda al final del grupo conservando orden estable
    (se logra usando el índice original como desempate)."""
    idx, topic = item
    rank = _verdict_rank(topic)
    metric = _en_ratio(topic)
    if metric is None:
        metric = _en_views(topic)
    # metric desc → negativo; None → sin métrica (va después), desempata por idx (orden DB)
    has_metric = 0 if metric is not None else 1
    metric_val = -float(metric) if metric is not None else 0.0
    return (rank, has_metric, metric_val, idx)


def _render_value(value, indent: int) -> list[str]:
    """Renderiza recursivamente un valor (dict/list/escalar) a líneas indentadas."""
    pad = "  " * indent
    lines: list[str] = []
    if isinstance(value, dict):
        if not value:
            lines.append(f"{pad}—")
            return lines
        for k, v in value.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{k}:")
                lines.extend(_render_value(v, indent + 1))
            else:
                lines.append(f"{pad}{k}: {_scalar(v)}")
    elif isinstance(value, list):
        if not value:
            lines.append(f"{pad}—")
            return lines
        for i, v in enumerate(value):
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}- [{i}]")
                lines.extend(_render_value(v, indent + 1))
            else:
                lines.append(f"{pad}- {_scalar(v)}")
    else:
        lines.append(f"{pad}{_scalar(value)}")
    return lines


def _scalar(v) -> str:
    if v is None or v == "":
        return "—"
    if isinstance(v, float):
        # redondeo legible para ratios/saturación
        return f"{v:.2f}".rstrip("0").rstrip(".") if v != int(v) else str(int(v))
    return str(v)


def _g(topic: dict, key: str) -> str:
    """get con default '—' para campos de texto del topic raíz."""
    val = topic.get(key)
    if val is None or val == "":
        return "—"
    return str(val)


def _build_structured(topic: dict) -> dict:
    """Subconjunto estructurado para el .json (no muta el topic)."""
    return {
        "video_title": topic.get("video_title"),
        "id": topic.get("id"),
        "seed_id": topic.get("seed_id"),
        "discovery_mode": topic.get("discovery_mode"),
        "status": topic.get("status"),
        "market_verdict": _verdict_of(topic),
        "competition_level": topic.get("competition_level"),
        "search_keyword": topic.get("search_keyword"),
        "hook": topic.get("hook"),
        "angle": topic.get("angle"),
        "mystery": topic.get("mystery"),
        "reveal": topic.get("reveal"),
        "n_verified_facts": len(topic.get("verified_facts") or []),
        "n_sources": len(topic.get("sources") or []),
        "evidence_from_discovery": topic.get("evidence_from_discovery") or {},
    }


def main() -> None:
    if not TOPICS_DB_FILE.exists():
        print(f"[ERROR] no existe {TOPICS_DB_FILE}")
        return

    db = _load_db()
    topics = db.get("topics") or []

    # Ordenar conservando referencia al índice original (orden DB) como desempate
    ordered = sorted(enumerate(topics), key=_sort_key)

    md_lines: list[str] = []
    md_lines.append("# Volcado de evidencia por tema")
    md_lines.append("")
    md_lines.append(f"Total de temas: {len(topics)}")
    md_lines.append("")

    structured: list[dict] = []
    with_evidence = 0

    for n, (_, topic) in enumerate(ordered, start=1):
        ev = topic.get("evidence_from_discovery")
        has_ev = isinstance(ev, dict) and len(ev) > 0
        if has_ev:
            with_evidence += 1

        n_facts = len(topic.get("verified_facts") or [])
        n_sources = len(topic.get("sources") or [])

        md_lines.append(f"## [{n}] {_g(topic, 'video_title')}")
        md_lines.append(
            f"- id: {_g(topic, 'id')}  ·  seed_id: {_g(topic, 'seed_id')}  ·  "
            f"mode: {_g(topic, 'discovery_mode')}  ·  status: {_g(topic, 'status')}"
        )
        md_lines.append(
            f"- veredicto: {_verdict_of(topic)}  ·  competition_level: "
            f"{_g(topic, 'competition_level')}"
        )
        md_lines.append(f"- search_keyword: {_g(topic, 'search_keyword')}")
        md_lines.append(f"- hook: {_g(topic, 'hook')}")
        md_lines.append(f"- angle: {_g(topic, 'angle')}")
        md_lines.append(f"- mystery: {_g(topic, 'mystery')}")
        md_lines.append(f"- reveal: {_g(topic, 'reveal')}")
        md_lines.append(f"- facts: {n_facts}  ·  sources: {n_sources}")
        md_lines.append("")
        md_lines.append("### evidence_from_discovery")
        if has_ev:
            md_lines.extend(_render_value(ev, indent=0))
        else:
            md_lines.append("—")
        md_lines.append("")

        structured.append(_build_structured(topic))

    # Escribir salidas (solo los dumps, NUNCA topics_db.json)
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    without_evidence = len(topics) - with_evidence
    print(f"[OK] Markdown : {OUT_MD}")
    print(f"[OK] JSON     : {OUT_JSON}")
    print(
        f"[RESUMEN] {len(topics)} temas volcados · "
        f"{with_evidence} con evidence_from_discovery · "
        f"{without_evidence} sin evidence"
    )


if __name__ == "__main__":
    main()
