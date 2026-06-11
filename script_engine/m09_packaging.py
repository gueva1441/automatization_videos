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
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import requests
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
        "titulos": {"type": "ARRAY", "items": {"type": "STRING"}, "minItems": 3, "maxItems": 3},
        "descripcion": {"type": "STRING"},
        "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["titulos", "descripcion", "tags"],
}

_META_SYSTEM = """Sos el editor de empaquetado de un canal de YouTube de historia oscura
documental, en ESPAÑOL neutro-latino. Generás el paquete de metadata de un video a partir de
su guion. Todo se ancla en los hechos dados: NO inventes datos, nombres, fechas ni cifras que
no estén en el material; si dudás, omití.

TÍTULOS (3 candidatos, ≤90 caracteres cada uno):
- Estilo dark-history: intriga + especificidad concreta (lugar, año o dato del material).
- Los 3 deben ser ESTRATEGIAS distintas entre sí, no variaciones de una: por ejemplo uno de
  misterio, uno de dato brutal/concreto, uno en forma de pregunta.
- Sin clickbait mentiroso, sin mayúsculas sostenidas, sin emojis.

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
    facts = canonical.get("verified_facts", [])
    facts_txt = "\n".join(
        f"- {f.get('fact', f) if isinstance(f, dict) else f}" for f in facts
    )
    user = (
        f"TÍTULO DE TRABAJO: {canonical.get('video_title','')}\n\n"
        f"SUJETO CANÓNICO: {canonical.get('canonical_subject_description','')}\n\n"
        f"HECHOS VERIFICADOS (única fuente de datos permitida):\n{facts_txt}\n\n"
        f"NARRACIÓN COMPLETA:\n{narr}\n\n"
        f"Generá el paquete de metadata (3 títulos, descripción, tags)."
    )
    data = _gemini_json(_META_SYSTEM, user, _META_SCHEMA, META_TEMP)
    return _normalize_metadata(data)


def _normalize_metadata(data: dict) -> dict:
    titulos = [str(t).strip()[:MAX_TITLE_CHARS] for t in (data.get("titulos") or [])][:3]
    desc = str(data.get("descripcion", "")).strip()
    tags = _truncate_tags([str(t).strip() for t in (data.get("tags") or []) if str(t).strip()],
                          MAX_TAGS_CHARS)
    return {"titulos": titulos, "descripcion": desc, "tags": tags}


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
#  THUMB — hero prompt (Gemini) + render Flux 16:9 (clon mínimo fal.ai)
# ═══════════════════════════════════════════════════════════════
_HERO_SCHEMA = {"type": "OBJECT", "properties": {"prompt": {"type": "STRING"}}, "required": ["prompt"]}

_HERO_SYSTEM = """Sos director de arte de MINIATURAS (thumbnails) de YouTube. Tu objetivo NO es
ilustrar el tema: es DETENER EL SCROLL y generar intriga de click. Escribís UN prompt en inglés
para Flux 2 Pro.

Requisitos DUROS:
- UNA figura o sujeto icónico DOMINANTE sacado del material (nunca ambientes vacíos): el rostro
  o la figura que la gente asocia a esta historia.
- INTRIGA VISUAL: la imagen plantea una pregunta sin responderla. Mirada directa a cámara, o algo
  levemente "mal" en la escena (una figura donde no debería haber nadie, una puerta abierta hacia
  la oscuridad, una silueta a medio revelar). El espectador debe NECESITAR el video para entender
  la foto.
- EMOCIÓN LEGIBLE a 120px de ancho: inquietud, desasosiego — NUNCA gore ni shock. La intriga sale
  de la sugerencia, no del horror explícito.
- Calma tensa inviolable (AP9): nada de cuerpos, muerte explícita, aftermath ni el aparato de
  matar. Si el tema es muerte/ejecución, la tensión viene de un sujeto vivo inquietante o de UN
  objeto cargado, jamás del mecanismo.
- COMPOSICIÓN: el sujeto va a la DERECHA del cuadro; el tercio IZQUIERDO queda oscuro y despejado
  (ahí se sobreimprime el texto).
- UN acento de color fuerte (cálido o frío) como punto focal sobre una paleta oscura — alto
  contraste, luz dramática, profundidad real.
- Subject-first: etnia/edad/ropa y época integradas al sujeto. Prosa 30-80 palabras. SIN prompts
  negativos. SIN texto en la imagen. Period-correct."""


def generate_hero_prompt(canonical: dict) -> str:
    user = (
        f"TÍTULO: {canonical.get('video_title','')}\n"
        f"SUJETO CANÓNICO: {canonical.get('canonical_subject_description','')}\n\n"
        f"Escribí el prompt EN para la miniatura (hero shot)."
    )
    return str(_gemini_json(_HERO_SYSTEM, user, _HERO_SCHEMA, 0.4).get("prompt", "")).strip()


def _flux_16x9(prompt: str, out_path: Path, timeout: int = 180) -> None:
    """Render Flux 2 Pro 16:9 (1280×720) — clon mínimo del wiring fal.ai (no toca asset_manager)."""
    headers = {"Authorization": f"Key {api.fal_api_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": prompt, "num_images": 1, "enable_safety_checker": True,
        "output_format": "png", "image_size": {"width": THUMB_W, "height": THUMB_H},
    }
    submit = f"{api.fal_base_url}/{api.fal_image_model}"
    resp = requests.post(submit, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "images" not in data:
        start = time.time()
        status_url, response_url = data["status_url"], data["response_url"]
        while time.time() - start < timeout:
            s = requests.get(status_url, headers=headers, timeout=15); s.raise_for_status()
            st = s.json().get("status", "").upper()
            if st == "COMPLETED":
                data = requests.get(response_url, headers=headers, timeout=15).json(); break
            if st in ("FAILED", "ERROR"):
                raise RuntimeError(f"Flux thumbnail falló: {json.dumps(s.json())[:200]}")
            time.sleep(2)
        else:
            raise TimeoutError(f"Flux thumbnail timeout {timeout}s")
    if not data.get("images"):
        raise RuntimeError("Flux thumbnail sin imágenes")
    url = data["images"][0]["url"]
    out_path.write_bytes(requests.get(url, timeout=60).content)
    cost_tracker.track_flux_pro(description=f"thumb: {prompt[:50]}", images=1)


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


def compose_thumbnail(base_path: Path, text: str, out_path: Path, focus: str = "center") -> Path:
    """Compone la miniatura final 1280×720 con overlay de texto (Anton, blanco + stroke negro,
    tercio inferior-izquierdo, esquina inf-DER libre). `focus` controla el cover-crop de bases
    verticales. Devuelve el path realmente escrito (puede ser .jpg si el PNG superaba 2MB).
    Sin red — testeable."""
    base = _fit_cover(Image.open(base_path), THUMB_W, THUMB_H, focus)
    draw = ImageDraw.Draw(base)
    text = (text or "").upper().strip()
    lines = _wrap_lines(text, THUMB_MAX_LINES) if text else []

    if lines:
        font_px = int(THUMB_H * THUMB_TEXT_SCALE)
        font = ImageFont.truetype(str(THUMB_FONT_PATH), font_px)
        line_h = font_px + 10
        total_h = line_h * len(lines)
        y = THUMB_H - THUMB_MARGIN - total_h   # tercio inferior
        for ln in lines:
            draw.text((THUMB_MARGIN, y), ln, font=font, fill=(255, 255, 255),
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
        raise SystemExit("--text vacío. Pasá 2-4 palabras en MAYÚSCULAS.")
    if n > 5:
        print(f"  ⚠ --text tiene {n} palabras (>5): puede quedar ilegible en miniatura.")
    return text


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


def _generate_fresh(canonical: dict, cand_dir: Path, count: int, start_idx: int) -> list[str]:
    """Genera `count` bases frescas Flux 16:9 desde UN hero prompt CTR, numerando desde
    start_idx (sin pisar). Devuelve líneas .md describiendo el resultado."""
    try:
        hero = generate_hero_prompt(canonical)
    except Exception as e:
        return [f"- ⚠ hero prompt falló ({type(e).__name__}: {e}) — sin frescas."]
    lines = [f"- hero prompt (CTR): _{hero[:160]}_"]
    ok = 0
    for k in range(count):
        idx = start_idx + k
        out = cand_dir / f"fresh_{idx:02d}.png"
        try:
            _flux_16x9(hero, out)
            lines.append(f"- fresh_{idx:02d}.png ✓"); ok += 1
        except Exception as e:
            lines.append(f"- fresh_{idx:02d}.png ✗ ({type(e).__name__}: {str(e)[:80]})")
    if ok == 0:
        lines.append("- ⚠ Flux falló en todas — seguí con las existentes.")
    return lines


def run_candidates(tid: str, skip_fresh: bool = False, only_fresh: bool = False) -> None:
    canonical = _load_canonical(tid)
    pub = _publish_dir(tid); cand = _candidates_dir(tid)
    cand.mkdir(parents=True, exist_ok=True)

    # ── Modo --only-fresh: NO re-quema metadata ni re-copia existentes; solo más frescas ──
    if only_fresh:
        start = _next_fresh_index(cand)
        print(f"  [m09a] --only-fresh: {FRESH_THUMBS} frescas más desde fresh_{start:02d} (CTR)...")
        lines = _generate_fresh(canonical, cand, FRESH_THUMBS, start)
        md_path = pub / "metadata_candidatos.md"
        prev = md_path.read_text(encoding="utf-8") if md_path.exists() else ""
        md_path.write_text(prev + "\n\n## Frescas adicionales (--only-fresh)\n\n" + "\n".join(lines),
                           encoding="utf-8")
        print("\n".join("     " + l for l in lines))
        print(f"  ✅ frescas adicionales en {cand}")
        return

    print(f"  [m09a] metadata (Gemini, temp {META_TEMP})...")
    meta = generate_metadata(canonical)

    # metadata.json (parcial — los 3 títulos, sin elección aún)
    (pub / "metadata.json").write_text(json.dumps({
        "topic_id": tid, "stage": "candidates",
        "titulos": meta["titulos"], "descripcion": meta["descripcion"], "tags": meta["tags"],
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

    # Thumbnails frescas Flux 16:9 (CTR)
    md.append("\n## Miniaturas — bases frescas (Flux 16:9)\n")
    if skip_fresh:
        md.append("- (omitidas: --skip-fresh)")
    else:
        md += _generate_fresh(canonical, cand, FRESH_THUMBS, _next_fresh_index(cand))

    (pub / "metadata_candidatos.md").write_text("\n".join(md), encoding="utf-8")
    print(f"  ✅ candidates en {pub}")
    print(f"     Elegí título + base y corré: --compose --base <archivo> --text \"TEXTO\" --title N")


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


def run_compose(tid: str, base: str, text: str, title_idx: int, focus: str = "center") -> None:
    pub = _publish_dir(tid)
    meta = json.loads((pub / "metadata.json").read_text(encoding="utf-8"))
    titulos = meta.get("titulos", [])
    if not (1 <= title_idx <= len(titulos)):
        raise SystemExit(f"--title {title_idx} fuera de rango (hay {len(titulos)} títulos).")
    title = titulos[title_idx - 1]

    base_path = (_candidates_dir(tid) / base) if not Path(base).is_absolute() else Path(base)
    if not base_path.exists():
        raise SystemExit(f"Base no encontrada: {base_path}")
    text = _validate_text(text)

    thumb_out = pub / "thumb_final.png"
    written = compose_thumbnail(base_path, text, thumb_out, focus)

    # metadata.json final
    meta.update({"stage": "final", "titulo_elegido": title,
                 "base_thumb": base, "thumb_final": written.name})
    (pub / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    checklist = _CHECKLIST_TMPL.format(
        title=title, mp4=_final_mp4(tid), thumb=written,
        desc=meta.get("descripcion", ""), tags=", ".join(meta.get("tags", [])),
    )
    (pub / "CHECKLIST_PUBLICACION.md").write_text(checklist, encoding="utf-8")
    print(f"  ✅ thumb_final: {written.name} ({written.stat().st_size//1024} KB)")
    print(f"  ✅ CHECKLIST_PUBLICACION.md + metadata.json (final) en {pub}")


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    ap = argparse.ArgumentParser(description="m09a — paquete de publicación (metadata + thumbnail).")
    ap.add_argument("topic_id")
    ap.add_argument("--candidates", action="store_true", help="Paso 1: metadata + bases de thumbnail.")
    ap.add_argument("--skip-fresh", action="store_true", help="No generar frescas Flux (solo existentes).")
    ap.add_argument("--only-fresh", action="store_true",
                    help="Solo regenerar hero+frescas (no re-quema metadata ni re-copia existentes).")
    ap.add_argument("--compose", action="store_true", help="Paso 2: overlay + checklist.")
    ap.add_argument("--base", help="Archivo base elegido (en thumb_candidates/).")
    ap.add_argument("--text", help="Texto del thumb (2-4 palabras, MAYÚSCULAS).")
    ap.add_argument("--title", type=int, default=1, help="Índice del título elegido (1-3).")
    ap.add_argument("--focus", choices=["top", "center", "bottom"], default="center",
                    help="Franja del cover-crop para bases verticales (default center).")
    args = ap.parse_args()

    if args.candidates == args.compose:
        ap.error("elegí exactamente uno: --candidates o --compose")
    if args.candidates:
        run_candidates(args.topic_id, skip_fresh=args.skip_fresh, only_fresh=args.only_fresh)
    else:
        if not args.base or not args.text:
            ap.error("--compose requiere --base y --text")
        run_compose(args.topic_id, args.base, args.text, args.title, focus=args.focus)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
