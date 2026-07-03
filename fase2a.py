"""
fase2a.py — Orquestador Fase 2A: Generación de Assets.

Lee los scripts que dejó Fase 1 en data/scripts/<topic_id>.json,
los NORMALIZA al formato que esperan los managers, y corre en orden:

    1. audio_manager.process_script()  → output/<id>/audio/sync_map.json
    2. asset_manager.process_script()  → output/<id>/assets/assets_manifest.json

NO ensambla el video final — eso queda para fase2b.py.

USO:
    python fase2a.py                         # procesa todos los scripts
    python fase2a.py --topic top_a1b2c3      # procesa solo ese topic
    python fase2a.py --variation 2           # para shorts: fuerza variación 1-3
    python fase2a.py --dry-run               # muestra qué haría sin gastar créditos

POLÍTICA ANTE FALLO:
    Continúa con el siguiente topic y loguea el error.
    Los managers internos ya reintentan 503/429 vía error_handler.retry.
    Si un topic llega a fase2a y falla → es bug o rechazo de contenido;
    conviene seguir con los otros y revisar logs después.

NOTA SOBRE IMPORTS:
    Este archivo mezcla imports `from modules.xxx` (legacy) con imports
    planos (módulos nuevos: art_config, asset_manager, audio_manager).
    Si en tu proyecto los archivos nuevos viven dentro de modules/,
    cambiá los imports de raíz a `from modules.xxx`.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from config import DATA_DIR, OUTPUT_DIR
from cost_tracker import cost_tracker
from error_handler import error_handler, PipelineStage
from script_engine.topics_db import load_db, save_db

# Módulos nuevos (si los tenés dentro de modules/, cambiá los imports)
from audio_manager import process_script as audio_process
from asset_manager import process_script as asset_process
from foto_madre import generate_foto_madre_for_topic


SCRIPTS_DIR: Path = DATA_DIR / "scripts"
APPROVED_CSV: Path = DATA_DIR / "fase1_review.csv"


# ═══════════════════════════════════════════════════════════════
#  LISTA BLANCA desde CSV (Modelo B)
# ═══════════════════════════════════════════════════════════════
#
# Fase 2A solo procesa los topic_id que aparezcan en fase1_review.csv.
# El usuario borra las filas de los temas que NO quiere correr.
# Si el CSV no existe, se aborta con instrucciones claras.

def _read_approved_topic_ids_from_csv() -> set[str]:
    """Lee fase1_review.csv y devuelve el set de topic_ids presentes."""
    if not APPROVED_CSV.exists():
        raise FileNotFoundError(
            f"No existe el CSV de aprobación: {APPROVED_CSV}. "
            f"Corré fase1.py primero para generarlo."
        )
    approved: set[str] = set()
    with APPROVED_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "topic_id" not in (reader.fieldnames or []):
            raise ValueError(
                f"El CSV {APPROVED_CSV.name} no tiene columna 'topic_id'. "
                f"Columnas encontradas: {reader.fieldnames}"
            )
        for row in reader:
            tid = (row.get("topic_id") or "").strip()
            if tid:
                approved.add(tid)
    return approved


# ═══════════════════════════════════════════════════════════════
#  NORMALIZADOR Script v2 → Formato Managers
# ═══════════════════════════════════════════════════════════════
#
# El script_generator emite un formato rico (chapter_number, narration,
# image_prompt singular en shorts, etc). Los managers esperan un
# formato más genérico (id, text, image_prompts plural). Esta capa traduce.

def _chapter_id(n: int) -> str:
    """Convierte 1 → 'ch01', 12 → 'ch12'."""
    return f"ch{n:02d}"


def _as_list(value: Any) -> list:
    """Acepta str, list, o None. Devuelve lista (vacía si None)."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_long(script: dict) -> dict:
    """Normaliza un script LONG v2 al formato de los managers."""
    video_id = script["topic_id"]
    normalized_chapters = []

    for ch in script.get("chapters", []):
        n = ch["chapter_number"]
        norm_ch: dict[str, Any] = {
            "id": _chapter_id(n),
            "text": ch.get("narration", ""),
            "render_engine": ch.get("render_engine", "leonardo"),
            "art_profile": ch.get("art_profile"),
            "image_prompts": _as_list(
                ch.get("image_prompts") or ch.get("image_prompt")
            ),
        }
        # video_prompts solo cuando render_engine="veo"
        if norm_ch["render_engine"] == "veo":
            norm_ch["video_prompts"] = _as_list(
                ch.get("video_prompts") or ch.get("video_prompt")
            )
            # Híbrido Veo+Flux chat 29 #175: preservar supplementals (lista
            # de dicts con prompt + narration_anchor) y veo_position
            # ("start"|"end") inferido por m03 a partir del role del cap.
            # NO contamina image_prompts (que sigue siendo [Veo image_prompt]).
            norm_ch["supplemental_image_prompts"] = (
                ch.get("supplemental_image_prompts") or []
            )
            norm_ch["veo_position"] = ch.get("veo_position", "start")
        normalized_chapters.append(norm_ch)

    return {
        "video_id": video_id,
        "topic_id": video_id,
        "video_type": "long",
        "prompt_protocol_version": "v2",
        "chapters": normalized_chapters,
        # HANDOFF_129: pasar el registry del contrato al manager (sin esto el whitelist
        # de normalize lo tiraría — mismo seam que central_subject en el 128).
        "foto_madre_registry": script.get("foto_madre_registry", {}),
        "humanizer_phrases": script.get("humanizer_phrases", []),
    }


def _normalize_short(script: dict, variation_override: int | None = None) -> dict:
    """
    Normaliza un script SHORT v2. Elige UNA variación y convierte
    cada escena en un "capítulo" para los managers.

    Prioridad para elegir variación: variation_override > best > 1
    """
    video_id = script["topic_id"]
    variations = script.get("variations", [])
    if not variations:
        raise ValueError(f"Script SHORT sin variations: {video_id}")

    chosen_num = variation_override or script.get("best") or 1
    chosen = next(
        (v for v in variations if v.get("variation_number") == chosen_num),
        variations[0],
    )

    normalized_chapters = []
    for scene in chosen.get("scenes", []):
        n = scene["scene_number"]
        norm_ch: dict[str, Any] = {
            "id": _chapter_id(n),
            "text": scene.get("narration", ""),
            "render_engine": scene.get("render_engine", "veo"),
            "art_profile": scene.get("art_profile"),
            "image_prompts": _as_list(
                scene.get("image_prompt") or scene.get("image_prompts")
            ),
        }
        if norm_ch["render_engine"] == "veo":
            norm_ch["video_prompts"] = _as_list(
                scene.get("video_prompt") or scene.get("video_prompts")
            )
        normalized_chapters.append(norm_ch)

    return {
        "video_id": video_id,
        "topic_id": video_id,
        "video_type": "short",
        "prompt_protocol_version": "v2",
        "chosen_variation": chosen_num,
        "chapters": normalized_chapters,
        "humanizer_phrases": chosen.get("humanizer_phrases", []),
    }


def normalize_script(raw_script: dict, variation: int | None = None) -> dict:
    """Dispatcher: normaliza script v2 (short o long) al formato managers."""
    vt = raw_script.get("video_type", "short")
    if vt == "long":
        return _normalize_long(raw_script)
    return _normalize_short(raw_script, variation_override=variation)


# ═══════════════════════════════════════════════════════════════
#  Marcado de estado en topics_db
# ═══════════════════════════════════════════════════════════════

def _mark_topic_assets_rendered(topic_id: str, video_id: str) -> bool:
    """
    Marca el topic con status='assets_rendered' (Fase 2A completa).
    Cuando se construya fase2b.py, ese paso promueve a 'video_generated'.
    """
    db = load_db()
    for t in db.get("topics", []):
        if t.get("id") == topic_id:
            t["status"] = "assets_rendered"
            t["video_id"] = video_id
            t["assets_rendered_at"] = datetime.now().isoformat()
            save_db(db)
            return True
    return False


# Estados que indican que fase2a ya corrió para este topic.
SKIP_STATUSES: frozenset[str] = frozenset({"assets_rendered", "video_generated"})


def _get_topic_status(topic_id: str) -> str | None:
    """Lee el status actual del topic en topics_db. None si no existe."""
    db = load_db()
    for t in db.get("topics", []):
        if t.get("id") == topic_id:
            return t.get("status")
    return None


def _should_skip(script_path: Path, force: bool) -> tuple[bool, str]:
    """
    Decide si saltar un script según el status del topic.
    Returns: (skip: bool, reason: str)
    """
    if force:
        return False, "force flag activo"

    try:
        raw = json.loads(script_path.read_text(encoding="utf-8"))
        topic_id = raw.get("topic_id")
    except Exception:
        return False, "no se pudo leer topic_id"

    if not topic_id:
        return False, "script sin topic_id"

    status = _get_topic_status(topic_id)
    if status in SKIP_STATUSES:
        return True, f"status='{status}'"
    return False, f"status='{status}'"


# ═══════════════════════════════════════════════════════════════
#  Procesamiento por script
# ═══════════════════════════════════════════════════════════════

def _process_single_script(
    script_path: Path,
    variation: int | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Procesa UN script: normalizar → audio → assets → marcar topic.
    Returns: dict con status y metadatos para el reporte final.
    """
    result: dict[str, Any] = {
        "script": script_path.name,
        "topic_id": None,
        "status": "failed",
        "error": None,
        "audio_ok": False,
        "assets_ok": False,
    }

    try:
        raw = json.loads(script_path.read_text(encoding="utf-8"))
        result["topic_id"] = raw.get("topic_id")

        normalized = normalize_script(raw, variation=variation)
        video_id = normalized["video_id"]

        if dry_run:
            print(f"     [DRY] video_type={normalized['video_type']}, "
                  f"chapters={len(normalized['chapters'])}")
            for ch in normalized["chapters"]:
                print(f"       {ch['id']}: engine={ch['render_engine']} "
                      f"imgs={len(ch.get('image_prompts', []))}")
            result["status"] = "dry_run"
            return result

        # 1. Audio (narración + sync_map)
        # PR 1 chat 24: en LONG el audio se genera en fase1_5 antes de m03 (para
        # que m03 pueda usar timestamps Whisper en PR 3). Acá solo cargamos el
        # sync_map ya existente. SHORT mantiene el flujo actual 1-shot.
        if normalized.get("video_type") == "long":
            audio_dir = OUTPUT_DIR / "audio" / video_id
            sync_map_path = audio_dir / "sync_map.json"
            if not sync_map_path.exists():
                raise RuntimeError(
                    f"sync_map.json no existe en {sync_map_path}. "
                    f"Para LONG, el audio se genera en fase1_5 antes de m03. "
                    f"Re-correr: python fase1_5.py --topic {video_id} --from m01b"
                )
            print(f"     🎙️  Audio (LONG): cargando sync_map de fase1_5...")
        else:
            print(f"     🎙️  Audio (SHORT): generando 1-shot...")
            sync_map_path = audio_process(normalized, language="es")
        result["audio_ok"] = True
        print(f"     ✓ sync_map: {sync_map_path.name}")

        # 2.0 · paso0 EAGER: foto madre del sujeto-objeto + props anclados (topic-level).
        # Corre DESPUÉS del audio, ANTES de asset_process → la foto madre existe (en disco +
        # db) antes de las imágenes de capítulo.
        # paso0 red de seguridad (HANDOFF_132): el paso0 REAL corre en fase1_5 ANTES del assemble.
        # Este call queda como reintento idempotente (p.ej. content-reject transitorio en fase1_5).
        if result["topic_id"]:
            db = load_db()
            for t in db.get("topics", []):
                if t.get("id") == result["topic_id"]:
                    generate_foto_madre_for_topic(t, video_id)
                    save_db(db)
                    break

        # 2. Assets (imágenes Leonardo + clips Veo)
        print(f"     🎨 Assets...")
        manifest_path = asset_process(normalized, sync_map_path=sync_map_path)
        result["assets_ok"] = True
        print(f"     ✓ manifest: {manifest_path.name}")

        # 3. Marcar topic como procesado (no volverá al CSV)
        if result["topic_id"]:
            _mark_topic_assets_rendered(result["topic_id"], video_id)

        result["status"] = "ok"

    except Exception as e:
        error_handler.log_error(
            PipelineStage.VIDEO, e,
            context={
                "script": script_path.name,
                "topic_id": result.get("topic_id"),
            },
        )
        result["error"] = f"{type(e).__name__}: {str(e)[:200]}"

    return result


# ═══════════════════════════════════════════════════════════════
#  Main / CLI
# ═══════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fase 2A — Genera audio + imágenes + clips (sin ensamblar)",
    )
    parser.add_argument(
        "--topic", type=str, default=None,
        help="Procesa solo este topic_id. Sin esto, procesa todos.",
    )
    parser.add_argument(
        "--variation", type=int, default=None,
        help="Para shorts: fuerza la variación (1-3). Default: usa 'best'.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Muestra qué haría sin llamar a las APIs.",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-procesa scripts aunque ya estén marcados como 'assets_rendered'.",
    )
    args = parser.parse_args()

    # Resolver lista de scripts
    if not SCRIPTS_DIR.exists():
        print(f"\n❌ No existe {SCRIPTS_DIR}. Corré fase1 primero.")
        return 1

    if args.topic:
        # Bypass: el usuario pide un topic específico → ignora el CSV
        script_paths = [SCRIPTS_DIR / f"{args.topic}.json"]
        if not script_paths[0].exists():
            print(f"\n❌ Script no encontrado: {script_paths[0]}")
            return 1
    else:
        # Modelo B: solo procesar topic_ids presentes en fase1_review.csv
        try:
            approved_ids = _read_approved_topic_ids_from_csv()
        except (FileNotFoundError, ValueError) as e:
            print(f"\n❌ {e}")
            return 1

        if not approved_ids:
            print(
                f"\n⚠️  El CSV {APPROVED_CSV.name} está vacío (sin filas). "
                f"No hay nada que procesar."
            )
            return 0

        all_scripts = sorted(SCRIPTS_DIR.glob("*.json"))
        script_paths = [p for p in all_scripts if p.stem in approved_ids]

        # Avisar si hay topic_ids en el CSV sin script correspondiente
        found_ids = {p.stem for p in script_paths}
        missing = approved_ids - found_ids
        if missing:
            print(
                f"\n⚠️  {len(missing)} topic_id(s) en CSV sin script en "
                f"{SCRIPTS_DIR.name}/: {sorted(missing)[:3]}"
                f"{'...' if len(missing) > 3 else ''}"
            )

    if not script_paths:
        print(f"\n⚠️  No hay scripts en {SCRIPTS_DIR}")
        return 0

    # Filtrar por status (salvo --force o --topic explícito)
    pending_paths: list[Path] = []
    skipped_already_done: list[tuple[Path, str]] = []

    for sp in script_paths:
        # Si el usuario pidió un topic específico, NO filtramos por status
        # (asumimos que quiere re-procesarlo intencionalmente).
        if args.topic:
            pending_paths.append(sp)
            continue
        skip, reason = _should_skip(sp, force=args.force)
        if skip:
            skipped_already_done.append((sp, reason))
        else:
            pending_paths.append(sp)

    print(f"\n{'═' * 60}")
    print(f"  🎬 FASE 2A — Generación de Assets")
    print(f"  📂 Scripts encontrados: {len(script_paths)}")
    if skipped_already_done:
        print(f"  ⏭️  Ya procesados (saltados): {len(skipped_already_done)}")
    print(f"  ▶️  A procesar ahora: {len(pending_paths)}")
    if args.dry_run:
        print(f"  🧪 DRY RUN activado (no se gastan créditos)")
    if args.force:
        print(f"  💥 FORCE activado (re-procesa todo)")
    if args.variation:
        print(f"  🎞️  Variación forzada (shorts): {args.variation}")
    print(f"{'═' * 60}")

    if not pending_paths:
        print(f"\n  ✅ Nada nuevo que procesar. Usá --force para re-procesar.\n")
        return 0

    script_paths = pending_paths

    results: list[dict] = []
    for i, script_path in enumerate(script_paths, 1):
        print(f"\n  [{i}/{len(script_paths)}] {script_path.stem}")
        r = _process_single_script(
            script_path,
            variation=args.variation,
            dry_run=args.dry_run,
        )
        results.append(r)

        if r["status"] == "ok":
            print(f"     ✅ OK")
        elif r["status"] == "dry_run":
            print(f"     🧪 DRY OK")
        else:
            print(f"     ❌ {r['error']}")

    # Reporte final
    ok = sum(1 for r in results if r["status"] in ("ok", "dry_run"))
    failed = sum(1 for r in results if r["status"] == "failed")

    print(f"\n{'═' * 60}")
    print(f"  📊 RESUMEN FASE 2A")
    print(f"  ✅ OK:       {ok}")
    print(f"  ❌ Fallidos: {failed}")
    if failed:
        print(f"\n  Topics fallidos:")
        for r in results:
            if r["status"] == "failed":
                print(f"    - {r['topic_id'] or r['script']}: {r['error']}")
    print(f"{'═' * 60}\n")

    # Reporte de costos (si el tracker acumuló algo)
    if not args.dry_run:
        try:
            cost_tracker.print_summary()
        except Exception:
            pass  # Si print_summary no existe o falla, no rompemos el reporte

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
