"""
test_module_05_live.py — Primer test de m05 con Flash REAL.

⚠ ESTE SCRIPT CONSUME API CALLS DE GEMINI. Costo estimado: ~$0.005.

Corre judge_topic() sobre Wittenoom (topic más limpio del set).
Esperado: global_verdict = "PASS" (sin issues).

Resuelve el id por substring del título — robusto ante regeneraciones de UUID.

Ejecuta:
    python test_module_05_live.py
"""
import json
import sys
import time
from pathlib import Path

from script_engine.m05_judge import judge_topic


# Topic a auditar — buscamos por substring del título
TOPIC_TITLE_MATCH = "Wittenoom"


def resolve_topic_id_by_title(title_substring: str) -> tuple:
    """Lee topics_db.json y devuelve (id, full_title) del primer match."""
    db_path = Path("data") / "topics_db.json"
    raw = json.loads(db_path.read_text(encoding="utf-8"))
    topics = raw["topics"] if isinstance(raw, dict) and "topics" in raw else raw

    matches = [
        t for t in topics
        if title_substring.lower() in (t.get("video_title") or "").lower()
    ]
    if not matches:
        all_titles = [t.get("video_title") for t in topics]
        raise KeyError(
            f"No hay topic con '{title_substring}' en el título. "
            f"Disponibles: {all_titles}"
        )
    if len(matches) > 1:
        all_matches = [t.get("video_title") for t in matches]
        raise ValueError(
            f"Múltiples matches para '{title_substring}': {all_matches}"
        )
    topic = matches[0]
    # m03 ya acepta id o topic_id — replicamos la convención
    topic_id = topic.get("id") or topic.get("topic_id")
    if not topic_id:
        raise KeyError(
            f"Topic '{topic.get('video_title')}' no tiene ni 'id' ni 'topic_id'"
        )
    return topic_id, topic["video_title"]


def main():
    print(f"\n{'═' * 64}")
    print(f"  m05 LIVE TEST")
    print(f"{'═' * 64}")

    # Resolver id por título
    try:
        topic_id, full_title = resolve_topic_id_by_title(TOPIC_TITLE_MATCH)
    except (KeyError, ValueError) as e:
        print(f"\n  ❌ ERROR resolviendo topic: {e}\n")
        sys.exit(1)

    print(f"\n  Topic:    {full_title}")
    print(f"  topic_id: {topic_id}")
    print(f"\n  ⚠ Esto va a hacer 7 llamadas reales a Gemini Flash.")
    print(f"  ⚠ Costo estimado: ~$0.005")
    print(f"  ⚠ Tiempo estimado: ~1 min")
    print(f"\n¿Continuar? [y/N] ", end="", flush=True)
    confirm = input().strip().lower()
    if confirm != "y":
        print("\n  Abortado. Sin gastos.\n")
        sys.exit(0)

    print(f"\n  Arrancando audit...\n")
    t0 = time.time()

    try:
        result = judge_topic(topic_id)  # interactive=False
    except Exception as e:
        print(f"\n  ❌ ERROR durante audit: {type(e).__name__}: {e}\n")
        raise

    elapsed = time.time() - t0

    # Resultado
    print(f"\n{'═' * 64}")
    print(f"  RESULTADO")
    print(f"{'═' * 64}")
    print(f"\n  Veredicto global: {result['global_verdict']}")
    print(f"  Caps procesados:  {len(result['chapters'])}")
    print(f"  Issues totales:   {len(result['all_issues'])}")
    print(f"  Tiempo:           {elapsed:.1f}s")
    print(f"\n  Output persistido en data/scripts/_steps/{topic_id}/05_judge.json")

    # Reporte completo
    print(f"\n{'─' * 64}")
    print(f"  REPORTE GERENCIAL")
    print(f"{'─' * 64}\n")
    print(result["report_str"])


if __name__ == "__main__":
    main()
