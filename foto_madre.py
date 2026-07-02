"""
foto_madre.py — CONSUMO-A (HANDOFF_128_B): paso0 EAGER, genera y persiste la foto madre.

Pre-pass a nivel TOPIC que, ANTES de generar imágenes de capítulo, crea la foto madre del
sujeto-objeto (central_subject.kind=="object") y de cada prop anclado="si", una sola vez,
AISLADA (forma completa, fondo neutro, sin escena/evento/personas → content-safe, sin 422),
y guarda el PATH ABSOLUTO local en la db (holder["foto_madre"]).

Reúso entre re-runs: si holder["foto_madre"] ya apunta a un archivo que existe → skip (path
determinista, no regenera, no gasta otro render).

ALCANCE (§ handoff): SOLO genera + persiste. NO consume la foto madre (el ruteo /edit es
CONSUMO-B, otro handoff). Tras este pre-pass las imágenes de capítulo SIGUEN saliendo t2i puro.
El style constante es el del canal (m03:149, byte-idéntico).
"""
from __future__ import annotations

import re
from pathlib import Path

from config import OUTPUT_DIR
from error_handler import error_handler, PipelineStage
# Reúso del motor de imagen activo (kling/seedream/flux) y su error de content-safety.
from asset_manager import _generate_image_raw, ContentRejectedError

# Style constante del canal — VERBATIM del slot `style` de m03 (m03_visual.py:149).
_STYLE = "documentary photographic realism, dark-history, faceless"


def _slug(nombre: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (nombre or "").lower()).strip("_")
    return (s or "objeto")[:60]


# ═══════════════════════════════════════════════════════════════
#  PROMPTS (autorados por Claude-chat, MPR R4 — forma aislada, fondo neutro)
# ═══════════════════════════════════════════════════════════════
def _prompt_subject(topic: dict) -> str:
    """Forma del sujeto-objeto. Campos de era_visual_canon; omite la línea si el campo
    está vacío (no dejar 'Scale: .' colgando)."""
    era = topic.get("era_visual_canon") or {}
    df = (era.get("distinctive_features") or "").strip()
    mt = (era.get("materials_textures") or "").strip()
    sc = (era.get("scale_dimensions") or "").strip()

    lines = [f"Isolated technical study of a single subject: {df}"]
    ms = []
    if mt:
        ms.append(f"Materials and texture: {mt}.")
    if sc:
        ms.append(f"Scale: {sc}.")
    if ms:
        lines.append(" ".join(ms))
    lines.append(
        "The subject is centered and fully visible against a plain, neutral, seamless "
        "background — no scenery, no people, no event, no action, even neutral lighting "
        f"that reveals the full silhouette and proportions. {_STYLE}."
    )
    return "\n".join(lines)


def _prompt_prop(prop: dict) -> str:
    """Forma de un prop anclado="si"."""
    forma = (prop.get("forma") or "").strip()
    return (
        f"Isolated technical study of a single object: {forma}\n"
        "The object is centered and fully visible against a plain, neutral, seamless "
        "background — no scenery, no people, no event, even neutral lighting revealing "
        f"its full form. {_STYLE}."
    )


# ═══════════════════════════════════════════════════════════════
#  PRODUCTOR
# ═══════════════════════════════════════════════════════════════
def generate_foto_madre_for_topic(topic: dict, video_id: str) -> dict:
    """Genera + persiste la foto madre del sujeto-objeto y props anclados del topic.

    Muta el topic in-place (holder["foto_madre"] = path absoluto) y lo devuelve; el caller
    persiste con save_db. Skip por reúso si el archivo ya existe. NO crashea el topic si el
    motor rechaza el prompt (ContentRejectedError → foto_madre="" y sigue)."""
    candidatos: list[tuple[str, dict, str]] = []

    cs = topic.get("central_subject") or {}
    if cs.get("kind") == "object":
        candidatos.append(("subject", cs, _prompt_subject(topic)))
    for prop in (topic.get("documented_props") or []):
        if prop.get("anclado") == "si":
            candidatos.append(("prop", prop, _prompt_prop(prop)))

    if not candidatos:
        return topic

    madre_dir = OUTPUT_DIR / video_id / "foto_madre"
    for tag, holder, prompt in candidatos:
        label = "subject" if tag == "subject" else (holder.get("nombre") or "prop")
        dest = madre_dir / f"{_slug(label)}.png"

        # SKIP / reúso: holder ya apunta a un archivo que EXISTE → no regenerar.
        existing = holder.get("foto_madre")
        if existing and Path(existing).exists():
            print(f"     [foto_madre] skip {tag}:{label} (ya existe)")
            continue

        try:
            _generate_image_raw(prompt, dest, use_ultra=False, seed=None)
            holder["foto_madre"] = str(dest.resolve())   # PATH ABSOLUTO (Consumo-B lo lee)
            print(f"     [foto_madre] ✓ {tag}:{label} → {dest.name}")
        except ContentRejectedError as e:
            # NO crashear el topic: dejar foto_madre="" y seguir con el resto.
            error_handler.log_warning(
                PipelineStage.VIDEO,
                f"foto_madre rechazada por content-safety ({tag}:{label}): {str(e)[:150]}",
            )
            holder["foto_madre"] = ""

    return topic
