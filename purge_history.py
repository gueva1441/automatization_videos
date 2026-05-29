"""
purge_history.py — Borra basura histórica del proyecto.

Limpia:
  - data/topics_db.json (excepto topic --keep si se pasa)
  - data/selected_seeds.json
  - data/fase1_review.csv
  - data/scripts/_steps/<id>/  (excepto el de --keep)
  - data/scripts/<id>.json    (excepto el de --keep)
  - data/issues_log/<id>/      (excepto el de --keep)

Uso:
  python purge_history.py                          dry-run, muestra qué borraría
  python purge_history.py --execute                borra todo
  python purge_history.py --execute --keep <id>    borra todo menos el topic <id>

Ejemplo:
  python purge_history.py --execute --keep 9bcb8967-1234-...

NO TOCA: código fuente, ARCHITECTURE.md, ningún .py.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

from config import DATA_DIR


def _list_steps_dirs(keep_id: str | None) -> list[Path]:
    steps_root = DATA_DIR / "scripts" / "_steps"
    if not steps_root.exists():
        return []
    return [d for d in steps_root.iterdir() if d.is_dir() and d.name != keep_id]


def _list_final_scripts(keep_id: str | None) -> list[Path]:
    scripts_root = DATA_DIR / "scripts"
    if not scripts_root.exists():
        return []
    return [
        f for f in scripts_root.glob("*.json")
        if f.is_file() and (keep_id is None or f.stem != keep_id)
    ]


def _list_issues_log_dirs(keep_id: str | None) -> list[Path]:
    issues_root = DATA_DIR / "issues_log"
    if not issues_root.exists():
        return []
    return [d for d in issues_root.iterdir() if d.is_dir() and d.name != keep_id]


def _filter_topics_db(keep_id: str | None) -> tuple[int, int]:
    """Retorna (topics_antes, topics_despues). Solo escribe si execute=True afuera."""
    db_file = DATA_DIR / "topics_db.json"
    if not db_file.exists():
        return (0, 0)
    db = json.loads(db_file.read_text(encoding="utf-8"))
    topics = db.get("topics", [])
    n_before = len(topics)
    if keep_id:
        topics = [t for t in topics if t.get("id") == keep_id or t.get("topic_id") == keep_id]
    else:
        topics = []
    return (n_before, len(topics))


def _execute_purge(keep_id: str | None) -> None:
    # 1. topics_db.json
    db_file = DATA_DIR / "topics_db.json"
    if db_file.exists():
        db = json.loads(db_file.read_text(encoding="utf-8"))
        topics = db.get("topics", [])
        if keep_id:
            topics = [t for t in topics if t.get("id") == keep_id or t.get("topic_id") == keep_id]
        else:
            topics = []
        db["topics"] = topics
        db_file.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  ✅ topics_db.json: {len(topics)} topic(s) preservado(s)")

    # 2. selected_seeds.json
    seeds_file = DATA_DIR / "selected_seeds.json"
    if seeds_file.exists():
        seeds_file.write_text(
            json.dumps({"seeds": []}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  ✅ selected_seeds.json: vaciado")

    # 3. fase1_review.csv
    csv_file = DATA_DIR / "fase1_review.csv"
    if csv_file.exists():
        csv_file.unlink()
        print(f"  ✅ fase1_review.csv: borrado")

    # 4. _steps/ dirs
    for d in _list_steps_dirs(keep_id):
        shutil.rmtree(d)
        print(f"  ✅ _steps/{d.name}/: borrado")

    # 5. final scripts
    for f in _list_final_scripts(keep_id):
        f.unlink()
        print(f"  ✅ scripts/{f.name}: borrado")

    # 6. issues_log/ dirs
    for d in _list_issues_log_dirs(keep_id):
        shutil.rmtree(d)
        print(f"  ✅ issues_log/{d.name}/: borrado")


def _dry_run(keep_id: str | None) -> None:
    n_before, n_after = _filter_topics_db(keep_id)
    print(f"\n  📋 topics_db.json:")
    print(f"     Antes:    {n_before} topic(s)")
    print(f"     Después:  {n_after} topic(s)")

    print(f"\n  📋 selected_seeds.json: se vaciaría")

    csv_file = DATA_DIR / "fase1_review.csv"
    print(f"\n  📋 fase1_review.csv: {'se borraría' if csv_file.exists() else 'no existe'}")

    steps = _list_steps_dirs(keep_id)
    print(f"\n  📋 _steps/ dirs a borrar: {len(steps)}")
    for d in steps[:10]:
        print(f"     - {d.name}")
    if len(steps) > 10:
        print(f"     ... y {len(steps) - 10} más")

    finals = _list_final_scripts(keep_id)
    print(f"\n  📋 scripts/<id>.json a borrar: {len(finals)}")
    for f in finals[:10]:
        print(f"     - {f.name}")

    logs = _list_issues_log_dirs(keep_id)
    print(f"\n  📋 issues_log/ dirs a borrar: {len(logs)}")
    for d in logs[:10]:
        print(f"     - {d.name}")


def main():
    parser = argparse.ArgumentParser(description="Purga basura histórica del proyecto.")
    parser.add_argument("--execute", action="store_true",
                        help="Aplica los cambios. Sin esto, solo muestra qué borraría (dry-run).")
    parser.add_argument("--keep", type=str, default=None,
                        help="topic_id a preservar (todos sus archivos relacionados quedan).")
    args = parser.parse_args()

    print(f"\n{'═' * 60}")
    print(f"  🧹 PURGA DE BASURA HISTÓRICA")
    print(f"{'═' * 60}")

    if args.keep:
        print(f"\n  Preservando topic_id: {args.keep}")
    else:
        print(f"\n  ⚠ Sin --keep: se borra TODO incluyendo el topic recién inyectado.")

    if not args.execute:
        print(f"\n  Modo: DRY-RUN (no se borra nada)")
        _dry_run(args.keep)
        print(f"\n  Para ejecutar: python purge_history.py --execute"
              + (f" --keep {args.keep}" if args.keep else ""))
        sys.exit(0)

    print(f"\n  Modo: EJECUTAR")
    confirm = input(f"\n  ¿Confirmás borrar la basura histórica? [s/N]: ").strip().lower()
    if confirm != "s":
        print(f"\n  Abortado.")
        sys.exit(0)

    print()
    _execute_purge(args.keep)
    print(f"\n  ✅ Purga completa.\n")


if __name__ == "__main__":
    main()
