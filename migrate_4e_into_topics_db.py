"""
migrate_4e_into_topics_db.py — Migración única: agregar campos del 4e a
topics ya generados en topics_db.json.

Para topics generados ANTES del refactor del módulo 00 (que agregó el
sub-paso 4e), sus entradas en topics_db.json no tienen los 3 campos
nuevos: era_visual_canon, documented_people, anachronism_blocklist.

Este script lee los archivos `_steps/{topic_id}/05_visual_canon.json`
ya generados (por test_module_00_4e.py o por una corrida del m00 nuevo)
y los fusiona a las entradas correspondientes en topics_db.json.

Es IDEMPOTENTE: correrlo varias veces no rompe nada.

Es DEFENSIVO: hace backup de topics_db.json antes de sobrescribir.

Uso:
  python migrate_4e_into_topics_db.py

NO toca nada más del pipeline. Solo migra el topics_db.json.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
#  PATHS
# ═══════════════════════════════════════════════════════════════

DATA_DIR = Path("data")
TOPICS_DB_FILE = DATA_DIR / "topics_db.json"
STEPS_DIR = DATA_DIR / "scripts" / "_steps"

# Campos que el 4e agrega al topic
NEW_FIELDS = ("era_visual_canon", "documented_people", "anachronism_blocklist")
DEFAULTS = {
    "era_visual_canon": {},
    "documented_people": [],
    "anachronism_blocklist": [],
}


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def _load_topics_db() -> dict:
    """Carga topics_db.json. Lanza si no existe."""
    if not TOPICS_DB_FILE.exists():
        raise FileNotFoundError(
            f"No existe {TOPICS_DB_FILE}. ¿Estás en la raíz del proyecto?"
        )
    return json.loads(TOPICS_DB_FILE.read_text(encoding="utf-8"))


def _save_topics_db(db: dict) -> None:
    """Sobrescribe topics_db.json con el dict modificado."""
    TOPICS_DB_FILE.write_text(
        json.dumps(db, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _backup_topics_db() -> Path:
    """Hace backup timestampeado de topics_db.json antes de modificar."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = TOPICS_DB_FILE.parent / f"topics_db.backup_{timestamp}.json"
    shutil.copy2(TOPICS_DB_FILE, backup_path)
    return backup_path


def _load_canon_for_topic(topic_id: str) -> dict | None:
    """
    Carga el 05_visual_canon.json del topic. Devuelve None si no existe.
    """
    canon_path = STEPS_DIR / topic_id / "05_visual_canon.json"
    if not canon_path.exists():
        return None
    try:
        return json.loads(canon_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"    ⚠ Error leyendo {canon_path}: {e}")
        return None


def _topic_already_has_canon(topic: dict) -> bool:
    """
    Indica si el topic ya tiene los 3 campos del 4e POPULADOS.
    Considera populado si era_visual_canon tiene primary_decade no vacío.
    """
    era = topic.get("era_visual_canon", {})
    if not isinstance(era, dict):
        return False
    return bool(era.get("primary_decade", "").strip())


# ═══════════════════════════════════════════════════════════════
#  MIGRACIÓN
# ═══════════════════════════════════════════════════════════════

def _migrate_topic(topic: dict) -> str:
    """
    Migra UN topic. Mutación in-place. Devuelve un código de status:
      'merged'      → tenía 05_visual_canon en disco, se fusionó
      'overwritten' → ya tenía canon populado pero se sobrescribió con disco
      'defaulted'   → sin archivo en disco, se setearon defaults vacíos
      'skipped'     → ya tenía canon populado y no había archivo en disco
    """
    topic_id = topic.get("id", "?")
    canon = _load_canon_for_topic(topic_id)
    already_populated = _topic_already_has_canon(topic)

    if canon is None:
        # Sin archivo en disco
        if already_populated:
            # Ya tiene canon (probablemente de una corrida previa del m00 con 4e
            # integrado). No tocar nada.
            return "skipped"
        else:
            # Topic viejo sin migrar y sin archivo. Setear defaults para no
            # romper m03/m05 que harán topic.get("era_visual_canon", {}).
            for field in NEW_FIELDS:
                topic.setdefault(field, DEFAULTS[field])
            return "defaulted"

    # Hay archivo en disco → fusionar
    for field in NEW_FIELDS:
        topic[field] = canon.get(field, DEFAULTS[field])

    if already_populated:
        return "overwritten"
    return "merged"


def main():
    print("\n" + "═" * 60)
    print("  🔧 MIGRACIÓN — fusión 4e (visual_canon) → topics_db.json")
    print("═" * 60)

    # ─── 1. Cargar topics_db.json ───
    try:
        db = _load_topics_db()
    except FileNotFoundError as e:
        print(f"\n  ❌ {e}")
        return

    topics = db.get("topics", [])
    if not topics:
        print(f"\n  ⚠ topics_db.json no tiene topics. Nada que migrar.")
        return

    # ─── 2. Pre-scan para mostrar plan ───
    print(f"\n  Topics en topics_db.json: {len(topics)}")
    print(f"  Plan por topic:")

    plan: dict[str, list[str]] = {
        "merged": [],
        "overwritten": [],
        "defaulted": [],
        "skipped": [],
    }
    for t in topics:
        topic_id = t.get("id", "?")
        canon = _load_canon_for_topic(topic_id)
        already = _topic_already_has_canon(t)
        if canon is not None:
            status = "overwritten" if already else "merged"
        else:
            status = "skipped" if already else "defaulted"
        plan[status].append(t.get("title", topic_id)[:60])

    if plan["merged"]:
        print(f"\n    [merged] ({len(plan['merged'])}) — tienen 05_visual_canon en disco, se fusionarán:")
        for title in plan["merged"]:
            print(f"      • {title}")
    if plan["overwritten"]:
        print(f"\n    [overwritten] ({len(plan['overwritten'])}) — ya tenían canon, se sobrescriben con disco:")
        for title in plan["overwritten"]:
            print(f"      • {title}")
    if plan["defaulted"]:
        print(f"\n    [defaulted] ({len(plan['defaulted'])}) — sin archivo en disco, se setean defaults vacíos:")
        for title in plan["defaulted"]:
            print(f"      • {title}")
    if plan["skipped"]:
        print(f"\n    [skipped] ({len(plan['skipped'])}) — ya tenían canon y no hay archivo en disco:")
        for title in plan["skipped"]:
            print(f"      • {title}")

    # ─── 3. Confirmación ───
    will_modify = len(plan["merged"]) + len(plan["overwritten"]) + len(plan["defaulted"])
    if will_modify == 0:
        print(f"\n  ✓ Nada que modificar. topics_db.json ya está al día.")
        return

    print(f"\n  Topics que se modificarán: {will_modify}/{len(topics)}")
    confirm = input("  ¿Aplicar migración? [S/n]: ").strip().lower()
    if confirm in ("n", "no"):
        print("  Abortado. topics_db.json no se modificó.")
        return

    # ─── 4. Backup ───
    backup_path = _backup_topics_db()
    print(f"\n  ✓ Backup creado: {backup_path}")

    # ─── 5. Aplicar migración ───
    counts = {"merged": 0, "overwritten": 0, "defaulted": 0, "skipped": 0}
    for t in topics:
        status = _migrate_topic(t)
        counts[status] += 1

    # ─── 6. Persistir ───
    _save_topics_db(db)

    # ─── 7. Reporte ───
    print(f"\n  ─── Resultado ───")
    print(f"    merged       (fusionados de disco):  {counts['merged']}")
    print(f"    overwritten  (sobrescritos):         {counts['overwritten']}")
    print(f"    defaulted    (vacíos por defecto):   {counts['defaulted']}")
    print(f"    skipped      (sin tocar):            {counts['skipped']}")
    print(f"    TOTAL                                {sum(counts.values())}")

    print(f"\n  ✅ Migración completada. topics_db.json actualizado.")
    print(f"     Si algo se rompió, restaurar desde:")
    print(f"     {backup_path}")
    print("\n" + "═" * 60 + "\n")


if __name__ == "__main__":
    main()
