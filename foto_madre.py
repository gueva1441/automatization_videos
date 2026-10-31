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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from config import OUTPUT_DIR, DATA_DIR, api
from error_handler import error_handler, PipelineStage
from cost_tracker import cost_tracker
from engine_profiles import select_profile
# Motor de imagen activo (kling/seedream/flux) como FALLBACK, su error de content-safety,
# y los helpers fal compartidos (headers, poll de la queue, detección de rechazo).
# F60 B: + la cola de fal (_fal_queue_poll, FAL_SUBMIT_TIMEOUT_S), el payload t2i de Seedream, el filtro por era y
# la normalización de `persona` (la madre de persona se pide con la misma función de poll que clips y secuencia).
from asset_manager import (
    _generate_image_raw,
    ContentRejectedError,
    _fal_headers,
    _flux_poll,
    _is_content_rejection,
    _fal_queue_poll,
    _seedream_payload_for,
    _norm_persona,
    persona_aporta_madre,
    FAL_SUBMIT_TIMEOUT_S,
    FLUX_MAX_WORKERS,
)

# F60 B: `persona` se lee de _steps/<id>/03_visual.json (paso0 corre DESPUÉS de m03 en fase1_5). Patcheable en lab.
STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"

# Style constante del canal — VERBATIM del slot `style` de m03 (m03_visual.py:149).
_STYLE = "documentary photographic realism, dark-history, faceless"

# Motor de las FOTOS MADRE (HANDOFF_132): GPT Image 2 vía fal. Constante arriba para
# cambiarlo sin tocar lógica. La calidad de la madre manda la del video entero, y este
# motor rinde el canon completo mejor que Seedream (que se queda para el resto del pipeline).
MADRE_IMAGE_MODEL = "openai/gpt-image-2"

# F60 B: la madre de PERSONA sale con ropa neutra (la escena pone la suya): «sin manchas que se arrastren» (Omar 17:48).
ROPA_MADRE = "wearing a plain, clean, light-coloured shirt"
# F60 B: madre de persona solo si sale en ≥ 2 fotos dentro de su era (analista, handoff F60 base: con 1 foto no hay cara que mantener).
MADRE_PERSONA_MIN_FOTOS = 2


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
#  F60 B — MADRE POR PERSONA (Seedream t2i del perfil, por la cola de fal)
# ═══════════════════════════════════════════════════════════════
def _fotos_del_guion(visual: dict) -> list[dict]:
    """F60 B: todas las fotos de 03_visual.json en orden de guion (cap, índice): la foto del clip (image_f8), las
    image_prompts de caps flux y las supps de caps con clip. Cada una con `persona` normalizada, `anio` y `people_group`."""
    out: list[dict] = []
    for ch in sorted(visual.get("chapters") or [], key=lambda c: c.get("chapter_number") or 0):
        n = ch.get("chapter_number")
        f8 = ch.get("image_f8")
        if isinstance(f8, dict):
            out.append({"cap": n, "kind": "f8", "idx": 1, "persona": _norm_persona(f8.get("persona")),
                        "anio": f8.get("anio"), "people_group": f8.get("people_group") or []})
        for key, kind in (("image_prompts", "img"), ("supplemental_image_prompts", "supp")):
            for i, it in enumerate(ch.get(key) or [], start=1):
                if isinstance(it, dict):
                    out.append({"cap": n, "kind": kind, "idx": i, "persona": _norm_persona(it.get("persona")),
                                "anio": it.get("anio"), "people_group": it.get("people_group") or []})
    return out


def _fotos_con_madre_de(person: dict, fotos: list[dict]) -> list[dict]:
    """Las fotos donde el nombre está en `persona` (cualquier posición) Y la persona aporta madre por era (filtro F60 B)."""
    name = person.get("name")
    return [f for f in fotos if name in f["persona"] and persona_aporta_madre(person, f["anio"])]


def _grupo_mas_frecuente(fotos: list[dict], grupos: dict[str, dict]) -> str:
    """El `appearance` del people_group más frecuente en esas fotos (cualquier posición); empate → el que aparece primero
    en orden de guion. '' si ninguna foto trae grupo o el grupo no está en el canon."""
    cuenta: dict[str, int] = {}
    orden: list[str] = []
    for f in fotos:
        for g in f["people_group"] or []:
            if isinstance(g, str) and g:
                cuenta[g] = cuenta.get(g, 0) + 1
                if g not in orden:
                    orden.append(g)
    if not orden:
        return ""
    mejor = max(orden, key=lambda g: (cuenta[g], -orden.index(g)))
    return str((grupos.get(mejor) or {}).get("appearance") or "").strip()


def _prompt_persona(person: dict, appearance_grupo: str) -> str:
    """F60 B.1 (handoff B+C, punto 2; en código, sin LLM): `appearance_canon` entero (desde A3 trae solo el aspecto fijo;
    `condition_by_period` NO entra), ROPA_MADRE, el appearance del people_group, retrato neutro, ESTILO_C con el año de la
    madre (primer número de 4 dígitos de `era`; sin número → sin año) y NO_TEXT. Sin `_STYLE` (lleva «faceless»)."""
    from script_engine import m03_imagenes_v3 as v3img  # noqa: PLC0415
    canon = _clean(person.get("appearance_canon"))
    m = re.search(r"\d{4}", str(person.get("era") or ""))
    estilo = v3img.ESTILO_C.format(anio=m.group(0)) if m else v3img.ESTILO_C.replace(" taken in {anio}", "")
    grupo = appearance_grupo.strip()
    if grupo and not grupo.endswith("."):
        grupo += "."
    return (f"Head-and-shoulders portrait of {canon}, {ROPA_MADRE}. {grupo + ' ' if grupo else ''}Neutral expression, "
            f"facing the camera, plain mid-grey background, soft even light. {estilo} {v3img.NO_TEXT}")


def _generate_madre_seedream(prompt: str, dest: Path) -> dict:
    """F60 B: madre de PERSONA con Seedream t2i del perfil (model_id e image_size de engine_profiles) por la COLA de fal:
    submit a api.fal_base_url (timeout FAL_SUBMIT_TIMEOUT_S), espera con _fal_queue_poll (la misma función que clips y
    secuencia), baja el PNG, lo deja real y registra 1 imagen en el costo. Rechazo → ContentRejectedError; NO cae a GPT."""
    profile = select_profile("seedream")
    payload = _seedream_payload_for(prompt)
    try:
        resp = requests.post(f"{api.fal_base_url}/{profile.render.model_id}", headers=_fal_headers(), json=payload,
                             timeout=FAL_SUBMIT_TIMEOUT_S)
        resp.raise_for_status()
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        if _is_content_rejection(body):
            raise ContentRejectedError(f"{profile.render.model_id} rechazó prompt: {body[:300]}")
        raise
    sub = resp.json()
    data = sub if "images" in sub else _fal_queue_poll(sub["status_url"], sub["response_url"])
    if not data.get("images"):
        raise RuntimeError(f"{profile.render.model_id} sin imágenes: {json.dumps(data)[:300]}")
    img = data["images"][0]
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(img["url"], timeout=60)
    r.raise_for_status()
    dest.write_bytes(r.content)
    _ensure_real_png(dest)
    cost_tracker.track_seedream(description=f"foto madre persona {dest.stem}", images=1)
    return {"endpoint": profile.render.model_id, "path": str(dest), "seed": data.get("seed"),
            "nsfw": data.get("has_nsfw_concepts"), "request_id": sub.get("request_id")}


def generate_fotos_madre_personas(topic: dict, video_id: str, visual: dict | None = None) -> dict:
    """F60 B: madre por PERSONA del canon (`documented_people`) que sale en ≥ MADRE_PERSONA_MIN_FOTOS fotos (su nombre en
    `persona`, cualquier posición, en todos los caps incluidos los de clip) donde aporta madre por era. Lee `persona` de
    `_steps/<id>/03_visual.json` (o de `visual`). Motor: Seedream del perfil por la cola; si el motor activo no es seedream
    → sin madre de persona y aviso (no cae a GPT); rechazo o error → foto_madre="" y aviso. Mismo skip (archivo existente)
    y adopción manual que objeto/lugar. Destino output/<vid>/foto_madre/<slug(name)>.png; path absoluto en
    documented_people[i]["foto_madre"]. Las madres de distintas personas se piden a la vez (tope FLUX_MAX_WORKERS).
    Muta el topic y devuelve {nombre: {estado, fotos, prompt, dest}}."""
    personas = [p for p in (topic.get("documented_people") or []) if isinstance(p, dict) and p.get("name")]
    if not personas:
        return {}
    if visual is None:
        vpath = STEPS_DIR / str(topic.get("id") or video_id) / "03_visual.json"
        if not vpath.exists():
            print(f"     [foto_madre] sin {vpath} → sin madres de persona (correr m03 antes)")
            return {}
        visual = json.loads(vpath.read_text(encoding="utf-8"))
    fotos = _fotos_del_guion(visual)
    grupos = {g["id"]: g for g in (topic.get("people_groups") or []) if isinstance(g, dict) and g.get("id")}
    madre_dir = OUTPUT_DIR / video_id / "foto_madre"
    estados: dict[str, dict] = {}
    trabajos: list[tuple[dict, Path, str, int]] = []
    for p in personas:
        name = p["name"]
        mias = _fotos_con_madre_de(p, fotos)
        est = {"fotos": len(mias), "fotos_ids": [f"ch{f['cap']:02d}_{f['kind']}_{f['idx']:02d}" for f in mias]}
        estados[name] = est
        if len(mias) < MADRE_PERSONA_MIN_FOTOS:
            est["estado"] = f"sin madre: {len(mias)} foto(s) con persona dentro de su era"
            continue
        if not _clean(p.get("appearance_canon")):
            est["estado"] = "sin madre: appearance_canon vacío"
            continue
        dest = madre_dir / f"{_slug(name)}.png"
        est["dest"] = str(dest)
        existing = p.get("foto_madre")
        if existing and Path(existing).exists():
            est["estado"] = "skip (ya existe)"
            print(f"     [foto_madre] skip persona:{name} (ya existe)")
            continue
        if dest.exists():
            _ensure_real_png(dest)
            p["foto_madre"] = str(dest.resolve())
            est["estado"] = "ADOPTADA manual"
            print(f"     [foto_madre] ADOPTADA manual: {name}")
            continue
        if api.image_engine != "seedream":
            est["estado"] = f"sin madre: motor activo {api.image_engine} ≠ seedream"
            error_handler.log_warning(PipelineStage.VIDEO,
                                      f"foto_madre persona {name}: motor activo {api.image_engine!r} ≠ seedream → sin madre de persona")
            continue
        prompt = _prompt_persona(p, _grupo_mas_frecuente(mias, grupos))
        est["prompt"] = prompt
        trabajos.append((p, dest, prompt, len(mias)))

    def hacer(t):
        p, dest, prompt, n = t
        try:
            meta = _generate_madre_seedream(prompt, dest)
            p["foto_madre"] = str(dest.resolve())   # PATH ABSOLUTO (m06 lo lleva al registry)
            print(f"     [foto_madre] ✓ persona:{p['name']} → {dest.name}  ({n} fotos, {meta['endpoint']})")
            return p["name"], {"estado": "ok", **meta}
        except Exception as e:  # noqa: BLE001 — la madre NUNCA bloquea el topic
            error_handler.log_warning(PipelineStage.VIDEO, f"foto_madre persona {p['name']} no generada: {str(e)[:150]}")
            p["foto_madre"] = ""
            return p["name"], {"estado": f"error: {type(e).__name__}: {str(e)[:160]}"}

    if trabajos:
        with ThreadPoolExecutor(max_workers=min(len(trabajos), FLUX_MAX_WORKERS)) as ex:
            for name, st in ex.map(hacer, trabajos):
                estados[name].update(st)
    return estados


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
        # F60 B: ya no retorna acá — las madres de PERSONA van igual (abajo).
        print(f"     [paso0] central_subject kind={kind!r} → SIN madre/anclas de sujeto (por diseño)")

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

    # F60 B: madres por PERSONA (Seedream por la cola), después de las de sujeto/props.
    generate_fotos_madre_personas(topic, video_id)
    return topic
