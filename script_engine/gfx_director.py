"""
gfx_director.py — El contexto de un capítulo para la capa gráfica (sin modelo): script, skeleton, canonical, las fuentes
del candado literal, la narración del video y el pool de evidencia. Y la palabra clave de la pregunta de cierre.

F37 §B.4 (papel = único camino): se borró el borrador del director (Gemini Flash: un plan por cap con datos, recortes,
cita, contador, lupa y punch_in; su prompt, su esquema, su validador y su caché `gfx_plan_chNN.json`). El texto de
pantalla sale solo del guion en papel (m01e_pantalla, Fase 1); el title card sale del título de la partición
(01a_skeleton) en gfx_layer. Con el borrador se fueron también la elegibilidad de los verified_facts por cap, la
etiqueta de fuente, el zoom por visión y las cifras «ya animadas» (eran suyos).
"""
from __future__ import annotations

import json
import re
from typing import Any

from config import DATA_DIR

from script_engine.gfx_literal_lock import normalize


# ═══════════════════════════════════════════════════════════════
#  Contexto del cap (insumos compartidos con m03/flow_director, sin LLM)
# ═══════════════════════════════════════════════════════════════

def load_chapter_context(video_id: str, chplan: Any) -> dict[str, Any]:
    """Lee script, verified_facts, skeleton y canonical del cap. Fuentes del candado literal."""
    script = json.loads((DATA_DIR / "scripts" / f"{video_id}.json").read_text(encoding="utf-8"))
    n = int(str(chplan.chapter_id).replace("ch", ""))
    chapter = next((c for c in script.get("chapters", []) if int(c.get("chapter_number", -1)) == n),
                   script["chapters"][n - 1])
    topic_id = script.get("topic_id") or video_id
    steps = DATA_DIR / "scripts" / "_steps" / topic_id
    skeleton_ch: dict[str, Any] = {}
    canonical: Any = {}
    sk: dict[str, Any] = {}
    try:
        sk = json.loads((steps / "01a_skeleton.json").read_text(encoding="utf-8"))
        skeleton_ch = next((c for c in sk.get("chapters", []) if c.get("chapter_number") == n), {})
    except (OSError, ValueError):
        pass
    try:
        canonical = json.loads((steps / "02_canonical.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        canonical = {"canonical_subject_description": script.get("canonical_subject_description", "")}

    # verified_facts sin `id`: el orden ES el id (F01 = índice 0). Deuda anotada en DOC_MAESTRO §6.
    facts = [f["fact"] if isinstance(f, dict) else str(f) for f in script.get("verified_facts", [])]
    sources: dict[str, str] = {f"verified_facts[{i}]": t for i, t in enumerate(facts)}
    sources[f"narration_ch{n:02d}"] = chplan.narration or chapter.get("narration", "")
    if skeleton_ch.get("title"):
        sources["skeleton.title"] = skeleton_ch["title"]
    for j, b in enumerate(skeleton_ch.get("bullets", []) or []):
        sources[f"skeleton.bullets[{j}]"] = b
    sources["canonical"] = json.dumps(canonical, ensure_ascii=False)
    for j, src in enumerate(str(x) for x in script.get("sources", []) or []):   # F2 §0d: fuentes del research
        sources[f"sources[{j}]"] = src
    # F2 §0d: próximo cap (NO entra al candado literal del cap)
    next_ch = next((c for c in script.get("chapters", []) if int(c.get("chapter_number", -1)) == n + 1), None)
    next_sources: dict[str, str] = {}
    if next_ch is not None:
        next_sources[f"narration_ch{n + 1:02d}"] = str(next_ch.get("narration", ""))
        nsk = next((c for c in sk.get("chapters", []) if c.get("chapter_number") == n + 1), {})
        for j, b in enumerate(nsk.get("bullets", []) or []):
            next_sources[f"next.bullets[{j}]"] = b
    # F2b §2: narración completa del video (rareza de las palabras de énfasis)
    narration_all = " ".join(str(c.get("narration", "")) for c in script.get("chapters", []))
    # F5 §2: el evidence_pool entra al candado (un recorte que dice lo que la voz NO dice es el caso deseado)
    pool = script.get("evidence_pool") or None
    if pool:
        from script_engine.gfx_pool import pool_sources, short_source
        sources.update(pool_sources(pool))
        for k, it in enumerate(pool.get("datos") or []):
            if it.get("fuente"):
                sources[f"pool.fuente_corta.{k}"] = short_source(it["fuente"])
    return {
        "video_id": video_id, "topic_id": topic_id, "chapter_number": n, "script_chapter": chapter,
        "narration_all": narration_all,
        "facts": facts, "skeleton": skeleton_ch, "canonical": canonical, "sources": sources,
        "next_sources": next_sources,
        "chapters": script.get("chapters", []),           # F3: pregunta de cierre (cap actual + siguiente)
        "pool": pool, "skeleton_all": sk if pool else {},   # F5 §2 (None/{} sin pool: todo igual que antes)
    }


# ═══════════════════════════════════════════════════════════════
#  Pregunta de cierre: la palabra que se acentúa
# ═══════════════════════════════════════════════════════════════

_STOP = {"de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas", "y", "o", "en", "a", "al", "que", "qué",
         "por", "con", "para", "sin", "se", "su", "sus", "lo", "le", "les", "es", "fue", "era", "cómo", "como", "cuál",
         "cuáles", "cuánto", "cuántos", "cuántas", "quién", "quiénes", "dónde", "cuándo", "por qué", "más", "muy", "no"}


def question_keyword(text: str) -> str:
    """Palabra clave a acentuar: la palabra de contenido más larga."""
    words = re.findall(r"[\wáéíóúñü]+", text)
    cands = [w for w in words if len(w) >= 4 and normalize(w) not in _STOP]
    return max(cands, key=len) if cands else ""
