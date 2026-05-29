"""
m06_assembler.py — Ensambla el JSON final del contrato sagrado para fase2.

Lee los outputs de los módulos m00→m03 desde _steps/<topic_id>/ y arma
data/scripts/<topic_id>.json siguiendo la sección 7 de ARCHITECTURE.md.

NO toca prompts/narración. Solo combina campos.
"""

import json
from pathlib import Path
from datetime import datetime

from config import DATA_DIR


STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"
SCRIPTS_DIR: Path = DATA_DIR / "scripts"
TOPICS_DB: Path = DATA_DIR / "topics_db.json"


def _load_step(topic_id: str, filename: str) -> dict:
    path = STEPS_DIR / topic_id / filename
    if not path.exists():
        raise FileNotFoundError(f"m06_assembler: falta {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_topic(topic_id: str) -> dict:
    if not TOPICS_DB.exists():
        raise FileNotFoundError(f"m06_assembler: falta {TOPICS_DB}")
    db = json.loads(TOPICS_DB.read_text(encoding="utf-8"))
    topics = db.get("topics", []) if isinstance(db, dict) else db
    for t in topics:
        if t.get("id") == topic_id or t.get("topic_id") == topic_id:
            return t
    raise KeyError(f"m06_assembler: topic {topic_id} no existe en topics_db")


def _mode_art_profile(image_prompts: list) -> str:
    """Devuelve el art_profile de las imágenes — no-op desde chat 19.

    Antes calculaba la moda del array. Tras el refactor del catálogo,
    todos los items emiten art_profile="" como placeholder backward-compat,
    así que siempre devuelve "". Firma pública mantenida para no romper
    callers existentes.
    """
    return ""


def assemble_final_script(topic_id: str) -> Path:
    """Ensambla data/scripts/<topic_id>.json siguiendo el contrato sagrado.

    Returns:
      Path al archivo final escrito.

    Raises:
      FileNotFoundError: si falta algún input de _steps/.
    """
    topic = _load_topic(topic_id)
    narration = _load_step(topic_id, "01b_narration.json")
    visual = _load_step(topic_id, "03_visual.json")

    narration_by_cap = {c["chapter_number"]: c for c in narration.get("chapters", [])}
    visual_by_cap = {c["chapter_number"]: c for c in visual.get("chapters", [])}

    chapters_final = []
    for cap_num in sorted(visual_by_cap.keys()):
        narr = narration_by_cap.get(cap_num, {})
        vis = visual_by_cap[cap_num]

        render_engine = "veo" if cap_num in (1, 7) else "flux"
        cap_out = {
            "chapter_number": cap_num,
            "narration": narr.get("narration", ""),
            "render_engine": render_engine,
            "art_profile": vis.get("art_profile", ""),
        }

        if render_engine == "veo":
            cap_out["image_prompt"] = vis.get("image_prompt", "")
            cap_out["video_prompt"] = vis.get("video_prompt", "")
            # Chat 29 #175 — propagar keys del híbrido Veo+Flux al canonical
            # (gap del handoff original: m06_assembler no estaba en la lista
            # de archivos modificados; sin esto, fase2a/asset_manager/fase2b
            # recibirían el canonical sin supps y el branch híbrido NO se
            # activaría. Fix runtime BACKLOG #208).
            cap_out["narration_anchor"] = vis.get("narration_anchor", "")
            cap_out["veo_position"] = vis.get("veo_position", "start")
            cap_out["supplemental_image_prompts"] = (
                vis.get("supplemental_image_prompts") or []
            )
        else:
            # cap-level art_profile = "" (catálogo desconectado en chat 19;
            # backward compat con consumidores que esperan la key).
            image_prompts = vis.get("image_prompts", [])
            cap_out["image_prompts"] = image_prompts
            cap_out["art_profile"] = _mode_art_profile(image_prompts)

        chapters_final.append(cap_out)

    final = {
        "topic_id":                  topic_id,
        "video_type":                "long",
        "prompt_protocol_version":   "v2",
        "video_title":               topic.get("video_title", ""),
        "chapters":                  chapters_final,
        "humanizer_phrases":         narration.get("humanizer_phrases", []),
        # metadata trazable:
        "verified_facts":            topic.get("verified_facts", []),
        "sources":                   topic.get("sources", []),
        "research_summary":          topic.get("research_summary", ""),
        "canonical_subject_description": topic.get("canonical_subject_description", ""),
        "discovery_mode":            topic.get("discovery_mode", ""),
        "total_veo_chapters":        sum(1 for c in chapters_final if c["render_engine"] == "veo"),
        "total_flux_chapters":       sum(1 for c in chapters_final if c["render_engine"] == "flux"),
        "created_at":                datetime.utcnow().isoformat() + "Z",
    }

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = SCRIPTS_DIR / f"{topic_id}.json"
    out_file.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_file
