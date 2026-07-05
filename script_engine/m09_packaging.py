"""
m09_packaging.py — m09a: PAQUETE de publicación (metadata + thumbnail). chat 56.

Greenfield. NO toca ningún módulo existente. El upload es MANUAL (Omar en Studio);
m09b (API) queda para después.

Flujo en DOS pasos con gate humano en el medio:
  1) python -m script_engine.m09_packaging <topic_id> --candidates
       → metadata_candidatos.md + metadata.json(parcial) + thumb_candidates/ (bases SIN texto).
         PARA. Omar elige título y base.
  2) python -m script_engine.m09_packaging <topic_id> --compose --base <archivo>
        --text "TEXTO" [--title N]
       → thumb_final.png + metadata.json(final) + CHECKLIST_PUBLICACION.md.

Salida: output/<topic_id>/publish/.

Disciplina: metadata anclada en verified_facts (anti-alucinación). Thumbnail fresco
respeta §1 Flux R1-R6 + AP9 calma-tensa (regla 5 / APPARATUS OF KILLING). Fuente bundleada
(Anton OFL en script_engine/fonts/), NO depende de fuentes del sistema.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import webbrowser
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from config import OUTPUT_DIR, gemini_client, api
from google.genai import types as gt
from cost_tracker import cost_tracker

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ═══════════════════════════════════════════════════════════════
#  KNOBS (constantes — no hardcodear inline)
# ═══════════════════════════════════════════════════════════════
THUMB_W, THUMB_H = 1280, 720
THUMB_FONT_PATH = Path(__file__).parent / "fonts" / "Anton-Regular.ttf"
THUMB_TEXT_SCALE = 0.15          # alto de fuente por línea ≈ 15% del alto del thumb
THUMB_STROKE_PX = 8              # borde negro (≥6px a 1280×720)
THUMB_POSITION = "bottom-left"   # tercio inferior-izquierdo (esquina inf-DER libre = duración YT)
THUMB_MARGIN = 56

# Color del texto del overlay (stroke negro SIEMPRE). Default blanco.
THUMB_FILL_BLANCO = (255, 255, 255)
THUMB_FILL_AMARILLO = (255, 214, 0)
THUMB_FILL_ROJO = (231, 29, 29)
THUMB_FILLS = {"blanco": THUMB_FILL_BLANCO, "amarillo": THUMB_FILL_AMARILLO, "rojo": THUMB_FILL_ROJO}
THUMB_FILL_DEFAULT = "blanco"
THUMB_MAX_BYTES = 2 * 1024 * 1024
THUMB_MAX_LINES = 2

MAX_TITLE_CHARS = 90
MAX_TAGS_CHARS = 450
SHORTLIST_EXISTING = 4
FRESH_THUMBS = 3        # subido de 2 (chat 56): más tiros = más chance de ganadora, son centavos

META_TEMP = 0.35                 # generación creativa con gate humano (no clasificación)


# ═══════════════════════════════════════════════════════════════
#  Paths
# ═══════════════════════════════════════════════════════════════
def _assets_dir(tid: str) -> Path:
    return OUTPUT_DIR / tid / "assets"


def _publish_dir(tid: str) -> Path:
    return OUTPUT_DIR / tid / "publish"


def _candidates_dir(tid: str) -> Path:
    return _publish_dir(tid) / "thumb_candidates"


def _final_mp4(tid: str) -> Path:
    # ⚠ _final_v3_ZOOM.mp4, NO {id}_final.mp4 (ese es el stale del chat 54)
    return OUTPUT_DIR / tid / f"{tid}_final_v3_ZOOM.mp4"


def _load_canonical(tid: str) -> dict:
    return json.loads((Path("data") / "scripts" / f"{tid}.json").read_text(encoding="utf-8"))


# ═══════════════════════════════════════════════════════════════
#  Gemini helper (texto, temp controlada, response_schema) — clon local
# ═══════════════════════════════════════════════════════════════
def _gemini_json(system: str, user: str, schema: dict, temperature: float) -> dict:
    resp = gemini_client.models.generate_content(
        model=api.gemini_model, contents=user,
        config=gt.GenerateContentConfig(
            system_instruction=system, temperature=temperature,
            response_mime_type="application/json", response_schema=schema,
        ),
    )
    cost_tracker.track_gemini(description="m09 packaging", calls=1)
    return json.loads(resp.text)


# ═══════════════════════════════════════════════════════════════
#  METADATA (Gemini Flash texto)
# ═══════════════════════════════════════════════════════════════
_META_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "titulos": {"type": "ARRAY", "items": {"type": "STRING"}, "minItems": 6, "maxItems": 6},
        "overlays": {"type": "ARRAY", "items": {"type": "STRING"}, "minItems": 6, "maxItems": 6},
        "descripcion": {"type": "STRING"},
        "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["titulos", "overlays", "descripcion", "tags"],
}

_META_SYSTEM = """Sos el editor de empaquetado de un canal de YouTube de historia oscura
documental, en ESPAÑOL neutro-latino. Generás el paquete de metadata de un video a partir de
su guion. Todo se ancla en los hechos dados: NO inventes datos, nombres, fechas ni cifras que
no estén en el material; si dudás, omití.

TÍTULOS (6 candidatos, ≤70 caracteres cada uno — YouTube trunca ~70 en móvil):
- TODA cifra, fecha, nombre o dato del título debe salir LITERALMENTE de los VERIFIED FACTS
  provistos (no de tu memoria, no deducido, no redondeado inventando). Si un dato no está en
  esa lista, NO existe para el título. Cero excepciones: un canal documental muere por un
  número falso en el título.
- El GANCHO (la cifra o el dato brutal) va AL PRINCIPIO del título, nunca al final donde el
  truncado se lo come.
- Los 6 son ESTRATEGIAS distintas entre sí, no variaciones: (1) dato brutal/cifra,
  (2) misterio/pregunta, (3) acusación ("los dejaron..."), (4) lugar+año concreto,
  (5) contradicción/ironía histórica, (6) consecuencia humana.
- El título es un CONTRATO: solo prometé lo que la narración de verdad cuenta.
- Sin clickbait mentiroso, sin mayúsculas sostenidas, sin emojis.

OVERLAYS (6 candidatos, 2-4 palabras, MAYÚSCULAS):
- Texto que va SOBRE la miniatura. REGLA DE ORO: la imagen ya muestra la escena — el overlay
  NO la describe, ABRE UNA PREGUNTA que solo el video responde. "PRISIÓN INUNDADA" describe
  (mal); "LOS DEJARON MORIR AQUÍ" intriga (bien).
- Anclado en el material: acusación, pregunta corta, cifra de los VERIFIED FACTS, o
  consecuencia. Sin clickbait mentiroso. Si el TÍTULO elegido probablemente lleve la cifra,
  al menos 3 de los 6 overlays NO deben repetir cifra (título cuantifica, overlay acusa).
- Los 6 distintos entre sí: 2 acusación · 2 pregunta · 1 cifra · 1 consecuencia.

DESCRIPCIÓN (150-300 palabras):
- La PRIMERA oración es el gancho (es lo único visible antes de "ver más"): que dé intriga sin
  mentir.
- Luego un párrafo de contexto fiel al material y un cierre de una línea de canal.
- Sin relleno de keywords, sin listas de tags dentro del texto.

TAGS:
- Mayoría en español + 3 a 5 en inglés de alto volumen del tema (los nombres propios sirven en
  ambos idiomas). La suma de todos los tags no debe superar ~450 caracteres."""


def generate_metadata(canonical: dict) -> dict:
    narr = "\n\n".join(
        f"[Cap {c.get('chapter_number','?')}] {c.get('narration','').strip()}"
        for c in canonical.get("chapters", [])
    )
    # HANDOFF_137d §1.b: los facts se etiquetan F01..Fnn con el MISMO criterio del contrato
    # (m03: {f"F{i:02d}": facts[i-1]}) → una sola fuente de verdad para cifras del título.
    facts = canonical.get("verified_facts", [])
    facts_txt = "\n".join(
        f"F{i:02d}: {f.get('fact', f) if isinstance(f, dict) else f}"
        for i, f in enumerate(facts, start=1)
    )
    user = (
        f"TÍTULO DE TRABAJO: {canonical.get('video_title','')}\n\n"
        f"SUJETO CANÓNICO: {canonical.get('canonical_subject_description','')}\n\n"
        f"VERIFIED FACTS (única fuente válida de cifras/fechas/nombres):\n{facts_txt}\n\n"
        f"NARRACIÓN COMPLETA:\n{narr}\n\n"
        f"Generá el paquete de metadata (6 títulos, 6 overlays, descripción, tags)."
    )
    data = _gemini_json(_META_SYSTEM, user, _META_SCHEMA, META_TEMP)
    return _normalize_metadata(data)


def _normalize_metadata(data: dict) -> dict:
    titulos = [str(t).strip()[:MAX_TITLE_CHARS] for t in (data.get("titulos") or [])][:6]
    overlays = [str(o).strip().upper() for o in (data.get("overlays") or [])][:6]
    desc = str(data.get("descripcion", "")).strip()
    tags = _truncate_tags([str(t).strip() for t in (data.get("tags") or []) if str(t).strip()],
                          MAX_TAGS_CHARS)
    return {"titulos": titulos, "overlays": overlays, "descripcion": desc, "tags": tags}


def _truncate_tags(tags: list[str], max_chars: int) -> list[str]:
    """Recorta la lista de tags para que la suma (con comas) ≤ max_chars (regla YouTube)."""
    out: list[str] = []
    total = 0
    for t in tags:
        add = len(t) + (1 if out else 0)  # coma separadora
        if total + add > max_chars:
            break
        out.append(t)
        total += add
    return out


# ═══════════════════════════════════════════════════════════════
#  THUMB — shortlist de existentes top-punch (del audit_map.csv)
# ═══════════════════════════════════════════════════════════════
def shortlist_existing(audit_csv_path: Path, n: int = SHORTLIST_EXISTING) -> list[dict]:
    """Top-n imágenes por punch_total (desempate foco), excluyendo divergentes del eje1 y
    las que zoom_judge marcó superficie_plana. Puro y testeable.
    """
    rows = []
    with open(audit_csv_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("verdict_r1") or "fiel") != "fiel":
                continue
            if (r.get("zoom_judge_category") or "") == "superficie_plana":
                continue
            try:
                pt = int(r.get("punch_total_r1") or 0)
                foco = int(r.get("foco") or 0)
            except ValueError:
                continue
            rows.append({"filename": r["filename"], "cap": r["cap"], "img": r["img"],
                         "punch_total": pt, "foco": foco})
    rows.sort(key=lambda x: (x["punch_total"], x["foco"]), reverse=True)
    return rows[:n]


def _resolve_png(tid: str, filename: str) -> Path | None:
    hits = list(_assets_dir(tid).glob(f"**/{filename}.png"))
    return hits[0] if hits else None


# ═══════════════════════════════════════════════════════════════
#  THUMB — hero prompt (Gemini) + render seedream (vía productor)
# ═══════════════════════════════════════════════════════════════
_HERO_CONCEPT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "subject": {"type": "STRING"},   # casting: quién/qué eligió (PASO 1, trazabilidad)
        "prompt": {"type": "STRING"},
    },
    "required": ["subject", "prompt"],
}

# HANDOFF_137d §4: el hero devuelve TRES CONCEPTOS distintos (mata las trillizas — antes se
# renderizaba 3× el mismo prompt). Cada concepto = su propio casting + prompt.
_HERO_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "concepts": {"type": "ARRAY", "items": _HERO_CONCEPT_SCHEMA, "minItems": 3, "maxItems": 3},
    },
    "required": ["concepts"],
}

# Schema del ITERADOR con crítica: refina UN concepto → devuelve UN {subject, prompt}.
_HERO_ITER_SCHEMA = _HERO_CONCEPT_SCHEMA

_HERO_SYSTEM = """Sos director de arte de MINIATURAS (thumbnails) de YouTube. Tu objetivo NO es
ilustrar el tema: es DETENER EL SCROLL y generar intriga de click. Escribís UN prompt en inglés
para Flux 2 Pro.

PASO 1 — CASTING: leé la narración completa e identificá al sujeto más icónico y visualmente
magnético de ESTA historia. Prioridad: una PERSONA/personaje (la figura que encarna el drama) >
un OBJETO cargado > el LUGAR. El edificio o el espacio genérico SOLO si no hay nada mejor.
Devolvé en `subject` una frase corta con quién/qué elegiste.
PASO 2 — CONSTRUIR EL PROMPT: armá el prompt CTR alrededor de ESE sujeto, cumpliendo todos los
requisitos de abajo.

Requisitos DUROS:
- UNA figura o sujeto icónico DOMINANTE sacado del material (nunca ambientes vacíos): el rostro
  o la figura que la gente asocia a esta historia. En PLANO MEDIO o PRIMER PLANO — cara + torso
  GRANDES, ocupando buena parte de la mitad derecha, legibles a 120px. NUNCA cuerpo entero en
  plano abierto ni figura chica perdida en la arquitectura.
- INTRIGA VISUAL: la imagen plantea una pregunta sin responderla. Mirada directa a cámara, o algo
  levemente "mal" en la escena (una figura donde no debería haber nadie, una puerta abierta hacia
  la oscuridad, una silueta a medio revelar). El espectador debe NECESITAR el video para entender
  la foto.
- EMOCIÓN LEGIBLE a 120px de ancho — SOLO como física pintable: NUNCA la emoción
  como palabra abstracta ("miedo", "inquietud" a secas no renderizan). Escribila
  como evidencia física: mandíbula tensa, ojos muy abiertos con blanco visible,
  labios apretados, lágrimas surcando la mugre, nudillos blancos. UNA emoción
  dominante, 2-3 señales concretas. NUNCA gore ni shock — la intriga sale de la
  sugerencia, no del horror explícito.
- EL CUERPO CARGA LA SITUACIÓN: si la historia pone al sujeto en agua, fuego,
  encierro o intemperie, la miniatura lo muestra MARCADO por eso — empapado, pelo
  pegado al cráneo, ropa oscurecida por el agua, hollín, mugre con líneas de agua
  en cara y cuello. PROHIBIDO el sujeto seco, limpio y prolijo en una historia de
  desastre: es un error de continuidad que mata la credibilidad del click.
- Calma tensa inviolable (AP9): nada de cuerpos, muerte explícita, aftermath ni el aparato de
  matar. Si el tema es muerte/ejecución, la tensión viene de un sujeto vivo inquietante o de UN
  objeto cargado, jamás del mecanismo.
- COMPOSICIÓN: el sujeto va a la DERECHA del cuadro, GRANDE (plano medio/primer plano); el tercio
  IZQUIERDO queda oscuro y despejado (ahí se sobreimprime el texto). El lugar/contexto queda
  RECONOCIBLE pero SECUNDARIO detrás del sujeto (no desaparece — da el misterio del lugar).
- UN acento de color fuerte (cálido o frío) como punto focal sobre una paleta oscura — alto
  contraste, luz dramática, profundidad real.
- Subject-first: etnia/edad/ropa y época integradas al sujeto. Prosa 30-80 palabras. SIN prompts
  negativos. SIN texto en la imagen. Period-correct.

DEVOLVÉS TRES CONCEPTOS, NO UNO. REGLA INVIOLABLE: los TRES cumplen TODOS los requisitos
duros de arriba SIN EXCEPCIÓN — en los tres hay UNA figura humana GRANDE (plano medio o
primer plano, cara y torso dominando la mitad derecha, emoción LEGIBLE en física pintable a
120px, mirada a cámara o algo levemente "mal" que abre pregunta). Lo que varía entre
conceptos es LA HISTORIA que cuenta el cuadro, nunca la gramática del click:
  concepto 1 — el PROTAGONISTA en su momento pico (la cara que encarna el drama).
  concepto 2 — OTRO personaje u OTRO momento de la historia (el rescatista, el guardia que
               se fue, el sobreviviente después) — igual de GRANDE y frontal.
  concepto 3 — persona GRANDE interactuando con UN objeto cargado del material (las manos
               aferrando la reja, sosteniendo la pertenencia perdida, tocando la marca del
               agua) — el objeto SUMA intriga, la persona DOMINA el cuadro.
PROHIBIDO en cualquier concepto: siluetas lejanas, figuras chicas en la arquitectura, planos
donde la cara no se lee a 120px, ambientes sin persona dominante.
TEST DE CLICK antes de devolver: por cada concepto preguntate "¿un desconocido scrolleando
a las 2am frena el dedo Y se queda con una pregunta?" Si un concepto no pasa, reemplazalo."""


HERO_NARRATION_PER_CAP = 1400   # tope por cap para que la narración de los 7 caps entre holgada


def _narration_for_hero(canonical: dict) -> str:
    """Narración de los 7 caps para que el hero elija el sujeto (PASO 1). Cada cap se trunca a
    HERO_NARRATION_PER_CAP para no exceder contexto (se anota el truncado)."""
    parts = []
    for c in canonical.get("chapters", []):
        n = c.get("chapter_number", "?")
        txt = (c.get("narration") or "").strip()
        if len(txt) > HERO_NARRATION_PER_CAP:
            txt = txt[:HERO_NARRATION_PER_CAP] + " […]"
        parts.append(f"[Cap {n}] {txt}")
    return "\n\n".join(parts)


def _hero_user_prompt(canonical: dict) -> str:
    """Arma el user prompt del hero (PASO 1 necesita la narración). Puro/testeable."""
    return (
        f"TÍTULO: {canonical.get('video_title','')}\n"
        f"SUJETO CANÓNICO: {canonical.get('canonical_subject_description','')}\n\n"
        f"NARRACIÓN COMPLETA (PASO 1 — leela y elegí los sujetos más icónicos):\n"
        f"{_narration_for_hero(canonical)}\n\n"
        f"Devolvé los TRES conceptos de miniatura (cada uno con su `subject` y su `prompt` EN), "
        f"como pide el sistema: ideas COMPLETAMENTE distintas entre sí, no variaciones."
    )


def generate_hero_prompt(canonical: dict) -> list[dict]:
    """HANDOFF_137d §4: devuelve TRES conceptos [{'prompt','subject'}] DISTINTOS entre sí
    (mata las trillizas). Filtra los que vengan sin prompt."""
    d = _gemini_json(_HERO_SYSTEM, _hero_user_prompt(canonical), _HERO_SCHEMA, 0.4)
    out = []
    for c in (d.get("concepts") or []):
        p = str(c.get("prompt", "")).strip()
        if p:
            out.append({"prompt": p, "subject": str(c.get("subject", "")).strip()})
    return out


# ═══════════════════════════════════════════════════════════════
#  OVERLAY (Pillow)
# ═══════════════════════════════════════════════════════════════
def _fit_cover(im: Image.Image, w: int, h: int, focus: str = "center") -> Image.Image:
    """Escala (cover) + crop a (w,h). `focus` controla la franja VERTICAL del crop en
    fuentes verticales: 'center' (default), 'top' (preserva el tercio superior — caras
    altas), 'bottom'. Horizontal siempre centrado."""
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = round(im.width * scale), round(im.height * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    if focus == "top":
        top = 0
    elif focus == "bottom":
        top = nh - h
    else:
        top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def _wrap_lines(text: str, max_lines: int) -> list[str]:
    words = text.split()
    if len(words) <= 1:
        return words or [""]
    # balancear en hasta max_lines líneas por longitud
    if max_lines <= 1 or len(words) <= 1:
        return [" ".join(words)]
    mid = (len(words) + 1) // 2
    return [" ".join(words[:mid]), " ".join(words[mid:])][:max_lines]


def compose_thumbnail(base_path: Path, text: str, out_path: Path, focus: str = "center",
                      fill: str = THUMB_FILL_DEFAULT, size_factor: float = 1.0) -> Path:
    """Compone la miniatura final 1280×720 con overlay de texto (Anton, color `fill` +
    stroke negro, tercio inferior-izquierdo, esquina inf-DER libre). `fill` ∈
    {blanco, amarillo, rojo}. `focus` controla el cover-crop de bases verticales.
    HANDOFF_137d §3.c: `size_factor` escala el font (clamp 0.7–1.6, default 1.0). Devuelve
    el path realmente escrito (puede ser .jpg si el PNG superaba 2MB). Sin red — testeable."""
    base = _fit_cover(Image.open(base_path), THUMB_W, THUMB_H, focus)
    draw = ImageDraw.Draw(base)
    text = (text or "").upper().strip()
    lines = _wrap_lines(text, THUMB_MAX_LINES) if text else []
    color = THUMB_FILLS.get(fill, THUMB_FILLS[THUMB_FILL_DEFAULT])
    sf = max(0.7, min(1.6, float(size_factor or 1.0)))

    if lines:
        font_px = int(THUMB_H * THUMB_TEXT_SCALE * sf)
        font = ImageFont.truetype(str(THUMB_FONT_PATH), font_px)
        line_h = font_px + 10
        total_h = line_h * len(lines)
        y = THUMB_H - THUMB_MARGIN - total_h   # tercio inferior
        for ln in lines:
            draw.text((THUMB_MARGIN, y), ln, font=font, fill=color,
                      stroke_width=THUMB_STROKE_PX, stroke_fill=(0, 0, 0))
            y += line_h

    out_path.parent.mkdir(parents=True, exist_ok=True)
    base.save(out_path, "PNG", optimize=True)
    if out_path.stat().st_size <= THUMB_MAX_BYTES:
        return out_path
    # PNG > 2MB → fallback JPEG bajando calidad (YouTube acepta jpg <2MB)
    jpg = out_path.with_suffix(".jpg")
    for q in (92, 88, 84, 80, 75):
        base.save(jpg, "JPEG", quality=q)
        if jpg.stat().st_size <= THUMB_MAX_BYTES:
            break
    out_path.unlink(missing_ok=True)
    print(f"  ⚠ PNG superaba 2MB → usé {jpg.name} (q≤92)")
    return jpg


def _validate_text(text: str) -> str:
    n = len((text or "").split())
    if n == 0:
        raise ValueError("--text vacío. Pasá 2-4 palabras en MAYÚSCULAS.")
    if n > 5:
        print(f"  ⚠ --text tiene {n} palabras (>5): puede quedar ilegible en miniatura.")
    return text


def next_thumb_name(tid: str) -> str:
    """Próximo thumb_final_NN.png versionado (el form compone varias veces; Omar compara)."""
    pub = _publish_dir(tid)
    nums = [int(p.stem.rsplit("_", 1)[1]) for p in pub.glob("thumb_final_*.png")
            if p.stem.rsplit("_", 1)[1].isdigit()]
    return f"thumb_final_{(max(nums) + 1) if nums else 1:02d}.png"


# ═══════════════════════════════════════════════════════════════
#  PASO 1 — candidates
# ═══════════════════════════════════════════════════════════════
def _next_fresh_index(cand_dir: Path) -> int:
    """Próximo índice de fresh_NN.png sin pisar los existentes."""
    nums = []
    for p in cand_dir.glob("fresh_*.png"):
        part = p.stem.split("_", 1)[1]
        if part.isdigit():
            nums.append(int(part))
    return (max(nums) + 1) if nums else 1


def _render_fresh_from_hero(hero: str, cand_dir: Path, count: int, start_idx: int) -> tuple[list[str], list[str]]:
    """Renderiza `count` frescas seedream 16:9 desde un hero dado, numerando desde start_idx
    (sin pisar). Devuelve (líneas .md, nombres de archivo generados)."""
    import asset_manager as am   # noqa: PLC0415
    lines: list[str] = []
    files: list[str] = []
    for k in range(count):
        idx = start_idx + k
        out = cand_dir / f"fresh_{idx:02d}.png"
        try:
            am._generate_image_raw(hero, out, use_ultra=False)
            lines.append(f"- fresh_{idx:02d}.png ✓"); files.append(out.name)
        except Exception as e:
            lines.append(f"- fresh_{idx:02d}.png ✗ ({type(e).__name__}: {str(e)[:80]})")
    if not files:
        lines.append("- ⚠ render falló en todas — seguí con las existentes.")
    return lines, files


def _generate_fresh(canonical: dict, cand_dir: Path, count: int,
                    start_idx: int) -> tuple[list[str], list[dict], list[str]]:
    """HANDOFF_137d §4: genera 3 CONCEPTOS distintos y renderiza 1 frescas POR concepto
    (3 total, mismo costo que antes). Devuelve (líneas .md, concepts ALINEADOS a files, files).
    `concepts[i]` es el {prompt,subject} del que salió `files[i]`."""
    try:
        concepts = generate_hero_prompt(canonical)
    except Exception as e:
        return [f"- ⚠ hero prompt falló ({type(e).__name__}: {e}) — sin frescas."], [], []
    if not concepts:
        return ["- ⚠ hero no devolvió conceptos — sin frescas."], [], []
    lines: list[str] = []
    files: list[str] = []
    file_concepts: list[dict] = []
    for k, concept in enumerate(concepts):
        idx = start_idx + k
        lines.append(f"- concepto {k+1} · casting: _{concept['subject'][:80]}_")
        l2, f2 = _render_fresh_from_hero(concept["prompt"], cand_dir, 1, idx)
        lines += l2
        for fn in f2:
            files.append(fn)
            file_concepts.append(concept)
    return lines, file_concepts, files


def _render_concept_variations(concept_prompt: str, cand_dir: Path, count: int,
                               start_idx: int) -> tuple[list[str], list[str]]:
    """Renderiza `count` VARIACIONES del MISMO concepto (usado por GENERAR MÁS sobre una
    candidata elegida — el director ya eligió el concepto y quiere más tiros de ESE)."""
    return _render_fresh_from_hero(concept_prompt, cand_dir, count, start_idx)


def generate_hero_prompt_iter(prev_prompt: str, critique: str) -> dict:
    """Reescribe UN concepto de hero incorporando la crítica de Omar, SIN perder las reglas CTR
    del _HERO_SYSTEM (la crítica SUMA, no reemplaza). Devuelve UN {'prompt','subject'} refinado
    (HANDOFF_137d §4.b: la iteración con crítica trabaja sobre EL concepto elegido, no los tres)."""
    user = (
        f"PROMPT ANTERIOR (UN concepto):\n«{prev_prompt}»\n\n"
        f"El cliente (director) recibió esta imagen y pidió estas CORRECCIONES:\n«{critique}»\n\n"
        f"Reescribí ESE prompt incorporando la crítica, SIN perder ninguna de las reglas del "
        f"sistema (casting del sujeto, intriga CTR, sujeto a la derecha, tercio izquierdo "
        f"despejado, acento de color, AP9 calma-tensa). La crítica se SUMA a las reglas.\n"
        f"IMPORTANTE: acá NO devolvés tres conceptos — refinás UN SOLO concepto (el elegido) "
        f"y devolvés UN objeto {{\"subject\", \"prompt\"}}."
    )
    d = _gemini_json(_HERO_SYSTEM, user, _HERO_ITER_SCHEMA, 0.4)
    return {"prompt": str(d.get("prompt", "")).strip(), "subject": str(d.get("subject", "")).strip()}


def _iterations_path(pub: Path) -> Path:
    return pub / "hero_iterations.json"


def _load_iterations(pub: Path) -> list[dict]:
    p = _iterations_path(pub)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _record_iteration(pub: Path, feedback: str | None, files: list[str],
                      concepts: list[dict]) -> None:
    """Anexa una vuelta a hero_iterations.json. HANDOFF_137d §4: `concepts` va ALINEADO a
    `files` (concepts[i] = {subject,prompt} del que salió files[i]) → cada candidata muestra
    el casting de SU concepto. Compat lectura: los records viejos traían `subject` único."""
    hist = _load_iterations(pub)
    hist.append({"iteration": len(hist), "feedback": feedback,
                 "files": files, "concepts": concepts})
    _iterations_path(pub).write_text(json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")


def candidates_ready(tid: str) -> bool:
    """True si ya existe metadata.json (las candidatas fueron generadas)."""
    return (_publish_dir(tid) / "metadata.json").exists()


def run_candidates(tid: str, skip_fresh: bool = False, only_fresh: bool = False,
                   review: bool = False, video_path: str | None = None) -> None:
    canonical = _load_canonical(tid)
    pub = _publish_dir(tid); cand = _candidates_dir(tid)
    cand.mkdir(parents=True, exist_ok=True)

    # ── Modo --only-fresh: NO re-quema metadata ni re-copia existentes; solo más frescas ──
    if only_fresh:
        start = _next_fresh_index(cand)
        print(f"  [m09a] --only-fresh: {FRESH_THUMBS} frescas más desde fresh_{start:02d} (CTR)...")
        lines, concepts, files = _generate_fresh(canonical, cand, FRESH_THUMBS, start)
        if files:
            _record_iteration(pub, None, files, concepts)
        md_path = pub / "metadata_candidatos.md"
        prev = md_path.read_text(encoding="utf-8") if md_path.exists() else ""
        md_path.write_text(prev + "\n\n## Frescas adicionales (--only-fresh)\n\n" + "\n".join(lines),
                           encoding="utf-8")
        print("\n".join("     " + l for l in lines))
        print(f"  ✅ frescas adicionales en {cand}")
        if review:
            run_review(tid, video_path=video_path)
        return

    print(f"  [m09a] metadata (Gemini, temp {META_TEMP})...")
    meta = generate_metadata(canonical)

    # metadata.json (parcial — los 3 títulos, sin elección aún)
    (pub / "metadata.json").write_text(json.dumps({
        "topic_id": tid, "stage": "candidates",
        "titulos": meta["titulos"], "overlays": meta["overlays"],
        "descripcion": meta["descripcion"], "tags": meta["tags"],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # metadata_candidatos.md (legible)
    md = [f"# Metadata candidatos — {canonical.get('video_title','')}\n",
          "## Títulos (elegí 1 con --title N, 1-3)\n"]
    for i, t in enumerate(meta["titulos"], 1):
        md.append(f"{i}. {t}  _({len(t)} chars)_")
    md += ["\n## Descripción\n", meta["descripcion"],
           f"\n## Tags ({sum(len(t) for t in meta['tags']) + max(0,len(meta['tags'])-1)} chars)\n",
           ", ".join(meta["tags"]), "\n"]

    # Thumbnail bases existentes (top-punch)
    audit = Path("_lab_out/lab_fidelity_punch_chat56/audit_map.csv")
    md.append("## Miniaturas — bases existentes (top punch)\n")
    if audit.exists():
        sl = shortlist_existing(audit, SHORTLIST_EXISTING)
        for i, s in enumerate(sl, 1):
            src = _resolve_png(tid, s["filename"])
            if src:
                shutil.copy(src, cand / f"existing_{i:02d}.png")
                md.append(f"- existing_{i:02d}.png ← {s['filename']} "
                          f"(cap {s['cap']} img {s['img']}, punch {s['punch_total']}/8, foco {s['foco']})")
    else:
        md.append("- ⚠ audit_map.csv no encontrado — sin bases existentes.")

    # Thumbnails frescas seedream 16:9 (CTR)
    md.append("\n## Miniaturas — bases frescas (seedream 16:9)\n")
    if skip_fresh:
        md.append("- (omitidas: --skip-fresh)")
    else:
        fresh_lines, concepts, files = _generate_fresh(canonical, cand, FRESH_THUMBS, _next_fresh_index(cand))
        md += fresh_lines
        if files:
            _record_iteration(pub, None, files, concepts)

    (pub / "metadata_candidatos.md").write_text("\n".join(md), encoding="utf-8")
    print(f"  ✅ candidates en {pub}")
    print(f"     Elegí título + base y corré: --compose --base <archivo> --text \"TEXTO\" --title N")
    if review:
        run_review(tid, video_path=video_path)


# ═══════════════════════════════════════════════════════════════
#  PASO 2 — compose
# ═══════════════════════════════════════════════════════════════
_CHECKLIST_TMPL = """# Checklist de publicación — {title}

## Archivo
- **Video:** `{mp4}`
- **Miniatura:** `{thumb}`

## Pegar en YouTube Studio
**Título:**
{title}

**Descripción:**
{desc}

**Tags:**
{tags}

## Ajustes en Studio
- Idioma del video: **Español**
- Categoría: **Educación** o **Entretenimiento** (Omar decide)
- Audiencia: **No, no es contenido para niños**
- Visibilidad inicial: pública o programada (a elección de Omar)
- Agregar el video a una **playlist** del canal

## Pre-vuelo
- ⚠ Verificar **cap3 sin texto fantasma** antes de subir (pendiente de backlog).
"""


# ═══════════════════════════════════════════════════════════════
#  REVIEW LOOP visual (--review)
# ═══════════════════════════════════════════════════════════════
def _candidate_files(cand_dir: Path) -> list[Path]:
    """Bases candidatas en orden estable: existing_* y luego fresh_*."""
    return sorted(cand_dir.glob("existing_*.png")) + sorted(cand_dir.glob("fresh_*.png"))


def _open(path_or_url) -> None:
    """Abre un archivo o URL en el navegador (Windows os.startfile / webbrowser fallback)."""
    try:
        s = str(path_or_url)
        if os.name == "nt" and not s.startswith("http"):
            os.startfile(s)  # type: ignore[attr-defined]
        else:
            webbrowser.open(s)
    except Exception as e:
        print(f"  (no pude abrir el navegador: {e} — abrí a mano {path_or_url})")


def run_review(tid: str, video_path: str | None = None, on_compose=None,
               port: int | None = None, open_browser: bool = True,
               auto_generate_if_empty: bool = False) -> None:
    """--review levanta el FORM web local. video_path (de fase3/topics_db) va al CHECKLIST;
    on_compose(thumb_name) se llama tras cada COMPONER exitoso (fase3 lo usa para PACKAGED).
    port/open_browser (HANDOFF_135): el QA Studio lo spawnea con puerto fijo y sin abrir
    pestaña (lo embebe en iframe). Default = comportamiento de siempre (puerto libre + abre).
    auto_generate_if_empty (HANDOFF_136b): primera tanda automática si el topic no tiene
    candidatas (el QA Studio lo usa; ver serve())."""
    from script_engine.m09_review_server import serve
    serve(tid, video_path=video_path, on_compose=on_compose,
          port=port, open_browser=open_browser,
          auto_generate_if_empty=auto_generate_if_empty)


def _resolve_base(tid: str, base: str) -> Path:
    return (_candidates_dir(tid) / base) if not Path(base).is_absolute() else Path(base)


def compose_and_package(tid: str, base: str, text: str, title: str,
                        focus: str = "center", fill: str = THUMB_FILL_DEFAULT,
                        out_name: str = "thumb_final.png",
                        video_path: str | None = None, size_factor: float = 1.0) -> Path:
    """Compone la miniatura final + escribe metadata.json(final) + CHECKLIST. Reusable por el
    CLI (--compose, out_name fijo) y por el form (out_name versionado). `title` es el título
    ELEGIDO (string libre: una de las sugerencias o uno escrito a mano). El CHECKLIST referencia
    `video_path` si viene (fase3 lo resuelve desde topics_db); si no, cae al nombre v3 histórico.
    Devuelve el thumb escrito. Lanza ValueError/FileNotFoundError (el caller decide cómo mostrarlo)."""
    pub = _publish_dir(tid)
    meta = json.loads((pub / "metadata.json").read_text(encoding="utf-8"))
    title = (title or "").strip()[:MAX_TITLE_CHARS]
    if not title:
        raise ValueError("título vacío")
    base_path = _resolve_base(tid, base)
    if not base_path.exists():
        raise FileNotFoundError(f"Base no encontrada: {base_path}")
    text = _validate_text(text)

    written = compose_thumbnail(base_path, text, pub / out_name, focus, fill, size_factor)
    meta.update({"stage": "final", "titulo_elegido": title,
                 "base_thumb": base, "thumb_final": written.name})
    (pub / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    checklist = _CHECKLIST_TMPL.format(
        title=title, mp4=video_path or _final_mp4(tid), thumb=written,
        desc=meta.get("descripcion", ""), tags=", ".join(meta.get("tags", [])),
    )
    (pub / "CHECKLIST_PUBLICACION.md").write_text(checklist, encoding="utf-8")
    return written


def run_compose(tid: str, base: str, text: str, title_idx: int,
                focus: str = "center", fill: str = THUMB_FILL_DEFAULT,
                video_path: str | None = None) -> None:
    # CLI sigue eligiendo por índice (--title N, 1-3): resolvemos N→string acá, antes de componer.
    meta = json.loads((_publish_dir(tid) / "metadata.json").read_text(encoding="utf-8"))
    titulos = meta.get("titulos", [])
    if not (1 <= title_idx <= len(titulos)):
        raise SystemExit(f"--title {title_idx} fuera de rango (hay {len(titulos)}).")
    try:
        written = compose_and_package(tid, base, text, titulos[title_idx - 1], focus, fill,
                                      "thumb_final.png", video_path)
    except (ValueError, FileNotFoundError) as e:
        raise SystemExit(str(e))
    print(f"  ✅ thumb_final: {written.name} ({written.stat().st_size//1024} KB)")
    print(f"  ✅ CHECKLIST_PUBLICACION.md + metadata.json (final) en {_publish_dir(tid)}")


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════
def _resolve_mode(candidates: bool, compose: bool, review: bool) -> str:
    """Valida la combinación de flags y devuelve el modo: 'candidates' | 'compose' | 'review'.
    --review puede acompañar a --candidates (genera y abre el form); solo, abre el form sin
    generar. --compose es excluyente. Lanza ValueError en combinaciones inválidas."""
    if compose and (candidates or review):
        raise ValueError("--compose no se combina con --candidates ni --review")
    if candidates:
        return "candidates"   # review (si viene) se maneja dentro de run_candidates
    if compose:
        return "compose"
    if review:
        return "review"       # form solo, sin generar nada
    raise ValueError("elegí un modo: --candidates, --compose o --review")


def main() -> int:
    ap = argparse.ArgumentParser(description="m09a — paquete de publicación (metadata + thumbnail).")
    ap.add_argument("topic_id")
    ap.add_argument("--candidates", action="store_true", help="Paso 1: metadata + bases de thumbnail.")
    ap.add_argument("--skip-fresh", action="store_true",
                    help="No generar frescas (render del motor activo); solo existentes.")
    ap.add_argument("--only-fresh", action="store_true",
                    help="Solo regenerar hero+frescas (no re-quema metadata ni re-copia existentes).")
    ap.add_argument("--review", action="store_true",
                    help="Levanta el form web local. Solo (--review) abre el form sin generar; "
                         "junto a --candidates genera y abre el form.")
    ap.add_argument("--compose", action="store_true", help="Paso 2: overlay + checklist.")
    ap.add_argument("--base", help="Archivo base elegido (en thumb_candidates/).")
    ap.add_argument("--text", help="Texto del thumb (2-4 palabras, MAYÚSCULAS).")
    ap.add_argument("--title", type=int, default=1, help="Índice del título elegido (1-3).")
    ap.add_argument("--focus", choices=["top", "center", "bottom"], default="center",
                    help="Franja del cover-crop para bases verticales (default center).")
    ap.add_argument("--fill", choices=list(THUMB_FILLS), default=THUMB_FILL_DEFAULT,
                    help="Color del texto del overlay (stroke negro siempre). Default blanco.")
    ap.add_argument("--video-path", default=None,
                    help="Ruta del MP4 para el CHECKLIST (fase3 la resuelve desde topics_db). "
                         "Si falta, cae al nombre v3 histórico.")
    ap.add_argument("--port", type=int, default=None,
                    help="(HANDOFF_135, modo review) puerto fijo del form; default = libre.")
    ap.add_argument("--no-browser", action="store_true",
                    help="(HANDOFF_135, modo review) NO abrir pestaña (el QA Studio lo embebe).")
    ap.add_argument("--auto-first", action="store_true",
                    help="(HANDOFF_136b, modo review) si el topic no tiene candidatas, generar "
                         "la primera tanda (hero + frescas) en background al abrir el form.")
    args = ap.parse_args()

    try:
        mode = _resolve_mode(args.candidates, args.compose, args.review)
    except ValueError as e:
        ap.error(str(e))
    if mode == "candidates":
        run_candidates(args.topic_id, skip_fresh=args.skip_fresh, only_fresh=args.only_fresh,
                       review=args.review, video_path=args.video_path)
    elif mode == "compose":
        if not args.base or not args.text:
            ap.error("--compose requiere --base y --text")
        run_compose(args.topic_id, args.base, args.text, args.title, focus=args.focus,
                    fill=args.fill, video_path=args.video_path)
    else:  # review solo → form (con --auto-first genera la primera tanda si falta)
        run_review(args.topic_id, video_path=args.video_path,
                   port=args.port, open_browser=not args.no_browser,
                   auto_generate_if_empty=args.auto_first)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
