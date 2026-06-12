"""
Gestión centralizada de topics_db.json.

Responsabilidades:
- Cargar/guardar la DB de temas
- Marcar temas como video_generated (los excluye de próximas corridas de CSV)
- Consultas comunes (temas pendientes, generados, por id)

Uso típico en Fase 2 tras generar un video:
    from modules.topics_db import mark_as_generated
    mark_as_generated(topic_id, video_id, video_path="output/nazca_final.mp4")
"""

import json
from datetime import datetime
from pathlib import Path

from config import DATA_DIR

DB_FILE: Path = DATA_DIR / "topics_db.json"


# ─── I/O base ──────────────────────────────────────────────────────────

def load_db() -> dict:
    """Carga topics_db.json. Devuelve estructura vacía si no existe."""
    if not DB_FILE.exists():
        return {"created_at": datetime.now().isoformat(), "topics": []}
    return json.loads(DB_FILE.read_text(encoding="utf-8"))


def save_db(db: dict) -> None:
    """Guarda la DB en disco con formato legible."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    DB_FILE.write_text(
        json.dumps(db, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ─── Consultas ─────────────────────────────────────────────────────────

def get_topic_by_id(topic_id: str) -> dict | None:
    """Devuelve el topic con ese id o None."""
    db = load_db()
    for t in db.get("topics", []):
        if t.get("id") == topic_id:
            return t
    return None


def get_pending_for_video(only_green: bool = False) -> list[dict]:
    """Temas validados que aún no tienen video generado.
    
    Args:
        only_green: si True, solo devuelve competition_level == 'green'.
    """
    valid_levels = ["green"] if only_green else ["green", "yellow"]
    db = load_db()
    return [
        t for t in db.get("topics", [])
        if t.get("status") == "validated"
        and t.get("competition_level") in valid_levels
    ]


def get_generated_topics() -> list[dict]:
    """Temas que ya tienen video generado."""
    db = load_db()
    return [
        t for t in db.get("topics", [])
        if t.get("status") == "video_generated"
    ]


# ─── Mutación ──────────────────────────────────────────────────────────

def mark_as_generated(
    topic_id: str,
    video_id: str,
    video_path: str | None = None,
) -> bool:
    """Marca un topic como video_generated para excluirlo del CSV futuro.
    
    Args:
        topic_id: id del topic (ej. 'topic_9de169eb').
        video_id: id del video generado (ej. 'nazca_20260419_1030').
        video_path: ruta absoluta al video final (opcional).
    
    Returns:
        True si se actualizó, False si no se encontró el topic.
    """
    db = load_db()
    for t in db.get("topics", []):
        if t.get("id") == topic_id:
            t["status"] = "video_generated"
            t["video_id"] = video_id
            t["video_generated_at"] = datetime.now().isoformat()
            if video_path:
                t["video_path"] = video_path
            save_db(db)
            return True
    return False


def mark_as_packaged(topic_id: str) -> bool:
    """Marca un topic ya generado como PACKAGED (paquete de publicación armado en fase3).

    Es un FLAG aparte ('packaged'), NO cambia status='video_generated' — así no rompe los
    filtros existentes (get_generated_topics / revert_generation). Idempotente: el timestamp
    'packaged_at' se sella la PRIMERA vez (primer COMPONER) y no se pisa después.

    Returns:
        True si se marcó, False si no se encontró el topic.
    """
    db = load_db()
    for t in db.get("topics", []):
        if t.get("id") == topic_id:
            t["packaged"] = True
            t.setdefault("packaged_at", datetime.now().isoformat())
            save_db(db)
            return True
    return False


def get_unpackaged_generated() -> list[dict]:
    """Temas con video DONE que todavía NO se empaquetaron (menú de fase3)."""
    return [t for t in get_generated_topics() if not t.get("packaged")]


def revert_generation(topic_id: str) -> bool:
    """Revierte un topic de vuelta a 'validated' (útil si el video falló).

    Returns:
        True si se revirtió, False si no aplica.
    """
    db = load_db()
    for t in db.get("topics", []):
        if t.get("id") == topic_id and t.get("status") == "video_generated":
            t["status"] = "validated"
            t["video_id"] = None
            t.pop("video_generated_at", None)
            t.pop("video_path", None)
            save_db(db)
            return True
    return False
