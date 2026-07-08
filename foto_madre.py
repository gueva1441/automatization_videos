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

import json
import re
from pathlib import Path

import requests

from config import OUTPUT_DIR, api
from error_handler import error_handler, PipelineStage
# Motor de imagen activo (kling/seedream/flux) como FALLBACK, su error de content-safety,
# y los helpers fal compartidos (headers, poll de la queue, detección de rechazo).
from asset_manager import (
    _generate_image_raw,
    ContentRejectedError,
    _fal_headers,
    _flux_poll,
    _is_content_rejection,
)

# Style constante del canal — VERBATIM del slot `style` de m03 (m03_visual.py:149).
_STYLE = "documentary photographic realism, dark-history, faceless"

# Motor de las FOTOS MADRE (HANDOFF_132): GPT Image 2 vía fal. Constante arriba para
# cambiarlo sin tocar lógica. La calidad de la madre manda la del video entero, y este
# motor rinde el canon completo mejor que Seedream (que se queda para el resto del pipeline).
MADRE_IMAGE_MODEL = "openai/gpt-image-2"


def _slug(nombre: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (nombre or "").lower()).strip("_")
    return (s or "objeto")[:60]


def _clean(s: str | None) -> str:
    """Normaliza un campo del canon: sin espacios ni punto final colgando. Evita los
    '..' dobles al concatenar campos que YA vienen con punto — el template pone el suyo."""
    return (s or "").strip().rstrip(".").strip()


def _ensure_real_png(path: Path) -> None:
    """Garantiza que `path` sea un PNG REAL. Si los bytes no arrancan con el magic PNG
    (89 50 4e 47…), re-encoda con PIL a PNG de verdad. Lección del probe GPT→Seedream:
    GPT Image puede devolver JPEG con la URL/extensión .png (renombrar NO alcanza)."""
    with open(path, "rb") as f:
        sig = f.read(8)
    if sig.startswith(b"\x89PNG\r\n\x1a\n"):
        return
    from PIL import Image
    with Image.open(path) as im:
        im.convert("RGB").save(path, format="PNG", optimize=True)
    print(f"     [foto_madre] re-encodada a PNG real: {path.name}")


def _generate_madre_gpt(prompt: str, dest: Path) -> dict:
    """Genera una foto madre con GPT Image 2 (fal `openai/gpt-image-2`, t2i) y la deja en
    `dest` como PNG real. Mismo cliente/patrón fal que asset_manager (misma FAL_KEY, misma
    queue + poll). NO lleva @error_handler.retry a propósito: ese decorador envuelve el fallo
    final en PipelineError y se comería el ContentRejectedError; la resiliencia la da el
    fallback del caller (que sí cae en el motor decorado). Levanta ContentRejectedError si fal
    rechaza por content-safety, o la excepción de red/API cruda."""
    payload = {
        "prompt": prompt,
        # HANDOFF_140+ (FIX resolución madre): el preset "landscape_16_9" salía
        # 1088×608 — muy chico para anclar vía /edit. openai/gpt-image-2 en fal acepta
        # {width,height} explícito (múltiplos de 16, edge≤3840, aspecto≤3:1, px 655K–8.3M).
        # 2560×1440 = IGUAL al output de los caps (seedream/edit rinde 2560×1440) → la
        # referencia tiene el mismo detalle que el target, sin upscaling. 3.69M px.
        "image_size": {"width": 2560, "height": 1440},
        "quality": "high",
        "num_images": 1,
        "output_format": "png",
    }
    submit_url = f"{api.fal_base_url}/{MADRE_IMAGE_MODEL}"
    try:
        resp = requests.post(submit_url, headers=_fal_headers(), json=payload, timeout=120)
        resp.raise_for_status()
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        if _is_content_rejection(body):
            raise ContentRejectedError(f"{MADRE_IMAGE_MODEL} rechazó prompt: {body[:300]}")
        raise

    result = resp.json()
    # queue.fal.run → respuesta con status_url/response_url; algunos endpoints responden
    # directo con images. Cubrimos ambos (espejo del path flux de _generate_image_raw).
    # HANDOFF_140+ (FIX poll madre): timeout 300s (default 180). A 2560×1440 gpt-image-2
    # tarda ~150-200s; 180s dejaba margen mínimo → timeouts transitorios caían al fallback
    # seedream. 300s cubre la variación de cola sin cambiar el resto.
    data = result if "images" in result else _flux_poll(
        result["status_url"], result["response_url"], timeout=300)
    if "images" not in data or not data["images"]:
        raise RuntimeError(f"{MADRE_IMAGE_MODEL} sin imágenes: {json.dumps(data)[:300]}")

    image_url = data["images"][0]["url"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()
    dest.write_bytes(img_resp.content)
    _ensure_real_png(dest)   # GPT puede devolver JPEG → re-encoda a PNG real
    return {"endpoint": MADRE_IMAGE_MODEL, "path": str(dest)}


# ═══════════════════════════════════════════════════════════════
#  PROMPTS (autorados por Claude-chat, MPR R4 — forma aislada, fondo neutro)
# ═══════════════════════════════════════════════════════════════
def _prompt_subject(topic: dict) -> str:
    """Forma del sujeto-objeto con el canon COMPLETO (HANDOFF_132). Campos de
    era_visual_canon; se omite la línea si el campo está vacío. El sujeto va en su MEDIO
    natural (a un objeto gigante su entorno es parte de la forma), 3/4 a nivel de piso/mar
    (el ángulo en que los caps lo consumen). 'Archival documentary photograph' mata el look
    juguete/maqueta. _clean corta el punto colgante de cada campo → sin '..' dobles."""
    era = topic.get("era_visual_canon") or {}
    df = _clean(era.get("distinctive_features"))
    mt = _clean(era.get("materials_textures"))
    sc = _clean(era.get("scale_dimensions"))
    cp = _clean(era.get("color_palette"))
    dec = _clean(era.get("primary_decade"))
    fb = _clean(era.get("forbidden_anachronisms"))

    era_tag = f" from the {dec}" if dec else ""
    lines = [f"Archival{era_tag} documentary photograph of a single subject: {df}."]
    detail = []
    if mt:
        detail.append(f"Materials and texture: {mt}")
    if cp:
        detail.append(f"Color: {cp}")
    if sc:
        detail.append(f"Scale: {sc}")
    if detail:
        lines.append(". ".join(detail) + ".")
    if fb:
        lines.append(f"Period-correct technology only — strictly avoid: {fb}.")
    lines.append(
        "The subject is shown alone in its natural operating environment (open sea, "
        "open sky or bare terrain as appropriate), plain and empty — no people, no "
        "other vehicles or structures, no event, no action. Seen from ground/sea "
        "level at a three-quarter profile view, the whole subject fully visible from "
        f"its base or waterline to its highest point. {_STYLE}."
    )
    return "\n".join(lines)


def _prompt_prop(prop: dict, topic: dict) -> str:
    """Forma de un prop anclado="si". Sigue AISLADO en fondo neutro (objeto chico, el
    estudio le queda bien); HANDOFF_132 solo le suma época + prohibidos del canon."""
    era = topic.get("era_visual_canon") or {}
    forma = _clean(prop.get("forma"))
    dec = _clean(era.get("primary_decade"))
    fb = _clean(era.get("forbidden_anachronisms"))

    dec_tag = f" {dec}" if dec else ""
    lines = [
        f"Archival{dec_tag} documentary photograph, isolated technical study of a "
        f"single object: {forma}."
    ]
    if fb:
        lines.append(f"Period-correct only — strictly avoid: {fb}.")
    lines.append(
        "The object is centered and fully visible against a plain, neutral, seamless "
        "background — no scenery, no people, no event, even neutral lighting revealing "
        f"its full form. {_STYLE}."
    )
    return "\n".join(lines)


def _prompt_place(topic: dict) -> str:
    """Retrato del ESTABLECIMIENTO — RUTA B (HANDOFF_134d): la vista canónica identificatoria
    de un kind=place (aérea/establishing 3/4, silueta y footprint completos) para anclar la
    IDENTIDAD del sitio (la torre, la disposición del complejo) que driftea render a render.

    A DIFERENCIA de _prompt_subject (object): época-DEL-SUJETO (arquitectura period-correct),
    NUNCA época-de-la-foto — sin 'archival photograph from [era]' que fuerza B&N/placa (lección
    133); la plantilla nace SIN ese bug (dice 'full-color', ata la década a la arquitectura, no
    a la foto). Estado explícito desde condition_evolution (el dominante; si ambiguo, at_event),
    coherente con R1. Suma anachronism_blocklist."""
    era = topic.get("era_visual_canon") or {}
    df = _clean(era.get("distinctive_features"))
    sc = _clean(era.get("scale_dimensions"))
    mt = _clean(era.get("materials_textures"))
    cp = _clean(era.get("color_palette"))
    dec = _clean(era.get("primary_decade"))
    fb = _clean(era.get("forbidden_anachronisms"))
    cond = era.get("condition_evolution") or {}
    state = _clean(cond.get("at_event")) or _clean(cond.get("later"))
    blocklist = [str(b).strip() for b in (topic.get("anachronism_blocklist") or []) if str(b).strip()]

    arch = f"period-correct {dec} " if dec else ""
    lines = [f"A wide, full-color establishing view of a single place — its identifying "
             f"{arch}architecture: {df}."]
    detail = []
    if mt:
        detail.append(f"Materials and texture: {mt}")
    if cp:
        detail.append(f"Color: {cp}")
    if sc:
        detail.append(f"Scale and layout: {sc}")
    if detail:
        lines.append(". ".join(detail) + ".")
    if state:
        lines.append(f"Shown in this condition: {state}.")
    if fb:
        lines.append(f"Period-correct only — strictly avoid: {fb}.")
    if blocklist:
        lines.append("Never show: " + ", ".join(blocklist) + ".")
    lines.append(
        "The whole complex is seen from a high three-quarter aerial establishing angle, its "
        "full footprint and silhouette visible — every building, wing and tower in its real "
        "arrangement — set plainly in its surroundings, no people, no event, no action, in even "
        f"natural daylight that reveals the layout. {_STYLE}."
    )
    return "\n".join(lines)


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
    kind = cs.get("kind")
    if kind == "object":
        candidatos.append(("subject", cs, _prompt_subject(topic)))
    elif kind == "place":
        # RUTA B (HANDOFF_134d): un LUGAR también tiene foto carnet — la vista canónica del
        # establecimiento. Mismo tag "subject" → mismo bucket del registry (__subject__); el
        # resto de la cadena ni se entera de que es place. Toda la mecánica se hereda.
        candidatos.append(("subject", cs, _prompt_place(topic)))
    for prop in (topic.get("documented_props") or []):
        if prop.get("anclado") == "si":
            candidatos.append(("prop", prop, _prompt_prop(prop, topic)))

    if not candidatos:
        # CHASCADA 1 (HANDOFF_134d): EL SILENCIO GRITADO. Con object+place soportados, esto
        # queda para person/other → que NUNCA MÁS un topic pierda todas las anclas en silencio.
        print(f"     [paso0] central_subject kind={kind!r} → SIN madre/anclas (por diseño)")
        return topic

    madre_dir = OUTPUT_DIR / video_id / "foto_madre"
    for tag, holder, prompt in candidatos:
        label = "subject" if tag == "subject" else (holder.get("nombre") or "prop")
        dest = madre_dir / f"{_slug(label)}.png"

        # SKIP / reúso por DB: holder ya apunta a un archivo que EXISTE → no regenerar.
        existing = holder.get("foto_madre")
        if existing and Path(existing).exists():
            print(f"     [foto_madre] skip {tag}:{label} (ya existe)")
            continue

        # ADOPCIÓN de madre manual (HANDOFF_132): si Omar dejó un archivo en el destino,
        # ESE es el gate humano oficial (sin UI nueva). NO generar: adoptar el path y
        # persistirlo. Cubre el topic NUEVO (db sin path → el skip de arriba no lo agarra),
        # que antes se PISABA con una madre generada.
        if dest.exists():
            _ensure_real_png(dest)   # el archivo manual puede venir JPEG → PNG real
            holder["foto_madre"] = str(dest.resolve())
            print(f"     [foto_madre] ADOPTADA manual: {label}")
            continue

        # GENERAR: motor GPT Image 2, con FALLBACK al motor activo (seedream/kling/flux) si
        # GPT falla por lo que sea (error API o content-reject). La madre NUNCA bloquea el topic.
        try:
            try:
                _generate_madre_gpt(prompt, dest)
                motor = MADRE_IMAGE_MODEL
            except Exception as e_gpt:
                error_handler.log_warning(
                    PipelineStage.VIDEO,
                    f"foto_madre GPT falló ({tag}:{label}): {str(e_gpt)[:150]} "
                    f"→ fallback a {api.image_engine}",
                )
                _generate_image_raw(prompt, dest, use_ultra=False, seed=None)
                _ensure_real_png(dest)
                motor = api.image_engine
            holder["foto_madre"] = str(dest.resolve())   # PATH ABSOLUTO (Consumo-B lo lee)
            print(f"     [foto_madre] ✓ {tag}:{label} → {dest.name}  ({motor})")
        except Exception as e:
            # Ni GPT ni el fallback pudieron (p.ej. ambos content-reject): no crashear el
            # topic → foto_madre="" y seguir. Consumo-B degrada ese ancla a t2i.
            error_handler.log_warning(
                PipelineStage.VIDEO,
                f"foto_madre no generada ({tag}:{label}): {str(e)[:150]}",
            )
            holder["foto_madre"] = ""

    return topic
