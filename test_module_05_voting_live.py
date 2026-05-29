"""
test_module_05_voting_live.py — Live test de m05 con voting N=3.

⚠ ESTE SCRIPT CONSUME API CALLS DE GEMINI. Costo estimado: ~$0.015 (3x m05).

Corre judge_topic_with_voting() sobre Wittenoom (topic más limpio del set).
Hace 3 corridas independientes de m05 sobre el mismo 03_visual.json,
deduplica por (chapter_id, image_index, category) y reporta cada issue
único con su cohorte (1/3, 2/3, 3/3).

Política decidida: cohorte ≥1 → emitir TODOS los issues (no se filtra).
La cohorte es metadata informativa para que el usuario decida.

Persiste:
  - data/scripts/_steps/<id>/05_judge_run_1.json
  - data/scripts/_steps/<id>/05_judge_run_2.json
  - data/scripts/_steps/<id>/05_judge_run_3.json
  - data/scripts/_steps/<id>/05_judge_voting.json (merged + cohortes)

Ejecuta:
    python test_module_05_voting_live.py
"""
import json
import sys
import time
from pathlib import Path
import argparse


from script_engine.m05_judge import judge_topic_with_voting


# Topic a auditar — buscamos por substring del título
TOPIC_TITLE_MATCH = "Wittenoom"
N_RUNS = 3


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
    topic_id = topic.get("id") or topic.get("topic_id")
    if not topic_id:
        raise KeyError(
            f"Topic '{topic.get('video_title')}' no tiene ni 'id' ni 'topic_id'"
        )
    return topic_id, topic["video_title"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topic",
        default=TOPIC_TITLE_MATCH,
        help=f"Substring del título del topic (default: {TOPIC_TITLE_MATCH})",
    )
    args = parser.parse_args()

    print(f"\n{'═' * 64}")
    print(f"  m05 LIVE TEST — VOTING N={N_RUNS}")
    print(f"{'═' * 64}")

    # Resolver id por título
    try:
        topic_id, full_title = resolve_topic_id_by_title(args.topic)
    except (KeyError, ValueError) as e:
        print(f"\n  ❌ ERROR resolviendo topic: {e}\n")
        sys.exit(1)

    print(f"\n  Topic:    {full_title}")
    print(f"  topic_id: {topic_id}")
    print(f"\n  ⚠ Esto va a hacer {N_RUNS * 7} llamadas reales a Gemini Flash"
          f" ({N_RUNS} corridas × 7 caps).")
    print(f"  ⚠ Costo estimado: ~${0.005 * N_RUNS:.3f}")
    print(f"  ⚠ Tiempo estimado: ~{N_RUNS * 2.5:.0f} min")
    print(f"\n¿Continuar? [y/N] ", end="", flush=True)
    confirm = input().strip().lower()
    if confirm != "y":
        print("\n  Abortado. Sin gastos.\n")
        sys.exit(0)

    print(f"\n  Arrancando voting audit con N={N_RUNS}...\n")
    t0 = time.time()

    try:
        result = judge_topic_with_voting(topic_id, n=N_RUNS)
    except Exception as e:
        print(f"\n  ❌ ERROR durante audit: {type(e).__name__}: {e}\n")
        raise

    elapsed = time.time() - t0

    # Persistir corridas individuales y el merged
    steps_dir = Path("data") / "scripts" / "_steps" / topic_id
    steps_dir.mkdir(parents=True, exist_ok=True)

    for i, run_issues in enumerate(result.get("individual_runs", []), 1):
        run_path = steps_dir / f"05_judge_run_{i}.json"
        run_data = {
            "run_index": i,
            "topic_id": topic_id,
            "issues": run_issues,
        }
        run_path.write_text(json.dumps(run_data, indent=2, ensure_ascii=False),
                             encoding="utf-8")

    # Merged final
    merged_path = steps_dir / "05_judge_voting.json"
    # Excluir individual_runs de la salida persistida (ya está en archivos
    # separados — evita duplicación)
    merged_for_disk = {k: v for k, v in result.items() if k != "individual_runs"}
    merged_path.write_text(
        json.dumps(merged_for_disk, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Resumen
    stats = result["voting_stats"]
    print(f"\n{'═' * 64}")
    print(f"  RESULTADO")
    print(f"{'═' * 64}")
    print(f"\n  Veredicto global:  {result['global_verdict']}")
    print(f"  Issues únicos:     {stats['total_unique_issues']}")
    print(f"  Tiempo:            {elapsed:.1f}s")
    print()
    print(f"  Distribución por cohorte:")
    for c in range(N_RUNS, 0, -1):
        count = stats.get(f"cohort_{c}_of_{N_RUNS}", 0)
        if c == N_RUNS:
            label = "🎯 alta confianza"
        elif c * 2 > N_RUNS:
            label = "⚠ mayoría"
        else:
            label = "❓ baja confianza"
        print(f"    {c}/{N_RUNS} ({label}): {count} issue(s)")
    print()
    print(f"  Persistido:")
    for i in range(1, N_RUNS + 1):
        print(f"    - data/scripts/_steps/{topic_id}/05_judge_run_{i}.json")
    print(f"    - data/scripts/_steps/{topic_id}/05_judge_voting.json")

    # Reporte completo con cohortes
    print(f"\n{'─' * 64}")
    print(f"  REPORTE GERENCIAL (con cohortes)")
    print(f"{'─' * 64}\n")
    print(result["report_str"])


if __name__ == "__main__":
    main()
