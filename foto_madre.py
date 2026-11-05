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

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

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
    _destino_error_fal,
    _guardar_error_fal,
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

# F78a: descriptor de edad ≥ 20 = la tabla de researcher_steps/step_4e_visual_canon.py (REGLAS CRÍTICAS 1, «20-23 → early-20s»…),
# copiada tal cual; 60+ = «elderly» (una de sus dos opciones, adenda F78a 19:36). (desde, hasta, descriptor); hasta None = sin tope.
DESCRIPTOR_EDAD = (
    (20, 23, "early-20s"), (24, 26, "mid-20s"), (27, 29, "late-20s"),
    (30, 33, "early-30s"), (34, 36, "mid-30s"), (37, 39, "late-30s"),
    (40, 43, "early-40s"), (44, 46, "mid-40s"), (47, 49, "late-40s"),
    (50, 53, "early-50s"), (54, 56, "mid-50s"), (57, 59, "late-50s"),
    (60, None, "elderly"),
)
# F78a: < 20 → «fifteen-year-old» (analista F78a: no hay num2words en el repo). Índice = edad − 1.
EDAD_EN_PALABRAS = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
                    "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
# F78a: los rasgos inventados por persona (una llamada con todas) y la carpeta donde va lo viejo que se reemplaza.
RASGOS_JSON = "rasgos.json"
# F78b: lo visible del estado por (persona, tramo), una llamada con todas las filas; cache aparte de los rasgos.
ESTADOS_JSON = "estados.json"
# Carpeta de lo reemplazado = la de la tanda que lo reemplaza (F78a: madres sin rasgos; F78b: variantes con el estado crudo).
PREVIAS_DIR = "_previas_f78b"


def descriptor_edad(n: Any) -> str | None:
    """F78a: edad → descriptor (< 20: «fifteen-year-old»; ≥ 20: tabla DESCRIPTOR_EDAD). No número o < 1 → None."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        return None
    if n < 20:
        return f"{EDAD_EN_PALABRAS[n - 1]}-year-old"
    for desde, hasta, d in DESCRIPTOR_EDAD:
        if n >= desde and (hasta is None or n <= hasta):
            return d
    return None


def clave_de_foto(canon_persona: dict | None, anio: Any) -> dict:
    """F78a (regla única de la variante, la usan foto_madre y asset_manager): para una persona con madre y el año de una foto →
    {clave, tramo, condition, edad, anio_estilo}. tramo = el de `condition_by_period` que contiene el año (si se pisan, el más
    corto; empate → el primero del canon); edad = `age_at_event` + (año − primer año de `era`), solo si `age_at_event` es número
    y su descriptor difiere del de la madre. clave = «AAAA-AAAA» del tramo o «sin_estado», más «_<edad>» si hay edad; sin tramo
    ni edad → clave "" (madre limpia). anio_estilo = primer año del tramo; sin tramo, el año de la foto."""
    from script_engine.m03_visual import _tramo  # noqa: PLC0415 — el lector de tramos del canon (F50d)
    vacio = {"clave": "", "tramo": None, "condition": None, "edad": None, "anio_estilo": None}
    if not isinstance(canon_persona, dict):
        return vacio
    m = re.search(r"\d{4}", str(anio or ""))
    if not m:
        return vacio
    y = int(m.group(0))
    mejor = None
    for c in canon_persona.get("condition_by_period") or []:
        tr = _tramo(c.get("years")) if isinstance(c, dict) else None
        if tr and tr[0] <= y <= tr[1] and (mejor is None or tr[1] - tr[0] < mejor[0][1] - mejor[0][0]):
            mejor = (tr, _clean(c.get("condition")))
    edad = None
    a = canon_persona.get("age_at_event")
    era = _tramo(canon_persona.get("era"))
    if isinstance(a, int) and not isinstance(a, bool) and era:
        e = a + (y - era[0])
        if descriptor_edad(e) and descriptor_edad(e) != descriptor_edad(a):
            edad = e
    if mejor is None and edad is None:
        return vacio
    tramo = f"{mejor[0][0]}-{mejor[0][1]}" if mejor else None
    clave = (tramo or "sin_estado") + (f"_{edad}" if edad is not None else "")
    return {"clave": clave, "tramo": tramo, "condition": mejor[1] if mejor else None, "edad": edad,
            "anio_estilo": mejor[0][0] if mejor else y}


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


def _guardar_prompt_madre(dest: Path, prompt: str, modelo: str, firma: str | None = None) -> None:
    """F68: el prompt de la madre queda junto a ella (`<slug>.prompt.txt`), antes de pedirla. F78b: la variante lleva además su
    `firma` (md5 de estado_visible + edad) en una línea propia; si cambia, la variante se rehace."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    cab = f"modelo: {modelo}\n" + (f"firma: {firma}\n" if firma else "")
    dest.with_suffix(".prompt.txt").write_text(f"{cab}\n{prompt}\n", encoding="utf-8")


def _firma_de(dest: Path) -> str | None:
    """F78b: la `firma` guardada en el `.prompt.txt` de una variante (None si no hay archivo o no la tiene: variante vieja)."""
    t = dest.with_suffix(".prompt.txt")
    if not t.exists():
        return None
    m = re.search(r"^firma: (\w+)$", t.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def _generate_madre_gpt(prompt: str, dest: Path) -> dict:
    """Genera una foto madre con GPT Image 2 (fal `openai/gpt-image-2`, t2i) y la deja en
    `dest` como PNG real. Mismo cliente/patrón fal que asset_manager (misma FAL_KEY, misma
    queue + poll). NO lleva @error_handler.retry a propósito: ese decorador envuelve el fallo
    final en PipelineError y se comería el ContentRejectedError; la resiliencia la da el
    fallback del caller (que sí cae en el motor decorado). Levanta ContentRejectedError si fal
    rechaza por content-safety, o la excepción de red/API cruda."""
    _destino_error_fal(dest)
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
        _guardar_error_fal(body)
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


def _prompt_persona(person: dict, appearance_grupo: str, rasgos: str) -> str:
    """F60 B.1 / F78a: `appearance_canon` entero (desde A3 trae solo el aspecto fijo; `condition_by_period` NO entra), los
    `rasgos` inventados de la persona (F78a: una llamada con todas, `rasgos_personas`), ROPA_MADRE, el appearance del
    people_group, retrato neutro, ESTILO_C con el año de la madre (primer número de 4 dígitos de `era`; sin número → sin año) y
    NO_TEXT. Sin `_STYLE` (lleva «faceless»)."""
    from script_engine import m03_imagenes_v3 as v3img  # noqa: PLC0415
    canon = _clean(person.get("appearance_canon"))
    m = re.search(r"\d{4}", str(person.get("era") or ""))
    estilo = v3img.ESTILO_C.format(anio=m.group(0)) if m else v3img.ESTILO_C.replace(" taken in {anio}", "")
    grupo = appearance_grupo.strip()
    if grupo and not grupo.endswith("."):
        grupo += "."
    return (f"Head-and-shoulders portrait of {canon}, {_clean(rasgos)}, {ROPA_MADRE}. {grupo + ' ' if grupo else ''}"
            f"Neutral expression, facing the camera, plain mid-grey background, soft even light. {estilo} {v3img.NO_TEXT}")


def _generate_madre_seedream(prompt: str, dest: Path) -> dict:
    """F60 B: madre de PERSONA con Seedream t2i del perfil (model_id e image_size de engine_profiles) por la COLA de fal:
    submit a api.fal_base_url (timeout FAL_SUBMIT_TIMEOUT_S), espera con _fal_queue_poll (la misma función que clips y
    secuencia), baja el PNG, lo deja real y registra 1 imagen en el costo. Rechazo → ContentRejectedError; NO cae a GPT."""
    profile = select_profile("seedream")
    payload = _seedream_payload_for(prompt)
    _guardar_prompt_madre(dest, prompt, profile.render.model_id)
    _destino_error_fal(dest)
    try:
        resp = requests.post(f"{api.fal_base_url}/{profile.render.model_id}", headers=_fal_headers(), json=payload,
                             timeout=FAL_SUBMIT_TIMEOUT_S)
        resp.raise_for_status()
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        _guardar_error_fal(body)
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


# F78a (a): el pedido de rasgos, tal cual el handoff. Entrada = JSON con las personas que van a tener madre.
PROMPT_RASGOS = """Estas son personas reales de un documental. No tenemos fotos de ellas: el retrato de referencia de cada una se genera con IA, y
el espectador tiene que poder reconocer en cada foto quién es quién. Tu trabajo es darle a cada persona un aspecto propio.

Para cada persona escribí UNA frase en inglés con: forma de la cara, pelo (corte, color, canas), vello facial, si usa lentes y
contextura. A los niños no les pongas vello facial ni lentes.

Tiene que respetar, sin contradecirlos, su appearance_canon, el aspecto de su grupo y su sexo.
No pongas edad, ropa, heridas, enfermedad, expresión, oficio ni el nombre: eso lo ponen otras partes.
Dos personas del mismo sexo y de edad parecida no pueden compartir la misma combinación de pelo, vello facial y lentes."""


def _md5(obj: Any) -> str:
    return hashlib.md5(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _llamar_rasgos(entrada: list[dict]) -> dict[str, str]:
    """F78a (a): UNA llamada (MODELO_CASILLEROS con su esfuerzo de guion_v4, como los casilleros de m03; `call_json` registra el
    costo) con todas las personas → {name: rasgos}. Schema: lista de {name (enum = los name de entrada), rasgos}."""
    import claude_helpers  # noqa: PLC0415
    from script_engine import guion_v4  # noqa: PLC0415
    from script_engine.m03_visual import MODELO_CASILLEROS  # noqa: PLC0415
    schema = {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
        "name": {"type": "STRING", "enum": [e["name"] for e in entrada]}, "rasgos": {"type": "STRING"}},
        "required": ["name", "rasgos"]}}
    raw = claude_helpers.call_json(PROMPT_RASGOS + "\n\n" + json.dumps(entrada, ensure_ascii=False, indent=1),
                                   model=MODELO_CASILLEROS, response_schema=schema,
                                   effort=guion_v4.ESFUERZO[MODELO_CASILLEROS], description="foto madre rasgos")
    filas = raw if isinstance(raw, list) else next((v for v in (raw or {}).values() if isinstance(v, list)), [])
    return {str(f.get("name")): _clean(f.get("rasgos")) for f in filas
            if isinstance(f, dict) and f.get("name") and _clean(f.get("rasgos"))}


def rasgos_personas(entrada: list[dict], madre_dir: Path) -> tuple[dict[str, dict], dict[str, dict]]:
    """F78a (a): rasgos por persona con cache `foto_madre/rasgos.json` (md5 de la entrada). Misma entrada → los del cache, sin
    llamar. Devuelve (nuevos, previos): {name: {rasgos, md5}} de ahora y del cache anterior ({} si no había)."""
    cache = madre_dir / RASGOS_JSON
    previo: dict = {}
    if cache.exists():
        try:
            previo = json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previo = {}
    previos = previo.get("personas") or {}
    md5_entrada = _md5(entrada)
    if previo.get("md5_entrada") == md5_entrada and all(e["name"] in previos for e in entrada):
        return previos, previos
    rasgos = _llamar_rasgos(entrada)
    nuevos = {n: {"rasgos": r, "md5": _md5(r)} for n, r in rasgos.items()}
    madre_dir.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"md5_entrada": md5_entrada, "entrada": entrada, "personas": nuevos},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(cache)
    return nuevos, previos


def _a_previas(path: Path, carpeta: str = PREVIAS_DIR) -> Path | None:
    """F78a/F78b: mueve `path` y TODOS sus archivos hermanos (`<stem>_native.png`, `.prompt.txt`, `.llamada.json`) a
    `<dir>/<carpeta>/`; nada se borra (si el nombre ya está, sufijo _2, _3…). Devuelve dónde quedó `path` (None si no existía)."""
    if not path.exists():
        return None
    dest_dir = path.parent / carpeta
    dest_dir.mkdir(parents=True, exist_ok=True)
    sufijos = (path.suffix, "_native.png", ".prompt.txt", ".llamada.json")
    k = 1
    while any((dest_dir / f"{path.stem}{'' if k == 1 else '_' + str(k)}{suf}").exists() for suf in sufijos):
        k += 1
    stem = path.stem if k == 1 else f"{path.stem}_{k}"
    destino = dest_dir / f"{stem}{path.suffix}"
    path.rename(destino)
    for suf in sufijos[1:]:
        x = path.parent / f"{path.stem}{suf}"
        if x.exists():
            x.rename(dest_dir / f"{stem}{suf}")
    return destino


# F78b: el pedido de lo visible del estado, tal cual el handoff. Entrada = JSON con una fila por (persona, tramo) de variante.
PROMPT_ESTADOS = """Cada fila es una persona real de un documental, con la condición que el material documenta para esos años. Para cada fila escribí
en inglés, en una sola frase, SOLO lo que esa condición deja visible en su cuerpo, en una foto de cintura para arriba con la cara y
las dos manos a la vista: piel, cara, manos, brazos, pelo, postura y contextura, en términos concretos que se puedan fotografiar.
No pongas lugares, otras personas, objetos, ropa, acciones ni sentimientos.
No agregues nada que la condición no diga o no implique.
Si la condición no deja nada visible en el cuerpo, devolvé una cadena vacía."""


def _llamar_estados(filas: list[dict]) -> dict[tuple[str, str], str]:
    """F78b: UNA llamada (MODELO_CASILLEROS con su esfuerzo, como `_llamar_rasgos`) con todas las filas {name, tramo, condition}
    → {(name, tramo): estado_visible}. Schema: lista de {name (enum), tramo (enum), estado_visible}. Solo cuentan los pares de la
    entrada (un par cruzado no entra; el que falta vale "" en `estados_visibles`)."""
    import claude_helpers  # noqa: PLC0415
    from script_engine import guion_v4  # noqa: PLC0415
    from script_engine.m03_visual import MODELO_CASILLEROS  # noqa: PLC0415
    schema = {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
        "name": {"type": "STRING", "enum": sorted({f["name"] for f in filas})},
        "tramo": {"type": "STRING", "enum": sorted({f["tramo"] for f in filas})},
        "estado_visible": {"type": "STRING"}}, "required": ["name", "tramo", "estado_visible"]}}
    raw = claude_helpers.call_json(PROMPT_ESTADOS + "\n\n" + json.dumps(filas, ensure_ascii=False, indent=1),
                                   model=MODELO_CASILLEROS, response_schema=schema,
                                   effort=guion_v4.ESFUERZO[MODELO_CASILLEROS], description="foto madre estados")
    salida = raw if isinstance(raw, list) else next((v for v in (raw or {}).values() if isinstance(v, list)), [])
    pares = {(f["name"], f["tramo"]) for f in filas}
    return {(str(f.get("name")), str(f.get("tramo"))): _clean(f.get("estado_visible")) for f in salida
            if isinstance(f, dict) and (str(f.get("name")), str(f.get("tramo"))) in pares}


def estados_visibles(filas: list[dict], madre_dir: Path) -> dict[tuple[str, str], str]:
    """F78b: lo visible del estado por (persona, tramo) con cache `foto_madre/estados.json` (md5 de la entrada), aparte de
    `rasgos.json`. Misma entrada → el cache, sin llamar. Un par sin respuesta → ""."""
    cache = madre_dir / ESTADOS_JSON
    md5_entrada = _md5(filas)
    try:
        previo = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    except (OSError, ValueError):
        previo = {}
    if previo.get("md5_entrada") == md5_entrada:
        return {(e["name"], e["tramo"]): e["estado_visible"] for e in previo.get("estados") or []}
    resp = _llamar_estados(filas)
    vis = {(f["name"], f["tramo"]): resp.get((f["name"], f["tramo"]), "") for f in filas}
    madre_dir.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"md5_entrada": md5_entrada, "entrada": filas,
                               "estados": [{"name": n, "tramo": t, "estado_visible": v} for (n, t), v in vis.items()]},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(cache)
    return vis


def _prompt_variante(cv: dict, estado_visible: str) -> str:
    """F78b: el texto del /edit de la variante (completo, del handoff F78b): la edad EXACTA en dígitos si hay, el `estado_visible`
    (lo que el estado deja ver en el cuerpo, de `estados_visibles`; no la `condition` cruda) si hay, cintura para arriba con cara y
    manos, ROPA_MADRE, ESTILO_C con `anio_estilo` (primer año del tramo; sin tramo, el año de la foto), NO_TEXT."""
    from script_engine import m03_imagenes_v3 as v3img  # noqa: PLC0415
    partes = ["The same person as in the reference image: same face, same features, same identity."]
    if cv.get("edad") is not None:
        partes.append(f"The person is now {cv['edad']} years old; show that age in the face, hair and body.")
    ev = (estado_visible or "").strip().rstrip(".").strip()
    if ev:
        partes.append(ev + ".")
    partes.append(f"Waist-up portrait framed so that the face and both hands are visible, {ROPA_MADRE}, plain mid-grey "
                  "background, soft even light.")
    partes.append(v3img.ESTILO_C.format(anio=cv["anio_estilo"]))
    partes.append(v3img.NO_TEXT)
    return " ".join(partes)


def _generate_variante(prompt: str, madre: Path, dest: Path) -> dict:
    """F78a (b): la variante = /edit de producción (`asset_manager._generar_nb2`, sin la frase de madres; su respaldo Seedream
    vale igual) con la madre limpia de referencia. Registra el costo (lo hace `_generar_nb2`). F78b: el `.prompt.txt` (con la
    firma) lo escribe quien la pide, antes."""
    import asset_manager as am  # noqa: PLC0415
    meta = am._generar_nb2(prompt, dest, None, [am._path_to_data_uri(madre)], frase_de_madres=False)
    _ensure_real_png(dest)
    return meta


def _candidatas(topic: dict, visual: dict) -> tuple[list[tuple[dict, list[dict], str]], dict[str, dict]]:
    """F78c (sale de `generate_fotos_madre_personas` tal cual): las personas que van a tener madre — sale en ≥
    MADRE_PERSONA_MIN_FOTOS fotos de `visual` donde aporta por era y tiene `appearance_canon` — con sus fotos y el appearance
    de su grupo más frecuente. Devuelve ([(persona, fotos, grupo)], {nombre: estado de las que no entran})."""
    personas = [p for p in (topic.get("documented_people") or []) if isinstance(p, dict) and p.get("name")]
    fotos = _fotos_del_guion(visual)
    grupos = {g["id"]: g for g in (topic.get("people_groups") or []) if isinstance(g, dict) and g.get("id")}
    estados: dict[str, dict] = {}
    candidatas: list[tuple[dict, list[dict], str]] = []
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
        candidatas.append((p, mias, _grupo_mas_frecuente(mias, grupos)))
    return candidatas, estados


def entrada_rasgos(topic: dict, visual: dict) -> list[dict]:
    """F78c: la entrada EXACTA de la llamada de rasgos (la misma que arma `generate_fotos_madre_personas`): una fila por
    persona con madre {name, role, era, appearance_canon, grupo_appearance}. La usan foto_madre y m03: mismo md5."""
    candidatas, _ = _candidatas(topic, visual)
    return [{"name": p["name"], "role": p.get("role") or "", "era": p.get("era") or "",
             "appearance_canon": _clean(p.get("appearance_canon")), "grupo_appearance": g} for p, _, g in candidatas]


def rasgos_vigentes(topic: dict, video_id: str | None = None) -> tuple[dict[str, str], str]:
    """F78c (adenda 2): SOLO LECTURA, nunca llama. Los rasgos de `foto_madre/rasgos.json` del video si su `md5_entrada` coincide
    con `entrada_rasgos(topic, 03_visual.json del disco)`. Carpeta: OUTPUT_DIR/<video_id>/foto_madre, con video_id = id del topic
    si no se pasa (en LONG son el mismo, fase1_5 paso0). Devuelve ({nombre: rasgos}, "ok") o ({}, motivo)."""
    tid = str(topic.get("id") or "")
    vid = video_id or tid
    if not tid or not vid:
        return {}, "topic sin id"
    vpath = STEPS_DIR / tid / "03_visual.json"
    cache = OUTPUT_DIR / vid / "foto_madre" / RASGOS_JSON
    if not vpath.exists():
        return {}, f"sin {vpath.name}"
    if not cache.exists():
        return {}, f"sin {RASGOS_JSON}"
    try:
        visual = json.loads(vpath.read_text(encoding="utf-8"))
        previo = json.loads(cache.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {}, f"ilegible: {type(e).__name__}"
    entrada = entrada_rasgos(topic, visual)
    if not entrada:
        return {}, "sin personas con madre"
    if previo.get("md5_entrada") != _md5(entrada):
        return {}, f"md5 de la entrada distinto al de {RASGOS_JSON}"
    personas = previo.get("personas") or {}
    return {n: str(v.get("rasgos") or "") for n, v in personas.items() if isinstance(v, dict) and v.get("rasgos")}, "ok"


def generate_fotos_madre_personas(topic: dict, video_id: str, visual: dict | None = None) -> dict:
    """F60 B / F78a: madre por PERSONA del canon (`documented_people`) que sale en ≥ MADRE_PERSONA_MIN_FOTOS fotos (su nombre en
    `persona`, cualquier posición, en todos los caps incluidos los de clip) donde aporta madre por era. Lee `persona` de
    `_steps/<id>/03_visual.json` (o de `visual`). F78a (a): antes, UNA llamada con todas esas personas da los `rasgos` de cada
    una (cache `foto_madre/rasgos.json`); si los rasgos de una persona cambiaron (o su madre es de antes de los rasgos), su madre
    y sus variantes se mueven a `foto_madre/<PREVIAS_DIR>/` y se regeneran. Motor de la madre: Seedream del perfil por la cola;
    si el motor activo no es seedream/nb2_lite → sin madre de persona y aviso; rechazo o error → foto_madre="" y aviso. Mismo
    skip (archivo existente) y adopción manual que objeto/lugar. Destino output/<vid>/foto_madre/<slug(name)>.png.
    F78a (b): después, por cada persona con madre, una VARIANTE por clave (`clave_de_foto`: tramo de estado + edad) de sus fotos
    → `<slug>@<clave>.png` (/edit de la limpia); clave vacía = la madre limpia. F78b: el estado entra como `estado_visible` (UNA
    llamada con los pares (persona, tramo), cache `estados.json`) y la edad exacta; una clave sin estado visible ni edad no tiene
    variante (sus fotos van con la limpia; la vieja se mueve); una variante cuya firma (md5 de estado_visible + edad) cambió se
    mueve a `<PREVIAS_DIR>` y se rehace; si la firma coincide se reusa. Madres y variantes de
    distintas personas se piden a la vez (tope FLUX_MAX_WORKERS). Muta el topic (`foto_madre`, `foto_madre_variantes`) y
    devuelve {nombre: {estado, fotos, prompt, dest, rasgos, variantes}}."""
    personas = [p for p in (topic.get("documented_people") or []) if isinstance(p, dict) and p.get("name")]
    if not personas:
        return {}
    if visual is None:
        vpath = STEPS_DIR / str(topic.get("id") or video_id) / "03_visual.json"
        if not vpath.exists():
            print(f"     [foto_madre] sin {vpath} → sin madres de persona (correr m03 antes)")
            return {}
        visual = json.loads(vpath.read_text(encoding="utf-8"))
    madre_dir = OUTPUT_DIR / video_id / "foto_madre"
    candidatas, estados = _candidatas(topic, visual)   # F78c: la misma selección que usa `entrada_rasgos`
    if not candidatas:
        return estados

    # F78a (a): rasgos de todas a la vez (cache por md5 de la entrada); si fallan, no se mueve ni se genera nada.
    entrada = entrada_rasgos(topic, visual)   # F78c: la función pública que también usa m03 (mismo md5)
    try:
        rasgos, previos = rasgos_personas(entrada, madre_dir)
    except Exception as e:  # noqa: BLE001 — la madre NUNCA bloquea el topic
        error_handler.log_warning(PipelineStage.VIDEO, f"foto_madre rasgos no generados: {str(e)[:200]} → madres sin tocar")
        for p, _, _ in candidatas:
            estados[p["name"]]["estado"] = f"sin cambios: rasgos fallaron ({type(e).__name__})"
        return estados

    trabajos: list[tuple[dict, Path, str, int]] = []
    for p, mias, grupo in candidatas:
        name, est = p["name"], estados[p["name"]]
        dest = madre_dir / f"{_slug(name)}.png"
        est["dest"] = str(dest)
        r = rasgos.get(name)
        if not r:
            est["estado"] = "sin madre: la llamada no devolvió rasgos"
            continue
        est["rasgos"] = r["rasgos"]
        if (previos.get(name) or {}).get("md5") != r["md5"]:    # rasgos nuevos o madre de antes de los rasgos → a _previas
            movidos = [m for m in [_a_previas(dest)] + [_a_previas(v) for v in sorted(madre_dir.glob(f"{_slug(name)}@*.png"))
                                                          if not v.stem.endswith("_native")] if m]
            if movidos:
                print(f"     [foto_madre] {name}: rasgos nuevos → {len(movidos)} archivo(s) a {PREVIAS_DIR}/")
            if movidos or p.get("foto_madre"):
                p["foto_madre"], p["foto_madre_variantes"] = "", []
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
        if api.image_engine not in ("seedream", "nb2_lite"):   # F68: con Nano Banana la madre sigue saliendo de Seedream 4.5
            est["estado"] = f"sin madre: motor activo {api.image_engine} ≠ seedream"
            error_handler.log_warning(PipelineStage.VIDEO,
                                      f"foto_madre persona {name}: motor activo {api.image_engine!r} ≠ seedream → sin madre de persona")
            continue
        prompt = _prompt_persona(p, grupo, r["rasgos"])
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

    # F78a (b) / F78b: claves de las personas que tienen madre en disco; después, lo visible de cada estado (UNA llamada, una fila
    # por par (persona, tramo) único; cache estados.json). Si la llamada falla, no se mueve ni se genera ninguna variante.
    claves: list[tuple[dict, Path, dict[str, dict]]] = []
    for p, mias, _ in candidatas:
        madre = Path(p.get("foto_madre") or "")
        if not p.get("foto_madre") or not madre.exists():
            continue
        por_clave: dict[str, dict] = {}
        for f in mias:
            cv = clave_de_foto(p, f["anio"])
            if cv["clave"]:
                por_clave.setdefault(cv["clave"], {**cv, "fotos": []})["fotos"].append(
                    f"ch{f['cap']:02d}_{f['kind']}_{f['idx']:02d}")
        claves.append((p, madre, por_clave))
    filas: list[dict] = []
    for p, _, por_clave in claves:
        for cv in por_clave.values():
            fila = {"name": p["name"], "tramo": cv["tramo"], "condition": cv["condition"]}
            if cv["tramo"] and fila not in filas:
                filas.append(fila)
    vis: dict[tuple[str, str], str] = {}
    if filas:
        try:
            vis = estados_visibles(filas, madre_dir)
        except Exception as e:  # noqa: BLE001 — la variante NUNCA bloquea el topic
            error_handler.log_warning(PipelineStage.VIDEO, f"foto_madre estados no generados: {str(e)[:200]} → variantes sin tocar")
            for p, _, _ in claves:
                estados[p["name"]]["variantes"] = f"sin cambios: estados fallaron ({type(e).__name__})"
            return estados

    pedidas: list[tuple[dict, dict, Path, Path, str, str]] = []
    for p, madre, por_clave in claves:
        lista: list[dict] = []
        todas: list[dict] = []
        for clave, cv in por_clave.items():
            dest = madre_dir / f"{_slug(p['name'])}@{clave}.png"
            ev = vis.get((p["name"], cv["tramo"]), "") if cv["tramo"] else ""
            firma = _md5({"estado_visible": ev, "edad": cv["edad"]})
            fila = {"clave": clave, "tramo": cv["tramo"], "edad": cv["edad"], "estado_visible": ev,
                    "path": str(dest.resolve()), "fotos": cv["fotos"]}
            todas.append(fila)
            if not ev and cv["edad"] is None:       # nada que cambiar sobre la limpia → sin variante (sus fotos van con la limpia)
                if _a_previas(dest):
                    print(f"     [foto_madre] {dest.name}: sin estado visible → a {PREVIAS_DIR}/")
                fila["estado"] = "sin variante: sin estado visible"
                continue
            lista.append(fila)
            if dest.exists() and _firma_de(dest) != firma:   # cambió el estado o la edad (o es de antes de la firma)
                _a_previas(dest)
                print(f"     [foto_madre] {dest.name}: firma nueva → la vieja a {PREVIAS_DIR}/")
            if dest.exists():
                fila["estado"] = "skip (ya existe)"
                continue
            if api.image_engine not in ("seedream", "nb2_lite"):
                fila["estado"] = f"sin variante: motor activo {api.image_engine}"
                continue
            pedidas.append((p, fila, madre, dest, _prompt_variante(cv, ev), firma))
        p["foto_madre_variantes"] = lista
        estados[p["name"]]["variantes"] = todas

    def hacer_var(t):
        p, fila, madre, dest, prompt, firma = t
        import asset_manager as am  # noqa: PLC0415
        _guardar_prompt_madre(dest, prompt, f"{am.MOTOR_PRINCIPAL} /edit (frase_de_madres=False) · referencia {madre.name}", firma)
        try:
            meta = _generate_variante(prompt, madre, dest)
            print(f"     [foto_madre] ✓ variante {dest.name}  ({len(fila['fotos'])} fotos, {meta.get('motor')})")
            return fila, {"estado": "ok", "motor": meta.get("motor"), "usd": meta.get("usd"), "prompt": prompt}
        except Exception as e:  # noqa: BLE001 — sin variante, esas fotos van con la madre limpia
            error_handler.log_warning(PipelineStage.VIDEO, f"foto_madre variante {dest.name} no generada: {str(e)[:150]}")
            return fila, {"estado": f"error: {type(e).__name__}: {str(e)[:160]}", "prompt": prompt}

    if pedidas:
        with ThreadPoolExecutor(max_workers=min(len(pedidas), FLUX_MAX_WORKERS)) as ex:
            for fila, st in ex.map(hacer_var, pedidas):
                fila.update(st)
    for p, _, _ in candidatas:   # en el topic solo quedan las variantes que existen (sin estado/prompt/usd)
        if "foto_madre_variantes" in p:
            p["foto_madre_variantes"] = [{k: v[k] for k in ("clave", "tramo", "edad", "path", "fotos")}
                                         for v in p.get("foto_madre_variantes") or [] if Path(v["path"]).exists()]
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
            _guardar_prompt_madre(dest, prompt, MADRE_IMAGE_MODEL)
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
